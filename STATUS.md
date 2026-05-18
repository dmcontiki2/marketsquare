# TrustSquare · STATUS.md

## Live State
BEA v1.2.0 live at trustsquare.co · FastAPI + SQLite (9 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93–97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 (4 cities: Pretoria / New York / London / Sydney)
- World Heritage: 120 sites bundled in app, instant render + 3s background refresh
- All categories show correct live counts (no demo bleed-through)

## Last Completed (Session 62)
- Bundled 120 World Heritage sites as hardcoded array → instant Heritage strip render
- Fixed broken site: nested backtick JS syntax error in detail view seller profile button
- Fixed Local Market tile showing demo listings on live site
- Fixed adventure card photos for NY/London/Sydney (photos[] array vs photo field)
- Fixed live site showing demo listings (renderGrid + renderCatCounts filters)
- Fixed "View seller profile" broken for real BEA listings (undefined sellerIdx guard)
- Fixed Adventures currency/country filter for non-ZA cities

## Next Session (Session 63)
1. Company registration number (2026/340128/07) into EULA + footer
2. support@trustsquare.co mailbox confirmation
3. Privacy Policy page — draft and publish
4. Counsel EULA review brief
5. AI audit of marketsquare.html for pre-launch issues
6. Featured strip: mark real BEA listings as featured so strip is not empty on live site
7. Paystack live mode (pending CIPC registration)

## Blockers
- CIPC registration pending → Paystack live mode blocked
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
