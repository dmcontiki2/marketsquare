import sqlite3
conn = sqlite3.connect('/var/www/marketsquare/marketsquare.db')
BOOST = '2030-12-31T23:59:59+00:00'
for lid in [93, 102, 104]:
    conn.execute('UPDATE listings SET boost_until=? WHERE id=?', (BOOST, lid))
    row = conn.execute('SELECT id, title FROM listings WHERE id=?', (lid,)).fetchone()
    title = row[1][:50] if row else 'NOT FOUND'
    print('  #' + str(lid) + ' -> featured: ' + title)
conn.commit()
conn.close()
print('Done.')
