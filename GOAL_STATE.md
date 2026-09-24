# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Keep it short: it is a state file, not a
diary. Durable background lives in `GOAL_FACTS.md` — read that when you need the why.*

---

## SUNDAY SUMMARY

**Next one is due Sunday 27 September**, and it has one headline already: *the open rate on the
dashboard was measuring Google, not people — 331 "readers" were 34.* That correction went to
David on the night of 24 September rather than being held, because the wrong figure is the kind
he makes decisions on and it argued against the very move the evidence now supports.

The 20 September summary was removed rather than left standing, because one of its headline
sentences was false: it told David that 42 people had opened an account and none had published.
Nobody had opened an account — those were rows our own mailer creates when it sends to an estate
agent. The counter is fixed (RG-0428) and that correction went to him on 23 September.

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
| 2026-09-24 (run 19, 03:40–04:45) | **0** | 0 | 0 | raw 3, all e2e_test · **the letter to Rick has gone** · the publish journey was a dead end and is now walked green end to end |
| 2026-09-24 (run 20, 23:07–00:10) | **0** | 0 | 0 | 2,574 emailed · **the "331 human opens" were 34** · 9 clicks · Rick silent |

Target: **20 by Fri 31 Oct 2026** — 37 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–19 Opus 5.

## WHAT RUN 19 DID (24 Sep, 03:40–04:45) — compressed

Walked the whole cold-seller journey on the LIVE site in a real browser — the check five runs
called impossible — and found publishing was a **dead end for every first-time seller**:
`sobInit()`'s one call to `GET /users/<him>` sent no `X-Api-Key`, so `if (uRes.ok)` was false for
everybody and the Terms hand-over never fired (RG-0449). Fixed on two legs, shipped `c3c1fdd`,
live 04:20:01Z, re-walked green end to end. **The letter to Rick Wemple has gone** (04:26Z, Resend
id `01a0d1a8`), on the RG-0447 recipe: 7 days, `&draft=382`, `&src=recoup-382`. RG-0400 was found
already closed and the stale claim about it removed. The harness is in the repo:
`scripts/smoke_harness/verify_terms_handover.mjs`.

## WHAT RUN 20 DID (24–25 Sep 2026, 23:07–00:10 UTC, Opus 5)

1. **Rick has not answered.** Server row 83302, status `onboarded`, `published_at` NULL, no
   `src=recoup-382` arrival, nothing in `click_register` under his address. The letter is ~19 h
   old. Nothing further is owed to that loop by us (RUL-106(e), and the letter promised it).

2. **THE FINDING, and it is the same class as "42 registered": the funnel's OPEN rate is a
   measurement of Google, not of people. RG-0464 PROXY-OPEN-1.** The register read **331
   recipients `human_open`** — a 12.9% read rate on 2,574 letters. That number says the letter is
   widely read and simply not acted on, and it would have sent the next month of work into
   rewriting copy. PROBED on the live register, not inferred: **297 of the 331 had no open event
   that was anything but a proxy prefetch.** The evidence names itself — 229 events carry
   `GoogleImageProxy` in the User-Agent, 18 carry `YahooMailProxy`, 17 carry `MSOffice 16`, and
   301 carry the bare token `Mozilla/5.0`, which is Apple Mail Privacy Protection and which no
   real browser sends. Corroborated independently by IP: 326 of the open events came from
   74.125 / 142.250 / 66.249 / 66.102, all Google.
   **Why it graded human:** `MACHINE_UA` and `MACHINE_IP_PREFIXES` were built on 3 Sep to answer
   *"which of our CLICKS were people?"* — Proofpoint, Mimecast, Defender Safe Links. The module
   was then asked to grade OPENS too and **its evidence set was never re-aimed with it.** No image
   proxy is in either list, so a proxy fetch scored on one signal only, `clicked Nh after send`,
   worth −1, and −1 is "human". **328 of the 331 gradings rested on that single reason.**
   **Fixed, and not by deleting it:** a proxy fetch proves the letter reached a live mailbox and
   proves nothing about whether a person looked — the proxy fires either way. So it grades into
   its own `proxy_open` tier with its own reason string, is published as `opened_proxy`, and can
   never rejoin a human count. Re-scored on a copy of the live database before shipping:
   **human_open 331 → 34, uncertain 84 → 16, proxy_open 365, machine 203 unchanged, human_click 9
   unchanged.** Strictly tightening — nothing that graded machine became human, and the clicks are
   untouched because an image proxy fetches pixels, not links.

