# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST, before anything else. It exists so a fresh session costs a few
hundred tokens to orient instead of thousands. Update it at the END of every run.
Keep it under 100 lines: it is a state file, not a diary. The changelog is the diary.*

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline, set at handover |
| 2026-09-05 (run 3) | **0** | 0 | 0 | after the 129-person global wave — too early to show |
| 2026-09-05 (run 4, 19:00) | **0** | 0 | 0 | raw still 2 (both seeds, barred by §3) |
| 2026-09-05 (run 4b, 18:58, parallel) | **0** | 0 | 0 | 5 registered in total, none published; same 2 seeds |

Target: **20 by Fri 31 Oct 2026.** Model on this run: Fable 5.1 (as David asked).

## WHERE THE FUNNEL LEAKS (PROBED 5 Sep 2026, run 4)

- **Nobody who clicked has registered.** Since the link was fixed on 3 Sep about ten real
  people reached a working page; `marketsquare.users` has no non-test row since 25 Aug.
  The leak is click → register, before any listing exists.
- **The invited path was walked in a browser:** the magic link lands on Step 1 of 6,
  Photos, where "You on the job" is REQUIRED and the next button stays disabled until the
  AI accepts the photo. That is David's photo-first ruling (SELL-FLOW-REDO-2) — not changed.
- **The funnel is now INSTRUMENTED (ONBOARD-FUNNEL-1, live 19:29 SAST):** every sell-flow
  step posts to `/onboard/step`; read `GET https://trustsquare.co/onboard/funnel?days=7`
  (counts only). Whether people stop at the photo, before it, or later is now a reading.
- The 5 Sep 09:31 wave (129 sent): 16 bounced (12%), 44 opened, 7 real clicks, 0 published.
  No city latched stop-loss (all under the 3-bounce floor); ramp resets on dirty cities.
- France and Portugal stay OUT (RUL-101). `teachers_trainers` stays blocked (schools).

## WHAT RUN 4 DID (5 Sep 2026, 19:00–19:45 SAST)

1. **First-ever club wave: Pretoria sent 12 Sports Clubs emails at 19:31** (queued when the
   clubs were found imported after the morning wave; Pretoria's gap was clear). Six other
   cities correctly dry-ran on the one-day gap. Tomorrow's 00:10 wave doubles Pretoria if clean.
2. **Built and shipped the funnel instrument** (bea_main.py + ms.js, live and probed). Ledger
   RG-0293 locks it, with a probe that never pollutes the real counts.
3. **Read the first US general scrape:** 11 cities × 7 categories, 33 minutes, **1 address**
   — a South African shop mis-filed under Austin. General search scraping is dead for the
   US. Plan edited. Do NOT re-run `run_us_scraper.bat` expecting supply.
4. **Found and fixed the CityLauncher commit fault:** `CityLauncher\commit.bat` committed the
   MarketSquare repo (git_unlock changes directory and never returns), so CityLauncher's work
   since 3 Sep was never committed despite rc=0. One-line fix, RG-0294 asserts the class.
5. `request_deploy.py --help` used to ship HEAD. Now it prints usage. (One accidental deploy
   of already-committed work happened this run; health-checked, no harm.)
6. A parallel interactive session was building US-REGISTERS-1 at the same time (register
   reader + 88 USATF Pacific clubs imported as 'Northern California'). This run stayed out of
   those files. One session at a time is the rule — check for a live session before starting.

## SUPPLY (measured, both sessions)

- **Registers work; search does not.** ZA: 577 club contacts (Pretoria 366, Cape Town 211) —
  Pretoria's first 12 went tonight (5 opened, 3 clicked, 2 bounced in its first 5 minutes).
- **US, first register ever:** `CityLauncher/us_register_reader.py --adapter pausatf` read the
  USATF Pacific Association's public club list — 211 clubs, **88 with a mailbox, 8 minutes**
  (the 33-minute US search scrape found 1 wrong-country row). Imported to the server AND, via
  the allowlisted host importer, the local send pool: city=`Northern California` (a STATE
  BUCKET, real town in `suburb`), country=US, Sports Clubs, armed in the policy. The 00:10 wave
  visits it (88 people). RG-0295 locks the lane end to end; RG-0296 locks the ccTLD guard that
  stops a `.co.za` shop being filed under Austin again.
- Adding a register = ~20 lines in `ADAPTERS`, run `--csv` (resumable: `.done` file, because a
  sandbox call caps at ~3 min), then queue `run_py CityLauncher\scripts\club_import.py` (it
  reads `us_registers/` too, per-row country). Verify the page CARRIES EMAILS before writing
  an adapter.
- Dead ends already checked (do not re-check): USATF's national club finder is a JS widget
  (sport80); NY DEC licensed-guide open data (data.ny.gov, 6,762 rows) has no email column;
  rrca.org returns 403 to the sandbox.
- Next registers worth reading: other USATF associations with their own club pages (New
  England, Southern California, New York, Long Island), state soccer / masters-swimming club
  lists, state outfitter & guide associations (Idaho IOGA, Montana MOGA, Maine MPGA), US Chess
  affiliates, ACBL bridge clubs. Search the disk first.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **Never open the local prospects.db from the sandbox while a host job is running** (wave,
   scraper, import): check `host_queue/worker_log.txt` for a RUN without a DONE. On 5 Sep a
   sandbox read during the host scraper's commit left a hot journal and the DB unreadable
   until the next host open rolled it back. Prefer the server copy (read-only over SSH).
0. Run the number. Then `GET /onboard/funnel?days=2` — the first real readings will be from
   tonight's Pretoria clubs and tomorrow's 00:10 wave. Read opens/clicks off the server DB
   (`ssh root@178.104.73.239`, read-only; local prospects.db is often busy on the host).
1. Sunday: add the plain-language summary at the top of this file.
2. If the funnel shows people landing and stopping at `photos` with no `photo_pick`, that is
   the finding to take to David as a business trade-off (photo-first is his ruling) — with
   the counts, not a guess.
3. `run_us_scraper.bat` is not a supply engine (see above). Registers are. Extend the
   adapter registry in `CityLauncher/us_register_reader.py`; import via the queue.
4. Still unproven as ONE walk: seller form → save → publish → visible logged out. The
   instrument will show it the first time a real person does it (publish_ok).

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly to fix the CTA (1 Sep) — rolled back in 76 seconds.
- `fill_wave_gaps.py` via the host queue (4 Sep) — HTTP 401, RG-0263 still open.
- Reading "no sendable prospects" as a supply problem (4 Sep) — it was reach.
- Halving the batch for a "measurement week" (5 Sep) — disconnected the ramp. RG-0290.
- **US general search scraping (5 Sep): 33 min, 1 wrong row.** Registers only.
- Reading log silence as a dead host agent (5 Sep) — the agent only logs when it has work.
- Two onboarding-goal sessions running at once (5 Sep evening) — one overwrote the other's
  GOAL_STATE by 90 seconds and had to merge from its backup. Check for a live session first.
- Running the ledger in the background from the sandbox — the shell kills background jobs
  when the call ends. Run it in the foreground with a long timeout (it takes ~6 min).

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Nothing is waiting on him.** No clicks, no approvals, no decisions this run.
