## 2026-08-30 — ZOOM: the category view becomes a narrowing funnel (design ratified, RUL-076)

**ZOOM-HMI-1 · design only — nothing shipped, nothing deployed, flag not created yet.**

David asked how to simplify the category UX at scale: "a maximum of 4 boxes to zoom in".
Answer built rather than drafted — two live prototypes over 5 200 synthetic listings, then
ratified: the filter PANEL is replaced by a FUNNEL that asks one question at a time — the facet
with the highest measured information gain — as large tap targets each carrying its true count.
Zero-count options are removed, so a dead end is unreachable. Geography is one chip that deepens.
Typing is a shortcut through the funnel. A saved path is a standing interest — which is what
"For You" becomes: your saved paths run fresh, not a black box.

Measured tap budgets: rental in a named street 3 · gardener in your street 3 · a specific MtG
card 3 · used BMW at mileage and budget 4 · tour 4 / stay 5 / local guide 4 in a destination.

**Three engine rules were found by BUILDING it, and none would have survived a paper design:**
- Information gain ALONE asks incoherent questions ("which model?" before "which make?";
  "budget?" before "rent or buy?"). Facets therefore carry a dependency graph, and dropping a
  parent chip drops its children.
- Geography must never OPEN the funnel — suburb is the highest-entropy field in the data, so raw
  gain made "which part of town?" the first question in all four categories. Suppressed until
  intent exists.
- Geographic DEPTH matches how far a buyer travels for the thing: property and services reach
  STREET, cars SUBURB, collectables CITY only. It asked "which street?" for a trading card.

**Travel (tours / stays / guides) inverts the geometry** and is now a fifth lane in both
prototypes: the user is by definition not local, so geography stops being proximity and becomes
DESTINATION, opening a level higher at country.

Phone build separately verified in a real renderer (headless Chrome, 378×800): the question moves
to a bottom sheet in the thumb zone, results stay visible above, chips scroll on one line, never
more than 6 options, arrival collapses the sheet and gives the screen back. Two bugs the render
caught that logic tests could not — result cards collapsing to 7px slivers (grid rows stretching
instead of sizing to content) and the desktop design notes pushing the whole UI off a phone
screen — both fixed.

Supersedes the unapproved chip-row FEA direction in SEARCH_DIALIN_HMI_DESIGN.docx (6 Jul) for
SEARCH-HMI-1. The 6 Jul SERVER work — same-set facet counts on /listings — is untouched and is
the foundation this builds on.

**David's binding constraint, recorded:** *"I would actually like to see it on the actual app
first, not the live one that is in the field now."* So the build is flag-dark in the REAL app
(default OFF, existing view untouched), viewed locally and then in the gated sandbox RUL-075
already schedules for 30 Oct — shared, not duplicated — and **arming the flag in the field is
David's act.** Build window: first post-launch, riding with the RUL-065 listing-friction batch.

Files: `ZOOM_HMI_SPEC.md` (build spec) · `ZOOM_HMI_PROTOTYPE_2026-08-30.html` ·
`ZOOM_HMI_PHONE_2026-08-30.html` · `zoom_shots/` (rendered evidence) · both prototypes indexed
in `Projects\Visuals` · RULINGS.md RUL-076 · regression ledger RG-0221 (OPEN) ·
scripts/rulings_check.py RUL-076.
