# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 50 lines. Update it at the end of every session.*

---

## Current State · 17 April 2026

| Item | Detail |
|---|---|
| **Live URL** | trustsquare.co (buyer app) · trustsquare.co/admin.html (admin) |
| **Buyer app file** | `marketsquare.html` (local) → served as `index.html` |
| **Admin file** | `marketsquare_admin.html` (local) → served as `admin.html` |
| **BEA file** | `bea_main.py` (local) → served as `main.py` on server |
| **Codex** | `Solar_Council_Codex_v4_5.docx` |
| **BEA version** | Live — check GET /health (returns current version) |
| **Founding sellers** | Live — check trustsquare.co/admin.html or GET /listings?city=Pretoria |
| **Paystack** | Test mode (live pending CIPC registration) |
| **Photo storage** | Cloudflare R2 (EU) — `marketsquare-media` bucket, $0 egress |

---

## Last Completed Session · Session 17 (15 April 2026)

- Call-out fee field added to Services Technical + Casuals (optional, /visit, flat fee, POA) ✅
- Rate input display fixed — text input, live R preview, overflow:visible CSS ✅
- AI Coach email auto-register — unknown emails now auto-created in users table ✅
- Dave's email added to users table + seller_email column on listings ✅
- Tuppence deduction server-persisted on intro accept (intro_deduct transaction) ✅
- N8N_WEBHOOK_NEW_INTRO endpoint wired in BEA (env var still to be set) ✅
- Tiered AI packs live: 5T=40 uses · 10T=100 uses · 25T=320 uses ✅
- Wallet UI unified — 3-row format on all 6 purchase buttons ✅
- Dual balance widget (Tuppence + AI uses) in wallet screen ✅
- localPrice() helper added — ZAR equivalent shown on all prices ✅
- Cost model updated — tiered pack rows + blended sessions/T formula (B74) ✅
- All project files consolidated and deployed to Hetzner ✅

---

## Last Completed Session · Session 20 (17 April 2026)

- Edit-after-publish flow added to seller app (`marketsquare.html`) — full manual edit screen with per-category field sets ✅
- Edit modal added to admin app (`marketsquare_admin.html`) — Edit + Version History buttons on every listing ✅
- BEA: `listing_versions` table added — full JSON snapshot archived before every PUT ✅
- BEA: `PUT /listings/{id}?email=` endpoint — email-auth, NULL seller_email stamped on first edit ✅
- BEA: `GET /listings/mine`, `GET /listings/{id}`, version history endpoints added ✅
- AI Coach integrated into both edit screens (pay-per-use, optional) ✅
- Profile photo persistence fixed — photo uploaded to R2 via `POST /users/{email}/photo`, restored from BEA on login ✅
- Dev tools added to admin app — free Tuppence + AI session seeding for dev testing, **remove before launch** ✅
- `GET /tuppence/balance` endpoint + buyer app balance sync on load ✅
- CHANGELOG.md, AGENT_BRIEFING.md, STATUS.md updated ✅

## Next Task · Session 21

1. Deploy all three updated files to Hetzner (`deploy_marketsquare.bat`)
2. Maroushka + Dave test edit-after-publish on their live listings
3. Paystack live mode (pending CIPC registration — David action)
4. n8n email notifications — buyer emailed on intro accept/decline
5. CityLauncher Cowork setup
6. **Remove `/dev/credit` endpoint + Dev Tools nav tab before public launch**

---

## Known Server Facts (prevent drift)

- SSH key: `~/.ssh/id_ed25519` (ed25519, added 6 April 2026)
- Env vars live in /etc/environment (not /var/www/marketsquare/.env)
- Photo storage: Cloudflare R2 (EU) via HETZNER_S3_* env vars — endpoint uses `.eu.` for EU jurisdiction
- DB backups: daily 3 AM cron → R2 `backups/YYYY-MM-DD/`, 14-day retention, script at `/usr/local/bin/backup_dbs_to_r2.py`
- systemd drop-in: /etc/systemd/system/marketsquare.service.d/env.conf → points to /etc/environment
- BEA venv: /var/www/marketsquare/venv/ — always use venv pip
- n8n runs as Docker container — restart with: docker restart n8n
- Access n8n UI via SSH tunnel: ssh -L 5678:localhost:5678 root@178.104.73.239
- GEONAMES_USERNAME=dmcontiki2 in /etc/environment
- CityLauncher: /var/www/citylauncher/ · port 8001 · citylauncher.service · nginx at /launch/ and /launch-api/

---

## Known File Name Facts (prevent drift)

- Local filenames have **no version suffix**: `marketsquare.html`, `marketsquare_admin.html`, `bea_main.py`
- `AGENT_BRIEFING.md` references old names (`v8_6b`, `v1_1`) — ignore those, use the names above
- Placeholder listing ids start with `ph_` · BEA listing ids start with `bea_`
- Always use `findListing(id)` — never `LISTINGS[id]`
- BEA geo API query param is `country` (not `country_iso2`)
- `Cost_Breakdown_GlobalLaunch.xlsx` is the live cost model — Claude Code edits via openpyxl (pandas not installed)

---

## Open Items

- Paystack live mode (pending CIPC registration)
- Rename project files — remove Windows duplicate suffixes
- ⚠️ Remove `/dev/credit` BEA endpoint before public launch
- ⚠️ Remove Dev Tools nav tab from `marketsquare_admin.html` before public launch
- n8n email notifications for intro accept/decline

---
*Update the "Last Completed" and "Next Task" sections at the end of every session. Do not let this file exceed 60 lines.*
