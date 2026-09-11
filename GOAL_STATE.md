# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If the sandbox is dead, run it host-side: queue `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline |
| 2026-09-05 (runs 3–4b) | **0** | 0 | 0 | raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-06 (run 5) | **0** | 0 | 0 | 4,470 on the list · 570 emailed · 5 registered |
| 2026-09-07 (run 6) | **0** | 0 | 0 | 5,639 on the list · 845 emailed · 5 registered |
| 2026-09-08 (run 7) | **0** | 0 | 0 | 5,838 on the list · 1,076 emailed · 5 registered |
| 2026-09-09/10 (runs 8–10) | **unknown** | — | — | NOT MEASURED: sandbox dead (KB5124008) |
| 2026-09-12 (run 11, 01:00 SAST) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed · 5 registered · sandbox alive |

Target: **20 by Fri 31 Oct 2026.** Model: runs 5–8 and 11 Fable 5.1; runs 9–10 Opus 5 (drift, RUL-096h).

## SANDBOX: ALIVE since 10 Sep ~06:20 SAST (David removed KB5124008 — now RUL-119)

Windows Update will put the KB back unless paused. If every command dies with `no Plan9 drive
shares mounted`: retry ONCE, then follow SANDBOX-REPAIR-1 in Projects\CLAUDE.md (diagnose via the
host queue, boards host-side, .req files by hand). Never report it unfixable.

## WHAT RUN 11 DID (12 Sep 2026, 01:00–01:45 SAST, Fable 5.1)

1. **Measured.** Number 0, both probes agree. Fact board green (every locked fix holding, 22 open);
   rulings 0 fail. The two dashboard reds from run 10 are gone (11 Sep sessions deployed).
2. **Sends are flowing.** The host wave fired at 00:10 and sent **72 real emails** in 4 states —
   Alaska 12 (wave 2) · Colorado 24 (wave 3) · Maine 12 (wave 3) · Montana 24 (wave 5). Alaska and
   Maine are the 11 Sep registers (APHA 150, MPGA 564) already being drawn. No other state had anyone
   left. Emailed rose 1,076 → 1,482 since 8 Sep. A second wave tonight would hit the one-day-per-city
   gate, so none was queued.
3. **The missing 10 Sep ruling is on record** — RUL-119 in RULINGS.md with assertions in
   rulings_check.py (it was a debt from the no-shell days).
4. **Supply probed, seven sites, no new adapter** — see SUPPLY below. Plan corrected (12 Sep para).
5. No product code changed; nothing deployed.

## WHERE THE FUNNEL LEAKS (PROBED 12 Sep 2026, /onboard/funnel?days=4)

- 34 sessions · **9 humans** (dwell) · **8 of the 9 carry no source** (direct/own visits) · the 9th is
  `coa-cold-20260911`, a same-day verification pass, not an outfitter. **0 humans from any letter.**
- Montana 9 Sep letter: 14 landed → 14 subpick → 0 dwell → 0 photos. Landing without dwelling is the
  scanner signature; treat as machines.
- The n ≥ 10 humans-from-letters threshold for taking the click→publish rate to David is NOT met.
  People open and do nothing — **the ASK is the bottleneck**, not the send count. Letter changes
  without evidence are guesswork; the A/B arms already in the send lane are the instrument.

## SUPPLY — THE ASSOCIATION LANE IS NEARLY DONE; NEXT KIND IS OFFICIAL LICENCE FILES

- Harvested + drawn: rrca, pacific, moga (MT), wyoga (WY), coa (CO), apha (AK), mpga (ME). Adapter
  shape for a new association: one dict entry in `CityLauncher/us_register_assoc.py` (list pages →
  profile regex → plain mailbox on the profile). Run via `run_us_registers.bat` (allow-listed).
- **NOT harvestable, do not re-probe:** Idaho IOGA (form) · New Mexico NMCOG (Airtable) · Utah UOGA
  (Wix; directory = Guidefitter JS app) · New York NYSOGA (Cloudflare-obfuscated mailboxes — we do not
  decode anti-bot measures) · Oregon OOGA (same) · Washington WOGA (no directory) · Colorado DPO
  licence lookup (search form) · Vermont VOGA (site down, 525) · Nevada (one contact mailbox).
- **NEXT LEAD (host-side, unverified):** Texas TREC "High Value Data Sets" — the whole real-estate
  licensee register as free bulk text files (150,000+ rows, by statute). Category estate agents,
  drawn by the agency letter. Two things must be true first: the file's columns carry a mailbox
  (check host-side — trec.texas.gov does not answer the sandbox), and RG-0346 (agency letter with a
  console CTA) is closed so the letter tells the agency story. Note TREC said its licence system is
  offline "until December 15" (portal migration) — the bulk files may or may not still publish.
- ZA: Durban 588 + PMB 525 teachers (dbe_emis) are the big pool; Tutors arm-b rides them.
- Dead ends from earlier runs still stand: USATF national finder · NY DEC guides · USATF Mid-Atlantic /
  Three Rivers / MN / OR / GA / NJ / IN · US general search scraping · orienteeringusa · skifederation ·
  americancanoe · americanhiking · adventurecycling · coloradooutfitters.org/find-an-outfitter.

## WHAT THE NEXT RUN SHOULD PICK UP

0. Sunday: put the plain-language weekly summary at the top of this file (number, what moved it, next).
1. Run the number. Read the 00:10 wave log (`CityLauncher/logs/launchday_<date>010.log`) — how
   many states still had anyone. Expect the pool to run dry within days; that is expected (RUL-103).
2. Ledger in shards + rulings check. Both were green at the end of run 11.
3. **Close RG-0346** (three agency sending letters lack the console CTA block; the send lane never
   calls /agencies/wave-prep). It is the gate on the only large register kind left (licence files).
4. Queue host-side: fetch the TREC bulk file and print its header row (a small `run_py` is fine —
   read the `.result`). Build the licence-file importer only if a mailbox column exists.
5. Still unproven as ONE walk: seller form → save → publish → visible logged out.
6. YouTube: nine films live; film 07 (Liquidation) unpublished — David's click, when he chooses.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Reading "no sendable
  prospects" as supply. Halving the batch for a "measurement week" (RG-0290). US general search
  scraping. Trusting "wave #N logged", and trusting the wave NUMBER itself.
- Reading the funnel without grading it. Running the ledger in one call — use shards or the host bat.
- Probing register sites blind: many .org hosts do not answer the sandbox at all (000). Probe with
  curl first; web_fetch reaches some the sandbox cannot.
- Retrying a dead sandbox mount more than twice. Restarting the app to cure it (proven useless).
- Two sessions at once: space deploys; one is better than two.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

None new. Film 07 is his click, when he chooses.
