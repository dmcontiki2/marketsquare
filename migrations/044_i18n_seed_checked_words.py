#!/usr/bin/env python3
"""044_i18n_seed_checked_words.py -- I18N-SEED-1 (20 Sep 2026).

The main app translates on demand and caches every phrase (I18N-TRANSLATE-1/2). Machine output is
good enough for a paragraph and wrong for a LABEL: the first live run rendered Property as
"Impahla" (goods you carry), where the Quick door's own hand-written list says "Izindlu nezindawo".

So the checked words win: this seeds `i18n_cache` from roles/quick_i18n.json -- the same file
David's people are reading -- for isiZulu, Sesotho, Afrikaans and isiXhosa, and OVERWRITES any
machine translation already cached for those phrases. Re-runnable by hand; the deploy runs it once.

Nothing here is invented: every word comes from that file. When the reviewers correct it, ship the
file and re-run this migration (copy it to the next number) and the app follows.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
SRC = os.path.join(os.getcwd(), "roles", "quick_i18n.json")   # rides the deploy manifest
LANGS = ["af", "zu", "st", "xh"]

def main():
    if not os.path.isfile(DB):
        print("044: no database at %s -- nothing to do" % DB); return 0
    if not os.path.isfile(SRC):
        print("044: %s not on the server (not in the deploy manifest?) -- skipped" % SRC); return 0
    words = json.load(open(SRC, encoding="utf-8"))
    order = words.get("langs", LANGS)
    rows = []
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    for en, vals in (words.get("w") or {}).items():
        for i, lang in enumerate(order):
            if lang in LANGS and i < len(vals) and vals[i] and vals[i] != en:
                rows.append((lang, en, vals[i], now))
    print("044: %d checked phrases from %d strings" % (len(rows), len(words.get("w") or {})))
    if not APPLY:
        print("044: dry run -- pass --apply"); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        conn.execute("""CREATE TABLE IF NOT EXISTS i18n_cache(
            lang TEXT NOT NULL, src TEXT NOT NULL, out TEXT NOT NULL, created_at TEXT NOT NULL,
            PRIMARY KEY (lang, src))""")
        conn.executemany("INSERT INTO i18n_cache (lang, src, out, created_at) VALUES (?,?,?,?) "
                         "ON CONFLICT(lang, src) DO UPDATE SET out=excluded.out, created_at=excluded.created_at", rows)
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM i18n_cache").fetchone()[0]
        print("044: seeded; i18n_cache now holds %d phrases" % n)
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
