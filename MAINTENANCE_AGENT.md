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
5. Verify the fix on named machine evidence (AIK-VERIFY-1) and set `verified`. Then
   `GET /admin/faults/{id}/close-draft`, read it, and `POST .../close-send` once David
   approves — the send CLOSES the fault (NO-RETEST-1, 11 Aug 2026: there are no retests).
6. The reporter owes us nothing further; a "still broken" reply always reopens.

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

**AIK-VERIFY-1 — SUPERSEDES the paragraph above (David's ruling, 5 Aug 2026 evening).**
One month of evidence answered the design question early: *people report, but people do
not verify* — the retest chip sat at zero while fixed faults piled amber. Ruling, David's
words in substance: after a fix, the AI must also TEST it and then declare it fixed
(green). Operational form:
- A fault may move to **verified** on MACHINE evidence: the failing action reproduced
  clean, a tripwire/ledger assertion covering it, or a live probe — named in `fix_note`.
  No named evidence = no verified; "the code looks right" does not qualify.
- The tester retest letter becomes an optional **courtesy**, not the gate. A tester who
  writes back "still broken" REOPENS the fault (their word still outranks our evidence).
- The dashboard's honest ladder stays: open (amber) → fix shipped · retest (middle) →
  verified/closed (green) — only the *who* of verification changed, never the *whether*.
- Tooling: RECONCILE_FAULTS.bat / scripts/fault_reconcile.py applies this to the queue.

**NO-RETEST-1 — completes AIK-VERIFY-1 (David's ruling, 11 Aug 2026).** There are no
retests at all: "retest won't work for a customer's complaint — it needs to be
fixed/verified/validated and closed with a response to the person." The courtesy letter is
now a CLOSURE letter — fixed -> verified (machine evidence) -> closed-with-response in one
lane (`close-draft`/`close-send`); the retest-wait status is retired (migrations/012) and
the dashboard chips read "awaiting close" / "fix shipped · to close". A reporter's
"still broken" still reopens — their word outranks our evidence. Ledger RG-0048.

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
    owns closure letters (TS-nnnn faults); Feedback owns suggestion acknowledgements.

**AMENDMENT — 11 Aug 2026 (session):** OPEN item (1) of the LAUNCH BOUNDARY REDRAW is closed:
the stringent design-change guidelines are written — see `DESIGN_CHANGE_GUIDELINES.md` (ten
pass/fail criteria + dossier template + the gate line). Item (2), binding the designer role,
remains OPEN and is David's decision; until bound, David is the gate by default per that doc.
B3 escalation brief machinery: `scripts/escalation_brief.py` (stage-7 format, one-tick actions).
B4 Tier-2: `migrations/011_maint_b4_tier2.py` runs the server-side rehearsal on the next deploy.

---

## RUL-013 — Fault-resolution operating model, both phases (David, 15 Aug 2026)

Extends RUL-005 (total autonomy, no veto) by naming WHO resolves what, and WHEN David is involved
at all. It inherits RUL-005's condition unchanged: **any gate that stops asserting re-arms the veto.**

### PRE-LAUNCH (now → 1 Sep 2026)
- **The agent does NOT surface failures or reports to David.** Testers are the fault source; AI
  resolves without him. A run that finds nothing he must read is the intended outcome, not a
  degraded one.
- **Escalations route to the FIX AGENT (Fable)** under the standing pre-approvals in
  STANDING_ORDERS.md, with laptop resources open to it.
- Unchanged and NOT delegated: the deterministic REFUSE guard. Legal, currently-costly and
  trust-core surfaces stop for a human in EVERY phase (maintenance_agent.py REFUSE_MARKERS).
  Autonomy is over the fixable class, never over the refuse class.

### POST-LAUNCH (from 1 Sep 2026)
- Fault source becomes **user complaints** rather than testers.
- **Maintenance agent handles most.**
- **Fix agent handles 98% of the remainder.**
- **David on STANDBY for the residual ~2%, for the FIRST TWO MONTHS**, with Claude's support.
  After that window the standby expectation is reviewed, not assumed.

### KNOWN GAP — the Fable hand-off is not yet wireable (stated 15 Aug 2026, honestly)
The intent is recorded; the mechanism is not built, and this note exists so no session assumes it is:

1. **There is no Fable lane in the product.** `ai_active` accepts only `anthropic|openai|scaleway`
   (bea_main.py:13675) and no Fable provider exists in the register. "Give it to Fable" today means
   a Cowork session running `/fix`, not a server-side hand-off.
2. **The server agent cannot summon a session.** It runs unattended at 05:20/11:20/17:20 UTC; a
   Cowork session is started by David. So an ESCALATE item waits for a session either way — the
   change is that it waits for FABLE'S session rather than for David's attention.
3. **"Laptop resources open" cannot be granted unattended.** Folder, app and browser grants are
   per-session and human-gated — the fault that stalled the 13 Aug photo run at image 1 of 54.
   An unattended run can never hold them.

**What would close the gap, in order:** (a) a Fable entry in the provider register with its own key,
so escalations can be dispatched server-side rather than waiting for a human-started session;
(b) an escalation queue the fix agent drains on start, so a session picks up everything waiting
rather than only what David remembers; (c) `preflight` run at the START of any session expected to
do fix work, so grants exist before they are needed rather than after.

Until (a) and (b) exist, PRE-LAUNCH behaviour in practice is: the agent fixes the PATH_A class
autonomously and silently as ruled, and the ESCALATE class accumulates for the next fix session.
That is a real improvement on David reading every report — but it is not yet "AI fixes it without me".

## MAINT-DEPS-1 — the lane installs what its INSTRUMENTS need, not just what CRASHES (28 Aug 2026)

**Step 0 of every maintenance run, before the ledger:** `python3 scripts/maint_deps.py`
(idempotent, ~1 s warm; `--check` reports without installing and exits 1 if anything is missing).

Why it earned its own step. BRAIN-DEPS-2 taught the lane to install `httpx` because the shadow
agent *dies* without it — a loud failure, so it got fixed. `fastapi` fails **quietly**: the
regression ledger's harness-backed entries (RG-0181, RG-0182) die at their import line, RG-0187
honestly demotes them to `[ ???? ] NOT EVALUATED`, and the run signs off "that is not a green
board". Nothing goes red, so nothing forces the fix — and those two entries were blind on every
sandbox run from 26 Aug to 27 Aug inclusive (DW-071 closed while explicitly recording the
residual: *"fastapi is absent from the sandbox bootstrap"*). **A blind instrument that never
complains is worse than a red one.**

Proven 28 Aug 2026: with `fastapi` present, RG-0181 and RG-0182 both read `[  ok  ]` and the
board came back **0 UNVERIFIED for the first time** — 191 entries, 177 holding, 14 open,
0 REGRESSED. The two harnesses were never broken; nobody could see them.

CLASS property, deliberately not a two-package list: any module the lane's INSTRUMENTS import
belongs in `REQUIRED`. A new harness that needs a new package adds a line there — it does not
get to be silently blind for a fortnight first.

