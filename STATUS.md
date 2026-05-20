# TrustSquare - STATUS.md

## Live State
BEA v1.2.1 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- World Heritage: 120 sites bundled in app, instant render + 3s background refresh
- All categories show correct live counts (no demo bleed-through)
- smoke_test.py: 28-check post-deploy safety net in place
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use
- Gate inputmode fix: main login field accepts alphanumeric on all 4 apps

## Last Completed (Session 65)
- BEA-backed JWT login gate on all four apps (marketplace, admin, dashboard, CityLauncher)
- Master alphanumeric password for David (MS_ADMIN_PASSWORD env var)
- Team numeric PIN system with bcrypt storage in admin_users table
- Forced PIN change on first login - temp PIN 123456 blocks access until personal PIN set
- Fixed inputmode=numeric on main login field in admin.html + dashboard.html
- All 28 smoke test checks passing

## Open Actions (carry forward)
- Company registration number (2026/340128/07) - insert into EULA + footer
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)

## Next Session (Session 66)
Goal: FEA hollowing - move hardcoded data arrays out of marketsquare.html into BEA.
Target: reduce marketsquare.html from ~1.4MB to ~150KB render shell.
Priority order:
1. WONDERS_BUNDLED - move to BEA /heritage/sites endpoint (already exists)
2. Demo LISTINGS array - move to BEA /listings?demo=1 endpoint (new)
3. SELLERS array - move to BEA /sellers endpoint (new)
4. FEA becomes pure render shell - no hardcoded data, all fetched from BEA

## Blockers
- CIPC registration pending - Paystack live mode blocked
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
