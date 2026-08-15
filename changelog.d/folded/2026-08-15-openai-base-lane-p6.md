## 2026-08-15 — OPENAI-BASE-P6: spend attribution fixed, lane change audited, failover cost-gated

Scheduled pickup of the 14 Aug lane ruling (RUL-002). Found on arrival: the flip was ALREADY LIVE
(active=standing=openai since 14 Aug 20:05 UTC, key present — `available.openai:true` at /flags),
so P1 and P5 were done and P6 had become the open hole: with OpenAI as base, a failover to
Anthropic was invisible in the spend log and costed at the wrong rate.

**P6 landed (bea_main.py):** `_MODEL_PRICE` is now MODEL-keyed and loaded from `ai_price_card.json`
at boot (embedded fallback for card-less hosts), so code can never disagree with the register —
this also closes D1 (haiku was priced 0.80/4.00 vs the card's 1.00/5.00; every daily ceiling was
20-25% loose). `_log_ai_spend` takes `provider=`/`model=` and every one of the 24 call sites now
passes the SERVING lane from the AIResult (helper `_anon_photo_scan` returns it as a 4th element).
`_token_cost` resolves legacy tier keys via the serving lane's TASK_MODEL row. D2 closed: the
import-failure vision id dropped sonnet→haiku.

**D4 closed:** `POST /admin/flags` now writes a `_log.warning` for lane/pin changes plus an
`admin_audit` row (actor from JWT, prior, new, optional `reason` field, timestamp) for every field.
AL-3 satisfied: a pin records who and why. **D5 closed:** `ai_provider.complete()` builds its
fallback chain from AI_BASELINE.json failover order, cost-filters per tier (tolerance 6.0x,
safety net cost-exempt by role) — never dict insertion order. **AL-1/AL-2** implemented in
`_maybe_fire_lane_alert` (off-base >60 min / safety-net serving at all; webhook + log, 1/h,
heartbeats excluded).

**RG-0018 healed:** `gpt-5.6-sol` (design tier, RUL-013) added to the price card at $5/$30 —
web-verified 15 Aug (openrouter.ai, layer3labs.io; unchanged in the 30 Jul Terra/Luna cut), matches
STATUS Addendum 10. AI_BASELINE.json v2.0 gains the `design` tier (envelope DECLARED 12k/4k, no
caller until 1 Sep). `ai_baseline_check.py`: 6 FAIL → 0 FAIL (1 deliberate WARN: the import-failure
fallback names Anthropic ids — functionally right, that path speaks the raw Anthropic protocol).
Checker extended to verify the model-keyed table against the card.

**Ledger:** RG-0082/0083/0084 LOCKED (serving-lane attribution / audited lane change / baseline-
consulting failover). Run green start-to-finish delta: 1 REGRESSED → 0.

**P2/P3 NOT DONE — the honest remainder:** `scripts/golden_seam_v2.py` built (same 8 golden
prompts THROUGH `ai_provider.complete(provider="openai", probe=True)` — exercises the message
translation, the `reasoning_effort="none"` pin and max_completion_tokens handling that GS-OAI-V1's
raw vendor calls bypassed). It refuses to run without the production key; this sandbox has neither
the key nor OpenAI egress. One run on the Hetzner box → then add `openai` to GOLDEN_PASS (P3).
GOLDEN_PASS deliberately NOT touched. All changes repo-side, NOT deployed; the live box still runs
the pre-P6 accounting until the next /ship.
