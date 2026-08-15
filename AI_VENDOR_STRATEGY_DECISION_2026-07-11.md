# AI Vendor Strategy — Decision Note
**11 July 2026 · David's decision · companion to AI_PROVIDER_DEPENDENCY_POSTURE_2026-06-19.md**

## Decision (David, 11 Jul 2026)
1. **Staying with Claude.** The harness (Cowork + skills + memory + standing instructions
   + this codebase's Claude-shaped workflow) is the value, not the model-of-the-moment.
   Swapping vendors chasing benchmark leads is explicitly rejected as shortsighted.
2. **Subscription: drop to Max $100/mo when Fable 5 leaves subscriptions (13 Jul 2026).**
   Day-to-day dev work runs on the included models (Opus 4.8 tier).
3. **Fable 5 via usage credits ($10/$50 per Mtok) reserved for the most important work only.**
   Long, unsupervised, correctness-critical batches — where reviews show Fable's edge
   (SWE-Bench Pro 80.3%, fewer silent failures). Anthropic states Fable returns to
   subscriptions when capacity allows; credits are a bridge, not the end state.
4. **Add ChatGPT ($20/mo) as SECOND vendor, two roles:**
   a. Backup app-issue debugger (outage/diversity play — see posture note: this buys
      vendor diversity, NOT jurisdiction diversity; both are US).
   b. **Independent roving auditor** for MarketSquare — to be built up to scratch as an
      app agent. Rationale: Claude wrote most of this codebase; Claude auditing Claude
      has correlated blind spots. A second-vendor auditor breaks that correlation.

## Roving auditor — definition (to build when key exists)
- **Mission:** periodic independent sweep of the repo: canon-vs-code drift, cost-ceiling
  compliance (AI_FUNCTION_COST_CEILINGS), security/auth sweep, dead-code and dependency
  rot, "does STATUS.md match reality" checks.
- **Access: READ-ONLY.** It files findings; it never edits code. Findings land in an
  AUDIT_INDEPENDENT_<date>.md report next to AUDIT_PROGRESS.md.
- **Runner:** GPT-5.6 (Terra tier likely sufficient; Sol for deep passes) via the
  existing seam or a standalone script using OPENAI_API_KEY.
- **Cadence:** monthly, or after any major deploy.

## On-disk state (verified 11 Jul 2026)
- `ai_provider.py` — seam LIVE, 105 lines: ADAPTERS={anthropic, openai}, AI_ACTIVE env
  switch, fail-soft. OpenAI adapter is REAL (message translation + chat/completions +
  token logging), not vapor.
- **Stale:** OpenAI task→model map still lists gpt-4o-mini/gpt-4o (2024-era). Update to
  current model strings AND run eval_golden_set.py before any production traffic.
- `failover/ai_backends.py`, `eval_golden_set.py`, `golden_set.py` — failover path exists.

## Blocked on (David only)
- OPENAI_API_KEY (platform.openai.com, ~$10-20 credit) — the single missing piece for
  both the auditor build and a tested second adapter. ChatGPT $20 sub is separate
  (covers interactive use + Codex; contributes nothing to API).

## Explicitly rejected
- Replacing Fable-tier work with GPT-5.6 Sol for assignment batches (silent-failure risk
  on long unsupervised runs costs more in David's verification time than tokens saved).
- Vendor swap as jurisdiction hedge (posture note stands: only open-weight self-hosted
  insulates).


---

## Addendum 1 — Startup-phase cost posture (David's ruling, 17 Jul 2026, in-session)

David's words in substance: this is a BUSINESS decision, not a political one. Ruling:

1. **Cost leads in the startup phase.** While we operate outside the US (Stripe gap;
   launch focus ZA + EU/UK/AUS), the cheap open-weight lane (Kimi, DeepSeek, Qwen,
   Mistral) is a first-class vendor option, not a contingency shelf.
2. **The route is EU-hosted open weights** — which happens to be BOTH the cheapest and
   the GDPR/POPIA-clean route, so there is no cost-vs-compliance trade to argue about:
   - EU-resident inference hosts (all OpenAI-compatible, EU datacenters, no training on
     prompts): Scaleway (FR), OVHcloud AI Endpoints (FR), Nebius Token Factory (NL);
     EU routing layer: eurouter.ai (EU-residency OpenRouter equivalent).
   - OpenRouter itself is a US company routing globally — fine as a catalog/testing key,
     NOT an EU-residency answer.
3. **Kimi K3 path:** weights release ~27 Jul 2026 → wait for an EU host / eurouter to
   serve them → golden-set eval → into the per-task chains. Until then the open lane
   runs on DeepSeek/Qwen-class weights (available on EU hosts today). Moonshot's direct
   API is not needed for any of this.
4. **OpenAI key demoted to optional** (auditor-role purity only); the priority keys are:
   ONE EU open-weights host (Scaleway or OVH — David picks) + optionally eurouter/
   OpenRouter for breadth. The 11-Jul "ChatGPT second vendor" clause is amended
   accordingly for the startup phase; revisit at US market entry.
5. PII handling is unchanged and costs nothing under this route: EU hosts hold the data
   under EU law. Recorded as a compliance line-item, not a political position.

*Recorded by Claude from David's in-session ruling; supersedes conflicting lines above
for the startup phase.*


## Addendum 2 — Launch sequencing: cheap first, luxury later (David's ruling, 17 Jul 2026)

David's sequencing, in substance: make the launch as cheap as possible on in-app AI.
When funds arrive and we are profitable, first fund the operating stack
(server/AI/subscriptions/bank). Only then do we have the LUXURY of weighing safety,
security and best-capability model selection — and by safety/security he means the
luxury of worrying about politics/jurisdiction, not app security (which stays).

Operational meaning — this INVERTS Addendum 1's default for the launch phase:
- **Phase A (launch → first profits): cheapest capable model wins by default.**
  The EU open-weight lane (Scaleway: mistral-small / qwen3.6 / qwen3.5) is the
  PRIMARY route for every task that passes its golden-set eval. Anthropic is the
  quality rung, reserved for tasks the cheap lane measurably fails (expected:
  KYC-grade vision, possibly card grading) and as the failover in the other direction.
- The golden-set eval is the ONLY gate — a task moves to the cheap lane on eval pass,
  not on ideology; it moves back on eval fail, not on brand loyalty.
- Existing cost rails stay (ceilings, deliver-then-charge, spend log per provider).
- **Phase B (profitable):** operating stack funded first; revisit model mix.
- **Phase C (funded):** capability/jurisdiction selection becomes a choice, not a
  constraint — the standing trip-wires and validator/Karoo plans resume their weight.
- App security, POPIA/GDPR compliance and the anonymisation pipeline are NOT part of
  the deferred "politics" — they remain non-negotiable in all phases (and cost nothing
  extra under the EU lane).

Consequence for the build: P0 (call-site migration) is now the single highest-leverage
task in the project — it is what makes per-task cheap routing possible at all.


## Addendum 3 (18 Jul 2026) — Stability over price-chasing; bans are the exception

David's ruling: cheapest-model churn is a hidden cost, not a saving. If the app
re-picks its models every month as vendors compete on price, every swap costs
prompt re-tuning, golden-set re-runs, and behavior drift that users feel.
Stability outranks cost.

- Switch models on MEASURED FAILURE or FORCED EXIT only — never because a rival
  got cheaper this month. Price movements elsewhere are noted (at /housekeep) as
  fallback intelligence, not acted on.
- The one thing that legitimately breaks stability is a BAN (vendor account,
  geopolitical, export rule) — it forces a switch at a random moment. Therefore
  stability = a tested switching path, not an unchanging vendor: the standby
  lane stays warm and probed (seam architecture, T3 ban trip demonstrated
  17 Jul), so a ban degrades to a switch-flip on the +1 Executive page.

## Addendum 4 (18 Jul 2026) — Don't change tools mid-design (David's ruling, in-session)

- **Haiku 4.5 STAYS the production model for the app's haiku-class calls.**
  Not on cost grounds — the 18 Jul golden-set evals showed Mistral-Medium
  3.5-128B at quality parity (11/11 JSON incl. 2/2 vision on real photos) at
  ~40% of Haiku's cost with better latency from the box. The ruling is an
  aviation-electronics discipline: **do not change a tested, working tool
  mid-design.** Haiku has months of production history and prompts tuned to
  its behaviour; Medium has 20 eval calls. Switch when forced (ban, vendor
  exit, pricing shock, sustained outage) — then it is a different decision
  and the answer is already staged.
- **Mistral-Medium 3.5-128B is the DESIGNATED swap-out** in the "+1" registry
  card (TASK_MODEL scaleway haiku slot, shipped Session 142, live-verified).
  Triage stays mistral-small; vision slot pending (qwen3.6 failed the 18 Jul
  vision gate; Medium passed 2/2 and is the candidate when revisited).
- **Preconditions bound to ANY future flip** (carried from the evals, still
  open): (1) verify Medium pricing on the Scaleway console, (2) ship the
  Quality-Score >= 60 routing floor — sparse input makes EVERY cheap-lane
  model fabricate, Medium included, (3) breaker/heartbeat (P2) + a shadow
  period to build a track record.
- **Update (18 Jul, later):** David collapsed the standby row to ONE model —
  mistral-medium-3.5-128b for all four tiers (small + both qwens retired from
  the row). Rationale: one standby = one tested behaviour; Medium passed every
  gate the others failed. Preconditions above unchanged.
- QA note (David): the Haiku -> Sonnet quality step observed in the evals is
  valued; Sonnet 4.6 remains the quality-ceiling reference for advert copy
  (with the caveat that even Sonnet fabricated once — the no-invention guard
  lives in the prompt, not the model choice).


## Addendum 5 (31 Jul 2026) — GPT-5.6 second lane, sandbox ban drill, video swap lanes

David's rulings, recorded in-session:

1. **GPT-5.6 wired as the OpenAI lane** (Luna on haiku/vision/triage tiers, Terra on the
   sonnet tier) — seam, dashboard registry and any-of fallback chain all carry it; RG-0016
   locks the ids. Blocked on OPENAI_API_KEY only; golden-set eval gate before production
   traffic stands.
2. **Sandbox ban drill planned.** David will fund an OpenAI API key (platform.openai.com
   credit — NOTE: the $20 ChatGPT subscription is separate and contributes nothing to the
   API) and test the app in a sandbox with the Anthropic key absent, to prove the app runs
   with no Claude dependency. Claude stays the design/engineering harness by choice; the APP
   must not need any single vendor to run. The P2 design (AI_AUTO_FAILOVER_P2_DESIGN.md)
   carries the drill protocol.
3. **Video swap lanes designated: Kling 3.0 (~$0.075/s) and Luma Ray 2 (~$0.04/s)** as the
   ×10 cost-drop alternatives to Veo 3.1 standard (~$0.75/s) for the marketing video
   pipeline (no in-app video call site exists yet). Jurisdiction note: Kling is
   Kuaishou (Chinese endpoint) — acceptable for marketing spiels under the standing red
   line (no customer PII/KYC content to Chinese-jurisdiction endpoints; marketing prompts
   carry none). Luma is US. The true "through Scaleway" video route is self-hosting
   open-weight Wan on rented Scaleway GPUs — a Karoo-class build for later, not a swap flip.


## Addendum 6 (31 Jul 2026) — Review roles: GPT-5.6 becomes the formal PEER; video ruling refined

**1. Review-roles model (David's ruling, from his QA practice).** Every design review
carries five mandatory roles — QA, CM, Author (Engineer), Peer (another Engineer),
System Engineer. Mapped onto MarketSquare:

| Role | Held by |
|---|---|
| Author (Engineer) | Claude — writes the code and designs |
| Peer (Engineer)   | **GPT-5.6 — `scripts/peer_review.py`** (read-only; reports, never edits) |
| QA                | The executable machinery: regression ledger, BIT, audits |
| CM                | STATUS / CHANGELOG / CHANGE_REGISTER + git history |
| System Engineer   | David — decides, integrates, veto anchor |

This gives the 11-Jul "roving auditor" its concrete runner and its formal name. The Peer
reviews designs and code on request (`python3 scripts/peer_review.py FILE...`, Terra
default, ~$0.02–0.06 a review), writes Records/PEER_REVIEW_<date>.md, and David brings
the report back to the Author for discussion. The OpenAI key is therefore no longer
"optional (auditor purity only)" — it is the Peer's working key, alongside its standby
role in the app's fallback chain.

**2. Video ruling refined (supersedes Addendum 5 item 3).** The soul-line, David's words:
"all about cost but not at a price of selling our soul." Operational meaning:

- **No pure Chinese endpoints for ANY workload** — not only PII paths. Kling DIRECT
  (Kuaishou API) is out.
- **Chinese-origin models remain acceptable via Western/EU-hosted providers** (models
  vs endpoints doctrine): Wan 2.6 ≈ $0.05–0.071/s and Kling 3.0 ≈ $0.085–0.153/s are
  served by US aggregators (fal.ai, Atlas Cloud) under Western jurisdiction.
- **Fully Western lanes:** Luma Ray 2 ≈ $0.04/s, Veo 3.1 Lite ≈ $0.05/s (both ~10–15×
  under Veo 3.1 standard at $0.75/s).
- **Research finding (31 Jul 2026):** no European managed video-generation API exists —
  the sovereignty-grade EU providers (Scaleway, Nebius, T-Systems, OUTSCALE, Exoscale)
  serve text/vision/audio only. The EU-resident video route is therefore SELF-HOSTED
  open weights (Wan / LTX-class) on EU GPUs — the Karoo-class build, later. Until then
  the video pipeline's swap lanes are Luma Ray 2 and Western-hosted Wan/Kling, chosen
  per clip on cost; marketing prompts carry no customer PII, so US hosting is
  compliance-clean.


**Clarification (same day, David):** video is NOT an app feature and will not become
one — deliberately excluded because it would add a reliability, cost and complexity
dimension the marketplace does not need. Higgsfield covers ALL of David's own video
generation and is not linked to the app in any way. The video lanes above are therefore
SHELF INTELLIGENCE for his content pipeline only — consulted if Higgsfield ever fails,
reprices, or a video feature is one day deliberately chosen. Nothing is built, keyed,
or integrated on their account.


## Addendum 7 (31 Jul 2026) — Live-Values Doctrine; interim chain confirmed; Medium price corrected

David's rulings after the Peer's cost review:

1. **Interim three-lane chain stands** (anthropic → openai → scaleway; full provider
   registry deferred until the lane pool actually grows).
2. **Live values over historical values.** "We should not depend on historical values
   but live values, otherwise we are designing for failure of our intent." Operational
   form: `ai_price_card.json` is the ONLY legal source of AI prices (each entry: rate,
   currency, source, verified_at, capability gate); RG-0018 goes RED when the card is
   stale (>45 days) or misses a wired model; `scripts/price_truth.py` renders the card
   as the value ranking with David's two KPI drivers — CAPABILITY first, COST second.
   The ranking advises; Addendum 3 still governs switching. At P2, computed spend gets
   reconciled against vendor billing — a pricing page is a claim, an invoice is a fact.
3. **Correction of record:** the 18 Jul "Mistral Medium ≈ 40% of Haiku" claim is
   contradicted by Scaleway's live price page (€1.50/€7.50 ≈ 1.65× Haiku with FX buffer);
   the 40% likely inherited mistral-small's card. Until David's console check says
   otherwise, Medium's role is CONTINUITY/JURISDICTION standby, not a cheap lane. The
   cheap lane on current cards is GPT-5.6 Luna — GATED OUT until its golden-set passes.

## Addendum 8 (31 Jul 2026, late) — The Decision-Gate Process (built, enforced)

David's process, now running as code rather than intention:

1. **The Model Register** (`ai_price_card.json` v2): the single source of price AND
   capability truth. Every model carries verified prices (source + date), its AA
   Intelligence Index score (v4.1, variant + effort pinned: Haiku 4.5 = 29.58,
   Sonnet 4.6 = 47.21, Mistral Medium = 29.95, Luna = 51.24 max, Terra = 54.95 max),
   and its golden-set status. Schema includes the policy itself, so the rules travel
   with the data.
2. **The funnel** (`scripts/price_truth.py`): VALUE PROPOSES (AA points per $/1k, mid
   shape) → FLOOR → FITNESS DISPOSES (golden set, binary, pinned effort) → ANTI-JITTER
   (a procurement switch needs ≥30% sustained cost delta at equal-or-better gate, held
   ≥2 card refreshes / ≥30 days — thresholds live ON the card, amendable by David).
   Failover (T1–T3) exempt: ops, not procurement.
3. **Update triggers, enforced**: RG-0018 (freshness ≤45 days, full model coverage);
   RG-0019 (NEW — the live /flags lane must equal the register's active_lane, so a
   manual switch that outruns the record goes red the same day; extends to the P2b
   breaker block for auto-replace events); golden-set and vendor events update the
   card same-day by rule.
4. **First funnel reading (31 Jul)**: every tier's sitting model is the eligible
   winner except sonnet, where Mistral Medium is +42% cheaper at gate-parity — meets
   the bar, now HELD for the mandated two refreshes. The prize behind the gate
   remains Luna (value 69 vs 9 on haiku, 14 vs 1.8 on vision) — unlocked only by its
   golden set.

## Addendum 9 (1 Aug 2026) — Peer validation corrections adopted; governing switch policy chosen

David adopted all seven required corrections from the Peer's validation report
(Records/PEER_REVIEW_2026-08-01-0517_cost.md), now encoded on the Model Register v3:

1. Effort-matched capability (mismatched AA scores marked * = indicative, never decision-grade).
2. Executable cost rails — pre-dispatch computable maximum charge — specified as a P2a REQUIREMENT.
3. Gates are tuples (model, tier, prompt/eval version, effort, sampling) via gate_by_tier — never model-wide booleans.
4. **GOVERNING POLICY CHOSEN: Option 2 — cost-first after qualification.** Addendum 3 is
   expressly NARROWED, not repealed: a price move alone triggers EVALUATION, never a switch;
   a switch requires qualification (effort-matched golden set) + both materiality bars + the
   sustained hold. Stability remains the default state.
5. Dual materiality: >=30% relative AND >= $50 projected net saving over 90 days after
   evaluation/migration/shadow costs (amendable; formally unmet until spend volumes exist).
6. EUR lanes budgeted and alerted IN EUR; FX for comparison only; Scaleway = estimate until
   billed consumption observed; free-tier cap/expiry to record.
7. First-party sources only: Anthropic prices re-captured from platform.claude.com (1 Aug:
   Haiku 4.5 $1/$5, Sonnet 4.6 $3/$15 — third-party figures confirmed); OpenAI and Scaleway
   entries were already first-party. invoice_reconciled tracks the final proof.

## Addendum 10 (1 Aug 2026) — Dashboard ops layer: funnel strip + manual pin with decay

David's ruling, implemented (NOT yet deployed):

1. **Funnel strip on the +1 card:** latest comparison as ORDER AND GATE TYPES ONLY — no
   dollars on the dashboard; the numbers live in the Model Register. Served from
   `ai_funnel_snapshot.json`, generated by `scripts/price_truth.py --snapshot` (one
   ranking engine); RG-0020 goes red if the snapshot is staler than the register.
2. **Manual pin with decay:** the operator can PIN the live lane; the pin has PRECEDENCE
   over any automatic selection (including future P2 breaker logic) and EXPIRES after
   `AI_OVERRIDE_TTL_HOURS` (default 24), after which the STANDING lane resumes
   automatically. Pins are OPS, not procurement: the Model Register keeps tracking the
   standing lane and RG-0019 is pin-aware (a pin never trips it; a standing change
   without a register update still does).
3. **REVIEW dated ~1 Nov 2026** (after 3 months proven live): consider shortening the
   TTL to 1 hour — env change only, no deploy.
Plumbing: launch_switches gains ai_active_override + ai_override_expires (idempotent
migration); /admin/flags accepts ai_active_override (provider = pin, '' = unpin);
/flags.ai_provider now carries active (pin-aware), standing, override, funnel.


## Addendum 11 (1 Aug 2026) — Kimi K3: WAIT for Scaleway or OVHcloud; fewer servers preferred

David's ruling, recorded in-session after the EU-availability survey:

1. **The Addendum 1 trigger fired 1 Aug 2026** — EU serving of Kimi K3 (open weights,
   released 16 Jul 2026, weights public ~27 Jul) now exists: Nebius Token Factory (NL)
   at $3/$15 per Mtok, eurouter.ai (base $3/$15 + 15%/9%/3% routing markup), and
   HostYourAI at a claimed EUR 0.40/0.60.
2. **Ruling: WAIT for Scaleway or OVHcloud AI Endpoints to serve K3.** David prefers
   FEWER servers/providers — Scaleway is already wired and OVH is on the vetted EU
   list; adding Nebius or eurouter for one model works against consolidation. Neither
   Scaleway nor OVH lists any Kimi/Moonshot model as of 1 Aug 2026.
3. **HostYourAI is NOT pursued.** David is dubious of the EUR 0.40/0.60 rate (~25x
   under every other host for a 2.8T model — plausibly quantized or loss-leader).
   No probe, no key. Revisit only if it surfaces via a vetted route.
4. **Cost picture at decision time** (Model Register v2026-08-01.1): K3 at a credible
   EU host costs exactly Sonnet 4.6 ($3/$15) — 3x Haiku, 15x Luna, dearer than Terra.
   No procurement case on cost; the candidate role is EU FRONTIER/JURISDICTION STANDBY
   (Mistral Medium's role, higher capability class, ~1.7x Medium's price).
5. **Watch mechanism:** the /housekeep catalog re-scan (which already covers wired
   vendors) EXTENDS to two specific checks for this item: (a) Scaleway Generative APIs
   supported-models page, (b) OVHcloud AI Endpoints catalog — looking for Kimi K3 or
   any Moonshot model, capturing first-party price on sight. On sight: record price
   here + Model Register funnel per Addendum 9 (price triggers EVALUATION, never a
   switch); the golden-set gate still stands before any lane use.

---

## Addendum 10 (14 Aug 2026) — Grok placed FOURTH; and the retroactive-repricing rule

**David's ruling, in-session:** Grok goes in as a **fourth** text-tier lane. Scaleway's EU slot is
NOT demoted. David's words on the pricing discovery: *"I did not know about the retroactive cost
change and that is actually a very bad feature."*

**What was weighed.** Grok 4.6 (xAI, released 12 Aug 2026) is $2/M in, $6/M out with Intelligence
Index 61 — a tie with GPT-5.6 Sol, which lists at $5/M / $30/M. On cost-per-capability the honest
comparison is therefore against the **OpenAI slot**, not Scaleway's; Scaleway does not compete on
capability or price and never did. It is fourth regardless, because the tail of the chain exists
for **jurisdictional diversity**: promoting a third US provider above the EU lane would put three
US lanes ahead of any non-US one, and the T3 class (ban / suspension / key revocation, which by
definition "won't self-heal") is exactly the event that takes all three together. Vendor diversity
is not the same as jurisdiction diversity, and only the second one survives a T3.

**NEW STANDING RULE — retroactive repricing disqualifies a lane from carrying uncapped work.**
A generalisation of the existing bar on percentage-of-value costs (1 Aug 2026), and it applies to
every future vendor, not to Grok specifically:

> A price that can re-rate work ALREADY PERFORMED is unbudgetable in the same way a
> percentage-of-value cost is. Marginal tiering is fine — cross a threshold, pay more for what
> follows. Retroactive tiering is not: xAI rebills the ENTIRE request at $4/$12 once a prompt
> passes 200K tokens, so the last token can double the cost of the first. Any lane with a
> retroactive cliff may be used ONLY behind a hard cap that makes the cliff unreachable. No cap,
> no lane. The adapter refuses or truncates; it never discovers the cliff by paying for it.

**Conditions on the Grok slot** (all must clear before it is wired, none before launch —
Addendum 4 stands, don't change tools mid-design):

1. Hard context cap below 200K, enforced in the adapter, asserted by a test.
2. Vision support settled. Sources conflict — some document jpg/png image input; one analysis
   records vision/audio/video as unmentioned in the 4.6 disclosures. Vision is the binding
   constraint (8 of 22 features), so unresolved means NOT in the vision chain.
3. EU data residency verified, or Grok never carries jurisdiction-sensitive work. Availability
   in the EU is not residency.

**Also noted, unrelated to Grok:** Claude Sonnet 5's $2/M input is INTRODUCTORY through
31 Aug 2026 and becomes $3/M on 1 Sep 2026. That moves the primary lane's baseline ~2.5 weeks
from this ruling — budget from $3, not $2.

**Claude's declared bias:** Anthropic is Claude's own vendor and its recommendation was stated
with that on the record, per CLAUDE.md's model-selection rule. The recommendation given was: trial
Grok as a fourth lane, leave Scaleway, do not wire before launch — and if the trial holds, the
case to make afterwards is Grok displacing OpenAI on cost-per-capability. David took the placement.

---

## Addendum 11 (14 Aug 2026) — STANDING LANE MOVES TO OPENAI; and blockers that were only ever analysis

**David's ruling, in-session.** The standing lane becomes **OpenAI**. This supersedes Addendum 1's
"Staying with Claude" **as the standing lane only** — Claude remains the guidance/harness layer,
which was never the thing being procured.

**The reason is independence, not price.** David's words: this "will also ensure we don't use
Anthropic as the CEO/COO/Guidance and also then outsource our work to Anthropic." Claude authored
most of this codebase and advises at CEO/COO level; letting the same vendor also perform the
production work makes judgement and execution one correlated dependency. Addendum 1 already accepted
this logic for REVIEW — "Claude auditing Claude has correlated blind spots… a second-vendor auditor
breaks that correlation" — and this ruling extends the identical argument to EXECUTION. It is the
stronger case, and it stands with or without the cost numbers.

**Cost independently agrees but did not drive it.** The 2026-08-01.1 funnel ranks gpt-5.6-luna first
on haiku (+78%), triage (+78%) and vision (+79%), all golden-set passed.

**Noted exception, recorded not relitigated:** the sonnet tier reads +25% (gpt-5.6-terra vs
claude-sonnet-4-6), below the 30% materiality bar. It moves anyway, because a WHOLE-LANE independence
ruling is a different decision class from a per-tier procurement switch. The 30% anti-jitter bar
continues to govern per-tier procurement moves — it is not weakened by this.

**AMENDMENT — the $50/90d absolute floor is a POST-LAUNCH test, not a pre-launch gate.**
David's ruling, and he is right on the mechanics: that floor requires spend-log volumes, which by
definition cannot exist before launch. Applied pre-launch it is not a test that can be passed or
failed — it is a permanent block. His framing: these were "discussions that then became hammers to
keep us pegged" — analysis that hardened into a secondary requirement. From first revenue onward the
floor applies as written; before that it is INFORMATIONAL and never blocks. Recorded on the card
(`ai_price_card.json` → `policy.anti_jitter`), so the rule travels with the data as Addendum 8 intends.

**Standing principle taken from this exchange:** an analysis output is not a requirement. A gate that
cannot be satisfied in the current phase is a blocker masquerading as rigour, and it should be
phase-scoped when written — the same fault class as a guard asserting an implementation detail rather
than an invariant (see DRIFT-CACHEBUST-1 and the stale maint-scope guard, both 14 Aug).

**Resulting order:** 1. OpenAI (standing) · 2. Anthropic · 3. Scaleway EU · 4. Grok (capped, text
tiers only, not wired pre-launch).
