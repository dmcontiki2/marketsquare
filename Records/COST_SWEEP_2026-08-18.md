# Cost-Compliance Sweep — 2026-08-18
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/relaxed-optimistic-pascal/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:3869 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:5826 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:5939 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6008 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6104 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9734 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9990 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10647 `_sonnet_verify_identity` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:12547 `_anon_ai_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:14690 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:15185 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:15274 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:15847 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:16161 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:16396 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:16659 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:17590 `grade_card_condition` — ceiling ✓ spend-log ✓
- 🟠 **WARN** — bea_main.py:18345 `_ts_breaker_heartbeat` — spend-log ✓ but NO _check_cost_ceiling
- 🔴 **CRITICAL** — bea_main.py:18408 `planner_heritage_compose` — UNWRAPPED & UNMETERED Anthropic call (no ceiling, no spend log, no Tuppence)
- 🟠 **WARN** — bea_main.py:18346 `_hb_loop` — spend-log ✓ but NO _check_cost_ceiling
- ✅ **OK** — advert_agent.py:785 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- 🟠 **WARN** — MarketSquare/AI_BASELINE.json:85 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/AI_BASELINE.json:240 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/AI_BASELINE.json:282 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🔴 **CRITICAL** — MarketSquare/AI_BASELINE.json:282 uses OPUS (claude-opus-4-6) — cost model rejected Opus
- 🟠 **WARN** — MarketSquare/AI_BASELINE.json:424 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/AI_CHALLENGER_BOARD.html:64 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/AI_CHALLENGER_BOARD.html:112 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/AI_MODEL_BASELINE_MAP.html:84 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/AI_MODEL_BASELINE_MAP.html:198 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🔴 **CRITICAL** — MarketSquare/AI_MODEL_BASELINE_MAP.html:198 uses OPUS (claude-opus-4-6) — cost model rejected Opus
- 🟠 **WARN** — MarketSquare/ai_price_card.json:41 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- ℹ️ **INFO** — MarketSquare/ai_price_card.json:101 Sonnet pricing-table entry (per-MTok rate card) — reference data, not a call site
- ℹ️ **INFO** — MarketSquare/ai_provider.py:54 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1576 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:15135 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/dashboard.server.html:1194 model name inside a UI display label — text on a diagram, not a call site (DW-009)
- 🟠 **WARN** — MarketSquare/DEFENCE_COVERAGE_MAP.html:95 unknown model family `claude-fable-5` — classify
- ℹ️ **INFO** — MarketSquare/main.py:966 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:967 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:9614 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:10179 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:45 model constant `REASON_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:46 model constant `REASON_VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/marketing/src/build_set.py:14 model constant `SAMPLE_RUN_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- 🟠 **WARN** — MarketSquare/scripts/maintenance_agent.py:328 unknown model family `claude-fable-5` — classify
- 🟠 **WARN** — MarketSquare/scripts/regression_ledger.py:3228 unknown model family `claude-fable-5` — classify
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:115 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:158 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:262 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:312 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:357 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:391 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:501 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:535 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:587 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:649 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — CityLauncher/orchestration/strategist_agent.py:75 model constant `STRATEGIST_MODEL` = claude-sonnet-4-8 — used by Tuppence-metered endpoints; keep justified

## Paid provider flags — OFF until contracted (P3)

- ✅ **OK** — ai_service_tiers.py: all paid providers OFF
- ✅ **OK** — feature_flags.json: paid_tiers_enabled=false, all provider flags off

## BEFORE YOU TEST — live-cost surfaces & guards

