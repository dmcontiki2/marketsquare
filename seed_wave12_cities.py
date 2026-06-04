#!/usr/bin/env python3
"""Seed Wave 1 + Wave 2 cities into the TrustSquare geo hierarchy. Idempotent."""
import sqlite3, sys, shutil, datetime, os
DB = "/var/www/marketsquare/marketsquare.db"
COMMIT = "--commit" in sys.argv

COUNTRIES = [("US","United States","State"),("GB","United Kingdom","Region"),("AU","Australia","State")]
REGIONS = [("US","New York"),("US","California"),("US","Illinois"),("US","Texas"),("US","Arizona"),
           ("US","Pennsylvania"),("GB","England"),("GB","Scotland"),("GB","Wales"),("AU","New South Wales")]
CITIES = [
 ("US","New York","New York",40.7128,-74.0060,1),
 ("GB","England","London",51.5074,-0.1278,1),
 ("AU","New South Wales","Sydney",-33.8688,151.2093,1),
 ("US","California","Los Angeles",34.0522,-118.2437,2),
 ("US","Illinois","Chicago",41.8781,-87.6298,2),
 ("US","Texas","Houston",29.7604,-95.3698,2),
 ("US","Arizona","Phoenix",33.4484,-112.0740,2),
 ("US","Pennsylvania","Philadelphia",39.9526,-75.1652,2),
 ("US","Texas","San Antonio",29.4241,-98.4936,2),
 ("US","California","San Diego",32.7157,-117.1611,2),
 ("US","Texas","Dallas",32.7767,-96.7970,2),
 ("US","California","San Jose",37.3382,-121.8863,2),
 ("US","Texas","Austin",30.2672,-97.7431,2),
 ("GB","England","Manchester",53.4808,-2.2426,2),
 ("GB","England","Birmingham",52.4862,-1.8904,2),
 ("GB","England","Leeds",53.8008,-1.5491,2),
 ("GB","Scotland","Glasgow",55.8642,-4.2518,2),
 ("GB","England","Sheffield",53.3811,-1.4701,2),
 ("GB","Scotland","Edinburgh",55.9533,-3.1883,2),
 ("GB","England","Liverpool",53.4084,-2.9916,2),
 ("GB","England","Bristol",51.4545,-2.5879,2),
 ("GB","Wales","Cardiff",51.4816,-3.1791,2),
 ("GB","England","Leicester",52.6369,-1.1398,2),
 ("ZA","Eastern Cape","Port Elizabeth",-33.9608,25.6022,2),
 ("ZA","Eastern Cape","East London",-33.0153,27.9116,2),
 ("ZA","Mpumalanga","Nelspruit",-25.4753,30.9694,2),
]
def region_id(conn,iso2,name):
    r=conn.execute("SELECT id FROM geo_regions WHERE country_iso2=? AND name=?",(iso2,name)).fetchone()
    return r[0] if r else None
def main():
    if COMMIT:
        stamp=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        bak=f"{DB}.bak-{stamp}-wave12"; shutil.copy2(DB,bak)
        print(f"[backup] {bak} ({os.path.getsize(bak)} bytes)")
    conn=sqlite3.connect(DB); conn.execute("BEGIN")
    added={"countries":0,"regions":0,"cities":0}; skipped={"countries":0,"regions":0,"cities":0}
    for iso2,name,label in COUNTRIES:
        if conn.execute("SELECT 1 FROM geo_countries WHERE iso2=?",(iso2,)).fetchone(): skipped["countries"]+=1
        else:
            conn.execute("INSERT INTO geo_countries (iso2,name,region_label,active) VALUES (?,?,?,1)",(iso2,name,label))
            added["countries"]+=1; print(f"[+country] {iso2} {name}")
    for iso2,name in REGIONS:
        if region_id(conn,iso2,name): skipped["regions"]+=1
        else:
            conn.execute("INSERT INTO geo_regions (name,country_iso2,active) VALUES (?,?,1)",(name,iso2))
            added["regions"]+=1; print(f"[+region]  {iso2}/{name}")
    for iso2,rname,cname,lat,lng,wave in CITIES:
        rid=region_id(conn,iso2,rname)
        if rid is None: print(f"[!] region missing {iso2}/{rname} -> skip {cname}"); continue
        ex=conn.execute("SELECT id,lat,lng,region_id FROM geo_cities WHERE country_iso2=? AND name=?",(iso2,cname)).fetchone()
        if ex:
            if ex[1] is None or ex[2] is None or ex[3] is None:
                conn.execute("UPDATE geo_cities SET lat=?,lng=?,region_id=?,active=1 WHERE id=?",(lat,lng,rid,ex[0]))
                added["cities"]+=1; print(f"[~city]    {iso2}/{cname} healed")
            else: skipped["cities"]+=1
        else:
            conn.execute("INSERT INTO geo_cities (name,region_id,country_iso2,active,lat,lng) VALUES (?,?,?,1,?,?)",(cname,rid,iso2,lat,lng))
            added["cities"]+=1; print(f"[+city]    W{wave} {iso2}/{rname}/{cname} ({lat},{lng})")
    print("\nPLAN added=%s skipped=%s"%(added,skipped))
    if COMMIT: conn.commit(); print("[committed]")
    else: conn.rollback(); print("[dry-run rolled back]")
    conn.close()
main()
