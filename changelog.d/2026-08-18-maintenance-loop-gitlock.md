## 2026-08-18 — maintenance-loop addendum: GIT-LOCK-3 fired for real

- `git_unlock.py` found and healed TWO stranded lock-class files (`.git/index.lock`,
  `.git/HEAD.lock`) by rename into `.git/stale_locks/` before this run's commit, and
  noted 31 orphaned `tmp_obj` files for the host-side sweep. First live proof the
  sandbox half of the self-heal does its job unprompted.
- Also observed this run: `changelog_compile.py` and `status_compile.py` ran on the host
  at 07:35 while the session was mid-flight and folded this run's fragments into
  CHANGELOG.md / STATUS.md before the session could `git add` them. Not a fault — the
  machinery worked — but the lesson for the next session is: after writing a fragment,
  re-check whether it still exists before staging it, and stage the compiled file
  instead if it has already been folded.
