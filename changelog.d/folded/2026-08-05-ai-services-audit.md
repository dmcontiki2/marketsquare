## 2026-08-05 — Internal AI services audit (Phase 1) + Peer pack

- **AI-SERVICES-AUDIT-1:** Author's investigation of the whole internal AI estate
  (5 user-facing Tuppence services, 22 seam call sites, breaker, tier gates, cost
  rails, governance). Report: `Records/AI_SERVICES_AUDIT_2026-08-05.md` (+ nice
  docx). Verified sound: seam totality (RG-0017), breaker P2a attached fail-open,
  cost rails 17/17 wrapped (sweep 0 critical), paid feeds all OFF, register locks
  RG-0016..0020. Findings: **F1 HIGH** — 15 endpoints hard-gate on
  ANTHROPIC_API_KEY, breaking single-vendor independence (class fix = seam-level
  any-lane-configured check; pre-launch blocking); **F2 MEDIUM** — AI1/AI2/AI5
  charge Tuppence BEFORE the model call, contradicting the published "no Tuppence
  on server error" promise (AI3/AI4 already deliver-then-charge); **F3 DECISION**
  — help copy names "Claude" per service vs cost-first routing; F4=DW-009
  (known); F5=P2b/P2c residue (by design). No fixes shipped — findings filed,
  David's go pending; F1/F2 need ledger entries when fixed.
- **PEER_AUDIT_AI_SERVICES.bat** (repo root): one-click Phase 2 — GPT-5.6 Terra
  full-sweep over the report + estate, confirm/refute F1–F5. David
  double-clicks (OpenAI key + spend are his side). ~$0.05–0.10.
