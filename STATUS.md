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

- Task 2 — n8n email notifications: fully deployed and live ✅
  - n8n running as Docker container on server (localhost:5678 only)
  - Two workflows created: Intro Accepted + Intro Declined (Brevo SMTP)
  - N8N_WEBHOOK_ACCEPT and N8N_WEBHOOK_DECLINE set in /etc/environment
- Task 3 — Hetzner Object Storage: BEA code deployed, bucket created ✅
  - Bucket: marketsquare-media (nbg1.your-objectstorage.com)
  - HETZNER_S3_ENDPOINT and HETZNER_S3_BUCKET set in /etc/environment
  - HETZNER_S3_ACCESS_KEY and HETZNER_S3_SECRET_KEY still need to be added ⚠️
- Task 5 — GeoNames config guard: deployed ✅

---

## Next Task · Session 9

1. Finish Object Storage setup — add HETZNER_S3_ACCESS_KEY and HETZNER_S3_SECRET_KEY to /etc/environment via nano, restart BEA, confirm INFO log appears
2. Run POST /admin/migrate-photos to migrate existing local photos to S3
3. Paystack live mode — pending CIPC registration
4. Update start_marketsquare.bat with correct SCP deploy commands

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

## Open Items (non-session-7)

- n8n email notifications (buyer emailed on intro accept/decline)
- Hetzner Object Storage (migrate photos from local /media)
- Paystack live mode (pending CIPC registration)
- Rename project files — remove Windows duplicate suffixes
- Update `start_marketsquare.bat` with correct SCP deploy commands

---
*Update the "Last Completed" and "Next Task" sections at the end of every session. Do not let this file exceed 60 lines.*
