# Independent Peer Review — 2026-08-01-0517

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: cost · Author: Claude · System Engineer: David*

**Scope:**
  - ai_price_card.json (6,613 chars)
  - FUNNEL_OUTPUT_2026-07-31.txt (2,760 chars)
  - AI_VENDOR_STRATEGY_DECISION_2026-07-11.md (17,145 chars)

**Usage:** 8002 in / 9286 out tokens · actual cost ≈ $0.1274

---

# Peer Review — Cost / FinOps Validation Pass

## Review basis and verification boundary

I independently re-derived the arithmetic from the supplied card and output. I **cannot independently verify facts asserted as live on 31 July 2026** from the supplied material alone, nor can I browse the cited vendor and benchmark sites in this review.

My reliable pre-supplied knowledge of public model pricing ends before the stated verification date and predates the named `GPT-5.6 Luna/Terra`, `Claude Haiku 4.5`, and `Claude Sonnet 4.6` entries. Accordingly, I can validate **internal arithmetic and process logic**, but not certify the claimed live prices or AA scores.

---

## Findings

### [BLOCKER] The register uses benchmark scores from non-equivalent operating modes to rank the economics of default-mode production calls

**Files:** `ai_price_card.json`, all `aa_index.caveat` fields; `FUNNEL_OUTPUT_2026-07-31.txt`

The funnel’s stated formula is:

> “value score = AA index points per (USD per 1k calls, mid shape)”

But the scores being divided by default token-cost profiles are explicitly not scores for the stated production configuration:

- `claude-haiku-4-5-20251001`:
  > “benchmarked in reasoning mode; app runs default”
- `claude-sonnet-4-6`:
  > “max-effort score; app runs default effort”
- `gpt-5.6-luna`:
  > “51.24 at MAX effort but 33 at LOW”
- `gpt-5.6-terra`:
  > “max-effort score”

This makes the funnel’s comparative “value” metric invalid as an economics measure of the deployed modes. It combines:

1. capability at maximum/reasoning effort, and
2. price at an assumed ordinary request token profile.

For reasoning models, higher effort can change output/reasoning-token consumption substantially, and potentially latency, empty-response behavior, and retry rates. The model-card caveats acknowledge the mismatch, but the output still presents the resulting rankings as meaningful economics.

For example, if Luna actually runs at the documented low-effort score of **33**, rather than 51.24, its haiku/triage value score becomes:

\[
33 / 0.742 = 44.47
\]

not:

\[
51.24 / 0.742 = 69.06
\]

It would remain economically attractive on the supplied numbers, but the reported magnitude of the opportunity is overstated by approximately **55%**:

\[
69.06 / 44.47 - 1 = 55.3\%
\]

**Required correction:** Do not rank models using an AA score unless the card pins the same effort/reasoning mode used in the cost profile and golden-set run. Store at minimum: `effort`, max reasoning/output budget, actual measured input/output/reasoning-token distributions, and an effort-matched benchmark score where one exists.

---

### [BLOCKER] The claimed cost rails do not bound worst-case AI spend

**Files:** `ai_price_card.json`; `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addenda 2, 7, and 8

The decision note says:

> “Existing cost rails stay (ceilings, deliver-then-charge, spend log per provider).”

However, neither the price card nor the funnel contains an enforceable cost-bound mechanism. The material provides unit prices and a freshness rule, but no evidence of:

- per-request maximum input, output, and reasoning-token limits;
- a hard per-task/per-user/per-day monetary budget;
- retry limits and retry cost accounting;
- fallback-chain maximum attempt count;
- a prohibition on a failed/empty response consuming the full token budget;
- provider spend caps or alert thresholds;
- a monthly EUR cap for Scaleway’s free-tier exit;
- a maximum total cost for golden-set, shadow, heartbeat, and ban-drill traffic;
- reservation for price, FX, or provider-billing variance.

This is particularly material because the card itself records:

> “reasoning-burn risk observed 31 Jul (Terra empty reply at 4k budget)”

An empty reply can still incur a large token charge. A nominal “cost per successful call” is not a hard rail if failed calls, retries, and fallbacks remain chargeable.

**Required correction:** A cost rail must be executable, not merely a spend-log/reconciliation practice. For each task, define and enforce: maximum request count, retry count, fallback count, input/output/reasoning-token budget, and currency budget. The maximum charge should be computable before a request begins.

---

### [MAJOR] `golden_set` is model-wide, not tier- and effort-specific, so it cannot support the claimed binary gate

**Files:** `ai_price_card.json`, `policy.capability_floor`, all `golden_set` blocks; `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 8

