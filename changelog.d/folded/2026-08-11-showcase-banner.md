## 2026-08-11 — SHOWCASE-BANNER-1: showcase adverts wear the ★ banner, never the pin (David's ruling)

- David (11 Aug): property, cars, adventures-experiences and stays showcase adverts must
  carry the Super Advert flag. This collided with his 2 Aug ruling (migration 002 removed
  the flag because SUPER-PIN-1 pins flagged rows above REAL sellers in every sort — the
  flag drives banner AND pin). David chose: **banner without the pin.**
- Mechanics: new `listings.showcase` flag (boot column-adder + migration). super_example=1
  gives showcase demos the ★ SUPER ADVERT banner; every sort now excludes showcase rows
  from pinning — server `_sort_map` (all 5 variants + fallback: pin term is
  `super_example*(1-showcase)`) and the ms.js comparator. Real exemplars still pin first;
  real sellers outrank every demo. Detail-page ribbon reads "showcase listing, free for a
  real seller to claim" instead of "the benchmark listing" on showcase rows.
- **migrations/014_showcase_banner.py** marks the live trios (seller LIKE %showcase%,
  printed to the deploy log, sanity-capped, idempotent). Both creator scripts now write
  `super_example=1, showcase=1` so future trios are born correct — the LIST-001 class
  (recurred today as LIST-002, register updated) cannot come back silently: **RG-0052
  LOCKED** asserts the sort exclusion on both surfaces, the mapper field, the creators
  and the migration. Feeds ship the boolean via SELECT * (RG-0045-safe: identity
  blocklist untouched).
