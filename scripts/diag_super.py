"""
diag_super.py — SUPER-DIAG-1 (25 Jul 2026, David)  READ-ONLY. Writes nothing, ever.
====================================================================================
The 'eyes' wedge: prints the real state of the super_example listings + their sellers
so fixes are made against facts, not guesses. Runs during deploy (safe — SELECTs only).

Reports:
  • schema: does listings have a country column? category casing in use?
  • every super_example listing: category, country, city, stored trust_score, seller
  • the super-* seller accounts: whatever trust-related fields the users table holds
  • MISMATCH flags: listing.trust_score vs seller's stored trust (the 90-vs-45 bug)
  • per-country / per-category coverage tallies

Run ON THE SERVER:  python3 diag_super.py
"""
import os, sys, json, sqlite3

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found — set MS_DB_PATH=/path/to/marketsquare.db")

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
lcols = [r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()]
ucols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]

print("=" * 68)
print("SUPER-DIAG — read-only snapshot")
print("DB:", DB)
print("listings has country column:", "country" in lcols)
print("=" * 68)

# category casing across ALL listings (this is what bit us)
print("\n[categories in use] (LOWER -> exact spellings seen)")
seen = {}
for r in conn.execute("SELECT DISTINCT category FROM listings WHERE category IS NOT NULL"):
    seen.setdefault((r["category"] or "").lower(), set()).add(r["category"])
for k in sorted(seen):
    spellings = sorted(seen[k])
    flag = "  <-- MIXED CASING" if len(spellings) > 1 else ""
    print(f"   {k:24} : {spellings}{flag}")

# which trust field(s) exist on users
trust_ucols = [c for c in ucols if "trust" in c.lower() or "score" in c.lower()]
print("\n[users trust-ish columns]:", trust_ucols or "(none — seller trust is computed, not stored)")

# super_example listings — build SELECT from only the columns that exist (defensive)
print("\n[super_example listings]")
def col(name, default):
    return (f"COALESCE({name},{default}) {name}" if name in lcols else f"{default} {name}")
sel = ", ".join([
    "id",
    col("category", "'?'") if "category" in lcols else "'?' category",
    col("country", "'?'"),
    "city" if "city" in lcols else "'?' city",
    col("trust_score", "-1"),
    col("safety_score", "-1"),
    col("seller_email", "''"),
])
rows = conn.execute(
    f"SELECT {sel} FROM listings WHERE COALESCE(super_example,0)=1 ORDER BY country, category"
).fetchall()
print(f"   total super_example: {len(rows)}")
sellers = {}
for r in rows:
    sellers.setdefault((r["seller_email"] or "").lower(), []).append(r)
    print(f"   [{r['id']:>4}] {str(r['country']):<3} {str(r['category']):<26} trust={r['trust_score']:<4} "
          f"safety={r['safety_score']:<4} seller={r['seller_email']}")

# seller accounts referenced, with any stored trust field
print("\n[super sellers — stored fields]")
sel_trust = {}
for em in sorted(sellers):
    if not em:
        print("   (blank seller_email on some listings!)"); continue
    u = conn.execute("SELECT * FROM users WHERE LOWER(email)=?", (em,)).fetchone()
    if not u:
        print(f"   {em}: NO USER ROW (seller CV will fall back)"); continue
    d = dict(u)
    info = {c: d.get(c) for c in trust_ucols}
    sel_trust[em] = info
    ncred = None
    if "credentials" in ucols:
        ncred = d.get("credentials")
    print(f"   {em}: {info}  listings={len(sellers[em])}")

# mismatch flags: listing.trust_score vs any stored seller trust
print("\n[MISMATCH CHECK] listing.trust_score vs seller stored trust")
found = 0
for r in rows:
    em = r["seller_email"].lower()
    st = sel_trust.get(em, {})
    seller_vals = [v for v in st.values() if isinstance(v, (int, float))]
    if seller_vals and r["trust_score"] >= 0:
        sv = seller_vals[0]
        if sv != r["trust_score"]:
            found += 1
            print(f"   [{r['id']}] {r['country']} {r['category']}: listing={r['trust_score']} vs seller={sv}  <-- FLICKER SOURCE")
if not found:
    print("   (no numeric seller-trust column to compare, OR all consistent — "
          "if the flicker persists, the seller score is COMPUTED; capture it from the seller CV)")

# coverage
print("\n[coverage] super_example by country x category")
for iso2 in ("ZA","US","GB","AU"):
    cats = [r["category"] for r in rows if r["country"] == iso2]
    print(f"   {iso2}: {len(cats)} -> {sorted(set(cats))}")

conn.close()
print("\n" + "=" * 68)
print("END SUPER-DIAG (nothing was written)")