The card says:

> “the golden set (at a PINNED effort level) is a binary accept/reject on OUR use cases”

Yet the actual register records only one broad status per model. For Mistral Medium:

> “11/11 JSON incl. 2/2 vision (small sample)”

That does not show a separately passing result for each of `haiku`, `triage`, `sonnet`, and `vision`, nor does it record the effort level, sampling settings, prompt version, evaluator version, date range, or failure criteria.

The funnel then treats this single broad status as sufficient to make Mistral the eligible winner for the `sonnet` tier:

> “eligible winner mistral-medium-3.5-128b vs sitting claude-sonnet-4-6”

That conclusion is insufficiently supported. A model that passed two vision examples and eleven JSON cases may be a valid standby, but it has not thereby demonstrated parity for Sonnet-class advert-copy quality or every tier’s real use cases.

The card’s own policy requires an effort level to be pinned, but the provided `golden_set` records do not contain an `effort` field. This is an internal implementation gap against the stated policy.

**Required correction:** Record gates as `(model, task tier, prompt/eval version, effort/reasoning budget, sampling parameters)` rather than as one model-wide boolean. The cost funnel may only select a model for a tier where that exact tuple has passed.

---

### [MAJOR] The procurement-switch rule conflicts with the stated “never because a rival got cheaper” stability ruling

