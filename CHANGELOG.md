# MarketSquare · CHANGELOG

---

## Session 1 · 28 March 2026 · Morning

### What was built
- Claude Code 2.1.84 installed via winget on Windows 11
- Project folder created: C:\Users\David\Projects\MarketSquare
- Master CLAUDE.md created with 5 operating principles
- Three agent folders created: agents/architect/ · agents/frontend/ · agents/admin/
- Each agent folder has its own CLAUDE.md defining its lane
- Git initialised, identity configured, first commit made
- Core files renamed (removed Windows duplicate suffix) and committed:
  - marketsquare_v8_6b.html
  - marketsquare_admin_v1_1.html
  - Solar_Council_Codex_v4_0.docx
- 360 Total Security whitelisted: Claude Code · Git · MarketSquare folder

### Operating principles locked
1. When unsure — make best guess, implement, flag uncertainty at end
2. Change size — one feature or bug fix per task, one file section at a time
3. Git — auto-commit after every completed task with descriptive message
4. Definition of done — working code + one-paragraph entry appended to CHANGELOG.md
5. Conflict arbitration — Architect agent arbitrates via Codex; escalate to David only if Codex cannot resolve

### Agent structure
- Architect agent · agents/architect/CLAUDE.md · owns Codex rules and system design
- Frontend agent · agents/frontend/CLAUDE.md · owns marketsquare_v8_6b.html
- Admin agent · agents/admin/CLAUDE.md · owns marketsquare_admin_v1_1.html

### Decisions made
- BEA and CityAutoRollOut agents deferred — add when those concepts have their own dedicated files
- GitHub setup deferred to Session 2
- Startup script deferred to Session 2

### Open items for Session 2
1. Build master briefing document for the 3 Claude Code agents
2. Set up GitHub for project backup
3. Build and test start_marketsquare.bat desktop startup script
4. Correct Codex — Solis is a ChatGPT/OpenAI persona, not a Grok agent
5. Correct Codex — 1 Tuppence = USD $2 (not $1)
6. Update agent CLAUDE.md files to reflect MarketSquare is a marketplace app, not a game

### Notes
- MarketSquare is a local marketplace app (not a game)
- Three agents are Claude Code agents, not ChatGPT/Grok/Claude mix
- Solis is a David persona used in ChatGPT — external to Claude Code setup
- 1 Tuppence = USD $2
- Pro plan in use — no additional costs beyond subscription

---

## Session 2 · 28 March 2026 · Afternoon

### What was built
- start_marketsquare.bat created — desktop startup script
  - Copies last CHANGELOG entry to clipboard
  - Opens claude.ai/new in browser
  - Opens trustsquare.co and trustsquare.co/admin.html
  - Launches Claude Code in Windows Terminal at project folder
- CHANGELOG.md created (this file)

### Open items continuing
1. Build master briefing document for the 3 Claude Code agents
2. Set up GitHub for project backup
3. Test start_marketsquare.bat end-to-end

---

## Session 2 · 28 March 2026 · Afternoon (continued)

### What was built
- AGENT_BRIEFING.md completed — master briefing document for all three Claude Code agents.
  Single source of truth covering: product overview, core concepts, file map, agent lanes,
  BEA API reference, infrastructure, operating rules, and pending items.
- GitHub repository set up at https://github.com/dmcontiki2/marketsquare
  - Account created: dmcontiki2 (dmcontiki2@gmail.com)
  - Empty repo created: marketsquare
  - All project files pushed to main branch with tracking set up

### All Session 2 open items resolved
1. ✅ Master briefing document — AGENT_BRIEFING.md
2. ✅ GitHub backup — github.com/dmcontiki2/marketsquare
3. 🔜 Test start_marketsquare.bat end-to-end — deferred to Session 3

### Notes
- From Session 3 onward, agents should read AGENT_BRIEFING.md at session start
- Future commits will be backed up to GitHub automatically via Claude Code auto-commit rule
- CLAUDE.md still describes MarketSquare as a game — update is pending (Session 2 open item 8)

---

