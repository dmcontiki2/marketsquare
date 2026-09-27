#!/usr/bin/env python3
"""061_i18n_terms_r7.py -- R7 (27 Sep 2026): the words of David's 26-27 Sep decisions, in four languages.

BUYER-TERMS-1 (the one-tap Terms sheet for a first introduction request or top-up, and its toasts), EULA-1.19 (the
in-app notice card: "Our Terms change on 12 October 2026", its summary sentences, and the same sentences in the Seller
Terms box after the change), PROPERTY-ONE-1 (one buyer at a time: the How-it-works lines, the seller's "Paused while
you answer a buyer" note and the two refusals) and COUNTRY-OPEN-1 (the "coming soon" chip and the Germany, Botswana
and Mozambique refusals), INTRO-WITHDRAW-1 (her own Withdraw button on a request the seller has not answered, and the
Expired / Withdrawn chips that used to read 'Pending'). Claude's Afrikaans, isiZulu, isiXhosa and Sepedi are in roles/app_i18n_{af,zu,xh,nso}.json,
re-applied over the cache as in 058-060. New keys only, so DICTV stays 6.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")
LANGS = ("af", "zu", "xh", "nso")

def main():
    if not os.path.isfile(DB):
        print("061: no database at %s -- nothing to do" % DB); return 0
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    rows = []
    for lang in LANGS:
        src = os.path.join(os.getcwd(), "roles", "app_i18n_%s.json" % lang)
        if not os.path.isfile(src):
            print("061: %s not on the server (deploy manifest?) -- skipped" % src); continue
        data = json.load(open(src, encoding="utf-8"))
        t = [(lang, k, v, now) for k, v in (data.get("t") or {}).items() if k and v]
        e = [(lang, k, k, now) for k in (data.get("en") or []) if k]
        print("061: %s -- %d hand-drafted phrases, %d kept in English" % (lang, len(t), len(e)))
        rows += t + e
    if not APPLY:
        print("061: dry run -- pass --apply"); return 0
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
            print("061: applied; i18n_cache holds %d %s phrases" % (n, lang))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
