"""
seed_super_ladder_global.py — SUPER-AFRICA-1 (10 Aug 2026, David)
=================================================================
Seeds THREE super_example listings per (country, category) — an a/b/c trust
ladder (entry / established / top-of-field), each tier with its own persona
seller, evidence-true credential set and researched real-market price.

KENYA (Nairobi) is the pilot. The other six SUPER-AFRICA-1 countries (ZW, AO,
EG + extending NA/MZ/BW beyond adventures) are added by extending COUNTRIES
and TIERS below — nothing else changes.

Reuses the proven machinery:
  • Clone-a-live-ZA-exemplar pattern from seed_super_global.py (every column
    the app expects arrives filled), geo seeding included.
  • Persona pattern from supers_ladder_seed.py (real users rows +
    user_credentials, so Trust Score is COMPUTED, never painted).

IMPORTANT — do NOT add these cc codes to seed_super_global.py COUNTRIES:
its photo glob (sup_<cc>_<catkey>_<digit>_*) would swallow all three tiers'
photos as one listing. Ladder photos use  sup_<cc>_<catkey>_<tier>_<n>_<name>.jpg
with tier in {a,b,c}.

Trust targets: cars & property tiers use the ZA-proven signal sets (exact
arithmetic per _trust_math: 40 base + universal 20 (ID+profile) + category).
Other categories' b/c targets are stored estimates from the signal catalog;
the server-side recompute on first profile view is authoritative (same as
supers_ladder_seed) — confirm with diag at deploy (SUPER-TRUST-1).

SAFE BY DESIGN: dry-run default; --apply backs up the DB first; idempotent
(skips existing titles; INSERT OR IGNORE users; upsert credentials).

Run ON THE SERVER:
    python3 seed_super_ladder_global.py            # dry-run
    python3 seed_super_ladder_global.py --apply    # backup + write
Optional env: MS_DB_PATH, MS_SUPER_ASSETS
"""
import os, sys, re, json, glob, shutil, sqlite3
from datetime import datetime, timezone

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
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

