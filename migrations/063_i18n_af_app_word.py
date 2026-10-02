#!/usr/bin/env python3
"""063_i18n_af_app_word.py -- I18N-APP-WORD-1 (2 Oct 2026, David: "the English 'app' is translated to 'toep' ...
most people will understand the 'app' in Afrikaans and won't know what 'toep' is -- rather use the app for
Afrikaans as well even though it is currently an anglicism").

Two steps, Afrikaans only:
  1. re-apply roles/app_i18n_af.json over the cache (as 062 did) -- it now carries checked words, with 'app',
     for the main app's phrases that say "app" and were machine-translated;
  2. every OTHER cached Afrikaans phrase whose machine words say 'toep' / 'toepe' (the word, not 'toepassing' or
     'toepaslik', which mean 'applicable') is rewritten to 'app' / 'apps' in place -- no AI call, nothing re-asked.
The browsers' saved copies are dropped by ms.js DICTV 7. New machine words follow the server's glossary
(I18N_GLOSS['af'] in bea_main.py now says 'app').
"""
import json, os, re, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
SRC = os.path.join(os.getcwd(), "roles", "app_i18n_af.json")   # rides the deploy manifest
WORD = re.compile(r"\b([Tt])oep(e?)\b")

def app_word(text):
    return WORD.sub(lambda m: ("A" if m.group(1) == "T" else "a") + "pp" + ("s" if m.group(2) else ""), text)

def main():
    if not os.path.isfile(DB):
        print("063: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    if os.path.isfile(SRC):
        data = json.load(open(SRC, encoding="utf-8"))
        rows = [("af", k, v, now) for k, v in (data.get("t") or {}).items() if k and v]
        rows += [("af", k, k, now) for k in (data.get("en") or []) if k]
        print("063: af -- %d checked phrases to re-apply" % len(rows))
    else:
        print("063: %s not on the server (deploy manifest?) -- step 1 skipped" % SRC)
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        conn.execute("""CREATE TABLE IF NOT EXISTS i18n_cache(
            lang TEXT NOT NULL, src TEXT NOT NULL, out TEXT NOT NULL, created_at TEXT NOT NULL,
            PRIMARY KEY (lang, src))""")
        checked = set(r[1] for r in rows)   # step 1's own phrases are never rewritten by step 2
        toep = [(s, o) for s, o in conn.execute("SELECT src, out FROM i18n_cache WHERE lang='af'")
                if s not in checked and WORD.search(o or "")]
        print("063: af -- %d cached machine phrases say 'toep'" % len(toep))
        for s, o in toep[:20]:
            print("063:   %r -> %r" % (o[:90], app_word(o)[:90]))
        if not APPLY:
            print("063: dry run -- pass --apply"); return 0
        if rows:
            conn.executemany("INSERT INTO i18n_cache (lang, src, out, created_at) VALUES (?,?,?,?) "
                             "ON CONFLICT(lang, src) DO UPDATE SET out=excluded.out, created_at=excluded.created_at",
                             rows)
        conn.executemany("UPDATE i18n_cache SET out=?, created_at=? WHERE lang='af' AND src=?",
                         [(app_word(o), now, s) for s, o in toep])
        conn.commit()
        left = sum(1 for (o,) in conn.execute("SELECT out FROM i18n_cache WHERE lang='af'") if WORD.search(o or ""))
        print("063: applied; %d af phrases still say 'toep' (must be 0)" % left)
        return 0 if left == 0 else 1
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
