## 2026-08-05 — Fixback batch: the first 16 REPORT-tab faults, dispositioned (David approved in session)

Two testers (David, Maroushka), 16 reports, every one answered. Already fixed by the parallel
session this morning and verified as-is: TS-0001 (whole matches-box now clickable), TS-0002/0003
(openDetail dead-click guard — kept deliberately as a guard rather than auto-open, because feed
cards span cities and auto-opening would bypass the Global-tier gate), TS-0004 prompt (seller's
own product label = identity), TS-0013 uploader (MAROUSHKA-CRED shipped after her v441 test).

**Implemented this batch:**
- TS-0005: Agent Hub banner says "estate, car & tour agents" (form already had Tour agent).
- TS-0007/0008 (recurrence ×2): last-resort anonymiser blur — dedupe accumulated boxes + cap
  expansion at 6% of frame per side. The verify pass still gates output: anonymity untouched,
  sprawl fixed.
- TS-0009: Parking type field (Garage/Carport/Open/Street/None) in both property wizards;
  listing spec row now says "Parking · 2 · Carport" instead of claiming everything is a garage.
- TS-0010: credential review decisions (verified/rejected) now EMAIL the person, with the
  reason — no more silent re-upload loops. Rides POST /trust-score/credential; Resend-gated.
- TS-0011: Trust Score coach must always surface unearned professional credentials (FFC, PPRA,
  qualifications) and say exactly where to upload them.
- TS-0012: HEIC/HEIF accepted — pillow-heif registered (guarded), all four upload gates widened,
  ID path converts explicitly (it stores raw); pickers + error hint updated. Migration 008
  installs the wheel.
- TS-0019: migration 008 repairs "Waterklof" in listing data (substring-safe, proven), and the
  plain-description renderer now renders **bold** instead of printing asterisks.
- TS-0020: credentials section explains where to add them and that points come after ops verify.
- ALSO: portable-SQL fix for this morning's C1-RES table (created_at supplied by code, not
  datetime('now')) — returns the PG-readiness ratchet to green.

**Deferred with reasons:** TS-0006 duplicate-photo detection (perceptual hashing — design-change
lane). Agency-verify flow for agents (TS-0013 second half — design-change lane). TS-0021 is a
work order (AI services value audit), not an app fault — scheduled as its own session.
**Open action:** the honey listing (TS-0004) needs one POST /admin/anon-rescan-listing to redact
the existing photo — flagged for the next Maintenance run.

Verified: node --check on ms.js, py_compile on bea_main.py + migration, browser probe proves the
parking field registers and **bold** renders, migration replace proven substring-safe on a test
DB, predeploy gate back to REVIEW-only. Local until the next deploy.
