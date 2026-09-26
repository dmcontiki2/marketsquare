## 2026-09-26 — The last open security item closed; two slips from the morning's deploy fixed (INSPECT-FIX-6)

- **QA-11 — POST /agencies/wave-prep is admin-only, with no loopback pass.** It mints one-click sign-in links for any
  address, and it kept a loopback exemption only because CityLauncher called it over 127.0.0.1 with the public app key.
  CityLauncher's `mint_agency_console_link` now sends `X-Admin-Key` — the running app's key, which the nightly wave
  (root) reads from the service secrets file; proven equal to the app's key by hash on the box, never printed. The
  exemption and the handler's `_local_caller` branch are gone (route_policy.json, bea_main.py). CityLauncher's
  emailer.py was shipped to the box on its own (the rest of that folder's uncommitted work was already byte-identical
  to the server), with a backup beside it. Stranger test PASS on the new tree (320 routes).
- **CARD-WORDS-3** — the morning's CARD-WORDS-2 put 'Free forever' into the free plan's description, which the plan
  card already prints first, so the card read 'Free forever · Free forever · no card needed' for about an hour. The
  description is 'no card needed'; the subscription sheet's '2 listing slots · no card needed' carries checked
  Afrikaans and Claude's isiZulu, isiXhosa and Sepedi (migration 059).
- **XH-CONCORD-1** — Quick's isiXhosa read 'Nantsi isibhengezo sakho'; *isibhengezo* is class 7, so it is
  **'Nasi isibhengezo sakho'** (the app already had it right). No other class-7/class-9 slip in either dictionary.

Ledger: RG-0506 (wave-prep answers only the admin key; CityLauncher sends it and never logs it) — red on the deployed
tree, on the loopback branch put back, on CityLauncher without the header and on a logged key; green on the real files.
RG-0503 now also catches the doubled free-plan line (red on the morning's ms.js).
