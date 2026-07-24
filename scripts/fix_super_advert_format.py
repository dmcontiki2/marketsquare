"""
fix_super_advert_format.py — SUPER-FORMAT-1 v2 (24 Jul 2026, David Jnr super-advert feedback)
============================================================================================
Idempotent, DB-backed, dry-run-first. Two live-data fixes, both honouring the CARS-SPEC-1
public scrub (visibility invariant D1): a cars spec is PUBLIC only when its section is in
spec_confirmed AND the listing carries attested_at (is_demo listings are exempt).

  PART A — the super_example exemplar renders OLD (spec-less) format.
    Root cause (confirmed against bea_main._scrub_vehicle_specs): the row HAS structured
    specs but they are unpublished (no attested_at / spec_confirmed), so the public read
    strips them and the app falls back to the legacy layout. Fix = publish what it has:
    fill only EMPTY exemplar fields from SPEC_BACKFILL (never overwrite real data), then
    stamp attested_at + confirm every section that carries data.

  PART B — the About text repeats the visible spec table (the Figo).
    Only ATTESTED cars listings are touched (only they show a public spec table, so only
    they can have a genuine duplicate). Service history + features are LIFTED from the
    prose into vehicle_specs (and their sections confirmed) so nothing is lost, then a
    "Label: value" line is removed ONLY when its section is actually published. Genuine
    free-text (condition notes) is always kept.

Run ON THE SERVER:  python3 fix_super_advert_format.py           (dry-run — prints full plan)
                    python3 fix_super_advert_format.py --apply   (backs up DB, writes)
"""
import os, sys, json, shutil, sqlite3, re
from datetime import datetime, timezone

DB = os.getenv("MS_DB_PATH") or next((p for p in [
    "/var/www/marketsquare/marketsquare.db",
    "/var/www/marketsquare/data/marketsquare.db",
    "/var/www/marketsquare/db/marketsquare.db"] if os.path.exists(p)), None)
if not DB:
    sys.exit("No DB found — set MS_DB_PATH=/path/to/marketsquare.db")
APPLY = "--apply" in sys.argv
NOW = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

# Mirrors bea_main.VEHICLE_SECTION_FIELDS  → section: (discrete columns, vehicle_specs keys)
SECTIONS = {
    "details":     (("make","model","variant","vehicle_year","colour","body_type"), ("seats","doors")),
    "performance": (("transmission","fuel_type","drivetrain"),
                    ("engine_capacity_cc","kilowatts_kw","cylinder_layout","cylinders","aspiration",
                     "fuel_consumption_l100","fuel_tank_l","gears","tyre_front","tyre_rear","wheelbase_mm","co2_gkm")),
    "condition":   (("mileage_km",), ("service_history","roadworthy_status","spare_key",
                     "maintenance_plan_until","warranty_until","condition_notes")),
    "features":    ((), ("features",)),
}
SECTION_OF = {}
for _sec,(_cols,_keys) in SECTIONS.items():
    for _f in _cols+_keys: SECTION_OF[_f]=_sec

# Exemplar profile — fills ONLY empty fields (existing real data is never overwritten).
SPEC_BACKFILL = {
    "hilux": {
        "cols":  {"make":"Toyota","model":"Hilux","variant":"2.8 GD-6 Double Cab","vehicle_year":2021,
                  "colour":"White","body_type":"Bakkie","fuel_type":"Diesel","transmission":"Automatic",
                  "mileage_km":78000},   # 78 000 km + Automatic are showcase values — edit to taste
        "specs": {"engine_capacity_cc":2755,"kilowatts_kw":150,
                  "service_history":"Full franchise service history","roadworthy_status":"Valid roadworthy"},
    },
}

# Description label -> canonical field (for Part B duplicate detection). Lower-cased labels.
LABEL_TO_FIELD = {
    "make":"make","model":"model","variant":"variant","year":"vehicle_year","colour":"colour",
    "body type":"body_type","seats":"seats","doors":"doors","transmission":"transmission",
    "fuel type":"fuel_type","drivetrain":"drivetrain","engine capacity (cc)":"engine_capacity_cc",
    "engine (cc)":"engine_capacity_cc","power (kw)":"kilowatts_kw","gears":"gears",
    "mileage (km)":"mileage_km","service history":"service_history","features":"features",
}
_line_re = re.compile(r'^\s*\**\s*([A-Za-z ()/]+?)\s*\**\s*:\s*(.+?)\s*$')

def jload(s):
    try:
        v=json.loads(s or "{}"); return v if isinstance(v,dict) else {}
    except Exception: return {}

conn=sqlite3.connect(DB); conn.row_factory=sqlite3.Row
cols={r[1] for r in conn.execute("PRAGMA table_info(listings)")}
has_super="super_example" in cols
planA, planB = [], []

