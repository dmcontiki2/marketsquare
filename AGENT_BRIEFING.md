# MarketSquare · Master Agent Briefing
**Version 1.8 · 17 May 2026**
*Read this document at the start of every Claude Code session. It is the single source of truth for all three agents.*

---

## 1 · What MarketSquare Is

MarketSquare is a **mobile-first local marketplace** connecting buyers with trusted, anonymous sellers. It runs as a single-page web app deployed at **trustsquare.co**.

- No commission. Revenue comes from Tuppence introduction fees + buyer subscriptions only.
- Buyer and seller identities stay hidden until **both parties accept** an introduction.
- Launch city: **Pretoria, South Africa**. Wave 1 cities: New York · London · Sydney (Australia). Berlin removed — replaced by Sydney due to Germany's email marketing laws (UWG/GDPR cold outreach restrictions).
- Launch model (David ruling, 12 Jun 2026 · CC-003): **60 staged prospects per city is the WAVE TRIGGER** — CityLaunch fires the auto-email founding wave at 60 (ACTIVE ≠ LIVE on the dashboard). Cities **launch day-one with zero native listings by design**: the World Heritage layer (332 sites) + demo content carry the browse experience while density builds via waves (~5–7% end-to-end conversion, 3–4 founding sellers/wave — see docs/CITYLAUNCHER_SESSION_4_BREAKDOWN.md) + direct agency onboarding (David/Dave/Maroushka visiting estate-agency contacts; free Agency tier, their existing databases). The old '60 founding sellers = public launch threshold' wording was a doc error, never the design — being purged via CC-003.
- Three categories live: **Property · Tutors · Services** (Services has Technical / Casuals sub-filter). Help Wanted absorbed into Casuals.
- Phase 2 categories planned: **Adventures · Collectors** (not yet built — see PRINCIPLE_REQUIREMENTS.md D7).
- Adventures has two sub-classes: **Experiences** (guided activities: hiking, diving, safaris, etc.) and **Accommodation** (B&B, guesthouses, boutique hotels). Sub-class is declared at listing creation and drives Trust Score credential signals.

**This is a marketplace app, not a game.**

---

## 2 · Core Concepts Every Agent Must Know

### Tuppence (T)
- Introduction currency. **1 Tuppence = USD $2.**
- Only the **buyer** pays, and only **after the seller accepts** the introduction.
- Seller earns zero commission — they simply get connected.
- **AI Coach Credits** are a separate balance, never merged with intro Tuppence. Tiered packs: 5T=40 uses · 10T=100 uses · 25T=320 uses. Purchased via the same Paystack flow with `ai_pack_sessions` metadata.

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

Score is earned across three groups: Universal (ID verification, profile, referrals — max 30), Category Credentials (qualifications, registrations, per-category signals — max 40), and Platform Track Record (intros, reliability, tenure — max 30). Full criteria: `TRUST_SCORE_CRITERIA.md`. Codex amendment: `TRUST_SCORE_CODEX_AMENDMENT.md`.

**Local Market base score:** local_market sellers start at 40 pts automatically (Established tier immediately). Credentials earned on top push the score higher. Penalties can pull below 40.

**Declaration system (Session 36):** Declarable signals have `declaration_points` (80%) and `evidence_points` (20%). Seller submits free-text declaration via `POST /users/{email}/declare` → awarded declaration_points immediately, credential set to `declared` status. Uploading evidence later upgrades `declared` → `earned` and awards evidence_points. Audit trail stored in `user_declarations` table. Four LM signals currently declarable: `assoc_role` (12/3), `provincial_role` (8/2), `prof_body_2` (5/1), `experience_5yr` (2/1).

Introduction penalties (A3/A8): seller ignores intro → Trust Score −5 (Commitment) or −3 (Queue). Listing unpauses automatically. Seller declines → no penalty. Tuppence is NEVER deducted as punishment — see A8.
Complaint penalties: −8/−5/−3/−2/−1 per complaint (diminishing), capped at −22 total. Bad referral confirmed: −10 pts + reversal of referral pts.

