# Independent Peer Review — 2026-08-22-0714

*Peer: gpt-5.6-terra (second vendor, read-only) · Lens: cost · Author: Claude · System Engineer: David*

**Scope:**
  - Records/FORENSIC_C1C2_BRIEF.md (26,631 chars)
  - Records/PEER_PACK_BEA_EXTRACT.md (120,000 chars TRUNCATED)

**Usage:** 40587 in / 7246 out tokens · actual cost ≈ $0.1681

---

# Independent FinOps Peer Review

## Executive assessment

The submitted material does **not** substantiate the repeated claim that AI COGS are “capped” or that the economics are robust against AI cost drift. The application contains useful mechanisms—token-based costing, provider attribution, a pre-dispatch ceiling hook, and a low-cost heartbeat design—but the supplied evidence does not establish that the ceiling is configured, enforced against reservations/retries, or sized from real provider prices and real token distributions.

Most importantly, the source explicitly exposes an **“AI spend is UNCAPPED”** state when the platform ceiling is zero or unset, while neither Cycle 1 nor Cycle 2 reports the live configured ceiling. This is a material omission in a launch-readiness unit-economics conclusion.

---

## Findings

### [BLOCKER] The claimed AI cost cap is not proven live; the supplied code explicitly supports an uncapped production state

**Evidence**

- `Records/PEER_PACK_BEA_EXTRACT.md`, **“/admin/ai-spend summary endpoint”**, lines 6181–6195:
  - The endpoint reads `daily_user_ceiling_usd` and `daily_platform_ceiling_usd`.
  - It returns:
    > `"platform ceiling is 0/unset — AI spend is UNCAPPED"`

- `Records/PEER_PACK_BEA_EXTRACT.md`, **“ai_spend_config schema + ceiling columns”**, lines 885–895:
  - The supplied `CREATE TABLE` definition includes only:
    - `monthly_income_usd`
    - `alert_threshold_pct`
    - `alert_email`
    - `last_alerted_at`
  - It does **not** show `daily_user_ceiling_usd` or `daily_platform_ceiling_usd`, despite the summary endpoint selecting them.

- `FORENSIC_AUDIT_CYCLE1 — nice.docx`, probe facts:
  > “AI COGS capped”
  
  and:
  > “fixed opex … + capped AI COGS”

**Why this is a blocker**

The audit calls AI COGS capped without supplying any live value for either daily ceiling, proof that the database has the required columns, or proof that `_check_cost_ceiling()` successfully blocks an actual over-ceiling request.

The app’s own administrative endpoint says the platform is uncapped if the ceiling is zero/unset. The default shown for `monthly_income_usd` is `0.0`, and the monthly alert intentionally does nothing when income is not configured:

- `PEER_PACK`, lines 1891–1896:
  > `if not cfg or cfg["monthly_income_usd"] <= 0: return`

That means the monthly alert is also inert by default. An alert is not a hard spend bound in any event.

There is an internal documentation contradiction: the source excerpt’s displayed schema lacks the daily ceiling fields which the operational summary expects. They may be added by an omitted migration, but that cannot be assumed. The launch audit should not call this a capped control without a live `/admin/ai-spend/summary` result showing nonzero values and a controlled ceiling-rejection test.

**FinOps impact**

If public AI endpoints can be called at launch volume while `daily_platform_ceiling_usd = 0`, there is no demonstrated bound on daily provider expense. This is especially exposed because the externally visible launch gate is down according to both Cycle 1 and Cycle 2.

**Required discussion**

Before treating AI COGS as bounded, obtain and record:

1. Live `daily_platform_ceiling_usd` and `daily_user_ceiling_usd`.
2. The actual `_check_cost_ceiling()` implementation.
3. A non-production or controlled production test showing a request rejected once a ceiling is reached.
4. Evidence that reservations (`ai_spend_holds`) are included in the ceiling calculation, not merely described in comments.

---

### [MAJOR] Actual currency unit economics by AI provider lane cannot be calculated from the supplied material

**Evidence**

- The request material provides no provider price table, model register, model IDs, input-token price, output-token price, image-token pricing, cache pricing, or Scaleway pricing.
- `PEER_PACK`, lines 1776–1803 shows that `_token_cost(_mid, it, ot, _prov)` exists, but neither `_MODEL_PRICE` nor `_token_cost` is supplied.
- `PEER_PACK`, lines 16323–16332:
  - AI Listing Rewrite: `max_tokens=350`.
