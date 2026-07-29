"""
mark_showcase_supers.py — one-shot (29 Jul 2026, David: "there are many adverts not
marked as adverts"). The nine showcase listings created for the agency email
(312-314 experiences, 315-317 property, 318-320 cars) shipped WITHOUT
super_example=1, so they rendered as real adverts — breaking SO-1 (demo content
must never be mistakable for the real thing). This sets the flag that drives the
red "SUPER ADVERT" banner, the detail-page benchmark strip, and SUPER-PIN-1.
Touches ONLY ids 312-320. Marietjie's real adverts are not in this range.

Run ON THE SERVER:  python3 mark_showcase_supers.py           (dry-run)
                    python3 mark_showcase_supers.py --apply   (backs up DB, commits)
"""
import os, sys, shutil, sqlite3
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB: sys.exit("No DB found — set MS_DB_PATH")
APPLY = "--apply" in sys.argv
IDS = tuple(range(312, 321))

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
rows = conn.execute(
    f"SELECT id, title, COALESCE(super_example,0) se FROM listings WHERE id IN ({','.join('?'*len(IDS))})",
    IDS).fetchall()
todo = [r for r in rows if not r["se"]]
for r in rows:
    print(f"  {r['id']} '{r['title'][:44]}' super_example={r['se']}"
          f"{' -> 1' if not r['se'] else ' (already marked)'}")
print(f"  plan: mark {len(todo)} listing(s)")
if not APPLY:
    print("  DRY RUN — nothing written. Run with --apply to commit."); sys.exit(0)
bak = DB + ".bak-mark-supers-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
shutil.copy2(DB, bak); print(f"  DB backed up -> {bak}")
conn.execute(f"UPDATE listings SET super_example=1 WHERE id IN ({','.join('?'*len(IDS))}) "
             "AND COALESCE(super_example,0)=0", IDS)
conn.commit(); conn.close()
print("  APPLIED.")
