#!/usr/bin/env python3
"""014_showcase_banner.py — SHOWCASE-BANNER-1 (David, 11 Aug 2026).

David: the showcase adverts (property, cars, adventures experiences, stays) must
carry the star SUPER ADVERT banner. The 2 Aug design (migration 002) had removed
the flag because super_example ALSO pins rows above real sellers (SUPER-PIN-1).
David's resolution today: banner WITHOUT the pin — super_example=1 for the banner,
plus the new showcase=1 flag which every sort (server _sort_map + ms.js comparator)
now excludes from pinning. Real sellers keep top billing; SO-1 marking is satisfied.

Selector: seller_email LIKE '%showcase%' (showcase-email@, prop-showcase*, etc.).
Prints every row it touches into the deploy log. Sanity cap: aborts if the selector
matches an implausible number of rows. Idempotent: already-marked rows are skipped.
"""
import os, sqlite3, sys

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)


def main() -> int:
    apply = "--apply" in sys.argv
    if not DB:
        print("014_showcase_banner: no live DB found — nothing to do (dev machine)")
        return 0
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()]
        if "showcase" not in cols:
            conn.execute("ALTER TABLE listings ADD COLUMN showcase INTEGER")
            print("014_showcase_banner: added listings.showcase column")
        rows = conn.execute(
            "SELECT id, title, seller_email, COALESCE(super_example,0) se, "
            "       COALESCE(showcase,0) sc FROM listings "
            "WHERE seller_email LIKE '%showcase%' ORDER BY id").fetchall()
        if len(rows) > 30:
            print("014_showcase_banner: selector matched %d rows — implausible, ABORTING" % len(rows))
            return 1
        todo = [r for r in rows if not (r["se"] and r["sc"])]
        for r in rows:
            print("  #%-4s se=%s sc=%s %-28s %s" % (r["id"], r["se"], r["sc"],
                  (r["seller_email"] or "")[:28], (r["title"] or "")[:48]))
        print("014_showcase_banner: %d showcase advert(s), %d to mark" % (len(rows), len(todo)))
        if apply and todo:
            conn.execute("UPDATE listings SET super_example = 1, showcase = 1, "
                         "updated_at = strftime('%Y-%m-%dT%H:%M:%SZ','now') "
                         "WHERE seller_email LIKE '%showcase%' AND "
                         "(COALESCE(super_example,0) = 0 OR COALESCE(showcase,0) = 0)")
            conn.commit()
            print("014_showcase_banner: marked %d row(s) — banner on, pin excluded" % len(todo))
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
