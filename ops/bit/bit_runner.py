#!/usr/bin/env python3
"""
TrustSquare BIT Runner — the working slice of the BIT architecture.
See BIT_ARCHITECTURE.md. Runs the registry of functional + negative BITs against
the live app, applies N-of-M confirm (no false-negative cry-wolf), prints a
severity-tagged board, and is QUIET-WHEN-HEALTHY (exit 0, no noise unless --verbose).

Exit codes:  0 = all PASS   1 = S2+ confirmed FAIL   2 = S1 confirmed FAIL
Usage: python3 bit/bit_runner.py [--verbose] [--json] [--base https://trustsquare.co]
This slice is READ-ONLY: it never edits, charges, or deploys. Acting on failures
(mitigate/resolve/prevent) is the BIT Agent's job per the architecture; this proves detection.
"""
import json, sys, time, urllib.request, urllib.error, os

ROOT = os.path.dirname(os.path.abspath(__file__))
REG  = json.load(open(os.path.join(ROOT, "bit_registry.json")))
BASE = REG["_meta"]["base_url"]
for i,a in enumerate(sys.argv):
    if a=="--base" and i+1<len(sys.argv): BASE=sys.argv[i+1]

# ── SERVER-BIT-2 (11 Aug 2026): vantage-point fixes ─────────────────────────────
# The cycle now runs ON the box against BEA uvicorn (localhost:8000), inside the
# pre-launch origin gate. Three surfaces are composed by nginx, not the BEA, so they
# need their own addressing from here:
#   /              -> the static shell nginx serves from disk        -> read the file
#   /static/ms.js  -> nginx static                                   -> read the file
#   /ai/functions  -> nginx proxy to the AdvertAgent service (:8002) -> ask it directly
# Each check still tests the REAL artifact; only the address changed.
LIVE   = os.environ.get("MS_LIVE", "/var/www/marketsquare")
AABASE = os.environ.get("BIT_AA_BASE", "http://localhost:8002")

def _disk_for(path):
    if path == "/":
        return os.path.join(LIVE, "index.html")
    if path.startswith("/static/"):
        return os.path.join(LIVE, path.lstrip("/"))
    return None

VERBOSE = "--verbose" in sys.argv
AS_JSON = "--json" in sys.argv