## Session 3 · 30 March 2026 · Morning

### What was built

**Claude Code settings.json updated** — four settings configured:
- conversationRetentionDays: 365
- CLAUDE_CODE_MAX_OUTPUT_TOKENS: 150000
- CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: 75
- CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS: 1

**Three critical bugs fixed in marketsquare_v8_6b.html:**
1. Category mismatch — BEA listings showing in wrong category. Fixed by adding normCat() function in loadLiveListings() to normalise BEA category strings (e.g. 'property', 'PROPERTY') to exact CATS keys ('Property', 'Tutors', 'Services').
2. Adverts not clickable — openDetail(id) was using LISTINGS[id] as an array index, which fails for BEA string ids like 'bea_3'. Fixed by adding findListing(id) helper that searches by value. Also fixed all onclick handlers that interpolated l.id without quotes, causing browser to treat 'bea_3' as an undefined variable.
3. Magic claim links broken — admin tool generated correct URLs but frontend had no code to read the URL params. Fixed by adding URLSearchParams parser on DOMContentLoaded that reads magic=1, name, email, cat, city params and routes straight to the onboard screen with fields pre-filled.

**Hardcoded demo data removed from marketsquare_v8_6b.html:**
- 6 hardcoded listings replaced with 3 placeholder cards (one per category) — dashed border, faded, non-clickable, labelled 'Awaiting first [category] seller'
- 6 hardcoded seller CVs replaced with 3 minimal placeholder sellers
- Hardcoded dashState listings replaced with empty array — populated by loadLiveDash() from BEA
- renderGrid() updated to show placeholders despite paused:true flag
- renderFeatured() updated with empty state message when no featured listings exist
- Results count excludes placeholders

**Server deployment issues resolved:**
- Identified correct nginx serve path: /var/www/marketsquare/ (not /var/www/html/)
- admin.html was missing from server — uploaded via SCP from local Windows terminal
- nginx config updated to add location = /admin.html block so it doesn't fall through to FastAPI
- Correct SCP commands for future deployments documented below

**360 Total Security false positive resolved:**
- atiuxp64.dll (AMD GPU driver) flagged on every startup — confirmed false positive
- Fix: exclude entire C:\Windows\System32\DriverStore\FileRepository folder in 360 settings

### Deployment commands (save these)
```
# Deploy buyer app
scp C:\Users\David\Projects\MarketSquare\marketsquare_v8_6b.html root@178.104.73.239:/var/www/marketsquare/index.html

# Deploy admin tool
scp C:\Users\David\Projects\MarketSquare\marketsquare_admin_v1_1.html root@178.104.73.239:/var/www/marketsquare/admin.html
```

### Status at end of session
- trustsquare.co — live, Maroushka's property listings loading from BEA, fully clickable ✅
- trustsquare.co/admin.html — live, admin onboarding tool accessible ✅
- Magic claim links — working end-to-end ✅
- Placeholder cards — visible in browse grid, one per category ✅
- Email to Maroushka and David — drafted, ready to send ✅

### Open items for Session 4
1. Send email to Maroushka and David to start adding property listings
2. Maroushka to add real property listings via admin tool
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos off local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6. Correct Codex — Solis is a ChatGPT/OpenAI persona, not Grok
7. Correct Codex — 1 Tuppence = USD $2 (currently blank in table)
8. Update agent CLAUDE.md files to reflect marketplace, not game
9. Paystack live mode — pending CIPC registration

---

## Session 4 · 31 March 2026

### What was built
- `marketsquare_admin.html` upgraded from v1.0 (4-step wizard only) to v2.0 (full dashboard). The existing 4-step onboarding wizard is unchanged and now lives under the **Onboard** tab. Five new sections added via a fixed bottom nav bar: **My Listings** (fetch all BEA listings, filter by category, delete); **Seller Profile** (look up by email via `GET /users/{email}`, delete account); **Analytics** (live pending intro count + live listing count from BEA, with Coming Soon placeholders for BEA v1.2 metrics); **Account & Billing** (placeholder pending Paystack live mode); **Alerts** (load all pending intros from `GET /intros`, show 48hr countdown with colour coding, Accept/Decline buttons wired to BEA).

