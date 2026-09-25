## 2026-09-25 — maintenance-loop: HARNESS resync (RG-0450) + CENSUS-DOOR-1 (RG-0223)

Daily maintenance loop (scheduled, 05:35–06:10Z). Fault queue: 0 new, 0 fix-shipped, 26 verified,
12 closed; shadow agent saw 0 app faults and acted on 0. No escalations in 24h (no brief written).

- **RG-0450 regression fixed** — `genie/HARNESS.html` had drifted from `quick.html` (house rule:
  identical). Three 24 Sep commits (BUGSWEEP-24SEP e0a4d22, QUICK-WHERE-1 303fbc0, E2E-HMI-1 b951503)
  edited `quick.html` only. `quick.html` is the deployed file (manifest: `quick.html | q/index.html`)
  and carries the fixes, so it was copied over the prototype (`cp`, byte-identical by `cmp`;
  backup `genie/HARNESS.html.bak-20260925-054135`). `build_comic.py`, which reads HARNESS, now sees
  the fixed flow. Evidence: RG-0450 check run directly → no FAIL.
  (The resynced file was swept into the concurrent session's commit c444c99 from the shared tree.)
- **CENSUS-DOOR-1 — RG-0223 regression fixed.** SEC-GATE-1 (24 Sep) made
  `GET /dashboard/email-triage` admin-only, so the brain's customer-email census got 401 and the run
  reported "0 seen" on app faults only — exactly what RG-0223 forbids. Same class as GATE-SYNC-1
  (RG-0457) and the same decision: the reader moves to the staff door. `email_lane_census()` now
  tries anonymous first (loopback on the box is still admitted) and on 401/403 retries once with
  X-Admin-Key when this machine holds one. Counts only by construction: `items` is dropped whatever
  the door; the report gains `door`. Evidence: census probed live → 24 total, 5 held, door=staff;
  re-run agent heartbeat carries it; RG-0223 run directly → "heartbeat carries the customer lane:
  24 total, 5 held". Backup `scripts/maintenance_agent.py.bak-20260925-055852`.
- **RG-0351 and RG-0373** were red at the start of this run and were fixed by the concurrent
  David-directed session `cto-fix-2026-09-25` (PG-PORTABLE-4 in `bea_main.py`; COACH-EARNABLE-2 in
  the ledger). This loop did not touch those files (that session held the work lock).
