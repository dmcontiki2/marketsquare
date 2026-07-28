"""
create_email_showcase_adverts.py — EMAIL-SHOWCASE-1 (28 Jul 2026, David-approved OPEN_LOOPS D5)
================================================================================================
Insert the NINE adverts that the wave-1 agency-email phone cards depict, so every
"Click to view" lands on the exact advert shown on the card (?listing=<id> deep link).

Rules honoured:
- NORMAL demo adverts (super_example=0) — the pinned exemplar row stays at three.
- Idempotent + dry-run-first + DB backup on apply (house pattern, cf. seed_super_global.py).
- Rows are CLONED from an existing same-category exemplar so the insert always matches
  the live schema, then overridden field-by-field.
- Always prints "SHOWCASE id=<id> | <title>" for every advert (new or existing) so the
  caller can harvest ids for the email templates.

Run ON THE SERVER:  python3 create_email_showcase_adverts.py           (dry-run)
                    python3 create_email_showcase_adverts.py --apply   (backs up DB, writes)
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
FOOT = " Showcase advert: AI imagery; free for a real seller to claim and replace with their own product."

# (clone_template_id, title, price, suburb, photo, trust, blurb)
ADVERTS = [
 (270, "Big 5 Game Walk · Pilanesberg", "R1,850 / person", "Pretoria North",
  "/static/super/sup_email_gamewalk_1_main.jpg", 50,
  "Guided Big 5 bush walk with an armed field guide — golden-hour departure, small groups, all levels."),
 (270, "Quad Biking Dinokeng · Full Day", "R1,250 / person", "Pretoria North",
  "/static/super/sup_email_quad_1_main.jpg", 50,
  "Full-day guided quad trail through open bushveld — helmets, briefing and sundowner stop included."),
 (270, "Hot Air Balloon Safari · Hartbeespoort", "R3,200 / person", "Centurion",
  "/static/super/sup_email_balloon_1_main.jpg", 50,
  "Sunrise balloon flight over the Magaliesberg with sparkling-wine landing breakfast."),
 (264, "Vacant Stand — Silver Lakes Golf Estate", "R1 650 000", "Silver Lakes",
  "/static/super/sup_email_stand_1_main.jpg", 50,
  "North-facing 920 m2 stand on the fairway — build your forever home in a top security estate."),
 (264, "Modern 4-Bed Family Home — Waterkloof Ridge", "R4 250 000", "Waterkloof Ridge",
  "/static/super/sup_email_home_1_main.jpg", 50,
  "Architect-designed 4-bed with pool, jacaranda street and double lock-up — walk to top schools."),
 (264, "Penthouse Apartment — Brooklyn, Pretoria", "R3 100 000", "Brooklyn",
  "/static/super/sup_email_penthouse_1_main.jpg", 50,
  "Top-floor penthouse with skyline terrace, fire-pit lounge and two secure parkings."),
 (265, "2021 Mercedes-AMG C63 S · Saloon · 42 000km", "R1 450 000", "Brooklyn",
  "/static/super/sup_email_amg_1_main.jpg", 85,
  "One owner, full agent history, 375 kW bi-turbo V8 — balance of Premium Drive plan."),
 (265, "2020 Toyota Land Cruiser 79 · 4.5 V8 · Bakkie", "R1 100 000", "Pretoria North",
  "/static/super/sup_email_lc79_1_main.jpg", 50,
  "4.5 V8 diesel double-cab legend — canopy, dual tanks, service book stamped to date."),
 (265, "1966 Mercedes-Benz 250SE W108 · Restored", "R345 000", "Pretoria East",
  "/static/super/sup_email_250se_1_main.jpg", 50,
  "Nut-and-bolt restored W108 — numbers matching, original hubcaps, concours-ready."),
]

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

plan, existing = [], []
for tid, title, price, suburb, photo, trust, blurb in ADVERTS:
    hit = conn.execute("SELECT id FROM listings WHERE seller_email=? AND title=?",
                       (SELLER, title)).fetchone()
    if hit:
        existing.append((hit["id"], title))
        continue
    tmpl = conn.execute("SELECT * FROM listings WHERE id=?", (tid,)).fetchone()
    if not tmpl:
        sys.exit(f"template listing {tid} missing — aborting, nothing written")
    row = dict(tmpl)
    row.pop("id", None)
    row.update({
        "title": title, "price": price, "suburb": suburb,
        "description": f"[photos:{photo}]{blurb}{FOOT}",
        "photo_urls": json.dumps([photo]),
        "thumb_url": photo, "medium_url": None,
        "super_example": 0, "trust_score": trust,
        "seller_email": SELLER, "claim_status": "claimed",
        "created_at": now, "updated_at": now, "published_at": now,
        "view_count": 0, "boost_until": None, "suspension_reason": None,
        "listing_status": "live",
    })
    plan.append((row, title))

print(f"PLAN: insert {len(plan)}, already present {len(existing)}")
for _id, t in existing: print(f"SHOWCASE id={_id} | {t} (existing)")
for row, t in plan: print(f"  + {row['category']:<24} {row['price']:<16} | {t}")

if not APPLY:
    print("DRY-RUN only — rerun with --apply to back up the DB and insert.")
    conn.close(); sys.exit(0)

if plan:
    bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-emailshowcase"
    shutil.copy2(DB, bak); print(f"DB backed up -> {bak}")
    for row, t in plan:
        cols = list(row.keys())
        cur = conn.execute(f"INSERT INTO listings ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                           [row[c] for c in cols])
        print(f"SHOWCASE id={cur.lastrowid} | {t}")
    try:
        conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')")
    except sqlite3.OperationalError:
        pass
    conn.commit()
print("done.")
conn.close()
