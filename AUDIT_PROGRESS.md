# TrustSquare — Commercial Readiness Audit · Running Change Log

Companion to `TrustSquare_Commercial_Readiness_Audit.docx`. One line per change.
Severity-tagged findings (S=security, C=cost, P=perf, O=ops, D=data) match the report.

## Session 31 May 2026 — Audit + Phase 1 start

**Audit produced:** full-stack findings report (13 findings ranked CRIT/HIGH/MED) + 4-metric cost model. 128 BEA endpoints reviewed; no hardcoded secrets, all SQL parameterised, WAL already on.

**Fixes applied this session:**
- [S2 · CRIT · DONE] Pulled server-only modules `auth.py`, `database.py`, `storage.py` into the repo (payments.py already present). Verified byte-identical to server via sha256. Your auth/payment/storage IP is now versioned + backed up, not server-only.
- [S1 · CRIT · DONE] `auth.py`: removed guessable default API key (`ms_admin_changeme`). BEA now refuses to start if `MS_API_KEY` is unset (fail-closed). Confirmed `MS_API_KEY` is set on the server, so deploy is safe.
- [P1 · partial] Confirmed SQLite WAL + synchronous=NORMAL already enabled in database.py — corrected in report. Postgres migration remains a Phase-3 item.

**Next (Phase 1 cont.):** C1 token ceiling (per-user + platform daily budget, refuse-when-exceeded) · C2 real token-count costing · C3 add spend logging to AI3/AI4 · dashboard cost panels.

**Cost snapshot (modelled, see report for detail):** every paid AI op 93–99% margin; 100 users ≈ $11.61/mo total; 100k users ≈ $2,474/mo total, net positive. Real-token actuals replace these once C2/C3 land.

## Session continuity design (decided 31 May 2026)
Zero-manual-git session handoff, server as source of truth. See SESSION_BOOTSTRAP.md.
- Session end: Claude scp's STATUS/CHANGELOG/AUDIT_PROGRESS to server (no git, no manual push).
- Session start: paste "New TrustSquare session — baseline from the server and continue."
  Claude fetches /dashboard/summary and briefs back. Plus a scheduled morning brief (hands-off).
- Honest limit: a chat must be opened by a human, so the minimum input is one pasted line.
- Phase-1 build items: enrich /dashboard/summary (audit + 4 cost metrics + tasks);
  scheduled morning-brief task; deterministic session-end scp helper.

## Session 97 — 31 May 2026 · Phase 1 cost guardrails landed

- [C2 · DONE] Real-token costing. `_MODEL_PRICE` (per-1M-token list prices) + `_token_cost()` + `_usage_tokens()`. `ai_spend_log` += input_tokens/output_tokens/cost_is_real. `_log_ai_spend()` takes optional token counts → exact cost when present, flat estimate otherwise. Wired into all 7 paid AI ops. Live: real_token_pct 0→7.7% on first real call.
- [C3 · DONE] AI3 (price-check) + AI4 (yield) now log spend with real tokens (were unlogged).
- [C1 · DONE] `_check_cost_ceiling()` hard daily ceiling — REFUSES (429), not just alerts. Per-user ($0.50 default) + platform ($100 default) caps in ai_spend_config. Superusers exempt from user rail; fail-open on error; 0=off. Live-verified refusal: platform cap < today's spend → 429 + no spend logged.
- [C4 · DONE] `GET /dashboard/cost` (no-auth) + "💰 AI COST & MARGIN" dashboard panel: cost/user, cost/call, margin, real-token %, modelled @100/@100k, ceiling bar, per-endpoint ●real/○est. `/admin/ai-spend` enriched; config PUT accepts ceilings.
- Deployed main.py + dashboard.html, BEA restarted clean, Cloudflare purged, smoke 30/30. Server backups: main.py.s96bak, dashboard.html.s96bak.

**Next (Phase 1 close → Phase 2):** O2 guarded sync of auth/database/storage/payments into auto-deploy. Then Phase 2 audit items.

## Session 98 — 31 May 2026 · Operator-reported UX/data fixes (not audit findings)

- Dashboard: AI Cost panel moved above Email Triage.
- Session-end checklist rewritten (CLAUDE.md) — baseline write-back (scp 4 docs) is now a mandatory step; dashboard is live-data-driven, no DATA hand-edit.
- MtG cards: 9 sideways live cards rotated upright (234 left alone — genuinely landscape). Forward fix: `_vision_orient_image()` on landscape Collectors uploads (text-based, EXIF-independent). Admin sends category=Collectors.
- Horizontal card rows: arrows moved inside edge + shown all viewports; strips flex-wrap:nowrap + touch scroll. ms.css v114.
- O2 (auth/db/storage/payments deploy-sync) STILL deferred — next session priority.

## Session 99 — 31 May 2026 · O2 DONE (auto-deploy module sync)

- [O2 · DONE] `deploy_marketsquare.bat` now syncs `auth.py`/`database.py`/`storage.py`/`payments.py` to the server (pre-flight existence checks + new Step 3d scp before BEA restart + post-deploy verify line). These were repo-only and never auto-deployed.
- Live-deployed the four modules this run (server `auth.py` was still the pre-S1 `ms_admin_changeme` version — now the hardened fail-closed one). MS_API_KEY confirmed set in systemd env + running process first; server auth.py backed up to `auth.py.bak-20260531`. AST 4/4 OK, BEA active, /health v1.3.1, bad-key→401, CF purged, smoke 30/30.
- **Phase 1 + O2 now all CLOSED.** Next open items are Phase 2 audit findings from the readiness report.


## Session 100 — 1 June 2026 · Phase 2 starts — S4 CORS lock-down

- [S4 · HIGH · DONE] BEA CORS restricted from `allow_origins=["*"]` + `allow_origin_regex=".*"` to an explicit allowlist (`https://trustsquare.co`, `https://www.trustsquare.co`); regex removed; `allow_credentials` stays False. Same-origin apps + header/email auth → no legitimate caller affected. Deployed main.py (backup `main.py.bak-20260601`), AST OK local+server-venv, BEA active, /health v1.3.1, CF purged, smoke 39/39. Live: allowed origin echoed in ACAO, evil origin blocked (no ACAO).
- Continuity fix: also completed the **Session-99 baseline write-back** the previous runner had skipped (dashboard was stuck on Session 98 though O2 was done/committed). Docs now scp'd; /dashboard/summary current.
- **Phase 2 remaining:** S3 (HIGH — move API key from `?api_key=` query param to X-Api-Key header only; verify/remove the CDN header-stripping assumption first), S5 (MED — gate test/auto-approve payment endpoints behind a production env flag, fail-closed). Then S-sweep input validation, D1 fabrication sweep (Phase 4).
