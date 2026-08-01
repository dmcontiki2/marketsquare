# Cost Facts — AI Swap-Out Model (input sheet for the Peer's cost review, 31 Jul 2026)

Prepared by the Author for the Peer's FinOps lens. Prices verified 31 Jul 2026 against
vendor pages/press. NO live volume data is included — the platform is pre-launch
(founding-seller phase, target 60 sellers, launch 1 Sep 2026); treat volumes as scenarios,
not measurements, and say so in your findings.

## The app's abstract task tiers → model per lane (ai_provider.py TASK_MODEL)

| Tier | Used for | Anthropic (ACTIVE) | Scaleway EU (standby) | OpenAI (standby, unkeyed on server) |
|---|---|---|---|---|
| haiku | free drafts, coach, rewrites, email triage, search interpret | Haiku 4.5 — $1 / $5 per Mtok | Mistral Medium 3.5-128B — €1.50 / €7.50 (~$1.65 / $8.25) | GPT-5.6 Luna — $0.20 / $1.20 |
| sonnet | PAID 5T deep-dives (price-check etc.), agency-import photo scan | Sonnet 4.6 — $3 / $15 | same Mistral row | GPT-5.6 Terra — $2 / $12 |
| vision | photo-first onboarding (vision-draft, max_tokens 1200), KYC | Haiku 4.5 | same Mistral row (2/2 vision golden-set) | Luna (vision-capable) |
| triage | email triage, cheap classification | Haiku 4.5 | same | Luna |

22 call sites, all through one seam; any-of fallback anthropic → openai → scaleway.
House rule (3 Jul): Haiku-first everywhere; Sonnet only where buyer-funded (5T) or
no-slips-critical (agency scan). 18 Jul golden set: Mistral Medium quality parity with
Haiku on 11/11 incl. vision, ~40% of Haiku's cost, better latency — designated swap-out,
not active (Addendum 4: don't change a tested tool mid-design; switch on measured
failure/forced exit only).

## Typical call shapes (from code, not measurements)

- Text call (draft/rewrite/triage): ~0.5–2k tokens in, 120–700 out (max_tokens caps
  120/350/700 at various sites).
- Vision call: 1–12 photos resized ≤1568px (~1.1–1.6k tokens per image) + prompt;
  out ≤ 1200.
- Search interpret: ~140-token system + sentence; strict JSON out; cached; fires only on
  total deterministic-parser miss; its own $1/day micro-cap.

## Cost rails already live

$100/day platform hard ceiling · $0.50/user/day · B7 $20/mo watch · SEARCH_AI_DAILY_USD
$1/day · deliver-then-charge (no result = free) · per-call spend log with real tokens
(provider column lands with P2a) · monthly /housekeep notes competitor price moves as
fallback intelligence only (Addendum 3: stability outranks price-chasing).

## Revenue side (for ratio context)

Tuppence introduction credit 1T ≈ $2 (~R36). Paid deep-dive = 5T. Seller subscriptions
$0 / $5 / $20 per month + Agency tiers. No commission on sales.

## Known pricing risks

- Scaleway priced in EUR → FX exposure for a USD-modelled cost sheet.
- GPT-5.6 Luna price is 3 days old (80% cut, 30 Jul) — attractive but volatile; the
  stability doctrine forbids churn-chasing it.
- Anthropic Sonnet 5 intro pricing ($2/$10) ends 31 Aug — NOT currently used by the app
  (app pins Sonnet 4.6 at $3/$15), listed as a known upgrade decision with a date.
- Reasoning-token burn: GPT-5.6 and Qwen-class models consume output budget on thinking —
  observed twice in this project (17 Jul qwen3.5, 31 Jul Terra empty-reply) — a silent
  per-call cost multiplier if unwatched.

## What the Author asks the Peer to produce (show arithmetic)

1. Cost per call and per 1,000 calls per tier per lane, using the shapes above.
2. What a full swap to each standby actually saves or costs at, say, 1k/10k/100k free
   drafts + 100/1k paid deep-dives per month.
3. Where silent cost drift can enter this architecture (fallbacks, retries, probes,
   verbose models, vision creep) and what metric would catch each.
4. The cheapest SAFE configuration consistent with the stated rules (golden-set gate,
   stability doctrine, no Chinese endpoints for user content).
5. Anything cost-relevant the Author has not thought to ask.
