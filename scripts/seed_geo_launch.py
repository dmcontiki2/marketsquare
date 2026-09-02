#!/usr/bin/env python3
"""GEO-LAUNCH-1 (2 Sep 2026) -- make the app's location picker show exactly the
cities we are recruiting in. Idempotent; runs on EVERY deploy from post_deploy.sh
(step 1c), same contract as seed_super_global.py.

Truth = geo_launch_cities.json beside this script (generated from
CityLauncher/data/cities.json by scripts/build_geo_launch_cities.py).

Rules applied to the live geo_* tables:
  1. Every listed city exists (country/region/city inserted if missing, with coords).
  2. geo_cities.active = 1  iff  listed  OR  it has at least one listing
     (a city with real listings is never hidden -- Denver, Nairobi, Maun, Windhoek,
     Maputo, Garmisch, Adelaide carry the super/ladder demo listings).
  3. geo_regions.active = 1 iff it has an active city; geo_countries likewise.
Nothing is deleted; listings.geo_city_id is never touched. Reverse = flip active.

  python3 seed_geo_launch.py            dry run (prints the plan)
  python3 seed_geo_launch.py --apply    apply (backs the DB up first)
"""
import json, os, sys, shutil, sqlite3, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
DB = os.environ.get("MS_DB") or ("/var/www/marketsquare/marketsquare.db"
                                 if os.path.exists("/var/www/marketsquare/marketsquare.db")
                                 else os.path.join(HERE, "marketsquare.db"))
DATA = os.path.join(HERE, "geo_launch_cities.json")
APPLY = "--apply" in sys.argv


def region_id(conn, iso2, name):
    r = conn.execute("SELECT id FROM geo_regions WHERE country_iso2=? AND name=?", (iso2, name)).fetchone()
    return r[0] if r else None


def main():
    cities = json.load(open(DATA, encoding="utf-8"))["cities"]
    if not os.path.exists(DB):
        sys.exit("seed_geo_launch: DB not found at %s" % DB)
    if APPLY:
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        bak = "%s.bak-%s-geolaunch" % (DB, stamp)
        shutil.copy2(DB, bak); print("[backup]", bak)
    conn = sqlite3.connect(DB)
    conn.execute("BEGIN")
    n = {"country+": 0, "region+": 0, "city+": 0, "city_on": 0, "city_off": 0,
         "region_on": 0, "region_off": 0, "country_on": 0, "country_off": 0}
    listed_ids = set()
    for c in cities:
        if not conn.execute("SELECT 1 FROM geo_countries WHERE iso2=?", (c["iso2"],)).fetchone():
            conn.execute("INSERT INTO geo_countries (iso2,name,region_label,active) VALUES (?,?,?,1)",
                         (c["iso2"], c["country"], c["region_label"]))
            n["country+"] += 1; print("[+country]", c["iso2"], c["country"])
        rid = region_id(conn, c["iso2"], c["region"])
        if rid is None:
            conn.execute("INSERT INTO geo_regions (name,country_iso2,active) VALUES (?,?,1)",
                         (c["region"], c["iso2"]))
            rid = region_id(conn, c["iso2"], c["region"])
            n["region+"] += 1; print("[+region] ", c["iso2"], c["region"])
        row = conn.execute("SELECT id FROM geo_cities WHERE country_iso2=? AND name=?",
                           (c["iso2"], c["name"])).fetchone()
        if row is None:
            conn.execute("INSERT INTO geo_cities (name,region_id,country_iso2,active,lat,lng) VALUES (?,?,?,1,?,?)",
                         (c["name"], rid, c["iso2"], c["lat"], c["lng"]))
            row = conn.execute("SELECT id FROM geo_cities WHERE country_iso2=? AND name=?",
                               (c["iso2"], c["name"])).fetchone()
            n["city+"] += 1; print("[+city]   ", c["iso2"], c["region"], "/", c["name"])
        listed_ids.add(row[0])

    with_listings = {r[0] for r in conn.execute(
        "SELECT DISTINCT geo_city_id FROM listings WHERE geo_city_id IS NOT NULL")}
    keep = listed_ids | with_listings
    for cid, name, iso, active in conn.execute("SELECT id,name,country_iso2,active FROM geo_cities").fetchall():
        want = 1 if cid in keep else 0
        if want != active:
            conn.execute("UPDATE geo_cities SET active=? WHERE id=?", (want, cid))
            n["city_on" if want else "city_off"] += 1
            print("[%s] %s/%s%s" % ("show" if want else "hide", iso, name,
                                    " (has listings)" if want and cid not in listed_ids else ""))
    for rid, iso, active in conn.execute("SELECT id,country_iso2,active FROM geo_regions").fetchall():
        want = 1 if conn.execute("SELECT 1 FROM geo_cities WHERE region_id=? AND active=1 LIMIT 1", (rid,)).fetchone() else 0
        if want != active:
            conn.execute("UPDATE geo_regions SET active=? WHERE id=?", (want, rid)); n["region_on" if want else "region_off"] += 1
    for iso, active in conn.execute("SELECT iso2,active FROM geo_countries").fetchall():
        want = 1 if conn.execute("SELECT 1 FROM geo_cities WHERE country_iso2=? AND active=1 LIMIT 1", (iso,)).fetchone() else 0
        if want != active:
            conn.execute("UPDATE geo_countries SET active=? WHERE iso2=?", (want, iso)); n["country_on" if want else "country_off"] += 1
            print("[%s country] %s" % ("show" if want else "hide", iso))

    summary = " ".join("%s=%d" % kv for kv in n.items())
    if APPLY:
        conn.commit(); print("[applied]", summary)
    else:
        conn.rollback(); print("[dry-run]", summary, "-- re-run with --apply")
    vis = conn.execute("SELECT country_iso2, COUNT(*) FROM geo_cities WHERE active=1 GROUP BY 1 ORDER BY 1").fetchall()
    print("[visible]", ", ".join("%s:%d" % v for v in vis))
    conn.close()


if __name__ == "__main__":
    main()
