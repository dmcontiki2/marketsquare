# Independent Peer Review — 2026-07-31-0646

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: cost · Author: Claude · System Engineer: David*

**Scope:**
  - COST_FACTS_AI_SWAP_2026-07-31.md (3,842 chars)
  - ai_provider.py (9,805 chars)
  - AI_VENDOR_STRATEGY_DECISION_2026-07-11.md (14,056 chars)

**Usage:** 7678 in / 8346 out tokens · actual cost ≈ $0.1155

---

# Peer Review — FinOps / Cost Review

**Scope reviewed:** `COST_FACTS_AI_SWAP_2026-07-31.md`, `ai_provider.py`, and `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`.

**Important context:** the platform is pre-launch. The supplied call shapes are code-derived estimates, not observed usage. The following calculations are therefore scenario estimates, not forecasts or measured unit economics.

## Cost arithmetic

### Assumptions used

Text calls:

- **Low:** 0.5k input + 120 output tokens
- **High:** 2.0k input + 700 output tokens

Vision calls:

- **Low:** 1 photo × 1.1k image tokens + 1.2k output tokens
- **High:** 12 photos × 1.6k = 19.2k image tokens + 1.2k output tokens
- Excludes an unspecified text/system prompt token count. Thus the vision numbers are lower bounds.

Formula:

```text
cost/call = (input_tokens / 1,000,000 × input_price)
          + (output_tokens / 1,000,000 × output_price)
```

The Scaleway USD conversion supplied by the Author is used: **€1 = approximately $1.10**.

---

## Unit cost by lane and task tier

### Text tasks: `haiku`, `triage`, and ordinary text-shaped calls

| Provider / model | Price per Mtok in/out | Low cost / call | High cost / call | Cost / 1,000 calls |
|---|---:|---:|---:|---:|
| Anthropic Haiku 4.5 | $1 / $5 | $0.00110 | $0.00550 | $1.10–$5.50 |
| Scaleway Mistral Medium 3.5 | €1.50 / €7.50 | €0.00165 | €0.00825 | €1.65–€8.25 |
| Scaleway Mistral Medium 3.5 | ~$1.65 / ~$8.25 | $0.001815 | $0.009075 | $1.815–$9.075 |
| OpenAI GPT-5.6 Luna | $0.20 / $1.20 | $0.000244 | $0.001240 | $0.244–$1.240 |

Example, Haiku at the high text shape:

```text
(2,000 / 1,000,000 × $1) + (700 / 1,000,000 × $5)
= $0.002 + $0.0035
= $0.0055/call
```

### Paid deep-dives: `sonnet` tier

| Provider / model | Price per Mtok in/out | Low cost / call | High cost / call | Cost / 1,000 calls |
|---|---:|---:|---:|---:|
| Anthropic Sonnet 4.6 | $3 / $15 | $0.00330 | $0.01650 | $3.30–$16.50 |
| Scaleway Mistral Medium 3.5 | €1.50 / €7.50 | €0.00165 | €0.00825 | €1.65–€8.25 |
| Scaleway Mistral Medium 3.5 | ~$1.65 / ~$8.25 | $0.001815 | $0.009075 | $1.815–$9.075 |
| OpenAI GPT-5.6 Terra | $2 / $12 | $0.002440 | $0.012400 | $2.440–$12.400 |

### Vision tier

This is the specific `vision` mapping in `ai_provider.py`: Haiku on Anthropic, Mistral Medium on Scaleway, Luna on OpenAI.

| Provider / model | Vision lower-bound cost / call | Vision upper-bound cost / call | Cost / 1,000 calls |
|---|---:|---:|---:|
| Anthropic Haiku 4.5 | $0.00710 | $0.02520 | $7.10–$25.20 |
| Scaleway Mistral Medium 3.5 | €0.01065 | €0.03780 | €10.65–€37.80 |
| Scaleway Mistral Medium 3.5 | ~$0.011715 | ~$0.041580 | ~$11.715–$41.580 |
| OpenAI GPT-5.6 Luna | $0.001660 | $0.005280 | $1.660–$5.280 |

