- **Maintenance loop 7 Sep (05:31–05:55 UTC):** queue empty (new 0 / fix-shipped 0 / verified 26 / closed 12);
  shadow agent 0 seen 0 acted, heartbeat on `/dashboard/maint` at 05:36:50Z; no escalation brief.
  Ledger before: green, but RG-0308 printed a FALSE READY TO LOCK — `secret_consumers.py` read a
  failed ssh (no key loaded yet in that shard) as "no copies on the box". Fixed at the instrument
  (remote sentinel + self-heal ssh, OFFLINE-IS-NOT-ABSENT-1) and asserted as RG-0333 (LOCKED);
  RG-0308 reverted to OPEN with its pass branch tightened to the tool's own `OK:` line. Ledger
  after: 321 entries, 1 REGRESSED — RG-0271, tripped by the concurrent EMAIL-FORENSIC-1 session's
  uncommitted `emailer.py` change (country appended to legacy links); owned by that session.
  Committed, not pushed (NIGHTLY-SHIP-1).
