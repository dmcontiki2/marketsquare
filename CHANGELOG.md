# MarketSquare · CHANGELOG

---

## Session 12 · 14 April 2026 · Phase 1 category alignment — canonical register

Locked the canonical category register (Property · Tutors · Services · Adventures · Collectors) across all platform files. Services was split into two sub-classes — Technical (licensed/accredited trades: Electrical, Plumbing, HVAC, Solar, IT, Legal, Financial, Landscaping) and Casuals (domestic/informal: Domestic, Gardening, Dog Walking, Child Minding, Temp, General Labour) — with a single "Services" browse tile and an internal `service_class` filter. Help Wanted absorbed into Casuals. Automotive deferred (no phase). Adventures (formerly Travel & Experiences) and Collectors (merges MTG/Collectibles + Philately) confirmed as Phase 2. The `service_class` TEXT column was added to the `listings` table via idempotent `run_migrations()`. The `Listing` model and both insert paths (POST /listings and /advert-agent/publish) were updated to write `service_class`. The AdvertAgent AA_CATEGORIES object was rebuilt with the 5-category canonical register: Real Estate renamed to Property, Tutors added, Services given a `serviceClasses` sub-structure (Technical/Casuals each with their own field sets and photo checklists), Adventures and Collectors added as Phase 2. A `aaCatConfig(draft)` helper function routes field/photo config through `service_class` for Services drafts. The AA Stage 1 form now shows a class chip selector (Technical/Casuals) before rendering the Services form. The admin tool's Help Wanted category tile was removed; Services now shows a Class dropdown (Technical/Casuals) and a combined service type optgroup list. The buyer app filter sheet for Services gained a "Class" chip section (Any / Technical / Casuals) at the top. The `filterState.services.serviceClass` property was added, wired into `applyFilters`, `clearFilters`, and `renderActiveFilterTags`. Card badges show 🔧 Technical or 🤝 Casuals sub-badge where `service_class` is set. PRINCIPLE_REQUIREMENTS.md D7 updated to the locked 5-category register. AGENT_BRIEFING.md updated in both MarketSquare and AdvertAgent projects. CityLauncher gumtree.py updated to output `service_class` and normalise Casuals→Services category. `migrate_db_v2.py` extended with Part 4 to add `service_class` to `prospects` and `prospects_raw` tables. All three files deployed.

---

## Cross-project update · 12 April 2026 · PRINCIPLE_REQUIREMENTS v1.1

PRINCIPLE_REQUIREMENTS.md v1.1 — Rule B7 added: no consumption-based external API without David's explicit approval and cost ceiling. Triggered by Google Cloud API incident (R3,612 charged without approval). Updated in all 3 project folders: MarketSquare, CityLauncher, AdvertAgent. Dated 12 April 2026.

---

## Cross-project update · 11 April 2026 · Cowork framework + AdvertAgent scaffold

