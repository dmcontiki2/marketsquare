# GOAL_STATE — the onboarding agent's memory between runs

*Read this FIRST. Update it at the END of every run. Keep it under 100 lines: it is a state
file, not a diary. Durable background lives in `GOAL_FACTS.md` — read that when you need the
why; do not copy it back here. (The split run 16 asked for was done by run 17.)*

---

## SUNDAY SUMMARY

**Next one is due Sunday 27 September.** The 20 September summary has been removed rather than
left standing, because one of its headline sentences was false: it told David that 42 people had
opened an account and none had published. Nobody had opened an account. Those were rows our own
mailer creates when it sends to an estate agent — 40 of them, all made inside the 22:10 UTC wave
minute, not one ever used. The true figure was one real person. The counter is fixed (RG-0428)
and the correction went to David on the night of 23 September rather than waiting for Sunday.
Everything else in that summary stands: the cold list is running out, and the letter rewrite
shipped.

## THE NUMBER

Run it, never recall it: `python3 MarketSquare/scripts/onboarding_number.py`
If SSH is dead, queue it host-side: `run_py MarketSquare\scripts\onboarding_number.py`.

| date | published by own hand | probe A | probe B | notes |
|------|----------------------|---------|---------|-------|
| 2026-09-04 → 08 (runs 1–7) | **0** | 0 | 0 | baseline; raw 2 = e2e_test seeds, barred by §3 |
| 2026-09-12 (run 11) | **0** | 0 | 0 | 6,748 on the list · 1,482 emailed |
| 2026-09-13 (run 12) | **0** | 0 | 0 | 1,482 emailed at 01:00, +108 at 01:31 |
| 2026-09-18 (run 13, 02:30) | **0** | 0 | 0 | 1,942 emailed · first full journey walked |
| 2026-09-18 (run 14, 12:20) | **0** | 0 | 0 | 2,491 emailed · **8 human clicks ever** |
| 2026-09-19 (run 15, 01:00) | **0** | 0 | 0 | 2,499 emailed · listing 382 still a draft |
| 2026-09-20 (run 16, 01:00) | **0** | 0 | 0 | 2,499 emailed (pause held) · **466 sendable left** |
| 2026-09-23 (run 17, 16:50) | **0** | 0 | 0 | 2,549 emailed · **"45 registered" was 1** · both probes read live, and re-run host-side on a second vantage: same answer |

Target: **20 by Fri 31 Oct 2026** — 38 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–17 Opus 5.
*(Runs 21–22 Sep did not happen: the scheduled task was lost again. The server's own nightly
wave is unaffected by that — it fires from the box, not from a session.)*

## WHAT RUN 17 DID (23 Sep 2026, 16:50–19:30 UTC, Opus 5)

1. **Restored the measurement.** Port 22 timed out from both this sandbox and the cloud
   container; the daily-watch lane had it as RG-0099 red. The Hetzner rule ALREADY held this
   sandbox's IP (`hetzner_fw_selfheal.py --check`), so the standing advice — "add the IP" — was
   wrong; it propagated on its own minutes later. Consequences beyond the number: **RG-0234 went
   green too** (the backup lane needs SSH; it had been 11 days stale and made a verified,
   restore-tested archive at 17:05).
2. **THE FINDING — RG-0428 ONBOARD-REAL-1. "Registered" was counting our own sending.** The
   reconciler stamped `onboarded_at` on the mere existence of a `marketsquare.users` row, and
   `/agencies/wave-prep` creates one of those AT SEND TIME for every agency-class prospect.
   PROBED, not inferred: all 40 non-test rows were Estate Agents, created one every two or three
   seconds inside the 22:10 UTC wave minute on six consecutive nights, with last_seen, EULA,
   auth, photo and buyer token ALL NULL. Now counts only an account a human has used —
   **plus, and this leg is the point, anyone who has built a listing in any status.** Leg one
   alone would have been worse than the bug: it would have erased the one prospect who matters.
   Proven in all three directions (pre-fix code FAILs 3 ways; leg-one-only FAILs on exactly that
   assertion; current code passes). Measured on a copy of the live pair: 45 → 5, 41 retracted,
   1 correctly added, clicks preserved, second pass a no-op. **The goal number was never
   inflated by this** — `onboarding_number.py` demands published_at AND emailed_at AND a
   non-test source AND probe B. What was inflated is the funnel David reads.
