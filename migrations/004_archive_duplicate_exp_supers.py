#!/usr/bin/env python3
"""004_archive_duplicate_exp_supers.py — EMAIL-SHOWCASE-4 (2 Aug 2026).
Listings 312/313/314 (Big 5 Game Walk / Quad Biking / Balloon Safari, seller
super-adventures@, created 28 Jul as SUPER adverts) duplicate the by-design
showcase trio 321/322/323 (normal adverts, showcase-email@, migration 001) —
same titles, same sup_email_* photos. Buyers currently see each experience twice
and three extra ZA supers crowd the pinned exemplar row against the recorded
not-super design. This archives the super copies (soft + reversible: flip
listing_status back to 'live' to undo). Idempotent; title+seller guarded.
"""
import os, sqlite3, sys

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found")
APPLY = "--apply" in sys.argv
EXPECT = {312: "Big 5 Game Walk", 313: "Quad Biking", 314: "Hot Air Balloon"}

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
n = 0
for lid, frag in EXPECT.items():
    row = conn.execute("SELECT id, title, seller_email, listing_status FROM listings WHERE id=?", (lid,)).fetchone()
    if not row or frag not in str(row["title"]) or "super-adventures@" not in str(row["seller_email"]):
        print(f"[skip] {lid}: not the expected duplicate")
        continue
    if row["listing_status"] == "archived":
        print(f"[ok] {lid} already archived")
        continue
    print(f"[{'APPLY' if APPLY else 'dry'}] archive {lid} {row['title'][:40]}")
    if APPLY:
        conn.execute("UPDATE listings SET listing_status='archived', super_example=0 WHERE id=?", (lid,))
        n += 1
if APPLY:
    conn.commit()
    print(f"done — {n} duplicate supers archived (reversible)")
conn.close()
