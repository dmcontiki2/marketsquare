# MarketSquare · Master Agent Briefing
**Version 1.2 · 1 April 2026**
*Read this document at the start of every Claude Code session. It is the single source of truth for all three agents.*

---

## 1 · What MarketSquare Is

MarketSquare is a **mobile-first local marketplace** connecting buyers with trusted, anonymous sellers. It runs as a single-page web app deployed at **trustsquare.co**.

- No commission. Revenue comes from Tuppence introduction fees only.
- Buyer and seller identities stay hidden until **both parties accept** an introduction.
- Launch city: **Pretoria, South Africa**. Next cities: New York · London · Berlin.
- Public launch threshold: 60 founding sellers (20 per category). Current: 23 / 60.
- Three categories live: **Property · Tutors · Services**. Help Wanted deferred.

**This is a marketplace app, not a game.**

---

## 2 · Core Concepts Every Agent Must Know

### Tuppence (T)
- Introduction currency. **1 Tuppence = USD $2.**
- Only the **buyer** pays, and only **after the seller accepts** the introduction.
- Seller earns zero commission — they simply get connected.

### Introduction Models
| Model | Categories | Behaviour |
|---|---|---|
| **Commitment** | Property | Listing pauses on intro request. One buyer at a time. 48-hour response window. |
| **Soft Queue** | Tutors · Services | Listing stays live. Multiple buyers can queue. 48-hour response window. |

### Trust Score
| Range | Tier | Effect |
|---|---|---|
| 0–39 | New | Visible, no badge |
| 40–69 | Established | Blue badge |
| 70–89 | Trusted | Green badge |
| 90–100 | Highly Trusted | Gold badge + featured priority |

Penalties: seller ignores intro → 1T fee to resubmit (Commitment) or −3 Trust (Queue). Seller declines → 1T to resubmit (Commitment only).

### Anonymity Rule
Seller name and email are **never shown to buyers**. Identity is only revealed after mutual introduction acceptance. The seller CV shows an emoji avatar and anonymous stats until then.

---

## 3 · File Map

| File | Live URL | Agent owner |
|---|---|---|
| `marketsquare.html` | trustsquare.co (served as index.html) | Frontend agent |
| `marketsquare_admin.html` | trustsquare.co/admin.html | Admin agent |
| `bea_main.py` | trustsquare.co:8000 (served as main.py) | BEA / Architect agent |
| `Solar_Council_Codex_v4_3.docx` | Session upload only | Architect agent |
| `CHANGELOG.md` | Project root | All agents append |
| `CLAUDE.md` | Project root | Architect agent updates |
| `Cost_Breakdown_GlobalLaunch.xlsx` | Project root (upload to Claude Chat) | Architect agent flags changes |

All files live in `C:\Users\David\Projects\MarketSquare`.

### Server deployment commands
```
scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
scp bea_main.py root@178.104.73.239:/var/www/marketsquare/main.py
ssh root@178.104.73.239 "systemctl restart marketsquare"
```
Or use `deploy_marketsquare.bat` which does all four steps.

---

## 4 · Three Agents — Lanes and Responsibilities

### 4a · Architect Agent
**File:** `agents/architect/CLAUDE.md`
**Owns:** Codex (`Solar_Council_Codex_v4_1.docx`), system design, rule arbitration.

Responsibilities:
- Answers rule and design questions for the other two agents using the Codex as source of truth.
- Arbitrates conflicts between Frontend and Admin agents.
- Updates `CLAUDE.md` only for major structural changes.
- Does NOT edit `marketsquare_v8_6b.html` or `marketsquare_admin_v1_1.html` directly.

### 4b · Frontend Agent
**File:** `agents/frontend/CLAUDE.md`
**Owns:** `marketsquare.html` — the buyer-facing marketplace app.

**File structure (single file, do not restructure):**
```
1. DATA LAYER   — <script id="ms-data">  — listings, sellers, config
2. STYLES       — <style>               — CSS variables and rules
3. UI SCREENS   — <div id="screen-*">  — 12 screens (see below)
4. LOGIC        — <script>              — all JS functions
```

**The 12 screens:**
- `home` — featured carousel + city progress bar
- `browse` — filterable grid of all listings
- `detail` — single listing detail + intro CTA
- `seller-cv` — anonymous seller profile
- `saved` — buyer's saved listings
- `tuppence` — wallet top-up and transaction history
- `plans` — subscription plan selector
- `onboard` — new seller onboarding wizard (Listing-First flow)
- `publish` — seller publish wizard
- `dashboard` — seller dashboard (accept/decline intros, live stats)
- `cv-edit` — seller CV editing
- `recruit` — referral / recruit screen

