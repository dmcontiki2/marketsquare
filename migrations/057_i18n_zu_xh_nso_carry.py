#!/usr/bin/env python3
"""057_i18n_zu_xh_nso_carry.py -- I18N-SA5-2 (26 Sep 2026, INSPECT-FIX-2).

The 25 Sep inspection reworded some of the app's English (introduction instead of intro, 'sign-in link', the free plan's
card line, the trust levels the Seller Hub now names, the fresh-version bar). Afrikaans got its checked words in 055/056;
isiZulu, isiXhosa and Sepedi readers would have been handed the runtime machine lane for those lines instead of Claude's
hand drafts (RUL-165: the drafts are the live versions, readers correct them after launch). The 35 phrases are added to
roles/app_i18n_zu.json, app_i18n_xh.json and app_i18n_nso.json, and this migration re-applies the three files exactly as
048 does (the file is the source; a machine answer cached since the morning's deploy is overwritten). ms.js DICTV 5.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
LANGS = ("zu", "xh", "nso")

def main():
    if not os.path.isfile(DB):
        print("057: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for lang in LANGS:
        src = os.path.join(os.getcwd(), "roles", "app_i18n_%s.json" % lang)
        if not os.path.isfile(src):
            print("057: %s not on the server (deploy manifest?) -- skipped" % src); continue
        data = json.load(open(src, encoding="utf-8"))
        t = [(lang, k, v, now) for k, v in (data.get("t") or {}).items() if k and v]
        e = [(lang, k, k, now) for k in (data.get("en") or []) if k]
        print("057: %s -- %d hand-drafted phrases, %d kept in English" % (lang, len(t), len(e)))
        rows += t + e
    if not APPLY:
        print("057: dry run -- pass --apply"); return 0
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
            print("057: applied; i18n_cache holds %d %s phrases" % (n, lang))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