3. **SECOND FINDING, and it is the whole goal — RG-0429 PUBLISH-WALL-1.** That surviving leg
   named the one real person: **Rick Wemple, a licensed Montana outfitter from `register:moga`.**
   Letter 11 Sep, and on 12 Sep he built listing 382 "Guided Fair Chase Hunts" — his own words,
   his own price, **four of his own photographs, quality_score 94, the best non-demo advert on
   the platform.** `created_at == updated_at`: he wrote it once and never came back. **He has no
   `users` row at all.** `POST /listings` needs no account; `PUT publish` needs an account with
   an accepted EULA and a plan slot. So the wall sits after all the work and before any result —
   the exact shape David ruled against in RUL-145. He is one step from being the number 1.
4. **Did NOT build a nudge lane, and the reason is a ruling not a preference.** The obvious move
   — email him — is barred by RUL-106: a 60-day floor on re-contacting any address already
   written to, *whatever the lane*, and RUL-106(e) reserves any follow-up programme to David
   explicitly. Checking that before building it is the only reason a night was not wasted.
   **The question is with David, framed as his.** The fix that needs nobody's permission is the
   flow itself (RG-0429).
5. **Logged rather than rushed:** RG-0430 LISTING-COUNTRY-1 — `POST /listings` names no
   `country`, so every listing a real seller creates is born `ZA`. Live proof: every seeded
   market is right (Chicago US, Denver US, London GB, Sydney AU) and the only wrong pair is
   **Montana|ZA, 4 rows** — every wizard-created listing there, Rick's among them. 92% of the
   addresses left are American. One fix per task, so it is an OPEN entry, not a hurried second
   edit to `bea_main.py`.
6. **RG-0437 RULINGS-SETTLED-READ-1** — `rulings_check` returned 1 FAIL, then 2 FAIL, then 0, 0,
   0 within minutes with no edit between, naming rulings that grep proved present. It reads a
   file a parallel lane is writing. Recorded and NOT fixed: RUL-140/SO-5, `work_lock` shows
   `scripts/rulings_check.py` owned by `standup-2026-09-23`. The owner ships it.
7. **Boards.** Before: 413 entries, 2 regressed (RG-0099 ssh, RG-0234 backup) — both now green.
   After: 424 entries, 391 holding, **1 regressed (RG-0157, not mine)**, 0 UNVERIFIED.
   `rulings_check` 139 rulings, **0 FAIL**, three consecutive runs.
8. **Deliberately did NOT commit.** SO-5 says commit once the tree is silent, and it is not:
   33 paths are dirty and most are the language lane's live work (`bea_main.py`, `ms.js`,
   `quick.html`, `roles/quick_i18n.json`) plus their untracked migration 048. A `git add -A`
   tonight would sweep another session's half-finished change into a commit with my message on
   it. The CityLauncher deploy does not need the MarketSquare tree, so it went anyway; the
   commit waits for whoever finishes last. Changelog fragment written to
   `changelog.d/2026-09-23-onboard-real.md` so the record does not depend on that.

## RUN 17 ADDENDUM — DAVID CAME BACK LIVE (20:00Z) AND ASKED FOR RICK TO BE RECOUPED

He chose: fix the flow, then ONE letter asking Rick's permission, carrying a take-it-down link we
honour, explaining we are following up on the effort he already made. Permission recorded at
`.secrets/recontact_permission.json` with his words; letter drafted at `RECOUP_RICK_LETTER.md`;
**neither sent.**

**The correction that matters: RG-0429 is WRONG as written and must be rewritten.**
`HANDOVER-PUBLISH-1` already exists — `?magic=1&…&drafted=1&publish=1` skips the plan screen,
shows the Terms, publishes, and asks for the account afterwards, which is exactly RUL-145's
shape. `dashPublish` is a second surface for stranded drafts. The flow was built; **nothing ever
sends the link that reaches it.** That is the real defect and it is much smaller.

**Proven live and it is the thing to fix first:** a fresh address created a draft and published it
with no account and no Terms accepted — 200, publicly visible. Every first-time seller is that
shape, Rick included. Spec in `PENDING_FIXES_RUN17.md` (fix A).

**BLOCKED, and not on a decision:** `bea_main.py` and `ms.js` are locked by
`lang-quick-2026-09-23` (taken 19:55Z, 12 h expiry). RUL-140/SO-5 — recorded, not edited. Done
anyway because it needed no locked file: listing 382 now reads `country='US'`.

## WHAT RUN 17 SHIPPED FOR RICK (23 Sep, 20:00-21:00Z, David live at the keyboard)

He asked for the recoup, chose the route himself (fix the flow, then ONE letter asking Rick's
permission with a take-it-down option we honour), released the language lane's lock so the work
could proceed, and accepted the residual exposure explicitly.

