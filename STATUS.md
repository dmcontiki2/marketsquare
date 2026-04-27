# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 60 lines. Update it at the end of every session.*

---

## Current State · 27 April 2026

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

## Last Completed Session · Session 26 (27 April 2026)

- `LOCAL_MARKET_REQUIREMENTS.md` v0.1 — full spec, Tuppence model, bad actor rules, EULA clauses ✅
- `TRUST_SCORE_HUB_REQUIREMENTS.md` v0.1 — full UI spec with exact point values per category ✅
- Showcase seed script deployed — 12 aspirational listings live (IDs 40–51) ✅
- CHANGELOG.md updated ✅

---

## Next Tasks · Session 27

1. **Local Market build** — hand `LOCAL_MARKET_REQUIREMENTS.md` to Opus
2. **Trust Score Hub build** — hand `TRUST_SCORE_HUB_REQUIREMENTS.md` to Opus
3. **Showcase photos** — add `thumb_url` to listings 40–51 (royalty-free images)
4. **Geo/city selector bug** — audit all `activeCity` references in `marketsquare.html`
5. Maroushka + Dave phone test (lightbox, back buttons, My Requests tab)
6. Paystack live mode (pending CIPC registration — David action)
7. **Remove `/dev/credit` endpoint + Dev Tools nav tab before public launch**

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
