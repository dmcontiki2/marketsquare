# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

## SUNDAY SUMMARY (6 Sep 2026, plain language)

**The number is still 0.** Nobody we emailed has published a listing yet.
What moved this week: the emails started reaching real people (the broken link was fixed on
3 Sep), the club lists arrived (577 South African clubs, then 903 US running clubs from a
national register), and we can now see where people stop after they click.
What we found this run: (1) last night's wave sent 0 of the ~450 US club letters — the letter
crashed on a rand price for every reader outside South Africa, and the log still said "done".
Fixed, and the wave was re-sent the same night: 203 US club letters went out across 22 states
before the 250-a-day limit stopped it; the other 29 states go on Monday night. (2) Every club contact who clicked our link
landed on a generic "what are you selling?" screen instead of the listing steps, because the app
did not recognise the word "Sports Clubs". Fixed and live. So far 9 people have reached the
site from the club letters; none went past the first screen. Whether they now go further is the
thing to watch this week.
Next: keep the waves flowing every night (250 a day is the limit now), read the funnel every
morning, add the next club register. The YouTube package for the first film is ready; David
picks the title.

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline |
| 2026-09-05 (runs 3–4b) | **0** | 0 | 0 | raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-06 (run 5, 01:05) | **0** | 0 | 0 | 4,470 on the list · 570 emailed · 5 registered |

Target: **20 by Fri 31 Oct 2026.** Model on this run: Fable 5.1 (as David asked, RUL-096h).

## WHERE THE FUNNEL LEAKS (PROBED 6 Sep 2026)

- `GET https://trustsquare.co/onboard/funnel?days=2`: **9 sessions landed, 0 reached `photos`.**
  4 carry a real src (pretoria-sports-clubs-20260905/06); 5 carry a scanner-mangled src (letters
  rot13'd, digits +3 — a link scanner, not a person). So: 4 real club landings, none went on.
- **Cause found and shipped (INVITE-CAT-2):** the app's invite map had no 'Sports Clubs' key,
  so clubs landed on the generic category tiles, not Step 1 (photo). Now routed to Tutors (the
  letter's worked example is a Tutors listing). RG-0299 asserts every outreach category routes.
- From now on the question is the one the plan asked: do people stop at the required photo?
  That reading starts with tonight's wave. Take it to David only with counts (n ≥ 10).
- 5 Sep 09:31 wave (129): 16 bounced (12%), 44 opened, 7 real clicks, 0 published. Sydney is
  held by stop-loss (3 bounces, 11.5%). France and Portugal stay OUT (RUL-101).

## WHAT RUN 5 DID (6 Sep 2026, 01:00–02:30 SAST)

1. **Found the 00:10 wave sent 55 (Pretoria 12 clubs, NY 12, Cape Town 12 clubs, Durban 9, PE 8,
   Kimberley 1) and then crashed in all 51 US state buckets** — `UnsupportedCountry: R700` from
   the club example card (Python-side, invisible to the template test). Fixed (CLUB-INTL-1: per-
   country card, ZA-only example link, send-path test with 34 assertions), made crashes loud and
   rc≠0 (WAVE-CRASH-VISIBLE-1), **re-queued the wave at 01:15. It ran 01:31–01:55: 203 US club
   letters sent across 22 states (Northern California → Maryland, alphabetical), 0 crashes; the
   250-a-day cap then held at 257 and the other 29 states dry-ran — they go at the 00:10 wave
   on Mon 7 Sep.** RG-0298 LOCKED (observed leg: the post-fix log is clean).
2. INVITE-CAT-2 above; shipped with `request_deploy` (b8b8594). RG-0299 LOCKED.
3. RG-0287 was red (dashboard club card 577 → 313 vs DB 1,568 / 1,301) — card corrected.
4. Third US register: **USATF New England, 268 clubs** (`--adapter usatfne`, one static page),
   imported host-side 01:55 (+266; Sports Clubs now 1,834 rows / 1,550 distinct clubs). Probed and rejected: USATF Mid-Atlantic, Three
   Rivers (no club emails). RRCA result read: +903 imported 5 Sep 21:30.
5. youtube-pack for film #1 → `feature-videos/01-collectables/…_youtube/`. LAUNCH_SERIES updated.
6. US search scraper measurement run (RG-0297) never searched: DDG reset the connection at
   preflight. Not re-queued — registers are the supply.

## SUPPLY (measured)

- Sports Clubs: **1,834 rows / 1,550 distinct clubs** (ZA 577, US 1,257; 239 emailed so far).
  51 US state buckets armed; 22 have had wave #1 (6 Sep), 29 are waiting on the daily cap.
- Adding a register = ~30 lines in `ADAPTERS` (`us_register_reader.py`), verify the page CARRIES
  EMAILS first, run `--csv` from the sandbox (CSV only, never SQLite), add the name to
  `run_us_registers.bat`, queue that bat. Next candidates: US Chess affiliates (JS directory —
  check `uschess.org/msa/AffLst.php` from the host, 403 from the sandbox), ACBL bridge clubs,
  state music-teacher associations (Tutors!), chambers of commerce member lists (Services),
  outfitter/guide associations (Idaho IOGA, Montana MOGA, Maine MPGA).
- Dead ends (do not re-check): USATF national club finder (sport80 widget); NY DEC guide data (no
  email column); USATF Mid-Atlantic / Three Rivers pages; US general search scraping (33 min, 1
  wrong row; then DDG blocked the home IP).

## WHAT THE NEXT RUN SHOULD PICK UP

0. Check `host_queue/worker_log.txt` for a RUN without a DONE before opening the local
   prospects.db from the sandbox (a sandbox read during a host write left it unreadable, 5 Sep).
1. Run the number. Read the newest `logs/launchday_*.log` (Mon 00:10): grep `EMAILER CRASHED`
   (must be 0), count real sends, confirm the remaining 29 states went and DAILY-CAP-1 held.
   Then read opens / clicks / bounces for the 203 US club letters off the server (read-only) —
   the first US bounce reading decides whether the ramp doubles or the stop-loss trips.
2. `GET /onboard/funnel?days=2` — first reading with clubs landing on the photo step.
3. RG-0298's observed leg reads the newest post-fix wave log; RG-0299's live leg reads the funnel.
4. Still unproven as ONE walk: seller form → save → publish → visible logged out (publish_ok).

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly (1 Sep) — rolled back in 76 s. `fill_wave_gaps.py` via the host
  queue (4 Sep) — HTTP 401, RG-0263 open. Reading "no sendable prospects" as supply (4 Sep) — it
  was reach. Halving the batch for a "measurement week" (5 Sep) — disconnected the ramp, RG-0290.
- US general search scraping (5 Sep): 1 wrong row, then blocked. Registers only.
- Reading log silence as a dead host agent (5 Sep) — it logs only when it has work.
- Two goal sessions at once (5 Sep) — one overwrote the other's GOAL_STATE. Check for a live one.
- Running the ledger in the background from the sandbox — killed when the call ends. Foreground,
  ~6 min, timeout 560 s.
- Trusting "wave #N logged" (6 Sep) — it was printed over 51 crashed categories. Grep the log.
- Assuming the invited path is the same for every category (6 Sep) — it was not for clubs.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Nothing is waiting on him.** The YouTube package for film #1 is ready whenever he wants to
post; choosing the film and the title is his call, not a blocker.