1. **RG-0444 RETURN-LINK-1 — the line that lost him.** `goHandoff()` emailed a "here is your draft,
   finish anytime" link only `if (!magicLink.active)`, reasoned as "invited users already have
   their own link". They do not: a cold letter's link restarts the sell flow, it does not return
   anyone to a draft. Every cold prospect has `magicLink.active === true`, so the one safety net
   under a stranded draft was off for exactly the people outreach exists to reach. Now always on.
2. **RG-0443 EULA-PUBLISH-1.** Publishing required no recorded acceptance when the seller had no
   users row — which is every first-time seller. PROVEN live: a fresh address published, 200,
   publicly visible, nothing accepted. The browser gate was good and enforced nothing.
3. **RG-0430 LISTING-COUNTRY-1 closed** in code, and listing 382 corrected to `US` on the live DB.
4. **RECOUP-WITHDRAW-1** — the take-it-down link: archives, and really deletes the photographs.
5. **RG-0429 was WRONG and is corrected in `PENDING_FIXES_RUN17.md`:** HANDOVER-PUBLISH-1 already
   implements RUL-145's publish-first-account-after. The flow was built; nothing sent the link.

**WATCH THIS — the language lane's AUDIT-AUTH-1 (23 Sep) ships alongside.** Publish now acts as the
proven session, not a typed `?email=`. Correct, and I want it — but its written justification is
"there are no onboarded listers... nobody to lock out", and that stopped being true the same night.
A cold arrival with no session now gets 401 on publish, which silently reverses HANDOVER-PUBLISH-1
for that population. RETURN-LINK-1 is what keeps the road open: the emailed sign-in link is now the
only way a cold seller reaches publish at all. **Rick's letter must therefore carry a `?signin=`
link, not a `?magic=1` one** — `RECOUP_RICK_LETTER.md` is updated accordingly.

**LIVE AND VERIFIED 23 Sep 20:48Z.** Deploy ref 1aea5c4; the server's own copies carry both
markers; service active. PROBED, not read: a Montana draft now stores `country='US'` (was `ZA`),
and the exact call that returned `200 "Listing is now live"` with no account and nothing accepted
at 20:01Z is now refused. **Said precisely, because it matters:** it is refused `401 Please sign
in to do that` — AUDIT-AUTH-1 catches it before the EULA gate does, so the dangerous behaviour is
closed live but MY gate specifically was proven by source assertion and by the pre/post ledger
test, not exercised end to end on the live box (no session and no MS_ADMIN_KEY from this vantage).
It becomes load-bearing the moment a SIGNED-IN seller publishes — which is exactly Rick's path, and
exactly what the letter's checklist requires walking in a real browser before it sends.
Both test listings archived; nothing of mine is public. Boards after: 432 entries, 406 holding,
0 UNVERIFIED, `rulings_check` 142 / 0 FAIL. The one red is RG-0431 LANG-LAYER-1 — the language
lane's own entry, mid-flight, not ours.

**The letter is NOT sent.** David's order was flow first. Permission recorded with his words at
`.secrets/recontact_permission.json`; the pre-send checklist is in the letter file and every item
of it must pass, including walking the link end to end in a real browser as a signed-in arrival.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **PROBE that the CityLauncher deploy landed.** Requested 23 Sep ~19:20 UTC for RG-0428; read
   `CL_DEPLOY_RESULT.txt`, then check the SERVER's copy of `api/server.py` carries
   `ONBOARD-REAL-1`. A deploy tool printing success is EXECUTED, not PROBED. Then re-run the
   number and confirm the funnel line reports **1 registered, not 45**.
2. **RG-0429 IS THE BUILD. Nothing else comes close.** One man with a 94-scoring advert is
   stopped by a wall we put there. Bring the wizard under RUL-145: the account and the EULA are
   asked for *before* the work or folded into one tap at the end — the EULA is legally
   load-bearing and does not get removed, only moved. It touches `marketsquare.html`, so treat
   it as the session's one feature, never bash-write that file, and expect RG-0400 (the
   wizard's `sob-eula-box` is a fourth unsynced EULA copy) to land in the same piece of work.
3. **RG-0430** is the small one worth doing first if RG-0429 will not fit: one column on the
   create path, and the first American who publishes is not filed as South African.
4. **Do not raise the batch and do not go looking for a broken sender.** The list is being
   consumed; ~416 addresses remain. See `GOAL_FACTS.md`.
5. **RG-0157 is red and it is the language lane's, not ours** — untracked migration
   `048_i18n_zu_xh_nso_hand_drafts.py`. It blocks the MarketSquare deploy ref, not CityLauncher's
   own bat. Do not "fix" another lane's mid-flight work; if it is still red in a day, say so.
