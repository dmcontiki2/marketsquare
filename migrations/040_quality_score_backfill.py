#!/usr/bin/env python3
"""040_quality_score_backfill.py -- ZOOM-HMI-1 prerequisite (RG-0221, 17 Sep 2026).

WHY. Listing quality was computed per row by main.py::_import_quality_score and never
STORED, so nothing could ORDER BY it -- the Ranking Score (0.5 quality + 0.5 trust,
ZOOM_HMI_SPEC.md 6.1) ranked agents only and never touched the results a buyer browses.
main.py now stamps listings.quality_score on create / edit / publish / photo add; this is
the one-time backfill for every row written before the column existed.

Idempotent: rows already stamped are left alone. Dry by default; --apply writes, after a
backup. Imports the SAME scorer main.py uses -- no second definition of quality.
"""
import os, shutil, sqlite3, sys
from datetime import datetime, timezone
APPLY = "--apply" in sys.argv
DB = os.environ.get("MS_DB", "/var/www/marketsquare/marketsquare.db")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

def _scorer():
    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.environ.setdefault("MS_API_KEY", "migration-040-import-only")
    for mod in ("main", "bea_main"):
        try:
            m = __import__(mod)
            return getattr(m, "_import_quality_score")
        except Exception as ex:      # the other name, or an import-time env guard
            last = ex
    raise SystemExit("040: cannot import _import_quality_score from main.py/bea_main.py: %r" % (last,))

def main():
    if not os.path.exists(DB):
        print("040: database not found at %s -- nothing to do" % DB); return 0
    conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
    try:
        cols = [r[1] for r in conn.execute("PRAGMA table_info(listings)")]
        if "quality_score" not in cols:
            if not APPLY:
                print("040: listings.quality_score column absent -- would ADD it  [dry]"); 
            else:
                conn.execute("ALTER TABLE listings ADD COLUMN quality_score REAL"); conn.commit()
                print("040: added listings.quality_score")
        rows = conn.execute("SELECT * FROM listings WHERE quality_score IS NULL").fetchall() if (APPLY or "quality_score" in cols) else []
        if not rows and "quality_score" in cols:
            print("040: nothing to backfill -- every listing already carries quality_score"); return 0
        print("040: %d listing(s) to stamp%s" % (len(rows), "" if APPLY else "  [dry]"))
        if not APPLY:
            return 0
        score = _scorer()
        bak = "%s.bak-quality-%s" % (DB, TS)
        shutil.copy2(DB, bak); print("040: backup -> %s" % bak)
        n = 0
        for r in rows:
            try:
                q, _missing = score(r)
                conn.execute("UPDATE listings SET quality_score = ? WHERE id = ?", (float(q), r["id"])); n += 1
            except Exception as ex:
                print("040: listing %s skipped: %r" % (r["id"], ex))
        conn.commit()
        print("040: stamped %d listing(s)" % n)
        return 0
    finally:
        conn.close()

if __name__ == "__main__":
    sys.exit(main())
