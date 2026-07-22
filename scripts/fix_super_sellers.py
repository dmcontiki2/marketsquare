"""
fix_super_sellers.py — JNR-FIX-1 (22 Jul 2026, David Jnr feedback, David's verdict: fix)
=======================================================================================
Problem: all super_example exemplar listings share a handful of seller accounts, so the
buyer-facing Seller CV shows a COLLECTIVE category list (a "Tutor" whose seller also
trades Collectors + local_market). Fix: one specialist seller account per category
family; adventures_accommodation + adventures_experiences deliberately share one
"Adventures Seller" (a lodge selling stays + drives is realistic).

Trust integrity: /sellers/credentials keys off seller_email -> users, so each new
account CLONES the source user's trust-signal fields (id_verified_at, name/country/
photo_url etc.). Intro-request track record follows the listings (intro_requests keys
on listing_id), so each specialist keeps the intros on their own listings.

Run ON THE SERVER:  python3 fix_super_sellers.py           (dry-run, prints plan)
                    python3 fix_super_sellers.py --apply   (backs up DB, commits)
"""
import os, sys, shutil, sqlite3
from datetime import datetime

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB: sys.exit("No DB found — set MS_DB_PATH")
APPLY = "--apply" in sys.argv

def fam(cat):
    c = (cat or "").strip().lower()
    if c.startswith("adventures"): return "adventures", "Adventures Seller"
    key = c.replace(" ", "").replace("_", "")
    names = {"tutors":"Tutors Seller","services":"Services Seller","collectors":"Collectors Seller",
             "localmarket":"Local Market Seller","cars":"Cars Seller","property":"Property Seller"}
    return key, names.get(key, (cat or "Seller").title() + " Seller")

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
rows = conn.execute("SELECT id,title,category,seller_email,trust_score FROM listings "
                    "WHERE COALESCE(super_example,0)=1").fetchall()
if not rows: sys.exit("No super_example listings found — nothing to do.")

ucols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
plan = []
for r in rows:
    family, disp = fam(r["category"])
    target = f"super-{family}@trustsquare.co"
    cur = (r["seller_email"] or "").lower()
    plan.append((r["id"], r["title"][:48], r["category"], cur, target, disp, cur != target.lower()))

print(f"DB: {DB}\n{'ID':>5}  {'category':<28} {'current seller':<34} -> target")
for p in plan:
    print(f"{p[0]:>5}  {p[2]:<28} {p[3]:<34} -> {p[4]}{'' if p[6] else '  (already ok)'}")
changes = [p for p in plan if p[6]]
if not changes: sys.exit("All exemplars already on specialist accounts — nothing to do.")
if not APPLY: sys.exit(f"\nDRY RUN — {len(changes)} reassignment(s) pending. Re-run with --apply.")

bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-supersellers"
shutil.copy2(DB, bak); print("DB backup:", bak)

for lid, _t, cat, cur, target, disp, _c in changes:
    exists = conn.execute("SELECT 1 FROM users WHERE LOWER(email)=?", (target.lower(),)).fetchone()
    if not exists:
        src = conn.execute("SELECT * FROM users WHERE LOWER(email)=?", (cur,)).fetchone()
        if src:
            d = dict(src); d.pop("id", None); d["email"] = target
            if "name" in d: d["name"] = disp
            cols = [c for c in d if c in ucols]
            conn.execute(f"INSERT INTO users ({','.join(cols)}) VALUES ({','.join('?'*len(cols))})",
                         [d[c] for c in cols])
            print(f"  user created: {target} (cloned trust fields from {cur})")
        else:
            print(f"  WARNING: no source user {cur} — {target} created empty-handed? SKIPPING listing {lid}")
            continue
    conn.execute("UPDATE listings SET seller_email=? WHERE id=?", (target, lid))
    print(f"  listing {lid} -> {target}")

# JNR-FIX-5 (extended 22 Jul, David: tutor + garden + electrician all missing units):
# every rate-based exemplar (Tutors/Services) must carry its unit in the price string.
UNIT_MAP = [   # (title keyword, unit, price_num)  — David's picks: hour / day / call-out
    ("tutor",       "/ hour",     450),
    ("garden",      "/ day",      480),
    ("electrician", "/ call-out", 650),
]
for kw, unit, pnum in UNIT_MAP:
    r2 = conn.execute("SELECT id,price FROM listings WHERE COALESCE(super_example,0)=1 "
                      "AND LOWER(title) LIKE ?", (f"%{kw}%",)).fetchone()
    if r2 and "/" not in (r2["price"] or ""):
        import re as _re
        digits = _re.sub(r"[^0-9.]", "", r2["price"] or "") or str(pnum)
        amount = int(float(digits))
        newp = f"R{amount:,} {unit}".replace(",", " ") if amount >= 1000 else f"R{amount} {unit}"
        conn.execute("UPDATE listings SET price=?, price_num=? WHERE id=?", (newp, amount, r2["id"]))
        print(f"  listing {r2['id']} price: {r2['price']!r} -> {newp!r}")
# JNR-FIX-5B data pass (22 Jul, round 2): Bee Lady talk showed bare "R50" — fix it and
# any other unit-less rate-category listing we can classify; report the rest.
r_bee = conn.execute("SELECT id,title,price FROM listings WHERE LOWER(category)='tutors' "
                     "AND LOWER(title) LIKE '%talk%' AND REPLACE(price,' ','') IN ('R50','R50.00')").fetchone()
if r_bee:
    conn.execute("UPDATE listings SET price='R50 / person', price_num=50 WHERE id=?", (r_bee["id"],))
    print(f"  listing {r_bee['id']} ({r_bee['title'][:40]!r}) price: {r_bee['price']!r} -> 'R50 / person'")
for r_lint in conn.execute("SELECT id,title,category,price FROM listings WHERE "
        "LOWER(category) IN ('tutors','services','adventures_experiences','adventures_accommodation') "
        "AND price IS NOT NULL AND TRIM(price)<>'' AND price NOT LIKE '%/%' "
        "AND LOWER(price) NOT LIKE '%per %' AND LOWER(price) NOT LIKE '%once%' "
        "AND LOWER(price) NOT LIKE '%poa%' AND LOWER(price) NOT LIKE '%negotiable%' "
        "AND LOWER(price) NOT LIKE '%from %'").fetchall():
    print(f"  LINT: {r_lint['id']} [{r_lint['category']}] {r_lint['title'][:40]!r}: {r_lint['price']!r} — needs a basis, decide unit")

# safety net: report any remaining Tutors/Services exemplar without a visible unit
for r3 in conn.execute("SELECT id,title,price FROM listings WHERE COALESCE(super_example,0)=1 "
                       "AND LOWER(category) IN ('tutors','services') AND price NOT LIKE '%/%'").fetchall():
    print(f"  NOTE: exemplar {r3['id']} ({r3['title'][:40]!r}) still unit-less: {r3['price']!r} — decide unit")

conn.commit()
# audit
print("\nPost-fix seller summaries:")
for em in sorted({p[4] for p in changes}):
    cats = conn.execute("SELECT category, COUNT(*) n FROM listings WHERE LOWER(seller_email)=? "
                        "GROUP BY category", (em.lower(),)).fetchall()
    print(f"  {em}: " + ", ".join(f"{c['category']}×{c['n']}" for c in cats))
print("Done. Restart not needed (data only). Purge CF cache if listing JSON is edge-cached.")
