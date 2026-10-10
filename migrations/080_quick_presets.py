#!/usr/bin/env python3
"""080_quick_presets.py -- QUICK-FAST-1 (RUL-220, David 9-10 Oct 2026; CC-006): the Quick fast lane's one table.

A repeat trader ticks "Make this my quick icon" at the end of a Quick flow; the flow's setup is kept as a PRESET and
his phone gets a home-screen icon for it. Schema (the brief's one table, plus counters the dashboard reads):

    quick_presets(id, token UNIQUE, email, kind 'sell'|'find', settings_json, label, created_at, active,
                  uses, last_used_at, finds, fallbacks, parse_day, parse_n, ai_n)

and the dashboard switch launch_switches.quick_fastlane (default 0 = OFF: every fast-lane entry point hidden, the
routes answer 404). bea_main.py creates the same table and column itself at startup (CREATE ... IF NOT EXISTS /
ALTER guarded), so this migration is belt and braces: it makes them before the new code's first request and it is
idempotent (check-then-act). Nothing existing is changed or removed.

    python3 080_quick_presets.py            # dry run: says what it would do
    python3 080_quick_presets.py --apply    # does it (post_deploy.sh runs it once, CWD = live web root)
Reverse: DROP TABLE quick_presets (the presets only; listings are untouched) -- the switch column may stay, unused.
"""
import os
import sqlite3
import sys

APPLY = "--apply" in sys.argv
DB = os.path.join(os.environ.get("MS_LIVE", os.getcwd()), "marketsquare.db")

DDL = """CREATE TABLE IF NOT EXISTS quick_presets(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL,
    kind TEXT NOT NULL CHECK (kind IN ('sell','find')),
    settings_json TEXT NOT NULL,
    label TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    active INTEGER NOT NULL DEFAULT 1,
    uses INTEGER NOT NULL DEFAULT 0,
    last_used_at TEXT,
    finds INTEGER NOT NULL DEFAULT 0,
    fallbacks INTEGER NOT NULL DEFAULT 0,
    parse_day TEXT,
    parse_n INTEGER NOT NULL DEFAULT 0,
    ai_n INTEGER NOT NULL DEFAULT 0)"""


def main():
    if not os.path.exists(DB):
        print("080: no database at %s -- nothing to do" % DB)
        return 0
    conn = sqlite3.connect(DB)
    try:
        have = conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='quick_presets'").fetchone()
        cols = [r[1] for r in conn.execute("PRAGMA table_info(launch_switches)").fetchall()]
        todo = []
        if not have:
            todo.append("create table quick_presets")
        if cols and "quick_fastlane" not in cols:
            todo.append("add launch_switches.quick_fastlane (default 0 = OFF)")
        if not todo:
            print("080: already in place")
            return 0
        print("080: " + ("applying: " if APPLY else "would apply: ") + "; ".join(todo))
        if not APPLY:
            return 0
        conn.execute(DDL)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_quick_presets_email ON quick_presets(email)")
        if cols and "quick_fastlane" not in cols:
            conn.execute("ALTER TABLE launch_switches ADD COLUMN quick_fastlane INTEGER NOT NULL DEFAULT 0")
        conn.commit()
        print("080: done")
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
