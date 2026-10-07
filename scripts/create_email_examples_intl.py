"""
create_email_examples_intl.py -- EMAIL-EXAMPLES-INTL-1 (David, 5 Oct 2026)
=========================================================================
David: "how do these emails work for the other than ZA email recipients? ... do they work as well as the ZA
emails with their links and advert demos?" PROBED: no. The example cards are South-Africa-only (rand prices,
Pretoria adverts), so every US / UK / Australian letter ended on an example heading with nothing under it.
Each of those countries had ONE showcase advert per category (Denver / London / Sydney supers) and none for
casual work. This adds two per category (three for casual work) in New York, London and Sydney, so each letter
can show three cards that open real adverts in the reader's own country and currency.

Also corrects the three existing car showcase adverts (287 / 292 / 297) whose car details were cloned from a
South African Hilux: a "Classic Mini" advert showed Toyota Hilux 2.8 GD-6 specifications.

Same rules as create_email_examples_2.py / create_stays_showcase_adverts.py: super_example=1 + showcase=1, cloned
from the SAME country's live exemplar of the same category, every other category's columns nulled, price_num
explicit, rate categories carry a basis, idempotent on seller+title, DB backup on --apply.
"""
import os, sys, json, shutil, sqlite3
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in ["/var/www/marketsquare/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found -- set MS_DB_PATH")
APPLY = "--apply" in sys.argv
SELLER = "showcase-email@trustsquare.co"
FOOT = " Showcase advert: AI imagery; free for a real seller to claim and replace with their own."
P = "/static/super/sup_email2_"
CITY = {"US": ("New York", 40.7128, -74.0060), "GB": ("London", 51.5074, -0.1278), "AU": ("Sydney", -33.8688, 151.2093)}
TPL = {"US": {"Tutors": 289, "Collectors": 290, "Services": 291, "Property": 288, "Cars": 287},
       "GB": {"Tutors": 294, "Collectors": 295, "Services": 296, "Property": 293, "Cars": 292},
       "AU": {"Tutors": 299, "Collectors": 300, "Services": 301, "Property": 298, "Cars": 297}}
CARS = {"make": None, "model": None, "variant": None, "vehicle_specs": None, "drivetrain": None, "colour": None}

def A(cat, title, price, pnum, photos, trust, extra, blurb):
    return (cat, title, price, pnum, [P + x for x in photos], trust, extra, blurb)

