"""
seed_super_global.py — SUPER-GLOBAL-2 (25 Jul 2026, David)
==========================================================
Creates the US / UK / AUS super_example exemplar listings by CLONING the existing
ZA super_example rows (one per category), so every column the app expects is filled
exactly like a working ZA exemplar. Country is NOT a listings column — the app derives
a listing's country from geo_cities (see _seller_country_for_listing in bea_main.py) —
so this script SEEDS a minimal geo hierarchy (country → region → city) for US/GB/AU and
points each new listing at that city via city + geo_city_id. That makes the country,
flag and currency resolve correctly (ms.js ADV_COUNTRY_FLAGS / ADV_COUNTRY_CURRENCY).

Per (country, category) it overrides: city, geo_city_id, title, price, price_num,
description (+[photos:] prefix), photo_urls, thumb_url/medium_url, suburb (cleared),
and resets location fields. Everything else (seller_email, category, super_example,
trust_score, flags) is inherited from the live ZA exemplar.

SAFE BY DESIGN:
  • Dry-run first. --apply backs up the DB, then writes.
  • Idempotent: skips any listing whose exact title already exists.
  • Photos discovered on disk by naming convention  sup_<cc>_<catkey>_<n>_<name>.jpg.
  • Only inserts columns that actually exist in the listings table.

Run ON THE SERVER:
    python3 seed_super_global.py            # dry-run, prints the full plan
    python3 seed_super_global.py --apply    # backs up DB, seeds geo, inserts

Optional env:
    MS_DB_PATH=/path/to/marketsquare.db
    MS_SUPER_ASSETS=/var/www/marketsquare/static/super
"""
import os, sys, re, json, glob, shutil, sqlite3
from datetime import datetime

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found — set MS_DB_PATH=/path/to/marketsquare.db")

ASSETS = os.getenv("MS_SUPER_ASSETS") or next((p for p in [
    "/var/www/marketsquare/static/super",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "super"),
    "assets/super"] if os.path.isdir(p)), None)
if not ASSETS:
    sys.exit("No super assets dir found — set MS_SUPER_ASSETS=/path/to/static/super")

APPLY = "--apply" in sys.argv
STATIC_PREFIX = "/static/super/"

# cc (filename code) -> (iso2, country name, city, region label, region name, lat, lng, currency)
COUNTRIES = [
    ("us", "US", "United States", "Denver", "State",  "Colorado", 39.7392, -104.9903, "$"),
    ("uk", "GB", "United Kingdom", "London", "County", "Greater London", 51.5074, -0.1278, "£"),
    ("au", "AU", "Australia",      "Sydney", "State",  "New South Wales", -33.8688, 151.2093, "A$"),
]
CAT_KEY = {
    "adventures_experiences":   "advexp",
    "adventures_accommodation": "advacc",
    "cars":       "cars",
    "property":   "property",
    "tutors":     "tutors",
    "local_market": "lm",
    "collectors": "collect",
    "services":   "svc",
}

