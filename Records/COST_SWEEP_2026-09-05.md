# Cost-Compliance Sweep — 2026-09-05
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/busy-vibrant-cori/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:4223 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6705 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6818 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6887 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:6983 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7299 `aa_coach_ask` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:10753 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11009 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:11666 `_sonnet_verify_identity` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:14541 `_anon_ai_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:17220 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:17720 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:17809 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:18389 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:18703 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:18938 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:19293 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:20414 `grade_card_condition` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:21463 `_ts_breaker_heartbeat` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:21535 `planner_heritage_compose` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:21464 `_hb_loop` — ceiling ✓ spend-log ✓
- ✅ **OK** — advert_agent.py:795 `run_model` — metered via Tuppence hold/settle

## Model discipline — Haiku unless paid + metered (P1)

- ℹ️ **INFO** — MarketSquare/AI_BASELINE.json:85 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_BASELINE.json:249 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_BASELINE.json:291 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_BASELINE.json:438 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_CHALLENGER_BOARD.html:64 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_CHALLENGER_BOARD.html:112 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_MODEL_BASELINE_MAP.html:84 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/AI_MODEL_BASELINE_MAP.html:198 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/ai_price_card.json:41 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/ai_price_card.json:101 Sonnet pricing-table entry (per-MTok rate card) — reference data, not a call site
- ℹ️ **INFO** — MarketSquare/ai_provider.py:54 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1698 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:17670 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/dashboard.server.html:1341 model name inside a UI display label — text on a diagram, not a call site (DW-009)
- ℹ️ **INFO** — MarketSquare/DEFENCE_COVERAGE_MAP.html:136 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/main.py:966 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:967 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:9698 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:10263 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:433 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:960 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:45 model constant `REASON_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:46 model constant `REASON_VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/marketing/src/build_set.py:14 model constant `SAMPLE_RUN_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/scripts/maintenance_agent.py:375 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:3586 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:125 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:168 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:272 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:322 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:367 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:401 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:511 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:545 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:597 Sonnet — allowed: paid Level-2, Tuppence-metered
- ℹ️ **INFO** — AdvertAgent/service/advert_agent.py:659 Sonnet — allowed: paid Level-2, Tuppence-metered
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

## Paid call-site inventory (158 hits)

- **Anthropic API** (18): `MarketSquare/ai_provider.py:113`, `MarketSquare/ai_provider.py:114`, `MarketSquare/main.py:1014`, `MarketSquare/main.py:1024`, `MarketSquare/subscription_monitor.py:122`, `MarketSquare/failover/ai_backends.py:13`, `MarketSquare/failover/ai_backends.py:142`, `MarketSquare/failover/ai_backends.py:144`, `MarketSquare/scripts/install_anthropic_key.py:58`, `MarketSquare/scripts/install_anthropic_key.py:59`, `MarketSquare/scripts/peer_pack_ai.py:62`, `MarketSquare/scripts/regression_ledger.py:1076` …
- **Anthropic SDK** (5): `MarketSquare/data_audit.py:154`, `MarketSquare/main.py:8028`, `CityLauncher/emailer/emailer.py:157`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (17): `MarketSquare/ai_provider.py:226`, `MarketSquare/bea_main.py:13850`, `MarketSquare/bea_main.py:13851`, `MarketSquare/bea_main.py:16204`, `MarketSquare/citylauncher_ops.html:727`, `CityLauncher/citylauncher_launch.html:1089`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:429`, `CityLauncher/dashboard/citylauncher.html:928`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:217`, `CityLauncher/scraper/sources/google_maps.py:250` …
- **OpenAI** (41): `MarketSquare/add_openai_key.bat:10`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:13`, `MarketSquare/AI_BASELINE.json:442`, `MarketSquare/ai_provider.py:59`, `MarketSquare/ai_provider.py:156`, `MarketSquare/ai_provider.py:168`, `MarketSquare/ai_provider.py:292`, `MarketSquare/bea_main.py:16226`, `MarketSquare/bea_main.py:16359`, `MarketSquare/bea_main.py:16370` …
- **Paid data feeds** (66): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:110`, `MarketSquare/ai_service_tiers.py:111`, `MarketSquare/ai_service_tiers.py:113`, `MarketSquare/ai_service_tiers.py:198`, `MarketSquare/ai_service_tiers.py:199`, `MarketSquare/ai_service_tiers.py:206`, `MarketSquare/ai_service_tiers.py:207`, `MarketSquare/ai_service_tiers.py:238`, `MarketSquare/ai_service_tiers.py:239`, `MarketSquare/ai_service_tiers.py:243`, `MarketSquare/ai_service_tiers.py:244` …
- **Paystack (txn)** (11): `MarketSquare/bea_main.py:12645`, `MarketSquare/bea_main.py:12655`, `MarketSquare/bea_main.py:12659`, `MarketSquare/bea_main.py:12662`, `MarketSquare/bea_main.py:12666`, `MarketSquare/bea_main.py:16012`, `MarketSquare/payments.py:32`, `MarketSquare/subscription_monitor.py:157`, `MarketSquare/scripts/audit_env_file.sh:8`, `MarketSquare/scripts/fix_paystack_env.py:71`, `MarketSquare/scripts/verify_paystack_key.sh:17`

**Totals:** 0 critical · 0 warnings · 28 ok · 42 info
