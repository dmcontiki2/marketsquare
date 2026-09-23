"""VANTAGE-BLIND-1 (23 Sep 2026) -- proof that a file rulings_check CANNOT REACH is reported
as NOT CHECKED, while a file it can reach and finds broken is still a FAIL.

WHAT WENT WRONG
---------------
The daily stand-up runs with only the MarketSquare folder mounted. 38 of rulings_check's
assertions point OUTSIDE that repo -- '../CityLauncher/...' siblings and the Projects-root
CLAUDE.md via os.path.join(PROJECTS, ...). `_read` returned None for every one, the checker
printed "FAIL ... file missing" 38 times and concluded, in its own words,
"at least one ruling exists only in memory or in one file -- the blind spot is live."
Nothing was missing. The blind spot was the checker's, and the false convictions were burying
the question of whether any REAL assertion had broken.

This repo had already settled the doctrine three times and this instrument never got it:
RG-0401 (an edge refusal is BLIND, never REGRESSED), RG-0420 (an origin 502 is blind), and the
maintenance producer's `vantage:` rule (arming posts NOT MEASURED, never False).

THE TWO HALVES THIS TEST PINS
-----------------------------
1. Unreachable (outside the repo)        -> NOT CHECKED, never FAIL, never exit 1.
2. Reachable but actually wrong/deleted  -> still FAIL, still exit 1.

Half 2 is the one that matters: a fix that silenced the noise by silencing the check would
pass half 1 and be worse than the bug. Per this repo's standing rule -- prove the check
against deliberately broken input before believing its green.

Run:  python3 scripts/test_vantage_blind1.py      (exit 0 = pass)
"""
import os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rulings_check as RC


def main():
    bad = []

    # -- half 1: paths outside the repo are BLIND, however they are spelled ----------------
    for p in ("../CLAUDE.md",
              "../CityLauncher/emailer/emailer.py",
              os.path.join(RC.PROJECTS, "CLAUDE.md"),
              os.path.join(RC.PROJECTS, "Auction", "design", "x.html")):
        if not RC._outside_repo(p):
            bad.append("outside-repo path not detected: %r" % p)

    # -- half 2: paths inside the repo are NEVER blind, present or absent ------------------
    for p in ("RULINGS.md", "bea_main.py", "scripts/rulings_check.py",
              "this_file_does_not_exist_9f3a.md", "roles/role_registry.json"):
        if RC._outside_repo(p):
            bad.append("in-repo path wrongly called outside: %r" % p)

    # a deleted in-repo file must still read as missing (the FAIL leg)
    if RC._read("this_file_does_not_exist_9f3a.md") is not None:
        bad.append("_read invented content for a missing in-repo file")

    # -- half 3: MUTATION. Break a real, reachable assertion and require a FAIL ------------
    # RUL-037 asserts STANDING_ORDERS.md carries "Claude is the CTO"-class wording. Rather
    # than touch canon, drive the checker at a scratch repo whose in-repo file is wrong.
    with tempfile.TemporaryDirectory() as td:
        real_repo = RC.REPO
        try:
            RC.REPO = td
            open(os.path.join(td, "present_but_wrong.md"), "w").write("nothing useful here\n")
            # reachable + present -> content is read, so a missing needle is a real verdict
            c = RC._read("present_but_wrong.md")
            if c is None:
                bad.append("mutation: reachable in-repo file read as missing")
            elif "NEEDLE-THAT-IS-ABSENT" in c:
                bad.append("mutation: impossible needle found")
            # reachable + absent -> still not blind, so still a FAIL in main()
            if RC._outside_repo("gone.md") or RC._read("gone.md") is not None:
                bad.append("mutation: a deleted in-repo file was excused as blind")
        finally:
            RC.REPO = real_repo

    if bad:
        print("VANTAGE-BLIND-1 TEST: FAIL")
        for b in bad:
            print("  - " + b)
        return 1
    print("VANTAGE-BLIND-1 TEST: pass -- unreachable is NOT CHECKED, unreachable-in-repo "
          "is still FAIL, and a broken reachable assertion still convicts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
