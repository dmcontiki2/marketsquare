# TrustSquare — Status

## Live State
BEA v1.3.1 · FastAPI + SQLite · Hetzner CPX32 (8GB RAM) + 100GB volume · trustsquare.co · 56 live listings · World Heritage layer 332 sites · AI email triage live (draft-only) · Session 94 complete

## Last Completed (Session 94 — 2026-05-30)
- **AI email triage — end to end.** `POST /email/inbound` (secret-auth) classifies inbound mail with Claude Haiku → `{category, urgency, draft_reply, auto_safe}`, stores in new `email_triage` table, AI spend logged. Categories: support/billing/legal/compliance/spam/other.
- **Conservative auto-send gate**: draft-only by default. Auto-reply only when `EMAIL_AUTO_SEND=1` + `GMAIL_APP_PASSWORD` set + model `auto_safe` + category ∈ {support,billing}. Legal/compliance/ambiguous always held. Spam → skipped.
- `GET /admin/email-triage` (API-key) for ops review. `_smtp_send_reply()` Gmail SMTP sender (587 STARTTLS), threads replies.
- **Cloudflare Email Worker** built (`cloudflare_email_worker/`): postal-mime parse → POST to BEA + safety-net forward to inbox, never bounces mail. wrangler.toml + README + package.json.
- `EMAIL_INBOUND_SECRET` generated, added to `/etc/environment`, BEA restarted. Verified live: support→drafted, spam→skipped, legal→drafted/high, bad secret→401. Smoke 30/30 ✅.
- ⚠️ **Repaired truncated local `bea_main.py`** (was 9698 lines, missing `get_tuppence_history`+) by rebuilding from server's good copy before editing. Now 9972 lines, matches server.
- **For David**: (1) deploy worker via Wrangler + set `EMAIL_INBOUND_SECRET` secret (value in CHANGELOG); point Email Routing at it. (2) Add `GMAIL_APP_PASSWORD`+`EMAIL_AUTO_SEND=1` later to enable auto-reply. (3) Commit `bea_main.py` + `cloudflare_email_worker/` + docs from PowerShell.

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
- **Kronborg Estate listings**: 39 apartments (IDs 192–230) batch-created and published under miconradie1@gmail.com. Waterkloof, Pretoria. Prices R8,990–R35,990/pm. Photos uploaded for units 102a–116. Units 201+ need photos added via admin tool.
- **Yield calculator**: Button relabelled "📈 Investor Yield Calculator" with subtitle clarifying it's for investors, not renters. Admin tool updated.
- **Shopping POIs**: Added supermarket/grocery/convenience tags, 3km radius for shopping vs 15km for other categories. Local shops now appear correctly.
- **Overpass mirrors**: Three independent public mirrors confirmed working. Self-hosted Overpass DB import completed (SA, 39GB on volume) but index files corrupted — container deferred to Session 89.
- Smoke test: 30/30 ✅

## Last Completed (Session 87g — 2026-05-27)
- POI categories fixed: BEA now filters generic OSM names ("school ground" etc.) and deduplicates within 200m. Listing 169 POIs re-fetched — now shows Schools, Universities, Shopping, Hospitals, Police (5 tabs, all named). UP - Groenkloof not in OSM as amenity=university (OSM gap). BEA deployed.

## Last Completed (Session 87f — 2026-05-27)
- Map pin fix: `listing_lat`/`listing_lng` now mapped into live listing objects in `loadLiveListings()`. Map renderer uses `l.listing_lat || l.suburb_lat` — previously only suburb coords were mapped so listing-specific pins never appeared. Listing 169 (Brooklyn property) now shows pin at correct coordinates. ms.js v122 deployed.