# cc -> (iso2, country name, city, region label, region name, lat, lng, currency)
COUNTRIES = [
    ("ke", "KE", "Kenya", "Nairobi", "County", "Nairobi County", -1.2864, 36.8172, "KSh"),
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
CAT_SPECIFIC_COLS = [
    "beds","baths","garages","prop_type","floor_area","erf_size","listing_type",
    "subject","level","mode","service_type","availability",
    "collectible_type","condition","era_year","ai_grade","ai_grade_conf","ai_grade_notes","grade_tier",
    "make","model","variant","vehicle_year","mileage_km","transmission","fuel_type","body_type","drivetrain","colour",
    "environment_type","per",
]

# ── The ladder: per (cc, category) -> three tiers ────────────────────────────
# tier: (code, title, price, blurb, persona_email, persona_name,
#        earned_signals[], pending_signals[], target_trust)
# Prices researched 10 Aug 2026 (Jiji.co.ke, BuyRentKenya, safari operators,
# theteacher.co.ke, Nairobi cleaning/photography rate cards; USD/KES ~129).
# SO-1: no real business names; SO-1b: public heritage accurate, private generic.
TIERS = {
 ("ke","adventures_experiences"): [
  ("a","Naivasha & Hell's Gate Day Escape — Lake Boat & Gorge Walk","KSh 8,500 / person",
   "A full day out of Nairobi — down the Great Rift escarpment, a boat among hippos and fish eagles on Lake Naivasha, then cycling beneath the red basalt cliffs of Hell's Gate. Park fees, boat and guide included. Karibu!",
   "advexp-nairobi-a@trustsquare.co","Showcase Safaris A",[],[],60),
  ("b","Nairobi National Park Private Game Drive — Dawn Safari","KSh 22,000 / person",
   "Lion, rhino and giraffe against a city skyline — the world's only national park inside a capital. A private open-sided cruiser at dawn, park fees included, breakfast on the plains to finish.",
   "advexp-nairobi-b@trustsquare.co","Showcase Safaris B",
   ["category.adv_exp.permit","category.adv_exp.first_aid","category.adv_exp.exp_3_7"],[],80),
  ("c","Maasai Mara Safari — 3-Day Big Cat & Migration Package","KSh 85,000 / person",
   "Three days in the Maasai Mara — big cats at first light, the great herds on the move, sundowners over the Oloololo escarpment and nights in a tented camp under the stars. Guiding, park fees, full board and Nairobi transfers included.",
   "advexp-nairobi-c@trustsquare.co","Showcase Safaris C",
   ["category.adv_exp.guide_cert","category.adv_exp.permit","category.adv_exp.first_aid",
    "category.adv_exp.insurance","category.adv_exp.safety_cert","category.adv_exp.exp_7plus"],[],92),
 ],
 ("ke","adventures_accommodation"): [
  ("a","Garden Guesthouse Near the Park Gate — B&B","KSh 3,500 / night",
   "A quiet garden guesthouse minutes from the park gate — netted beds, hot showers, strong Kenyan chai at sunrise and a packed breakfast for early game drives. Karibu.",
   "advacc-nairobi-a@trustsquare.co","Showcase Stays A",[],[],60),
  ("b","Coffee-Garden Boutique Lodge — Karen","KSh 18,000 / night",
   "A boutique lodge in Karen's green coffee country — verandah rooms under old trees, log fires at night, birdsong at breakfast and giraffe country on your doorstep.",
   "advacc-nairobi-b@trustsquare.co","Showcase Stays B",
   ["category.adv_acc.licence","category.adv_acc.health_safety"],[],80),
  ("c","Safari Tented Suite — Mara River Frontage","KSh 60,000 / night",
   "A canvas-and-timber suite above the Mara river — claw-foot tub, private deck with hippos below, lamplit dinners under the stars and the migration passing in season.",
   "advacc-nairobi-c@trustsquare.co","Showcase Stays C",
   ["category.adv_acc.licence","category.adv_acc.health_safety","category.adv_acc.fire",
    "category.adv_acc.tgcsa_4","category.adv_acc.award"],[],92),
 ],
 ("ke","cars"): [
  ("a","Toyota Vitz — Clean City Runner, Low Mileage","KSh 550,000",
   "A tidy, economical city runabout — fresh import, low mileage, cold aircon, sips fuel. Ideal first car or daily commuter. Bei poa — inspection welcome.",
   "cars-nairobi-a@trustsquare.co","Showcase Motors KE A",[],[],60),
  ("b","Subaru Forester — One Owner, Full Service History","KSh 2,800,000",
   "A clean Forester with full service history — all-wheel drive for upcountry roads, tow bar fitted, new tyres. Sawa sawa condition; test drives welcome.",
   "cars-nairobi-b@trustsquare.co","Showcase Motors KE B",
   ["category.cars.ownership","category.cars.rwc","category.cars.service_history"],[],80),
  ("c","Toyota Land Cruiser Prado — Immaculate, Safari Ready","KSh 7,500,000",
   "An immaculate Prado — leather cabin, low mileage, dealer-maintained, ready for the Mara or the school run. Full inspection file on hand; serious buyers welcome.",
   "cars-nairobi-c@trustsquare.co","Showcase Motors KE C",
   ["category.cars.dealer_reg","category.cars.ownership","category.cars.rwc",
    "category.cars.service_history","category.cars.finance_clear"],[],92),
 ],
 ("ke","property"): [
  ("a","2-Bed Apartment — Kilimani, Modern Finish","KSh 11,000,000",
   "A bright two-bed in Kilimani — open-plan living, fitted kitchen, secure parking, borehole and backup power. Walk to cafés and the mall. First-time buyers welcome.",
   "prop-nairobi-a@trustsquare.co","Showcase Estates KE A",[],[],60),
  ("b","3-Bed Townhouse — Gated Community, Garden","KSh 35,000,000",
   "A family townhouse in a leafy gated court — three beds, a sunny garden, staff quarters, clubhouse and pool, minutes from international schools.",
   "prop-nairobi-b@trustsquare.co","Showcase Estates KE B",
   ["category.property.ppra","category.property.nqf4"],["category.property.ffc"],81),
  ("c","Villa on an Acre — Karen, Mature Gardens","KSh 120,000,000",
   "A gracious villa on a landscaped acre in Karen — deep verandahs, fireplaces, staff cottages, and giraffe country at the end of the road.",
   "prop-nairobi-c@trustsquare.co","Showcase Estates KE C",
   ["category.property.ppra","category.property.ffc","category.property.nqf4",
    "category.property.body"],[],96),
 ],
 ("ke","tutors"): [
  ("a","Primary & High School Homework Coach","KSh 700 / session",
   "Patient, reliable after-school coaching — homework, revision and confidence, at your home or online. Asante notes from happy parents available.",
   "tutors-nairobi-a@trustsquare.co","Showcase Tutors A",[],[],60),
  ("b","Maths & Sciences Tutor — High School","KSh 1,200 / hour",
   "Experienced maths, physics and chemistry tutor — clear methods, steady results, exam technique a specialty. In-home across Nairobi or online.",
   "tutors-nairobi-b@trustsquare.co","Showcase Tutors B",
   ["category.tutors.clearance","category.tutors.bachelor","category.tutors.strong_cv"],[],80),
  ("c","KCSE & IGCSE Exam Specialist — Proven Results","KSh 2,500 / hour",
   "A specialist exam coach — KCSE and IGCSE syllabuses, past-paper mastery, structured study plans and mock marking. Limited places each term.",
   "tutors-nairobi-c@trustsquare.co","Showcase Tutors C",
   ["category.tutors.clearance","category.tutors.honours","category.tutors.specialisation",
    "category.tutors.exp_2_5"],[],92),
 ],
 ("ke","local_market"): [
  ("a","Maasai Beadwork — Handmade Bracelets & Necklaces","KSh 350",
   "Hand-strung Maasai beadwork in traditional colours — every pattern with a meaning. Made by hand, bought fairly. Karibu!",
   "lm-nairobi-a@trustsquare.co","Showcase Makers A",[],[],60),
  ("b","Kiondo Baskets — Woven Sisal & Leather","KSh 1,000",
   "Genuine hand-woven kiondo baskets — sisal and leather-trimmed, in market and gift sizes. Strong enough for market day, beautiful enough for a shelf.",
   "lm-nairobi-b@trustsquare.co","Showcase Makers B",
   ["category.lm.phone_verified","category.lm.banking","category.lm.formal_cert",
    "category.lm.experience_1yr"],[],80),
  ("c","Fresh Farm Basket — Weekly Family Box","KSh 2,500",
   "A weekly family box from the farm — sukuma wiki, tomatoes, bananas, avocado and herbs, picked at dawn and delivered fresh. Harambee — from our shamba to your table.",
   "lm-nairobi-c@trustsquare.co","Showcase Makers C",
   ["category.lm.assoc_role","category.lm.formal_cert","category.lm.formal_cert_2",
    "category.lm.experience_5yr","category.lm.media_feature"],[],92),
 ],
 ("ke","collectors"): [
  ("a","East African Vinyl — Classic Benga & Rumba LPs","KSh 800",
   "Classic benga and rumba LPs from the golden decades — sleeves honest, vinyl cleaned and play-graded. Start your collection here.",
   "collect-nairobi-a@trustsquare.co","Showcase Collectors A",[],[],60),
  ("b","Hand-Carved Ebony Sculpture — Master Carver","KSh 3,000",
   "A hand-carved ebony piece with real weight and grain — master-carver work, oiled and finished. Certificate of origin included.",
   "collect-nairobi-b@trustsquare.co","Showcase Collectors B",
   ["category.collectors.specialisation","category.collectors.provenance",
    "category.collectors.tx_1_4"],[],80),
  ("c","Kenyatta-Era Coin & Stamp Collection — Graded","KSh 15,000",
   "A curated Kenyatta-era coin and first-issue stamp collection — graded, sleeved and catalogued, with provenance notes. Viewing by appointment.",
   "collect-nairobi-c@trustsquare.co","Showcase Collectors C",
   ["category.collectors.auth_cert","category.collectors.appraisal","category.collectors.assoc",
    "category.collectors.provenance","category.collectors.dealer_reg"],[],92),
 ],
 ("ke","services"): [
  ("a","Licensed Electrician — Callouts & Repairs","KSh 2,000 / call-out",
   "Licensed electrician for homes and offices — faults, sockets, lighting, wiring. Fair callout, deducted from the job. Tidy work, sawa sawa guaranteed.",
   "svc-nairobi-a@trustsquare.co","Showcase Services A",[],[],60),
  ("b","Professional Deep Cleaning — Homes & Apartments","KSh 6,000 / clean",
   "A professional team-clean for your home — kitchens degreased, bathrooms sparkling, floors and windows done properly. Weekly or one-off, supplies included.",
   "svc-nairobi-b@trustsquare.co","Showcase Services B",
   ["category.services_tech.trade_cert","category.services_tech.coc",
    "category.services_tech.insurance","category.services_tech.strong_cv"],[],80),
  ("c","Event Photography Studio — Weddings & Corporate","KSh 75,000 / event",
   "Full-day event photography — two shooters, same-week edited gallery, album options. Weddings, corporate and gala coverage across Nairobi. Portfolio on request.",
   "svc-nairobi-c@trustsquare.co","Showcase Services C",
   ["category.services_tech.body_reg","category.services_tech.trade_cert",
    "category.services_tech.insurance","category.services_tech.coc",
    "category.services_tech.exp_3_7"],[],94),
 ],
}

def price_to_num(s):
    m = re.search(r"[0-9][0-9,\. ]*", s or "")
    if not m: return None
    digits = re.sub(r"[^0-9.]", "", m.group(0))
    try: return int(float(digits))
    except Exception: return None

def photos_for(cc, catkey, tier):
    hits = glob.glob(os.path.join(ASSETS, f"sup_{cc}_{catkey}_{tier}_*.jpg"))
    def idx(p):
        m = re.search(rf"sup_{cc}_{catkey}_{tier}_(\d+)_", os.path.basename(p))
        return int(m.group(1)) if m else 999
    hits.sort(key=idx)
    return [STATIC_PREFIX + os.path.basename(p) for p in hits]

def ensure_geo_city(conn, iso2, cname, region_label, region_name, city, lat, lng):
    conn.execute("INSERT OR IGNORE INTO geo_countries (iso2,name,region_label,active) VALUES (?,?,?,1)",
                 (iso2, cname, region_label))
    r = conn.execute("SELECT id FROM geo_regions WHERE name=? AND country_iso2=?",
                     (region_name, iso2)).fetchone()
    region_id = r["id"] if r else conn.execute(
        "INSERT INTO geo_regions (name,country_iso2,active) VALUES (?,?,1)",
        (region_name, iso2)).lastrowid
    c = conn.execute("SELECT id FROM geo_cities WHERE name=? AND country_iso2=?",
                     (city, iso2)).fetchone()
    if c: return c["id"]
    gcols = [x[1] for x in conn.execute("PRAGMA table_info(geo_cities)").fetchall()]
    if "lat" in gcols and "lng" in gcols:
        return conn.execute(
            "INSERT INTO geo_cities (name,region_id,country_iso2,lat,lng,active) VALUES (?,?,?,?,?,1)",
            (city, region_id, iso2, lat, lng)).lastrowid
    return conn.execute(
        "INSERT INTO geo_cities (name,region_id,country_iso2,active) VALUES (?,?,?,1)",
        (city, region_id, iso2)).lastrowid

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
has = {r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()}
if "super_example" not in has:
    sys.exit("No super_example column — wrong DB.")
ucols = {r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()}
RESET_NULL = ["listing_lat","listing_lng","street_address","nearby_pois","boost_until"]
RESET_ZERO = ["view_count"]

plan, skips, warns = [], [], []
for cc, iso2, cname, city, rlabel, rname, lat, lng, cur in COUNTRIES:
    for cat, catkey in CAT_KEY.items():
        tiers = TIERS.get((cc, cat))
        if not tiers:
            warns.append(f"no tiers for {cc}/{cat} — skipped"); continue
        for (tcode, title, price, blurb, pemail, pname, earned, pending, target) in tiers:
            photos = photos_for(cc, catkey, tcode)
            if not photos:
                warns.append(f"no photos for {cc}/{cat}/{tcode} (sup_{cc}_{catkey}_{tcode}_*.jpg) — skipped"); continue
            if conn.execute("SELECT id FROM listings WHERE title=? LIMIT 1", (title,)).fetchone():
                skips.append(f"{iso2}/{cat}/{tcode}: '{title[:40]}...' exists"); continue
            cat_row = conn.execute(
                "SELECT category FROM listings WHERE LOWER(category)=LOWER(?) LIMIT 1", (cat,)).fetchone()
            actual_cat = cat_row["category"] if cat_row else cat
            tmpl = conn.execute(
                "SELECT * FROM listings WHERE COALESCE(super_example,0)=1 AND LOWER(category)=LOWER(?) LIMIT 1",
                (cat,)).fetchone()
            base_used = False
            if not tmpl:
                tmpl = conn.execute("SELECT * FROM listings WHERE COALESCE(super_example,0)=1 LIMIT 1").fetchone()
                base_used = True
            if not tmpl:
                warns.append(f"no super_example template in DB — skipped {iso2}/{cat}/{tcode}"); continue
            row = dict(tmpl); row.pop("id", None)
            row["category"] = actual_cat
            if base_used:
                for _k in CAT_SPECIFIC_COLS:
                    if _k in has: row[_k] = None
            row.update({
                "city": city, "title": title, "price": price,
                "description": "[photos:" + "|".join(photos) + "]\n" + blurb,
                "photo_urls": json.dumps(photos),
                "seller_email": pemail,
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
            if "trust_score" in has: row["trust_score"] = target
            if "tour" in has: row["tour"] = ""
            for k in RESET_NULL:
                if k in has: row[k] = None
            for k in RESET_ZERO:
                if k in has: row[k] = 0
            for k in ("created_at","updated_at","published_at"):
                if k in has: row[k] = now
            row = {k: v for k, v in row.items() if k in has and k != "country"}
            plan.append((cc, iso2, cname, city, rlabel, rname, lat, lng, cat, tcode,
                         title, price, len(photos), pemail, pname, earned, pending, target, tmpl["id"], row))

print(f"DB     : {DB}")
print(f"ASSETS : {ASSETS}")
print(f"MODE   : {'APPLY' if APPLY else 'DRY-RUN'}")
print(f"PLAN   : {len(plan)} new ladder listings, {len(skips)} skipped, {len(warns)} warnings\n")
for (cc, iso2, cname, city, rl, rn, lat, lng, cat, tcode, title, price, nph, pemail, pname,
     earned, pending, target, tid, _row) in plan:
    print(f"  + {iso2}/{cat}/{tcode}  T{target}  {nph} ph  {price:<20} {pemail:<34} | {title[:44]} (clone ZA #{tid})")
for s in skips: print(f"  = SKIP {s}")
for w in warns: print(f"  ! WARN {w}")

if not APPLY:
    print("\nDRY-RUN only — rerun with --apply to back up, seed geo, insert, create personas.")
    conn.close(); sys.exit(0)

bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-superladder"
shutil.copy2(DB, bak); print(f"DB backed up -> {bak}")

city_id = {}
for cc, iso2, cname, city, rlabel, rname, lat, lng, cur in COUNTRIES:
    city_id[iso2] = ensure_geo_city(conn, iso2, cname, rlabel, rname, city, lat, lng)
    print(f"  geo: {iso2} {city} -> geo_city_id {city_id[iso2]}")

photo_default = "/static/email_hero_property.jpg"
seen_personas, ins = set(), 0
for (cc, iso2, cname, city, rl, rn, lat, lng, cat, tcode, title, price, nph, pemail, pname,
     earned, pending, target, tid, row) in plan:
    if pemail not in seen_personas:
        seen_personas.add(pemail)
        fields = {"email": pemail, "name": pname}
        for c, v in [("country", cname), ("photo_url", photo_default),
                     ("id_verified_at", now_iso), ("eula_accepted_at", now_iso),
                     ("created_at", now_iso), ("trust_score", target)]:
            if c in ucols: fields[c] = v
        cols = ", ".join(fields); ph = ", ".join("?" * len(fields))
        conn.execute(f"INSERT OR IGNORE INTO users ({cols}) VALUES ({ph})", tuple(fields.values()))
        lcat = row.get("category") or cat
        for sid in earned:
            conn.execute("""INSERT INTO user_credentials (email, signal_id, status, listing_category)
                            VALUES (?,?,?,?) ON CONFLICT(email, signal_id)
                            DO UPDATE SET status='earned'""", (pemail, sid, "earned", lcat))
        for sid in pending:
            conn.execute("""INSERT INTO user_credentials (email, signal_id, status, listing_category)
                            VALUES (?,?,?,?) ON CONFLICT(email, signal_id)
                            DO UPDATE SET status='pending'""", (pemail, sid, "pending", lcat))
    if "geo_city_id" in has:
        row["geo_city_id"] = city_id[iso2]
    cols = list(row.keys())
    conn.execute(f"INSERT INTO listings ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                 [row[c] for c in cols])
    ins += 1

conn.commit()
bf = conn.execute(
    "UPDATE listings SET country = (SELECT gc.country_iso2 FROM geo_cities gc WHERE gc.id = listings.geo_city_id) "
    "WHERE geo_city_id IS NOT NULL AND (SELECT gc.country_iso2 FROM geo_cities gc WHERE gc.id = listings.geo_city_id) IS NOT NULL "
    "AND COALESCE(country,'') <> (SELECT gc.country_iso2 FROM geo_cities gc WHERE gc.id = listings.geo_city_id)").rowcount
conn.commit()
print(f"Inserted {ins} ladder listings; personas created/kept {len(seen_personas)}; country backfilled on {bf}.")
try:
    conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')"); conn.commit()
    print("FTS rebuilt.")
except Exception as e:
    print("FTS rebuild skipped:", e)
print("APPLIED. First profile view re-verifies every persona score via the evidence ledger (SUPER-TRUST-1).")
conn.close()