**Files:** `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 3 versus Addendum 8; `ai_price_card.json`, `policy.anti_jitter`

Addendum 3 says:

> “Switch models on MEASURED FAILURE or FORCED EXIT only — never because a rival got cheaper this month.”

The new anti-jitter policy says:

> “A PROCUREMENT switch requires ... >=30% sustained cost saving at an equal-or-better gate result”

And the funnel explicitly proposes a future price-driven Sonnet switch:

> “+42% cost delta · MEETS the 30% materiality bar — hold for 2 card refreshes (>=30 days), then convene the funnel”

These are substantively different policies. The latter allows a price-led switch after 30 days; the former forbids a price-led switch altogether. The text says Addendum 3 still governs switching, but Addendum 8 supplies a contradictory switch criterion rather than merely a reporting threshold.

This is not a semantic issue. Under the supplied numbers, it changes whether Mistral Medium can replace Sonnet absent measured failure or forced exit.

**Required correction:** David/System Engineer should explicitly choose one rule:

1. **Stability-first:** price changes never trigger a production switch, only update standby intelligence; or
2. **Cost-first after qualification:** a sufficiently material, sustained, task-specific saving may trigger a switch.

If option 2 is intended, Addendum 3 must be expressly superseded or narrowed.

---

### [MAJOR] The 30% threshold is not a sufficient economic decision test because it ignores absolute savings and switching cost

**Files:** `ai_price_card.json`, `policy.anti_jitter`; `FUNNEL_OUTPUT_2026-07-31.txt`

A percentage-only threshold can authorize a switch that saves trivially little money while imposing meaningful engineering, validation, prompt-retuning, and behavioral-drift costs.

For the Sonnet example, the nominal midpoint saving is:

\[
\$9.90000 - \$5.71725 = \$4.18275 \text{ per 1,000 calls}
\]

Whether that is material depends on annual call volume:

| Sonnet-tier volume | Nominal saving from Sonnet → Mistral Medium |
|---:|---:|
| 1,000 calls/month | $4.18/month |
| 10,000 calls/month | $41.83/month |
| 100,000 calls/month | $418.28/month |

At low startup volumes, a 42.25% unit saving may not repay even one golden-set rerun, shadow period, prompt tuning cycle, or incident investigation. Conversely, a 20% decrease at high volume could be worth more than the threshold permits.

**Required correction:** Require both a relative threshold and an absolute projected saving over a defined period, net of switch cost and contingency reserve. Example: “≥30% unit saving **and** projected net saving ≥$X over 90 days after evaluation, migration, and shadow costs.”

---

### [MAJOR] EUR conversion is an estimate, not a rail; the documented 5% buffer does not protect against the relevant spend risks

**Files:** `ai_price_card.json`, `fx`; `FUNNEL_OUTPUT_2026-07-31.txt`

The card correctly warns:

> “a USD rail cannot hard-bound unbuffered EUR spend”

However, the funnel then uses a fixed EUR/USD rate of 1.10 plus 5%:

\[
1.10 \times 1.05 = 1.155
\]

This is suitable for indicative comparison, but not for a hard dollar budget. Actual exposure includes:

- EUR/USD movement exceeding 5%;
- card/payment-provider FX spread;
- VAT, if applicable;
- vendor price changes denominated in EUR;
- a free-tier credit ending or monthly cap being exceeded;
- a difference between published rate and billed rate;
- rounding and token-accounting differences.

The Scaleway card explicitly admits the crucial rate has not been invoice-verified:

> “console rate UNOBSERVABLE while the free tier nets billing to EUR 0”

Therefore the most cost-sensitive conclusion—whether Medium is a viable economic replacement—rests on a published EUR rate rather than a billable invoice rate.

**Required correction:** Treat Scaleway costs as `EUR estimate` until billed consumption is observed. Set budgets and alerts in EUR, not converted USD; use the FX conversion only for cross-provider comparison. Record the free-tier monthly cap, expiry, and marginal post-credit rate.

---

### [MAJOR] Source quality is insufficient for the claimed “single source of price truth”

**Files:** `ai_price_card.json`, provider `source` fields

Anthropic pricing cites:

> “metacto.com Anthropic pricing”

That is not identified as Anthropic’s own price page, contract, invoice, or API billing record. The Scaleway source is a public pricing page, but the card itself states it has not been reconciled against billed usage. OpenAI cites a first-party documentation URL, but the material does not preserve the quoted page, price table, plan, region, cached-token treatment, or billing evidence.

A “single source of internal truth” is reasonable. Calling it “price truth” is stronger than the evidence supports, especially when it will drive procurement decisions.

**Required correction:** Record a first-party source URL and captured price text/version for each model, plus invoice reconciliation status. A third-party pricing page may be a discovery source, not the authoritative cost source.

---

### [MINOR] The label “+42% cheaper” is mathematically imprecise, although the underlying midpoint calculation is correct

**File:** `FUNNEL_OUTPUT_2026-07-31.txt`

The report says:

> “Mistral Medium is +42% cheaper”

Using the supplied prices and the documented FX buffer, Mistral Medium costs **42.25% less** than Claude Sonnet at the midpoint. “+42% cheaper” is colloquial and can be misread.

The correct calculation is:

\[
\text{Sonnet midpoint} = \frac{(500 \times 3 + 120 \times 15) + (2000 \times 3 + 700 \times 15)}{2 \times 10^6} \times 1000
\]

\[
= \frac{3.30 + 16.50}{2} = \$9.90 / 1{,}000\ calls
\]

For Mistral Medium:

\[
\text{Raw EUR midpoint} = \frac{€1.65 + €8.25}{2} = €4.95 / 1{,}000\ calls
\]

\[
\text{Buffered USD midpoint} = €4.95 \times 1.155 = \$5.71725 / 1{,}000\ calls
\]

\[
\text{Saving} = \frac{9.90 - 5.71725}{9.90} = 0.4225 = 42.25\%
\]

Equivalently, Sonnet is **73.16% more expensive than** Mistral Medium:

\[
\frac{9.90}{5.71725} - 1 = 73.16\%
\]

**Correction:** State “Mistral Medium is 42.25% lower cost than Sonnet at this token mix” or “Sonnet costs 73.16% more.”

---

### [PRAISE] The funnel arithmetic is internally correct for the stated nominal token shapes and FX assumptions

**Files:** `ai_price_card.json`; `FUNNEL_OUTPUT_2026-07-31.txt`

I re-derived the displayed cost and value figures. They are correct, subject to the assumptions explicitly stated in the card.

The midpoint for the standard `500/120` to `2000/700` shapes is:

\[
(1250\ input,\ 410\ output)
\]

The midpoint for vision is:

\[
(10{,}750\ input,\ 1{,}200\ output)
\]

The EUR conversion factor used is:

\[
1.10 \times 1.05 = 1.155
\]

#### Re-derived nominal unit economics

All figures below are **per call / per 1,000 calls**. “Mid” is the arithmetic midpoint of the stated low and high token shapes.

##### Haiku and triage shapes: 500/120 low, 2,000/700 high

| Provider/model | Low per call | Mid per call | High per call | Low / 1k | Mid / 1k | High / 1k |
|---|---:|---:|---:|---:|---:|---:|
| OpenAI Luna | $0.000244 | $0.000742 | $0.001240 | $0.244 | $0.742 | $1.240 |
| Anthropic Haiku | $0.001100 | $0.003300 | $0.005500 | $1.100 | $3.300 | $5.500 |
| Scaleway Medium, raw | €0.001650 | €0.004950 | €0.008250 | €1.650 | €4.950 | €8.250 |
| Scaleway Medium, USD-buffered | $0.001906 | $0.005717 | $0.009529 | $1.906 | $5.717 | $9.529 |

The reported value scores are also correct:

\[
\text{Luna} = 51.24 / 0.742 = 69.06
\]

\[
\text{Haiku} = 29.58 / 3.30 = 8.96
\]

\[
\text{Medium} = 29.95 / 5.71725 = 5.24
\]

##### Sonnet shapes: 500/120 low, 2,000/700 high

| Provider/model | Low per call | Mid per call | High per call | Low / 1k | Mid / 1k | High / 1k |
|---|---:|---:|---:|---:|---:|---:|
| OpenAI Terra | $0.002440 | $0.007420 | $0.012400 | $2.440 | $7.420 | $12.400 |
| Scaleway Medium, USD-buffered | $0.001906 | $0.005717 | $0.009529 | $1.906 | $5.717 | $9.529 |
| Anthropic Sonnet | $0.003300 | $0.009900 | $0.016500 | $3.300 | $9.900 | $16.500 |

Reported value scores:

\[
\text{Terra} = 54.95 / 7.42 = 7.41
\]

\[
\text{Medium} = 29.95 / 5.71725 = 5.24
\]

\[
\text{Sonnet} = 47.21 / 9.90 = 4.77
\]

##### Vision shapes: 1,500/1,200 low, 20,000/1,200 high

| Provider/model | Low per call | Mid per call | High per call | Low / 1k | Mid / 1k | High / 1k |
|---|---:|---:|---:|---:|---:|---:|
| OpenAI Luna | $0.001740 | $0.003590 | $0.005440 | $1.740 | $3.590 | $5.440 |
| Anthropic Haiku | $0.007500 | $0.016750 | $0.026000 | $7.500 | $16.750 | $26.000 |
| Scaleway Medium, raw | €0.011250 | €0.025125 | €0.039000 | €11.250 | €25.125 | €39.000 |
| Scaleway Medium, USD-buffered | $0.012994 | $0.029019 | $0.045045 | $12.994 | $29.019 | $45.045 |

Reported value scores:

\[
\text{Luna} = 51.24 / 3.59 = 14.27
\]

\[
\text{Haiku} = 29.58 / 16.75 = 1.77
\]

\[
\text{Medium} = 29.95 / 29.019375 = 1.03
\]

The output’s cost ranges and displayed value scores are therefore arithmetically consistent.

---

### [MAJOR] The claimed swap savings are nominal only; retries, fallback behavior, and effort burn can reverse them

**Files:** `FUNNEL_OUTPUT_2026-07-31.txt`; `ai_price_card.json`; `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 5

