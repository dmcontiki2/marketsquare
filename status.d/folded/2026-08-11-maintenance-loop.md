- **Maintenance loop, 11 Aug (daily run):** the loop's own intake was broken and reporting
  green — `UA-EDGE-1`. Cloudflare refused every UA-less call from our tooling (error 1010)
  before it reached the origin, so `maintenance_agent.py` read an empty queue and exited 0.
  Fixed for the whole class (5 scripts that call our edge now send a User-Agent); verified
  by reproducing the failing action clean (403 → 200, 7 faults appeared). **RG-0053 LOCKED**,
  with a live half so a silent re-break turns the ledger red. Committed, not deployed —
  NIGHTLY-SHIP-1 carries it through the gates.
- **Fault queue after the fix is readable again: 30 total · 7 new · 19 verified · 2 duplicate
  · 1 closed · 1 stale `awaiting-retest` (TS-0022 — status retired by NO-RETEST-1/migrations
  012; row not touched by this session, flagged for `fault_reconcile`).** All 7 new are
  severity=major: TS-0001, TS-0006, TS-0018, TS-0021, TS-0024, TS-0027, TS-0030.
- **None of the 7 were fixed this session — and the reason is itself a finding.** The shadow
  agent routed all 7 to PATH_B with `why: "ai_provider unavailable -- defaulting to the
  batched design lane"`. That is RG-0049 degradation working as designed (a brain failure
  degrades, never kills), but it means **the queue is currently classified by the fallback,
  not by judgement** — no fault reached "gates GREEN, patch ready", so per the loop's strict
  contract nothing was applied. The brain binding needs an ai_provider lane reachable from
  wherever the loop runs, or the 3×/day sessions will keep binning real faults as design work.
- Escalation brief: none written — no safety / legal / cost items in the last 24h.
