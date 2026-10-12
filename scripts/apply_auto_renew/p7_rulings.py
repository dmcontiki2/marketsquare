#!/usr/bin/env python3
"""AUTO-RENEW-1 patch 7/8 -- scripts/rulings_check.py: RUL-224 is asserted where the next session will read."""
import os, py_compile
from patchlib import load, save, rep, root

R = root()
P = os.path.join(R, "scripts", "rulings_check.py")
s, crlf, orig = load(P)
if '"RUL-224"' in s:
    print("rulings_check.py already asserts RUL-224 -- skipped")
    raise SystemExit(0)
s = rep(s, 'REFLECTIONS = {\n', '''REFLECTIONS = {
 "RUL-224": [
   # AUTO-RENEW-1 (built 12 Oct 2026): a paid plan renews automatically as the standard; one tick box makes it
   # month-by-month. Built behind launch_switches.auto_renew, which ships OFF and is David's to arm.
   ("RULINGS.md", ["A PAID PLAN RENEWS AUTOMATICALLY AS THE STANDARD"], []),
   ("PRICING_CANON.md", ["RUL-224"], []),
   ("AUTO_RENEW_BRIEF.md", ["RUL-224"], []),
   ("bea_main.py", ["AUTO-RENEW-1 (RUL-224", 'return _bit_flag("auto_renew", False)',
                    "ALTER TABLE launch_switches ADD COLUMN auto_renew INTEGER NOT NULL DEFAULT 0",
                    '@app.post("/payment/seller-subscription/cancel")', "def _auto_renew_webhook("],
                   ["ADD COLUMN auto_renew INTEGER NOT NULL DEFAULT 1", "/transaction/charge_authorization"]),
   ("payments.py", ["AUTO-RENEW-1 (RUL-224", 'payload["plan"] = plan'], ["/transaction/charge_authorization"]),
   ("ms.js", ["AUTO-RENEW-1 (RUL-224", "Renew automatically each month", "Automatic renewal needs a card payment",
              "Cancel renewal"], []),
   ("route_policy.json", ['"POST /payment/seller-subscription/cancel"'], []),
   ("dashboard.server.html", ["ls_m_autorenew:'auto_renew'"], []),
   ("scripts/regression_ledger.py", ['@entry("RG-0964", "AUTO-RENEW-1 (RUL-224'], []),
 ],
''')
save(P, s, crlf, orig)
py_compile.compile(P, doraise=True)
print("rulings_check.py OK (py_compile)")
