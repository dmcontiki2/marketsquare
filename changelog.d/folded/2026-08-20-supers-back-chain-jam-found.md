## 2026-08-20 — Supers are BACK, and the eyes immediately found the thing underneath (RG-0125)

David deployed and confirmed the supers show. Verified live rather than taken on trust: listings
265–272 all read `listing_status: live`, and every shelf answers — including local_market
(id 272), which must be asked for with `?category=local_market` because the default feed excludes
it by design.

**What actually fixed it:** the seed lane. `post_deploy_status.json` reads `seed: ok` — SUPER-HEAL-1
did the work, exactly as designed, in the lane that cannot be jammed.

**And the first thing the new eyes saw:** `023_relink_wonders_railexp.py` is **FAILING**, and has
been stranding 024, 025, 026 and 027 behind it. This is the same jam recorded on 18 Aug and
believed closed by MIGRATE-IMPORT-1 — 023 carries the CWD guard and still fails, so the import fix
was not the whole cause. It also explains the morning cleanly: 027 never ran because it never
could. Twelve hours ago that finding would have cost a session and an SSH login; it cost one
`curl`.

Recorded as **RG-0125** (OPEN): the migration chain must not be jammed. A migration that cannot
run is either FIXED or listed in `migrations/DEFERRED.txt` — the one thing it may never do is sit
there stranding the queue, which is precisely the DEFER-1 rule written on 9 Aug for this class and
not applied to 023.

**POSTDEPLOY-EYES-2:** EYES-1 named which migration jammed but not why, and the why still needed
SSH — half an eye is still a blind spot. The status file now carries the migration's own output
(last 3 lines on failure, last line on success). Proven locally against a simulated 023 failure:
the report reads `CHAIN JAMMED HERE (later migrations skipped) :: [023] REFUSE: cannot import
main (No module named main)`. So the next deploy states the cause without anyone logging in.

**Ledger.** RG-0123 (supers immortal) and RG-0124 (a deploy reports what it did) both **LOCKED** —
live-verified green. RG-0124's design corrected while locking it: a failed step is a FINDING it
reports, not a failure of its own — otherwise the entry that gives us eyes goes red for what the
eyes see. Chain health is RG-0125's job. RG-0123's local_market assertion **corrected, not
weakened**: it asked the default feed for a category the feed deliberately excludes, and reported
an empty shelf that was never empty. The app was right; the check was wrong.

Board: 118 entries, 0 regressed, RG-0125 the one real open item.

**Tooling note for the next session:** `io.open(path, "w", newline="\n")` raises ValueError on
this Python *after* truncating the file — post_deploy.sh was left 0 bytes and only the standing
"verify the write landed" rule caught it. Restored with `git show HEAD:<path> >` (unlink and
`git checkout --` are both blocked on this mount). Never pass `newline=` here.
