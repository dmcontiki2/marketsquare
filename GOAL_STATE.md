# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Keep it short: it is a state file, not a
diary. Durable background lives in `GOAL_FACTS.md` — read that when you need the why.*

---

## SUNDAY SUMMARY — written by run 22, Sunday 27 September 2026

**The number is 0.** Both probes agree: nobody we contacted cold has published a listing.
Thirty-four days left.

**Last night the whole campaign sent one letter.** Not twelve, not thirteen. One — to an estate
agent in Bloemfontein. That is not a fault; it is the first honest night we have had. Fixing
*which places we write to* two nights ago took away the thousands of American addresses that
could never have published anything, and what was left underneath turned out to be very small.
Most of this week was spent finding out how small, and why.

**The list is not what we thought it was, in two specific ways.**

*First, the teachers.* Last Sunday you were told the biggest thing standing between us and
sellers was a decision only you could make — 1,114 South African teachers sitting on our list,
held back by a privacy ruling. That was wrong and I am sorry it reached you in that form. Those
1,114 rows are not teachers. They are **schools** — the name on the row is "Dalibo Primary
School", the address is the school's own office mailbox. And they are held by two separate
things, not one: the privacy ruling you were being asked about, and a completely independent
rule that refuses to cold-mail an organisation rather than a person. **Lifting the privacy
ruling would release none of them.** You can take that decision off your desk; it was never
worth the weight it was given. Worse, we already knew: someone wrote that same measurement down
on 5 September and the board that should have shown it to me had been printing a blank.

*Second, we have been mailing addresses that were never real.* One of our sources, property24,
takes an estate agent's name and their agency's web address and **makes up an email address from
them** — first name, dot, surname, at the agency. It says so in its own notes. Of the twelve such
letters we have sent, **eight bounced**. The agency domains are genuine, which is why last week's
health check pronounced the whole South African list 96% clean: you cannot tell an invented
mailbox from a real one by checking the domain. Those invented addresses were sitting at the top
of the queue in Durban, Port Elizabeth, Cape Town and Johannesburg, they are what silently
switched Cape Town and Port Elizabeth off eight days ago, and they were about to be most of what
we sent for the next fortnight. They are now held. The invented-address habit itself is written
down as still to fix.

**So what is actually left?** Across every South African city we have armed: about **twenty**
addresses we can honestly write to, nearly all in Pretoria. Not thousands, not the 96 I reported
on Friday. Twenty.

**The plain conclusion, five weeks early rather than on the last day: twenty sellers by 31
October cannot come from this list.** Nothing is wrong with the letter — of the people we can
prove read one, about one in four clicked it. Nothing is now wrong with the journey — it was
repaired on 24 September. What we do not have is people to ask. Every hour spent on copy,
timing or the funnel from here is an hour spent on the wrong end of the problem.

**What is next, in one line:** the 1,091 schools are worthless to us as sellers and genuinely
valuable as *employers* — a school employs the cleaners, groundskeepers and assistants the Quick
door was built for — and the enrolment door for exactly that is being built in the other lane
this week; the measurement goes to it on Monday rather than a second cold-mail attempt at the
same 1,091 front offices.

**Nothing on this goal needs a decision from you.** The one question that was at the top of your
list last week has been withdrawn.

