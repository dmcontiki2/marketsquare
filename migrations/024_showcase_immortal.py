#!/usr/bin/env python3
"""024_showcase_immortal.py — RUL-026 (18 Aug 2026): showcase supers never fade.

The lifecycle sweep had been treating showcase listings like user listings —
fade warnings went out and some could fade/archive. The sweep + delete guards
are fixed in code; THIS heals the data: any showcase listing not 'live' comes
back, and fade-nudge stamps are cleared so no stale warning lingers.
Idempotent; safe to re-run.
"""
import sys
from datetime import datetime, timezone

def main():
    try:
        import main as bea  # CWD = live web root per the migrations contract
    except Exception as e:
        print("[024_showcase] REFUSE: cannot import main (%s)" % e); return 3
    conn = bea.database.get_db()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hurt = conn.execute(
        "SELECT id, listing_status FROM listings WHERE showcase = 1 AND "
        "(listing_status IN ('faded','archived') OR fade_nudge_sent_at IS NOT NULL)"
    ).fetchall()
    for r in hurt:
        conn.execute("UPDATE listings SET listing_status = CASE WHEN listing_status IN "
                     "('faded','archived') THEN 'live' ELSE listing_status END, "
                     "status_changed_at = CASE WHEN listing_status IN ('faded','archived') "
                     "THEN ? ELSE status_changed_at END, fade_nudge_sent_at = NULL WHERE id = ?",
                     (now, r["id"]))
    conn.commit()
    n = len(hurt)
    conn.close()
    print("[024_showcase] healed %d showcase listing(s) (revived/cleared)" % n)
    return 0

if __name__ == "__main__":
    sys.exit(main())
