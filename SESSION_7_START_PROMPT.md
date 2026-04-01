# MarketSquare · Session 7 Start Prompt (continued)
# Paste this into Claude Code at the start of the session.

Read AGENT_BRIEFING.md now. It is the single source of truth for this session.

## Status check
Tasks 1–5 are complete (confirmed via git history in Session 7).
The only remaining work is Task 6 — Three-level location hierarchy.

Today's working files:
- marketsquare.html — buyer-facing app (served as index.html)
- marketsquare_admin.html — admin onboarding tool (served as admin.html)
- Solar_Council_Codex_v4_3.docx — canonical rules (upload to session)
- suburbs_seed.json — SA suburb seed data (in project root)

---

## Task 6 — Three-level location hierarchy

Implement a full Country → City → Suburb location hierarchy across the
BEA, buyer app, and admin tool. Complete each part fully before starting
the next.

**Part A — BEA: database and endpoints**
- Add a `suburbs` table to SQLite: `id, name, city, country,
  active (bool), created_at`
- Add a `suburb` field (text) to the `listings` table
- On BEA startup, run a one-time migration: set suburb = "Central" for
  any existing listing where suburb is null
- Seed the suburbs table from `suburbs_seed.json` in the project root
  on first run (skip if already seeded). Each entry has name, city,
  country fields.
- Add `GET /suburbs?city=Pretoria` — returns array of suburb names,
  sorted alphabetically, active only. No auth required.
- Add `GET /cities?country=ZA` — returns array of active city names for
  that country. No auth required.
- Add `GET /cities` — returns all active cities grouped by country.
  No auth required.
- Add `POST /cities` — creates a city record and triggers a background
  job to call GeoNames API (`api.geonames.org/searchJSON?q={city}
  &featureClass=P&country={iso2}`) to fetch and seed suburbs. Auth
  required. Flag that GEONAMES_USERNAME must be added to BEA .env file.
- Update `GET /listings?city=Pretoria` to accept optional
  `&suburb=Elarduspark` filter. If omitted, returns all suburbs.
- Update `POST /listings` to require `suburb` field — reject with 400
  if missing.

**Part B — Admin tool: suburb field and city management**
- In the listing form (Step 3 of onboarding wizard), add a suburb
  dropdown below the city field. Populate it dynamically by calling
  `GET /suburbs?city={selectedCity}` when city is set. Suburb is
  required — disable save button until selected.
- Add a City Management tab to the admin dashboard bottom nav. Shows
  a table of all cities (from `GET /cities`), their country, active
  status, and suburb count. "Add city" button opens a form with city
  name and country (ISO2), submits to `POST /cities`, shows
  "Fetching suburbs..." status until complete.

**Part C — Buyer app: three-level location selector**
- Replace the current single city selector with a three-level
  drill-down bottom sheet: Country → City → Suburb.
- Default: user's local country → user's local city → "All suburbs".
- "All suburbs" is always the first option within any city.
- Tier gating at city level only:
  - Free → locked to local city, can browse all suburbs freely
  - Starter ($5) → can select any city in their country
  - Premium ($15) → can select any city globally
- Recruiting button label shows current scope:
  "Pretoria · All suburbs" or "Pretoria · Elarduspark"
- Founding seller progress bars track at city level only (not suburb).
- Stats strip (Sellers / Listings / Tuppence / Intros) filters to
  selected city scope.
- `loadLiveListings()` passes both `city=` and optionally `suburb=`
  based on selector state.
- Category listing counts (Task 4) also respect suburb filter.

---

## Task 1 — Currency formatting

In both marketsquare.html and marketsquare_admin.html, format all
monetary values as R1,234,456.00 (capital R, no space, comma thousands
separators, two decimal places). Write a shared formatZAR(value) helper
and replace all ad-hoc price display code with calls to it. This applies
to listing prices, deposit amounts, Tuppence wallet balances, and any
other numeric currency field. Do not change how values are stored —
display only.

---

## Task 3 — Photo carousel with swipe support

In marketsquare.html, the listing detail screen currently shows only the
first photo. Fix it so that when a listing has multiple photos the image
area becomes a horizontally swipeable carousel with: left/right arrow
buttons, dot indicators at the bottom, and touch/swipe support for
mobile. Use the medium_url array from the BEA listing object as the
image source list. If only one photo exists, show it statically with no
controls.

---

## Task 4 — Category listing counts (city-scoped)

In marketsquare.html, the Categories section on the home screen shows a
listing count per category. Fix it so the count is derived dynamically
from the live listings array after loadLiveListings() completes,
filtered to the currently active city AND suburb scope. Exclude
placeholders (ids starting with ph_). Use normCat() to normalise
category strings before counting. Re-render the category cards after
live listings load so counts are always accurate.

---

## Task 2 — Structured description editor and renderer

**Part A — Admin tool (marketsquare_admin.html):**
Replace the single free-text description textarea in the listing form
with a structured description editor containing:
- Headline field (single line)
- Tagline field (single line)
- Summary paragraph field (multiline textarea, 3–5 sentences)
- Sections builder — repeatable blocks, each with a Section Heading
  (single line) and bullet points (one per line textarea). Admin can
  add as many sections as needed.

Serialise as JSON into the existing description field when POSTing to
BEA. Format:
{"headline":"...","tagline":"...","summary":"...","sections":
[{"heading":"...","bullets":["...","..."]}]}

**Part B — Buyer app (marketsquare.html):**
Update the listing detail description renderer to detect whether the
description field is a JSON string (starts with {). If yes, parse and
render as:
- <h2> for headline
- <p class="tagline"> in italics for tagline
- <p> for summary
- <h4> per section heading followed by <ul><li> bullet list

If plain text (legacy listings), fall back to existing plain text
rendering. Backward compatible with all existing BEA listings.

---

## Task 5 — City selector tier-gated

Note: Task 5 extends the location selector built in Task 6 Part C.
Complete Task 6 first. Then add tier gating:

- Free tier: city locked to local city (non-interactive). Recruiting
  button is display-only.
- Starter ($5/mo): Recruiting button opens country-scoped city selector
  (all cities in buyer's country from GET /cities?country=).
- Premium ($15/mo): Recruiting button opens global city selector
  (all cities from GET /cities).
- On city change: re-call loadLiveListings(), update progress bars,
  update stats strip, update Recruiting button label.
- Read current user tier from existing plan/subscription state variable.
  If variable does not exist, default all users to Free and add one-line
  flag noting tier state needs wiring when Paystack goes live.
- Add placeholder GET /cities endpoint response if BEA endpoint is not
  yet live: return ["Pretoria"] as fallback.

---

## After all tasks complete

1. Run through the full buyer flow end to end in the browser
2. Run through admin onboarding with a test listing including suburb
   selection and structured description
3. Deploy both files to server:
   scp marketsquare.html root@178.104.73.239:/var/www/marketsquare/index.html
   scp marketsquare_admin.html root@178.104.73.239:/var/www/marketsquare/admin.html
4. Append one paragraph per completed task to CHANGELOG.md
5. Git commit with message: "Session 7: Tasks 1-6 complete"
6. Push to GitHub

---

## Operating rules reminder
- One task at a time, complete fully before starting next
- Use findListing(id) not LISTINGS[id] for BEA listings
- Quote all BEA listing ids in onclick handlers: openDetail('${l.id}')
- Check Codex (Solar_Council_Codex_v4_3.docx) before adding business logic
- Auto-commit after each completed task
- Append to CHANGELOG.md — definition of done requires both working
  code AND changelog entry
