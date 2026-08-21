## 2026-08-21 — TRIP-ESSENTIALS-1: the adverts stop being a map and a sentence

David, on the Pilanesberg advert: *"would you plan your holiday with only this available? A map
and a single sentence? No itinerary, no budget, no visa requirements, no safety advice, no
travelling notices, no local taxes, tips etc.?"* — and, pointedly, *"I have actually asked this
similar question before and asked for it to be implemented and then got side tracked."* He had:
the 17 Aug LAYERS-4-1 entry recorded his sequencing call ("maps first, dossier-summary work
second") and the second half never came. RUL-038 + regression ledger RG-0135 are what stop it
being lost a third time.

**Built — "Before you go", under the map on all 13 journeys** (9 country maps + 4 tour maps):
- `trip_essentials.js` — 13 journeys, 440 fact rows, **76% carry a live source URL**, generated
  by `scripts/build_trip_essentials.py` (the curated facts live in the generator; the .js is
  never hand-edited). Itineraries are read straight off `journeys/*.json`, so the written route
  and the map can never drift apart. 136 KB, ~39 KB gzipped.
- Per journey: the itinerary · what it actually costs · entry & documents (per passport, with
  fees and processing times) · health · safety & travel notices · money, tax & tipping · best
  season · connectivity · and a dated **"Check these on the day"** list.
- `ms.js` `tripEssentialsPanel()` renders it; `ms.css` carries only what inline styles cannot do
  (open/closed state, hover, and the print stylesheet).
- **Print / save the brief** expands every section first, so the PDF a traveller hands to an
  agency is the whole dossier — not just the two blocks that happened to be open.

**Placement is part of the fix.** David's ruling the same session: the panel goes BELOW the map,
never above — *"from a readers scanning sweeps we only look at the first bit we see and then move
on, and if what they see isnt an interesting looking map then they will pass by."* RG-0135
asserts the call site sits after the map block, so a later refactor cannot quietly invert it.

**Model constraint honoured (CLAUDE.md, 1 Aug).** All of it is FREE pre-information from an
introductory service. The panel ends by handing the traveller to a travel agency through the
EXISTING introduction flow — no new payment path, no booking, no quote. RG-0135 and the self-test
both fail on copy that implies MarketSquare sells the trip.

**Honesty machinery, because a travel dossier is exactly the thing that rots into fiction:**
every row carries a source; volatile figures (visa fees, park tariffs, advisory levels, tax rates)
are flagged **RE-CHECK** in the UI and repeated in the per-trip verify list; a row quoting a number
with no source and no hedge is a hard FAIL in both `scripts/trip_essentials_selftest.js` and
RG-0135. Where research could not confirm a figure the panel says so — Bazaruto's conservation fee
reads "NOT PUBLISHED — get it in writing from your operator", not a made-up number.

**Facts verified 21 Aug 2026** across three parallel research passes against primary sources.
Things travellers actually get caught by, now on the page: Kenya needs a yellow-fever certificate
to come HOME to South Africa (not to enter Kenya); the Maasai Mara fee steps US$100 → US$200 from
1 Jul; Yellowstone now adds a US$100 per-person non-resident surcharge (the US$250 non-resident
annual pass beats it for two adults doing Yellowstone + Grand Teton); UK tax-free shopping is gone
and South Africans need a full £135 visitor visa, not the ETA; EES went live 10 Apr 2026 and does
apply to visa holders while ETIAS does not apply to South Africans at all; Namibian fuel is
effectively cash-only; Botswana does not take rand; Mozambique ATMs will not take Mastercard;
Bavarian huts are cash and TBE vaccination is a 3-dose series started months ahead; Pilanesberg is
malaria-free (and Smartraveller names its approaches for vehicle crime).

**Ledger RG-0135 is OPEN, correctly** — the only failing assertion is "live /static/trip_essentials.js
is 404". It flips to READY TO LOCK on the next deploy of the `deploy` ref. Full ledger run this
session: every LOCKED fix holding, no regressions. `rulings_check` 38/38 reflected.

**Scope stated honestly:** this covers the 13 super-example Adventures journeys. Stays, guides and
non-super tours are the same class and are NOT yet covered — RG-0135's scope line says so rather
than letting the entry imply the family is done.

Also: `TRIP_ESSENTIALS_PREVIEW.html` (all 13 panels, standalone) indexed into `Visuals`.
Files: trip_essentials.js · scripts/build_trip_essentials.py · scripts/trip_essentials_selftest.js ·
ms.js (v455) · ms.css (v285) · marketsquare.html · ops/autodeploy/deploy_manifest.txt ·
scripts/regression_ledger.py RG-0135 · RULINGS.md RUL-038 · scripts/rulings_check.py.
