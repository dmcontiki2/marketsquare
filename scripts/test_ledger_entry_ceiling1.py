"""LEDGER-ENTRY-CEILING-1 (24 Sep 2026) -- proof that ONE over-cap entry cannot wedge the
chunked board, and that being cut by the clock reads BLIND, never green.

WHAT WENT WRONG
---------------
LEDGER-CHUNK-1 (23 Sep 2026) split the board by TIME instead of by count, checkpointing after
every entry so the board survives any aggregate weight. It survives aggregate weight. It does
not survive ONE entry heavier than the whole cap.

On 24 Sep the daily stand-up's board stopped dead:

    call 1 -> next=24/449
    call 2 -> next=24/449
    call 3 -> next=24/449

Entry 24 is RG-0025 (eleven live map-page reads plus a manifest-wide regex scan). Every call
spent its whole ~180s inside that one check, the checkpoint after it was never reached, and the
board became permanently unrunnable from the stand-up's vantage -- silently, because a killed
command prints nothing. An instrument that cannot be run at all is worse than one that runs
slowly: nobody sees it stop.

THE FIRST CUT OF THE FIX WAS WRONG AND THIS TEST PINS WHY
---------------------------------------------------------
It raised ProbeOffline from the SIGALRM handler. RG-0025 wraps each page read in
`except Exception` -- so it swallowed the cut as one more FAIL line and carried on to the next
page, and the board stayed wedged at 24. The ceiling therefore raises a BaseException subclass,
which no entry's `except Exception` can absorb, and converts it to ProbeOffline outside the
check's own frame.

THE THREE HALVES THIS TEST PINS
-------------------------------
1. An entry that exceeds its ceiling is CUT (the board advances past it).
2. The cut cannot be swallowed by a check that catches Exception -- the exact shape of RG-0025.
3. A cut entry reads UNVERIFIED / NOT EVALUATED, never PASS. Half 3 is the one that matters: a
   ceiling that turned slow checks green would be far worse than the wedge it fixes.

Run:  python3 scripts/test_ledger_entry_ceiling1.py      (exit 0 = pass)
"""
import importlib.util, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("rl", os.path.join(HERE, "regression_ledger.py"))
rl = importlib.util.module_from_spec(spec)
sys.argv = ["regression_ledger.py", "--no-bootstrap"]
spec.loader.exec_module(rl)

fails = []

if not hasattr(rl, "_call_capped"):
    print("FAIL: _call_capped() is gone -- the chunked board can wedge on one entry again")
    sys.exit(1)

if not hasattr(os, "fork"):        # SIGALRM is POSIX; the host lane runs uncapped by design
    print("SKIP: no SIGALRM on this platform -- the ceiling is a sandbox affordance")
    sys.exit(0)

# --- Half 1 + 2: a check shaped exactly like RG-0025 must still be cut -------------------
def greedy_like_rg0025():
    out = []
    for _ in range(11):
        try:
            time.sleep(2)          # stands in for a live page read
        except Exception as ex:    # RG-0025's shape: it catches its own transport errors
            out.append((rl.FAIL, "unreachable: %r" % (ex,)))
            continue
    return out

t0 = time.time()
try:
    greedy_like_rg0025.__name__
    rl._call_capped(greedy_like_rg0025, 3)
    fails.append("a 22s check ran to completion under a 3s ceiling -- it was never cut")
except rl.ProbeOffline as ex:
    took = time.time() - t0
    if took > 8:
        fails.append("the cut took %.1fs under a 3s ceiling -- it was swallowed by the "
                     "check's own `except Exception` and only landed on a later pass" % took)
    if "ceiling" not in str(ex):
        fails.append("the cut does not name itself as a ceiling -- the blind reason is unreadable")
except BaseException as ex:
    fails.append("the ceiling escaped as %r instead of ProbeOffline -- callers cannot handle it"
                 % (ex,))

# --- Half 3: a cut entry must read UNVERIFIED, never PASS --------------------------------
entry = {"id": "RG-TEST", "title": "t", "state": "LOCKED", "fixed_on": "2026-01-01",
         "scope": "s", "ref": "r", "fn": greedy_like_rg0025}
v = rl._judge(entry, ceiling_s=2)
if v.get("status") == "HOLDING":
    fails.append("a cut entry reads HOLDING -- running out of clock now counts as passing, "
                 "which is worse than the wedge this fixes")
if v.get("status") != "UNVERIFIED":
    fails.append("a cut entry reads %r, not UNVERIFIED" % v.get("status"))
if v.get("fails"):
    fails.append("a cut entry produced FAILs -- a check that was never allowed to finish must "
                 "not convict (RG-0187)")

# --- No ceiling must behave exactly as before -------------------------------------------
def quick():
    return [(rl.INFO, "fine")]
if rl._call_capped(quick, None) != [(rl.INFO, "fine")]:
    fails.append("ceiling_s=None changed behaviour -- the uncapped host full run is not intact")

if fails:
    print("FAIL (%d):" % len(fails))
    for f in fails:
        print("  - " + f)
    sys.exit(1)
print("LEDGER-ENTRY-CEILING-1 OK: an over-cap entry is cut even when it catches Exception, "
      "reads UNVERIFIED not HOLDING, and an uncapped run is unchanged.")
