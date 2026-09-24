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
| 2026-09-24 (run 18, 02:51) | **0** | 0 | 0 | 2,573 emailed · funnel now says **5 registered** (4 e2e_test + Rick), so RG-0428 landed · raw 3, all e2e_test |

Target: **20 by Fri 31 Oct 2026** — 37 days. Runs 5–8, 11, 12 Fable 5.1; runs 9–10, 13–18 Opus 5.
*(Runs 21–22 Sep did not happen: the scheduled task was lost again. The server's own nightly
wave is unaffected by that — it fires from the box, not from a session.)*

## WHAT RUN 17 DID (23 Sep 2026, Opus 5) — compressed; the detail is in the ledger and changelog

1. **Restored the measurement.** Port 22 was dead from both vantages; the Hetzner rule already held
   this sandbox's IP and propagated on its own. RG-0099 and RG-0234 both went green (the backup lane
   needs SSH; it made a restore-tested archive at 17:05).
2. **RG-0428 ONBOARD-REAL-1 — "registered" was counting our own sending.** The reconciler stamped
   `onboarded_at` on the mere existence of a `users` row, and the agency wave creates one AT SEND
   TIME. All 40 non-test rows were estate agents created seconds apart inside one 22:10 UTC wave
   minute with every human field NULL. Now counts only an account a human has used **plus anyone who
   has built a listing in any status** — and that second leg is the point: leg one alone would have
   erased the one prospect who matters. 45 → 5. The goal number was never inflated; the funnel David
   reads was.
3. **RG-0429 named the one real person: Rick Wemple**, a licensed Montana outfitter from
   `register:moga`. Letter 11 Sep, and on 12 Sep he built listing 382 "Guided Fair Chase Hunts" —
   his words, his price, **four of his own photographs, quality_score 94**, the best non-demo advert
   on the platform. `created_at == updated_at`. No `users` row at all.
4. **Shipped that night, live and verified at 20:48Z (deploy ref 1aea5c4):** RG-0444 RETURN-LINK-1
   (the `!magicLink.active` line that exempted every cold prospect from the emailed way back — *the
   line that lost him*), RG-0443 EULA-PUBLISH-1 (publishing required no recorded acceptance when the
   seller had no users row, which is every first-time seller — PROVEN live with a 200 and a public
   listing), RG-0430 LISTING-COUNTRY-1 (every wizard listing was born `ZA`; 382 corrected to `US`),
   and RECOUP-WITHDRAW-1 (the take-it-down link, which really deletes the photographs).
5. **David came back live at 20:00Z and asked for Rick to be recouped.** He chose the route himself:
   fix the flow first, then ONE letter asking permission, carrying a take-it-down link we honour.
   Permission recorded with his words at `.secrets/recontact_permission.json`; letter drafted at
   `RECOUP_RICK_LETTER.md`; **not sent** — his order was flow first.
6. Also logged: RG-0437 (`rulings_check` can print a false FAIL from a mid-write read).

## WHAT RUN 18 DID (24 Sep 2026, 02:51–03:40 UTC, Opus 5)

0. **Probed run 17's deploy rather than trusting its success line.** The server's own
   `citylauncher/api/server.py` carries `ONBOARD-REAL-1` (4 hits, file dated 17:35Z) and the funnel
   now reads **5 registered** — four `e2e_test` rows and **Rick Wemple**, nobody else. The 45 is
   gone from the number David reads. (GOAL_STATE said to expect "1"; 5 is the figure run 17's own
   measurement predicted — 45 → 5 — and four of the five are declared test seeds.)

