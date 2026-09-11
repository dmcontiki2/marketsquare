### Maintenance loop — 11 Sep 2026 (unattended)

Ledger started at **2 regressed**, ends **green**. Both reds were the same class, named the
day before: a freshness guard with nothing that produces the evidence it checks.

- **Wave-hygiene witness had no producer.** Both proof suites still passed; the witness file
  had been hand-written on 28 Aug and never rewritten. `scripts/wave_hygiene_witness.py` now
  re-runs both suites every loop and writes their real verdicts — a failing suite writes
  `not_ok`, so the board goes red on the fact, never on the clock. Sabotage-proven. RG-0353.
- **The ops dashboard was reading a section 22 days old.** The endpoint matches the first
  `## Last Completed` heading; sessions fold under `## Current Session`. Seven fragments were
  also unfolded, because the compiler only ran from a deploy and none had run since 8 Sep.
  The fold now maintains the heading the reader actually matches. RG-0354.
- Fault queue empty (0 new, 0 acted). Heartbeat posted and read back live at 06:32:40Z.
- Backup `2026-09-11_0633.zip` produced and restore-proven: users=71, listings=113.
- No escalations in 24h. Rulings: 106 checked, 0 FAIL.

Not fixed, deliberately: **RG-0346 stays open** — the three agency letters the sending lane
draws still carry the solo-seller story, and the lane never mints the agency console link.
That is a copy-and-flow change to live outreach, not a mechanical fix.
