- **Maintenance loop 14 Aug (shadow, unattended).** Queue 3 new / 0 fix-shipped / 23
  verified. No application code changed — no fault reached "gates GREEN, patch ready".
  Two faults in the LOOP ITSELF found and fixed: **GATE-CACHE-1** (RG-0070) — the shared
  ts_review token cache; without it a session burned the 8/10min login limit and the
  ledger printed 13 FALSE regressions against a healthy site. **HOST-CAP-1** (RG-0071) —
  the run report is now flushed per fault, plus `--only=REF` and `MAINT_TIME_BUDGET_S`,
  so a run killed by the sandbox's ~178s bash cap can no longer vanish without a trace.
  Ledger green after: 71 entries, 0 regressed, 6 open. Heartbeat live
  (2026-08-14T06:01:28Z). **Open for David:** TS-0033 (Sydney → SA adventures) was never
  examined to completion — a PATH_A fault on a megabyte file does not fit inside the
  sandbox cap, so it needs an attended session or an uncapped host. TS-0032 is the same
  class and the brain declined a clean patch for it.
