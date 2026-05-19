# TrustSquare · STATUS.md

## Live State
BEA v1.2.0 live at trustsquare.co · FastAPI + SQLite (9 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 (4 cities: Pretoria / New York / London / Sydney)
- World Heritage: 120 sites bundled in app, instant render + 3s background refresh
- All categories show correct live counts (no demo bleed-through)

## Last Completed (Session 63)
- Fixed all categories showing 0 listings (nested backtick JS syntax error, regression from S62)
- Fixed demo listings bleeding through to live site (Local Market tile, renderGrid, renderCatCounts)
- Fixed View seller profile crashing on live BEA listings (sellerIdx null, IIFE pattern)
- Fixed live listing photos not loading (photo_urls JSON array never parsed by FEA)
- Fixed seller sign-in path: added inline email sign-in to My Space tab (no magic link needed)
- Fixed openBEASellerProfile crash (cvScore undefined, used l.trust instead)
- Added smoke_test.py: 28-check post-deploy safety net, all checks passing
- Updated CLAUDE.md session-end checklist to require smoke test before close

## Open Actions (Session 63 carry forward)
- Company registration number (2026/340128/07) - insert into EULA + footer
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)

## Next Session (Session 64)
Goal: Begin FEA hollowing - move data arrays out of marketsquare.html into BEA. Target ~150KB FEA shell.
Priority order:
1. WONDERS_BUNDLED - move to BEA-Heritage endpoint (endpoint already exists at /heritage/sites)
2. Demo LISTINGS array - move to BEA-Listings demo mode endpoint (new: /listings?demo=1)
3. SELLERS array - move to BEA-Sellers endpoint (new: /sellers or embedded in listing response)
4. FEA becomes pure render shell - no business logic, no hardcoded data arrays

## Blockers
- CIPC registration pending - Paystack live mode blocked
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
