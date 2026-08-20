## 2026-08-20 — DASH-FEED-1: the ops dashboard was reading sections nobody had updated since June

David asked for the ops dashboard to be brought to current status. The refresh ran, the docs
pushed, and the **Last done** and **Next up** panels still showed Session 155 and Session 139's
rental-availability work.

**Cause.** `/dashboard/summary` (bea_main.py) does NOT read the `## Current Session` narrative —
the block every session actually writes. It parses three specific headings and takes the **first
match in the file**: `## Live State`, `## Last Completed`, `## Next Session`. Those first matches
were dated **2026-07-06** and **Session 140 (June)**. Six weeks of sessions wrote diligently to a
part of STATUS.md the dashboard never looks at, and nothing anywhere said so.

**Fix (documents only, no code change).** Fresh `## Live State`, `## Last Completed (2026-08-20)`
and `## Next Session (priorities)` blocks inserted at the TOP of STATUS.md, above
`## Current Session`, so they win first-match. The stale June/July sections are left in place
untouched — nothing deleted, they simply no longer win. `## Next Session` bullets are ordered
deliberately: `_bullet_items()` feeds the "Session N — Next up" card and only the first four
render, so DW-057 (secret rotation), DW-051, DW-027 and DW-054 are the four a reader sees.

**Verified live**, not assumed: `GET /dashboard/summary` at 15:14 UTC returns the new liveState,
lastDone and nextGoals, and `directions[dir_next].items` carries the intended four. Parser also
simulated locally against the file before the push.

**Also this session:** DW-051 moved OPEN -> FIXED-UNVERIFIED in DAILY_WATCH/OPEN_ITEMS.md with
the MIGRATE-ENV-1 evidence (023/024/027 rc=0). It is deliberately NOT closed — 025/026 are not
individually evidenced, and only a passing check closes a row.

**Residual, named honestly:**
- **No ledger entry asserts this.** A future session could add a `## Last Completed` section
  higher in STATUS.md, or the endpoint could change its headings, and the panels would silently
  rot back to June with nothing going red. An assertion that `/dashboard/summary`'s `lastDone`
  is dated within N days of the newest `## Current Session` entry would close the class.
  Outstanding against the standing rule.
- **STATUS-COLLISION-1 was breached** in this session: the `## Current Session` afternoon entry
  was written with the Edit tool rather than a `status.d/` fragment. It landed intact (verified
  by line count and tail), but the rule exists because that write is exactly the one that got
  silently clobbered on 5 Aug. Recorded so it is not repeated.
- Session counter deliberately left at 155 — David's numbering convention, not Claude's to bump.
- BACKLOG.md's High/Medium panels still date from 15 Aug; two rows read "DONE (verified 2 Jun)".
