#!/usr/bin/env python3
"""apply_i18n_cost_rail.py -- I18N-COST-RAIL-1 (DW-142, 23 Sep 2026). One-shot, idempotent.

The Translate button's AI call (bea_main.py i18n_translate -> _i18n_ask) had its own 400/day
call cap but sat OUTSIDE the platform rail: no _check_cost_ceiling (the $100 ceiling could not
stop it) and no _log_ai_spend (its tokens were invisible on the spend dashboard). The cost sweep
graded it CRITICAL on 23 Sep. This script wraps it exactly the way every other call is wrapped.

WHY A SCRIPT AND NOT AN EDIT: bea_main.py was under a WORK-LOCK-1 lock (RUL-140) held by the
lang-quick session when the fix was written. The watch lane is the one RUL-140 was written about,
so it does not edit a locked file. This script REFUSES while any lock covers bea_main.py, and
applies the moment it clears -- run by whichever session gets there first.

Behaviour of the patched code:
  * _i18n_ask calls _check_cost_ceiling("") before every AI call. Over the ceiling it raises
    HTTP 429, which the endpoint's existing try/except catches -- the reader simply gets the
    cached lines and English for the rest. The Translate button degrades; it never errors.
  * after each call it logs the real tokens on the lane that actually answered
    (provider/model from AIResult), like /planner/heritage/compose. _log_ai_spend never raises.
  * the 400/day I18N_DAILY_CALL_CAP stays exactly as it is.

Proof before write: the patched text must py_compile AND the cost sweep's own
wrapper_compliance() must grade i18n_translate + _i18n_ask with no CRITICAL/WARN.

  python3 scripts/apply_i18n_cost_rail.py           # apply (refuses while locked)
  python3 scripts/apply_i18n_cost_rail.py --check   # prove on a copy, change nothing
Exit: 0 applied or already applied · 3 locked · 1 anchor/proof failed (nothing written).
"""
import os, py_compile, shutil, subprocess, sys, tempfile, time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
BEA = HERE / "bea_main.py"
MARK = "I18N-COST-RAIL-1"
CHECK = "--check" in sys.argv

A_OLD = '''        import ai_provider
        calls[0] += 1
        res = ai_provider.complete([{"role": "user", "content": _i18n_prompt(lang, items)}],
                                   task=I18N_TASK, max_tokens=1600, timeout=40)
        lines = {}
'''
A_NEW = '''        import ai_provider
        # I18N-COST-RAIL-1 (DW-142, 23 Sep 2026): inside the platform rail like every other
        # AI call. Over the ceiling this raises 429; the caller's try/except catches it and the
        # reader gets cache + English, never an error. The 400/day cap above still applies.
        _check_cost_ceiling("")
        calls[0] += 1
        res = ai_provider.complete([{"role": "user", "content": _i18n_prompt(lang, items)}],
                                   task=I18N_TASK, max_tokens=1600, timeout=40)
        _log_ai_spend("", "/i18n/translate", I18N_TASK, res.in_tokens, res.out_tokens,
                      provider=res.provider, model=res.model)
        lines = {}
'''


def locked():
    r = subprocess.run([sys.executable, str(HERE / "scripts" / "work_lock.py"), "check", "bea_main.py"],
                       cwd=HERE, capture_output=True, text=True)
    return r.returncode == 3, (r.stdout or r.stderr).strip()


def sweep_grade(text):
    """Run the sweep's own wrapper_compliance() over a temp tree holding the patched file."""
    sys.path.insert(0, str(HERE / "scripts"))
    import cost_compliance_sweep as ccs
    root = Path(tempfile.mkdtemp(prefix="i18nrail-"))
    try:
        (root / ccs.MAIN_REPO).mkdir(parents=True)
        (root / ccs.MAIN_REPO / "bea_main.py").write_text(text, encoding="utf-8")
        found = ccs.wrapper_compliance(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)
    return [(lvl, msg) for lvl, msg in found if "i18n" in msg]


def main():
    src = BEA.read_text(encoding="utf-8")
    if MARK in src:
        print("already applied (%s present in bea_main.py)" % MARK); return 0
    if src.count(A_OLD) != 1:
        print("REFUSED: anchor found %d times (expected 1) -- the helper changed; re-derive the patch"
              % src.count(A_OLD)); return 1
    new = src.replace(A_OLD, A_NEW)
    tmp = Path(tempfile.mkdtemp()) / "bea_main.py"
    tmp.write_text(new, encoding="utf-8")
    py_compile.compile(str(tmp), doraise=True)
    grades = sweep_grade(new)
    for lvl, msg in grades:
        print("sweep:", lvl, msg)
    bad = [g for g in grades if "OK" not in str(g[0]) and "✅" not in str(g[0])]
    if not grades or bad:
        print("REFUSED: the sweep does not grade the patched call clean -- nothing written"); return 1
    if CHECK:
        print("CHECK ok: patch compiles and the sweep grades it clean; nothing written"); return 0
    is_locked, why = locked()
    if is_locked:
        print("LOCKED -- not applied. %s" % why); return 3
    bak = BEA.with_name("bea_main.py.bak-i18nrail-%s" % time.strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(BEA, bak)
    BEA.write_text(new, encoding="utf-8")
    back = BEA.read_text(encoding="utf-8")
    if back != new:
        shutil.copy2(bak, BEA)
        print("WRITE DID NOT LAND INTACT -- restored from %s" % bak.name); return 1
    py_compile.compile(str(BEA), doraise=True)
    print("APPLIED %s -- backup %s; now commit and ship through the one deploy lane" % (MARK, bak.name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
