## 2026-09-04 — The Genie: proposed, prototyped, ruled, parked (RUL-097 / GENIE-FILTER-1)

David proposed a floating AI "genie" search: tap it, get a circle of 3D category icons, pick one,
get another circle of sub-types, then city, suburb, level, then deeper facets (chess: openings /
middle game / endgame / speed / online). He asked whether it was too complex.

**Built rather than argued.** `GENIE_SEARCH_CONCEPT.html` — both shapes tappable, 812 synthetic
listings across the real seven categories using the real facet names (`subject`/`level`/`mode`/
`area`, `make`/`yr`/`trans`, …), with a live meter reporting taps, full-screen steps and whether
anything on screen is covered. Measured on "find a chess tutor": described wizard = 7 taps,
5 full-screen steps, nothing for sale on screen until the last answer, lands on 1 result; helper
shape = 2-4 taps, 1 full-screen step, listings visible throughout, lands on 12 then 3.

**David's ruling (RUL-097):** *"Your idea is better Claude, and your reasons are valid. The genie
should not cover any of the other selectors. Please write this up as a genie filter to be looked
at again after we have a stable user base."*

**REUSE-BEFORE-RECREATE CATCH — the important half.** A disk check before writing found
`ZOOM_HMI_SPEC.md` (RUL-076, ratified 30 Aug, unbuilt, ledger RG-0221): one question at a time,
true counts, zero-count options removed, singleton auto-collapse, typing as a shortcut through
the funnel. That is the same design. The genie is therefore NOT a new feature and did NOT get its
own spec — it is written up as **section 11 of the Zoom spec**: Zoom's front door and voice. It
contributes exactly two things Zoom lacks — the pre-category circle of seven with true counts
(Zoom opens *inside* a category) and a persona on the existing question sheet. Everything below
the first tap stays section 3. A genie with its own narrowing logic would be a second search
engine and every future facet would be built twice.

**Covering rule (David's, binding):** inline band that takes its own space, never an overlay;
search / category chips / filter / sort / trust / bottom bar stay live and hittable; exactly ONE
full-screen moment (the opening ring, allowed only because nothing is selected yet); the orb
parks where no control lives. This strengthens spec section 5 from "results are never hidden" to
"nothing on screen is hidden — results or controls".

**Cut:** circles below the top level (eight 84px nodes at 378px touch), real 3D models (CSS
gradients give the look with no assets), the city/suburb questions (section 3.3 owns geography).
**Kept automatically:** the chess-depth facets — the gain ranker only asks a facet that splits the
set and auto-collapse skips one with a single answer, so depth appears when stock supports it.

**Deferred to a STOCK trigger, never a calendar date:** Zoom armed in the field (David's act) AND
all seven categories non-zero in a typical user's city AND ~30 days of funnel behaviour to compare
against. A ring showing 0 on four of seven advertises an empty shop. Filed in `BACKLOG.md`'s
deferred list (surfaced in the morning brief).

**Machinery:** RULINGS.md RUL-097; `rulings_check.py` reflection entry (green, 0 FAIL);
RG-0221 scope extended with acceptance criteria 12-15, three new spec needles
("front door, not a second funnel" · "the genie never covers a selector" · "never a calendar
date") and `GENIE_SEARCH_CONCEPT.html` added to the must-survive prototype list — RG-0221 harness
re-run in isolation, 0 FAIL, still PENDING BUILD by design.

**Deliverable:** `Genie Filter — nice.docx` (Professional Navy house style).

**Verified:** `node --check` on the extracted script; jsdom drives both shapes end to end —
ring renders 7 balls with correct counts, chips narrow the grid, a zero-count chip is inert and
toasts instead, the category chips and filter pills still act with the genie band open, the band
is proven non-absolute (`position` is not absolute/fixed), tag removal restores — zero console
errors. `python3 -m py_compile` on both edited scripts. Indexed into `Projects/Visuals`.

**Not done:** nothing wired into `ms.js` / `marketsquare.html` / `bea_main.py`. No flag, no
deploy. This is a decision and a design only.
