# ZOOM — the narrowing funnel · build spec
**Status: RATIFIED BY DAVID 30 Aug 2026 (RUL-076) · NOT YET BUILT · flag-dark when built**
**Ledger: RG-0221 (OPEN) · Prototypes: `ZOOM_HMI_PROTOTYPE_2026-08-30.html`, `ZOOM_HMI_PHONE_2026-08-30.html`**

> David, 30 Aug: *"This is great Claude, please save it and set this up for our first opportunity
> when we will implement the other changes we have lined up. I like this and would actually like to
> see it on the actual app first, not the live one that is in the field now."*

---

## 1 · What is being replaced, and why

The category view is a **flat list plus a filter panel**. It is honest at 65 listings and
unusable at thousands: the user must know which filters exist and set them one at a time, the
panel has no sense of "where am I", and a control can offer a tick that leads nowhere. The
canonical illustration is the status-filter row David screenshotted on 30 Aug — five controls,
all pre-ticked, every one reading `(0)`.

**A form asks the user to hunt. A funnel asks one question and does the work.**

Zoom replaces the panel with a narrowing funnel: at each step the app asks the **single** facet
that splits the remaining set hardest, as large tap targets each carrying its true count. The
chosen values accumulate as a breadcrumb rail. Nothing else is on screen.

This SUPERSEDES the chip-row design in `SEARCH_DIALIN_HMI_DESIGN.docx` (6 Jul 2026, never
approved) as the FEA direction for SEARCH-HMI-1. The server work that doc describes — Step 1
of the filter engine, live since 6 Jul — is unaffected and is the foundation Zoom builds on.

---

## 2 · The five rules

1. **One question at a time**, chosen by measured information gain — not a hand-ordered wizard.
2. **Every option carries its true count**, computed from the same filtered set as the list.
   **Zero-count options are removed**, so a dead end is unreachable rather than merely discouraged.
3. **Geography is one chip that deepens** — `Pretoria › Menlo Park › 12th Street` — never one
   chip per level.
4. **Typing is a shortcut *through* the funnel**, not a separate search. Text fills the chips so
   the user sees where they landed and can widen from there.
5. **The path is saveable.** A saved path is a standing interest — and that is what "For You"
   should be: your saved paths run fresh, visible and editable, not a black box.

Sixth, implied by all of them: **results stay on screen throughout.** Zoom is not a wizard.

---

## 3 · The engine (all three corrections were found by BUILDING it, not by designing it)

### 3.1 Information gain picks the question
For each askable facet, compute the entropy of the split it would make over the remaining set;
score = normalised entropy × a per-facet weight. Highest score is asked. This is what produces
the "minimum ticks" property David asked for — it is an optimisation, not a UI opinion.

### 3.2 A dependency graph keeps the question COHERENT
Gain alone will happily ask *"which model?"* before *"which make?"*, or *"what is your budget?"*
before *"rent or buy?"* — both mathematically excellent, both nonsense to a human. Every facet
may declare `dep` (parent facet) and optionally `depVal` (parent must hold this value). A facet
is askable only when its parent is answered. **Dropping a parent chip drops its children** —
otherwise the rail lies.

### 3.3 Geography never opens the funnel, and its DEPTH is category-specific
Raw gain makes "which part of town?" the opening question in every category, because suburb is
the highest-entropy field in the data. That is the wrong first question. Geography is suppressed
(×0.18, no bonus) until at least one non-geo facet is chosen, then becomes the strongest
remaining cut (+0.30).

**Depth must match how far a buyer will travel for the thing.** A house *is* a street. A gardener
comes to your street. A car you will drive across town for. A rare card you will drive across the
country for, or have posted.

| Category | Geo depth (`GEO_MAX`) | Starts at (`GEO_START`) | Levels mean |
|---|---|---|---|
| Property | street | city known | City · Suburb · Street |
| Services | street | city known | City · Suburb · Street |
| Cars | suburb | city known | City · Suburb |
| Collectables | city only — never asked | city known | City |
| **Travel** | **area** | **nothing known** | **Country · City/region · Area** |

### 3.4 Travel inverts the geometry
For Property and Services geography means *near me*, and the app already knows the user's city,
so geography opens at suburb. **For tours, stays and guides the user is by definition NOT local:**
geography stops being proximity and becomes **destination**, and starts one level higher — the
country is a real question. Same chip, opposite meaning. This is why `GEO_START` exists.