# Localised copy per (cc, category): (title, price, blurb). AUD shown as A$.
COPY = {
 ("us","adventures_experiences"): ("Yellowstone Country Big-Game Safari — Guided Wildlife Drive","$180 / person","A full-day guided wildlife drive through world-famous geyser-and-wildlife country in Wyoming. Bison, elk, wolf, grizzly and moose from an open-sided touring truck, with a sundowner over the canyon."),
 ("us","adventures_accommodation"): ("The Great Lodge — Timber & Stone Retreat","$420 / night","A handcrafted timber-and-stone lodge on the lake. Fireside lounge, hot-spring deck, and dinner under the stars — the base camp for your wildlife days."),
 ("us","cars"): ("Silverline Full-Size Pickup — Clean, One Owner","$28,500","A clean, well-kept full-size pickup. Full service history, tidy leather cabin, tow-ready. Inspection welcome."),
 ("us","property"): ("Craftsman Family Home — Move-In Ready","$675,000","A handsome craftsman home with a covered porch, stone fireplace, island kitchen and a spacious backyard deck. Move-in ready."),
 ("us","tutors"): ("Math & Science Tutor — High School & College","$55 / hour","Experienced math and science tutor. Clear, patient, results-driven. In-home or online, high school through college."),
 ("us","local_market"): ("Sugar Hill Farm — Pure Maple Syrup & Preserves","$18","Small-batch pure maple syrup, maple cream and maple butter from the family sugarbush. Gift boxes available."),
 ("us","collectors"): ("American Gold Eagle — Graded Collector Coin","$3,200","A gleaming American Gold Eagle in graded holder. Full provenance. Serious collectors welcome — viewing by appointment."),
 ("us","services"): ("Licensed Electrician — Home Wiring & Panels","$120 / call-out","Licensed, insured electrician. Panels, wiring, safety inspections. Tidy work, no mess, guaranteed."),

 ("uk","adventures_experiences"): ("Stonehenge & Wessex Heritage Tour — Guided Day Out","£95 / person","A guided heritage day across the Wiltshire downs — the real Stonehenge and Avebury stone circles, a chalk white-horse, a deer park and a sundowner over the barrows, aboard a vintage open-top touring coach."),
 ("uk","adventures_accommodation"): ("The Country House — Georgian Manor Stay","£350 / night","A honey-stone Georgian country house. Fireside library, four-poster rooms, walled-garden dinners and misty mornings on the terrace."),
 ("uk","cars"): ("Classic Mini — Restored, British Racing Green","£12,750","A charming restored classic Mini in British racing green with a white roof. Tidy vintage interior, runs beautifully. A joy to own."),
 ("uk","property"): ("Period Stone Cottage — Character & Charm","£595,000","A handsome period English home of honey-coloured stone — beamed sitting room, range-cooker kitchen, brass-bed rooms and a classic English garden."),
 ("uk","tutors"): ("Maths & Science Tutor — GCSE & A-Level","£40 / hour","Experienced maths and science tutor. GCSE and A-Level, exam technique a speciality. In-home or online."),
 ("uk","local_market"): ("Farmhouse Cheese & Chutney — Artisan Selection","£9","Artisan farmhouse cheeses with homemade chutneys and preserves. Market boards and gift hampers to order."),
 ("uk","collectors"): ("Gold Sovereign — Antique Graded Coin","£1,850","An antique gold sovereign in graded holder, with loupe-ready detail and full provenance. Viewing by appointment."),
 ("uk","services"): ("Landscape Gardener — Design & Planting","£280 / day","Landscape gardener — design, planting, borders and lawns. Tidy, reliable, beautiful results. References available."),

 ("au","adventures_experiences"): ("Great Barrier Reef Dive & Snorkel — Guided Reef Day","A$160 / person","A guided day on the Great Barrier Reef aboard a reef dive catamaran — coral gardens, sea turtles, manta rays and a sandy cay, finishing with a sunset on the water. All levels."),
 ("au","adventures_accommodation"): ("Reef Island Eco-Lodge — Over-Water Villas","A$540 / night","A reef-island eco-lodge of over-water timber-and-thatch villas above a turquoise lagoon. Beach dinners, infinity pool and sunrise from your deck."),
 ("au","cars"): ("Workhorse Ute — Tidy, Full Service History","A$21,900","A clean, tidy ute with an open tray and full service history. Reliable workhorse, ready to go. Inspection welcome."),
 ("au","property"): ("Modern Coastal Home — Pool & Deck","A$1,150,000","A bright modern home with open-plan living, a stone-island kitchen, a sparkling pool and a sunny entertaining deck amid native planting."),
 ("au","tutors"): ("Maths & Science Tutor — High School & HSC","A$65 / hour","Experienced maths and science tutor. High school through HSC, exam prep a strength. In-home or online."),
 ("au","local_market"): ("Native Wildflower Honey & Macadamias — Bush Harvest","A$22","Golden native wildflower honey and fresh macadamias, small-batch and hand-labelled. Bush-food gift boxes available."),
 ("au","collectors"): ("Australian Opal & Gold Nugget — Collector Piece","A$1,400","A brilliant flashing Australian opal and gold nugget, in graded holders with full provenance. Viewing by appointment."),
 ("au","services"): ("Pool Care & Maintenance — Weekly Service","A$75 / visit","Reliable pool care — cleaning, water testing and balancing, equipment checks. Weekly or fortnightly. Sparkling results."),
}