1. **THE FINDING, and it is the same leak one layer down — RG-0444's fix was wired to the wrong
   sender. RETURN-LANE-1.** `goHandoff()` — the sell flow's "draft saved" step — POSTed
   `/auth/request-link` and put a toast on screen saying *"we emailed you a link so you can finish
   anytime."* `/auth/request-link` is the **interactive** sign-in lane: a **20-minute** token, and
   no `&draft=` on the link. So "finish anytime" was twenty minutes, and inside those twenty
   minutes it dropped him on the hub's front page instead of the advert he had just written.
   **The right letter was already being sent** and had been since SELLFLOW-RETURN-1 (18 Sep):
   `POST /listings` fires `_quick_draft_return` for the self-serve lanes — seven-day token,
   `&draft=<id>`, fails closed on an empty signing secret. PROBED, not read: a `source='sellflow'`
   draft logged `quick-return mail for draft 398: sent`. So the client call was a **second letter,
   worse than the first, arriving beside it — and the one the seller was told to expect.** Removed;
   the toast stays (a letter really is sent) and now says what is in it.
2. **RG-0444's assertion was a PROXY and is corrected, not weakened.** It read
   `"/auth/request-link" in ms.js` as proof "the return path has a sender" — it was pointing at the
   wrong sender, so what it proved present was exactly the letter that fails. It now asserts the
   lane that carries him back: `sellflow` in `_SELF_SERVE_LANES`, `_quick_draft_return` present,
   `goHandoff` tagging `source:'sellflow'`, and the block NOT calling the 20-minute lane.
3. **RG-0447 RECOUP-LINK-TTL-1 — the class, and it caught the letter before it went.** A sign-in
   link that travels in a *letter* is never minted from the interactive lane. The code was already
   right in all six minting sites; the defect was in a **written recipe**. `RECOUP_RICK_LETTER.md`
   (23 Sep) told whoever sent it to mint Rick's publish link from `/auth/request-link` — a
   twenty-minute button, posted to a man who opens his post when he opens it — and it carried no
   `&draft=382` either. The entry FAILs against the 23 Sep letter on **both** legs and passes
   against the corrected one. Recipe now: 7 days, `&draft=382`, `&src=recoup-382`, minted the way
   `_quick_draft_return` does, plus the unexpiring fallback stated in the letter's own words.