### Anonymity Rule
Seller name and email are **never shown to buyers**. Identity is only revealed after mutual introduction acceptance. The seller CV shows an emoji avatar and anonymous stats until then.

---

## 3 · File Map

**Critical: Local filenames carry NO version suffix. Any reference to v8_6b or v1_1 in older docs is outdated — use the names below.**

| Local filename | Serves as (server) | Live URL | Agent owner |
|---|---|---|---|
| `marketsquare.html` | `index.html` | trustsquare.co | Frontend agent |
| `marketsquare_admin.html` | `admin.html` | trustsquare.co/admin.html | Admin agent |
| `bea_main.py` | `main.py` | trustsquare.co:8000 | BEA / Architect agent |
| `Solar_Council_Codex_v4_5.docx` | — | Session upload only | Architect agent |
| `CHANGELOG.md` | — | Project root | All agents append |
| `CLAUDE.md` | — | Project root | Architect agent updates |
| `Cost_Breakdown_GlobalLaunch.xlsx` | — | Project root (upload to Claude Chat) | Architect agent flags changes |

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
**Owns:** Codex (`Solar_Council_Codex_v4_5.docx`), system design, rule arbitration.

Responsibilities:
- Answers rule and design questions for the other two agents using the Codex as source of truth.
- Arbitrates conflicts between Frontend and Admin agents.
- Updates `CLAUDE.md` only for major structural changes.
- Does NOT edit `marketsquare.html` or `marketsquare_admin.html` directly.

### 4b · Frontend Agent
**File:** `agents/frontend/CLAUDE.md`
**Owns:** `marketsquare.html` — the buyer-facing marketplace app.

**File structure (single file, do not restructure):**
```
1. DATA LAYER   — <script id="ms-data">  — listings, sellers, config
2. STYLES       — <style>               — CSS variables and rules
3. UI SCREENS   — <div id="screen-*">  — 12 screens
4. LOGIC        — <script>              — all JS functions
```

**Critical id handling rule:**
BEA listings have string ids ('bea_N'). Always use `findListing(id)` not `LISTINGS[id]`. All onclick handlers that interpolate listing ids must quote them: `openDetail('${l.id}')` not `openDetail(${l.id})`.

**Geo rules:**
- `activeCity` is always `{id, name}` — never a bare string
- `activeSuburb` is `{id, name}` or null
- BEA geo API param is `country` — NOT `country_iso2`

### 4c · Admin Agent
**File:** `agents/admin/CLAUDE.md`
**Owns:** `marketsquare_admin.html` — seller onboarding dashboard (4-step wizard).

City selection uses a **search-filter UI** — there is no Add City form and no POST /geo/cities endpoint. Do not attempt to re-add it.

---

## 5 · Backend API (BEA — version: check GET /health)

**Base URL:** `https://trustsquare.co`
**API key header:** `X-Api-Key: ms_mk_2026_pretoria_admin`

