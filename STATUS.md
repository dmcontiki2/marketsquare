# TrustSquare — STATUS.md
**Updated: Session 46 · 9 May 2026**

---

## ⚙️ CLAUDE INTERACTION PRINCIPLES (Founder Directives)

**Effective**: David sets these rules for all Claude sessions (Chat, Code, Design)

### Rule 1: Independence > Subscriptions
When advising on tooling, **surface open-source and self-hosted options FIRST**, then paid SaaS as alternatives. Rank by:
1. Self-hosted (free, sovereign)
2. Free tier open-source
3. Low-cost SaaS (<$20/mo)
4. Premium / consumption-based (flag cost ceiling always)

**Exception**: Tools where there is no reasonable open-source equivalent, or time-to-value is critical.

### Rule 2: Token Transparency
Before recommending a Claude-powered feature:
- Estimate token cost (in/out)
- Flag if consumption-based
- Suggest alternatives if cost is >10% of budget
- Never hide token math

**Rule**: "Should we use Claude Code for this, or would a bash script be faster/cheaper?"

### Rule 3: Flag Better Claude Functions
When you discover a newer Claude function, tool, or capability:
- **Always mention it as a possibility** (not a requirement)
- Explain what it enables vs current approach
- Let David decide

**Example**: "Claude Design would work better here. Should I switch?" (not: "Let me use Claude Design")

### Rule 4: Cost/Sovereignty Matrix
Every architectural decision gets this framing:

| Option | Cost | Sovereignty | Token Impact | Recommendation |
|--------|------|-------------|--------------|---|
| Self-hosted n8n | $0 (hosting only) | 100% | N/A | ✅ Primary |
| Zapier | $20–200/mo | 0% | N/A | ⚠️ Fallback only |
| Claude Code + bash | ~300 tokens/session | 100% | Transparent | ✅ Preferred |

### Rule 5: Question Your Own Advice
If David asks "Why didn't you suggest X?" or "What's the self-hosted version?":
- **Stop and answer directly**
- Don't assume he's aware of cost principles
- Reframe the decision

**Bottom line**: David's principles are *your* guardrails, not his responsibility to enforce.

---

## Live State
- **Legal entity: Trustsquare (Pty) Ltd · Reg 2026/340128/07 · Director: David Maurice Conradie · Registered 29/04/2026**
- BEA v1.3.0 live at trustsquare.co · FastAPI + SQLite + Redis on Hetzner CPX22
- Launch city: Pretoria, South Africa · **5 live listings (Maroushka — IDs 93–97) · 70 demo listings active**
- Maroushka registered in BEA: `miconradie1@gmail.com` · magic link sent via Gmail
- n8n outreach wave workflow: imported but SendGrid credentials NOT wired — untested ⚠️
- Platform rebranded: MarketSquare → **TrustSquare** (all apps, BEA, EULA)
- GitHub: github.com/dmcontiki2/marketsquare

---

## Last Completed — Session 47

### Maroushka live simulation test ✅
- 5 Property listings created and published live under `dmcontiki2@gmail.com` (IDs 93–97): 1-bed Waterkloof apartment, 2-bed garden apartment Waterkloof, 3-bed family home Waterkloof Ridge, executive studio Arcadia, 2-bed penthouse Brooklyn
- All published via `PUT /listings/{id}/publish` — confirmed live in buyer feed at trustsquare.co
- 70 demo listings confirmed present client-side alongside real listings
- Maroushka registered in BEA: `miconradie1@gmail.com` · `POST /users` called
- Magic link personalised and sent to Maroushka via Gmail: `https://trustsquare.co/?magic=1&name=Maroushka&email=miconradie1@gmail.com&cat=Property&city=Pretoria`
- Maroushka added to CityLauncher `prospects` table (table created this session — was missing)

### n8n outreach wave — NOT tested ⚠️
- `n8n_outreach_workflow.json` imported into n8n UI successfully
- SendGrid credentials NOT wired — workflow cannot execute
- **Session 48 sole goal: wire SendGrid credentials + test single outreach email end-to-end**

---

## Last Completed — Session 46

### n8n email notifications — intro accept/decline ✅ FULLY LIVE
- `intro_accepted.html` + `intro_declined.html` branded TrustSquare templates (dark navy/gold, CSS-inlined for n8n)
- Both n8n workflows live and tested — emails delivered to inbox from `noreply@trustsquare.co`
- `trustsquare.co` domain authenticated in Brevo — SPF/DKIM aligned, inbox delivery confirmed
- BEA decline webhook payload extended with `category` + `city` fields
- `N8N_WEBHOOK_ACCEPT` + `N8N_WEBHOOK_DECLINE` set on Hetzner, duplicates cleaned from `/etc/environment`
- `bea_main.py` committed and pushed (Session 46 fix)
- Key n8n fix: `activeVersionId` in `workflow_entity` must match `workflow_history` — direct DB edits require updating both tables and restarting the container

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

## Next Session — Session 48

### Priority
1. **n8n outreach wave — wire SendGrid credentials and test single email to miconradie1@gmail.com end-to-end** (sole goal)

### Backlog
- Paystack live mode — awaiting CIPC bank account setup (David action)
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
