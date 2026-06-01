# TrustSquare — Status

## Live State
BEA v1.3.1 · FastAPI + SQLite · Hetzner CPX32 (8GB RAM) + 100GB volume · trustsquare.co · 65 live listings · World Heritage layer 332 sites · AI email triage LIVE · AI Price Check feed-driven + deliver-then-charge · AI cost guardrails LIVE (real-token + hard daily ceiling + dashboard panel) · Card photos: vision auto-orient on collectibles + 9 live cards fixed upright · Backend modules (auth/database/storage/payments) now in guarded auto-deploy (O2) · CORS locked to trustsquare.co origins (S4) · KYC verification path crash-fixed (SCAN-1 SONNET_MODEL + SCAN-2/3/4/6 missing imports re/hashlib/urllib/base64 + _json name + SCAN-5 doc-upload MEDIA_DIR→_LOCAL_MEDIA_DIR) · Session 103 complete

## Last Completed (Session 103 — 2026-06-01)
- **SCAN-5 DONE (CRIT · KYC doc-upload crash-bug).** `upload_seller_document` (`POST /users/{email}/documents`, bea_main.py:7111) used undefined `MEDIA_DIR` in its R2-unconfigured local-fallback branch — a latent `NameError` → HTTP 500 on any document upload when `_S3_CONFIGURED` is false. Replaced with the module's `_LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"` (line 942) after confirming it is the intended dir: it is the same dir `_s3_upload` mirrors to, nginx serves it at `/media/`, and the fallback's returned `url = /media/{safe}` resolves there.
- Latent in prod (R2 is configured, so the fallback never runs) → fix is behavior-neutral on the live path. One surgical Python str.replace (old-string unique); the `_LOCAL_MEDIA_DIR` definition (942) and its existing correct use (972) untouched; `os` (line 9) and `_LOCAL_MEDIA_DIR` both module-level bound so the line resolves at runtime.
- `ast.parse` clean local + BEA venv; deployed main.py (server backup `main.py.bak-20260601-scan5`); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke all-green ✅**.
- **Continuity:** synced the 09:14Z weekly-discovery-scan block into the server's AUDIT_PROGRESS.md (was local-only) and purged the stale Cloudflare-cached `/dashboard/summary` (it had been pinned to a 31 May Session-98 snapshot; now reflects the live session).
- **Cost model impact:** none — undefined name → correct module constant; no new AI calls, no pricing/concurrency change.

## Next Session (104)
- **SCAN-7 (HIGH) — the last KYC crash-bug, then Phase 2 resumes.** `bea_main.py` `background_tasks` undefined at ~9365 inside `vision_draft` (F821) — the spend-logging `background_tasks.add_task(...)` will crash the vision-draft endpoint if reached. Fix: add `background_tasks: BackgroundTasks` to the endpoint signature (`BackgroundTasks` already imported) and confirm FastAPI injects it / the call site is inside the handler. Verify AST + smoke before deploy.
- **After SCAN-7: resume Phase 2 normal order** — **S3** (move API key off the `?api_key=` query param → X-Api-Key header only; verify/remove the CDN header-stripping assumption first), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), **L3a** (support@trustsquare.co real mailbox — SUPPORT_MAILBOX_SETUP.md), then SCAN-8…12 cleanup + the weekly discovery-scan dashboard panel (SCAN-PANEL-1/2) + the ms.js latent-crash fixes JS-1/JS-2 + HTML-1/HTML-2 dead-var cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 102 — 2026-06-01)
- **SCAN-2/3/4/6 DONE (CRIT · KYC crash-bugs, batched).** Four latent `NameError` → HTTP 500 bugs on the SA-ID / KYC verification path in `bea_main.py`, all fixed in one run as the runner override permits (every edit is a top-level import or a name fix in the same file).
- **SCAN-2** bare `re.*` (7428/7455/7461/7558/7614/7757) was unbound — module had only `re as _re_match`. **SCAN-3** `hashlib.sha256` (7456) unbound. **SCAN-4** `urllib.request` (7503/7504) + `base64` (7506) unbound in the KYC doc-fetch block. **SCAN-6** two bare `_json.loads` (~6826/6830) where `_json` was never bound.
- **Fix:** added four module-level imports after `import json` — `import re`, `import hashlib`, `import urllib.request`, `import base64`; and changed the two `_json.loads` → `json.loads`. Pre-existing aliases/in-function imports left untouched (harmless shadows). Single Python str.replace driver, each old-string asserted unique.
- `ast.parse` clean local + BEA venv; module loads under systemd env with re/hashlib/urllib/base64 all bound. Deployed main.py (server backup `main.py.bak-20260601-scan2346`); BEA **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅**.
- **Cost model impact:** none — stdlib imports + a name fix; no new AI calls, no pricing/concurrency change.

