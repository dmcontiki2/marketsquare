#!/usr/bin/env python3
"""064_i18n_af_ex_switch.py -- HOME-EX-SWITCH-1 (3 Oct 2026, David: "i had the adverts switched off, but that switch
only shows on the Browse page and not the Home page").

The AI-examples switch now also sits on Home, beside the Categories heading. Its Afrikaans was machine-made and
mixed two words for AI -- 'KI-voorbeelde aan' but 'AI-voorbeelde af' -- while Quick says 'Versteek KI-voorbeelde'.
roles/app_i18n_af.json now carries the checked words; this re-applies that file over the server's cache (as 062 and
063 did). Every browser drops its saved copy through ms.js DICTV 8. Idempotent: an upsert of the same rows.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
SRC = os.path.join(os.getcwd(), "roles", "app_i18n_af.json")   # rides the deploy manifest
MUST = {"AI examples on": "KI-voorbeelde aan", "AI examples off": "KI-voorbeelde af"}

def main():
    if not os.path.isfile(DB):
        print("064: no database at %s -- nothing to do" % DB); return 0
    if not os.path.isfile(SRC):
        print("064: %s not on the server (deploy manifest?) -- refusing" % SRC); return 1
    data = json.load(open(SRC, encoding="utf-8"))
    t = data.get("t") or {}
    for k, v in MUST.items():
        if t.get(k) != v:
            print("064: checked file says %r for %r -- refusing" % (t.get(k), k)); return 1
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = [("af", k, v, now) for k, v in t.items() if k and v]
    rows += [("af", k, k, now) for k in (data.get("en") or []) if k]
    print("064: af -- %d checked phrases to re-apply" % len(rows))
    if not APPLY:
        print("064: dry run -- pass --apply"); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        conn.execute("""CREATE TABLE IF NOT EXISTS i18n_cache(
            lang TEXT NOT NULL, src TEXT NOT NULL, out TEXT NOT NULL, created_at TEXT NOT NULL,
            PRIMARY KEY (lang, src))""")
        conn.executemany("INSERT INTO i18n_cache (lang, src, out, created_at) VALUES (?,?,?,?) "
                         "ON CONFLICT(lang, src) DO UPDATE SET out=excluded.out, created_at=excluded.created_at", rows)
        conn.commit()
        bad = [k for k, v in MUST.items()
               if (conn.execute("SELECT out FROM i18n_cache WHERE lang='af' AND src=?", (k,)).fetchone() or [None])[0] != v]
        print("064: applied; switch words wrong after apply: %d (must be 0)" % len(bad))
        return 0 if not bad else 1
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
