## 2026-09-02 — GEO-LAUNCH-1: location picker now shows the launch cities, synced from CityLauncher

David: "the cities in the app selections are not updated with what we have started to send emails to."
Probed live: ZA offered 55 GeoNames towns but not Knysna or Mossel Bay (both emailed); US offered
Denver/Colorado (never emailed); DE/NA/MZ/BW/KE showed as countries from the super-listing seeds.

- **One source of truth.** `CityLauncher/data/cities.json` (active|prospect = shown, planned = hidden)
  → `scripts/build_geo_launch_cities.py` → `scripts/geo_launch_cities.json` (37 cities, shipped by manifest).
- **Idempotent server seed every deploy.** `scripts/seed_geo_launch.py --apply` runs as post_deploy step 1c
  (same contract as the super seeds): inserts missing launch cities with coords, flips `geo_*.active`,
  deletes nothing. A city that carries listings is never hidden; regions/countries follow their cities.
- **Picker UX.** `ms.js` skips the Region step when a country has ≤15 active cities (`GEO_REGION_STEP_ABOVE`);
  the city row shows its region as a hint; back goes to Countries when no Region step was shown.
- **Ledger RG-0243 (OPEN → lock after deploy).** Asserts manifest/post_deploy/ms.js wiring, that the shipped
  JSON is not stale against cities.json, and — live through the gate — that every launch city is selectable,
  no country is offered empty, and ZA is no longer the GeoNames dump.
- Dry run on a copy of the live DB: +2 cities, 43 ZA towns hidden, 2 regions hidden. Not yet deployed.
