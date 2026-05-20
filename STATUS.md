# TrustSquare - STATUS.md

## Live State
BEA v1.2.1 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- marketsquare.html: 325 KB HTML shell (reduced from 1,380 KB over sessions 65-67)
- Static assets: /static/ms.css (103 KB) + /static/ms.js (494 KB), cached 1 year
- World Heritage: 120 sites from BEA /wonders
- Demo data: 293 listings + 40 sellers from BEA /demo-listings and /demo-sellers
- smoke_test.py: 30-check post-deploy safety net
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use

## Last Completed (Session 67)
- Extracted CSS (103 KB) to /static/ms.css -- linked via <link rel="stylesheet">
- Extracted JS (483 KB) to /static/ms.js -- linked via <script src defer>
- nginx /static/ location: Cache-Control immutable, 1-year expiry, bypasses FastAPI
- HTML shell reduced from 905 KB to 325 KB
- Cache-busting via ?v=67 query param (bump version each session that changes assets)
- smoke_test.py updated to 30 checks -- verifies static assets reachable + cache headers
- All 30 checks passing

## File anatomy (325 KB HTML shell after Session 67)
- HTML markup + ms-data + gate script: 325 KB  (sent every page load)
- /static/ms.css?v=67:               103 KB  (cached 1 year after first load)
- /static/ms.js?v=67:                494 KB  (cached 1 year after first load)
- On first visit: ~922 KB total transfer
- On repeat visits: 325 KB only (assets served from cache)

## Cache-busting rule (AI-enforced)
When ms.css or ms.js change, bump the ?v= version in marketsquare.html to match
the current session number. This forces browsers and Cloudflare to fetch the new file.
Current version: ?v=67

## Open Actions (carry forward)
- Company registration number (2026/340128/07) - insert into EULA + footer
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)

## Next Session (Session 68)
Goal: Pre-launch audit and featured listings fix.
Priority order:
1. Featured strip: at least one real BEA listing marked featured=true so strip is not empty
2. AI audit of marketsquare.html for pre-launch issues (EULA, company reg, privacy policy refs)
3. Insert company registration number (2026/340128/07) into EULA and footer
4. Cache-busting: if assets changed, bump ?v=68 in marketsquare.html

## Blockers
- CIPC registration pending - Paystack live mode blocked
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