| Method | Endpoint | Auth | Purpose |
|---|---|---|---|
| GET | `/health` | None | Health check — returns current version |
| GET | `/listings?city=Pretoria` | None | Fetch live listings |
| POST | `/listings` | API key | Create listing |
| DELETE | `/listings/{id}` | API key | Delete listing |
| POST | `/listings/photo` | API key | Upload photo → thumb_url + medium_url |
| POST | `/users` | API key | Register seller |
| GET | `/users/{email}` | None | Fetch user |
| DELETE | `/users/{email}` | API key | Delete user |
| POST | `/intros` | None | Buyer submits intro request |
| GET | `/intros` | None | All pending intros |
| GET | `/intros/{listing_id}` | None | Intros for one listing |
| PUT | `/intros/{id}/accept` | API key | Accept intro · charges 1T |
| PUT | `/intros/{id}/decline` | API key | Decline intro |
| POST | `/payment/initialize?tuppence=N&ai_pack_sessions=M` | None | Paystack checkout — M=0 for intro Tuppence, M>0 for AI pack |
| GET | `/payment/verify` | None | Verify payment · credit Tuppence + AI sessions if ai_pack_sessions>0 |
| GET | `/advert-agent/status?email=` | None | AA session balance for seller |
| POST | `/advert-agent/coach` | None | Run AI coach — auto-registers unknown emails |
| POST | `/advert-agent/publish` | None | Submit draft listing + photos (FormData) |
| POST | `/advert-agent/buy-pack?email=&sessions=N` | None | Admin: manually credit AI sessions |
| GET | `/geo/countries` | None | Active countries |
| GET | `/geo/regions?country=ZA` | None | Regions for country |
| GET | `/geo/cities?region_id=N` | None | Cities for region |
| GET | `/geo/cities?country=ZA` | None | All cities for country (includes region_name) |
| GET | `/geo/suburbs?city_id=N` | None | Suburbs for city (includes lat/lng) |
| GET | `/wonders` | None | All Heritage Sites (filterable: ?type=&country=&q=) |
| GET | `/wonders/{id}` | None | Single Heritage Site by id |
| POST | `/listings/{id}/wonders` | Email match | Link up to 5 Heritage Sites to a listing (JSON array of ids) |
| GET | `/listings/{id}/wonders` | None | Full wonder objects linked to a listing |
| GET | `/geo/nearby?lat=X&lng=Y&radius=10` | None | Suburbs within radius (Haversine) |
| POST | `/geo/countries` | API key | Add country + trigger GeoNames seed |
| GET | `/listings/mine?email=` | None | Seller's own listings by email |
| GET | `/listings/{id}` | None | Single listing by ID |
| PUT | `/listings/{id}?email=` | Email match | Update listing — archives version snapshot before saving |
| GET | `/listings/{id}/versions` | API key | Version history metadata for a listing |
| GET | `/listings/{id}/versions/{version_num}` | API key | Full JSON snapshot of a specific version |
| POST | `/users/{email}/photo` | None | Upload profile photo → square-cropped 400×400 JPEG → R2 → photo_url |
| GET | `/tuppence/balance?email=` | None | Current Tuppence balance from transactions table |
| POST | `/dev/credit?email=&tuppence=N&ai_sessions=N` | API key | **Dev-phase only** — seed account with T + AI sessions, no Paystack · **REMOVE BEFORE LAUNCH** |

---

## 6 · Infrastructure

| Component | Detail | Status |
|---|---|---|
| Server | Hetzner **CPX32** · 178.104.73.239 · Ubuntu 24.04 · 4 vCPU · 8 GB RAM · 160 GB NVMe · €15.49/month *(upgraded from CPX22 on 25 May 2026)* | ✅ Live |
| SSH key | ed25519 · ~/.ssh/id_ed25519 (added 6 April 2026) | ✅ Active |
| Domain | trustsquare.co · Cloudflare DNS + DDoS | ✅ Active |
| SSL | Let's Encrypt · expires 21 June 2026 | ✅ Secured |
| nginx | /var/www/marketsquare/ · 20MB upload limit | ✅ Running |
| FastAPI BEA | systemd · auto-restart · version via GET /health | ✅ Running |
| SQLite | WAL mode · 9 tables (5 core + 4 geo) · 7 indexes · `listing_versions` added Session 20 | ✅ Active |
| Redis | Session cache · rate limiting | ✅ Running |
| Photo storage (primary) | Cloudflare R2 (EU) · bucket: marketsquare-media · $0 egress · HETZNER_S3_* in /etc/environment | ✅ Active |
| Photo storage (mirror) | Hetzner local disk · /var/www/marketsquare/media/ · write-to-both from Session 61 · `r2Fallback()` JS failover | ✅ Active |
| Hetzner Volume | Independent block storage · €0.052/GB/month · **on standby** · activate when disk >80% full | 🔜 Standby |
| DB backups | Daily 3 AM cron → R2 backups/ · 14-day retention · /usr/local/bin/backup_dbs_to_r2.py | ✅ Active |
| n8n | Docker container · `docker restart n8n` · UI: SSH tunnel port 5678 | ✅ Running |
| Paystack | Test mode · live pending CIPC registration | 🔜 Pending |
| CityLauncher | /var/www/citylauncher/ · port 8001 · citylauncher.service · nginx /launch/ + /launch-api/ | ✅ Running |

