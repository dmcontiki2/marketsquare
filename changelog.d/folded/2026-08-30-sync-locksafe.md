## 2026-08-30 — WAVE 2 SENT (15) · SYNC-LOCKSAFE-1: the sync waits, bails and stops lying (RG-0219 LOCKED)

**Wave 2 fired host-side on David's word**: 15 sends probed in the local store — Pretoria
adventures_accommodation×12, Johannesburg adventures_experiences×3 (JHB's clean Stays & Tours
pool is that thin; under-filling beats junk, RG-0217). First fully-tracked wave (pixels live).

**The post-send sync failed loudly and then lied**: dozens of `database is locked (5)` against
the running citylauncher.service, then "SYNC COMPLETE" — sqlite3 without `.bail` exits 0 over
errors, and the apply ran with no busy timeout, one lock fight per statement. Fixed at the
class in sync_local_to_server.py (both apply paths, prospects + gumtree): generated SQL now
opens `.bail on` + `.timeout 30000` + `BEGIN IMMEDIATE` and closes `COMMIT` (wait for the
lock once, apply atomically, roll back whole on failure); the caller retries up to 3× on
"locked" and treats rc==0 with dirty stderr as FAILURE. The SQL's idempotency (OR IGNORE,
guarded UPDATEs, NOT EXISTS events) is what makes the retry safe — asserted in RG-0219.
Backup: sync_local_to_server.py.bak-locksafe-*. Re-run of sync_to_server.bat completes the
partial apply; sends are NOT re-fired by a sync re-run.

**Observed, noted for the ramp seam (not fixed today):** wave_runner stamped today's events
wave_number=1 (110 total incl. yesterday's) — last_wave read 0 because yesterday's sends
bypassed the runner. Bookkeeping only: batch size is governed by the explicit 12 override
(waves_policy), and true bounce data still lives server-side (RG-0176(a)/RG-0204 pull-down
seam, still open). Straighten wave numbering when the bounce pull-down lands.
