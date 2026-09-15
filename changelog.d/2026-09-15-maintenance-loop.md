## 2026-09-15 — maintenance-loop: RG-0114 cleared, and the scan that could not see the tree

**Fault queue: empty.** The shadow maintenance agent ran clean (0 faults seen, 0 acted); the
email lane census reported 24 rows, 6 held over 30 days. The heartbeat posted to
`/dashboard/maint` at 05:41:25Z. No patch came out of the queue, so the session's work was the
regression the ledger found instead.

**RG-0114 was RED: `pg-readiness` had sat DANGER on NINE consecutive pre-deploy scans.**
The ratchet read `datetime_now=25` against a baseline of 17. The growth was real, not a false
positive — `git blame` put all eight new occurrences in the 14 Sep COMMS-VIEW-1 and Buzz
commits (six windows in `dashboard_comms`, the Buzz retention prune, and the `/buzz` hourly
rate-limit count).

Fixed the way PG-PORTABLE-1 (19 Aug) and PG-PORTABLE-2 were, and **never** by re-baselining
upward — the baseline file is byte-unchanged at 17. New named helper `_sql_since(days, hours)`
in `bea_main.py` returns a UTC cutoff in the shape SQLite stores; all eight sites now bind it
as a parameter and move to Postgres untouched. Naming the helper once is what stops a fourth
instance: the common factor in all three was that no helper existed, so every window was
written by hand.

**`tester-intake` was on the same DANGER line at 5 scans, three from chronic.**
RG-0114's own record warns that tags sharing that line "would have gone chronic in turn", so it
was fixed now rather than waited for. `quick.html`, `genie/q_index.html` and `confirm.html` were
all in the deploy manifest with **no `ts_report.js`** — a tester landing on the new Quick door,
the one just put on the front page, had no way to report anything. Added the same one-line
script tag every other tester page already carries.

**Then a third fault, found because of the second:** after the fixes the pre-deploy scan printed
`Working tree: 0 file(s) uncommitted` against a tree with five modified files, one of them
`bea_main.py` — a deploy target. `predeploy_check.py::_git()` ran git **without**
`GIT_OPTIONAL_LOCKS=0` (required on this FUSE mount since GIT-LOCK-3, 16 Aug), so read-only
`status` sat past its 20s timeout every time — and the `except` returned `''`, which is
indistinguishable from a clean tree. Consequence was not cosmetic: `modified = rel in dirty` was
False for every target, so the **torn-file detection — the only thing that makes the STRICT
nightly abort — could never fire.** `_git()` now returns `(ok, stdout)`, blindness is printed and
stamped `dirty=?` in the audit log, and it is deliberately NOT added to `danger` so a slow git can
never abort a good nightly.

### Evidence (AIK-VERIFY-1)
- `test_pg_readiness.py` → **PASS**, `datetime_now=17`, baseline untouched.
- `python3 -m py_compile` clean on `bea_main.py`, `predeploy_check.py`, `scripts/regression_ledger.py`.
- Behavioural proof in `:memory:` — `CURRENT_TIMESTAMP` and `_sql_since()` agree to the second, and
  all eight rewritten queries return rows identical to the literal form, the prune keeping the
  identical id set.
- `test_tester_intake.py` 17 PASS + 1 FAIL → **18 PASS**.
- Two consecutive scans on one unchanged tree: `dirty=0` → `dirty=7 changed=1 recent=bea_main.py`.
- Pre-deploy scan after the fixes: `danger=- verdict=ok` — the streak RG-0114 counts is broken.

### Ledger
New: **RG-0376** (the modifier form cannot creep back; one named helper, eight bound cutoffs,
baseline guarded against being raised), **RG-0377** (every deployed tester page can report a
fault), **RG-0378** (the pre-deploy scan can see the working tree). All three **sabotage-proven** —
nine mutations, nine bites. Two of them had to be corrected in the same session they were written:
RG-0376's first draft searched token-joined text for a three-token pattern no join can contain, and
RG-0378's own *success* line quoted the phrase the runner greps for to detect blindness, which
demoted the entry to UNVERIFIED and took the board off green. A leg that cannot pass is not strict,
and an instrument that quotes the runner's words reports on itself.

Also healed a stranded 0-byte `.git/HEAD.lock` (61 min old) that had turned RG-0015 and RG-0197 red.
