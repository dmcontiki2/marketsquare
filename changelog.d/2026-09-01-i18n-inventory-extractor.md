## 2026-09-01 — I18N readiness item 1 BUILT: string inventory extractor

RUL-075 preparation lane (freeze intact — nothing the live app serves was touched).
New: scripts/i18n_inventory.py (read-only, stdlib) walks marketsquare.html + ms.js +
ts_fares/ts_report/ts_demo_banner and emits i18n/inventory.json + a trend row per run
(i18n/inventory_trend.csv). trip_essentials.js excluded by design — generated file,
localise at its generator. First measured baseline (1 Sep): 4,813 unique strings —
2,532 high-confidence user-visible, 2,281 js-literal candidates needing Phase-A triage
— ~40,500 words. Readiness items 2–7 (parity harness, pseudo-locale, staging, dictionary
pipeline, flags plan, ledger drafts) remain open toward Fri 30 Oct.
