# TrustSquare — STATUS.md
**Updated: Session 52 · 11 May 2026**

> ⚠️ **LAUNCH FREEZE — DO NOT TRIGGER WAVE 1 OR ANY OUTREACH**
> Pre-launch sequence must be fully complete before any email is sent.
> Sending even one email exposes prior art and voids patent defence.
> Sequence: Financial integration ✅ test → Patent filed → Whitepaper → Cities DB refreshed → David confirms launch → THEN Wave 1.

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
- **n8n outreach wave workflow: FULLY LIVE ✅** — tested end-to-end, first email sent to miconradie1@gmail.com, wave report delivered to dmcontiki2@gmail.com, `emailed_at` stamped in CityLauncher DB
- Platform rebranded: MarketSquare → **TrustSquare** (all apps, BEA, EULA)
- GitHub: github.com/dmcontiki2/marketsquare

---

## Last Completed — Session 52

### Adventures detail view upgrade ✅
- `ADV_ENV_LABELS`, `ADV_EXP_TYPE_LABELS`, `ADV_ACC_TYPE_LABELS` constants added (were referenced but never defined)
- Photo thumbnail row: 5 small thumbnails appear at bottom of hero strip for adventure listings — active thumb highlights white, clicking scrolls main strip, swiping syncs thumbs
- Enhanced stat strip: type badge (🦁 Luxury Safari, ⛺ Bush Camp etc.), environment pill, group size, duration, country badge — all styled with dedicated CSS classes (`.adv-stat`, `.adv-stat-strip`)
- `advThumbClick()` and `syncAdvThumbs()` JS functions added; strip `onscroll` wired to keep thumbs in sync
- JS syntax verified clean; deployed to trustsquare.co

## Last Completed — Session 51

### Graph 3-level navigation ✅
- Level 2 hover: detail panel slides in from right with type badge, breadcrumb, full context
- Level 3 click: centred detail card with colour-accented border and breadcrumb navigation
- Fixed D3 v7 event bubbling — native SVG listener replaces D3 bgRect handler
- Fixed mouseleave flicker — all visual children set pointer-events:none, single hit-circle per satellite
- Fixed missing openLevel3/closeLevel3 functions — inserted cleanly

### Live dashboard — permanent fix ✅
- `session_dashboard_live.html` no longer contains a static `const DATA = {...}` block
- On every load, `loadDashboard()` calls `GET /dashboard/summary` and populates the UI from live BEA data
- Loading state shown while fetch is in progress; auto-retries after 5s on error
- `GET /dashboard/summary` extended: new `directions` field — 4 auto-generated direction cards (Session next, Launch Blockers, CityLauncher Wave 1, AdvertAgent tier gating)
- Directions built from parsed STATUS.md next-session priorities + blockers — update STATUS.md only, dashboard refreshes automatically next load
- Both BEA and dashboard deployed to server and verified live

## Last Completed — Session 50

### My Space personal dashboard ✅
- New `screen-myspace` screen with 4 tabs: Overview, Intros, Trust, Me
- Bottom nav "Seller" button renamed "My Space" — now routes to personal dashboard
- Overview: wallet summary (links to existing Tuppence screen), open intro actions with Accept/Decline, 4-stat summary grid
- Intros tab: received/sent lists loaded live from BEA + wishlist prospects
- Trust tab: live score bar, 8 per-signal breakdown rendered from new BEA endpoint, AI coaching CTA
- Me tab: editable display name (localStorage), email, city, member-since date, roles chips, browse history, seller hub link
- Browse history: tracked client-side in localStorage via `msTrackView()` hooked into `openDetail()`
- New `GET /users/{email}/trust` BEA endpoint — score + tier + 8 signal objects
- Fixed pre-existing BEA truncation bug (line 6530 `tuppence_total =` incomplete since prior session) — restored from git

---

## Last Completed — Session 49

### Adventures page category system redesign ✅
- Scrolling environment chips replaced with fixed 4-chip category bar inside dark hero header
- Chip row hidden on "All" tab, shown only for Stays/Experiences with correct pinned categories
- "More ▾" bottom sheet slides up with all 7 (Experiences) or 8 (Accommodation) typed categories
- Gold active state for Experiences, blue for Stays — consistent visual identity
- 7 experience types: Luxury safari · Luxury train · Guided tours · Once in a lifetime · Water & coastal · Sky & aerial · Arts & culture
- 8 accommodation types: Private lodge · Bush camp · Mountain retreat · Coastal & island · Boutique hotel · Self-catering · Unique stays · Caravan & camping
- 10 luxury accommodation demo listings added (ZA × 8, MZ × 1, NA × 1) spanning all 8 types
- Card badges now show specific category type labels with colour coding
- Environment chip filter bug fixed (& → _and_ normalisation)

## Last Completed — Session 48

