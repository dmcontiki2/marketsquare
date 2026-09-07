## 2026-09-06 — EMAIL-VARIANT-1 + FUNNEL-READ-1 (the letter can now be tested, and the test can be read)

**David's framing after the viability review:** *"Our best weapon is the running cost which is super
low, it allows us the freedom of changing and if needed experimenting."* Correct — and that freedom was
theoretical, because there was no way to run an experiment on the letter and no cheap way to read one.
Both now exist.

**Why the letter is the right target.** The review measured 981 sent, **20.8% human opens** (healthy —
subject line and deliverability are fine) and **0.45% human clicks**. People read it and do nothing. The
bottleneck is the ASK, and the current ask is large: fill a listing form, add subjects, rate, bio and up
to ten photos, accept terms, create an account — then consider a $20/mo Pro subscription and a Founders
Badge. That is asked of a stranger, for a marketplace with no buyers on it yet.

**EMAIL-VARIANT-1 — A/B on the letter.** `active_variants()` reads arms per category from
`waves_policy.json` (`defaults.email_variants`); absent or single-armed means no split, so nothing
changes for any category nobody has armed. `pick_variant()` assigns deterministically so a re-send never
moves someone between arms and a dry-run shows exactly what a real run sends. `load_template(cat, arm)`
resolves `<base>.<arm>.html` and **falls back to the base letter when the file is absent** — arming a
category can never stop a wave. The arm rides the EXISTING `?src=` tag (WAVE-TAG-1's one builder), so a
variant's signups attribute themselves with no app change at all, and is recorded on the send event so
opens and clicks split by arm even with zero signups — which at 0.45% is the case we will mostly read.

**The bug this nearly shipped with, caught in test the same hour.** `arms[pid % len(arms)]` put four
consecutive Durban prospects (2127, 2129, 2131, 2133) all in arm 'b' — the scraped ids are all odd. A
two-arm split on a modulus of structured ids is not a split: it sends everyone one letter and then
reports a confident, meaningless result. Now hashed. Verified **294/306 across 600 real rows**, stable
per prospect. Asserted, so the modulus cannot come back.

**FUNNEL-READ-1 — `emailer/funnel_report.py`.** The funnel in one command, graded, with `--by category
| city | country | variant` and `--server`. It enforces the evidence rules the review had to discover by
hand: bounces off `prospects.bounced_at` (never `email_events` — RG-0312), opens and clicks from
`click_register`'s **human** counts with the raw numbers printed beside them so the gap stays visible,
and a guard that refuses to name a winner under ~30 human clicks per arm. Reading the live board today:
976 sent · 71 undelivered · 139 human opens (15.4%) · **4 human clicks (0.44%)** · 62 raw click events.

**`--server` exists because the local mirror lies.** `pull_from_server.py` brings verdicts down but not
engagement: the local copy reported **48 human opens and 2 human clicks where the server held 186 and 4**.
An experiment judged on the mirror is judged on a quarter of its evidence.

**First experiment armed:** Tutors + teachers_trainers. Arm 'b' (`tutors_outreach.b.html`) shortens the
ask to *"I have written your listing — check whether it is right"*, removes the $20 Pro and Founders
Badge money ask from a first cold email entirely, and says plainly that the marketplace launched a week
ago and is thin. Same visual shell as arm 'a', so the test measures the ask and not the design. It goes
out with the next wave — which is currently held by the domain bounce gate until the address list is
cleaned. **RG-0313 LOCKED.**
