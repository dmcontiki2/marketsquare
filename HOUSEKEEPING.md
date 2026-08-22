# HOUSEKEEPING — the monthly sweep, dated log

Newest first. One entry per `/housekeep` run. Fixed / needs-David / measured.

## 2026-08-21 — pre-launch sweep (8 days to SOFT-to-PUBLIC, 11 to FULL LAUNCH per RUL-001)

**Ran concurrently with another live session** (commits at 05:58, 06:05, 06:14 SAST while this
sweep was reading). Nothing here was committed for that reason — CHANGELOG-COLLISION-1 discipline.
Changes sit in the working tree and in `changelog.d/`, for the next committer to fold in.

### Fixed
- **deep_scan back to zero-new.** `scripts/prove_ai_failover.py:20` imported `json` and never used
  it (ruff F401, the one NEW finding of the run). Removed; `py_compile` green; scan 183 -> 182,
  **0 new, 0 crash-class**. Backup beside it: `.bak-20260821-f401`.
- **Stale git locks healed (GIT-LOCK class, RG-0015).** A stranded `.git/HEAD.lock` was live when
  this sweep started — left by the concurrent session. `git_unlock.py` renamed it aside; a
  `packed-refs.lock` and a branch ref-lock created during a branch-delete attempt were swept into
  `.git/stale_locks/` the same way. Repo verified sane afterwards. No lock stranded >60 min.
- **Quarantined, reversibly** (`_CLEANUP_REVIEW_2026-08-21/` + RESTORE_MANIFEST.txt): three stale
  LibreOffice `.~lock.*#` files (16 Jul, 14 Aug) and two orphaned `.fuse_hidden*` files in
  `backups/`. Auto-safe classes per CLEANUP_POLICY.md. **The sandbox cannot unlink on this mount**
  — the purge step is David's, host-side.

### Measured — green
- **Site:** `GET /health` 200 in **0.36 s**, BEA v1.3.1, DB integrity ok, 2.88 MB primary.
- **SSL:** valid to **24 Sep 2026 — 34 days remaining** (Google Trust Services WE1). Green.
  Note it expires 23 days AFTER full launch; confirm auto-renewal rather than assuming it.
- **Regression ledger:** exit 0 — **120 entries, 118 holding, 0 REGRESSED, 2 open, 0 unverified.**
- **Rulings check:** **36 rulings, 0 FAIL, 0 WARN** — every ruling reflected in canon.
- **Deploy manifest:** 127 entries, **every file present on disk**. No drift.
- **Secret hygiene in the repo:** `.env` and `.secrets/` both git-ignored; no credential-bearing
  file tracked; entropy scan of tracked files found only the `sk_live_xxxx` placeholder in
  `.env.example`. The repo is clean — the exposure in DW-029/DW-057 is transcript-side, not here.
- **Shipped code:** no `DEBUG=True` / `reload=True` / development-mode flags in tracked source;
  no `console.log` in app JS (the 5 hits are repro scripts and Cloudflare workers).

### Needs David
1. **DW-057 / DW-029 — rotate the production secrets. Still the red one, day 15.** The same
   credential set is now burnt twice and the pre-launch origin gate is down (RG-0115), so the site
   is publicly readable while the old values are live. `ROTATE_SECRETS.bat`; MS_API_KEY,
   MS_DEPLOY_TOKEN and FOUNDERS_ID_SALT also need the systemd unit edited.
2. **Three commits are unpushed — to BOTH `main` (the GitHub mirror) and `deploy`.** EULA v1.14
   (Country Schedules D-G) and RUL-036/SO-3 exist only on this laptop. The mirror push is pure
   backup and overdue; the `deploy` push is a live release and stays David's under SO-3.
3. **Local backup has lapsed.** Newest laptop archive is `2026-08-05_1247.zip` — **16 days old**;
   BACKUP_LOCATIONS.md's own honest gap still reads "current baseline is a one-time snapshot
   (2026-07-05), not an ongoing sync". Eight days from public launch, with a live DB that has
   grown to 104 listings / 59 sellers / 115 introductions. `/backup` exists and would close it.
4. **1,205 `*.bak` files, 512 MB, across the project.** CLEANUP_POLICY.md marks `*.bak` as
   never-auto-touch, so nothing was moved. A dated retention rule (keep the newest N per file)
   would reclaim most of it — David's call to set the N.
5. **Stale branch `claude/flamboyant-shtern`** — last commit 15 Apr 2026, fully merged into main,
   0 unique commits. Deletion attempted and abandoned: it needs a host-side `git branch -d`
   because the sandbox cannot unlink the ref lock.
6. **`.git` is 1.5 GB for 1,525 tracked files** — video blobs (`.femdub`/`.predub` mp4s, a 8.2 MB
   wav) are in history. Not touchable safely before launch; noted for a post-launch decision.

### Not fixed, and why
- **Server disk / log growth on the Hetzner box:** not measured. Reading it needs SSH, and the one
  standing lesson from DW-057 is not to run commands that print server environment into a
  transcript. Deferred to an attended session with the rotation.
- **Dependency freshness:** no `requirements.txt` at project root (only `assets/`), so the FastAPI
  stack's pinned set was not enumerable from here. Needs the server-side venv to answer honestly.

## Unit-file sanity (added 22 Aug 2026)

    ssh root@178.104.73.239 "systemd-analyze verify marketsquare.service 2>&1 | grep -i 'invalid environment'"

Must return NOTHING. A non-empty result means systemd is silently discarding a setting —
found exactly that on 22 Aug: `demand.conf` set `DEMAND_FROM_EMAIL` to the single word
"TrustSquare" because the value contained a space and was not quoted, and the address was
dropped. Nothing broke only because `_safe_from()` substituted an identical fallback, which
is precisely why it went unnoticed. Quote any `Environment=` whose value contains a space:

    Environment="VAR=value with spaces"
