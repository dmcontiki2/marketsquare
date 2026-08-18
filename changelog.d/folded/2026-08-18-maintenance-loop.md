## 2026-08-18 — maintenance-loop: queue drained, ledger green, no code change

- B2b brain run 2026-08-18T05:33:32Z, mode SHADOW (kill switch OFF — the default;
  arming stays David's act alone), phase postlaunch, trust-core GUARDED, brain
  KEYED:anthropic. Code stamp 99202e7. Report: `.maint_agent/run_20260818T053332Z.json`
  — 0 faults seen, 0 acted. Heartbeat POST landed and was read back from
  `GET /dashboard/maint` (received_at 05:33:46Z), so the +1 page B2b readiness row is
  current, not stale.
- Fault register is fully drained: 35 rows total — 26 verified, 7 closed, 2 duplicate,
  **0 new and 0 fix-shipped**. Nothing met the "SHADOW: gates GREEN, patch ready" bar,
  so no patch was applied and no fault row was touched. Strict contract honoured:
  no register rows in, no commits of code out.
- Regression ledger green both sides of the session (exit 0 before and after): every
  LOCKED fix holding, 3 known defects still open and expected — RG-0075 (admin-gate
  script duplicated across 5 files), RG-0090 (gated index document cacheable at the
  edge), RG-0101 (live gzip on /wonders unprovable from here: /ops/selfcheck 401).
- Escalation brief: none written — no escalations in the last 24h.
- Session note (not a product fault): probes to the origin using urllib's default
  User-Agent answer 403 at the edge, including with a valid ts_review cookie. The
  ledger's `_get` sends a named UA and reads through cleanly. Any future session
  hand-probing the live site must send a real User-Agent or it will misread an edge
  UA block as a gate failure.
