## 2026-08-21 — maintenance-loop (daily B2b session)

Daily maintenance loop ran end to end with nothing to fix. Regression ledger GREEN on both
the pre- and post-run passes (every LOCKED entry holding, 3 known defects still OPEN). The
shadow maintenance agent ran in the foreground and saw **0 faults, 0 actions**
(`.maint_agent/run_20260821T053334Z.json`), and its heartbeat is confirmed on
`GET /dashboard/maint` at `2026-08-21T05:33:34Z` (received 05:33:49Z, brain KEYED:anthropic,
shadow) — the dashboard's B2b readiness row is live and current.

Fault queue: new 0 · triaged 0 · fix-shipped 0 · verified 26 · closed 7. No patches applied,
therefore no AIK-VERIFY-1 evidence rows and no new ledger entries were due. No escalation
brief for the date (escalation_brief.py: no escalations in the last 24h). Nothing pushed and
nothing deployed — NIGHTLY-SHIP-1 (05:45 nightly TSL) carries committed work through the gates.

Standing open items unchanged and tracked by the ledger, not by prose: RG-0121 (photo-anon
canary dark, eval pending) and RG-0132 (openai has no production golden run on record —
`scripts/golden_seam_v2.py` must be run on the server with the production key, then the lane
added to GOLDEN_PASS).
