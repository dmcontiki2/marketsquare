# MarketSquare · STATUS
*Read this FIRST, before AGENT_BRIEFING.md or CLAUDE.md. Keep this file under 80 lines. Update it at the end of every session.*

---

## Current State · 1 May 2026

| Item | Detail |
|---|---|
| **Live URL** | trustsquare.co (buyer app) · trustsquare.co/admin.html (admin) |
| **Buyer app file** | `marketsquare.html` (local) → served as `index.html` |
| **Admin file** | `marketsquare_admin.html` (local) → served as `admin.html` |
| **BEA file** | `bea_main.py` (local) → served as `main.py` on server |
| **Codex** | `Solar_Council_Codex_v4_5.docx` |
| **Cost model** | `Cost_Breakdown_GlobalLaunch.xlsx` — ZAR/USD rate B62 |
| **BEA version** | v1.3.0 live — KYC endpoints active |
| **Founding sellers** | 23 / 60 · check trustsquare.co/admin.html |
| **Paystack** | Test mode — **awaiting Paystack live mode review** (submitted 30 Apr 2026) |
| **CIPC** | TRUSTSQUARE (PTY) LTD · 2026/340128/07 · registered 29/04/2026 |
| **FNB account** | Gold Business · 63208160117 · Branch 250655 · activated |
| **Photo storage** | Cloudflare R2 (EU) — `marketsquare-media` bucket, $0 egress |

---

## Last Completed Session · Session 34 (1 May 2026) — Part 2: KYC

- BEA: SA ID Luhn validator + Sonnet vision identity verification (POST /users/{email}/verify-identity) ✅
- BEA: Banking details storage + fuzzy name-match against verified ID (POST /users/{email}/banking) ✅
- BEA: Certificate name-match via Sonnet background task (_run_cert_name_check) ✅
- Admin: ID verification UI panel in Document Hub — inline after id_doc upload ✅
- DB: user_credentials.updated_at column + 10 KYC columns on users table ✅
- Trust signal hierarchy live: id_uploaded(+3) → id_number_valid(+4) → id_ai_verified(+8) → id_admin_confirmed(+10) ✅
- All endpoints smoke-tested on live server ✅
- HEAD: commit pending

---

## Previous Session · Session 34 Part 1 (1 May 2026)

- LM multi-photo upload (up to 5), Document Hub (9 doc types, visibility toggle), seller_documents DB table ✅
- 12 LM Trust Score signals (was 2) · buyer seller profile shows post_intro docs ✅


---

## Next Tasks · Session 35

1. **Paystack live mode** — when approval email arrives: paste `sk_live_...` + webhook secret into `/var/www/marketsquare/.env`, restart, test with real card
2. **n8n email notifications** — buyer emailed on intro accept/decline
3. **Maroushka + Dave phone test** — lightbox, back buttons, My Requests tab
4. **LM edit flow** — add multi-photo management and Document Hub to edit-after-publish screen
5. **KYC cost analysis** — estimate Sonnet vision tokens per verification vs PaddleOCR on-server option
6. **CIPC Beneficial Ownership** — file at cipc.co.za by ~13 May 2026 (David action)

---

## ⚠️ Legal Actions — David (Time-Critical)

| Action | Deadline | Status |
|---|---|---|
| **File Beneficial Ownership with CIPC** | ~13 May 2026 | ⚠️ Outstanding — cipc.co.za |
| **Paystack live mode approval** | Awaiting review | Submitted 30 Apr 2026 |
| **TRUSTSQUARE name challenge window** | Closes 29 July 2026 | Monitor CIPC correspondence |
| **First Annual Return to CIPC** | ~Feb/Mar 2027 | Financial year end: February |

---

## Known Server Facts

- SSH: `load_sandbox_ssh.sh` at session start · Server: 178.104.73.239 · Ubuntu 24.04
- Env vars: `/var/www/marketsquare/.env` · BEA venv: `/var/www/marketsquare/venv/`
- Photo storage: Cloudflare R2 (EU) via HETZNER_S3_* env vars
- DB backups: daily 3 AM cron → R2 `backups/YYYY-MM-DD/`, 14-day retention
- n8n: Docker container — restart: `docker restart n8n` · UI: SSH tunnel port 5678

## Known File Facts

- Local filenames: `marketsquare.html`, `marketsquare_admin.html`, `bea_main.py` (no version suffix)
- Placeholder listing ids: `ph_*` · BEA listing ids: `bea_*` · Always use `findListing(id)`
- BEA geo API param: `country` (not `country_iso2`)
- Cost model edited via openpyxl in sandbox
- Git commits: always from PowerShell — never from sandbox (cross-OS lock conflict)
