# Cost-Compliance Sweep — 2026-06-12
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/tmp/shadow/root`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:2285 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3548 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3669 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3743 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3844 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7013 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7274 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9471 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9909 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10003 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10353 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10675 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10916 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11165 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11605 `grade_card_condition` — ceiling ✓ spend-log ✓
- ✅ **OK** — advert_agent.py:709 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/bea_main.py:916 model constant `SONNET_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9290 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9859 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
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

- **Anthropic API** (32): `MarketSquare/bea_main.py:2333`, `MarketSquare/bea_main.py:2335`, `MarketSquare/bea_main.py:3573`, `MarketSquare/bea_main.py:3576`, `MarketSquare/bea_main.py:3717`, `MarketSquare/bea_main.py:3719`, `MarketSquare/bea_main.py:3792`, `MarketSquare/bea_main.py:3794`, `MarketSquare/bea_main.py:4096`, `MarketSquare/bea_main.py:4099`, `MarketSquare/bea_main.py:7132`, `MarketSquare/bea_main.py:7135` …
- **Anthropic SDK** (5): `MarketSquare/bea_main.py:7851`, `MarketSquare/data_audit.py:154`, `CityLauncher/emailer/emailer.py:99`, `CityLauncher/orchestration/strategist_agent.py:301`, `CityLauncher/orchestration/haiko_agent.py:228`
- **Google APIs** (13): `MarketSquare/citylauncher_ops.html:717`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218`, `CityLauncher/scraper/sources/google_maps.py:495`, `CityLauncher/scraper/sources/google_maps.py:501`, `CityLauncher/scraper/sources/property24.py:320`, `CityLauncher/scraper/sources/property24.py:331`, `CityLauncher/scraper/sources/property24.py:480`, `CityLauncher/api/server.py:172` …
- **Paid data feeds** (58): `MarketSquare/test_ai_service_tiers.py:6`, `MarketSquare/test_ai_service_tiers.py:53`, `MarketSquare/test_ai_service_tiers.py:55`, `MarketSquare/test_ai_service_tiers.py:56`, `MarketSquare/test_ai_service_tiers.py:60`, `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:68`, `MarketSquare/ai_service_tiers.py:69`, `MarketSquare/ai_service_tiers.py:71`, `MarketSquare/ai_service_tiers.py:156`, `MarketSquare/ai_service_tiers.py:157`, `MarketSquare/ai_service_tiers.py:164` …
- **Paystack (txn)** (1): `MarketSquare/payments.py:32`

**Totals:** 0 critical · 2 warnings · 20 ok · 18 info