3. **THE HONEST FUNNEL, and it points somewhere different from last night's:**
   2,574 letters · **34 people we can show opened one** · 365 more delivered but unmeasurable ·
   **9 clicked** · 0 published. Run 19 read "2,573 letters, 8 human clicks" and concluded the
   letter was the lever. The arithmetic now says the opposite: **nine clicks from thirty-four
   readers we can actually see is about 26%** — that is a letter that works on the people who read
   it. The shortfall is **reach, not copy**, which is D4 and D5, and the phantom 12.9% was the one
   figure that argued against them.

4. **RG-0110 was a FALSE RED and is cleared — RG-0465 FN-WINDOW-1.** The board printed
   *"auth_verify no longer routes through `_establish_user_session`"* and carried "Do not deploy
   over this". auth_verify's **last line** is that exact call. The check read
   `bea.split("def auth_verify(")[1][:1400]` — not the function, but the first 1400 bytes of
   everything after it — and SIGNIN-ONCE-1, a correct David-approved hardening shipped the same
   day, added ~1,050 characters and pushed the call to offset **2056**. Measured:
   `auth_verify` 2056, `auth_verify_code` **1372** — the second sign-in door was **twenty-eight
   characters** from the same false conviction. `fn_body()` now bounds the read by the next
   top-level def; RG-0110's two reads go through it. **Not claimed as closed: 22 other checks in
   this file still read a fixed byte window** — a sweep, not a late-night edit, and none is red
   today.

5. **Boards.** Before: 450 · 425 holding · **4 REGRESSED** · 19 open · 1 ready to lock · 1
   UNVERIFIED. After: **452 · 429 holding · 3 REGRESSED · 19 open · 1 ready to lock · 0
   UNVERIFIED**; `rulings_check` 142 rulings, **0 FAIL**, 25 WARN. Both new entries were run
   against a reverted tree as well as this one — RG-0464 FAILs on the pre-fix source, RG-0465's
   byte-window form FAILs on today's.

6. **The three remaining reds are not ours.** RG-0351 (17 modifier-form SQLite clocks against a
   baseline of 15 — the ratchet ran backwards) and RG-0450 (`genie/HARNESS.html` differs from
   `quick.html`) are the parallel lane's RUL-167 work, written today; RG-0450 is that lane's own
   brand-new entry. RG-0373 is a live probe: the trust plan's step 4 offers a referral signal that
   is not tracked, so the step can never award its points. No lock is held on any of those files
   (SO-5 checked); they were left alone because the work is hours old and in flight, and RG-0450
   in particular is a house-rule file-identity check whose owner is mid-edit.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **Confirm the CityLauncher deploy landed.** `python3 scripts/request_deploy.py --status` — it
   was PENDING on the 20-minute tick when run 20 closed. Then **re-run the funnel and read
   `opened_human` / `opened_proxy`** on the live board, do not assume the re-score: the live
   register still holds the old tiers until the refresh pass runs against the shipped grader.
   **The dashboard David reads will drop from ~331 opens to ~34 the moment it does.** That is the
   correction, not a fault — but it must not surprise him, so it is in the note to him below.

1. **The number did not move and the reason is now measured, not guessed.** ~390 cold addresses
   remain and 9 of 2,574 have ever clicked. The route to 20 is D4 and D5 — a door aimed at one
   kind of person, and a list of those people. **Run 20's finding strengthens that case rather
   than weakening it:** the letter converts the people who read it at roughly one in four. There
   is nothing left to fix in the copy that would be worth a month.

