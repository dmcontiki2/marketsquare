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

## Last Completed Session · Session 38 (3 May 2026) — Two-Path Sell Flow

- **Path A (new seller, 3 taps)**: `screen-publish` replaced with 3-step flow: photo → category/headline/price + inline AI market note → identity + EULA → live. `openSellNav()` routes no-email to Path A ✅
- **Path B (returning seller, B1–B8)**: new `screen-sell-b` with full AI-guided flow. B1 account confirm → B2 category + agent/private gate → B3 structured fields + inline AI note → B4 AI description draft → B5 dynamic photo gallery → B6 skippable selfie → B7 Trust Score checklist with signal tables → B8 publish ✅
- **Routing wired**: `sellSheetContinue()` → `goTo('sell-b')`, `goTo()` calls `sbReset()` for sell-b, demo mode blocks sell-b ✅
- **File integrity**: rebuilt after truncation — 11,095 lines, ends with `</html>` ✅
- Not yet deployed — git commit + deploy pending

---

## Next Tasks · Session 39

1. **Git commit + deploy** — commit Session 38 changes, `scp marketsquare.html` to server, restart BEA
2. **Test Path A end-to-end** — new seller: photo → category/price → submit → confirm listing goes live + 3 AI sessions credited
3. **Test Path B end-to-end** — returning seller: account sheet → B1–B8 → publish
4. **Paystack live mode** — when approval email arrives: paste `sk_live_...` + webhook secret into `/var/www/marketsquare/.env`
5. **n8n email notifications** — buyer emailed on intro accept/decline
5. **CIPC Beneficial Ownership** — file at cipc.co.za by ~13 May 2026 (David action)

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
