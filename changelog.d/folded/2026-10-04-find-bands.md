## 2026-10-04 — FIND-BANDS-1: Quick's Find fills local-first again, on top of FIND-HONOUR-1 (RG-0841, RUL-200(c) amended)

David, after FIND-HONOUR-1 shipped: *"I agree regarding the suburbs and have forgotten what our design intent was - to show
what is close, or to be told which area, or in the quick to just click one with available items in the current vicinity.
Let us then stick to our set up rule with these new fixes ... No visuals should be from the local drive, live should only
operate from the server."*

- **RUL-118 restored inside the new fixes:** the area answer is the FIRST BAND, not a gate. Her area first, then the rest of
  her city under a **Nearby** label, RS -> TS -> LS inside each band. Every other answer stays a gate -- a townhouse to sell
  still never shows under Renting.
- **Honest head:** "Yes -- N on TrustSquare" counts adverts in her area only; with none there but some in the city it says
  "Yes -- N near you" (an existing translated pattern). 'Nearby' added to roles/quick_i18n.json in all five languages.
- **The area chips** keep offering the suburbs that have a fitting live advert (FIND-AREAS-LIVE-1) -- "just click one with
  available items".
- **Pictures:** all 180 picture URLs the live door uses answer 200 from trustsquare.co / R2 -- none from a local drive;
  RG-0841 fails if PH_BASE leaves the server or a file:// / drive path appears.
- **Verified** in headless Chromium before shipping: Menlyn -> "Yes -- 2 near you", both Rietvalleirand townhouses under
  NEARBY; Rietvalleirand -> "Yes -- 2 on TrustSquare"; a flat to rent in Brooklyn -> Brooklyn first, Waterkloof under Nearby.

Cost model impact: none.
