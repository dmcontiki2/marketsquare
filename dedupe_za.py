#!/usr/bin/env python3
"""Merge duplicate ZA city entries created by the Wave 2 seed.
Keeps the official GeoNames entries (which carry the suburbs), renames them to
include the still-common former name in parens, and removes the 0-suburb dupes.
Idempotent. Dry-run unless --commit."""
import sqlite3, sys, shutil, datetime, os
DB="/var/www/marketsquare/marketsquare.db"
COMMIT="--commit" in sys.argv

# (dupe_name_to_remove, canonical_name, canonical_new_name)
PAIRS=[
    ("Nelspruit",       "Mbombela", "Mbombela (Nelspruit)"),
    ("Port Elizabeth",  "Gqeberha", "Gqeberha (Port Elizabeth)"),
]

def main():
    if COMMIT:
        stamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        bak=f"{DB}.bak-{stamp}-dedupe"; shutil.copy2(DB,bak)
        print(f"[backup] {bak} ({os.path.getsize(bak)} bytes)")
    conn=sqlite3.connect(DB); conn.row_factory=sqlite3.Row; conn.execute("BEGIN")
    for dupe_name, canon_name, canon_new in PAIRS:
        # canonical row may already be renamed (idempotent) — match either spelling
        canon=conn.execute(
            "SELECT id,name,(SELECT COUNT(*) FROM geo_suburbs WHERE city_id=geo_cities.id) sub "
            "FROM geo_cities WHERE country_iso2='ZA' AND name IN (?,?)",
            (canon_name, canon_new)).fetchone()
        dupe=conn.execute(
            "SELECT id,name,(SELECT COUNT(*) FROM geo_suburbs WHERE city_id=geo_cities.id) sub "
            "FROM geo_cities WHERE country_iso2='ZA' AND name=?",(dupe_name,)).fetchone()
        if not canon:
            print(f"[!] canonical {canon_name!r} not found — skipping {dupe_name}"); continue
        # safety: never delete a dupe that has suburbs or listings
        if dupe:
            nlist=conn.execute("SELECT COUNT(*) FROM listings WHERE geo_city_id=?",(dupe["id"],)).fetchone()[0]
            if dupe["sub"]>0 or nlist>0:
                print(f"[ABORT] dupe {dupe_name} (id{dupe['id']}) has {dupe['sub']} suburbs / {nlist} listings — NOT deleting"); 
                conn.rollback(); conn.close(); sys.exit(1)
            conn.execute("DELETE FROM geo_cities WHERE id=?",(dupe["id"],))
            print(f"[-dupe]   removed {dupe_name} (id{dupe['id']}, {dupe['sub']} suburbs)")
        else:
            print(f"[skip]    no dupe {dupe_name!r} present (already removed)")
        if canon["name"]!=canon_new:
            conn.execute("UPDATE geo_cities SET name=? WHERE id=?",(canon_new,canon["id"]))
            print(f"[rename]  id{canon['id']} {canon['name']!r} -> {canon_new!r} (keeps {canon['sub']} suburbs)")
        else:
            print(f"[skip]    id{canon['id']} already named {canon_new!r}")
    print("\n=== resulting Mpumalanga/E-Cape city check ===")
    for nm in ("Mbombela (Nelspruit)","Gqeberha (Port Elizabeth)","Nelspruit","Port Elizabeth","Mbombela","Gqeberha"):
        rows=conn.execute("SELECT id,name FROM geo_cities WHERE name=? AND country_iso2='ZA'",(nm,)).fetchall()
        print(f"  {nm!r}: {[r['id'] for r in rows] or 'ABSENT'}")
    if COMMIT: conn.commit(); print("\n[committed]")
    else: conn.rollback(); print("\n[dry-run rolled back]")
    conn.close()
main()
