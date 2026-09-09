## 09 September 2026 — Genie / Porthole cost model: the AI-cost objection, measured

David placed the one-question front door at Stage 5 (running as Stage 3 if Stages 1–2 succeed) partly
because it implies extra AI cost, and said the answer would be open-source or free models. This puts
numbers against that, built from `AI_BASELINE.json` v2.0 worst-case envelopes and `PRICING_CANON` §4.

**Built:** `MarketSquare/genie/GENIE_COST_MODEL.html` (indexed in Visuals).

Findings, all on the base lane (`gpt-5.6-luna` / `gpt-5.6-terra`, worst-case envelope per call):

- **Free conversation** (route + 4 follow-ups) = 5 triage-tier calls = **$0.0049**; priced
  pessimistically at the haiku tier, **$0.0148**. Headline figure uses the pessimistic one.
- **Paid 5T dossier** = that conversation + one **design-tier** call ($0.18, the app's most expensive
  envelope) = **$0.195** against **$10.00** earned (1T = $2 fixed). Compute is **1.9% of the sale**.
  At ten times the write-up tokens it is still under a fifth.
- **Free conversations that never buy** are the only real exposure: 1 000/day = **$444/month**.
- **Free hosted lanes** carry ~**744 conversations/day at $0** — Groq (1 000 req/day), Cerebras
  (~1M tok/day), OpenRouter (1 000/day after a one-off $10). Google AI Studio and Mistral's free tiers
  are **disqualified**: both use prompts for training, and the input here is a user's own sentence.
  Cohere is non-commercial only.
- **Open weights ≠ free.** Smallest currently useful open model needs an 80GB card; cheapest tracked
  on-demand A100 80GB is $1.09/hr = **$785/month** flat. Break-even vs pay-per-call is **1 768 free
  conversations/day** (~53 000/month). At pre-launch volume, self-hosting is ~2 orders of magnitude
  the wrong side of that. The Hetzner CPX22 cannot run these models at all.

**Architecture conclusion:** a free lane is one adapter plus one registry line behind the existing
`ai_provider.py` seam (AI_PROVIDER_SEAM.md / AI_SWAP_ARCHITECTURE.md) — the 14 Aug lane-role ruling
already separates lanes by role, not vendor. Proposed addition to that ruling: the free lane is base
for the **free conversation only** and fails over **to** the paid base lane, never the reverse — a
capped lane must never stand between a paying customer and their dossier.

**Stage-order note:** the narrow Porthole (`ai_pa_porthole_CONCEPT.html`, built today) routes with plain
code and makes **no AI call at all**, so the cost argument does not apply to it. Stage order is David's
and is a scope decision; this only removes one stated reason for the placement.

Chart palette validated for colour-blind separation before use (blue/amber/purple, adjacent-pair ΔE ≥ 21.9).
Free-tier allowances read from published comparisons on 9 Sep 2026 — re-check before depending on them.