Example, high-end Haiku vision:

```text
Input: 12 × 1,600 = 19,200 image tokens
Output: 1,200 tokens

(19,200 / 1,000,000 × $1) + (1,200 / 1,000,000 × $5)
= $0.0192 + $0.006
= $0.0252/call
```

This matters because a high-photo vision flow costs roughly **4.6×** the high ordinary Haiku text call, even before including text prompt tokens.

---

# Findings

## [BLOCKER] The supplied Scaleway price makes Mistral Medium *more expensive*, not “~40% of Haiku”

**Evidence**

- `COST_FACTS_AI_SWAP_2026-07-31.md`: Mistral Medium is priced at **€1.50 / €7.50 per Mtok**, approximately **$1.65 / $8.25**.
- The same file and `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 4, state that Mistral Medium achieved parity “at **~40% of Haiku’s cost**.”
- Haiku is listed at **$1 / $5 per Mtok**.

At the supplied USD rates, Mistral Medium costs:

```text
Input:  $1.65 / $1.00 = 1.65× Haiku
Output: $8.25 / $5.00 = 1.65× Haiku
```

Therefore Mistral Medium costs **165% of Haiku**, or **65% more**, at every identical input/output token mix. This is not a nuanced result dependent on token mix, because both input and output prices have exactly the same 1.65 multiplier.

For the stated text-call range:

```text
Haiku:          $1.10–$5.50 / 1,000 calls
Mistral Medium: $1.815–$9.075 / 1,000 calls
Difference:     +$0.715–+$3.575 / 1,000 calls
```

For vision:

```text
Haiku:          $7.10–$25.20 / 1,000 calls
Mistral Medium: $11.715–$41.580 / 1,000 calls
Difference:     +$4.615–+$16.380 / 1,000 calls
```

**Impact**

The central cost justification for the designated Scaleway swap-out is false under the prices in the submitted cost sheet. A forced Anthropic exit may still make Mistral Medium a valid continuity option, but it is not a cost-saving option at these rates.

**Required discussion**

Resolve one of these facts before treating the lane as a FinOps swap:

1. The listed Scaleway price is wrong;
2. the historic “40%” result used a different Scaleway model or price card;
3. the $/€ conversion is wrong by an implausibly large amount; or
4. Mistral Medium is a quality/availability standby, not a cheap lane.

---

## [MAJOR] The claimed “full swap” economics differ sharply by tier; Mistral saves on paid Sonnet work but increases free and vision spend

A full provider swap means different things because `TASK_MODEL` maps the abstract task tiers differently:

```python
"anthropic": {"haiku": Haiku, "sonnet": Sonnet, "vision": Haiku, "triage": Haiku}
"scaleway":  {"haiku": Medium, "sonnet": Medium, "vision": Medium, "triage": Medium}
"openai":    {"haiku": Luna, "sonnet": Terra, "vision": Luna, "triage": Luna}
```

### Per-1,000-call swap effects versus current Anthropic lane

| Task type | Scaleway Medium vs current Anthropic | OpenAI vs current Anthropic |
|---|---:|---:|
| Free text / triage | **Costs $0.715–$3.575 more** | Saves $0.856–$4.260 |
| Paid deep-dives | Saves $1.485–$7.425 | Saves $0.860–$4.100 |
| Vision | **Costs $4.615–$16.380 more** | Saves $5.440–$19.920 |

Thus:

- Scaleway is cheaper only where it replaces **Sonnet**, not where it replaces Haiku.
- OpenAI is the cheapest lane on the supplied nominal token prices across all listed application tiers.
- Neither fact is sufficient to authorize a switch: OpenAI has no provisioned key and no completed golden-set gate; Scaleway’s documented preconditions remain open.

### Scenario totals: free drafts + paid deep-dives

These exclude vision, triage, retries, fallbacks, probes, and all non-draft free call sites. They are therefore not platform spend estimates.

| Free drafts / month | Paid deep-dives / month | Anthropic current lane | Scaleway full lane | OpenAI full lane |
|---:|---:|---:|---:|---:|
| 1,000 | 100 | $1.43–$7.15 | $2.00–$9.98 | $0.49–$2.48 |
| 1,000 | 1,000 | $4.40–$22.00 | $3.63–$18.15 | $2.68–$13.64 |
| 10,000 | 100 | $11.33–$56.65 | $18.33–$91.66 | $2.68–$13.64 |
| 10,000 | 1,000 | $14.30–$71.50 | $19.97–$99.83 | $4.88–$24.80 |
| 100,000 | 100 | $110.33–$551.65 | $181.68–$908.16 | $22.64–$125.24 |
| 100,000 | 1,000 | $113.30–$566.50 | $183.33–$916.58 | $24.84–$136.40 |

Example: 10,000 free drafts and 1,000 deep-dives, high-shape case:

```text
Anthropic:
10 × $5.50 + 1 × $16.50 = $71.50

