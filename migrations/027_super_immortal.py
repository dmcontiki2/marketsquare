#!/usr/bin/env python3
"""027_super_immortal.py — SUPER-IMMORTAL-2 (20 Aug 2026): the supers come back.

RUL-026 (18 Aug) ruled the super/showcase adverts immortal: they stay live and are
deleted only by an admin. 024_showcase_immortal.py healed the data — but it keyed on
`showcase = 1`, and the seeded supers carry `super_example = 1` with `showcase` NULL.
So the exemption never covered them: the 19 Aug 20:17 release restarted the service,
the lifecycle sweep fired 2 minutes after boot, and at 18:21Z it faded all eight ZA
supers (Cars, Tutors, Services x2, Collectors, Adventures x2, Local Market) — which is
why the Collectors and Services shelves read "0 listings" on the morning of 20 Aug.

This heals the data for the SUPER flag as well as the banner flag: any super_example
or showcase listing sitting in faded/archived comes back live, and stale fade-nudge
stamps are cleared so no warning lingers. Idempotent; safe to re-run.
"""
import os as _os, sys as _sys
# MIGRATE-IMPORT-1 (19 Aug 2026): post_deploy runs us as `cd $LIVE && python3 <abs path>`.
# Python puts THIS FILE's directory on sys.path[0] -- never the CWD -- so `import main`
# raised "No module named 'main'". CWD is where main.py actually lives.
if _os.getcwd() not in _sys.path:
    _sys.path.insert(0, _os.getcwd())
import sys
from datetime import datetime, timezone

PROTECTED = "(COALESCE(super_example, 0) = 1 OR COALESCE(showcase, 0) = 1)"


def main():
    try:
        import main as bea  # CWD = live web root per the migrations contract
    except Exception as e:
        print("[027_super] REFUSE: cannot import main (%s)" % e); return 3
    conn = bea.database.get_db()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    hurt = conn.execute(
        "SELECT id, category, listing_status FROM listings WHERE " + PROTECTED + " AND "
        "(listing_status IN ('faded','archived') OR fade_nudge_sent_at IS NOT NULL)"
    ).fetchall()
    for r in hurt:
        conn.execute(
            "UPDATE listings SET listing_status = CASE WHEN listing_status IN "
            "('faded','archived') THEN 'live' ELSE listing_status END, "
            "status_changed_at = CASE WHEN listing_status IN ('faded','archived') "
            "THEN ? ELSE status_changed_at END, fade_nudge_sent_at = NULL WHERE id = ?",
            (now, r["id"]))
    conn.commit()

    # Prove it: no protected listing may be left out of sight.
    left = conn.execute(
        "SELECT COUNT(*) n FROM listings WHERE " + PROTECTED +
        " AND listing_status IN ('faded','archived')").fetchone()["n"]
    revived = [(r["id"], r["category"], r["listing_status"]) for r in hurt]
    conn.close()

    print("[027_super] healed %d protected listing(s): %s" % (len(hurt), revived))
    if left:
        print("[027_super] FAIL: %d protected listing(s) still faded/archived" % left)
        return 1
    print("[027_super] verified: 0 protected listings faded or archived")
    return 0


if __name__ == "__main__":
    sys.exit(main())