- ✅ **OK** — AI dry-run toggle default: ON — replays fixtures, $0
- ✅ **OK** — CityLauncher google_maps.py: GOOGLE_MAPS_API_KEY unset — $0 Playwright fallback active; paid Places API not reachable (the incident path is closed).
- ℹ️ **INFO** — Cost-bearing surfaces for live testing: /ai/run (Tuppence + Sonnet tokens), /advert-agent/market-note (Haiku), /listings/draft-from-photo (Haiku, template-fallback), /listings/photo orientation (Haiku vision), Paystack init (test keys = $0)
- ℹ️ **INFO** — Qualifying rule: ONE paid live run per feature; scenario testing uses dry-run fixtures or unset ANTHROPIC_API_KEY (all flows fail open to $0 paths)
- ℹ️ **INFO** — Ceilings live in DB (ai_spend_config); ceiling 0 = OFF. Before any test day set daily_user/platform ceilings low (e.g. $1/$5) and verify via /admin/ai-spend/summary. Authoritative check: live_spend() flags CRITICAL if the platform ceiling is 0/unset when MS_BEA_URL+MS_API_KEY are set — a static $0 sweep cannot read the DB itself.

## Cost-workbook drift (P2)

- ✅ **OK** — Workbook tier assumptions match the Simpler Model
- ℹ️ **INFO** — Workbook last modified 2026-07-22; latest CHANGELOG cost-impact entry: not found — reconcile if the code moved later

## Live spend

- ℹ️ **INFO** — Live spend: set MS_BEA_URL + MS_API_KEY to pull /admin/ai-spend/summary (endpoint staged 11 Jun)

## Operator-only sanctioned paid scripts (P3)

- ✅ **OK** — `AdvertAgent/run_video_reports.py` — sanctioned operator-only paid script (Generates live rich AdvertAgent feature reports for the feature videos; outputs ); not reachable from any app code path

## Paid call-site inventory (142 hits)

- **Anthropic API** (14): `MarketSquare/ai_provider.py:106`, `MarketSquare/ai_provider.py:107`, `MarketSquare/main.py:1014`, `MarketSquare/main.py:1024`, `MarketSquare/subscription_monitor.py:122`, `MarketSquare/failover/ai_backends.py:13`, `MarketSquare/failover/ai_backends.py:142`, `MarketSquare/failover/ai_backends.py:144`, `MarketSquare/scripts/peer_pack_ai.py:62`, `MarketSquare/scripts/regression_ledger.py:888`, `AdvertAgent/run_video_reports.py:37`, `AdvertAgent/run_video_reports.py:125` …
- **Anthropic SDK** (5): `MarketSquare/data_audit.py:154`, `MarketSquare/main.py:8028`, `CityLauncher/emailer/emailer.py:106`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (14): `MarketSquare/bea_main.py:13791`, `MarketSquare/citylauncher_ops.html:717`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:172`, `CityLauncher/dashboard/citylauncher.html:899`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218`, `CityLauncher/scraper/sources/google_maps.py:495`, `CityLauncher/scraper/sources/google_maps.py:501`, `CityLauncher/scraper/sources/property24.py:320` …
- **OpenAI** (40): `MarketSquare/add_openai_key.bat:10`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:13`, `MarketSquare/AI_BASELINE.json:428`, `MarketSquare/ai_provider.py:59`, `MarketSquare/ai_provider.py:149`, `MarketSquare/ai_provider.py:161`, `MarketSquare/ai_provider.py:261`, `MarketSquare/bea_main.py:13813`, `MarketSquare/bea_main.py:13946`, `MarketSquare/bea_main.py:13957` …
- **Paid data feeds** (66): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:110`, `MarketSquare/ai_service_tiers.py:111`, `MarketSquare/ai_service_tiers.py:113`, `MarketSquare/ai_service_tiers.py:198`, `MarketSquare/ai_service_tiers.py:199`, `MarketSquare/ai_service_tiers.py:206`, `MarketSquare/ai_service_tiers.py:207`, `MarketSquare/ai_service_tiers.py:238`, `MarketSquare/ai_service_tiers.py:239`, `MarketSquare/ai_service_tiers.py:243`, `MarketSquare/ai_service_tiers.py:244` …
- **Paystack (txn)** (3): `MarketSquare/bea_main.py:13710`, `MarketSquare/payments.py:32`, `MarketSquare/subscription_monitor.py:157`

**Totals:** 3 critical · 14 warnings · 24 ok · 28 info
