#!/usr/bin/env python3
"""047_i18n_af_local_market.py -- I18N-AF-1c (20 Sep 2026).

David read the live Afrikaans and said it had many mistakes and sounded Dutch. He was right:
the runtime lane translates on the cheapest tier with a one-line prompt and no context, so it
gave "Uitgelicht" for Featured (Dutch), "Wereld Erfenis" for World Heritage (Dutch spacing, no
circumflex), "Vertroue Telling" for the Trust Score brand name, "KPA" for CPA and "FOUTE" for
OPS -- it translated the acronyms -- and it silently dropped lines it could not manage.

So the whole Afrikaans cache was re-done by hand, once, and is now kept: roles/app_i18n_af.json
holds 1,564 checked phrases. This migration OVERWRITES the machine Afrikaans with them.

The file's "en" list is the other half of the decision: 502 phrases stay ENGLISH on purpose --
EULA and legal clauses (RUL-143 keeps the English binding, and a half-checked Afrikaans legal
text is worse than English), acronyms, codes, and admin references. Those are seeded as
THEMSELVES, so the runtime finds a cache hit and never machine-translates them again.

Re-runnable by hand; the deploy runs it once. When a reader corrects a word, edit the file, copy
this migration to the next number and ship -- the app follows the file, never the other way.

047 is the third turn of that handle, and the first one David turned himself: "the local
market should translate to 'Plaaslike Mark'" -- capital M, because it is the name of a place in
the app, not a description. Six phrases carry it. Same code as 045 and 046.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB  = os.path.join(os.getcwd(), "marketsquare.db")
SRC = os.path.join(os.getcwd(), "roles", "app_i18n_af.json")   # rides the deploy manifest
LANG = "af"

def main():
    if not os.path.isfile(DB):
        print("047: no database at %s -- nothing to do" % DB); return 0
    if not os.path.isfile(SRC):
        print("047: %s not on the server (not in the deploy manifest?) -- skipped" % SRC); return 0
    data = json.load(open(SRC, encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [(LANG, src, out, now) for src, out in (data.get("t") or {}).items() if src and out]
    kept = [(LANG, src, src, now) for src in (data.get("en") or []) if src]
    print("047: %d checked Afrikaans phrases, %d kept in English" % (len(rows), len(kept)))
    if not APPLY:
        print("047: dry run -- pass --apply"); return 0
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
        print("047: applied; i18n_cache now holds %d Afrikaans phrases" % n)
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
