### Maintenance loop — 12 Sep 2026 (unattended)

Fault queue empty (0 new). Both ledger reds were instrument faults and both are fixed at class level.

- **RG-0257 / AGENT-ASLEEP-1** — a stale agent heartbeat no longer accuses the agent on its own. It
  now needs a second fact: an independent host writer dated after the last beat. No witness = the PC
  was asleep = NOT EVALUATED (exit 2), never REGRESSION. Third false alarm from that leg; proven in
  both directions against the real check. Locked by new entry **RG-0355**.
- **RG-0295 / JURIS-SUPPLY-SPLIT-1** — the entry demanded `armed+gates_green` on a bucket the
  jurisdiction gate had deliberately disarmed this morning under RUL-071. Re-arming the US is
  David's legal call, so the assertion was demanding a reserved act. Amended: a gate-stamped disarm
  reads INFO, an unstamped one still reads RED. Live: 88 'Northern California' US rows in the pool.
- Shadow maintenance agent clean (0 seen / 0 acted); heartbeat posted and probed back at 15:33:52Z.
- `rulings_check.py` 0 FAIL. No escalation brief (nothing in 24h).
- Operational note: ledger shards at 1/3 no longer fit the sandbox's ~180s command cap — run the
  board host-side (queued `run_py`) or at finer shard counts.
