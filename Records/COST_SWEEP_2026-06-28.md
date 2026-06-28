# Cost-Compliance Sweep — 2026-06-28
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/dazzling-ecstatic-euler/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:2440 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3813 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3885 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3984 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7149 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7406 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9750 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10184 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10274 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10730 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11049 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11287 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11532 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11968 `grade_card_condition` — ceiling ✓ spend-log ✓
- ✅ **OK** — advert_agent.py:708 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/ai_provider.py:22 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/ai_provider.py:23 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:966 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:967 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9569 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:10134 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:45 model constant `REASON_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:46 model constant `REASON_VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/marketing/src/build_set.py:14 model constant `SAMPLE_RUN_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:104 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:149 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:232 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:286 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:335 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:373 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:464 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:502 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:541 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:607 Sonnet — allowed: paid Level-2, Tuppence-metered
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
- ℹ️ **INFO** — Workbook last modified 2026-06-21; latest CHANGELOG cost-impact entry: 17 June 2026 — reconcile if the code moved later

## Live spend

- ℹ️ **INFO** — Live spend: set MS_BEA_URL + MS_API_KEY to pull /admin/ai-spend/summary (endpoint staged 11 Jun)

## Paid call-site inventory (93 hits)

- **Anthropic API** (9): `MarketSquare/ai_provider.py:38`, `MarketSquare/ai_provider.py:39`, `MarketSquare/bea_main.py:1014`, `MarketSquare/bea_main.py:1024`, `MarketSquare/failover/ai_backends.py:13`, `MarketSquare/failover/ai_backends.py:142`, `MarketSquare/failover/ai_backends.py:144`, `AdvertAgent/service/advert_agent.py:25`, `AdvertAgent/service/advert_agent.py:720`
- **Anthropic SDK** (5): `MarketSquare/bea_main.py:7983`, `MarketSquare/data_audit.py:154`, `CityLauncher/emailer/emailer.py:99`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (13): `MarketSquare/citylauncher_ops.html:717`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:172`, `CityLauncher/dashboard/citylauncher.html:899`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218`, `CityLauncher/scraper/sources/google_maps.py:495`, `CityLauncher/scraper/sources/google_maps.py:501`, `CityLauncher/scraper/sources/property24.py:320`, `CityLauncher/scraper/sources/property24.py:331` …
- **OpenAI** (5): `MarketSquare/ai_provider.py:74`, `MarketSquare/ai_provider.py:79`, `MarketSquare/bea_main.py:1015`, `MarketSquare/bea_main.py:1022`, `MarketSquare/bea_main.py:9145`
- **Paid data feeds** (60): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:104`, `MarketSquare/ai_service_tiers.py:105`, `MarketSquare/ai_service_tiers.py:107`, `MarketSquare/ai_service_tiers.py:192`, `MarketSquare/ai_service_tiers.py:193`, `MarketSquare/ai_service_tiers.py:200`, `MarketSquare/ai_service_tiers.py:201`, `MarketSquare/ai_service_tiers.py:232`, `MarketSquare/ai_service_tiers.py:233`, `MarketSquare/ai_service_tiers.py:237`, `MarketSquare/ai_service_tiers.py:238` …
- **Paystack (txn)** (1): `MarketSquare/payments.py:32`

**Totals:** 0 critical · 0 warnings · 20 ok · 25 info
