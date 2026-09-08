- **Maintenance loop 8 Sep (14:14–14:30 UTC, late slot):** queue empty (new 0 / fix-shipped 0 /
  verified 26 / closed 12 / duplicate 2); shadow agent 0 seen 0 acted, heartbeat on
  `/dashboard/maint` at 14:19:13Z (probed through the review gate); no escalation brief (nothing in
  24 h). Ledger: 333 entries · 311 holding · 0 REGRESSED · 22 open · 0 ready to lock · 0
  UNVERIFIED — green before, unchanged after (no fix made). Sandbox deps (httpx, fastapi) were
  missing and installed by `maint_deps.py` before the ledger ran. Committed, not pushed
  (NIGHTLY-SHIP-1).
