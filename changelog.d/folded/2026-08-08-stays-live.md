## 2026-08-08 — STAYS-SHOWCASE-1 LIVE: the fourth trio exists (OPEN_LOOPS D8 closed)

Migration 009 applied cleanly after the NOT NULL fix. **Adverts 336 / 337 / 338 are live.**
Verified from outside against `/listings`, not from the deploy log:

| id | title | price | price_num | super | country | clone junk |
|----|-------|-------|-----------|-------|---------|-----------|
| 336 | Thatch & Bushveld Safari Lodge · Pilanesberg | R2,450 / night | 2450.0 | 0 | ZA | clean |
| 337 | Jacaranda Boutique Guesthouse · Hartbeespoort | R1,850 / night | 1850.0 | 0 | ZA | clean |
| 338 | Marula Bush Camp · Magaliesberg | R1,450 / night | 1450.0 | 0 | ZA | clean |

Every guard did its job: `super_example=0` so they cannot outrank real sellers under SUPER-PIN-1;
`price_num` correct so price sort and filters are honest; `country=ZA` (RG-0001) and city/country
agreeing (RG-0004); no attestation stamp, no linked wonders; no vehicle, property, tutor or
collector fields carried through; `rental_status='available'` retained from the template by the
new NOT NULL guard. `photo_urls` and `thumb_url` resolve to the live heroes uploaded on the media
lane, so the cards render rather than showing broken images. `is_demo=0`, `listing_status=live`.
Real `listing_lat`/`listing_lng` on every row — the map reads pins from the DB, not hardcoded.

**Deep links wired, both surfaces.**
- `flip_showcase_hrefs.py thatch=336 jacaranda=337 marula=338` — 6 hrefs flipped, 2 per card.
  Asserted after: 0 bare hrefs left, 0 unsplash, each card's id appears exactly twice around its
  own image. The three sibling templates still carry 6 deep links each — the flip touched nothing
  else. The Stays track now matches agency / cars_dealer / tour_guide / travel_agency exactly;
  the 0-cards-vs-3 gap David caught on 2 Aug is closed.
- `adventures_za_map.html`: `STAY_IDS` set to {336, 337, 338}, so each B&B pin's
  "Request introduction · 1T" button now opens its own advert instead of the category fallback.
  Re-asserted after the edit: only script src is `/static/ts_report.js` (RG-0025), no unpkg /
  tp-em / jsdelivr / googleapis, intro still 1T and "20T" absent. Rides the next deploy.

D8 is done: adverts, photos, phone cards, email track and the 4-layer map pilot all exist and are
verifiable live. What remains are ordinary follow-ups, not D8: DW-023 (data endpoints answer 200
anonymously since the Cloudflare rule came off), and the untested question of whether migration
007 halts the chain — 009's own bug turned out to explain the missing adverts, so that theory was
never proven.
