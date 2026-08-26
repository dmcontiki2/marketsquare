- **Maintenance loop 2026-08-26 (B2b brain, shadow).** Fault queue drained — 0 new, 26
  verified, 7 closed, 2 duplicate; agent heartbeat posted 05:35:32Z; no escalations in 24h.
  Top item was the RG-0125 red: migration 033 jammed the chain on the 04:05:08Z deploy.
  Root-caused to the migration's settle loop, which exited on a STABLE answer rather than the
  EXPECTED one and therefore measured the stale policy one second after the reload — the
  fourth consecutive failure in 033's measurement organ, never in its rewrite. Fixed the poll,
  widened post_deploy.sh's failing-step capture (3 lines/300 chars was narrower than the
  evidence and had destroyed the diagnostic four times), added scripts/prove_csp_settle.py
  (11/11) and locked RG-0191. **RG-0125 remains red until a deploy runs 033 again** — it reads
  the last deploy report and this loop does not deploy; the commit is left for the nightly TSL.
  Ledger 166 ok / 17 open / 1 red; rulings 57/57 reflected.
