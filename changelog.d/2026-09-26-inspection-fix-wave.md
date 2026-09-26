## 2026-09-26 — Inspection fix wave: the rest of the 25 Sep register closed in both apps (INSPECT-FIX-2)

David, 25 Sep 2026: "please fix the language suggestions you made and also fix all of the bugs … fix the total findings,
and please verify their closures with a feedback of all 266+". This wave carries every remaining item of
`INSPECTION_2026-09-25.html` (266 findings + 16 QA-bot items) that could be closed in code; the per-item closure note for
all 282 is on the board itself (status column) and in `INSPECTION_2026-09-25_closures.json`.

- **Quick** (quick.html = genie/HARNESS.html): the door fits a 360x640 phone and scrolls; '1,500' / '1 500' / '1.500' read
  as R1 500 (AMOUNT-PARSE-1); the saved card is opaque and says each thing once in her language; the WhatsApp note links
  her draft; 'List something else' stays on the same account (quick-02, KEY-ID-HIDE-1); Back returns to her advert from
  the reference and phone-around previews; answers survive a reload (WIP-KEEP-1); city and area choices are kept; the
  first screen downloads only the picture on show and reads the account once (speed); every Quick screen uses whole-
  sentence translations; Sepedi replaces Sesotho in both apps' language lists (a saved Sesotho choice maps to Sepedi).
- **TrustSquare app** (ms.js, marketsquare.html, ms.css): saving an edit before the Terms were accepted now shows the real
  Terms, not the Local Market box (TERMS-GATE-EDIT-1); photos are shrunk one at a time in the seller's own order before
  upload (PHOTO-SMALL-1); the map library and the trip-guide data load only when needed (MAP-LAZY-1, TRIP-LAZY-1);
  Local Market links open their own free page; rentals are 'To Rent' everywhere; the emailed link is a 'sign-in link'
  everywhere; the sell flow no longer claims a draft is saved before it is; fading adverts carry the Keep live button;
  code names and rule numbers are gone from what users read; grammar and spelling pass across the app.
- **Server** (bea_main.py, security_gate.py, route_policy.json): the Listing Coach files the advert under the seller's city
  and keeps her private notes off the public page; a signed-out advert list answers 304 when unchanged (ETag); signed-out
  AI search is capped per address; POST /users needs a sign-in and registers only the signed-in address (qa-16);
  GET /dashboard/summary is admin-only (qa-04); the loopback exemptions on admin routes are gone and the box's own
  automation (deploy purge, sensor, ops sweep, maintenance census, media and dashboard bats) sends the admin key the
  running app holds, read from its own process and never printed (ADMIN-KEY-LOCAL-1). POST /agencies/wave-prep keeps its
  exemption until CityLauncher sends the key (qa-11, OPEN_LOOPS).
- **Afrikaans** (roles/app_i18n_af.json, migration 055, DICTV 4 — I18N-AF-3): Handrat, Laerskool, Nutsman, Verbintenis,
  Die topverkoper, per keer / uitvoering, Oop tou, Uitgelig, Een reël, Alles is welkom; 'AI' throughout (never 'KI');
  checked Afrikaans added for the reworded English so no reader gets a machine translation.
- **Kept, not changed:** 'AI EXAMPLE GENERATED ADVERT' stays word for word (RUL-040, David's own wording); the Terms text
  is untouched (its wording items wait for David, version bump and eula_sync.py).

Regression ledger: RG-0495 (introductions follow the server's gate), RG-0496 (Local Market never charged as a paid
introduction), RG-0497 (an untouched price is never rewritten), RG-0498 (every painted field output-encoded, run against
hostile records), RG-0499 (the Afrikaans corrections, OPEN until checked live), RG-0500 (Quick amounts); RG-0383 and
RG-0400 re-aimed at the new code shape and proven red-on-break; RG-0167 honestly REOPENED — it was green only because a
user-facing tooltip carried its code name, and the agent's own Pro-seat purchase lane has never been built.

Proof before shipping: `node --check` / `py_compile` / JSON parse on every changed file; quick.html byte-identical to
genie/HARNESS.html; rulings check (no new FAIL; the three FAILs are files that live outside git); full ledger run on the
merged tree versus the same tree without this wave — identical board except RG-0167 (reopened on purpose); a local browser
run with every write faked (introduction button, Local Market link, Back after Sell, Quick door at 360x640, '1,500', the
saved card). Live check after the deploy is recorded in OPEN_LOOPS L19.
