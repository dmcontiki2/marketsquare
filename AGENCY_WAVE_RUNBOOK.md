# Agency Wave Runbook — sending the recruited-agency emails (AGENCY-WAVE-1, 23 Aug 2026)

The lane that turns scraped estate agencies (and dealers / travel agencies) into
console-holding accounts via the city-wave email launcher. Built 23 Aug 2026;
asserted by regression ledger RG-0163 / RG-0164 / RG-0165. Sending is DAVID's act
(RUL-046 reserved class) — this runbook is the checklist for that day.

## Preconditions (hard)
1. **Gate is DOWN** (soft-public, Fri 29 Aug 2026 per RUL-001). Every link in the
   outreach emails — Import Guide, Agents-as-a-Service, ranking explainer, listing
   deep-links — 403s for anonymous recipients while GATE-ENFORCE-1 stands.
   Probe one email link from a clean/incognito browser before sending.
2. The deploy carrying AGENCY-LINK-1 has ridden (`GET /agencies/wave-prep` answers
   405 to a bare GET, not 404 — the ledger checks this).
3. The n8n instance has RE-IMPORTED `n8n/n8n_outreach_workflow.json` (the repo file
   is the master; the change adds the Estate Agents→agency_outreach lane, honors
   prospect.magic_link, and DROPS agency prospects without a console link).

## Which verticals may wave (RG-0169 rule)
Only verticals whose console SKIN exists may receive console-CTA waves: estate
agencies, travel agencies/operators, car dealers. Collector shops, tutor
institutions, service companies and placement agencies WAIT until their skin
(labels + credential gate + import wording) ships — RG-0169 tracks this and the
picker marks them "(skin coming)". Their templates exist; sending them early would
land recipients in a console wearing another vertical's labels and gates.

## Wave-day steps (per city)
1. **Pick the agency prospects** in CityLauncher (category: Estate Agents) — name,
   admin email per agency.
2. **Mint consoles + links**: `POST https://trustsquare.co/agencies/wave-prep`
   (X-Api-Key: app key) with `{"agencies":[{"name":"...","admin_email":"..."}],
   "link_days":14}`. Idempotent — safe to re-run; existing orgs get a fresh link,
   never a duplicate. Orgs land verified=0 (verification is earned on application).
   NO email is sent by this call.
3. **Paste each returned console_link into prospects.magic_link** in the
   CityLauncher DB (the launcher's prospect table shows a Copy button per row;
   the exportCSV/import path also carries the magic_link column).
4. **Set the wave's reply-to** to a monitored inbox (lane 1 of the email is
   "reply with your stock list — we do it for you"). support@trustsquare.co.
5. **Trigger the n8n wave** with `category: "Estate Agents"` (dry-run first —
   the payload node logs how many agency prospects were dropped for missing links;
   0 dropped is the target).
6. **Lane-1 replies** (concierge): EITHER paste their list into their console's
   ⇪ Bulk import adverts box (ADVERT-BULK-1 — no code), OR use the Import Guide flow —
   `/agencies/{id}/agents/bulk` for the roster, `/agencies/{id}/import` for the book;
   both keys are in the agency's console header.

## What the recipient experiences
Email CTA → trustsquare.co/?signin=<jwt>&agency=1 → signed in, lands INSIDE their
console (name on the door, API key visible, invite/bulk-add ready). The signin CODE
path also works: after code sign-in, the My Space "Agency console" card is visible
to any agency admin (AGENCY-LINK-1 card, resolves via /agencies/by-admin).

Dealers: same flow with &dealer=1 · cars_dealer_outreach. Travel: &operator=1 ·
travel_agency_outreach. wave-prep takes `"skin": "agency" | "operator" | "dealer"`
and mints the matching console param for those waves.
