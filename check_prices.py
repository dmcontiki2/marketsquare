import sqlite3
DB = '/var/www/marketsquare/marketsquare.db'
conn = sqlite3.connect(DB)
rows = conn.execute("SELECT id, price, title FROM listings ORDER BY id").fetchall()
print(f"{'ID':<5} {'Price':<20} {'Title'[:40]}")
print('-' * 70)
for r in rows:
    print(f"{r[0]:<5} {str(r[1]):<20} {str(r[2] or '')[:40]}")
conn.close()
