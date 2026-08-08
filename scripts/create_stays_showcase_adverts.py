"""
create_stays_showcase_adverts.py — STAYS-SHOWCASE-1 (7 Aug 2026, OPEN_LOOPS D8)
================================================================================
Insert the THREE Stays / B&B adverts that the adventures_accommodation outreach
track's phone cards depict, so every "Click to view" lands on the exact advert
shown on the card (?listing=<id> deep link). This is the missing fourth trio:
property 315-317, cars 318-320, adventures-experiences 321-323, stays 3xx-3xx.

Rules honoured (every one of these was learned the hard way — see CHANGELOG
EMAIL-SHOWCASE-1/2/3 and migrations 002/003/004):
- NORMAL demo adverts (super_example=0). SUPER-PIN-1 pins super rows to the top
  of EVERY sort, so a super showcase advert would outrank real sellers. The
  29 Jul mark_showcase_supers.py run was reversed by migration 002 for exactly
  this reason; do not re-introduce it.
- CLONE-JUNK GUARD: rows are cloned from the live adventures_accommodation
  exemplar (271) so the insert always matches the live schema, then EVERY
  column belonging to another category is explicitly nulled. The 28 Jul trios
  silently inherited the template's vehicle/property fields and price_num;
  migration 002 had to heal six rows. Born clean instead.
- price_num set explicitly (sort/filter integrity), never inherited.
- No false attestation stamp, no auto-linked heritage wonders.
- Price carries a BASIS ("/ night") — adventures_accommodation is in
  RATE_UNIT_CATEGORIES, so a bare amount is rejected by _validate_price_unit.
- seller_email reuses showcase-email@trustsquare.co, the same seller migration
  001 used for 321-323: RG-0008 normalises adventures* to one family, so the
  wiring stays same-category without inventing a seller row.
- Idempotent (seller+title match) + dry-run-first + DB backup on apply.
- Always prints "SHOWCASE id=<id> | <title>" for every advert (new or existing)
  so the caller can harvest ids for flip_showcase_hrefs.py.

Run ON THE SERVER:  python3 create_stays_showcase_adverts.py           (dry-run)
                    python3 create_stays_showcase_adverts.py --apply   (backs up DB, writes)
"""
import os, sys, json, shutil, sqlite3
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found — set MS_DB_PATH=/path/to/marketsquare.db")
APPLY = "--apply" in sys.argv
SELLER = "showcase-email@trustsquare.co"
FOOT = " Showcase advert: AI imagery; free for a real seller to claim and replace with their own property."
CATEGORY = "adventures_accommodation"
TEMPLATE_ID = 271          # the ZA advacc exemplar (stone-and-thatch lodge suite)

# (title, price, price_num, suburb, photo, lat, lng, trust, blurb)
# Suburb stays a Pretoria-metro suburb — the launch market — exactly as the
# balloon-safari advert does ("Hot Air Balloon Safari · Hartbeespoort" / Centurion).
# The real place lives in the TITLE and the map pin.
ADVERTS = [
 ("Thatch & Bushveld Safari Lodge · Pilanesberg", "R2,450 / night", 2450.0, "Pretoria North",
  "/static/super/sup_email_thatch_1_main.jpg", -25.3300, 27.0900, 50,
  "Six stone-and-thatch rooms on a low rise, each with its own deck and a shared plunge pool. "
  "Fifteen minutes from the Manyane Gate, so the Pilanesberg is a morning drive, not an expedition."),
 ("Jacaranda Boutique Guesthouse · Hartbeespoort", "R1,850 / night", 1850.0, "Centurion",
  "/static/super/sup_email_jacaranda_1_main.jpg", -25.7450, 27.8850, 50,
  "A white-walled guesthouse under jacarandas, looking across the dam to the Magaliesberg. "
  "Breakfast on the deck, shuttered rooms, and the water changing colour all afternoon."),
 ("Marula Bush Camp · Magaliesberg", "R1,450 / night", 1450.0, "Pretoria North",
  "/static/super/sup_email_marula_1_main.jpg", -25.8650, 27.5600, 50,
  "Canvas tents on timber decks under old marulas — off-grid, lantern-lit, no traffic to hear. "
  "Dinner happens around the fire in the stone boma, which is the point of coming."),
]

