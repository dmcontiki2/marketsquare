## 2026-09-10 — maintenance loop: five ledger regressions cleared, backup lane given a producer

**Board:** 339 entries, 0 regressed, 22 open (was 336 · 5 regressed at the start of the run).
Fault queue empty — 0 new app faults, 0 acted; the shadow agent's heartbeat posted and was read
back live off `/dashboard/maint` at 13:52:46Z.

### RG-0015 / RG-0197 / RG-0257 — one cause, self-healed
All three reds were the same event: David's PC was off overnight, so the 20-minute host agent did
not tick for 558 minutes, so the host-side `git_unlock.bat` never ran and a `HEAD.lock` sat
stranded for 544 minutes. The agent resumed at 15:51 SAST and cleared it. Probed after the fact:
no lock file in either repo, `git_unlock.py` reports nothing to sweep, heartbeat current. No code
change — the machinery did what it was built to do once the machine was awake.

### RG-0114 + RG-0112 — pg-readiness (PG-PORTABLE-2)
The ratchet read 62 against a baseline of 49 and had put DANGER on 8 consecutive pre-deploy scans.
Real growth, not a false positive. Every no-modifier `datetime('now')` in `bea_main.py` — 45 of
them, across DDL column defaults, `UPDATE ... SET`, and `INSERT ... VALUES` — is now the portable
`CURRENT_TIMESTAMP`. Baseline auto-**tightened** 49 → 17; it was never re-baselined upward. The 17
modifier forms (`datetime('now', ?)`) need the PG-PORTABLE-1 caller-supplied-stamp treatment and
are recorded as out of scope in RG-0351.

Evidence: `test_pg_readiness.py` PASS · `py_compile` clean · behavioural proof in `:memory:` that
`CURRENT_TIMESTAMP` and `datetime('now')` return the identical string as a DDL default, in an
INSERT and in an UPDATE, and that all 14 rewritten `CREATE TABLE` statements execute clean.

### RG-0234 — the backup lane had a guard and no producer (BACKUP-UNATTENDED-1)
The newest archive was 9 days old; it had sat 27 days stale before 1 Sep. `backup_marketsquare.bat`
is native-Windows, on no schedule and on no allowlist, so the lane ran only when a human remembered.
A freshness assertion with no producer behind it can only ever report the same failure again.

New `scripts/backup_db_sandbox.py` produces the archive with no host click: `sqlite3 .backup` on the
box (consistent, read-only), scp, md5 matched both ends, zipped to the exact shape RG-0234 restores,
the archive re-extracted and integrity-checked, proof appended to `backups/RESTORE_PROOF.md`. Wired
into step 2a of every maintenance run via the BACKUP-UNATTENDED-1 section of `MAINTENANCE_AGENT.md`.
It **deletes nothing** — retention stays with the host bat, because deletions are David's (RUL-095).

Occurrence closed the same run: `backups/2026-09-10_1356.zip`, restores clean, users=71 listings=113.

### The rest of the DANGER line (TRUTH-REVIEW-4)
With pg-readiness cleared, `maintenance-agent` and `tester-intake` were still on the same scan line
and would have gone chronic in turn.

- **tester-intake** was a real gap: seven `visuals/assoc/assoc_*.html` pages a tester can land on
  carried no fault-report widget. All seven now load `/static/ts_report.js` (first-party, so
  RG-0025's no-third-party-script rule is untouched).
- **maintenance-agent** was a wrong red. The ack guard pinned the literal `reference {fault_code}`;
  the code has read `reference {ref_override or fault_code}` since REF-HONESTY-1, because a support
  form supplies its own ref. The behaviour was never lost. The guard was fixed, not the code: it now
  asserts the property on both bodies the branch can send, and its window reaches the whole branch
  (it began at +3817 and ran past the old +4500 cut). Fourth instance of this file's own documented
  class, second time the window rather than the needle was the fault.

`predeploy_check.py` now logs `danger=- verdict=ok` — the first clean scan since 2 Sep.

### New ledger entries
- **RG-0350** — the archive lane has an unattended producer, proves its own restore, deletes nothing.
- **RG-0351** — the plain SQLite clock is gone from `bea_main.py`; baseline may only fall.
- **RG-0352** — every assoc page offers the fault widget; the ack guard reads the property; the
  pre-deploy scan reaches clean.

Escalation brief: none written — no escalations in 24h. `rulings_check.py`: 106 rulings, 0 FAIL.
Not deployed — NIGHTLY-SHIP-1 ships committed work through the gates.
