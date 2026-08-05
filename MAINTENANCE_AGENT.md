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
| 1 | Log every complaint | **BUILT** | Email: CF Worker → POST /email/inbound → email_triage. **In-app APP FAULTS: the REPORT tab → POST /app/fault → app_faults (MAINT-B1b, 5 Aug).** NB seller_complaints / lm_complaints are marketplace CONDUCT, not app faults — different lane. Still missing: the app's own error log as a third channel |
| 2 | Respond to the logger | **80% — gated off** | Haiku classifies (support/billing/legal/compliance/spam/other + urgency) and DRAFTS a reply; EMAIL_AUTO_SEND=0 today; needs GMAIL_APP_PASSWORD on server. Launch mode: auto-ACK every non-spam complaint in seconds (ref number, "logged, being handled"), full answers auto-send for support/billing only |
| 3 | Sort / analyze to bins | **70%** | Both lanes now carry a bin. app_faults has the dedupe boundary in the schema: `dup_of` on a child increments the parent's `recurrence` (register rule 3). MISSING: the SEMANTIC dedupe that decides two differently-worded reports are one fault — done by hand this month, which is exactly how we learn what the rule should be |
| 4 | Manage fixes, majors first | **skills exist, not scheduled** | /feedback → /fix → /fixback do exactly this when invoked. MISSING: the scheduled Maintenance session that runs them unattended |
| 5 | Update live app, invisible to users | **BUILT this week** | Guarded deploy + tripwire gates + autobump + working CF purge; users get every fix on next load, no action, no visible process |
| 6 | Parallel recurrence watch → design changes | **30%** | Deploy-gate tripwires catch CODE regression. MISSING: failure-code recurrence counting in the register; threshold → "design change" item |
| 7 | David sees only safety/legal/cost, with solutions + tick | **concept wired** | legal/compliance excluded from auto-send. The retest letter's draft/send split is the first working instance of the shape (read, then one action). MISSING: the escalation brief format (issue → solution options → one-tick choice) |

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

## Independence map + brain-binding ruling (29 Jul 2026 evening, David)
**The spine is server-resident and subscription-free TODAY:** ingestion (CF Worker
→ BEA endpoint), triage classification (Anthropic API key on the server, through
the ai_provider.py swap seam — pay-per-token, engine = one config line), fault
codes + register, the ACK (Resend), all gates (canon tests / BIT / predeploy),
and Phase-3 self-deploy. FEA involvement: none (the agent edits FEA files like
any developer). BEA involvement: the pipeline endpoints only, by design.

**The brain (B2 fix sessions) — RULED:** runs as scheduled Claude sessions (the
subscription) FOR LAUNCH — fastest to build and rehearse. Its contract is strict
so the binding stays swappable: REGISTER ROWS IN → GATE-PASSING COMMITS OUT,
nothing else. **Re-bind trigger (mirrors the Postgres ruling):** once the launch
rush of issues has been managed down to a trickle, the brain is re-bound to a
DEDICATED server-resident worker (Agent SDK / any vendor / self-hosted) on
Hetzner, API-billed, provider-swappable by key. A planned config-grade move,
not a redesign — the spine never changes.

## THE PRE-LAUNCH MONTH — Claude runs the loop by hand (5 Aug → 1 Sep)
**David's ruling, 4 Aug 2026.** Testers report through the app's own complaint channel;
Claude fixes what comes in and writes back to the tester with what changed so they can
retest and confirm. This is not a stopgap while the agent is built — **it is how the agent
gets specified.** A month of real faults, filed by real testers on real screens, answers
the questions no design session can answer honestly from an armchair.

**The daily rhythm (one session, unattended-capable):**
1. Read `GET /admin/faults?status=new` — blockers first, the endpoint already sorts.
2. Bin and code each one against FAULT_REGISTER.md; mark duplicates with `dup_of` so
   recurrence counts itself.
3. Decide Path A (mechanical → fix now) or Path B (design change → dossier, batched).
4. Fix, add the tripwire, ship through the normal gates.
5. `GET /admin/faults/{id}/retest-draft`, read it, then `POST .../retest-send` once David
   approves. Fault moves to `awaiting-retest`.
6. The tester's confirmation — and only that — moves it to `verified`.