---

## 7 · Operating Rules (All Agents)

1. **Uncertainty** — Make the best guess, implement it, add one-line flag at the end. Never stop mid-task to ask.
2. **Change size** — One feature or one bug fix per task. Complete each part fully before starting the next.
3. **Git commits** — Auto-commit after every completed task with a clear descriptive message. Do not wait for user approval.
4. **Definition of done** — Code works AND a one-paragraph summary is appended to `CHANGELOG.md`. Done means both.
5. **Conflict resolution** — Architect agent arbitrates via Codex. Escalate to David only if Codex cannot resolve.
6. **No large rewrites** — Never rewrite large sections unless explicitly instructed.
7. **Codex first** — Check Codex (`Solar_Council_Codex_v4_5.docx`) before adding any business logic.
8. **Demo-mode wiring (AI-enforced, no human memory)** — Any new FEA feature that calls the BEA API must include a `DEMO_MODE` guard in the same task. Before marking done, verify both branches: demo shows correct data from LISTINGS/SELLERS arrays, live calls the BEA as expected. This is never optional.
9. **Demo data integrity audit (AI-enforced)** — After any change to `LISTINGS` or `SELLERS`, run the audit script (keep a copy at `/tmp/full_audit.py` on the server) before writing CHANGELOG. Audit checks: sellerIdx in correct city range, sellerIdx matches category, currency prefix, trust score 70–96, LM titles present. Zero issues required. Verify all 4 cities, all categories — never just the city shown in the screenshot.

---

## 8 · World Heritage Content Layer (Sessions 57–58, 15 May 2026)

### Architecture
- **wonders.json** — `/var/www/marketsquare/wonders.json` — 35 Heritage Sites (15 National Parks + 20 UNESCO sites). Fields: id, name, type, country, region, photo (Wikimedia Commons CC/PD URL at 1280px), description (600+ chars), history (600+ chars), wikipedia (URL), lat, lon.
- **BEA endpoints** — `GET /wonders`, `GET /wonders/{id}`, `POST /listings/{id}/wonders` (email-auth, max 5, validates ids), `GET /listings/{id}/wonders`.
- **listings table** — `linked_wonders TEXT` column added via startup migration. Stores JSON array of wonder ids.

### FEA (marketsquare.html) components
- **Wonder picker (seller)** — in `screen-edit-listing`, dark-background section `#el-wonder-section`. Search by name/country, link up to 5 wonders, chips show linked wonders. Saved on listing Save via `POST /listings/{id}/wonders`.
- **Detail strip (buyer)** — in listing detail view, `#detail-wonders-strip` — appears when seller has linked wonders. Each card opens the wonder detail screen.
- **Wonder detail screen** — `#screen-wonder-detail` — hero photo (1280px), type badge, name, country/region, description paragraph, "History" heading + history paragraph, Wikipedia link button, back button.
- **Home strip** — `#home-wonders-section` between Featured and For You. All 35 wonders, Africa-first. Country + type filter dropdowns inline with heading. ‹ › scroll arrows (`wondersStripScroll()`).
- **`_wpAllWonders`** — global JS array, populated once by `loadHomeWonders()` from `GET /wonders`.
- **`openWonderDetail(wonderId, returnListingId)`** — async function. Reads from `_wpAllWonders` first; falls back to `GET /wonders/{id}`. Back button returns to listing or home.