2. **RUL-167 landed today (24 Sep) and is the first real supply-side lever in weeks** — David
   approved the account key being a phone number (SMS code) or the private draft link itself.
   That removes the e-mail address as the price of entry for exactly the population D3/D5 are
   about. The parallel lane is building it (RG-0450). **Do not duplicate that work**; check
   whether it is finished and, if it is, whether the Quick door's reach argument has changed.

3. **The three reds** (RG-0351, RG-0450, RG-0373). If `bea_main.py`, `genie/HARNESS.html` and
   `quick.html` have been quiet for hours, the lane has moved on — say so, then fix them. RG-0450
   is a file-identity check and is a one-line fix once the owner is done.

4. **Residual from run 20, deliberately named rather than swept:** 22 checks in
   `regression_ledger.py` still read a function as a fixed byte window (`split("def x(")[1][:N]`).
   The next one whose function grows past its window will convict correct code and carry a deploy
   block with it, exactly as RG-0110 did. `fn_body()` exists; the sweep is a focused session.

5. **Worth an instrument, not a fix:** the terms box is 39,829 px in a 338 px window — about 118
   screenfuls on a phone before the confirm row appears. The scroll gate is deliberate and the
   text is David's (RUL-020), so this is reported, never adjusted by a session.

6. Still carried, with the reason each was deferred: **RG-0409** ladder values + cap 40 ·
   **RG-0410** reachability gate · **RG-0411** taxi-drop area unit · **RG-0412** EULA in the launch
   languages · **RG-0414** DOOR-RETURN-1 · **RG-0419** Quick door prices only in rands.

## OPEN LOOPS

- **Rick: sent, no answer after ~19 h. Nothing further is owed to that loop by us.**
- **CityLauncher deploy PENDING** at run 20's close (RG-0464). Confirm it shipped, then confirm
  the live register re-scored.
- **RG-0351, RG-0450 (red, the parallel lane's RUL-167 work) · RG-0373 (red, live probe: trust
  plan step 4 offers a referral signal that is not tracked).**
- **22 fixed-byte-window function reads left in `regression_ledger.py`** (RG-0465 residual).
- **RG-0419 (open): the Quick door prices only in rands.** Not a defect to paper over.
- **RG-0414 (open): the only way back from the public door** is an emailed sign-in link plus one
  browser's localStorage.
- `_get_json()` still does not exist (specified by run 13, unwritten). 14 `json.loads(_get(...))`
  sites remain individually unprotected against a 200 that is not JSON.
- The ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run — why a shard is slow.
- **`git status` is unusable from this sandbox** — it creates `.git/index.lock`, cannot unlink it,
  returns empty output, and leaves a lock that blocks Windows git. Use `git show` (safe) or the
  host queue. `mount_check.sh` and `request_deploy.py --all` both work fine.
- Listings 386/387/388/391/393/395/396/397/398/399/400 are ARCHIVED, not deleted; 3 files in
  `_to_delete/` and 9 orphaned `tmp_obj` files need a deletion, which is David's. Run 19's walks
  left two `users` rows (`probe-run19-walk@` and `probe-run19-walk2@trustsquare.co`). They cannot
  touch any onboarding figure: `reconcile_conversions` joins FROM prospects and neither address is
  a prospect. Recorded anyway, because an unexplained account is how the 42 started.
- Two probe addresses (`probe-returnlane-20260924@`, `probe-recoup-20260924@trustsquare.co`) now
  appear in `click_register`, both graded `machine`, `prospect_id` NULL. Harmless, recorded.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**Nothing on this goal is waiting on him tonight.** No clicks, no approvals, no decisions needed
to keep going.

- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry very
  different weight in South Africa. The Quick door is labelled `homehelp` today.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than sitting as a strip under a "list your business" letter written for companies?
- **D5 — where does she come from at all?** We have no list of housecleaners and no directory to
  harvest. Four-week or four-month move.
- **D8 — the 1,114 teachers on the education register.** The largest reachable block left, held by
  `blocked_categories` as a person-only/POPIA call, not by anything technical.

**Two things David should KNOW, not decide:**