## Next Session (103)
- **SCAN-5 (CRIT) then SCAN-7 (HIGH) — finish the KYC crash-bug block, numeric order.** SCAN-5: `MEDIA_DIR` undefined at 7104 in `upload_seller_document` → replace with `_LOCAL_MEDIA_DIR` (`/var/www/marketsquare/media`, line 935) after confirming that's the intended dir. SCAN-7: `background_tasks` undefined at ~9358 in `vision_draft` → add `background_tasks: BackgroundTasks` to the endpoint signature (BackgroundTasks already imported) and confirm the call site is inside the handler. Verify AST + smoke before deploy.
- **After SCAN-7: resume Phase 2 normal order** — **S3** (API key off `?api_key=` query param → X-Api-Key header only), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), **L3a** (support@trustsquare.co real mailbox — see SUPPORT_MAILBOX_SETUP.md), then SCAN-8…12 cleanup + the weekly discovery-scan dashboard panel (SCAN-PANEL-1/2).
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 101 — 2026-06-01)
- **SCAN-1 DONE (CRIT · KYC crash-bug, first of SCAN-1→7 per the runner priority override).** `bea_main.py` referenced `SONNET_MODEL` at three sites in the SA-ID / KYC ID-verification path (model arg + two response payloads, ~7544/7571/7575) but the name was **never defined anywhere** in the module — a guaranteed `NameError` (HTTP 500) the moment that endpoint executed. Latent because the KYC path isn't exercised in prod yet.
- **Fix:** added a module-level constant `SONNET_MODEL = "claude-sonnet-4-6"` next to the other `*_MODEL` constants (line 900, right after `AA_MODEL`), matching the existing `VISION_MODEL` standard. One surgical Python string-replace; `ast.parse` passed locally and in the BEA venv on the server (SONNET_MODEL now resolves: 1 definition + 3 usages).
- Deployed main.py (server backup `main.py.bak-20260601`); BEA restarted **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 30/30 ✅**.
- **Cost model impact:** none — defines a constant already implied by the existing call; no new AI calls, no pricing/concurrency change.

