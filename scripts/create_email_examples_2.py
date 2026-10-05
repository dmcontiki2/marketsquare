"""
create_email_examples_2.py -- EMAIL-EXAMPLES-2 (David, 5 Oct 2026)
==================================================================
David, in the Email Templates view: "the three examples don't open up ... the links that work are where we do
have examples? Should we perhaps then at least generate examples as per these emails?"

PROBED: only five letters' phone cards opened a real advert (property 315-317, cars 318-320, experiences
321-323, stays 336-338, travel 304/306/308). The collectors, tutors, services-technical, services-casual
letters (and their dealer / institution / company versions) showed three cards that opened nothing, with
stock photos that did not match the card text. This creates the missing adverts so every card opens the exact
advert it shows. Each trio = one existing super example (269 / 266 / 267 / 268, already live with a gallery)
+ two new adverts below, on our own Quick pictures (assets/super/sup_email2_*.jpg, served at /static/super/).

Same rules as create_stays_showcase_adverts.py (read its header -- every rule there was learned the hard way):
super_example=1 + showcase=1 (star banner, never pinned), cloned from a live exemplar of the SAME category
then every other category's columns nulled, price_num explicit, rate categories carry a price basis,
seller showcase-email@trustsquare.co, idempotent on seller+title, DB backed up on --apply, prints
"SHOWCASE id=<id> | <title>" for every advert.

Run ON THE SERVER (post_deploy runs it via migrations/065_email_examples_2.py with --apply).
"""
import os, sys, json, shutil, sqlite3
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found -- set MS_DB_PATH=/path/to/marketsquare.db")
APPLY = "--apply" in sys.argv
SELLER = "showcase-email@trustsquare.co"
FOOT = " Showcase advert: AI imagery; free for a real seller to claim and replace with their own."
P = "/static/super/sup_email2_"

# (template_id, category, title, price, price_num, suburb, photos, lat, lng, trust, extra-columns, blurb)
ADVERTS = [
 (269, "Collectors", "Vintage Omega Seamaster · 1960s, serviced", "R 18 500", 18500.0, "Waterkloof",
  [P + "watch_1.jpg", P + "watch_2.jpg"], -25.7790, 28.2430, 78,
  {"collectible_type": "Watches", "condition": "Excellent", "era_year": "1960s"},
  "An automatic Seamaster from the sixties, serviced last year, keeping good time on the wrist. "
  "Original dial, honest case wear, papers from the service."),
 (269, "Collectors", "Union of SA stamp collection · 1910–1961", "R 4 200", 4200.0, "Pretoria Central",
  [P + "stamps_1.jpg", P + "stamps_2.jpg"], -25.7470, 28.1880, 71,
  {"collectible_type": "Stamps", "condition": "Very Good", "era_year": "1910-1961"},
  "Two albums of Union-period stamps, mint and used, mounted and annotated by one collector over thirty years."),
 (266, "Tutors", "English Home Language · Grade 8–12", "R 300 / hour", 300.0, "Hatfield",
  [P + "english_1.jpg"], -25.7480, 28.2370, 71,
  {"subject": "English", "level": "Grade 8-12", "mode": "In-person or Online"},
  "Essay structure, literature set works and exam technique, one learner at a time."),
 (266, "Tutors", "Coding for teens · Python & Scratch", "R 350 / hour", 350.0, "Lynnwood",
  [P + "coding_1.jpg"], -25.7660, 28.2770, 66,
  {"subject": "Coding", "level": "Grade 7-12", "mode": "In-person or Online"},
  "From the first Scratch game to real Python projects -- learners build something they can show by week four."),
 (267, "Services", "Plumber · leaks, geysers & blocked drains", "R 550 / call-out", 550.0, "Centurion",
  [P + "plumber_1.jpg"], -25.8600, 28.1890, 78,
  {"service_class": "Technical", "service_type": "Plumbing"},
  "Burst pipes, geyser replacements and blocked drains, with a written quote before any work starts."),
 (267, "Services", "Solar PV installer · inverters & batteries", "R 950 / site visit", 950.0, "Faerie Glen",
  [P + "solar_1.jpg"], -25.7860, 28.2960, 71,
  {"service_class": "Technical", "service_type": "Solar"},
  "Site visit, load calculation and a sized quote for panels, inverter and batteries; installation signed off with a CoC."),
 (268, "Services", "Home cleaner · weekly or once-off", "R 350 / day", 350.0, "Mamelodi",
  [P + "cleaner_1.jpg"], -25.7200, 28.3950, 78,
  {"service_class": "Casuals", "service_type": "Cleaning"},
  "Floors, kitchens, bathrooms and ironing -- weekly days or a once-off deep clean."),
 (268, "Services", "Moving help · loading & carrying", "R 140 / hour", 140.0, "Pretoria East",
  [P + "removals_1.jpg"], -25.7900, 28.3000, 71,
  {"service_class": "Casuals", "service_type": "Removals"},
  "Two careful hands for loading, carrying and packing on moving day; furniture wrapped, nothing dragged."),
]

