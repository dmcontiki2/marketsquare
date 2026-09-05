# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST, before anything else. It exists so a fresh session costs a few
hundred tokens to orient instead of thousands. Update it at the END of every run.
Keep it under 60 lines: it is a state file, not a diary. The changelog is the diary.*

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline, set at handover |
| 2026-09-04 (run 1) | **0** | 0 | 0 | raw query says 2 — both seed rows, barred by §3 |
| 2026-09-05 (run 2) | **0** | 0 | 0 | raw still 2, same two seeds; no new clicks on the 5th |
| 2026-09-05 (run 3) | **0** | 0 | 0 | after the 129-person global wave — too early to show |

Target: **20 by Fri 31 Oct 2026.**

## WHERE THE FUNNEL LEAKS (PROBED 5 Sep 2026, run 3)

- The listing floor is fixed and locked; the live app answers in under half a second.
- **The constraint was never supply — it was REACH.** Every gap was one list not
  matching another, failing silently. Fixed today: the Services lane, 7 armed US
  cities with no line in the wave script, 19 unknown cities, the club lane, and
  4 letters drawable by nothing. **43 cities now, was 14.**
- **Reachable universe: 1,441 people** — 864 individuals + 577 clubs (imported today).
- **France and Portugal are OUT — David ruled it 5 Sep (RUL-101).** Measured first: of
  the 179, only 35 are business addresses that could ever be cold-emailed lawfully; the
  other 65 clean ones are personal mailboxes needing opt-in. A representative costs
  €490–€1,000/yr to unlock 35 people. Do not re-propose it as an emailing cost — it
  returns only as a market decision. Do not set TS_EU_REPRESENTATIVE without a ruling.
- `teachers_trainers` stays blocked: 1,194 of its 1,235 clean rows are named schools.

## WHAT RUN 3 DID (5 Sep 2026)

1. **SENT 129 emails to 38 cities in 6 countries** — ZA, US, GB, AU, NZ, AR. 0 failed,
   0 skipped. New York correctly held by its one-day gap. First ever sends to
   Argentina, New Zealand, and 7 US and 4 UK cities.
2. Imported **577 club contacts** (Pretoria 366, Cape Town 211) — they had sat in CSVs
   since 4 Sep with no importer, no category and no lane.
3. The wave and the stop-loss cleaner now ASK the policy which cities to visit instead
   of naming them in a .bat. Adding a city to the policy is now enough.
4. Country NAMES resolve to codes; the clearance fence is untouched.
5. Rewrote ONBOARDING_PLAN.md — the old one still claimed a supply shortage a day after
   it was disproved. It now carries the rule that a plan is edited in the session whose
   measurement contradicts it.
6. Retired the measure-only calendar. **Gates, not calendars** — a send waits for a real
   gate and nothing else. The 6-per-city batch cap is the restraint.

## PHASE 1 MEASUREMENT (the 130 apology recipients)

| | |
|---|---|
| apology emails sent 4 Sep | 130 |
| opened 4 Sep | 98 |
| raw click events 4 Sep | 31 |
| **distinct real people who clicked** | **2** |
| any events on 5 Sep | none |
| published | **0** |

Click→publish is still unmeasured. Two clicks is not a sample. **Today's 129 sends are the real
experiment** — the first wave ever aimed at individuals rather than desks and schools,
and the first outside South Africa's neighbours. Read them before doing anything else.

## THE PLAN

`MarketSquare/ONBOARDING_PLAN.md`. Phase 1 (to 11 Sep) is MEASURE ONLY. The decision
gate is at the end of Phase 1. We have roughly one pass through the list.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **Read the 00:10 wave log** (`CityLauncher/logs/launchday_06Sun09_*.log`) and the
   result of the queued stop-loss clean in `MarketSquare/host_queue/done/`. Then run
   the number. Then read opens/clicks for the ~62.
1. ~~The host agent looked dead at the end of run 2~~ — **it was not, and the
   instrument was wrong, not the agent.** All three requests ran at 01:51 SAST, rc=0,
   18 minutes after being queued. The agent only writes to its log when it has work,
   so silence meant an empty queue. Fixed both halves: the agent now stamps a
   heartbeat every tick, and the check judges how long a *request* has waited.
   **Do not read log silence as a dead agent.**
2. The stop-loss clean ran and **released all four latched cities** (probed 08:50
   SAST). 12 of 14 lanes pass; New York clears its one-day gap tonight.
2. RG-0263 (`LAUNCH_API_KEY`) is **no longer the supply blocker** and should not be
   treated as urgent. Supply exists; it was reach that was broken.
3. Still unproven as ONE walk: seller form → save → publish → visible logged out.
   Build it as a composite probe; do not create a listing (§3 bars it).
4. Tomorrow is Sunday — add the plain-language summary at the top of this file.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly to fix the CTA (1 Sep) — exposed the admin console;
  rolled back in 76 seconds. The fix is the LINK, never the gate.
- `fill_wave_gaps.py` via the host queue (4 Sep) — HTTP 401, RG-0263. Do not retry
  until the key is provisioned; it will fail the same way.
- Reading "no sendable prospects" as a supply problem (4 Sep) — it was a reach
  problem, and a session was spent scraping for supply we already had. Check whether
  the planner can SEE a lane before concluding the lane is empty.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

1. ~~Re-mail the people whose link was broken?~~ **ANSWERED 4 Sep** — 130 sent. The
   ~310 who only received the broken email are still uncontacted; that is a wider
   send than his words covered, so it stays unasked until the warm 130 show a rate.

**Nothing else is waiting on him.** No clicks, no approvals, no decisions.