### Status at end of session
- marketsquare_admin.html (local) — v2.0 dashboard built ✅
- Needs SCP deploy to server to go live at trustsquare.co/admin.html

### Open items carried forward
1. Deploy marketsquare_admin.html to server (SCP command in AGENT_BRIEFING)
2. Maroushka real listings — add via admin tool
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos off local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6–8. Codex corrections and agent CLAUDE.md updates (Architect agent)
9. Paystack live mode — pending CIPC registration

## Session 5 · 31 March 2026

### Completed in this session

**Planning and architecture (claude.ai):**
- Session 4 briefing completed — open items 1, 6, 7 confirmed done
- Admin dashboard spec defined: 5 panels (Profile, Listings, 
  Analytics, Billing, Alerts) with full field and metric breakdown
- Property filter gap analysis completed — buyer app filter sheet 
  missing 9 property types, Listing Type, Furnished, Pet Friendly, 
  Internet, 10 features vs admin tool
- Auto-research session protocol designed — OIM framework documented
  for future sessions
- Token management strategy confirmed — Claude Code preferred over
  claude.ai for all file editing tasks

**Deployment:**
- Both files deployed to server via PowerShell SCP:
  - marketsquare.html → /var/www/marketsquare/index.html
  - marketsquare_admin.html → /var/www/marketsquare/admin.html
- Correct local filenames confirmed: marketsquare.html and 
  marketsquare_admin.html (no version suffix on disk)
- AGENT_BRIEFING, CHANGELOG, CLAUDE, settings files still have 
  Windows duplicate suffixes — rename in Claude Code Session 5

### Open items for Session 6
1. Fix buyer app property filter sheet to match admin tool fields
2. Build seller self-service dashboard in admin tool (5 panels)
3. Maroushka real listings — add via admin tool
4. n8n email notifications — buyer emailed on intro accept/decline
5. Hetzner Object Storage — migrate photos from local /media
6. Update start_marketsquare.bat with correct SCP deploy commands
7. Rename project files — remove Windows duplicate suffixes
8. Paystack live mode — pending CIPC registration

## Session 6 · 1 April 2026

### Completed in this session

**Planning and architecture (claude.ai):**
- Maroushka test review analysed — 4 bugs identified and task
  instructions written for Claude Code
- Security warning on start_marketsquare.bat diagnosed — Windows
  SmartScreen false positive, not 360 antivirus; fix is to unblock
  the file via Properties
- Codex v4.2 produced — new §6 Buyer Subscription Tiers & Cost Model
  added covering tier definitions, fixed infrastructure costs,
  breakeven scenarios, and server capacity notes

**Five Claude Code tasks worded and ready for execution:**

- Task 1 · Currency formatting — standardise all monetary values to
  R1,234,456.00 format throughout both apps using a shared formatZAR()
  helper function
- Task 2 (revised) · Structured description — replace free-text
  description field in admin tool with structured editor (headline,
  tagline, summary, repeatable sections + bullets); serialise as JSON
  into existing BEA description field; buyer app renderer detects JSON
  and renders as formatted HTML, falls back to plain text for legacy
  listings
- Task 3 · Photo carousel — listing detail screen becomes a
  horizontally swipeable carousel with arrow buttons, dot indicators,
  and touch/swipe support; uses medium_url array from BEA listing
- Task 4 · Category listing counts (city-scoped) — counts derived
  dynamically from live listings filtered to active city only;
  excludes ph_ placeholders; re-renders after loadLiveListings()
  completes
- Task 5 · City selector tier-gated — Free tier locked to local city
  (non-interactive); Starter ($5/mo) opens country-scoped city
  dropdown; Premium ($15/mo) opens global city dropdown; stats strip
  updates to match selected city; BEA /cities endpoint flagged as
  pending

**Buyer subscription tier model defined (preliminary):**

