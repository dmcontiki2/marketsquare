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

Target: **20 by Fri 31 Oct 2026.** Model on runs 5–7: Fable 5.1 (as David asked, RUL-096h).

## WHERE THE FUNNEL LEAKS (PROBED 8 Sep 2026)

- Graded funnel (`GET /onboard/funnel?days=2`): 21 sessions, **1 human** (no src — organic), **0 humans
  from any letter**. The "photos" hits (Ohio, Texas, Wisconsin…) land 20–40 s after the send with no
  dwell — the scanner pattern. Denominator n=1: no click→publish rate exists yet. Take it to David
  only at n ≥ 10 humans.
- Email side (server, graded, 4 days): 914 sent · 5.3% bounced · 13.2% human opens · **2 human
  clicks (0.23%)** · 0 signed. People open and do nothing — the ASK is the bottleneck. Arm 'b'
  (shorter ask, no money) is armed for Tutors; the new outfitter letter carries no money ask either.

## WHAT RUN 7 DID (8 Sep 2026, 01:03–02:15 SAST)

1. Read the 00:10 wave: **254 real sends, 0 crashes**. All 17 remaining states got wave #1; Cape
   Town + N.Cal/Cal/FL/GA/IL/MA/MI wave #2; cap hit at 254 (47 dry-ran). Bounces on tonight's 254 so
   far: 14 (5.5%); domain since the 6 Sep clean 22/505 = 4.36% (gate 5%).
2. **WAVE-COUNTER-1 (RG-0339 LOCKED):** `email_events.wave_number` has DEFAULT 1, so the runner's
   `IS NULL` stamp never matched — 1,486 sent events, ALL wave 1, every city "wave #2" for ever.
   Ramp structurally capped at 24; stop-loss judged cumulative bounces; Cape Town's release for
   "wave 1" matched permanently. Fixed: a wave = one city's sends on one send-day (derived from
   created_at, no DB write); stamp unconditional; clean_city_list uses the same counter. Tomorrow:
   MA/FL/MI/IL earn 48; Pretoria (12/3), Rhode Island (4/12), Vermont (3/12) hold on their own data.
3. **REGISTER-LETTER-1 (RG-0317 LOCKED):** `adventures_outfitter_outreach.html` in the club letter's
   RUL-099 shape; `template_key_for()` routes `register:*` rows to `<category>:register` for letter
   and subject; Montana + Wyoming draw adventures_experiences. Montana composes 12 tonight.
4. **LETTER-FILE-1 (RG-0340):** RUL-099(e) was never built — `visuals/letters/` held only a README.
   The send lane now files one copy per letter shape × country per day. Preview filed.
5. RUL-104 finally in the club letter; David then ruled the origin out too (RUL-110): all three
   letters open with "a global marketplace" and rulings_check asserts the absence. RG-0326 promoted (a session passed the photo screen).
6. **WYOGA-1:** Wyoming outfitters adapter written; host run 01:51 SAST read 95 listings, 94 with a
   mailbox, **+90 imported** (result file read). wyoga.org is NOT reachable from the sandbox — host-side only.
7. Commits pushed via the queue at 01:51 (both repos, rc=0). Ledger after: 328 · 0 regressed · 21 open.

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

0. Check `host_queue/worker_log.txt` for a RUN without a DONE before opening prospects.db.
1. Run the number. Newest `logs/launchday_*.log`: `EMAILER CRASHED` = 0; confirm the doublings to 48
   happened where days were clean (MA/FL/MI/IL) — the first proof the ramp works; confirm Montana
   drew adventures_experiences under the outfitter letter and `visuals/letters/` gained a file.
2. `GET /onboard/funnel?days=2` — humans, and which step. Still n<10 → no rate claim.
3. Ledger in shards (`--shard=k/3`, `--combine=3`); rulings_check.
4. Next register: Colorado Outfitters (`/find-your-outfitter/`), Alaska APHA, New Mexico NMCOG,
   Oregon OGA, Utah — via web_fetch; one adapter per run is enough.
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

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

None this run. Film 07 (Liquidation) is the only unpublished film — his click, when he chooses.
