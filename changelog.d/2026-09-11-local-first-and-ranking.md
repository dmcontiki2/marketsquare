## 2026-09-11 — Local-first shelf and the RS/TS/LS order, built across all eight categories

David: *"we dont want geo location complexity, but it should have a starting point and the starting
point should be the users current location... presented data should be from local first sources and
in the absence thereof further out. The listed items should be in order of our three ranking
scores, first the RS, then the TS and then the LS; with the trust-score TS being the only one
displayed. Is this possible for all of the categories?"*

**Yes — and it is built.** RUL-118. All eight categories, verified in a rendered mobile browser.

**Location without geo machinery.** No map, no radius, no permission prompt. The app already passes
`city=` on every listing call, so the profile's city IS the starting point and it costs zero taps.
The prototype seeds it from the phone's own timezone, which needs no permission.

**Local first is a SOURCE rule, the scores are the ORDER inside it** — so the two never fight. The
shelf fills from the user's own suburb, then the rest of the city, then further out, with a band
label on each group, reaching wider only when the local band runs short.

**The three scores, all of which already existed:**
- **LS** — listing quality 0–100, `_import_quality_score()`, works on every category branch.
- **TS** — seller trust 0–100, the Trust Score / VEL ladder, per seller not per category.
- **RS** — `0.5 × LS + 0.5 × TS`, the same 50/50 as `estate_agents.py::_rank_agents`, extended to
  listing level by RANK-SURFACE-1 (30 Aug).

Ordering RS → TS → LS is coherent precisely because RS is built from the other two: equal ranking is
settled by trust first and listing quality second. **Only TS is printed** — a star and a number
coloured by the four canon bands (grey / blue / green / gold). RS and LS never appear on a card.

**Prerequisite named, not hidden:** listing quality is computed per row and is NOT stored, so SQL
cannot `ORDER BY` it. A maintained `listings.quality_score` column is required before the live feed
can do this — already recorded in `ZOOM_HMI_SPEC.md` and the RG-0221 scope. The prototype computes
it in the page.

Verified: all eight categories put the local band first, zero ordering violations against
RS → TS → LS within every band, 18 cards each, and no card prints anything but TS. Console clean.
