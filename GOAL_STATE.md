# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline |
| 2026-09-05 (runs 3–4b) | **0** | 0 | 0 | raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-06 (run 5, 01:05) | **0** | 0 | 0 | 4,470 on the list · 570 emailed · 5 registered |
| 2026-09-07 (run 6, 01:05) | **0** | 0 | 0 | 5,639 on the list · 845 emailed · 5 registered |

Target: **20 by Fri 31 Oct 2026.** Model on runs 5–6: Fable 5.1 (as David asked, RUL-096h).

## WHERE THE FUNNEL LEAKS (PROBED 7 Sep 2026 — and the instrument was wrong until tonight)

- **Every funnel reading before 7 Sep 01:30 SAST was link scanners, not people.** The 9 "clubs at
  the photo step" (6 Sep) were created 20–40 s after their wave's send, 4 at a time within 8 s, by
  Google-Safety (nginx-confirmed). The `yt-*` landings are the same class. Humans at the photo
  step: **0**. Humans landed from club letters: **unknown** — the instrument could not tell.
- Fixed and live (FUNNEL-HUMAN-1): `/onboard/step` stores UA + bot flag; `/onboard/funnel` hides
  bot and ungraded rows unless `bots=1`; `humans` = sessions that fired `dwell` (12 s + a real
  input). **The click→publish measurement starts 7 Sep.** Read `GET /onboard/funnel?days=2` and
  use `humans` as the denominator; take it to David only with n ≥ 10 humans.
- Email side (server, graded): 981 sent to 6 Sep · 15–21% human opens · **0.44% human clicks**.
  People open and do nothing — the ASK is the bottleneck. EMAIL-VARIANT-1 arm 'b' (shorter ask,
  no money) is armed for Tutors + teachers_trainers and rides the next wave that draws them.

## WHAT RUN 6 DID (7 Sep 2026, 01:00–02:10 SAST)

1. Read the 00:10 wave: **251 real sends, 0 crashes**; Cape Town 12 + 23 US states; ramp doubled
   to 24 in N. California / California / Illinois; 12 states got wave #1; 17 states (North
   Carolina → Wyoming, 166 letters) dry-ran on the 250 cap → they go tonight. US club bounces:
   6 Sep wave 0/203; tonight 7/251 so far (2.8%). Domain gate now has its 50 post-clean sends.
2. FUNNEL-HUMAN-1 above, shipped twice via relay (RG-0315 LOCKED; RG-0293 read moved to bots=1).
3. Ran the ledger in pieces (the sandbox call cap is ~178 s; a background run dies with the
   call). Board after: **311 entries · 0 REGRESSED · 22 open**. Cleared 3 stale reds (session
   counter, harness call site, .ps1 CRLF). NOTE: the canonical way is now the ledger's own
   `--shard=k/n` + `--combine=n` (LEDGER-SHARD-1, built 06:56 the same morning); my 01:17
   `ledger_slices.py` is retired to a pointer.
4. MOGA-1: **199 Montana licensed outfitters** harvested (`--adapter moga`, one page, embedded
   JSON) → category adventures_experiences, bucket Montana; import queued. Caught: the register
   CSV had no category column → would have imported as Sports Clubs and got the CLUB letter.
   Fixed + RG-0316 LOCKED. Lane is collected, NOT drawn (letter lacks the source line) — RG-0317
   OPEN says exactly what unlocks it.
5. RUL-103 check re-pinned; LAUNCH_SERIES.md now says nine films are LIVE (only 07 on disk).

## SUPPLY (measured 7 Sep)

- US Sports Clubs uncontacted: **815** (MA 213, TX 57, CA 55, N.CA 52, NY 44, PA 39, FL 38…) ≈
  3–4 nights at 250/day. **The US club lane runs dry ~10–11 Sep. Next register must land first.**
- ZA: Pretoria 342 club:agn uncontacted but the city drew nothing tonight (club:agn now 4 bounces
  in 24 → source gate, most likely; the planner prints "-" without naming the gate — fix that
  print). Durban 588 + PMB 525 teachers (dbe_emis) are the big ZA pool; Tutors arm-b rides them.
- Montana outfitters 199 banked (undrawn). Adding a register = ~30 lines in `ADAPTERS`
  (`us_register_reader.py`), verify the page CARRIES EMAILS first (curl + grep from the sandbox
  works for most sites), `--csv` from the sandbox, add to `run_us_registers.bat`, queue that bat.
  Next candidates: other state outfitter/guide associations (Idaho IOGA members page 404 — find
  the new URL; Wyoming WYOGA; Colorado COA; Alaska APHA), ACBL bridge, US Chess (host only).
- Dead ends (do not re-check): USATF national finder; NY DEC guides; USATF Mid-Atlantic / Three
  Rivers / MN / OR / GA / NJ / IN; US general search scraping; orienteeringusa; skifederation;
  americancanoe; americanhiking; adventurecycling.

## WHAT THE NEXT RUN SHOULD PICK UP

0. Check `host_queue/worker_log.txt` for a RUN without a DONE before opening prospects.db.
   Read `host_queue/done/*run-us-registers.result` — did the 199 Montana rows import (+199)?
1. Run the number. Newest `logs/launchday_*.log`: `EMAILER CRASHED` must be 0; confirm the 17
   remaining states went and the ramp doubled where wave #1 was clean. Bounces off the server.
2. `GET /onboard/funnel?days=2` — FIRST graded reading: `humans`, and which step they reach.
   If humans ≥ 10 and none pass `photo_pick`, the required photo is the leak — fix as a class.
3. Ledger: `python3 scripts/regression_ledger.py --shard=1/3` (then 2/3, 3/3) and `--combine=3`.
4. Letter work that unlocks supply: bring `adventures_experiences_outreach.html` into RUL-099
   shape (source line; consider dropping the $20 ask like arm 'b'), then add
   adventures_experiences to Montana's category_priority → RG-0317 prints READY TO LOCK.
5. Still unproven as ONE walk: seller form → save → publish → visible logged out (publish_ok).
6. YouTube: nine films live, links clickable since 00:19 7 Sep. Read `yt-*` humans off the
   funnel (graded from now). Film 07 Liquidation is the one not yet posted — David's click.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly (1 Sep). `fill_wave_gaps.py` via the queue (401, RG-0263).
  Reading "no sendable prospects" as supply (4 Sep). Halving the batch for a "measurement week"
  (5 Sep, RG-0290). US general search scraping (5 Sep). Trusting "wave #N logged" (6 Sep).
- Reading the funnel without grading it (6 Sep) — scanners run our JS. Grade first.
- Running the ledger in one call (7 Sep): the call cap is ~178 s. Running it on the server: 45
  false reds. Use the slices.
- Two sessions at once: David was interactive at 01:32 tonight and saw my two deploy restarts
  as "everything red" on the +1 page. Space deploys; one is better than two.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

None this run. Film 07 (Liquidation) is the only unpublished film — his click, when he chooses.
