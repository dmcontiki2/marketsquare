# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Keep it short: it is a state file, not a
diary. Durable background lives in `GOAL_FACTS.md` — read that when you need the why.*

---

## RUN 24 — Tue 29 Sep 2026, 20:56–21:3x UTC, first run under GOAL_RUN_PROMPT v2 (Opus 5.5)

- **Acting:** folder mounted and writable; server reachable by ssh from the device shell.
- **Walk (casual/services, `docs/E2E_2026-09-29.md`):** Quick → email link → Seller Hub draft #440 worked,
  email in under a minute. **Publish NOT walked** — the session's safety layer refused publishing a public
  advert on the live site from an unattended run. Steps after Publish were last proven 27 Sep (walk 3).
  Where she'd stop: Sell has no door that names a cleaner (Quick is a small "In a hurry?" line); her hub
  opens with an "Agent Hub — estate, car & tour agents" card above her own draft.
- **Number: 0** (`onboarding_number.py`, server): 6,748 listed · 2,601 emailed · 5 registered · 0 qualifying.
  Live adverts 108 = 85 super-examples + 18 David/family + **5 QA adverts public** (GI-0002). By a stranger's hand: **0**.
- **Outreach, 28 Sep wave (first live send in 10 days):** 13 sent, 1 bounce, 0 human clicks (scanner click +
  2 scanner Quick sessions within 60 s; 3 Google-proxy opens). 12 of 13 to schools/colleges/universities.
  `[sendable]` **9 · runway 0.** onboard_steps marks those scanner sessions bot=0 — the funnel counts machines.
- **The prize (§7):** 1,111 phone-only Gumtree South Africans advertising their own services; 0 phone-only rows
  in `prospects` (the scraper drops them). Cold SMS/WhatsApp to them is a POPIA s69 question — David's (GI-0004).
- **Built:** GI-0001 (hub agent card fit + Quick line wording) — **not live**: `ms.js` and the ledger are under
  `lm-walk`'s work lock (21:03Z). Patch in `docs/goal_patches/`. Follow-up scheduled to ship it.
- **REVIEW NOW:** GI-0002 archive QA adverts · GI-0003 full-size Quick card in Sell (changes RG-0478) ·
  GI-0004 SMS account ≈ R100–135/month + legal read on the 1,111.
- **First-run check (§9):** "Daily Agent Stand-up (with Pulse)" and "trustsquare-onboarding-goal" are OFF;
  "D-U-N-S email watch" ON.
- **Not reached:** Publish and everything after it; ledger/rulings boards (ledger locked by another lane);
  deploy (waits for the lock and for the tree to go quiet, SO-5).
- **Stray file:** `.goalrun_write_test` (empty, repo root) — my write probe; `rm` is not permitted from this shell.

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

---

### Correction to the summary above, from run 23 (28 Sep) — two figures, one of them mine to own

- **"about twenty addresses we can honestly write to" was right.** Probed again on the server:
  **21** — Pretoria 20, Cape Town 1. That number has now survived two independent measurements.
- **"the 1,091 schools" was low.** Probed fresh rather than copied: **1,354** never-emailed
  `teachers_trainers` rows with no verdict against them, **every one of them MX-clean**, 1,267 of
  them school-named. The pool is a quarter larger than last night's paragraph said, and it is the
  lane the goal now depends on, so the figure matters. Full measurement in
  `EMPLOYER_LANE_SUPPLY.md`.
