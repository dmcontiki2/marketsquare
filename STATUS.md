# TrustSquare — STATUS.md
**Updated: Session 44 · 6 May 2026**

---

## Live State
- **Legal entity: Trustsquare (Pty) Ltd · Reg 2026/340128/07 · Director: David Maurice Conradie · Registered 29/04/2026**
- BEA v1.3.0 live at trustsquare.co · FastAPI + SQLite + Redis on Hetzner CPX22
- Launch city: Pretoria, South Africa · **0 live listings (clean slate) · 70 demo listings active**
- Platform rebranded: MarketSquare → **TrustSquare** (all apps, BEA, EULA)
- GitHub: github.com/dmcontiki2/marketsquare

---

## Last Completed — Session 44

### End-to-end seller onboarding test — all 7 categories verified
- Full magic link → draft → tier picker → EULA → publish flow tested live on trustsquare.co
- All 7 categories published and confirmed live: Property, Tutors, Services, Adventures, Collectors, Cars, Local Market
- Local Market correctly routes through `/local-market/listings` (separate endpoint by design)
- Demo listings (70 client-side) co-exist with live BEA listings in renderGrid() without conflict

### BEA Bug Fixes (bea_main.py)
- **trust_score NULL on publish:** `PUT /listings/{id}/publish` now reads `users.trust_score` and stamps it onto the listing row at publish time via `COALESCE(trust_score, ?)`
- **ai_sessions not credited:** `User` model extended with `ai_sessions: Optional[int]`; `POST /users` now credits sessions on first registration only
- **Idempotency guard:** `POST /users` changed from bare INSERT + try/except to `INSERT OR IGNORE` + `rowcount` check — repeat magic link completions cannot stack free session credits

---

## Next Session — Session 45

### Priority: Paystack subscription + AI coach verification
1. Complete a Paystack test mode subscription payment flow end-to-end
2. Verify AI coach (advert-agent/coach) fires correctly per category with real listing data
3. Admin ops queue — review credential upload flow with a real listing
4. Gate `sbTriggerMarketNote` behind subscription tier for free sellers

### Backlog
- Paystack live mode — awaiting CIPC bank account setup
- Admin ops queue — review uploaded credentials
- Gate `sbTriggerMarketNote` behind subscription tier for free sellers
- For You trust score refresh on wishlist re-match

---

## Known Rules (session reminders)
- **NEVER use Edit or Write tool on `marketsquare.html` or `bea_main.py`** — Python `open/read/replace/write` only. Always verify tail ends with `</html>` or final function respectively.
- **Mandatory pre-deploy JS check**: extract inline scripts, run `node --check`
- **Python command**: use `python` not `python3` on Windows; use `python3` in sandbox
- **BEA venv**: always use `/var/www/marketsquare/venv/bin/pip` for server installs
- **Git commits**: ask David to run from PowerShell — never commit from sandbox (index.lock conflict)
- **SSH key**: run `bash load_sandbox_ssh.sh` at session start before any SSH/SCP
- **Cost model**: xlsx unchanged since Session 24 — no cost model impact this session