## Next Session (102)
- **SCAN-2→7 (CRIT/HIGH · KYC crash-bugs) — continue in numeric order.** SCAN-2/3/4/6 are all "add a missing module-level import / fix a name" edits in `bea_main.py` (`re`, `hashlib`, `urllib.request`+`base64`, `_json`→`json`) and **may be batched into one run** per the override; SCAN-5 (`MEDIA_DIR`→`_LOCAL_MEDIA_DIR` at 7104) and SCAN-7 (`background_tasks` param on `vision_draft`, 9358) are separate. Verify AST + smoke 30/30 before deploy.
- After SCAN-7: resume Phase 2 normal order — **S3** (API key off `?api_key=` query param → X-Api-Key header only), **S5** (gate test/auto-approve payment endpoints behind a prod env flag, fail-closed), then SCAN-8…12 cleanup.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 100 — 2026-06-01)
- **S4 DONE (Phase 2 · HIGH).** BEA CORS locked down. Was `allow_origins=["*"]` + `allow_origin_regex=".*"` (any site could call the BEA from a visitor's browser); now an explicit allowlist `https://trustsquare.co` + `https://www.trustsquare.co`, regex removed, `allow_credentials` still False.
- Same-origin apps (buyer/admin/dashboard all on trustsquare.co) + header/email auth mean no legitimate caller is affected. One surgical Python string-replace; `ast.parse` passed local and in the BEA venv on the server.
- Deployed main.py (server backup `main.py.bak-20260601`); BEA restarted **active**, `/health` ok v1.3.1; Cloudflare purged; **smoke 39/39 ✅**. Live CORS check: allowed origin → ACAO echoed; `https://evil.example` → no ACAO (blocked).
- **Continuity fix:** also completed the Session-99 baseline write-back the previous runner had left unsynced — the dashboard was still reporting Session 98 even though O2 was done + committed. STATUS/CHANGELOG/AUDIT_PROGRESS now scp'd; /dashboard/summary reflects the true latest session.
- **Cost model impact:** none — security/config change only.

## Next Session (101)
- **Phase 2 cont.** — **S3 (HIGH)**: move API key off the `?api_key=` query param (lands in nginx/Cloudflare logs + browser history) to X-Api-Key header only across the 3 endpoints + ms.js; first verify and then remove the CDN header-stripping assumption that justified the query fallback. **S5 (MED)**: gate the test/auto-approve payment endpoints behind a production env flag, fail-closed (launch blocker while Paystack live-mode pending).
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths; set `monthly_income_usd` via `PUT /admin/ai-spend/config` once first paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 99 — 2026-05-31)
- **O2 DONE (deferred since 96/97/98).** Guarded sync of the four backend modules `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat`. Previously these were imported by `main.py` but never auto-deployed (server-only).
- **deploy_marketsquare.bat**: added (a) pre-flight existence checks for all four modules (abort if any missing), (b) a new **Step 3d** that scp's the four modules to the server *before* the BEA restart so the new code is picked up atomically, each with the standard fail-on-error guard, and (c) a verify line confirming all four are present on the server post-deploy.
- **Live deploy this session**: server `auth.py` was still the old (pre-S1) version with the guessable `ms_admin_changeme` default; deployed the hardened fail-closed version (the other three were already byte-identical). Confirmed `MS_API_KEY` is set in the systemd unit env and the running process before deploying — fail-closed auth is therefore live-safe.
- Backed up server `auth.py` → `auth.py.bak-20260531`. scp'd all four modules; AST-checked each in the BEA venv (4/4 OK); shas now match local exactly. BEA restarted **active**, `/health` ok v1.3.1, bad-key write → 401 (auth still enforced), Cloudflare purged. smoke 30/30 ✅.
- **Cost model impact**: none — deploy-tooling change only, no AI-path or pricing change.

## Next Session (100)
- **Phase 2 audit items** (from the readiness report): next ranked findings after Phase 1 + O2 are now all closed.
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths; set `monthly_income_usd` via `PUT /admin/ai-spend/config` once first paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 98 — 2026-05-31)
- **Dashboard**: AI Cost & Margin panel moved above Email Triage (Ops tab).
- **Session-end write-back now mandatory** (CLAUDE.md checklist rewritten to 5 steps): scp STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to the server every session — dashboard is live-data-driven (no DATA hand-edit). Corrected the stale step-4. This guarantees the latest is always viewable.
- **MtG card orientation**: root cause = EXIF correction can't fix tag-less rotated scans (not a regression). (a) Rotated the 9 genuinely-sideways live cards upright (231,232,233,235,236,237,238,239,240); 234 left alone (genuinely landscape). Verified visually (first pass was 180° off — caught before finalising). (b) Forward fix `_vision_orient_image()`: landscape Collectors uploads get a cheap Haiku text-orientation check → rotate before baking. EXIF-independent, scales, fails open. Admin sends `category=Collectors`.
- **Horizontal card rows**: arrows were positioned outside the strip and clipped; moved inside (4px), shown on all viewports, strips set `flex-wrap:nowrap` + touch scroll. Fixes all 6 carousels. ms.css v114.
- Deployed main.py + dashboard.html + ms.css + admin.html + index.html; BEA restarted clean; Cloudflare purged; smoke 30/30 ✅.
- **Cost model impact**: vision-orient fires only on landscape Collectors uploads (~1 Haiku call, logged + ceiling-bound). Negligible.