- lines 16427–16436:
  - AI Seller Audit: `max_tokens=400`.
- lines 17558–17569:
  - AI Batch Cards: up to 10 images and `max_tokens=2000`.
- lines 11166–11189:
  - KYC: image input, `max_tokens=300`.
- Cycle 1 says:
  > “OpenAI as base, a sustained failover to Anthropic is a ~4.4x cost event on the haiku tier”
- `PEER_PACK`, lines 1857–1859 says the safety-net lane can create:
  > “an ~8x cost event nobody approved”

**Assessment**

The documents make comparative cost claims—Anthropic approximately **4.4×** the OpenAI base lane for Haiku-tier work and safety-net operation approximately **8×**—but omit the underlying USD/token prices and expected token profiles. Therefore no reviewer can independently calculate:

- cost per call;
- cost per 1,000 calls;
- gross margin per AI service;
- margin erosion under fallback;
- exposure from vision/KYC image payloads;
- the correct daily ceiling amount.

This is not a minor presentation defect. The quoted Cycle 1 conclusion, “Cost never breaks it,” requires exactly these inputs.

### What can be calculated from supplied information

The only provider-call cost stated in actual currency is the heartbeat comment:

- `PEER_PACK`, lines 19437–19442:
  > “Text ping only (~$0.00002)”

The loop is capped at **one probe per 60 seconds total**, not one per provider:

- Maximum theoretical daily calls:
  \[
  24 \times 60 = 1,440
  \]

- Theoretical maximum daily spend, if there is always an eligible breaker row and every probe is billable:
  \[
  1,440 \times \$0.00002 = \$0.0288/day
  \]

- Thirty-day maximum under that extreme condition:
  \[
  \$0.0288 \times 30 = \$0.864/month
  \]

This is genuinely negligible **if** `$0.00002` remains accurate and `_check_cost_ceiling()` works. It does not establish a cap for customer traffic.

### Cost-per-call formula that should have been supplied

For each provider lane and task:

\[
\text{Call cost} =
\left(\frac{\text{input tokens}}{1,000,000} \times P_{in}\right)
+
\left(\frac{\text{output tokens}}{1,000,000} \times P_{out}\right)
+
\text{image / tool / cache charges}
\]

Then:

\[
\text{Cost per 1,000 calls} = 1,000 \times \text{Call cost}
\]

For a fallback from OpenAI to Anthropic in the stated Haiku tier:

\[
C_{\text{Anthropic}} \approx 4.4 \times C_{\text{OpenAI}}
\]

and the incremental cost per call is:

\[
\Delta C = 3.4 \times C_{\text{OpenAI}}
\]

No actual USD value can be substituted because the base-lane price is absent.

**Required discussion**

The System Engineer should require a versioned provider price register, date stamped and in USD, with expected p50/p95 input and output token profiles for each endpoint and each lane. “Model tier” is not a price.

---

### [MAJOR] Batch vision work has no supplied input-size or image-cost guard, while revenue is fixed at 2T

**Evidence**

- `PEER_PACK`, lines 17484–17505:
  > “up to 10 card photos”
  >
  > “2T flat cost regardless of card count.”
- lines 17535–17556:
  - The endpoint accepts base64 image payloads.
  - It detects MIME type but shows no image byte-size limit, dimension limit, pixel limit, cumulative request limit, or recompression step.
- lines 17561–17564:
  - Up to 10 images are sent to the model.
  - `max_tokens=2000` limits output only; it does not show an input-image cost bound.
- lines 17595–17607:
  - A successful parse causes a fixed 2T deduction.

**Arithmetic**

The document establishes:

\[
1T = \$2
\]

For a 2T batch-card service:

- Customer gross payment:
  \[
  2T \times \$2 = \$4.00
  \]

Using the stated approximate Paystack fee of 2.9% from Cycle 2:

\[
\$4.00 \times (1 - 0.029) = \$3.884
\]

So the maximum contribution available to pay **all** of the following is approximately **$3.884 per batch request**:

- model input images;
- input text;
- up to 2,000 output tokens;
- retries/failovers;
- payment fees already deducted above;
- storage/network/operational cost, if allocated.

Without a payload cap and actual vision price schedule, there is no evidence that a 10-image request is profitable on every enabled lane, particularly the safety-net or a vision-capable fallback.