Scaleway:
10 × $9.075 + 1 × $9.075 = $99.825

OpenAI:
10 × $1.24 + 1 × $12.40 = $24.80
```

**Important qualification:** because the models may emit different token counts, the price-sheet comparison assumes the same input and output token profile across providers. That assumption is especially unsafe for reasoning-capable GPT models and for JSON repair loops.

---

## [MAJOR] The stated cost rails cannot be verified as hard spend bounds from `ai_provider.py`

**Evidence**

`COST_FACTS_AI_SWAP_2026-07-31.md` says:

> “$100/day platform hard ceiling · $0.50/user/day ... per-call spend log with real tokens”

But `ai_provider.py` states:

> “Spend logging is injected by the caller (keeps DB out of this module).”

The supplied module contains no:

- daily-budget read or write;
- atomic reservation before an API call;
- user-level budget enforcement;
- maximum number of provider attempts;
- retry budget;
- spending calculation;
- provider-side cost reconciliation;
- alert or fail-closed behavior when usage metadata is absent.

The module makes up to three sequential provider attempts per logical request:

```python
res = fn(messages, model, ...)
if not res.ok:
    for alt in [p for p in ADAPTERS if p != prov]:
        r2 = ADAPTERS[alt](...)
```

A provider can consume tokens yet return a timeout, 429, malformed payload, or empty content. In that case, its token usage is not returned in the final `AIResult` when a later provider succeeds. The caller receives only the winning attempt’s usage and provider:

```python
if r2.ok: return r2
```

**Impact**

The logging and budget system can undercount actual vendor spend exactly during degraded operation, when the fallback chain is active. A “$100/day hard ceiling” is not a demonstrated hard ceiling unless it accounts for attempted calls and reserves spend before dispatch.

**Cost exposure**

At the maximum text caps, a single logical request can plausibly cause up to three billable attempts. Using the current active Anthropic order:

```text
Anthropic Haiku high text attempt:     $0.00550
OpenAI Luna high text attempt:         $0.00124
Scaleway Medium high text attempt:     $0.009075
Three-attempt total:                   $0.015815
```

For a vision request at the stated high image shape:

```text
Anthropic Haiku:                       $0.02520
OpenAI Luna:                           $0.00528
Scaleway Medium:                       $0.04158
Three-attempt total:                   $0.07206
```

Those are still individually small, but failure storms are precisely where a budget rail needs to be stricter than normal-path economics.

---

## [MAJOR] Fallback-attempt cost and unavailable-usage accounting are structurally invisible in the returned interface

**Evidence**

`AIResult` contains only one token pair:

```python
class AIResult:
    text: str; in_tokens: int|None; out_tokens: int|None; provider: str; model: str; ok: bool=True
```

Adapters return `None` token counts on exceptions:

```python
except Exception:
    return AIResult("", None, None, "...", model, ok=False)
