# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 50 lines. Update it at the end of every session.*

---

## Current State · 2 April 2026

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

## Last Completed Session · Session 8 (2 April 2026)

- Task 1 — Maroushka real listings re-entered (done prior to this session)
- Task 2 — n8n email notifications: webhook fire-and-forget on intro accept/decline (BEA)
- Task 3 — Hetzner Object Storage: S3 upload path + /admin/migrate-photos endpoint (BEA)
- Task 5 — GeoNames config guard: warning log added when GEONAMES_USERNAME not set (BEA)

---

## Next Task · Session 9

1. Deploy Session 8 BEA changes to server (scp + pip install + restart — see CHANGELOG)
2. Set up n8n as systemd service; create accept/decline workflows; add webhook URLs to .env
3. Create Hetzner Object Storage bucket; add S3 env vars to .env; run migrate-photos
4. Paystack live mode — pending CIPC registration
5. Update start_marketsquare.bat with correct SCP deploy commands

---

## Known File Name Facts (prevent drift)

- Local filenames have **no version suffix**: `marketsquare.html`, `marketsquare_admin.html`
- `AGENT_BRIEFING.md` references old names (`v8_6b`, `v1_1`) — ignore those, use the names above
- Placeholder listing ids start with `ph_` · BEA listing ids start with `bea_`
- Always use `findListing(id)` — never `LISTINGS[id]`

---

## Open Items (non-session-7)

- n8n email notifications (buyer emailed on intro accept/decline)
- Hetzner Object Storage (migrate photos from local /media)
- Paystack live mode (pending CIPC registration)
- Rename project files — remove Windows duplicate suffixes
- Update `start_marketsquare.bat` with correct SCP deploy commands

---
*Update the "Last Completed" and "Next Task" sections at the end of every session. Do not let this file exceed 60 lines.*