At stated midpoint costs, the nominal differences versus sitting models are:

| Tier | Proposed model | Sitting model | Nominal midpoint change per 1k calls | Percent change |
|---|---|---|---:|---:|
| Haiku / triage | Luna | Haiku | saves $2.558 | **77.5% lower** |
| Haiku / triage | Medium | Haiku | costs $2.417 | **73.2% higher** |
| Sonnet | Medium | Sonnet | saves $4.183 | **42.25% lower** |
| Sonnet | Terra | Sonnet | saves $2.480 | **25.05% lower** |
| Vision | Luna | Haiku | saves $13.160 | **78.57% lower** |
| Vision | Medium | Haiku | costs $12.269 | **73.25% higher** |

However, a low-price lane is not necessarily a low-cost lane if it has a higher failure, refusal, malformed-JSON, retry, or fallback rate. For example, Luna saves $2.558/1,000 midpoint haiku calls nominally. But if it materially increases failed workflows that are retried on Haiku, the effective cost is:

\[
C_{\text{effective}} =
C_{\text{Luna}} +
p_{\text{retry}} \times (C_{\text{Luna}} + C_{\text{Haiku}})
\]

The price card does not contain measured success rates or retry rates. The documented “Terra empty reply at 4k budget” is direct evidence that this is not theoretical.

**Required correction:** Record effective cost per accepted completion, not merely cost per API attempt, using real production or controlled-shadow telemetry. Include all fallback and retry calls in the provider and task cost.

---

### [MAJOR] The model-price card omits material billable dimensions, especially for vision and reasoning

**Files:** `ai_price_card.json`; `FUNNEL_OUTPUT_2026-07-31.txt`

