## 2026-09-13 — maintenance-loop (daily B2b run)

- **Fact board, before and after:** regression ledger run in three shards plus `--combine=3`,
  both ends of the session. Both runs: **every locked fix is holding, 22 known defects still
  open, exit 0.** No LOCKED entry went red, so the session had no forced top item.
- **Fault queue: empty.** `GET /admin/faults?status=new` = 0 rows. Whole register census:
  40 rows — 26 verified, 12 closed, 2 duplicate. Nothing in a fixable state.
- **Shadow agent ran clean** (`scripts/maintenance_agent.py`, MS_BEA_URL=https://trustsquare.co,
  foreground per BRAIN-DEPS-2): mode SHADOW (kill switch OFF — arming is David's act alone),
  phase postlaunch, brain KEYED:anthropic, **0 seen / 0 acted**. Report:
  `.maint_agent/run_20260913T053717Z.json`. Heartbeat PROBED live at `GET /dashboard/maint`
  — it carries this run's stamp `2026-09-13T05:37:17Z` (received 05:37:39Z), so the
  dashboard's B2b readiness row is fed by today's run, not a stale one.
- **Email lane census (not a fix lane):** 24 rows total; 30d by category legal 1 / other 5 /
  spam 1 / support 7; 30d by status drafted 6 / sent 6 / skipped 1 / system 1; 6 held.
- **Step 2a (BACKUP-UNATTENDED-1): skipped by its own rule.** Newest archive
  `backups/2026-09-12_1553.zip` is 13.7 h old — younger than a day, so a second archive today
  is waste, not safety. The producer was not run; the lane is fresh.
- **Step 2b (WAVE-WITNESS-1): producer run.** `scripts/wave_hygiene_witness.py` re-ran both
  proof suites and rewrote `wave_hygiene_status.json` with their real verdicts —
  intl_pass ok, source_tags ok, suppression ok, stamped 2026-09-13T05:38:34Z, exit 0. RG-0175
  is green on the fact, not on the clock.
- **Escalation brief: none.** `scripts/escalation_brief.py` — no escalations in the last 24 h,
  so no `Records/ESCALATION_BRIEF_2026-09-13.md` was written. Nothing for David to read.
- **No code changed.** No fault reached "gates GREEN, patch ready", so nothing was patched,
  no fault row moved, and no new ledger entry is owed (AIK-VERIFY-1 unaffected — there was
  nothing to verify).
- Instrument note: `GET /health` answers 403 to a bare stdlib `urllib` User-Agent and 200 with
  an ordinary browser UA. The agent, the ledger and this run's probes all set a UA, so nothing
  is broken — but a new probe written with default `urllib` headers will read a false red.