## Next Session (99)
- **O2 (deferred since 96/97/98) — do first**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat`. Live-safe (MS_API_KEY set).
- Optional follow-ups: extend vision auto-orient to the single-photo + create-listing photo paths (currently batch-card path covered); set `monthly_income_usd` once paid subs arrive to light the dashboard margin %.
- Standing: self-hosted Overpass re-import (BLOCKER), GET /listings pagination, Paystack plan wiring, EULA v1.6 attorney review.

## Last Completed (Session 97 — 2026-05-31)
- **Phase-1 cost guardrails (audit C1–C3 + dashboard).** All BEA edits via Python string-replacement after a mid-session truncation was caught and the file restored byte-clean from the server.
- **C2 real-token costing**: `_MODEL_PRICE` per-1M-token table + `_token_cost()`/`_usage_tokens()`; `ai_spend_log` += input_tokens/output_tokens/cost_is_real; `_log_ai_spend()` computes exact cost from real tokens (flag `cost_is_real`), flat estimate when absent. Wired into all 7 paid AI ops. Live: real_token_pct 0→7.7% on first real call.
- **C3**: AI3 (price-check) + AI4 (yield) now log spend with real tokens (were unlogged).
- **C1 hard ceiling**: `_check_cost_ceiling()` REFUSES paid AI calls (HTTP 429) when daily per-user ($0.50 default) or platform ($100 default) USD cap is hit. Superusers exempt from user rail; fail-open; 0=off. Live-verified refusal + no-spend-on-refusal. Tunable via `PUT /admin/ai-spend/config`.
- **Dashboard**: no-auth `GET /dashboard/cost` + "💰 AI COST & MARGIN" Ops panel (cost/user, cost/call, margin, real-token %, modelled @100/@100k, ceiling bar, per-endpoint ●real/○est). `/admin/ai-spend` enriched.
- Deployed main.py + dashboard.html, BEA restarted clean, Cloudflare purged, smoke 30/30 ✅. Server backups: `main.py.s96bak`, `dashboard.html.s96bak`.
- **Cost model impact**: per-call economics unchanged; costing now exact (real tokens). C1 is a true spend cap — at the $100/day platform default, max AI exposure ≈ $3,000/mo regardless of load.

## Next Session (98)
- **O2 (deferred from 96/97)**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into `deploy_marketsquare.bat` auto-deploy. The auth.py fail-closed change is live-safe (`MS_API_KEY` set), but wiring needs a coordinated deploy — do it as the first task.
- **Set AI spend config** once first paid subs arrive: `PUT /admin/ai-spend/config` with `monthly_income_usd` (unlocks the margin % on the dashboard) — ceilings already default-on.
- **Phase 2 audit items** (from the readiness report): next ranked findings after Phase 1.
- Standing: self-hosted Overpass re-import (BLOCKER), `GET /listings` pagination (M0), Paystack plan wiring, EULA v1.6 attorney review.
- Continuity: session-end scp of STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to server is the handoff — `/dashboard/summary` parses currentSession from STATUS.

## Last Completed (Session 96 — 2026-05-31)
- **Full commercial-readiness audit** (deliverable: `TrustSquare_Commercial_Readiness_Audit.docx`; running log: `AUDIT_PROGRESS.md`). Reviewed all 128 BEA endpoints, FEA, server modules, deploy, security, cost. Findings: no hardcoded secrets, all SQL parameterised, SQLite WAL already on, every paid AI op modelled at 93–99% margin.
- **S2 (CRIT) DONE**: pulled server-only IP modules `auth.py`, `database.py`, `storage.py` into the repo (payments.py was already local); verified byte-identical to server via sha256. Previously unversioned/unbacked-up.
- **S1 (CRIT) DONE**: removed guessable default API key (`ms_admin_changeme`) from `auth.py` — BEA now fails closed if `MS_API_KEY` unset. Confirmed set on server, safe to deploy.
- **P1**: confirmed WAL + synchronous=NORMAL already enabled (no change needed).
- **Deferred (O2)**: auth/database/storage/payments NOT yet wired into auto-deploy — server copies are source of truth; auth.py change needs a coordinated guarded sync.
- **Cost model impact**: none this session (no AI-path changes). 100 users ≈ $11.61/mo, 100k users ≈ $2,474/mo, both net positive.

## Next Session (97)
- **Phase 1 cont. (the audit's next items):**
  1. **C1** — hard token/cost ceiling per-user + platform-wide: refuse when exceeded, not just alert.
  2. **C2** — derive cost from real API token counts, not flat constants.
  3. **C3** — add missing spend-logging to AI3 (price check) and AI4 (yield).
  4. Cost + margin + server-cost panels on `dashboard.html`.
- **O2**: guarded one-time sync of `auth.py`/`database.py`/`storage.py`/`payments.py` into auto-deploy (coordinated; auth.py fail-closed change is live-safe since MS_API_KEY is set).
- **Continuity**: session-end now scp's STATUS/CHANGELOG/BACKLOG/AUDIT_PROGRESS to the server (done this session — `/dashboard/summary` was stale at Session 94). Add a deterministic session-end scp helper + scheduled morning brief per SESSION_BOOTSTRAP.md.
- Architecture decision (recorded): server scaling/KPI logic lives INSIDE the BEA as read-only observe-and-alert feeding the dashboard — never auto-scale, no new service, no machine that can spend money on its own.

## Last Completed (Session 95 — 2026-05-30, incl. 95b/95c/95d)
- **AI Price Check integrity (95)**: re-architected AI3 on "the model writes the sentence, the system produces the number." New helpers `live_usd_zar()`, `resolve_scryfall_id()`, `scryfall_price_by_id()`, `price_caution()`. Verified Scryfall prices for collectibles; no-feed categories return an honest qualitative guide or cannot_assess.
- **95b deliver-then-charge**: Tuppence deducted only after a verified service is delivered. AI3 no-feed → `cannot_verify`, free. AI4 yield rebuilt — gross computed in Python from purchase price + rent, missing input prompts the user, free until a real number is produced.
- **95c**: softened low-price warning to a neutral price-position note (no fraud/counterfeit language); `fraud_flag()` → `price_caution()`, verdict `below_verified_market`.
- **95d**: `deploy_marketsquare.bat` now auto-bumps `ms.js`/`ms.css` `?v=` and deploys static assets + Cloudflare purge — one-script deploy.

## Last Completed (Session 94 — 2026-05-30)
- **AI email triage — end to end.** `POST /email/inbound` (secret-auth) classifies inbound mail with Claude Haiku → `{category, urgency, draft_reply, auto_safe}`, stores in new `email_triage` table, AI spend logged. Categories: support/billing/legal/compliance/spam/other.
- **Conservative auto-send gate**: draft-only by default. Auto-reply only when `EMAIL_AUTO_SEND=1` + `GMAIL_APP_PASSWORD` set + model `auto_safe` + category ∈ {support,billing}. Legal/compliance/ambiguous always held. Spam → skipped.
- `GET /admin/email-triage` (API-key) for ops review. `_smtp_send_reply()` Gmail SMTP sender (587 STARTTLS), threads replies.
- **Cloudflare Email Worker** built (`cloudflare_email_worker/`): postal-mime parse → POST to BEA + safety-net forward to inbox, never bounces mail. wrangler.toml + README + package.json.
- `EMAIL_INBOUND_SECRET` generated, added to `/etc/environment`, BEA restarted. Verified live: support→drafted, spam→skipped, legal→drafted/high, bad secret→401. Smoke 30/30 ✅.
- **ROLLOUT COMPLETE (done this session)**: Cloudflare worker deployed (dashboard, postal-mime parser), `EMAIL_INBOUND_SECRET` set as Wrangler secret, `support@trustsquare.co` routed to worker. `GMAIL_APP_PASSWORD` + `GMAIL_ADDRESS` + `EMAIL_AUTO_SEND=1` added to `/etc/environment`. Live-verified: real support email auto-replied via Gmail SMTP (status=sent), legal email held (status=drafted). Replies currently send FROM dmcontiki2@gmail.com.
- **Ops dashboard panel**: `GET /dashboard/email-triage` (no-auth, obscure-URL) + "📧 EMAIL TRIAGE" panel on Ops tab — category/status counts + recent emails with drafts inline.
- ⚠️ **Repaired two truncations this session** (large-file Edit hazard): local `bea_main.py` (rebuilt from server, now 9972 lines) and `dashboard.html` (rebuilt tail via Python after a broken copy briefly deployed; now intact, smoke 30/30).
- **For David**: (1) Commit from PowerShell: `bea_main.py`, `dashboard.html`, `cloudflare_email_worker/`, `STATUS.md`, `CHANGELOG.md`. (2) Optional: route `legal@`/`billing@`/`compliance@`/catch-all to the same worker. (3) Optional: switch reply From-address to support@trustsquare.co via a transactional sender (e.g. Resend, already used in CityLauncher).

## Last Completed (Session 93 — 2026-05-29)
- **World Heritage / Wonders layer expanded 120 → 332 sites** (+212; clears ≥320 target). UNESCO-led: 142 UNESCO, 97 National Park, 47 National Museum, 46 Archaeological. South Africa 5 → **30 sites**; 91 countries total.
- **Photos all royalty-free (Wikimedia Commons)** with photographer attribution: 228/231 new scenic photos credit a named author; all 332 photo URLs verified HTTP-200 before deploy. `photo_author`/`photo_licence`/`photo_source` populated from Commons extmetadata.
- **Path fix**: canonical `wonders.json` moved to project root (matches loader + server layout); `assets/` synced; deploy script updated.
- **Auto-link cap 3 → 5** (`auto_link_wonders` default in bea_main.py) — reversible, flagged for David. FEA renders 5 cleanly.
- **All 55 live listings re-linked** via `relink_wonders.py` (seller-set wonders preserved). Pretoria listing now links 5 relevant Gauteng sites.
- Deployed to Hetzner, BEA restarted, Cloudflare purged, `GET /wonders` = 332 live. Smoke test: all checks ✅.
- Corrected stale Session 59 CHANGELOG claim that 400 sites had shipped (they never did).
- ⚠️ **For David**: review the auto-link cap change (3→5) — revert the single `max_links` default if undesired. **Commit `wonders.json` (data file) + bea_main.py + relink_wonders.py + deploy_marketsquare.bat + docs from PowerShell.**

## Last Completed (Session 91 — 2026-05-29)
- **Subscription tier redesign**: 5 tiers — Free $0/2 slots, Standard $12/10, Professional $20/25, Business $40/60, Elite $100/500. DB: `slot_limit`, `pending_downgrade_tier`, `billing_period_end` on `users`. BEA: slot enforcement at publish (HTTP 402 on limit breach), `GET /subscription/tiers`, `GET /users/{email}/subscription`, downgrade-to-free endpoint, pending downgrade worker at startup. Admin UI: rebuilt billing panel with plan card, slot bar, tier cards. Superusers: 500 slot limit.
- **Real transaction history**: `GET /tuppence/history` endpoint (paginated, running balance). Tuppence screen wired with live data + load-more. My Space Billing tab transaction section. Monthly grouping, type icons, coloured amounts.
- Smoke test: 30/30 ✅.

## Last Completed (Session 90 — 2026-05-28)
- **AI guardrails**: Existence gate on 5 open AI endpoints (market-note, coach, guidance, upload-comment, vision-draft). Unknown email → HTTP 401 before any Anthropic call.
- **Spend register**: `ai_spend_log` table + async `_log_ai_spend()` background task logging every AI call (non-blocking). `ai_spend_config` singleton with income/threshold/alert config.
- **Admin endpoints**: `GET /admin/ai-spend` (current-month summary + trend) and `PUT /admin/ai-spend/config` (update income + threshold).
- **Red flag alert**: n8n webhook fires when spend crosses % of income — max once/day. Set `N8N_WEBHOOK_AI_ALERT` in .env and `PUT /admin/ai-spend/config` with your monthly income to activate.
- Smoke test: 30/30 ✅

## Last Completed (Session 89 — 2026-05-28)
- **Kronborg anonymity fix**: Stripped "193 Albert Street" from all 39 listing descriptions. Cleared street_address to NULL. Zero address leaks remain.
- **Kronborg photos**: SCP'd all 39 unit folders. Uploaded 510 photos across 37 listings (avg 14/unit). Multi-photo carousel populated. Unit 109 (video only) and 308 (corrupt JPEG) remain photo-free — Maroushka to supply.
- **POI verification**: All 39 listings have 11 POIs across schools/shopping/hospitals/police. Shopping at 3km confirmed live.
- **Full anonymity pass (all 39 listings)**: Titles renamed "Kronborg Estate" → "Luxury Furnished Apartments". Descriptions stripped of all estate/address references. Map pins cleared (listing_lat/lng → NULL) — all 39 now show suburb centroid (Waterkloof), not building coordinates.
- **Services + features block**: Appended to every listing description — electricity, water, WiFi, cleaning, linen, laundry prices + estate features (luxury, riverside, US Embassy/UN approved).
- **Unit 116 price**: Cleared to NULL (title shows "POA") — Maroushka to re-enter correct price.
- Smoke test: 30/30 ✅

## Last Completed (Session 88 — 2026-05-28)
- **Server upgrade**: CPX22 → CPX32 (8GB RAM, 4 vCPU). Added 100GB Hetzner volume. Moved 39GB Overpass DB to volume (`/mnt/HC_Volume_105840760/overpass`). Root disk: 100% → 22% (57GB free).
- **Kronborg Estate listings**: 39 apartments (IDs 192–230) batch-created and published under miconradie1@gmail.com. Waterkloof, Pretoria. Prices R8,990–R35,990/pm. Photos uploaded for units 102a–116. Unit