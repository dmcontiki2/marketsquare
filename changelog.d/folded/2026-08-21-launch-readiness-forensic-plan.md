## 2026-08-21 — LAUNCH-AUDIT-PLAN-1: the 3-cycle launch-readiness forensic programme, scheduled for D-7

David's last assignment of the night: a full forensic audit of launch readiness for soft 29 Aug /
full 1 Sep (RUL-001), in three independent cycles — Claude's forensic pass, a doctoral peer
analysis of that pass, then an OpenAI-API peer review of the final report.

- Plan authored as `LAUNCH_READINESS_FORENSIC_PLAN — nice.docx`. Ten dimensions: business
  viability, financial growth, profitability/unit economics, server capability, robustness,
  reliability, maintainability, scalability, hardening, hack-proofness. Every dimension scored
  GREEN/AMBER/RED with its evidence grade and blocker-vs-fast-follow, under the Evidence Ladder.
- The plan is built on REAL instruments verified on disk this session — scripts/peer_review.py
  (nine lenses incl. security/cost/performance/maintainability/privacy, GPT-5.6, read-only),
  scripts/peer_pack_ai.py (line-numbered extract for the 850 KB bea_main.py), regression_ledger,
  rulings_check, predeploy_check, FINANCE_CANON, THIRD_PARTY_LAUNCH_REGISTER, LAUNCH_BAR.
- Cycle 3 maps directly onto David's existing 5-role QA practice (31 Jul): the OpenAI model is
  the second-vendor Peer Engineer. The paid call is gated on David's approval (RUL-037 spend).
- The known going-in blocker is stated, not buried: DW-057/DW-029 unrotated exposed secrets with
  the WAF allowlist down — dimensions 9/10 begin there; Cycle 1 must confirm or clear it.
- Scheduled task `launch-readiness-forensic-cycle1` fires Sat 22 Aug 07:00 SAST (fireAt, one-shot)
  so David sees Cycle 1 start. Timed to BE the D-7 gate-review evidence base (15 Aug rule: any RED
  at D-7 = hold declared that day; the launch ruling stays David's).

Cost model impact: the plan itself, none. Cycle 3's OpenAI call is dry-run-sized first and
David-approved before any spend (ballpark cents to low tens of cents).
