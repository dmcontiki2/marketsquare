# TrustSquare - STATUS.md

## Live State
BEA v1.2.1 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- World Heritage: 120 sites bundled in app, instant render + 3s background refresh
- All categories show correct live counts (no demo bleed-through)
- smoke_test.py: 28-check post-deploy safety net in place
- Admin gate: BEA-backed JWT password protection on admin.html and dashboard.html
- Team login: Maroushka and Maurice seeded with numeric PINs

## Last Completed (Session 65)
- Added BEA-backed JWT login gate to admin.html and dashboard.html
- Master password (alphanumeric) for David via MS_ADMIN_PASSWORD env var
- Team PIN system: numeric PINs (4-8 digits) stored bcrypt-hashed in admin_users table
- /admin/login checks master first, then team PIN fallback
- /admin/users POST/GET/DELETE for team management - API-key protected
- Token sub field: master or team:{name} for audit trail
- Maroushka (PIN 123456) and Maurice (PIN 654321) seeded as initial team members
- All 28 smoke test checks passing

## Open Actions (carry forward)
- Company registration number (2026/340128/07) - insert into EULA + footer
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Change Maroushka and Maurice PINs from seeded values to their own chosen PINs

## Next Session (Session 66)
Goal: Begin FEA hollowing - move data arrays out of marketsquare.html into BEA. Target ~150KB FEA shell.
Priority order:
1. WONDERS_BUNDLED - move to BEA-Heritage endpoint (endpoint already exists at /heritage/sites)
2. Demo LISTINGS array - move to BEA-Listings demo mode endpoint (new: /listings?demo=1)
3. SELLERS array - move to BEA-Sellers endpoint (new: /sellers or embedded in listing response)
4. FEA becomes pure render shell - no business logic, no hardcoded data arrays

## Blockers
- CIPC registration pending - Paystack live mode blocked
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
