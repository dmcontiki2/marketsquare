## 2026-08-17 — maintenance-loop: quiet run, ledger green, RG-0098 info tidied

- Pre-run regression ledger: GREEN (every locked fix holding; RG-0075 and RG-0090 remain
  the two known open defects, unchanged).
- Shadow maintenance agent ran foreground (run 2026-08-17T05:32:59Z, brain KEYED anthropic,
  SHADOW mode): fault queue 0 seen / 0 acted — nothing new, nothing fix-shipped awaiting
  verification (queue totals: 26 verified, 7 closed, 2 duplicate, 0 open). Heartbeat
  confirmed live at /dashboard/maint (this run's timestamp).
- RG-0098 (FX-LIVE-1) found already promoted to LOCKED (fixed_on 2026-08-17) and passing
  live (/api/fx ZAR 16.16 via frankfurter). Its check still printed the stale
  "READY TO LOCK" info string from its OPEN days — misleading for any session reading the
  run. Tidied the info string only (no assertion touched):
  scripts/regression_ledger.py, .bak beside it, py_compile clean.
- Escalation brief: no escalations in last 24h, no brief written.
- Post-run ledger: GREEN, exit 0.