### 3.5 Stopping and relaxing
- **Arrived** when the remaining set fits a screen (prototype: ≤24) or no question remains. The
  funnel stops asking rather than filling the screen with controls the user no longer needs. A
  "keep narrowing" affordance stays available — arrival is a default, not a wall (RUL-066).
- **Relaxation**: when the set gets thin, compute which single active chip, if dropped, returns
  the most results, and offer exactly that one.

---

## 4 · Facet map (as prototyped — the build may extend, not reorder arbitrarily)

| Category | Question chain (dependencies in brackets) |
|---|---|
| **Property** | Renting or buying? → *(geo: suburb → street)* → kind of place · bedrooms · budget **[dep: mode]** · pets |
| **Services** | What kind of work? → which trade **[dep: group]** → *(geo: suburb → street)* → when · rate band |
| **Collectables** | What do you collect? → which line **[dep: family]** → which piece **[dep: line]** → condition · budget |
| **Cars** | Which make? → *(geo: suburb)* → model **[dep: make]** · new/used · mileage band · budget |
| **Travel** | What are you after? (Tours / Stays / Guides) → lane questions **[depVal]** → *(geo: country → region → area)* → budget **[dep: lane]** |
| — Tours | tour type · duration · private/small group/join-in |
| — Stays | kind of place · how many people |
| — Guides | a guide for what · which language |

**Condition/grade is an AI output from photos, never a seller dropdown** — the tiered-grading
doctrine. The funnel surfaces it as a facet; it does not invite self-grading.

### Measured tap budgets (prototype, 5 200 synthetic listings)
| Journey | Taps | Result |
|---|---|---|
| Rental in a specific street | 3 | 15 |
| A gardener in my street | 3 | 5 |
| A specific MtG card | 3 | 16 |
| Used BMW + mileage + budget | 4 | 2 |
| A tour in a destination | 4 | 20 |
| A stay in a destination | 5 | 9 |
| A local guide in a destination | 4 | 14 |

David's stated budget was "a maximum of 4 boxes". Only Stays exceeds it, and only because a stay
is genuinely located at an area rather than a region.

---

## 5 · Phone is the design target, not an adaptation

| Decision | Reason |
|---|---|
| **The question is a BOTTOM SHEET** | On desktop the question sits above the results. On a phone that puts every tap target at the far end of the screen from the thumb. Options land in the lower ~40%. |
| Options **two per row, ≥56px tall**, count on each | Above the 44px touch minimum; measured 172×56 at 378px width. |
| **Never more than 6 options**, tail folded behind search | A phone must never render a 40-item facet list. |
| Chip rail is **one line, horizontal scroll**, newest scrolled into view | Four wrapped chips eat three lines of a phone screen. |
| Sheet **peeks** (title only) on handle tap | Results are never hidden by the thing that narrows them. |
| On arrival the sheet **collapses to a slim bar** (taps used · matches · widen) | The screen goes back to results. |
| Cut from the phone: rules list, tap budget, watch list; search → one icon; categories → sheet | Four things survive on screen: chips, count, results, question. |

---

## 6 · Server work required

`/listings?facets=1` (bea_main.py, live since 6 Jul) already computes counts **from the same
filtered set as the list**, which is the property rule 2 depends on. It is the right foundation.
What is missing:

1. **A next-facet ranker.** New response section (or `?next=1`) returning, for the current filter
   state, the ranked askable facets with their option counts. Entropy + weight + dependency +
   geo rules live SERVER-side so the client never needs the full candidate set.
2. **Facets that do not exist yet.** Today's block covers makes, years, trust bands, service
   types and price. Zoom additionally needs: property `mode`/type/beds, geography at
   suburb/street, car condition and mileage bands, collectable family/line/item/grade, and the
   whole travel lane (lane, tour type, duration, group, stay type, sleeps, expertise, language).
   Several of these are not columns on `listings` today — **schema work is part of this build,
   and it overlaps the structured-facets track.**
