# TrustSquare - STATUS.md

## Live State
BEA v1.3.0 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 3 real listings live (#93, #102 Property + #104 Collectors, Pretoria) — all featured (boost_until 2030)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- marketsquare.html: 348 KB HTML shell
- Static assets: /static/ms.css?v=86 + /static/ms.js?v=86, cached 1 year
- World Heritage: 120 sites from BEA /wonders
- Demo data: 293 listings + 40 sellers from BEA /demo-listings and /demo-sellers
- smoke_test.py: 35-check post-deploy safety net (scans html + ms.js combined corpus)
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use
- POST /listings/vision-draft live — photo-first AI onboarding BEA endpoint
- guided-onboard Step 1 live — multi-photo upload + AI vision + missing_shots guidance
- Route 2 (in-app Sell+) — email/name capture works; EXIF rotation fixed; seller CV anonymous
- AI Tuppence Services live: AI1 rewrite + AI2 audit + AI3 price-check + AI4 yield-calc + AI5 batch-cards
- Local Market tile count fixed in demo mode (reads LISTINGS array, not BEA)
- Me tab: Profile photo row with Change link added to Personal Details
- Wallet screen: AI Tuppence services menu with costs + navigation paths
- missing_shots Phase 2: confidence bar gated by missing shots count (−12.5% per shot)
- Tuppence refund purge COMPLETE — marketsquare.html + EULA v1.4_Final + Whitepaper v3.1 all clean
- Back buttons on dark backgrounds fixed (ms.css grouped rule for .tn-header/.el-hdr/.cv-edit-hdr/.aa-hdr)
- Tuppence test values: both Introductions + AI Guidance set to 50 (marked 🧪 TEST — grep to rollback before launch)
- ms.js restored from git (was truncated) — all 35 smoke checks passing on v=84
- Anonymity enforcement: vision-draft + AI1 + AI2 system prompts now strip addresses/names/contacts; #go-anonymity-notice banner shown to seller when scrubbed
- Smoke test: live listings check now queries DB directly (category-agnostic) — survives listing deletions
- Multi-photo upload fixed: goHandoff now uploads all goState.photoFiles; photo/draft endpoint maintains photo_urls JSON array
- Photo re-selection fixed: goHandlePhotos + goResetStep1UI now reset input.value so re-picking same files fires onchange
- Anonymity photo suppression: when anonymity_scrubbed=true, violating photos cleared from state + strip; Next button blocked until seller re-shoots
- Intros My Space fixed: GET /intros?status=all now works; buyer_email filter added; self-intro guard added (409)
- AI price-check: David credited 50T on server for testing (dmcontiki2@gmail.com)

## Last Completed (Session 74 continued 10)
- Price check sign-in error fixed: buyerEmail now reads from localStorage not undefined userEmail var; cache v=92; 35/35 passing

## Last Completed (Session 74 continued 9)
- Delete listing fix: gate login now stores email in localStorage; admin_users.email column added; BEA returns email on login; cache v=91

## Last Completed (Session 74 continued 8)
- Anonymity: violating photos silently cleared; seller proceeds normally; optional Add better photos button; cache v=90; 35/35 passing

## Last Completed (Session 74 continued 7)
- Anonymity hard block: removed Keep option; single Replace button + Next disabled until new photos analysed; cache v=89; 35/35 checks passing

## Last Completed (Session 74 continued 6)
- Anonymity warning: replaced hard block with two buttons — 📷 Replace photos (clears + reopens picker) or ✅ Keep & continue (dismisses notice)
- Cache bumped to v=88; all 35 smoke checks passing

## Last Completed (Session 74 continued 5)
- Anonymity photo suppression: goRevealDraft() now clears photoFiles/photoDataUrl + hides strip when anonymity_scrubbed=true; Next button disabled until seller re-shoots
- Cache bumped to v=87; all 35 smoke checks passing

## Last Completed (Session 74 continued 4)
- Photo re-selection bug fixed: goHandlePhotos() + goResetStep1UI() now reset input.value='' so same files re-trigger onchange
- Cache bumped to v=86; all 35 smoke checks passing

## Last Completed (Session 74 continued)
- Back button visibility: ms.css grouped rule fixes dark arrow on navy for .tn-header/.el-hdr/.cv-edit-hdr/.aa-hdr
- Tuppence test values: Introductions + AI Guidance both set to 50 (🧪 TEST — rollback before launch)
- ms.js restored from git (truncated pre-existing issue) + edits reapplied — syntax clean
- Cache bumped to v=83; all 35 smoke checks passing

## Last Completed (Session 74)
- CityLauncher emailer.py: fixed template map, expanded render() placeholders, AI Haiku title generation, magic link draft_id param
- BEA AI4: POST /listings/{id}/yield-calc (1T, Haiku) — Property yield calculator with SA 2026 benchmarks
- BEA AI5: POST /listings/batch-cards (2T, Sonnet Vision) — bulk trading card listing from photos, max 10 cards
- Featured strip: set boost_until=2030 on listings #93, #102, #104 — strip non-empty on live site
- Tuppence refund purge: 6 edits to marketsquare.html, EULA v1.4_Final.docx, Whitepaper v3.1.docx — zero refund language remains
- All 35 smoke checks passing

## Last Completed (Session 72)
- Fixed Route 2 (in-app Sell+) go-live: added email+name fields to Step 2 for non-magic-link sellers
- Fixed EXIF photo rotation: `ImageOps.exif_transpose()` applied to all 4 PIL image-open calls in BEA
- Fixed seller CV headline: was showing listing title; now shows "{category} Seller" (anonymous)
- Added `missing_shots` to vision-draft response: Claude identifies item type and suggests specific missing photos
- Added "Suggested shots" strip to FEA Zone D: tappable cards per missing shot, opens camera pre-labelled
- Removed debug logging (sobGoLive STATE / Debug: drafts=N) — was left from Session 71 debugging
- Updated smoke_test.py to scan html_and_js combined corpus — fixes false FAILs from external ms.js
- All 35 smoke checks passing; cache-busted to ?v=76

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=92

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- Tuppence refund purge — NEXT_SESSION_TUPPENCE_NO_REFUND.md — must complete before patent filing
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip e