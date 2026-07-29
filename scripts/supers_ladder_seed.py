"""
supers_ladder_seed.py — one-shot (29 Jul 2026, David's sign-off: "Please proceed").
Gives the nine showcase adverts REAL seller accounts with evidence-true credential
ladders, each showing a DIFFERENT route to a high Trust Score (for the agency wave).

Personas (arithmetic per _trust_math: 40 base + universal<=30 + track<=30 + cat<=40):
  315 Vacant Stand      -> prop-showcase-a@trustsquare.co  ID+profile            = 60
  316 Family Home       -> prop-showcase-b@trustsquare.co  +PPRA15 +NQF4 6,
                                                            FFC PENDING (0 pts)   = 81
  317 Penthouse         -> prop-showcase-c@trustsquare.co  +PPRA15+FFC10+NQF4 6
                                                            +IEASA body 5         = 96
  318 AMG C63           -> cars-showcase-c@trustsquare.co  +MIRA8+NATIS10+RWC6
                                                            +service4+finance4    = 92
  319 Land Cruiser 79   -> cars-showcase-b@trustsquare.co  +NATIS10+RWC6+service4 = 80
  320 250SE Restored    -> cars-showcase-a@trustsquare.co  ID+profile            = 60
  312-314 experiences   -> attached to the EXISTING Adventures specialist seller
                           (same account as listings 270/271), whose ladder is live.

All demo accounts; SO-1 applies. Existing seller_emails on 312-320 are replaced only
if they have no users row (never steals a real seller's listing).

Run ON THE SERVER:  python3 supers_ladder_seed.py           (dry-run)
                    python3 supers_ladder_seed.py --apply   (backs up DB, commits)
"""
import os, sys, shutil, sqlite3
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB: sys.exit("No DB found — set MS_DB_PATH")
APPLY = "--apply" in sys.argv
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

PERSONAS = {
    315: ("prop-showcase-a@trustsquare.co", "Showcase Estates A", "Property", [], [], 60),
    316: ("prop-showcase-b@trustsquare.co", "Showcase Estates B", "Property",
          ["category.property.ppra", "category.property.nqf4"],
          ["category.property.ffc"], 81),                      # FFC pending — 0 pts
    317: ("prop-showcase-c@trustsquare.co", "Showcase Estates C", "Property",
          ["category.property.ppra", "category.property.ffc",
           "category.property.nqf4", "category.property.body"], [], 96),
    318: ("cars-showcase-c@trustsquare.co", "Showcase Motors C", "Cars",
          ["category.cars.dealer_reg", "category.cars.ownership", "category.cars.rwc",
           "category.cars.service_history", "category.cars.finance_clear"], [], 92),
    319: ("cars-showcase-b@trustsquare.co", "Showcase Motors B", "Cars",
          ["category.cars.ownership", "category.cars.rwc",
           "category.cars.service_history"], [], 80),
    320: ("cars-showcase-a@trustsquare.co", "Showcase Motors A", "Cars", [], [], 60),
}

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
ucols = {r[1] for r in conn.execute("PRAGMA table_info(users)")}

# Adventures: reuse the existing specialist seller from the original supers
adv = conn.execute("SELECT seller_email FROM listings WHERE id IN (270,271) "
                   "AND seller_email IS NOT NULL LIMIT 1").fetchone()
adv_email = adv["seller_email"] if adv else None
print(f"  adventures specialist: {adv_email or 'NOT FOUND — 312-314 will be skipped'}")

plan = []
for lid, (email, name, cat, earned, pending, target) in PERSONAS.items():
    l = conn.execute("SELECT id, title, seller_email FROM listings WHERE id=?", (lid,)).fetchone()
    if not l: print(f"  {lid}: listing missing — skip"); continue
    cur = l["seller_email"]
    has_user = cur and conn.execute("SELECT 1 FROM users WHERE LOWER(email)=LOWER(?)", (cur,)).fetchone()
    if has_user:
        print(f"  {lid} '{l['title'][:34]}': seller {cur} already has an account — SKIP (never steal)")
        continue
    plan.append((lid, l["title"], email, name, cat, earned, pending, target))
    print(f"  {lid} '{l['title'][:34]}': seller -> {email}  target Trust {target}"
          f"  earned={len(earned)} pending={len(pending)}")
for lid in (312, 313, 314):
    l = conn.execute("SELECT id, title, seller_email FROM listings WHERE id=?", (lid,)).fetchone()
    if l and adv_email:
        print(f"  {lid} '{l['title'][:34]}': seller -> {adv_email} (existing adventures ladder)")

if not APPLY:
    print("  DRY RUN — nothing written. Run with --apply to commit."); sys.exit(0)

bak = DB + ".bak-ladder-seed-" + now.replace(":", "")
shutil.copy2(DB, bak); print(f"  DB backed up -> {bak}")

photo_default = "/static/email_hero_property.jpg"
for lid, title, email, name, cat, earned, pending, target in plan:
    fields = {"email": email, "name": name}
    for c, v in [("country", "South Africa"), ("photo_url", photo_default),
                 ("id_verified_at", now), ("eula_accepted_at", now),
                 ("created_at", now), ("trust_score", target)]:
        if c in ucols: fields[c] = v
    cols = ", ".join(fields); ph = ", ".join("?" * len(fields))
    conn.execute(f"INSERT OR IGNORE INTO users ({cols}) VALUES ({ph})", tuple(fields.values()))
    for sid in earned:
        conn.execute("""INSERT INTO user_credentials (email, signal_id, status, listing_category)
                        VALUES (?,?,?,?) ON CONFLICT(email, signal_id)
                        DO UPDATE SET status='earned'""", (email, sid, "earned", cat))
    for sid in pending:
        conn.execute("""INSERT INTO user_credentials (email, signal_id, status, listing_category)
                        VALUES (?,?,?,?) ON CONFLICT(email, signal_id)
                        DO UPDATE SET status='pending'""", (email, sid, "pending", cat))
    conn.execute("UPDATE listings SET seller_email=?, trust_score=? WHERE id=?", (email, target, lid))
if adv_email:
    advts = conn.execute("SELECT trust_score FROM users WHERE LOWER(email)=LOWER(?)", (adv_email,)).fetchone()
    conn.execute("UPDATE listings SET seller_email=?, trust_score=? WHERE id IN (312,313,314)",
                 (adv_email, (advts["trust_score"] if advts else 90)))
conn.commit(); conn.close()
print("  APPLIED. First profile view re-verifies every score via the evidence ledger.")