**Key functions to know before editing:**
- `loadLiveListings()` — async fetch from BEA `/listings?city=` + activeCity.name, 30-second background refresh
- `loadLiveDash()` — async fetch from BEA `/intros`, populates seller dashboard
- `renderGrid()` — renders listing cards into browse screen
- `renderFeatured()` — renders featured carousel on home (has empty state message)
- `openDetail(id)` — opens listing detail screen
- `openSellerCV(sellerIdx, listingId)` — opens seller CV (blurred until intro accepted)
- `renderDash()` / `renderDashCard(dl)` — renders dashboard cards with accept/decline
- `goTo(name)` — navigates between screens
- `showToast(msg)` — shows snackbar notification
- `updateTuppenceUI()` — refreshes wallet balance display
- `findListing(id)` — safe listing lookup by id value (supports both numeric and 'bea_N' string ids)
- `normCat(raw)` — normalises BEA category strings to CATS keys

**Critical id handling rule:**
BEA listings have string ids ('bea_N'). Always use `findListing(id)` not `LISTINGS[id]`. All onclick handlers that interpolate listing ids must quote them: `openDetail('${l.id}')` not `openDetail(${l.id})`.

**Placeholder listings:**
- ids start with 'ph_' (ph_property, ph_tutors, ph_services)
- paused:true but shown in grid via isPlaceholder check in renderGrid()
- Not counted in results count
- Replaced automatically as real BEA listings load

**Data layer globals (edit in DATA LAYER only, never in Logic):**
- `LISTINGS[]` — placeholder listings only (3 entries). Real listings injected by loadLiveListings()
- `SELLERS[]` — placeholder sellers only (3 entries). Real sellers come from BEA
- `CATS{}` — category config with icon, gradient, model type
- `acceptedIntros` — Set of `"sellerIdx-listingId"` keys for blur reveal
- `dashState` — empty listings array, populated by loadLiveDash()

**Magic link URL format:**
`trustsquare.co?magic=1&name=...&email=...&cat=...&city=...`
Parsed on DOMContentLoaded, routes to onboard screen with fields pre-filled.

**Design tokens (CSS variables):**
```
--navy, --navy-light       dark backgrounds
--accent, --accent-bright  blue (#2a5298, #4d8af0)
--gold, --gold-bg          Property / featured (#d4a843)
--purple, --purple-bg      Queue model (#a371f7)
--green, --green-bg        Trusted badge
--red, --red-bg            Alerts
```

**Phase 2 note:** When live seller count exceeds ~50 listings, the DATA LAYER `<script id="ms-data">` will be replaced by a `loadData()` fetch from Google Sheets API. Do not tightly couple logic to static data.

### 4c · Admin Agent
**File:** `agents/admin/CLAUDE.md`
**Owns:** `marketsquare_admin.html` — seller onboarding dashboard.

**What the admin tool does:**
The admin tool is used by David (founder) to manually onboard sellers. It is a 4-step wizard:
1. **Who is the seller?** — name, email, province, city
2. **What are they selling?** — category selection (Property / Tutors / Services / Help Wanted)
3. **Add listings** — title, price, photos, category-specific fields, commitment model
4. **Review + publish** — sends to BEA, generates magic claim link for seller

**Magic claim link:** After publishing, a unique URL is generated for the seller. The seller taps the link, lands on the onboard screen with name, email and category pre-filled, enters their email, and the listing is claimed. (n8n email automation is pending — currently sent manually.)

**Key JS globals:**
- `sellerData` — `{ name, email, city, geo_city_id }`
- `listingQueue[]` — array of `{ formData, photos, status: 'queued'|'published' }`
- `selectedCat` — current category selection
- `BEA_URL` / `MS_URL` — API base URLs

**Key functions:**
- `goStep(n)` / `goNext()` / `goBack()` — wizard navigation
- `selectCat(cat)` — sets category, updates commitment model display
- `openListingForm()` — shows inline listing form
- `saveListingToQueue()` — validates + adds listing to queue
- `renderListingQueue()` — re-renders queued listing cards
- `startFresh()` — resets all state for next seller

**Photo upload:** Photos POST to BEA `/listings/photo`, returns `thumb_url` + `medium_url`. nginx limit is 20MB per upload. File size is shown on selection; upload is blocked if over limit.

**Commitment models displayed in Step 2:**
- Property → Commitment (listing pauses per intro)
- Tutors / Services → Soft Queue (listing stays live)
- Help Wanted → Soft Queue (helper owns listing)

---

## 5 · Backend API (BEA v1.1.0)

