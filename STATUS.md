# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 60 lines. Update it at the end of every session.*

---

## Current State · 26 April 2026

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

## Last Completed Session · Session 24 (26 April 2026)

- Wishlist Feed — full requirements document written: `WISHLIST_REQUIREMENTS.md` v0.2 ✅
- Trust Score filter as first-class safety gate (≥90 = Highly Trusted) locked in ✅
- Free (national) / Global ($5/month) subscription tiers defined ✅
- Tuppence boost at 2T with expanded reach and match tolerance specified ✅
- Empty-state showcase (gold coins, Rolex, rare cards) — wow factor confirmed ✅
- Haiko 4.5 as matching agent socket, keyword fallback specified ✅
- Apple Watch (APNs) in scope for V1 ✅
- Privacy architecture formalised: "Your wishlist never leaves MarketSquare" ✅
- CHANGELOG.md updated for both MarketSquare and CityLauncher ✅

---

## Next Tasks · Session 25

1. **Wishlist Feed build** — hand `WISHLIST_REQUIREMENTS.md` to Opus · implement BEA tables, matching job, scroll feed UI, wearable push
2. Update cost model — add Global subscription ($5/mo) + boost (2T) revenue projections to Cost_Breakdown_GlobalLaunch.xlsx
3. Maroushka + Dave test on phone (lightbox, back buttons, My Requests tab) — from Session 23
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
