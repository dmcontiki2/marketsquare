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

---

## 10 · Tutors lane — nearby institutions and their subjects (David, 1 Sep 2026 · RUL-089)

David's 3 a.m. direction, quoted: tutors need two more components — *"1. To use our already
local geo knowledge to identify the close by teaching institutions and to have them as drill
downs, 2. To have the close by institutions main subjects also as drill downs"* — and each must
cost **a single click, not a selection of many options**.

### The data is already on hand
- DBE register: 3,187 geocoded school addresses (Durban/PMB belt), teachers lane.
- Scraped institutions with coordinate-proven lat/lon (STAYS-GEO-1 discipline).
- Tutors themselves carry lat/lon. Precompute tutor → nearby-institution edges
  (Haversine, radius per settlement density) into two derived facets:
  `near_institution` and `subjects` (an institution's subject profile = DBE phase/curriculum
  data ∪ what tutors near it actually offer).

### How a drill-down becomes ONE click — three devices, all extensions of the existing engine
1. **Ask NEAR, not WHICH.** A "which institution?" list of 12 is the many-options failure.
   The geography chip has already answered *where*; the engine ranks institutions by
   proximity × listing count and asks a question whose top tile is the user's obvious answer:
   "**Near Maritzburg College** · 14" with at most 3 runner-ups. One tap. The long tail lives
   behind the deepening geo chip (rule 3), so an unusual choice is possible but the default
   journey never pays for it.
2. **AUTO-COLLAPSE — the singleton rule (new engine rule 3.6).** When an askable facet has
   exactly ONE non-zero option in the remaining set, it is not asked: the chip is applied
   silently and appears in the rail. A question with one answer is not a question. In a
   suburb with one school this makes the institution drill-down ZERO clicks. (General rule —
   applies to every facet, not only tutors: it can only shorten paths.)
3. **Subjects inherit the answered institution** (`dep: near_institution`). The institution's
   subject profile ranks the tiles; zero-count removed; top 4 shown (Maths/Science/English
   dominate real pools). One tap. If the user skips the institution question, subjects still
   ask — ranked by the whole area instead.

### Facet-map addition (extends §4; engine still orders by gain)
| Category | Question chain |
|---|---|
| **Tutors** | What subject? *(or first, by gain)* → *(geo: suburb)* → near which institution? **[auto-collapse when 1]** → level/exam board **[dep: subject]** |

Tap budget: subject 1 + institution 1 (or 0) + geo chip = **2–3 taps**, inside the 4-box budget.

### Why this is more than UX
The institution is the introduction seam: a school is where tutors and students already
coexist. A buyer who reaches a tutor THROUGH their school's tile has told the seller the
context that matters most — same doctrine as the travel funnel ending in an agency handoff.

