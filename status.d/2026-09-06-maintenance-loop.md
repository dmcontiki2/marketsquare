## 2026-09-06 — Maintenance loop

- Fault queue EMPTY: 0 new, 26 verified, 12 closed, 2 duplicate (40 total). The 5 rows added
  since yesterday are internal support-form/AI-lane tests, closed the same hour. Shadow agent ran
  05:41:46Z, heartbeat read back from /dashboard/maint at 05:42:06Z. No escalation brief (none due).
- Board GREEN before and after: 292 entries · 273 holding · 0 REGRESSED · 19 open · 0 UNVERIFIED.
  rulings_check 97 rulings, 0 FAIL, 6 WARN (unchanged). Yesterday's RG-0229 false red did not recur.
- No fixes this run, so no fault row moved and no ledger entry added. DW-087 (LOW static findings)
  stays with the Monday deep-scan lane per its own next_action.
- Ledger run via scripts/ledger_resume.py (checkpointed slices) because a full board exceeds the
  sandbox's per-call cap. Nightly TSL 05:45 IN SYNC, 19/19 tracked files match live.
- Committed, not deployed: NIGHTLY-SHIP-1 ships this through the gates.