Updated `CLAUDE.md` Codex reference from v4_3 to v4_4. `AGENT_BRIEFING.md` was already at v1.3 (11 April 2026) with correct Codex reference. AdvertAgent project scaffolded at `C:\Users\David\Projects\AdvertAgent\` — governed by PRINCIPLE_REQUIREMENTS.md Part G (G1–G4), with its own AGENT_BRIEFING.md (v0.1 pre-kickoff), STATUS.md, CHANGELOG.md, and CLAUDE.md. PRINCIPLE_REQUIREMENTS.md v1.0 copied to both CityLauncher and AdvertAgent project roots. Architecture, subscription pricing, and UI integration point for AdvertAgent deferred to kickoff session.

---

## Cross-project update · 10 April 2026 (CityLauncher Session 9)

### Photo storage migrated to Cloudflare R2, admin app UX fixes

Photo storage moved from degraded Hetzner Object Storage (NBG1, down since 5 March 2026) to Cloudflare R2 EU jurisdiction. Bucket: `marketsquare-media`. Public URL: `pub-3c51d058a6494b93af4d242d07bdc4da.r2.dev`. Server env vars updated (`HETZNER_S3_*` reused — S3-compatible, no code changes). `_s3_upload()` in `main.py` updated to return R2 public dev URL. Three admin app fixes: (1) property feature checkboxes now clickable — excluded checkboxes from `-webkit-appearance: none`; (2) multiple photo upload race condition fixed — slots reserved synchronously; (3) removed extra click — direct onclick handler + drag-drop + clipboard paste support. Native `<select>` dropdowns restored on mobile with `appearance: menulist`.

Cost model impact: Photo storage $0 (10 GB free, zero egress). Replaces Hetzner Object Storage which was unreliable and charged per-GB egress.

---

## Session 10 · 5 April 2026 · 4-level location hierarchy — buyer app + admin tool

Replaced the flat city/suburb selectors in both frontends with a full Country → Region → City → Suburb drill-down. Buyer app: activeCity is now an object {id, name} (resolved to Pretoria's DB id on startup via _resolveActiveCity()); activeSuburb is {id, name} or null; activeCountry and activeRegion track the full hierarchy. updateBadgeLabel() shows all four levels. The location selector sheet now has four panels (country, region, city, suburb) driven by /geo/* API calls. Tier gating: free opens suburb panel directly; starter opens city panel; premium opens country panel. loadLiveListings() and renderGrid/renderCatCounts updated to use .name properties. Admin tool: static city dropdown replaced with cascading Province → City selects populated from /geo/regions?country=ZA and /geo/cities?region_id=. goNext() step 1 now stores geo_city_id on sellerData. loadSuburbsForForm() switched to /geo/suburbs?city_id= returning {id, name} objects.

---

## Session 10 · 5 April 2026 · Geographic hierarchy — BEA database restructure

Replaced the flat suburbs table with a proper 4-level relational schema: geo_countries, geo_regions, geo_cities, geo_suburbs. South Africa seeded on first startup from the GeoNames ZA data dump (downloaded to /tmp, parsed, deleted). Provinces, cities and suburbs linked relationally via admin1+admin2 codes. New /geo/* endpoints serve the full hierarchy. Old /suburbs and /cities endpoints preserved as compatibility shims. New POST /geo/countries endpoint triggers background GeoNames API seed for any new country. GEONAMES_USERNAME=dmcontiki2 added to /etc/environment. Existing listings migrated to geo_city_id where city name matches exactly.

---

## Session 10 · 5 April 2026 · buyer_name field in buyer app

Added buyer_name input to the intro request form in marketsquare.html. Field appears above the email input, styled consistently. The POST /intros fetch payload now includes buyer_name (null if left blank — field is optional). Intro sheet reset now clears the name field alongside email and message. BEA stores and forwards the value through n8n webhook payloads on accept/decline.

---

## Session 10 · 5 April 2026 · buyer_name fix (BEA)

Added buyer_name field to the intro_requests table and throughout the intro submission flow. run_migrations() now detects and adds the column on startup (idempotent). IntroRequest Pydantic model accepts buyer_name as an optional field. POST /intros stores it. Both n8n webhook payloads (accept and decline) now read buyer_name from the DB row instead of sending null. No frontend changes required — the field is optional so existing intro submissions without it continue to work.

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
1. Deploy all Task 6 changes to server (both HTML files + bea_main.py)
2. Maroushka real listings — re-enter via admin tool using structured description editor
3. n8n email notifications — buyer emailed on intro accept/decline
4. Hetzner Object Storage — migrate photos from local /media
5. Update start_marketsquare.bat with correct SCP deploy commands
6. Paystack live mode — pending CIPC registration

---

## Session 7 · 1 April 2026 · Task 6 Part A — BEA suburbs & cities

Added three-level location hierarchy support to the BEA (main.py). Migration runs on startup: creates `suburbs` table (id, name, city, country, active, created_at) with index on city+active, adds `suburb TEXT` column to listings, and defaults existing rows to "Central". Seed function loads suburbs_seed.json (31 Pretoria suburbs) on first start, skipping subsequent runs. `GET /listings` now accepts optional `&suburb=` filter. `POST /listings` now requires `suburb` field (400 if missing), and inserts it. New endpoints: `GET /suburbs?city=` returns sorted active suburb names; `GET /cities?country=` returns city list for that country; `GET /cities` returns all cities grouped by country; `POST /cities` (auth required) creates a city placeholder and triggers a background GeoNames fetch to seed its suburbs (requires GEONAMES_USERNAME in .env). `httpx` added as import for async GeoNames calls.

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `scp suburbs_seed.json root@178.104.73.239:/var/www/marketsquare/suburbs_seed.json` then `systemctl restart marketsquare.service`.

## Session 7 · 1 April 2026 · Task 6 Part C — Buyer app three-level location selector

Replaced the single-city badge with a Country → City → Suburb drill-down. Added `activeSuburb` (null = All suburbs) and `availableSuburbs` state variables. Added `updateBadgeLabel()` which sets the badge to `{city} · All suburbs` or `{city} · {suburb}`. The location bottom sheet now has two panels: city panel and suburb panel. `openLocPanel('city'|'suburb')` switches between them. Selecting a city drills directly into the suburb panel. `selectSuburb()` sets `activeSuburb`, updates the badge, and re-calls `loadLiveListings()`. `loadLiveListings()` now appends `&suburb=` to the BEA query when a suburb is active. Tier gating: Free opens suburb panel directly (city locked); Starter opens city panel filtered to ZA; Premium opens city panel globally. `renderCatCounts()` and `renderGrid()` both respect `activeSuburb`. Startup sequence: `loadCities → loadSuburbsForSelector → loadLiveListings`.

## Session 7 · 1 April 2026 · Task 6 Part B — Admin tool suburb dropdown + City Management tab

Added suburb selection to the listing form in Step 3 of the admin onboarding wizard. When the form opens, `loadSuburbsForForm()` fetches `GET /suburbs?city={sellerData.city}` and populates a dropdown. Suburb is required — `saveListingToQueue()` blocks submission if unset. The suburb value is stored in `formData.suburb` and included in the BEA publish payload. The old free-text "Area / Suburb" field is now labelled "Area" (still optional/freeform). Added a City Management tab (nav icon 🌍) with a cities table (city, country, suburb count) loaded from `GET /cities`, and an "Add city" form that POSTs to `POST /cities` and shows a "fetching suburbs in background" status. `goView('cities')` auto-loads the table on tab open.

---

## Session 8 · 2 April 2026 · Task 2 — n8n email notifications (BEA)

Added fire-and-forget webhook calls to `PUT /intros/{id}/accept` and `PUT /intros/{id}/decline`. Two new env vars — `N8N_WEBHOOK_ACCEPT` and `N8N_WEBHOOK_DECLINE` — are read at startup via `os.getenv()`; if either is missing the BEA logs one warning and continues without sending that email. Both endpoints now accept `BackgroundTasks` and schedule an async `_fire_webhook()` call after the DB update completes. The webhook uses `httpx.AsyncClient` with a 5-second timeout; any failure is logged and the API response is unaffected. Webhook payloads include event type, intro/listing IDs, listing title, buyer email, city, and UTC timestamp. `buyer_name` and `seller_display_name` are sent as `null` — these fields are not yet stored in the current schema (noted as a future addition). No frontend changes required. **n8n setup is a one-time manual step — see deploy notes below.**

**n8n server setup (one-time manual steps on Hetzner):**
1. `npm install -g n8n`
2. Create `/etc/systemd/system/n8n.service`:
   ```
   [Unit]
   Description=n8n workflow automation
   After=network.target
   [Service]
   Type=simple
   User=root
   ExecStart=/usr/bin/n8n start
   Restart=on-failure
   Environment=N8N_PORT=5678
   Environment=N8N_PROTOCOL=http
   Environment=N8N_HOST=localhost
   Environment=WEBHOOK_URL=http://localhost:5678
   [Install]
   WantedBy=multi-user.target
   ```
   Then: `systemctl enable n8n && systemctl start n8n`
3. n8n runs on `localhost:5678` only — do NOT expose publicly; do not add nginx proxy.
4. Access via SSH tunnel: `ssh -L 5678:localhost:5678 root@178.104.73.239` then open `http://localhost:5678`
5. Create two workflows in n8n UI: Webhook trigger → Send Email (accepted), Webhook trigger → Send Email (declined). Configure SMTP credentials (Brevo / Mailgun / Resend — free tier sufficient).
6. Add to `/var/www/marketsquare/.env`:
   ```
   N8N_WEBHOOK_ACCEPT=http://localhost:5678/webhook/<your-accept-uuid>
   N8N_WEBHOOK_DECLINE=http://localhost:5678/webhook/<your-decline-uuid>
   ```

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `systemctl restart marketsquare.service`