ADS = {
 "US": [
  A("Tutors", "English essays & SAT reading prep", "$65 / hour", 65, ["english_1.jpg"], 78, {"subject": "English", "level": "High school", "mode": "In-person or Online"}, "Essay structure, close reading and SAT reading technique, one student at a time."),
  A("Tutors", "Coding for teens · Python & JavaScript", "$60 / hour", 60, ["coding_1.jpg"], 71, {"subject": "Coding", "level": "Middle & high school", "mode": "In-person or Online"}, "From a first game to real Python and JavaScript projects students can show by week four."),
  A("Collectors", "Vintage wristwatch · 1960s automatic, serviced", "$1,950", 1950, ["watch_2.jpg"], 78, {"collectible_type": "Watches", "condition": "Excellent", "era_year": "1960s"}, "A sixties automatic, serviced last year and keeping good time. Original dial, honest case wear."),
  A("Collectors", "US stamp collection · commemoratives 1930–1970", "$640", 640, ["stamps_1.jpg", "stamps_2.jpg"], 71, {"collectible_type": "Stamps", "condition": "Very Good", "era_year": "1930-1970"}, "Two albums of mint and used commemoratives, mounted and annotated by one collector."),
  A("Services", "Licensed plumber · leaks, water heaters & drains", "$120 / call-out", 120, ["plumber_1.jpg"], 78, {"service_class": "Technical", "service_type": "Plumbing"}, "Leaks, water heater swaps and blocked drains, with a written quote before work starts."),
  A("Services", "Solar installer · panels, inverters & batteries", "$150 / site visit", 150, ["solar_1.jpg"], 71, {"service_class": "Technical", "service_type": "Solar"}, "Site visit, load calculation and a sized quote for panels, inverter and batteries."),
  A("Services", "House cleaner · weekly or one-off", "$160 / day", 160, ["cleaner_1.jpg"], 78, {"service_class": "Casuals", "service_type": "Cleaning"}, "Floors, kitchens, bathrooms and laundry -- weekly days or a one-off deep clean."),
  A("Services", "Gardener · mowing, beds & clean-up", "$35 / hour", 35, ["gardener_1.jpg"], 71, {"service_class": "Casuals", "service_type": "Gardening"}, "Lawns mowed and edged, beds weeded, leaves and green waste cleared."),
  A("Services", "Moving help · loading & carrying", "$30 / hour", 30, ["removals_1.jpg"], 66, {"service_class": "Casuals", "service_type": "Removals"}, "Careful hands for loading, carrying and packing on moving day."),
  A("Property", "Brownstone apartment · two bedrooms", "$865,000", 865000, ["flat_1.jpg"], 78, {"beds": 2, "baths": 1, "garages": 0, "prop_type": "Apartment", "floor_area": 95, "erf_size": None}, "Two bedrooms on the parlour floor of a brownstone: high ceilings, original mouldings, light on both sides."),
  A("Property", "Family townhouse · garden & garage", "$1,150,000", 1150000, ["townhouse_1.jpg"], 71, {"beds": 3, "baths": 2, "garages": 1, "prop_type": "Townhouse", "floor_area": 160, "erf_size": 210}, "Three bedrooms over three floors, a small walled garden and a garage -- a quiet street, ten minutes from the subway."),
  A("Cars", "Family SUV · 2019, one owner", "$21,400", 21400, ["suv_1.jpg"], 78, dict(CARS, vehicle_year=2019, mileage_km=72000, transmission="Automatic", fuel_type="Petrol", body_type="SUV"), "One owner, full service history, seven seats folded flat for weekends away."),
  A("Cars", "Compact hatchback · low mileage", "$11,900", 11900, ["hatch_1.jpg"], 71, dict(CARS, vehicle_year=2018, mileage_km=41000, transmission="Automatic", fuel_type="Petrol", body_type="Hatchback"), "Low mileage, tidy inside and out, cheap to run and easy to park."),
 ],
 "GB": [
  A("Tutors", "English & essay coaching · GCSE and A-Level", "£38 / hour", 38, ["english_1.jpg"], 78, {"subject": "English", "level": "GCSE & A-Level", "mode": "In-person or Online"}, "Essay structure, set texts and exam technique, one student at a time."),
  A("Tutors", "Coding for teens · Python & web", "£35 / hour", 35, ["coding_1.jpg"], 71, {"subject": "Coding", "level": "KS3 & KS4", "mode": "In-person or Online"}, "From a first game to real Python and web projects students can show by week four."),
  A("Collectors", "Vintage wristwatch · 1960s automatic, serviced", "£1,450", 1450, ["watch_2.jpg"], 78, {"collectible_type": "Watches", "condition": "Excellent", "era_year": "1960s"}, "A sixties automatic, serviced last year and keeping good time. Original dial, honest case wear."),
  A("Collectors", "GB stamp collection · definitives & commemoratives", "£480", 480, ["stamps_1.jpg", "stamps_2.jpg"], 71, {"collectible_type": "Stamps", "condition": "Very Good", "era_year": "1936-1980"}, "Two albums of mint and used British issues, mounted and annotated by one collector."),
  A("Services", "Gas Safe plumber · boilers, leaks & drains", "£95 / call-out", 95, ["plumber_1.jpg"], 78, {"service_class": "Technical", "service_type": "Plumbing"}, "Boiler faults, leaks and blocked drains, with a written quote before work starts."),
  A("Services", "Solar PV installer · panels & batteries", "£120 / site visit", 120, ["solar_1.jpg"], 71, {"service_class": "Technical", "service_type": "Solar"}, "Site survey, load calculation and a sized quote for panels, inverter and battery."),
  A("Services", "House cleaner · weekly or one-off", "£14 / hour", 14, ["cleaner_1.jpg"], 78, {"service_class": "Casuals", "service_type": "Cleaning"}, "Floors, kitchens, bathrooms and ironing -- weekly visits or a one-off deep clean."),
  A("Services", "Gardener · lawns, hedges & tidy-up", "£18 / hour", 18, ["gardener_1.jpg"], 71, {"service_class": "Casuals", "service_type": "Gardening"}, "Lawns mowed and edged, hedges trimmed, beds weeded and green waste cleared."),
  A("Services", "Moving help · loading & carrying", "£16 / hour", 16, ["removals_1.jpg"], 66, {"service_class": "Casuals", "service_type": "Removals"}, "Careful hands for loading, carrying and packing on moving day."),
  A("Property", "Victorian terrace · two bedrooms", "£485,000", 485000, ["townhouse_1.jpg"], 78, {"beds": 2, "baths": 1, "garages": 0, "prop_type": "Terrace", "floor_area": 85, "erf_size": 120}, "A two-bedroom Victorian terrace with a south-facing garden, ten minutes' walk from the station."),
  A("Property", "City flat · one bedroom, balcony", "£365,000", 365000, ["flat_1.jpg"], 71, {"beds": 1, "baths": 1, "garages": 0, "prop_type": "Flat", "floor_area": 52, "erf_size": None}, "A light one-bedroom flat with a balcony over the square; lift, concierge and secure bike store."),
  A("Cars", "Family estate · 2018, full history", "£9,450", 9450, ["suv_1.jpg"], 78, dict(CARS, vehicle_year=2018, mileage_km=88000, transmission="Manual", fuel_type="Diesel", body_type="Estate"), "Full service history, MOT to next summer, a boot that swallows a family holiday."),
  A("Cars", "Small hatchback · first car, low insurance", "£5,200", 5200, ["hatch_1.jpg"], 71, dict(CARS, vehicle_year=2016, mileage_km=54000, transmission="Manual", fuel_type="Petrol", body_type="Hatchback"), "Low insurance group, cheap to run, tidy inside and out -- an easy first car."),
 ],
 "AU": [
  A("Tutors", "English & HSC essay coaching", "A$70 / hour", 70, ["english_1.jpg"], 78, {"subject": "English", "level": "Years 9-12", "mode": "In-person or Online"}, "Essay structure, set texts and exam technique for the HSC, one student at a time."),
  A("Tutors", "Coding for teens · Python & Scratch", "A$65 / hour", 65, ["coding_1.jpg"], 71, {"subject": "Coding", "level": "Years 7-12", "mode": "In-person or Online"}, "From a first Scratch game to real Python projects students can show by week four."),
  A("Collectors", "Vintage wristwatch · 1960s automatic, serviced", "A$2,300", 2300, ["watch_2.jpg"], 78, {"collectible_type": "Watches", "condition": "Excellent", "era_year": "1960s"}, "A sixties automatic, serviced last year and keeping good time. Original dial, honest case wear."),
  A("Collectors", "Australian stamp collection · pre-decimal", "A$720", 720, ["stamps_1.jpg", "stamps_2.jpg"], 71, {"collectible_type": "Stamps", "condition": "Very Good", "era_year": "1913-1965"}, "Two albums of pre-decimal issues, mint and used, mounted and annotated by one collector."),
  A("Services", "Licensed plumber · leaks, hot water & drains", "A$140 / call-out", 140, ["plumber_1.jpg"], 78, {"service_class": "Technical", "service_type": "Plumbing"}, "Leaks, hot water systems and blocked drains, with a written quote before work starts."),
  A("Services", "Solar installer · panels & batteries", "A$180 / site visit", 180, ["solar_1.jpg"], 71, {"service_class": "Technical", "service_type": "Solar"}, "Site visit, load calculation and a sized quote for panels, inverter and battery."),
  A("Services", "House cleaner · weekly or one-off", "A$40 / hour", 40, ["cleaner_1.jpg"], 78, {"service_class": "Casuals", "service_type": "Cleaning"}, "Floors, kitchens, bathrooms and ironing -- weekly visits or a one-off deep clean."),
  A("Services", "Gardener · mowing, hedges & clean-up", "A$45 / hour", 45, ["gardener_1.jpg"], 71, {"service_class": "Casuals", "service_type": "Gardening"}, "Lawns mowed and edged, hedges trimmed, beds weeded and green waste cleared."),
  A("Services", "Moving help · loading & carrying", "A$42 / hour", 42, ["removals_1.jpg"], 66, {"service_class": "Casuals", "service_type": "Removals"}, "Careful hands for loading, carrying and packing on moving day."),
  A("Property", "Inner-west terrace · two bedrooms", "A$1,290,000", 1290000, ["townhouse_1.jpg"], 78, {"beds": 2, "baths": 1, "garages": 0, "prop_type": "Terrace", "floor_area": 110, "erf_size": 150}, "A two-bedroom terrace with a north-facing courtyard, a short walk to the light rail."),
  A("Property", "Harbour-side apartment · one bedroom", "A$865,000", 865000, ["flat_1.jpg"], 71, {"beds": 1, "baths": 1, "garages": 1, "prop_type": "Apartment", "floor_area": 58, "erf_size": None}, "A one-bedroom apartment with a balcony towards the water; lift, pool and secure parking."),
  A("Cars", "Family SUV · 2019, full service history", "A$28,500", 28500, ["suv_1.jpg"], 78, dict(CARS, vehicle_year=2019, mileage_km=76000, transmission="Automatic", fuel_type="Petrol", body_type="SUV"), "Full service history, seven seats, roof racks and a tow bar for the long weekends."),
  A("Cars", "Small hatch · low kms", "A$13,900", 13900, ["hatch_1.jpg"], 71, dict(CARS, vehicle_year=2018, mileage_km=46000, transmission="Automatic", fuel_type="Petrol", body_type="Hatchback"), "Low kilometres, tidy inside and out, cheap to run and easy to park."),
 ],
}
# The three existing car showcases carried a South African Hilux's details under other cars' titles.
CAR_FIX = {287: dict(CARS, vehicle_year=2018, mileage_km=98000, transmission="Automatic", fuel_type="Petrol", body_type="Pickup"),
           292: dict(CARS, vehicle_year=1990, mileage_km=58000, transmission="Manual", fuel_type="Petrol", body_type="Hatchback"),
           297: dict(CARS, vehicle_year=2017, mileage_km=142000, transmission="Manual", fuel_type="Diesel", body_type="Ute")}

