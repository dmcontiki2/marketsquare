# MAINTENANCE AGENT — canon spec + readiness (29 Jul 2026, David's ruling)

**RULED — 29 Jul 2026, David:** one-word-per-day ship gate approved. Engine-agnostic
per AGENTS.md doctrine (role/capability-defined, AI binding swappable).

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

## The honest design decision (recorded)
A 100% hands-off loop would require auto-deploying AI-written fixes with no gate —
destroying the control system that stopped our recurring bugs. The launch design
keeps ONE human word per day: the Maintenance session runs on schedule, prepares
fixes + tripwires overnight, leaves a READY flag (the /tsl nightly pattern already
built), and David's single morning word ships the batch — that same daily brief IS
the safety/legal/cost tick list. Majors get a same-day extra run. Everything else
is fully autonomous. n8n note: inbound triage does NOT run on n8n (memory served
the outreach fleet) — it is Cloudflare Worker + BEA, already live.

## Build batches (each rides a normal deploy; each leaves tripwires)
- **B1 — Register + codes:** FAULT_REGISTER.md; every triaged complaint gets a
  failure code + bin; recurrence counter; auto-ACK reply switched on after test.
- **B2 — The scheduled session:** cloud scheduled task, 3×/day: pull new rows via
  admin API, dedupe/bin, rank majors, prepare fixes on the repo, leave READY flag
  + morning brief (solutions + ticks). Majors → immediate push notification.
- **B3 — Escalation brief format + cost watch:** safety/legal/cost detector over
  bins; brief template; Paystack/API-cost thresholds feeding it.
- **B4 — LAUNCH REHEARSAL:** synthetic complaint storm (the E2E-email method):
  seeded complaints of every category incl. one legal + one safety → prove the
  whole loop end-to-end, then sign it READY.

Target: B1–B4 complete and rehearsed ≥ 1 week before 1 Sep (i.e. by ~22 Aug).
