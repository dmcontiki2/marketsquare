"""
archive_tester_listings.py — one-shot (28 Jul 2026, David's instruction during the
E2E email test: "Please remove this advert as it was placed as a tester and we can
not ever list such garbage live").

1. ARCHIVE the two tester adverts (never delete — archive is the standing rule):
     · 276  "2017 Ford Figo Ambiante 1.2 For Sale"   (David Jnr's test advert)
     · 277  "1-bed Apartment — Waterkloof"           (tester placement; specs 0/0/0)
2. Quietly DECLINE any still-pending intro requests on listings owned by
   *@trustsquare.co demo/showcase seller accounts, so the demo estate stops
   accruing RESP-1 "unanswered introduction" penalties (the existing -5 stays,
   per the rules — recovery is time-gated, never bought back).
   Direct SQL: no decline emails are sent by this path.

Run ON THE SERVER:  python3 archive_tester_listings.py           (dry-run)
                    python3 archive_tester_listings.py --apply   (backs up DB, commits)
"""
import os, sys, shutil, sqlite3
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB: sys.exit("No DB found — set MS_DB_PATH")
APPLY = "--apply" in sys.argv
TESTER_IDS = (276, 277)
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
rows = conn.execute(
    "SELECT id, title, listing_status FROM listings WHERE id IN (?,?)", TESTER_IDS).fetchall()
for r in rows:
    print(f"  listing {r['id']} '{r['title'][:40]}' status={r['listing_status']}"
          f" -> {'archived' if r['listing_status'] != 'archived' else '(already archived)'}")

pend = conn.execute("""SELECT ir.id, ir.listing_id, l.title FROM intro_requests ir
    JOIN listings l ON l.id = ir.listing_id
    WHERE ir.status='pending' AND LOWER(l.seller_email) LIKE '%@trustsquare.co'""").fetchall()
for p in pend:
    print(f"  pending intro {p['id']} on demo listing {p['listing_id']} '{p['title'][:36]}' -> declined")
print(f"  plan: archive {sum(1 for r in rows if r['listing_status'] != 'archived')}, "
      f"decline {len(pend)} pending demo intro(s)")

if not APPLY:
    print("  DRY RUN — nothing written. Run with --apply to commit."); sys.exit(0)

bak = DB + ".bak-archive-testers-" + now.replace(":", "")
shutil.copy2(DB, bak); print(f"  DB backed up -> {bak}")
conn.execute("UPDATE listings SET listing_status='archived', status_changed_at=? "
             "WHERE id IN (?,?) AND listing_status != 'archived'", (now,) + TESTER_IDS)
conn.execute("""UPDATE intro_requests SET status='declined' WHERE status='pending' AND listing_id IN
    (SELECT id FROM listings WHERE LOWER(seller_email) LIKE '%@trustsquare.co')""")
conn.commit(); conn.close()
print("  APPLIED.")