3. **Zero-count suppression is a server guarantee**, not a client filter.
4. **RESULT ORDER = THE RANKING SCORE, applied at LISTING level.** *(added 30 Aug after
   David's question — see §6.1 below.)*
5. **Saved paths (Watches)** — persistence + the "For You = your saved paths, run fresh" read.
   This is also the natural feed for the demand loop (search-miss → prospect match).

### 6.1 · Result order — the Ranking Score gap (PROBED 30 Aug 2026)

David asked whether properties are always ranked by the Ranking Score. **They are not**, and the
gap is real rather than a prototype omission.

**What is true on disk:**

- The Ranking Score is `round(0.5 * avg_listing_quality + 0.5 * trust_score, 1)`
  (`estate_agents.py::_rank_agents`) — a **straight 50/50, no further divide**. Its own
  self-description: *"0.5 x avg live-listing quality (0-100) + 0.5 x trust score (0-100). Listing
  quality never weighs less than half."* Asserted by `test_estate_agents.py` for three verticals
  (79.0 property · 75.0 cars · 73.0 travel).
- It **did** generalise beyond estate agencies: `VERTICALS` now carries **seven** —
  property, cars, travel, collector, institution, service_company, placement.
- **But it ranks AGENTS, not listings.** It orders `agent_profiles` for `/agents/nearby`
  (suburb match first, then rank). Nothing in the listing feed consults it.
- **Listings** are ordered by `_sort_map` in `bea_main.py`: default *newest*; options
  *price_asc / price_desc / trust*; and *smart* = **trust 60% + freshness 40%** — with
  **no listing-quality term at all**. `super_example` exemplars stay pinned first (SUPER-PIN-1,
  David 20 Jul) in every variant.

**Consequence:** the method meant to promote listing quality and trust does not touch the
results a buyer actually browses. A seller can lift their listing quality and see no movement in
the only place it would be felt.

**CTO decision (RUL-037), executing David's stated intent rather than re-asking him:** Zoom's
default result order becomes the **Ranking Score at listing level** — `0.5 x listing quality +
0.5 x seller trust` — the same 50/50 as the agent formula, so one method governs both surfaces.
Freshness drops from a 40% headline dial to a tiebreak. `super_example` pinning is unchanged
(SUPER-PIN-1 stands). Both prototypes now sort this way and print the score on each card.

**Build blocker this creates, named not hidden:** listing quality is computed per row today
(`_import_quality_score`), **not stored** — so SQL cannot order by it. A maintained
`quality_score` column on `listings` (written on create/edit, backfilled once) is a prerequisite
of the Zoom result order, and belongs with the §6.2 schema work.

### 6.2 · Reach — the funnel must count only what the viewer can actually see (PROBED 30 Aug 2026)

David: *"the local searcher should only see local items and services; for stays and travel we do
allow global but then searchable."* Canon confirms the model — and probing found the enforcement
is not where Zoom needs it.

**What is true on disk:**

- **Buyer reach is its own two-tier axis** (`PRICING_CANON.md` §2): **Free $0 = local city ·
  Global $5 = national + global.** `_buyer_tier()` returns exactly `free` | `global`.
- The **$5 / $20 pair is the SELLER slot ladder** — Starter $5 (10 slots, 2T) and Pro $20
  (30 slots, 10T). Two different axes. *Global buyer reach costs $5, not $20.*
- **Travel and stays are exempt and borderless** on any tier (§2a): adventures, experiences,
  accommodation, tours, heritage. **Online-mode listings are exempt too** (§2b) — an online tutor
  is as usable from Sydney as from Pretoria. Physical categories stay tier-gated: *the Global
  tier's value is reach for the physical world.*
- **The gate is enforced ONLY on `/wishlist/feed`.** `GET /listings` — the endpoint every
  category view and therefore Zoom uses — **takes no buyer identity at all.** No token, no tier.
  Local-only behaviour is a client convention: the FEA asks for `activeCity.name` and gets it.
  Anyone may call `/listings?city=Cape%20Town` directly.

**Why this matters more for Zoom than for the current list:** the funnel puts geography on screen
as a *question with counts*. The moment it offers "Cape Town · 37" to a Free buyer, either the
count is a lie or the buyer taps into something they cannot see — rule 2 breaks. The present list
view hides the hole because it never offers another city; the funnel would expose it immediately.

**CTO decisions (RUL-037):**

1. **The reach gate moves into `/listings`**, server-side from the buyer token, applied *inside*
   the same filtered set the facet counts come from — never as a post-filter. Prerequisite of
   the Zoom build, alongside the `quality_score` column.
2. **Geography is tier-shaped.** For a local (Free) buyer the geography question opens at
   *suburb within my city* and city is not an askable level. For a Global buyer, city becomes a
   level. Travel and online-mode ignore this entirely — they are borderless by §2a/§2b, and the
   destination funnel (§3.4) IS the "global but searchable" mechanism David asked for.
3. **"Empty" and "locked" are different, and only one of them is hidden.** Rule 2 removes
   zero-count options. An out-of-reach option is NOT zero-count — it is real inventory behind a
   $5 tier. Per the ceiling doctrine (RUL-066 rung 1: the rejection and the offer arrive
   together), out-of-reach geography is **shown with its true count and an explicit lock**, never
   silently hidden. That makes the funnel the most honest upgrade surface in the product: the
   buyer sees exactly what $5 buys, counted, at the moment they want it.
4. Every ceiling-hit logs its event (RUL-066 rung 3) — locked-geography taps are demand telemetry
   for which cities to open next.

---

## 7 · How it gets seen — DAVID'S CONSTRAINT

> *"I would actually like to see it on the actual app first, not the live one that is in the field now."*

**Binding rule for the build session:**

1. Zoom is built into the **real app code** (`ms.js` / `marketsquare.html` / `bea_main.py`) —
   not a further standalone prototype. The prototypes have done their job.
2. It ships **flag-dark**: default OFF, the existing category view untouched and serving.
3. David sees it **on the actual app before it is armed in the field** — locally on the laptop
   first (the laptop is the design tool, RUL-070), and in the **sandbox/staging environment with
   its own DB copy behind the gate** once that exists. That sandbox is already ruled and
   scheduled by **RUL-075 (I18N_READINESS.md, target Fri 30 Oct 2026)** — Zoom SHARES it. Do not
   build a second preview mechanism.
4. **Arming the flag in the field is David's call**, not the CTO's — it changes what every user
   sees on the front door of every category.
5. Nothing here deploys on its own: a new deployable file needs a line in
   `ops/autodeploy/deploy_manifest.txt` (ONE_DEPLOY). Flag-dark code may ride an ordinary deploy;
   the FLAG does not flip with it.

### Build window
Rides with the **first post-launch build window**, alongside the listing-friction batch approved
under RUL-065 (RG-0205 / RG-0206 / RG-0207 — SF-AIDESC-1, SF-MULTIVISION-1, SF-COACH-ASK-1).
Same window, same discipline, no launch-weekend deploys. Full launch is Mon 1 Sep 2026 (RUL-001).

---

## 8 · Acceptance criteria (what RG-0221 will assert when it is built)

1. No option is ever rendered with a count of 0.
2. Counts come from the same query as the list — a facet count and the result count can never
   disagree.
3. No facet is asked before its `dep` parent is answered; dropping a parent drops its children.
4. Geography is never the first question in any category.
5. "Which street?" is never asked for Collectables; travel geography opens at country.
6. On a viewport ≤ 420px wide: at most 6 options rendered, each ≥ 44px tall, question in the
   lower half, no horizontal page overflow.
7. The four named journeys complete within their measured tap budgets against live data.
8. The flag defaults OFF and the pre-Zoom category view still renders when it is off.
10. Facet counts are reach-scoped: a Free buyer is never offered a count that includes listings
    they cannot open, and travel/online-mode remain borderless on every tier.
11. An out-of-reach option is shown LOCKED with its true count, never hidden; a zero-count option
    is still removed. Empty and locked are distinguishable in the UI.
9. Results are ordered by the Ranking Score (0.5 quality + 0.5 trust), identically to the agent
   list, with `super_example` still pinned first — one ranking method, two surfaces.

---

## 9 · Reserved to David (not CTO calls)

- **Arming the flag in the field** (§7.4).
- **The travel endpoint.** The funnel's natural conclusion for tours/stays/guides is a **plan**,
  not a listing — the Expedition Dossier handed to a partnered agency, and that handoff IS the
  Tuppence introduction. So travel likely wants a fifth state the other categories do not have:
  *arrived → build the dossier*. That is commercial shape, not technical shape.

---

*Written 30 Aug 2026. Prototypes verified in a real renderer (headless Chrome, 378×800) — geometry
measured, not asserted; both files indexed in `Projects\Visuals`.*
