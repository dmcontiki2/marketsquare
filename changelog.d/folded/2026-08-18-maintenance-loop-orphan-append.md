- GIT-LOCK-3 fired for real this run: `git_unlock.py` found and healed TWO stranded
  lock-class files (`.git/index.lock`, `.git/HEAD.lock`) by rename into
  `.git/stale_locks/` before the commit, plus 31 orphaned `tmp_obj` files noted for the
  host-side sweep. The commit then went through first try — the self-heal did exactly
  the job it was built for.
