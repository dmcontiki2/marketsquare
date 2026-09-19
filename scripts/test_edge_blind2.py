"""EDGE-BLIND-2 (19 Sep 2026) -- proof that an edge refusal is BLIND, never REGRESSED.

RG-0401 is LOCKED: "an edge refusal makes an entry BLIND, never REGRESSED -- the board may
not convict the app of a fault it was never allowed to look at." On the 19 Sep 18:49Z board
RG-0163 printed REGRESSION whose sole fail was
    wave-prep probe unreadable: ProbeOffline('gate credential rate-limited (429 at /review/l
-- the gate 429'd, the payload was never read, and the endpoint was fine. _judge() only
reclassified caught-and-re-emitted ProbeOffline text when _NET["ok"] was False (whole machine
blind); an edge refusal on a reachable site fell straight through to REGRESSION.

Run:  python3 scripts/test_edge_blind2.py      (exit 0 = pass)
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import regression_ledger as R

EDGE = ("wave-prep probe unreadable: ProbeOffline('gate credential rate-limited "
        "(429 at /review/l")
CF = "read failed: ProbeOffline('edge (Cloudflare) refused this client with HTTP 403"
REAL = "/agencies/wave-prep not live (404) -- the AGENCY-LINK-1 deploy has not ridden"


def judge(state, out):
    return R._judge({"id": "RG-TEST", "title": "t", "state": state, "scope": "",
                     "fixed_on": "", "ref": "", "fn": lambda: out})


def main():
    # The site is reachable -- this is the exact condition under which the bug bit.
    R._NET["ok"] = True
    bad = []

    r = judge(R.LOCKED, [(R.FAIL, EDGE)])
    if r["status"] != "UNVERIFIED":
        bad.append("gate-429-only should be UNVERIFIED, got %s" % r["status"])
    if r["fails"]:
        bad.append("gate-429-only should carry no fails, got %r" % (r["fails"],))

    r = judge(R.LOCKED, [(R.FAIL, CF)])
    if r["status"] != "UNVERIFIED":
        bad.append("cloudflare-only should be UNVERIFIED, got %s" % r["status"])

    # A real fault sharing the entry is NOT hidden by the blind one.
    r = judge(R.LOCKED, [(R.FAIL, EDGE), (R.FAIL, REAL)])
    if r["status"] != "REGRESSION":
        bad.append("edge+real should stay REGRESSION, got %s" % r["status"])
    if REAL not in r["fails"]:
        bad.append("edge+real must keep the real fail, got %r" % (r["fails"],))
    if any(EDGE in f for f in r["fails"]):
        bad.append("edge+real must not keep the blind fail as a fail")

    # Unchanged behaviour on both ends of the ladder.
    r = judge(R.LOCKED, [(R.FAIL, REAL)])
    if r["status"] != "REGRESSION":
        bad.append("plain fail should be REGRESSION, got %s" % r["status"])
    r = judge(R.LOCKED, [(R.INFO, "all good")])
    if r["status"] != "HOLDING":
        bad.append("clean LOCKED should be HOLDING, got %s" % r["status"])

    for b in bad:
        print("FAIL:", b)
    print("EDGE-BLIND-2: %s (%d checks)" % ("PASS" if not bad else "FAIL", 6))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
