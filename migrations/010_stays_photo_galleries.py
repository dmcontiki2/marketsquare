#!/usr/bin/env python3
"""010_stays_photo_galleries.py — STAYS-GALLERY-1 (9 Aug 2026).

THE DEFECT (mine, found by David looking at the screen — not by any check I wrote)
---------------------------------------------------------------------------------
Fifteen photos were generated for the Stays trio, five per property. Only THREE
reached the app: create_stays_showcase_adverts.py wrote a single-element photo
array, so 336/337/338 render one flat image with no carousel, while the super
advert beside them (271) shows an eight-photo gallery with thumbnails. Twelve
photos have been sitting unused on the server since the media push.

David chose full five-photo sets over one-main-each deliberately. The generation
was done; the wiring was not.

THE SHAPE THAT WORKS (copied from live listing 271, not from memory)
--------------------------------------------------------------------
  photo_urls  : JSON array of every photo, main first
  description : "[photos:<url1>|<url2>|...]<blurb>"   <- PIPE separated, all of them
Both must agree; the renderer reads the description prefix.

SAFETY
------
Idempotent (skips a listing already carrying its full set). Verifies every photo
file exists on disk before writing that listing. Matches on seller+title, never on
a bare id. Backs up the DB. Leaves the blurb and the showcase footer untouched.

Run ON THE SERVER:  python3 010_stays_photo_galleries.py           (dry-run)
                    python3 010_stays_photo_galleries.py --apply
"""
import os, sys, json, shutil, sqlite3, re
from datetime import datetime

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found — set MS_DB_PATH=/path/to/marketsquare.db")
APPLY  = "--apply" in sys.argv
SELLER = "showcase-email@trustsquare.co"
WEBROOT = os.path.dirname(DB)
P = "/static/super/"

SETS = {
 "Thatch & Bushveld Safari Lodge · Pilanesberg": [
   "sup_email_thatch_1_main.jpg", "sup_email_thatch_2_room.jpg",
   "sup_email_thatch_3_pool.jpg", "sup_email_thatch_4_breakfast.jpg",
   "sup_email_thatch_5_game.jpg"],
 "Jacaranda Boutique Guesthouse · Hartbeespoort": [
   "sup_email_jacaranda_1_main.jpg", "sup_email_jacaranda_2_room.jpg",
   "sup_email_jacaranda_3_deck.jpg", "sup_email_jacaranda_4_breakfast.jpg",
   "sup_email_jacaranda_5_dam.jpg"],
 "Marula Bush Camp · Magaliesberg": [
   "sup_email_marula_1_main.jpg", "sup_email_marula_2_tent.jpg",
   "sup_email_marula_3_boma.jpg", "sup_email_marula_4_deck.jpg",
   "sup_email_marula_5_sunrise.jpg"],
}

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
plan, skipped = [], []

for title, files in SETS.items():
    row = conn.execute("SELECT id, description, photo_urls FROM listings "
                       "WHERE seller_email=? AND title=?", (SELLER, title)).fetchone()
    if not row:
        skipped.append((title, "listing not found — nothing written")); continue

    missing = [f for f in files if not os.path.isfile(os.path.join(WEBROOT, "static", "super", f))]
    if missing:
        skipped.append((title, "photo file(s) missing on disk, refusing: " + ", ".join(missing)))
        continue

    urls = [P + f for f in files]
    try:
        have = json.loads(row["photo_urls"] or "[]")
    except Exception:
        have = []
    if have == urls:
        skipped.append((title, "already carries all %d — nothing to do" % len(urls))); continue

    desc = row["description"] or ""
    blurb = re.sub(r"^\[photos:[^\]]*\]", "", desc)      # strip the old prefix, keep the words
    new_desc = "[photos:" + "|".join(urls) + "]" + blurb
    plan.append((row["id"], title, len(have), urls, new_desc))

print("PLAN: update %d listing(s), skip %d" % (len(plan), len(skipped)))
for _id, t, was, urls, _ in plan:
    print("  + id=%-4s %-46s %d photo -> %d" % (_id, t[:46], was, len(urls)))
for t, why in skipped:
    print("  · %-46s %s" % (t[:46], why))

if not plan:
    print("nothing to do."); conn.close(); sys.exit(0)
if not APPLY:
    print("DRY-RUN only — rerun with --apply to back up the DB and write.")
    conn.close(); sys.exit(0)

bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-staysgallery"
shutil.copy2(DB, bak); print("DB backed up -> " + bak)
now = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
for _id, t, _was, urls, new_desc in plan:
    conn.execute("UPDATE listings SET photo_urls=?, thumb_url=?, description=?, updated_at=? "
                 "WHERE id=?", (json.dumps(urls), urls[0], new_desc, now, _id))
    print("GALLERY id=%s | %s | %d photos" % (_id, t, len(urls)))
conn.commit(); conn.close()
print("done.")
