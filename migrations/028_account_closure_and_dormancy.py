#!/usr/bin/env python3
"""028_account_closure_and_dormancy.py — ACCOUNT-CLOSE-1 + TUPPENCE-DORMANCY-1 schema.

Creates the two additive tables the 21 Aug 2026 EULA work needs on the live box:

  account_closures           — EULA SS14.1/14.2/14.3. Records every account closure, how
                               much Tuppence was retained (or forfeited, for causes B5/B6
                               only), and whether it has since been restored to a
                               returning user.
  tuppence_dormancy_notices  — EULA SS6.3. Records every 30-day pre-expiry warning, so an
                               expiry can PROVE a notice preceded it. The sweep refuses to
                               expire anything without an aged row here.
  users.closed_at            — soft-close marker. The old DELETE endpoint hard-deleted the
                               row, which made SS14.1's restore promise impossible to keep.

Purely additive: no data is modified, nothing is dropped, no existing row is touched.
Idempotent — safe to re-run. Refuses rather than guesses if the DB cannot be opened.
"""
import os as _os, sys as _sys
if _os.getcwd() not in _sys.path:
    _sys.path.insert(0, _os.getcwd())
import sqlite3, sys

TAG = "[028_account_closure]"


def main():
    try:
        import main as bea            # CWD = live web root per the migrations contract
        conn = bea.database.get_db()
    except Exception as e:
        print(f"{TAG} REFUSE: cannot open the live DB ({e})")
        return 3

    try:
        before = set()
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            before.add(r[0])

        conn.executescript("""
        CREATE TABLE IF NOT EXISTS account_closures (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            email             TEXT NOT NULL,
            id_number_hash    TEXT,
            closed_at         TEXT NOT NULL,
            closure_type      TEXT NOT NULL,
            cause             TEXT,
            retained_tuppence INTEGER NOT NULL DEFAULT 0,
            forfeited         INTEGER NOT NULL DEFAULT 0,
            restored_at       TEXT,
            restored_to_email TEXT,
            restore_match     TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_closures_email  ON account_closures(email);
        CREATE INDEX IF NOT EXISTS idx_closures_idhash ON account_closures(id_number_hash);

        CREATE TABLE IF NOT EXISTS tuppence_dormancy_notices (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            email              TEXT NOT NULL,
            activity_at        TEXT NOT NULL,
            warned_at          TEXT NOT NULL,
            balance_at_warning INTEGER NOT NULL,
            expired_at         TEXT,
            expired_amount     INTEGER,
            message_id         TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_dormancy_email ON tuppence_dormancy_notices(email);
        CREATE UNIQUE INDEX IF NOT EXISTS idx_dormancy_once
            ON tuppence_dormancy_notices(email, activity_at);
        """)

        try:
            conn.execute("ALTER TABLE users ADD COLUMN closed_at TEXT")
            print(f"{TAG} users.closed_at added")
        except sqlite3.OperationalError:
            print(f"{TAG} users.closed_at already present")

        conn.commit()

        after = set()
        for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'"):
            after.add(r[0])
        for t in ("account_closures", "tuppence_dormancy_notices"):
            if t not in after:
                print(f"{TAG} FAILED: {t} was not created")
                return 1
        made = after - before
        print(f"{TAG} ok — tables present: account_closures, tuppence_dormancy_notices"
              + (f" (created this run: {', '.join(sorted(made))})" if made else " (already existed)"))
        return 0
    finally:
        try:
            conn.close()
        except Exception:
            pass


if __name__ == "__main__":
    sys.exit(main())