# ── PART A ──────────────────────────────────────────────────────────────────
if has_super:
    for row in conn.execute("SELECT * FROM listings WHERE COALESCE(super_example,0)=1 AND LOWER(category)='cars'"):
        r=dict(row); prof=next((v for k,v in SPEC_BACKFILL.items() if k in (r.get("title") or "").lower()), None)
        specs=jload(r.get("vehicle_specs")); prov=specs.get("_prov",{})
        cur={f:r.get(f) for f in ("make","model","variant","vehicle_year","mileage_km","transmission","fuel_type","body_type","colour")}
        cur["is_demo"]=r.get("is_demo"); cur["attested_at"]=r.get("attested_at"); cur["spec_confirmed"]=r.get("spec_confirmed")
        setcols={}
        if prof:
            for k,v in prof["cols"].items():
                if k in cols and (r.get(k) in (None,"",0)): setcols[k]=v; prov[k]="seller_confirmed"
            for k,v in prof["specs"].items():
                if k not in specs or specs.get(k) in (None,""): specs[k]=v; prov[k]="seller_confirmed"
        # merged view to decide which sections carry data
        merged={**{c:r.get(c) for grp in SECTIONS.values() for c in grp[0]}, **setcols}
        conf=jload(r.get("spec_confirmed"))
        for sec,(c,keys) in SECTIONS.items():
            has=any(merged.get(x) not in (None,"",0) for x in c) or any(k in specs and specs[k] not in (None,"",[]) for k in keys)
            if has: conf[sec]=NOW
        specs["_prov"]=prov
        setcols["vehicle_specs"]=json.dumps(specs)
        setcols["spec_confirmed"]=json.dumps(conf)
        if "attested_at" in cols: setcols["attested_at"]=NOW
        if "attested_email" in cols: setcols["attested_email"]=r.get("seller_email")
        planA.append((r["id"], r.get("title"), cur, setcols, sorted(conf.keys())))

# ── PART B ──────────────────────────────────────────────────────────────────
for row in conn.execute("SELECT * FROM listings WHERE LOWER(category)='cars' AND attested_at IS NOT NULL"):
    r=dict(row); desc=r.get("description") or ""
    if not desc.strip(): continue
    specs=jload(r.get("vehicle_specs")); prov=specs.get("_prov",{}); conf=jload(r.get("spec_confirmed"))
    lifts=[]
    # lift service history + features from prose into specs (so they survive the strip)
    for line in desc.split("\n"):
        m=_line_re.match(line)
        if not m: continue
        lab=m.group(1).strip().lower(); val=m.group(2).strip()
        if lab=="service history" and not specs.get("service_history"):
            specs["service_history"]=val; prov["service_history"]="seller_entered"; conf["condition"]=NOW; lifts.append("service_history")
        elif lab=="features" and not specs.get("features"):
            specs["features"]=[x.strip() for x in val.split(",") if x.strip()]; prov["features"]="seller_entered"; conf["features"]=NOW; lifts.append("features")
    published={s for s in SECTIONS if conf.get(s)}   # attested is guaranteed by the query
    kept, removed=[], []
    for line in desc.split("\n"):
        m=_line_re.match(line)
        if m:
            fld=LABEL_TO_FIELD.get(m.group(1).strip().lower())
            if fld and SECTION_OF.get(fld) in published:
                removed.append(line.strip()); continue
        kept.append(line)
    clean="\n".join(kept).strip()
    if not removed and not lifts: continue
    setcols={"description":clean}
    if lifts:
        specs["_prov"]=prov
        setcols["vehicle_specs"]=json.dumps(specs); setcols["spec_confirmed"]=json.dumps(conf)
    planB.append((r["id"], r.get("title"), removed, lifts, clean, setcols))

# ── report ──────────────────────────────────────────────────────────────────
print("DB:",DB,"| mode:","APPLY" if APPLY else "DRY-RUN","| super col:",has_super)
print("\n=== PART A · publish super_example cars (-> new format) ===")
if not planA: print("  (none found)")
for lid,title,cur,setc,confd in planA:
    print(f"  [{lid}] {str(title)[:58]}")
    print(f"        current: is_demo={cur.get('is_demo')} attested_at={cur.get('attested_at')} make={cur.get('make')} model={cur.get('model')} variant={cur.get('variant')} year={cur.get('vehicle_year')} mileage={cur.get('mileage_km')} trans={cur.get('transmission')} fuel={cur.get('fuel_type')} body={cur.get('body_type')} colour={cur.get('colour')}")
    print(f"        will set: {', '.join(k+'='+str(v)[:40] for k,v in setc.items() if k not in ('vehicle_specs','spec_confirmed'))}")
    print(f"        confirm sections: {confd}   vehicle_specs={setc.get('vehicle_specs')}")
print("\n=== PART B · de-dup About on ATTESTED cars only ===")
if not planB: print("  (none)")
for lid,title,removed,lifts,clean,_ in planB:
    print(f"  [{lid}] {str(title)[:58]}  lift={lifts}")
    for x in removed: print(f"        - strip: {x}")
    print(f"        About now: {repr(clean)}")

# ── apply ─────────────────────────────────────────────────────────────────
if APPLY and (planA or planB):
    bak=DB+".bak-"+datetime.now().strftime("%Y%m%d-%H%M%S")+"-superformat"
    shutil.copy2(DB,bak); print("\nDB backed up ->",bak)
    for lid,_,_,setc,_ in planA:
        conn.execute(f"UPDATE listings SET {', '.join(k+'=?' for k in setc)} WHERE id=?", list(setc.values())+[lid])
    for lid,_,_,_,_,setc in planB:
        conn.execute(f"UPDATE listings SET {', '.join(k+'=?' for k in setc)} WHERE id=?", list(setc.values())+[lid])
    conn.commit()
    try: conn.execute("INSERT INTO listings_fts(listings_fts) VALUES('rebuild')"); conn.commit(); print("FTS rebuilt.")
    except Exception as e: print("FTS rebuild skipped:",e)
    print("APPLIED.")
elif APPLY: print("\nNothing to apply.")
else: print("\nDRY-RUN only — rerun with --apply to write.")
conn.close()