```

The system does not preserve a list of attempts, HTTP statuses, request IDs, latency, errors, or usage for failed calls. It also suppresses exceptions entirely.

**Impact**

The system cannot distinguish, at the spend-log seam:

- API key absent, which should be zero vendor cost;
- pre-response network failure, probably zero vendor cost;
- provider timeout after work began, potentially billable;
- 200 response with an invalid or empty completion, potentially billable;
- 429 that might include charged input work depending on vendor behavior;
- fallback success after one or two charged failures.

This is not only an observability gap: it makes vendor costs difficult to reconcile to invoices and creates misleading per-provider unit-cost reports.

**Metric needed**

Record one immutable row per provider **attempt**, not only per completed logical request:

```text
logical_request_id
attempt_number
provider / model
task
request timestamp
HTTP status / exception type
elapsed time
input tokens, output tokens if received
estimated cost
vendor request ID
whether final successful result
whether caller was charged / credited
```

The platform-level and user-level budget should use attempted-cost reservations or a conservative estimated maximum; later reconcile to actual token usage.

---

## [MAJOR] The `max_tokens` caps do not bound cost tightly enough for reasoning models, and output cost can drift without an application-level token budget

**Evidence**

`COST_FACTS_AI_SWAP_2026-07-31.md` identifies:

> “Reasoning-token burn: GPT-5.6 and Qwen-class models consume output budget on thinking ... a silent per-call cost multiplier if unwatched.”

`ai_provider.py` applies `max_completion_tokens` to GPT-5 models:

```python
_tokkey = "max_completion_tokens" if model.startswith(("gpt-5","o")) else "max_tokens"
```

The document does not establish whether the vendor bills hidden reasoning tokens as output tokens, whether they are included in `completion_tokens`, or whether the stated “max completion” parameter caps visible output plus reasoning jointly.

**Impact**

The Luna figures are very attractive nominally, but the implementation and cost sheet do not establish that Luna’s output token accounting is comparable with Haiku’s. The cited Terra empty-reply incident is evidence that this is an active, not theoretical, risk.

**Metric needed**

By model and task, monitor:

```text
input tokens
reported completion tokens
reasoning / cached / audio / image token fields if supplied
visible output character count
completion-to-visible-output ratio
empty-result rate
JSON-validation failure rate
attempts per successful completion
estimated and invoice-reconciled cost
```

Alert when output tokens per visible character, empty-result rate, or retry rate departs materially from the golden-set baseline.

---

## [MAJOR] Vision cost is not covered by the provided per-user cap evidence and can dominate ordinary text traffic

**Evidence**

`COST_FACTS_AI_SWAP_2026-07-31.md` specifies:

> “Vision call: 1–12 photos resized ≤1568px (~1.1–1.6k tokens per image) + prompt; out ≤ 1200.”

The same document claims a `$0.50/user/day` rail, but provides no shown enforcement and no per-user maximum count of vision calls, image count, or uploaded-image reprocessing policy.

**Impact**

At current Haiku prices, one maximum-shape vision call is estimated at **$0.0252**, excluding prompt tokens. Twenty such calls are approximately:

```text
20 × $0.0252 = $0.504/user/day
```

This reaches the claimed user-day ceiling before accounting for any ordinary draft, rewrite, KYC retry, fallback, or prompt tokens.

At the supplied Scaleway Medium price, the analogous amount is reached after roughly 12 maximum-shape calls:

```text
12 × $0.04158 = $0.49896/user/day
```

The user-day rail is therefore not credible as a hard cap unless it prevents a subsequent call before dispatch and counts prior failed/fallback attempts.

**Metric needed**

Track per user/day:

- image count submitted;
- unique image hashes versus reprocessed images;
- vision calls;
- vision input tokens;
- successful and failed vision attempts;
- cost before and after fallback;
- resubmission / JSON-repair rate.

---

## [MAJOR] The cheapest configuration that is safe under the documented rules is the current Anthropic production configuration—not a switch

This conclusion follows from the project’s own stated gates, not from a preference for Anthropic.

### Candidate 1: OpenAI GPT-5.6 lane

Nominally the cheapest:

- Luna free text: $0.244–$1.240 per 1,000 calls.
- Terra paid deep-dives: $2.440–$12.400 per 1,000 calls.
- Luna vision: $1.660–$5.280 per 1,000 calls.

But it is not eligible under the stated rules:

- `COST_FACTS_AI_SWAP_2026-07-31.md`: OpenAI is “standby, unkeyed on server.”
- `ai_provider.py`: “golden-set eval before production traffic.”
- `AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 5: same gate remains.
- There is no evidence of a completed OpenAI golden-set, a shadow period, or stable production behavior.

