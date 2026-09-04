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

Target: **20 by Fri 31 Oct 2026.**

## WHERE THE FUNNEL LEAKS (PROBED 4 Sep 2026, run 1)

- The listing floor is FIXED and locked (price-basis, invitee AI draft, first-time
  publish — all shipped 3 Sep). The outreach link opens for a stranger: HTTP 200,
  no password box, PROBED 10:36Z.
- **The constraint is now SUPPLY.** Fired the gated wave; 0 emails went out. Of 14
  city lanes: 9 had no sendable prospects, 2 were latched by stop-loss, 1 by min-gap.
- 542 of 546 emailed people got the OLD broken link. **130 of them — everyone who
  opened or clicked — now have the working link** (sent 4 Sep). About 310 who never
  opened remain uncontacted. Before today only 30 people had ever been sent a link
  that works.

## WHAT THE LAST RUN DID (4 Sep 2026, run 1)

0. **Sent the apology to 130 people** — everyone who opened or clicked an outreach email
   and met the password box. David's permission, his words, 4 Sep. New lane:
   `resend_broken_link_now.bat`. First attempt reached only 18 (wrong column); corrected
   the same run to 112 more. Nobody was sent it twice. 11 people in the first 18 had also
   had the human-clicks follow-up — that was before the never-twice guard existed and
   cannot recur.

1. Found the scoring probe reads HIGH — the contract's raw query returns 2 on the live
   server and both rows are seed records never emailed. Built the honest scorer
   (`scripts/onboarding_number.py`), locked as RG-0261.
2. Promoted RG-0239 — its check still probed `/admin.html`, the URL we stopped sending,
   so it stayed red for a fault fixed on 3 Sep.
3. Fired the gated wave, read the result, and traced every block.
4. Released the stop-loss on Pretoria, New York and Polokwane (list cleaned). Polokwane
   is GREEN; the other two clear on min-gap tomorrow.
5. Fixed WAIT-REDIR-1 (RG-0262): five allowlisted bats paced themselves with
   `timeout.exe`, which dies silently under the host queue's redirected stdin.
6. Opened RG-0263 — the supply top-up tool is locked out of our own API.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **Read what the 130 apology emails did.** Opens and clicks land in `email_events` via
   webhook. That is the first real test of a working funnel on a warm audience — measure
   it before doing anything else, then run the number.
1. The wave is eligible again from **5 Sep** (min-gap). Fire it and read the result.
2. RG-0263: `LAUNCH_API_KEY` was never provisioned, so `fill_wave_gaps.py` 401s and the
   nine empty pools cannot be topped up through the API. Until it is live, supply must
   come from `run_local_scraper.bat`. Provisioning needs a production restart — do it
   when someone is watching, and never by weakening the fail-closed gate.
3. Still unproven as ONE walk: seller form → save listing → publish → visible logged out.
   Build it as a composite probe; do not create a listing (§3 bars it).

## THINGS ALREADY TRIED THAT DID NOT WORK

- Opening `/admin.html` publicly to fix the CTA (1 Sep) — exposed the admin console and
  its delete control; rolled back in 76 seconds. The fix is the LINK, never the gate.
- `fill_wave_gaps.py` via the host queue (4 Sep) — HTTP 401, see RG-0263. Do not retry
  until the key is provisioned; it will fail the same way.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

1. ~~Re-mail the people whose link was broken?~~ **ANSWERED 4 Sep 2026** — David: *"i think
   we should at least resend the ones that did open their emails?"* Done: 130 sent.
   The ~310 who only RECEIVED the broken email (never opened it) are still uncontacted;
   that is a wider send than his words covered, so it stays unasked until there is
   evidence the warm 130 convert.
