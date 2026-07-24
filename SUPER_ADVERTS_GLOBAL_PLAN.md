# Global Super Adverts — Prep Notes (homework for tomorrow)
Date: 24 Jul 2026 · Status: PLAN, not built · Base = the ZA Adventures pass shipped/armed today.

## 0) Golden rule first — STANDING_ORDERS SO-1
Every place David named is a REAL, famous, protected / trademarked site:
- **Yellowstone** — US National Park Service, protected name.
- **Stonehenge** — UK, English Heritage; ticketed, protected, restricted imagery.
- **Great Barrier Reef** — AUS Marine Park Authority; World Heritage.
- (**Uluru**, if used — sacred Anangu land; imagery is culturally restricted. Extra care.)

Per SO-1 these cannot go on an exemplar as-is. Two safe routes per item:
  (a) **Genericise** to an unmistakably-illustrative equivalent (default for the build), or
  (b) **Flag** it so David approaches the real body/operator to take the LEAD advert
      (they bring the real name + a real, accurate map) — the upsell path.

## 1) Launch countries (confirm)
ZA (done) · US · UK · AUS · **4th? — David wrote "Canadian stay" under US; is CA the 4th, or a US typo?**
Per country: currency, units (km/mi, °C/°F), price bands, date/format, spelling (colour/color).

## 2) The matrix — one super-advert set per country, across categories
Categories in play: Adventures (experience + accommodation), Cars, Property, Tutors,
Local Market, Collectors, Services.

Genericised Adventures concepts (safe versions of David's ideas):
| Country | Experience (drive/activity)                         | Accommodation                          |
|--------|------------------------------------------------------|----------------------------------------|
| US     | "a world-famous geyser & wildlife park drive"        | "a lakeside timber lodge with hot-spring deck" |
| UK     | "a Highland walk to an ancient standing-stone circle"| "a whisky-country stone cottage stay"  |
| AUS    | "a world-heritage coral-reef dive"                   | "an over-water reef eco-lodge"         |
Each country also gets Cars / Property / Tutor / Local / Collectors exemplars in the same house style.

## 3) What we LIFT wholesale from today (no reinvention)
- Higgsfield **Nano Banana Pro + reference-image consistency** pipeline (per-country vehicle/lodge refs).
- `assets/super/` naming convention + deploy **step 3d** hash-sync.
- **Idempotent, flag-guarded one-shot** DB script pattern (photos + text) — one hook per batch.
- The **self-contained illustrative map** component — parameterise pins/route/labels per country;
  keep the deliberate offset + "illustrative, not surveyed" framing.
- **SO-1 safety pass** baked in from the first draft, not bolted on.
- **Gesture-handling** map (two-finger on mobile) — already solved, reused.

## 4) Rough size / cost
~7 categories × 4 countries ≈ 28 exemplars; Adventures carry ~8 photos, others 3–6.
Order-of-magnitude ~120–160 images. Batch under the Higgsfield unlimited window if it's still open.

## 5) Open questions for David (tomorrow)
1. 4th country (CA?).  2. Genericise-by-default vs flag-for-outreach, per item?
3. All categories per country, or a subset to start?  4. Currency/units/price bands.
5. One shared map per country, or per-listing?  6. Photo budget / unlimited window timing.
