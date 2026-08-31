## 2026-08-30 — RANK-SURFACE-1: the Ranking Score ranks agents, not listings (gap found, closed in the Zoom spec)

David asked whether properties are always ranked by the Ranking Score — "our important method to
promote listing quality and trust score, originally designed for Real Estate Agencies, but since
also for all agencies". PROBED against disk rather than answered from memory. Findings:

- **The formula is a straight 50/50, no further divide.** `estate_agents.py::_rank_agents`:
  `rank = round(0.5 * avg_listing_quality + 0.5 * trust_score, 1)`, self-described as "listing
  quality never weighs less than half" and asserted by `test_estate_agents.py` across three
  verticals (79.0 property · 75.0 cars · 73.0 travel). David's recalled version carried a stray
  extra `/2` (which would total 0.75 weight) — corrected against canon, no change on disk needed.
- **It did generalise beyond estate agencies** — `VERTICALS` now carries seven: property, cars,
  travel, collector, institution, service_company, placement.
- **But it ranks AGENTS, never listings.** It orders `agent_profiles` for `/agents/nearby`.
  The listing feed's `_sort_map` in `bea_main.py` offers newest (default), price, trust, and
  "smart" = trust 60% + freshness 40% — **no listing-quality term anywhere.** `super_example`
  stays pinned first in every variant (SUPER-PIN-1, David 20 Jul).

**Consequence:** the method meant to promote listing quality and trust does not touch the results
a buyer actually browses. A seller can raise their listing quality and see no movement in the one
place it would be felt.

**CTO decision (RUL-037), executing David's stated intent rather than handing the fork back:**
Zoom's default result order becomes the Ranking Score at LISTING level — 0.5 × listing quality +
0.5 × seller trust, the same 50/50 as the agent formula, so one method governs both surfaces.
Freshness drops from a 40% headline dial to a tiebreak; SUPER-PIN-1 pinning is unchanged.

**Prerequisite named, not hidden:** listing quality is computed per row (`_import_quality_score`)
and is NOT stored, so SQL cannot order by it. A maintained `listings.quality_score` column
(written on create/edit, backfilled once) is part of the Zoom build.

Both prototypes updated the same session: results now sort by the Ranking Score and print it on
each card. Verified descending in both builds (97,97,96,95,95,95), zero JS errors.

Recorded in `ZOOM_HMI_SPEC.md` §6.1 + acceptance criterion 9, and in the RG-0221 scope, which now
asserts the ordering rule and the stored-quality prerequisite. No ruling needed — RUL-076 already
covers Zoom and this executes David's stated purpose for the score.
