## 2026-09-04 — ASSOC-EXAMPLE-1: David's SABIO page, turned into a generator

David hand-built a worked example page for SABIO — bee removals, mock listing cards, the
Trust Score ladder, what is shown and what is never published — and then made the
observation that turns it into machinery: *"There would similar examples for every type of
club, the chess tutors, the Judo clubs etc."* So it is a generator, not fifty hand-made
pages.

`scripts/assoc_example_page.py` + `scripts/assoc_specs.json` build a SABIO-shaped page for
any membership body from a short spec. Six are written and rendered into
`visuals/assoc/`: chess, judo, athletics, dance, plumbers, tour guides.

**The finding that came out of building it.** Writing the specs meant checking each
credential against the live signal tables in `bea_main.py`, and two of the six need
NOTHING built:

- **Plumbers (IOPSA)** — PIRB trade licence +12, professional body registration +12, formal
  trade certificate +8, public liability +5, CIPC +5 are all ALREADY scored. A member can
  list tonight and reach 100 — Highly Trusted — with no work on our side.
- **Tour guides** — provincial registration +12, CATHSSETA +8, first aid +6, indemnity
  insurance +5, 3+ languages +4. Same story.

Chess, judo, athletics and dance each need one or two additions (FIDE trainer title, JSA
coaching licence, ASA coaching licence, teaching diploma) and their pages say so plainly.
Chess is the strongest of those because the registry already exists: 4,237 verified FIDE
trainer rows sit in CityLauncher awaiting FIDE-CLAIM-1.

**RG-0267 LOCKED — the honesty rule, which is David's, taken from his own page.** His SABIO
page marked DALRRD and SABIO membership as *proposed* and stated "they are not on our
credential list". That discipline is now asserted: the generator must keep its LIVE and
PROPOSED tags and its honesty paragraph, every spec must declare both lists, and the COLD
EMAIL may name live badges only. A page may responsibly propose a badge — it is a proposal,
sent to the body that would define it. A letter may not, because nobody is there to read
the caveat. The failure this prevents is quiet and expensive: an association tells its
members a badge exists, members list expecting it, and it never appears.

**The letter now carries one card, not a brochure.** The club email gains a single mock
listing — title, score, three live badges, price — plus a line pointing at the full worked
page for that sport. Keyed off the federation the row was scraped from. Rendered against a
real scraped club: no merge field left unfilled.
