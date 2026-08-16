## 2026-08-16 — Ledger opens: currency model + map canon (RG-0003/0004/0011)

Session split ruled by David (file-disjoint, main session concurrently on RG-0075/0090):
this session took the three items whose files the main session was not touching.

- **RG-0003 (fix shipped, live pass rides the next deploy):** all 243 no-country
  non-Adventures listings in demo_listings.json now carry an explicit country by city
  (London→GB, New York→US, Pretoria→ZA, Sydney→AU). The currency-guess-from-price-string
  era ends at the data model.
- **RG-0004 (fix shipped, live pass rides the next deploy):** the two Pretoria impostors
  were mislabelled CITIES, not countries — demo_stay_4 is the Bazaruto villa (city now
  Vilanculos, MZ), demo_stay_9 is the Sossusvlei lodge (city now Sesriem, NA). Ledger
  CITY_CCY/CITY_COUNTRY extended (Maun/Nairobi pattern).
- **RG-0011 (re-LOCKED):** map filenames match their ISO code — RUL-021: ZA → the 4-layer
  Pilanesberg pilot at adventures_za_map.html (David's product call, Dinokeng supers switch);
  GB → adventures_gb_map.html (uk content at the canon name, gb row added to the deploy
  manifest, old files kept for cached clients).
- **RG-0081 red during the run:** /review/request-link answered 429 — suspected probe-burst
  rate limiting (3 ledger runs this session + main session deploying the gate lane same
  morning). Re-checked after cooldown; see status fragment for the verdict.
