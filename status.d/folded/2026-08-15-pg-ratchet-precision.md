- **PG-RATCHET-PRECISION-1 (15 Aug 2026) — the fourth "guard measuring the wrong thing" in two days,
  and the one that was silently blocking every unattended release.** `nightly_ship.bat` runs with
  `PREDEPLOY_MODE=strict`, and `predeploy_check.py` ends `if danger: if MODE=='strict': return 1`.
  `deploy_audit.log` shows verdict=DANGER on EVERY scan since at least 13 Aug. Attended deploys
  survive because they run mode=warn (always exits 0); the nightly would have aborted every time.
  So "fixes never reach live" had a mechanical cause, not a discipline one.
- **Half the DANGER was measuring Python.** `test_pg_readiness.py` counted `strftime\(` — which also
  matches PYTHON's `datetime.strftime()`, a portable stdlib call with nothing to do with SQLite or
  the Postgres move. Of 40 hits, **25 were Python**; only 15 were real SQL
  `strftime('%Y-%m-%dT%H:%M:%SZ','now')`. Adding ordinary date formatting anywhere in bea_main.py
  tripped the ratchet and blocked the release. Pattern tightened to `(?<!\.)strftime\(` and the
  strftime baseline re-cut to the TRUE surface (15). The other three patterns
  (datetime('now'), julianday, INSERT OR) are SQL-only and were already precise.
- **CLAUDE ERROR, caught and reversed in the same step:** the first re-baseline wrote ALL current
  counts, which silently absorbed a genuine `datetime_now` growth 53 -> 54. That is exactly the
  "never weaken an assertion to make it pass" rule, broken by the person quoting it all day.
  Baseline restored to 53; the ratchet now FAILS honestly on the real growth.
- **The remaining growth is REAL and belongs to the concurrent session.** Commit `5dc62a7`
  ("WIP: session commit Sat 08/15 09:46") added `" ts TEXT NOT NULL DEFAULT (datetime('now')),"`
  at bea_main.py:14025 — a CREATE TABLE column default. Portable form is a Python-supplied
  timestamp at insert, or `DEFAULT now()` at the Postgres migration. NOT edited here: it is another
  session's in-flight code and editing it is the concurrent-writer hazard that produced
  CHANGELOG-COLLISION-1 and STATUS-COLLISION-1.
- **STATE: unattended publishing is one line away.** Task `TrustSquare Nightly Ship` is registered
  (02:00 daily, Ready, first fire 16 Aug), battery blocks removed by David, and `media_push` now runs
  in it (MEDIA-NIGHTLY-1) so photos finally have an automated path to live. The single remaining
  blocker is that one `datetime('now')`.
