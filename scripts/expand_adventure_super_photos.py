"""
expand_adventure_super_photos.py — ADV-SUPER-PHOTOS-1 + ADV-SAFE-1 (24 Jul 2026, David)
=======================================================================================
Idempotent, DB-backed, dry-run-first. TWO safe changes to the two Adventures SUPER ADVERT
exemplars (matched by super_example=1 + category, never hardcoded id):

  1) PHOTOS  — append the 5 new Higgsfield photos to each listing's photo_urls (JSON) AND
     its [photos:a|b|...] description prefix (270 & 271 go 3 -> 8). New files ship via
     deploy step 3d (assets/super -> /static/super).

  2) SAFE PASS (Option A) — genericise real-place references so an exemplar is never mistaken
     for, or implies affiliation with, a real business/reserve: 'Dinokeng' -> generic in the
     title/description, and the 'Dinokeng' suburb field cleared. Province (Gauteng) and city
     (Pretoria) are generic locators and are kept. Standing rule: super adverts always err safe.

Idempotent: every step only changes what still needs changing; a second run is a clean no-op.

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

def genericise_text(s):
    """Remove specific real-reserve names; keep province/city locators."""
    if not s: return s
    out = s.replace("Dinokeng's", "the reserve's").replace("Dinokeng Game Reserve", "the reserve")
    out = out.replace("Dinokeng", "Gauteng")   # any residual name -> province locator
    return out

conn = sqlite3.connect(DB); conn.row_factory = sqlite3.Row
cols = {r[1] for r in conn.execute("PRAGMA table_info(listings)")}
if "super_example" not in cols:
    sys.exit("No super_example column — wrong DB.")

plan = []
for cat, adds in NEW.items():
    for row in conn.execute(
        "SELECT * FROM listings WHERE COALESCE(super_example,0)=1 AND category=?", (cat,)):
        r = dict(row); lid = r["id"]; desc = r.get("description") or ""
        title = r.get("title") or ""; suburb = r.get("suburb") or ""
        # 1) photo_urls
        urls = parse_urls(r.get("photo_urls"))
        new_urls = urls + [u for u in adds if u not in urls]
        # 2) [photos:] prefix
        m = PREFIX_RE.match(desc)
        if m:
            existing = [x for x in m.group(1).split("|") if x]
            merged = existing + [u for u in adds if u not in existing]
            new_desc = "[photos:" + "|".join(merged) + "]" + desc[m.end():]
        else:
            existing = []
            merged = list(adds)
            new_desc = "[photos:" + "|".join(adds) + "]\n" + desc
        # 3) SAFE PASS — genericise title/desc/suburb
        new_title = genericise_text(title)
        new_desc = genericise_text(new_desc)
        new_suburb = "" if "dinokeng" in suburb.lower() else suburb
        sets = {}
        if new_urls != urls:   sets["photo_urls"] = json.dumps(new_urls)
        if new_desc != desc:   sets["description"] = new_desc
        if new_title != title: sets["title"] = new_title
        if new_suburb != suburb: sets["suburb"] = new_suburb
        plan.append((lid, title, new_title, cat, len(urls), len(new_urls),
                     len(existing), len(merged), suburb, new_suburb, sets, new_desc))

print("DB:", DB, "| mode:", "APPLY" if APPLY else "DRY-RUN")
for lid, ot, nt, cat, ou, nu, op, npc, osub, nsub, sets, nd in plan:
    print("="*70)
    print(f"[{lid}] {cat}")
    if "title" in sets: print(f"   title : {ot!r}\n        -> {nt!r}")
    print(f"   photos: photo_urls {ou}->{nu}  [photos:] {op}->{npc}")
    if "suburb" in sets: print(f"   suburb: {osub!r} -> {nsub!r}")
    print(f"   changes: {sorted(sets.keys())}")

if APPLY and any(p[10] for p in plan):
    bak = DB + ".bak-" + datetime.now().strftime("%Y%m%d-%H%M%S") + "-advsafe"
    shutil.copy2(DB, bak); print("\nDB backed up ->", bak)
    for lid, ot, nt, cat, ou, nu, op, npc, osub, nsub, sets, nd in plan:
        if not sets: continue
        conn.execute(f"UPDATE listings SET {', '.join(k+'=?' for k in sets)} WHERE id=?",
                     list(sets.values()) + [lid])
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
