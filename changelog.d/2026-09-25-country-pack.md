## 2026-09-25 — Quick: examples follow her country and city (COUNTRY-PACK-1, RUL-170)

David: *"we need to while we have this fixed also fix the other countries for these fixes? Will it be possible?"*
Picture budget chosen: *"Destinations only (~US$7)"*.

Found while checking: every Quick visitor — in every country, and in every ZA city except Pretoria — was offered
Pretoria suburbs and prices in Rand.

- **Country:** ?cc= > Cloudflare's country header (new `geo` in GET /quick/me, read-only, never stored) > phone
  time zone > South Africa. **City:** ?city= > her account > Cloudflare's city > her earlier choice on this phone >
  one "Which city?" tap (skipped where the country has one live city); a "Not in X? Change city" link on WHERE.
- **Per country** (roles/quick_country_packs.json, injected as QPACK): areas for all 43 live cities, currency and
  price bands (cars, collectables, stays, local market), the minimum-wage floor already built (RUL-168), trip
  destinations per kind, example names from one local naming tradition per country, local words
  (bakkie -> ute/pickup, matric -> Year 12/Form 4, body corporate -> strata/HOA ...).
- **Pictures:** 118 destination pictures for the lodge / tour / self-drive lists of NA, BW, MZ, KE, GB, DE, AU, US
  (~US$7, prepaid, RUL-164). Rail and fishing lists show pictures where they overlap, labelled buttons otherwise.
- Languages untouched (RUL-165). "Which city?" and the change-city line added in the five ZA languages.
- Rendered test before shipping: GB Manchester cleaner, KE game lodge, ZA Cape Town, ZA Pretoria unchanged.
- Ledger RG-0482 also compares the pack with the live /cities list, so a new city without areas turns red.

Cost model impact: ~US$7 one-off on the prepaid picture account.
- Fix after the live check (25 Sep 10:35 UTC): a signed-in account city from another country (David's Pretoria account previewing ?cc=KE) set LOC.city behind the pack's back, so the advert would have been filed in Pretoria. The chosen city now always wins at every step, and an account city beats this phone's remembered city.
