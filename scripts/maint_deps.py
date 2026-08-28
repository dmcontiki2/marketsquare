#!/usr/bin/env python3
"""MAINT-DEPS-1 (28 Aug 2026) -- one command that gives the daily maintenance lane
every third-party module its instruments need, so the ledger board can be READ rather
than demoted.

Why this exists
---------------
BRAIN-DEPS-2 taught the lane to install `httpx` because the shadow agent dies without
it -- a LOUD failure, so it got fixed. `fastapi` fails QUIETLY: the regression ledger's
harness-backed entries (RG-0181, RG-0182) die at their import line, RG-0187 honestly
demotes them to `[ ???? ] NOT EVALUATED`, and the run ends "that is not a green board".
Nothing is red, so nothing forces the fix, and the same two entries have been blind on
every sandbox run since 26 Aug (DW-071's recorded residual: "fastapi is absent from the
sandbox bootstrap"). A blind instrument that never complains is the worst kind.

CLASS property, not a two-package list: any module the lane's INSTRUMENTS import lives
in REQUIRED below. A new harness that needs a new package adds a line here -- it does
not get to be silently blind for a fortnight first.

Usage (idempotent, safe to run every session, ~1 s warm):
    python3 scripts/maint_deps.py            # install what is missing, report
    python3 scripts/maint_deps.py --check    # report only, exit 1 if anything missing

Exit 0 = every instrument can run. Exit 1 = something is still missing (named).
"""
import importlib.util
import subprocess
import sys

# module name -> (pip name, what goes BLIND without it)
REQUIRED = {
    "httpx":   ("httpx",   "scripts/maintenance_agent.py -- the shadow agent cannot run at all"),
    "fastapi": ("fastapi", "regression_ledger RG-0181/RG-0182 harnesses -- demoted to NOT EVALUATED"),
}


def _missing():
    return [m for m in REQUIRED if importlib.util.find_spec(m) is None]


def main(argv):
    check_only = "--check" in argv
    missing = _missing()

    if not missing:
        print("[maint-deps] ok -- every instrument dependency present (%s)"
              % ", ".join(sorted(REQUIRED)))
        return 0

    for m in missing:
        print("[maint-deps] MISSING %s -- blinds: %s" % (m, REQUIRED[m][1]))

    if check_only:
        print("[maint-deps] --check: %d missing, nothing installed" % len(missing))
        return 1

    pkgs = [REQUIRED[m][0] for m in missing]
    cmd = [sys.executable, "-m", "pip", "install", "--break-system-packages", "-q"] + pkgs
    print("[maint-deps] installing: %s" % " ".join(pkgs))
    try:
        subprocess.run(cmd, check=True, timeout=600)
    except Exception as exc:
        print("[maint-deps] FAILED: %r" % (exc,))
        print("[maint-deps] the lane is BLIND on: %s" % ", ".join(missing))
        return 1

    still = _missing()
    if still:
        print("[maint-deps] FAILED -- still missing after install: %s" % ", ".join(still))
        return 1
    print("[maint-deps] ok -- installed %s; every instrument dependency present"
          % ", ".join(pkgs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
