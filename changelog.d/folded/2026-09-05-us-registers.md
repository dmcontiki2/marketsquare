## 2026-09-05 — US-REGISTERS-1: the first US official register is in the send pool; search scraping measured dead for the US

Onboarding-goal run (Fable 5.1, 18:58–19:45 SAST, in parallel with a second goal session — see GOAL_STATE).

**The number: 0** (probe A 0, probe B 0; 5 registered in total, none published; the raw query's 2 are the seeds).

**Measured.** The first ever US run of `run_us_scraper.bat` (SCRAPER-COUNTRY-1, 18:51–19:24, 11 cities × 7
categories, DDG + Bing) returned **one** address, `info@antiques-vintages.co.za`, filed under Austin. In the
same hour the first US **register** — the USATF Pacific Association's public club list — yielded **88 clubs
with a mailbox from 211 in 8 minutes**. David's 5 Sep instinct ("the pattern that produces volume is the
official register") is now a measurement, not an opinion.

**Built.**
- `CityLauncher/us_register_reader.py` — US sibling of `club_reader.py`, an ADAPTER REGISTRY (one entry per
  body; `pausatf` first). Resumable: a `.done` file records every register key and rows are appended as they
  are read, because a sandbox call is capped at ~3 minutes and a 210-page register does not fit in one.
  Writes only a gitignored CSV under `us_registers/` — never a database (31 Aug rule).
- State bucket: rows land as city=`Northern California` (real town in `suburb`), country=US, Sports Clubs.
  `waves_policy.json` carries the bucket armed + gates_green with `category_priority: ["Sports Clubs"]`;
  `localize._CITY_COUNTRY` maps it to US. One bucket = one-day-per-city gap and the ramp pace the register.
- `CityLauncher/club_import.py` (server-side importer) takes `--country/--category/--source-prefix` and
  carries phone/suburb/source; defaults unchanged for the ZA rosters.
- `CityLauncher/scripts/club_import.py` (the allowlisted HOST importer, run with no arguments by the queue)
  now also reads `us_registers/*.club.csv` and honours a per-row `country`/`category`/`suburb`/`phone`/
  `source`. Without this the US roster would have landed in the local pool as ZA — or not at all, since
  `pull_from_server.py` carries verdicts down, not rows.
- SCRAPER-GEO-1: `run_local_scraper.py` gains `foreign_cctld()` and applies it in both the DDG and Bing
  result loops — a mailbox whose domain carries another country's ccTLD is dropped at the collector.

**Shipped / executed.** 88 rows imported to the server (`club_import.py --country US --commit`, PROBED 88)
and to the local send pool via the queue (`run_py CityLauncher\scripts\club_import.py`, result: added 88,
already present 577; local PROBED 88 scraped in 'Northern California'). The 00:10 wave visits the bucket.

**Ledger.** RG-0295 (US register lane wired end to end: reader → CSV → host importer → policy bucket →
country map, plus a live server count ≥ 80) and RG-0296 (ccTLD guard, static + behavioural). Both LOCKED,
both pass.

**Lesson, class-level.** A sandbox read of the local `prospects.db` at 19:04, while the host scraper was
committing, left a hot journal (valid header, 4 pages) and the DB unreadable from the sandbox until the
host's next open rolled it back at 19:31. Reads are only safe while the host is idle: check
`host_queue/worker_log.txt` for a RUN without a DONE first, or read the server copy over SSH. Recorded in
GOAL_STATE as the first pick-up item.

**Dead ends recorded so nobody re-checks them:** USATF national club finder (sport80 JS widget, unreadable);
NY DEC licensed-guide open dataset on data.ny.gov (6,762 rows, no email column); rrca.org (403).

**Engagement of the day's 141 sends (PROBED 19:35 UTC+2):** 34 opened and 7 clicked of the 129 morning
sends, but 6 of the 7 clicks were Azure/Defender scanner ranges within 10 minutes — one real human click.
18 of 141 bounced (12.8%), 1–2 per city across 14 cities: under the 3-bounce stop-loss floor everywhere,
but every one of those cities' ramp streaks reset to 12. The 19:31 Pretoria club wave: 12 sent, 5 opened,
3 clicked, 2 bounced in its first five minutes.