JUNK = ["make", "model", "variant", "vehicle_year", "mileage_km", "transmission", "fuel_type", "body_type", "drivetrain",
        "colour", "vehicle_specs", "spec_confirmed", "attested_at", "attested_email", "beds", "baths", "garages", "prop_type",
        "floor_area", "erf_size", "scryfall_id", "collectible_type", "condition", "era_year", "ai_grade", "ai_grade_conf",
        "ai_grade_notes", "grade_tier", "subject", "level", "mode", "service_type", "service_class", "available_from",
        "linked_wonders", "nearby_pois", "ai_suggested_price", "import_source", "tour", "street_address", "boost_until",
        "suspension_reason", "block_cause", "expires_at", "warning_sent_at", "fade_nudge_sent_at", "numista_id",
        "numista_title", "numista_matched_at", "numista_matched_by", "ai_report_job", "ai_report_fn", "ai_report_at",
        "ai_range_text", "title_extra", "desc_extra", "extra_back", "extra_status", "search_en"]
conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
nullable = {r["name"] for r in conn.execute("PRAGMA table_info(listings)") if not r["notnull"]}
live = os.path.dirname(os.path.abspath(DB))
plan, existing = [], []
for cc, ads in ADS.items():
    city, lat, lng = CITY[cc]
    for k, (cat, title, price, pnum, photos, trust, extra, blurb) in enumerate(ads):
        tid = TPL[cc][cat]
        t = conn.execute("SELECT * FROM listings WHERE id=?", (tid,)).fetchone()
        if not t or t["category"] != cat:
            sys.exit("template %s missing or not %s -- aborting, nothing written" % (tid, cat))
        for ph in photos:
            if not os.path.exists(os.path.join(live, ph.lstrip("/"))):
                sys.exit("photo %s missing on this server -- aborting" % ph)
        hit = conn.execute("SELECT id FROM listings WHERE seller_email=? AND title=? AND city=?", (SELLER, title, city)).fetchone()
        if hit:
            existing.append((hit["id"], cc, title)); continue
        row = dict(t); row.pop("id", None)
        for c in JUNK:
            if c in row and c in nullable:
                row[c] = None
        row.update({"title": title, "price": price, "price_num": float(pnum), "category": cat, "city": city, "suburb": "",
                    "area": None if "area" in nullable else row.get("area"),
                    "description": "[photos:%s]%s%s" % ("|".join(photos), blurb, FOOT), "photo_urls": json.dumps(photos),
                    "thumb_url": photos[0], "medium_url": None,
                    "listing_lat": lat + (k % 5 - 2) * 0.012, "listing_lng": lng + (k % 3 - 1) * 0.015,
                    "super_example": 1, "showcase": 1, "trust_score": trust, "seller_email": SELLER, "claim_status": "claimed",
                    "created_at": now, "updated_at": now, "published_at": now, "view_count": 0, "listing_status": "live"})
        row.update({c: v for c, v in extra.items() if c in row})
        plan.append((row, cc, title))
print("PLAN: insert %d, already present %d; car fixes %d" % (len(plan), len(existing), len(CAR_FIX)))
for _id, cc, t in existing:
    print("SHOWCASE id=%s | %s | %s (existing)" % (_id, cc, t))
for row, cc, t in plan:
    print("  + %s %-10s %-18s | %s" % (cc, row["category"], row["price"], t))
if not APPLY:
    print("DRY-RUN only -- rerun with --apply."); sys.exit(0)
bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-examplesintl"
shutil.copy2(DB, bak); print("DB backed up -> " + bak)
for row, cc, t in plan:
    cols = list(row.keys())
    cur = conn.execute("INSERT INTO listings (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))), [row[c] for c in cols])
    print("SHOWCASE id=%s | %s | %s" % (cur.lastrowid, cc, t))
for lid, vals in CAR_FIX.items():
    sets = {c: v for c, v in vals.items() if c in nullable or v is not None}
    conn.execute("UPDATE listings SET %s WHERE id=? AND seller_email IS NOT NULL" % ",".join("%s=?" % c for c in sets), list(sets.values()) + [lid])
    print("CARFIX id=%s" % lid)
try:
    conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')")
except sqlite3.OperationalError:
    pass
conn.commit(); conn.close(); print("done.")
