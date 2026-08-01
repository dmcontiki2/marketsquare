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