### Build placement
Rides the RUL-076 build window (flag-dark, sandbox first, David sees it before the field;
arming is David's act). The edge precompute is a server-side batch job — no live-app touch.
RG-0221's acceptance criteria extend to: singleton auto-collapse proven, institution tile
counts true, zero-count institutions unreachable.

---

## 11 · The Genie — Zoom's front door and its voice (David, 4 Sep 2026 · RUL-097)

David's proposal, quoted: *"The user clicks an AI floating Genie, then he asks 'what would you
like to search?', the background can then become a circle with the 7 categories as 3d icon
representations, then on selecting one, the Genie asks now showing the different type of
properties in a circle of floating 3d representative icons... at any moment the user can click
search, but the genie can delve even further than the level; openings, middle game, end game,
speed chess, personal, online etc. I think this will be too complex for the app."*

He was right that the described shape is too heavy, and right that the instinct behind it is
good. Ruled the same day, after tapping both shapes in `GENIE_SEARCH_CONCEPT.html`:
*"Your idea is better Claude, and your reasons are valid. The genie should not cover any of the
other selectors. Please write this up as a genie filter to be looked at again after we have a
stable user base."*

### 11.1 · What the genie is

**The genie is a front door, not a second funnel.** Everything below the first tap IS Zoom: the
gain ranker picks the question (3.1), the dependency graph keeps it coherent (3.2), geography
behaves per category (3.3/3.4), zero-count options are unreachable (rule 2), a facet with one
answer auto-collapses (3.6), and arrival/relaxation decide when to stop asking (3.5).

This is the whole reason the genie is cheap. **A genie that runs its own narrowing logic is a
second search engine**, permanently out of step with the first one, and every future facet has
to be built twice. That sentence is the one thing that must survive the wait.

### 11.2 · What it adds that Zoom does not have

1. **The pre-category step.** Zoom as specced opens *inside* a category — the user has already
   chosen from the chip row. The genie answers the question that comes before that one: *what is
   even in here?* The circle of seven, each ball carrying its true count in the user's city, is
   the cold-start fix for a marketplace whose seven categories have nothing in common. Seven is
   also the largest number a ring can hold on a phone, which is why the ring stops there.
2. **A persona for the question.** §5 already puts the question in a bottom sheet. The genie
   gives that sheet a face and phrases the facet as a sentence. It is presentation, not logic.

Nothing else. Ordering, counts, depth, stopping and relaxing all come from §3 unchanged.

### 11.3 · DAVID'S RULE — the genie never covers a selector

His words: *"The genie should not cover any of the other selectors."* Made concrete and testable:

1. **The genie band is a row, not a sheet.** It takes its own space in the column and the result
   list shrinks above it. It does not slide over anything, at any height.
2. **Every app control stays live while the genie is working** — search field, category chips,
   filter, sort and trust pills, bottom bar. Tapping one mid-question acts immediately and the
   genie re-asks against the new state.
3. **Exactly one full-screen moment is allowed** in the whole flow: the opening circle of seven,
   and only because nothing has been selected yet, so there is nothing to cover. After a category
   exists, full-screen is forbidden.
4. **The orb parks where no control lives** — the gutter above the bottom bar — and hides itself
   whenever the band or any panel is open. If a control is ever added in that corner, the orb moves.
5. On arrival the band collapses to the slim bar of §5 — still inline, still taking its own space.

This **strengthens** §5's peek rule. "Results are never hidden by the thing that narrows them"
becomes: *nothing on screen is hidden by it — results or controls.* A sheet that peeks is no
longer sufficient.

### 11.4 · What was cut from the original description, and why

| David's original | Call | Reason |
|---|---|---|
| Floating genie you tap to start | **Kept** | One friendly door into search, and the charm of the idea. |
| Circle of the 7 categories | **Kept** | Seven fits a ring; it is the one moment a picture beats a word; it is the step Zoom does not have. |
| A circle at every level below that | **Cut** | A ring holds seven. Tutors have 8 subjects, Services ~10 trades. Measured at 378px: eight 84px nodes on a 110px radius sit 84px apart centre to centre — the labels touch. Below the top level, chips (§5: ≤6 options, ≥44px, tail behind search). |
| Real 3D icons | **Cut** | The look is kept, the technology is not — CSS radial gradient, inset shadows, one specular highlight. No models to ship, no library, no per-subject artwork. |
| Ask city, then suburb | **Cut** | The app knows the city, and §3.3 already handles geography properly — never the opening question, depth per category. Asking again is a wasted screen. |
| Search available at any moment | **Kept, and stronger** | Results are never hidden, so there is no search button to return to. |
| Deeper than level — openings, middle game, endgame, speed chess | **Kept, but automatic** | Not a hand-built extra tier. §3.1 only asks a facet that splits the remaining set, and §3.6 skips a facet with one answer, so chess depth appears by itself once there are enough chess tutors and stays silent when there are not. |

### 11.5 · Measured in the prototype (`GENIE_SEARCH_CONCEPT.html`, 812 synthetic listings)

Journey: find a chess tutor.

| | Rejected wizard | Agreed genie |
|---|---|---|
| Taps | 7 | 2–4 |
| Full-screen steps | 5 | 1 |
| Controls covered while narrowing | all of them | none |
| Listings on screen before the last answer | none | every step |
| Lands on | 1 result | 12, then 3 |

The prototype carries a live meter reporting taps, full-screen steps, and whether anything is
covered — so the rule in 11.3 is demonstrated rather than asserted. jsdom drives both shapes end
to end; the category chips and filter pills are proven to still act with the genie band open.

### 11.6 · Why it waits, and the trigger to look again

David: *"to be looked at again after we have a stable user base."* Recorded as a **stock trigger,
never a calendar date** — the genie's entire value is the counts on those seven balls. A ring
showing 0 on four of seven categories advertises an empty shop to the first person who taps it,
which is worse than no genie at all.

Revisit when **all three** hold:

1. **Zoom is built and armed in the field** (§7.4 — David's act). The genie has nothing to stand
   on until the funnel it fronts is live.
2. **All seven categories return a non-zero count** in a typical user's city.
3. **About 30 days of live funnel behaviour** exists to compare against, so the genie can be
   judged on whether it helped rather than on whether it looked good.

Until then it is not on the roadmap and not in a build window. It sits in `BACKLOG.md`'s deferred
list, and this section is the design of record.

### 11.7 · Build placement and cost

Rides **after** the RUL-076 build window, never inside it — Zoom first, front door second. Built
on the funnel it is an opening screen, a persona and the covering rule over machinery that already
exists. Built as its own path it is the second engine named in 11.1, and the estimate stops being
small. The genie writes into the same facet state the funnel already uses; it never holds its own.

Flag-dark and sandbox-first exactly as §7 requires. Arming is David's act.

### 11.8 · Acceptance criteria (extends §8; RG-0221 asserts these when built)

12. With the genie band open, every control that was hittable before it opened is still hittable,
    and the page's scroll height is unchanged beneath it — the genie never covers a selector.
13. Exactly one full-screen genie step exists, it is the opening category ring, and it is
    unreachable once a category is chosen.
14. Each of the seven category balls shows a count from the same reach-scoped query as the list
    (§6.2), and a category with no reachable listings is dimmed with its offer, never hidden.
15. The genie sets the same facet state as the chip rail; a chip added by the genie is
    indistinguishable from one added by hand, and is removable the same way.

*Written 4 Sep 2026. Prototype `GENIE_SEARCH_CONCEPT.html`, indexed in `Projects\Visuals`.*
