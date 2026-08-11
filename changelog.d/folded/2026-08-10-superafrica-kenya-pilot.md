### SUPER-AFRICA-1 — Kenya (Nairobi) pilot: 3-tier super-advert ladders (10 Aug 2026)
- NEW `scripts/seed_super_ladder_global.py` — seeds 3 supers per (country, category) with evidence-true persona ladders (a/b/c · T60/T80/T92-96). Kenya pilot: 24 listings, 24 personas, researched real KSh prices (Jiji, BuyRentKenya, safari operators, 10 Aug 2026). Fixture-DB rehearsal green: inserts, geo, personas, credentials, country backfill, idempotent rerun.
- NEW `journeys/kenya.json` → `adventures_ke_map.html` (Leaflet, 5 days, 25 stops, RG-0025 clean) + deploy_manifest line. JOURNEY_HIGGSFIELD_PROMPTS.md regenerated (136 prompts / 5 journeys).
- NEW `SUPER_LADDER_PROMPTS.md` via `scripts/make_super_prompt_pack.py` — 114 advert photo prompts generated from the seeder spec (no drift).
- ms.js: KE flag/currency (KSh)/map wired. regression_ledger.py: nairobi CITY_CCY/CITY_COUNTRY + KSh in SYMBOLS.
- waves_policy.json: Nairobi, Cairo, Harare, Luanda, Windhoek, Maputo, Maun added as OPEN markets (unarmed).
- NOT deployed — awaits photos (supervised Higgsfield run) then /tsl.
