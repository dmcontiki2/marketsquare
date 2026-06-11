# Cost-Compliance Sweep — 2026-06-11
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/affectionate-zealous-newton/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- 🟠 **WARN** — bea_main.py:2285 `_vision_orient_image` — helper; caller logs spend, but add a ceiling check
- ✅ **OK** — bea_main.py:3536 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3657 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:3758 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6927 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7188 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9385 `vision_draft` — ceiling ✓ spend-log ✓
- 🟠 **WARN** — bea_main.py:9823 `ai_listing_rewrite` — Tuppence-metered (revenue covers it) but NOT spend-logged: tokens invisible to the dashboard
- 🟠 **WARN** — bea_main.py:9911 `ai_seller_audit` — Tuppence-metered (revenue covers it) but NOT spend-logged: tokens invisible to the dashboard
- ✅ **OK** — bea_main.py:10255 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10577 `ai_yield_calc` — ceiling ✓ spend-log ✓
- 🟠 **WARN** — bea_main.py:10818 `ai_batch_card_listings` — Tuppence-metered (revenue covers it) but NOT spend-logged: tokens invisible to the dashboard
- 🟠 **WARN** — bea_main.py:11061 `_classify_email` — helper; caller logs spend, but add a ceiling check
- 🔴 **CRITICAL** — bea_main.py:11488 `grade_card_condition` — UNWRAPPED & UNMETERED Anthropic call (no ceiling, no spend log, no Tuppence)
- ✅ **OK** — advert_agent.py:428 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/bea_main.py:916 model constant `SONNET_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9204 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:9773 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- 🟠 **WARN** — MarketSquare/bea_main.py:10904 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- 🔴 **CRITICAL** — MarketSquare/data_audit.py:158 uses OPUS (claude-opus-4-6) — cost model rejected Opus
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:94 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:141 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:206 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:240 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:277 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:289 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:300 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:331 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:343 Sonnet — allowed: paid Level-2, Tuppence-metered
- 🟠 **WARN** — CityLauncher/orchestration/strategist_agent.py:26 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- ℹ️ **INFO** — CityLauncher/orchestration/strategist_agent.py:74 model constant `STRATEGIST_MODEL` = claude-sonnet-4-8 — used by Tuppence-metered endpoints; keep justified

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

- 🟠 **WARN** — Workbook Assumptions still on OLD tiers ['standard', 'professional', 'business', 'elite']; Simpler Model tiers missing ['starter', 'pro'] — code says [('free', '0'), ('starter', '5'), ('pro', '20'), ('agency', '0')]. Update the workbook.
- ℹ️ **INFO** — Workbook last modified 2026-05-28; latest CHANGELOG cost-impact entry: 11 June 2026 — reconcile if the code moved later

## Live spend

- ℹ️ **INFO** — Live spend: set MS_BEA_URL + MS_API_KEY to pull /admin/ai-spend/summary (endpoint staged 11 Jun)

## Paid call-site inventory (107 hits)

- **Anthropic API** (30): `MarketSquare/bea_main.py:2324`, `MarketSquare/bea_main.py:2326`, `MarketSquare/bea_main.py:3561`, `MarketSquare/bea_main.py:3564`, `MarketSquare/bea_main.py:3706`, `MarketSquare/bea_main.py:3708`, `MarketSquare/bea_main.py:4010`, `MarketSquare/bea_main.py:4013`, `MarketSquare/bea_main.py:7046`, `MarketSquare/bea_main.py:7049`, `MarketSquare/bea_main.py:7252`, `MarketSquare/bea_main.py:7255` …
- **Anthropic SDK** (5): `MarketSquare/bea_main.py:7765`, `MarketSquare/data_audit.py:154`, `CityLauncher/emailer/emailer.py:99`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:300`
- **Google APIs** (13): `MarketSquare/citylauncher_ops.html:717`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:172`, `CityLauncher/dashboard/citylauncher.html:899`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218`, `CityLauncher/scraper/sources/google_maps.py:495`, `CityLauncher/scraper/sources/google_maps.py:501`, `CityLauncher/scraper/sources/property24.py:320`, `CityLauncher/scraper/sources/property24.py:331` …
- **Paid data feeds** (58): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:68`, `MarketSquare/ai_service_tiers.py:69`, `MarketSquare/ai_service_tiers.py:71`, `MarketSquare/ai_service_tiers.py:156`, `MarketSquare/ai_service_tiers.py:157`, `MarketSquare/ai_service_tiers.py:164`, `MarketSquare/ai_service_tiers.py:165`, `MarketSquare/ai_service_tiers.py:196`, `MarketSquare/ai_service_tiers.py:197`, `MarketSquare/ai_service_tiers.py:201`, `MarketSquare/ai_service_tiers.py:202` …
- **Paystack (txn)** (1): `MarketSquare/payments.py:32`

**Totals:** 2 critical · 10 warnings · 12 ok · 17 info
