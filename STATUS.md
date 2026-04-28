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

## Last Completed Session · Session 28 (27 April 2026)

- Local Market end-to-end live: BEA v1.3.0, buyer page, admin form, intro flow ✅
- Trust Score Hub live: credential checklist, Haiko tip card, per-category awareness ✅
- Geo/city selector bug fixed — all views now consume activeCity dynamically ✅
- Wishlist category dropdown removed — free-text only ✅
- Hotfix: Trust Score is buyer-filter not server gate (spec corrected to v0.2) ✅
- Hotfix: R2 public URL, lm_get_listing 500, LM trust filter live-join ✅
- All commits pushed to GitHub by Opus (a93f69c is HEAD) ✅
- ⚠️ One invisible button in Local Market admin modal — CSS fix pending next session

---

## Next Tasks · Session 29

1. **Fix invisible Confirm button** in Local Market admin modal — CSS only, ~5 min
2. **Showcase photos** — add thumb_url to listings 40–51 (royalty-free images)
3. Maroushka + Dave phone test (lightbox, back buttons, My Requests tab)
4. Paystack live mode (pending CIPC registration — David action)
5. n8n email notifications — buyer emailed on intro accept/decline
6. **Remove `/dev/credit` endpoint + Dev Tools nav tab before public launch**

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
