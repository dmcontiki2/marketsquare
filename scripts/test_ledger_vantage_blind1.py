"""LEDGER-VANTAGE-BLIND-1 (23 Sep 2026) -- proof that a SIBLING PROJECT this machine cannot
see is reported BLIND, while a sibling it CAN see and finds broken is still a REGRESSION.

WHAT WENT WRONG
---------------
The 23 Sep 19:00Z stand-up ran the full board from a session with ONLY the MarketSquare folder
mounted. It printed:

    RESULT: 4 previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.

and the four were RG-0229, RG-0230, RG-0252 and RG-0399 -- every one of them asserting on
'../CityLauncher/...' files or the Projects-root CLAUDE.md:

    verify_optout_lane.py is GONE -- the opt-out lane has no proof
    CityLauncher/ssh_bootstrap.py is GONE -- the python lane lost its self-heal
    Projects/CLAUDE.md lost the SSH-BOOTSTRAP-1 section
    ../CityLauncher/deploy_citylauncher.bat lost 'if not defined UNATTENDED pause'
    CityLauncher/WAVE_RUNS_ON_SERVER is missing ... the laptop bat would send again at 00:10

Nothing was missing. All of it is on David's machine. The instrument could not see the project
and read its own blindness as four rotted fixes -- carrying "Do not deploy over this" with it.

A false RED costs the same trust as a false green, and this one blocks deploys.

THE DOCTRINE WAS ALREADY IN THIS FILE, FIVE TIMES, AND THESE FOUR NEVER INHERITED IT
------------------------------------------------------------------------------------
RG-0187  an instrument that cannot RUN reads UNVERIFIED, never REGRESSION
RG-0401  an edge refusal is BLIND, never REGRESSED           (EDGE-BLIND-1/2)
RG-0420  an origin 502 makes a leg blind                     (UPSTREAM-BLIND-1)
RG-0423  a torn read is not four guards vanishing at once    (SELFREAD-DIAG-1)
VANTAGE-BLIND-1  the same fix for scripts/rulings_check.py, shipped earlier the SAME DAY

THE TWO HALVES THIS TEST PINS
-----------------------------
1. Project not mounted   -> INFO / NOT EVALUATED, never FAIL.
2. Project mounted, file genuinely gone -> still FAIL.

Half 2 is the one that matters. A fix that silenced the noise by silencing the check would
pass half 1 and be strictly worse than the bug: it would hand back a green board on a laptop
that really was about to double-send the 00:10 wave. The test therefore DELETES a file inside
a visible sibling and requires the conviction to survive.

Run:  python3 scripts/test_ledger_vantage_blind1.py      (exit 0 = pass)
"""
import os, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.argv = ["regression_ledger.py", "--no-bootstrap"]
import regression_ledger as R


def _mk(path, body=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(body)


def _fails(out):
    return [m for lvl, m in out if lvl == R.FAIL]


def _infos(out):
    return [m for lvl, m in out if lvl == R.INFO]


def main():
    bad = []

    # The helper may be absent (pre-fix code). That is itself a problem, but the test does NOT
    # stop there: the entry-level halves below are what actually prove the behaviour, and they
    # must run against old code too or this file only ever proves a name exists.
    have = hasattr(R, "sibling_visible")
    if not have:
        bad.append("regression_ledger has no sibling_visible() -- LEDGER-VANTAGE-BLIND-1 is not "
                   "in this file")
        R.sibling_visible = lambda p: True          # old behaviour: everything looks checkable
        R.projects_root_visible = lambda: os.path.isdir(os.path.join(R.REPO, ".."))

    real_repo = R.REPO
    try:
        # ============ vantage A: MarketSquare alone (the stand-up's real mount) ============
        with tempfile.TemporaryDirectory() as td:
            repo = os.path.join(td, "mnt", "MarketSquare")
            os.makedirs(repo)
            R.REPO = repo

            if have and R.projects_root_visible():
                bad.append("A: projects_root_visible() true with no sibling project on disk -- "
                           "the mere existence of a parent directory is being read as evidence")
            for p in (os.path.join(repo, "..", "CityLauncher", "ssh_bootstrap.py"),
                      os.path.join(repo, "..", "CityLauncher", "verify_optout_lane.py"),
                      os.path.join(repo, "..", "CLAUDE.md")):
                if have and R.sibling_visible(p):
                    bad.append("A: unmounted sibling reported visible: %s" % p)
            # in-repo paths are NEVER blind -- present or absent
            for p in ("bea_main.py", "scripts/regression_ledger.py", "no_such_file_9f3a.md"):
                if have and not R.sibling_visible(os.path.join(repo, p)):
                    bad.append("A: in-repo path wrongly called blind: %s" % p)

            # the real entry, on the real blind vantage
            _mk(os.path.join(repo, "load_sandbox_ssh.sh"), "#!/bin/sh\n")
            _mk(os.path.join(repo, "ssh_hetzner_key"), "key\n")
            out = R.rg_sandbox_ssh_selfheal()
            for m in _fails(out):
                if "ssh_bootstrap.py" in m or "CLAUDE.md" in m:
                    bad.append("A: REGRESSION convicted on an unreadable sibling: %s" % m[:90])
            if not any("NOT EVALUATED" in m for m in _infos(out)):
                bad.append("A: the blind read was silent -- a skipped assertion must SAY it was "
                           "skipped, or a green board hides it")

        # ============ vantage B: the whole Projects folder, file really deleted ============
        with tempfile.TemporaryDirectory() as td:
            proj = os.path.join(td, "Projects")
            repo = os.path.join(proj, "MarketSquare")
            os.makedirs(repo)
            os.makedirs(os.path.join(proj, "CityLauncher"))   # project visible...
            R.REPO = repo

            if have and not R.projects_root_visible():
                bad.append("B: a mounted Projects folder was not recognised")
            # ...but ssh_bootstrap.py deliberately NOT created, and CLAUDE.md lacks the needle
            _mk(os.path.join(proj, "CLAUDE.md"), "# notes\nnothing about the ssh lane here\n")
            for p in (os.path.join(proj, "CityLauncher", "ssh_bootstrap.py"),
                      os.path.join(proj, "CLAUDE.md")):
                if have and not R.sibling_visible(p):
                    bad.append("B: a REACHABLE sibling was called blind -- the fix is hiding real "
                               "faults, which is worse than the bug: %s" % p)

            _mk(os.path.join(repo, "load_sandbox_ssh.sh"), "#!/bin/sh\n")
            _mk(os.path.join(repo, "ssh_hetzner_key"), "key\n")
            out = R.rg_sandbox_ssh_selfheal()
            got = " | ".join(_fails(out))
            if "ssh_bootstrap.py is GONE" not in got:
                bad.append("B: a genuinely DELETED ssh_bootstrap.py no longer FAILs -- the "
                           "assertion was weakened, not made honest. got: %s" % got[:140])
            if "CLAUDE.md lost the SSH-BOOTSTRAP-1" not in got:
                bad.append("B: a readable CLAUDE.md missing its section no longer FAILs. "
                           "got: %s" % got[:140])
    finally:
        R.REPO = real_repo

    if bad:
        print("LEDGER-VANTAGE-BLIND-1: %d problem(s)" % len(bad))
        for b in bad:
            print("  FAIL  " + b)
        return 1
    print("LEDGER-VANTAGE-BLIND-1 ok -- an unmounted sibling reads NOT EVALUATED and says so; a "
          "mounted sibling with a genuinely missing file still REGRESSES")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
