# Cost-Compliance Sweep — 2026-09-23
_Principles: P1 $0-first · P2 budget every call · P3 independence/hot-swap. Sweep is static + $0; scanned 7 repos under `/sessions/jolly-inspiring-heisenberg/mnt/Projects`._

## Wrapper compliance — every AI call ceiling-checked + spend-logged (P2)

- ✅ **OK** — bea_main.py:4702 `_vision_orient_image` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:4917 `photos_order_suggest` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:7954 `aa_market_note` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:8067 `listing_draft_from_photos` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:8136 `listing_draft_from_photo` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:8232 `aa_coach` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:8556 `aa_coach_ask` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:12377 `trust_score_guidance` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:12728 `trust_score_upload_comment` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:13397 `_vision_verify_identity` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:16851 `_anon_ai_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:19617 `vision_draft` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:20117 `ai_listing_rewrite` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:20206 `ai_seller_audit` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:20786 `ai_price_check` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:21100 `ai_yield_calc` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:21335 `ai_batch_card_listings` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:21722 `_classify_email` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:22759 `maint_brain` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:23447 `grade_card_condition` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:24876 `_squire_draft_brief` — ceiling ✓ spend-log ✓
- 🔴 **CRITICAL** — bea_main.py:25111 `i18n_translate` — UNWRAPPED & UNMETERED Anthropic call (no ceiling, no spend log, no Tuppence)
- ✅ **OK** — bea_main.py:25784 `_ts_breaker_heartbeat` — ceiling ✓ spend-log ✓
- ✅ **OK** — bea_main.py:25856 `planner_heritage_compose` — ceiling ✓ spend-log ✓
- 🟠 **WARN** — bea_main.py:25163 `_i18n_ask` — helper; caller logs spend, but add a ceiling check
- ✅ **OK** — bea_main.py:25785 `_hb_loop` — ceiling ✓ spend-log ✓
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
- ℹ️ **INFO** — MarketSquare/ai_price_card.json:369 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/ai_provider.py:54 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:1839 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/bea_main.py:20067 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/boards_host.bat:4 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/dashboard.server.html:1592 model name inside a UI display label — text on a diagram, not a call site (DW-009)
- ℹ️ **INFO** — MarketSquare/DEFENCE_COVERAGE_MAP.html:156 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/fix_sandbox_windows.bat:16 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/main.py:966 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:967 Sonnet in the provider-model registry (TASK_MODEL/fallback) — single-source, Tuppence-metered; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:9698 model constant `VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/main.py:10263 model constant `PRICE_CHECK_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/maint_host.bat:8 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/remove_kb5124008.bat:6 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/sandbox_repair.bat:9 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:434 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:962 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:963 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:1380 Sonnet in a reference document describing the model field — not a call site (reference-doc exemption, 30 Aug 2026)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:1404 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/DAILY_WATCH/OPEN_ITEMS.json:1404 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:45 model constant `REASON_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/failover/ai_backends.py:46 model constant `REASON_VISION_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/marketing/src/build_set.py:14 model constant `SAMPLE_RUN_MODEL` = claude-sonnet-4-6 — used by Tuppence-metered endpoints; keep justified
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:3804 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:17032 Fable (claude-fable-5) in reference text — not a call site (DW-047)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:21421 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:23326 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:23328 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:23342 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
- ℹ️ **INFO** — MarketSquare/scripts/regression_ledger.py:23354 `claude-code` is the CLI tool / its GitHub repo, not a model family (DW-128)
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

## Paid call-site inventory (162 hits)

- **Anthropic API** (18): `MarketSquare/ai_provider.py:118`, `MarketSquare/ai_provider.py:119`, `MarketSquare/main.py:1014`, `MarketSquare/main.py:1024`, `MarketSquare/subscription_monitor.py:122`, `MarketSquare/failover/ai_backends.py:13`, `MarketSquare/failover/ai_backends.py:142`, `MarketSquare/failover/ai_backends.py:144`, `MarketSquare/scripts/install_anthropic_key.py:58`, `MarketSquare/scripts/install_anthropic_key.py:59`, `MarketSquare/scripts/peer_pack_ai.py:62`, `MarketSquare/scripts/regression_ledger.py:1121` …
- **Anthropic SDK** (6): `MarketSquare/data_audit.py:154`, `MarketSquare/main.py:8028`, `MarketSquare/_verify_rig/letters/emailer.py:173`, `CityLauncher/emailer/emailer.py:173`, `CityLauncher/orchestration/haiko_agent.py:228`, `CityLauncher/orchestration/strategist_agent.py:301`
- **Google APIs** (18): `MarketSquare/ai_provider.py:231`, `MarketSquare/bea_main.py:16084`, `MarketSquare/bea_main.py:16085`, `MarketSquare/bea_main.py:18588`, `MarketSquare/citylauncher_ops.html:727`, `MarketSquare/scripts/gen_role_pictures.py:58`, `CityLauncher/citylauncher_launch.html:1089`, `CityLauncher/CITYLAUNCHER_REDESIGN.html:50`, `CityLauncher/api/server.py:488`, `CityLauncher/dashboard/citylauncher.html:930`, `CityLauncher/scraper/sources/google_maps.py:14`, `CityLauncher/scraper/sources/google_maps.py:217` …
- **OpenAI** (43): `MarketSquare/add_openai_key.bat:10`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:11`, `MarketSquare/add_openai_key.bat:13`, `MarketSquare/AI_BASELINE.json:442`, `MarketSquare/ai_provider.py:64`, `MarketSquare/ai_provider.py:161`, `MarketSquare/ai_provider.py:173`, `MarketSquare/ai_provider.py:297`, `MarketSquare/bea_main.py:18610`, `MarketSquare/bea_main.py:18747`, `MarketSquare/bea_main.py:18758` …
- **Paid data feeds** (66): `MarketSquare/ai_service_tiers.py:19`, `MarketSquare/ai_service_tiers.py:114`, `MarketSquare/ai_service_tiers.py:115`, `MarketSquare/ai_service_tiers.py:117`, `MarketSquare/ai_service_tiers.py:202`, `MarketSquare/ai_service_tiers.py:203`, `MarketSquare/ai_service_tiers.py:210`, `MarketSquare/ai_service_tiers.py:211`, `MarketSquare/ai_service_tiers.py:242`, `MarketSquare/ai_service_tiers.py:243`, `MarketSquare/ai_service_tiers.py:247`, `MarketSquare/ai_service_tiers.py:248` …
- **Paystack (txn)** (11): `MarketSquare/bea_main.py:14404`, `MarketSquare/bea_main.py:14414`, `MarketSquare/bea_main.py:14418`, `MarketSquare/bea_main.py:14421`, `MarketSquare/bea_main.py:14425`, `MarketSquare/bea_main.py:18364`, `MarketSquare/payments.py:32`, `MarketSquare/subscription_monitor.py:157`, `MarketSquare/scripts/audit_env_file.sh:8`, `MarketSquare/scripts/fix_paystack_env.py:71`, `MarketSquare/scripts/verify_paystack_key.sh:17`

**Totals:** 1 critical · 1 warnings · 31 ok · 57 info