**Session 8 deploy notes (actual):**
- Env vars live in `/etc/environment` (not `.env`) — systemd drop-in points there
- n8n installed via Docker (npm global install failed on isolated-vm native build)
- n8n Docker command: `docker run -d --name n8n --restart unless-stopped -p 127.0.0.1:5678:5678 -v n8n_data:/home/node/.n8n docker.n8n.io/n8nio/n8n`
- Access n8n UI via SSH tunnel: `ssh -L 5678:localhost:5678 root@178.104.73.239`
- N8N_WEBHOOK_ACCEPT and N8N_WEBHOOK_DECLINE confirmed live ✅
- HETZNER_S3_ACCESS_KEY and HETZNER_S3_SECRET_KEY still to be added via `nano /etc/environment` ⚠️

---

## Session 8 · 2 April 2026 · Task 3 — Hetzner Object Storage photo migration (BEA)

Added S3-compatible photo storage to the BEA with graceful local-disk fallback. Four new env vars — `HETZNER_S3_ENDPOINT`, `HETZNER_S3_BUCKET`, `HETZNER_S3_ACCESS_KEY`, `HETZNER_S3_SECRET_KEY` — are read at startup. If any are missing the BEA logs one warning and continues using local `/media` (existing behaviour unchanged). When all four are set, `boto3` client is initialised at startup and `POST /listings/photo` uploads the compressed medium JPEG to S3 (key pattern: `media/{uuid}_{filename}`), sets `ACL=public-read`, and returns the S3 public URL as both `thumb_url` and `medium_url` (Hetzner does not auto-generate thumbnails — same URL for now). New admin endpoint `POST /admin/migrate-photos` (API-key auth) scans all listings with local `/media/` paths, uploads each file (thumb + medium separately) to S3, and updates the DB rows in place. Returns `{"migrated": N, "failed": M, "skipped": K}`. Idempotent — skips rows already pointing to an S3 URL. Never deletes local files. `boto3` added to `requirements.txt`.

