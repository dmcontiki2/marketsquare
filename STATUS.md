# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 50 lines. Update it at the end of every session.*

---

## Current State · 10 April 2026

| Item | Detail |
|---|---|
| **Live URL** | trustsquare.co (buyer app) · trustsquare.co/admin.html (admin) |
| **Buyer app file** | `marketsquare.html` (local) → served as `index.html` |
| **Admin file** | `marketsquare_admin.html` (local) → served as `admin.html` |
| **BEA file** | `bea_main.py` (local) → served as `main.py` on server |
| **Codex** | `Solar_Council_Codex_v4_3.docx` |
| **BEA version** | Live — check GET /health (returns current version) |
| **Founding sellers** | Live — check trustsquare.co/admin.html or GET /listings?city=Pretoria |
| **Paystack** | Test mode (live pending CIPC registration) |
| **Photo storage** | Cloudflare R2 (EU) — `marketsquare-media` bucket, $0 egress |

---

## Last Completed Session · Session 11 (5 April 2026)

- Proximity search: lat/lng on geo_cities/geo_suburbs, _backfill_geo_coords() from GeoNames ZA dump ✅
- GET /geo/nearby endpoint — bounding-box + Haversine, returns suburbs within radius ✅
- GET /listings JOINs geo_suburbs for suburb_lat/suburb_lng per listing ✅
- Buyer app: Leaflet.js map view + MarkerCluster, grid/map toggle, OSM tiles ✅
- Browser geolocation → distance badges on cards, distance-sorted results ✅
- "📍 Near me" suburb filter — 10km radius, client-side multi-suburb filtering ✅
- Admin: replaced Add City form with search filter, removed POST /geo/cities endpoint ✅
- Cleaned up duplicate lowercase "pretoria" (id 101) on server ✅

---

## Next Task · Session 12

1. Fix magic onboarding link (reported not working for Maroushka and Dave)
2. Paystack live mode — pending CIPC registration
3. n8n email notifications — buyer emailed on intro accept/decline
4. (Done in CityLauncher Session 9) Photo storage → Cloudflare R2, admin app fixes

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
- `Cost_Breakdown_GlobalLaunch.xlsx` is the live cost model — edit in Claude Chat only, not Claude Code

---

## Open Items

- Paystack live mode (pending CIPC registration)
- Rename project files — remove Windows duplicate suffixes

---
*Update the "Last Completed" and "Next Task" sections at the end of every session. Do not let this file exceed 60 lines.*
