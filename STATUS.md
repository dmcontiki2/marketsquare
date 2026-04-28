# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 60 lines. Update it at the end of every session.*

---

## Current State · 28 April 2026

| Item | Detail |
|---|---|
| **Live URL** | trustsquare.co (buyer app) · trustsquare.co/admin.html (admin) |
| **Buyer app file** | `marketsquare.html` (local) → served as `index.html` |
| **Admin file** | `marketsquare_admin.html` (local) → served as `admin.html` |
| **BEA file** | `bea_main.py` (local) → served as `main.py` on server |
| **Codex** | `Solar_Council_Codex_v4_5.docx` |
| **Cost model** | `Cost_Breakdown_GlobalLaunch.xlsx` — ZAR/USD rate B62, accountant rows added |
| **BEA version** | v1.3.0 live — check GET /health |
| **Founding sellers** | 23 / 60 · check trustsquare.co/admin.html |
| **Paystack** | Test mode (live pending CIPC registration) |
| **Photo storage** | Cloudflare R2 (EU) — `marketsquare-media` bucket, $0 egress |

---

## Last Completed Session · Session 29 (28 April 2026)

- Fixed invisible Confirm button in LM admin modal (`--navy` CSS var added) ✅
- SSH deploy from sandbox fixed permanently (project `.ssh/` folder) ✅
- Superuser access added for David, Maroushka, Dave, Maurice (client + BEA) ✅
- `.gitattributes` eol=lf enforced — CRLF truncation bug fixed permanently ✅
- Local Market tile added to sell wizard Step 2 ✅
- `sellSheetContinue()` fixed — routes to wizard not dashboard ✅
- Photo auto-compress >2MB silently (canvas 1200px/80% JPEG) ✅
- `API_KEY` added to marketsquare.html (fixed LM publish connection error) ✅
- Double photo field in LM modal fixed (Step A photo passed through) ✅
- Local Market full-width tile added to home Categories grid ✅
- HEAD: 4e7c97f

---

## Next Tasks · Session 30

1. **Showcase photos** — add thumb_url to listings 40–51 (royalty-free images)
2. Maroushka + Dave phone test (lightbox, back buttons, My Requests tab)
3. Paystack live mode (pending CIPC registration — David action)
4. n8n email notifications — buyer emailed on intro accept/decline
5. **Remove `/dev/credit` endpoint + Dev Tools nav tab before public launch**

---

## Known Server Facts

- SSH key: `.ssh/id_ed25519` in project folder · Server: 178.104.73.239 · Ubuntu 24.04
- Env vars: /etc/environment · BEA venv: /var/www/marketsquare/venv/
- Photo storage: Cloudflare R2 (EU) via HETZNER_S3_* env vars
- DB backups: daily 3 AM cron → R2 `backups/YYYY-MM-DD/`, 14-day retention
- n8n: Docker container — restart: `docker restart n8n` · UI: SSH tunnel port 5678

## Known File Facts

- Local filenames: `marketsquare.html`, `marketsquare_admin.html`, `bea_main.py` (no version suffix)
- Placeholder listing ids: `ph_*` · BEA listing ids: `bea_*` · Always use `findListing(id)`
- BEA geo API param: `country` (not `country_iso2`)
- Cost model edited via openpyxl (pandas not installed in sandbox)
- ⚠️ Never use Edit tool on marketsquare.html — always use Python scripts (file is 9000+ lines)

## Open Items

- ⚠️ Remove `/dev/credit` BEA endpoint + Dev Tools nav tab before public launch
- Paystack live mode (pending CIPC registration)
- n8n email notifications for intro accept/decline
- SA corporate tax rows B30:D30 in cost model — fill once P&L is finalised

---
*Keep this file under 60 lines. Update Last Completed + Next Tasks every session.*