**Why this matters**

A fixed-price vision product must bound the expensive variable: image count alone is not enough. Ten high-resolution images can have a radically different model-input cost from ten optimized thumbnails.

The docstring says “Claude Sonnet Vision,” while the source comment says `task="vision"` resolves to a Haiku model “today” (`PEER_PACK`, lines 17558–17560). That makes the service’s cost and quality characteristics configuration-dependent, not fixed. A future “re-arm” to Sonnet can silently change COGS while the customer price remains 2T.

**Recommended safe configuration**

At launch, the cheapest safe configuration is:

1. Keep vision/batch cards dark unless a tested lane-specific worst-case cost is below the net $3.884 revenue with a conservative margin.
2. If enabled, enforce:
   - maximum decoded bytes per image;
   - maximum total decoded bytes per request;
   - maximum pixel dimensions;
   - server-side resize/re-encode;
   - maximum total image-token/cost estimate before dispatch;
   - no automatic expensive fallback for this fixed-price service.
3. Make the service price lane-aware or reduce its included image count if a higher-cost vision lane becomes active.

---

### [MAJOR] Failed, retried, and fallback provider calls may create spend that the spend log does not record

**Evidence**

- `PEER_PACK`, lines 1769–1775:
  > “log AI call cost”
  >
  > “called via background_tasks.add_task() after every AI call.”
- However, the supplied endpoints invoke `_log_ai_spend()` only after a successful `ai_provider.complete()` result:
  - Rewrite: lines 16323–16342.
  - Audit: lines 16427–16452.
  - Batch cards: lines 17558–17593.
  - KYC: lines 11166–11189.
- On any exception, the endpoint returns an error and does not show logging of:
  - vendor attempt count;
  - input tokens sent before failure;
  - partial output;
  - timeout-billed attempts;
  - fallback attempts that failed before a final success.
- The retry/fallback semantics of `ai_provider.complete()` are not supplied.

**Assessment**

The accounting measures a final successful response, not necessarily every billable provider attempt. That is a serious FinOps blind spot. Vendor APIs can bill a request that times out at the application layer, returns malformed JSON, or emits output that the application rejects. A seamless fallback may mean multiple vendor calls for one customer action.

The reservation design acknowledges concurrent overspend risk:

- `PEER_PACK`, lines 897–902:
  > “N concurrent calls all passed the check before any recorded its cost”
  >
  > “A reservation is a short-lived worst-case hold placed BEFORE dispatch”

But the material does not include the implementation of `_check_cost_ceiling()`, reservation amount calculation, hold expiry duration, retry accounting, or evidence that holds cover each fallback attempt.

**Cost exposure**

For a request that makes one base attempt and one fallback attempt:

\[
C_{\text{actual}} = C_{\text{base failed}} + C_{\text{fallback successful}}
\]

but the user-facing log may record only:

\[
C_{\text{logged}} = C_{\text{fallback successful}}
\]

If the first call was billable, then:

\[
C_{\text{actual}} > C_{\text{logged}}
\]

The gap is exactly where an apparent hard ceiling can fail in practice.

**Required discussion**

The price/usage ledger should record one row per provider attempt, including failed, timed-out, rejected, and fallback attempts, with request ID linkage to the customer action. A ceiling must reserve worst-case cost for the configured retry/fallback chain before the first dispatch.

---

### [MAJOR] The cost reporting dimension is internally inconsistent: actual model cost is calculated using `_mid`, but the log writes the model key instead

**Evidence**

- `PEER_PACK`, lines 1795–1803:
  ```python
  _mid = model or _tier_model(model_key, _prov)
  ...
  cost = _token_cost(_mid, it, ot, _prov)
  ```
- Lines 1806–1811:
  ```python
  INSERT INTO ai_spend_log
  (email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real, provider)
  VALUES (?,?,?,?,?,?,?,?)
  ...
  (email or '', endpoint, model_key, cost, it, ot, is_real, _prov)
  ```
- The dashboard summary groups by `endpoint, model`:
  - lines 6183–6186.

**Assessment**

The cost itself may be computed using the actual served model (`_mid`), but the persisted `model` field stores `model_key`, such as `haiku` or `sonnet_vision`, rather than the actual model identifier. This will make cost reporting by model misleading, especially when:

- model maps change;
- provider lanes use different concrete models for the same task key;
- fallbacks occur;
- the `vision` task is remapped from Haiku to Sonnet;
- a vendor reprices a concrete model.

