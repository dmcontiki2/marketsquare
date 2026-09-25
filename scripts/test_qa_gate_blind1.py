#!/usr/bin/env python3
"""test_qa_gate_blind1.py -- QA-GATE-BLIND-1 (25 Sep 2026).

Pins the half that matters: a QA Bot run in which the bot never reached the app must NOT be
graded, must NOT be accepted over the baseline, and must NOT let a release through.

The fault this is red on: on 25 Sep both deploy-gate reports answered 403 to every probe before
the request reached the app (640/640 at 08:07Z, 629/629 at 07:18Z) -- public routes included.
judge() reads 403 as PASS "refused", so a wall in front of the app is indistinguishable from
perfect security: the gate passed, and accept() then wrote that blind run over last.json.
Because regressions() skips any route whose previous verdict was UNPROVEN or PASS, one accepted
blind run disarms the gate for every route until a clean run replaces it.

NOT a weakening: a genuinely locked-down app still PASSes route by route and still gates. Only a
run whose answers are one wall -- or whose public canary never answered -- is refused a verdict.

  python3 scripts/test_qa_gate_blind1.py            # against the current source
  python3 scripts/test_qa_gate_blind1.py <file.py>  # against a copy (use the pre-fix one: must fail)
"""
import importlib.util, os, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "qa_bot", "qa_bot.py")

def load(path):
    state = tempfile.mkdtemp(prefix="qabot-test-")
    os.environ["QA_STATE"] = state            # never touch the real /var/lib state
    spec = importlib.util.spec_from_file_location("qa_bot_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod, state

def run_of(statuses):
    """A finished run whose persona answers are exactly `statuses`."""
    return {"at": "now", "base": "https://example.invalid", "cleanup": {"found": 0, "removed": 0, "ids": []},
            "results": [{"id": "GET /r%d" % i, "class": "session", "verdict": "PASS",
                         "personas": {"stranger": {"status": st, "verdict": "PASS", "detail": ""}}}
                        for i, st in enumerate(statuses)]}

def main():
    fails = []
    def check(name, cond, detail=""):
        print("%-58s %s" % (name, "ok" if cond else "FAIL " + detail))
        if not cond:
            fails.append(name)

    try:
        qb, state = load(TARGET)
    except Exception as e:
        print("could not load %s: %r" % (TARGET, e)); return 1

    for fn in ("blind_run", "not_measured", "choose_vantage"):
        if not hasattr(qb, fn):
            print("%-58s FAIL (absent -- the guard does not exist in this source)" % ("has %s()" % fn))
            fails.append(fn)
    if fails:
        # Show the DAMAGE, not just the absent symbol: drive the pre-fix accept() with the exact
        # run shape of the 25 Sep gate reports and print what it does to the baseline.
        try:
            base = os.path.join(state, "last.json")
            qb.jsave(base, {"GET /real": "PASS"})
            qb.accept(run_of([403] * 640))
            after = qb.jload(base, {})
            verdicts = set(after.values())
            print("\n  proof on this source: a run in which all 640 answers were 403 was accepted;")
            print("  the baseline of 1 real verdict is now %d route(s) holding %s --"
                  % (len(after), sorted(verdicts)))
            print("  regressions() skips any route whose previous verdict is PASS/UNPROVEN, so the")
            print("  gate is now disarmed for every one of them.")
        except Exception as e:
            print("\n  (could not demonstrate the damage: %r)" % (e,))
        print("\nRED: %d check(s) failed -- %s" % (len(fails), TARGET)); return 1

    # 1. the real shape of the 25 Sep reports: every answer 403
    blind, why = qb.blind_run(run_of([403] * 640))
    check("640/640 answering 403 is NOT MEASURED", blind, why)

    # 2. a real mixed board is still measured -- the guard must not swallow ordinary runs
    mixed = [200] * 120 + [403] * 260 + [404] * 140 + [422] * 80 + [401] * 40
    blind_mixed, _ = qb.blind_run(run_of(mixed))
    check("a mixed board is still graded normally", not blind_mixed)

    # 3. a genuinely locked-down app (mostly 401/403 but a real spread) still grades
    locked = [403] * 300 + [401] * 200 + [404] * 60 + [200] * 40
    blind_locked, _ = qb.blind_run(run_of(locked))
    check("a genuinely locked-down app still grades", not blind_locked)

    # 4. a failed canary alone makes the run NOT MEASURED, whatever the spread
    r = run_of(mixed); r["vantage"] = {"ok": False, "detail": "canary GET /health -> 403"}
    nm, why4 = qb.not_measured(r)
    check("a failed public canary alone is NOT MEASURED", nm, why4)

    # 4b. a narrower-but-real door IS a measurement: falling back to the app's own loopback port
    #     must keep grading (and keep releases flowing), while naming what it no longer covers.
    r = run_of(mixed)
    r["vantage"] = {"ok": True, "via": "app loopback (front door refused)", "detail": "",
                    "not_covered": "nginx and the Cloudflare edge"}
    nm2, _ = qb.not_measured(r)
    check("a narrower real door still grades (not blind)", not nm2)

    # 5. THE DAMAGE: a blind run must never be written over the baseline
    base = os.path.join(state, "last.json")
    qb.jsave(base, {"GET /real": "PASS"})
    qb.accept(run_of([403] * 640))
    kept = qb.jload(base, {})
    check("accept() refuses a blind run (baseline survives)", kept == {"GET /real": "PASS"},
          "baseline was overwritten with %r" % (kept,))

    # 6. and a measured run is still accepted -- the guard must not freeze the baseline
    qb.accept(run_of(mixed))
    check("accept() still writes a measured run", qb.jload(base, {}) != {"GET /real": "PASS"})

    print()
    if fails:
        print("RED: %d check(s) failed -- %s" % (len(fails), TARGET)); return 1
    print("GREEN: a run the bot could not see is not a verdict, is not accepted, and does not "
          "certify a release -- %s" % TARGET)
    return 0

if __name__ == "__main__":
    sys.exit(main())
