- **STALE-CODE-1 — two of today's runs tested older code and looked like valid tests.** `git
  pull` says "Already up to date" whether or not the fix was pushed, and the 08:10 live run
  returned output identical to the previous one. Every run now prints
  `code <sha> [DIRTY-WORKTREE] <subject>` before anything else, pinned to the agent's own
  checkout rather than the rehearsal sandbox. **RG-0059 LOCKED.**
- Sixth green-looking no-op of the day, and the reason the count matters: every one of them
  passed its own check. The ledger and the "name the cause" discipline are what caught them,
  not the automation.