The card only models input and output token rates. That may be incomplete for the intended use:

- Vision usage may include image-token conversion, image-resolution rules, preprocessing, or modality-specific charges.
- Reasoning modes may consume hidden or separately counted reasoning tokens.
- Cached input, prompt caching, batch processing, priority tiers, and regional pricing may differ from ordinary input/output rates.
- Tool calls, web/search features, structured-output constraints, and storage can have separate charges, depending on provider.
- The vision shape assumes 1,200 output tokens in both low and high cases, but does not state whether image payload/token conversion is included in the 1,500 or 20,000 input tokens.

The funnel’s most dramatic result is the vision-Luna value advantage. That result is especially sensitive to whether the image component is represented correctly.

**Required correction:** State exactly what the token profiles include and exclude. For vision, collect actual billed token usage for representative image sizes and resolutions. For reasoning models, separately log visible output and billed reasoning tokens.

---

### [QUESTION] What is the exact definition, publisher, and reproducible dataset for “AA Intelligence Index v4.1”?

**Files:** `ai_price_card.json`, all `aa_index` blocks; `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 8

The card cites:

> “benchmarklist.com AA v4.1 leaderboard”

I cannot independently verify the existence, methodology, score values, model variants, effort settings, or date of this leaderboard from the material provided or from my pre-supplied knowledge.

The quoted scores are:

| Model/variant cited | Quoted AA v4.1 score | Independent verification status |
|---|---:|---|
| Haiku 4.5 Reasoning | 29.58 | Not independently verifiable |
| Sonnet 4.6 Adaptive Reasoning, Max Effort | 47.21 | Not independently verifiable |
| Mistral Medium 3.5 | 29.95 | Not independently verifiable |
| Luna, Max Effort | 51.24 | Not independently verifiable |
| Terra, Max Effort | 54.95 | Not independently verifiable |

**Question for the Author:** Is the benchmark source retained as a dated export/screenshot/data artifact, including methodology and model invocation settings? A URL and date alone are not sufficient for a score used as the formal ranking numerator, particularly where the benchmark variants differ from production modes.

---

### [QUESTION] What live price evidence supports each claimed price, and what plan/region/token category does it cover?

**File:** `ai_price_card.json`

I cannot certify any listed 31 July 2026 price against independently verified live vendor data. My confidence in any assertion that a particular supplied figure is wrong is therefore **low**; I do not have sufficient evidence to call a figure factually incorrect rather than merely unsupported.

My knowledge date for reliable public-rate comparison is pre-31-July-2026 and predates several named products. Specifically:

| Entry | Listed price per M input/output | My independent verdict | Confidence / knowledge boundary |
|---|---:|---|---|
| Claude Haiku 4.5 | $1 / $5 | Cannot verify | High confidence that this is beyond my reliable pricing knowledge; no conclusion on correctness |
| Claude Sonnet 4.6 | $3 / $15 | Cannot verify | Same |
| Mistral Medium 3.5 via Scaleway | €1.50 / €7.50 | Cannot verify | Same; additionally invoice evidence is explicitly absent |
| GPT-5.6 Luna | $0.20 / $1.20 | Cannot verify | Same |
| GPT-5.6 Terra | $2 / $12 | Cannot verify | Same |

I do note that the reported $3/$15 Sonnet rate resembles a historically familiar Anthropic price band for earlier Sonnet offerings, but that is **not evidence** that it is the correct price for the named `claude-sonnet-4-6` model in 2026.

**Question for the Author:** Can the register attach the primary vendor price URL, product-plan/region, retrieval timestamp, captured rate text, and invoice-reconciliation status for every record? That would make later review possible without relying on a mutable third-party page.

---

### [MINOR] The “Sonnet 5 intro $2/$10 ends 31 Aug 2026” risk is recorded but not priced into a forward decision

**File:** `ai_price_card.json`, `claude-sonnet-4-6.note`

The card records:

> “Sonnet 5 intro $2/$10 ends 31 Aug 2026 — dated upgrade decision, not automatic.”

This is a good warning, but it is not operationalized. There is no entry for that model, no post-intro expected price, no expiry event owner, and no scenario showing how a price change affects the funnel. Similar risks apply to the stated recent OpenAI “80% cut 30 Jul” event and the Scaleway free tier.

**Required correction:** Maintain expiry/repricing fields with an owner and deadline, and compute the post-expiry scenario before the temporary price is allowed to influence a procurement decision.

---

### [PRAISE] The process correctly distinguishes a value ranking from a quality gate, and correctly resists automatic production changes

**Files:** `ai_price_card.json`, `policy.funnel`; `FUNNEL_OUTPUT_2026-07-31.txt`

The architecture has several sound elements:

- Price/capability ranking does not automatically equal a deployment decision.
- Luna and Terra are correctly marked ineligible while their golden sets remain pending.
- The output explicitly identifies the potential economic prize “behind the gate,” rather than treating a benchmark score as production evidence.
- The card recognizes vendor events, deprecations, bans, and stale pricing as triggers for review.
- The explicit warning that “a pricing page is a claim, an invoice is a fact” is correct FinOps discipline.

The main issue is not the concept of funnel-plus-gate; it is the insufficient fidelity of the inputs and the unresolved contradiction in the subsequent switch policy.

---

### [MINOR] RG-0018 and RG-0019 validate metadata freshness and lane matching, not economic correctness

**Files:** `ai_price_card.json`, `policy.update_triggers`; `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 8

