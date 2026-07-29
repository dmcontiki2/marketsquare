# MAINTENANCE AGENT — canon spec + readiness (29 Jul 2026, David's ruling)

**RULED — 29 Jul 2026 (evening), David — SUPERSEDES the morning ruling:** TOTAL
AUTONOMY, NO VETO. Every fix ships itself immediately through MECHANICAL gates;
David receives reports only, and his absence never stalls anything. The morning
"one word per day" design is retired: it made David the single point of failure —
the exact grinding halt the agent exists to prevent. Engine-agnostic per AGENTS.md.

**What replaces the human gate (all four are launch-blocking requirements):**
1. **Gates are tests** — a fix deploys only when the full canon suite + predeploy
   checks pass; payment/auth/schema changes additionally require their own BIT
   markers to pass (extra scrutiny is mechanical, never human).
2. **Automatic rollback** — after EVERY autonomous deploy the BIT self-test probes
   the live site; failure auto-reverts to the tagged rollback point, no one asked.
3. **Rate limiting + kill switch** — the loop may not deploy more than N times per
   hour (runaway protection), and MAINTENANCE_AGENT_ENABLED is David's one lever:
   off = the agent stops shipping (doctrine: he can disable/re-bind any agent).
4. **Act-safest-first escalation** — safety/legal/cost items are ACTED on
   immediately with the safest option (e.g. take the feature dark), then reported
   to David with a solution list + tick actions to REDIRECT after the fact.
   Reports inform; they never block.

**Infrastructure this requires (Phase 3, already commissioned 26 Jul):** deploys
must run WITHOUT David's PC — fix sessions commit to the git mirror; the SERVER
pulls, runs the gates, applies, BIT-verifies, and auto-reverts on failure.

**Mission:** from launch minute one, complaints are handled by AI end-to-end —
logged, acknowledged, binned, fixed majors-first, shipped invisibly, recurrence-
watched — with David seeing ONLY safety / legal / cost, always as a solution
list with tick actions.

## The pipeline vs. what exists today

| # | Stage (David's spec) | Status | What exists / what's missing |
|---|---------------------|--------|------------------------------|
| 1 | Log every complaint | **BUILT** | Cloudflare Email Worker → POST /email/inbound (secret-authed) → email_triage table; in-app: seller_complaints, lm_complaints, demand_tickets |
| 2 | Respond to the logger | **80% — gated off** | Haiku classifies (support/billing/legal/compliance/spam/other + urgency) and DRAFTS a reply; EMAIL_AUTO_SEND=0 today; needs GMAIL_APP_PASSWORD on server. Launch mode: auto-ACK every non-spam complaint in seconds (ref number, "logged, being handled"), full answers auto-send for support/billing only |
| 3 | Sort / analyze to bins | **40%** | Email-level categories exist. MISSING: failure-code binning (which part of the app) + FAULT_REGISTER.md with dedupe + votes (the /feedback pattern, made automatic) |
| 4 | Manage fixes, majors first | **skills exist, not scheduled** | /feedback → /fix → /fixback do exactly this when invoked. MISSING: the scheduled Maintenance session that runs them unattended |
| 5 | Update live app, invisible to users | **BUILT this week** | Guarded deploy + tripwire gates + autobump + working CF purge; users get every fix on next load, no action, no visible process |
| 6 | Parallel recurrence watch → design changes | **30%** | Deploy-gate tripwires catch CODE regression. MISSING: failure-code recurrence counting in the register; threshold → "design change" item |
| 7 | David sees only safety/legal/cost, with solutions + tick | **concept wired** | legal/compliance already excluded from auto-send. MISSING: the escalation brief format (issue → solution options → one-tick choice) |

## The honest design decision (revised 29 Jul evening)
The control system that stopped our recurring bugs was never a human — it was the
mechanical gates (canon tests, BIT, rollback tags). Total autonomy keeps ALL of
them and adds auto-rollback, rate limiting, payment-path markers and a kill
switch. The daily 21h00 stand-up gives David full visibility of everything the
agent did — after it did it. n8n note: inbound triage does NOT run on n8n (memory served
the outreach fleet) — it is Cloudflare Worker + BEA, already live.

## Role map (N×N review, 29 Jul — Gemini input, adopted as ROLES not runtimes)
Per the AGENTS.md doctrine these are role stages of ONE pipeline, each separately
re-bindable — NOT five deployed services (a solo-founder stack earns no microservice
fleet; the separation lives in the spec so any stage can be re-bound later):
  Ingestion & Translation  = CF Worker + /email/inbound + Haiku classify  (built)
                             + error-log channel (B1)
  Triage & Grouping        = FAULT_REGISTER bins + semantic dedupe → one master
                             incident per storm, recurrence counter        (B1)
  Feasibility & Guardrail  = ADOPTED — the explicit Path A/B boundary:
     Path A (mechanical: copy, config, flags, logic bugs) → Fix Agent,
       full total-autonomy self-ship through the gates.
     Path B (design change: layout, new UI, flows, brand) → Bridge dossier
       (grouped user context + files + spec) into the DESIGN BACKLOG; built by
       the Design agent role (roster discussion pending), shipped through the
       SAME gates. Autonomous too — but batched, never hotfixed.
  Automated Fix Agent      = B2 scheduled sessions + Phase 3 self-deploy +
                             auto-rollback (our 'shadow environment' = predeploy
                             suite + BIT; our 'feature flags' = env gates +
                             /admin/flags, both already in the stack)
  Bridge Agent             = dossier writer + escalation briefs               (B3)
Stack answer for the record: FastAPI + SQLite + Redis on Hetzner; git mirror on
GitHub; ticketing IS email_triage + FAULT_REGISTER (no Jira/Zendesk).

## Build batches (each rides a normal deploy; each leaves tripwires)
- **B1 — Register + codes:** FAULT_REGISTER.md; every triaged complaint gets a
  failure code + bin; recurrence counter; auto-ACK reply switched on after test.
  PLUS (adopted from N×N review, 29 Jul): the SERVER ERROR LOG becomes a complaint
  channel — the app files incidents about itself, catching what users never report.
- **B2 — The autonomous loop (largest batch):** (a) Phase 3 self-deploy: server
  pulls from the git mirror, runs gates, applies, BIT-verifies, AUTO-REVERTS on
  failure; rate limiter + MAINTENANCE_AGENT_ENABLED kill switch. (b) Scheduled
  fix sessions 3×/day: pull new complaint rows via admin API, dedupe/bin, rank
  majors, implement fixes + tripwires, commit to the mirror. Majors → immediate
  extra run + push notification to David (informational).
- **B3 — Escalation brief format + cost watch:** safety/legal/cost detector over
  bins; brief template; Paystack/API-cost thresholds feeding it.
- **B4 — LAUNCH REHEARSAL:** synthetic complaint storm (the E2E-email method):
  seeded complaints of every category incl. one legal + one safety → prove the
  whole loop end-to-end, then sign it READY.

Target: B1–B4 complete and rehearsed ≥ 1 week before 1 Sep (i.e. by ~22 Aug).
