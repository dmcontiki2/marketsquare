# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Under 100 lines: it is a state file, not a
diary — the changelog is the diary.*

---

## SUNDAY SUMMARY — 13 Sep 2026 (plain language)

**The number is still 0 of 20.** Nobody we emailed has published a listing yet. 6,748 people are on
the list and 1,482 have been emailed. **What moved this week:** the US outfitter letters went out
every night until Friday, then stopped — not because the list ran dry, but because a session on
Friday morning switched off every US, UK and Australian city, reading a document heading rule
against three of David's earlier decisions. Found and reversed tonight; 854 people in Maine, Alaska,
Montana and Colorado are sendable again, and the re-run wave sent **108 letters** at 01:31 (0 failed). **Next:** watch the funnel for
the first real person from a letter, and find the next member directory that publishes mailboxes —
the Texas licence file turned out to have no email column.

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If the sandbox is dead, run it host-side: queue `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-09/10 (runs 8–10) | **unknown** | — | — | NOT MEASURED: sandbox dead (KB5124008) |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed · 5 registered |
| 2026-09-13 (run 12, 01:00 SAST) | **0** | 0 | 0 | 6,748 · 1,482 emailed at 01:00, +108 at 01:31 (re-armed wave) · 5 registered |

Target: **20 by Fri 31 Oct 2026.** Model: runs 5–8, 11, 12 Fable 5.1; runs 9–10 Opus 5 (drift, RUL-096h).

## WHAT RUN 12 DID (13 Sep 2026, 01:00–01:50 SAST, Fable 5.1)

1. **Measured.** Number 0, both probes agree. Fact board green (every locked fix holding, 22 open);
   rulings 0 fail. Sandbox alive.
2. **Found why the 13 Sep 00:10 wave sent nothing.** Log: "no armed city has anyone to send to".
   Cause: at 06:17 on 12 Sep a session disarmed all 72 US/UK/AU wave entries (11 US cities, 5 UK,
   4 AU, 52 US state buckets) executing the jurisdiction gate (RG-0215) because the US/UK/AU law
   research sat in an APPENDIX of OUTREACH_LAW, not under a `##` heading. That contradicted RUL-071
   (cities.json lane=outreach for every US/UK/AU city), RUL-074 ("all three countries are
   outreach-covered per the 20 Aug law notes"), RUL-082 and RUL-059. Nothing legal changed.
3. **Fixed as a class, then re-armed (JURIS-RULED-1).** US/UK/AU promoted to ruled sections 10–12
   of the law notes (text unchanged); RG-0215 now reads localize._CITY_COUNTRY so state buckets are
   judged, not "unknown"; 72 entries re-armed and stamped `rearmed_by`; new LOCKED RG-0361 goes red
   if the gate and the rulings disagree again (sabotage-tested against the 12 Sep policy); RUL-074
   reflection added to rulings_check. PROBED before re-arming: US render carries identity, reg no.,
   street postal address, why-received, source line, unsubscribe; GB/AU identity + why-received +
   unsubscribe; test_intl_templates.py ALL PASS.
4. **Pool after re-arm (chokepoint count): 854** — Maine 536, Alaska 137, Montana 118, Colorado 63.
   Every other armed city 0. Wave queued 01:25, RAN 01:31–01:35 SAST: **108 sent, 0 failed** — Alaska 24
   (wave 3), Colorado 48 (wave 4, ramp doubled), Maine 24 (wave 4), Montana 12 (wave 6, reset by a dirty wave).
5. **Texas TREC lead is DEAD** (probed data.texas.gov s7ft-44qi: 20 columns, no email — stripped by
   statute). Plan corrected (13 Sep para). The sandbox CAN read Socrata portals (data.<state>.gov).
6. No product code changed; nothing deployed. No ruling from David this run (unattended).

## WHERE THE FUNNEL LEAKS (PROBED 12 Sep 2026, /onboard/funnel?days=4 — not re-read tonight)

- 34 sessions · 9 humans · **0 humans from any letter.** People open and do nothing — the ASK is the
  bottleneck. The n ≥ 10 humans-from-letters threshold for taking click→publish to David is NOT met.

## SUPPLY — ASSOCIATION LANE NEARLY DONE; LICENCE FILES CARRY NO MAILBOX

- Harvested + drawn: rrca, pacific, moga, wyoga, coa, apha, mpga. New association = one dict entry in
  `CityLauncher/us_register_assoc.py`; run via `run_us_registers.bat`. ZA Durban/PMB rows = blocked category, 0 sendable.
- **NOT harvestable, do not re-probe:** Idaho IOGA (form) · NM NMCOG (Airtable) · Utah UOGA (Wix/
  Guidefitter) · NY NYSOGA + Oregon OOGA (Cloudflare-obfuscated) · WA WOGA (no directory) · Colorado
  DPO lookup (form) · Vermont VOGA (525) · Nevada (one mailbox) · **Texas TREC file (no email column)**
  · Idaho IOGLB board site (000 from sandbox) · Oregon Marine Board guide search (404) · Alaska CBPL
  licence search (403) · Wyoming board home page (200, no mailboxes on the front page — a list page may exist).
- **Working kinds:** member directories that PUBLISH a mailbox. Untested leads of that kind: US Forest
  Service outfitter-guide permit-holder lists (per-forest PDFs, often with email); chamber-of-commerce
  member directories (GrowthZone/ChamberMaster pages are server-rendered); state fly-fishing / hunting
  guide associations not yet probed (AZ, NV, SD, ND, NE, KS, OK, AR, MO, MN, WI, MI, PA, VA, NC, TN).
- Older dead ends stand: USATF finder/regionals · NY DEC guides · US search scraping · orienteeringusa
  · skifederation · americancanoe · americanhiking · adventurecycling · coloradooutfitters.org.

## WHAT THE NEXT RUN SHOULD PICK UP

1. Run the number. Read `CityLauncher/logs/launchday_14Mon09_2026010.log` — the per-city gap counts
   LOCAL CALENDAR DAYS (MIN-GAP-1), so the 14 Sep 00:10 wave should send again in ME/AK/MT/CO. Read it.
2. Ledger in shards + rulings check. Both green at the end of run 12 (RG-0361 new, locked).
3. Read /onboard/funnel?days=3 for the first human from a letter (grade it: dwell + touch).
4. Supply: probe ONE untested kind above (USFS permittee PDFs or a chamber directory) with curl first;
   build an adapter only if mailboxes render.
5. RG-0346 (agency letters lack the console CTA) — still open; agency sends are David's per-send act
   (RUL-053f), so it adds no nightly volume. Lower priority than 3–4.
6. Still unproven as ONE walk: seller form → save → publish → visible logged out. 7. YouTube: film 07
   (Liquidation) unpublished — David's click, when he chooses.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly. `fill_wave_gaps.py` via the queue (401). Reading "no sendable
  prospects" as supply (13 Sep: it was a DISARM — check `armed`/`gates_green` in waves_policy.json and
  any `disarmed_by` stamp FIRST). Halving the batch for a "measurement week" (RG-0290). US general
  search scraping. Trusting "wave #N logged". Running the ledger in one call — use shards.
- Probing register sites blind: many .org/.gov hosts do not answer the sandbox (000). Curl first.
- Retrying a dead sandbox mount more than twice; restarting the app to cure it (proven useless).
  Assuming an official licence file carries a mailbox (Texas: it does not).

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

None new. The US/UK/AU re-arm is reported with the veto stated; film 07 is his click, when he chooses.
