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

app = FastAPI(title="MarketSquare BEA", version="1.2.0")

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
    if "seller_email" not in listing_cols:
        conn.execute("ALTER TABLE listings ADD COLUMN seller_email TEXT")
    if "updated_at" not in listing_cols:
        conn.execute("ALTER TABLE listings ADD COLUMN updated_at TEXT")
    # ── Category-specific edit fields (ListingUpdate) ────────────
    for _col, _type in [
        ("trust_score",  "INTEGER"),
        ("beds",         "INTEGER"),
        ("baths",        "INTEGER"),
        ("garages",      "INTEGER"),
        ("prop_type",    "TEXT"),
        ("floor_area",   "INTEGER"),
        ("erf_size",     "INTEGER"),
        ("listing_type", "TEXT"),
        ("subject",      "TEXT"),
        ("level",        "TEXT"),
        ("mode",         "TEXT"),
        ("service_type", "TEXT"),
        ("availability", "TEXT"),
    ]:
        if _col not in listing_cols:
            conn.execute(f"ALTER TABLE listings ADD COLUMN {_col} {_type}")

    # ── Listing version history (audit trail for edits) ──────────
    conn.execute("""CREATE TABLE IF NOT EXISTS listing_versions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id INTEGER NOT NULL,
        version_num INTEGER NOT NULL DEFAULT 1,
        changed_by TEXT,
        changed_at TEXT DEFAULT (datetime('now')),
        snapshot_json TEXT NOT NULL
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lv_listing ON listing_versions(listing_id, version_num)")

    # ── Advert Agent columns on users ───────────────────────────
    user_cols = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "aa_free_used" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN aa_free_used INTEGER DEFAULT 0")
    if "aa_sessions_remaining" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN aa_sessions_remaining INTEGER DEFAULT 0")
    if "photo_url" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN photo_url TEXT")
    if "buyer_token" not in user_cols:
        conn.execute("ALTER TABLE users ADD COLUMN buyer_token TEXT")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_users_buyer_token ON users(buyer_token)")

    # ── Wishlist Feed feature (v1.2.0) ──────────────────────────
    # Per-buyer signals: implicit (browse_search/browse_view) + explicit
    conn.execute("""CREATE TABLE IF NOT EXISTS wishlist_signals (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_token     TEXT NOT NULL,
        signal_type     TEXT NOT NULL,
        raw_text        TEXT,
        category        TEXT,
        suburb_id       INTEGER,
        city_id         INTEGER,
        country_iso2    TEXT,
        price_min       REAL,
        price_max       REAL,
        min_trust_score INTEGER NOT NULL DEFAULT 0,
        weight          REAL NOT NULL DEFAULT 1.0,
        ping_enabled    INTEGER NOT NULL DEFAULT 1,
        created_at      TEXT NOT NULL DEFAULT (datetime('now')),
        expires_at      TEXT NOT NULL
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ws_buyer ON wishlist_signals(buyer_token)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ws_category ON wishlist_signals(category)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ws_expires ON wishlist_signals(expires_at)")

    # Match queue per buyer — populated by the matching job
    conn.execute("""CREATE TABLE IF NOT EXISTS wishlist_matches (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_token     TEXT NOT NULL,
        listing_id      INTEGER NOT NULL,
        signal_id       INTEGER,
        match_score     REAL NOT NULL,
        seller_trust    INTEGER NOT NULL DEFAULT 0,
        matched_at      TEXT NOT NULL DEFAULT (datetime('now')),
        seen            INTEGER NOT NULL DEFAULT 0,
        pinged          INTEGER NOT NULL DEFAULT 0,
        boost_rank      INTEGER NOT NULL DEFAULT 0,
        UNIQUE(buyer_token, listing_id)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wm_buyer ON wishlist_matches(buyer_token, matched_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wm_listing ON wishlist_matches(listing_id)")

    # Wearable / web-push device registrations
    conn.execute("""CREATE TABLE IF NOT EXISTS wearable_devices (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_token     TEXT NOT NULL,
        push_endpoint   TEXT NOT NULL,
        push_keys       TEXT NOT NULL,
        platform        TEXT NOT NULL,
        device_label    TEXT,
        enabled         INTEGER NOT NULL DEFAULT 1,
        created_at      TEXT NOT NULL DEFAULT (datetime('now')),
        last_ping_at    TEXT,
        UNIQUE(buyer_token, push_endpoint)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_wd_buyer ON wearable_devices(buyer_token, enabled)")

    # Editorially curated showcase scroll for empty-state buyers
    conn.execute("""CREATE TABLE IF NOT EXISTS wishlist_showcase (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id      INTEGER NOT NULL UNIQUE,
        sort_order      INTEGER NOT NULL DEFAULT 0,
        added_at        TEXT NOT NULL DEFAULT (datetime('now')),
        added_by        TEXT NOT NULL DEFAULT 'admin'
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_show_order ON wishlist_showcase(sort_order)")

    # Buyer subscription tier — controls geographic reach of the wishlist feed
    conn.execute("""CREATE TABLE IF NOT EXISTS wishlist_subscriptions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_token     TEXT NOT NULL UNIQUE,
        tier            TEXT NOT NULL DEFAULT 'free',
        activated_at    TEXT,
        expires_at      TEXT,
        paystack_ref    TEXT
    )""")

    # Listing publish timestamp + boost columns for the matching job
    listing_cols2 = [r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()]
    if "published_at" not in listing_cols2:
        conn.execute("ALTER TABLE listings ADD COLUMN published_at TEXT")
        conn.execute("UPDATE listings SET published_at = COALESCE(created_at, datetime('now')) WHERE published_at IS NULL")
    if "boost_until" not in listing_cols2:
        conn.execute("ALTER TABLE listings ADD COLUMN boost_until TEXT")
    if "view_count" not in listing_cols2:
        conn.execute("ALTER TABLE listings ADD COLUMN view_count INTEGER NOT NULL DEFAULT 0")

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
N8N_WEBHOOK_ACCEPT     = os.getenv("N8N_WEBHOOK_ACCEPT")
N8N_WEBHOOK_DECLINE    = os.getenv("N8N_WEBHOOK_DECLINE")
N8N_WEBHOOK_NEW_INTRO  = os.getenv("N8N_WEBHOOK_NEW_INTRO")
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
    # Trust
    trust_score: Optional[int] = None
    seller_email: Optional[str] = None

class User(BaseModel):
    email: str
    name: Optional[str] = None

class ListingUpdate(BaseModel):
    """Partial update model for seller edits — all fields optional."""
    title: Optional[str] = None
    price: Optional[str] = None
    description: Optional[str] = None
    suburb: Optional[str] = None
    area: Optional[str] = None
    prop_type: Optional[str] = None
    beds: Optional[int] = None
    baths: Optional[int] = None
    garages: Optional[int] = None
    floor_area: Optional[int] = None
    erf_size: Optional[int] = None
    listing_type: Optional[str] = None
    subject: Optional[str] = None
    level: Optional[str] = None
    mode: Optional[str] = None
    service_class: Optional[str] = None
    service_type: Optional[str] = None
    availability: Optional[str] = None

class IntroRequest(BaseModel):
    listing_id: int
    buyer_email: str
    buyer_name: Optional[str] = None
    message: Optional[str] = None

# ── HEALTH ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "MarketSquare BEA", "version": "1.2.0"}

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
def create_listing(listing: Listing, background_tasks: BackgroundTasks, _key: str = Depends(auth.require_api_key)):
    if not listing.suburb:
        raise HTTPException(status_code=400, detail="suburb is required")
    conn = database.get_db()
    cursor = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description, thumb_url, medium_url,
            service_class, prop_type, beds, baths, garages,
            subject, level, mode, service_type, availability,
            trust_score, seller_email, published_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))""",
        (listing.title, listing.price, listing.category, listing.city,
         listing.area, listing.suburb, listing.description, listing.thumb_url, listing.medium_url,
         listing.service_class, listing.prop_type, listing.beds, listing.baths, listing.garages,
         listing.subject, listing.level, listing.mode, listing.service_type, listing.availability,
         listing.trust_score, listing.seller_email)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    # Wishlist matching — async, never blocks publish (PR-14)
    background_tasks.add_task(run_match_job, new_id)
    return {"id": new_id, "message": "Listing created successfully"}

@app.get("/listings/mine")
def get_seller_listings(email: str):
    """Return all listings for this seller email — no auth key required."""
    conn = database.get_db()
    rows = conn.execute(
        """SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
           FROM listings l
           LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
           WHERE l.seller_email = ? ORDER BY l.created_at DESC""",
        (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/listings/{listing_id}")
def get_listing(listing_id: int):
    """Fetch a single listing by ID."""
    conn = database.get_db()
    row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return dict(row)

@app.put("/listings/{listing_id}")
def update_listing(listing_id: int, update: ListingUpdate, background_tasks: BackgroundTasks, email: Optional[str] = None):
    """Update a published listing.
    Auth: ?email= must match seller_email on the listing.
    If seller_email is NULL (admin-created listing with no owner yet), any email is
    accepted and stamped onto the listing — this covers the testing / founding-seller
    workflow where listings are created via the admin tool before sellers claim them.
    Archives the current state as a version before applying changes (audit trail).
    Changes go live immediately.
    """
    conn = database.get_db()
    existing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")

    if not email:
        conn.close()
        raise HTTPException(status_code=401, detail="Seller email required — pass ?email=your@email.com")

    # If listing has no seller_email yet (admin-created), accept the supplied email
    # and stamp it — first editor becomes the owner.
    if not existing["seller_email"]:
        conn.execute("UPDATE listings SET seller_email = ? WHERE id = ?", (email, listing_id))
    elif existing["seller_email"] != email:
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorised to edit this listing")

    # Archive current snapshot before updating
    version_num = conn.execute(
        "SELECT COALESCE(MAX(version_num), 0) + 1 FROM listing_versions WHERE listing_id = ?",
        (listing_id,)
    ).fetchone()[0]
    conn.execute(
        """INSERT INTO listing_versions (listing_id, version_num, changed_by, snapshot_json)
           VALUES (?, ?, ?, ?)""",
        (listing_id, version_num, email, json.dumps(dict(existing)))
    )

    # Apply only the non-None fields
    d = {k: v for k, v in update.dict().items() if v is not None}
    if not d:
        conn.close()
        return {"message": "No fields changed", "listing_id": listing_id}

    sets = ", ".join(f"{k} = ?" for k in d.keys())
    vals = list(d.values())
    conn.execute(
        f"UPDATE listings SET {sets}, updated_at = datetime('now') WHERE id = ?",
        vals + [listing_id]
    )
    conn.commit()
    conn.close()
    # Re-match on edit — listing content may have changed enough to surface new buyers
    background_tasks.add_task(run_match_job, listing_id)
    return {"message": "Listing updated — live immediately", "listing_id": listing_id, "version_archived": version_num}

@app.get("/listings/{listing_id}/versions")
def get_listing_versions(listing_id: int, _key: str = Depends(auth.require_api_key)):
    """Admin: return version history for a listing (snapshots excluded — metadata only)."""
    conn = database.get_db()
    existing = conn.execute("SELECT id FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    rows = conn.execute(
        """SELECT id, listing_id, version_num, changed_by, changed_at
           FROM listing_versions WHERE listing_id = ? ORDER BY version_num DESC""",
        (listing_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/listings/{listing_id}/versions/{version_num}")
def get_listing_version_snapshot(listing_id: int, version_num: int, _key: str = Depends(auth.require_api_key)):
    """Admin: return the full JSON snapshot of a specific version."""
    conn = database.get_db()
    row = conn.execute(
        "SELECT * FROM listing_versions WHERE listing_id = ? AND version_num = ?",
        (listing_id, version_num)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Version not found")
    r = dict(row)
    try:
        r["snapshot"] = json.loads(r.pop("snapshot_json"))
    except Exception:
        pass
    return r

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

@app.post("/users/{email}/photo")
async def upload_user_photo(email: str, file: UploadFile = File(...)):
    """Upload a seller profile photo. Compresses to 400×400 JPEG, stores to R2 or local,
    saves URL to users.photo_url. No API key required — seller identifies by email."""
    allowed = {"image/jpeg", "image/png", "image/webp"}
    content_type = file.content_type or "image/jpeg"
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WebP accepted")

    raw = await file.read()
    if len(raw) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Photo too large — max 10MB")

    try:
        img = Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail="Could not read image file")

    # Square-crop to centre, then resize to 400×400
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top  = (h - side) // 2
    img  = img.crop((left, top, left + side, top + side))
    img  = img.resize((400, 400), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=82, optimize=True)
    photo_bytes = buf.getvalue()

    # Upload to R2 or local fallback
    if _S3_CONFIGURED:
        key = f"profiles/{uuid.uuid4().hex}_profile.jpg"
        photo_url = _s3_upload(photo_bytes, key, "image/jpeg")
    else:
        fname = f"profile_{uuid.uuid4().hex}.jpg"
        local_path = f"/var/www/marketsquare/media/{fname}"
        try:
            with open(local_path, "wb") as fh:
                fh.write(photo_bytes)
            photo_url = f"/media/{fname}"
        except Exception as exc:
            _log.error("Profile photo local save failed: %s", exc)
            raise HTTPException(status_code=500, detail="Photo storage unavailable")

    # Upsert user record and save photo_url
    conn = database.get_db()
    conn.execute(
        "INSERT INTO users (email, photo_url) VALUES (?, ?) ON CONFLICT(email) DO UPDATE SET photo_url = excluded.photo_url",
        (email, photo_url)
    )
    conn.commit()
    conn.close()
    return {"photo_url": photo_url}

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
def create_intro(intro: IntroRequest, background_tasks: BackgroundTasks):
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
    if N8N_WEBHOOK_NEW_INTRO:
        payload = {
            "event":         "intro_submitted",
            "listing_id":    intro.listing_id,
            "listing_title": listing["title"],
            "category":      listing["category"],
            "buyer_email":   intro.buyer_email,
            "buyer_name":    intro.buyer_name,
            "message":       intro.message,
            "seller_email":  listing["seller_email"] if listing["seller_email"] else None,
            "timestamp":     datetime.now(timezone.utc).isoformat(),
        }
        background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_NEW_INTRO, payload)
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
    # Deduct 1 Tuppence from the buyer's wallet
    conn.execute(
        "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'intro_deduct', -1, ?)",
        (intro["buyer_email"], f"Intro accepted · listing #{intro['listing_id']} · {listing['title'] if listing else ''}")
    )
    conn.commit()
    conn.close()
    if N8N_WEBHOOK_ACCEPT:
        payload = {
            "event":              "intro_accepted",
            "intro_id":           intro_id,
            "listing_id":         intro["listing_id"],
            "listing_title":      listing["title"] if listing else None,
            "category":           listing["category"] if listing else None,
            "buyer_email":        intro["buyer_email"],
            "buyer_name":         intro["buyer_name"],
            "seller_email":       listing["seller_email"] if listing and listing["seller_email"] else None,
            "city":               listing["city"] if listing else None,
            "timestamp":          datetime.now(timezone.utc).isoformat(),
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
def initialize_payment(email: str, tuppence: int, ai_pack_sessions: int = 0):
    amount_rands = tuppence * 36
    reference = f"ms_tuppence_{uuid.uuid4().hex[:12]}"
    result = payments.initialize_payment(
        email=email,
        amount_rands=amount_rands,
        reference=reference,
        metadata={"tuppence": tuppence, "email": email, "ai_pack_sessions": ai_pack_sessions}
    )
    if result.get("status"):
        return {
            "status": "ok",
            "reference": reference,
            "authorization_url": result["data"]["authorization_url"],
            "tuppence": tuppence,
            "ai_pack_sessions": ai_pack_sessions,
            "amount_rands": amount_rands
        }
    raise HTTPException(status_code=400, detail="Payment initialization failed")

@app.get("/payment/verify")
def verify_payment(reference: str):
    result = payments.verify_payment(reference)
    if result.get("status") and result["data"]["status"] == "success":
        metadata = result["data"]["metadata"]
        tuppence = metadata.get("tuppence", 0)
        email    = metadata.get("email", "")
        ai_sessions = int(metadata.get("ai_pack_sessions", 0) or 0)
        conn = database.get_db()
        conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
            (email, "topup", tuppence, f"Tuppence top-up via Paystack · ref {reference}")
        )
        if ai_sessions > 0:
            # Ensure user record exists, then credit AI sessions
            conn.execute(
                "INSERT INTO users (email, aa_free_used, aa_sessions_remaining) VALUES (?, 0, 0) ON CONFLICT(email) DO NOTHING",
                (email,)
            )
            conn.execute(
                "UPDATE users SET aa_sessions_remaining = aa_sessions_remaining + ? WHERE email = ?",
                (ai_sessions, email)
            )
        conn.commit()
        conn.close()
        return {"status": "ok", "tuppence_credited": tuppence, "ai_sessions_credited": ai_sessions, "email": email}
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
        "SELECT aa_free_used, aa_sessions_remaining, trust_score FROM users WHERE email = ?",
        (req.email,)
    ).fetchone()

    if not row:
        # Auto-register — first-time sellers get 1 free coaching session
        conn.execute(
            "INSERT INTO users (email, aa_free_used, aa_sessions_remaining) VALUES (?, 0, 0)",
            (req.email,)
        )
        conn.commit()
        row = conn.execute(
            "SELECT aa_free_used, aa_sessions_remaining, trust_score FROM users WHERE email = ?",
            (req.email,)
        ).fetchone()

    free_used     = row["aa_free_used"] or 0
    sessions      = row["aa_sessions_remaining"] or 0
    current_score = row["trust_score"] or 0

    if free_used and sessions == 0:
        conn.close()
        raise HTTPException(
            status_code=402,
            detail="No coaching sessions remaining. Purchase an AI Pack (8 sessions · 1T) to continue."
        )

    def _tier_label(s):
        if s < 40: return "New — no badge yet"
        if s < 70: return "Established — blue badge"
        if s < 90: return "Trusted — green badge"
        return "Highly Trusted — gold badge + featured at top of results"

    # Category-specific credential reference used in system prompt
    _TS_CREDENTIALS = {
        "Property": (
            "CATEGORY: Property\n"
            "Available credential signals and their points:\n"
            "• PPRA/EAAB Registration Certificate (active) → 15 pts — check ppra.org.za\n"
            "• NQF4 Real Estate qualification → 6 pts\n"
            "• NQF5 Real Estate → cumulative 12 pts\n"
            "• NQF6+ or professional designation → cumulative 20 pts\n"
            "• Professional body membership (IEASA, SAPOA, NAR) → 5 pts\n"
            "• Government ID verified by MarketSquare → 15 Universal pts\n"
            "• Verified referrals from buyers → up to 10 Universal pts\n"
            "Note: A Property seller without PPRA registration earns 0 Category pts."
        ),
        "Tutors": (
            "CATEGORY: Tutors\n"
            "Available credential signals and their points:\n"
            "• SACE registration (South African Council for Educators) → 8 pts — sace.org.za\n"
            "• Certificate or Diploma (NQF5–6) → 6 pts\n"
            "• Bachelor's Degree (NQF7) → 10 pts (replaces diploma pts)\n"
            "• Honours or Postgraduate (NQF8+) → 14 pts (replaces degree pts)\n"
            "• Subject specialisation certificate or transcript → 5 pts\n"
            "• Teaching/tutoring experience 2–5 yrs → 5 pts · 5+ yrs → 11 pts\n"
            "• Well-structured CV (verifiable dates, no gaps) → 2 pts\n"
            "• Government ID verified by MarketSquare → 15 Universal pts\n"
            "• Verified referrals from students or parents → up to 10 Universal pts"
        ),
        "Services": (
            "CATEGORY: Services\n"
            "For TECHNICAL trades — available credential signals:\n"
            "• Professional/statutory body registration (ECSA, PIRB, NHBRC, FSCA, SAICA) → 12 pts\n"
            "• Trade certificate (City & Guilds, TVET, MERSETA, CETA, Red Seal) → 8 pts\n"
            "• Primary industry ticket/licence (CoC electrical, gas CoC, PIRB licence) → 5 pts\n"
            "• Additional safety tickets (First Aid, working at heights, confined space) → 3 pts each, max 2\n"
            "• Trade experience 3–7 yrs → 4 pts · 7+ yrs → 8 pts\n"
            "• Strong, verifiable CV → 2 pts\n"
            "For CASUALS — available credential signals:\n"
            "• Reference letter from past employer or client (with contact details) → 8 pts first, +5 second\n"
            "• Any NQF qualification or accredited short course → 8 pts\n"
            "• Years in service 2–4 yrs → 6 pts · 5+ yrs → 14 pts\n"
            "• Strong profile description (specific services, suburb, availability) → 5 pts\n"
            "For BOTH: Government ID verified by MarketSquare → 15 Universal pts (critical for Casuals)"
        ),
        "Adventures": (
            "CATEGORY: Adventures\n"
            "For EXPERIENCES (guided activities) — available credential signals:\n"
            "• Guide/activity certification (FGASA, MCSA, PADI Divemaster+, SACAA) → 12 pts\n"
            "• First Aid / Emergency Response certificate (current, not expired) → 6 pts\n"
            "• Liability / public indemnity insurance (activity-appropriate) → 5 pts\n"
            "• Additional safety certification (Wilderness First Responder, swift water rescue) → 4 pts\n"
            "• Guided experience 3–7 yrs → 5 pts · 7+ yrs → 10 pts\n"
            "• Secondary qualification or activity endorsement → 3 pts\n"
            "For ACCOMMODATION (B&B / Guesthouse / Hotel) — available credential signals:\n"
            "• TGCSA star grading: 1★=6 · 2★=10 · 3★=14 · 4★=18 · 5★=22 pts — tourismgrading.co.za\n"
            "• Municipal/city operating licence for B&B or guesthouse → 6 pts\n"
            "• Health & safety compliance certificate → 5 pts\n"
            "• Fire clearance certificate → 4 pts\n"
            "• AA Travel Award, TripAdvisor Travellers Choice, or Booking.com Preferred → 3 pts\n"
            "For BOTH: Government ID verified by MarketSquare → 15 Universal pts"
        ),
        "Collectors": (
            "CATEGORY: Collectors\n"
            "Available credential signals and their points:\n"
            "• Collecting domain declaration (specific, detailed description) → 4 pts\n"
            "• Successful platform transactions: 1–4 → 8 pts · 5–14 → 14 pts · 15+ → 20 pts\n"
            "• Authentication certificate for listed item (SANA, PCGS, PSA, CGC) → 8 pts\n"
            "• Professional appraisal or valuation from recognised appraiser → 5 pts\n"
            "• Collector association membership (SANA, Philatelic Foundation) → 3 pts\n"
            "• Government ID verified by MarketSquare → 15 Universal pts\n"
            "• Verified referrals → up to 10 Universal pts\n"
            "Note: Collectors primarily build score through platform transactions — "
            "responding promptly to every introduction is the single most important habit."
        ),
    }

    _cred_ref = _TS_CREDENTIALS.get(req.category, "")

    # System prompt — returns structured JSON for inline field suggestions + Trust Score plan
    system_prompt = (
        "You are the MarketSquare Advert Agent. "
        "Respond with ONLY a valid JSON object — no markdown fences, no prose, no text outside the JSON.\n\n"

        "REQUIRED JSON SCHEMA:\n"
        "{\n"
        '  "fields": {\n'
        '    "<field_id>": {"suggestion": "<improved ready-to-use text>", "reason": "<one-line why>"}\n'
        "    // Only include fields where you have a meaningful improvement.\n"
        "    // Use ONLY the exact field IDs listed in the user message.\n"
        "    // The suggestion value must be the ACTUAL improved text — ready to paste in, not advice about it.\n"
        "  },\n"
        '  "trust_score_actions": [\n'
        '    {"action": "<specific action the seller must take>", "points": <integer>, "doc": "<exact document name>"}\n'
        "    // Ordered highest points first. Only include actions with a verifiable document.\n"
        "    // Never fabricate credentials not implied by the seller's input.\n"
        "  ],\n"
        '  "anonymity_warning": "<text if seller name or business name found in fields, else null>"\n'
        "}\n\n"

        "MISSION 1 — LISTING FIELD IMPROVEMENTS\n"
        "For each listing field, provide a specific improvement: clearer title, better description, "
        "price positioning. The suggestion must be the actual improved text, not advice about it.\n\n"

        "MISSION 2 — TRUST SCORE MAXIMISATION\n"
        "The Trust Score (0–100) is the seller's most important asset.\n"
        "  0–39:  New — no badge\n"
        "  40–69: Established — blue badge\n"
        "  70–89: Trusted — green badge\n"
        "  90–100: Highly Trusted — gold badge, top of search results\n\n"
        "STEPS:\n"
        "1. Read every field. Identify ALL credentials mentioned: qualifications, registrations, "
        "certifications, memberships, reference letters, experience years, trade tickets.\n"
        "2. Assign exact points per credential using the CREDENTIAL REFERENCE below.\n"
        "3. Include additional achievable credentials for this seller's background.\n"
        "4. Order trust_score_actions by points descending — highest-value first.\n"
        "5. Every action must name an exact document in 'doc'.\n\n"

        "ANONYMITY RULES:\n"
        "Set anonymity_warning to null if no real name or business name appears in listing fields. "
        "Phone numbers and email addresses in listings are ALLOWED — do not flag them. "
        "If the seller's actual name or business name appears in title or description, set "
        "anonymity_warning to: 'NAME FOUND — remove before publishing: [exact text found]'\n\n"
        + (f"CREDENTIAL REFERENCE FOR THIS CATEGORY:\n{_cred_ref}" if _cred_ref else "")
    )

    import json as _json
    field_ids = [k for k, v in req.fields.items() if v]
    fields_text = "\n".join(f"  [{k}]: {v}" for k, v in req.fields.items() if v)
    user_message = (
        f"Category: {req.category}\n"
        f"Available field IDs (use exactly these in your JSON): {field_ids}\n"
        f"My current Trust Score: {current_score} ({_tier_label(current_score)})\n"
        f"Listing fields:\n{fields_text}\n"
        f"Photos completed: {', '.join(req.photo_slots_completed) or 'none yet'}\n\n"
        "Analyse my listing and return the JSON object as specified. Nothing else."
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
                    "max_tokens": 1800,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_message}],
                },
            )
        resp.raise_for_status()
        coaching_text = resp.json()["content"][0]["text"]
    except Exception as exc:
        conn.close()
        _log.error("AA coach Claude call failed: %s", exc)
        raise HTTPException(status_code=502, detail="AI Coach unavailable — please try again")

    # Parse structured JSON response; fall back gracefully if AI wraps it in markdown
    try:
        coaching_json = _json.loads(coaching_text)
    except Exception:
        import re as _re
        m = _re.search(r'\{[\s\S]*\}', coaching_text)
        try:
            coaching_json = _json.loads(m.group(0)) if m else {}
        except Exception:
            coaching_json = {}
    # Ensure required keys exist
    coaching_json.setdefault("fields", {})
    coaching_json.setdefault("trust_score_actions", [])
    coaching_json.setdefault("anonymity_warning", None)

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

    return {"coaching_json": coaching_json, "sessions_remaining": max(0, sessions - (0 if not free_used else 1))}


@app.post("/advert-agent/buy-pack")
def aa_buy_pack(email: str, sessions: int = 8):
    """Credit seller with coaching sessions. Default 8 (1T standard pack). Pass sessions= for bulk packs."""
    conn = database.get_db()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not registered")
    conn.execute(
        "UPDATE users SET aa_sessions_remaining = aa_sessions_remaining + ? WHERE email = ?",
        (sessions, email)
    )
    conn.commit()
    new_bal = conn.execute(
        "SELECT aa_sessions_remaining FROM users WHERE email = ?", (email,)
    ).fetchone()["aa_sessions_remaining"]
    conn.close()
    return {"sessions_remaining": new_bal}


@app.post("/advert-agent/publish")
async def aa_publish(
    background_tasks: BackgroundTasks,
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

    # Build structured description block from all category-specific fields
    structured_lines = []
    field_labels = {
        "subject":      "Subjects",
        "level":        "Level",
        "mode":         "Mode",
        "rate":         "Rate",
        "radius":       "Travel radius",
        "area":         "Area",
        "suburb":       "Suburb",
        "service_type": "Service type",
        "experience":   "Experience",
        "availability": "Availability",
        "languages":    "Languages",
        "certifications": "Certifications",
        "specialisation": "Specialisation",
        "tools":        "Tools / equipment",
        "payment":      "Payment",
    }
    skip_fields = {"title", "item_name", "desc", "price", "price_per_person", "service_class"}
    for key, label in field_labels.items():
        val = field_data.get(key, "").strip() if isinstance(field_data.get(key), str) else ""
        if val:
            structured_lines.append(f"**{label}:** {val}")

    if structured_lines:
        structured_block = "\n".join(structured_lines)
        desc = f"{structured_block}\n\n{desc}".strip() if desc else structured_block

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
           (title, price, category, city, area, suburb, description, thumb_url, medium_url, service_class, seller_email, published_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?, datetime('now'))""",
        (title, price, category, "Pretoria", suburb, suburb, desc, thumb_url, medium_url, service_class, email),
    )
    listing_id = cursor.lastrowid
    # Upsert user record so seller can use AA coach going forward
    conn.execute(
        "INSERT INTO users (email, aa_free_used, aa_sessions_remaining) VALUES (?, 0, 0) ON CONFLICT(email) DO NOTHING",
        (email,)
    )
    conn.commit()
    conn.close()

    # Wishlist matching — async, never blocks publish (PR-14)
    background_tasks.add_task(run_match_job, listing_id)
    return {"listing_id": listing_id, "pdf_url": None}  # PDF generation added in Stage 4


# ── TUPPENCE BALANCE (public read) ───────────────────────────

@app.get("/tuppence/balance")
def get_tuppence_balance(email: str):
    """Return Tuppence balance for an email — sum of all transaction amounts.
    Used by the buyer app to sync dev-seeded balances without Paystack.
    """
    conn = database.get_db()
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as balance FROM transactions WHERE user_email = ?",
        (email,)
    ).fetchone()
    conn.close()
    return {"email": email, "balance": int(row["balance"])}


# ── WISHLIST MATCHING ENGINE (zero-cost, Section 2) ──────────
# Local keyword + lightweight stem matcher. NO external API calls.
# Hot-swappable: a future Haiko 4.5 implementation can replace
# LocalKeywordMatcher behind the same interface (extract_intent +
# score_match). Until then, this IS the V1 implementation — not a
# placeholder. The Haiko agent socket is defined as MATCHER below.

import re as _re_match
from datetime import timedelta

# Stop words filtered before keyword scoring — keeps matches signal-rich
_STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "for", "with", "of", "in", "on",
    "at", "to", "from", "by", "is", "are", "was", "were", "be", "been",
    "being", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "this", "that", "these", "those",
    "i", "you", "he", "she", "it", "we", "they", "my", "your", "our",
    "their", "his", "her", "its", "as", "if", "than", "then", "so",
    "very", "really", "just", "some", "any", "all", "no", "not", "yes",
    "looking", "want", "need", "like", "wanted", "wanting", "after",
    "near", "around", "good", "great", "nice", "best",
}

# Common synonyms — symmetric expansion. Tuned to MarketSquare verticals.
# Keeping this small and conservative on purpose; semantic richness comes
# from stemming + token overlap, not from a giant manually-curated list.
_SYNONYMS = {
    "bike": {"bicycle", "cycle"},
    "bicycle": {"bike", "cycle"},
    "cycle": {"bike", "bicycle"},
    "house": {"home", "property"},
    "home": {"house", "property"},
    "apartment": {"flat", "unit"},
    "flat": {"apartment", "unit"},
    "car": {"vehicle", "auto", "motor"},
    "vehicle": {"car", "auto", "motor"},
    "tutor": {"tutoring", "teacher", "lessons", "lesson", "tuition"},
    "tutoring": {"tutor", "teacher", "lessons", "lesson", "tuition"},
    "teacher": {"tutor", "tutoring", "lessons", "lesson"},
    "math": {"mathematics", "maths"},
    "maths": {"mathematics", "math"},
    "mathematics": {"math", "maths"},
    "plumbing": {"plumber"},
    "plumber": {"plumbing"},
    "electric": {"electrician", "electrical"},
    "electrician": {"electric", "electrical"},
    "electrical": {"electric", "electrician"},
    "garden": {"gardening", "gardener", "landscaping"},
    "gardening": {"garden", "gardener", "landscaping"},
    "cleaning": {"cleaner", "clean", "housekeeping"},
    "cleaner": {"cleaning", "clean"},
    "hike": {"hiking", "trek", "trekking"},
    "hiking": {"hike", "trek", "trekking"},
    "dive": {"diving", "scuba"},
    "diving": {"dive", "scuba"},
    "coin": {"coins", "numismatic", "numismatics"},
    "stamp": {"stamps", "philatelic", "philatelics"},
    "watch": {"watches", "timepiece"},
    "rolex": {"watch", "watches", "timepiece"},
    "card": {"cards", "trading"},
    "red": {"crimson", "scarlet"},
    "crimson": {"red", "scarlet"},
}


def _light_stem(token: str) -> str:
    """Tiny inline Porter-style stemmer. NOT pip nltk — zero dependencies.
    Strips a few high-frequency English suffixes. Good enough for V1; the
    interface stays stable so a real Snowball stemmer can drop in later.
    """
    if len(token) <= 3:
        return token
    for suf in ("ingly", "edly"):
        if token.endswith(suf) and len(token) > len(suf) + 2:
            return token[: -len(suf)]
    for suf in ("ing", "ies", "ied"):
        if token.endswith(suf) and len(token) > len(suf) + 2:
            stem = token[: -len(suf)]
            if suf in ("ies", "ied"):
                stem += "y"
            return stem
    for suf in ("ed", "es", "ly"):
        if token.endswith(suf) and len(token) > len(suf) + 2:
            return token[: -len(suf)]
    if token.endswith("s") and not token.endswith("ss") and len(token) > 3:
        return token[:-1]
    return token


def _tokenize(text: str) -> list[str]:
    """Lowercase, split on non-alphanumerics, strip stopwords, return raw tokens."""
    if not text:
        return []
    raw = _re_match.findall(r"[a-z0-9]+", text.lower())
    return [t for t in raw if t and t not in _STOP_WORDS and len(t) > 1]


def _expand_tokens(tokens: list[str]) -> set[str]:
    """Return the set of tokens + their stems + synonyms — used for matching."""
    out: set[str] = set()
    for t in tokens:
        out.add(t)
        out.add(_light_stem(t))
        out.update(_SYNONYMS.get(t, set()))
    return out


class LocalKeywordMatcher:
    """V1 matcher — pure Python, zero external API cost.

    extract_intent(listing) → dict of structured matchable features
    score_match(signal, listing) → float in [0, 100]

    The Haiko agent socket can later replace this class with a semantic
    implementation; the call surface stays identical.
    """

    name = "local_keyword_v1"

    @staticmethod
    def extract_intent(listing: dict) -> dict:
        """Pull keywords + structured fields out of a listing for matching."""
        text_parts = [
            listing.get("title") or "",
            listing.get("description") or "",
            listing.get("subject") or "",
            listing.get("level") or "",
            listing.get("service_type") or "",
            listing.get("prop_type") or "",
        ]
        title_tokens = _expand_tokens(_tokenize(listing.get("title") or ""))
        all_tokens = _expand_tokens(_tokenize(" ".join(text_parts)))
        # Numeric price extraction — strip currency symbols and commas
        price_raw = (listing.get("price") or "").replace(",", "")
        price_match = _re_match.search(r"\d+(?:\.\d+)?", price_raw)
        price_val = float(price_match.group(0)) if price_match else None
        return {
            "title_tokens": title_tokens,
            "all_tokens": all_tokens,
            "category": listing.get("category"),
            "suburb": (listing.get("suburb") or "").lower() or None,
            "geo_city_id": listing.get("geo_city_id"),
            "city": (listing.get("city") or "").lower() or None,
            "price": price_val,
        }

    @staticmethod
    def score_match(signal: dict, listing_intent: dict) -> float:
        """Score 0–100. Components:
           - Category exact match: +30 (or hard-zero if signal specifies a different category)
           - Title-token overlap: up to +35 (highest-signal text)
           - Body-token overlap: up to +20
           - Suburb / city match: +10
           - Price-range fit: +5
        """
        # Category gate: if the signal specifies a category and it doesn't match, no score
        sig_cat = signal.get("category")
        if sig_cat and listing_intent["category"] and sig_cat != listing_intent["category"]:
            return 0.0

        sig_tokens = _expand_tokens(_tokenize(signal.get("raw_text") or ""))
        # Explicit signals with no text but a category still match weakly
        if not sig_tokens and not sig_cat:
            return 0.0

        score = 0.0
        # Category bonus
        if sig_cat and sig_cat == listing_intent["category"]:
            score += 30.0
        elif not sig_cat and listing_intent["category"]:
            # No category preference stated — neutral, no bonus, no penalty
            pass

        # Title-token overlap (highest weight — title is the cleanest signal)
        title_overlap = len(sig_tokens & listing_intent["title_tokens"])
        if sig_tokens:
            title_ratio = title_overlap / max(len(sig_tokens), 1)
            score += min(35.0, title_ratio * 35.0 + (3.0 if title_overlap >= 2 else 0))

        # Body-token overlap
        body_overlap = len(sig_tokens & listing_intent["all_tokens"])
        if sig_tokens:
            body_ratio = body_overlap / max(len(sig_tokens), 1)
            score += min(20.0, body_ratio * 20.0)

        # Suburb / city match
        sig_suburb_id = signal.get("suburb_id")
        sig_city_id = signal.get("city_id")
        if sig_city_id and listing_intent.get("geo_city_id") and sig_city_id == listing_intent["geo_city_id"]:
            score += 10.0
        elif signal.get("raw_text") and listing_intent.get("suburb"):
            # Loose suburb mention in raw_text
            sub = listing_intent["suburb"]
            if sub and sub in (signal.get("raw_text") or "").lower():
                score += 6.0

        # Price-range fit
        price = listing_intent.get("price")
        pmin = signal.get("price_min")
        pmax = signal.get("price_max")
        if price is not None:
            in_range = True
            if pmin is not None and price < pmin:
                in_range = False
            if pmax is not None and price > pmax:
                in_range = False
            if in_range and (pmin is not None or pmax is not None):
                score += 5.0

        return min(100.0, score)


# Hot-swap socket — replace with HaikoMatcher() instance to switch implementations.
MATCHER = LocalKeywordMatcher()


def _seller_country_for_listing(conn, listing_row: dict) -> Optional[str]:
    """Return the listing's country ISO2 via geo_cities lookup."""
    geo_city_id = listing_row.get("geo_city_id")
    if geo_city_id:
        row = conn.execute(
            "SELECT country_iso2 FROM geo_cities WHERE id = ?", (geo_city_id,)
        ).fetchone()
        if row:
            return row["country_iso2"]
    # Fallback: match by city name
    city = listing_row.get("city")
    if city:
        row = conn.execute(
            "SELECT country_iso2 FROM geo_cities WHERE name = ? LIMIT 1", (city,)
        ).fetchone()
        if row:
            return row["country_iso2"]
    return None


def _buyer_tier(conn, buyer_token: str) -> str:
    """Return 'free' or 'global' for this buyer_token. Defaults to 'free'."""
    row = conn.execute(
        "SELECT tier, expires_at FROM wishlist_subscriptions WHERE buyer_token = ?",
        (buyer_token,)
    ).fetchone()
    if not row:
        return "free"
    if row["tier"] != "global":
        return "free"
    # Check expiry
    if row["expires_at"]:
        try:
            if datetime.fromisoformat(row["expires_at"]) < datetime.now(timezone.utc):
                return "free"
        except Exception:
            pass
    return "global"


def _ping_quota_ok(conn, buyer_token: str) -> bool:
    """Return True if buyer is under the 3-pings-per-hour limit (PR-36).
    Counted off wishlist_matches.matched_at WHERE pinged=1."""
    one_hour_ago = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()
    row = conn.execute(
        """SELECT COUNT(*) AS n FROM wishlist_matches
           WHERE buyer_token = ? AND pinged = 1 AND matched_at >= ?""",
        (buyer_token, one_hour_ago)
    ).fetchone()
    return (row["n"] or 0) < 3


def run_match_job(listing_id: int):
    """Background worker — score this listing against every active wishlist signal,
    insert qualifying matches, flag pings. Never raises — logs and exits.
    Re-entrant: the unique (buyer_token, listing_id) constraint on wishlist_matches
    means re-running for the same listing is a no-op for already-matched buyers."""
    try:
        conn = database.get_db()
        listing = conn.execute(
            "SELECT * FROM listings WHERE id = ?", (listing_id,)
        ).fetchone()
        if not listing:
            conn.close()
            return
        listing = dict(listing)
        intent = MATCHER.extract_intent(listing)
        seller_trust = int(listing.get("trust_score") or 0)
        listing_country = _seller_country_for_listing(conn, listing)

        # Determine if this listing is currently boosted (PR-39: looser threshold)
        boost_until = listing.get("boost_until")
        is_boosted = False
        if boost_until:
            try:
                is_boosted = datetime.fromisoformat(boost_until) > datetime.now(timezone.utc)
            except Exception:
                is_boosted = False
        feed_threshold = 45.0 if is_boosted else 60.0

        signals = conn.execute(
            """SELECT * FROM wishlist_signals
               WHERE expires_at > ?""",
            (datetime.now(timezone.utc).isoformat(),)
        ).fetchall()

        match_inserts = 0
        for s in signals:
            sig = dict(s)
            buyer_token = sig["buyer_token"]
            # Trust gate — absolute (PR-08, PR-43)
            min_trust = int(sig.get("min_trust_score") or 0)
            if seller_trust < min_trust:
                continue
            # Geo gate — free buyer = same country only; global = any (PR-16/17, PR-39)
            tier = _buyer_tier(conn, buyer_token)
            if tier == "free" and not is_boosted:
                buyer_country = sig.get("country_iso2")
                if buyer_country and listing_country and buyer_country != listing_country:
                    continue
            # Score
            score = MATCHER.score_match(sig, intent)
            if score < feed_threshold:
                continue
            # Apply explicit-vs-browse weight (PR-03) — multiplied in, capped at 100
            weighted = min(100.0, score * float(sig.get("weight") or 1.0))
            # Insert (silently ignore unique-constraint violations — already matched)
            try:
                cur = conn.execute(
                    """INSERT INTO wishlist_matches
                       (buyer_token, listing_id, signal_id, match_score, seller_trust, boost_rank, matched_at)
                       VALUES (?,?,?,?,?,?, ?)""",
                    (buyer_token, listing_id, sig["id"], weighted, seller_trust,
                     1 if is_boosted else 0,
                     datetime.now(timezone.utc).isoformat())
                )
                new_match_id = cur.lastrowid
                match_inserts += 1
                # Ping decision — PR-13/PR-34: ≥80 + ping_enabled + rate-limit OK
                if (weighted >= 80.0 and int(sig.get("ping_enabled") or 0) == 1
                        and _ping_quota_ok(conn, buyer_token)):
                    conn.execute(
                        "UPDATE wishlist_matches SET pinged = 1 WHERE id = ?",
                        (new_match_id,)
                    )
                    # Section 5: actually deliver the push. Synchronous-ish (8s timeout
                    # per device), but this whole function is already running in a
                    # FastAPI BackgroundTask so it never blocks the request handler.
                    _send_push_for_match(buyer_token, new_match_id, listing)
            except Exception:
                # Unique-constraint violation = already matched — skip silently
                pass
        conn.commit()
        conn.close()
        _log.info("run_match_job listing=%s matcher=%s inserts=%d boosted=%s",
                  listing_id, MATCHER.name, match_inserts, is_boosted)
    except Exception as exc:
        _log.error("run_match_job failed for listing %s: %s", listing_id, exc)


# ── WISHLIST FEED — buyer_token + signal capture (v1.2.0) ────
# Push-marketplace foundation. Buyer browsing/searches build wishlist
# signals against an anonymous buyer_token (UUID). The matching engine
# (Section 2) consumes these signals to surface matched listings in the
# bottom-half scroll feed. NO seller identity is ever returned in any
# wishlist response — anonymity is absolute.
#
# COST CONSTRAINT (locked): all matching/intent extraction is local
# Python — no OpenAI / Google / Anthropic / vector DB calls in this path.

class BuyerTokenRequest(BaseModel):
    email: Optional[str] = None  # if provided, links token to users row

class WishlistSignalIn(BaseModel):
    buyer_token: str
    signal_type: str            # 'browse_search' | 'browse_view' | 'explicit'
    raw_text: Optional[str] = None
    category: Optional[str] = None
    suburb_id: Optional[int] = None
    city_id: Optional[int] = None
    country_iso2: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    min_trust_score: int = 0
    ping_enabled: int = 1

class WishlistSignalUpdate(BaseModel):
    raw_text: Optional[str] = None
    category: Optional[str] = None
    suburb_id: Optional[int] = None
    city_id: Optional[int] = None
    country_iso2: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    min_trust_score: Optional[int] = None
    ping_enabled: Optional[int] = None


def _signal_weight(signal_type: str) -> float:
    """Explicit wishlist items count double — see PR-03."""
    return 2.0 if signal_type == "explicit" else 1.0


def _signal_expiry_iso() -> str:
    """90 days from now (PR-06). Refreshed every time a signal is touched."""
    return (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()


def _purge_expired_signals(conn):
    """Lazy purge — called on signal reads. Keeps the table small without a cron."""
    conn.execute(
        "DELETE FROM wishlist_signals WHERE expires_at < ?",
        (datetime.now(timezone.utc).isoformat(),)
    )


@app.post("/buyer-token")
def mint_buyer_token(req: BuyerTokenRequest):
    """Issue or fetch an anonymous buyer_token.
    If email is provided AND a users row exists with a buyer_token, return that.
    If email is provided AND users row exists without one, mint and store.
    If no email: mint a fresh anonymous token — never linked to any users row.
    """
    new_token = uuid.uuid4().hex
    if not req.email:
        return {"buyer_token": new_token, "linked": False}
    conn = database.get_db()
    row = conn.execute(
        "SELECT buyer_token FROM users WHERE email = ?", (req.email,)
    ).fetchone()
    if row and row["buyer_token"]:
        conn.close()
        return {"buyer_token": row["buyer_token"], "linked": True}
    if row:
        conn.execute(
            "UPDATE users SET buyer_token = ? WHERE email = ?",
            (new_token, req.email)
        )
        conn.commit()
        conn.close()
        return {"buyer_token": new_token, "linked": True}
    # No users row — return token but don't auto-create row (per build plan)
    conn.close()
    return {"buyer_token": new_token, "linked": False}


@app.post("/wishlist/signal")
def create_wishlist_signal(sig: WishlistSignalIn):
    """Capture a wishlist signal. Public — no API key required.
    Identical (buyer_token, signal_type, raw_text, category) signals refresh
    expires_at instead of inserting duplicates — keeps the table compact while
    treating repeated browses as a stronger signal of intent.
    """
    if sig.signal_type not in ("browse_search", "browse_view", "explicit"):
        raise HTTPException(status_code=400, detail="signal_type must be browse_search, browse_view, or explicit")
    if not sig.buyer_token or len(sig.buyer_token) < 8:
        raise HTTPException(status_code=400, detail="valid buyer_token required")
    weight = _signal_weight(sig.signal_type)
    conn = database.get_db()
    # Dedup on (buyer_token, signal_type, lower(raw_text), category)
    existing = conn.execute(
        """SELECT id FROM wishlist_signals
           WHERE buyer_token = ? AND signal_type = ?
             AND COALESCE(LOWER(raw_text), '') = COALESCE(LOWER(?), '')
             AND COALESCE(category, '') = COALESCE(?, '')
           LIMIT 1""",
        (sig.buyer_token, sig.signal_type, sig.raw_text, sig.category)
    ).fetchone()
    if existing:
        conn.execute(
            """UPDATE wishlist_signals SET
                 expires_at = ?,
                 suburb_id = COALESCE(?, suburb_id),
                 city_id = COALESCE(?, city_id),
                 country_iso2 = COALESCE(?, country_iso2),
                 price_min = COALESCE(?, price_min),
                 price_max = COALESCE(?, price_max),
                 min_trust_score = ?,
                 ping_enabled = ?
               WHERE id = ?""",
            (_signal_expiry_iso(), sig.suburb_id, sig.city_id, sig.country_iso2,
             sig.price_min, sig.price_max, sig.min_trust_score, sig.ping_enabled,
             existing["id"])
        )
        conn.commit()
        conn.close()
        return {"id": existing["id"], "refreshed": True}
    cur = conn.execute(
        """INSERT INTO wishlist_signals
           (buyer_token, signal_type, raw_text, category, suburb_id, city_id, country_iso2,
            price_min, price_max, min_trust_score, weight, ping_enabled, expires_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (sig.buyer_token, sig.signal_type, sig.raw_text, sig.category,
         sig.suburb_id, sig.city_id, sig.country_iso2,
         sig.price_min, sig.price_max, sig.min_trust_score, weight,
         sig.ping_enabled, _signal_expiry_iso())
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return {"id": new_id, "refreshed": False}


@app.get("/wishlist/signals")
def list_wishlist_signals(buyer_token: str):
    """Buyer reads their own signals. Public — buyer_token IS the auth here.
    Anyone holding the token can read; the token itself never leaves the buyer's
    device under normal flows."""
    conn = database.get_db()
    _purge_expired_signals(conn)
    rows = conn.execute(
        """SELECT id, signal_type, raw_text, category, suburb_id, city_id, country_iso2,
                  price_min, price_max, min_trust_score, weight, ping_enabled,
                  created_at, expires_at
           FROM wishlist_signals
           WHERE buyer_token = ?
           ORDER BY created_at DESC""",
        (buyer_token,)
    ).fetchall()
    conn.commit()
    conn.close()
    return [dict(r) for r in rows]


@app.put("/wishlist/signals/{signal_id}")
def update_wishlist_signal(signal_id: int, update: WishlistSignalUpdate, buyer_token: str):
    """Edit a single signal — change min_trust_score, edit explicit text, toggle ping."""
    conn = database.get_db()
    existing = conn.execute(
        "SELECT id FROM wishlist_signals WHERE id = ? AND buyer_token = ?",
        (signal_id, buyer_token)
    ).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Signal not found for this buyer_token")
    d = {k: v for k, v in update.dict().items() if v is not None}
    if not d:
        conn.close()
        return {"message": "No fields changed", "signal_id": signal_id}
    sets = ", ".join(f"{k} = ?" for k in d.keys())
    vals = list(d.values())
    conn.execute(
        f"UPDATE wishlist_signals SET {sets}, expires_at = ? WHERE id = ?",
        vals + [_signal_expiry_iso(), signal_id]
    )
    conn.commit()
    conn.close()
    return {"message": "Signal updated", "signal_id": signal_id}


@app.delete("/wishlist/signals/{signal_id}")
def delete_wishlist_signal(signal_id: int, buyer_token: str):
    """Permanent, immediate deletion (PR-05). Also drops any existing matches
    surfaced from this signal so the feed never shows orphaned cards."""
    conn = database.get_db()
    existing = conn.execute(
        "SELECT id FROM wishlist_signals WHERE id = ? AND buyer_token = ?",
        (signal_id, buyer_token)
    ).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Signal not found for this buyer_token")
    conn.execute("DELETE FROM wishlist_signals WHERE id = ?", (signal_id,))
    conn.execute("DELETE FROM wishlist_matches WHERE signal_id = ?", (signal_id,))
    conn.commit()
    conn.close()
    return {"message": "Signal and related matches deleted", "signal_id": signal_id}


@app.delete("/wishlist/signals")
def delete_all_wishlist_signals(buyer_token: str):
    """Wipe everything for a buyer_token — used by the 'forget me' control."""
    conn = database.get_db()
    conn.execute("DELETE FROM wishlist_signals WHERE buyer_token = ?", (buyer_token,))
    conn.execute("DELETE FROM wishlist_matches WHERE buyer_token = ?", (buyer_token,))
    conn.commit()
    conn.close()
    return {"message": "All wishlist data deleted for this buyer_token"}


# ── WISHLIST FEED · matches, showcase, boost, subscription ────
# All responses scrub seller identity. Anonymity is absolute (PR-04).
# These endpoints serve the bottom-half scroll feed in marketsquare.html.

def _strip_seller_identity(row: dict) -> dict:
    """Remove every field that could identify a seller. Used on every row
    returned by feed/showcase endpoints. PR-29: no seller name, no seller_email,
    no aa_* fields, no buyer_token leakage."""
    forbidden = {"seller_email", "name", "email", "aa_free_used",
                 "aa_sessions_remaining", "photo_url"}
    return {k: v for k, v in row.items() if k not in forbidden}


def _listing_age_label(published_at: Optional[str]) -> str:
    """Human-readable 'time since listed' for the feed card (PR-30)."""
    if not published_at:
        return "just now"
    try:
        if published_at.endswith("Z"):
            published_at = published_at[:-1] + "+00:00"
        dt = datetime.fromisoformat(published_at)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - dt
        secs = int(delta.total_seconds())
        if secs < 60: return "just now"
        if secs < 3600: return f"{secs // 60}m ago"
        if secs < 86400: return f"{secs // 3600}h ago"
        return f"{secs // 86400}d ago"
    except Exception:
        return "recently"


@app.get("/wishlist/feed")
def get_wishlist_feed(buyer_token: str, min_trust_override: int = 0, limit: int = 30):
    """Return the buyer's personalised feed — anonymised listing cards.
    Cards are sorted boosted-first (PR-39 'Featured'), then newest-match-first.
    `min_trust_override` lets the buyer apply a session-level Trust Score floor
    on top of per-signal thresholds (PR-07). Free-tier buyers get a flag in the
    response if cross-country matches exist they cannot see (PR-17).
    """
    conn = database.get_db()
    # Increment view_count opportunistically when a card surfaces (lazy mark-as-seen
    # happens on tap, not here — we only count appearances)
    rows = conn.execute(
        """SELECT m.id AS match_id, m.match_score, m.seller_trust, m.matched_at,
                  m.seen, m.boost_rank, m.signal_id,
                  l.id AS listing_id, l.title, l.category, l.city, l.suburb,
                  l.area, l.thumb_url, l.medium_url, l.published_at, l.view_count,
                  l.geo_city_id, l.boost_until,
                  l.price, l.beds, l.baths, l.garages, l.prop_type,
                  l.subject, l.level, l.mode, l.service_type, l.service_class,
                  l.trust_score AS listing_trust_score
           FROM wishlist_matches m
           JOIN listings l ON l.id = m.listing_id
           WHERE m.buyer_token = ?
             AND m.seller_trust >= ?
           ORDER BY m.boost_rank DESC, m.matched_at DESC
           LIMIT ?""",
        (buyer_token, max(0, min_trust_override), limit)
    ).fetchall()

    # Detect cross-country matches the buyer is missing on free tier (PR-17)
    tier = _buyer_tier(conn, buyer_token)
    upgrade_prompt = None
    if tier == "free":
        # Find buyer's most-recent country signal
        country_row = conn.execute(
            """SELECT country_iso2 FROM wishlist_signals
               WHERE buyer_token = ? AND country_iso2 IS NOT NULL
               ORDER BY created_at DESC LIMIT 1""",
            (buyer_token,)
        ).fetchone()
        if country_row and country_row["country_iso2"]:
            buyer_country = country_row["country_iso2"]
            # Count listings the matcher would surface in OTHER countries by category overlap
            # Approximated by: any listing in a country ≠ buyer's whose category appears in any of this buyer's signals
            cats_row = conn.execute(
                "SELECT DISTINCT category FROM wishlist_signals WHERE buyer_token = ? AND category IS NOT NULL",
                (buyer_token,)
            ).fetchall()
            cats = [c["category"] for c in cats_row]
            if cats:
                placeholders = ",".join("?" * len(cats))
                row = conn.execute(
                    f"""SELECT COUNT(DISTINCT l.id) AS n,
                              (SELECT gc2.country_iso2 FROM listings l2
                               JOIN geo_cities gc2 ON gc2.id = l2.geo_city_id
                               WHERE l2.category IN ({placeholders})
                                 AND gc2.country_iso2 != ?
                               ORDER BY l2.published_at DESC LIMIT 1) AS sample_country
                       FROM listings l
                       JOIN geo_cities gc ON gc.id = l.geo_city_id
                       WHERE l.category IN ({placeholders})
                         AND gc.country_iso2 != ?""",
                    (*cats, buyer_country, *cats, buyer_country)
                ).fetchone()
                if row and (row["n"] or 0) > 0:
                    upgrade_prompt = {
                        "matches_elsewhere": int(row["n"]),
                        "sample_country": row["sample_country"],
                        "message": "Upgrade to Global to see matching listings in other countries."
                    }

    conn.close()

    cards = []
    now = datetime.now(timezone.utc)
    for r in rows:
        d = dict(r)
        boost_until = d.get("boost_until")
        is_boosted = False
        if boost_until:
            try:
                is_boosted = datetime.fromisoformat(boost_until) > now
            except Exception:
                is_boosted = False
        cards.append({
            "match_id":        d["match_id"],
            "listing_id":      d["listing_id"],
            "title":           d["title"],
            "category":        d["category"],
            "thumb_url":       d["thumb_url"],
            "medium_url":      d["medium_url"],
            "city":            d["city"],
            "suburb":          d["suburb"],
            "area":            d["area"],
            "price":           d["price"],
            "beds":            d.get("beds"),
            "baths":           d.get("baths"),
            "garages":         d.get("garages"),
            "prop_type":       d.get("prop_type"),
            "subject":         d.get("subject"),
            "level":           d.get("level"),
            "mode":            d.get("mode"),
            "service_type":    d.get("service_type"),
            "service_class":   d.get("service_class"),
            "trust_score":     d["listing_trust_score"] or 0,
            "match_score":     round(float(d["match_score"]), 1),
            "seller_trust":    int(d["seller_trust"] or 0),
            "view_count":      int(d.get("view_count") or 0),
            "age_label":       _listing_age_label(d.get("published_at")),
            "is_featured":     bool(is_boosted) or (d.get("boost_rank") or 0) > 0,
            "matched_at":      d["matched_at"],
            "seen":            bool(d.get("seen")),
        })
    return {
        "tier": tier,
        "upgrade_prompt": upgrade_prompt,
        "cards": cards,
        "matcher": MATCHER.name,
    }


@app.post("/wishlist/feed/seen/{match_id}")
def mark_match_seen(match_id: int, buyer_token: str):
    """Buyer tapped or scrolled past — mark seen so it doesn't keep re-surfacing."""
    conn = database.get_db()
    conn.execute(
        "UPDATE wishlist_matches SET seen = 1 WHERE id = ? AND buyer_token = ?",
        (match_id, buyer_token)
    )
    conn.commit()
    conn.close()
    return {"message": "marked seen"}


@app.post("/listings/{listing_id}/view")
def increment_listing_view(listing_id: int):
    """Public view counter — feeds PR-30 demand signal on the feed card."""
    conn = database.get_db()
    conn.execute(
        "UPDATE listings SET view_count = COALESCE(view_count, 0) + 1 WHERE id = ?",
        (listing_id,)
    )
    conn.commit()
    conn.close()
    return {"message": "view counted"}


# ── SHOWCASE (curated empty-state feed) ──────────────────────

@app.get("/wishlist/showcase")
def get_showcase(limit: int = 30):
    """Public, anonymous. Curated by David via the admin tool. Drives the
    empty-state scroll for new visitors and registered buyers with <3 signals."""
    conn = database.get_db()
    rows = conn.execute(
        """SELECT s.id AS showcase_id, s.sort_order, s.added_at,
                  l.id AS listing_id, l.title, l.category, l.city, l.suburb,
                  l.thumb_url, l.medium_url, l.price,
                  l.trust_score AS listing_trust_score,
                  l.published_at, l.view_count
           FROM wishlist_showcase s
           JOIN listings l ON l.id = s.listing_id
           ORDER BY s.sort_order ASC, s.added_at DESC
           LIMIT ?""",
        (limit,)
    ).fetchall()
    conn.close()
    return [{
        "showcase_id":   r["showcase_id"],
        "listing_id":    r["listing_id"],
        "title":         r["title"],
        "category":      r["category"],
        "thumb_url":     r["thumb_url"],
        "medium_url":    r["medium_url"],
        "city":          r["city"],
        "suburb":        r["suburb"],
        "price":         r["price"],
        "trust_score":   r["listing_trust_score"] or 0,
        "view_count":    int(r["view_count"] or 0),
        "age_label":     _listing_age_label(r["published_at"]),
        "sort_order":    r["sort_order"],
    } for r in rows]


@app.post("/wishlist/showcase")
def add_showcase(listing_id: int, sort_order: int = 0, _key: str = Depends(auth.require_api_key)):
    """Admin-only — add a listing to the curated showcase."""
    conn = database.get_db()
    listing = conn.execute("SELECT id FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    try:
        conn.execute(
            "INSERT INTO wishlist_showcase (listing_id, sort_order, added_by) VALUES (?, ?, 'admin')",
            (listing_id, sort_order)
        )
        conn.commit()
    except Exception:
        conn.close()
        raise HTTPException(status_code=400, detail="Listing already in showcase")
    conn.close()
    return {"message": "Added to showcase", "listing_id": listing_id}


@app.put("/wishlist/showcase/{showcase_id}")
def reorder_showcase(showcase_id: int, sort_order: int, _key: str = Depends(auth.require_api_key)):
    """Admin-only — change the sort_order of an existing showcase entry."""
    conn = database.get_db()
    res = conn.execute(
        "UPDATE wishlist_showcase SET sort_order = ? WHERE id = ?",
        (sort_order, showcase_id)
    )
    if res.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Showcase entry not found")
    conn.commit()
    conn.close()
    return {"message": "Reordered", "showcase_id": showcase_id, "sort_order": sort_order}


@app.delete("/wishlist/showcase/{showcase_id}")
def remove_showcase(showcase_id: int, _key: str = Depends(auth.require_api_key)):
    """Admin-only — remove a listing from the curated showcase."""
    conn = database.get_db()
    res = conn.execute("DELETE FROM wishlist_showcase WHERE id = ?", (showcase_id,))
    if res.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Showcase entry not found")
    conn.commit()
    conn.close()
    return {"message": "Removed from showcase"}


# ── BOOST (2 Tuppence — PR-38) ───────────────────────────────

class BoostRequest(BaseModel):
    listing_id: int
    seller_email: str  # used to check seller owns the listing AND to charge transactions

BOOST_COST_T = 2
BOOST_DAYS = 7


@app.post("/wishlist/boost")
def boost_listing(req: BoostRequest, background_tasks: BackgroundTasks):
    """Spend 2T to boost a listing into matched feeds for 7 days.
    Verifies the seller owns the listing (seller_email match), checks Tuppence
    balance, deducts via the standard transactions table (type='boost_deduct'),
    extends boost_until, and re-runs the match job to surface this listing
    under the boosted threshold (45 instead of 60) — PR-38, PR-39, PR-41.
    """
    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (req.listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    if not listing["seller_email"] or listing["seller_email"] != req.seller_email:
        conn.close()
        raise HTTPException(status_code=403, detail="You do not own this listing")
    # Check Tuppence balance
    bal_row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS bal FROM transactions WHERE user_email = ?",
        (req.seller_email,)
    ).fetchone()
    balance = int(bal_row["bal"] or 0)
    if balance < BOOST_COST_T:
        conn.close()
        raise HTTPException(status_code=402, detail=f"Insufficient Tuppence — boost requires {BOOST_COST_T}T (you have {balance}T)")
    # Deduct 2T
    conn.execute(
        "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, ?, ?, ?)",
        (req.seller_email, "boost_deduct", -BOOST_COST_T,
         f"Listing boost · listing #{req.listing_id} · {BOOST_DAYS} days")
    )
    # Extend boost — if already boosted, extend by 7 more days from current expiry
    current_until = listing["boost_until"]
    base = datetime.now(timezone.utc)
    if current_until:
        try:
            existing_dt = datetime.fromisoformat(current_until)
            if existing_dt > base:
                base = existing_dt
        except Exception:
            pass
    new_until = (base + timedelta(days=BOOST_DAYS)).isoformat()
    conn.execute(
        "UPDATE listings SET boost_until = ? WHERE id = ?",
        (new_until, req.listing_id)
    )
    conn.commit()
    conn.close()
    # Re-run the match job under the boosted threshold (45) to surface to more buyers
    background_tasks.add_task(run_match_job, req.listing_id)
    return {
        "message": f"Listing boosted for {BOOST_DAYS} days",
        "listing_id": req.listing_id,
        "boost_until": new_until,
        "tuppence_charged": BOOST_COST_T,
    }


@app.get("/wishlist/boost/stats")
def boost_stats(listing_id: int, seller_email: str):
    """Aggregate-only stats for a boosted listing — never returns buyer identity (PR-42)."""
    conn = database.get_db()
    listing = conn.execute(
        "SELECT seller_email, boost_until FROM listings WHERE id = ?", (listing_id,)
    ).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["seller_email"] != seller_email:
        conn.close()
        raise HTTPException(status_code=403, detail="You do not own this listing")
    row = conn.execute(
        """SELECT COUNT(*) AS shown_to,
                  SUM(CASE WHEN seen = 1 THEN 1 ELSE 0 END) AS seen_by,
                  SUM(CASE WHEN pinged = 1 THEN 1 ELSE 0 END) AS pinged_to
           FROM wishlist_matches WHERE listing_id = ?""",
        (listing_id,)
    ).fetchone()
    conn.close()
    return {
        "listing_id": listing_id,
        "boost_until": listing["boost_until"],
        "shown_to_buyers": int(row["shown_to"] or 0),
        "seen_by_buyers": int(row["seen_by"] or 0),
        "pinged_to_buyers": int(row["pinged_to"] or 0),
        # Deliberately NO buyer_token, NO email, NO any identifier — PR-42
    }


# ── GLOBAL SUBSCRIPTION ($5/month — PR-16, PR-18) ────────────

# Paystack only quotes ZAR. $5 USD ≈ R90 at typical rates; pricing reviewed
# in cost model when activated. Currency conversion lives in payments helper.
WISHLIST_GLOBAL_USD = 5
WISHLIST_GLOBAL_ZAR = 90  # update from cost model when FX shifts


@app.post("/wishlist/subscription/initialize")
def init_global_subscription(buyer_token: str, email: str):
    """Start the Paystack flow for $5/month Global tier. Email is required by
    Paystack but is NOT stored against wishlist data — it lives only in the
    Paystack reference and the resulting subscription row's paystack_ref."""
    if not buyer_token or len(buyer_token) < 8:
        raise HTTPException(status_code=400, detail="valid buyer_token required")
    reference = f"ms_wishlist_{uuid.uuid4().hex[:12]}"
    result = payments.initialize_payment(
        email=email,
        amount_rands=WISHLIST_GLOBAL_ZAR,
        reference=reference,
        metadata={
            "wishlist_global": 1,
            "buyer_token": buyer_token,
            "tier": "global",
        }
    )
    if result.get("status"):
        return {
            "status": "ok",
            "reference": reference,
            "authorization_url": result["data"]["authorization_url"],
            "amount_rands": WISHLIST_GLOBAL_ZAR,
            "amount_usd": WISHLIST_GLOBAL_USD,
        }
    raise HTTPException(status_code=400, detail="Subscription initialization failed")


@app.get("/wishlist/subscription/verify")
def verify_global_subscription(reference: str):
    """Paystack callback — activate Global tier on success."""
    result = payments.verify_payment(reference)
    if result.get("status") and result["data"]["status"] == "success":
        meta = result["data"].get("metadata") or {}
        if int(meta.get("wishlist_global", 0)) != 1:
            raise HTTPException(status_code=400, detail="Reference is not a wishlist subscription")
        buyer_token = meta.get("buyer_token", "")
        if not buyer_token:
            raise HTTPException(status_code=400, detail="Missing buyer_token in metadata")
        now = datetime.now(timezone.utc)
        expires = (now + timedelta(days=30)).isoformat()
        conn = database.get_db()
        conn.execute(
            """INSERT INTO wishlist_subscriptions (buyer_token, tier, activated_at, expires_at, paystack_ref)
               VALUES (?, 'global', ?, ?, ?)
               ON CONFLICT(buyer_token) DO UPDATE SET
                   tier = 'global',
                   activated_at = excluded.activated_at,
                   expires_at = excluded.expires_at,
                   paystack_ref = excluded.paystack_ref""",
            (buyer_token, now.isoformat(), expires, reference)
        )
        conn.commit()
        conn.close()
        return {"status": "ok", "tier": "global", "expires_at": expires}
    raise HTTPException(status_code=400, detail="Payment verification failed")


@app.get("/wishlist/subscription/status")
def get_subscription_status(buyer_token: str):
    """Return current tier (free|global) for a buyer_token."""
    conn = database.get_db()
    tier = _buyer_tier(conn, buyer_token)
    row = conn.execute(
        "SELECT activated_at, expires_at FROM wishlist_subscriptions WHERE buyer_token = ?",
        (buyer_token,)
    ).fetchone()
    conn.close()
    return {
        "buyer_token": buyer_token,
        "tier": tier,
        "activated_at": row["activated_at"] if row else None,
        "expires_at": row["expires_at"] if row else None,
    }


# ── WEARABLE WEB PUSH (free VAPID — Section 5) ───────────────
# Uses the open Web Push standard with VAPID auth (RFC 8292). Free —
# no paid push service. Compatible with Android, modern Chrome / Edge /
# Firefox / Safari 16+, and most smartwatches that mirror phone notifs.
# Apple Watch via APNs requires a future native PWA wrapper — out of
# scope for V1 (PR-33). For V1 the same Web Push subscription a user
# creates on their phone surfaces on their wrist via OS notification
# mirroring on iOS 16+ and Wear OS.
#
# COST CONSTRAINT: pywebpush is a free Python library that talks
# directly to the browser push services (FCM/Mozilla/Apple) using the
# user's VAPID-signed subscription. NO paid SaaS in the path.

VAPID_KEY_PATH = os.getenv("MS_VAPID_KEY_PATH", "/etc/marketsquare-vapid.json")
VAPID_SUBJECT  = os.getenv("MS_VAPID_SUBJECT", "mailto:dmcontiki2@gmail.com")

_vapid_private_pem: Optional[str] = None
_vapid_public_b64: Optional[str] = None
_PUSH_AVAILABLE = False

try:
    from pywebpush import webpush as _webpush, WebPushException as _WebPushException
    _PUSH_AVAILABLE = True
except Exception as _exc:
    _log.warning("pywebpush not installed — wearable pings disabled (%s)", _exc)
    _webpush = None
    _WebPushException = Exception

def _bootstrap_vapid_keys():
    """Load VAPID keypair from disk; generate if missing. ZERO cost — pure
    elliptic-curve crypto from the cryptography stdlib. Safe to call repeatedly."""
    global _vapid_private_pem, _vapid_public_b64
    if not _PUSH_AVAILABLE:
        return
    if os.path.exists(VAPID_KEY_PATH):
        try:
            with open(VAPID_KEY_PATH, "r") as fh:
                cfg = json.load(fh)
            _vapid_private_pem = cfg.get("private_pem")
            _vapid_public_b64  = cfg.get("public_b64")
            if _vapid_private_pem and _vapid_public_b64:
                _log.info("VAPID keys loaded from %s", VAPID_KEY_PATH)
                return
        except Exception as exc:
            _log.warning("Could not load VAPID keys from %s: %s — regenerating", VAPID_KEY_PATH, exc)
    # Generate
    try:
        import base64
        from cryptography.hazmat.primitives.asymmetric import ec
        from cryptography.hazmat.primitives import serialization
        priv = ec.generate_private_key(ec.SECP256R1())
        pem  = priv.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode()
        pub_numbers = priv.public_key().public_numbers()
        # Uncompressed P-256 point: 0x04 || X(32) || Y(32)
        raw = b"\x04" + pub_numbers.x.to_bytes(32, "big") + pub_numbers.y.to_bytes(32, "big")
        pub_b64 = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
        try:
            os.makedirs(os.path.dirname(VAPID_KEY_PATH), exist_ok=True)
            with open(VAPID_KEY_PATH, "w") as fh:
                json.dump({"private_pem": pem, "public_b64": pub_b64}, fh)
            os.chmod(VAPID_KEY_PATH, 0o600)
        except Exception as exc:
            _log.warning("Could not persist VAPID keys to %s: %s — keeping in-memory only", VAPID_KEY_PATH, exc)
        _vapid_private_pem = pem
        _vapid_public_b64  = pub_b64
        _log.info("VAPID keypair generated · public_b64=%s…", pub_b64[:16])
    except Exception as exc:
        _log.error("VAPID bootstrap failed: %s", exc)

_bootstrap_vapid_keys()


class WearableRegisterReq(BaseModel):
    buyer_token: str
    push_endpoint: str
    push_keys: dict        # {"p256dh": "...", "auth": "..."}
    platform: str = "web"  # 'web' | 'android' | 'ios'
    device_label: Optional[str] = None


@app.get("/wishlist/vapid-public-key")
def get_vapid_public_key():
    """Frontend fetches this once during push subscription setup."""
    if not _vapid_public_b64:
        raise HTTPException(status_code=503, detail="Push not configured on server")
    return {"public_key": _vapid_public_b64}


@app.post("/wishlist/wearable/register")
def register_wearable(req: WearableRegisterReq):
    """Buyer subscribes a device. Idempotent on (buyer_token, push_endpoint).
    The endpoint URL alone is harmless — it cannot be used to find the buyer's
    identity. The browser-managed push_keys are needed to encrypt payloads
    so only the buyer's device can read them."""
    if not req.buyer_token or len(req.buyer_token) < 8:
        raise HTTPException(status_code=400, detail="valid buyer_token required")
    if not req.push_endpoint or not req.push_keys:
        raise HTTPException(status_code=400, detail="push_endpoint and push_keys required")
    conn = database.get_db()
    conn.execute(
        """INSERT INTO wearable_devices
             (buyer_token, push_endpoint, push_keys, platform, device_label)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(buyer_token, push_endpoint) DO UPDATE SET
             push_keys = excluded.push_keys,
             platform = excluded.platform,
             device_label = COALESCE(excluded.device_label, wearable_devices.device_label),
             enabled = 1""",
        (req.buyer_token, req.push_endpoint, json.dumps(req.push_keys),
         req.platform, req.device_label)
    )
    conn.commit()
    row = conn.execute(
        "SELECT id FROM wearable_devices WHERE buyer_token = ? AND push_endpoint = ?",
        (req.buyer_token, req.push_endpoint)
    ).fetchone()
    conn.close()
    return {"id": row["id"], "message": "Wearable registered"}


@app.get("/wishlist/wearable/list")
def list_wearables(buyer_token: str):
    """Return the buyer's registered devices — never includes push_keys."""
    conn = database.get_db()
    rows = conn.execute(
        """SELECT id, platform, device_label, enabled, created_at, last_ping_at
           FROM wearable_devices WHERE buyer_token = ? ORDER BY created_at DESC""",
        (buyer_token,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.delete("/wishlist/wearable/{device_id}")
def delete_wearable(device_id: int, buyer_token: str):
    """Buyer removes a device — sets enabled=0 and deletes the row."""
    conn = database.get_db()
    res = conn.execute(
        "DELETE FROM wearable_devices WHERE id = ? AND buyer_token = ?",
        (device_id, buyer_token)
    )
    if res.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Device not found for this buyer_token")
    conn.commit()
    conn.close()
    return {"message": "Wearable removed"}


def _send_push_for_match(buyer_token: str, match_id: int, listing: dict):
    """Fan out a push to every active wearable device for this buyer_token.
    Payload contains category + suburb/city + short description excerpt only —
    NO seller identity, NO price, NO listing_id (PR-35). Listing_id is fetched
    when the buyer opens the app via the standard feed flow.
    Never raises: failures are logged. Disabled devices (410 Gone) are auto-removed."""
    if not _PUSH_AVAILABLE or not _vapid_private_pem:
        return
    try:
        conn = database.get_db()
        rows = conn.execute(
            """SELECT id, push_endpoint, push_keys, platform FROM wearable_devices
               WHERE buyer_token = ? AND enabled = 1""",
            (buyer_token,)
        ).fetchall()
        if not rows:
            conn.close()
            return
        suburb_or_city = listing.get("suburb") or listing.get("city") or ""
        desc = (listing.get("description") or listing.get("title") or "").strip()
        if len(desc) > 90:
            desc = desc[:87] + "…"
        payload = json.dumps({
            "title": "✨ Match in your wishlist",
            "body":  f"{listing.get('category') or ''} · {suburb_or_city} · {desc}".strip(" ·"),
            "match_id": match_id,
            # NO seller_email, NO listing.id, NO price (PR-35)
        })
        delivered = 0
        for r in rows:
            try:
                _webpush(
                    subscription_info={
                        "endpoint": r["push_endpoint"],
                        "keys": json.loads(r["push_keys"]),
                    },
                    data=payload,
                    vapid_private_key=_vapid_private_pem,
                    vapid_claims={"sub": VAPID_SUBJECT},
                    timeout=8,
                )
                conn.execute(
                    "UPDATE wearable_devices SET last_ping_at = ? WHERE id = ?",
                    (datetime.now(timezone.utc).isoformat(), r["id"])
                )
                delivered += 1
            except _WebPushException as exc:
                # 404/410 = subscription gone; remove the dead device
                resp = getattr(exc, "response", None)
                status = getattr(resp, "status_code", None)
                if status in (404, 410):
                    conn.execute("DELETE FROM wearable_devices WHERE id = ?", (r["id"],))
                    _log.info("Removed dead push subscription %s (status %s)", r["id"], status)
                else:
                    _log.warning("Push failed for device %s: %s", r["id"], exc)
            except Exception as exc:
                _log.warning("Push failed for device %s: %s", r["id"], exc)
        conn.commit()
        conn.close()
        if delivered:
            _log.info("Pushed match %s to %d device(s) for buyer %s…",
                      match_id, delivered, buyer_token[:8])
    except Exception as exc:
        _log.error("_send_push_for_match failed: %s", exc)


# ── DEV TOOLS (disable before public launch) ─────────────────
# Allows the development team to seed Tuppence and AI coaching sessions
# without going through Paystack. All API costs run on the existing
# Anthropic / Hetzner billing. Remove or gate with a hard env-var check
# before the public launch of TrustSquare.

@app.post("/dev/credit")
def dev_credit(
    email: str,
    tuppence: int = 20,
    ai_sessions: int = 500,
    _key: str = Depends(auth.require_api_key)
):
    """Seed a dev/test account with Tuppence and AI coaching sessions.
    DEV PHASE ONLY — protected by API key.
    Remove this endpoint before public launch.
    """
    conn = database.get_db()

    # Upsert user — create if not exists, credit AI sessions if exists
    conn.execute(
        """INSERT INTO users (email, aa_free_used, aa_sessions_remaining)
           VALUES (?, 0, ?)
           ON CONFLICT(email) DO UPDATE SET
               aa_sessions_remaining = aa_sessions_remaining + ?""",
        (email, ai_sessions, ai_sessions)
    )

    # Credit Tuppence as a dev transaction
    if tuppence > 0:
        conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, ?, ?, ?)",
            (email, "dev_topup", tuppence,
             f"Dev credit — {tuppence}T Tuppence + {ai_sessions} AI sessions (pre-launch testing)")
        )

    conn.commit()

    user = conn.execute(
        "SELECT aa_sessions_remaining FROM users WHERE email = ?", (email,)
    ).fetchone()
    balance = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?", (email,)
    ).fetchone()
    conn.close()

    return {
        "email": email,
        "tuppence_balance": int(balance["bal"]),
        "ai_sessions_remaining": user["aa_sessions_remaining"] if user else ai_sessions,
        "warning": "⚠️ DEV ENDPOINT — disable before public launch"
    }


# ── EMAIL OPT-OUT ────────────────────────────────────────────
# Called when a prospect clicks "Unsubscribe" in an outreach email.
# Writes the suppression back into the CityLauncher SQLite DB via
# the CityLauncher API (running on same server at localhost:8001).
# Falls back to logging only if CityLauncher is unreachable.

CITYLAUNCHER_API = os.getenv("CITYLAUNCHER_API_URL", "http://localhost:8001")

@app.get("/opt-out")
async def opt_out(email: str, city_id: int = 0, category: str = ""):
    """
    One-click unsubscribe endpoint for outreach emails.
    Marks the prospect as opted_out in the CityLauncher database.
    Returns a friendly HTML confirmation page — no account needed.

    Query params:
      email      — prospect email address (URL-encoded)
      city_id    — CityLauncher city ID (0 = all cities for this email)
      category   — listing category (empty = all categories for this email)
    """
    _log.info(f"Opt-out request: email={email} city_id={city_id} category={category}")

    suppressed = False
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(
                f"{CITYLAUNCHER_API}/prospects/opt-out",
                json={"email": email, "city_id": city_id, "category": category}
            )
            if resp.status_code in (200, 204):
                suppressed = True
                _log.info(f"Opt-out confirmed by CityLauncher for {email}")
            else:
                _log.warning(f"CityLauncher opt-out returned {resp.status_code} for {email}")
    except Exception as exc:
        _log.error(f"Could not reach CityLauncher for opt-out: {exc}")

    # Return a clean HTML confirmation regardless of backend success
    html_response = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Unsubscribed — TrustSquare</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #f5f5f0; display: flex; align-items: center; justify-content: center;
            min-height: 100vh; margin: 0; }}
    .card {{ background: #fff; border-radius: 12px; padding: 48px 40px; max-width: 440px;
             text-align: center; box-shadow: 0 2px 16px rgba(0,0,0,0.08); }}
    .icon {{ font-size: 48px; margin-bottom: 16px; }}
    h1 {{ font-size: 22px; font-weight: 700; color: #1a1a2e; margin-bottom: 12px; }}
    p {{ font-size: 15px; color: #666; line-height: 1.6; }}
    a {{ color: #1a1a2e; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="icon">✅</div>
    <h1>You're unsubscribed</h1>
    <p>We've removed <strong>{email}</strong> from our outreach list.<br>
    You won't receive any further emails from TrustSquare about listing opportunities.</p>
    <p style="margin-top:24px; font-size:13px; color:#aaa;">
      Changed your mind? Visit <a href="https://trustsquare.co">trustsquare.co</a> to list directly.
    </p>
  </div>
</body>
</html>"""

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_response, status_code=200)
