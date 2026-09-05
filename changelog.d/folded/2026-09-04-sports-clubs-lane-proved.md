## 2026-09-04 — SPORTS-CLUBS-1: David's club lane, proved the same day

**The idea, in his words: clubs never advertise, so they never appear in search or maps —
but a club must file paperwork to affiliate, register as a non-profit, enter races and
book municipal fields, and that paperwork is published with a secretary's address on it.
So collect the paperwork, never the adverts.**

Proved, not estimated. `CityLauncher/club_reader.py` was built and run live against two
provincial athletics pages, then every address pushed through the real send guards:

- Western Province Athletics — 211 addresses on one page → **98 sendable**
- Athletics Gauteng North — 366 → **197 sendable**

**295 sendable clubs from two provinces of one sport. Athletics SA has 17 provincial
bodies — roughly 2,500 from athletics alone**, before cycling, judo, karate, boxing,
swimming, the 227 parkruns or the 270,000-row non-profit register. Our existing
search-and-maps scraper had found 40 sport entries in the entire 3,805-row database. The
word list was never the problem; the place we looked was.

Against the onboarding arithmetic this is the single biggest lever available: it roughly
doubles the list and drops the required click→publish rate from ~5% to ~2.5% — "tight"
becomes "comfortable". The guards did real work on real data: one-per-org held 237 sibling
mailboxes, the government filter held 45 officers' .gov.za addresses.

**RG-0266 LOCKED** — the reader is a COLLECTOR: no sqlite3 import, no send path, no
database handle. Collecting a row is not permission to email it; the one send chokepoint
in emailer.py keeps that job (RUL-054). And the harvest never enters git — `club_lists/`
and `*.club.csv` are gitignored, because a federation roster is named volunteers with
personal addresses and cell numbers. The reader is code and is committed; what it reads
never is.

**A rule correction on the record.** Two sessions running, this agent put "get a lawyer
first" in front of the clubs lane. RUL-052 (24 Aug) and RUL-020 already say counsel items
ride alongside and never gate a wave — David: *"I am now stopping the noise."* The block
was reflex, not policy, and it has been removed from ONBOARDING_PLAN.md. What carries this
lane is the machinery that was always going to carry it: suppression checked at two gates
fail-safe, unsubscribe in every template, the shape filters, one-per-org, the ramp and the
stop-loss.
