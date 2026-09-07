## 2026-09-07 — EMAIL-FORENSIC-1: end-to-end audit of the prospect letter, its links, and the road to a published listing

David asked for a forensic, from-scratch walk of the outreach letter as a reader receives it —
every click, and the app flow behind each one, all the way to a published listing. Nothing was
taken from an earlier check; every statement below was PROBED live on 7 Sep 2026.

**What was walked.** The live Sports Clubs lane (251 letters sent 6 Sep, the only lane sending
that night): `emailer/templates/sports_club_outreach.html` rendered through the real
`emailer.render()` for a real emailed prospect (PR Racing Team, Lewiston, Maine), every anchor
extracted, every destination fetched anonymously, then the landing page driven in two independent
browsers (David's Chrome and a clean-profile browser) and the sell-flow read in the live
`/static/ms.js`, the publish gates read in `bea_main.py`, and the outcome measured on
`/onboard/funnel`.

**Headline measurement.** 1,206 letters sent; 0 prospects onboarded; 0 published. Over 30 days
the funnel shows 62 sessions `landed`, 15 reached `photos`, and **zero reached any later step**.

**Six new OPEN ledger entries** (each runs live and prints READY TO LOCK when fixed):

- **RG-0325** — the invited seller's city is dropped. `sfInit()` seeds `sfState.city` from
  `activeCity.name || 'Pretoria'` and never reads `magicLink.area`, and that value is what
  `goHandoff()` posts as the listing's city. PROBED: `magicLink.area='Maine'` while
  `sfState.city='Pretoria'`. Same function hard-codes `country_iso2='ZA'`. 1,132 of 1,206
  prospects emailed (94%) are not in Pretoria. Sibling of MAGICLINK-CITY-1, which repaired the
  link while the app kept ignoring it.
- **RG-0326** — the opening photo gate is a wall. The forward button renders `disabled` until
  `sfState.photos.main===2`, and "Skip the rest of the photos" only appears after the main photo
  is accepted. No arrival has ever passed it.
- **RG-0327** — the CTA carries parameters the app never reads: `suburb` (shipped as
  `neighborhood=` on US/AU/GB letters because localize.py rewrites the word) and `draft_id`.
- **RG-0328** — the live `/support` page, linked from every letter, contradicts the letter:
  "You must have an active subscription to publish listings", "create a seller account via the
  TrustSquare admin panel" (Basic-auth gated), and "currently live in Pretoria" while letters go
  to Maine, New York, Illinois and California.
- **RG-0329** — `static/examples/athletics.html`, linked from the ZA club letter, renders the
  literal placeholder "your provincial athletics body" as though it were the body's name.
- **RG-0330** — rendering a letter WRITES to `prospects.db` (`_apply_launch_special` →
  `launch_codes.get_or_create_code`). Hit during this audit: the write failed mid-transaction on
  the FUSE mount and left a hot journal that made the database unreadable to every opener,
  read-only included. Recovered the same run (journal rolled back on a sandbox-local copy,
  `integrity_check` ok, 5,838 rows, 1,111 emailed). Backup kept at
  `CityLauncher/data/prospects.db.bak-hotjournal-20260907-050133`.

**Confirmed working**, so it is on record: all five links in the letter answer 200 anonymously;
the CID-inlined logo needs no remote image load; the unsubscribe link is a correct two-step
(GET shows a confirmation, POST performs it) with RFC 8058 one-click headers on the message;
the Sports Clubs → Tutors category mapping (INVITE-CAT-2) works; and the funnel beacon fires.

Files: `scripts/regression_ledger.py` (+6 entries, backup
`scripts/regression_ledger.py.bak-emailforensic-20260907-050708`).
