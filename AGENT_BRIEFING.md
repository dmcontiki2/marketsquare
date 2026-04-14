# MarketSquare · Master Agent Briefing
**Version 1.3 · 11 April 2026**
*Read this document at the start of every Claude Code session. It is the single source of truth for all three agents.*

---

## 1 · What MarketSquare Is

MarketSquare is a **mobile-first local marketplace** connecting buyers with trusted, anonymous sellers. It runs as a single-page web app deployed at **trustsquare.co**.

- No commission. Revenue comes from Tuppence introduction fees + buyer subscriptions only.
- Buyer and seller identities stay hidden until **both parties accept** an introduction.
- Launch city: **Pretoria, South Africa**. Next cities: New York · London · Berlin.
- Public launch threshold: 60 founding sellers (20 per category). Current count: check trustsquare.co/admin.html or GET /listings?city=Pretoria.
- Three categories live: **Property · Tutors · Services** (Services has Technical / Casuals sub-filter). Help Wanted absorbed into Casuals.
- Phase 2 categories planned: **Adventures · Collectors** (not yet built — see PRINCIPLE_REQUIREMENTS.md D7).

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

**Critical: Local filenames carry NO version suffix. Any reference to v8_6b or v1_1 in older docs is outdated — use the names below.**

| Local filename | Serves as (server) | Live URL | Agent owner |
|---|---|---|---|
| `marketsquare.html` | `index.html` | trustsquare.co | Frontend agent |
| `marketsquare_admin.html` | `admin.html` | trustsquare.co/admin.html | Admin agent |
| `bea_main.py` | `main.py` | trustsquare.co:8000 | BEA / Architect agent |
| `Solar_Council_Codex_v4_4.docx` | — | Session upload only | Architect agent |
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
**Owns:** Codex (`Solar_Council_Codex_v4_4.docx`), system design, rule arbitration.

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
| POST | `/payment/initialize` | None | Paystack checkout |
| GET | `/payment/verify` | None | Verify payment · credit Tuppence |
| GET | `/geo/countries` | None | Active countries |
| GET | `/geo/regions?country=ZA` | None | Regions for country |
| GET | `/geo/cities?region_id=N` | None | Cities for region |
| GET | `/geo/cities?country=ZA` | None | All cities for country (includes region_name) |
| GET | `/geo/suburbs?city_id=N` | None | Suburbs for city (includes lat/lng) |
| GET | `/geo/nearby?lat=X&lng=Y&radius=10` | None | Suburbs within radius (Haversine) |
| POST | `/geo/countries` | API key | Add country + trigger GeoNames seed |

---

## 6 · Infrastructure

| Component | Detail | Status |
|---|---|---|
| Server | Hetzner CPX22 · 178.104.73.239 · Ubuntu 24.04 | ✅ Live |
| SSH key | ed25519 · ~/.ssh/id_ed25519 (added 6 April 2026) | ✅ Active |
| Domain | trustsquare.co · Cloudflare DNS + DDoS | ✅ Active |
| SSL | Let's Encrypt · expires 21 June 2026 | ✅ Secured |
| nginx | /var/www/marketsquare/ · 20MB upload limit | ✅ Running |
| FastAPI BEA | systemd · auto-restart · version via GET /health | ✅ Running |
| SQLite | WAL mode · 8 tables (4 core + 4 geo) · 6 indexes | ✅ Active |
| Redis | Session cache · rate limiting | ✅ Running |
| Photo storage | Cloudflare R2 (EU) · bucket: marketsquare-media · $0 egress · HETZNER_S3_* in /etc/environment | ✅ Active |
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
7. **Codex first** — Check Codex (`Solar_Council_Codex_v4_4.docx`) before adding any business logic.
8. **Context management** — Run `/compact` when context starts filling up.
9. **Cost model flag** — Any change affecting infrastructure, pricing, city launch mechanics, subscription tiers, payment processing, or server scaling: append "Cost model impact:" to CHANGELOG.md entry.

---

## 8 · Open Items for Session 12

| Priority | Item | Owner |
|---|---|---|
| 1 | Fix magic onboarding link (not working for Maroushka + Dave) | Frontend agent |
| 2 | Paystack live mode (pending CIPC registration) | David action |
| 3 | n8n email notifications — buyer emailed on intro accept/decline | Architect / BEA |
| 4 | CityLauncher Cowork setup — Principle Requirements + folder framework | In progress |
| 5 | Real founding seller content — Maroushka re-listings via admin tool | Maroushka / Admin agent |
| 6 | Rename project files — remove Windows duplicate suffixes | David / Claude Code |

---

## 9 · What This Project Is NOT

- **Not a game.** No game mechanics, scoring loops, or entertainment UX patterns.
- **Not a multi-AI system inside Claude Code.** All three agents are Claude (Anthropic). Solis is David's persona used in ChatGPT externally.
- **Not open to large refactors.** Single-file HTML architecture. Surgical edits only.
- **Not hardcoded.** No static city/suburb lists, no hardcoded counts or prices. All live data from BEA endpoints.

---

*End of briefing v1.3. Codex reference corrected to v4.4. File name rule clarified. Infrastructure updated to reflect actual server state. Append updates to CHANGELOG.md, not here.*
