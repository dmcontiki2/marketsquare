# Cost-Compliance Sweep — 2026-08-05
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/sharp-elegant-dijkstra/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:3303 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:4957 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:5069 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:5137 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:5232 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:8831 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9081 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:9647 `_sonnet_verify_identity` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11330 `_anon_ai_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:13293 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:13745 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:13827 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:14395 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:14706 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:14936 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:15196 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:16073 `grade_card_condition` — ceiling ✓ spend-log ✓
- ✅ **OK** — advert_agent.py:785 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/ai_price_card.json:91 Sonnet pricing-table entry (per-MTok rate card) — reference data, not a call site
- ℹ️ **INFO** — MarketSquare/ai_provider.py:45 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1345 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1346 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:13695 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- 🟠 **WARN** — MarketSquare/dashboard.server.html:906 Sonnet outside the metered AdvertAgent registry — justify or downgrade to Haiku
- ℹ️ **INFO** — MarketSquare/main.py:966 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:967 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:9614 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:10179 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:45 model constant `REASON_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:46 model constant `REASON_VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/marketing/src/build_set.py:14 model constant `SAMPLE_RUN_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_main.stage2.py:1345 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_main.stage2.py:1346 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_main.stage2.py:13674 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164014.py:1345 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164014.py:1346 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164014.py:13674 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164109.py:1345 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164109.py:1346 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164109.py:13674 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
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

## Paid call-site inventory (146 hits)

- **Anthropic API** (13): `MarketSquare/ai_provider.py:95`, `MarketSquare/ai_provider.py:96`, `MarketSquare/main.py:1014`, `MarketSquare/main.py:1024`, `MarketSquare/subscription_monitor.py:122`, `MarketSquare/failover/ai_backends.py:13`, `MarketSquare/failover/ai_backends.py:142`, `MarketSquare/failover/ai_backends.py:144`, `MarketSquare/scripts/regression_ledger.py:641`, `AdvertAgent/run_video_reports.py:37`, `AdvertAgent/run_video_reports.py:125`, `AdvertAgent/service/advert_agent.py:29` …
- **Anthropic SDK** (5): `MarketSquare/data_audit.py:154`, `MarketSquare/main.py:8028`, `CityLauncher/emailer/emailer.py:101`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (17): `MarketSquare/bea_main.py:12451`, `MarketSquare/citylauncher_ops.html:717`, `MarketSquare/_to_delete/stray-stage-copies-20260805/bea_main.stage2.py:12430`, `MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164014.py:12430`, `MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164109.py:12430`, `CityLauncher/citylauncher_launch.html:1052`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:172`, `CityLauncher/dashboard/citylauncher.html:899`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:185`, `CityLauncher/scraper/sources/google_maps.py:218` …
- **OpenAI** (39): `MarketSquare/add_openai_key.bat:10`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:13`, `MarketSquare/ai_provider.py:50`, `MarketSquare/ai_provider.py:138`, `MarketSquare/ai_provider.py:150`, `MarketSquare/bea_main.py:12473`, `MarketSquare/bea_main.py:12594`, `MarketSquare/bea_main.py:12605`, `MarketSquare/bea_main.py:13312`, `MarketSquare/main.py:1015` …
- **Paid data feeds** (66): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:110`, `MarketSquare/ai_service_tiers.py:111`, `MarketSquare/ai_service_tiers.py:113`, `MarketSquare/ai_service_tiers.py:198`, `MarketSquare/ai_service_tiers.py:199`, `MarketSquare/ai_service_tiers.py:206`, `MarketSquare/ai_service_tiers.py:207`, `MarketSquare/ai_service_tiers.py:238`, `MarketSquare/ai_service_tiers.py:239`, `MarketSquare/ai_service_tiers.py:243`, `MarketSquare/ai_service_tiers.py:244` …
- **Paystack (txn)** (6): `MarketSquare/bea_main.py:12370`, `MarketSquare/payments.py:32`, `MarketSquare/subscription_monitor.py:157`, `MarketSquare/_to_delete/stray-stage-copies-20260805/bea_main.stage2.py:12349`, `MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164014.py:12349`, `MarketSquare/_to_delete/stray-stage-copies-20260805/bea_verify_164109.py:12349`

**Totals:** 0 critical · 1 warnings · 24 ok · 37 info
