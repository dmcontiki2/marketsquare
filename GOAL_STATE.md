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

Target: **20 by Fri 31 Oct 2026.**

## WHERE THE FUNNEL LEAKS (PROBED 5 Sep 2026, run 2)

- The listing floor is fixed and locked. That is not the constraint.
- **The constraint was never supply — it was reach.** 9 of 14 lanes reported empty
  yesterday. They were not empty: `Services` (482 rows, 443 never contacted) was
  missing from `agency_categories`, so the planner could not see the lane at all.
  Fixed. **13 of 14 lanes now sendable, 93 guard-clean individuals** (was 5).
- **We had been mailing the wrong kind of recipient.** `Services` and
  `us_university_tutors` were not person-only, so 11 real emails went to university
  front desks at 00:13 today. Both are person-only now.
- `teachers_trainers` (1,509 rows) is **a list of schools, not teachers** — 1,194 of
  the 1,235 that pass every address guard are named "… Primary School". It stays
  blocked. Do not reopen this; the measurement is in the policy note.
- 133 invitations carried the **wrong city** (all "Pretoria"). Row now wins; 114 of
  the 133 had not been mailed yet, so most are repaired before first contact.

## WHAT THE LAST RUN DID (5 Sep 2026, run 2)

1. SUPPLY-SERVICES-1 + PERSON-ONLY-3 (RG-0272) — opened the Services lane and made
   both individual lanes person-only. 5 sendable → 93.
2. ORG-NAME-1 (RG-0270) — organisations held by NAME on person-only lanes. Upheld
   the teachers block **with** the measurement the 3 Sep note lacked.
3. MAGICLINK-CITY-1 (RG-0271) — the prospect row beats a scraper's baked-in city.
4. STOPLOSS-DISCOVER-1 (RG-0273) — the stop-loss cleaner asks which cities are
   latched instead of naming three that were released two days ago; also removed a
   waiting prompt that would have hung the unattended agent.
5. MEASURE-RATE-1 — `batch_size` 12 → 6 for the measurement week, so night one is
   ~62 not ~93. **Restore to 12 at Phase 3 (18 Sep).**
6. Queued the stop-loss clean for Cape Town, Durban, Port Elizabeth, Pietermaritzburg.

## PHASE 1 MEASUREMENT (the 130 apology recipients)

| | |
|---|---|
| apology emails sent 4 Sep | 130 |
| opened 4 Sep | 98 |
| raw click events 4 Sep | 31 |
| **distinct real people who clicked** | **2** |
| any events on 5 Sep | none |
| published | **0** |

Click→publish is still unmeasured. Two clicks is not a sample. **Tonight's ~62 sends
are the first wave ever aimed at individuals rather than desks and schools — they are
the real experiment.** Read them in the morning before doing anything else.

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
