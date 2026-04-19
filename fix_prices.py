import sqlite3
DB = '/var/www/marketsquare/marketsquare.db'
conn = sqlite3.connect(DB)

fixes = [
    (5,  '18990'),   # R 18 990  → clean numeric
    (6,  '21990'),   # R21,990.00 → clean numeric
    (7,  '21990'),   # R21,990.00 per month → clean numeric
    (8,  '26990'),   # R26,990/month (all-inclusive...) → primary monthly price only
]

for listing_id, clean_price in fixes:
    old = conn.execute("SELECT price FROM listings WHERE id=?", (listing_id,)).fetchone()
    conn.execute("UPDATE listings SET price=? WHERE id=?", (clean_price, listing_id))
    print(f"ID {listing_id}: '{old[0]}' → '{clean_price}'")

conn.commit()
print('\nAll prices fixed.')
conn.close()
