"""
relink_maurice.py — same verified procedure as the Marietjie relink (Session 148).
Run ON THE SERVER:  python3 relink_maurice.py maurice.new@address.com          (dry-run)
                    python3 relink_maurice.py maurice.new@address.com --apply  (backs up DB, commits)
"""
import os, sys, shutil, sqlite3
from datetime import datetime

OLD = "mauriceconradie@yahoo.com"
if len(sys.argv) < 2 or "@" not in sys.argv[1]:
    sys.exit("Usage: python3 relink_maurice.py <new-email> [--apply]")
NEW = sys.argv[1].strip().lower()
APPLY = "--apply" in sys.argv

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB: sys.exit("No DB found — set MS_DB_PATH")

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
tables = [("users","email"), ("listings","seller_email"), ("user_credentials","email")]
print(f"DB: {DB}\nRelink {OLD} -> {NEW}")
total = 0
for t, col in tables:
    try:
        n = conn.execute(f"SELECT COUNT(*) FROM {t} WHERE LOWER({col})=?", (OLD,)).fetchone()[0]
    except sqlite3.OperationalError as e:
        print(f"  {t}.{col}: skipped ({e})"); continue
    clash = conn.execute(f"SELECT COUNT(*) FROM {t} WHERE LOWER({col})=?", (NEW,)).fetchone()[0]
    print(f"  {t}.{col}: {n} row(s) to update" + (f"  WARNING: {clash} row(s) already use {NEW}" if clash else ""))
    total += n
if not total: sys.exit("Nothing references the old address — check spelling / maybe already relinked.")
if not APPLY: sys.exit("DRY RUN — re-run with --apply.")

bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-maurice-relink"
shutil.copy2(DB, bak); print("DB backup:", bak)
for t, col in tables:
    try:
        conn.execute(f"UPDATE {t} SET {col}=? WHERE LOWER({col})=?", (NEW, OLD))
    except sqlite3.OperationalError:
        pass
conn.commit()
left = sum(conn.execute(f"SELECT COUNT(*) FROM {t} WHERE LOWER({c})=?", (OLD,)).fetchone()[0]
           for t, c in tables if True)
print(f"Done. Old refs remaining: {left} (must be 0). Superuser flag and PIN untouched.")
