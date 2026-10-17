#!/usr/bin/env python3
"""083_buzz_board.py -- BUZZ-BOARD-1 (RUL-237, David 17 Oct 2026).

The Buzz Board: her own nicknames and tags for her connections (buzz_people), a log of group sends for the
daily/weekly limits (buzz_group_log), and a special with an end date on a listing (listings.special_label,
listings.special_until). The BEA also creates these on first use (_bb_ensure); this pass makes the schema exist
before the first request. Idempotent and additive only -- no data changed. Dry by default; --apply writes,
after a backup copy.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

TABLES = [
    """CREATE TABLE IF NOT EXISTS buzz_people (
        owner_email TEXT NOT NULL, pair_id INTEGER NOT NULL, nickname TEXT NOT NULL DEFAULT '',
        tags TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (owner_email, pair_id))""",
    """CREATE TABLE IF NOT EXISTS buzz_group_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT, owner_email TEXT NOT NULL, kind TEXT NOT NULL,
        target TEXT NOT NULL, n_sent INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""",
    "CREATE INDEX IF NOT EXISTS idx_buzz_group_owner ON buzz_group_log(owner_email, created_at)",
]
COLS = [("listings", "special_label", "TEXT"), ("listings", "special_until", "TEXT")]


def main():
    if not os.path.exists(DB):
        print("083: database not found at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB)
    try:
        have = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        lcols = {r[1] for r in conn.execute("PRAGMA table_info(listings)")}
        todo_t = [n for n in ("buzz_people", "buzz_group_log") if n not in have]
        todo_c = [c for t, c, _ in COLS if c not in lcols]
        print("083: tables to create %s; listing columns to add %s" % (todo_t or "none", todo_c or "none"))
        if not APPLY:
            print("083: dry run -- pass --apply to write"); return 0
        if todo_t or todo_c:
            shutil.copy2(DB, DB + ".bak-083-" + TS)
        for t in TABLES:
            conn.execute(t)
        for t, c, ty in COLS:
            if c not in lcols:
                conn.execute("ALTER TABLE %s ADD COLUMN %s %s" % (t, c, ty))
        conn.commit()
        print("083: done")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
