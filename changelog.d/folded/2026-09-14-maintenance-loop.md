## 2026-09-14 — maintenance-loop: the dashboard's Last-done panel was blank by construction

**RG-0127 RED, and the fault was in the fix that was meant to end it.** The 11 Sep DASH-FEED-1
work (RG-0354) gave the dashboard-feed section a producer: every status fold now rewrites one
managed block above the first `## Last Completed` heading, so whatever a session folds is what
`GET /dashboard/summary` reads. Placement correct, date correct, panel still blank.

Cause: status fragments are written as `## <date> — <title>`, and the endpoint captures its
section with `## Last Completed[^\n]*\n(.*?)(?=\n## |\Z)` — the capture stops at the next
level-2 heading. The block's **first body line** was a level-2 heading, so it terminated the
section it existed to fill. Every fold since 11 Sep produced a correctly-placed, correctly-dated,
empty section. Reproduced against the repo file with the endpoint's own regex before touching
anything; confirmed live through the admin door (`lastDone` empty while `liveState` and
`nextGoals` answered).

- **FEED-BODY-DEMOTE-1** — `scripts/status_compile.py` gains `_demote_headings()`, applied to the
  body on the way into the managed block. Every heading is pushed one level down, so no fragment
  written in any future shape can truncate the block. Class fix, not a re-word of one fragment.
- **RG-0365 (new, LOCKED)** — asserts the artefact, not the intention: parsing STATUS.md with
  bea_main's own regex must yield a NON-EMPTY body, and the compiler must still demote. This is
  the leg any session can run before anything ships — RG-0127's live leg needs the admin key and
  a deploy, which is why three green boards sat on top of a blank panel.
- **RG-0363 and RG-0364 promoted OPEN → LOCKED** — the offline banner's anti-latch properties and
  service-worker registration at app start both passed; the board printed READY TO LOCK.

Third instance in four days of one class: a producer and a consumer that address the same file by
different rules agree on placement, disagree on content, and every freshness check between them
reads green.

**Maintenance agent:** shadow run clean — 0 faults in the queue, 0 acted, heartbeat posted to
`/dashboard/maint`. Email lane census only: 24 total, 6 held over 30 days. Sandbox SSH to the
origin restored via `load_sandbox_ssh.sh`, which un-blinds RG-0362's secret-divergence probe.
