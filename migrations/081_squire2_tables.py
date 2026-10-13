#!/usr/bin/env python3
"""081_squire2_tables.py -- SQUIRE-2 Phase 1 (SQUIRE_2_BUILD_BRIEF.md s2-s4, built 10 Oct 2026).

Creates what Squire becomes the full personal assistant with: brief kinds + rules on squire_briefs, the
card lines of a bulk list, card_price_history (MTGJSON daily prices, 90 days rolling) with its id map,
alerts (instant / digest), feedback (learning), reports (monthly + crux) and recurring_charges (the Pro PA
monthly Tuppence -- machinery only; the squire_pro_pa switch stays OFF). The BEA also creates these on
first use (_squire2_ensure), so this pass only makes the schema exist before the first request.

Numbered 081 (not 073): another branch already holds 080; leaving 073-079 free for main avoids a clash.
Idempotent (CREATE ... IF NOT EXISTS; columns added only when missing). Additive only -- no data is
changed. Dry by default; --apply writes, after a backup copy.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

TABLES = [
    """CREATE TABLE IF NOT EXISTS squire_lines(
        id INTEGER PRIMARY KEY AUTOINCREMENT, brief_id INTEGER NOT NULL, line_no INTEGER NOT NULL,
        name TEXT NOT NULL, set_code TEXT, user_price REAL, quantity INTEGER NOT NULL DEFAULT 1,
        scryfall_id TEXT, resolved INTEGER NOT NULL DEFAULT 0, note TEXT, advice TEXT, advice_at TEXT)""",
    "CREATE INDEX IF NOT EXISTS idx_sq_lines_brief ON squire_lines(brief_id)",
    """CREATE TABLE IF NOT EXISTS card_price_history(
        uuid TEXT NOT NULL, provider TEXT NOT NULL, finish TEXT NOT NULL, date TEXT NOT NULL,
        price REAL NOT NULL, currency TEXT NOT NULL, PRIMARY KEY(uuid, provider, finish, date))""",
    "CREATE TABLE IF NOT EXISTS mtgjson_ids(scryfall_id TEXT PRIMARY KEY, uuid TEXT NOT NULL, set_code TEXT)",
    """CREATE TABLE IF NOT EXISTS squire_alerts(
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, brief_id INTEGER, kind TEXT NOT NULL,
        urgency TEXT NOT NULL, listing_id INTEGER, ref TEXT NOT NULL, title TEXT NOT NULL, body TEXT,
        created_at TEXT NOT NULL, sent_at TEXT, channel TEXT, UNIQUE(email, ref))""",
    """CREATE TABLE IF NOT EXISTS squire_feedback(
        id INTEGER PRIMARY KEY AUTOINCREMENT, brief_id INTEGER NOT NULL, listing_id INTEGER NOT NULL,
        email TEXT NOT NULL, reason TEXT NOT NULL, change_text TEXT, rules_before TEXT, rules_after TEXT,
        created_at TEXT NOT NULL)""",
    """CREATE TABLE IF NOT EXISTS squire_reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT, brief_id INTEGER NOT NULL, email TEXT NOT NULL, kind TEXT NOT NULL,
        period TEXT NOT NULL, listing_id INTEGER NOT NULL DEFAULT 0, body TEXT NOT NULL,
        charged INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL, UNIQUE(brief_id, kind, period, listing_id))""",
    """CREATE TABLE IF NOT EXISTS recurring_charges(
        id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, brief_id INTEGER NOT NULL,
        tuppence_per_month INTEGER NOT NULL, feeds_json TEXT NOT NULL, started_at TEXT,
        last_charged_period TEXT, status TEXT NOT NULL DEFAULT 'quoted', caution_text TEXT,
        caution_accepted_at TEXT, created_at TEXT NOT NULL)""",
    "CREATE TABLE IF NOT EXISTS squire2_jobs(name TEXT PRIMARY KEY, last_key TEXT, last_at TEXT, last_result TEXT)",
]


def main():
    if not os.path.exists(DB):
        print("081: database not found at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB)
    try:
        have = {r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        cols = [r[1] for r in conn.execute("PRAGMA table_info(squire_briefs)")] if "squire_briefs" in have else []
        todo = [t.split("(")[0].split()[-1] for t in TABLES if t.startswith("CREATE TABLE") and t.split("(")[0].split()[-1] not in have]
        add = [c for c in ("kind", "rules") if cols and c not in cols]
        print("081: tables to create %s; squire_briefs columns to add %s%s" % (todo, add, "" if APPLY else "  [dry]"))
        if not APPLY or (not todo and not add):
            return 0
        shutil.copy2(DB, DB + ".bak-081-" + TS)
        for t in TABLES:
            conn.execute(t)
        if "kind" in add:
            conn.execute("ALTER TABLE squire_briefs ADD COLUMN kind TEXT NOT NULL DEFAULT 'buy'")
        if "rules" in add:
            conn.execute("ALTER TABLE squire_briefs ADD COLUMN rules TEXT NOT NULL DEFAULT '{}'")
        conn.commit()
        print("081: done; backup %s" % (DB + ".bak-081-" + TS))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
