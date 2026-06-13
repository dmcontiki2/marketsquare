# Cost-Compliance Sweep — 2026-06-13
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/inspiring-amazing-ramanujan/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:2289 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3551 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3672 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3746 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3847 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7016 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7277 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9474 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9912 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10006 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10356 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10678 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10919 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11168 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11608 `grade_card_condition` — ceiling ✓ spend-log ✓
- ✅ **OK** — advert_agent.py:709 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/bea_main.py:916 model constant `SONNET_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9293 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9862 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- 🟠 **WARN** — MarketSquare/marketing/src/build_set.py:294 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🟠 **WARN** — MarketSquare/marketing/src/build_set.py:309 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:104 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:151 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:233 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:287 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:336 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:374 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:465 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:503 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:542 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:608 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — CityLauncher/orchestration/strategist_agent.py:75 model constant `STRATEGIST_MODEL` = claude-sonnet-4-8 — used by Tuppence-metered endpoints; keep justified

## Paid provider flags — OFF until contracted (P3)

- ✅ **OK** — ai_service_tiers.py: all paid providers OFF
- ✅ **OK** — feature_flags.json: paid_tiers_enabled=false, all provider flags off

## BEFORE YOU TEST — live-cost surfaces & guards

- ✅ **OK** — AI dry-run toggle default: ON — replays fixtures, $0
- 🟠 **WARN** — CityLauncher google_maps.py: Places API is PAID when GOOGLE_MAPS_API_KEY is set — unset the key for test runs; the Playwright fallback is $0 (the incident path)
- ℹ️ **INFO** — Cost-bearing surfaces for live testing: /ai/run (Tuppence + Sonnet tokens), /advert-agent/market-note (Haiku), /listings/draft-from-photo (Haiku, template-fallback), /listings/photo orientation (Haiku vision), Paystack init (test keys = $0)
- ℹ️ **INFO** — Qualifying rule: ONE paid live run per feature; scenario testing uses dry-run fixtures or unset ANTHROPIC_API_KEY (all flows fail open to $0 paths)
- 🟠 **WARN** — Ceilings live in DB (ai_spend_config); ceiling 0 = OFF. Before any test day: set daily_user/platform ceilings low (e.g. $1/$5) — verify via /admin/ai-spend/summary

## Cost-workbook drift (P2)

- ✅ **OK** — Workbook tier assumptions match the Simpler Model
- ℹ️ **INFO** — Workbook last modified 2026-06-12; latest CHANGELOG cost-impact entry: 11 June 2026 — reconcile if the code moved later

## Live spend

- ℹ️ **INFO** — Live spend: set MS_BEA_URL + MS_API_KEY to pull /admin/ai-spend/summary (endpoint staged 11 Jun)

## Paid call-site inventory (109 hits)

- **Anthropic API** (32): `MarketSquare/bea_main.py:2337`, `MarketSquare/bea_main.py:2339`, `MarketSquare/bea_main.py:3576`, `MarketSquare/bea_main.py:3579`, `MarketSquare/bea_main.py:3720`, `MarketSquare/bea_main.py:3722`, `MarketSquare/bea_main.py:3795`, `MarketSquare/bea_main.py:3797`, `MarketSquare/bea_main.py:4099`, `MarketSquare/bea_main.py:4102`, `MarketSquare/bea_main.py:7135`, `MarketSquare/bea_main.py:7138` …
- **Anthropic SDK** (5): `MarketSquare/bea_main.py:7854`, `MarketSquare/data_audit.py:154`, `CityLauncher/emailer/emailer.py:99`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (13): `MarketSquare/citylauncher_ops.html:717`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:172`, `CityLauncher/dashboard/citylauncher.html:899`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218`, `CityLauncher/scraper/sources/google_maps.py:495`, `CityLauncher/scraper/sources/google_maps.py:501`, `CityLauncher/scraper/sources/property24.py:320`, `CityLauncher/scraper/sources/property24.py:331` …
- **Paid data feeds** (58): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:68`, `MarketSquare/ai_service_tiers.py:69`, `MarketSquare/ai_service_tiers.py:71`, `MarketSquare/ai_service_tiers.py:156`, `MarketSquare/ai_service_tiers.py:157`, `MarketSquare/ai_service_tiers.py:164`, `MarketSquare/ai_service_tiers.py:165`, `MarketSquare/ai_service_tiers.py:196`, `MarketSquare/ai_service_tiers.py:197`, `MarketSquare/ai_service_tiers.py:201`, `MarketSquare/ai_service_tiers.py:202` …
- **Paystack (txn)** (1): `MarketSquare/payments.py:32`

**Totals:** 0 critical · 4 warnings · 20 ok · 18 info
