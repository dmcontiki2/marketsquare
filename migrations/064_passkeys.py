#!/usr/bin/env python3
"""064_passkeys.py -- PASSKEY-1 (David, 3 Oct 2026: "I would like to test 10 first ... for me to approve after testing").

ADDS ONE NEW TABLE, `passkeys`, and touches nothing else: no existing table, column or row is read or changed.
  passkeys(id, email, cred_id UNIQUE, public_key BLOB, alg, sign_count, label, created_at, last_used_at)
It stores only each phone's PUBLIC key (the private key never leaves the phone) against the account's email.

DEFERRED: listed in migrations/DEFERRED.txt until David approves; removing that line makes the next deploy run it
(after post_deploy's automatic snapshot of the live *.db files). Until then the BEA's passkey routes answer 503 and the
app shows no Face ID button.

Undo:  python3 064_passkeys.py --rollback --apply   (drops the table; everyone signs in by email/code/Google as before;
       passkeys saved on phones simply stop working -- nothing else is lost).
"""
import os, sqlite3, sys

APPLY = "--apply" in sys.argv
ROLLBACK = "--rollback" in sys.argv
DB = os.environ.get("MS_DB") or os.path.join(os.getcwd(), "marketsquare.db")

DDL = """CREATE TABLE IF NOT EXISTS passkeys (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    email        TEXT    NOT NULL,
    cred_id      TEXT    NOT NULL UNIQUE,
    public_key   BLOB    NOT NULL,
    alg          INTEGER NOT NULL,
    sign_count   INTEGER NOT NULL DEFAULT 0,
    label        TEXT,
    created_at   TEXT    NOT NULL,
    last_used_at TEXT
)"""


def main():
    if not os.path.isfile(DB):
        print("064: no database at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        have = bool(conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='passkeys'").fetchone())
        if ROLLBACK:
            n = conn.execute("SELECT COUNT(*) FROM passkeys").fetchone()[0] if have else 0
            print("064 rollback: table %s, %d passkey(s) would be dropped" % ("present" if have else "absent", n))
            if APPLY and have:
                conn.execute("DROP TABLE passkeys"); conn.commit(); print("064 rollback: dropped")
            return 0
        print("064: table passkeys %s" % ("already present" if have else "will be created"))
        if APPLY and not have:
            conn.execute(DDL)
            conn.execute("CREATE INDEX IF NOT EXISTS ix_passkeys_email ON passkeys(LOWER(email))")
            conn.commit(); print("064: created")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
