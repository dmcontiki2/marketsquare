# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST, before anything else. It exists so a fresh session costs a few
hundred tokens to orient instead of thousands. Update it at the END of every run.
Keep it under 60 lines: it is a state file, not a diary. The changelog is the diary.*

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`

| date | published by own hand | probe A (prospects.db) | probe B (public site) | notes |
|------|----------------------|------------------------|------------------------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline, set at handover |
| 2026-09-04 (run 1) | **0** | 0 | 0 | raw query says 2 — both are seed rows, barred by §3 |

Target: **20 by Fri 31 Oct 2026.**

## WHERE THE FUNNEL LEAKS (PROBED 4 Sep 2026, run 1)

- The floor is FIXED and locked: price-basis 422, invitee AI draft 401, and the
  first-time-publish 403 all shipped 3 Sep. RG-0249 / RG-0250 / RG-0253 green.
- The outreach link opens for a stranger — PROBED 4 Sep 10:36Z, HTTP 200, no
  password box. RG-0239 promoted to LOCKED (its check had been probing the wrong URL).
- **The real leak is now supply, not plumbing.** 542 of the 546 people we emailed got
  the OLD link — a browser username/password box. None has been re-mailed. Only
  **30 people have ever been sent a working link.**
- Of 64 recorded clicks only **2** score as real human clicks; the rest are scanners.
  The funnel has never actually been exercised by people.

## WHAT THE LAST RUN DID (4 Sep 2026, run 1)

1. Found the scoring probe reads HIGH: the contract's raw query returns 2 on the live
   server, and both rows are `e2e_test` seed records never emailed by us. Built
   `scripts/onboarding_number.py` — the honest scorer — and locked it with RG-0261.
2. Promoted RG-0239. Its assertion still probed `/admin.html`, the URL we deliberately
   stopped sending, so it stayed red for a fault fixed on 3 Sep. Repointed at the CTA
   the emailer actually builds; kept the console-gated leg.
3. Queued the gated wave (`launch_day_wave.bat`) to put the repaired funnel in front
   of fresh prospects.

## WHAT THE NEXT RUN SHOULD PICK UP

1. Read `host_queue/done/20260904-104629_run_bat_launch_day_wave.result` — did the wave
   fire, and how many went?
2. If David has answered the re-mail question below, run the broken-link resend.
3. Still unproven as ONE walk: seller form → save listing → publish → visible logged out.
   The three gates are each green against live, but nobody has walked the whole path.
   It cannot be walked by creating a listing (§3 bars that) — build it as a composite
   probe over the existing live checks.

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly to fix the CTA (1 Sep) — exposed the admin console
  and its delete control; rolled back in 76 seconds. The fix is the LINK, never the gate.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

1. **Re-mail the 441 people whose link was broken?** `CityLauncher/resend_broken_link.py`
   is built, honours every send guard, and defaults to a dry run. It is not on the
   allowlist, so it needs his word. Asked 4 Sep 2026.
