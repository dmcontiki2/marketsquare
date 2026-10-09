#!/usr/bin/env python3
"""apply_trainers_gate.py -- TRAINERS-DOOR-1 (RUL-217(d)): a trainer's police clearance is read and uploaded as the Tutors
clearance credential (category.tutors.clearance), which the stranger gate already accepts (_GATE_CLEARANCE_SIGNALS).
  * bea_main.py /listings/mine: her card's clearance status reads either clearance credential, not only the Services one;
  * ms.js msClearanceUpload: 'Upload my police clearance' picks the clearance credential her advert's category offers.
Idempotent; refuses to apply twice."""
import io, os, shutil, sys, time
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARK = "TRAINERS-GATE-1"
EDITS = {
 "bea_main.py": [(
  '''        _clr = conn.execute("SELECT status FROM user_credentials WHERE LOWER(email) = LOWER(?) AND signal_id = ?",
                            (email, "category.services_cas.clearance")).fetchone()''',
  '''        _clr = conn.execute("SELECT status FROM user_credentials WHERE LOWER(email) = LOWER(?) AND signal_id IN (?, ?) "
                            "ORDER BY CASE status WHEN 'earned' THEN 0 WHEN 'pending' THEN 1 ELSE 2 END LIMIT 1",   # TRAINERS-GATE-1
                            (email, "category.services_cas.clearance", "category.tutors.clearance")).fetchone()''')],
 "ms.js": [(
  "      sel.value = _lic ? 'category.services_tech.coc' : 'category.services_cas.clearance';",
  "      const _tut = !_lic && ![].some.call(sel.options || [], function(o){ return o.value === 'category.services_cas.clearance'; })\n"
  "        && [].some.call(sel.options || [], function(o){ return o.value === 'category.tutors.clearance'; });   // TRAINERS-GATE-1: a trainer's advert is a Tutors advert\n"
  "      sel.value = _lic ? 'category.services_tech.coc' : (_tut ? 'category.tutors.clearance' : 'category.services_cas.clearance');")],
}
def main():
    ts = time.strftime("%Y%m%d-%H%M%S")
    for fn, reps in EDITS.items():
        f = os.path.join(ROOT, fn); s = io.open(f, encoding="utf-8").read()
        if MARK in s: sys.exit("already applied in %s" % fn)
        for a, b in reps:
            if s.count(a) != 1: sys.exit("%s: anchor found %d times" % (fn, s.count(a)))
            s = s.replace(a, b)
        shutil.copyfile(f, f + ".bak-trnGate-%s" % ts)
        io.open(f, "w", encoding="utf-8").write(s)
        print("%s: TRAINERS-GATE-1 applied" % fn)
if __name__ == "__main__":
    main()
