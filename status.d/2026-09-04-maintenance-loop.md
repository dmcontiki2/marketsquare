**Maintenance loop (4 Sep 2026, 05:34–06:00Z) — GREEN.** Fault queue empty: 35 rows,
**0 new / 0 fix-shipped** (26 verified · 7 closed · 2 duplicate), so no tester fix work
existed. The session's two items were instruments misreporting their own state.

- **RG-0259 (CODE-STAMP-2)** — `/dashboard/maint` was publishing `code: unknown
  (TimeoutExpired)` every sandbox run. `git status` measured 21.0 s on the FUSE mount
  against a 20 s timeout, and one shared `try` let that kill a SHA read in 0.1 s. Legs
  split, slow leg 300 s, unmeasurable dirtiness now says `DIRTY-UNKNOWN`. Live proof: run
  `2026-09-04T05:48:17Z` publishes `b26ca4d  DIRTY-WORKTREE …`.
- **RG-0260 (LEDGER-BOOTSTRAP-1)** — the ledger now bootstraps its own dependencies in
  `main()`. Third time the board read blind on `fastapi` (DW-082, DW-083, today); the cure
  existed since 28 Aug but its ordering lived only in prose, and the sandbox is ephemeral.
  Machinery replaces memory, per the standing rule.
- **RG-0187 corrected** (over-broad harness scanner, carve-out keyed to the installer's
  name, rationale on the record) and **RG-0236's false READY TO LOCK removed** — its own
  bar is "measured on real traffic", so it now stays open until
  `Records/OUTREACH_TRIAGE_MEASURED.md` exists. Not promoted.
- **Promoted OPEN → LOCKED:** RG-0252 (autodeploy agent live), RG-0255 (dev toggle gone
  from the served index), RG-0258 (maps read live stays).

**Ledger after: 253 entries · 235 holding · 0 REGRESSED · 18 open · 0 ready to lock ·
0 UNVERIFIED · exit 0.** Rulings: 93 checked, 0 FAIL, 3 WARN (RUL-093/094/095 have no
reflection assertions — pre-existing, named not fixed). No escalation brief (none due).
Committed only — NIGHTLY-SHIP-1 ships it.
