#!/usr/bin/env python3
"""049_lang_layer_on.py -- LANG-ON-1 (David, 23 Sep 2026, in chat: "please switch the languages on").

Arms launch_switches.lang_layer for everybody: the country language menus (South Africa: English,
isiZulu, isiXhosa, Afrikaans, Sepedi), the advert's one approved second language, code chips and
the English search layer. Until now it was on for testers only. The switch was David's act (RUL-162);
this migration carries his instruction to the box and writes the admin_audit row the flags route
would have written. Reversible without a deploy: POST /admin/flags {"lang_layer": false}.
"""
import os, sqlite3, sys
from datetime import datetime, timezone
APPLY = "--apply" in sys.argv
DB = os.path.join(os.getcwd(), "marketsquare.db")

def main():
    if not os.path.isfile(DB):
        print("049: no database -- nothing to do"); return 0
    if not APPLY:
        print("049: dry run -- would set launch_switches.lang_layer = 1"); return 0
    conn = sqlite3.connect(DB)
    try:
        conn.execute("PRAGMA busy_timeout=8000")
        cols = [r[1] for r in conn.execute("PRAGMA table_info(launch_switches)").fetchall()]
        if "lang_layer" not in cols:
            conn.execute("ALTER TABLE launch_switches ADD COLUMN lang_layer INTEGER NOT NULL DEFAULT 0")
        prior = conn.execute("SELECT lang_layer FROM launch_switches WHERE id=1").fetchone()
        conn.execute("UPDATE launch_switches SET lang_layer=1, updated_at=CURRENT_TIMESTAMP WHERE id=1")
        try:
            conn.execute("INSERT INTO admin_audit (ts, actor, action, field, prior, new, reason) VALUES (?,?,?,?,?,?,?)",
                         (datetime.now(timezone.utc).isoformat(timespec="seconds"), "migration-049 (David, chat 23 Sep 2026)",
                          "flags", "lang_layer", str(prior[0] if prior else None), "1", "David: 'please switch the languages on'"))
        except Exception as e:
            print("049: audit row skipped (%s)" % e)
        conn.commit()
        now = conn.execute("SELECT lang_layer FROM launch_switches WHERE id=1").fetchone()
        print("049: applied; lang_layer = %s" % (now[0] if now else None))
    finally:
        conn.close()
    return 0

if __name__ == "__main__":
    sys.exit(main())
