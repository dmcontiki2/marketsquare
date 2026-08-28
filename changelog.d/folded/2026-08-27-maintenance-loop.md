## 2026-08-27 — maintenance-loop (B2b daily brain run)

- **Fault queue EMPTY.** Shadow agent run `2026-08-27T05:35:50Z` saw **0 rows** (0 acted).
  Live queue counts read off `/admin/faults`: new **0**, triaged **0**, fix-shipped **0**,
  verified **26**, closed **7**. No patches applied, nothing escalated, no PATH_B routing —
  there was nothing to route. Report: `.maint_agent/run_20260827T053550Z.json`.
- **Heartbeat confirmed by PROBE, not by the agent's own say-so.** `GET /dashboard/maint`
  returns `run=2026-08-27T05:35:50Z`, `received_at=2026-08-27T05:36:06Z`,
  `brain_keyed=true`, `brain_lane=anthropic`, `mode=SHADOW`, `armed=false`. The B2b
  readiness row on the dashboard is fed by this run.
- **Regression ledger green both ends** — pre-run and post-run: *every locked fix is
  holding, 14 known defect(s) still open.* Exit 0 on both.
- **LEDGER-DEPS-1 recurrence, instrument-side (worth recording).** The FIRST pre-run
  demoted RG-0181 and RG-0182 to UNVERIFIED because this sandbox had no `fastapi` —
  RG-0187's demotion machinery behaved exactly as designed, and named the real reason
  rather than blaming the network. `pip install --break-system-packages fastapi httpx`
  restored a fully-evaluated board (177 ok / 14 open / 0 unevaluated). Cowork sandboxes
  are ephemeral, so this recurs every fresh session: **install `fastapi` alongside `httpx`
  in step 2 of the loop, not just `httpx`** — otherwise the day's first ledger reading is
  structurally two entries blind.
- **Escalation brief:** none written — `escalation_brief.py` reports no escalations in the
  last 24h. Silence here is green.
- No deploy, no push (NIGHTLY-SHIP-1 owns shipping).