---

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If SSH is dead, queue it host-side: `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed |
| 2026-09-13 (run 12) | **0** | 0 | 0 | 1,482 emailed at 01:00, +108 at 01:31 |
| 2026-09-18 (runs 13–14) | **0** | 0 | 0 | 2,491 emailed · **8 human clicks ever** · first full journey walked |
| 2026-09-19 (run 15) | **0** | 0 | 0 | 2,499 emailed · listing 382 still a draft |
| 2026-09-20 (run 16) | **0** | 0 | 0 | 2,499 emailed (pause held) · **466 sendable left** |
| 2026-09-23 (run 17) | **0** | 0 | 0 | 2,549 emailed · **"45 registered" was 1** |
| 2026-09-24 (run 18, 02:51) | **0** | 0 | 0 | 2,573 emailed · funnel reads 5 registered (4 e2e_test + Rick) |
| 2026-09-24 (run 19, 03:40–04:45) | **0** | 0 | 0 | raw 3, all e2e_test · **the letter to Rick has gone** · publish journey walked green end to end |
| 2026-09-24 (run 20, 23:07–00:10) | **0** | 0 | 0 | 2,574 emailed · **the "331 human opens" were 34** · 9 clicks |
| 2026-09-26 (run 21, 04:15–05:30) | **0** | 0 | 0 | 2,587 emailed · **1,499 of 1,911 US letters had no home on the site** · ZA pool MX-cleaned |
| 2026-09-27 (run 22, 23:07–00:15) | **0** | 0 | 0 | 2,588 emailed — **the 26 Sep wave sent ONE letter** · **true sendable ZA pool ≈ 20** · a source was inventing addresses · D8 withdrawn |

Target: **20 by Fri 31 Oct 2026** — 34 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–22 Opus 5.

## WHAT RUN 22 DID (26–27 Sep 2026, from 23:07 UTC, Opus 5)

0. **Boards FIRST this time** (run 21's own deviation, corrected). Pre-work: `rulings_check`
   150 rulings, **0 FAIL**, 25 WARN. Ledger, 6 shards combined: **493 entries · 472 holding ·
   1 REGRESSED · 20 open · 0 ready to lock · 0 UNVERIFIED.** The single red is **RG-0373**,
   carried from run 20 and not ours (trust plan step 4 offers a referral signal nothing tracks).

1. **THE REACHABILITY GATE WORKS — confirmed on the box, which was the one handover item.**
   The 22:10 UTC wave visited **Pretoria, Cape Town, Bloemfontein** and no American state.
   **And it sent exactly one letter.** Pretoria (12 queued) and Cape Town were held in DRY-RUN
   by stop-loss; only Bloemfontein sent, one estate agent. So the fix did what it promised and
   immediately exposed what it was hiding.

2. **THE SIXTH NUMBER THAT READ HIGH, and this one had already been measured correctly once and
   then lost — RG-0508 HELD-BLIND-1.** `held_by_guard()` promises "so a shrunken pool is never
   a mystery" and applied the source-quality clause and `category IN (...)` **in its own query**,
   so a row held by SOURCE-QUALITY-1 or by a blocked category was filtered out before anything
   counted it. MEASURED across the twelve armed ZA cities: **2,248 scraped rows, 97 pass every
   guard, and the census returned an EMPTY DICT for eleven of the twelve.** Pretoria printed
   "sendable 20" with 352 rows held and no explanation; Durban printed "sendable 0, held {}"
   over 633 rows. **That blindness is what produced run 21's D8 paragraph**, which told David the
   teachers register was "held only by a POPIA ruling, not by anything technical" and was "92% of
   the entire remaining reachable South African list". Both halves wrong: **1,091 of the 1,114 are
   ALSO held by ORG-NAME-1 because they are schools** (name == business_name == "<X> Primary
   School"), so lifting the ruling releases none of them — and PERSON-ONLY-1's own note had
   measured exactly that on **5 September** and written it down. Fixed: the census now reads the
   city's whole scraped pool and buckets every row by the reason it is held, buckets summing to
   the pool, with `passes_every_guard` published as the pre-dedupe ceiling.

3. **A SOURCE THAT INVENTS ADDRESSES, and the reason an MX sweep could never see it — RG-0507
   SOURCE-HARDSTOP-1 (shipped) + RG-0509 GUESSED-ADDRESS-1 (open, the root cause).**
   `property24.py` says it in its own docstring: *"Fallback: construct
   firstname.lastname@agencydomain.co.za"*, and `guess_email()` does it. PROBED: **12 sent, 8
   bounced — 66.7%, the worst rate in the database**, four of the eight at one agency domain.
   The agency domains are real, so every invented address passes MX — which is exactly why run
   21's 2,240-row MX sweep pronounced the ZA pool 96% clean and concluded the bounces were
   "mailbox-level, not domain-level". Correct, and this is the machine that manufactures them.
   **SOURCE-QUALITY-1 could not hold it**: the gate required sends ≥ 20 AND bounces ≥ 3 AND rate
   > 5%, so the send floor sheltered any proportion of an under-20 sample. property24 was
   therefore the **only non-teacher supply left in Durban, PE, Cape Town and Johannesburg (67
   unsent rows), the top of every one of those queues**, and the proven cause of two of the three
   ZA stop-loss latches (Cape Town 3/3 on 18 Sep, PE 2/2 the same night). Fixed: the floor may be
   cleared by sample size **or** by an absolute bounce count (default 5). **Strictly tightening,
   and measured that way against the live register before shipping: old 11 sources blocked, new
   12, released 0, newly held exactly property24.**

4. **THE DELIBERATE COST, stated rather than hidden.** Holding property24 removes 67 of the 97
   guard-clean ZA rows and takes the honest sendable pool to **about 20, nearly all in Pretoria**.
   That was always the true number; what changed is that the wave will no longer spend the
   domain's reputation discovering it one bounce at a time. A gate is not weakened to keep a send
   count non-zero — run 21 refused exactly that on MX evidence, and this is the same discipline
   pointing the other way.

5. **MY OWN CHECK CONVICTED MY OWN FIX FOR EXPLAINING ITSELF — caught by running it.** RG-0508's
   first form asserted `"_source_clause" not in body`, and the new docstring **names** the two
   filters it must no longer apply, so the entry FAILed on the fixed tree. Exactly RG-0494's
   proxy-assertion fault, one night later, in the same session that wrote the lesson down. The
   check now judges the code after the docstring. **Both new entries were then proven in both
   directions on a reverted tree** — RG-0507 and RG-0508 FAIL on the pre-fix `wave_runner.py`
   and pass on this one.

6. **RG-0494's residual was AMENDED rather than left standing.** Its own ref text carried the
   "~96 addresses / 1,066 / 1,114 POPIA" arithmetic that reached David. It now carries the
   measurement that replaces it, and names RG-0508 as the reason the first one was written.

7. **SHIPPED AND PROBED ON THE BOX, not left on the tick.** Requested 23:35Z via
   `request_deploy.py --cl`; the agent landed it **23:58Z** and the box md5 now matches the repo
   (`c6d4de52…`, 45,749 bytes). `wave_runner.py` is in `deploy_citylauncher.bat` line 114 —
   checked first, because this is the third session running where a manifest line was the
   difference between a fix and the appearance of one. **LIVE PROBE on the server, against the
   live register:** `blocked_sources()` returns 12 sources and `property24` is among them; the
   census now sums to each city's whole pool — Pretoria `{source_quality 314, category_not_asked
   37, passes_every_guard 20, government 1}` = 372, **Durban `{category_not_asked 596,
   source_quality 37}` = 633 where it printed `{}` this morning.**

8. **Boards, post-work: `rulings_check` 150 rulings, 0 FAIL, 25 WARN (unchanged). Ledger:
   496 entries · 475 holding · 0 REGRESSED · 21 open · 0 ready to lock · 0 UNVERIFIED** —
   against the pre-work 493 · 472 · 1 · 20 · 0 · 0, so the run closed the inherited red as well
   as adding three entries. One red appeared mid-run and was **this run's own** — the box
   running a stale `wave_runner.py` while the deploy sat on the tick — and cleared when it
   landed. RG-0509 was ALSO caught mid-run printing `[ LOCK ] ready to lock` on its first board:
   an OPEN entry that returns no FAIL is judged ready for promotion, which is RG-0431 and
   RG-0437's family exactly. It now returns FAIL while the root cause stands, and reads `open`.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **THE SHIP IS CONFIRMED (md5 + live probe, 23:58Z) — do not redo it.** What is NOT yet
   observed is a WAVE running under it. Read `logs/launchday_20260927_2210*.log`: Pretoria and
   Cape Town should still be DRY-RUN (stop-loss, untouched), and **no estate-agent letter should
   be rendered in any city** — Bloemfontein's nightly Estate Agents×1 is the one to look for,
   because that is what went out on 26 Sep. If an estate agent is still rendered, RG-0507 is not
   reaching the emailer's own chokepoint and only the PLANNER is honouring it.

1. **THE ARITHMETIC, and it now decides the goal rather than colouring it.** 2,248 scraped ZA
   rows → 97 pass every guard → 67 of those were property24 and are now held → **about 20
   sendable, nearly all Pretoria.** 20 sellers by 31 Oct is not reachable from this list. This is
   not yet STALLED under §9 — the employer lane below is untried — but it is the honest
   trajectory and it was reported to David tonight rather than in the last week of October.

2. **THE ONE UNTRIED LANE: the employer door (RUL-150, `org_enrol.py`).** We hold **1,091 South
   African schools with working mailboxes**. They are worthless as sellers — that is now measured
   twice — and a school is precisely the employer kind the enrolment door was built for: it
   employs cleaners, groundskeepers, caretakers and assistants, who are the Quick door's people.
   This converts the largest dead weight on the list into the only supply lane we own.
   **DO NOT BUILD IT HERE: `org_enrol.py` is the parallel lane's, hours old, and SO-5 says the
   owner ships it.** Hand it the measurement (1,091 schools, 12 cities, source
   `teachers_trainers:dbe_emis`, all MX-clean) and let it choose. That hand-off is the next run's
   first substantive act.

3. **RG-0509 is open and it is the root cause:** a scraper may not invent an address and hand it
   on as a harvested one. Closing it = either `guess_email()` stops being a fallback, or a
   constructed address is written under its own source suffix so the quality gate judges invented
   addresses separately. Re-tagging the 67 existing rows is a write to the live prospects register
   — a focused session, not a tail-end edit. Nothing guessed can be sent meanwhile.

4. **The stop-loss latches are correct and were left alone.** Pretoria 3/12, Cape Town 3/3, PE
   2/2 — and now that we know what caused Cape Town's and PE's, releasing them before the source
   fix would simply have re-latched them. The release path exists (`clean_city_list.py` stamps
   `stop_loss_released_wave`) and should be used **after** RG-0507 is confirmed live, not before.

5. **Nobody has clicked since 24 Sep.** All 9 human clicks predate the RG-0449 publish fix, so the
   repaired journey has still never been walked by a real cold prospect.

6. **Residual from run 20, still open:** 22 checks in `regression_ledger.py` read a function as a
   fixed byte window. `fn_body()` exists; the sweep is a focused session.

7. Still carried: **RG-0409** ladder values + cap 40 · **RG-0410** CONFIRM-GLIMPSE-1 · **RG-0411**
   taxi-drop area unit · **RG-0412** EULA in the launch languages · **RG-0414** DOOR-RETURN-1 ·
   **RG-0419** Quick door prices only in rands · the terms box at 39,829 px (deliberate, RUL-020).

## OPEN LOOPS

- **D8 is WITHDRAWN, not deferred.** The teachers register is 1,091 schools held by two
  independent rules; the POPIA question was worth nothing and should not go back on David's list.
- **RG-0509 (open):** property24 invents addresses. Whole source held meanwhile by RG-0507.
- **RG-0373 (red, not ours):** trust plan step 4 offers a referral signal that is not tracked.
- **Run 22's CityLauncher ship LANDED 23:58Z and is probed live.** The REPO COMMIT is queued
  host-side; confirm both repos committed.
- **22 fixed-byte-window function reads left in `regression_ledger.py`** (RG-0465 residual).
- **RG-0419 (open):** the Quick door prices only in rands. **RG-0414 (open):** the only way back
  from the public door is an emailed sign-in link plus one browser's localStorage.
- `_get_json()` still does not exist (specified by run 13, unwritten). 14 `json.loads(_get(...))`
  sites remain individually unprotected against a 200 that is not JSON.
- **`git status` is unusable from this sandbox** — it creates `.git/index.lock`, cannot unlink it,
  and leaves a lock that blocks Windows git. Use `git show` or the host queue.
- Listings 386–400 range ARCHIVED, not deleted; 3 files in `_to_delete/` and 9 orphaned `tmp_obj`
  files need a deletion, which is David's. Two `users` rows from run 19's walks
  (`probe-run19-walk@`, `probe-run19-walk2@trustsquare.co`) and two probe addresses in
  `click_register` are recorded and cannot touch any onboarding figure.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.
- **Rick Wemple: CLOSED.** He is in Montana and the site never offered him a place to stand.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Nothing on this goal is waiting on him.** The list is shorter than last week because the top
item was withdrawn rather than answered.

- **D5 — where does she come from at all?** Unchanged and now the only question that matters. We
  have no list of housecleaners and no directory to harvest. The employer door (item 2 above) is
  the first answer that does not need one; if it fails, this becomes a four-week or four-month
  move and David should know which.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than a strip under a "list your business" letter written for companies?
- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry
  very different weight in South Africa. The Quick door is labelled `homehelp` today.

**~~D8 — the 1,114 teachers.~~ WITHDRAWN 27 Sep.** They are 1,091 schools, held by a
person-only rule as well as the POPIA one. Lifting the ruling would release none of them. This
was the top item on his list for a week and it should never have been on it.

## WHAT RUNS 17–22 LEARNED ABOUT THEMSELVES

**A BLANK IS A CLAIM, AND THIS ONE COST A WEEK (run 22).** `held_by_guard` printed `{}` for
eleven of twelve cities and every reader — including run 21, including the paragraph that went
to David — read the blank as "nothing is being held". It meant "I filtered out everything I was
built to count, before counting." The two reasons it could not see were the two largest. **An
instrument that reports nothing is not reporting nothing; it is reporting that it looked
somewhere else.**

**THE ANSWER WAS ALREADY WRITTEN DOWN, IN THE FILE, IN ENGLISH (run 22).** PERSON-ONLY-1's note
has said since 5 September that the teachers pool is "a list of schools", that 1,194 of 1,235
rows are named "<X> Primary School", and that releasing it "would spend the biggest pool in the
database on the least likely converters". Run 21 then spent a session concluding the opposite
and put it at the top of David's list. **Two of the six wrong numbers in this project were not
discovered by measurement — they were rediscovered, because the measurement was already on
disk and nobody read the note attached to the thing they were about to change.**

**AUDIT WHAT YOU ARE ABOUT TO SEND, NOT ONLY WHAT YOU HAVE SENT (run 22).** Five audits have
gone backwards into the register — who opened, who clicked, who registered, which states, which
letters. The one that found the invented addresses went forwards: *what is at the top of the
queue tomorrow night?* The answer was a source that bounces two letters in three, and no
backwards-looking audit would have reached it before the letters were gone.

**A HEALTH CHECK THAT CANNOT SEE THE DISEASE WILL CERTIFY THE PATIENT (run 22).** The MX sweep
was correct, honest and useless against this fault: it verifies domains, and an invented address
has a real domain by construction. "96% clean" was true and meant nothing. **Before trusting a
clean bill, ask what the instrument is physically incapable of seeing.**

**AUDIT THE DENOMINATOR, NOT ONLY THE RATE (run 21).** Run 20 corrected the numerator — 331
"readers" were 34 — and then reasoned from "2,587 letters sent" without asking what a letter
WAS. A rate has two numbers and this project has now been wrong about both, separately.

**A PERSON IS NOT A PROSPECT UNTIL THE PRODUCT HAS A PLACE FOR THEM (run 21).** Two runs on Rick
Wemple — a personal letter, a recoup link, a vigil, an OPEN LOOP across three state files. He is
in Montana. The cheapest question about a prospect is the one nobody asked: can they even
complete the action?

**MY OWN REVERT TEST CAUGHT MY OWN PROXY ASSERTION (runs 21 and 22, two nights running).**
RG-0494's manifest leg passed a tree with the shipping line deleted, because the entry's own
comment contained the filename. RG-0508 then FAILed a correct fix because the fix's own docstring
named the thing it had removed. Same fault, both directions, one night apart. **Writing the
revert test is not the discipline; running it is.**

**An instrument re-aimed at a new question needs its EVIDENCE re-aimed with it (run 20).** The
click register was built to answer "which of our clicks were people?" It was then asked to grade
OPENS, and nobody re-asked what a machine looks like when the machine is a mailbox. The answer
was in the data in plain English — the User-Agent literally says `GoogleImageProxy`.

**Audit the number that is RISING, not the one that is stuck.** Six now: FUNNEL-DENOM-1,
ONBOARD-REAL-1, the contract's naive probe, PROXY-OPEN-1, "2,587 emailed", and "96 reachable
South Africans". Every one flattered. Flattering numbers do not get audited.

**A red is a claim, and a claim gets checked before it is inherited (run 20).** RG-0110 said both
sign-in doors had broken and carried a deploy block. The function's last line disproved it in
thirty seconds. A false RED costs the same trust as a false green.

**A thing "only a person can do" is worth re-testing before it is inherited (run 19).** A blocker
written in confident language was recopied into three runs' state without being tried once. It
dissolved in ten minutes.

**The measurement is a suspect before the app is (run 19).** The acceptance box read "0 chars"
(hidden, not empty) and the confirm row "never appeared" (the loop ran out 27,000 px short). The
app was innocent both times.

**A fix is not finished until you follow the wire to the far end (run 18).** RETURN-LINK-1 was
correct, proven, deployed — and switched on the twenty-minute sender instead of the seven-day
one two functions away.

**Ask what CREATES a number before you believe what it means (run 17).** "42 registered" survived
four runs and reached David in writing because it was plausible, rising and flattering. One query
— group the rows by the minute they were created — killed it in seconds.