RG-0018 detects a card older than 45 days or missing a wired model. RG-0019 compares `active_lane` with live `/flags`, and later may compare a breaker block.

These are useful configuration-drift controls, but they do not establish:

- that a source price is still correct;
- that the billed rate matches the published rate;
- that the live model ID matches the card’s model ID for every tier;
- that fallback chain ordering and retry behavior match the cost model;
- that the card’s effort, token caps, or prompt version match production;
- that the model’s gate passed for the task receiving traffic.

Also, a singular:

> `active_lane: "anthropic"`

cannot fully describe a per-tier routing system with different primary and fallback models. A provider-level match can be green while a specific tier routes to an unintended model or effort setting.

**Required correction:** Expand configuration validation to compare the effective runtime tuple per tier: provider, model ID, effort, token caps, retry policy, fallback order, and gate version.

---

## Decision-gate assessment

The proposed funnel is directionally sound but is not yet sufficient as a procurement control.

### What is accurate and useful

1. **Value proposes, gate disposes** is appropriate.
2. A tested standby path is more valuable than an untested low-price alternative.
3. Anti-jitter is a legitimate response to model churn and prompt-behavior drift.
4. The 30-day/two-refresh concept is better than chasing a one-day price change.
5. The card’s explicit source/date/currency fields are a strong start.

### What is missing before it can safely govern spend

1. **Comparable operating configurations.** Benchmark and golden-set effort must equal production effort.
2. **Task-specific gates.** A model-wide pass is not evidence for every tier.
3. **Effective cost.** Include retries, failures, fallbacks, and reasoning tokens.
4. **Hard spend controls.** Unit-price visibility is not a budget.
5. **Absolute economics.** The decision must account for volume and switching cost.
6. **Invoice truth.** Published rates need reconciliation to billed rates.
7. **Policy precedence.** Price-driven switching must either be permitted or forbidden; the documents currently say both.
8. **Versioned evidence.** Mutable URLs are inadequate for a formal “truth” register.

---

## The three findings the System Engineer should discuss first

1. **[BLOCKER] Effort mismatch invalidates the value ranking.** The funnel ranks max/reasoning benchmark scores against default-mode cost assumptions. Decide whether every production tier will have an effort-matched benchmark, golden set, and token profile before using the ranking for procurement.

2. **[BLOCKER] Cost rails are not hard limits.** Establish enforceable maximum token/reasoning/retry/fallback budgets and account for failed calls. The known Terra empty-response behavior demonstrates why nominal per-call pricing is not a spend bound.

3. **[MAJOR] Resolve the governing switch policy.** Addendum 3 says never switch because another vendor became cheaper; Addendum 8 permits a ≥30% sustained price-led procurement switch. The System Engineer must choose which rule governs.

---

## What I could not verify

I could not independently verify from the supplied material:

- any vendor’s live 31 July 2026 price;
- whether the listed model identifiers exist, are available to this account, or map to the cited price tiers;
- whether prices include/exclude cached input, reasoning tokens, image processing, batch discounts, regional differences, VAT, or other billable dimensions;
- the AA Intelligence Index v4.1 publisher, methodology, score values, model variants, or benchmark conditions;
- the claimed Scaleway console/free-tier behavior or the eventual invoice rate;
- the contents or results of the golden-set runs beyond the brief descriptions supplied;
- the actual runtime fallback, retry, token-cap, effort, and spend-limit implementation;
- RG-0018/RG-0019 implementation or whether they truly block deployment/operation rather than merely report red status.
