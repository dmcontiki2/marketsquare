## 2026-09-14 — Maintenance loop: the Last-done panel was blank by construction

The ops dashboard's Last-done panel has been empty since 11 September, and every instrument
around it read green — the heading was fresh, the compiler had run, the fragment was folded.
The block's own first line was a level-2 heading, and the endpoint that reads the section stops
at the next level-2 heading. So the fold wrote the content into a section that ended before it
began.

- Fixed at the producer: `scripts/status_compile.py` now pushes every heading in the block one
  level down, so no fragment shape can truncate the section again.
- New ledger entry RG-0365 judges the file the consumer actually reads, not the compiler's
  intention — it fails the moment the section parses empty, without needing a deploy or a key.
- RG-0363 (offline banner cannot latch) and RG-0364 (service worker registered at app start)
  promoted to LOCKED — both were passing.
- Maintenance agent shadow run: fault queue empty, nothing to fix, heartbeat posted.