Provider is correctly stored from `_sr.provider` for the supplied successful paths, which is a positive. But the model breakdown shown to operators cannot be trusted as a true model-level spend breakdown.

**FinOps impact**

The company can see the cost total but lose the causal detail required to detect why it changed. That defeats the stated purpose of a lane/fallback cost alert.

**Required discussion**

Persist both:

- `task_key` / intended tier, e.g. `haiku`, `vision`;
- `served_model` / concrete provider model ID, e.g. whatever `_sr.model` returns.

Do not overload one column for two concepts.

---

### [MAJOR] The unit-economics conclusion does not include the worst-case revenue leakage from “deliver then charge” concurrency failures

**Evidence**

- `PEER_PACK`, lines 16261–16267:
  - `_require_tuppence()` performs a read-only balance check.
- Lines 16227–16244:
  - `_deduct_tuppence()` separately reads a balance, then inserts a negative transaction.
- Rewrite endpoint:
  - preflight check at line 16293;
  - provider invocation at lines 16323–16327;
  - later independent deduction at lines 16346–16350.
- Similar patterns exist for Audit (lines 16394, 16427–16436, 16454–16459) and Batch Cards (lines 17504, 17561–17569, 17595–17600).

**Assessment**

This is an intentionally customer-friendly “deliver then charge” flow, but it is not shown to be atomic. Multiple concurrent requests from the same wallet can pass preflight before any deduction. They can then all incur provider cost. At settlement, outcomes include:

1. all deductions succeed and the balance can go negative if transactions interleave unexpectedly;
2. one or more deductions fail due to locking or insufficient balance after another request commits;
3. the customer receives multiple successful results but some are uncharged;
4. SQLite contention creates provider cost plus an error response.

The material does not show a transaction isolation strategy, unique idempotency key, wallet reservation, or atomic conditional debit.

This is a **FinOps** problem even if it is intentionally not treated as a security problem: the app can spend variable AI cost before reliably realizing the fixed Tuppence revenue.

**Example**

For batch cards, a wallet with 2T can submit two concurrent 2T requests:

- Both pass `_require_tuppence(..., 2)`.
- Both can dispatch up to 10 images.
- The system may incur two model costs.
- Only one 2T debit is reliably funded.

The revenue ceiling is $3.884 net for one batch, while cost can be incurred twice.

**Required discussion**

Use an atomic wallet hold before dispatch, then settle/release it after verified delivery. This preserves the “no charge for failed service” policy while stopping unfunded concurrent consumption.

---

### [MINOR] The customer-facing description of the price-check product overstates what the implementation provides, creating revenue and refund pressure

**Evidence**

- `PEER_PACK`, `marketsquare.html`, lines 1584–1588:
  > “Our AI compares the asking price to current SA market rates and gives a verdict — fair, above or below market — plus a suggested fair range.”
- `PEER_PACK`, AI3 implementation, lines 17089–17113:
  > “No verified price feed for this category”
  >
  > “we do NOT sell a guess”
  >
  > returns `cannot_verify`, with `charged: False`.

**Assessment**

The implementation is more honest than the UI copy: for most categories without a verified feed, it returns no paid assessment. That is good safety behavior, but the public product description creates expectations of a broad paid “fair-price” service.

This is not direct provider overspend because the no-feed branch is free. It is a revenue-realization and support-cost risk: buyer demand/conversion assumptions should not count AI-price-check revenue as broadly available until feed coverage by category is measured.

**Recommended adjustment**

Describe the product as “available where verified data is available; otherwise we show a free no-guess result.” Track:

\[
\text{paid verified outcomes} / \text{price-check attempts}
\]

This conversion rate is more useful than raw endpoint traffic.

---

### [MINOR] Cycle 1’s “cost never breaks it” statement is stronger than the available economic evidence

**Evidence**

- `FORENSIC_AUDIT_CYCLE1 — nice.docx`:
  > “Cost never breaks it; only revenue realization does.”
- `FORENSIC_AUDIT_CYCLE2_PEER — nice.docx` correctly overturns the profitability GREEN and reports break-even sensitivity.
- Cycle 2’s table provides revenue-per-seller scenarios, but it does not separately model AI service uptake, AI cost per service, fallback rate, KYC activity, image-heavy activity, payment disputes/refunds, or provider repricing.

