## 2026-09-28 — Maintenance loop (daily B2b run)

- Ledger BEFORE: 528 entries, 501 holding, 0 REGRESSED, 22 open, 5 ready-to-lock, 0 UNVERIFIED (exit 0).
  First combine read RG-0428 NOT EVALUATED: shard 1 was the process whose bootstrap installed fastapi,
  so its import cache still missed it; shard 1 re-run -> RG-0428 holding. Instrument quirk, not a fault.
- Fault queue (GET /admin/faults, probed 05:44Z): new 0 · fix-shipped 0 · verified 26 · open 0.
  maintenance_agent.py run 20260928T054331Z: seen 0, acted 0; heartbeat PROBED on /dashboard/maint.
- Lanes: backup OK (2026-09-28_0544.zip restores clean, users=136 listings=131); screen walk OK (5 languages);
  wave witness OK; host-queue STALLED -- 1 commit on main not pushed to the mirror (2.2 h). Not pushed here:
  this loop's contract forbids push/deploy; NIGHTLY-SHIP-1 owns it.
- NOT promoted: RG-0532/0534/0536/0537/0539 print READY TO LOCK, but each is a REPO-only check whose own ref
  says "lock after a rendered walk on the live app". A repo pass is weaker evidence than the entry demands,
  so they stay OPEN until that walk is done.
- Escalation brief: none in 24 h (no file written).
- No code changed.