- **One thing the summary could not have said, because it was not known: the campaign was not
  sending at all.** Not "one letter a night" — zero. The 27 Sep wave rendered 13 letters and sent
  none of them; both remaining cities were latched. That is fixed as of tonight.

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
| 2026-09-24 (run 19, 03:40–04:45) | **0** | 0 | 0 | raw 3, all e2e_test · **the letter to Rick has gone** · publish journey walked green |
| 2026-09-24 (run 20, 23:07–00:10) | **0** | 0 | 0 | 2,574 emailed · **the "331 human opens" were 34** · 9 clicks |
| 2026-09-26 (run 21, 04:15–05:30) | **0** | 0 | 0 | 2,587 emailed · **1,499 of 1,911 US letters had no home on the site** · ZA pool MX-cleaned |
| 2026-09-27 (run 22, 23:07–00:15) | **0** | 0 | 0 | 2,588 emailed — the 26 Sep wave sent ONE letter · true sendable ZA pool ≈ 20 · a source was inventing addresses · D8 withdrawn |
| 2026-09-28 (run 23, 23:08–01:0x) | **0** | 0 | 0 | 2,588 emailed — **the campaign was sending ZERO, both cities latched** · dashboard said 365 sendable, truth is **21** · **both latches released, gates now clear** |
| 2026-09-29 (run 24, 20:56–21:3x) | **0** | 0 | 0 | 2,601 emailed · 28 Sep wave: 13 sent, 0 human clicks · **sendable 9, runway 0** · 5 QA adverts public |

Target: **20 by Fri 31 Oct 2026** — 33 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–23 Opus 5.

## WHAT RUN 23 DID (27–28 Sep 2026, from 23:08 UTC, Opus 5)

0. **Boards first. Pre-work:** `rulings_check` **166 rulings, 0 FAIL, 25 WARN** (the parallel lane
   has added 16 rulings since last night). Ledger, 6 shards: **526 entries · 499 holding ·
   0 REGRESSED · 22 open · 5 ready to lock · 0 UNVERIFIED.** The 5 ready-to-lock are the Ripple
   lane's own entries from 27 Sep — **left to their owner (SO-5), not promoted here.**

1. **RUN 22's HANDOVER ITEM IS DISCHARGED — RG-0507 reaches the emailer, not just the planner.**
   The 27 Sep 22:10 wave was the first under it. It visited Pretoria and Cape Town, rendered 13
   letters, and **not one was an Estate Agent and not one came from property24.** Confirmed in the
   log on the box.

2. **AND THE SAME LOG SAID THE THING NOBODY HAD ASKED: THE CAMPAIGN SENT NOTHING.** Not one letter.
   Both cities ran in DRY-RUN under stop-loss (Pretoria 25%, Cape Town 50%). `2,588 emailed` is
   unchanged from last night because **nothing was sent on either of the last two nights**, and
   nothing would have been sent on any night after. A campaign at zero and a campaign at twelve a
   night look identical in a state file that only records the total.

3. **A FALSE RED CHECKED AND CLEARED before it was inherited.** The rendered letters go to
   organisation desks (`info@christalhopebookstore.com`, `books@kalkbaybooks.co.za`), which looked
   exactly like the fault that holds the 1,091 schools. It is not: `_looks_org_name` and
   `_looks_role_address` apply **only** to `defaults.person_only_categories`, and Collector Shops /
   Tutor Institutions / Service Companies are the RUL-059 agency lane, deliberately excluded. The
   guards are working as written. Thirty minutes to clear, and a false red costs what a false green
   costs.

4. **THE SEVENTH FLATTERING NUMBER, and this one was on David's own dashboard — RG-0540
   SENDABLE-REACH-1.** `publish_sendable.py` promises "what the send chokepoint would ACTUALLY
   accept tonight" and applied armed + gates_green + disarmed_by — **but not GEO-REACH-1**, the gate
   that has decided which cities are *asked* since 26 Sep. Measured on the server, both directions:
   deployed file **365 sendable, runway 28 nights**; fixed file **21 sendable, runway 1**, with
   **344 held unreachable: Maine 344**. So 94% of the "supply" was people in a state whose sellers
   cannot say where they are on the site. FIXED: the gate is imported from `wave_cities` (one
   implementation), every dropped city is named with its count, and `reachability_state` is
   published so GEO-REACH-1's deliberate fail-open reads as NOT MEASURED instead of quietly
   restoring 365.

