# Maintenance loop 2026-09-23 — hand-off (WORK-LOCK-1 stand-off)

Written to Records/ because lane `lang-quick-2026-09-23` holds the work lock (taken 17:16Z) on
`scripts/regression_ledger.py`, `changelog.d/*` and `status.d/*`. This run's ledger edits were
made BEFORE the lock was taken (17:07–17:09Z) and sit in the working tree; this run did not
`git add` the ledger (that would stage the owner's 600+ in-flight lines). The two fragments below
are verbatim and ready to drop into `changelog.d/` and `status.d/` once the lock is released —
the next maintenance run should do that (and `python3 scripts/changelog_compile.py` /
`status_compile.py` fold them).

## Ledger entries left in the working tree (uncommitted, in the locked file)
- RG-0427 NEW, LOCKED — SANDBOX-EGRESS-1 (sandbox lane self-heals the SSH allowlist).
- RG-0245 AMENDED — "exactly one live IP" → "exactly the live vantages"; rule count ≤ 2; a
  stale /32 still red; UNVERIFIED (not red) while the other vantage has never beaconed.
- RG-0099 — fix line now names the vantage-aware cure.
- RG-0350 STRENGTHENED — asserts `maintenance_agent.py` CALLS the backup producer (BACKUP-IN-AGENT-1).
All seven touched entries re-evaluated in isolation after the edits: all green.

## Board verdict this run (combine of 6 shards, 424 entries, 19:31 SAST)
390 holding · 2 REGRESSED · 29 open · 3 ready to lock · 0 UNVERIFIED.
The 2 reds are NOT this run's: RG-0154 (session counter 204 vs 205 — recomputed this run,
`--check` now OK, SESSION_COUNTER.json committed) and RG-0157 (untracked
migrations/048_i18n_zu_xh_nso_hand_drafts.py — the lock owner's in-flight work; theirs to commit).
Ready to lock: RG-0429, RG-0430, RG-0437 — all the lock owner's entries.

---
### changelog.d/2026-09-23-maintenance-loop.md

## 2026-09-23 — maintenance-loop: SANDBOX-EGRESS-1 + BACKUP-IN-AGENT-1

Queue: 0 new · 0 fix-shipped · 26 verified. Shadow agent ran clean (report run_20260923T165510Z,
heartbeat posted to /dashboard/maint). Escalation brief: none in 24 h.

Ledger BEFORE (4 shards, partial — shard 2/4 could not finish inside the 178 s cap while port 22
was shut): 2 LOCKED reds, RG-0099 and RG-0234. Both fixed at the class:

- **SANDBOX-EGRESS-1** — RG-0099 red from three sessions today: port 22 timed out from the sandbox
  (egress 197.184.121.169) while the host's 20-min self-heal log said "ok: SSH rule holds exactly
  165.165.181.198/32" six ticks running. David's PC and the sandbox had DIFFERENT public IPs for
  about half an hour (~16:35–17:05 SAST) and NO-STALE-IP-1's one-IP pruner locked the sandbox out
  by design. Fix: `scripts/hetzner_fw_selfheal.py` is vantage-aware — every run beacons its own
  IP into `.secrets/egress_peers.json` (24 h TTL); the HOST lane SETS the rule to host IP + fresh
  sandbox beacons (still the pruner); the SANDBOX lane is ADD-ONLY (cannot lock the host out).
  `load_sandbox_ssh.sh` runs it on every SSH load, never fatal. PROBED: sandbox run added its IP,
  ssh answered 3/3; the 17:07Z host tick then read the beacon, both vantages back on the same IP,
  rule converged to one /32. Shard 2/4 dropped from >178 s to 85 s once port 22 answered.
  RG-0427 new (LOCKED, proven both ways), RG-0245 amended (not weakened), RG-0099 fix line updated.
- **BACKUP-IN-AGENT-1** — RG-0234 red at 11 days (newest 2026-09-12_1553.zip). The 10 Sep producer
  was wired as a SENTENCE ("step 2a") in MAINTENANCE_AGENT.md; the scheduled loop's step list never
  carried it, so it ran 10–12 Sep and stopped. Now `scripts/maintenance_agent.py` calls
  `backup_db_sandbox.py` at the end of every run (`_backup_lane`: skipped <20 h, 150 s cap, never
  raises, outcome in the run report under `backup`). Occurrence closed: 2026-09-23_1705.zip,
  restores clean, users=113 listings=119. Proven: guarded call ran a stub to ok / recorded a failing
  stub as FAILED without raising / skipped on the real tree. RG-0350 strengthened to assert the call.
- RG-0154: SESSION_COUNTER.json recomputed (204 → 205), `--check` OK.

Backups beside every edited file (`*.bak-20260923-18xxxx`). py_compile clean on all three .py;
`bash -n` clean on the loader. Ledger AFTER: 390 holding, 2 reds (both the lang-quick lane's
in-flight state, see Records hand-off), 0 unverified.

---
### status.d/2026-09-23-maintenance-loop.md

## 2026-09-23 — maintenance-loop
- Queue 0 new / 0 fix-shipped / 26 verified; shadow agent + heartbeat OK; no escalations.
- Two LOCKED reds fixed at the class: SSH lockout when sandbox and PC egress differ
  (SANDBOX-EGRESS-1, RG-0427) and the backup lane silently stopping (BACKUP-IN-AGENT-1, RG-0350).
  Fresh backup 2026-09-23_1705.zip restores clean. Port 22 answers from the sandbox again.
- Ledger edits + these fragments are held back by the lang-quick work lock (RUL-140); hand-off in
  Records/MAINT_LOOP_2026-09-23_HANDOFF.md. Next maintenance run: drop the fragments in and
  confirm the lock owner's commit carried RG-0427 / RG-0245 / RG-0350 / RG-0099 edits.
