#!/usr/bin/env python3
"""BIT-STORE-FLOOR-1 (26 Sep 2026) -- red on the pre-fix source, green on the fix.

WHAT WAS BROKEN, measured live at 19:36:04Z on 26 Sep 2026. POST /dashboard/bit stored
dict(payload) unconditionally. A caller POSTed an empty body; bit_status.json became
{"received_at": "2026-09-26T19:36:04Z"} and nothing else, and GET /dashboard/bit served
exactly that -- no state, no results, no verdict. It could not even reach the handler's
"no BIT run recorded yet" branch, because the file existed. Two probes 60 s apart both
returned the stub, so it was persistent, not a mid-write.

The board had read 8/8 PASS at 19:02:29Z and an independent edge-vantage run returned
8/8 PASS minutes after the wipe, so the SITE was healthy the whole time. One empty POST
replaced a real verdict with a blank and the dashboard panel read neither green nor red.

This is QA-GATE-BLIND-1's lesson (25 Sep) one store along: there the damage was not the
blind run but accept() writing it over the baseline. Same rule -- a run that measured
nothing is NOT MEASURED, and NOT MEASURED never becomes the record.

WHAT THE FIX MUST NOT DO, asserted below: it must not refuse a real board that is all
FAIL. This floor is about EMPTINESS, never about a bad verdict -- a gate that suppressed
red would be far worse than the fault it replaces.

Run:  python3 scripts/test_bit_store_floor1.py
"""
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FAILS = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (("  -- " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


def store(src_text, payload, existing):
    """Run the handler body's storage logic against a throwaway bit_status.json."""
    tmp = tempfile.mkdtemp(prefix="bitfloor_")
    p = os.path.join(tmp, "bit_status.json")
    if existing is not None:
        io.open(p, "w", encoding="utf-8").write(json.dumps(existing))
    body = src_text
    start = body.index("def dashboard_bit_post(")
    tail = 'raise HTTPException(status_code=400, detail="bad bit payload: "'
    end = body.index(tail, start)
    end = body.index("\n", end) + 1
    fn = body[start:end]
    # strip the decorator's DI signature and the HTTPException dependency
    fn = fn.replace("def dashboard_bit_post(payload: dict = Body(...)):",
                    "def dashboard_bit_post(payload):")
    ns = {"HTTPException": RuntimeError, "__file__": os.path.join(tmp, "x.py")}
    exec(compile(fn, "handler", "exec"), ns)
    res = ns["dashboard_bit_post"](payload)
    got = json.load(io.open(p, encoding="utf-8")) if os.path.exists(p) else None
    return res, got


def main():
    src = io.open(os.path.join(REPO, "bea_main.py"), encoding="utf-8").read()
    print("BIT-STORE-FLOOR-1")
    print("source shape:")
    check("the store has a measured/not-measured floor", "BIT-STORE-FLOOR-1" in src)
    check("a blind post is recorded, not silent", "last_blind_post" in src)

    REAL = {"state": "pass", "worst": 0, "pass": 8, "total": 8, "failing": [],
            "results": [{"id": "B-BEA-HEALTH", "state": "PASS"}], "ran_at": "2026-09-26T19:02:29Z"}

    if FAILS:
        print("\nPRE-FIX SOURCE -- the damage, reproduced on this very file:")
        res, got = store(src, {}, REAL)
        print("    POST {} over a real 8/8 board ->", res)
        print("    bit_status.json is now:", json.dumps(got))
        print("    GET /dashboard/bit would serve that: no state, no results, no verdict,")
        print("    over a site that was healthy throughout. The verdict is gone.")
        print("\nRED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1

    print("behaviour:")
    res, got = store(src, {}, REAL)
    check("an empty post does NOT overwrite a real board",
          got.get("state") == "pass" and len(got.get("results") or []) == 1,
          "board became %s" % json.dumps(got)[:120])
    check("the caller is told it was not stored", res.get("stored") is False and "reason" in res)
    check("the caller is NOT errored (a runner that cannot post is a second failure)",
          res.get("ok") is True)
    check("the blindness is visible in the surviving board",
          isinstance(got.get("last_blind_post"), dict) and "NOT MEASURED" in
          got["last_blind_post"].get("reason", ""))

    # a real board still overwrites -- including an all-FAIL one. This is the important half.
    RED = {"state": "fail", "worst": 1, "pass": 0, "total": 8,
           "failing": ["B-BEA-HEALTH"], "results": [{"id": "B-BEA-HEALTH", "state": "FAIL"}]}
    res2, got2 = store(src, RED, REAL)
    check("an ALL-FAIL board still overwrites (the floor never suppresses red)",
          res2.get("stored") is True and got2.get("state") == "fail"
          and got2.get("failing") == ["B-BEA-HEALTH"])

    res3, got3 = store(src, REAL, None)
    check("a real board stores normally on a fresh box", res3.get("stored") is True
          and got3.get("state") == "pass")

    res4, got4 = store(src, {}, None)
    check("an empty post with nothing to keep records not_measured, not a fake pass",
          got4.get("state") == "not_measured" and res4.get("stored") is False)

    print("")
    if FAILS:
        print("RED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("GREEN: an empty board never replaces a real verdict; an all-FAIL board still does.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
