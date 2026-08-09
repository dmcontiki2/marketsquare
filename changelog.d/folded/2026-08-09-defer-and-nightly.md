## 2026-08-09 — DEFER-1 + NIGHTLY-SHIP-1: the "run one more command" class, engineered out

David, after the third "now run this over SSH" in two days: "we also need to fix the human need
to run one more time. This is not progress, it is just another delaying glitch."
He is right, and the fix is structural, not another checklist.

**Why a human kept being needed.** Two mechanical reasons, no policy involved:
(1) DW-030 — the migration chain sat halted behind 005, so every migration since 5 Aug needed a
hand-run over SSH; (2) the git push key lives on David's machine BY DESIGN (Codex B3 — credentials
never leave it), so only his machine can publish the deploy ref, and "his machine" had degraded to
meaning "his fingers".

**DEFER-1 — deferral is now a recorded state, not a silent jam.** `post_deploy.sh` reads
`migrations/DEFERRED.txt` (in-repo, version-controlled): a listed migration is skipped LOUDLY on
every deploy — banner in the log, never marked done, chain continues past it. 005 and 007 are
listed with reasons (both are the one gate-posture decision David has not yet made). Everything
else now self-runs on deploy. Rehearsed: the exact sed/grep skip logic against the real filenames
(005/007 deferred, 006/008/010 run), bash -n clean. 006 and 008 dry-run rehearsed against the
local DB snapshot — both plan sanely and both exit green-not-blocking when there is nothing to do.

**NIGHTLY-SHIP-1 — the ship itself goes unattended, with ZERO new registration.** David chose
computer-control registration; the harness rightly refused typing into a click-tier terminal and
no workaround was attempted. Better door found: the "TrustSquare Nightly TSL" task David himself
registered 24 Jul already fires daily at 05:45 (log-proven) and runs `nightly_tsl.bat` — a repo
file. That script is UPGRADED in place: old contract (prepare + flag, deploy nothing) is
superseded on David's explicit 9 Aug instruction — drift-ahead + STRICT-green gates now SHIPS
through the ONE deploy engine; any finding BLOCKS and flags instead. Key never leaves his
machine (B3). Caveat stated plainly: the laptop must be awake at 05:45 — a missed night ships
the next one. `nightly_ship.bat`/`register_nightly_ship.bat` remain as an optional 02:00 slot. Net effect: Claude stages work + commits,
the machine ships it at 02:00, migrations apply themselves, and the morning check verifies —
zero commands from David on the routine path. SSH remains for genuine emergencies only.

**STAYS-GALLERY-1 rides this.** Migration 010 (the 5-photo galleries — the original one-photo
wiring was my bug; 12 of 15 generated photos sat unused) now applies itself on the next deploy.
Verification standard tightened after David caught "done" meaning "the API answered": done now
means SEEN RENDERED — the page, the way a user meets it.
