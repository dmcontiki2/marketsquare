#!/usr/bin/env python3
"""022_planner_specs.py — Planner Lane Phase A (16 Aug 2026): the personal-journey store.

One row per composed plan. The spec is the whole artifact (renderable any time by
journey_render); nothing else to migrate. Idempotent by construction.
"""
import os, sqlite3, sys

APPLY = "--apply" in sys.argv
DB = "/var/www/marketsquare/marketsquare.db"

def main():
    if not os.path.exists(DB):
        print("[022_planner] REFUSE: %s not found" % DB); return 3
    if not APPLY:
        print("[022_planner] dry-run OK: would CREATE TABLE IF NOT EXISTS planner_specs"); return 0
    c = sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS planner_specs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        kind TEXT NOT NULL,
        spec_json TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now')))""")
    c.execute("CREATE INDEX IF NOT EXISTS idx_planner_user ON planner_specs(user_email, created_at)")
    c.commit(); c.close()
    print("[022_planner] applied: planner_specs ready")
    return 0

if __name__ == "__main__":
    sys.exit(main())
