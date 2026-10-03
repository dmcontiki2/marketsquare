## 2026-10-03 — RUL-198 LICENCE-SHOWN-1: a plain driving licence is shown, not a gate

David's own Delivery rider advert (#473, "Afleweringsryer — Menlyn, Pretoria East") sat behind "Only people you send your link to
can see this listing ... Upload my licence". "this is not the same as the caretakers checks that is legally required ... we just
show his TS as license not verified ... the people shopping for a driver can then still be introduced".

- **Registry:** Driver and Delivery rider lose the licence gate and carry `licence_shown` (scripts/build_role_registry.py SHOWN ->
  roles/role_registry.json -> quick.html SVC_ROLES). Their adverts are public at once (a Delivery rider still passes RUL-115's
  casual check -- one confirmation or an ID check -- like every casual worker).
- **Buyer:** `GET /listings/{id}` carries `licence_unverified: "Driving licence"` until a person has checked it; the app shows
  "Driving licence not verified — it adds nothing to the Trust Score until our team has checked it. You can still ask for an
  introduction." under the Trust Score, and a line in the introduction form. Never a block.
- **Seller:** her Hub card says customers see the listing with "Driving licence not verified", with Upload my licence.
- **Kept as gates:** PrDP-G / PrDP-P (Code 10/14 driver, Taxi / shuttle driver), PSIRA, DoEL, SAQCC (RUL-156).
- **Guides:** "driver" moved from the electrician guide (licence gate) to the plumber guide (no gate); gallery.json regenerated;
  RG-0655 now 17 / 7.
- Ledger RG-0802; rulings_check RUL-198; FEEDBACK F-025.

Cost model impact: none. Schema: none (one registry field).
