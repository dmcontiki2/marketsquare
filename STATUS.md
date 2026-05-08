# TrustSquare — STATUS.md
**Updated: Session 45 · 8 May 2026**

---

## Live State
- **Legal entity: Trustsquare (Pty) Ltd · Reg 2026/340128/07 · Director: David Maurice Conradie · Registered 29/04/2026**
- BEA v1.3.0 live at trustsquare.co · FastAPI + SQLite + Redis on Hetzner CPX22
- Launch city: Pretoria, South Africa · **0 live listings (clean slate) · 70 demo listings active**
- Platform rebranded: MarketSquare → **TrustSquare** (all apps, BEA, EULA)
- GitHub: github.com/dmcontiki2/marketsquare

---

## Last Completed — Session 45

### Paystack seller subscription flow + AI coach verification
- `POST /payment/seller-subscription/initialize` + `GET /payment/seller-subscription/verify` — full Paystack round-trip for Starter (R90/mo) and International (R270/mo) tiers
- `sobContinueFromTier()` — tier picker Continue now redirects paid tiers to Paystack; `sessionStorage` preserves onboarding state across redirect; `?ps_sub_return=1` resumes at EULA
- `POST /advert-agent/market-note` — new lightweight endpoint for inline B3/B4 market notes (no session gate, 1-sentence Haiku); fixes 422 error that was silently swallowing all inline AI notes
- All 7 categories verified against live coach endpoint (Property · Tutors · Services · Adventures · Cars · Collectors · Local Market)
- B4 free-seller nudge: `aa_sessions_remaining=0` shows "Free preview" banner pointing to AI Pack purchase
- Admin `docHubUpload()` now calls `/trust-score/upload-comment` after every non-ID upload — Haiku coaching comment displayed inline

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

## Next Session — Session 46

### Priority
1. Paystack live mode — awaiting CIPC bank account setup (David action)
2. n8n email notifications — buyer emailed on intro accept/decline
3. For You trust score refresh on wishlist re-match
4. Remove `/dev/credit` endpoint and Dev Tools nav tab before public launch

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