5. **THE RELEASE PATH FOR THE LATCHES WAS BROKEN AND WOULD HAVE FAILED SILENTLY — RG-0541
   RELEASE-STAMP-SERVER-1.** `clean_city_list.py` is host-side and stamped the wave number from the
   **laptop** DB; the gate that reads the stamp runs on the **server**. Measured on both machines:
   Pretoria host 8 / server 8, Cape Town host **13** / server **14**, Port Elizabeth host **8** /
   server **9**. **Two of the three releases would have been a no-op with a success line over
   them.** The laptop was 123 sends behind because `pull_from_server.py` had not run — and
   WAVE-SERVER-1's own note already named `clean_city_list` as one of the four tools that
   over-count without it. FIXED: the bat pulls first and fails closed; the stamp comes from
   `scripts/server_wave_no.py`, which calls the gate's **own** `wave_history()` on the box.

6. **MY OWN FIX WAS WRONG TWICE AND BOTH WERE CAUGHT BY PROBING IT INSTEAD OF TRUSTING IT.** Its
   first cut (a) tested `ssh_rows()` for `state == 'ok'` when that function returns `'read'`, so it
   refused to stamp every city and **released nothing on its first live run**; and (b) counted
   `DISTINCT date(created_at)` — **UTC** days — getting Pretoria 7 / Cape Town 12 where the gate's
   `wave_history()` says 8 / 14, because a wave is a day in the **send timezone** and a 22:10 UTC
   send belongs to the next SAST day. Wrong counter (WAVE-COUNTER-1), wrong machine (this entry),
   wrong arithmetic (that first cut). There is now exactly one place the ordinal comes from.

7. **AND THE PROXY-ASSERTION TRAP FIRED FOR THE THIRD NIGHT RUNNING, this time on my own check.**
   RG-0541's check FAILed the correct tree because the fix's own **docstring** names the SQL it had
   just removed — and the filter I copied only stripped `#` lines and lines *containing* a quote
   mark, which a docstring's body does not. Fixed properly: `_code_only()` strips triple-quoted
   blocks whole, and both new entries use it. RG-0494, RG-0508, RG-0541 — three nights, three
   entries, one trap, the third written by a session that had just read the lesson.

8. **THE LATCHES ARE RELEASED, ON MEASURED EVIDENCE, AND THE WIRE WAS FOLLOWED TO ITS FAR END.**
   The sources that latched Pretoria (`osm:shop=motorcycle` 2 of 3, `osm:shop=car`) have **zero
   unsent rows left** — exhausted, so they cannot re-latch it. Cape Town's and PE's latches were
   **100% property24**, which RG-0507 now holds. Port Elizabeth was **never latched** (2 bounces,
   floor is 3). Stamped and probed: Pretoria `released=8`, Cape Town `released=14`, both matching
   the server. Then simulated `gate_check` on the box with those stamps: **`may_send=True,
   blocks=[]` for both** — the stop-loss was the only thing stopping the campaign, so this is
   genuinely the switch and not another layer of appearance.

9. **THE EMPLOYER LANE HAND-OFF IS WRITTEN — `EMPLOYER_LANE_SUPPLY.md`, OPEN_LOOPS L27.** Probed
   fresh, not inherited: **1,354** never-emailed no-verdict `teachers_trainers` rows, **every one
   `mx_ok`**, 1,267 school-named, in **nine cities that are all armed, gates_green AND reachable** —
   Durban 596, Pietermaritzburg 535, so **84% in KwaZulu-Natal and this is an isiZulu lane first**.
   `org_enrol.py` was **not touched** (SO-5, hours old, its owner ships it). The document carries
   the measurement, the city/reachability table, and the three questions only that lane can answer.

10. **Boards, post-work: `rulings_check` 166 / 0 FAIL / 25 WARN (unchanged). Ledger: 528 entries ·
    501 holding · 0 REGRESSED · 22 open · 5 ready to lock · 0 UNVERIFIED** against pre-work
    526 · 499 · 0 · 22 · 5 · 0. Both new entries proven to **FAIL on a reverted tree**
    (`git show HEAD:`) and pass on this one.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **FIRST ACT: READ THE 28 Sep 22:10 WAVE LOG. This is the one thing only the next run can see.**
   `/var/www/citylauncher/logs/launchday_20260928_2210*.log`. Pretoria and Cape Town should now be
   **LIVE, not DRY-RUN** — the release stamp lets **ONE** wave out per city and that wave's own
   bounces govern again. Expect roughly **12 letters in Pretoria and 1 in Cape Town**. What to
   check, in order: (a) did they send, or is a gate still blocking; (b) what bounced — if Pretoria
   bounces 3 of 12 again it re-latches immediately and the source that did it must be found and
   held before any second release; (c) `[sendable]` should now read about **21 · 2/40 cities ·
   runway 1**, not 365. **Do not re-release a latch that closes again without finding the source
   first** — that is spending the domain's reputation to discover something a query answers.

