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
| 2026-09-06 (run 5) | **0** | 0 | 0 | 4,470 on the list · 570 emailed · 5 registered |
| 2026-09-07 (run 6) | **0** | 0 | 0 | 5,639 on the list · 845 emailed · 5 registered |
| 2026-09-08 (run 7, 01:03) | **0** | 0 | 0 | 5,838 on the list (5,928 after the Wyoming import) · 1,076 emailed · 5 registered |
| 2026-09-09 (run 8, 06:15) | **unknown** | — | — | NOT MEASURED: sandbox shell failed to mount, no probe possible. Last probed 0 (8 Sep). |

Target: **20 by Fri 31 Oct 2026.** Model on runs 5–8: Fable 5.1 (as David asked, RUL-096h).

## WHERE THE FUNNEL LEAKS (PROBED 8 Sep 2026)

- Graded funnel (`GET /onboard/funnel?days=2`): 21 sessions, **1 human** (no src — organic), **0 humans
  from any letter**. The "photos" hits (Ohio, Texas, Wisconsin…) land 20–40 s after the send with no
  dwell — the scanner pattern. Denominator n=1: no click→publish rate exists yet. Take it to David
  only at n ≥ 10 humans.
- Email side (server, graded, 4 days): 914 sent · 5.3% bounced · 13.2% human opens · **2 human
  clicks (0.23%)** · 0 signed. People open and do nothing — the ASK is the bottleneck. Arm 'b'
  (shorter ask, no money) is armed for Tutors; the new outfitter letter carries no money ask either.

## WHAT RUN 8 DID (9 Sep 2026, 06:15–07:00 SAST — a crippled run; run 7 detail is in the changelog)

1. **The PC slept through the night.** The host 00:10 DailyWave left NO `launchday_09Wed09_*.log`, and
   this session fired at 06:15 instead of 01:03. Two misses, one cause. Not yet a ledger entry (no shell).
2. **No sandbox shell** (mount failed 3×, identical). No number, no ledger, no rulings_check, no
   heredoc writes. Only file reads, tiny verified Writes, web_fetch (provenance-limited) and Chrome.
3. **Re-queued the wave by hand:** `host_queue/20260909-042000-000_…launch-day-wave.req` and
   `…-042100-000_…run-us-registers.req` (five-line format, allowlisted, read back complete). Worker
   was alive at 8 Sep 17:51. Result files were NOT in when this run ended — next run reads them first.
4. **COA-1 found, drafted, not wired:** Colorado Outfitters Association = open register, 92 profiles
   via `/wp-json/wp/v2/outfitter?per_page=100`, mailbox on each profile page (`Email:` label).
   Adapter draft: `CityLauncher/us_registers/coa_adapter_DRAFT.py` (Wyoming shape, splice notes inside).
5. Run 7 (8 Sep) for the record: 254 real sends · WAVE-COUNTER-1 fixed the wave numbering (ramp can
   now reach 48) · outfitter letter live · Wyoming +90 imported · ledger 328 / 0 regressed / 21 open.

## SUPPLY (measured 8 Sep, server)

- **usatf-new-england is dead supply:** 25 sent, 7 bounced (28%), personal mailboxes on live domains
  (cox.net, aol, yahoo) — MX cleaning cannot rescue it. SOURCE-QUALITY-1 holds the source from
  tomorrow, parking Massachusetts' 213. Correct. Do not build a release for it.
- US club lane left: rrca 292 (2.1% bounce) + usatf-pacific 40 ≈ 330 → **dry ~9–10 Sep**.
- Outfitters: Montana 199 (drawn from tonight), Wyoming 90 (imported 01:51, drawn from tonight). Same pattern next:
  state outfitter/guide associations that publish members WITH mailboxes. Probe them with
  `web_fetch` (sandbox curl is proxy-blocked for most .org sites); write the adapter text-based
  like `_wyoga`; harvest host-side via the bat; read the `.result` before claiming an import.
- ZA: Pretoria club:agn is source-held (3/24 = 12.5%). Durban 588 + PMB 525 teachers (dbe_emis)
  are the big ZA pool; Tutors arm-b rides them.
- Dead ends (do not re-check): USATF national finder; NY DEC guides; USATF Mid-Atlantic / Three
  Rivers / MN / OR / GA / NJ / IN; US general search scraping; orienteeringusa; skifederation;
  americancanoe; americanhiking; adventurecycling; Idaho IOGA (404s); coloradooutfitters.org
  /find-an-outfitter (404 — the live page is /find-your-outfitter/, unprobed).

## WHAT THE NEXT RUN SHOULD PICK UP

0. Read `host_queue/done/20260909-042000-000_*.result` and `…042100-000_*.result` (the hand-queued
   9 Sep wave + register run). If the wave never ran, the 9 Sep send-day was lost — queue it again.
1. Run the number. Newest `logs/launchday_*.log`: `EMAILER CRASHED` = 0; confirm the doublings to 48
   happened where days were clean (MA/FL/MI/IL) — the first proof the ramp works; confirm Montana
   drew adventures_experiences under the outfitter letter and `visuals/letters/` gained a file.
2. `GET /onboard/funnel?days=2` — humans, and which step. Still n<10 → no rate claim.
3. Ledger in shards (`--shard=k/3`, `--combine=3`); rulings_check. Add: OPEN entry "DailyWave did not
   fire while the PC slept (9 Sep)" — check the Task Scheduler wake setting and last-run result host-side.
4. **Wire COA-1** from `us_registers/coa_adapter_DRAFT.py` (heredoc into `us_register_reader.py` +
   `run_us_registers.bat`), py_compile, queue the bat, read the result, ledger entry. Then next
   register: Alaska APHA, New Mexico NMCOG, Oregon OGA, Utah — probe via David's Chrome (JSON
   endpoints often sit under `/wp-json/wp/v2/types` on WordPress directories).
5. Still unproven as ONE walk: seller form → save → publish → visible logged out (publish_ok).
6. YouTube: nine films live. Film 07 Liquidation unpublished — David's click, when he chooses.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly (1 Sep). `fill_wave_gaps.py` via the queue (401, RG-0263).
  Reading "no sendable prospects" as supply (4 Sep). Halving the batch for a "measurement week"
  (5 Sep, RG-0290). US general search scraping (5 Sep). Trusting "wave #N logged" (6 Sep) — and
  trusting the wave NUMBER itself (8 Sep: it was 1 for ever).
- Reading the funnel without grading it (6 Sep). Running the ledger in one call (7 Sep) — use shards.
  Running `wave_runner --plan` from the sandbox (8 Sep): 122 cities over FUSE exceeds the call cap;
  call `city_stats`/`ramp_state` for named cities instead.
- Probing register sites with sandbox curl (8 Sep): most .org hosts return a 143-byte proxy 404.
- Two sessions at once: space deploys; one is better than two.
- Retrying a dead sandbox mount more than twice (9 Sep): identical error each time. Fall back to file
  reads + Chrome + hand-written `.req` files; put the ledger/number work on the next run.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

None this run. Film 07 (Liquidation) is the only unpublished film — his click, when he chooses.