## Last Completed (Session 87e — 2026-05-27)
- Price check panel headers now category-aware (Property→"LOCAL PROPERTY MARKET"/"REGIONAL & NATIONAL MARKET", Cars→"SA USED CAR MARKET"/"BOOK VALUE & NATIONAL", etc.). Contrast fixes: 16x rgba white text bumped from .5/.6 to .8/.85 opacity across sell flow + vision overlay. Nearby amenities fixed for listing 169 (geo_city_id was NULL — root cause: create_listing INSERT didn't set it; fixed for all future listings). ms.js v118 deployed.

## Last Completed (Session 87d — 2026-05-27)
- AI trust coach dynamic tier target: score_target now points to next tier above seller's current score (65 → targets 70 "Trusted", not hardcoded 50). Intro text always overridden server-side to prevent AI hallucinating old target. All fallback paths updated. BEA file truncation repaired again (ai-batch-cards closing lines).

## Last Completed (Session 87c — 2026-05-27)
- AI trust coach guidance fixed: `current_score` now reads from `users.trust_score` (was recomputing from credentials, showing 15 instead of 65). All category transaction signals now show "My Dashboard → Intros tab" instructions. AI no longer recommends already-earned signals. BEA file repaired — was silently truncated mid-string at line 9002.

## Last Completed (Session 87b — 2026-05-27)
- Trust tab ID upload: "Upload ID →" action button on unearned Government-issued ID signal row. BEA POST /users/{email}/upload-id (no API key, auto-approves, +15 pts). Score updates live without page reload. ms.js v114, ms.css v113.

## Last Completed (Session 87 — 2026-05-26)
- Category Home Mode: long-press any category tile to personalise the home screen. Full-bleed hero, live count + price range stats, CTA to Browse. One-time tooltip, ⭐ star on active tile, Reset Home button. Persisted in localStorage. All 7 categories supported. ms.js v113, ms.css v112 deployed.
- Smoke test: 30/30 ✅

## Blueprint v1.1 Complete (Sessions 80–84)
All five sessions of the photo pipeline + listing lifecycle build plan are done:
- listing_photos table (r2_key UNIQUE, ON DELETE CASCADE)
- listing_tier_config (single source of truth for tier timing)
- seller_extra_slots (extra slot purchase audit ledger)
- expires_at + warning_sent_at on listings, all 17 live listings backfilled
- BEA Photo API: presign, confirm, delete, reorder, list
- GET /listings/{id} returns photos[] array
- Expiry worker (live→expired at expires_at, hourly)
- Warning worker (n8n webhook 7 days before expiry, 6-hourly) — NOW WIRED TO LIVE n8n
- Admin UI: presign→PUT→confirm upload, structured photo strip, per-operation delete
- Auto-seed at publish + create — pipeline fully self-maintaining

## Last Completed (Session 91 — 2026-05-29)
- **Subscription tier redesign**: 5 tiers — Free $0/2 slots, Standard $12/10, Professional $20/25, Business $40/60, Elite $100/500. DB: `slot_limit`, `pending_downgrade_tier`, `billing_period_end` on `users`. BEA: slot enforcement at publish (HTTP 402 on limit breach), `GET /subscription/tiers`, `GET /users/{email}/subscription`, downgrade-to-free endpoint, pending downgrade worker at startup. Admin UI: rebuilt billing panel with plan card, slot bar, tier cards. Superusers: 500 slot limit.
- **Real transaction history**: `GET /tuppence/history` endpoint (paginated, running balance). Tuppence screen wired with live data + load-more. My Space Billing tab transaction section. Monthly grouping, type icons, coloured amounts.
- Smoke test: 30/30 ✅.
- **Subscription tier redesign**: 5 tiers — Free $0/2 slots, Standard $12/10, Professional $20/25, Business $40/60, Elite $100/500. DB: `slot_limit`, `pending_downgrade_tier`, `billing_period_end` on `users`. BEA: slot enforcement at publish (HTTP 402 on limit breach), `GET /subscription/tiers`, `GET /users/{email}/subscription`, downgrade-to-free endpoint, pending downgrade worker at startup. Admin UI: rebuilt billing panel with plan card, slot bar, tier cards. Superusers: 500 slot limit. Smoke test: 30/30 ✅.

## Last Completed (Session 92 — 2026-05-29)
- **Transaction history**: GET /tuppence/history BEA endpoint live. Tuppence screen + Billing tab wired with real paginated data, monthly grouping, type icons, running balance.
- **Billing tab fixes**: Plans loading fixed (cache-bust v127), T&C modal now renders clean HTML from Word doc source.
- **EULA v1.6**: All 18 identified gaps closed. Removed reviewer notes. FICA repositioned — not applicable to TrustSquare as introduction-only platform. Tuppence recharacterised as platform service fee. All [COUNSEL REQUIRED] placeholders filled. 3 [COUNSEL REVIEW] flags remain for attorney.
- **Email infrastructure**: 4 live @trustsquare.co addresses via Cloudflare Email Routing (support/legal/billing/compliance → dmcontiki2@gmail.com). Catch-all enabled. Gmail filters + labels configured.
- Smoke test: 30/30 ✅

## Next Session (95)
- Read STATUS.md first. Session 94 complete. Go straight into execution.
- **Finish email triage rollout (David action)**: deploy the Cloudflare worker (`cloudflare_email_worker/`), set its `EMAIL_INBOUND_SECRET` Wrangler secret, and point Email Routing rules at it. Optionally add `GMAIL_APP_PASSWORD`+`EMAIL_AUTO_SEND=1` to enable auto-reply for support/billing.
- Recommended priorities:
  1. **Self-hosted Overpass (BLOCKER)** — corrupt index files. Re-import SA PBF, wire localhost:12345 as primary BEA mirror.
  2. **GET /listings pagination (M0)** — replace LIMIT 200 with offset pagination + infinite scroll.
  3. **Paystack plan wiring** — create Paystack subscription plans for the 4 paid tiers; wire plan_code into the subscription initialize endpoint.
  4. **Admin ops: email-triage panel** — surface `GET /admin/email-triage` in dashboard.html (drafts + 30-day category counts).
  5. **EULA v1.6 attorney review** — send to Michalsons/Werksmans/Hogan Lovells before publish.
  6. **Yield calculator breakdown (H7a)** — render full workings + financial advice disclaimer.
- Standing reminders: set AI spend config (`PUT /admin/ai-spend/config` with monthly_income_usd) once first paid subs arrive; update Cost_Breakdown_GlobalLaunch.xlsx with tier prices ($12/$20/$40/$100).
