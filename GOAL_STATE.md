# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST, before anything else. It exists so a fresh session costs a few
hundred tokens to orient instead of thousands. Update it at the END of every run.
Keep it under 60 lines: it is a state file, not a diary. The changelog is the diary.*

---

## THE NUMBER

| date | published by own hand | probe A (prospects.db) | probe B (public site) | notes |
|------|----------------------|------------------------|------------------------|-------|
| 2026-09-04 | **0** | 0 | 0 | baseline, set at handover |

Target: **20 by Fri 31 Oct 2026.**

## WHERE THE FUNNEL LEAKS (as at handover, 4 Sep 2026)

- 3,805 prospects · 546 emailed · 61 clicked · **0 published**.
- Self-serve listing impossible since 22 Jul (422 price-basis). Fix on disk, unshipped — RG-0249.
- Invitees never received the AI draft (401 gate). Fix on disk, unshipped — RG-0250.
- `outreach_campaigns` and `onboard_events` are empty. Conversion has never been counted,
  only inferred. `reconcile_conversions()` exists in CityLauncher/api/server.py, undeployed — RG-0244.

**The floor is broken. Do not open the tap until an end-to-end pass is PROVED.**

## WHAT THE LAST RUN DID

(nothing yet — first run is Sat 5 Sep 01:00)

## WHAT THE NEXT RUN SHOULD PICK UP

1. Ship the two listing fixes (RG-0249, RG-0250) via `scripts/request_deploy.py`, read the result.
2. Prove one real end-to-end pass: cold link → sign in → create listing → visible logged out.
3. Only then look at volume.

## THINGS ALREADY TRIED THAT DID NOT WORK

(empty — add one line each time, so no future run repeats a dead end)

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

(empty)
