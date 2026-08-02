#!/usr/bin/env python3
"""002_fix_showcase_clone_fields.py — EMAIL-SHOWCASE-2 (2 Aug 2026, David's screenshots).
The six live showcase adverts (315-320, created 28 Jul by row-cloning exemplars) kept the
TEMPLATE'S structured fields: the AMG C63 and the '66 250SE showed Make: Toyota Hilux,
Diesel, 2 755 cc; the vacant stand showed 4 beds / 280 m2 house; every price_num was the
template's (breaking price sort/filters); all six carried super_example=1 (against the
recorded not-super design, so the pinned exemplar rows grew), a false seller-attestation
stamp and auto-linked heritage wonders. This one-time migration sets every field to match
what each advert actually says. Idempotent: plain UPDATEs keyed by id+seller sanity check.
"""
import json, os, sqlite3, sys

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found")
APPLY = "--apply" in sys.argv

COMMON = {"super_example": 0, "linked_wonders": None, "spec_confirmed": None,
          "attested_at": None, "attested_email": None, "nearby_pois": None}
def vs(cc, kw, hist, rw="Valid roadworthy"):
    return json.dumps({"engine_capacity_cc": cc, "kilowatts_kw": kw,
                       "service_history": hist, "roadworthy_status": rw})

FIX = {
 315: dict(COMMON, price_num=1650000.0, seller_like="prop-showcase%", prop_type="Vacant Land",
           beds=None, baths=None, garages=None, floor_area=None, erf_size=920),
 316: dict(COMMON, price_num=4250000.0, seller_like="prop-showcase%"),   # 4-bed/3-bath house fields are right for this one
 317: dict(COMMON, price_num=3100000.0, seller_like="prop-showcase%", prop_type="Apartment",
           beds=3, baths=2, garages=2, erf_size=None, floor_area=210),
 318: dict(COMMON, price_num=1450000.0, seller_like="cars-showcase%", make="Mercedes-AMG",
           model="C63 S", variant="4.0 V8 Biturbo Saloon", vehicle_year=2021, mileage_km=42000,
           transmission="Automatic", fuel_type="Petrol", body_type="Saloon", colour="White",
           vehicle_specs=vs(3982, 375, "Full agent history")),
 319: dict(COMMON, price_num=1100000.0, seller_like="cars-showcase%", make="Toyota",
           model="Land Cruiser 79", variant="4.5 V8 Double Cab", vehicle_year=2020, mileage_km=68000,
           transmission="Manual", fuel_type="Diesel", body_type="Double cab", colour="White",
           vehicle_specs=vs(4498, 151, "Service book stamped to date")),
 320: dict(COMMON, price_num=345000.0, seller_like="cars-showcase%", make="Mercedes-Benz",
           model="250SE (W108)", variant="2.5 straight-six", vehicle_year=1966, mileage_km=89000,
           transmission="Automatic", fuel_type="Petrol", body_type="Saloon", colour="Silver-blue",
           vehicle_specs=vs(2496, 110, "Restoration file on hand")),
}

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
changed = 0
for lid, f in FIX.items():
    like = f.pop("seller_like")
    row = conn.execute("SELECT id, seller_email, title FROM listings WHERE id=?", (lid,)).fetchone()
    if not row:
        print(f"[skip] listing {lid} not found"); continue
    if like.rstrip("%") not in str(row["seller_email"]):
        print(f"[skip] listing {lid} seller {row['seller_email']!r} unexpected — refusing to touch"); continue
    sets = ", ".join(f"{k}=?" for k in f)
    print(f"[{'APPLY' if APPLY else 'dry'}] {lid} {row['title'][:45]} -> {len(f)} fields")
    if APPLY:
        conn.execute(f"UPDATE listings SET {sets} WHERE id=?", list(f.values()) + [lid]); changed += 1
if APPLY:
    try: conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')")
    except sqlite3.OperationalError: pass
    conn.commit(); print(f"done — {changed} listings healed")
else:
    print("dry-run; post_deploy runs me with --apply")
conn.close()
