# Daily-watch fix pass 2026-09-23 — hand-off (WORK-LOCK-1 stand-off)

David asked (23 Sep, ~20:00Z): "please fix these 3 issues — REAL ISSUES" (DW-140, DW-141, DW-142).

## Done and verified
- DW-140 CLOSED — SSH works again. RG-0099 / RG-0427 / RG-0245 ok. Fix was the maintenance loop's
  SANDBOX-EGRESS-1 (`3d770e2`).
- DW-141 CLOSED — backup 2026-09-23_1705.zip restores (users=113). RG-0234 / RG-0350 ok. Fix was
  the maintenance loop's BACKUP-IN-AGENT-1 (`3d770e2`). This pass added BACKUP-ORIGIN-SKIP-1 in
  `scripts/maintenance_agent.py`: the server's own copy of the agent (/opt/marketsquare-src,
  maintenance-agent.timer, next 05:20Z) now skips the backup lane instead of trying to back the
  server up onto itself over ssh. Proven both ways. Reaches the server with the next push/deploy.

## NOT applied — waiting on the lock (next session: do this first)
- DW-142 — `bea_main.py` is locked by `lang-quick-2026-09-23` (taken 19:55Z, expires 07:55Z 24 Sep).
  1. `python3 scripts/work_lock.py check bea_main.py` → must say clear.
  2. `python3 scripts/apply_i18n_cost_rail.py` → expects `APPLIED I18N-COST-RAIL-1` (exit 0).
     It is idempotent, refuses if locked (exit 3) or if the anchor moved (exit 1, nothing written).
  3. Commit, ship through the one deploy lane (`scripts/request_deploy.py`), then
     `cost_compliance_sweep.py` must show `i18n_translate — ceiling ✓ spend-log ✓` → close DW-142.
  4. Add the ledger entry (the ledger file was locked too), suggested text:
     "I18N-COST-RAIL-1: the Translate endpoint's AI call is inside the platform rail —
     `_i18n_ask` calls `_check_cost_ceiling` before and `_log_ai_spend` after every
     `ai_provider.complete`, and the 400/day I18N_DAILY_CALL_CAP stays." LOCKED once live.

## Changelog fragment (changelog.d/ was locked — drop in when clear)
## 2026-09-23 — daily-watch fix pass: DW-140 + DW-141 closed, DW-142 staged
- Verified the maintenance loop's SSH (SANDBOX-EGRESS-1) and backup (BACKUP-IN-AGENT-1) fixes live.
- BACKUP-ORIGIN-SKIP-1: backup lane skips when the agent runs on the origin.
- I18N-COST-RAIL-1 staged as scripts/apply_i18n_cost_rail.py (bea_main.py under RUL-140 lock).