1. **THE POOL IS 21 AND THE GOAL NEEDS 20. This is now arithmetic, not pessimism.** Two nights of
   sending empties it. Nothing about the letter, the timing or the funnel is the constraint — of the
   people we can prove read one, about 1 in 4 clicked. **We have run out of people to ask, on this
   list, for this lane.** Not yet STALLED under §9 only because the employer lane is untried.

2. **THE EMPLOYER LANE IS THE GOAL'S ONLY CREDIBLE PATH — and it is a hand-off, not a build.**
   `EMPLOYER_LANE_SUPPLY.md` + OPEN_LOOPS **L27**. 1,354 MX-clean school mailboxes against 21
   sellers: 64×. Next run's job is to find out whether that lane's owner has picked it up, and if
   the answer is no after a reasonable interval, **say so to David plainly** — because at that point
   the goal is blocked on something outside this lane's authority, which is a §9 BLOCKED, not a
   silence.

3. **RG-0509 is still open and is still the root cause of the invented addresses.** A scraper may
   not invent an address and hand it on as harvested. Closing it = `guess_email()` stops being a
   fallback, or a constructed address is written under its own source suffix. Re-tagging the 67
   existing rows is a write to the live prospects register — a focused session. Nothing guessed can
   be sent meanwhile (RG-0507 holds the whole source).

4. **Nobody has clicked since 24 Sep**, and all 9 human clicks predate the RG-0449 publish fix — so
   the repaired journey has **still** never been walked by a real cold prospect. The letters going
   out tonight are the first chance for that in the project's history.

5. **Residual, run 20:** 22 checks in `regression_ledger.py` read a function as a fixed byte window.
   `fn_body()` exists; the sweep is a focused session.

6. Still carried: **RG-0409** ladder values + cap 40 · **RG-0410** CONFIRM-GLIMPSE-1 · **RG-0411**
   taxi-drop area unit · **RG-0412** EULA in the launch languages · **RG-0414** DOOR-RETURN-1 ·
   **RG-0419** Quick door prices only in rands · the terms box at 39,829 px (deliberate, RUL-020).

## OPEN LOOPS

- **The 28 Sep wave is the open question of this goal.** First live sends in ten days. Unwatched
  until the next run reads the log.
- **L27 / `EMPLOYER_LANE_SUPPLY.md`** — handed to `org_enrol.py`'s owner tonight. Not yours to
  build; yours to check whether it moved.
- **RG-0509 (open):** property24 invents addresses. Whole source held meanwhile by RG-0507.
- **RG-0373 is GREEN again** — the parallel lane fixed it (trust-plan referral wording). Not ours.
- **5 entries print READY TO LOCK and were deliberately not promoted** — RG-0532, 0534, 0536, 0537,
  0539, all the Ripple lane's, all shipped 27 Sep. SO-5: the owner promotes. Flag it to them if it
  is still true in a few days, because a fix that prints READY TO LOCK and is never promoted cannot
  trip red when it rots (DW-079).
- **Run 23's CityLauncher deploy is REQUESTED, not confirmed** — it carries the stamped
  `waves_policy.json`, RG-0540's `publish_sendable.py` and RG-0541's `server_wave_no.py`. **Confirm
  it landed before trusting tonight's wave**, and confirm both repos committed (two `git_push`
  actions were queued at 00:21Z). `server_wave_no.py` was already scp'd to the box by hand and
  probed (8 / 14 / 9), so the deploy's job for it is only to make that permanent.
- **22 fixed-byte-window function reads left in `regression_ledger.py`** (RG-0465 residual).
- **RG-0419 / RG-0414** open, as above.
- `_get_json()` still does not exist (specified by run 13, unwritten). 14 `json.loads(_get(...))`
  sites remain individually unprotected against a 200 that is not JSON.
