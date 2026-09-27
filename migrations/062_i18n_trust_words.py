#!/usr/bin/env python3
"""062_i18n_trust_words.py -- CC-005 / TRUST-WORDS-1 (27 Sep 2026, David approved the wording as written).

The Trust Score bands now name the strength of EVIDENCE, never a quality of the person (RUL-088):
Some evidence (40+) / Strong evidence (70+) / Fullest evidence (90+), plus the two standing lines shown wherever
the score is shown or filtered. Their Afrikaans, isiZulu, isiXhosa and Sepedi (Claude's drafts, RUL-165) are in
roles/app_i18n_{af,zu,xh,nso}.json; this migration re-applies all four files over the cache, as 059 did.
New keys only, so DICTV stays.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
LANGS = ("af", "zu", "xh", "nso")

def main():
    if not os.path.isfile(DB):
        print("062: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for lang in LANGS:
        src = os.path.join(os.getcwd(), "roles", "app_i18n_%s.json" % lang)
        if not os.path.isfile(src):
            print("062: %s not on the server (deploy manifest?) -- skipped" % src); continue
        data = json.load(open(src, encoding="utf-8"))
        t = [(lang, k, v, now) for k, v in (data.get("t") or {}).items() if k and v]
        e = [(lang, k, k, now) for k in (data.get("en") or []) if k]
        print("062: %s -- %d hand-drafted phrases, %d kept in English" % (lang, len(t), len(e)))
        rows += t + e
    if not APPLY:
        print("062: dry run -- pass --apply"); return 0
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
            print("062: applied; i18n_cache holds %d %s phrases" % (n, lang))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
