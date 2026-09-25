"""053 - QUICK-PASS-1 (25 Sep 2026, David: "Build it now").

quick_invites: one row per "Pass Quick on" invite. Single use, no timer (status open -> accepted |
cancelled). Holds a first name at most and, only when the sender was signed in, her session e-mail --
never a phone number (RUL-146), never her key link. New table only; no existing table is touched.
bea_main._qi_db() also creates it on first use, so this file just keeps every copy of the DB in step."""
import sqlite3, sys

def main(apply):
    c = sqlite3.connect("marketsquare.db")
    c.execute("PRAGMA busy_timeout=15000")
    have = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='quick_invites'").fetchone()
    if have:
        print("053: quick_invites already present")
    elif apply:
        c.execute("CREATE TABLE IF NOT EXISTS quick_invites (token_hash TEXT PRIMARY KEY, created_at TEXT NOT NULL, "
                  "cat TEXT, lang TEXT, inviter_name TEXT, inviter_email TEXT, status TEXT NOT NULL DEFAULT 'open', "
                  "accepted_at TEXT, cancelled_at TEXT)")
        c.commit()
        print("053: quick_invites created")
    else:
        print("053 dry run: would create quick_invites")

if __name__ == "__main__":
    main("--apply" in sys.argv)
