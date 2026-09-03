## 2026-09-02 — PATCH-CADENCE-1: origin patched + rebooted (DW-085 closed), RG-0246 LOCKED

David: "lets do it now" on the morning watch's one decision. Window 18:47 SAST, David present:
DB `.backup` + integrity ok, 37 packages upgraded, kernel 6.8.0-117 -> 6.8.0-138, **34 s** down
(521 at t+26s, /health 200 at t+34s). All six credential fingerprints identical pre/post in
`/proc/<MainPID>/environ` — the DW-084 restart landmine proven defused. BIT 8/8, /payment/test ok,
smoke ALL PASS, subscription monitor 35 UP / 0 issues. Uptime before: 97 days.

Locked: **RG-0246** — newest REBOOT row in `ops/maintenance/PATCH_LOG.md` (new) must be < 45 d old
with `reboot_required=absent`; the daily watch remains the live half. Ledger after: 239 entries ·
217 holding · 0 REGRESSED · exit 0. DAILY_WATCH register + coverage map updated (58 green, 0 red).
