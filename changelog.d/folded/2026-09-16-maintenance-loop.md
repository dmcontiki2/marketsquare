## 2026-09-16 — maintenance-loop: quiet run, ledger green both sides, one ledger wording fix

- Regression ledger BEFORE (3 shards + combine): every locked fix holding, 22 known defects still open, exit 0.
- Shadow maintenance agent (foreground, MS_BEA_URL=https://trustsquare.co): mode SHADOW, brain KEYED:anthropic, 0 faults seen / 0 acted. Report .maint_agent/run_20260916T053653Z.json. Heartbeat PROBED on GET /dashboard/maint: run=2026-09-16T05:36:53Z (answers 200 anonymously — the cookie workaround is no longer needed).
- Fault queue PROBED via /admin/faults: new 0 · fix-shipped 0 · verified 26. Nothing to apply, nothing to verify.
- Email lane census: 24 total, 6 held in 30d (legal 1, other 5, spam 1, support 7) — counts only, not a fix lane.
- Escalation brief: no escalations in the last 24h, no brief written.
- Regression ledger AFTER: green, exit 0, 22 open.
- LEDGER-WORDING-1: RG-0308 (LOCKED 7 Sep) still printed "READY TO LOCK" in its passing info line — a leftover from its OPEN days that reads as a promotion request. Wording changed to "holding"; assertion logic untouched; py_compile ok; entry re-evaluated in isolation and passes. Backup: scripts/regression_ledger.py.bak-<ts>.
- No push, no deploy (NIGHTLY-SHIP-1 carries it).
