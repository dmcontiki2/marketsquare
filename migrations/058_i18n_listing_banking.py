#!/usr/bin/env python3
"""058_i18n_listing_banking.py -- I18N-LISTING-1 (26 Sep 2026).

David chose one word for both apps, 'listing' (25 Sep inspection, langt-21), and kept the banking details -- they
confirm who the seller is and are used when she buys Tuppence; nothing is ever paid out (langt-06). The app's English
changed accordingly, and a banking-details form arrived. The checked Afrikaans and Claude's isiZulu, isiXhosa and
Sepedi drafts for those lines are in roles/app_i18n_{af,zu,xh,nso}.json; this migration re-applies all four files over
the cache (the files are the source, as in 045-057). ms.js DICTV 6.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
LANGS = ("af", "zu", "xh", "nso")

def main():
    if not os.path.isfile(DB):
        print("058: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for lang in LANGS:
        src = os.path.join(os.getcwd(), "roles", "app_i18n_%s.json" % lang)
        if not os.path.isfile(src):
            print("058: %s not on the server (deploy manifest?) -- skipped" % src); continue
        data = json.load(open(src, encoding="utf-8"))
        t = [(lang, k, v, now) for k, v in (data.get("t") or {}).items() if k and v]
        e = [(lang, k, k, now) for k in (data.get("en") or []) if k]
        print("058: %s -- %d hand-drafted phrases, %d kept in English" % (lang, len(t), len(e)))
        rows += t + e
    if not APPLY:
        print("058: dry run -- pass --apply"); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        conn.execute("""CREATE TABLE IF NOT EXISTS i18n_cache(
            lang TEXT NOT NULL, src TEXT NOT NULL, out TEXT NOT NULL, created_at TEXT NOT NULL,
            PRIMARY KEY (lang, src))""")
        conn.executemany("INSERT INTO i18n_cache (lang, src, out, created_at) VALUES (?,?,?,?) "
                         "ON CONFLICT(lang, src) DO UPDATE SET out=excluded.out, created_at=excluded.created_at",
                         rows)
        conn.commit()
        for lang in LANGS:
            n = conn.execute("SELECT COUNT(*) FROM i18n_cache WHERE lang=?", (lang,)).fetchone()[0]
            print("058: applied; i18n_cache holds %d %s phrases" % (n, lang))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