1. **His dashboard's open rate is about to fall from ~331 to ~34, and the smaller number is the
   true one.** Gmail, Yahoo and Apple Mail fetch the tracking pixel in a letter themselves,
   whether or not the person ever looks at it, and we were counting those fetches as readers.
   The 365 proxy fetches are not thrown away — they are reported separately, because they do prove
   the letter reached a real, live mailbox.
2. **The correction is good news about the letter and bad news about the list.** Of the 34 people
   we can actually show read it, 9 clicked through — about one in four, which is a strong letter.
   The wall is that only 2,574 letters have gone out, ~390 addresses remain, and that arithmetic
   does not reach 20 sellers. **D4 and D5 are the route**, and the phantom 12.9% open rate was
   the single piece of evidence that argued against them.

## WHAT RUNS 17–20 LEARNED ABOUT THEMSELVES

**An instrument re-aimed at a new question needs its EVIDENCE re-aimed with it (run 20).** The
click register was built to answer "which of our clicks were people?" and its scanner list was
right for that. It was then asked to grade OPENS, and nobody re-asked what a machine looks like
when the machine is a mailbox rather than a firewall. The answer was sitting in the data in plain
English — the User-Agent literally says `GoogleImageProxy` — and it went unread for three weeks
because the number it produced was going up.

**The fourth number that read HIGH by default (run 20).** FUNNEL-DENOM-1, ONBOARD-REAL-1, the
contract's own naive probe, and now the open rate. Every one of them flattered, and every one
survived because flattering numbers do not get audited. The standing rule this project keeps
re-learning: **audit the number that is rising, not the one that is stuck.**

**A red is a claim, and a claim gets checked before it is inherited (run 20).** RG-0110 said both
sign-in doors had broken and carried a deploy block. The function's last line disproved it in
thirty seconds. The checker had been measuring the first 1400 bytes after a marker and calling it
a function body, and a correct security fix shipped that morning had pushed the truth 656 bytes
out of view. A false RED costs the same trust as a false green.

**A thing "only a person can do" is worth re-testing before it is inherited.** Item 1 of this
file said the last pre-send check needed David at a keyboard, because driving a browser to a URL
carrying a sign-in token is refused in an unattended session. Run 19 spent ten minutes checking
that premise and it dissolved: the refusal is about acting on somebody's real credentials, and the
walk needs neither — a throwaway address, a draft made through the app's own door, and a link
minted the way the product mints it. A blocker written down in confident language was recopied
into three runs' state without being tried once.

**The measurement is a suspect before the app is.** Twice in one hour: the acceptance box read
"0 chars" (it was hidden, not empty — `innerText` of an unrendered element is `''`), and the
confirm row "never appeared" after scrolling (the loop ran out of hops 27,000 px short of the
bottom). Both looked like serious defects, and the app was innocent both times. The rule that
caught it is CLAUDE.md's own: a checker that disagrees with the authority suspects itself first.

**Ask what the person RECEIVES, not whether the code ran (run 18), and then go and look at it
(run 19).** RG-0400 asserts three true source properties about the EULA box and has held since
20 September. RG-0396's own residual, written on 19 September, named the gap exactly: *"both
assertions read ms.js in the repo, so the SERVED build is proven by deploy timing plus one manual
walk... the next binding change could still break the no-session path silently and no instrument
would say so."* The next binding change (AUDIT-AUTH-1, 23 September) did exactly that, and nothing
said so for a day. The residual was right, it was written down, and it was not turned into an
instrument. RG-0449 and the harness are that instrument.

**A fix is not finished until you follow the wire to the far end (run 18).** RETURN-LINK-1 was
correct, proven, deployed and celebrated — and it switched on the twenty-minute sender instead of
the seven-day one two functions away.

**A lesson recorded in the one function it was learned in does not generalise by itself (run 18).**
QUICK-RETURN-TTL-1 was written about this exact man, with the seven-day figure in full, and five
days later a brand-new artefact reached for the twenty-minute lane again. What stops that is an
assertion about the CLASS — RG-0447.

**Ask what CREATES a number before you believe what it means (run 17).** "42 registered" survived
four runs and reached David in writing because it was plausible, rising and flattering. One query
— group the rows by the minute they were created — killed it in seconds.
