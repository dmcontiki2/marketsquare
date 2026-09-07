## 2026-09-07 — maintenance-loop: a false READY TO LOCK caught and fixed at the instrument (OFFLINE-IS-NOT-ABSENT-1, RG-0333)

Daily B2b maintenance run, 05:31–05:55 UTC, unattended.

**Queue.** `GET /admin/faults`: new 0 · fix-shipped 0 · verified 26 · closed 12. Shadow agent
(`maintenance_agent.py`, foreground, SHADOW mode, kill switch OFF): 0 seen, 0 acted, no patches.
Heartbeat posted — `GET /dashboard/maint` shows run `2026-09-07T05:36:50Z`, received 05:37:10Z.
Escalation brief: nothing in 24 h, no brief written.

**Ledger BEFORE.** 318 entries, exit 0, no regressions — and RG-0308 (rotation discovery) printed
READY TO LOCK. The loop promoted it to LOCKED, per the DW-079 rule, then re-ran the single entry
as a check: **13 surprises** — the same 13 as 6 Sep. The READY TO LOCK was false.

**Why.** Shard 3/3 ran RG-0308 before any entry had loaded the sandbox's ssh key (`~/.ssh`
appeared 07:35:03 local; the shard ended 07:35:31). `secret_consumers.py` asked the box 22
questions with no key; each ssh call failed (rc 255) with empty output, and the tool read empty
output as "this name lives nowhere on the box" — zero copies, zero surprises, exit 0, READY TO
LOCK. A blind instrument reported a clean box. Proven before the fix: `server_consumers()`
against `root@localhost` returned `[]`; after the fix, `None`.

**Fixed (both halves, same session).**
- `scripts/secret_consumers.py`: the remote script now echoes a sentinel as its last line; if the
  sentinel is missing or rc is 255 the box is OFFLINE (`None`), never "not present". The tool
  self-heals ssh at entry (`_ensure_ssh()`, SSH-BOOTSTRAP-1 pattern) so a fresh sandbox loads the
  key before asking. Reachable box still reports the same 13 surprises (LAUNCH_CODE_SECRET 5 places,
  etc.).
- `scripts/regression_ledger.py`: RG-0308 REVERTED to OPEN (promotion was live for eleven
  minutes, never committed); its READY TO LOCK branch now requires the tool's own `OK:` verdict
  line, never a bare exit 0. NEW **RG-0333** (LOCKED): sentinel present, `None` on missing
  sentinel, self-heal at entry, RG-0308 demands the OK line, and a BEHAVIOURAL probe —
  `server_consumers()` against an unreachable host must answer `None`. Filed beside RG-0308 rather
  than at the tail because a concurrent session was appending at the tail the same minute.

**Ledger AFTER.** 321 entries · 291 holding · **1 REGRESSED** · 29 open. RG-0333 HOLDING,
RG-0308 OPEN (13 surprises, expected). The one red is **RG-0271** ("an already-correct link was
rewritten"), tripped by the concurrent EMAIL-FORENSIC-1 session's *uncommitted* change in
`CityLauncher/emailer/emailer.py` (INVITE-PLACE-1 appends `&country=` to legacy links, which
RG-0271's no-op fixture does not carry). Not caused by this run and not this run's to reconcile —
the session that owns both the change and the fixture resolves it. RG-0308 stays OPEN until
SECRETS_REGISTER.md's out-of-band table lists the 13.

**Commit.** Only this run's files: `scripts/secret_consumers.py`, the RG-0308/RG-0333 hunk of
`scripts/regression_ledger.py` (staged by hunk — the other session's RG-0325..RG-0332 tail stays
theirs to commit), the shadow report, these fragments. No push, no deploy (NIGHTLY-SHIP-1).
