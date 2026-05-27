# TrustSquare — Status

## Live State
BEA v1.3.2 · FastAPI + SQLite + Redis · Hetzner CPX32 · trustsquare.co · 17 live listings · Session 87g complete

## Last Completed (Session 87g — 2026-05-27)
- POI categories fixed: BEA now filters generic OSM names ("school ground" etc.) and deduplicates within 200m. Listing 169 POIs re-fetched — now shows Schools, Universities, Shopping, Hospitals, Police (5 tabs, all named). UP - Groenkloof not in OSM as amenity=university (OSM gap). BEA deployed.

## Last Completed (Session 87f — 2026-05-27)
- Map pin fix: `listing_lat`/`listing_lng` now mapped into live listing objects in `loadLiveListings()`. Map renderer uses `l.listing_lat || l.suburb_lat` — previously only suburb coords were mapped so listing-specific pins never appeared. Listing 169 (Brooklyn property) now shows pin at correct coordinates. ms.js v122 deployed.

## Last Completed (Session 87e — 2026-05-27)
- Price check panel headers now category-aware (Property→"LOCAL PROPERTY MARKET"/"REGIONAL & NATIONAL MARKET", Cars→"SA USED CAR MARKET"/"BOOK VALUE & NATIONAL", etc.). Contrast fixes: 16x rgba white text bumped from .5/.6 to .8/.85 opacity across sell flow + vision overlay. Nearby amenities fixed for listing 169 (geo_city_id was NULL — root cause: create_listing INSERT didn't set it; fixed for all future listings). ms.js v118 deployed.

## Last Completed (Session 87d — 2026-05-27)
- AI trust coach dynamic tier target: score_target now points to next tier above seller's current score (65 → targets 70 "Trusted", not hardcoded 50). Intro text always overridden server-side to prevent AI hallucinating old target. All fallback paths updated. BEA file truncation repaired again (ai-batch-cards closing lines).

## Last Completed (Session 87c — 2026-05-27)
- AI trust coach guidance fixed: `current_score` now reads from `users.trust_score` (was recomputing from credentials, showing 15 instead of 65). All category transaction signals (`tx_1_4`, `tx_5_14`, `tx_15plus` for Collectors/Property/Adventures/Cars) now show "My Dashboard → Intros tab" instructions instead of "System tracked." AI no longer recommends already-earned signals (Upload ID, etc.). BEA file repaired — was silently truncated mid-string at line 9002; restored from git, verified with ast.parse.

## Last Completed (Session 87b — 2026-05-27)
- Trust tab ID upload: "Upload ID →" action button on unearned Government-issued ID signal row. BEA POST /users/{email}/upload-id (no API key, auto-approves, +15 pts). Score updates live without page reload. ms.js v114, ms.css v113.

## Last Completed (Session 87 — 2026-05-26)
- Category Home Mode: long-press any category tile to personalise the home screen. Full-bleed hero, live count + price range stats, CTA to Browse. One-time tooltip, ⭐ star on active tile, Reset Home button. Persisted in localStorage. All 7 categories supported. ms.js v113, ms.css v112 deployed.
- Smoke test: 30/30 ✅

## Last Completed (Session 86 — 2026-05-26)
- Seller intro notification live (H3): n8n workflow new-intro-notification-s86 fires branded email to seller on every intro request — both standard and LM intros. N8N_WEBHOOK_NEW_INTRO wired into BEA env. End-to-end verified.
- Local Market listing parity (H1): LM cards now 2-column (matching standard grid), photo carousel uses listing_photos table, BEA list/detail endpoints return photos[] and correct thumb_url. ms.js/ms.css v111 deployed.
- Smoke test: 30/30 ✅

## Last Completed (Session 85 — 2026-05-26)
- n8n expiry warning workflow live (ID: expiry-warning-s85) — webhook fires branded email to seller 7 days before listing expires
- N8N_WEBHOOK_LISTING_EXPIRY_WARNING set in /etc/environment + .env
- Seller tier enforcement: publish_listing hard-gates at listing_tier_config.max_listings (superusers bypass); create_listing adds advisory cap_warning
- Fixed seller_extra_slots column name (email not seller_email) in both query sites
- Ops tab added to dashboard.html as third nav button — full ops widget layout with live data
- Support Centre live at trustsquare.co/support — password-gated (96315), linked from FEA Me tab + admin header
- Paystack activation response sent — Word doc with 8 screenshots, pricing, refund policy, support infra, live activation request
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

## Next Session (88)
- Read STATUS.md first. Session 87g is complete. Go straight into execution.
- Recommended priorities (check BACKLOG.md for current blockers):
  1. Paystack live mode — activate when approval arrives (paste sk_live_ + webhook secret into .env)
  2. Maroushka + Dave phone test — lightbox, back buttons, My Requests tab (H4 in BACKLOG)
  3. Buyer intro accept/decline notification — buyer emailed when seller responds (H2 in BACKLOG)
  4. Support page content review — refine FAQs, consider removing password gate
  5. H5 Showcase photos — add thumb_url to demo listings 40–51
