## 2026-08-05 — Testers can now report a fault from inside the app (MAINT-B1b)

**David's ruling (4 Aug):** for the month before launch the testers log their feedback
through the app's own complaint channel — not email — so the Maintenance agent's NCR
intake is exercised every day before it has to carry a real launch. Claude fixes what
comes in and writes back to the tester with what changed, so they can retest and confirm.

**The gap this closes.** There was no way to report an APP FAULT from inside the app.
`seller_complaints` / `lm_complaints` are marketplace conduct (no-shows, seller conduct),
and `/email/inbound` is the email lane — a tester on a broken screen had nowhere to go
but David's inbox, which is exactly the single point of failure the agent exists to remove.

**What shipped.**
- `app_faults` table — the in-app half of `FAULT_REGISTER.md`. Reporter gets a reference
  (`TS-nnnn`) instantly; the `BIN-nnn` fault code is assigned at triage, which is also the
  dedupe boundary: `dup_of` on a child increments the parent's `recurrence`, and that
  counter is what trips a Path B design-change dossier (register rule 3).
- `POST /app/fault` — multipart, optional screenshot. Captures the page URL, app version,
  viewport, server-side user-agent and the last few console errors, so a report arrives
  with its own evidence rather than "it didn't work".
- Auto-ACK on filing (`FAULT_ACK_SEND=0` is the off switch), quoting the reference and
  promising the retest letter. `GET /app/faults/mine` lets a tester see where each of
  their reports stands without asking anyone.
- `GET /admin/faults` (blockers first) · `PUT /admin/faults/{id}` for triage ·
  `GET /admin/faults/{id}/retest-draft` and `POST /admin/faults/{id}/retest-send` — the
  draft/send split IS David's approval gate for the first weeks: nothing reaches a
  founding seller unread.
- `ts_report.js` — a 13 KB first-party widget, no CDN, no dependency on ms.js or ms.css,
  wired into all 14 tester-facing pages (index, admin, legal, support, 9 adventure maps).
  Right-edge tab at z-index 9000 — the one fixed slot no other element already claims.

**Fail-closed, twice over.** The whole lane 503s unless `launch_switches.fault_report = 1`,
and the widget hides itself if `/flags` cannot be read. An unauthenticated POST is refused:
a caller needs a pre-launch reviewer token (header or `ts_review` cookie) or the app key.
Rate limits are 12 reports per tester per hour (durable, DB-counted) and 20 per IP per
10 minutes.

**Verified before shipping.** 49 assertions against the real code and a real SQLite —
fail-closed gate, forged-token refusal, validation, screenshot MIME + size, rate limiting,
duplicate accounting (including that re-marking the same duplicate does not double-count),
the admin queue's severity ordering, and the full draft-then-send retest path. Plus
`test_tester_intake.py` (8 source-level tripwires) wired into `predeploy_check.py`.
`datetime('now')` was deliberately kept out of the new SQL — the PG-readiness ratchet
holds at 53 (scale-shape invariant 1).

**Ledger.** `RG-0030` added as OPEN: the widget must be served, `/flags` must still carry
`fault_report`, and an unauthenticated `POST /app/fault` must never return 200. Promote to
LOCKED once it passes against the live site.

**Cost model impact:** none. No AI call is made on this path — triage is Claude-in-session
for the pre-launch month, by design (it is what generates the agent's real specification).
