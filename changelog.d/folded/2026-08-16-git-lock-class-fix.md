## 2026-08-16 — GIT-LOCK-3: the stale-lock class gets its machinery (DW-026 executed)

David's call-out, and he was right: stale .git leftovers were the RULE (17 CHANGELOG
mentions, 44 accumulated HEAD.lock.stale-* asides, 4 next-index-*.lock, 480 orphaned
tmp_obj files, and DW-026 sitting OPEN since 7 Aug with the fix already prescribed).
The sandbox half of GIT-LOCK-1 had been left at "note it — do not force". Executed today:

- **scripts/git_unlock.py (NEW)** — the sandbox lane's self-heal, twin of git_unlock.bat.
  Key discovery: RENAME works on the FUSE mount where unlink is blocked (git's own
  commits prove it). Stale lock-class files (>15 min, no live git) are renamed into
  .git/stale_locks/; the host sweep deletes them. Ran it: 48 files healed on the spot.
- **git_unlock.bat widened** — next-index-*.lock joins the class; host sweep now deletes
  the stale_locks/ asides, HEAD.lock.stale-*, and tmp_obj orphans on every guarded run.
- **RG-0015 widened (DW-026's ask)** — asserts the class in BOTH lanes (bat coverage,
  py existence, deploy-bat DW-026 abort) plus a LIVE tripwire: a stranded blocking lock
  >60 min or a day-old next-index turns the ledger red the SAME DAY. Strengthened, never
  weakened.
- **Projects CLAUDE.md GIT-LOCK section extended** — sandbox rule on the record: run
  git_unlock.py before sandbox git writes; never rm a lock from the sandbox.
- Deploy-bat abort: verified already present since 7 Aug (DW-026 first ask — done then).
- DW-026 can close on tomorrow's watch: all three prescriptions now exist and are asserted.
