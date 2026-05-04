# MarketSquare — STATUS.md
**Updated: Session 40 · 3 May 2026**

---

## Live State
- BEA v1.2.0 live at trustsquare.co · FastAPI + SQLite + Redis on Hetzner CPX22
- Launch city: Pretoria, South Africa · 6 live listings (23 / 60 founding sellers target)
- GitHub: github.com/dmcontiki2/marketsquare

---

## Last Completed — Session 41

### Draft-first listing flow — seller onboarding gate
1. **BEA `POST /listings`** — now saves all new listings with `listing_status = 'draft'` and `published_at = NULL`. Listings are invisible to buyers until the seller completes onboarding.
2. **BEA `PUT /listings/{id}/publish`** — new endpoint. Transitions `draft → live`, stamps `published_at = now()`. Email-auth: seller_email must match or is stamped if NULL on first call.
3. **Admin app Step 4** — renamed "Review & save draft". Button now reads "Save drafts →". All success messaging updated to reflect draft state. Magic link hint explains full seller journey.

### Onboarding flow design (3-session build)
- **Session 41 (done)**: BEA draft gate + admin app draft save
- **Session 42 (next)**: `marketsquare.html` magic link landing — private preview, tier picker, EULA, registration
- **Session 43**: End-to-end test all categories + AI Coach offer post-registration

---

## Next Session — Session 42

### Priority: Seller onboarding funnel in marketsquare.html
Build the magic link landing flow:
1. **Private listing preview** — seller sees their draft listing exactly as buyers will, with a "Not live yet" banner
2. **Subscription tier picker** — Free / Starter R59/mo / Premium R149/mo with visual reach comparison
3. **EULA screen** — inline acceptance, logged to BEA
4. **Registration screen** — name confirm, ID upload (defer bank details to first intro acceptance)
5. **Go live** — call `PUT /listings/{id}/publish`, show confirmation + AI Coach offer with free session

### Backlog
- Draft save/resume — save at B7, exit, re-enter, confirm resume banner
- For You trust score refresh — existing matched cards show old score (25); needs wishlist re-match or score refresh trigger
- Paystack live mode — awaiting CIPC approval email
- Local Market detail view — multi-photo strip for LM listings
- Admin ops queue — review pending credentials uploaded by sellers
- Gate `sbTriggerMarketNote` behind subscription tier for free sellers (low priority — ~$67/yr cost)

---

## Known Rules (session reminders)
- **NEVER use Edit or Write tool on `marketsquare.html` or `bea_main.py`** — Python `open/read/replace/write` only. Always verify tail ends with `</html>` or final function respectively.
- **Mandatory pre-deploy JS check**: extract inline scripts, run `node --check`
- **Python command**: use `python` not `python3` on Windows; use `python3` in sandbox
- **BEA venv**: always use `/var/www/marketsquare/venv/bin/pip` for server installs
- **Git commits**: ask David to run from PowerShell — never commit from sandbox (index.lock conflict)
- **SSH key**: run `bash load_sandbox_ssh.sh` at session start before any SSH/SCP