CLONE_JUNK = [
    "make", "model", "variant", "vehicle_year", "mileage_km", "transmission", "fuel_type", "body_type",
    "drivetrain", "colour", "vehicle_specs", "spec_confirmed", "attested_at", "attested_email",
    "beds", "baths", "garages", "prop_type", "floor_area", "erf_size",
    "scryfall_id", "collectible_type", "condition", "era_year", "ai_grade", "ai_grade_conf", "ai_grade_notes", "grade_tier",
    "subject", "level", "mode", "service_type", "service_class",
    "rental_status", "available_from", "linked_wonders", "nearby_pois", "ai_suggested_price", "import_source", "tour",
    "street_address", "boost_until", "suspension_reason", "block_cause", "expires_at", "warning_sent_at", "fade_nudge_sent_at",
]

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
nullable = {r["name"] for r in conn.execute("PRAGMA table_info(listings)") if not r["notnull"]}
live_dir = os.path.dirname(os.path.abspath(DB))
plan, existing = [], []
for tid, cat, title, price, pnum, suburb, photos, lat, lng, trust, extra, blurb in ADVERTS:
    tmpl = conn.execute("SELECT * FROM listings WHERE id=?", (tid,)).fetchone()
    if not tmpl or str(tmpl["category"]) != cat:
        sys.exit("template %s missing or not %s -- aborting, nothing written" % (tid, cat))
    if cat == "Services" and str(tmpl["service_class"] or "") != extra["service_class"]:
        sys.exit("template %s is service_class %s, expected %s -- aborting" % (tid, tmpl["service_class"], extra["service_class"]))
    for ph in photos:   # refuse to publish an advert whose picture is not on this box
        if not os.path.exists(os.path.join(live_dir, ph.lstrip("/"))):
            sys.exit("photo %s missing on this server -- aborting, nothing written" % ph)
    hit = conn.execute("SELECT id FROM listings WHERE seller_email=? AND title=?", (SELLER, title)).fetchone()
    if hit:
        existing.append((hit["id"], title)); continue
    row = dict(tmpl); row.pop("id", None)
    for col in CLONE_JUNK:
        if col in row and col in nullable:
            row[col] = None
    row.update({
        "title": title, "price": price, "price_num": pnum, "suburb": suburb, "category": cat, "city": "Pretoria",
        "description": "[photos:%s]%s%s" % ("|".join(photos), blurb, FOOT),
        "photo_urls": json.dumps(photos), "thumb_url": photos[0], "medium_url": None,
        "listing_lat": lat, "listing_lng": lng, "super_example": 1, "showcase": 1, "trust_score": trust,
        "seller_email": SELLER, "claim_status": "claimed", "created_at": now, "updated_at": now,
        "published_at": now, "view_count": 0, "listing_status": "live",
    })
    row.update({k: v for k, v in extra.items() if k in row})
    plan.append((row, title))

print("PLAN: insert %d, already present %d" % (len(plan), len(existing)))
for _id, t in existing:
    print("SHOWCASE id=%s | %s (existing)" % (_id, t))
for row, t in plan:
    print("  + %-12s %-18s | %s" % (row["category"], row["price"], t))
if not APPLY:
    print("DRY-RUN only -- rerun with --apply."); sys.exit(0)
if plan:
    bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-emailexamples2"
    shutil.copy2(DB, bak); print("DB backed up -> " + bak)
    for row, t in plan:
        cols = list(row.keys())
        cur = conn.execute("INSERT INTO listings (%s) VALUES (%s)" % (",".join(cols), ",".join("?" * len(cols))),
                           [row[c] for c in cols])
        print("SHOWCASE id=%s | %s" % (cur.lastrowid, t))
    try:
        conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')")
    except sqlite3.OperationalError:
        pass
    conn.commit()
print("done.")
conn.close()
