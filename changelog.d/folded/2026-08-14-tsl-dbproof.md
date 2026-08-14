## 2026-08-14 — TSL-DBPROOF-1: the pre-deploy gate can prove the database from any session

**The defect (class, not instance).** `/TSL`'s pre-deploy gate had exactly one transport for
proving the live database healthy: `ssh msdeploy@`. That private key lives on David's machine
by design, and must never enter a cloud session. So every gate run anywhere but his desktop —
cloud sandbox, and any future runner — printed *"could not prove the databases healthy this
run"* and returned **REVIEW**. Not because anything was wrong: because nothing *could* be
proven. A gate that can never go green is a gate people learn to wave through, which is the
opposite of what it is for.

**The fix.**

- `bea_main.py` — new `_tsl_dbproof()` publishes a **facts-only** `db` block on `/health`, the
  one endpoint nginx leaves open anonymously after GATE-ENFORCE-1: `primary_present`,
  `primary_bytes`, `integrity`, `redis`. No paths, no schema, no counts, no customer data.
  `integrity_check` is a full-file scan so it is cached (`TSL_DBPROOF_TTL_SEC`, default 900s);
  presence and size are a live `stat`, which is what actually catches the zero-byte case.
  Every probe is individually guarded and the whole block **can never raise** — a throwing
  `/health` would make the deploy engine auto-roll-back a perfectly good ship.
- `tsl_gate.py` — `check_db()` now reads HTTPS `/health` first (`check_db_http`, overridable
  via `MS_HEALTH_URL`) and keeps the original SSH probe as a second opinion
  (`check_db_ssh`). **REVIEW is now reserved for both transports failing** — a real
  cannot-prove — rather than being the permanent resting state of every non-desktop run.
- The key still never leaves David's machine. The proof simply stopped depending on it.

**Ledger.** `RG-0069` added, state **OPEN** — it asserts the repo half (gate prefers the
credential-free transport, `/health` publishes the block) *and* the live half (the block is
readable anonymously and reports a present, non-zero, integral primary DB). It flips to
READY TO LOCK the moment the server carrying this change is live.

**Observed, not chased:** one ledger run during this session reported 13 regressions; the two
runs immediately after, and every run since, report 0 REGRESSED / 63 holding. Logged here so
it is not lost — if it recurs it wants a ledger entry of its own.
