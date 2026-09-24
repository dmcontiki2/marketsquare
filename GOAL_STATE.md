# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Keep it short: it is a state file, not a
diary. Durable background lives in `GOAL_FACTS.md` — read that when you need the why.*

---

## SUNDAY SUMMARY

**Next one is due Sunday 27 September.** The 20 September summary was removed rather than left
standing, because one of its headline sentences was false: it told David that 42 people had opened
an account and none had published. Nobody had opened an account — those were rows our own mailer
creates when it sends to an estate agent. The counter is fixed (RG-0428) and the correction went
to David on the night of 23 September.

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

Target: **20 by Fri 31 Oct 2026** — 37 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–19 Opus 5.

## WHAT RUN 18 DID (24 Sep, 02:51–03:40) — compressed

RETURN-LANE-1: `goHandoff()` was sending the seller the **20-minute interactive** sign-in letter
while telling him "finish anytime", beside the correct seven-day one — removed. RG-0444's
assertion was a proxy pointing at the wrong sender and was corrected. RG-0447 caught the same
short-lane mistake in the *written recipe* for Rick's letter before it was sent. RG-0429 rewritten
(it was false in both halves against RUL-166). Its deploy was
**relayed 03:39Z and live at 03:41:53Z (1a7a23c)** — run 19 probed that rather than trusting it: the server's `ms.js` carries RETURN-LANE-1, the
only `/auth/request-link` left in `goHandoff` is the comment recording its removal, and all three
legs (`sellflow` in `_SELF_SERVE_LANES`, `_quick_draft_return`, `source:'sellflow'`) hold on the
server's own files.

## WHAT RUN 19 DID (24 Sep 2026, 03:40–04:45 UTC, Opus 5)

1. **WALKED THE WHOLE COLD-SELLER JOURNEY ON THE LIVE SITE, IN A REAL BROWSER — the check five
   runs called impossible.** Headless Chromium at 412×915 from the cloud container, against
   trustsquare.co, as a seller with no acceptance on record arriving on a 7-day
   `?signin=&draft=` link (probe drafts 399 then 400, created through the app's own
   `POST /listings` door, both archived within minutes and never in a public feed). **The
   "credential guard" that blocked run 18 was never the obstacle it looked like:** the letter link
   is a URL a browser I drive can simply be pointed at, on a throwaway address of my own making,
   and the harness is now in the repo: `scripts/smoke_harness/verify_terms_handover.mjs`.
2. **THE FINDING, and it is why the number could never have moved: publishing was a DEAD END for
   every first-time seller. RG-0449 TERMS-HANDOVER-1.** Two requests apart, measured:
   `PUT /listings/399/publish` → **403** (EULA — RG-0443 working), then `GET /users/<him>` →
   **401**. That endpoint carries `Depends(auth.require_api_key)`; the ONE call in `sobInit()`
   that makes it sent no `X-Api-Key`, while every neighbour in the same file sends it. So
   `if (uRes.ok)` was false for **everybody**: `_eulaSigned` was never read, the note explaining
   why he is on that screen stayed hidden, and `sobGoPhase(3)` never fired. `dashPublish` said
   *"One step first — please read and accept the Terms"* and then dropped him on **phase 1**, a
   listing preview whose only button reads "Looks good". Nothing there mentions terms; they are
   two unexplained taps further on. Fixed on two legs — send the key, and a gate that cannot read
   the truth now fails **towards** asking (a failed lookup still lands a refused publish on the
   Terms). Strictly tightening. Shipped `c3c1fdd`, **live 04:20:01Z**, then re-walked: handover
   lands on `sob-p3`, the note shows, terms render **v1.18 / 106,368 chars**, the scroll gate
   opens, both boxes tick, publish answers **200**, and a **logged-out** reader sees
   `listing_status: "live"`. PASS on every leg.
3. **THE LETTER TO RICK WEMPLE HAS GONE.** 04:26Z, Resend id `01a0d1a8-9cd1-778a-8831-93b9bb4626a0`,
   through `emailer.send_email` on the box — the one place every send passes (RUL-106(a)) — with
   David's permission printed into `sent_log.json` (RUL-106(b)). His order was **flow first**, and
   the flow fix was live and walked green before the send. All six pre-send checks pass; the sixth
   is this run's walk. The publish link is the RG-0447 recipe: 7 days, `&draft=382`,
   `&src=recoup-382`, minted on the box, fail-closed on an empty secret. The withdraw link needs
   no session. Opt-out in the footer plus the RFC 8058 header. One send, no follow-up.
   **Rick's OWN link was deliberately NOT walked:** consuming it creates a users row for him and
   stamps something that looks like human use on the funnel ONBOARD-REAL-1 just cleaned, and
   publishing his advert is barred by §3. Two identical links on the same code path were walked
   instead. Evidence grade: Resend **accepted** the message and returned an id; delivery itself is
   not confirmed, because that key is send-only (`GET /emails/{id}` → 403).
4. **RG-0400 was already closed and GOAL_STATE was carrying a stale claim about it.** The
   "fourth, unsynced v1.10 copy in `sob-eula-box`" does not exist: there is no such element, the
   live page's acceptance box holds **no** EULA text of its own, and the box renders `_EULA_HTML`
   at runtime — **proven in the browser**, v1.18, 106k chars, the version the site publishes. The
   entry has been holding since 20 Sep. An hour of the session was spent confirming that the thing
   this file called the biggest unowned item in the publish path was finished.
