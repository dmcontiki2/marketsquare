# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
While the sandbox is dead, run it host-side: queue `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline |
| 2026-09-05 (runs 3–4b) | **0** | 0 | 0 | raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-06 (run 5) | **0** | 0 | 0 | 4,470 on the list · 570 emailed · 5 registered |
| 2026-09-07 (run 6) | **0** | 0 | 0 | 5,639 on the list · 845 emailed · 5 registered |
| 2026-09-08 (run 7) | **0** | 0 | 0 | 5,838 on the list · 1,076 emailed · 5 registered |
| 2026-09-09 (run 8) | **unknown** | — | — | NOT MEASURED: no shell, no probe possible |
| 2026-09-10 (run 9, 03:15) | **unknown** | — | — | NOT MEASURED: no shell; run spent on the sandbox fault |
| 2026-09-10 (run 10, 05:40) | **queued** | — | — | scorer allow-listed + queued host-side; result unread at write time — READ IT FIRST |

Target: **20 by Fri 31 Oct 2026.** Model: runs 5–8 Fable 5.1; runs 9–10 **Opus 5** (drift, RUL-096h).

## THE SANDBOX IS DEAD — AND IT IS NOW DAVID'S DECISION, NOT A DEFECT

Windows update **KB5124008** (installed 8 Sep, build 26200.9445) broke the Plan9 share between the
Cowork VM and the disk. Upstream issue anthropics/claude-code#92984: **no vendor fix; uninstalling
the KB is the only known remedy.** Same class on ARM64 (#92958 / KB5124012). App restart proven
useless 9 Sep — the HCS VM outlives the app. Retry the mount ONCE per run, then stop.

**David ruled, 10 Sep 2026: "please proceed and remove that update until Anthropic has fixed the
issue."** `MarketSquare\remove_kb5124008.bat` is written and ready. Claude may NOT execute it —
removing a security update is a system/security change barred to the agent even on request, and the
queue agent has no admin token. It is David's one action. **This ruling is not yet in RULINGS.md**
(no fragment compiler, file too large to rewrite safely without a shell): the next run with a
working sandbox must append it and add the assertion to `rulings_check.py`.

Without a shell: file reads, small verified Writes, WebSearch (web_fetch is provenance-limited),
Chrome, and hand-written `.req` files into `host_queue\`. Both fact boards run host-side
(`ledger_host.bat`, `rulings_host.bat`, `boards_host.bat`).

## WHAT RUN 10 DID (10 Sep 2026, 05:30–06:30 SAST)

1. **Sends are happening.** The host DailyWave fired on time at 00:10 and sent **86 real emails**
   across 7 states at wave #3 — Montana 24 · Texas 24 · New York 12 · Wyoming 12 · Virginia 10 ·
   Pennsylvania 3 · Tennessee 1. The ramp's first doubling is holding at 24. California dry-ran on
   the stop-loss gate (last wave 12.5% bounce). The 9 Sep overnight-sleep miss did not repeat.
2. **Queued today, in order:** the scorer · `clean_stoploss_cities.bat` · a second
   `launch_day_wave.bat` · `run_us_registers.bat`. **READ ALL FOUR `.result` FILES FIRST.**
3. **COA-1 shipped without touching the 486-line reader.** `CityLauncher/us_register_coa.py` is a
   standalone, self-contained, resumable harvester for the Colorado Outfitters Association (92
   licensed members, mailbox on each profile page). It writes the same `us_registers/coa.club.csv`
   that `club_import.py` globs. One line added to `run_us_registers.bat`. Delete
   `us_registers/coa_adapter_DRAFT.py` once the first harvest is confirmed in a `.result`.
4. **Measurement lane restored:** `onboarding_number.py` added to the queue allowlist. The
   allowlist rebuild verified all 33 prior rows present before writing (the 05:00 near-miss rule).
5. **Fact board 05:11 (host-side):** 336 entries · 311 holding · 2 regressed · 22 open. Both reds
   are dashboard-truth, not the goal funnel: live badge says session 192, disk says 194; the
   provenance auditor reds on the live page. Both local remedies pass clean — so the fault is the
   gap between disk and server, i.e. a deploy. Not deployed: never deploy over a red board.

## WHERE THE FUNNEL LEAKS (PROBED 8 Sep 2026 — not re-probed since; no shell)

- Graded funnel: 21 sessions, **1 human**, **0 humans from any letter**. n=1 — no click→publish
  rate exists. Take it to David only at n ≥ 10 humans.
- Email side (4 days): 914 sent · 5.3% bounced · 13.2% human opens · **2 human clicks (0.23%)** ·
  0 signed. People open and do nothing — **the ASK is the bottleneck**, not the send count.

## SUPPLY — THE POOL IS DRYING UP, WHICH IS EXPECTED (RUL-103)

**The 00:10 wave visited 8 cities; the 9 Sep wave visited 18.** Ten states produced no sendable
prospect at all. Never throttle to postpone this — answer it with supply.

- Next adapters, in order of promise: **IOGA Adventure Finder** (~250 Idaho outfitters, public;
  members.ioga.org is login-gated) · Alaska APHA · New Mexico NMCOG · Utah UGOA · Maine
  Professional Guides Association. Same shape as `_wyoga`/`coa`: text-based, harvested host-side.
- **Oregon OOGA member list is NOT a quick win** — script-rendered and Cloudflare-obfuscated
  mailboxes. Do not re-probe blind.
- US club lane left: rrca 292 + usatf-pacific 40. `usatf-new-england` is dead supply (28% bounce,
  personal mailboxes) and is source-held — correct, do not build a release for it.
- ZA: Durban 588 + PMB 525 teachers (dbe_emis) are the big pool; Tutors arm-b rides them.
- Dead ends (do not re-check): USATF national finder · NY DEC guides · USATF Mid-Atlantic / Three
  Rivers / MN / OR / GA / NJ / IN · US general search scraping · orienteeringusa · skifederation ·
  americancanoe · americanhiking · adventurecycling · coloradooutfitters.org/find-an-outfitter.

## WHAT THE NEXT RUN SHOULD PICK UP

0. Re-test the sandbox ONCE. If David removed KB5124008 and it is alive: say so with the date,
   resume normal method, and **append the 10 Sep ruling to RULINGS.md with its assertion**.
1. Read the four queued `.result` files (scorer, stop-loss clean, wave, registers). Confirm the
   COA harvest actually wrote rows before believing it.
2. Run the number. Then `GET /onboard/funnel?days=2` — humans, and which step.
3. Ledger in shards (`--shard=k/3`, `--combine=3`) or `ledger_host.bat`; then `rulings_host.bat`.
4. The two dashboard reds need a **deploy**, not a code fix — ship once the board is otherwise green.
5. Build the next register adapter (IOGA Adventure Finder first).
6. Still unproven as ONE walk: seller form → save → publish → visible logged out.
7. YouTube: nine films live; film 07 (Liquidation) unpublished — David's click, when he chooses.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Reading "no sendable
  prospects" as supply. Halving the batch for a "measurement week" (RG-0290). US general search
  scraping. Trusting "wave #N logged", and trusting the wave NUMBER itself.
- Reading the funnel without grading it. Running the ledger in one call — use shards or the host bat.
- Probing register sites with sandbox curl: most .org hosts return a 143-byte proxy 404.
- Retrying a dead sandbox mount more than twice. Restarting the app to cure it (proven useless).
- Two sessions at once: space deploys; one is better than two.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

One, already asked and answered: remove KB5124008 (granted). Film 07 is his click, when he chooses.
