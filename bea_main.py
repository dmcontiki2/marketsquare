from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import database
import auth
import storage
import os
import json
import httpx
from PIL import Image
import io
import logging
from datetime import datetime, timezone

app = FastAPI(title="MarketSquare BEA", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_origin_regex=".*",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()


def run_migrations(conn):
    """Add suburbs table and suburb column to listings if not present."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS suburbs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL DEFAULT 'ZA',
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.execute("CREATE INDEX IF NOT EXISTS idx_suburbs_city ON suburbs(city, active)")

    cols = [r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()]
    if "suburb" not in cols:
        conn.execute("ALTER TABLE listings ADD COLUMN suburb TEXT")
        conn.execute("UPDATE listings SET suburb = 'Central' WHERE suburb IS NULL")

    intro_cols = [r[1] for r in conn.execute("PRAGMA table_info(intro_requests)").fetchall()]
    if "buyer_name" not in intro_cols:
        conn.execute("ALTER TABLE intro_requests ADD COLUMN buyer_name TEXT")

    # ── 4-level geographic hierarchy ─────────────────────────
    conn.execute("""CREATE TABLE IF NOT EXISTS geo_countries (
        iso2 TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        region_label TEXT NOT NULL DEFAULT 'Region',
        active INTEGER NOT NULL DEFAULT 1
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS geo_regions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country_iso2 TEXT NOT NULL REFERENCES geo_countries(iso2),
        active INTEGER NOT NULL DEFAULT 1
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS geo_cities (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        region_id INTEGER NOT NULL REFERENCES geo_regions(id),
        country_iso2 TEXT NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS geo_suburbs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        city_id INTEGER NOT NULL REFERENCES geo_cities(id),
        active INTEGER NOT NULL DEFAULT 1
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_geo_regions_country ON geo_regions(country_iso2, active)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_geo_cities_region ON geo_cities(region_id, active)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_geo_suburbs_city ON geo_suburbs(city_id, active)")

    # ── Lat/lng for proximity search ────────────────────────
    city_cols = [r[1] for r in conn.execute("PRAGMA table_info(geo_cities)").fetchall()]
    if "lat" not in city_cols:
        conn.execute("ALTER TABLE geo_cities ADD COLUMN lat REAL")
        conn.execute("ALTER TABLE geo_cities ADD COLUMN lng REAL")
    suburb_cols = [r[1] for r in conn.execute("PRAGMA table_info(geo_suburbs)").fetchall()]
    if "lat" not in suburb_cols:
        conn.execute("ALTER TABLE geo_suburbs ADD COLUMN lat REAL")
        conn.execute("ALTER TABLE geo_suburbs ADD COLUMN lng REAL")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_geo_suburbs_name_city ON geo_suburbs(name, city_id)")

    listing_cols = [r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()]
    if "geo_city_id" not in listing_cols:
        conn.execute("ALTER TABLE listings ADD COLUMN geo_city_id INTEGER")
    if "service_class" not in listing_cols:
        conn.execute("ALTER TABLE listings ADD COLUMN service_class TEXT")

    # ── Advert Agent columns on users ───────────────────────────
    user_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "aa_free_used" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN aa_free_used INTEGER DEFAULT 0")
    if "aa_sessions_remaining" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN aa_sessions_remaining INTEGER DEFAULT 0")

    conn.commit()


def seed_geo_za(conn):
    """Seed ZA geographic hierarchy from GeoNames data dump. Skipped if geo_countries is already populated."""
    import urllib.request
    import zipfile

    count = conn.execute("SELECT COUNT(*) FROM geo_countries").fetchone()[0]
    if count > 0:
        return

    _log.info("Seeding ZA geographic data from GeoNames dump...")
    zip_path = "/tmp/geonames_za.zip"
    try:
        urllib.request.urlretrieve("https://download.geonames.org/export/dump/ZA.zip", zip_path)
    except Exception as exc:
        _log.error("Failed to download GeoNames ZA dump: %s", exc)
        return

    try:
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open("ZA.txt") as f:
                lines = f.read().decode("utf-8").splitlines()
    except Exception as exc:
        _log.error("Failed to parse GeoNames ZA dump: %s", exc)
        return
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    conn.execute(
        "INSERT OR IGNORE INTO geo_countries (iso2, name, region_label) VALUES (?, ?, ?)",
        ("ZA", "South Africa", "Province")
    )

    adm1 = {}    # admin1_code -> name
    cities = []  # {name, admin1, admin2, code}
    ppls = []    # {name, admin1, admin2}

    for line in lines:
        cols = line.split("\t")
        if len(cols) < 15:
            continue
        name        = cols[1]
        feat_cls    = cols[6]
        feat_code   = cols[7]
        admin1_code = cols[10]
        admin2_code = cols[11]
        lat = float(cols[4]) if cols[4] else None
        lng = float(cols[5]) if cols[5] else None
        if feat_cls == "A" and feat_code == "ADM1":
            adm1[admin1_code] = name
        elif feat_cls == "P" and feat_code in ("PPLC", "PPLA", "PPLA2", "PPLA3"):
            cities.append({"name": name, "lat": lat, "lng": lng, "admin1": admin1_code, "admin2": admin2_code, "code": feat_code})
        elif feat_cls == "P" and feat_code == "PPL":
            ppls.append({"name": name, "lat": lat, "lng": lng, "admin1": admin1_code, "admin2": admin2_code})

    # Pass 1: regions
    region_map = {}  # admin1_code -> region_id
    for code, rname in adm1.items():
        cur = conn.execute("INSERT INTO geo_regions (name, country_iso2) VALUES (?, ?)", (rname, "ZA"))
        region_map[code] = cur.lastrowid

    # Pass 1: cities — PPLA takes priority over PPLA2 for same admin2
    city_map = {}  # (admin1, admin2) -> city_id
    priority = {"PPLC": 0, "PPLA": 1, "PPLA2": 2, "PPLA3": 3}
    for c in sorted(cities, key=lambda x: priority.get(x["code"], 9)):
        region_id = region_map.get(c["admin1"])
        if not region_id:
            continue
        key = (c["admin1"], c["admin2"])
        if key in city_map:
            continue
        cur = conn.execute(
            "INSERT INTO geo_cities (name, region_id, country_iso2, lat, lng) VALUES (?, ?, ?, ?, ?)",
            (c["name"], region_id, "ZA", c["lat"], c["lng"])
        )
        city_map[key] = cur.lastrowid

    # Pass 2: suburbs — link via matching admin1+admin2
    n_suburbs = 0
    for p in ppls:
        city_id = city_map.get((p["admin1"], p["admin2"]))
        if not city_id:
            continue  # no matching city — skip, do not guess
        conn.execute("INSERT INTO geo_suburbs (name, city_id, lat, lng) VALUES (?, ?, ?, ?)",
                     (p["name"], city_id, p["lat"], p["lng"]))
        n_suburbs += 1

    conn.commit()
    _log.info("ZA seed complete: %d provinces, %d cities, %d suburbs",
              len(region_map), len(city_map), n_suburbs)


def migrate_listings_to_geo_city(conn):
    """One-time: set geo_city_id on listings where city name exactly matches geo_cities."""
    rows = conn.execute("SELECT id, city FROM listings WHERE geo_city_id IS NULL").fetchall()
    n = 0
    for row in rows:
        city_row = conn.execute(
            "SELECT id FROM geo_cities WHERE name=? AND active=1 LIMIT 1", (row["city"],)
        ).fetchone()
        if city_row:
            conn.execute("UPDATE listings SET geo_city_id=? WHERE id=?", (city_row["id"], row["id"]))
            n += 1
    if n:
        conn.commit()
        _log.info("Migrated %d listings to geo_city_id", n)


def _backfill_geo_coords(conn):
    """One-time: populate lat/lng on geo_cities and geo_suburbs from GeoNames ZA dump."""
    sample = conn.execute("SELECT lat FROM geo_cities WHERE lat IS NOT NULL LIMIT 1").fetchone()
    if sample:
        return  # already backfilled

    import urllib.request
    import zipfile

    zip_path = "/tmp/geonames_za_coords.zip"
    try:
        urllib.request.urlretrieve("https://download.geonames.org/export/dump/ZA.zip", zip_path)
    except Exception as exc:
        _log.warning("Coord backfill: failed to download ZA dump: %s", exc)
        return

    try:
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open("ZA.txt") as f:
                lines = f.read().decode("utf-8").splitlines()
    except Exception as exc:
        _log.warning("Coord backfill: failed to parse ZA dump: %s", exc)
        return
    finally:
        if os.path.exists(zip_path):
            os.remove(zip_path)

    # Re-derive mapping from dump
    adm1 = {}       # admin1_code -> name
    cities_data = [] # {name, lat, lng, admin1, admin2, code}
    suburbs_data = [] # {name, lat, lng, admin1, admin2}
    for line in lines:
        cols = line.split("\t")
        if len(cols) < 15:
            continue
        name = cols[1]
        lat = float(cols[4]) if cols[4] else None
        lng = float(cols[5]) if cols[5] else None
        feat_cls = cols[6]
        feat_code = cols[7]
        admin1_code = cols[10]
        admin2_code = cols[11]
        if feat_cls == "A" and feat_code == "ADM1":
            adm1[admin1_code] = name
        elif feat_cls == "P" and feat_code in ("PPLC", "PPLA", "PPLA2", "PPLA3"):
            cities_data.append({"name": name, "lat": lat, "lng": lng,
                                "admin1": admin1_code, "admin2": admin2_code, "code": feat_code})
        elif feat_cls == "P" and feat_code == "PPL":
            suburbs_data.append({"name": name, "lat": lat, "lng": lng,
                                 "admin1": admin1_code, "admin2": admin2_code})

    # Map DB regions by name
    db_regions = conn.execute("SELECT id, name FROM geo_regions WHERE country_iso2='ZA'").fetchall()
    region_name_to_id = {r["name"]: r["id"] for r in db_regions}

    # admin1_code -> region_id
    admin1_to_rid = {}
    for code, rname in adm1.items():
        rid = region_name_to_id.get(rname)
        if rid:
            admin1_to_rid[code] = rid

    # Update cities — match by name + region_id
    priority = {"PPLC": 0, "PPLA": 1, "PPLA2": 2, "PPLA3": 3}
    city_key_map = {}  # (admin1, admin2) -> db city_id
    n_cities = 0
    for c in sorted(cities_data, key=lambda x: priority.get(x["code"], 9)):
        region_id = admin1_to_rid.get(c["admin1"])
        if not region_id:
            continue
        key = (c["admin1"], c["admin2"])
        if key in city_key_map:
            continue
        db_city = conn.execute(
            "SELECT id FROM geo_cities WHERE name=? AND region_id=? AND active=1 LIMIT 1",
            (c["name"], region_id)
        ).fetchone()
        if db_city:
            city_key_map[key] = db_city["id"]
            conn.execute("UPDATE geo_cities SET lat=?, lng=? WHERE id=?",
                         (c["lat"], c["lng"], db_city["id"]))
            n_cities += 1

    # Update suburbs — match by name + city_id
    n_suburbs = 0
    for s in suburbs_data:
        city_id = city_key_map.get((s["admin1"], s["admin2"]))
        if not city_id:
            continue
        result = conn.execute(
            "UPDATE geo_suburbs SET lat=?, lng=? WHERE name=? AND city_id=? AND lat IS NULL",
            (s["lat"], s["lng"], s["name"], city_id))
        n_suburbs += result.rowcount

    conn.commit()
    _log.info("Coord backfill complete: %d cities, %d suburbs updated", n_cities, n_suburbs)


import math

def _haversine_km(lat1, lng1, lat2, lng2):
    """Return distance in km between two lat/lng points (Haversine formula)."""
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLng = math.radians(lng2 - lng1)
    a = (math.sin(dLat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dLng / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


# ── STARTUP LOGGING + ENV CONFIG ─────────────────────────────
logging.basicConfig(level=logging.INFO)
_log = logging.getLogger("bea")

_startup_conn = database.get_db()
run_migrations(_startup_conn)
seed_geo_za(_startup_conn)
migrate_listings_to_geo_city(_startup_conn)
_backfill_geo_coords(_startup_conn)
_startup_conn.close()

# n8n webhook URLs (Task 2 — optional, skip silently if not set)
N8N_WEBHOOK_ACCEPT  = os.getenv("N8N_WEBHOOK_ACCEPT")
N8N_WEBHOOK_DECLINE = os.getenv("N8N_WEBHOOK_DECLINE")
if not N8N_WEBHOOK_ACCEPT:
    _log.warning("N8N_WEBHOOK_ACCEPT not set — intro-accepted emails disabled")
if not N8N_WEBHOOK_DECLINE:
    _log.warning("N8N_WEBHOOK_DECLINE not set — intro-declined emails disabled")

# Hetzner Object Storage (Task 3 — optional, falls back to local /media)
HETZNER_S3_ENDPOINT   = os.getenv("HETZNER_S3_ENDPOINT")
HETZNER_S3_BUCKET     = os.getenv("HETZNER_S3_BUCKET")
HETZNER_S3_ACCESS_KEY = os.getenv("HETZNER_S3_ACCESS_KEY")
HETZNER_S3_SECRET_KEY = os.getenv("HETZNER_S3_SECRET_KEY")
_S3_CONFIGURED = all([HETZNER_S3_ENDPOINT, HETZNER_S3_BUCKET,
                       HETZNER_S3_ACCESS_KEY, HETZNER_S3_SECRET_KEY])
if _S3_CONFIGURED:
    import boto3 as _boto3
    _s3 = _boto3.client(
        "s3",
        endpoint_url=HETZNER_S3_ENDPOINT,
        aws_access_key_id=HETZNER_S3_ACCESS_KEY,
        aws_secret_access_key=HETZNER_S3_SECRET_KEY,
    )
    _log.info("Hetzner Object Storage configured: %s / %s", HETZNER_S3_ENDPOINT, HETZNER_S3_BUCKET)
else:
    _log.warning("Object Storage not configured — using local /media fallback")

# Anthropic — Advert Agent AI Coach
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AA_MODEL = "claude-haiku-4-5-20251001"

# GeoNames username — used in seed_geo_za (ZA dump) and _seed_country_from_geonames (API)
# Default: dmcontiki2. Override via GEONAMES_USERNAME in /etc/environment.

# ── HELPERS ───────────────────────────────────────────────────

def _s3_upload(data: bytes, key: str, content_type: str) -> str:
    """Upload bytes to Hetzner Object Storage; return public URL."""
    _s3.put_object(
        Bucket=HETZNER_S3_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
        ACL="public-read",
    )
    return f"{HETZNER_S3_ENDPOINT}/{HETZNER_S3_BUCKET}/{key}"


async def _fire_webhook(url: str, payload: dict):
    """Fire-and-forget webhook POST — never raises, logs errors only."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception as exc:
        _log.error("Webhook POST to %s failed: %s", url, exc)


# Serve local media files (fallback when Hetzner Object Storage not yet configured)
os.makedirs("/var/www/marketsquare/media", exist_ok=True)
app.mount("/media", StaticFiles(directory="/var/www/marketsquare/media"), name="media")

# ── PHOTO COMPRESSION SETTINGS ─────────────────────────────
THUMB_SIZE   = (400, 300)   # ~100KB target
MEDIUM_SIZE  = (1200, 900)  # ~500KB target
JPEG_QUALITY_THUMB  = 72
JPEG_QUALITY_MEDIUM = 82

# ── MODELS ──────────────────────────────────────────────────

class Listing(BaseModel):
    title: str
    price: Optional[str] = None
    category: str
    city: str
    area: Optional[str] = None
    suburb: Optional[str] = None
    description: Optional[str] = None
    thumb_url: Optional[str] = None
    medium_url: Optional[str] = None
    # Property fields
    prop_type: Optional[str] = None
    beds: Optional[int] = None
    baths: Optional[int] = None
    garages: Optional[int] = None
    # Tutor fields
    subject: Optional[str] = None
    level: Optional[str] = None
    mode: Optional[str] = None
    # Services fields
    service_class: Optional[str] = None   # 'Technical' | 'Casuals'
    service_type: Optional[str] = None
    availability: Optional[str] = None

class User(BaseModel):
    email: str
    name: Optional[str] = None

class IntroRequest(BaseModel):
    listing_id: int
    buyer_email: str
    buyer_name: Optional[str] = None
    message: Optional[str] = None

# ── HEALTH ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "MarketSquare BEA", "version": "1.1.0"}

# ── LISTINGS (public read, protected write) ──────────────────

@app.get("/listings")
def get_listings(city: str = "Pretoria", category: Optional[str] = None, suburb: Optional[str] = None):
    conn = database.get_db()
    clauses = ["l.city = ?"]
    params: list = [city]
    if category:
        clauses.append("l.category = ?")
        params.append(category)
    if suburb:
        clauses.append("l.suburb = ?")
        params.append(suburb)
    where = " AND ".join(clauses)
    rows = conn.execute(
        f"""SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
            FROM listings l
            LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
            WHERE {where} ORDER BY l.created_at DESC LIMIT 50""",
        params
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.post("/listings")
def create_listing(listing: Listing, _key: str = Depends(auth.require_api_key)):
    if not listing.suburb:
        raise HTTPException(status_code=400, detail="suburb is required")
    conn = database.get_db()
    cursor = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description, thumb_url, medium_url, service_class)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (listing.title, listing.price, listing.category, listing.city,
         listing.area, listing.suburb, listing.description, listing.thumb_url, listing.medium_url,
         listing.service_class)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "message": "Listing created successfully"}

@app.delete("/listings/{listing_id}")
def delete_listing(listing_id: int, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    conn.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.commit()
    conn.close()
    return {"message": "Listing deleted"}

# ── GEO HIERARCHY ────────────────────────────────────────────

@app.get("/geo/countries")
def geo_get_countries():
    conn = database.get_db()
    rows = conn.execute(
        "SELECT iso2, name, region_label FROM geo_countries WHERE active=1 ORDER BY name"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/geo/regions")
def geo_get_regions(country: str = "ZA"):
    conn = database.get_db()
    rows = conn.execute(
        "SELECT id, name FROM geo_regions WHERE country_iso2=? AND active=1 ORDER BY name",
        (country,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/geo/cities")
def geo_get_cities(region_id: Optional[int] = None, country: Optional[str] = None):
    conn = database.get_db()
    if region_id:
        rows = conn.execute(
            "SELECT id, name, lat, lng FROM geo_cities WHERE region_id=? AND active=1 ORDER BY name",
            (region_id,)
        ).fetchall()
    elif country:
        rows = conn.execute(
            """SELECT c.id, c.name, c.lat, c.lng, r.name as region_name
               FROM geo_cities c JOIN geo_regions r ON c.region_id=r.id
               WHERE c.country_iso2=? AND c.active=1 ORDER BY c.name""",
            (country,)
        ).fetchall()
    else:
        rows = []
    conn.close()
    return [dict(r) for r in rows]

@app.get("/geo/suburbs")
def geo_get_suburbs(city_id: int):
    conn = database.get_db()
    rows = conn.execute(
        "SELECT id, name, lat, lng FROM geo_suburbs WHERE city_id=? AND active=1 ORDER BY name",
        (city_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/geo/nearby")
def geo_nearby(lat: float, lng: float, radius_km: float = 10.0, limit: int = 20):
    """Return suburbs within radius_km of the given lat/lng, sorted by distance."""
    conn = database.get_db()
    # Bounding-box pre-filter for performance
    lat_range = radius_km / 111.0
    lng_range = radius_km / (111.0 * max(math.cos(math.radians(lat)), 0.01))
    rows = conn.execute("""
        SELECT s.id, s.name, s.city_id, s.lat, s.lng, c.name as city_name
        FROM geo_suburbs s
        JOIN geo_cities c ON s.city_id = c.id
        WHERE s.lat IS NOT NULL
          AND s.lat BETWEEN ? AND ?
          AND s.lng BETWEEN ? AND ?
          AND s.active = 1
    """, (lat - lat_range, lat + lat_range, lng - lng_range, lng + lng_range)).fetchall()
    conn.close()
    results = []
    for r in rows:
        d = _haversine_km(lat, lng, r["lat"], r["lng"])
        if d <= radius_km:
            results.append({
                "id": r["id"], "name": r["name"],
                "city_id": r["city_id"], "city_name": r["city_name"],
                "lat": r["lat"], "lng": r["lng"],
                "distance_km": round(d, 2)
            })
    results.sort(key=lambda x: x["distance_km"])
    return results[:limit]


@app.post("/geo/countries")
def geo_add_country(
    iso2: str,
    name: str,
    region_label: str = "Region",
    background_tasks: BackgroundTasks = None,
    _key: str = Depends(auth.require_api_key)
):
    conn = database.get_db()
    try:
        conn.execute(
            "INSERT INTO geo_countries (iso2, name, region_label) VALUES (?, ?, ?)",
            (iso2.upper(), name, region_label)
        )
        conn.commit()
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="Country already exists or invalid data")
    conn.close()
    if background_tasks:
        background_tasks.add_task(_seed_country_from_geonames, iso2.upper(), name, region_label)
    return {"message": f"Country '{name}' added. Seeding geographic data in background."}


async def _seed_country_from_geonames(iso2: str, name: str, region_label: str):
    """Background task: seed a new country's geo hierarchy from GeoNames API."""
    username = os.getenv("GEONAMES_USERNAME", "dmcontiki2")
    base = "http://api.geonames.org/searchJSON"
    _log.info("GeoNames seeding %s (%s)...", name, iso2)

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(base, params={
                "country": iso2, "featureCode": "ADM1",
                "maxRows": 100, "username": username
            })
            regions_data = r.json().get("geonames", [])
    except Exception as exc:
        _log.warning("GeoNames ADM1 fetch failed for %s: %s", iso2, exc)
        return

    conn = database.get_db()
    try:
        region_map = {}  # adminCode1 -> (region_id, admin1_code)
        for reg in regions_data:
            cur = conn.execute(
                "INSERT INTO geo_regions (name, country_iso2) VALUES (?, ?)",
                (reg["name"], iso2)
            )
            region_map[reg.get("adminCode1", "")] = cur.lastrowid
        conn.commit()
        _log.info("GeoNames: %d regions inserted for %s", len(region_map), iso2)

        # Fetch cities per region
        city_map = {}  # (admin1, admin2) -> city_id
        async with httpx.AsyncClient(timeout=10.0) as client:
            for admin1_code, region_id in region_map.items():
                for feat_code in ("PPLA", "PPLA2"):
                    try:
                        r = await client.get(base, params={
                            "country": iso2, "adminCode1": admin1_code,
                            "featureCode": feat_code, "maxRows": 100,
                            "username": username
                        })
                        for city in r.json().get("geonames", []):
                            key = (admin1_code, city.get("adminCode2", ""))
                            if key in city_map:
                                continue
                            cur = conn.execute(
                                "INSERT INTO geo_cities (name, region_id, country_iso2, lat, lng) VALUES (?, ?, ?, ?, ?)",
                                (city["name"], region_id, iso2,
                                 float(city.get("lat", 0)), float(city.get("lng", 0)))
                            )
                            city_map[key] = cur.lastrowid
                    except Exception as exc:
                        _log.warning("GeoNames %s fetch for %s/%s failed: %s",
                                     feat_code, iso2, admin1_code, exc)
        conn.commit()

        # Fetch suburbs per region, link via admin1+admin2
        n_suburbs = 0
        async with httpx.AsyncClient(timeout=10.0) as client:
            for admin1_code in region_map:
                try:
                    r = await client.get(base, params={
                        "country": iso2, "adminCode1": admin1_code,
                        "featureCode": "PPL", "maxRows": 500,
                        "username": username
                    })
                    for sub in r.json().get("geonames", []):
                        key = (admin1_code, sub.get("adminCode2", ""))
                        city_id = city_map.get(key)
                        if not city_id:
                            continue
                        conn.execute(
                            "INSERT INTO geo_suburbs (name, city_id, lat, lng) VALUES (?, ?, ?, ?)",
                            (sub["name"], city_id,
                             float(sub.get("lat", 0)), float(sub.get("lng", 0)))
                        )
                        n_suburbs += 1
                except Exception as exc:
                    _log.warning("GeoNames PPL fetch for %s/%s failed: %s", iso2, admin1_code, exc)
        conn.commit()
        _log.info("GeoNames seed complete for %s: %d regions, %d cities, %d suburbs",
                  iso2, len(region_map), len(city_map), n_suburbs)
    except Exception as exc:
        _log.error("GeoNames seed failed for %s: %s", iso2, exc)
    finally:
        conn.close()


# ── COMPATIBILITY SHIMS (old /suburbs and /cities) ────────────

@app.get("/suburbs")
def get_suburbs(city: str = "Pretoria"):
    conn = database.get_db()
    city_row = conn.execute(
        "SELECT id FROM geo_cities WHERE name=? AND active=1 LIMIT 1", (city,)
    ).fetchone()
    if city_row:
        rows = conn.execute(
            "SELECT name FROM geo_suburbs WHERE city_id=? AND active=1 ORDER BY name",
            (city_row["id"],)
        ).fetchall()
        conn.close()
        return [r["name"] for r in rows]
    # Fallback: old suburbs table
    rows = conn.execute(
        "SELECT name FROM suburbs WHERE city=? AND active=1 ORDER BY name ASC", (city,)
    ).fetchall()
    conn.close()
    return [r["name"] for r in rows]

@app.get("/cities")
def get_cities(country: Optional[str] = None):
    conn = database.get_db()
    if country:
        rows = conn.execute(
            "SELECT DISTINCT name FROM geo_cities WHERE country_iso2=? AND active=1 ORDER BY name",
            (country,)
        ).fetchall()
        conn.close()
        return [r["name"] for r in rows]
    rows = conn.execute(
        """SELECT c.name, c.country_iso2 as country
           FROM geo_cities c WHERE c.active=1 ORDER BY c.country_iso2, c.name"""
    ).fetchall()
    conn.close()
    grouped: dict = {}
    for r in rows:
        grouped.setdefault(r["country"], []).append(r["name"])
    return grouped


# ── PHOTO UPLOAD ─────────────────────────────────────────────
# Accepts a photo, compresses to thumb + medium, stores both,
# returns URLs. Called by admin tool before creating listing.

@app.post("/listings/photo")
async def upload_listing_photo(
    file: UploadFile = File(...),
    _key: str = Depends(auth.require_api_key)
):
    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp"}
    content_type = file.content_type or "image/jpeg"
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WebP photos accepted")

    raw = await file.read()
    if len(raw) > 20 * 1024 * 1024:  # 20MB hard limit
        raise HTTPException(status_code=400, detail="Photo too large — max 20MB")

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # ── Thumbnail (~100KB) ──────────────────────────────────
    thumb = img.copy()
    thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
    thumb_buf = io.BytesIO()
    thumb.save(thumb_buf, format="JPEG", quality=JPEG_QUALITY_THUMB, optimize=True)
    thumb_bytes = thumb_buf.getvalue()

    # ── Medium (~500KB) ─────────────────────────────────────
    medium = img.copy()
    medium.thumbnail(MEDIUM_SIZE, Image.LANCZOS)
    medium_buf = io.BytesIO()
    medium.save(medium_buf, format="JPEG", quality=JPEG_QUALITY_MEDIUM, optimize=True)
    medium_bytes = medium_buf.getvalue()

    # ── Upload both ─────────────────────────────────────────
    if _S3_CONFIGURED:
        # Upload to Hetzner Object Storage — same URL for thumb and medium
        # (Hetzner does not auto-generate thumbnails)
        orig_name = (file.filename or "photo.jpg").replace(" ", "_")
        key = f"media/{uuid.uuid4().hex}_{orig_name}"
        s3_url = _s3_upload(medium_bytes, key, "image/jpeg")
        return {
            "thumb_url":  s3_url,
            "medium_url": s3_url,
            "thumb_kb":   round(len(thumb_bytes)  / 1024, 1),
            "medium_kb":  round(len(medium_bytes) / 1024, 1),
        }

    # Local /media fallback (used when Object Storage is not configured)
    base = storage.generate_filename("listing")
    thumb_name  = base.replace(".jpg", "_thumb.jpg")
    medium_name = base.replace(".jpg", "_medium.jpg")

    thumb_url  = storage.upload_photo(thumb_bytes,  thumb_name,  "image/jpeg")
    medium_url = storage.upload_photo(medium_bytes, medium_name, "image/jpeg")

    return {
        "thumb_url":  thumb_url,
        "medium_url": medium_url,
        "thumb_kb":   round(len(thumb_bytes)  / 1024, 1),
        "medium_kb":  round(len(medium_bytes) / 1024, 1),
    }

# ── USERS (protected write) ──────────────────────────────────

@app.post("/users")
def create_user(user: User, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    try:
        conn.execute(
            "INSERT INTO users (email, name) VALUES (?,?)",
            (user.email, user.name)
        )
        conn.commit()
    except:
        conn.close()
        raise HTTPException(status_code=400, detail="Email already exists")
    conn.close()
    return {"message": "User created successfully"}

@app.get("/users/{email}")
def get_user(email: str):
    conn = database.get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(row)

@app.delete("/users/{email}")
def delete_user(email: str, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    conn.execute("DELETE FROM users WHERE email = ?", (email,))
    conn.commit()
    conn.close()
    return {"message": "User deleted"}

# ── INTRO REQUESTS ───────────────────────────────────────────
# Intros are buyer-initiated — no API key required to submit.
# Accept/decline are seller actions — protected.

@app.post("/intros")
def create_intro(intro: IntroRequest):
    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro.listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    conn.execute(
        "INSERT INTO intro_requests (listing_id, buyer_email, buyer_name, message) VALUES (?,?,?,?)",
        (intro.listing_id, intro.buyer_email, intro.buyer_name, intro.message)
    )
    conn.commit()
    conn.close()
    return {"message": "Introduction request submitted"}

@app.get("/intros")
def get_all_intros(status: str = "pending"):
    conn = database.get_db()
    rows = conn.execute(
        """SELECT i.*, l.title as listing_title, l.category, l.city
           FROM intro_requests i
           JOIN listings l ON i.listing_id = l.id
           WHERE i.status = ?
           ORDER BY i.created_at DESC""",
        (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/intros/{listing_id}")
def get_intros(listing_id: int):
    conn = database.get_db()
    rows = conn.execute(
        "SELECT * FROM intro_requests WHERE listing_id = ? ORDER BY created_at DESC",
        (listing_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.put("/intros/{intro_id}/accept")
def accept_intro(intro_id: int, background_tasks: BackgroundTasks, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    intro = conn.execute("SELECT * FROM intro_requests WHERE id = ?", (intro_id,)).fetchone()
    if not intro:
        conn.close()
        raise HTTPException(status_code=404, detail="Intro not found")
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro["listing_id"],)).fetchone()
    conn.execute(
        "UPDATE intro_requests SET status = 'accepted', tuppence_charged = 1 WHERE id = ?",
        (intro_id,)
    )
    conn.commit()
    conn.close()
    if N8N_WEBHOOK_ACCEPT:
        payload = {
            "event": "intro_accepted",
            "intro_id": intro_id,
            "listing_id": intro["listing_id"],
            "listing_title": listing["title"] if listing else None,
            "buyer_email": intro["buyer_email"],
            "buyer_name": intro["buyer_name"],
            "seller_display_name": None, # not stored in listings schema
            "city": listing["city"] if listing else None,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_ACCEPT, payload)
    return {"message": "Introduction accepted — 1T charged"}

@app.put("/intros/{intro_id}/decline")
def decline_intro(intro_id: int, background_tasks: BackgroundTasks, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    intro = conn.execute("SELECT * FROM intro_requests WHERE id = ?", (intro_id,)).fetchone()
    if not intro:
        conn.close()
        raise HTTPException(status_code=404, detail="Intro not found")
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (intro["listing_id"],)).fetchone()
    conn.execute(
        "UPDATE intro_requests SET status = 'declined' WHERE id = ?",
        (intro_id,)
    )
    conn.commit()
    conn.close()
    if N8N_WEBHOOK_DECLINE:
        payload = {
            "event": "intro_declined",
            "intro_id": intro_id,
            "listing_id": intro["listing_id"],
            "listing_title": listing["title"] if listing else None,
            "buyer_email": intro["buyer_email"],
            "buyer_name": intro["buyer_name"],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_DECLINE, payload)
    return {"message": "Introduction declined"}

# ── PAYMENTS (Paystack) ──────────────────────────────────────
import payments
import uuid

@app.post("/payment/initialize")
def initialize_payment(email: str, tuppence: int):
    amount_rands = tuppence * 36
    reference = f"ms_tuppence_{uuid.uuid4().hex[:12]}"
    result = payments.initialize_payment(
        email=email,
        amount_rands=amount_rands,
        reference=reference,
        metadata={"tuppence": tuppence, "email": email}
    )
    if result.get("status"):
        return {
            "status": "ok",
            "reference": reference,
            "authorization_url": result["data"]["authorization_url"],
            "tuppence": tuppence,
            "amount_rands": amount_rands
        }
    raise HTTPException(status_code=400, detail="Payment initialization failed")

@app.get("/payment/verify")
def verify_payment(reference: str):
    result = payments.verify_payment(reference)
    if result.get("status") and result["data"]["status"] == "success":
        metadata = result["data"]["metadata"]
        tuppence = metadata.get("tuppence", 0)
        email = metadata.get("email", "")
        conn = database.get_db()
        conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
            (email, "topup", tuppence, f"Tuppence top-up via Paystack · ref {reference}")
        )
        conn.commit()
        conn.close()
        return {"status": "ok", "tuppence_credited": tuppence, "email": email}
    raise HTTPException(status_code=400, detail="Payment verification failed")

@app.get("/payment/test")
def test_payment_connection():
    result = payments.get_balance()
    return {"status": "ok", "paystack_connected": result.get("status", False)}

# ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──

@app.post("/admin/migrate-photos")
def migrate_photos(_key: str = Depends(auth.require_api_key)):
    """Migrate existing local photos to Hetzner Object Storage.
    Idempotent — skips listings already pointing to an S3 URL.
    Does NOT delete local files.
    Returns: { migrated, failed, skipped }
    """
    if not _S3_CONFIGURED:
        raise HTTPException(status_code=503, detail="Object Storage not configured — set HETZNER_S3_* env vars")
    conn = database.get_db()
    rows = conn.execute(
        "SELECT id, thumb_url, medium_url FROM listings WHERE thumb_url LIKE '/media/%'"
    ).fetchall()
    migrated = failed = skipped = 0
    for row in rows:
        listing_id  = row["id"]
        thumb_path  = row["thumb_url"]  or ""
        medium_path = row["medium_url"] or ""
        if not thumb_path.startswith("/media/"):
            skipped += 1
            continue
        try:
            thumb_local = f"/var/www/marketsquare{thumb_path}"
            with open(thumb_local, "rb") as fh:
                thumb_data = fh.read()
            thumb_key = f"media/{uuid.uuid4().hex}_{os.path.basename(thumb_local)}"
            new_thumb = _s3_upload(thumb_data, thumb_key, "image/jpeg")
            # Upload medium separately if it also has a local path
            new_medium = new_thumb
            if medium_path.startswith("/media/"):
                medium_local = f"/var/www/marketsquare{medium_path}"
                if os.path.exists(medium_local):
                    with open(medium_local, "rb") as fh:
                        medium_data = fh.read()
                    medium_key = f"media/{uuid.uuid4().hex}_{os.path.basename(medium_local)}"
                    new_medium = _s3_upload(medium_data, medium_key, "image/jpeg")
            conn.execute(
                "UPDATE listings SET thumb_url = ?, medium_url = ? WHERE id = ?",
                (new_thumb, new_medium, listing_id)
            )
            conn.commit()
            migrated += 1
        except Exception as exc:
            _log.error("Photo migration failed for listing %s: %s", listing_id, exc)
            failed += 1
    conn.close()
    return {"migrated": migrated, "failed": failed, "skipped": skipped}


# ── ADVERT AGENT ─────────────────────────────────────────────

class AACoachRequest(BaseModel):
    email: str
    category: str
    fields: dict
    photo_slots_completed: list


class AAPublishRequest(BaseModel):
    email: str
    category: str
    fields: dict
    coach_output: Optional[str] = None


@app.get("/advert-agent/status")
def aa_status(email: str):
    """Return the seller's free-use flag and coaching sessions remaining."""
    conn = database.get_db()
    row = conn.execute(
        "SELECT aa_free_used, aa_sessions_remaining FROM users WHERE email = ?", (email,)
    ).fetchone()
    conn.close()
    if not row:
        return {"aa_free_used": 0, "aa_sessions_remaining": 0, "registered": False}
    return {
        "aa_free_used": row["aa_free_used"] or 0,
        "aa_sessions_remaining": row["aa_sessions_remaining"] or 0,
        "registered": True,
    }


@app.post("/advert-agent/coach")
async def aa_coach(req: AACoachRequest):
    """Gate check + Claude Haiku call + return coaching output."""
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI Coach not configured")

    conn = database.get_db()
    row = conn.execute(
        "SELECT aa_free_used, aa_sessions_remaining FROM users WHERE email = ?", (req.email,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not registered")

    free_used = row["aa_free_used"] or 0
    sessions  = row["aa_sessions_remaining"] or 0

    if free_used and sessions == 0:
        conn.close()
        raise HTTPException(
            status_code=402,
            detail="No coaching sessions remaining. Purchase an AI Pack (8 sessions · 1T) to continue."
        )

    # Build system prompt — Trust Score is hardcoded per A5 governance
    system_prompt = (
        "You are the MarketSquare Advert Agent — a listing coach that helps sellers "
        "write better classified ads. Your job is to review a seller's draft listing "
        "and return specific, actionable improvements. Be concise. Use bullet points. "
        "Focus on: title clarity, price positioning, description completeness, and "
        "photo guidance for the category. Never fabricate facts about the listing.\n\n"
        "ANONYMITY RULES — confirm these in every response:\n"
        "1. The listing title and description must never contain the seller's name or "
        "business name. The seller's identity is only revealed after both parties accept "
        "a mutual introduction request.\n"
        "2. Phone numbers and email addresses in listing descriptions are ALLOWED — "
        "the MarketSquare platform automatically masks them with a blur and a lock icon "
        "until introduction is accepted. Do NOT ask the seller to remove contact details.\n"
        "3. The seller profile (About, credentials) should describe qualifications, "
        "years of experience, and work history — no personal name or business name.\n"
        "4. Credential certificate photos (e.g. Red Seal, COC, trade licences) are "
        "blurred to buyers until introduction is accepted.\n"
        "5. If the listing contains the seller's actual name or business name, flag it "
        "with: '⚠️ NAME FOUND — remove before publishing: [item]'.\n"
        "6. End every response with: '✓ Anonymity check passed.' or "
        "'⚠️ Name/business identifier found — see above.'"
    )

    fields_text = "\n".join(f"  {k}: {v}" for k, v in req.fields.items() if v)
    user_message = (
        f"Category: {req.category}\n"
        f"Listing details:\n{fields_text}\n"
        f"Photos completed: {', '.join(req.photo_slots_completed) or 'none yet'}\n\n"
        "Please review this listing and give me specific improvements to make it stronger."
    )

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model": AA_MODEL,
                    "max_tokens": 1024,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_message}],
                },
            )
        resp.raise_for_status()
        coaching = resp.json()["content"][0]["text"]
    except Exception as exc:
        conn.close()
        _log.error("AA coach Claude call failed: %s", exc)
        raise HTTPException(status_code=502, detail="AI Coach unavailable — please try again")

    # Deduct session: free first use or paid pack
    if not free_used:
        conn.execute("UPDATE users SET aa_free_used = 1 WHERE email = ?", (req.email,))
    else:
        conn.execute(
            "UPDATE users SET aa_sessions_remaining = aa_sessions_remaining - 1 WHERE email = ?",
            (req.email,)
        )
    conn.commit()
    conn.close()

    return {"coaching": coaching, "sessions_remaining": max(0, sessions - (0 if not free_used else 1))}


@app.post("/advert-agent/buy-pack")
def aa_buy_pack(email: str):
    """Credit seller with 8 coaching sessions (called after successful Tuppence payment)."""
    conn = database.get_db()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not registered")
    conn.execute(
        "UPDATE users SET aa_sessions_remaining = aa_sessions_remaining + 8 WHERE email = ?",
        (email,)
    )
    conn.commit()
    new_bal = conn.execute(
        "SELECT aa_sessions_remaining FROM users WHERE email = ?", (email,)
    ).fetchone()["aa_sessions_remaining"]
    conn.close()
    return {"sessions_remaining": new_bal}


@app.post("/advert-agent/publish")
async def aa_publish(
    email: str = Form(...),
    category: str = Form(...),
    fields: str = Form(...),        # JSON string
    coach_output: str = Form(""),
    photos: list[UploadFile] = File(default=[]),
):
    """Receive draft + photos, upload to R2, create pending listing, return listing id."""
    import json as _json

    try:
        field_data = _json.loads(fields)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid fields JSON")

    title         = field_data.get("title") or field_data.get("item_name", "")
    price         = field_data.get("price") or field_data.get("rate")
    suburb        = field_data.get("suburb") or field_data.get("area", "")
    desc          = field_data.get("desc", "")
    service_class = field_data.get("service_class") or None

    if coach_output:
        desc = f"{desc}\n\n---\nAI coaching notes:\n{coach_output}".strip()

    # Upload photos to R2 (or local fallback)
    thumb_url  = None
    medium_url = None
    for idx, photo in enumerate(photos):
        data = await photo.read()
        if _S3_CONFIGURED:
            key = f"aa/{uuid.uuid4().hex}_{photo.filename or f'photo_{idx}.jpg'}"
            url = _s3_upload(data, key, photo.content_type or "image/jpeg")
        else:
            fname = f"aa_{uuid.uuid4().hex}.jpg"
            local_path = f"/var/www/marketsquare/media/{fname}"
            try:
                with open(local_path, "wb") as fh:
                    fh.write(data)
                url = f"/media/{fname}"
            except Exception:
                url = None
        if url and idx == 0:
            thumb_url  = url
            medium_url = url

    conn = database.get_db()
    cursor = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description, thumb_url, medium_url, service_class)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (title, price, category, "Pretoria", suburb, suburb, desc, thumb_url, medium_url, service_class),
    )
    listing_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {"listing_id": listing_id, "pdf_url": None}  # PDF generation added in Stage 4
