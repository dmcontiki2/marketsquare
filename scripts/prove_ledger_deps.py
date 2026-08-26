#!/usr/bin/env python3
"""prove_ledger_deps.py — LEDGER-DEPS-1 (26 Aug 2026).

WHY THIS HARNESS EXISTS
-----------------------
On the morning of 26 Aug 2026 the maintenance loop's opening ledger run printed:

    [ !!!! ] RG-0181  The affiliate lane is a SERVER-SIDE link-out that fails closed
             REGRESSION: the lane's own selftest FAILS -- its refusals no longer refuse:
             ModuleNotFoundError: No module named 'fastapi'
    [ !!!! ] RG-0182  The indicative-fare lane is CACHE-ONLY ...
             REGRESSION: the dark/lit harness FAILS: ... No module named 'fastapi'

    RESULT: 5 previously-fixed issue(s) HAVE COME BACK. Do not deploy over this.

Nothing about the app had changed, or could have. The sandbox running the ledger
simply had no `fastapi` installed, so both harnesses died on their import line
having run ZERO assertions. `pip install fastapi` turned them into 9/9 and 13/13.

That is the cry-wolf failure this whole file exists to prevent, and it is the
THIRD instance of one shape: the instrument reporting itself as the app.
  * LEDGER-OFFLINE-1 (7 Aug)  -- no network      -> UNVERIFIED, not REGRESSION
  * GATE-CACHE-1     (14 Aug) -- 429 credential  -> UNVERIFIED, not REGRESSION
  * LEDGER-DEPS-1    (26 Aug) -- missing module  -> UNVERIFIED, not REGRESSION

A false red is worse than no answer: it invites the next session to "fix" what is
not broken, and it blocks a deploy for nothing.

THE NARROWNESS IS THE POINT
The demotion applies ONLY to third-party modules. If the missing module is one of
OUR OWN repo files, the fix really has been deleted and the entry MUST stay red.
A demotion that swallowed that would be a silent green -- the quiet failure the
ledger preamble calls the worse one. Test 6 below is the guard on exactly that.

Run:  python3 scripts/prove_ledger_deps.py      (exit 0 = proven)
Stdlib only. Ledger RG-0185.
"""
import importlib.util
import os
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER_PY = os.path.join(REPO, "scripts", "regression_ledger.py")


def load_ledger():
    spec = importlib.util.spec_from_file_location("_led_under_test", LEDGER_PY)
    m = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["regression_ledger.py"]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    return m


def main():
    if not os.path.exists(LEDGER_PY):
        print("scripts/regression_ledger.py is GONE")
        return 1
    L = load_ledger()

    for needed in ("_harness", "_missing_third_party"):
        if not hasattr(L, needed):
            print("  [FAIL] the ledger lost %s() -- LEDGER-DEPS-1 has been removed, and a "
                  "sandbox without a dependency will cry REGRESSION again" % needed)
            return 1

    fails = []

    def check(label, cond):
        print(("  [OK] " if cond else "  [FAIL] ") + label)
        if not cond:
            fails.append(label)

    print("LEDGER-DEPS-1 -- a missing dependency reads BLIND, never RED\n")
    d = tempfile.mkdtemp(prefix="ledgerdeps-")
    try:
        print("A MISSING THIRD-PARTY MODULE IS AN INSTRUMENT LIMIT")
        p = os.path.join(d, "a.py")
        open(p, "w").write("import definitely_not_a_real_pkg_xyz\n")
        ok, blind, det = L._harness([sys.executable, p])
        check("a harness killed by a missing third-party import reads BLIND",
              (not ok) and blind)
        check("the message says NOT EVALUATED, which run() demotes to UNVERIFIED",
              "NOT EVALUATED" in det)
        check("the message names the missing module, so it is actionable",
              "definitely_not_a_real_pkg_xyz" in det)

        print("\nBUT A REAL FAILURE MUST STILL BE RED")
        p = os.path.join(d, "b.py")
        open(p, "w").write("print('refusal no longer refuses')\nraise SystemExit(1)\n")
        ok, blind, det = L._harness([sys.executable, p])
        check("a genuine assertion failure stays RED", (not ok) and (not blind))
        check("its real output survives into the report", "refusal no longer refuses" in det)

        print("\nAND A DELETED REPO MODULE IS A DELETION, NOT A DEPENDENCY")
        ours = None
        for fn in sorted(os.listdir(REPO)):
            if fn.endswith(".py") and fn[:-3].isidentifier():
                ours = fn[:-3]
                break
        if ours is None:
            check("could not find any repo module to test the narrowing with", False)
        else:
            p = os.path.join(d, "c.py")
            open(p, "w").write("import %s\n" % ours)
            ok, blind, det = L._harness([sys.executable, p], cwd=d)
            check("a missing OUR-OWN module (%s) stays RED -- a deleted fix cannot hide as "
                  "'unverified'" % ours, (not ok) and (not blind))
            check("_missing_third_party() refuses to demote a repo module",
                  L._missing_third_party(
                      "ModuleNotFoundError: No module named '%s'" % ours) is None)

        print("\nTHE CLASSIFIER IS NOT TRIGGER-HAPPY")
        check("a third-party name is recognised",
              L._missing_third_party(
                  "ModuleNotFoundError: No module named 'fastapi'") == "fastapi")
        check("unrelated failure text is never demoted",
              L._missing_third_party("AssertionError: the refusal failed") is None)

        print("\nA PASSING HARNESS IS STILL A PASS")
        p = os.path.join(d, "e.py")
        open(p, "w").write("print('13/13 passed')\n")
        ok, blind, det = L._harness([sys.executable, p])
        check("a passing harness reports ok and keeps its stdout",
              ok and (not blind) and "13/13" in det)

        total = 10
        print("\n%d/%d passed" % (total - len(fails), total))
        return 1 if fails else 0
    finally:
        shutil.rmtree(d, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