# Every column that belongs to ANOTHER category. Cloning 271 would otherwise drag
# these through silently — the exact fault migration 002 had to heal on six rows.
CLONE_JUNK = [
    # vehicles (CARS-SPEC-1)
    "make", "model", "variant", "vehicle_year", "mileage_km", "transmission",
    "fuel_type", "body_type", "drivetrain", "colour", "vehicle_specs",
    "spec_confirmed", "attested_at", "attested_email",
    # property
    "beds", "baths", "garages", "prop_type", "floor_area", "erf_size",
    # collectors
    "scryfall_id", "collectible_type", "condition", "era_year",
    "ai_grade", "ai_grade_conf", "ai_grade_notes", "grade_tier",
    # services / tutors
    "subject", "level", "mode", "service_type", "service_class",
    # rentals + misc carry-over
    "rental_status", "available_from", "linked_wonders", "nearby_pois",
    "ai_suggested_price", "import_source", "tour", "street_address",
    "boost_until", "suspension_reason", "block_cause", "expires_at",
    "warning_sent_at", "fade_nudge_sent_at",
]

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

tmpl = conn.execute("SELECT * FROM listings WHERE id=?", (TEMPLATE_ID,)).fetchone()
if not tmpl:
    sys.exit(f"template listing {TEMPLATE_ID} missing — aborting, nothing written")
if str(tmpl["category"] or "") != CATEGORY:
    sys.exit(f"template {TEMPLATE_ID} is category '{tmpl['category']}', expected "
             f"'{CATEGORY}' — aborting rather than cloning the wrong shape")
live_cols = set(dict(tmpl).keys())
# NOT-NULL GUARD (8 Aug 2026): the first --apply run died on
#   sqlite3.IntegrityError: NOT NULL constraint failed: listings.rental_status
# Some clone-junk columns are declared NOT NULL, so blanking them to None is an
# invalid write, not a clean one. Ask the live schema which columns tolerate NULL
# and only blank those; a NOT NULL column keeps the template's own value, which is
# always a legal value for that column. Self-adjusting: any future NOT NULL column
# is handled without another edit here.
nullable = {r["name"] for r in conn.execute("PRAGMA table_info(listings)") if not r["notnull"]}
protected = sorted(c for c in CLONE_JUNK if c in live_cols and c not in nullable)
print(f"template {TEMPLATE_ID} ok: category={CATEGORY}, {len(live_cols)} columns")
if protected:
    print(f"NOT NULL — keeping the template's value on: {', '.join(protected)}")

plan, existing = [], []
for title, price, price_num, suburb, photo, lat, lng, trust, blurb in ADVERTS:
    hit = conn.execute("SELECT id FROM listings WHERE seller_email=? AND title=?",
                       (SELLER, title)).fetchone()
    if hit:
        existing.append((hit["id"], title))
        continue
    row = dict(tmpl)
    row.pop("id", None)
    row.update({
        "title": title, "price": price, "price_num": price_num,
        "suburb": suburb, "category": CATEGORY,
        "description": f"[photos:{photo}]{blurb}{FOOT}",
        "photo_urls": json.dumps([photo]),
        "thumb_url": photo, "medium_url": None,
        "listing_lat": lat, "listing_lng": lng,
        "super_example": 0, "trust_score": trust,
        "seller_email": SELLER, "claim_status": "claimed",
        "created_at": now, "updated_at": now, "published_at": now,
        "view_count": 0, "listing_status": "live",
    })
    for col in CLONE_JUNK:
        if col in live_cols and col in nullable:
            row[col] = None
    plan.append((row, title))

print(f"PLAN: insert {len(plan)}, already present {len(existing)}")
for _id, t in existing:
    print(f"SHOWCASE id={_id} | {t} (existing)")
for row, t in plan:
    print(f"  + {row['category']:<26} {row['price']:<16} price_num={row['price_num']:<9} | {t}")

if not APPLY:
    print("DRY-RUN only — rerun with --apply to back up the DB and insert.")
    conn.close(); sys.exit(0)

if plan:
    bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-staysshowcase"
    shutil.copy2(DB, bak); print(f"DB backed up -> {bak}")
    for row, t in plan:
        cols = list(row.keys())
        cur = conn.execute(
            f"INSERT INTO listings ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
            [row[c] for c in cols])
        print(f"SHOWCASE id={cur.lastrowid} | {t}")
    try:
        conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')")
    except sqlite3.OperationalError:
        pass
    conn.commit()
print("done.")
conn.close()