### Photo policy (LEGAL — do not change without counsel review)
- All photos sourced from Wikimedia Commons via Wikipedia REST API thumbnail. CC BY, CC BY-SA, or Public Domain only.
- Unsplash or other sources **prohibited** — Unsplash does not permit hotlinking in commercial contexts without API.
- URL format: `https://upload.wikimedia.org/wikipedia/commons/thumb/{hash}/{filename}/1280px-{filename}`.
- Valid Wikimedia thumbnail sizes: 1280px (confirmed working). Do not use 800px, 1200px — these return 400.
- `referrerpolicy="no-referrer"` is required on all wonder `<img>` tags.
- Photo credits must be added to the UI in a future session (counsel requirement — see Patent Amendment doc).

### Regulatory position
- WHCL is non-commercial, non-transactional, informational only.
- Does not trigger FICA, FAIS, Property Practitioners Act, or any additional POPIA obligations.
- EULA v1.1 (15 May 2026) adds Sections 16 (photo licensing + seller accountability) and 17 (regulatory scope + user accountability acknowledgement).
- Patent: Claim 8 (dependent on Claim 1) drafted in `TrustSquare_Patent_Amendment_WorldHeritage_2026-05-15.docx` — awaiting counsel review.
8. **Context management** — Run `/compact` when context starts filling up.
9. **Cost model flag** — Any change affecting infrastructure, pricing, city launch mechanics, subscription tiers, payment processing, or server scaling: append "Cost model impact:" to CHANGELOG.md entry.

---

## 8 · Open Items (updated Session 21)

| Priority | Item | Owner |
|---|---|---|
| 1 | Paystack live mode (pending CIPC registration) | David action |
| 2 | n8n email notifications — buyer emailed on intro accept/decline | Architect / BEA |
| 3 | Seller-facing intro accept/decline email notifications (n8n) | Architect / BEA |
| 4 | Real founding seller content — Maroushka re-listings via admin tool | Maroushka / Admin agent |
| 5 | Tutors & Services edit parity — confirm all structured fields save/display correctly | Frontend agent |
| 6 | **Remove `/dev/credit` endpoint before public launch** | BEA agent |
| 7 | **Remove Dev Tools nav tab from admin app before public launch** | Admin agent |
| 8 | CityLauncher Cowork setup — Principle Requirements + folder framework | In progress |

---

## 9 · What This Project Is NOT

- **Not a game.** No game mechanics, scoring loops, or entertainment UX patterns.
- **Not a multi-AI system inside Claude Code.** All three agents are Claude (Anthropic). Solis is David's persona used in ChatGPT externally.
- **Not open to large refactors.** Single-file HTML architecture. Surgical edits only.
- **Not hardcoded.** No static city/suburb lists, no hardcoded counts or prices. All live data from BEA endpoints.

---

*Updated v1.6: Session 21 — trust_score live from DB (no longer hardcoded to 40); create_listing now saves all 21 fields including structured category data; smart + Sell routing with account picker; price sanitisation preventing AI-suggested text corruption; 20 demo listings seeded under dmcontiki2@gmail.com (10 tutors + 10 services, trust 48–92); category shopfront photos (Property / Tutors / Services) on home screen tiles and as listing card fallbacks. REMOVE /dev/credit + Dev Tools nav before public launch.*

*Updated v1.7: Session 36 — Declaration system: `POST /users/{email}/declare` awards 80% of signal points immediately on free-text declaration; evidence upload awards remaining 20%. `user_declarations` DB table added. Local Market 40-pt base score (Established tier on signup). Stacking signal chains (`_DOC_TYPE_SIGNAL_CHAINS`). Auto-earn for all non-ID docs. AI upload comment (Haiku 4.5). Live Trust Score refresh after declaration or upload. Declaration cards rendered in buyer app Doc Hub. Four LM declarable signals: `assoc_role` (12/3 pts), `provincial_role` (8/2), `prof_body_2` (5/1), `experience_5yr` (2/1). REMOVE /dev/credit + Dev Tools nav before public launch.*