4. **RG-0429 rewritten, because as written it was false in both halves.** It claimed the wizard has
   no route past the account wall (HANDOVER-PUBLISH-1 already implements RUL-145's shape) and that
   the wall is the defect (**RUL-166**, David, 23 Sep, rules the EULA acceptance *moves* and never
   goes away — an entry demanding no-account publishing would have put this board in standing
   conflict with a later ruling of his). It now asserts the property that is load-bearing, in three
   legs: the road exists · something sends the link with nobody exempted · that link outlives the
   reading of the letter.
5. **Two of the recoup letter's six pre-send checks now PASS on live evidence.** The withdraw link
   was walked in a real browser: a throwaway draft with a real uploaded photograph went
   `archived / withdrawn_by_seller`, and the photograph answered **404** at its public URL
   afterwards (200 before) — the letter's promise to delete is kept, not merely displayed. And the
   23 Sep publish hole stays shut: `PUT /listings/{id}/publish` answers 401 with *and* without
   `accepted_terms=1` for a caller with no session. Fix B is live too: a fresh Montana draft is
   born `country='US'`.
6. **Boards.** Before: 433 entries, 408 holding, 1 regressed (RG-0431, the language lane's),
   0 UNVERIFIED. After: 434, 408 holding, **1 regressed — still RG-0431, still not ours**,
   0 UNVERIFIED, 4 ready to lock. `rulings_check` 142 rulings, 0 FAIL, twice.
   RG-0154 went red mid-run because a new changelog fragment put `session_counter` behind the
   evidence; re-derived to 206 and green again — my consequence, not a finding.
7. **LIVE AND PROBED 24 Sep 03:44Z, deploy ref `1a7a23c`.** Not read from a success line: the
   server's own `static/ms.js` and the CDN-served copy both carry `RETURN-LANE-1`, the return-link
   block no longer calls `/auth/request-link`, the condition no longer exempts invited arrivals, and
   the toast now reads "a link straight back to this advert. It works for a week."
8. **Housekeeping worth knowing:** `git status` **cannot be run from this sandbox any more.** It
   creates `.git/index.lock` and then cannot unlink it (deletion is off), so it returns empty
   output and leaves a lock that blocks Windows git. Mine is moved to `_to_delete/`. Read git state
   host-side or not at all; the commit went through the host queue (`quiet_commit.py`), which is
   what that lane is for.

## WHAT THE NEXT RUN SHOULD PICK UP

0. **PROBE that run 18's deploy landed.** `scripts/request_deploy.py --status`, then confirm the
   SERVER's `static/ms.js` carries `RETURN-LANE-1` and no longer POSTs `/auth/request-link` from
   `goHandoff`. A tool printing success is EXECUTED, not PROBED.
1. **THE RECOUP LETTER IS ONE CHECK FROM SENDING, AND THAT CHECK NEEDS A HUMAN.** Five of the six
   pre-send items in `RECOUP_RICK_LETTER.md` now pass on live evidence. The sixth — walk the publish
   link end to end in a real browser **as a signed-in arrival**, confirm the advert is publicly
   visible, archive the probe — could not be done by run 18: driving a browser to a URL that carries
   a sign-in token is refused in an unattended session by a credential guard, and every other route
   to a session needs the same token. It is about five minutes of work **with David at the
   keyboard**, or by any attended session. Do not send the letter until it passes; do not weaken the
   item. Everything else for the letter is ready, including the corrected link recipe.
2. **RG-0400 is now the biggest unowned thing in the publish path** — the EULA box a seller actually
   ticks (`sob-eula-box` in marketsquare.html) is a FOURTH, unsynced copy reading v1.10 while the
   site publishes v1.18. It is legally load-bearing, it sits inside every publish journey including
   Rick's, and it blocks RG-0412. Restyled markup, so no safe mechanical sync: render the box from
   the one source. Treat it as the session's one feature and **never bash-write that file.**
3. **RG-0430 is closed; RG-0419 (Quick door prices only in rands) and RG-0414 are the small ones.**
4. **Do not raise the batch and do not go looking for a broken sender.** ~390 addresses remain.
   See `GOAL_FACTS.md`.
5. **RG-0431 is red for the second day and it is the language lane's** — `bea_main.py` lost
   `extra_status='draft' WHERE id=?`. No work lock is held on it any more, so the owner may have
   finished and left the entry behind. Run 18 did not touch it (RUL-140 was about the lock; the
   reason now is one-fix-per-task). If it is still red on the 25th, it has been abandoned rather
   than in flight — say so, then fix it.
6. Still carried, with the reason each was deferred: **RG-0409** ladder values + cap 40 ·
   **RG-0410** reachability gate + post-confirm glimpse · **RG-0411** taxi-drop area unit ·
   **RG-0412** EULA in the launch languages (**waits on RG-0400**) · **RG-0414** DOOR-RETURN-1 ·
   **RG-0419** per-country question sets for the Quick door · **RG-0437** rulings_check false FAIL.

## OPEN LOOPS

- **The recoup letter to Rick: one pre-send check left, and it needs a person** (see next-run item 1).
- **RG-0400 (open): the EULA a seller actually ticks is a FOURTH, unsynced copy** —
  `sob-eula-box` in marketsquare.html reads v1.10 while the site publishes v1.18. Restyled markup,
  so no safe mechanical sync; render the box from the one source. **Blocks RG-0412.** Now the
  biggest unowned thing in the publish path.
- **RG-0431 (red, not ours): the language lane's `extra_status='draft'`.** Second day. No lock held.
- **RG-0437 (open): rulings_check can print a false FAIL from a mid-write read.** Owned lane.
- **RG-0419 (open): the Quick door prices only in rands.** Not a defect to paper over.
- **RG-0414 (open): the only way back from the public door** is an emailed sign-in link plus one
  browser's localStorage. Rick is the proof. Run 18 at least made the emailed half real.
- `_get_json()` still does not exist (specified by run 13, unwritten). RG-0401 covers most of it;
  14 `json.loads(_get(...))` sites remain individually unprotected against a 200 that is not JSON.
- The ledger's `rg_no_third_party_script_on_surface` downloads ~16 MB per run — why a shard is slow.
- `marketsquare.html` reports `[TORN]` to `mount_guard.py` as "mount LARGER than committed but
  git-clean". Probably CRLF normalisation, not a tear — but **never bash-write that file**.
- **`git status` is unusable from this sandbox** — it creates `.git/index.lock`, cannot unlink it,
  returns empty output, and leaves a lock that blocks Windows git. Use the host queue.
- Listings 386/387/388 ARCHIVED not deleted; probe listings 397/398 archived (run 18, never public);
  3 files in `_to_delete/` and 9 orphaned `tmp_obj` files need a deletion, which is David's.
- RG-0346 (agency letters lack the console CTA) — open, adds no nightly volume.
- Film 07 (Liquidation) unpublished — David's click, when he chooses.

## OPEN QUESTIONS FOR DAVID (batched, never dripped)

**D9 IS ANSWERED — he answered it live on 23 Sep and chose the route himself.** It is not re-asked.
What replaces it is not a question but a five-minute job only a person can do:

- **THE ONE THING WAITING ON HIM.** The letter to Rick is drafted, its permission is recorded in his
  own words, its link recipe is corrected, and five of its six pre-send checks pass on live evidence.
  The sixth needs someone signed in, in a real browser: open the minted link, tap Publish, read the
  Terms, tick, confirm the advert is publicly visible, archive the probe. An unattended session is
  refused when it drives a browser to a URL carrying a sign-in token, so this one cannot be automated
  away. **It is the last thing between this goal and the number 1.**
- **D3 — what is she called?** "Housecleaner", "domestic worker", "home help", "cleaner" carry very
  different weight in South Africa. The Quick door is labelled `homehelp` today.
- **D4 — do the South African letters get re-aimed at the Quick door** as the primary call to action,
  rather than sitting as a strip under a "list your business" letter written for companies?
- **D5 — where does she come from at all?** We have no list of housecleaners and no directory to
  harvest. Four-week or four-month move.
- **D8 — the 1,114 teachers on the education register.** The largest reachable block left, held by
  `blocked_categories` as a person-only/POPIA call, not by anything technical.

**One thing David should KNOW, not decide:** cold email has roughly 390 addresses left and, on
measured performance, that is not 20 listings. The route to 20 is "stop losing the people who already
said yes". Run 17 found we were losing 100% of them at the last step. Run 18 found that the fix for
that was wired to the wrong sender, so the letter promising "finish anytime" was dying in twenty
minutes and landing him on the wrong page. Both halves are now closed.

## WHAT RUNS 17-18 LEARNED ABOUT THEMSELVES

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

**A fix is not finished until you follow the wire to the far end (run 18).** RETURN-LINK-1 was
correct, proven, deployed and celebrated — and it sent the wrong letter, because the sender it
switched on was the twenty-minute interactive lane rather than the seven-day one sitting two
functions away. The entry guarding it asserted the presence of that wrong sender as proof of health.
Nobody was careless; the assertion was written about the thing that was there, not about the thing
the seller needs. **Ask what the person RECEIVES, not whether the code ran.**

**Every good fix leaves a comment naming what it removed, so a substring test on a fix marker
convicts the fix (run 18).** Twice in twenty minutes: RG-0429's leg matched `!magicLink.active`
inside the paragraph documenting its removal, then the corrected RG-0444 matched
`/auth/request-link` inside the comment I had just written explaining its deletion. Both were caught
by running the entry against pre-fix, post-fix and reverted trees — never by reading it. Judge the
condition line, or the block forward from it; never the function.

**A lesson recorded in the one function it was learned in does not generalise by itself (run 18).**
QUICK-RETURN-TTL-1 was written on 18 Sep, about this exact man, with the seven-day figure and the
reasoning in full — and five days later a brand-new artefact reached for the twenty-minute lane
again. What stops it is an assertion about the CLASS, which is now RG-0447.
