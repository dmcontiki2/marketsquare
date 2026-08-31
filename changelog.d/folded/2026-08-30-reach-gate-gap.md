## 2026-08-30 — REACH-SURFACE-1: the buyer reach gate is enforced on the wishlist feed, not on /listings

David, on the Zoom design: "the local searcher should only see local items and services, for stays
and travel we do allow global but then searchable. Originally the local view was restricted for the
$5 subscriptions, and the $20 subscribers has global view." PROBED against disk:

- **Buyer reach is its own two-tier axis** (PRICING_CANON §2): **Free $0 = local city · Global $5 =
  national + global**. `_buyer_tier()` returns exactly `free` | `global`.
- **The $5/$20 pair is the SELLER slot ladder** — Starter $5 (10 slots, 2T), Pro $20 (30 slots,
  10T). Two different axes; David's recollection merged them. **Global buyer reach costs $5, not
  $20** — corrected against canon, nothing on disk needs changing.
- **Travel and stays are exempt and borderless on any tier** (§2a: adventures, experiences,
  accommodation, tours, heritage) — so "global but searchable" is exactly canon. **Online-mode
  listings are exempt too** (§2b, tutors + online-capable services), which is the same class and
  was not mentioned.
- **The gate is enforced ONLY on `/wishlist/feed`.** `GET /listings` — the endpoint every category
  view uses, and the one Zoom builds on — **takes no buyer identity at all.** Local-only behaviour
  is a client convention: the FEA asks for `activeCity.name` and gets it. `/listings?city=Cape Town`
  answers anyone.

**Why it surfaced now:** the current list view hides the hole because it never offers another city.
Zoom puts geography on screen as a COUNTED QUESTION — the moment it offers "Cape Town · 37" to a
local buyer, either the count is a lie or the buyer taps into something they cannot open. Rule 2
("counts never lie, dead ends unreachable") breaks. The funnel does not create the gap; it makes it
impossible to ignore.

**CTO decisions (RUL-037), recorded in ZOOM_HMI_SPEC.md §6.2:**
1. The reach gate moves into `/listings`, server-side from the buyer token, applied INSIDE the same
   filtered set the facet counts come from — never a post-filter. Prerequisite of the Zoom build,
   alongside the `listings.quality_score` column from RANK-SURFACE-1.
2. Geography is tier-shaped: a Free buyer's geography question opens at suburb-within-my-city and
   city is not an askable level; a Global buyer gets city as a level. Travel and online-mode ignore
   this — they are borderless, and the destination funnel IS the "searchable" half David asked for.
3. **Empty and locked are different, and only one is hidden.** A zero-count option is removed. An
   out-of-reach option is real inventory behind a $5 tier, so per the ceiling doctrine (RUL-066
   rung 1) it is shown with its true count and an explicit lock. This makes the funnel the most
   honest upgrade surface in the product — the buyer sees exactly what $5 buys, counted, at the
   moment they want it.
4. Locked-geography taps log as ceiling events (RUL-066 rung 3) — demand telemetry for which
   cities to open next.

Acceptance criteria 10 and 11 added. RG-0221 scope extended to assert both the reach prerequisite
and the locked-vs-empty distinction. No new ruling — RUL-076 covers Zoom, RUL-066 already sets the
ceiling doctrine this applies, and PRICING_CANON §2/§2a/§2b is unchanged and still correct.
