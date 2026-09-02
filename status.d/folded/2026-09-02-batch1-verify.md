## 2026-09-02 — Batch 1 scheduled run: VERIFY-ONLY (all build items already shipped 30 Aug–1 Sep)

Unattended 04:00Z run of the RUL-065 Batch 1 task. Every build step in the task file had
already been executed by the 30 Aug unattended session and carried by David's later
releases, so this run PROBED rather than rebuilt:
- SF-AIDESC-1 (RG-0205) + A2HS-ASK-1 (RG-0209): markers in repo ms.js AND in the SERVED
  /static/ms.js (curl, 1,157,186 bytes, both markers present). Both LOCKED, both `ok`.
- connect-src (RG-0180): served header on /terms reads
  `connect-src 'self' https://unpkg.com https://cdnjs.cloudflare.com https://tile.openstreetmap.org`.
  LOCKED, `ok`. Server `.migrations_done` ends 033 / 034 / 035; post_deploy_status.json
  03:20Z: seed ok, ladder_seed ok, migrations "none pending". RG-0125 `ok`.
- D15: `.secrets/github_push_token.txt` still absent -> fallback MAP-LIVE-1 (migration 035 +
  bea_main routes) is applied on the box; RG-0214 `ok`. D15 stays OPEN (shipping class).
- DW-084: CLOSED 1 Sep (register). Re-probed as root: junk `id-verify.confsystemctl...` gone,
  drop-ins clean (16 .conf), inline LAUNCH_SPECIAL_DEADLINE removed from the unit (0 hits;
  live env carries one value via zz-launch/launch.conf).
- DW-085: STILL OPEN — /var/run/reboot-required present, kernel 6.8.0-117, 59 packages
  upgradable, uptime 13w 6d. Needs David's same-morning window (apt upgrade + reboot +
  service restart, /health watched back up, RG-0147 + ops-key re-verify after).
- Ledger 04:05Z: 235 entries, 208 holding, 21 open, 3 REGRESSED — none in Batch 1 scope:
  RG-0114 (pg-readiness guard red 8 scans), RG-0187 (one bare subprocess harness call site),
  RG-0189 (`.secrets/deploy_keys.txt.bak-20260902-044021` — a fresh backup from the
  CONCURRENT attended session, minutes old). Left untouched: another session owns that tree
  state (uncommitted RG-0242 + tours-resubmit fragment). Nothing committed by this run.
