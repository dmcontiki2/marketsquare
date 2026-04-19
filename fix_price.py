import sqlite3
DB = '/var/www/marketsquare/marketsquare.db'
conn = sqlite3.connect(DB)

# Find the bad listing
rows = conn.execute("SELECT id, price, title FROM listings WHERE price = '2699028480'").fetchall()
print("Found listings with bad price:")
for r in rows:
    print(f"  ID={r[0]}  price={r[1]}  title={r[2][:50]}")

# Fix it — update to correct monthly rental
conn.execute("UPDATE listings SET price = '21990' WHERE price = '2699028480'")
conn.commit()
print(f"\nFixed {conn.total_changes} listing(s).")
conn.close()
