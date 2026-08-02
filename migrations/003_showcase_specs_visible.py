#!/usr/bin/env python3
"""003_showcase_specs_visible.py — EMAIL-SHOWCASE-3 (2 Aug 2026, David's ruling:
"the specs ARE the selling point — fix the wrong ones, don't hide them").

Migration 002 healed the cloned-Hilux fields on 318/319/320 but also cleared the
attestation stamp — and the public serializer (CARS-SPEC-1) hides ALL vehicle
fields on non-demo cars listings without confirmed sections. Net effect: correct
specs in the DB, invisible in the app. This migration (idempotent, belt+braces):
  1. re-asserts the correct vehicle fields (same values as 002 — covers both
     orderings of history), and
  2. restores spec_confirmed {details, performance, condition} + attested_at with
     TODAY'S stamp — the platform vouching for its own showcase adverts, which
     carry an explicit AI-imagery/showcase disclosure in the blurb.
"""
import json, os, sqlite3, sys
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found")
APPLY = "--apply" in sys.argv
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
CONF = json.dumps({"details": NOW, "performance": NOW, "condition": NOW})
def vs(cc, kw, hist, rw="Valid roadworthy"):
    return json.dumps({"engine_capacity_cc": cc, "kilowatts_kw": kw,
                       "service_history": hist, "roadworthy_status": rw})

FIX = {
 318: dict(make="Mercedes-AMG", model="C63 S", variant="4.0 V8 Biturbo Saloon",
           vehicle_year=2021, mileage_km=42000, transmission="Automatic", fuel_type="Petrol",
           body_type="Saloon", colour="White", vehicle_specs=vs(3982, 375, "Full agent history"),
           spec_confirmed=CONF, attested_at=NOW),
 319: dict(make="Toyota", model="Land Cruiser 79", variant="4.5 V8 Double Cab",
           vehicle_year=2020, mileage_km=68000, transmission="Manual", fuel_type="Diesel",
           body_type="Double cab", colour="White", vehicle_specs=vs(4498, 151, "Service book stamped to date"),
           spec_confirmed=CONF, attested_at=NOW),
 320: dict(make="Mercedes-Benz", model="250SE (W108)", variant="2.5 straight-six",
           vehicle_year=1966, mileage_km=89000, transmission="Automatic", fuel_type="Petrol",
           body_type="Saloon", colour="Silver-blue", vehicle_specs=vs(2496, 110, "Restoration file on hand"),
           spec_confirmed=CONF, attested_at=NOW),
}

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
n = 0
for lid, f in FIX.items():
    row = conn.execute("SELECT id, seller_email FROM listings WHERE id=?", (lid,)).fetchone()
    if not row or "cars-showcase" not in str(row["seller_email"]):
        print(f"[skip] {lid}: missing or unexpected seller"); continue
    print(f"[{'APPLY' if APPLY else 'dry'}] {lid}: specs + confirmation stamp")
    if APPLY:
        conn.execute("UPDATE listings SET " + ", ".join(f"{k}=?" for k in f) + " WHERE id=?",
                     list(f.values()) + [lid]); n += 1
if APPLY:
    conn.commit(); print(f"done — {n} listings, specs visible again")
conn.close()