### n8n founding seller outreach wave — FULLY LIVE ✅
- Abandoned SendGrid (Twilio trial sandbox — unusable). Switched to already-authenticated Brevo SMTP (same cred used for intro emails since Session 46).
- Converted `Query CityLauncher Prospects` and `Mark Prospect as Emailed` nodes from SQLite plugin type (rejected by n8n API) → Code nodes using `require('sqlite3')` directly.
- Fixed CityLauncher DB schema mismatch: original query had `JOIN cities` — table doesn't exist. Removed JOIN, injected `city_name` from trigger params instead.
- Fixed n8n Code node sandbox restrictions: added `NODE_FUNCTION_ALLOW_EXTERNAL=sqlite3` and `NODE_FUNCTION_ALLOW_BUILTIN=fs,path` to Docker env so Code nodes can require sqlite3 and read template files with fs.
- Fixed email template file permissions: templates deployed with `-rwx------ root:root` — n8n container (uid 1000) couldn't read them. Fixed with `chmod 644`.
- Fixed `Mark Prospect as Emailed` JS: `$input.first()` disallowed in `runOnceForEachItem` mode — changed to `$('Build Email Payloads').item.json` to retrieve prospectId from upstream item lineage.
- Fixed CityLauncher DB readonly error: `chmod 666` on `citylauncher.db`, `citylauncher.db-wal`, `citylauncher.db-shm` and `chmod 777` on `/var/www/citylauncher/` — required for Docker container to write WAL files.
- Fixed Rate Limiter: `milliseconds` unit not supported in n8n v2.14 — changed to `1 second`.
- Execution 40: all 13 nodes green. Email delivered to miconradie1@gmail.com, wave report to dmcontiki2@gmail.com, `emailed_at = 2026-05-10 11:50:14` confirmed in CityLauncher DB.

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

## Next Session — Session 53

### Priority
1. **Paystack live mode** — complete financial integration end-to-end test (awaiting CIPC bank account — David action)
2. **Patent filing** — David to confirm readiness; do NOT proceed with any outreach until patent is filed
3. **Whitepaper** — draft and review before launch
4. **AI-Guided Listing Onboarding** — build 3-step card-preview onboarding screen (concept fully designed in Session 52; Maroushka is approved first tester after patent filed)

### Pre-Launch Gate (in order — ALL must be done before Wave 1)
> ⛔ Wave 1 is intentionally removed from all session priorities until David explicitly re-adds it.
> Reason: prior art defence — a single outreach email sent before patent filing voids the defence.

1. ✅ Financial integration complete + tested end-to-end
2. ✅ All applications completed and tested
3. ✅ Patent filed
4. ✅ Whitepaper published
5. ✅ Cities DB refreshed with current prospects
6. ✅ David confirms: "ready to launch"
→ Only then: load prospects, trigger Wave 1

### Backlog
- Admin ops queue — review uploade
- **Post-launch auto-scale** — n8n polls /health/resources, alerts at 70%, auto-upgrades Hetzner at 85%
- **UX degradation KPIs** — response time, 5xx rate, DB size thresholds
- Gate `sbTriggerMarketNote` behind subscription tier for free sellers
- For You trust score refresh on wishlist re-match
- Email template visual QA — review actual delivered email in Gmail

### 🌟 Session 53 Feature — AI-Guided Listing Onboarding
> ⚠️ Build before Wave 1. Test only after patent filed. Maroushka (miconradie1@gmail.com) is approved first tester.

**Concept:** Replace magic link → form → publish with a guided 3-step card-preview experience.

**The email:** Prospect receives invite showing their item as a pre-populated DRAFT listing card. Category-specific placeholder if no real data yet (e.g. Pretoria estate agent sees "3-bed home, Pretoria" with generic photo + DRAFT watermark). They see exactly what they'll get before clicking anything.

**Step 1 — Photo:** Opens with the draft card (empty). AI coach points to photo block. Seller uploads → card updates live showing exactly how it looks. Redo until happy. Press Step 2.

**Step 2 — Details:** AI points to item/service fields. Seller fills in → card reflects changes in real time. Input → view → update → view loop. AI confirms progress. Press Step 3.

**Step 3 — Review:** Full card preview. AI confirms completion. Seller clicks "Take me to the app →".

**In-app handoff:** Draft transfers into marketplace app. Same card-preview + AI guidance continues: EULA → registration → bank details → GO LIVE.

**Why this works:**
- Eliminates imagination gap — seller sees their listing from click 1
- Progressive disclosure — one job per step, no cognitive overload
- Card updates in real time — feels like polish not form-filling
- AI guidance is contextual, not instructional
- Existing infrastructure reused: BEA drafts + AI coach + magic link all exist

**Technical approach:** New front-end screen wired to existing BEA endpoints. Category-specific placeholder cards for cold prospects. DRAFT watermark overlay on existing listing card component.

---

## Known Rules (session reminders)
- **NEVER use Edit or Write tool on `marketsquare.html` or `bea_main.py`** — Python `open/read/replace/write` only. Always verify tail ends with `</html>` or final function respectively.
- **Mandatory pre-deploy JS check**: extract inline scripts, run `node --check`
- **Python command**: use `python` not `python3` on Windows; use `python3` in sandbox
- **BEA venv**: always use `/var/www/marketsquare/venv/bin/pip` for server installs
- **Git commits**: ask David to run from PowerShell — never commit from sandbox (index.lock conflict)
- **SSH key**: run `bash load_sandbox_ssh.sh` at session start before any SSH/SCP
- **Cost model**: xlsx unchanged since Session 24 — no cost model impact this session
