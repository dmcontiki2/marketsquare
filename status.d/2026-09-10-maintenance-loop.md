### Maintenance loop — 10 Sep 2026 (unattended)

Ledger **green**: 339 entries, 317 holding, **0 regressed**, 22 open. Started the run at 5 regressed.

- Fault queue empty (0 new, 0 acted). Shadow-agent heartbeat posted and read back live at 13:52:46Z.
- Three of the five reds were one event: the PC was off overnight, the 20-minute host agent missed
  558 minutes of ticks, a git `HEAD.lock` sat stranded 544 minutes. The agent resumed at 15:51 SAST
  and cleared it itself. No code change needed.
- **pg-readiness fixed** (PG-PORTABLE-2): 45 no-modifier `datetime('now')` calls in `bea_main.py`
  are now the portable `CURRENT_TIMESTAMP`. Ratchet baseline tightened 49 → 17, never re-baselined
  upward. 17 modifier forms still to convert — tracked in RG-0351, not a blocker.
- **Backup lane fixed at class level**: it had a freshness guard and nothing that made a backup.
  `scripts/backup_db_sandbox.py` now produces one unattended and proves it restores; wired into
  step 2a of the daily run. Fresh archive today: `2026-09-10_1356.zip`, users=71, listings=113.
  It deletes nothing — retention stays David's.
- Seven association pages a tester can land on had no fault-report widget; all seven wired.
- The ack guard was red against correct code (it pinned a spelling); guard fixed, not the code.
- `predeploy_check.py` reaches `verdict=ok` — first clean scan since 2 Sep.

New ledger entries: RG-0350, RG-0351, RG-0352. Committed, not deployed — the 05:45 nightly ships it.
