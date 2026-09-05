## 2026-09-05 — Maintenance loop

- Fault queue EMPTY: 0 new, 26 verified, 7 closed, 2 duplicate (35 total). Shadow agent ran
  05:45:58Z, heartbeat read back from /dashboard/maint at 05:46:16Z. No escalation brief (none due).
- Ledger red RG-0099 (SSH lockout) HEALED and fixed as a class: the allowlist held a dead IP;
  `hetzner_fw_selfheal.py` now runs on every 20-min tick of autodeploy_agent.bat instead of waiting
  for a human. Asserted by new RG-0274. Port 22 re-probed open 3/3, SSH returns the box.
- RG-0138 now PROBES the external uptime Worker instead of reading a hand-typed date — which was
  one day from going red by arithmetic alone.
- Cost sweep exits 0 again: `claude-relay` (a git branch) classified as a non-model, stopping a
  WARN count that was feeding on its own output (5 → 13 in a day). Asserted by new RG-0275.
- Board after: 268 entries · 249 holding · 0 REGRESSED · 18 open · 0 UNVERIFIED. rulings_check 0 FAIL.
- DAILY_WATCH: DW-095, DW-096, DW-098 CLOSED with named evidence. DW-097 (the watch's alert path
  travels the same SSH transport as the failures it reports) stays OPEN — needs a Worker deploy.
- Committed, not deployed: NIGHTLY-SHIP-1 ships this through the gates.
