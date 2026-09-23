#!/usr/bin/env python3
"""048_i18n_zu_xh_nso_hand_drafts.py -- LANG-LAYER-1 / I18N-SA5-1 (RUL-162, 23 Sep 2026).

David, 23 Sep 2026: set up the other three launch languages. South Africa's list is English,
isiZulu, isiXhosa, Afrikaans and Sepedi (Sepedi replaced Sesotho, following census 2022).
Afrikaans was re-done by hand on 20 Sep (migration 045). This does the same for the other
three: roles/app_i18n_zu.json, app_i18n_xh.json and app_i18n_nso.json each hold 1,569 phrases
drafted by hand (RUL-160: Claude drafts, the Language reviewer proofreads, users' flags correct).
They OVERWRITE whatever the runtime machine lane cached for zu and xh, and seed Sepedi fresh.

Each file's "en" list (502 phrases -- EULA and legal clauses, acronyms, codes) is seeded as
ITSELF, so the runtime never machine-translates the binding English (RUL-143).

Re-runnable. When a reader corrects a word: edit the file, copy this migration to the next
number and ship -- the app follows the file.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
LANGS = ("zu", "xh", "nso")

def main():
    if not os.path.isfile(DB):
        print("048: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for lang in LANGS:
        src = os.path.join(os.getcwd(), "roles", "app_i18n_%s.json" % lang)
        if not os.path.isfile(src):
            print("048: %s not on the server (deploy manifest?) -- skipped" % src); continue
        data = json.load(open(src, encoding="utf-8"))
        t = [(lang, k, v, now) for k, v in (data.get("t") or {}).items() if k and v]
        e = [(lang, k, k, now) for k in (data.get("en") or []) if k]
        print("048: %s -- %d hand-drafted phrases, %d kept in English" % (lang, len(t), len(e)))
        rows += t + e
    if not APPLY:
        print("048: dry run -- pass --apply"); return 0
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
            print("048: applied; i18n_cache holds %d %s phrases" % (n, lang))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