### Candidate 2: Scaleway Mistral Medium lane

It has an 11/11 golden-set claim, including 2/2 vision, and is EU-hosted. However:

- Under the supplied prices, it is more expensive than Haiku for `haiku`, `triage`, and `vision`.
- Addendum 4 lists explicit unresolved prerequisites before a flip:
  1. verify Medium pricing on Scaleway console;
  2. ship the Quality-Score >= 60 routing floor;
  3. breaker/heartbeat plus a shadow period.

The supplied material does not show those three prerequisites as complete.

### Cheapest safe current configuration

| Tier | Safe production selection from supplied evidence | Reason |
|---|---|---|
| `haiku` | Anthropic Haiku 4.5 | Active, prompt-tuned, production history; designated standby costs more at supplied rates; OpenAI not gate-cleared. |
| `triage` | Anthropic Haiku 4.5 | Same conclusion. Search has its own $1/day cap, but enforcement was not shown. |
| `vision` | Anthropic Haiku 4.5 | Only current lane is established; Mistral has a small eval sample and is more costly in supplied facts; Luna is unevaluated. |
| `sonnet` / paid deep-dives | Anthropic Sonnet 4.6 | Buyer-funded and the stated quality rung; both alternatives are cheaper nominally but lack full demonstrated eligibility. |

This is not the cheapest nominal-price configuration. It is the cheapest **safe, rule-compliant configuration documented in the review packet**. The minimum safe cost-reduction path is to finish the OpenAI gate and shadow/reconciliation work—not to flip based on a price table.

---

## [MINOR] The current fallback order can cause an expensive lane to be used unexpectedly, depending on active provider

**Evidence**

The comment says:

```python
# Fallback chain order = dict order: anthropic -> openai -> scaleway
```

But actual behavior is “active provider first, then all others in dictionary order excluding active provider.”

Examples:

| `AI_ACTIVE` | Actual sequence |
|---|---|
| `anthropic` | Anthropic → OpenAI → Scaleway |
| `openai` | OpenAI → Anthropic → Scaleway |
| `scaleway` | Scaleway → Anthropic → OpenAI |

If Scaleway is active, a failure sends requests to Anthropic before OpenAI. This may be a reasonable quality decision, but it is not a cost-minimizing fallback sequence. If OpenAI is active, a failure routes free calls to Haiku before Scaleway—which is cheaper than Scaleway on supplied prices, so that happens to be economically favorable.

**Question:** Is fallback ordering intentionally quality-first, availability-first, jurisdiction-first, or cost-first per task? The code applies one global order to every tier, but the economics and quality roles differ by tier.

---

## [MINOR] “Deliver-then-charge” protects user credits but does not protect vendor spend

**Evidence**

`COST_FACTS_AI_SWAP_2026-07-31.md` lists:

> “deliver-then-charge (no result = free)”

The adapters can incur upstream processing and return `ok=False`, including:

- exceptions/timeouts;
- a 200 response with empty content;
- malformed response structures;
- possibly content filtered or otherwise unusable responses.

**Impact**

This is correctly customer-friendly, but it creates an intentional gross-margin leakage channel during provider degradation or adversarial malformed input. It should be treated as a cost of service, measured separately from successful-call cost.

**Metric needed**

