"""051 - SESSION-END-1 / SIGNIN-ONCE-1 (24 Sep 2026, security assessment).

users.session_version (sign-out and account closure end every session) and used_signin_links
(a sign-in link works once). Additive and idempotent. Applied by hand on the live DB before the
SEC-ASSESS-3 deploy, because the QA Bot reads a schema change mid-run as 'changed another
person's data (users)' and rolled c66c216 back; this file keeps every other copy of the DB in step."""
import sqlite3, sys

def main(apply):
    c = sqlite3.connect("marketsquare.db")
    c.execute("PRAGMA busy_timeout=15000")
    cols = [r[1] for r in c.execute("PRAGMA table_info(users)")]
    if "session_version" not in cols:
        print("add users.session_version")
        if apply:
            c.execute("ALTER TABLE users ADD COLUMN session_version INTEGER DEFAULT 0")
    if apply:
        c.execute("CREATE TABLE IF NOT EXISTS used_signin_links (link_hash TEXT PRIMARY KEY, used_at REAL NOT NULL)")
        c.commit()
    print("051 done" if apply else "051 dry run")

if __name__ == "__main__":
    main("--apply" in sys.argv)
