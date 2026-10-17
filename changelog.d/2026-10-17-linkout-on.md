## 2026-10-17 -- LINKOUT-ON-1: Travelpayouts partner links switched on, server-side only (RUL-236)

David, 17 Oct 2026 07:56 SAST: "Please switch it on", then "yes, create the links".

- **Panel check first (PROBED 07:50 SAST):** Drive shows "not working" with all five features Off; the live index and
  quick.html carry zero Travelpayouts script; no repo page loads one (RG-0025 clean, 139 files). 26 programs Available,
  20 locked behind "stable monthly traffic for at least three consecutive months" plus "site under development".
- **25 real links made** in the Travelpayouts link tool (project Trustsquare, partner 758984): 23 via "Generate link",
  Kiwi.com and GigSky via "Ready-made by brands" (their generic generator refuses them). Every one probed to 302 to the
  brand with 758984 in the tracking parameter. Aviasales keeps its marker deeplink. Registry now has 0 of 26 at None.
- **travelpayouts_partners.py:** `LINKOUT_ON_BY_RULING = True`; `TP_LINKOUT_ENABLED` kept as the kill switch, now read
  from the process env and then the app's .env (systemd does not export .env); exact `*.tpx.lv` short-link hosts added to
  the allowlist (no wildcard) and passed through untouched (no marker/u appended); `/go/partners` returns brand+category
  for drawing (reward rates not exposed). Selftest 11/11.
- **ts_partners.js (new, first-party):** "Plan the rest of your trip" pill + panel on every journey map, grouped and
  colour-coded (flights, transfers, car & bike hire, tours, eSIM, insurance, delayed-flight claims, luggage storage);
  only ever calls our own /go routes; disclosure + "not a travel agency" in the card; silent when the lane is off.
  Added to all 15 adventures maps + scripts/journey_template.html + deploy manifest.
- **QA bot:** OpenAI's server-side policy already rules GET /go/partners and GET /go/partner/{slug} public, so the
  deploy gate does not treat the switch-on as a newly opened route.
- **Ledger:** RG-1026 LOCKED (switch, registry, card, manifest, live list of 26, click-out 302s to klook.tpx.lv).
  AGE-ZERO-1: RG-0182 printed a false FAIL for a fare refreshed today (age_days 0.0 is falsy); the assertion now tests
  for a missing age (`is None`), which is what it always meant.