**Recomputed marketplace revenue arithmetic**

Using the material’s stated 1T price and 2.9% payment fee:

\[
1T = \$2.00
\]

\[
\text{Net revenue per introduction} = \$2.00 \times (1 - 0.029) = \$1.942
\]

For Cycle 2’s base conversion mix of 15% Pro and 25% Starter:

\[
(0.15 \times \$20) + (0.25 \times \$5) = \$4.25
\]

At two introductions per seller per month:

\[
2 \times \$1.942 = \$3.884
\]

\[
\$4.25 + \$3.884 = \$8.134 \approx \$8.13/\text{seller/month}
\]

This reproduces Cycle 2’s table.

At the observed-rate proxy of 0.5 introductions per seller per month:

\[
0.5 \times \$1.942 = \$0.971
\]

\[
\$4.25 + \$0.971 = \$5.221 \approx \$5.22/\text{seller/month}
\]

This also reproduces Cycle 2.

For the freemium-realistic mix of 5% Pro and 10% Starter:

\[
(0.05 \times \$20) + (0.10 \times \$5) = \$1.50
\]

At 0.5 intros/month:

\[
\$1.50 + \$0.971 = \$2.471 \approx \$2.47/\text{seller/month}
\]

These are valid revenue calculations. However, they are not complete contribution-margin calculations unless AI costs, vendor fallback, failed charges, support, storage, refund/dispute costs, and tax treatment are included or deliberately excluded.

I agree with Cycle 2 that the profitability verdict should be **AMBER**, not GREEN.

---

### [QUESTION] Which currency basis and FX date support the claimed fixed opex, stress cases, and break-even results?

**Evidence**

- Cycle 1 says:
  > “€28 server + ~$135/mo accountant”
- Cycle 2 says:
  > “accountant R2,000 + R500 software (~$139), Hetzner CPX32 (~$30)”
  >
  > “Base opex ~$194/mo; stress opex ~$255/mo”
- Cycle 1 uses:
  > “15% ZAR depreciation”
- No FX rate/date/source is provided.

**Question**

What exact exchange rate and date were used to convert:

- R2,500/month to approximately $139;
- €28/month to USD;
- the 15% ZAR depreciation stress;
- provider invoices billed in EUR, USD, or ZAR?

The opex presentations are directionally compatible but not reproducible. Currency conversion is a real launch risk because revenue appears substantially ZAR-linked while much of AI and hosting expense is likely USD/EUR-linked. The model should state whether seller subscription and Tuppence amounts are net of VAT and payment fees, and whether accountant/software figures include VAT.

---

### [QUESTION] What prevents a silent cost reprice after model-map or provider-switch changes?

**Evidence**

- `PEER_PACK`, lines 1640–1680:
  - The active provider can be changed through database-backed state and an override can remain in force for 24 hours by default.
- lines 15021–15047:
  - `/flags` exposes OpenAI, Anthropic, and Scaleway availability and models.
- lines 1822–1825:
  - An off-base lane is treated as a “re-pricing event.”
- lines 1857–1859:
  - Safety-net use can be an “~8x cost event.”
- lines 17558–17560:
  - Vision currently resolves to Haiku, but the documented revert can “re-arm” Sonnet.

**Question**

What approval gate prevents an operator, config change, expired manual pin, provider model-map update, or vendor API deprecation from moving an enabled paid endpoint to a lane/model whose worst-case cost exceeds the service’s net revenue or the daily ceiling budget?

An hourly alert is detection, not prevention. A 24-hour manual pin is potentially an entire day of changed marginal cost.

The cheapest safe launch policy is not merely “OpenAI base.” It is:

- one explicitly approved base model per paid endpoint;
- fallback disabled for fixed-price image-heavy services unless it is priced and cost-bounded;
- a per-endpoint maximum estimated cost;
- an approval-required model/price manifest update;
- automatic disabling of a service when the model-price manifest is stale or missing.

---

### [PRAISE] The design has several sound FinOps primitives, if they are completed and evidenced

The following are good engineering choices:

1. **Token-count-based costing rather than only flat estimates**
   - `PEER_PACK`, lines 1776–1803.
   - Real token counts are preferable to a blanket per-call estimate.

2. **Provider attribution from the serving result**
   - Lines 1779–1785 correctly identify that fallback cost must be charged to the provider that actually answered.
   - This is materially better than attributing all spend to the intended lane.

