# Cost-Compliance Sweep — 2026-07-18
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `.`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:12337 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — advert_agent.py:785 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/ai_provider.py:45 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1231 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1232 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:12746 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:966 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:967 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:9614 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:10179 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:45 model constant `REASON_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:46 model constant `REASON_VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/marketing/src/build_set.py:14 model constant `SAMPLE_RUN_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
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
- ℹ️ **INFO** — Workbook last modified 2026-06-21; latest CHANGELOG cost-impact entry: 17 June 2026 — reconcile if the code moved later

## Live spend

- ℹ️ **INFO** — Live spend: set MS_BEA_URL + MS_API_KEY to pull /admin/ai-spend/summary (endpoint staged 11 Jun)

## Operator-only sanctioned paid scripts (P3)

- ✅ **OK** — `AdvertAgent/run_video_reports.py` — sanctioned operator-only paid script (live API by design); not reachable from any app code path

## Paid call-site inventory (113 hits)

- **Anthropic API** (14): `MarketSquare/ai_provider.py:67`, `MarketSquare/ai_provider.py:68`, `MarketSquare/bea_main.py:1279`, `MarketSquare/bea_main.py:1291`, `MarketSquare/main.py:1014`, `MarketSquare/main.py:1024`, `MarketSquare/subscription_monitor.py:122`, `MarketSquare/failover/ai_backends.py:13`, `MarketSquare/failover/ai_backends.py:142`, `MarketSquare/failover/ai_backends.py:144`, `AdvertAgent/run_video_reports.py:37`, `AdvertAgent/run_video_reports.py:125` …
- **Anthropic SDK** (5): `MarketSquare/data_audit.py:154`, `MarketSquare/main.py:8028`, `CityLauncher/emailer/emailer.py:99`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (13): `MarketSquare/citylauncher_ops.html:717`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:172`, `CityLauncher/dashboard/citylauncher.html:899`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218`, `CityLauncher/scraper/sources/google_maps.py:495`, `CityLauncher/scraper/sources/google_maps.py:501`, `CityLauncher/scraper/sources/property24.py:320`, `CityLauncher/scraper/sources/property24.py:331` …
- **OpenAI** (13): `MarketSquare/add_openai_key.bat:19`, `MarketSquare/ai_provider.py:47`, `MarketSquare/ai_provider.py:103`, `MarketSquare/ai_provider.py:108`, `MarketSquare/bea_main.py:1280`, `MarketSquare/bea_main.py:1288`, `MarketSquare/bea_main.py:11675`, `MarketSquare/bea_main.py:11686`, `MarketSquare/main.py:1015`, `MarketSquare/main.py:1022`, `MarketSquare/main.py:9190`, `MarketSquare/subscription_monitor.py:123` …
- **Paid data feeds** (66): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:110`, `MarketSquare/ai_service_tiers.py:111`, `MarketSquare/ai_service_tiers.py:113`, `MarketSquare/ai_service_tiers.py:198`, `MarketSquare/ai_service_tiers.py:199`, `MarketSquare/ai_service_tiers.py:206`, `MarketSquare/ai_service_tiers.py:207`, `MarketSquare/ai_service_tiers.py:238`, `MarketSquare/ai_service_tiers.py:239`, `MarketSquare/ai_service_tiers.py:243`, `MarketSquare/ai_service_tiers.py:244` …
- **Paystack (txn)** (2): `MarketSquare/payments.py:32`, `MarketSquare/subscription_monitor.py:157`

**Totals:** 0 critical · 0 warnings · 8 ok · 27 info
