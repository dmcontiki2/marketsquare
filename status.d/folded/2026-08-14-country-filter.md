- **COUNTRY-FILTER-1 (14 Aug 2026) — David's ruling honoured: borderless AND filterable, both.**
  The two were never in tension; they are different layers. Branch C (`bea_main.py`, David 28 Jun)
  still returns every adventure regardless of city, so a Kenyan lodge stays discoverable from
  Pretoria — untouched, no backend change. The picker is now an EXPLICIT narrowing on top. What was
  actually broken: `advCountry` defaulted to `'ZA'` (ms.js:2108), which delivered NEITHER — pinned
  to one country and unfilterable — so South African adventures appeared under every selection.
  Four changes: (1) Kenya and Botswana rows added to the picker (marketsquare.html) — both had
  live listings and no way in; deliberately NOT adding TZ/ZW/UG/RW/ET, which would return empty;
  (2) default is now `ALL` with the tick moved off ZA, so borderless is what you get until you
  choose; (3) `renderGrid()` now applies the country filter to adventures rows — `renderAdvGrid()`
  always did, `renderGrid()` never did, which is why the browse grid ignored the picker entirely;
  (4) the choice persists in `localStorage` (`ms_adv_country`) instead of resetting to ZA on every
  reload. `node --check` green.
- **RG-0073 locks the INVARIANT, not a country list.** Kenya's 24 listings went live with no picker
  row — reachable only under "All countries". Botswana had been in that state since July, with
  `ADV_COUNTRY_FLAGS`/`CURRENCY` carrying both codes while the sheet never gained the rows. Seeder,
  photos, media push and deploy all succeeded; the market was simply unbrowsable. The new entry
  compares the picker against the countries actually present in live `/listings`, so it stays true
  when the NEXT market ships rather than rotting like the hardcoded list it replaces. Passing: 9
  countries with listings, 9 reachable.
- **Stale maint-scope guard repaired (test_tester_intake.py).** It asserted the PRE-ruling scope
  (`/admin/faults` only, count 4) and so failed on correct code, putting **DANGER** on every deploy
  — the same class as DRIFT-CACHEBUST-1: a check written against an implementation detail that
  legitimately moved. Now asserts the scope David actually ruled (RG-0065): `/admin/faults*` PLUS
  `/dashboard/maint`, exact allowlist, count 5 — still strict, anything outside still fails. All 17
  intake guards pass. That verdict should read clean on the next deploy instead of crying wolf.
