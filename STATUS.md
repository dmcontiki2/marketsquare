# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 50 lines. Update it at the end of every session.*

---

## Current State · 1 April 2026

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

## Last Completed Session · Session 7 (1 April 2026)

- Tasks 1–6 all complete:
  - Task 1 — Currency formatting R1,234,456.00 across both files
  - Task 2 — Structured description editor (admin) + renderer (buyer app)
  - Task 3 — Photo carousel with swipe support (detail screen)
  - Task 4 — Category listing counts city-scoped, excludes placeholders
  - Task 5 — City selector tier-gated (Free / Starter / Premium)
  - Task 6 — Three-level location hierarchy (BEA + admin + buyer app) · deployed

---

## Next Task · Session 8

1. Maroushka real listings — delete experimental data, re-enter via admin tool using structured description editor and suburb field
2. n8n email notifications — buyer emailed on intro accept/decline
3. Hetzner Object Storage — migrate photos from local /media
4. Paystack live mode — pending CIPC registration
5. Add GEONAMES_USERNAME to BEA .env to enable auto-suburb seeding for new cities

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
