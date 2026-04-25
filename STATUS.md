# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 60 lines. Update it at the end of every session.*

---

## Current State · 25 April 2026

| Item | Detail |
|---|---|
| **Live URL** | trustsquare.co (buyer app) · trustsquare.co/admin.html (admin) |
| **Buyer app file** | `marketsquare.html` (local) → served as `index.html` |
| **Admin file** | `marketsquare_admin.html` (local) → served as `admin.html` |
| **BEA file** | `bea_main.py` (local) → served as `main.py` on server |
| **Codex** | `Solar_Council_Codex_v4_5.docx` |
| **Cost model** | `Cost_Breakdown_GlobalLaunch.xlsx` — ZAR/USD rate B62, accountant rows added |
| **BEA version** | Live — check GET /health |
| **Founding sellers** | 23 / 60 · check trustsquare.co/admin.html |
| **Paystack** | Test mode (live pending CIPC registration) |
| **Photo storage** | Cloudflare R2 (EU) — `marketsquare-media` bucket, $0 egress |

---

## Last Completed Session · Session 23 (25 April 2026)

- Desktop Featured carousel scroll arrows (pointer:fine devices only) ✅
- Photo lightbox — tap listing photo → full-screen overlay, arrow/keyboard/Escape navigation ✅
- My Requests tab added to seller dashboard (saved + intro-sent listings) ✅
- Back buttons added: Browse, Saved, Tuppence Wallet, City Deployment screens ✅
- Coming soon placeholder cards now always sort to end of grid ✅
- Credentials renderer fixed — handles string and object formats (was showing "undefined") ✅
- Trust Score composition note added to seller CV hero ✅
- Cost model: ZAR/USD rate, accountant R2k/mo, software R500/mo, SA tax 27% added ✅
- Revenue vs Cost rows 21–25 number format fixed (was $, now units) ✅
- TrustSquare WhitePaper v3 — IP hardening, 7 patent claims, dual-entity, 5 timestamp authorities ✅
- 5-Wave launch email campaign — Pretoria agents, KW RSA, global — all templates written ✅
- marketsquare.html deployed to Hetzner ✅

---

## Next Tasks · Session 24

1. Maroushka + Dave test on phone (lightbox, back buttons, My Requests tab)
2. Video links on seller CV — show only after introduction accepted (Codex-required)
3. Featured personalisation — weight carousel toward user's recent category searches
4. Paystack live mode (pending CIPC registration — David action)
5. n8n email notifications — buyer emailed on intro accept/decline
6. Load email list into Mailchimp/Sendgrid and schedule 5-wave campaign for launch day
7. File WhitePaper v3 at CIPRO (provisional patent) + IP.com + archive.org on Day 0
8. **Remove `/dev/credit` endpoint + Dev Tools nav tab before public launch**

---

## Known Server Facts

- SSH key: `~/.ssh/id_ed25519` · Server: 178.104.73.239 · Ubuntu 24.04
- Env vars: /etc/environment · BEA venv: /var/www/marketsquare/venv/
- Photo storage: Cloudflare R2 (EU) via HETZNER_S3_* env vars
- DB backups: daily 3 AM cron → R2 `backups/YYYY-MM-DD/`, 14-day retention
- n8n: Docker container — restart: `docker restart n8n` · UI: SSH tunnel port 5678
- CityLauncher: /var/www/citylauncher/ · port 8001 · nginx at /launch/ + /launch-api/

## Known File Facts

- Local filenames: `marketsquare.html`, `marketsquare_admin.html`, `bea_main.py` (no version suffix)
- Placeholder listing ids: `ph_*` · BEA listing ids: `bea_*` · Always use `findListing(id)`
- BEA geo API param: `country` (not `country_iso2`)
- Cost model edited via openpyxl (pandas not installed in sandbox)

## Open Items

- ⚠️ Remove `/dev/credit` BEA endpoint + Dev Tools nav tab before public launch
- Paystack live mode (pending CIPC registration)
- n8n email notifications for intro accept/decline
- SA corporate tax rows B30:D30 in cost model — fill once P&L is finalised

---
*Keep this file under 60 lines. Update Last Completed + Next Tasks every session.*
