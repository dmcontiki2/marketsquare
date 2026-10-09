#!/usr/bin/env python3
"""072_i18n_quick_pill.py -- QUICK-PILL-1 (David, 10 Oct 2026: "change the yellow 'Demo example' at the bottom right to
'to Quick Listing'"). The invitation cards' pill now reads 'To Quick Listing'; this puts its words in Afrikaans, isiZulu,
isiXhosa and Sepedi into the server's translation cache from the checked files (roles/app_i18n_<lang>.json), so the page
never machine-translates it. Browsers drop their saved copy through ms.js DICTV 9. Idempotent upsert."""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
KEY = "To Quick Listing"

def main():
    if not os.path.isfile(DB):
        print("072: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for lang in ("af", "zu", "xh", "nso"):
        src = os.path.join(os.getcwd(), "roles", "app_i18n_%s.json" % lang)
        if not os.path.isfile(src):
            print("072: %s not on the server (deploy manifest?) -- refusing" % src); return 1
        v = (json.load(open(src, encoding="utf-8")).get("t") or {}).get(KEY)
        if not v:
            print("072: %s has no %r -- refusing" % (src, KEY)); return 1
        rows.append((lang, KEY, v, now))
    print("072: %d rows" % len(rows))
    if not APPLY:
        print("072: dry run -- pass --apply"); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        conn.execute("""CREATE TABLE IF NOT EXISTS i18n_cache(
            lang TEXT NOT NULL, src TEXT NOT NULL, out TEXT NOT NULL, created_at TEXT NOT NULL,
            PRIMARY KEY (lang, src))""")
        conn.executemany("INSERT INTO i18n_cache (lang, src, out, created_at) VALUES (?,?,?,?) "
                         "ON CONFLICT(lang, src) DO UPDATE SET out=excluded.out, created_at=excluded.created_at", rows)
        conn.commit()
        print("072: applied")
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
