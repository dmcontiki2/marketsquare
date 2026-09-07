## 7 Sep 2026 — AI model and stand-in allocation, read from canon and PROBED live (AI-ALLOC-1)

David: *"Next i will need to see the AI model/redundancy allocations, what models will we need, which
ones are stand ins for them?"* Answered from `AI_BASELINE.json` + `ai_price_card.json` and then
checked against the running server, per the evidence ladder. Deliverable:
`genie/bots/AI Models & Stand-ins — nice.docx`.

**The structure (unchanged, and sound):** openai BASE · anthropic AUTO-FAILOVER · scaleway SAFETY NET
(EU, cost-exempt, alert-on-use) · gemini CANARY for photo box coordinates only. Failover tolerance 6.0x
base; the safety net is deliberately exempt because it is reached when the alternative is being down or
banned. Per-tier chains with worst-case prices are tabled in the doc (triage/haiku/vision/sonnet/design).

**Every BOT and genie job maps to a size that already exists** — triage for a wish, haiku for a coaching
turn or an advert, vision for reading a seller's photos, sonnet+haiku for a plan, design for a dossier.
No new tier is needed, which is why the cost model in `BOT Financial Model — nice.docx` holds.

**FOUR FINDINGS, all from probing rather than reading:**

1. **The DESIGN tier has NO auto-failover.** `AI_BASELINE.json` gives it openai BASE and scaleway
   SAFETY NET and nothing between. A dossier — the flagship PA errand — falls straight to the EU
   emergency lane (a 37% capability drop per the card's own capability_note) on any OpenAI dropout.
   This sits directly under the feature David is planning. RECOMMENDED: rebuild the dossier out of
   sonnet+haiku pieces that DO have stand-ins, rather than contracting a second design-class supplier —
   it costs nothing and removes a dependency instead of adding one.
2. **The serving lane has not passed its own gate.** PROBED `/flags` 7 Sep: `ai_provider.active=openai`,
   `standing=openai`, `override=null` — and the funnel labels openai **`pending-golden-set` on ALL FOUR
   live tiers**, with anthropic the only lane at `production`. `ai_price_card.json` on disk marks the
   same model `golden-set-passed`. Both cannot be operative; the server serves customers, so the server
   is the truth. This is precondition P2/P3 of David's own 14 Aug decision, still NOT DONE 24 days later
   while the lane was moved anyway.
3. **Post-failover cost figures are wrong by construction** (baseline known-drift D3): `_log_ai_spend`
   records the INTENDED lane, not the lane that answered, and `_token_cost` is keyed on tier not model.
   The moment a stand-in takes over — exactly when the cost matters — the numbers stop being true.
4. **Small drifts that move money with the model id untouched:** D1 `_MODEL_PRICE['haiku']`=(0.80,4.00)
   vs card (1.00,5.00), so every haiku row is logged 20-25% low and the daily rails are that much
   looser than set; D2 a failed `import ai_provider` silently upgrades every vision call to Sonnet (3x);
   and `AI_BASELINE.json` is pinned to price card `2026-08-19.1` while the live card is `2026-08-26.1`.

**Full field presented, nothing pre-filtered (RUL-009):** luna 51.24 / terra 54.95 / sol 61.0 (OpenAI),
sonnet-4-6 47.21 / haiku-4-5 29.58 (Anthropic), mistral-medium-3.5 29.95 (Scaleway, the ONLY one scored
effort-matched), gemini-3.7-flash (eval pending). Scores are not like-for-like — most are max-effort
while the app runs default — so any procurement re-scores at production effort.

**Claude's one-line pick, David's call:** keep the structure exactly as it is and spend the effort on
the outstanding sign-off instead of on choosing a different model — an unexamined lane is a bigger risk
than a lane scoring two points lower.

**Split of work:** model/vendor/lane changes and whether the design tier gets a paid stand-in are
David's (RUL-009/RUL-037). The four items above are FAULTS, not choices, and are Claude's to fix:
run the outstanding golden set, correct `_MODEL_PRICE`, make the spend log record the lane that
answered, and close the silent vision upgrade. **None touched this session** — nothing was changed.

### Re-costed with DeepSeek (4th) and Mistral (5th), on one honest scale (AI-ALLOC-2)

David: *"please redo the costing with a fourth AI being Deepseek and a fifth Mistral... each replacement
equivalent need to be functionally and effort equal... we want to use the open ones from Scaleway and if
there are cheaper ones then from there. No hidden weights on the scale."*

**Method, made auditable because he asked for no thumb on the scale:**
- Every model priced on the SAME five envelopes from `AI_BASELINE.json` (triage 2500/400, haiku
  4000/1800, sonnet 4000/1400+1img, vision 2000/2000+10img, design 12000/4000).
- Image cost DERIVED, not assumed: **1,806 input tokens per image** is the only value that makes six
  existing baseline figures come out exactly right, so every lane is charged on David's own accounting.
- **My first pass GUESSED gpt-5.6-terra and sol prices — that is precisely the hidden weight he warned
  about, so it was thrown away.** Both were instead SOLVED from the file's own worst-case figures:
  terra = $2.00/$12.00 per Mtok, sol = $5.00/$30.00. METHOD PROVEN: six independent recomputations
  (luna@haiku, luna@vision, terra@sonnet, sol@design, haiku-4-5@vision, mistral-medium@sonnet) all EXACT.
- Scaleway Paris serverless list fetched live 7 Sep 2026; converted at the file's own FX (1.155).

**FINDINGS, several against expectation:**
- **DeepSeek V4 Flash is NOT the cheap option on list price** — 1.19x base on haiku, 1.56x on triage,
  and it has **no vision at all**, so it cannot serve 2 of the 5 tiers. BUT its cached input is €0.08 vs
  €0.40, and our prompts are ~90% repeated system text: at 90% caching it is **0.74x base — 26% cheaper**.
  It is the only model on the list whose answer depends on how we BUILD rather than what we buy.
- **Mistral Medium 3.5 — the incumbent safety net — is the DEAREST open model on the shelf** (7.61x base
  haiku, 8.12x vision). Correct as insurance, but it is not the cheap Mistral.
- **The actual find: `mistral-small-3.2-24b` beats the incumbent base on EVERY tier it can serve**
  (0.48x haiku, 0.67x vision, 0.06x sonnet, 0.02x design) **and it has vision.** `pixtral-12b` is
  similar. `gpt-oss-120b` is 0.66x haiku but text-only.
- **The biggest single number found: the DESIGN tier.** gpt-5.6-sol costs $0.18/call and every
  alternative is between 2% and 31% of that — even staying inside OpenAI and using luna is a 96% saving.
  This is the tier the PA dossier errand uses, so it matters before that feature is built, not after.

**WHAT WAS REFUSED, deliberately:** capability. There is **no effort-matched score** for DeepSeek,
Mistral Small, gpt-oss or any Qwen, and the scores already on the register are not comparable either
(most are max-effort while the app runs default; `mistral-medium` is the ONLY `effort_matched: true`
entry). Filling that in from a leaderboard would be the hidden weight David barred. The gap is cheap to
close with machinery already owned: the 5-part equivalence test in `AI_BASELINE.json`, golden set run at
production effort. Scaleway's first 1M tokens/month are free and batch work is -50%, so the audition
costs nothing.

**Claude's one-line pick (David's call, RUL-009):** audition `mistral-small-3.2-24b` and
`deepseek-v4-flash` on the existing golden set at production effort before choosing anything — a cheap
model that fails the golden set costs more than a dear one that passes, and neither has taken the test.

**Jurisdiction, stated once and factually because he asked for no lecture:** hosting decides
jurisdiction, and every non-OpenAI/Anthropic model here runs on Scaleway's machines in Paris. Where
weights were trained does not change where customer data is processed — a fact that works in favour of
what he asked for.

Deliverable: `genie/bots/Five Lanes One Scale — nice.docx`. Nothing changed, no lane moved.
