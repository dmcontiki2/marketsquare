"""
set_featured.py — marks real BEA listings as featured by setting boost_until far-future.
Run on server: python3 /tmp/set_featured.py
"""
import sqlite3

DB = '/var/www/marketsquare/marketsquare.db'
FEATURED_IDS = [93, 94, 95, 96, 97, 103]
BOOST_UNTIL  = '2030-12-31T23:59:59+00:00'

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

for lid in FEATURED_IDS:
    row = conn.execute("SELECT id, title, category FROM listings WHERE id = ?", (lid,)).fetchone()
    if row:
        conn.execute(
            "UPDATE listings SET boost_until = ? WHERE id = ?",
            (BOOST_UNTIL, lid)
        )
        print(f"  ✓ #{lid} {row['category']} — {row['title'][:50]} → featured until 2030")
    else:
        print(f"  ✗ #{lid} not found")

conn.commit()
conn.close()

# Verify
print("\nVerification:")
conn2 = sqlite3.connect(DB)
conn2.row_factory = sqlite3.Row
for lid in FEATURED_IDS:
    row = conn2.execute("SELECT id, title, boost_until FROM listings WHERE id = ?", (lid,)).fetchone()
    if row:
        print(f"  #{lid}: boost_until={row['boost_until']} title={row['title'][:40]}")
conn2.close()
print("\nDone.")
