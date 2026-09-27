## 2026-09-27 — Maintenance loop: two sometimes-reds closed at the cause (COACH-HIRED-1, WITNESS-IN-AGENT-1)

- Fault queue: 0 new, 0 fix-shipped, 26 verified, 12 closed. Shadow agent run 20260927T054257Z saw 0 and acted on 0; heartbeat confirmed on /dashboard/maint. No escalations in 24 h (no brief written).
- Ledger before: green (a first pass read RG-0428 NOT EVALUATED because shard 1 installed fastapi mid-process; re-run clean). Ledger after the loop's first re-run: RG-0373 and RG-0175 read REGRESSED with no code change.
- **COACH-HIRED-1 (RG-0519)** — bea_main.py trust_score_guidance(): the AI rewords the trust plan on every call and one wording of the verified-client step dropped the 'I hired them' button name. Now a step saying 'hired' is matched to the referral signal first, and a referral step that does not name the tap gets the canonical wording and do='wait'. Scope: every category, every market. Needs the nightly ship to reach the live coach; RG-0373 is the live half.
- **WITNESS-IN-AGENT-1 (RG-0520)** — wave_hygiene_status.json claimed to be re-run every maintenance loop; nothing ran it, so at 05:38Z it aged past 14 days and RG-0175 (POPIA suppression witness) went red. Witness re-run (all three proofs ok, 05:49Z) and scripts/maintenance_agent.py now runs it as a lane on every run.
- Ledger after: exit 0, every locked fix holding, 21 open.
