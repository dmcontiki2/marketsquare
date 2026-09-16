## 2026-09-16 — Four reds cleared, and two of them were the instrument lying

Attended pass on David's instruction, "fix what is fixable". Board went from
**1 regressed** (and then 2 on the evening run) to **0 regressed, 0 unverified, exit 0** —
366 entries, 344 holding. Rulings check 108 / 0 FAIL.

**DW-123 — GIT-LOCK-5: both unlock lanes can now see a ref lock.** On 14 Sep the daily
watch's own commit died on `.git/refs/heads/main.lock` while `git_unlock.py` — which had run
first, exactly as GIT-LOCK-3 requires — reported "no stale locks, nothing to sweep". It swept
`index.lock`, `HEAD.lock`, `packed-refs.lock`, `next-index-*.lock`; a ref lock lives one
directory down. The tool written to clear the blocker could not see the blocker, and
`git_unlock.bat` was blind the same way — which corrects the watch row's own claim that the
host lane already covered it. Now: a **recursive** glob over `.git/refs` (tags and remote refs
strand like branches, and a hand-kept branch list is one somebody forgets), ref locks counted
as **blocking** (without that `--check` exits 0 over a lock that makes commits impossible),
aside names flattened to `refs_heads_main.lock` so same-named refs cannot collide, and the
matching `for /r ".git\refs"` sweep host-side. Safety untouched: nothing swept while `pgrep`
sees a live git; the sandbox renames and never unlinks. **Proven by sabotage** — lock planted,
commit confirmed to fail with the exact 14 Sep message, old rule confirmed blind, `--check`
exited 1 naming the file, sweep renamed it aside, same commit succeeded. Asserted by
**RG-0379** (LOCKED), which returns four FAILs against the pre-fix copies.

**DW-126 — the Model Register had aged past its own limit.** `ai_price_card.json` was
`verified_at` 2026-08-01, 46 days against a 45-day maximum, so by the Live-Values Doctrine
every AI cost decision was running on remembered prices. All 7 priced models re-verified
against first-party pages and dated vendor sources. Six unchanged. **One moved: `gpt-5.6-sol`
$5/$30 → $4/$20**, cut 21 Aug 2026, which OpenAI describes as holding "at least through
21 Nov 2026" — promotional, not a new floor, and Sol is wired, so a comparison run off the old
figure would have ruled it out on a cost it no longer carries. Captured while verifying:
`gemini-3.7-flash`'s $0.75/$3.75 is effective only **through 31 Dec 2026 and doubles on
1 Jan 2027** — now a diary entry rather than a January surprise. Both entries carry
`price_review_by`. Card bumped to 2026-09-16.1 with a `last_verification` block naming what was
unchanged, what moved, and what could not be checked (the Scaleway EUR console rate is
unobservable without the account — recorded as not-verifiable rather than guessed).
`ai_funnel_snapshot.json` regenerated so the +1 strip is not staler than the register
(RG-0020), and the stale `Sol $5/$30` **comment** beside `TASK_MODEL` in `ai_provider.py`
corrected — a stale comment next to the routing table is exactly how a decision runs on a
remembered price. **No model choice was changed**: RUL-009 reserves that to David.

**DW-127 — RG-0347's red was the instrument, not the product.** The board reported that the
buyer-facing credentials list had stopped naming the interim ID points, which would be a
truthfulness defect on a page buyers read. Traced rather than assumed:
`seller_public_credentials()` builds **all three** of its groups through `_earned_display()`,
the very function that appends "— confirmation pending". The property held throughout. The
15 Sep TRUST-ONE-SET-1 refactor correctly moved that copy into the shared formatter, and the
assertion was a **forward-only 4000-character window** from the panel's `def` — so it went red
over a change that improved the code. Second instance of a class that already cost a session
(RG-0367, amended 14 Sep for the same reason). Replaced with three **reachability** legs —
formatter still names it, buyer panel still routes through it, seller's own breakdown still
shares it — which is **stronger** than the window, because a window can pass on dead copy while
the panel renders from elsewhere. Sabotage-tested three ways.

**DW-121 (half).** `list(zip(cities[:12], stamps, strict=True))` in `regression_ledger.py` —
in the file that grades everything else, a silent truncation was worth more than its LOW grade.
Row deliberately **left open**: its originating check is the Monday deep-scan lane, and running
`deep_scan.py` off-lane would rewrite the baseline Monday's delta is measured against.

**Verified, fixed overnight by the maintenance loop, not by this session:** DW-124 (pg-readiness
— ten call sites made portable via `_sql_since()`, baseline **tightened 17 → 15**, so the count
came down rather than the bar going up; `deploy_audit.log` clean since 05:44, ending an
eleven-day DANGER streak) and DW-125 (the fault-report widget on `quick.html`, `q/index.html`
and `confirm/index.html` — 18/18, all three probed live at 200 carrying it).

Not shipped: the two deploy-target changes here (the `ai_provider.py` comment and the
regenerated funnel snapshot) are committed but not deployed — another session has uncommitted
work in `bea_main.py`, and neither change needs to be live tonight.
