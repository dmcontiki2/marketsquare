#!/usr/bin/env python3
"""055_i18n_af_inspection.py -- I18N-AF-3 (26 Sep 2026).

The 25 Sep inspection (INSPECTION_2026-09-25.html, langt-32/33/51-54) found Afrikaans words that mean something
else on screen: "Handmatig" for a manual gearbox (now "Handrat"), "Primer" for primary school ("Laerskool"),
"Verbind" on the Commitment badge ("Verbintenis"), "kragverkoper" for power seller ("topverkoper"), "lopie" for an
AI run ("keer"/"uitvoering"/"versoek"), "Sagte tou" ("Oop tou"), "Uitgestal" for Featured ("Uitgelig"),
"Nutsman" for Handyman, and "live" as "regstreeks"/"lewend" ("aanlyn"/"sigbaar"). The same pass reworded some
English (intro -> introduction, the free plan's card line, the queue badges), and the checked Afrikaans for the new
English is added so the runtime lane never machine-translates it.

Same mechanism as 045/046/054: the words live in roles/app_i18n_af.json and this migration re-applies the whole
checked file over the cache; ms.js DICTV is raised to 4 so every browser drops its old copy.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB  = os.path.join(os.getcwd(), "marketsquare.db")
SRC = os.path.join(os.getcwd(), "roles", "app_i18n_af.json")   # rides the deploy manifest
LANG = "af"

def main():
    if not os.path.isfile(DB):
        print("055: no database at %s -- nothing to do" % DB); return 0
    if not os.path.isfile(SRC):
        print("055: %s not on the server (not in the deploy manifest?) -- skipped" % SRC); return 0
    data = json.load(open(SRC, encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [(LANG, src, out, now) for src, out in (data.get("t") or {}).items() if src and out]
    kept = [(LANG, src, src, now) for src in (data.get("en") or []) if src]
    print("055: %d checked Afrikaans phrases, %d kept in English" % (len(rows), len(kept)))
    if not APPLY:
        print("055: dry run -- pass --apply"); return 0
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
        print("055: applied; i18n_cache now holds %d Afrikaans phrases" % n)
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
