# TrustSquare - STATUS.md

## Live State
BEA v1.3.0 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 6 real listings live (IDs 93-97 Property + ID 103 Collectors, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- marketsquare.html: 340 KB HTML shell
- Static assets: /static/ms.css?v=76 (103 KB) + /static/ms.js?v=76 (~510 KB), cached 1 year
- World Heritage: 120 sites from BEA /wonders
- Demo data: 293 listings + 40 sellers from BEA /demo-listings and /demo-sellers
- smoke_test.py: 35-check post-deploy safety net (updated to scan ms.js for function checks)
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use
- POST /listings/vision-draft live — photo-first AI onboarding BEA endpoint
- guided-onboard Step 1 live — multi-photo upload + AI vision + missing_shots guidance
- Route 2 (in-app Sell+) — email/name capture now works; EXIF rotation fixed; seller CV anonymous

## Last Completed (Session 72)
- Fixed Route 2 (in-app Sell+) go-live: added email+name fields to Step 2 for non-magic-link sellers
- Fixed EXIF photo rotation: `ImageOps.exif_transpose()` applied to all 4 PIL image-open calls in BEA
- Fixed seller CV headline: was showing listing title; now shows "{category} Seller" (anonymous)
- Added `missing_shots` to vision-draft response: Claude identifies item type and suggests specific missing photos (MtG card → three red dots, coin → edge + certificate, car → odometer + engine bay, etc.)
- Added "Suggested shots" strip to FEA Zone D: tappable cards per missing shot, opens camera pre-labelled
- Removed debug logging (sobGoLive STATE / Debug: drafts=N) — was left from Session 71 debugging
- Updated smoke_test.py to scan html_and_js combined corpus — fixes false FAILs from external ms.js
- All 35 smoke checks passing; cache-busted to ?v=76

## Last Completed (Session 71)
- Rebuilt guided-onboard Step 1 with 5-zone photo-first AI pattern (Zone A upload → B strip → C overlay → D draft reveal → E skip)
- Added 13 new JS functions for photo-first flow
- Multi-photo input (1–12), thumbnail strip, animated analysis overlay, draft reveal with editable fields
- "✨ Improve wording" button → calls /advert-agent/market-note → shows improved text with Undo
- Cache-bust: ?v=70 → ?v=71; all 30 smoke checks passing

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=76

## Open Actions (carry forward)
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review (remaining [COUNSEL REQUIRED] items: NCC reg no, FICA/KYC justification, NCA applicability, FSCA classification, arbitration clause)
- Tuppence refund purge — NEXT_SESSION_TUPPENCE_NO_REFUND.md — must complete before patent filing
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)

## Next Session (Session 73)
Goal: AI-Powered Listing Polish — email outreach listings + app listings, Tuppence AI services

### Session 73 Build Plan

**Part A — Listing quality polish (all categories)**
1. **AI listing rewrite (Tuppence service)** — seller pays 1T to have Claude rewrite their description using current market language and buyer psychology. BEA endpoint `POST /listings/{id}/ai-rewrite?email=`. Haiku model. Deducts 1T from seller balance, returns improved title + description. Available from listing edit screen in admin + from the seller's live listing card.
2. **"Why am I not getting intros?" AI audit (Tuppence service)** — seller pays 1T, Claude reviews listing title/description/price/trust score and returns 3 specific improvement actions. BEA endpoint `POST /listings/{id}/ai-audit?email=`. Show as a coach card in admin dashboard.
3. **"Is this a fair price?" buyer check (Tuppence service)** — buyer pays 1T before requesting intro to get a market comparison for the specific listing. BEA endpoint `POST /listings/{id}/price-check?email=`. Sonnet model with web context. Show on listing detail card.

**Part B — Email outreach listing polish**
4. **CityLauncher email templates** — update Property, Services, Tutors, Casuals templates to include AI-generated listing preview pulled from BEA at send time. Each email shows the seller's actual listing card (title, price, suburb, AI-generated description snippet) rather than generic category copy.
5. **Magic link pre-fill from email** — ensure email links carry enough context that the guided-onboard Step 1 is pre-seeded with category, city, and any BEA draft already in the system.

**Part C — missing_shots Phase 2 (confidence gating)**
6. **Lower confidence score when critical shots missing** — if `missing_shots.length > 0`, reduce the displayed confidence bar by 10–15% per missing shot. Add "Complete your photo set to increase buyer confidence" message below the strip.

### Key implementation notes for Session 73
- Tuppence deduction: use existing `tuppence_ledger` table with negative delta; check balance before allowing call
- AI rewrite: Haiku model, ~$0.001/call — safe to offer at 1T ($2) margin
- Price-check: Sonnet model with market context, ~$0.025/call — justified at 1T
- Email template update: pull from `/listings/mine?email=` at send time in n8n flow
- All new Tuppence services must be non-refundable per platform policy

## Blockers
- CIPC registration confirmed (2026/340128/07) - Paystack live mode still pending activation
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
- Tuppence refund purge must complete before EULA published externally
