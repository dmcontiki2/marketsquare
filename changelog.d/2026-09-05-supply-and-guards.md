## 2026-09-05 — the wave was starving beside a full pantry (SUPPLY-SERVICES-1, ORG-NAME-1, MAGICLINK-CITY-1, PERSON-ONLY-3, STOPLOSS-DISCOVER-1)

**The number is 0.** Probe A 0, probe B 0, read from the live server. Nothing today could
have moved it; what moved is the machinery that has to move it.

### What was actually wrong

The 05 Sep 00:10 wave reported *"no sendable agency prospects — top up the pool first"* for
**9 of 14 cities** and sent 5 real emails. Yesterday's session read that as a supply shortage
and opened RG-0263 to unlock a scraper API. It was not a supply shortage.

- **SUPPLY-SERVICES-1 (RG-0272).** `Services` — 482 individual service providers, 443 never
  contacted — was in **no city's `category_priority` and missing from `agency_categories`**.
  `city_categories()` intersects those two lists, so the lane was invisible to the planner and
  silently dropped. Adding it to one list alone would have changed nothing, which is how it
  hid. Fixed both. Plan and chokepoint now agree exactly, city by city: **13 of 14 lanes
  sendable, 93 guard-clean individuals, up from 5.**
- **PERSON-ONLY-3 (same entry).** `Services` and `us_university_tutors` are individual-seller
  lanes that were **not** person-only, so the office-desk guard never ran on them. The 00:13
  New York wave really did send 11 emails to `admissions@nyadi.edu`,
  `reception@lallianceny.org`, `gsbgraduate@fordham.edu`, `oareda@cuny.edu` and 7 more
  university front desks, inviting each to publish a personal tutoring listing. Both lanes are
  person-only now. That send cannot be recalled (RUL-073); it can only stop repeating.
- **ORG-NAME-1 (RG-0270).** PERSON-ONLY-1 blocked `teachers_trainers` on 3 Sep pending "the
  person-only scraper filter". Measured today, that condition is **unreachable by an address
  filter**: 1,235 of 1,509 rows (81%) already pass every address-shape guard, 87% of them on
  gmail.com — and **1,194 of those 1,235 are named "… Primary School", "… Secondary School",
  "… College"**. `mdusifo555@gmail.com` is Maduna Primary School. A KZN school's official
  mailbox *is* a personal Gmail account, so the address is a person while the entity is an
  institution. Only 41 rows survive a NAME test. **The block stays** — upheld with the
  measurement written into the policy note so no future session removes it on the strength of
  an address filter — and `_looks_org_name()` now guards Tutors, Services and
  us_university_tutors too, where nobody had looked. Agency lanes untouched (RUL-059).
- **MAGICLINK-CITY-1 (RG-0271).** Three Durban operators and one in Port Elizabeth were each
  rendered an invitation saying `city=Pretoria`. Probed the pool: **133 rows carry a link whose
  city contradicts the row**, all stamped "Pretoria" by the adventures scrapers; 19 already
  mailed, 114 not yet. The app reads `?city=` to pre-fill the first listing, so a Durban dive
  operator was invited to publish in Pretoria. Repaired at the READ like CTA-URL-1 — the row
  wins. name/email/category probed clean (0 of 3,547) and left alone.
- **STOPLOSS-DISCOVER-1 (RG-0273).** `clean_stoploss_cities.bat` named New York, Pretoria and
  Polokwane — the cities latched on 3 Sep, all since released. The four actually latched today
  (Cape Town, Durban, Port Elizabeth, Pietermaritzburg) were not in it, so the designed release
  path ran and released nothing while 21 sendable individuals stayed shut in. It now asks
  `gate_check` which cities are latched. It also carried a waiting prompt while sitting on the
  unattended allowlist, which would have hung the host agent the first time it was queued.

### Restraint, deliberately

**MEASURE-RATE-1.** The supply fix takes the nightly wave from 5 sends to ~93. ONBOARDING_PLAN
Phase 1 says do not open the tap before the click→publish rate is known — we have roughly one
pass through the list. `batch_size` halved 12 → 6 for the measurement week (restore at Phase 3,
18 Sep): **up to 62 genuine individuals on night one across 13 cities**, leaving about a third
of the clean pool unspent. This is a restraint on a lane that just got 19× wider.

### Phase 1 measurement so far

130 apology emails (4 Sep) → 98 opens and 31 click events on the 4th → **2 distinct real
people** → 0 published. No new events on the 5th. Click→publish remains unmeasured; two clicks
is not a sample. The 62 going out tonight are the first wave ever aimed at individuals rather
than office desks and schools, so they are also the first honest test of it.

Ledger: RG-0270, RG-0271, RG-0272, RG-0273 added and green; every locked fix still holding,
18 open unchanged. Rulings check: 0 fail.
