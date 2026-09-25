#!/usr/bin/env python3
"""054_i18n_af_ai_cards.py -- I18N-AF-2 (25 Sep 2026).

David read the Afrikaans AI-function cards and corrected three words the runtime lane had cached:
"Eksamenstu dieplan" -> "Eksamens studieplan", "Marktverslag" (Dutch 'markt') -> "Mark verslag", and
"aangebode naweekpakket" -> "voorgestelde naweekpakket". The same pass fixed three plain errors on the same
screen ("navorsingssdossier", "'n ... toetsritkontroles", "Eenmalige Ekspedisiedossier" for Once-in-a-Lifetime)
and hand-translated the two card blurbs that were too long for the lane (Heritage, Retirement).

Same mechanism as 045, as its own note asks: the words live in roles/app_i18n_af.json and this migration
re-applies the whole checked file over the cache. ms.js DICTV is raised so every browser drops its old copy.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB  = os.path.join(os.getcwd(), "marketsquare.db")
SRC = os.path.join(os.getcwd(), "roles", "app_i18n_af.json")   # rides the deploy manifest
LANG = "af"

def main():
    if not os.path.isfile(DB):
        print("054: no database at %s -- nothing to do" % DB); return 0
    if not os.path.isfile(SRC):
        print("054: %s not on the server (not in the deploy manifest?) -- skipped" % SRC); return 0
    data = json.load(open(SRC, encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [(LANG, src, out, now) for src, out in (data.get("t") or {}).items() if src and out]
    kept = [(LANG, src, src, now) for src in (data.get("en") or []) if src]
    print("054: %d checked Afrikaans phrases, %d kept in English" % (len(rows), len(kept)))
    if not APPLY:
        print("054: dry run -- pass --apply"); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        conn.execute("""CREATE TABLE IF NOT EXISTS i18n_cache(
            lang TEXT NOT NULL, src TEXT NOT NULL, out TEXT NOT NULL, created_at TEXT NOT NULL,
            PRIMARY KEY (lang, src))""")
        conn.executemany("INSERT INTO i18n_cache (lang, src, out, created_at) VALUES (?,?,?,?) "
                         "ON CONFLICT(lang, src) DO UPDATE SET out=excluded.out, created_at=excluded.created_at",
                         rows + kept)
        conn.commit()
        n = conn.execute("SELECT COUNT(*) FROM i18n_cache WHERE lang=?", (LANG,)).fetchone()[0]
        print("054: applied; i18n_cache now holds %d Afrikaans phrases" % n)
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
