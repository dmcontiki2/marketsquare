# TrustSquare - STATUS.md

## Live State
BEA v1.2.1 live at trustsquare.co - FastAPI + SQLite (10 tables) + Redis on Hetzner CPX22
- 5 real Property listings live (IDs 93-97, Pretoria)
- 23 / 60 founding sellers registered
- Demo mode accessible via ?demo=1 OR via in-app DEMO/LIVE toggle (top bar)
- World Heritage: 120 sites served from BEA /wonders (not bundled)
- Demo listings: 293 entries served from BEA /demo-listings (not bundled)
- Demo sellers: 40 entries served from BEA /demo-sellers (not bundled)
- marketsquare.html: 906 KB (was 1,380 KB -- 475 KB removed in Session 66)
- smoke_test.py: 28-check post-deploy safety net in place
- ALL FOUR APPS GATED: JWT login required on trustsquare.co/, admin.html, dashboard.html, /launch/
- Team logins: Maurice, Maroushka, David Jnr - temp PIN 123456 - forced change on first use

## Last Completed (Session 66)
- FEA hollowing pass 1: removed 475 KB of bundled data arrays
- WONDERS_BUNDLED (164 KB) removed -- FEA fetches from BEA GET /wonders
- LISTINGS array (275 KB) removed -- new BEA GET /demo-listings endpoint
- SELLERS array (38 KB) removed -- new BEA GET /demo-sellers endpoint
- DOMContentLoaded init made async -- awaits demo data before first renderGrid()
- devSetMode() made async -- refetches demo data when toggling to demo mode
- smoke_test.py updated for new BEA-served architecture
- All 28 smoke checks passing

## File anatomy (906 KB after Session 66)
- HTML markup:  311 KB (34%) -- render shell, cannot reduce without structural rewrite
- CSS:          103 KB (11%) -- extractable to ms.css via <link>
- JavaScript:   491 KB (54%) -- extractable to ms.js via <script src="">
- No remaining large data arrays -- BEA migration is complete
- Remaining JS config blocks (AA_CATEGORIES, SB_SIGNALS etc) are app logic, not data

## 150 KB target: what it actually requires
The 150 KB target is achievable but requires static asset extraction, not more BEA migration:
1. Extract CSS to /static/ms.css -- saves 103 KB from HTML, browser caches it
2. Extract JS to /static/ms.js -- saves ~491 KB from HTML, browser caches it
3. HTML shell becomes ~311 KB + ~15 KB of minimal inline bootstrap = ~326 KB on first load
4. On repeat visits (cached assets): HTML shell only = ~326 KB total transfer
Note: requires cache-busting strategy (content hash or version query param in asset URLs)
This is a build-pipeline task, not a data migration task.

## Open Actions (carry forward)
- Company registration number (2026/340128/07) - insert into EULA + footer
- support@trustsquare.co mailbox - confirm active
- Privacy Policy page - draft and publish
- Counsel brief for EULA review
- AI audit of marketsquare.html for pre-launch issues
- Featured strip: mark real BEA listings as featured (strip empty on live site)
- Yield System: select SA patent attorney (required before provisional application)
- Yield System: Solar Council review of YIELD_SYSTEM_TECHNICAL_DISCLOSURE v0.2 (Step 0.2)

## Next Session (Session 67)
Goal: Static asset extraction -- reduce marketsquare.html to a thin HTML shell.
Approach: extract CSS and JS to separately-served static files.
Steps:
1. Extract all <style> blocks to /var/www/marketsquare/static/ms.css
2. Extract all <script> blocks to /var/www/marketsquare/static/ms.js
3. Replace in marketsquare.html with <link rel="stylesheet" href="/static/ms.css?v=67">
   and <script src="/static/ms.js?v=67"></script>
4. Configure nginx to serve /static/ with long cache headers
5. Verify all functionality intact -- smoke test must pass
6. Result: HTML file ~315 KB (markup + minimal bootstrap), assets cached by browser
Cache-busting: use ?v=SESSION_NUMBER query param, bump each session that changes assets
Prerequisite: confirm nginx config allows /static/ path and sets Cache-Control headers

## Blockers
- CIPC registration pending - Paystack live mode blocked
- Git commits must be run by David from PowerShell (sandbox index.lock conflict)
- Patent registration pending - apps gated until SA provisional filed
