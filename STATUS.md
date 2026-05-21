# TrustSquare - STATUS.md

## Live State
BEA v1.3.0 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 6 real listings live (IDs 93-97 Property + ID 103 Collectors, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- marketsquare.html: 340 KB HTML shell
- Static assets: /static/ms.css?v=77 (103 KB) + /static/ms.js?v=78 (~510 KB), cached 1 year
- World Heritage: 120 sites from BEA /wonders
- Demo data: 293 listings + 40 sellers from BEA /demo-listings and /demo-sellers
- smoke_test.py: 35-check post-deploy safety net (scans html + ms.js combined corpus)
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use
- POST /listings/vision-draft live — photo-first AI onboarding BEA endpoint
- guided-onboard Step 1 live — multi-photo upload + AI vision + missing_shots guidance
- Route 2 (in-app Sell+) — email/name capture works; EXIF rotation fixed; seller CV anonymous
- AI Tuppence Services live: AI1 rewrite + AI2 audit (admin) + AI3 price-check (buyer app)
- Local Market tile count fixed in demo mode (reads LISTINGS array, not BEA)
- Me tab: Profile photo row with Change link added to Personal Details
- Wallet screen: AI Tuppence services menu with costs + navigation paths
- missing_shots Phase 2: confidence bar gated by missing shots count (−12.5% per shot)

## Last Completed (Session 73)
- Built 3 AI Tuppence service BEA endpoints: POST /listings/{id}/ai-rewrite, /ai-audit, /price-check
- Shared helper `_deduct_tuppence()` — HTTP 402 if insufficient balance, ledger entry on success
- AI1 (Listing Rewrite): Haiku rewrites title + desc; pre-fills admin edit form fields on success
- AI2 (Seller Audit): Haiku returns 3 coach actions in context of intro count + trust score
- AI3 (Buyer Price Check): Sonnet returns verdict + market context + suggested SA price range
- Admin dashboard: gold AI Tuppence strip with Rewrite + Why No Intros buttons on every edit modal
- Buyer app: "💡 Is this a fair price?" button on listing detail card with colour-coded verdict card
- missing_shots Phase 2: displayed confidence reduced 12.5%/missing shot; amber guidance message added
- Cache-busted ?v=76 → ?v=78; all 35 smoke checks passing

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
Current version: ?v=78

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- Tuppence refund purge — NEXT_SESSION_TUPPENCE_NO_REFUND.md — must complete before patent filing
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)
- AI3 pricing review — Sonnet price-check margin near-zero at 1T; consider raising to 2T (Session 75)

## Next Session (Session 74)
Goal: CityLauncher email template polish + magic link pre-fill + Tier 2 AI Tuppence services

### Session 74 Build Plan

**Part A — CityLauncher email templates**
1. Update Property, Services, Tutors, Casuals email templates to include AI-generated listing preview pulled from BEA at send time — show seller's actual title, price, suburb, AI snippet rather than generic category copy
2. Magic link pre-fill: ensure email links carry category, city, and any BEA draft ID so guided-onboard Step 1 is pre-seeded on arrival

**Part B — Tier 2 AI Tuppence services (BACKLOG.md)**
3. **AI4 — Property Yield Calculator** (1T, Haiku) — `POST /listings/{id}/yield-calc?email=`; for Property listings, calculates gross yield, net estimate, and SA market comparison
4. **AI5 — Batch Card Listings** (2T, Sonnet Vision) — semi-automated bulk listing for trading card sellers; accepts multi-photo set, returns array of draft listings

**Part C — Ongoing polish**
5. Featured strip: mark real BEA listings as featured so the strip is non-empty on live site
6. Tuppence refund purge — complete NEXT_SESSION_TUPPENCE_NO_REFUND.md task before EULA goes external

### Key implementation notes for Session 74
- Email template update: pull from `/listings/mine?email=` at send time in n8n flow (CityLauncher project)
- Yield calc: Haiku, ~$0.001/call, data from listing fields (price, listingType, suburb) + SA yield tables
- Batch cards: Sonnet Vision, ~$0.023/card; cap at 10 cards per 2T call; return array of draft JSONs
- Magic link: ?magic=1&name=...&email=...&cat=...&city=... already wired; just need draft_id param added

## Blockers
- CIPC registration confirmed (2026/340128/07) - Paystack live mode still pending activation
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
- Tuppence refund purge must complete before EULA published externally