```text
vendor-attempt cost for failed/free user requests
failed/free cost as percentage of successful revenue
failure rate by provider/model/task
credits withheld versus vendor spend incurred
```

---

## [MINOR] Paid deep-dive margin cannot be evaluated because Tuppence-to-currency conversion and deep-dive entitlement are not defined

**Evidence**

The cost sheet states:

> “Tuppence introduction credit 1T ≈ $2 (~R36). Paid deep-dive = 5T.”

This suggests 5T might correspond to approximately $10, but it does not state:

- whether 5T is always purchased at that effective rate;
- whether T is a credit, a promotional entitlement, or a currency-equivalent price;
- whether taxes, payment processor fees, refunds, and unused credit liability are included;
- whether one 5T purchase grants exactly one deep-dive;
- whether agency plans include bundled deep-dives.

If 5T is approximately $10 gross revenue, the direct model cost of Sonnet is very low under the stated typical text profile:

```text
Sonnet direct model cost: $0.0033–$0.0165/deep-dive
As share of $10: 0.033%–0.165%
```

Even a 10× output/retry surprise would not threaten direct token margin. The principal cost concern is therefore free usage, fallback storms, and bundled/abused subscription access—not paid deep-dive inference cost.

---

## [QUESTION] What is the actual unit and currency of the platform’s $100/day ceiling when one vendor bills EUR?

**Evidence**

The declared rail is denominated in USD:

> “$100/day platform hard ceiling”

Scaleway is EUR-priced:

> “€1.50 / €7.50 (~$1.65 / $8.25)”

No exchange-rate source, timestamp, FX buffer, invoice currency conversion policy, or budget-reservation currency is defined.

**Why it matters**

A USD-denominated rail cannot be a hard financial bound if EUR usage is converted only at reporting time. The platform needs to reserve a conservative USD amount at request time, such as a rate with an explicit FX safety buffer, then reconcile invoice currency later.

---

## [QUESTION] Are image tokens charged and reported consistently across the three providers?

The cost sheet applies a single estimated “1.1–1.6k tokens per image” range across all providers. The adapters then read:

- Anthropic: `input_tokens`, `output_tokens`
- OpenAI and Scaleway: `prompt_tokens`, `completion_tokens`

The supplied materials do not establish whether each provider counts image inputs in the same reported fields, at the same detail level, or at all. If image input is billed under a different modality accounting field, the spend logger may materially understate vision cost.

This should be confirmed by live invoice-reconcilable test calls before using cross-provider vision unit costs as routing data.

---

## [QUESTION] Is the low 2/2 vision golden-set sample sufficient for the highest-cost and potentially highest-risk call type?

**Evidence**

Addendum 4 says Medium passed “11/11 JSON incl. 2/2 vision on real photos.” It also says Haiku has “months of production history” while Medium has “20 eval calls.”

The cost conclusion is additionally invalidated by the listed pricing, but even if pricing is corrected, two vision examples do not establish:

- behavior over 1-photo and 12-photo inputs;
- malformed or low-light photos;
- non-JPEG / image MIME variation;
- long image batches near API request-size limits;
- KYC-specific false accept/reject behavior;
- output token verbosity;
- retry/fallback rates.

A cost-saving claim based on model token price is incomplete if the cheaper candidate produces more retries, human review, customer support, or failed onboarding.

---

## [PRAISE] The single provider seam is a strong cost-control foundation

`ai_provider.py` correctly centralizes task-to-model selection in `TASK_MODEL`, preventing call-site model sprawl. This materially improves the ability to:

- obtain cost reporting by abstract task;
- conduct controlled swaps;
- prevent accidental use of premium models in free flows;
- test fallback behavior;
- apply a future routing/budget policy consistently.

The abstract task names (`haiku`, `sonnet`, `vision`, `triage`) are especially useful because they provide an appropriate reporting and policy dimension independent of vendor branding.

The implementation is not yet sufficient to prove the budget ceilings, but the architectural seam is the right prerequisite.

---

## [PRAISE] The project correctly distinguishes nominal token price from operational switching cost

`AI_VENDOR_STRATEGY_DECISION_2026-07-11.md`, Addendum 3, rightly identifies prompt retuning, golden-set reruns, behavior drift, and operational churn as real switching costs. That is a sound FinOps position. The issue is not the stability doctrine; it is that the submitted pricing and the “40% cost” claim contradict one another and should be reconciled before the designated swap-out is described as economical.

---

# Cost drift register

| Drift source | How it enters this design | Catching metric |
|---|---|---|
| Fallbacks | Up to three provider attempts per logical request; final result exposes only winner usage | Attempts per logical request; attempted cost / successful result; fallback rate by provider/task |
| Timeouts and 200-empty replies | Work may occur before response is unusable; user receives free result | Failed-attempt spend; empty-response rate; timeout rate; provider request-ID reconciliation |
| Retries outside shown module | Callers, web handlers, queues, or users may retry after 30-second waits | Logical request IDs, idempotency keys, duplicate prompt hashes, user resubmission rate |
| Reasoning-token burn | GPT/Qwen may consume completion budget in hidden thought, then return short/empty output | Completion tokens per visible character; reasoning-token fields; cost per validated JSON response |
| Vision creep | More images, larger photos, repeated processing, KYC loops | Images/call; vision tokens/call; image hash deduplication; cost/user/day |
| Output verbosity | A model may routinely consume the full 700/1,200 output cap | P50/P95/P99 output tokens by task/model; cap-hit rate |
| JSON failures | Invalid JSON causes retries, repairs, or human handling | JSON-valid-first-pass rate; repair attempts; cost per valid structured response |
| Probe traffic | “Warm and probed” standby lanes create spend even without users | Probe count and cost by provider/day; probe success/latency; probe budget |
| FX | Scaleway invoices in EUR while rail is USD | EUR spend; applied FX rate; FX variance; USD budget buffer |
| Vendor repricing | GPT-5.6 pricing is explicitly only three days old; intro pricing ends; vendors can change SKU pricing | Price-card version and effective date; pre-deploy price verification; variance against invoice |
| Subscription bundle abuse | Free drafts and included plan entitlements can create high AI usage without proportional revenue | AI cost per active seller, per plan, per user, and per paid subscription dollar |

---

# The three findings the System Engineer should discuss first

1. **[BLOCKER] Reconcile the Mistral Medium price contradiction.** The supplied price card makes it 65% more expensive than Haiku, directly contradicting the “~40% of Haiku cost” rationale for the designated swap-out.

2. **[MAJOR] Demonstrate that the $100/day and $0.50/user/day rails are actual pre-dispatch, concurrency-safe spend controls.** Nothing shown in `ai_provider.py` proves this, and fallback attempts can be billable but invisible to the final spend record.

3. **[MAJOR] Decide whether OpenAI’s very low nominal cost is worth completing the required golden-set, shadow, and invoice-reconciliation gates.** It is the cheapest quoted lane, but it is not presently safe or rule-compliant for production. Until then, the cheapest safe documented configuration remains the current Anthropic configuration.

# What I could not verify from the material given

I could not verify:

- live vendor pricing pages, model availability, pricing applicability to image or reasoning tokens, or the claimed EUR/USD conversion;
- whether Mistral Medium’s actual Scaleway console price differs from the sheet;
- actual production volume, token distributions, image counts, retry rates, failure rates, or customer behavior;
- the implementation of the stated `$100/day`, `$0.50/user/day`, `$1/day search`, B7, spend-log, breaker, heartbeat, Quality-Score, or shadow-period controls;
- whether provider invoice usage reconciles to adapter-reported token fields;
- OpenAI and Scaleway golden-set results beyond the narrative claims;
- paid-credit pricing, processor fees, taxes, refunds, plan entitlements, or therefore true gross margin;
- whether no Chinese endpoint is involved anywhere in the actual configured production inference path.
