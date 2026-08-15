## 2026-08-14 — BORDERLESS-COUNT-1 + SPEC-PROVENANCE-1: the tester queue cleared to zero new

**BORDERLESS-COUNT-1 (TS-0032 Maun, TS-0033 Sydney) — a tile that promised what its page would not show.**
Two testers at opposite ends of the world filed the same fault: pick a city, the Adventures tile
reads "1 listing" / "2 listings", tap it and the page shows every adventure on the platform —
"it reverts away from Botswana and shows me many adventures."

Neither surface was wrong alone. `renderCatCounts()` filtered EVERY category to `activeCity`,
while `renderAdvGrid()` has no city filter by design — Adventures is deliberately borderless
(the 28 Jun ruling that travel-planning categories are not local to the buyer; COUNTRY-FILTER-1
then made `advCountry=ALL` the default, which exposed the gap rather than causing it). They
disagreed, and the tile was the liar: it counted a set the grid can never show.

Fix: `BORDERLESS_CATS` / `isBorderlessCat()` declared next to `normCat`, and BOTH count branches
(live counts and the placeholder fallback) now skip the city filter for a borderless category and
apply the SAME country predicate the grid uses. Evidence: `scripts/repro_borderless_count.js`
reproduces the testers' exact numbers against the pre-fix file (Sydney tile 2 / grid 6, Maun tile
1 / grid 6, exit 1) and passes against the fixed one (6/6; 2/2 with the picker narrowed to AU,
exit 0). **RG-0078** locks it and re-runs that repro on every ledger pass — including the grid
half, so nobody "fixes" this from the wrong end by pinning Adventures back to the buyer's city.

**SPEC-PROVENANCE-1 (TS-0031, David Jnr, relayed).** He reported the cars pre-final stage added
his vehicle's details wrong and doubted the "AI searches and populates" explanation. He was right
about the mechanism: there is no lookup in that lane — make, model and variant are read off his
photos by vision plus a model prior (CARS-SPEC-1), and the market note is an ungrounded
one-sentence Haiku, so an uncommon variant can come back confidently wrong. The screen asked him
to warrant "I have personally verified every detail above" while saying nothing about where the
details came from — that is how a seller ends up signing for a guess. The attestation block now
states it in place: read from your photos, nothing looked up in a vehicle database, check every
figure against your own papers. **RG-0079** locks it, including that the warranty text stays —
provenance is added alongside the attestation, never instead of it.

Whether to GROUND the cars lane in real vehicle data is a design and cost decision, so it was not
taken by an agent: recorded in BACKLOG.md (14 Aug) with the three options and the fault left
`triaged`, not closed.

**Also:** RG-0065 (migration 018 landed — the maint lane answers on the key alone), RG-0066
(GATE-TRUTH-1 live — a wrong reviewer code says so in words) and RG-0069 (TSL-DBPROOF-1 — the DB
proves itself over anonymous HTTPS) all read "READY TO LOCK" and were promoted to LOCKED as their
own entries instructed. Queue: **0 new** (was 3) — 2 fixed, 1 triaged.