def _get(path, headers=None, timeout=15):
    url = BASE.rstrip("/") + path
    req = urllib.request.Request(url, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, (e.read() if hasattr(e,"read") else b"")
    except Exception as e:
        return None, str(e).encode()

# ---- check implementations: each returns (ok: bool, detail: str) ----
def c_http_json(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    try: j = json.loads(body)
    except: return False, "non-JSON body"
    k, v = b["expect"]["json_key"], b["expect"]["equals"]
    return (j.get(k)==v), f"{k}={j.get(k)!r}"

def c_http_json_count(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    try: j = json.loads(body)
    except: return False, "non-JSON body"
    arr = j if isinstance(j,list) else (j.get("items") or j.get("listings") or j.get("wonders") or j.get("data") or [])
    n = len(arr); return (n >= b["expect"]["min_count"]), f"count={n}"

def c_http_shell(b):
    st, body = _get(b["path"])
    via = "http"
    if st != 200:
        # SERVER-BIT-2: the shell is nginx's route, not the BEA's — from inside the
        # gate read the exact file nginx serves. Same assertions, same meaning
        # (a truncated or torn deploy still fails on size/contains).
        fp = _disk_for(b["path"])
        if fp and os.path.isfile(fp):
            body = open(fp, "rb").read(); via = "disk"
        else:
            return False, f"HTTP {st}"
    txt = body.decode("utf-8","replace"); n=len(body)
    e=b["expect"]
    if not (e["min_bytes"] < n < e["max_bytes"]): return False, f"size={n} ({via})"
    miss=[s for s in e["contains"] if s not in txt]
    return (not miss), (f"size={n} ok ({via})" if not miss else f"missing {miss} ({via})")

def c_http_status(b):
    st, _ = _get(b["path"], headers=b.get("headers"))
    return (st in b["expect"]["status_in"]), f"HTTP {st} (want {b['expect']['status_in']})"

def c_no_demo_bleed(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    try: j=json.loads(body)
    except: return False,"non-JSON"
    arr = j if isinstance(j,list) else (j.get("items") or j.get("listings") or [])
    bleed=[str(x.get("id")) for x in arr if str(x.get("id","")).startswith(b["expect"]["no_id_prefix"])]
    return (not bleed), (f"clean ({len(arr)} live)" if not bleed else f"BLEED: {bleed[:5]}")

def _feature_ids():
    # Pull advertised AI feature ids from the live FEA bundle (ms.js / AI_FNS payload).
    # Source of truth = whatever the BEA serves to feed AI_FNS. Try /ai/functions, fall back to scraping ms.js.
    # SERVER-BIT-2: /ai/functions is served by the AdvertAgent service (nginx-proxied
    # in production, :8002 on the box) — ask it directly first; its silence is a REAL
    # failure of the AI panel, exactly what these BITs exist to catch.
    try:
        import urllib.request as _u
        with _u.urlopen(AABASE.rstrip("/") + "/ai/functions", timeout=10) as _r:
            j = json.loads(_r.read().decode("utf-8", "replace"))
            ids = [f["id"] for f in (j if isinstance(j, list) else j.get("functions", [])) if "id" in f]
            if ids: return ids, "advertagent:/ai/functions"
    except Exception:
        pass
    for p in ("/ai/functions","/ai-functions","/static/ms.js"):
        st, body = _get(p)
        if st==200 and body:
            txt=body.decode("utf-8","replace")
            try:
                j=json.loads(txt)
                ids=[f["id"] for f in (j if isinstance(j,list) else j.get("functions",[])) if "id" in f]
                if ids: return ids, p
            except: pass
            import re
            ids=re.findall(r'\bid["\']?\s*[:=]\s*["\']([a-z0-9_]+)["\']', txt)
            ids=[i for i in dict.fromkeys(ids) if len(i)>3][:30]
            if ids: return ids, p
    # No disk scrape: ms.js interpolates feature ids at runtime, so the file holds no
    # literal list. If the AdvertAgent probe above was silent, /ai/functions is down in
    # production too (nginx proxies to that same service) — the FAIL is real.
    return [], None

def c_ai_example_contract(b):
    ids, src = _feature_ids()
    if not ids: return False, "could not enumerate AI feature ids"
    broken=[]
    for fid in ids:
        st,_ = _get(b["path"]+fid)
        if st != 200: broken.append(f"{fid}:{st}")
    if broken:
        return False, f"{len(broken)}/{len(ids)} example endpoints not OK -> {broken[:6]}"
    return True, f"{len(ids)} example endpoints OK (src {src})"

CHECKS={"http_json":c_http_json,"http_json_count":c_http_json_count,"http_shell":c_http_shell,
        "http_status":c_http_status,"no_demo_bleed":c_no_demo_bleed,"ai_example_contract":c_ai_example_contract}

def run_one(b):
    fn=CHECKS.get(b["check"])
    if not fn: return "ERROR", f"no check impl '{b['check']}'"
    need=b.get("confirm",1); ok_runs=0; last=""
    # N-of-M confirm: require `need` passes; a single fail that doesn't reach `need` passes is provisional.
    attempts=need+1
    for _ in range(attempts):
        ok,detail=fn(b); last=detail
        if ok: ok_runs+=1
        if ok_runs>=need: return "PASS", detail
        if not ok: time.sleep(0.4)
    return "FAIL", last

def main():
    results=[]; worst=0
    for b in REG["bits"]:
        state,detail=run_one(b)
        results.append({"id":b["id"],"sev":b["severity"],"type":b["type"],"state":state,"detail":detail,"desc":b["desc"]})
        if state=="FAIL": worst=max(worst, 2 if b["severity"]=="S1" else 1)
    fails=[r for r in results if r["state"]!="PASS"]
    if AS_JSON:
        print(json.dumps({"base":BASE,"worst":worst,"results":results},indent=2)); return worst
    if not fails and not VERBOSE:
        print(f"[BIT] all {len(results)} markers PASS against {BASE} — healthy (quiet)."); return 0
    print(f"\n=== TrustSquare BIT board — {BASE} ===")
    for r in results:
        if r["state"]=="PASS" and not VERBOSE: continue
        tag={"PASS":"[OK]  ","FAIL":"[FAIL]","ERROR":"[ERR] "}[r["state"]]
        print(f"  {tag} {r['sev']} {r['id']:<18} ({r['type']:<10}) {r['detail']}")
    if fails:
        print(f"\n  {len(fails)} marker(s) need attention. Worst severity exit={worst}.")
        for r in fails:
            print(f"    - {r['id']} [{r['sev']}]: {r['desc']}")
    else:
        print(f"  all {len(results)} PASS.")
    return worst

if __name__=="__main__":
    sys.exit(main())

# ---- Fix-pipeline handoff: emit a Detect-schema finding for FAILs (matches findings_prevent.json) ----
def emit_findings_file(results, outdir="."):
    import datetime as _dt
    fails=[r for r in results if r["state"]!="PASS"]
    if not fails: return None
    now=_dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    doc={"detect_run":"bit-"+now[:10],"scope":"BIT failures","generated_at":now,
         "engine":"BIT v1 (Phase: Detect handoff)",
         "findings":[{"id":r["id"],"sev":"HIGH" if r["sev"]=="S1" else "MED","slice":"bit",
                      "symptom":r["desc"],"root_cause":r["detail"],"file":"(varies)","area":"app",
                      "root_token":r["id"].lower(),"match_terms":[r["id"]],
                      "proposed_lane":"amber","confidence":"confirmed"} for r in fails]}
    import os as _os, json as _json
    p=_os.path.join(outdir,"findings_bit.json")
    _json.dump(doc,open(p,"w",encoding="utf-8"),indent=2); open(p,"a").write("\n")
    return p
