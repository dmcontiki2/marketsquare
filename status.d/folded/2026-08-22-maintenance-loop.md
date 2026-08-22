### Maintenance loop — 22 Aug 2026, 05:33Z (D-10 to full launch)

Quiet run. **0 faults in the queue** (new 0 · triaged 0 · fix-shipped 0 · rejected 0;
verified 26, closed 7), so no fixes were shipped and no fault rows changed status.

- Regression ledger GREEN both passes — every LOCKED fix holding, 11 known defects open
  (exit 0). No regression to chase.
- Shadow agent ran foreground, 0 seen / 0 acted; heartbeat PROBED live at
  `GET /dashboard/maint` (run 05:33:56Z, received 05:34:12Z, armed false). The endpoint
  answers anonymously now — migration 018 is on the box, so the runbook line saying the
  heartbeat GET still needs a ts_review cookie is out of date.
- Escalation brief: none written — no escalations in 24h.
- Reviewer gate: the code in `.secrets/review_code.txt` is PROVEN valid (200, token minted
  05:37:57Z). An earlier 429 in the same window came from failure budget the reviewer lane
  did not generate — see the changelog fragment; it owes a LIVE-half ledger entry against
  RG-0134 that was deliberately not written while the forensic session holds 201
  uncommitted lines in `scripts/regression_ledger.py`.
- Not pushed, not deployed.
