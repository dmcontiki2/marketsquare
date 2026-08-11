#!/usr/bin/env python3
"""012_no_retest_status.py — NO-RETEST-1 (David, 11 Aug 2026).

There are no retests. A complaint is fixed by us, VERIFIED by us on named machine
evidence (AIK-VERIFY-1), and CLOSED with a letter to the reporter. This one-shot
moves any row still parked in the retired retest-wait status back to 'fixed' so it
lands in the dashboard's 'awaiting close' bucket and exits through the normal
close-draft -> David approves -> close-send lane (which stamps verified_at and
closes). The Ops Map showed exactly 1 such row on 11 Aug 2026.

Idempotent: a re-run finds zero rows and changes nothing. The retest_sent_at
column is kept — it now records when the closure letter went.
"""
import os, sqlite3, sys

DB = "/var/www/marketsquare/marketsquare.db"
if not os.path.isfile(DB):
    DB = os.path.join(os.getcwd(), "marketsquare.db")   # dev fallback


def main() -> int:
    apply = "--apply" in sys.argv
    if not os.path.isfile(DB):
        print("011_no_retest_status: no database at %s — nothing to do" % DB)
        return 0
    conn = sqlite3.connect(DB)
    try:
        rows = conn.execute("SELECT id, ref, title FROM app_faults "
                            "WHERE status = 'awaiting-retest'").fetchall()
        print("011_no_retest_status: %d row(s) in the retired status" % len(rows))
        for r in rows:
            print("  #%s %s — %s" % (r[0], r[1], (r[2] or "")[:60]))
        if apply and rows:
            conn.execute("UPDATE app_faults SET status = 'fixed', "
                         "updated_at = datetime('now') WHERE status = 'awaiting-retest'")
            conn.commit()
            print("011_no_retest_status: moved -> 'fixed' (awaiting close)")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
