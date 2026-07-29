# DB Ruling — SQLite at launch, Postgres by walked descent (29 Jul 2026, David)

## The ruling
1. **Launch runs on SQLite.** No engine migration inside the launch window.
2. **Postgres migration is a post-launch project**, executed when ANY trigger fires:
   - "database is locked" errors under real user concurrency
   - sustained write growth (intros/signups) beyond a single writer's comfort
   - the need for a second app server
3. **The DESCENT RULE (the teeth):** every normal update that touches `bea_main.py`
   also converts a SMALL DELIBERATE BATCH (3–5 expressions) of SQLite-specific SQL
   to portable form — so the surface walks to ~zero during pre-launch improvement,
   and the eventual changeover approaches "data transfer + driver swap".
4. **The surface may NEVER grow** — enforced by `test_pg_readiness.py` in
   `predeploy_check.py` (fails the gate on growth; baseline auto-tightens on shrink).

## Measured surface at ruling (bea_main.py, 16k lines)
datetime('now'): 53 · strftime: 38 · INSERT OR IGNORE/REPLACE: 13 · julianday: 2
Data migration itself: minutes (pgloader). Code descent: mechanical, batched.

## Conversion protocol (learned the hard way — the format trap)
- SQLite `datetime('now')` writes `YYYY-MM-DD HH:MM:SS` (SPACE separator). Python
  `isoformat()` writes a `T`. The DB already holds both. String comparisons on
  mixed formats mis-sort — so conversions MUST go through one shared `_now()` /
  `_cutoff(delta)` helper that emits the SAME format as the column it joins.
  Build the helper ONCE (first descent batch), audit each column's existing
  format before switching its writer.
- `INSERT OR IGNORE` → `ON CONFLICT DO NOTHING` (portable both engines).
- `julianday` (smart-sort freshness): leave until migration — needs a dialect
  helper; it is 2 expressions, not a risk.
- Each batch rides a normal fix/improvement deploy; the ratchet baseline
  tightens automatically; predeploy prints the remaining count every deploy.

## Why not migrate now (for the record)
Migration pre-launch = new bug surface at maximum stakes for a problem we do not
have. SQLite serves our launch read/write volumes comfortably; nightly /backup
captures the single file; the descent rule keeps the later move cheap and shrinking.
