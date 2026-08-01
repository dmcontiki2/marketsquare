# GOLDEN SET GS-OAI-V1 — GPT-5.6 Luna & Terra audition (1 Aug 2026)

**Gate tuple:** (model, tier, eval=GS-OAI-V1 on PRODUCTION prompts from bea_main.py 31-Jul
build, effort=reasoning_effort "none" [pinned — see below], sampling=api-default,
production max_completion_tokens per task). Runner: scripts/golden_openai_v1.py (repeatable).
Vision fixtures: 2 real jewelry photos (Jewelry/IMG_8032-8033). Total eval cost: ~$0.012.

## Results

| # | model | tier | task | verdict | latency | tokens in+out (reasoning) | cost |
|---|---|---|---|---|---|---|---|
| T1 | luna | haiku | draft-from-intent | PASS | 3.3s | 183+135 (r53) | $0.00020 |
| T2 | luna | haiku | search-interpret | FAIL | 1.7s | 162+120 (r120) | $0.00018 |
| T3 | luna | haiku | anon-rewrite | PASS | 1.7s | 248+100 (r44) | $0.00017 |
| T4 | luna | triage | email-triage | PASS | 2.3s | 274+134 (r52) | $0.00022 |
| T5 | luna | vision | vision-draft-2-photos | PASS | 6.3s | 6330+814 (r253) | $0.00224 |
| T6 | terra | sonnet | anon-rewrite-hard | PASS | 1.1s | 250+41 (r0) | $0.00099 |
| T7 | terra | sonnet | price-check-no-invention | PASS | 1.2s | 112+76 (r23) | $0.00114 |
| T8 | terra | sonnet | photo-anon-scan | PASS | 1.7s | 2200+39 (r15) | $0.00487 |

**First run: 7/8.** The single failure was decision-grade gold: at API-DEFAULT effort,
search-interpret's production budget of 120 tokens was consumed ENTIRELY by hidden
reasoning (120 reasoning, 0 visible) — the same class as the 17 Jul qwen3.5 finding and
the 31 Jul Terra empty-reply. Variants tested: effort "low" @120 also burned out;
default @400 answered but INVENTED trust_min=80 ("reliable bakkie" is not a seller-trust
request); **reasoning_effort "none" @120 passed cleanly on both test queries** (0 burn,
correct price/category/listingType, trust_min correctly null). VERDICT: Luna passes at
effort "none" — 8/8 — and the seam now PINS reasoning_effort="none" for all gpt-5 lanes
(ai_provider.py; changing it invalidates this gate — re-run the eval).

## Quality notes (judged)
- T1 draft: honest, specific, kept the scratch, no invention.
- T5 vision: read the "9ct" hallmark off the photo AND flagged it "not independently
  verified"; price_confidence honestly low (0.28); wear noted; full schema respected.
- T3/T6 anonymity: agency names, agent names, phone numbers, addresses, socials all
  scrubbed; price/suburb/facts kept. T6 kept city-level "Nelspruit" (allowed).
- T7: estimate stayed inside the provided comps range; verdict correct (not fair).
- T4: refused the refund correctly (Tuppence non-refundable), signed reply, auto_safe honest.

## Standing after this gate
Luna: haiku/vision/triage = PASSED. Terra: sonnet = PASSED. Funnel: Luna is now the
ELIGIBLE WINNER on haiku/triage/vision at +78-79% cost delta — meets the 30% bar, HELD by
the anti-jitter rule (2 card refreshes / 30 days) and the absolute floor (needs volume
data). Preconditions to any flip (unchanged): shadow period + executable rails (P2a) +
server OPENAI_API_KEY (this eval ran on the local key; the APP lane stays DISABLED until
the server .env carries the key). Caveat: 8-call sample — the shadow period is the real
volume test.
