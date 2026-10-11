## 2026-10-11 — REACH-NATIONAL-1 (RUL-220): a free 'Nationwide' switch on every advert; tier cascade recorded (RUL-221)

David, 11 Oct 2026 (the Bee Lady ships and travels ZA-wide): reach follows what the seller does, not what she pays.
- listings.reach (NULL/'local' = her city; 'national' = every city of her own country). Migration in init (ALTER TABLE).
- GET /listings branch A, _zoom_candidates_raw and GET /local-market/listings include nationwide adverts of the buyer's
  country (UPPER(COALESCE(country,'ZA'))). POST /listings, POST /local-market/listings and PUT /listings accept `reach`
  (normalised by _norm_reach).
- ms.js: the seller's own card carries one button -- '📍 My city only' / '🌍 Nationwide ✓' (msReachButton,
  msToggleReach -> PUT reach); the advert detail shows '· Nationwide'.
- Paid multi-city 402 text now says the paid lane is for reach beyond her own country; in-country reach is the free switch.
- RULINGS.md RUL-220 (switch) + RUL-221 (tier cascade: new functions at $20, previous $20 features step down to $5,
  e.g. PA -> $5 when super-PA lands); PRICING_CANON.md §2e.
- Ledger RG-0956 (LOCKED). RG-0954 duplicate from the Goal run 35 merge renumbered: AI-PROPS-1 is RG-0955.