- **`git status` is unusable from this sandbox** — it creates `.git/index.lock` it cannot unlink and
  blocks Windows git. Use `git show` or the host queue. (`git show HEAD:<file>` was how both of
  tonight's entries were proven on a reverted tree.)
- Listings 386–400 range ARCHIVED, not deleted; 3 files in `_to_delete/` and 9 orphaned `tmp_obj`
  files need a deletion, which is David's. Two `users` rows from run 19's walks and two probe
  addresses in `click_register` are recorded and cannot touch any onboarding figure.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.
- **Rick Wemple: CLOSED.** He is in Montana and the site never offered him a place to stand.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Nothing on this goal is waiting on him**, and that is now the third week running. If the employer
lane does not get picked up, that changes — see "next run" item 2.

- **D5 — where does she come from at all?** The only question that matters, and the employer door is
  the first answer to it that does not need a directory we do not have.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than a strip under a "list your business" letter written for companies?
- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry very
  different weight in South Africa. The Quick door is labelled `homehelp` today. **Tonight's
  measurement sharpens this: 84% of the employer supply is in KwaZulu-Natal, so the answer is
  wanted in isiZulu first, not English.**

**~~D8 — the 1,114 teachers.~~ WITHDRAWN 27 Sep**, and it stays withdrawn. They are schools, held
by a person-only rule as well as the POPIA one; lifting the ruling would release none of them. Run
23 re-measured the pool at 1,354 rows — a bigger prize, in a different lane, with no decision
needed from David to reach it.

## WHAT RUNS 17–23 LEARNED ABOUT THEMSELVES

**A TOTAL IS NOT A RATE, AND ZERO HIDES INSIDE ONE (run 23).** `2,588 emailed` was true on
26, 27 and 28 September. It was the same number because **the campaign had stopped sending
entirely** — two cities latched, thirteen letters rendered into a dry run, none sent. Every state
file recorded the cumulative total and none recorded the nightly rate, so a dead campaign and a
slow one were the same line of text. **Record the derivative, not just the integral: what went out
LAST NIGHT is the number that tells you whether the machine is alive.**

**A VALUE WRITTEN ON ONE MACHINE AND COMPARED ON ANOTHER (run 23).** The stop-loss release stamped
the laptop's wave number; the gate that reads it runs on the server. Two of three releases would
have printed success and changed nothing. WAVE-COUNTER-1 had already fixed this stamp once, for the
wrong COUNTER; this was the right counter on the wrong MACHINE; and the first attempt at the fix
re-derived the ordinal a third way and got UTC days instead of send-timezone days. **Three ways to
compute one number is three faults. Ask the thing that will judge you what it thinks the number
is.**

**MY OWN FIX WAS WRONG TWICE AND ONLY PROBING FOUND IT (run 23).** It tested a helper for
`state == 'ok'` when that helper returns `'read'`, and released nothing on its first live run
while exiting 0. Reading my own code would never have found either fault; running it against the
real box found both in minutes. **A fix is a hypothesis until it has been fired at the real
target — and `rc=0` is not evidence that anything happened.** What proved it was probing the
policy file afterwards, not the exit code.

**THE PROXY-ASSERTION TRAP, THREE NIGHTS RUNNING, THE THIRD TIME ON A SESSION THAT HAD JUST READ
THE LESSON (run 23).** RG-0494, RG-0508, RG-0541. Each check matched its own fix's prose instead of
its code. Knowing about the trap did not prevent it; the shortcut filter I copied stripped `#`
lines and lines containing a quote mark, and a docstring's body is neither. **A lesson written down
is not a lesson installed. `_code_only()` is now the installed version** — the difference between
remembering the rule and making it impossible to break.

**FOLLOW THE WIRE TO THE FAR END BEFORE YOU CALL IT A SWITCH (run 23).** Releasing the latches
would have been worthless if any other gate still blocked those cities. That took one probe:
`gate_check` on the box with the new stamps, `may_send=True, blocks=[]`. **The cheap question
before claiming a fix will have an effect: is this the ONLY thing in the way?**

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