**What the month must produce (the agent's real requirements, measured not guessed):**
| Evidence | The design question it settles |
|---|---|
| Time from filing to shipped fix, per bin | Where autonomy pays and where it is theatre |
| Path A : Path B ratio | How big the design-backlog lane really has to be |
| How often two reports were the same fault | Whether semantic dedupe needs a model at all |
| How often the tester's retest said "still broken" | Whether "fixed" can ever be self-declared |
| Which faults Claude got WRONG on first attempt | The escalation threshold — when to stop and ask |
| Which faults were safety / legal / cost | Whether stage 7's filter fires often enough to matter |

**The one thing this month must not do:** let a fault close without an outside confirmation.
`awaiting-retest` exists precisely so a fix we have only verified ourselves cannot be
recorded as verified. That distinction is the honest core of the whole agent.

## Build batches (each rides a normal deploy; each leaves tripwires)
- **B1b — In-app tester intake (DONE, 5 Aug 2026):** app_faults + POST /app/fault + auto-ACK
  with reference TS-nnnn + admin triage queue + the draft/send retest letter + ts_report.js on
  all 14 tester-facing pages. Fail-closed behind `launch_switches.fault_report`. RG-0030.
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


## LAUNCH BOUNDARY REDRAW — David, 5 Aug 2026 (amends the 29 Jul evening ruling for Path B ONLY)
David's ruling, his words: for launch the Maintenance Agent has "autonomy of complaints
regarding customer faults found and customer feedback reporting, with the possible design
changes then to be measured against more stringent guidelines with a designer approval gate."
- **Path A (mechanical fixes) — UNCHANGED.** Total autonomy, no veto, mechanical gates only.
- **Path B (design changes) — AMENDED.** The dossier lane stays, but a design change now
  requires (a) measurement against stringent design-change guidelines (to be written before
  launch) and (b) a DESIGNER APPROVAL GATE before build. The 29 Jul "Autonomous too — but
  batched" wording no longer applies to Path B; batched-never-hotfixed still does. This does
  NOT reintroduce the single point of failure the 29 Jul ruling removed: Path B is the batched
  lane, so a stalled approval delays a design change, never a fix.
- **Pre-launch (now → 1 Sep):** improvement vs design change deliberately NOT strictly
  differentiated — the tester pool is contained to three (David, Maroushka, David Junior), so
  drift/baseline risk is controlled by the people, not the process. The strict Path A/B
  boundary + designer gate activates AT LAUNCH.
- **OPEN before launch:** (1) write the stringent design-change guidelines; (2) bind the
  designer role (AGENTS.md roster discussion still pending) — per doctrine a ROLE with a
  swappable binding (David, a design agent, or both); (3) the Maintenance vs
  Feedback-Triage roster boundary. **David's correction, 5 Aug 2026 (later same day):** do NOT
  assume feedback folds under Maintenance — "it may very well be 2 agents." Boundary review
  RULED by David, 5 Aug 2026 — "I agree to the two-agent split", with an explicit
  information flow / hand-over between them:
  * TWO agents, ONE intake. The reporter never picks a lane (the register proves testers
    can't: F-013 was "feedback" with a wrong diagnosis hiding a real fault; F-015 opened
    F-016/F-017). Triage routes: failure claim -> FAULT_REGISTER (Maintenance); preference /
    suggestion / praise -> FEEDBACK.md (Feedback-Triage); cross-link when one reveals the other.
  * Maintenance Agent = adjudicate-fix-verify-harden. NCR lane, majors first, immediate,
    Path A total autonomy. Escalates on safety/legal/cost.
  * Feedback-Triage Agent = listen-synthesize-prioritize-route. Voice-of-customer lane,
    batched, vote-counting, fix-now/next/later/out-of-scope classes. Autonomous in reporting
    and classification; never fixes — routes fix-now items to Maintenance.
  * The designer approval gate sits on NEITHER agent — it gates the ONE design backlog that
    BOTH feed (Maintenance via recurrence rule 3 dossiers; Feedback via design-change items).
    One lane, one gate, two feeders.
  * HAND-OVER CONTRACT (David, 5 Aug): items cross by REFERENCE, never by copy.
    Feedback routes a fix-now item to Maintenance as a FAULT_REGISTER row citing the
    F-nnn verbatim; Maintenance reports fix/ship status back so the F-row closes on the
    same evidence (FEEDBACK.md's link column already does this). A Maintenance
    NOT-A-FAULT adjudication that reveals a wish/preference routes back as a new F-row.
    Recurrence counts and theme votes stay visible to both. Reporter replies: Maintenance
    owns retest letters (TS-nnnn faults); Feedback owns suggestion acknowledgements.
