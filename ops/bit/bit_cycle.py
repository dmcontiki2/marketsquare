#!/usr/bin/env python3
"""
bit_cycle.py — one BIT cycle: run the registry against the live site, post the board to the
dashboard, and on a confirmed FAIL hand off to the Mitigator + the Triage->Fix loop.
Designed to be invoked every ~15 min by the Cowork scheduler (quiet-when-healthy).

Flow:
  1. run bit_runner.main() in-process -> results list (functional + negative BITs, N-of-M confirm)
  2. build a compact board {state, worst, pass, fail, results, ran_at}
  3. POST it to <base>/dashboard/bit so the dashboard health panel + Ops view can read it
  4. if any FAIL: emit findings (findings_bit.json -> Triage->Fix) and run the Mitigator (dry-run
     unless BIT_APPLY=1 and a token is set). Mitigation is reversible; it is never the fix.

Read-only against the app except the single status POST and the allow-listed reversible flag flips
(those only when BIT_APPLY=1). Stdlib only; budget-counted.
"""
import json, os, sys, datetime, urllib.request, urllib.error, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bit_runner

BASE  = os.environ.get("BIT_BASE", "https://trustsquare.co")
TOKEN = os.environ.get("BIT_ADMIN_TOKEN", "")
APPLY = os.environ.get("BIT_APPLY", "0") == "1"
bit_runner.BASE = BASE  # cycle + runner must test the SAME host (else runner uses the registry default)

def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def post_board(board):
    data=json.dumps(board).encode()
    req=urllib.request.Request(BASE.rstrip("/")+"/dashboard/bit", data=data,
                               headers={"Content-Type":"application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=12) as r: return r.status
    except Exception as e:
        return "post-failed: "+type(e).__name__

def run():
    # reachability: if /health doesn't answer 200/ok, this is UNKNOWN (e.g. site down / edge error), not a BIT failure.
    try:
        import json as _j
        _r=__import__("urllib.request",fromlist=["x"]).urlopen(BASE.rstrip("/")+"/health",timeout=10)
        _up=(_r.status==200 and _j.loads(_r.read()).get("status")=="ok")
    except Exception:
        _up=False
    if not _up:
        post_board({"state":"unknown","worst":0,"pass":0,"total":0,"failing":[],"results":[],"ran_at":now(),"base":BASE})
        print(f"[bit-cycle] {BASE} not reachable/healthy — UNKNOWN, not a failure."); return 0
    # run each BIT via the runner's logic
    results=[]
    worst=0
    for b in bit_runner.REG["bits"]:
        state, detail = bit_runner.run_one(b)
        results.append({"id":b["id"],"sev":b["severity"],"type":b["type"],
                        "state":state,"detail":detail,"desc":b["desc"]})
        if state!="PASS":
            worst=max(worst, 2 if b["severity"]=="S1" else 1)
    fails=[r for r in results if r["state"]!="PASS"]
    board={"state": "pass" if not fails else ("critical" if worst==2 else "degraded"),
           "worst": worst, "pass": len(results)-len(fails), "total": len(results),
           "failing": [r["id"] for r in fails], "results": results, "ran_at": now(), "base": BASE}
    status=post_board(board)
    print(f"[bit-cycle] {board['pass']}/{board['total']} PASS · state={board['state']} · posted={status} · {now()}")
    if fails:
        ids=[r["id"] for r in fails]
        print("  FAILing:", ids)
        # 1) emit findings into the Triage->Fix loop
        bit_runner.emit_findings_file(results, outdir=HERE)
        # 2) run the Mitigator (reversible; apply only if explicitly enabled + token present)
        cmd=[sys.executable, os.path.join(HERE,"bit_mitigator.py"), "--failed", *ids, "--base", BASE]
        if APPLY and TOKEN: cmd += ["--apply","--token",TOKEN]
        out=subprocess.run(cmd, capture_output=True, text=True)
        # only surface mitigation lines that actually DID/WOULD act (drop the ESCALATE noise in deploy output)
        acted=[l for l in out.stdout.splitlines() if ("WOULD" in l or "APPLIED" in l)]
        if acted: print("  mitigation: " + " | ".join(s.strip() for s in acted))
    return 0 if not fails else (2 if worst==2 else 1)

if __name__=="__main__":
    sys.exit(run())