def price_to_num(s):
    m = re.search(r"[0-9][0-9,\. ]*", s or "")
    if not m:
        return None
    digits = re.sub(r"[^0-9.]", "", m.group(0))
    try:
        return int(float(digits))
    except Exception:
        return None

def photos_for(cc, catkey):
    hits = glob.glob(os.path.join(ASSETS, f"sup_{cc}_{catkey}_*.jpg"))
    def idx(p):
        m = re.search(rf"sup_{cc}_{catkey}_(\d+)_", os.path.basename(p))
        return int(m.group(1)) if m else 999
    hits.sort(key=idx)
    return [STATIC_PREFIX + os.path.basename(p) for p in hits]

def ensure_geo_city(conn, iso2, cname, region_label, region_name, city, lat, lng):
    """Idempotently ensure country→region→city exist; return the city id."""
    conn.execute("INSERT OR IGNORE INTO geo_countries (iso2,name,region_label,active) VALUES (?,?,?,1)",
                 (iso2, cname, region_label))
    r = conn.execute("SELECT id FROM geo_regions WHERE name=? AND country_iso2=?",
                     (region_name, iso2)).fetchone()
    region_id = r["id"] if r else conn.execute(
        "INSERT INTO geo_regions (name,country_iso2,active) VALUES (?,?,1)",
        (region_name, iso2)).lastrowid
    c = conn.execute("SELECT id FROM geo_cities WHERE name=? AND country_iso2=?",
                     (city, iso2)).fetchone()
    if c:
        return c["id"]
    gcols = [x[1] for x in conn.execute("PRAGMA table_info(geo_cities)").fetchall()]
    if "lat" in gcols and "lng" in gcols:
        return conn.execute(
            "INSERT INTO geo_cities (name,region_id,country_iso2,lat,lng,active) VALUES (?,?,?,?,?,1)",
            (city, region_id, iso2, lat, lng)).lastrowid
    return conn.execute(
        "INSERT INTO geo_cities (name,region_id,country_iso2,active) VALUES (?,?,?,1)",
        (city, region_id, iso2)).lastrowid

# ── Build the plan ────────────────────────────────────────────────────────────
conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
has = {r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()}
if "super_example" not in has:
    sys.exit("No super_example column — wrong DB.")
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
RESET_NULL = ["listing_lat","listing_lng","street_address","nearby_pois","boost_until"]
RESET_ZERO = ["view_count"]

