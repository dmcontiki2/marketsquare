"""
create_email_showcase_adverts.py — EMAIL-SHOWCASE-1 (28 Jul 2026, David-approved OPEN_LOOPS D5)
================================================================================================
Insert the NINE adverts that the wave-1 agency-email phone cards depict, so every
"Click to view" lands on the exact advert shown on the card (?listing=<id> deep link).

Rules honoured:
- SHOWCASE-BANNER-1 (11 Aug 2026, David): super_example=1 + showcase=1 — the star
  banner WITHOUT the pin; the pinned exemplar row still stays at three because
  every sort (server + client) excludes showcase rows from pinning.
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

# (clone_template_id, title, price, suburb, photo, trust, blurb, price_num)
ADVERTS = [
 (270, "Big 5 Game Walk · Pilanesberg", "R1,850 / person", "Pretoria North",
  "/static/super/sup_email_gamewalk_1_main.jpg", 50,
  "Guided Big 5 bush walk with an armed field guide — golden-hour departure, small groups, all levels.", 1850.0),
 (270, "Quad Biking Dinokeng · Full Day", "R1,250 / person", "Pretoria North",
  "/static/super/sup_email_quad_1_main.jpg", 50,
  "Full-day guided quad trail through open bushveld — helmets, briefing and sundowner stop included.", 1250.0),
 (270, "Hot Air Balloon Safari · Hartbeespoort", "R3,200 / person", "Centurion",
  "/static/super/sup_email_balloon_1_main.jpg", 50,
  "Sunrise balloon flight over the Magaliesberg with sparkling-wine landing breakfast.", 3200.0),
 # PROPERTY TRIO REMOVED 2 Aug 2026 (David: "complete D5 now" session): these three
 # already exist LIVE as listings 315/316/317 (sellers prop-showcase-a/b/c@trustsquare.co,
 # created 28 Jul) and agency_outreach.html is already deep-linked to them. Re-adding them
 # here would DUPLICATE (this script's idempotency keys on seller showcase-email@ + title,
 # which does not match the live prop-showcase-* rows). Remaining to create: 3 Cars + 3
 # Adventures below -> cars_dealer / tour_guide / travel_agency templates.
 # CARS TRIO REMOVED 2 Aug 2026 (post-ship discovery, same class as the property trio):
 # already LIVE as listings 318/319/320 (sellers cars-showcase-a/b/c@trustsquare.co) —
 # this script's showcase-email@ idempotency would have duplicated them.
 # cars_dealer_outreach.html deep-linked to 318-320 on 2 Aug. Only the THREE
 # Adventures adverts above remain for this script to create.
]

conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

plan, existing = [], []
for tid, title, price, suburb, photo, trust, blurb, price_num in ADVERTS:
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
        "super_example": 1, "showcase": 1, "trust_score": trust,
        "seller_email": SELLER, "claim_status": "claimed",
        "created_at": now, "updated_at": now, "published_at": now,
        "view_count": 0, "boost_until": None, "suspension_reason": None,
        "listing_status": "live",
        # EMAIL-SHOWCASE-2 (2 Aug 2026): clone-junk guard — the 28 Jul trios kept the
        # template's price_num/wonders/attestation stamps; never inherit those again.
        "price_num": price_num, "linked_wonders": None, "spec_confirmed": None,
        "attested_at": None, "attested_email": None, "nearby_pois": None,
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
