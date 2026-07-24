"""
expand_adventure_super_photos.py — ADV-SUPER-PHOTOS-1 (24 Jul 2026, David)
==========================================================================
Idempotent, DB-backed, dry-run-first. Adds the 5 new Higgsfield photos to each
of the two Adventures SUPER ADVERT exemplars, extending both photo carriers:
  - photo_urls           (JSON array column)
  - [photos:a|b|...] prefix on description

Listings are matched by super_example=1 + category (NOT hardcoded id), so it is
safe across environments. Only paths not already present are appended, so
re-running is a no-op. New image files ship via deploy step 3d (assets/super ->
/static/super).

Run ON THE SERVER:  python3 expand_adventure_super_photos.py           (dry-run)
                    python3 expand_adventure_super_photos.py --apply   (backs up DB, writes)
"""
import os, sys, json, shutil, sqlite3, re
from datetime import datetime

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found — set MS_DB_PATH=/path/to/marketsquare.db")
APPLY = "--apply" in sys.argv

# category -> ordered new photo paths to append
NEW = {
    "adventures_experiences": [
        "/static/super/sup_advexp_4_lions.jpg",
        "/static/super/sup_advexp_5_leopard.jpg",
        "/static/super/sup_advexp_6_buffalo.jpg",
        "/static/super/sup_advexp_7_snake_meerkat.jpg",
        "/static/super/sup_advexp_8_rhino.jpg",
    ],
    "adventures_accommodation": [
        "/static/super/sup_advacc_4_bar.jpg",
        "/static/super/sup_advacc_5_braai.jpg",
        "/static/super/sup_advacc_6_boma.jpg",
        "/static/super/sup_advacc_7_lounge.jpg",
        "/static/super/sup_advacc_8_sunrise.jpg",
    ],
}
PREFIX_RE = re.compile(r"^\[photos:([^\]]*)\]")

def parse_urls(s):
    try:
        v = json.loads(s or "[]"); return v if isinstance(v, list) else []
    except Exception:
        return []

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
cols = {r[1] for r in conn.execute("PRAGMA table_info(listings)")}
if "super_example" not in cols:
    sys.exit("No super_example column — wrong DB.")

plan = []
for cat, adds in NEW.items():
    for row in conn.execute(
        "SELECT * FROM listings WHERE COALESCE(super_example,0)=1 AND category=?", (cat,)):
        r = dict(row); lid = r["id"]; desc = r.get("description") or ""
        # 1) photo_urls array
        urls = parse_urls(r.get("photo_urls"))
        new_urls = urls + [u for u in adds if u not in urls]
        # 2) [photos:...] prefix
        m = PREFIX_RE.match(desc)
        if m:
            existing = [x for x in m.group(1).split("|") if x]
            merged = existing + [u for u in adds if u not in existing]
            new_desc = "[photos:" + "|".join(merged) + "]" + desc[m.end():]
        else:
            merged = list(adds)
            new_desc = "[photos:" + "|".join(adds) + "]\n" + desc
        changed = (new_urls != urls) or (new_desc != desc)
        plan.append((lid, r.get("title"), cat, len(urls), len(new_urls),
                     len(existing) if m else 0, len(merged),
                     new_urls, new_desc, changed))

print("DB:", DB, "| mode:", "APPLY" if APPLY else "DRY-RUN")
for lid, title, cat, o_u, n_u, o_p, n_p, nu, nd, ch in plan:
    print("="*70)
    print(f"[{lid}] {cat} | {str(title)[:52]}")
    print(f"   photo_urls: {o_u} -> {n_u}   [photos:] gallery: {o_p} -> {n_p}   changed={ch}")
    print(f"   photo_urls now: {nu}")
    print(f"   desc prefix now: {nd[:200]}")

if APPLY and any(p[-1] for p in plan):
    bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-advphotos"
    shutil.copy2(DB, bak); print("\nDB backed up ->", bak)
    for lid, title, cat, o_u, n_u, o_p, n_p, nu, nd, ch in plan:
        if not ch: continue
        conn.execute("UPDATE listings SET photo_urls=?, description=? WHERE id=?",
                     (json.dumps(nu), nd, lid))
    conn.commit()
    try:
        conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')"); conn.commit()
        print("FTS rebuilt.")
    except Exception as e:
        print("FTS rebuild skipped:", e)
    print("APPLIED.")
elif APPLY:
    print("\nNothing to apply (already up to date).")
else:
    print("\nDRY-RUN only — rerun with --apply to write.")
conn.close()
