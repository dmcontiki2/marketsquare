## CityLauncher brought up to the app — QUICK-LINK-1 + EMPLOYER-HARVEST-1 (25 Sep 2026)

David: *"the CityLauncher has fallen behind with our design improvements… please check the app
against our latest changes and update the app as well."* It had fallen behind by a whole business
model, not by a few templates.

**What was measured first.** The 6,748-row prospect list is entirely businesses that list
themselves — sports clubs, teachers, outfitters, estate agents, tutors, car dealers — and carries
**zero rows of any employer kind**, so `services_casuals_outreach.html` had never been sent to
anybody. Every letter posted a bare `https://trustsquare.co/q/homehelp`: the pre-RUL-159 door name,
no role, no language, no source tag. The emailer had **no** language handling at all while the door
takes `?lang=` and the WhatsApp greeting already used all five SA languages. 4,672 prospects carry a
phone number and every `channel` row still reads `email`.

- **QUICK-LINK-1 (RG-0490).** New `CityLauncher/emailer/quick_door.py` builds the link the door
  actually understands, reading MarketSquare's own `roles/role_registry.json` and
  `roles/lang_countries.json` rather than keeping a second copy. A role attaches only on an exact
  key or English-label match — a fuzzy match would put a welder's picture on a cleaner's letter.
  Only RUL-162 `offered` languages appear; a `reader` language is drafted and unsigned (RUL-160) and
  offering one promises a door that is not open. 14 templates moved to `{{quick_link}}`; the two
  worker letters gained `{{language_row}}`. Measured before and after on all 16 templates for a ZA
  prospect: 14 carried a door link, 14 still do, **0 lost one**. A ZA cleaner now opens
  `/q/services?role=home_cleaner&src=<wave>` plus four language links; a US outfitter stays English
  (RUL-165); a sports club stays doorless **by decision**, named in `DOORLESS`.
  Two traps caught before shipping: `quick_door.py` was not in the deploy manifest and `emailer.py`
  imports it; and the sibling is `MarketSquare` locally but `marketsquare` on the server — **which
  also carries an empty `/var/www/MarketSquare`**, so a single hard-coded spelling resolves to a real
  directory holding none of these files and silently drops every role and language.
- **EMPLOYER-HARVEST-1 (RG-0492).** RUL-150 makes the employer the supply channel and
  MarketSquare's employer door shipped the same morning (`org_enrol.py`), but nothing was looking
  for the organisations. 24 OSM tags derived from the registry's own `employer_kinds`, ordered by
  how many live roles each employs. Probed in Tshwane before being claimed: `tourism=hotel` 85 found
  / 19 email / 37 website; `amenity=restaurant` 300 / 16 / 33; `office=government` 92 / 15 / 50;
  `landuse=industrial` 182 / **1** / 2 — a dud, kept only because `source_health` kills a barren tag
  per-tag. **`household` is the largest employer kind in the registry and is deliberately absent** —
  private homes are not on a map and are never harvested; `EMPLOYER_KINDS_NOT_ON_A_MAP` records that
  as a decision so nobody later "fixes" it by scraping addresses.
- **RG-0344** went red on the way through: the Ops Dashboard's Email Templates preview mirrors the
  sending copies, and 15 had drifted. Rebuilt with `scripts/build_email_templates_page.py`.

Not done, and why: the employer **letter** is unwritten because its CTA must choose between the
agency console and the hours-old enrolment door, and that lane is still being shaped (SO-5).
RG-0391 (the Quick manifest id moving) is another session's locked file — recorded as DW-159.

Cost model impact: none. SMS pricing was researched, nothing purchased.