3. **Pre-dispatch reservation intent**
   - Lines 897–902 identify the concurrency overshoot problem accurately.
   - This is the right mechanism conceptually; the remaining issue is evidence of implementation and coverage.

4. **Heartbeat global rate bound**
   - Lines 19437–19442 explicitly cap the recovery loop to one probe per minute total.
   - At the stated $0.00002 probe cost, the theoretical maximum of $0.864/month is appropriately immaterial.

5. **KYC disables fallback**
   - `PEER_PACK`, line 11177:
     > `allow_fallback=False`
   - This is good privacy practice and avoids unintentionally distributing identity documents to additional vendors. It should also be applied to a documented cost policy.

---

## Cheapest safe launch configuration under the supplied stability and golden-set constraints

The material states that:

- OpenAI is the base lane and serves 100% of live AI traffic.
- `RG-0132` remains open because:
  > “openai base lane has no production golden run”
- The openai base lane has no production golden validation despite being the lane every user reaches.
- No live ceiling configuration is supplied.
- Fixed-price batch vision has no demonstrated worst-case cost bound.

Therefore, I disagree with any implication that the present multi-lane production configuration is already the cheapest **safe** configuration.

### Recommended launch posture

1. **Keep all customer-paid AI services dark** until:
   - OpenAI has a production golden-set pass;
   - platform and per-user ceilings are verified nonzero and enforced;
   - provider model prices and token distributions are registered;
   - each enabled service has positive worst-case unit margin.

2. If an AI service must launch, enable only **text-only rewrite and audit** on the validated base lane, with:
   - no automatic cross-provider fallback;
   - a strict request/input-length cap;
   - output caps already shown (`350` and `400`) retained;
   - atomic Tuppence holds before provider dispatch;
   - explicit actual-provider-attempt logging.

3. Keep **Batch Cards / vision** dark:
   - 10 image inputs at a fixed $3.884 net revenue are not cost-bounded in the supplied source.

4. Keep **KYC** dark or manually rate-limited until its:
   - authentication path;
   - volume forecast;
   - per-document provider cost;
   - platform daily cap;
   - retention/compliance cost  
   are independently verified. It creates cost without a shown direct customer charge.

5. Keep **fallback** for reliability drills and operator-controlled incidents, not silently enabled as a normal paid-service path, until the fallback lane has:
   - a golden pass;
   - a per-service margin calculation;
   - a maximum fallback budget.

This is cheaper than always-on multi-lane behavior and safer than relying on alerting after a repricing has already occurred.

---

## The three findings the System Engineer should discuss first

1. **[BLOCKER] Is `daily_platform_ceiling_usd` live, nonzero, and actually enforced?**  
   The code explicitly declares spend uncapped when it is zero/unset, while the audits claim capped AI COGS without live proof.

2. **[MAJOR] Where is the actual provider pricing and token-profile model?**  
   No one can calculate cost per call, per 1,000 calls, batch-card margin, fallback impact, or a defensible ceiling from the material provided.

3. **[MAJOR] Can concurrency, retries, failures, and fallback generate provider cost without matching logged cost or collected Tuppence revenue?**  
   The shown deliver-then-charge flow and success-only logging make this a credible cost-leakage path.

---

## What I could not verify from the material given

I could not verify:

- the actual OpenAI, Anthropic, and Scaleway model IDs and their USD input/output/image prices;
- any provider contract terms, promotional pricing expiry, committed-use discounts, FX billing currency, tax treatment, or vendor repricing protections;
- p50/p95 token counts, image dimensions, input sizes, call volumes, retry rates, fallback rates, or KYC volumes;
- the implementation of `_check_cost_ceiling()`, `_token_cost()`, `_MODEL_PRICE`, reservation creation, hold expiry, hold settlement, or whether holds are included in spend checks;
- live values of `daily_user_ceiling_usd`, `daily_platform_ceiling_usd`, `monthly_income_usd`, or current AI spend;
- whether the daily-ceiling columns are actually present in the production database despite their absence from the supplied table creation excerpt;
- whether provider failures, timeouts, malformed responses, and retried calls are billable and/or logged;
- whether wallet deductions are atomic and idempotent under concurrent calls;
- the live golden-set status beyond the audit’s statement that `RG-0132` is open;
- the actual live configuration of enabled AI endpoints, provider fallback policy, and model maps.