**Deploy:**
1. Add to `/var/www/marketsquare/.env`:
   ```
   HETZNER_S3_ENDPOINT=https://<your-region>.your-objectstorage.com
   HETZNER_S3_BUCKET=<your-bucket-name>
   HETZNER_S3_ACCESS_KEY=<your-access-key>
   HETZNER_S3_SECRET_KEY=<your-secret-key>
   ```
2. `/var/www/marketsquare/venv/bin/pip install -r requirements.txt` (installs `boto3` — use venv pip, not system pip)
3. `scp requirements.txt root@178.104.73.239:/var/www/marketsquare/requirements.txt`
4. `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py`
5. `systemctl restart marketsquare.service`
6. Once running: `curl -X POST https://trustsquare.co/admin/migrate-photos -H "X-Api-Key: ms_mk_2026_pretoria_admin"` to migrate existing local photos to S3.

---

## Session 8 · 2 April 2026 · Task 5 — GeoNames config guard (BEA)

The `_fetch_geonames_suburbs` background task already checked for `GEONAMES_USERNAME` via `os.getenv()` (added in Session 7 Task 6). Updated the silent return to emit a `WARNING` log: `"GEONAMES_USERNAME not set in .env — suburb auto-seed skipped for city {city_name}"`. No other logic changes. To enable suburb auto-seeding for new cities, register free at geonames.org and add `GEONAMES_USERNAME=<your_username>` to `/var/www/marketsquare/.env`, then `systemctl restart marketsquare.service`.

**Deploy:** `scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py` then `systemctl restart marketsquare.service`

---

## Session 9 · 3 April 2026

Hetzner Object Storage fully activated: `HETZNER_S3_ACCESS_KEY` and `HETZNER_S3_SECRET_KEY` added to `/etc/environment`, BEA restarted, and the INFO log confirming S3 initialisation was verified on the server. The `POST /admin/migrate-photos` endpoint was run and returned 0 local photos to migrate — all existing listings had no local `/media/` paths, so new uploads will go directly to S3 from this point forward. `start_marketsquare.bat` was updated to include the correct SCP deploy commands for both `marketsquare.html` and `marketsquare_admin.html` in the end-of-session reminder block, so the deploy commands are visible each time a session is started.

---

STATUS.md + AGENT_BRIEFING.md: replaced stale hardcoded values with live pointers to BEA/admin sources of truth.

---

## Session 10 · 5 April 2026 · Proximity search — lat/lng, distance badges, map view, near-me filter

Full proximity search built across BEA and buyer app. BEA: added lat/lng REAL columns to geo_cities and geo_suburbs; updated seed_geo_za() and _seed_country_from_geonames() to store coordinates from GeoNames data; added _backfill_geo_coords() one-time function that re-downloads ZA.zip and UPDATEs existing rows with lat/lng; added _haversine_km() helper; new GET /geo/nearby endpoint returns suburbs within a configurable radius sorted by distance (bounding-box pre-filter + Haversine); GET /geo/suburbs and /geo/cities now return lat/lng; GET /listings JOINs geo_suburbs for suburb_lat/suburb_lng on each listing. Buyer app: added Leaflet.js 1.9.4 + MarkerCluster CDN; browser Geolocation API detects buyer GPS on startup; distance badges ("2.3 km") shown on listing cards; grid/map view toggle with Leaflet map using OpenStreetMap tiles, clustered listing pins with popups, blue circle for buyer location; "📍 Near me" option in suburb panel calls /geo/nearby (10 km radius), filters listings client-side to matching suburbs; listings sort by distance when GPS is available. Zero-cost tile solution: OpenStreetMap/OpenFreeMap, scalable to self-hosted Protomaps on Hetzner if needed.

---

## Session 11 · 5 April 2026 · Admin city search + duplicate cleanup

Replaced the "Add a new city" form in the admin Cities tab with a search input that filters the cities table by city name or province as you type. Removed POST /geo/cities endpoint from BEA — cities are seeded exclusively from GeoNames, not created manually. The old Add City form had caused a duplicate lowercase "pretoria" (id 101) with 0 suburbs; deactivated on server via UPDATE geo_cities SET active=0 WHERE id=101. Real Pretoria (id 47) has 140 suburbs.