plan, skips, warns = [], [], []
for cc, iso2, cname, city, rlabel, rname, lat, lng, cur in COUNTRIES:
    for cat, catkey in CAT_KEY.items():
        photos = photos_for(cc, catkey)
        if not photos:
            warns.append(f"no photos for {cc}/{cat} (sup_{cc}_{catkey}_*.jpg) — skipped"); continue
        title, price, blurb = COPY.get((cc, cat), (None, None, None))
        if not title:
            warns.append(f"no copy for {cc}/{cat} — skipped"); continue
        if conn.execute("SELECT id FROM listings WHERE title=? LIMIT 1", (title,)).fetchone():
            skips.append(f"{iso2}/{cat}: '{title[:40]}...' already exists"); continue
        tmpl = conn.execute(
            "SELECT * FROM listings WHERE COALESCE(super_example,0)=1 AND category=? LIMIT 1",
            (cat,)).fetchone()
        if not tmpl:
            warns.append(f"no ZA template for category {cat} — skipped {iso2}"); continue
        row = dict(tmpl); row.pop("id", None)
        row.update({
            "city": city, "title": title, "price": price,
            "description": "[photos:" + "|".join(photos) + "]\n" + blurb,
            "photo_urls": json.dumps(photos),
        })
        if "suburb" in has: row["suburb"] = ""
        if "area" in has: row["area"] = ""
        if "price_num" in has: row["price_num"] = price_to_num(price)
        if "thumb_url" in has: row["thumb_url"] = photos[0]
        if "medium_url" in has: row["medium_url"] = photos[0]
        if "is_demo" in has: row["is_demo"] = 0
        if "listing_status" in has: row["listing_status"] = "live"
        if "suspension_reason" in has: row["suspension_reason"] = ""
        if "super_example" in has: row["super_example"] = 1
        for k in RESET_NULL:
            if k in has: row[k] = None
        for k in RESET_ZERO:
            if k in has: row[k] = 0
        for k in ("created_at","updated_at","published_at"):
            if k in has: row[k] = now
        row = {k: v for k, v in row.items() if k in has and k != "country"}
        plan.append((cc, iso2, cname, city, rlabel, rname, lat, lng, cat, title, price, len(photos), tmpl["id"], row))

# ── Report ────────────────────────────────────────────────────────────────────
print(f"DB     : {DB}")
print(f"ASSETS : {ASSETS}")
print(f"MODE   : {'APPLY' if APPLY else 'DRY-RUN'}")
geo_needed = sorted({(iso2, cname, city) for (cc,iso2,cname,city,*_rest) in plan})
print(f"GEO    : ensure {len(geo_needed)} city(s): " + ", ".join(f"{c} ({i})" for i,cn,c in geo_needed))
print(f"PLAN   : {len(plan)} new listings, {len(skips)} skipped (exist), {len(warns)} warnings\n")
for cc, iso2, cname, city, rlabel, rname, lat, lng, cat, title, price, nph, tid, _row in plan:
    print(f"  + {iso2:<3} {cat:<26} {nph} ph  {price:<16} {city:<8} | {title[:48]}  (clone ZA #{tid})")
for s in skips: print(f"  = SKIP {s}")
for w in warns: print(f"  ! WARN {w}")

if not APPLY:
    print("\nDRY-RUN only — rerun with --apply to seed geo + insert.")
    conn.close(); sys.exit(0)
if not plan:
    print("\nNothing to insert (all up to date)."); conn.close(); sys.exit(0)

bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-superglobal"
shutil.copy2(DB, bak); print(f"\nDB backed up -> {bak}")

# seed geo once per country, cache city ids
city_id = {}
for cc, iso2, cname, city, rlabel, rname, lat, lng, cat, title, price, nph, tid, row in plan:
    if iso2 not in city_id:
        city_id[iso2] = ensure_geo_city(conn, iso2, cname, rlabel, rname, city, lat, lng)
        print(f"  geo: {iso2} {city} -> geo_city_id {city_id[iso2]}")

ins = 0
for cc, iso2, cname, city, rlabel, rname, lat, lng, cat, title, price, nph, tid, row in plan:
    if "geo_city_id" in has:
        row["geo_city_id"] = city_id[iso2]
    cols = list(row.keys())
    conn.execute(f"INSERT INTO listings ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                 [row[c] for c in cols])
    ins += 1
conn.commit()
print(f"Inserted {ins} listings.")
try:
    conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')"); conn.commit()
    print("FTS rebuilt.")
except Exception as e:
    print("FTS rebuild skipped:", e)
print("APPLIED. Adventures appear pinned in the feed; refresh (purge CDN cache if edge-cached).")
conn.close()