6. Still carried, with the reason each was deferred: **RG-0409** ladder values + cap 40 ·
   **RG-0410** reachability gate + post-confirm glimpse · **RG-0411** taxi-drop area unit ·
   **RG-0412** EULA in the launch languages (**waits on RG-0400**) · **RG-0414** DOOR-RETURN-1 ·
   **RG-0419** per-country question sets for the Quick door.

## OPEN LOOPS

- **RG-0429 (open): the publish wall.** The goal's single biggest leak. See above.
- **RG-0400 (open): the EULA a seller actually ticks is a FOURTH, unsynced copy** —
  `sob-eula-box` in marketsquare.html reads v1.10 while the site publishes v1.18. Restyled
  markup, not a byte copy, so there is no safe mechanical sync; the real fix renders the box
  from the one source. **Blocks RG-0412, and sits inside RG-0429's scope.**
- **RG-0430 (open): every wizard-created listing is born country='ZA'.**
- **RG-0437 (open): rulings_check can print a false FAIL from a mid-write read.** Owned lane.
- **RG-0419 (open): the Quick door prices only in rands.** Not a defect to paper over.
- **RG-0414 (open): the only way back from the public door** is an emailed sign-in link plus one
  browser's localStorage — the two things this market is least likely to have. Rick is the proof.
- `_get_json()` still does not exist (specified by run 13, unwritten). RG-0401 covers most of it;
  14 `json.loads(_get(...))` sites remain individually unprotected against a 200 that is not JSON.
- The ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run — why shard 1 is slow.
- `marketsquare.html` reports `[TORN]` to `mount_guard.py` as "mount LARGER than committed but
  git-clean". Probably CRLF normalisation, not a tear — but **never bash-write that file**.
- Listing 386/387/388 ARCHIVED not deleted; 2 files in `_to_delete/` and 9 orphaned `tmp_obj`
  files need a deletion, which is David's.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**D9 is the only one that is worth anything this week. The rest are positioning.**

- **D9 — NEW, and it is one sentence.** May a short note go to someone who has built an advert
  and not put it live, telling them it is ready and how to finish? RUL-106 bars it (60-day floor,
  every lane) and RUL-106(e) reserves the programme to him. The door already exists and is
  dated: `TS_RECONTACT_PERMISSION`. **Rick Wemple is the live case and his advert is eleven days
  old.** Asked 23 Sep. Nothing is built until he answers; the flow fix (RG-0429) proceeds either
  way.
- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry
  very different weight in South Africa. The Quick door is labelled `homehelp` today.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to
  action, rather than sitting as a strip under a "list your business" letter written for companies?
- **D5 — where does she come from at all?** We have no list of housecleaners and no directory to
  harvest. Four-week or four-month move.
- **D8 — the 1,114 teachers on the education register.** The largest reachable block left, held
  by `blocked_categories` as a person-only/POPIA call, not by anything technical.

**One thing David should KNOW, not decide:** cold email has roughly 416 addresses left and, on
measured performance, that is not 20 listings. The route to 20 is no longer "send more"; it is
"stop losing the people who already said yes". Run 17 found that we have been losing 100% of them
at the last step, and that we had been counting our own mailer as if they were people.

## WHAT RUN 17 LEARNED ABOUT ITSELF

**Ask what CREATES a number before you believe what it means.** "42 registered" survived four
runs and reached David in a written summary, because it was plausible, it was rising, and it
flattered. One query — group the user rows by the minute they were created — killed it in
seconds and turned the week's headline into a correction. An instrument that reads HIGH is the
one least likely to be questioned; the contract says so in §2 and it was still true here.

**The fix that is obviously right can be worse than the bug, and the check for that is to run
it.** Leg one of ONBOARD-REAL-1 — "count only accounts a human has used" — was correct,
defensible, and would have erased Rick Wemple from the record, because the app creates a bare
account row the moment a listing is made. Writing the assertion as a *behavioural* test against
a synthetic pair, instead of grepping for a needle, is what exposed it, and the same test now
stands guard over it.

**Read the ruling before building the thing.** The night's second plan was a draft-nudge sender.
It is barred by RUL-106 in terms so specific they name the lane, the enforcement point and the
one permitted door. Ten minutes of reading saved a wasted build and turned it into the one
question worth putting to David. Run 16 wrote that the cheapest step in the chain is the one
nobody takes; the cheap step is not always a probe — sometimes it is reading our own law.

**And a quiet log is not a dead machine.** Three and a half days of silence in
`autodeploy_agent_log.txt` nearly went to David as "your automation is down". The agent logs
only when it has work; the heartbeat file said it had ticked 17 minutes earlier. RG-0355 has
said this in writing since 12 September. The alarm I was about to raise was already answered by
the board I had not finished reading.
