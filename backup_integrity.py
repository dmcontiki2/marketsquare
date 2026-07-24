#!/usr/bin/env python3
# backup_integrity.py <db_path> - PRAGMA integrity_check + per-table row counts
# for a pulled MarketSquare DB snapshot. Uses only the stdlib sqlite3 (always on
# David's machine), so no sqlite3.exe needs to be installed on Windows.
import sqlite3, sys
p = sys.argv[1] if len(sys.argv) > 1 else "marketsquare.db"
try:
    c = sqlite3.connect(p)
    ic = c.execute("PRAGMA integrity_check").fetchone()[0]
    print("integrity_check:", ic)
    tables = [r[0] for r in c.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()]
    print("tables: %d" % len(tables))
    for t in tables:
        try:
            n = c.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
        except Exception as e:
            n = "err: %s" % e
        print("  %-28s %s" % (t, n))
    c.close()
except Exception as e:
    print("INTEGRITY ERROR:", repr(e))
    sys.exit(1)
