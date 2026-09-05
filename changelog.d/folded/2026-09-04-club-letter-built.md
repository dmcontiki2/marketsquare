## 2026-09-04 — The club letter: built, wired, rendered — and waiting on one word

The club lane now runs end to end, dry. What was missing after SPORTS-CLUBS-1 was not
permission, it was three artefacts that did not exist yet, and they exist now:

- **`emailer/templates/sports_club_outreach.html`** — the club letter. Registered under a
  new `Sports Clubs` category in the template and subject maps. PROVED by rendering it
  through the real `emailer.render()` against a real scraped club row: no merge field left
  unfilled, magic link at the app root (never /admin.html, RG-0239), unsubscribe present.
  The localiser correctly REFUSED the first attempt because the test row said country
  "South Africa" rather than "ZA" — the fail-closed guard doing its job on a dry run.
- **`club_import.py`** — the harvest into the live pool. Dry by default, `--commit` to
  write. Applies one-per-club before insert so the pool never carries rows the sender would
  only hold later. 577 addresses → **313 clubs** (Pretoria 212, Cape Town 101).
- Both cities are already armed with gates green, so no policy change is needed.

**Nothing is in the database and nothing has been sent.** That ordering is deliberate and
worth stating: reading a public page costs nothing and is undone by deleting a file, but
putting 313 named volunteers into the prospect store is real personal-data processing, and
deletions are reserved to David (RUL-096(f)). So the harvest waits in gitignored CSVs until
the letter is approved. Code first, data second.

**What is actually blocking the send is the letter, and only the letter.** It goes out over
David's name to 313 strangers as their first impression of TrustSquare — commercial
positioning and sending to third parties, both reserved under RUL-096(f). Not a legal gate:
RUL-052 settled that, and this agent put the counsel blocker up twice by reflex before
David corrected it. To make the review a read rather than a writing task, the draft is in
his house style as `Letter to the Clubs — nice.docx`, with every claim tabled against the
canon that backs it.

**Recommended order, as a technical call:** send the already-reviewed 17 provincial letters
now, and do NOT wait on their replies before mailing the clubs. Volunteers answer slowly,
the club preparation takes days anyway, and that natural gap is the courtesy. The federation
route also scores nothing toward the 20 — anyone arriving via a forwarded paragraph was
never contacted by us and `onboarding_number.py` will exclude them.
