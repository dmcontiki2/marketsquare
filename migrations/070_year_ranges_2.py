#!/usr/bin/env python3
"""070_year_ranges_2.py -- YEAR-EXACT-1b. 069 found nothing to do: listings has no `source` column (Quick's
source tag never reaches the table), so it stopped before looking. This pass matches Quick's own words instead.

YEAR-EXACT-1 (Dave jnr via David, 7 Oct 2026: "the year changes its value between quick and
trustsquare"; AUD-212).

Quick's year chips are ranges ('2020+', '2015-2019', '2010-2014'); until today parseInt filed the range's lower bound
as the car's exact year, so a 2018 car read 2015 in TrustSquare. Quick now stores only an exact year it was given.
This one-time pass clears the wrongly exact year on cars saved from Quick whose own advert text still carries the range
chip, so TrustSquare shows no year (and Edit asks for it) instead of a wrong one. The range stays in the advert text.

Idempotent (a cleared year is NULL and no longer matches). Dry by default; --apply writes, after a backup copy.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
# the chip label -> the year parseInt made of it
RANGES = {"2020+": 2020, "2015–2019": 2015, "2010–2014": 2010}


def main():
    if not os.path.exists(DB):
        print("070: database not found at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(listings)")]
        if "vehicle_year" not in cols:
            print("070: listings has no vehicle_year column -- nothing to do"); return 0
        hits = []
        for label, yr in RANGES.items():
            for r in conn.execute("SELECT id FROM listings WHERE vehicle_year = ? AND COALESCE(description,'') LIKE ?",
                                  (yr, "%Year: " + label + "%")):
                hits.append((r["id"], label, yr))
        print("070: %d Quick car(s) carry a range chip filed as an exact year%s: %s"
              % (len(hits), "" if APPLY else "  [dry]", [h[0] for h in hits]))
        if not hits or not APPLY:
            return 0
        shutil.copy2(DB, DB + ".bak-070-" + TS)
        for lid, label, yr in hits:
            conn.execute("UPDATE listings SET vehicle_year = NULL WHERE id = ? AND vehicle_year = ?", (lid, yr))
        conn.commit()
        print("070: cleared the year on %d advert(s); backup %s" % (len(hits), DB + ".bak-070-" + TS))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