| Tier     | Price   | Sessions/day | City scope                  |
|----------|---------|-------------|------------------------------|
| Free     | $0      | 3 (hard)    | Local city only              |
| Starter  | $5/mo   | 20          | All cities in same country   |
| Premium  | $15/mo  | 50          | All cities globally          |

Note: prices and session limits are preliminary pending Paystack
go-live and final product decision.

**Infrastructure cost model established:**
- Fixed costs: ~$10/month (Hetzner CPX22 + domain)
- Breakeven: 2 Starter subscribers covers all infra costs
- CPX22 can comfortably serve ~16,000 free-only users before upgrade
- Next tier: Hetzner CPX32 at ~$17/month
- AI agent app token costs are a separate model — not applicable to
  MarketSquare itself

### Open items for Session 7
1. Execute Task 1 — currency formatting (Claude Code)
2. Execute Task 2 — structured description editor + renderer (Claude Code)
3. Execute Task 3 — photo carousel (Claude Code)
4. Execute Task 4 — category listing counts city-scoped (Claude Code)
5. Execute Task 5 — city selector tier-gated (Claude Code)
6. Deploy all changes to server after testing
7. Maroushka real listings — re-enter via admin tool using new
   structured description editor once Task 2 is done
8. n8n email notifications — buyer emailed on intro accept/decline
9. Hetzner Object Storage — migrate photos from local /media
10. Update start_marketsquare.bat — correct SCP deploy commands
11. Paystack live mode — pending CIPC registration
12. Rename project files — remove Windows duplicate suffixes

---

## Session 7 · 1 April 2026 (continued)

### Completed in this session

Tasks 1–5 confirmed complete via git history. The SESSION_7_START_PROMPT.md process was validated — agent correctly identified outstanding work and confirmed completed tasks instantly. Start prompt format confirmed solid for future sessions.

- **Task 1 · Currency formatting** — formatZAR() helper implemented across both marketsquare.html and marketsquare_admin.html. All monetary values display as R1,234,456.00.
- **Task 2 · Structured description** — admin tool listing form replaced with structured editor (headline, tagline, summary, sections + bullets), serialised as JSON. Buyer app renderer detects JSON and renders as formatted HTML, falls back to plain text for legacy listings.
- **Task 3 · Photo carousel** — listing detail screen updated with swipeable carousel, arrow buttons, dot indicators, and touch/swipe support. Uses medium_url array from BEA listing object.
- **Task 4 · Category listing counts** — counts now derived dynamically from live listings, filtered to active city and suburb scope, excluding ph_ placeholders. Re-renders after loadLiveListings() completes.
- **Task 5 · City selector tier-gated** — Free locked to local city, Starter opens country-scoped selector, Premium opens global selector. Tier state defaults to Free pending Paystack go-live.

### Open items for next session
1. Task 6 Parts B & C — Admin suburb dropdown + buyer app three-level location selector
2. Maroushka real listings — re-enter via admin tool using structured description editor
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos from local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6. Paystack live mode — pending CIPC registration

---

## Session 7 · 1 April 2026 · Task 6 Part A — BEA suburbs & cities

Added three-level location hierarchy support to the BEA (main.py). Migration runs on startup: creates `suburbs` table (id, name, city, country, active, created_at) with index on city+active, adds `suburb TEXT` column to listings, and defaults existing rows to "Central". Seed function loads suburbs_seed.json (31 Pretoria suburbs) on first start, skipping subsequent runs. `GET /listings` now accepts optional `&suburb=` filter. `POST /listings` now requires `suburb` field (400 if missing), and inserts it. New endpoints: `GET /suburbs?city=` returns sorted active suburb names; `GET /cities?country=` returns city list for that country; `GET /cities` returns all cities grouped by country; `POST /cities` (auth required) creates a city placeholder and triggers a background GeoNames fetch to seed its suburbs (requires GEONAMES_USERNAME in .env). `httpx` added as import for async GeoNames calls.

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `scp suburbs_seed.json root@178.104.73.239:/var/www/marketsquare/suburbs_seed.json` then `systemctl restart marketsquare-bea`.