**Base URL:** `https://trustsquare.co`
**API key header:** `X-Api-Key: ms_mk_2026_pretoria_admin`

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | None | Health check |
| GET | `/listings?city=Pretoria` | None | Fetch live listings |
| POST | `/listings` | API key | Create listing |
| DELETE | `/listings/{id}` | API key | Delete listing |
| POST | `/listings/photo` | API key | Upload photo → returns thumb_url + medium_url |
| POST | `/users` | API key | Register seller |
| GET | `/users/{email}` | None | Fetch user |
| DELETE | `/users/{email}` | API key | Delete user |
| POST | `/intros` | None | Buyer submits intro request |
| GET | `/intros` | None | All pending intros |
| GET | `/intros/{listing_id}` | None | Intros for one listing |
| PUT | `/intros/{id}/accept` | API key | Accept intro · charges 1T |
| PUT | `/intros/{id}/decline` | API key | Decline intro |
| POST | `/payment/initialize` | None | Paystack checkout |
| GET | `/payment/verify` | None | Verify payment · credit Tuppence |
| GET | `/geo/countries` | None | Active countries |
| GET | `/geo/regions?country=ZA` | None | Regions for country |
| GET | `/geo/cities?region_id=N` | None | Cities for region |
| GET | `/geo/cities?country=ZA` | None | All cities for country (includes region_name) |
| GET | `/geo/suburbs?city_id=N` | None | Suburbs for city |
| POST | `/geo/countries` | API key | Add country + trigger GeoNames seed |
| POST | `/geo/cities?city=X&region_id=N` | API key | Add city to region |

**Public endpoints:** all GETs + POST `/intros`
**Protected:** all POST · PUT · DELETE (except POST `/intros`)

---

## 6 · Infrastructure

| Component | Detail | Status |
|---|---|---|
| Server | Hetzner CPX22 · 178.104.73.239 · Ubuntu 24.04 | ✅ Live |
| Domain | trustsquare.co · Cloudflare DNS + DDoS | ✅ Active |
| SSL | Let's Encrypt · expires 21 June 2026 | ✅ Secured |
| nginx | Serves from /var/www/marketsquare/ · 20MB upload limit | ✅ Running |
| FastAPI BEA | v1.2.0 · systemd · auto-restart | ✅ Running |
| SQLite | WAL mode · 8 tables (4 core + 4 geo) · 6 indexes | ✅ Active |
| Redis | Session cache · rate limiting | ✅ Running |
| Photo storage | Local /media (Object Storage migration pending) | 🔜 Pending |
| Paystack | Test mode (live mode pending CIPC registration) | 🔜 Pending |

---

## 7 · Operating Rules (All Agents)

These rules apply to every agent without exception:

1. **Uncertainty** — Make the best guess, implement it, add one-line flag at the end. Never stop mid-task to ask.
2. **Change size** — One feature or one bug fix per task. If a change touches more than one file section, complete each part fully before starting the next.
3. **Git commits** — Auto-commit after every completed task with a clear descriptive message. Do not wait for user approval.
4. **Definition of done** — Code works AND a one-paragraph summary is appended to `CHANGELOG.md`. Done means both.
5. **Conflict resolution** — Architect agent arbitrates via Codex. Escalate to David only if Codex cannot resolve.
6. **No large rewrites** — Never rewrite large sections unless explicitly instructed.
7. **Codex first** — Check Codex rules before adding any business logic.
8. **Context management** — Run `/compact` when context starts filling up.
9. **Cost model flag** — After any change that affects infrastructure, pricing, city launch mechanics, wave cascade assumptions, subscription tiers, payment processing, or server scaling: append a "Cost model impact:" line to the CHANGELOG.md entry describing what changed and how it affects the cost model. David will update the xlsx in Claude Chat.

---

## 8 · Open Items for Session 11

| Priority | Item | Owner |
|---|---|---|
| 1 | Paystack live mode (pending CIPC registration) | Pending |
| 2 | n8n email notifications — buyer emailed on intro accept/decline | Architect / BEA |
| 3 | Hetzner Object Storage — migrate photos from local /media | Architect / BEA |
| 4 | Maroushka real listings — re-enter via admin tool | Maroushka / Admin agent |
| 5 | Rename project files — remove Windows duplicate suffixes | David / Claude Code |

---

## 9 · What This Project Is NOT

- **Not a game.** Do not apply game mechanics, scoring loops, or entertainment UX patterns.
- **Not a chatGPT/Grok multi-AI system.** All three Claude Code agents are Claude (Anthropic). Solis is David's persona used in ChatGPT externally — not part of the Claude Code agent setup.
- **Not open to large refactors.** Both HTML files are single-file architectures that work. Surgical edits only.

---

*End of briefing. Append updates to CHANGELOG.md, not here. Update this document only if the agent structure, file map, or core product model changes.*
