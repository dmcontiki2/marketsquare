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

## Last Completed Session · Session 38 (3 May 2026) — Two-Path Sell Flow + Post-Publish Bug Fixes

- **Path A (new seller, 3 taps)**: `screen-publish` replaced with 3-step flow: photo → category/headline/price + inline AI market note → identity + EULA → live. `openSellNav()` routes no-email to Path A ✅
- **Path B (returning seller, B1–B8)**: new `screen-sell-b` with full AI-guided flow. B1 account confirm → B2 category + agent/private gate → B3 structured fields + inline AI note → B4 AI description draft → B5 dynamic photo gallery → B6 skippable selfie → B7 Trust Score checklist with signal tables → B8 publish ✅
- **Routing wired**: `sellSheetContinue()` → `goTo('sell-b')`, `goTo()` calls `sbReset()` for sell-b, demo mode blocks sell-b ✅
- **Post-publish fixes deployed**: X-Api-Key added to `sbDoPublish()` fetch; trust_score + structured fields (beds/baths/garages/floor_area/erf_size/prop_type/listing_type) sent as top-level POST fields; all photos uploaded (not just first); selfie upload X-Api-Key fixed; seller CV credentials section parses signals from structured_fields ✅
- **File**: 11,299 lines, ends with `</html>` ✅

---

## Next Tasks · Session 39

1. **⚠️ Retest Path B end-to-end** — publish a fresh Property listing with full fields (beds/baths/floor_area/erf_size/prop_type) — confirm trust score, all photos, all chips, and credentials show correctly on the live listing and seller CV
2. **Fix home page Local Market scroll** — horizontal advert scroller on home page has stopped scrolling; investigate and restore
3. **Fix "For You" adverts** — cards lack visuals and do not match the style of real listing cards; align layout and imagery
4. **Test Path A end-to-end** — new seller: photo → category/price → submit → confirm listing goes live
5. **Test draft save/resume** — save at B7, exit to dashboard, re-enter sell flow, confirm resume banner + state restored
6. **Paystack live mode** — when approval email arrives: paste `sk_live_...` + webhook secret into `/var/www/marketsquare/.env`
7. **n8n email notifications** — buyer emailed on intro accept/decline

## Session 38 — Additional Hotfixes (deployed 3 May 2026, Part 2)

- **0-listings root cause identified** — BEA had restarted 19,594 times in 7 days due to the `opt_out` duplicate crash (fixed in Part 1). Since BEA fix: 1 restart only. Startup blank screen was the BEA crash loop, not a client timing issue ✅
- **Inline `<script>` tag in template literal** — credentials section fix introduced a `<script>` tag inside a JS template literal string; browser closed outer script block early, breaking entire app JS → 0 listings. Fixed by rewriting as pure IIFE expression inside template literal ✅
- **loadLiveListings retry** — upgraded from single 4s retry to 3× exponential backoff (3s→6s→12s) with "Tap to refresh" fallback. Safety net for genuine network blips only — BEA crash loop was the real cause ✅

## Session 38 Hotfixes (deployed 3 May 2026)

- **BEA crash fixed** — `opt_out` function body was duplicated 3× in `bea_main.py` (tail-repair artifact); removed 102 duplicate lines; syntax clean; server restarted ✅
- **BEA_BASE → BEA_URL** — sell flow publish + AI coach calls were using undefined `BEA_BASE`; all 6 occurrences replaced ✅  
- **Stale B8 error cleared** — error banner and publish button now reset every time B8 is entered ✅
- **load_sandbox_ssh.sh** — was hardcoded to old session name `quirky-brave-galileo`; fixed to use `$(dirname "${BASH_SOURCE[0]}")` — now works every session ✅
- **Edit tool → Python for large files** — all future edits to `marketsquare.html` and `bea_main.py` will use Python open/read/replace/write to prevent truncation-induced duplicates ✅

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
