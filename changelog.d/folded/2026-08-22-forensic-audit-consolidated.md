## 2026-08-22 — Launch-readiness forensic audit, Cycles 2+3 + consolidated verdict

Completed the three-cycle launch-readiness forensic HALT audit (D-7 gate evidence base).

- **Consolidated verdict: HOLD.** Board 2 RED · 8 AMBER · 0 GREEN. 15 Aug rule → any RED at D-7 =
  hold declared today; launch ruling is David's.
- **Cycle 2 (fresh Fable doctoral peer):** overturned two Cycle-1 greens — Profitability GREEN→AMBER
  (break-even recomputed at ~49–103 sellers under realistic demand, not 25–30) and Reliability
  GREEN→AMBER (no external uptime monitor, fail-open overuse). Found /dashboard/summary leaks the
  security posture ("WAF allowlist DISABLED, origin gate the only guard" + CPX32 sizing) to any
  anonymous caller — confirmed PROBED.
- **Cycle 3 (OpenAI GPT-5.6, second vendor, $0.87):** found accept_intro is NON-IDEMPOTENT —
  repeated/retried PUT /intros/{id}/accept inserts another -1 intro_deduct every call, no guard on
  prior status/tuppence_charged, no idempotency key, no balance floor (bea_main.py 5740–5748,
  CONFIRMED on disk). Neither Claude cycle caught it. Also: live AI spend ceiling unverified (code
  supports uncapped when 0), KYC ID-doc routing to active AI provider (POPIA/GDPR) + 120s event-loop
  block, pre-auth wallet-oracle concern.
- **Cleared/mitigated (PROBED):** IL-01 now 401 (authenticated); account_binding live ON; core app
  auth holds every probed attack (injection/enum/exhaustion/fail-closed); git-lock ledger regression
  healed.
- **Recommended LOCKED ledger entries (for the session that ships the fixes):** (1) accept_intro
  replay charges once; (2) /dashboard/summary carries no infra/WAF posture for anonymous callers;
  (3) live AI platform ceiling is nonzero. Reserved to David: GO/HOLD ruling, secret rotation,
  shipping B2/B3 fixes (deploys), scope/date change.
- Deliverables: FORENSIC_AUDIT_CYCLE1/CYCLE2_PEER/CONSOLIDATED — nice.docx + two colour-coded boards
  (indexed to Visuals). Peer reports: Records/PEER_REVIEW_2026-08-22-*.md.
