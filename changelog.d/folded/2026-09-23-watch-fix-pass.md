## 2026-09-23 — daily-watch fix pass: DW-140 + DW-141 closed, DW-142 staged

- Verified the maintenance loop's SSH (SANDBOX-EGRESS-1) and backup (BACKUP-IN-AGENT-1) fixes live.
- BACKUP-ORIGIN-SKIP-1: backup lane skips when the agent runs on the origin.
- I18N-COST-RAIL-1 staged as scripts/apply_i18n_cost_rail.py (bea_main.py under RUL-140 lock) —
  applied and shipped 24 Sep (see 2026-09-24-i18n-cost-rail).