5. **Boards.** Before: 434 entries · 408 holding · 1 regressed · 0 UNVERIFIED.
   After: **437 · 409 holding · 3 REGRESSED · 21 open · 4 ready to lock · 0 UNVERIFIED**;
   `rulings_check` 142 rulings, **0 FAIL**, 24 WARN. RG-0449 reads `[ ok ]`, and it FAILs on all
   three source legs against a reverted tree (run 18's rule: judge the condition, and run the
   entry against both trees rather than reading it).
6. **Two of the three reds are NOT ours and arrived mid-run, in a file a parallel lane is editing
   live** — `bea_main.py`, last written 04:23:48Z, after our deploy: **RG-0351** (3 plain
   `datetime('now')` calls back) and **RG-0405** (the door's publish-visibility assertion moved
   with ONE-TAP-PUBLISH-1). The third is the standing **RG-0431**. No lock is held on the file;
   SO-5 says the owner ships it. They are red on the ledger, which is a findings board, so they
   are recorded — they were NOT also written into the DAILY_WATCH table, and that is a deliberate
   omission of a 1,250-line surgical edit at the end of a budget, not an oversight.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **Did Rick answer?** `sqlite3 -readonly CityLauncher/data/prospects.db` on his row, and look
   for `src=recoup-382` arrivals. If he published, the number is 1 — **re-run the scorer, do not
   assume**. If he withdrew, that is also a complete answer and the loop closes. **Do not write to
   him again either way** (RUL-106(e), and the letter promised it).
1. **The three reds.** RG-0351 and RG-0405 are the parallel lane's if it is still in flight; if
   `bea_main.py` has been quiet for hours, they have been abandoned — say so, then fix them.
   RG-0431 has now been red for three days on the same line (`extra_status='draft' WHERE id=?`).
2. **The journey is green end to end for the first time. The bottleneck is now upstream of it.**
   2,573 letters have produced 8 human clicks ever. ~390 addresses remain, and on measured
   performance that is not 20 listings. The next lever is the letter and what the click lands on,
   not the publish flow — see the note to David below.
3. **Worth an instrument, not a fix:** the terms box is 39,829 px in a 338 px window — about
   **118 screenfuls** to swipe on a phone before the confirm row appears. The scroll gate is
   deliberate (conspicuous *and* acknowledged) and the text is David's (RUL-020), so this is
   reported, never adjusted by a session.
4. Still carried, with the reason each was deferred: **RG-0409** ladder values + cap 40 ·
   **RG-0410** reachability gate · **RG-0411** taxi-drop area unit · **RG-0412** EULA in the launch
   languages · **RG-0414** DOOR-RETURN-1 · **RG-0419** Quick door prices only in rands ·
   **RG-0437** rulings_check false FAIL (now READY TO LOCK).

## OPEN LOOPS

- **Rick: sent, waiting. Nothing further is owed to that loop by us.**
- **RG-0431 (red, day 3, not ours)** · **RG-0351 and RG-0405 (red, arrived mid-run, the parallel
  lane's `bea_main.py`)**.
- **RG-0419 (open): the Quick door prices only in rands.** Not a defect to paper over.
- **RG-0414 (open): the only way back from the public door** is an emailed sign-in link plus one
  browser's localStorage. Run 18 made the emailed half real; run 19 made the far end of it work.
- `_get_json()` still does not exist (specified by run 13, unwritten). 14 `json.loads(_get(...))`
  sites remain individually unprotected against a 200 that is not JSON.
- The ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run — why a shard is slow.
- **`git status` is unusable from this sandbox** — it creates `.git/index.lock`, cannot unlink it,
  returns empty output, and leaves a lock that blocks Windows git. Use `git show` (safe) or the
  host queue. `mount_check.sh` and `request_deploy.py --all` both work fine.
- Listings 386/387/388/391/393/395/396/397/398 and run 19's **399 and 400** are ARCHIVED, not
  deleted; 3 files in `_to_delete/` and 9 orphaned `tmp_obj` files need a deletion, which is
  David's. Run 19's walks also left two `users` rows (`probe-run19-walk@` and
  `probe-run19-walk2@trustsquare.co`, EULA stamped). They cannot touch any onboarding figure:
  `reconcile_conversions` joins FROM prospects, and neither address is a prospect — the funnel
  read 5 registered before and after. Recorded anyway, because an unexplained account is how the
  42 started.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**The one thing that was waiting on him is DONE and needed nobody.** The pre-send check that five
runs called a five-minute job only a person could do was a browser walk, and a browser I drive can
do it on a throwaway address. Nothing on this goal is waiting on David today.

- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry very
  different weight in South Africa. The Quick door is labelled `homehelp` today.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than sitting as a strip under a "list your business" letter written for companies?
- **D5 — where does she come from at all?** We have no list of housecleaners and no directory to
  harvest. Four-week or four-month move.
- **D8 — the 1,114 teachers on the education register.** The largest reachable block left, held by
  `blocked_categories` as a person-only/POPIA call, not by anything technical.

**One thing David should KNOW, not decide:** the floor is now fixed all the way to a live advert,
and it is proven by a harness that can be re-run on demand. What is left is arithmetic: ~390 cold
addresses and a measured click rate of about three in a thousand do not make 20 sellers. The route
to 20 runs through D4 and D5 — a door aimed at one kind of person, and a list of those people —
not through more of the same letter.

## WHAT RUNS 17–19 LEARNED ABOUT THEMSELVES

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
