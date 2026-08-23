## 2026-08-22 — Note: commit 76606ff carries a second session's work

Housekeeping, so later archaeology is not misled. The SESSION-COUNTER-1 commit
`76606ff` also swept in **uncommitted working-tree changes from a concurrent
session** — INTRO-HOLD-1 / RG-0145 (the 1T hold on introduction request, the
`_release_intro_hold` helper, and its ledger edits) in `bea_main.py` and
`scripts/regression_ledger.py`. That work is **not** SESSION-COUNTER-1's and the
commit message does not describe it.

Nothing was lost or altered — the changes were on disk before the commit and are
byte-identical in it; committing them protected them rather than risking them.
History was deliberately **not** rewritten: on this FUSE mount a rebase is far
more dangerous than a mislabelled commit.

**Lesson, cheap to apply:** naming explicit paths on `git add` is not sufficient
isolation when a file is one *both* sessions are editing. Before adding a shared
hot file (`bea_main.py`, `main.py`, `scripts/regression_ledger.py`), diff it and
check whether the hunks are actually yours. `main.py` in the same commit was
clean; `bea_main.py` was not.
