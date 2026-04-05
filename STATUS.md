# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 50 lines. Update it at the end of every session.*

---

## Current State · 3 April 2026

| Item | Detail |
|---|---|
| **Live URL** | trustsquare.co (buyer app) · trustsquare.co/admin.html (admin) |
| **Buyer app file** | `marketsquare.html` (local) → served as `index.html` |
| **Admin file** | `marketsquare_admin.html` (local) → served as `admin.html` |
| **Codex** | `Solar_Council_Codex_v4_3.docx` |
| **BEA version** | v1.1.0 · live at trustsquare.co |
| **Founding sellers** | 23 / 60 · Pretoria only |
| **Paystack** | Test mode (live pending CIPC registration) |

---

## Last Completed Session · Session 10 (5 April 2026)

- buyer_name fix — column added to intro_requests, stored in POST /intros, wired through n8n webhook payloads ✅
- buyer_name field added to intro request form in buyer app ✅
- 4-level geo hierarchy — geo_countries/regions/cities/suburbs tables, ZA seeded from GeoNames dump: 9 provinces, 54 cities, 11,679 suburbs ✅
- /geo/* endpoints live, old /suburbs and /cities preserved as shims ✅
- GEONAMES_USERNAME=dmcontiki2 in /etc/environment ✅

---

## Next Task · Session 11

1. Prompt B — frontend geo hierarchy (admin tool + buyer app suburb selectors)
2. Paystack live mode — pending CIPC registration

---

## Known Server Facts (prevent drift)

- Env vars live in /etc/environment (not /var/www/marketsquare/.env)
- systemd drop-in: /etc/systemd/system/marketsquare.service.d/env.conf → points to /etc/environment
- BEA venv: /var/www/marketsquare/venv/ — always use venv pip
- n8n runs as Docker container — restart with: docker restart n8n
- Access n8n UI via SSH tunnel: ssh -L 5678:localhost:5678 root@178.104.73.239

---

## Known File Name Facts (prevent drift)

- Local filenames have **no version suffix**: `marketsquare.html`, `marketsquare_admin.html`
- `AGENT_BRIEFING.md` references old names (`v8_6b`, `v1_1`) — ignore those, use the names above
- Placeholder listing ids start with `ph_` · BEA listing ids start with `bea_`
- Always use `findListing(id)` — never `LISTINGS[id]`

---

## Open Items

- Paystack live mode (pending CIPC registration)
- Rename project files — remove Windows duplicate suffixes

---
*Update the "Last Completed" and "Next Task" sections at the end of every session. Do not let this file exceed 60 lines.*
