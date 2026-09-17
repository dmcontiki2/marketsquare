- Maintenance loop ran 2026-09-17. Fault queue empty: 0 new, 0 triaged, 0 fix-shipped,
  0 escalated (26 verified, 12 closed). No escalation brief — no escalations in 24h.
- Regression ledger green before and after (368 entries, 22 known defects still open,
  no LOCKED entry red).
- One defect found and fixed, in the maintenance lane's own instrument: a brain the run
  cannot reach from where it stands now reads NOT MEASURED instead of AMBER. The brain
  endpoint is local-only by design, so every remote run was painting the same amber a real
  outage would. Fixed in maintenance_agent.py and dashboard.server.html; Path B fail-safe
  routing unchanged. RG-0382 LOCKED, negative-tested.
- Committed, not pushed and not deployed — the nightly TSL carries it through the gates.
