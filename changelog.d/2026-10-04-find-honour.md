## 2026-10-04 — FIND-HONOUR-1: Quick's Find honours every answer, in every category (RG-0817, RUL-200)

David, three screenshots: *"David put this up for sale, and now it is showing as a rental. Please fix it, but fix the
process so that it can't happen ... for the principle as it applies to all products"*; *"David listed this under
Rietvalleirand, and it is being advertised in all suburbs ... use the generic demo photos we generated where there are
no live ones"*; *"the Maroushka live apartments ... appears as a single unit (Brooklyn) but also in all suburbs, while
there was no option for Brooklyn"*.

- **CAUSE (one, not three):** Quick's Find (quick.html drawLookup) turned her FIRST answer into one search word and used
  her area only to choose the city. Every other answer -- to buy or to rent, the area, the price band, the school level,
  the day, the trip length -- was dropped without a word, in all eight doors. Listing 468 (Townhouse, 'To sell',
  Rietvalleirand) therefore answered "Yes" to Renting and to every area; the Brooklyn flats answered every area too.
  The record itself was right all along -- it reads as a sale everywhere.
- **PROCESS FIX:** every Find question is now DECLARED in `FIND_FROM` as a test, 'text' (the existing search word / group /
  role match) or 'ask' (no advert can state it -- urgency, season, rarity). `qFindHonour()` tests the adverts themselves:
  an advert that CONTRADICTS an answer is never shown, one silent on it is not hidden. RG-0817 parses CATS and fails the
  deploy the moment a Find step exists without a declaration, or a declared test is missing (mutation-proven: dropping
  `deal`, adding a new step, bypassing the tests, or the old 20-row fetch each go red).
- **AREA:** by name (suburb or any listed area) or within the area's reach -- 3 km from a suburb on the city's /geo list,
  7-8 km for the districts (Pretoria East, Centurion, Midrand, Sandton). FIND-AREAS-LIVE-1: the area question also offers
  the suburbs where a fitting live advert actually is (Flat + Renting offers Waterkloof and Brooklyn; Townhouse + Buying
  offers Rietvalleirand).
- **KIND:** a property's kind is tested on prop_type, not a word -- "Flat" now finds the Apartment adverts it never found.
- **EMPTY SHELF:** where nothing real fits, three AI EXAMPLE cards on the category's generated photos (prop_townhouse.jpg
  etc.), built from her answers, never tappable as a real advert.
- **WRITE SIDE:** Quick stores 'For Sale' / 'For Rent' (the words Edit, Browse and imports use), not 'To sell' / 'To let'.
- **VERIFIED** in headless Chromium against the live API (`scripts/smoke_harness/verify_quick_find_honour.mjs`): the old
  file failed 8 checks reproducing all three screenshots; the new file passed all 12.

Cost model impact: none (one extra /geo read per city per visit; Find reads 200 rows instead of 20).
