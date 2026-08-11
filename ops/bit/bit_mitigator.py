#!/usr/bin/env python3
"""
bit_mitigator.py — FAST, reversible safe-state step between "BIT fails" and "Fix loop / human resolves".
The existing Detect->Triage->Fix loop is daily — too slow for an S1 erroring at users now. The Mitigator
runs in seconds, NEVER edits code, and only flips pre-declared flags to a SAFE state via the BEA's existing
POST /admin/flags endpoint. It is the one place the BIT writes production state, so it is fenced by five guards:

  G1 ALLOW-LIST    — may write ONLY the flags in SAFE_FLAGS; anything else -> escalate to human.
  G2 SAFE-DIRECTION— may move a flag ONLY toward its declared safe value (e.g. disable a broken feature).
                     It can never ENABLE anything. Re-enabling after a fix is a separate human/Fix-loop action.
  G3 RECORD-FIRST  — reads + journals the CURRENT value BEFORE writing, so every flip is one-command reversible.
  G4 AUTH+IDEMPOTENT+RATE-LIMIT — admin token over HTTPS; no-op if already safe; capped flips per run so a
                     flapping BIT can't hammer the app.
  G5 --apply GATE + AUDIT — default is dry-run; live writes require --apply; every action is logged to the journal.

Rollback:  bit_mitigator.py --rollback   (replays the journal in reverse, restoring prior values).
Budget: stdlib only, no app imports, talks to the BEA only over HTTP.
"""
import argparse, json, os, sys, datetime, urllib.request, urllib.error

# G1 allow-list + G2 safe direction. 'safe' = the only value the Mitigator may WRITE.
SAFE_FLAGS = {
    "ai_example_enabled":   {"safe": False, "bit": "B-FEA-EXAMPLE",
                             "user_msg": "Examples are temporarily unavailable — the paid run is unaffected."},
    "auth_fail_closed":     {"safe": True,  "bit": "B-NEG-AUTH",        "user_msg": None},
    "tuppence_burn_enabled":{"safe": False, "bit": "B-NEG-DELIVER-CHARGE",
                             "user_msg": "A service is being checked; you will not be charged in the meantime."},
}
# Which flag a failed BIT triggers. cache_purge has no flag (idempotent op), handled separately.
BIT_TO_FLAG = {
    "B-FEA-EXAMPLE": "ai_example_enabled", "B-FEA-CONTRACT": "ai_example_enabled",
    "B-NEG-AUTH": "auth_fail_closed",
    "B-NEG-DELIVER-CHARGE": "tuppence_burn_enabled", "B-NEG-COST-CEILING": "tuppence_burn_enabled",
}
MAX_FLIPS_PER_RUN = 3            # G4 rate-limit
JOURNAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mitigation_journal.jsonl")

def now(): return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def _req(method, url, token=None, body=None, timeout=12):
    data = json.dumps(body).encode() if body is not None else None
    h = {"Content-Type": "application/json"} if data else {}
    if token: h["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {"error": (e.read() or b"").decode("utf-8","replace")[:200]}
    except Exception as e:
        return None, {"error": type(e).__name__ + ": " + str(e)[:160]}

def get_flags(base):
    st, j = _req("GET", base.rstrip("/") + "/flags")
    return j if st == 200 else {}

def journal_append(entry):
    with open(JOURNAL, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")

def mitigate(failed_ids, base, token, apply):
    current = get_flags(base)
    flips = []; escalate = []
    seen = set()
    for fid in failed_ids:
        flag = BIT_TO_FLAG.get(fid)
        if not flag:
            escalate.append((fid, "no flag mapping — escalate")); continue
        if flag not in SAFE_FLAGS:                      # G1
            escalate.append((fid, f"{flag} not on allow-list — escalate")); continue
        if flag in seen:                                 # dedupe
            continue
        seen.add(flag)
        safe = SAFE_FLAGS[flag]["safe"]
        cur = current.get(flag, None)
        if cur == safe:                                  # G4 idempotent
            flips.append({"bit": fid, "flag": flag, "status": "already-safe", "value": safe}); continue
        flips.append({"bit": fid, "flag": flag, "status": "flip", "from": cur, "to": safe,
                      "user_msg": SAFE_FLAGS[flag]["user_msg"]})
    to_apply = [f for f in flips if f["status"] == "flip"][:MAX_FLIPS_PER_RUN]   # G4 rate-limit
    for f in to_apply:
        if apply:
            # G3 record-first
            journal_append({"ts": now(), "action": "flip", "bit": f["bit"], "flag": f["flag"],
                            "prior": f["from"], "new": f["to"]})
            st, resp = _req("POST", base.rstrip("/") + "/admin/flags", token=token, body={f["flag"]: f["to"]})
            f["applied"] = (st == 200); f["http"] = st
        else:
            f["applied"] = False
    return flips, escalate

def rollback(base, token, apply):
    if not os.path.exists(JOURNAL):
        print("no journal — nothing to roll back"); return 0
    lines = [json.loads(l) for l in open(JOURNAL, encoding="utf-8") if l.strip()]
    # replay in reverse, restoring 'prior'
    seen = set(); restored = []
    for e in reversed(lines):
        if e.get("action") != "flip" or e["flag"] in seen: continue
        seen.add(e["flag"])
        print(f"  restore {e['flag']} -> {e['prior']} (undo {e['ts']})")
        if apply and e["prior"] is not None:
            st, _ = _req("POST", base.rstrip("/") + "/admin/flags", token=token, body={e["flag"]: e["prior"]})
            print(f"    http {st}")
        restored.append(e["flag"])
    if apply:
        journal_append({"ts": now(), "action": "rollback", "flags": restored})
    print(f"{'rolled back' if apply else 'WOULD roll back'} {len(restored)} flag(s). (use --apply to execute)")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--failed", nargs="*", default=[], help="failed BIT ids")
    ap.add_argument("--apply", action="store_true", help="execute live writes (default dry-run)")
    ap.add_argument("--rollback", action="store_true", help="undo prior mitigations from the journal")
    ap.add_argument("--base", default=os.environ.get("BIT_BASE", "https://trustsquare.co"))
    ap.add_argument("--token", default=os.environ.get("BIT_ADMIN_TOKEN", ""))
    a = ap.parse_args()

    if a.rollback:
        return rollback(a.base, a.token, a.apply)
    if not a.failed:
        print("mitigator: no failed BITs — nothing to do (healthy)."); return 0
    if a.apply and not a.token:
        print("REFUSING to --apply without an admin token (set BIT_ADMIN_TOKEN). Dry-run only."); a.apply = False

    flips, escalate = mitigate(a.failed, a.base, a.token, a.apply)
    print(f"=== BIT Mitigator — {'APPLY (live)' if a.apply else 'DRY-RUN plan'} · {a.base} ===")
    for f in flips:
        if f["status"] == "already-safe":
            print(f"  [skip ] {f['flag']} already safe ({f['value']})")
        else:
            tag = "APPLIED" if f.get("applied") else ("WOULD" if not a.apply else "FAILED")
            print(f"  [{tag:7}] {f['bit']:<14} {f['flag']} : {f.get('from')} -> {f['to']}"
                  + (f"  http={f.get('http')}" if a.apply else ""))
    for fid, why in escalate:
        print(f"  [ESCALATE] {fid}: {why}")
    print("  NOTE: mitigation is reversible (run --rollback) and is NEVER the fix. Resolve via the Fix loop.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
