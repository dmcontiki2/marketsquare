#!/usr/bin/env python3
"""006_requeue_legal_credentials.py — EVIDENCE-TRUE-2 (3 Aug 2026, David's ruling:
"Re-queue them please").

THE DEFECT
----------
POST /users/{email}/documents carried the comment

    # All other doc types: auto-earn immediately (self-attestation).

so ANY uploaded file instantly awarded a credential its full points, with no human in
the loop. That included the credentials that are a LEGAL prerequisite to trade:

    category.property.ppra     15 pts   "Checked against the PPRA register (ppra.org.za)"
    category.property.ffc      10 pts   "Current-year FFC ... may not legally trade without it"
    category.property.mandate   8 pts   "Prevents fraudulent listings"

That contradicts three things the project had already decided:

  1. TRUST_SCORE_CRITERIA.md §4a — "Certificate number checked against PPRA public
     register", "Certificate uploaded and reviewed".
  2. TRUST_SCORE_CRITERIA.md Addendum 2026-07-21 §1, the evidence-true principle
     (David's ruling, 20 Jul): "every point of a displayed trust score must map to a
     specific certificate, accreditation, experience or platform-recorded result."
     A file nobody opened is not that.
  3. The app's own promise to the agent, in ms.js: "ops verifies before points".

An ops verification queue already existed (GET /trust-score/credentials/pending,
POST /trust-score/credential) — it was simply never used for these.

THE FIX
-------
bea_main.py now lands every signal in _LEGAL_SIGNALS as 'pending' on upload.
This migration applies the same rule backwards: any legal credential already sitting
at 'earned' returns to 'pending' so a person actually checks it.

Deliberately NOT re-queued:
  * 'declared' rows — a declaration was never evidence and carries its own status.
  * 'rejected' rows — already adjudicated.
  * non-legal credentials (NQF certificates, body memberships, Local Market signals) —
    self-attestation remains the model there by design.

Trust scores WILL move down for affected sellers until ops verifies. That is the point:
the score was asserting something nobody had checked.

USAGE
-----
    python3 migrations/006_requeue_legal_credentials.py --db /path/to/marketsquare.db [--apply]

Dry-run by default. Prints exactly who is affected and by how many points.
"""
import argparse
import os
import sqlite3
import sys
from datetime import datetime, timezone

LEGAL_SIGNALS = [
    "category.property.ppra",
    "category.property.ffc",
    "category.property.mandate",
    "category.cars.dealer_reg",
    "category.travel.asata",
    "category.services.trade_licence",
]


def main() -> int:
    ap = argparse.ArgumentParser()
    # post_deploy.sh runs every pending migration as `cd $MS_LIVE && python3 <m> --apply`,
    # with no --db. A required --db would abort with rc!=0, be recorded as FAILED, and
    # block every later migration in the chain — while looking like it had been handled.
    # Default to the live database relative to that cwd.
    ap.add_argument("--db", default="marketsquare.db")
    ap.add_argument("--apply", action="store_true", help="write changes (default: dry run)")
    args = ap.parse_args()

    if not os.path.exists(args.db):
        print("No database at %r — nothing to re-queue. Skipping cleanly so the "
              "migration chain is not blocked." % args.db)
        return 0

    conn = sqlite3.connect(args.db)
    conn.row_factory = sqlite3.Row
    ph = ",".join("?" * len(LEGAL_SIGNALS))

    rows = conn.execute(
        "SELECT email, signal_id, points, verified_at FROM user_credentials "
        "WHERE status='earned' AND signal_id IN (" + ph + ") ORDER BY email, signal_id",
        LEGAL_SIGNALS,
    ).fetchall()

    if not rows:
        print("Nothing to re-queue — no legal credential is sitting at 'earned'.")
        conn.close()
        return 0

    by_seller: dict = {}
    for r in rows:
        by_seller.setdefault(r["email"], []).append(r)

    print("Legal credentials currently 'earned' without a recorded human verification:\n")
    for email, creds in by_seller.items():
        pts = sum(int(c["points"] or 0) for c in creds)
        print("  %-38s  %-3d pts across %d credential(s)" % (email, pts, len(creds)))
        for c in creds:
            print("        %-34s %3s pts   verified_at=%s"
                  % (c["signal_id"], c["points"], c["verified_at"] or "(never)"))
    print("\n%d credential(s) across %d seller(s)." % (len(rows), len(by_seller)))

    if not args.apply:
        print("\nDRY RUN — nothing written. Re-run with --apply to re-queue.")
        conn.close()
        return 0

    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "UPDATE user_credentials SET status='pending', verified_at=NULL, "
        "notes=COALESCE(notes || ' | ', '') || ? "
        "WHERE status='earned' AND signal_id IN (" + ph + ")",
        ["re-queued " + now + " (EVIDENCE-TRUE-2: legal credential awaiting human verification)"]
        + LEGAL_SIGNALS,
    )
    conn.commit()
    print("\nRe-queued %d credential(s). They now appear in GET /trust-score/credentials/pending."
          % cur.rowcount)
    print("Trust scores recompute on next read; affected sellers should be told why.")
    conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
