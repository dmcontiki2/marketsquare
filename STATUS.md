# TrustSquare — STATUS.md
**Updated: Session 43 · 5 May 2026**

---

## Live State
- **Legal entity: Trustsquare (Pty) Ltd · Reg 2026/340128/07 · Director: David Maurice Conradie · Registered 29/04/2026**
- BEA v1.3.0 live at trustsquare.co · FastAPI + SQLite + Redis on Hetzner CPX22
- Launch city: Pretoria, South Africa · **0 live listings (clean slate) · 70 demo listings active**
- Platform rebranded: MarketSquare → **TrustSquare** (all apps, BEA, EULA)
- GitHub: github.com/dmcontiki2/marketsquare

---

## Last Completed — Session 43

### Rebrand + Legal Entity
- MarketSquare → TrustSquare across all apps, BEA, and EULA
- EULA updated with Trustsquare (Pty) Ltd · Reg 2026/340128/07 · registered address · tax number
- All test data wiped (51 listings, 5 users, all transactional records) · geo data preserved

### 70 Demo Listings — All Categories Complete
- 10 listings per category: Property, Tutors, Services, Adventures, Collectors, Cars, Local Market
- 5 Unsplash photos each, realistic SA pricing, fully detailed descriptions
- All tagged `demo_` prefix — distinguishable from live listings
- Local Market required 3 fixes: missing chip, cat normalisation in renderGrid, BEA-only lmLoadGrid fallback

### Trust Score Integrity
- All demo scores recalculated from actual `_TRUST_SIGNALS` / `_CATEGORY_SIGNALS` in bea_main.py
- Property private sellers: Established tier (~44) · Tutors: Trusted (~81) · Services: Trusted (~88)
- Seller CV now displays `s.trustScore` (seller-level verified score) — not arbitrary per-listing number
- Defensible and traceable — legal/trust exposure concern addressed

### Seller CV Fixes
- Availability "undefined · undefined" fixed — all SELLERS entries use `{day, time}` objects
- Property seller credentials updated to match private seller signal set

---

## Next Session — Session 44

### Priority: End-to-end seller onboarding test
1. Full magic link → draft → preview → tier picker → EULA → publish flow
2. Verify trust score calculated correctly on first real listing
3. Verify AI coach fires correctly per category
4. Paystack test mode — complete a subscription payment flow
5. Cross-category browse test with real listings alongside demo listings

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
