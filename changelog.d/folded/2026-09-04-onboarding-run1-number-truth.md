## 2026-09-04 — Onboarding goal, run 1: the scoreboard was reading high

**NUMBER-TRUTH-1 — the goal's own probe was gameable, and already wrong.**
ONBOARDING_GOAL.md §2 names `SELECT COUNT(*) FROM prospects WHERE published_at IS NOT
NULL` as probe A. PROBED on the live origin 4 Sep: it returns **2**. Both rows are
`source='e2e_test'`, `emailed_at IS NULL` — seed records for David's own household,
never cold-contacted. §3 bars exactly those rows, so the contract's probe reported 2
where the honest number is 0. Left alone, the next session reads 2 in good faith and
reports 10% of the target reached on day one, having done nothing. New instrument:
`scripts/onboarding_number.py` — runs both probes, applies the anti-gaming filter as a
pure testable `qualifies()`, takes `min(A, B)`, reports UNVERIFIED rather than a
healthy-looking zero when it cannot measure, and always prints the naive count beside
the honest one so the gap can never go quiet. **RG-0261 LOCKED**, asserting the filter
behaviourally on synthetic rows so it cannot rot while the live data is empty.
Live reading: honest **0**, naive 2.

**RG-0239 promoted to LOCKED — the check had outlived its own URL.**
Its body still probed a hardcoded `https://trustsquare.co/admin.html?magic=1…`, which
is the URL CTA-URL-1 stopped us sending on 1 Sep. So it measured a door we deliberately
keep shut and stayed red for a fault fixed on 3 Sep — on the one entry the whole funnel
hangs from. Repointed at the CTA `emailer.build_magic_link()` actually produces (leg 1)
and kept "bare /admin.html stays gated" (leg 2). Strictly stronger, not weaker: a
builder regressing to /admin.html now trips leg 1, and the wrong fix of 1 Sep trips
leg 2. PROBED 4 Sep 10:36Z — real CTA HTTP 200, no WWW-Authenticate; bare /admin.html
HTTP 401. Assertion corrected and said so in the ref, per CLAUDE.md.

**Funnel truth, measured not inferred.** 542 of the 546 emailed prospects received the
broken link and none has ever been re-mailed; only **30 people have ever been sent a
working one**. Of 64 recorded clicks, the click register scores just **2** as real human
clicks. The floor fixes (RG-0249 price basis, RG-0250 invitee AI draft, RG-0253
first-time publish) all shipped 3 Sep and are green, so the constraint has moved from
plumbing to supply. Queued the gated `launch_day_wave.bat` through the host queue.

**Reserved to David (batched, one question):** re-mailing the 441 still-mailable people
whose link was broken. `CityLauncher/resend_broken_link.py` exists, honours every send
guard and defaults to dry-run, but it is not on the allowlist — RUL-096(d) grants no new
sending authority.

Ledger after: every locked fix holding, 17 open (was 18). Rulings: 94 checked, 0 FAIL.
