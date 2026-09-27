## 2026-09-25 — ORG-ENROL-1: the employer door ships · STATUS-CARD-FIT-1: her card reads as words

- **ORG-ENROL-1 (RUL-150, QUICK_LISTING_SPEC s12/12a; reach proposal 1) — RG-0474.** New module `org_enrol.py`
  (router seam, mounted like estate_agents): `POST /agencies/{id}/enrol` (the organisation's own admin or the
  admin key) takes a list of name + role + language and, per person, mints HER OWN RUL-167 key account (no
  e-mail, no phone held; the secret is shown once and stored only as a hash), an `agency_members` row and an
  `org_enrolments` slip. `?format=sheet` returns printable QR slips in her language. `GET /e/<secret>` signs
  her in and opens `/q/services?role=<role>&lang=<lang>&src=org<id>`, or the app once she has an advert; the
  link never lapses (RUL-141) and is the same key `/k/` honours. A VERIFIED organisation's enrolment is its
  employer confirmation (`universal.employer_confirmed`, 12 pts, once; a rejected one never re-earns; an
  organisation verified after the import confirms at claim). `GET /agencies/{id}/enrolments` shows the
  organisation enrolled / opened / confirmed / published, never a link. `scripts/enrol_import.py` is the CSV
  lane on the server. **The hard line:** the module never writes the listings table and reaches no
  advert-creating path; RG-0474 asserts it from source AND by enrolling two people on an in-memory database
  (0 adverts). Behavioural test before shipping: 19/19. Sends nothing to anyone -- the slips are handed out
  by the organisation. `roles/role_registry.json` now ships (the importer validates roles against it).
- **STATUS-CARD-FIT-1 — RG-0475.** Found on the live card for listing 367: the 24 Sep one-line ellipsis cut
  "The Great American Yellowstone Safari" to "The Great Ameri…", and "Ask me on TrustSquare" crossed the
  panel border. The title now steps 92 → 76 → 64 px and takes two lines before any ellipsis; the panel
  heading shrinks to fit. RG-0475 renders a long title and fails on any text past the card edge or a
  two-line-fitting title that is cut -- proven able to say no against the old renderer.
- Shipped in the same deploy, by David's "Release" (25 Sep): the open-rate lane's RUL-168 typed-rates work
  and the cto-fix lane's aged git-lock sweep log, which had sat uncommitted under that lane's work lock.

Cost model impact: none.

- **First deploy refused, correctly (06:42Z).** The stranger gate refused 19f89c3 because the three new routes
  had no rule in `route_policy.json`; the live site was not changed. Declared: enrol and enrolments = signed-in
  user who OWNS the agency; `/e/{secret}` = token. Hardened in the same pass: the door now runs its own
  organisation-admin guard (`_org_admin`: admin key, or a session that IS that organisation's admin), so the
  kill switch that can drop the shared agency seam into shadow mode can never open enrolment. Behavioural test
  22/22 including shadow-mode stranger -> 401 and signed-in intruder -> 403. RG-0474 now also asserts the guard
  and the three route declarations.
