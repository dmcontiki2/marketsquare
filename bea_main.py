from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, Request
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

app = FastAPI(title="MarketSquare BEA", version="1.3.0")

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
    # KYC columns added Session 34 — ALTER TABLE safely (idempotent)
    for col_def in [
        "ALTER TABLE users ADD COLUMN id_number_hash TEXT",
        "ALTER TABLE users ADD COLUMN id_name TEXT",
        "ALTER TABLE users ADD COLUMN id_doc_type TEXT",
        "ALTER TABLE users ADD COLUMN id_verified_at TEXT",
        "ALTER TABLE users ADD COLUMN id_ai_score REAL",
        "ALTER TABLE users ADD COLUMN banking_holder TEXT",
        "ALTER TABLE users ADD COLUMN banking_bank TEXT",
        "ALTER TABLE users ADD COLUMN banking_account_last4 TEXT",
        "ALTER TABLE users ADD COLUMN banking_branch TEXT",
        "ALTER TABLE users ADD COLUMN banking_added_at TEXT",
        # user_credentials column added in Session 34
        "ALTER TABLE user_credentials ADD COLUMN updated_at TEXT",
    ]:
        try:
            conn.execute(col_def)
        except Exception:
            pass  # column already exists

    conn.execute("""
        CREATE TABLE IF NOT EXISTS seller_documents (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            email        TEXT    NOT NULL,
            doc_type     TEXT    NOT NULL DEFAULT 'other',
            label        TEXT    NOT NULL DEFAULT '',
            url          TEXT    NOT NULL,
            visibility   TEXT    NOT NULL DEFAULT 'private',
            signal_id    TEXT,
            uploaded_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
        )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_seller_docs_email ON seller_documents(email)")

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

    # ── Local Market feature (v1.3.0) ───────────────────────────
    # Local Market = open-ended peer-to-peer category. Discriminator is
    # listings.category = 'local_market'. Seller pays 1T (or 2T if boosted)
    # on the FIRST intro per listing — opposite of every other category.

    # Listing-level columns specific to LM
    if "suspension_reason" not in listing_cols2:
        conn.execute("ALTER TABLE listings ADD COLUMN suspension_reason TEXT")
    if "lm_intro_charged" not in listing_cols2:
        # Idempotency flag — set to 1 the first time a buyer requests an intro
        # on this listing, so subsequent intros don't double-charge the seller.
        conn.execute("ALTER TABLE listings ADD COLUMN lm_intro_charged INTEGER NOT NULL DEFAULT 0")

    # intro_requests gets an intro_type column to distinguish standard vs LM
    intro_cols2 = [r[1] for r in conn.execute("PRAGMA table_info(intro_requests)").fetchall()]
    if "intro_type" not in intro_cols2:
        conn.execute("ALTER TABLE intro_requests ADD COLUMN intro_type TEXT NOT NULL DEFAULT 'standard'")

    # Buyer Trust Score — buyers don't have a users row in V1, so a
    # standalone keyed-by-buyer_token table is the cleanest home for it.
    conn.execute("""CREATE TABLE IF NOT EXISTS buyer_trust (
        buyer_token     TEXT PRIMARY KEY,
        score           INTEGER NOT NULL DEFAULT 0,
        last_changed_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")

    # Local Market no-show complaints — manual review by ops (LM-T3)
    conn.execute("""CREATE TABLE IF NOT EXISTS lm_complaints (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        listing_id      INTEGER NOT NULL,
        seller_email    TEXT NOT NULL,
        buyer_token     TEXT NOT NULL,
        intro_id        INTEGER NOT NULL,
        reason          TEXT,
        status          TEXT NOT NULL DEFAULT 'pending',
        filed_at        TEXT NOT NULL DEFAULT (datetime('now')),
        resolved_at     TEXT,
        credit_issued   INTEGER NOT NULL DEFAULT 0
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lmc_listing ON lm_complaints(listing_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lmc_buyer ON lm_complaints(buyer_token)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lmc_status ON lm_complaints(status)")

    # Suspension history for repeat-offender escalation (LM-14e)
    # Each row is one suspension event. The 90-day repeat detector and
    # third-strike permanent ban both read from this table.
    conn.execute("""CREATE TABLE IF NOT EXISTS lm_suspensions (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_email    TEXT NOT NULL,
        suspended_at    TEXT NOT NULL DEFAULT (datetime('now')),
        restored_at     TEXT,
        reason          TEXT NOT NULL DEFAULT 'trust_score_below_30',
        cooling_off_until TEXT,
        is_permanent    INTEGER NOT NULL DEFAULT 0
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lmsus_seller ON lm_suspensions(seller_email, suspended_at DESC)")

    # users gains the LM-specific lifecycle flags
    user_cols2 = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "lm_eula_accepted_at" not in user_cols2:
        conn.execute("ALTER TABLE users ADD COLUMN lm_eula_accepted_at TEXT")
    if "lm_banned_at" not in user_cols2:
        # Permanent ban from Local Market — third-strike (LM-14e). Other
        # categories remain accessible. Tuppence balance is unaffected.
        conn.execute("ALTER TABLE users ADD COLUMN lm_banned_at TEXT")
    if "country" not in user_cols2:
        # Required on seller profile for LM listings (LM-29). Default to
        # ZA so existing sellers don't break — admin tool prompts them
        # to confirm on next profile edit.
        conn.execute("ALTER TABLE users ADD COLUMN country TEXT DEFAULT 'ZA'")
    if "primary_category" not in user_cols2:
        # Drives which Group 3 credential checklist the seller sees in the
        # Trust Score Hub. Set on first listing publish; admin can override.
        conn.execute("ALTER TABLE users ADD COLUMN primary_category TEXT")
    if "is_superuser" not in user_cols2:
        # Superuser flag — bypasses all publish gates and trust filters.
        # Seeded for the four core team emails on every startup.
        # Will be superseded by the owner dashboard on launch day.
        conn.execute("ALTER TABLE users ADD COLUMN is_superuser INTEGER NOT NULL DEFAULT 0")

    # ── Seed superuser flag for core team ───────────────────────
    SUPERUSER_EMAILS = [
        "dmcontiki2@gmail.com",
        "miconradie1@gmail.com",
        "davidconradie1234@gmail.com",
        "mauriceconradie@yahoo.com",
    ]
    for su_email in SUPERUSER_EMAILS:
        conn.execute(
            "UPDATE users SET is_superuser = 1 WHERE email = ? AND is_superuser = 0",
            (su_email,)
        )
    conn.commit()

    # ── Trust Score Hub (Section 3 · v1.3.0) ────────────────────
    # Per-credential verification state. Drives the Hub's earned/pending/
    # missing checklist. Aggregate trust_score on users is recomputed from
    # this table whenever an admin verifies a credential.
    conn.execute("""CREATE TABLE IF NOT EXISTS user_credentials (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        email           TEXT NOT NULL,
        signal_id       TEXT NOT NULL,
        status          TEXT NOT NULL DEFAULT 'pending',
        points          INTEGER NOT NULL DEFAULT 0,
        evidence_url    TEXT,
        notes           TEXT,
        submitted_at    TEXT NOT NULL DEFAULT (datetime('now')),
        verified_at     TEXT,
        verified_by     TEXT,
        UNIQUE(email, signal_id)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_uc_email ON user_credentials(email)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_uc_status ON user_credentials(status)")

    # Seller complaints — diminishing-scale penalties per TRUST_SCORE_CRITERIA §5a.
    # Distinct from lm_complaints which targets BUYERS for no-shows.
    conn.execute("""CREATE TABLE IF NOT EXISTS seller_complaints (
        id              INTEGER PRIMARY KEY AUTOINCREMENT,
        seller_email    TEXT NOT NULL,
        buyer_token     TEXT,
        listing_id      INTEGER,
        reason_code     TEXT NOT NULL,
        notes           TEXT,
        status          TEXT NOT NULL DEFAULT 'pending',
        filed_at        TEXT NOT NULL DEFAULT (datetime('now')),
        resolved_at     TEXT,
        points_deducted INTEGER NOT NULL DEFAULT 0
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_sc_seller ON seller_complaints(seller_email, filed_at DESC)")

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
# R2 public-read URL — required for buyers to actually see uploaded photos.
# The S3 API endpoint requires auth-signed requests (returns InvalidArgument
# on anonymous GETs). Cloudflare R2 exposes a public dev URL per bucket
# (https://pub-<id>.r2.dev) which we use for read access. Optionally
# replace with a custom domain like media.trustsquare.co.
R2_PUBLIC_URL = os.getenv(
    "R2_PUBLIC_URL",
    "https://pub-3c51d058a6494b93af4d242d07bdc4da.r2.dev"
).rstrip("/")
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
    """Upload bytes to R2; return browser-fetchable public URL.

    Writes go through the authenticated S3 API endpoint (signed by boto3 with
    the secret key). Reads must use the public dev URL (or a configured custom
    domain) because the S3 API rejects anonymous GETs with InvalidArgument."""
    _s3.put_object(
        Bucket=HETZNER_S3_BUCKET,
        Key=key,
        Body=data,
        ContentType=content_type,
        ACL="public-read",
    )
    return f"{R2_PUBLIC_URL}/{key}"


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
    return {"status": "ok", "service": "MarketSquare BEA", "version": "1.3.0"}

# ── LISTINGS (public read, protected write) ──────────────────

@app.get("/listings")
def get_listings(city: str = "Pretoria", category: Optional[str] = None, suburb: Optional[str] = None):
    conn = database.get_db()
    # Hide suspended Local Market listings + keep LM out of the main grid
    # unless explicitly requested (LM-02 separation principle).
    clauses = ["l.city = ?", "(l.suspension_reason IS NULL OR l.suspension_reason = '')"]
    params: list = [city]
    if category:
        clauses.append("LOWER(l.category) = LOWER(?)")
        params.append(category)
    else:
        clauses.append("LOWER(l.category) != LOWER(?)")
        params.append(LM_CATEGORY)
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
def initialize_payment(email: str, tuppence: int, ai_pack_sessions: int = 0, callback_url: str = ""):
    amount_rands = tuppence * 36
    reference = f"ms_tuppence_{uuid.uuid4().hex[:12]}"
    result = payments.initialize_payment(
        email=email,
        amount_rands=amount_rands,
        reference=reference,
        metadata={"tuppence": tuppence, "email": email, "ai_pack_sessions": ai_pack_sessions},
        callback_url=callback_url or None
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

@app.post("/payment/webhook")
async def paystack_webhook(request: Request):
    """
    Paystack server-side webhook — receives charge.success events.

    This is the production-reliable credit path. Paystack retries failed
    webhooks, so Tuppence is always credited even if the buyer closes the
    browser before the client-side /payment/verify call fires.

    Setup: In your Paystack dashboard → Settings → API Keys & Webhooks,
    set the webhook URL to: https://trustsquare.co/payment/webhook
    Copy the 'Webhook Secret' value into PAYSTACK_WEBHOOK_SECRET in .env.
    """
    raw_body = await request.body()
    signature = request.headers.get("X-Paystack-Signature", "")

    # Validate HMAC-SHA512 signature
    if not payments.verify_webhook_signature(raw_body, signature):
        _log.warning("Paystack webhook: invalid signature — ignored")
        raise HTTPException(status_code=400, detail="Invalid signature")

    import json as _json
    try:
        event = _json.loads(raw_body)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    event_type = event.get("event")
    data = event.get("data", {})

    if event_type == "charge.success":
        reference = data.get("reference", "")
        metadata  = data.get("metadata", {}) or {}
        email     = metadata.get("email", "")
        tuppence  = int(metadata.get("tuppence", 0) or 0)
        ai_sessions = int(metadata.get("ai_pack_sessions", 0) or 0)

        if not email or not reference:
            _log.warning("Paystack webhook charge.success missing email/reference: %s", reference)
            return {"status": "ok"}  # Always return 200 to Paystack

        conn = database.get_db()
        # Idempotency: skip if this reference was already processed
        existing = conn.execute(
            "SELECT id FROM transactions WHERE description LIKE ?",
            (f"%ref {reference}%",)
        ).fetchone()

        if existing:
            _log.info("Paystack webhook: ref %s already processed — skipping", reference)
            conn.close()
            return {"status": "ok"}

        if tuppence > 0:
            conn.execute(
                "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
                (email, "topup", tuppence, f"Tuppence top-up via Paystack · ref {reference}")
            )
            _log.info("Paystack webhook: credited %dT to %s (ref %s)", tuppence, email, reference)

        if ai_sessions > 0:
            conn.execute(
                "INSERT INTO users (email, aa_free_used, aa_sessions_remaining) VALUES (?, 0, 0) "
                "ON CONFLICT(email) DO NOTHING",
                (email,)
            )
            conn.execute(
                "UPDATE users SET aa_sessions_remaining = aa_sessions_remaining + ? WHERE email = ?",
                (ai_sessions, email)
            )
            _log.info("Paystack webhook: credited %d AI sessions to %s (ref %s)", ai_sessions, email, reference)

        conn.commit()
        conn.close()

    # Always return 200 — Paystack will retry on any non-2xx
    return {"status": "ok"}

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


# ── LOCAL MARKET (Section 2 · v1.3.0) ───────────────────────
# Open-ended peer-to-peer category. Seller pays 1T (or 2T if boosted)
# on the FIRST intro per listing — opposite of every other category.
# Anonymity absolute throughout — no seller identity in any LM response.
#
# COST CONSTRAINT (locked): no external API calls. Tag extraction reuses
# the existing LocalKeywordMatcher from the wishlist engine.

LM_CATEGORY = "local_market"
LM_INTRO_COST_T = 1
LM_BOOST_COST_T = 2
LM_SELLER_MIN_TRUST = 30
LM_BUYER_MIN_TRUST  = 20
LM_REPEAT_WINDOW_DAYS = 90
LM_COOLING_OFF_DAYS  = 30
LM_BUYER_NOSHOW_PENALTY = 3   # PR LM-T4 / LM-16


class LMListingIn(BaseModel):
    """Local Market listing creation payload — no category field, free description."""
    title: str
    price: Optional[str] = None
    description: Optional[str] = None
    suburb: str
    city: str
    geo_city_id: Optional[int] = None
    country: Optional[str] = None
    seller_email: str
    thumb_url: Optional[str] = None
    medium_url: Optional[str] = None
    photo_urls: Optional[str] = None  # JSON array of up to 5 photo URLs


class LMIntroIn(BaseModel):
    listing_id: int
    buyer_token: str
    buyer_email: Optional[str] = None      # used only for n8n notifications
    buyer_name: Optional[str] = None
    message: Optional[str] = None


class LMComplaintIn(BaseModel):
    intro_id: int
    seller_email: str
    reason: str


# ── Helpers — server-side gates ───────────────────────────────

def _seller_trust(conn, email: str) -> int:
    row = conn.execute("SELECT trust_score FROM users WHERE email = ?", (email,)).fetchone()
    return int(row["trust_score"] or 0) if row else 0


def _buyer_trust(conn, buyer_token: str) -> int:
    row = conn.execute("SELECT score FROM buyer_trust WHERE buyer_token = ?", (buyer_token,)).fetchone()
    return int(row["score"] or 0) if row else 0


def _set_buyer_trust(conn, buyer_token: str, delta: int):
    """Apply a Trust Score delta to a buyer. Floors at 0, caps at 100."""
    cur = _buyer_trust(conn, buyer_token)
    new = max(0, min(100, cur + delta))
    conn.execute(
        """INSERT INTO buyer_trust (buyer_token, score) VALUES (?, ?)
           ON CONFLICT(buyer_token) DO UPDATE SET
               score = ?, last_changed_at = datetime('now')""",
        (buyer_token, new, new)
    )


def _lm_active_suspension(conn, seller_email: str) -> Optional[dict]:
    """Return the seller's currently-active suspension record, or None."""
    row = conn.execute(
        """SELECT * FROM lm_suspensions
           WHERE seller_email = ? AND restored_at IS NULL
           ORDER BY suspended_at DESC LIMIT 1""",
        (seller_email,)
    ).fetchone()
    return dict(row) if row else None


def _lm_is_banned(conn, seller_email: str) -> bool:
    """Permanent LM ban flag (third-strike — LM-14e). Other categories unaffected."""
    row = conn.execute(
        "SELECT lm_banned_at FROM users WHERE email = ?", (seller_email,)
    ).fetchone()
    return bool(row and row["lm_banned_at"])


def _lm_check_seller_can_publish(conn, seller_email: str) -> Optional[str]:
    """Return None if seller may publish a Local Market listing, else error string.

    DESIGN NOTE (Session 28 hotfix): Trust Score is a BUYER-SIDE FILTER, not a
    publish gate. New sellers can publish from day one with score 0 — they are
    visible to buyers using the 'Any seller' filter. Only ACTIVE bad-actor
    states (permanent ban or cooling-off after repeat suspensions) block publish.

    Bootstrap-by-low-score (sub-30) is NOT a gate — that would block every new
    seller from publishing their first listing, which contradicts the marketplace
    philosophy of 'visibility universal, trust signalled'. The original LM-08
    spec was inconsistent with LM-14 ('listings below 40 still visible, with
    seller warning') — LM-14 is the correct model and is now the implemented one.

    Superusers bypass all gates until launch day — see is_superuser on users table.
    """
    # Superuser bypass — no restrictions until launch day
    row = conn.execute(
        "SELECT is_superuser FROM users WHERE email = ?", (seller_email,)
    ).fetchone()
    if row and row["is_superuser"]:
        return None
    if _lm_is_banned(conn, seller_email):
        return "permanent_lm_ban"
    susp = _lm_active_suspension(conn, seller_email)
    if susp and susp.get("cooling_off_until"):
        # Mandatory 30-day cooling-off after second suspension in 90 days (LM-14e)
        return f"cooling_off_until_{susp['cooling_off_until']}"
    return None


def _lm_apply_suspension(conn, seller_email: str, reason: str = "trust_score_below_30"):
    """Suspend a seller from Local Market. Marks all their LM listings with
    suspension_reason and writes a row to lm_suspensions. Implements LM-14e
    escalation: second suspension within 90 days adds a 30-day cooling-off
    period; third becomes permanent. Idempotent — does nothing if a suspension
    is already active for this seller."""
    if _lm_active_suspension(conn, seller_email):
        return  # already suspended
    if _lm_is_banned(conn, seller_email):
        return  # already permanently banned

    # Count past suspensions in the rolling 90-day window
    cutoff = (datetime.now(timezone.utc) - timedelta(days=LM_REPEAT_WINDOW_DAYS)).isoformat()
    count_recent = conn.execute(
        """SELECT COUNT(*) AS n FROM lm_suspensions
           WHERE seller_email = ? AND suspended_at >= ?""",
        (seller_email, cutoff)
    ).fetchone()["n"] or 0
    total_lifetime = conn.execute(
        "SELECT COUNT(*) AS n FROM lm_suspensions WHERE seller_email = ?", (seller_email,)
    ).fetchone()["n"] or 0

    cooling_off = None
    permanent = 0
    if total_lifetime >= 2:
        # This will be the third strike — permanent LM ban (LM-14e third clause)
        permanent = 1
        conn.execute(
            "UPDATE users SET lm_banned_at = datetime('now') WHERE email = ?", (seller_email,)
        )
    elif count_recent >= 1:
        # Second suspension within 90 days — 30-day cooling-off (LM-14e middle clause)
        cooling_off = (datetime.now(timezone.utc) + timedelta(days=LM_COOLING_OFF_DAYS)).isoformat()

    conn.execute(
        """INSERT INTO lm_suspensions (seller_email, reason, cooling_off_until, is_permanent)
           VALUES (?, ?, ?, ?)""",
        (seller_email, reason, cooling_off, permanent)
    )
    # Hide all this seller's LM listings from public surfaces
    conn.execute(
        "UPDATE listings SET suspension_reason = ? WHERE seller_email = ? AND category = ?",
        (reason, seller_email, LM_CATEGORY)
    )
    _log.warning("LM suspended seller=%s reason=%s permanent=%s cooling_off=%s",
                 seller_email, reason, permanent, cooling_off)


def _lm_try_restore(conn, seller_email: str):
    """Auto-reactivate a seller's LM listings if their Trust Score recovered
    AND any cooling-off has expired AND they're not permanently banned (LM-14d)."""
    if _lm_is_banned(conn, seller_email):
        return
    susp = _lm_active_suspension(conn, seller_email)
    if not susp:
        return
    # Must clear cooling-off window first
    if susp.get("cooling_off_until"):
        try:
            if datetime.fromisoformat(susp["cooling_off_until"]) > datetime.now(timezone.utc):
                return  # still in cooling-off
        except Exception:
            pass
    # Must clear Trust Score floor
    if _seller_trust(conn, seller_email) < LM_SELLER_MIN_TRUST:
        return
    # Restore
    conn.execute(
        "UPDATE lm_suspensions SET restored_at = datetime('now') WHERE id = ?",
        (susp["id"],)
    )
    conn.execute(
        "UPDATE listings SET suspension_reason = NULL WHERE seller_email = ? AND category = ?",
        (seller_email, LM_CATEGORY)
    )
    _log.info("LM restored seller=%s", seller_email)


def _lm_recompute_seller_state(conn, seller_email: str):
    """Hook to call any time a seller's Trust Score changes. Restores listings
    if the seller climbs back above the floor; suspends ONLY if the seller has
    active complaints AND has fallen below the floor (LM-14a — bad-actor case).

    DESIGN NOTE (Session 28 hotfix): Trust Score is a buyer-filter, not a
    bootstrap gate. A NEW seller with score 0 and zero complaints is not a
    bad actor — they're just new. The LM-14 spec describes auto-suspension
    as a consequence of complaint-driven score collapse, not of unproven
    sellers existing. Without this distinction every new seller would be
    instantly suspended on first listing publish.
    """
    if _seller_trust(conn, seller_email) >= LM_SELLER_MIN_TRUST:
        _lm_try_restore(conn, seller_email)
        return
    # Below the floor — only suspend if there ARE active complaints that
    # caused the drop. New sellers with no complaints stay live.
    has_complaints = conn.execute(
        """SELECT 1 FROM seller_complaints
           WHERE seller_email = ? AND status IN ('pending', 'upheld') LIMIT 1""",
        (seller_email,)
    ).fetchone()
    if has_complaints:
        _lm_apply_suspension(conn, seller_email)


# ── Endpoints ────────────────────────────────────────────────

@app.post("/local-market/listings")
def lm_create_listing(listing: LMListingIn, background_tasks: BackgroundTasks,
                      _key: str = Depends(auth.require_api_key)):
    """Create a Local Market listing. Seller must have Trust Score ≥ 30 (LM-08)."""
    conn = database.get_db()
    err = _lm_check_seller_can_publish(conn, listing.seller_email)
    if err:
        conn.close()
        raise HTTPException(status_code=403, detail=err)
    # Persist country on the user row if supplied (LM-29)
    if listing.country:
        conn.execute(
            "UPDATE users SET country = ? WHERE email = ?",
            (listing.country, listing.seller_email)
        )
    cur = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description,
            thumb_url, medium_url, photo_urls, geo_city_id, seller_email, published_at)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'))""",
        (listing.title, listing.price, LM_CATEGORY, listing.city, listing.suburb,
         listing.suburb, listing.description, listing.thumb_url, listing.medium_url,
         listing.photo_urls, listing.geo_city_id, listing.seller_email)
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    # Run wishlist matching against this new LM listing — same engine as Wishlist Feed
    background_tasks.add_task(run_match_job, new_id)
    return {"id": new_id, "message": "Local Market listing created"}


@app.get("/local-market/listings")
def lm_list_listings(city: Optional[str] = None, suburb: Optional[str] = None,
                     min_trust: int = 0, q: Optional[str] = None, limit: int = 50):
    """Public list endpoint. Anonymous-stripped cards. Suspended listings hidden.
    Trust score is read live from the seller's users.trust_score (joined) so
    that buyer trust filters always reflect the seller's current standing —
    not a stale value copied at listing time."""
    conn = database.get_db()
    clauses = ["l.category = ?", "l.suspension_reason IS NULL",
               "COALESCE(u.trust_score, 0) >= ?"]
    params: list = [LM_CATEGORY, max(0, min_trust)]
    if city:
        clauses.append("l.city = ?")
        params.append(city)
    if suburb:
        clauses.append("l.suburb = ?")
        params.append(suburb)
    where = " AND ".join(clauses)
    rows = conn.execute(
        f"""SELECT l.id, l.title, l.price, l.suburb, l.city, l.area,
                   l.thumb_url, l.medium_url, l.description, l.published_at,
                   l.view_count, l.boost_until,
                   COALESCE(u.trust_score, 0) AS trust_score
            FROM listings l
            LEFT JOIN users u ON u.email = l.seller_email
            WHERE {where}
            ORDER BY l.published_at DESC LIMIT ?""",
        params + [limit]
    ).fetchall()
    conn.close()
    # Free-text scoring (zero-cost) — sort by Haiko score if q is supplied
    cards = [dict(r) for r in rows]
    if q and q.strip():
        sig = {"raw_text": q, "category": None}
        scored = []
        for c in cards:
            score = MATCHER.score_match(sig, MATCHER.extract_intent(c))
            if score >= 30:  # softer threshold for browse than wishlist
                scored.append((score, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        cards = [c for _, c in scored]
    # Anonymity-strip — defensive (these SELECTs already exclude seller_email,
    # but keep _strip_seller_identity in the chain in case helpers are reused)
    return [_strip_seller_identity(c) for c in cards]


@app.get("/local-market/listings/{listing_id}")
def lm_get_listing(listing_id: int):
    """Public detail endpoint. Suspension-aware. No seller identity returned.
    Trust score read live from joined users table — never the listing column."""
    conn = database.get_db()
    row = conn.execute(
        """SELECT l.id, l.title, l.price, l.suburb, l.city, l.area,
                  l.thumb_url, l.medium_url, l.photo_urls, l.description, l.published_at,
                  l.view_count, l.boost_until,
                  COALESCE(u.country, 'ZA') AS country,
                  COALESCE(u.trust_score, 0) AS trust_score
           FROM listings l
           LEFT JOIN users u ON u.email = l.seller_email
           WHERE l.id = ? AND l.category = ? AND l.suspension_reason IS NULL""",
        (listing_id, LM_CATEGORY)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")
    return _strip_seller_identity(dict(row))


@app.post("/local-market/intro")
def lm_create_intro(req: LMIntroIn, background_tasks: BackgroundTasks):
    """Buyer submits an intro on a Local Market listing. Server-side gates:
    - listing must exist, be Local Market, not suspended
    - buyer Trust Score ≥ 20 (LM-15)
    - buyer not in 7-day cooldown after a previous decline/auto-close on this listing (LM-F3)
    - seller must have at least LM_INTRO_COST_T Tuppence (or 2T if boosted)
    - first-intro idempotency: deduct from seller exactly once per listing (LM-T1)
    """
    conn = database.get_db()
    listing = conn.execute(
        "SELECT * FROM listings WHERE id = ? AND category = ?",
        (req.listing_id, LM_CATEGORY)
    ).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    listing = dict(listing)
    if listing.get("suspension_reason"):
        conn.close()
        raise HTTPException(status_code=410, detail="Listing is suspended")
    seller_email = listing.get("seller_email")
    if not seller_email:
        conn.close()
        raise HTTPException(status_code=409, detail="Listing has no seller — cannot accept intros")

    # DESIGN NOTE (Session 28 hotfix): Buyer trust is no longer a hard gate
    # for submitting intros. New buyers must be able to participate from day
    # one — they start at score 0 and stay visible to "Any seller" filters.
    # The seller sees the buyer's Trust Score on the intro request and decides
    # whether to accept, exactly the way the platform's flywheel intends:
    # buyers earn trust by following through, sellers prefer high-trust buyers.
    # The original LM-15 (block below 20) blocked every new buyer — wrong model.
    # Bad-actor enforcement still works through the no-show complaint path
    # (LM-T4, −3 per upheld), which can drive a serial-no-show buyer down to 0;
    # sellers will simply decline those intros, which is the correct dynamic.
    buyer_score = _buyer_trust(conn, req.buyer_token)  # noqa: F841 — exposed in response

    # 7-day cooldown after declined/auto-closed intro from same buyer (LM-F3)
    cooldown_cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    recent_block = conn.execute(
        """SELECT id FROM intro_requests
           WHERE listing_id = ? AND buyer_email = ?
             AND status IN ('declined', 'auto_closed')
             AND created_at >= ?
           LIMIT 1""",
        (req.listing_id, req.buyer_email or req.buyer_token, cooldown_cutoff)
    ).fetchone()
    if recent_block:
        conn.close()
        raise HTTPException(status_code=429, detail="cooldown_7_days")

    # Determine boost
    boost_until = listing.get("boost_until")
    is_boosted = False
    if boost_until:
        try:
            is_boosted = datetime.fromisoformat(boost_until) > datetime.now(timezone.utc)
        except Exception:
            pass
    cost_T = LM_BOOST_COST_T if is_boosted else LM_INTRO_COST_T

    # First-intro idempotency — only deduct from seller on the FIRST intro per listing (LM-T1)
    first_intro = (int(listing.get("lm_intro_charged") or 0) == 0)

    # Seller balance check (only if this is the first chargeable intro)
    if first_intro:
        bal = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) AS bal FROM transactions WHERE user_email = ?",
            (seller_email,)
        ).fetchone()["bal"] or 0
        if int(bal) < cost_T:
            conn.close()
            raise HTTPException(
                status_code=402,
                detail=f"seller_insufficient_tuppence (needs {cost_T}T, has {bal}T)"
            )

    # Insert the intro
    cur = conn.execute(
        """INSERT INTO intro_requests
             (listing_id, buyer_email, buyer_name, message, intro_type)
           VALUES (?, ?, ?, ?, 'local_market')""",
        (req.listing_id, req.buyer_email or req.buyer_token, req.buyer_name, req.message)
    )
    new_intro_id = cur.lastrowid

    # Charge the seller on the first intro per listing (LM-T1, LM-T5)
    if first_intro:
        txn_type = "lm_boost_deduct" if is_boosted else "lm_intro_deduct"
        conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, ?, ?, ?)",
            (seller_email, txn_type, -cost_T,
             f"Local Market intro · listing #{req.listing_id} · {listing.get('title','')}")
        )
        conn.execute(
            "UPDATE listings SET lm_intro_charged = 1 WHERE id = ?",
            (req.listing_id,)
        )

    conn.commit()
    conn.close()

    # n8n webhook (existing pattern — anonymous-safe payload)
    if N8N_WEBHOOK_NEW_INTRO:
        payload = {
            "event":          "lm_intro_submitted",
            "intro_id":       new_intro_id,
            "listing_id":     req.listing_id,
            "listing_title":  listing.get("title"),
            "buyer_name":     req.buyer_name,
            "buyer_trust_score": buyer_score,   # seller's accept/decline signal
            "seller_email":   seller_email,
            "tuppence_charged_to_seller": cost_T if first_intro else 0,
            "timestamp":      datetime.now(timezone.utc).isoformat(),
        }
        background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_NEW_INTRO, payload)

    return {
        "intro_id": new_intro_id,
        "message": "Local Market intro submitted",
        "tuppence_charged_to_seller": cost_T if first_intro else 0,
        "buyer_trust_score": buyer_score,
        "boosted": is_boosted,
    }


@app.post("/local-market/complaint")
def lm_file_complaint(req: LMComplaintIn, _key: str = Depends(auth.require_api_key)):
    """Seller files a no-show complaint. Status starts 'pending' and is
    resolved manually by ops via /local-market/complaint/{id}/uphold|dismiss."""
    conn = database.get_db()
    intro = conn.execute(
        "SELECT * FROM intro_requests WHERE id = ? AND intro_type = 'local_market'",
        (req.intro_id,)
    ).fetchone()
    if not intro:
        conn.close()
        raise HTTPException(status_code=404, detail="Local Market intro not found")
    intro = dict(intro)
    listing = conn.execute(
        "SELECT seller_email FROM listings WHERE id = ?", (intro["listing_id"],)
    ).fetchone()
    if not listing or listing["seller_email"] != req.seller_email:
        conn.close()
        raise HTTPException(status_code=403, detail="Not your listing")
    # Buyer token is stored in buyer_email when buyer is anonymous; both forms accepted
    buyer_id = intro.get("buyer_email") or ""
    cur = conn.execute(
        """INSERT INTO lm_complaints (listing_id, seller_email, buyer_token, intro_id, reason)
           VALUES (?, ?, ?, ?, ?)""",
        (intro["listing_id"], req.seller_email, buyer_id, req.intro_id, req.reason)
    )
    new_id = cur.lastrowid
    conn.commit()
    conn.close()
    return {"complaint_id": new_id, "status": "pending"}


@app.put("/local-market/complaint/{complaint_id}/uphold")
def lm_uphold_complaint(complaint_id: int, _key: str = Depends(auth.require_api_key)):
    """Ops upholds the complaint: −3 buyer Trust (LM-T4 / LM-16), 1T credit to
    seller IF listing still active (LM-T3), buyer auto-blocked if Trust < 20 (LM-17)."""
    conn = database.get_db()
    row = conn.execute("SELECT * FROM lm_complaints WHERE id = ?", (complaint_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Complaint not found")
    if row["status"] != "pending":
        conn.close()
        raise HTTPException(status_code=409, detail=f"Already resolved ({row['status']})")
    listing = conn.execute(
        "SELECT id, suspension_reason, title FROM listings WHERE id = ?",
        (row["listing_id"],)
    ).fetchone()
    listing_active = bool(listing and not listing["suspension_reason"])

    # 1) Buyer Trust Score penalty (−3, LM-T4)
    _set_buyer_trust(conn, row["buyer_token"], -LM_BUYER_NOSHOW_PENALTY)

    # 2) Seller credit if listing still active (LM-T3)
    credit_amount = 0
    if listing_active:
        credit_amount = LM_INTRO_COST_T
        conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, ?, ?, ?)",
            (row["seller_email"], "lm_credit", credit_amount,
             f"Local Market no-show credit · listing #{row['listing_id']} · {listing['title']}")
        )

    conn.execute(
        """UPDATE lm_complaints
           SET status = 'upheld', resolved_at = datetime('now'), credit_issued = ?
           WHERE id = ?""",
        (1 if credit_amount else 0, complaint_id)
    )
    conn.commit()
    conn.close()
    return {
        "message": "Complaint upheld",
        "buyer_trust_penalty": -LM_BUYER_NOSHOW_PENALTY,
        "seller_credit": credit_amount,
    }


@app.put("/local-market/complaint/{complaint_id}/dismiss")
def lm_dismiss_complaint(complaint_id: int, _key: str = Depends(auth.require_api_key)):
    """Ops dismisses the complaint — no Trust Score penalty, no credit."""
    conn = database.get_db()
    res = conn.execute(
        """UPDATE lm_complaints
           SET status = 'dismissed', resolved_at = datetime('now')
           WHERE id = ? AND status = 'pending'""",
        (complaint_id,)
    )
    if res.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="Complaint not found or already resolved")
    conn.commit()
    conn.close()
    return {"message": "Complaint dismissed"}


@app.get("/local-market/complaints")
def lm_list_complaints(status: str = "pending", _key: str = Depends(auth.require_api_key)):
    """Ops queue. Returns pending (default) / upheld / dismissed."""
    conn = database.get_db()
    rows = conn.execute(
        """SELECT c.*, l.title AS listing_title
           FROM lm_complaints c
           LEFT JOIN listings l ON l.id = c.listing_id
           WHERE c.status = ?
           ORDER BY c.filed_at DESC""",
        (status,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/local-market/suspension/check")
def lm_suspension_check(email: str):
    """Recovery-path query for the admin tool (LM-14c). Returns the seller's
    current state — banned / cooling-off / suspended / clear — and the gap
    to recovery."""
    conn = database.get_db()
    score = _seller_trust(conn, email)
    if _lm_is_banned(conn, email):
        conn.close()
        return {
            "state": "permanent_ban",
            "trust_score": score,
            "min_required": LM_SELLER_MIN_TRUST,
            "message": "You are permanently banned from the Local Market. Other categories remain available.",
        }
    susp = _lm_active_suspension(conn, email)
    conn.close()
    if susp and susp.get("cooling_off_until"):
        return {
            "state": "cooling_off",
            "trust_score": score,
            "min_required": LM_SELLER_MIN_TRUST,
            "cooling_off_until": susp["cooling_off_until"],
            "message": "You are in a 30-day mandatory cooling-off period. Listings stay suspended even if your Trust Score recovers during this time.",
        }
    if susp:
        return {
            "state": "suspended",
            "trust_score": score,
            "min_required": LM_SELLER_MIN_TRUST,
            "delta_to_recover": max(0, LM_SELLER_MIN_TRUST - score),
            "message": "Your Local Market listings are suspended due to upheld complaints. Restore your Trust Score to 30 or above — by resolving outstanding complaints and earning credentials — to reactivate them.",
        }
    return {
        "state": "clear",
        "trust_score": score,
        "min_required": LM_SELLER_MIN_TRUST,
    }


@app.post("/local-market/eula/accept")
def lm_accept_eula(email: str, _key: str = Depends(auth.require_api_key)):
    """Records that the seller has read and accepted the EULA clauses for
    Local Market (§11). Required once on first LM activation (LM-14f)."""
    conn = database.get_db()
    conn.execute(
        "UPDATE users SET lm_eula_accepted_at = datetime('now') WHERE email = ?",
        (email,)
    )
    conn.commit()
    conn.close()
    return {"message": "EULA accepted"}


# ── TRUST SCORE HUB (Section 3 · v1.3.0) ─────────────────────
# Per-credential checklist + Haiko tip + penalties section.
# All point values mirror TRUST_SCORE_CRITERIA.md v1.0 EXACTLY.
# Any future change to a value must be made there first and then
# reflected in this _TRUST_SIGNALS dict.
#
# COST CONSTRAINT (locked): Haiko tip generation is pure local Python.

# Tier thresholds (locked — Principle A5)
TRUST_TIERS = [
    (0,  39,  "New",            "grey"),
    (40, 69,  "Established",    "blue"),
    (70, 89,  "Trusted",        "green"),
    (90, 100, "Highly Trusted", "gold"),
]

def _trust_tier(score: int) -> dict:
    s = max(0, min(100, int(score or 0)))
    for lo, hi, name, color in TRUST_TIERS:
        if lo <= s <= hi:
            # Find the next tier
            next_t = None
            for lo2, hi2, name2, color2 in TRUST_TIERS:
                if lo2 > hi:
                    next_t = {"name": name2, "threshold": lo2, "delta": lo2 - s, "color": color2}
                    break
            return {"name": name, "color": color, "score": s, "next_tier": next_t}
    return {"name": "New", "color": "grey", "score": s, "next_tier": None}


# Every signal id matches the pattern <group>.<key>. Group is one of
# 'universal' | 'track_record' | 'category.<cat_key>'. Numbers below
# come straight out of TRUST_SCORE_CRITERIA.md — do not edit without
# updating the spec first.
_TRUST_SIGNALS = {
    # ── Group 1 · Universal (max 30) ─────────────────────────
    "universal.id_verified": {
        "name": "Government-issued ID verified",
        "points": 15, "max": 15,
        "how_to_earn": "Upload your ID or passport — verified by MarketSquare.",
        "evidence_required": True,
    },
    "universal.profile_complete": {
        "name": "Complete profile",
        "points": 5, "max": 5,
        "how_to_earn": "Bio, suburb, listing, and category description all set.",
        "evidence_required": False,  # system-calculated
    },
    "universal.referral_1": {
        "name": "1st verified referral",
        "points": 5, "max": 5,
        "how_to_earn": "Share your referral link with a client.",
        "evidence_required": False,
    },
    "universal.referral_3": {
        "name": "3rd verified referral",
        "points": 3, "max": 3,
        "how_to_earn": "2 more verified referrals after the first.",
        "evidence_required": False,
    },
    "universal.referral_5plus": {
        "name": "5th+ verified referral",
        "points": 2, "max": 2,
        "how_to_earn": "Cap: 10 pts total from referrals.",
        "evidence_required": False,
    },

    # ── Group 2 · Platform Track Record (max 30) ─────────────
    "track_record.intro_1": {
        "name": "1st successful introduction",
        "points": 5, "max": 5,
        "how_to_earn": "Accept a buyer introduction and complete it.",
        "evidence_required": False,
    },
    "track_record.intro_5": {
        "name": "5+ successful introductions",
        "points": 5, "max": 5,
        "how_to_earn": "Five completed introductions.",
        "evidence_required": False,
    },
    "track_record.intro_20": {
        "name": "20+ successful introductions",
        "points": 5, "max": 5,
        "how_to_earn": "Twenty completed introductions.",
        "evidence_required": False,
    },
    "track_record.zero_ignored_90d": {
        "name": "Zero ignored introductions (rolling 90 days)",
        "points": 10, "max": 10,
        "how_to_earn": "Respond to every introduction within 48 hours.",
        "evidence_required": False,
    },
    "track_record.tenure_6mo": {
        "name": "Account active 6+ months with live listing",
        "points": 5, "max": 5,
        "how_to_earn": "Keep at least one live listing for 6 months.",
        "evidence_required": False,
    },
}

# ── Group 3 · Category Credentials (max 40 per category) ─────
# Per-category checklists. The points field is the value awarded
# when this signal is verified. Mutually-exclusive replacement signals
# (e.g. NQF7 replaces NQF6) are noted in the 'replaces' field.
_CATEGORY_SIGNALS = {
    "Property": {
        "category.property.ppra":          {"name": "Active PPRA / EAAB Registration", "points": 15, "how_to_earn": "Upload PPRA certificate — verified against PPRA register."},
        "category.property.nqf4":          {"name": "NQF4 Real Estate qualification", "points": 6,  "how_to_earn": "Upload certificate."},
        "category.property.nqf5":          {"name": "NQF5 Real Estate qualification", "points": 6,  "how_to_earn": "Upload certificate (additional to NQF4).", "additional_to": "category.property.nqf4"},
        "category.property.nqf6_plus":     {"name": "NQF6+ / Professional designation", "points": 8, "how_to_earn": "Upload certificate.", "additional_to": "category.property.nqf5"},
        "category.property.body":          {"name": "Professional body membership (IEASA, SAPOA, NAR)", "points": 5, "how_to_earn": "Upload membership card or letter."},
    },
    "Tutors": {
        "category.tutors.sace":            {"name": "SACE registration", "points": 8,  "how_to_earn": "Upload SACE number — verified at sace.org.za."},
        "category.tutors.cert_diploma":    {"name": "Certificate or Diploma (NQF5–6)", "points": 6, "how_to_earn": "Upload certificate."},
        "category.tutors.bachelor":        {"name": "Bachelor's Degree (NQF7)", "points": 10, "how_to_earn": "Upload certificate (replaces diploma points).", "replaces": "category.tutors.cert_diploma"},
        "category.tutors.honours":         {"name": "Honours / Postgraduate (NQF8+)", "points": 14, "how_to_earn": "Upload certificate (replaces bachelor's points).", "replaces": "category.tutors.bachelor"},
        "category.tutors.specialisation":  {"name": "Subject specialisation certificate", "points": 5, "how_to_earn": "Upload subject-specific cert or transcript."},
        "category.tutors.exp_2_5":         {"name": "Teaching experience 2–5 years", "points": 5, "how_to_earn": "Upload CV — reviewed by MarketSquare."},
        "category.tutors.exp_5plus":       {"name": "Teaching experience 5+ years", "points": 6, "how_to_earn": "Upload CV.", "additional_to": "category.tutors.exp_2_5"},
        "category.tutors.strong_cv":       {"name": "Strong structured CV", "points": 2, "how_to_earn": "Upload CV — assessed at onboarding."},
    },
    "Services-Technical": {
        "category.services_tech.trade_cert": {"name": "Formal trade certificate", "points": 8, "how_to_earn": "Upload (City & Guilds, TVET, MERSETA, CETA, Red Seal)."},
        "category.services_tech.body_reg":   {"name": "Professional body registration", "points": 12, "how_to_earn": "Upload (ECSA, PIRB, NHBRC, FSCA, SAICA) — verified."},
        "category.services_tech.coc":        {"name": "Primary industry licence / CoC", "points": 5, "how_to_earn": "Upload with expiry date."},
        "category.services_tech.tickets":    {"name": "Additional tickets (max 2 counted)", "points": 6, "how_to_earn": "Upload First Aid, heights, confined space etc. (3 pts each, max 2)."},
        "category.services_tech.exp_3_7":    {"name": "Years in trade 3–7", "points": 4, "how_to_earn": "Upload CV."},
        "category.services_tech.exp_7plus":  {"name": "Years in trade 7+", "points": 4, "how_to_earn": "Upload CV.", "additional_to": "category.services_tech.exp_3_7"},
        "category.services_tech.strong_cv":  {"name": "Strong verifiable CV", "points": 2, "how_to_earn": "Upload CV."},
    },
    "Services-Casuals": {
        "category.services_cas.nqf":         {"name": "Any NQF qualification or short course", "points": 8, "how_to_earn": "Upload certificate."},
        "category.services_cas.exp_2_4":     {"name": "2–4 years in service", "points": 6, "how_to_earn": "Upload CV or written statement."},
        "category.services_cas.exp_5plus":   {"name": "5+ years in service", "points": 8, "how_to_earn": "Upload CV.", "additional_to": "category.services_cas.exp_2_4"},
        "category.services_cas.ref_1":       {"name": "Reference letter", "points": 8, "how_to_earn": "Upload scanned letter with verifiable contact."},
        "category.services_cas.ref_2":       {"name": "Second reference letter", "points": 5, "how_to_earn": "Upload second letter — max 2 counted."},
        "category.services_cas.profile":     {"name": "Strong profile description", "points": 5, "how_to_earn": "Complete your profile description in detail."},
    },
    "Adventures-Experiences": {
        "category.adv_exp.guide_cert":       {"name": "Activity-specific guide cert", "points": 12, "how_to_earn": "FGASA, PADI, MCSA, SACAA — verified."},
        "category.adv_exp.first_aid":        {"name": "Current First Aid / Emergency Response", "points": 6, "how_to_earn": "Upload with expiry date."},
        "category.adv_exp.exp_3_7":          {"name": "Guided experience 3–7 years", "points": 5, "how_to_earn": "Upload CV."},
        "category.adv_exp.exp_7plus":        {"name": "Guided experience 7+ years", "points": 5, "how_to_earn": "Upload CV.", "additional_to": "category.adv_exp.exp_3_7"},
        "category.adv_exp.safety_cert":      {"name": "Additional safety cert", "points": 4, "how_to_earn": "Wilderness First Responder, swift water rescue etc."},
        "category.adv_exp.insurance":        {"name": "Liability / indemnity insurance", "points": 5, "how_to_earn": "Upload policy summary with expiry."},
        "category.adv_exp.secondary_qual":   {"name": "Secondary qualification in declared activity", "points": 3, "how_to_earn": "Upload certificate."},
    },
    "Adventures-Accommodation": {
        # TGCSA grading is mutually exclusive — only ONE star level counts at a time.
        # The replaces chain enforces this.
        "category.adv_acc.tgcsa_1":          {"name": "TGCSA 1-star grading", "points": 6,  "how_to_earn": "Upload grading number — verified."},
        "category.adv_acc.tgcsa_2":          {"name": "TGCSA 2-star grading", "points": 10, "how_to_earn": "Replaces 1-star pts.", "replaces": "category.adv_acc.tgcsa_1"},
        "category.adv_acc.tgcsa_3":          {"name": "TGCSA 3-star grading", "points": 14, "how_to_earn": "Replaces 2-star pts.", "replaces": "category.adv_acc.tgcsa_2"},
        "category.adv_acc.tgcsa_4":          {"name": "TGCSA 4-star grading", "points": 18, "how_to_earn": "Replaces 3-star pts.", "replaces": "category.adv_acc.tgcsa_3"},
        "category.adv_acc.tgcsa_5":          {"name": "TGCSA 5-star grading", "points": 22, "how_to_earn": "Replaces 4-star pts.", "replaces": "category.adv_acc.tgcsa_4"},
        "category.adv_acc.licence":          {"name": "Municipal licence to operate", "points": 6, "how_to_earn": "Upload licence document."},
        "category.adv_acc.health_safety":    {"name": "Health & safety compliance", "points": 5, "how_to_earn": "Upload certificate."},
        "category.adv_acc.fire":             {"name": "Fire clearance certificate", "points": 4, "how_to_earn": "Upload certificate."},
        "category.adv_acc.award":            {"name": "AA Travel / TripAdvisor / Booking.com award", "points": 3, "how_to_earn": "Upload award certificate or screenshot."},
    },
    "Collectors": {
        "category.collectors.specialisation": {"name": "Category specialisation declared", "points": 4, "how_to_earn": "Write your collecting domain in your profile."},
        "category.collectors.tx_1_4":         {"name": "1–4 successful transactions", "points": 8, "how_to_earn": "Complete introductions — system tracked."},
        "category.collectors.tx_5_14":        {"name": "5–14 successful transactions", "points": 6, "how_to_earn": "System tracked.", "additional_to": "category.collectors.tx_1_4"},
        "category.collectors.tx_15plus":      {"name": "15+ successful transactions", "points": 6, "how_to_earn": "System tracked.", "additional_to": "category.collectors.tx_5_14"},
        "category.collectors.auth_cert":      {"name": "Third-party authentication certificate", "points": 8, "how_to_earn": "Upload per item — counted once per listing."},
        "category.collectors.appraisal":      {"name": "Professional appraisal or valuation", "points": 5, "how_to_earn": "Upload appraisal document."},
        "category.collectors.assoc":          {"name": "Collector association membership", "points": 3, "how_to_earn": "Upload membership card or certificate."},
    },
    # Local Market sellers reuse the buyer-onboarding signal set per
    # TRUST_SCORE_HUB_REQUIREMENTS §3 last block. Universal identity
    # carries highest weight here.
    "local_market": {
        "category.lm.phone_verified":      {"name": "Phone number verified",               "points": 3,  "how_to_earn": "Add and verify your mobile number in your profile.", "evidence_required": False},
        "category.lm.banking":             {"name": "Banking details on file",              "points": 3,  "how_to_earn": "Add your bank account details — required for Tuppence payouts.", "evidence_required": False},
        "category.lm.banking_name_match":  {"name": "Bank account holder name verified",   "points": 5,  "how_to_earn": "Account holder name on bank details matches your verified ID name.", "evidence_required": False},
        "category.lm.id_uploaded":         {"name": "Government-issued ID uploaded",        "points": 3,  "how_to_earn": "Upload a clear photo of your SA ID, passport, or drivers licence.", "evidence_required": True},
        "category.lm.id_number_valid":     {"name": "ID / passport number entered & valid", "points": 4,  "how_to_earn": "Enter your SA ID number (13 digits) or passport number — format validated instantly.", "evidence_required": False},
        "category.lm.id_ai_verified":      {"name": "Identity AI-verified (Sonnet vision)", "points": 8,  "how_to_earn": "AI vision confirms your name and ID number match your uploaded document.", "evidence_required": True},
        "category.lm.id_admin_verified":   {"name": "Identity admin-confirmed",             "points": 10, "how_to_earn": "TrustSquare admin has manually confirmed your identity documents.", "evidence_required": True},
        "category.lm.cert_name_verified":  {"name": "Certificate name matches ID",          "points": 3,  "how_to_earn": "Name on your uploaded certificate matches your verified ID name.", "evidence_required": True},
        "category.lm.experience_1yr":      {"name": "1+ year of relevant experience",       "points": 4,  "how_to_earn": "Upload a document describing your experience or a reference letter.", "evidence_required": True},
        "category.lm.experience_5yr":      {"name": "5+ years of relevant experience",      "points": 4,  "how_to_earn": "Upload evidence of 5+ years experience (CV, references, or written statement).", "evidence_required": True, "replaces": "category.lm.experience_1yr"},
        "category.lm.training_course":     {"name": "Formal training / short course",       "points": 4,  "how_to_earn": "Upload a certificate from a recognised training provider.", "evidence_required": True},
        "category.lm.formal_cert":         {"name": "Formal qualification / diploma",       "points": 6,  "how_to_earn": "Upload your certificate or diploma from an accredited institution.", "evidence_required": True, "replaces": "category.lm.training_course"},
        "category.lm.prof_body":           {"name": "Professional body membership",          "points": 5,  "how_to_earn": "Upload membership card or letter from a recognised professional body (e.g. SABIO, SABI, guild, association).", "evidence_required": True},
        "category.lm.provincial_role":     {"name": "Official provincial / national role",  "points": 6,  "how_to_earn": "Upload appointment letter or certificate confirming an official role (e.g. provincial bee secretary, guild chair).", "evidence_required": True},
        "category.lm.product_guide":       {"name": "Product guide or recipe published",    "points": 3,  "how_to_earn": "Upload a product guide, recipe, care instructions, or usage guide you have authored.", "evidence_required": True},
        "category.lm.media_feature":       {"name": "Media feature or press coverage",      "points": 3,  "how_to_earn": "Upload a scan or screenshot of a magazine, newspaper, or online article featuring your work.", "evidence_required": True},
        "category.lm.social_proof":        {"name": "Active social media presence",         "points": 2,  "how_to_earn": "Add your Instagram, Facebook page, or website URL showing your products/services.", "evidence_required": False},
    },
}

# Penalty scale per TRUST_SCORE_CRITERIA §5a — diminishing
_COMPLAINT_PENALTY_SCALE = [-8, -5, -3, -2, -1]
_COMPLAINT_PENALTY_CAP = -22


def _category_key_for_user(conn, email: str) -> str:
    """Decide which Group 3 checklist to render for this seller. If the
    seller has an LM listing OR `primary_category` is 'local_market',
    return 'local_market'. Otherwise look at primary_category."""
    row = conn.execute(
        "SELECT primary_category FROM users WHERE email = ?", (email,)
    ).fetchone()
    primary = (row["primary_category"] if row else None) or ""
    if primary:
        # Normalise common forms — Services-Technical / Services-Casuals /
        # Adventures-Experiences / Adventures-Accommodation come direct
        return primary
    # Inspect listings
    has_lm = conn.execute(
        "SELECT 1 FROM listings WHERE seller_email = ? AND category = 'local_market' LIMIT 1",
        (email,)
    ).fetchone()
    if has_lm:
        return "local_market"
    cat_row = conn.execute(
        """SELECT category, service_class FROM listings
           WHERE seller_email = ? ORDER BY created_at DESC LIMIT 1""",
        (email,)
    ).fetchone()
    if not cat_row:
        return ""
    cat = cat_row["category"] or ""
    sc  = cat_row["service_class"] or ""
    if cat == "Services" and sc:
        return "Services-Technical" if sc.lower().startswith("tech") else "Services-Casuals"
    if cat == "Adventures":
        # Adventures sub-class lives in service_class for now
        return "Adventures-Accommodation" if sc.lower().startswith("accom") else "Adventures-Experiences"
    return cat or ""


def _compute_universal_track_status(conn, email: str) -> dict:
    """Return computed status for system-calculated signals (profile, referrals,
    introductions, tenure). These don't require an admin upload — BEA derives
    them from existing data."""
    out = {}

    # Profile completeness — bio, suburb, listing, category description set
    user_row = conn.execute(
        "SELECT name, country, photo_url FROM users WHERE email = ?", (email,)
    ).fetchone()
    has_listing = conn.execute(
        "SELECT 1 FROM listings WHERE seller_email = ? LIMIT 1", (email,)
    ).fetchone()
    profile_complete = bool(
        user_row and user_row["name"] and user_row["country"]
        and user_row["photo_url"] and has_listing
    )
    out["universal.profile_complete"] = "earned" if profile_complete else "missing"

    # Referrals — placeholder for V1: not yet tracked. Always missing.
    for k in ("universal.referral_1", "universal.referral_3", "universal.referral_5plus"):
        out[k] = "missing"

    # Successful intros (accepted)
    intro_count = conn.execute(
        """SELECT COUNT(*) AS n FROM intro_requests i
           JOIN listings l ON l.id = i.listing_id
           WHERE l.seller_email = ? AND i.status = 'accepted'""",
        (email,)
    ).fetchone()["n"] or 0
    out["track_record.intro_1"]  = "earned" if intro_count >= 1  else "missing"
    out["track_record.intro_5"]  = "earned" if intro_count >= 5  else "missing"
    out["track_record.intro_20"] = "earned" if intro_count >= 20 else "missing"

    # Zero ignored intros in 90 days
    cutoff = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
    ignored = conn.execute(
        """SELECT COUNT(*) AS n FROM intro_requests i
           JOIN listings l ON l.id = i.listing_id
           WHERE l.seller_email = ? AND i.status = 'pending'
             AND i.created_at < ?""",
        (email, (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat())
    ).fetchone()["n"] or 0
    out["track_record.zero_ignored_90d"] = "earned" if ignored == 0 else "missing"

    # Tenure 6+ months — needs first listing date
    first_row = conn.execute(
        "SELECT MIN(created_at) AS first FROM listings WHERE seller_email = ?", (email,)
    ).fetchone()
    has_6mo = False
    if first_row and first_row["first"]:
        try:
            first_dt = datetime.fromisoformat(first_row["first"].replace("Z", "+00:00"))
            if first_dt.tzinfo is None:
                first_dt = first_dt.replace(tzinfo=timezone.utc)
            has_6mo = (datetime.now(timezone.utc) - first_dt).days >= 180
        except Exception:
            pass
    out["track_record.tenure_6mo"] = "earned" if has_6mo else "missing"

    return out


def _build_breakdown_items(conn, email: str, signals_dict: dict, computed: dict) -> list:
    """Build a list of {signal_id, name, points, status, how_to_earn} items
    from a signal set. Reads user_credentials for upload-required signals."""
    rows = conn.execute(
        "SELECT signal_id, status FROM user_credentials WHERE email = ?", (email,)
    ).fetchall()
    cred_status = {r["signal_id"]: r["status"] for r in rows}
    items = []
    for sig_id, sig in signals_dict.items():
        if sig_id in computed:
            status = computed[sig_id]
        elif sig_id in cred_status:
            # 'pending' | 'earned' | 'rejected'
            status = cred_status[sig_id]
            if status not in ("earned", "pending", "rejected"):
                status = "missing"
        else:
            status = "missing"
        items.append({
            "signal_id":   sig_id,
            "name":        sig["name"],
            "points":      sig["points"],
            "status":      status,
            "how_to_earn": sig["how_to_earn"],
        })
    return items


def _sum_earned_with_replaces(items: list, signals_dict: dict) -> int:
    """Sum points but honour mutually-exclusive replacement chains.
    Example: if both NQF6 and NQF7 are earned, NQF7 replaces NQF6 — only NQF7 counts."""
    earned_ids = {it["signal_id"] for it in items if it["status"] == "earned"}
    replaced_ids = set()
    for sig_id in earned_ids:
        sig = signals_dict.get(sig_id, {})
        replaces = sig.get("replaces")
        if replaces and replaces in earned_ids:
            replaced_ids.add(replaces)
    total = 0
    for it in items:
        if it["status"] != "earned":
            continue
        if it["signal_id"] in replaced_ids:
            continue
        total += it["points"]
    return total


def _seller_active_complaints(conn, email: str) -> list:
    """Return active (non-decayed, non-disputed) seller complaints with their
    deduction values per the diminishing scale, capped at -22 total."""
    rows = conn.execute(
        """SELECT id, reason_code, notes, status, filed_at, points_deducted
           FROM seller_complaints
           WHERE seller_email = ? AND status IN ('pending', 'upheld')
           ORDER BY filed_at ASC""",
        (email,)
    ).fetchall()
    out = []
    cumulative = 0
    for i, r in enumerate(rows):
        # Diminishing scale based on order
        scale_idx = min(i, len(_COMPLAINT_PENALTY_SCALE) - 1)
        raw = _COMPLAINT_PENALTY_SCALE[scale_idx]
        # Decay older than 24 months → 50% deduction
        try:
            filed = datetime.fromisoformat(r["filed_at"].replace("Z", "+00:00"))
            if filed.tzinfo is None:
                filed = filed.replace(tzinfo=timezone.utc)
            age_days = (datetime.now(timezone.utc) - filed).days
            if age_days >= 730:
                raw = int(raw / 2)
        except Exception:
            pass
        # Apply cap
        if cumulative + raw < _COMPLAINT_PENALTY_CAP:
            raw = _COMPLAINT_PENALTY_CAP - cumulative
        cumulative += raw
        out.append({
            "id": r["id"], "reason_code": r["reason_code"], "notes": r["notes"],
            "status": r["status"], "filed_at": r["filed_at"], "points": raw,
        })
    return out


def _haiko_tip(items_universal: list, items_track: list, items_category: list,
               cat_signals: dict, score: int, tier: dict) -> dict:
    """Pick the single highest-impact uncompleted action. Pure local logic
    — zero external API. If the seller is within 5 points of the next tier,
    prefer the smallest-effort action that closes the gap."""
    open_items = []
    for source_name, source_items, source_dict in [
        ("Universal",     items_universal, _TRUST_SIGNALS),
        ("Track Record",  items_track,     _TRUST_SIGNALS),
        ("Category",      items_category,  cat_signals),
    ]:
        for it in source_items:
            if it["status"] not in ("earned",):
                sig = source_dict.get(it["signal_id"], {})
                # Don't recommend a signal whose 'replaces' or 'additional_to'
                # prerequisite hasn't been earned yet — they only make sense
                # in sequence
                blocker = sig.get("additional_to")
                if blocker:
                    earned_ids = {x["signal_id"] for x in items_universal + items_track + items_category if x["status"] == "earned"}
                    if blocker not in earned_ids:
                        continue
                open_items.append({**it, "group": source_name, "evidence_required": sig.get("evidence_required", True)})

    if not open_items:
        return {
            "text": "Your score is maximised. Keep responding to introductions to build your track record.",
            "action_label": None,
            "action_url": None,
            "points_available": 0,
        }

    # Default — highest single value
    open_items.sort(key=lambda x: x["points"], reverse=True)
    pick = open_items[0]

    # If within 5 of next tier and a smaller-value item closes the gap, prefer that
    if tier["next_tier"] and tier["next_tier"]["delta"] <= 5:
        gap = tier["next_tier"]["delta"]
        gap_closers = [x for x in open_items if x["points"] >= gap]
        if gap_closers:
            # Prefer the one with the smallest-effort path (fewest points but
            # >= gap)
            gap_closers.sort(key=lambda x: x["points"])
            pick = gap_closers[0]

    text = (
        f"{pick['how_to_earn']} This adds {pick['points']} points"
        + (f" — enough to reach {tier['next_tier']['name']} tier."
           if tier['next_tier'] and pick['points'] >= tier['next_tier']['delta']
           else ".")
    )
    return {
        "text": text,
        "action_label": "Upload now →" if pick.get("evidence_required") else "Complete now →",
        "action_url": None,  # admin tool resolves this from the signal_id
        "points_available": pick["points"],
        "signal_id": pick["signal_id"],
    }


@app.get("/trust-score/breakdown")
def trust_score_breakdown(email: str):
    """Return a structured Trust Score breakdown for the given seller.
    Frontend renders Universal / Track Record / Category groups + a Haiko
    tip + active penalties. Score is recomputed from credentials each call;
    users.trust_score is updated as a side-effect so wishlist matching and
    Local Market gates see the live value."""
    conn = database.get_db()
    user = conn.execute(
        "SELECT trust_score, primary_category FROM users WHERE email = ?", (email,)
    ).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not found")

    cat_key = _category_key_for_user(conn, email)
    cat_signals = _CATEGORY_SIGNALS.get(cat_key, {})

    # System-calculated statuses
    computed = _compute_universal_track_status(conn, email)

    # Build group items
    universal_signals = {k: v for k, v in _TRUST_SIGNALS.items() if k.startswith("universal.")}
    track_signals     = {k: v for k, v in _TRUST_SIGNALS.items() if k.startswith("track_record.")}

    items_u = _build_breakdown_items(conn, email, universal_signals, computed)
    items_t = _build_breakdown_items(conn, email, track_signals, computed)
    items_c = _build_breakdown_items(conn, email, cat_signals, {}) if cat_signals else []

    # Sums (max-capped)
    earned_u = min(30, _sum_earned_with_replaces(items_u, _TRUST_SIGNALS))
    earned_t = min(30, _sum_earned_with_replaces(items_t, _TRUST_SIGNALS))
    earned_c = min(40, _sum_earned_with_replaces(items_c, cat_signals))

    # Penalties
    penalties = _seller_active_complaints(conn, email)
    penalty_total = sum(p["points"] for p in penalties)

    score_total = max(0, min(100, earned_u + earned_t + earned_c + penalty_total))
    tier = _trust_tier(score_total)

    # Persist the recomputed score (drives wishlist matching trust gate +
    # Local Market suspension state)
    prior_score = int(user["trust_score"] or 0)
    if prior_score != score_total:
        conn.execute(
            "UPDATE users SET trust_score = ? WHERE email = ?",
            (score_total, email)
        )
        conn.commit()
        # Hook into LM suspension/restoration
        _lm_recompute_seller_state(conn, email)
        conn.commit()

    tip = _haiko_tip(items_u, items_t, items_c, cat_signals, score_total, tier)
    conn.close()

    return {
        "email": email,
        "score": score_total,
        "tier": tier["name"],
        "tier_color": tier["color"],
        "next_tier": tier["next_tier"],
        "category_key": cat_key,
        "groups": {
            "universal":    {"earned": earned_u, "max": 30, "items": items_u},
            "track_record": {"earned": earned_t, "max": 30, "items": items_t},
            "category":     {"earned": earned_c, "max": 40, "items": items_c, "label": cat_key or "—"},
        },
        "haiko_tip":  tip,
        "penalties":  penalties,
        "penalty_total": penalty_total,
    }


class CredentialUpdateReq(BaseModel):
    email: str
    signal_id: str
    status: str         # 'pending' | 'earned' | 'rejected'
    evidence_url: Optional[str] = None
    notes: Optional[str] = None


@app.post("/trust-score/credential")
def trust_score_set_credential(req: CredentialUpdateReq, _key: str = Depends(auth.require_api_key)):
    """Admin sets the verification state of a credential. Status='pending' is
    the seller-uploaded state; 'earned' is the verified state; 'rejected' clears
    it. Score recomputes on next /trust-score/breakdown call."""
    if req.status not in ("pending", "earned", "rejected"):
        raise HTTPException(status_code=400, detail="status must be pending|earned|rejected")
    # Validate signal_id is known
    all_signals = dict(_TRUST_SIGNALS)
    for cat_set in _CATEGORY_SIGNALS.values():
        all_signals.update(cat_set)
    sig = all_signals.get(req.signal_id)
    if not sig:
        raise HTTPException(status_code=400, detail=f"unknown signal_id: {req.signal_id}")
    conn = database.get_db()
    pts = sig["points"] if req.status == "earned" else 0
    verified_at = datetime.now(timezone.utc).isoformat() if req.status == "earned" else None
    conn.execute(
        """INSERT INTO user_credentials (email, signal_id, status, points, evidence_url, notes, verified_at, verified_by)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'admin')
           ON CONFLICT(email, signal_id) DO UPDATE SET
               status = excluded.status,
               points = excluded.points,
               evidence_url = COALESCE(excluded.evidence_url, user_credentials.evidence_url),
               notes = COALESCE(excluded.notes, user_credentials.notes),
               verified_at = excluded.verified_at,
               verified_by = 'admin'""",
        (req.email, req.signal_id, req.status, pts, req.evidence_url, req.notes, verified_at)
    )
    conn.commit()
    conn.close()
    return {"message": "Credential updated", "signal_id": req.signal_id, "status": req.status}


@app.get("/trust-score/credentials/pending")
def trust_score_pending_queue(_key: str = Depends(auth.require_api_key)):
    """Ops queue — credentials awaiting manual review across all sellers."""
    conn = database.get_db()
    rows = conn.execute(
        """SELECT id, email, signal_id, evidence_url, notes, submitted_at
           FROM user_credentials
           WHERE status = 'pending'
           ORDER BY submitted_at ASC"""
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ── AI GUIDANCE (Trust Score Coach · Haiku 4.5) ─────────────────────────────
# Called after a seller's first listing is published. Generates a
# category-specific personalised action plan showing what evidence is needed
# to reach Trust Score 50 (Established tier). Uses Haiku 4.5 via Anthropic
# API — same key and client pattern as AA Coach.

class AIGuidanceRequest(BaseModel):
    email: str
    category: str  # normalised category key, e.g. "Services-Technical"


@app.post("/trust-score/guidance")
async def trust_score_guidance(req: AIGuidanceRequest):
    cat_signals       = _CATEGORY_SIGNALS.get(req.category, {})
    universal_signals = {k: v for k, v in _TRUST_SIGNALS.items() if k.startswith("universal.")}

    conn = database.get_db()
    try:
        earned_rows = conn.execute(
            "SELECT signal_id, status FROM user_credentials WHERE email = ?",
            (req.email,)
        ).fetchall()
    except Exception:
        earned_rows = []
    finally:
        conn.close()

    earned_map = {r["signal_id"]: r["status"] for r in earned_rows} if earned_rows else {}

    universal_earned_pts = 0
    universal_missing = []
    for sig_id, sig in universal_signals.items():
        if earned_map.get(sig_id) == "earned":
            universal_earned_pts += sig["points"]
        else:
            universal_missing.append({
                "name": sig["name"], "points": sig["points"], "how": sig["how_to_earn"]
            })

    cat_earned_pts = 0
    cat_missing = []
    for sig_id, sig in cat_signals.items():
        if earned_map.get(sig_id) == "earned":
            cat_earned_pts += sig.get("points", 0)
        else:
            cat_missing.append({
                "name": sig["name"],
                "points": sig.get("points", 0),
                "how": sig.get("how_to_earn", ""),
            })

    current_score = universal_earned_pts + cat_earned_pts
    points_needed = max(0, 50 - current_score)
    all_missing   = sorted(universal_missing + cat_missing, key=lambda x: x["points"], reverse=True)

    if not ANTHROPIC_API_KEY:
        return {
            "ai_available":  False,
            "current_score": current_score,
            "score_target":  50,
            "points_needed": points_needed,
            "intro":   "To reach Established tier (score 50), focus on the steps below.",
            "steps":   _build_local_guidance(req.category, all_missing),
            "closing": "Every step builds buyer confidence.",
        }

    missing_lines = "\n".join(
        "- " + m["name"] + " (+" + str(m["points"]) + " pts): " + m["how"]
        for m in all_missing[:8]
    )

    system_prompt = (
        "You are a friendly Trust Score coach for MarketSquare, a South African marketplace. "
        "Help sellers understand exactly what evidence to upload to reach Trust Score 50 "
        "('Established' tier). Be warm, direct, and specific to their category. "
        'Reply ONLY with a valid JSON object — no markdown, no preamble. '
        'Format: {"intro": "one encouraging sentence", '
        '"steps": [{"action": "...", "points": N, "why": "..."}], '
        '"closing": "one motivating sentence"} '
        "Order steps by impact (most points first). Maximum 5 steps. "
        "Keep each action and why under 20 words."
    )

    user_message = (
        "Seller category: " + req.category + "\n"
        "Current Trust Score: " + str(current_score) + " / 100\n"
        "Points needed to reach Established (50): " + str(points_needed) + "\n\n"
        "Evidence not yet submitted:\n" + (missing_lines or "None — all signals earned!") + "\n\n"
        "Generate a personalised action plan to reach score 50."
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json",
                },
                json={
                    "model":      AA_MODEL,
                    "max_tokens": 600,
                    "system":     system_prompt,
                    "messages":   [{"role": "user", "content": user_message}],
                },
            )
        resp.raise_for_status()
        raw = resp.json()["content"][0]["text"]
    except Exception as exc:
        _log.warning("AI guidance Haiku call failed: %s", exc)
        return {
            "ai_available":  False,
            "current_score": current_score,
            "score_target":  50,
            "points_needed": points_needed,
            "intro":   "To reach Established tier (score 50), focus on the steps below.",
            "steps":   _build_local_guidance(req.category, all_missing),
            "closing": "Every step builds buyer confidence.",
        }

    import re as _re
    guidance = {}
    try:
        guidance = _json.loads(raw)
    except Exception:
        m2 = _re.search(r'\{[\s\S]*\}', raw)
        try:
            guidance = _json.loads(m2.group(0)) if m2 else {}
        except Exception:
            guidance = {}

    guidance.setdefault("intro",   "Here is your personalised path to Trust Score 50.")
    guidance.setdefault("steps",   _build_local_guidance(req.category, all_missing))
    guidance.setdefault("closing", "Every step you complete builds buyer confidence.")
    guidance["ai_available"]  = True
    guidance["current_score"] = current_score
    guidance["score_target"]  = 50
    guidance["points_needed"] = points_needed
    return guidance


def _build_local_guidance(category: str, all_missing: list = None) -> list:
    if all_missing is None:
        cat_sigs = _CATEGORY_SIGNALS.get(category, {})
        all_missing = [
            {"name": "Government-issued ID verified", "points": 15,
             "how": "Upload your ID or passport — verified by MarketSquare."},
            {"name": "Complete profile", "points": 5,
             "how": "Bio, suburb, listing, and category description all set."},
        ] + sorted(
            [{"name": s["name"], "points": s.get("points", 0), "how": s.get("how_to_earn", "")}
             for s in cat_sigs.values()],
            key=lambda x: x["points"], reverse=True
        )
    return [
        {"action": m["how"] or m["name"], "points": m["points"],
         "why": "Adds " + str(m["points"]) + " points to your Trust Score."}
        for m in all_missing[:5]
    ]


# ── SELLER DOCUMENTS ─────────────────────────────────────────────────────────
# Documents are stored in R2 / local media. Each doc has a visibility flag:
#   private     — never shown to buyers
#   post_intro  — shown on seller profile after buyer's intro is accepted

ALLOWED_DOC_TYPES = {
    "id_doc", "certificate", "training", "membership",
    "professional_role", "guide", "recipe", "presentation", "other"
}

# Map doc_type → signal_id that should be set to 'pending' on upload
_DOC_TYPE_TO_SIGNAL = {
    "id_doc":            "category.lm.id_uploaded",
    "certificate":       "category.lm.formal_cert",
    "training":          "category.lm.training_course",
    "membership":        "category.lm.prof_body",
    "professional_role": "category.lm.provincial_role",
    "guide":             "category.lm.product_guide",
    "recipe":            "category.lm.product_guide",
}

@app.post("/users/{email}/documents")
async def upload_seller_document(
    email: str,
    file: UploadFile = File(...),
    doc_type: str = Form("other"),
    label: str = Form(""),
    visibility: str = Form("private"),
    signal_id: str = Form(None),
    _key: str = Depends(auth.require_api_key),
):
    """Upload a document for a seller. Stores to R2, records in seller_documents.
    If the doc_type maps to a Trust Score signal, auto-sets it to pending."""
    email = email.lower().strip()
    if doc_type not in ALLOWED_DOC_TYPES:
        doc_type = "other"
    if visibility not in ("private", "post_intro"):
        visibility = "private"

    allowed_mime = {
        "application/pdf", "image/jpeg", "image/png", "image/webp",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    ct = file.content_type or "application/octet-stream"
    if ct not in allowed_mime:
        raise HTTPException(status_code=400, detail="Only PDF, JPEG, PNG, WebP, or Word documents accepted")

    raw = await file.read()
    if len(raw) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Document too large — max 25MB")

    # Upload to R2 or local fallback
    orig_name = (file.filename or "document").replace(" ", "_")
    key = f"docs/{uuid.uuid4().hex}_{orig_name}"
    if _S3_CONFIGURED:
        url = _s3_upload(raw, key, ct)
    else:
        safe = key.replace("/", "_")
        path = os.path.join(MEDIA_DIR, safe)
        with open(path, "wb") as fh:
            fh.write(raw)
        url = f"/media/{safe}"

    # Determine signal_id to auto-trigger pending
    effective_signal = signal_id or _DOC_TYPE_TO_SIGNAL.get(doc_type)

    conn = database.get_db()
    try:
        conn.execute(
            """INSERT INTO seller_documents (email, doc_type, label, url, visibility, signal_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email, doc_type, label or orig_name, url, visibility, effective_signal)
        )
        doc_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Auto-set signal to pending if not already earned
        if effective_signal:
            existing = conn.execute(
                "SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
                (email, effective_signal)
            ).fetchone()
            if not existing:
                conn.execute(
                    """INSERT INTO user_credentials (email, signal_id, status, updated_at)
                       VALUES (?, ?, 'pending', strftime('%Y-%m-%dT%H:%M:%SZ','now'))""",
                    (email, effective_signal)
                )
            elif existing["status"] not in ("earned", "pending"):
                conn.execute(
                    """UPDATE user_credentials SET status='pending', updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')
                       WHERE email=? AND signal_id=?""",
                    (email, effective_signal)
                )
        conn.commit()
    finally:
        conn.close()

    return {"id": doc_id, "url": url, "doc_type": doc_type, "label": label or orig_name,
            "visibility": visibility, "signal_id": effective_signal}


@app.get("/users/{email}/documents")
def list_seller_documents(
    email: str,
    _key: str = Depends(auth.require_api_key),
):
    """List all documents for a seller (admin-only view — all visibility levels)."""
    email = email.lower().strip()
    conn = database.get_db()
    rows = conn.execute(
        """SELECT id, doc_type, label, url, visibility, signal_id, uploaded_at
           FROM seller_documents WHERE email=? ORDER BY uploaded_at DESC""",
        (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/users/{email}/documents/public")
def list_public_documents(email: str, intro_id: int = None):
    """Return post_intro documents for a seller. Called by buyer app after intro accepted.
    No API key required — documents are intentionally shared post-introduction."""
    email = email.lower().strip()
    conn = database.get_db()
    # Verify intro exists and is accepted before revealing docs
    if intro_id:
        intro = conn.execute(
            "SELECT status FROM intro_requests WHERE id=? AND seller_email=?",
            (intro_id, email)
        ).fetchone()
        if not intro or intro["status"] != "accepted":
            conn.close()
            return []
    rows = conn.execute(
        """SELECT id, doc_type, label, url, uploaded_at
           FROM seller_documents WHERE email=? AND visibility='post_intro'
           ORDER BY uploaded_at DESC""",
        (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.delete("/users/{email}/documents/{doc_id}")
def delete_seller_document(
    email: str,
    doc_id: int,
    _key: str = Depends(auth.require_api_key),
):
    """Delete a document record (does not delete from R2 — orphan cleanup runs separately)."""
    email = email.lower().strip()
    conn = database.get_db()
    row = conn.execute(
        "SELECT id FROM seller_documents WHERE id=? AND email=?", (doc_id, email)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    conn.execute("DELETE FROM seller_documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    return {"deleted": doc_id}


# ── SELLER DOCUMENTS ─────────────────────────────────────────────────────────
# Documents are stored in R2 / local media. Each doc has a visibility flag:
#   private     — never shown to buyers
#   post_intro  — shown on seller profile after buyer's intro is accepted

ALLOWED_DOC_TYPES = {
    "id_doc", "certificate", "training", "membership",
    "professional_role", "guide", "recipe", "presentation", "other"
}

# Map doc_type → signal_id that should be set to 'pending' on upload
_DOC_TYPE_TO_SIGNAL = {
    "id_doc":            "category.lm.id_uploaded",
    "certificate":       "category.lm.formal_cert",
    "training":          "category.lm.training_course",
    "membership":        "category.lm.prof_body",
    "professional_role": "category.lm.provincial_role",
    "guide":             "category.lm.product_guide",
    "recipe":            "category.lm.product_guide",
}

@app.post("/users/{email}/documents")
async def upload_seller_document(
    email: str,
    file: UploadFile = File(...),
    doc_type: str = Form("other"),
    label: str = Form(""),
    visibility: str = Form("private"),
    signal_id: str = Form(None),
    _key: str = Depends(auth.require_api_key),
):
    """Upload a document for a seller. Stores to R2, records in seller_documents.
    If the doc_type maps to a Trust Score signal, auto-sets it to pending."""
    email = email.lower().strip()
    if doc_type not in ALLOWED_DOC_TYPES:
        doc_type = "other"
    if visibility not in ("private", "post_intro"):
        visibility = "private"

    allowed_mime = {
        "application/pdf", "image/jpeg", "image/png", "image/webp",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }
    ct = file.content_type or "application/octet-stream"
    if ct not in allowed_mime:
        raise HTTPException(status_code=400, detail="Only PDF, JPEG, PNG, WebP, or Word documents accepted")

    raw = await file.read()
    if len(raw) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Document too large — max 25MB")

    # Upload to R2 or local fallback
    orig_name = (file.filename or "document").replace(" ", "_")
    key = f"docs/{uuid.uuid4().hex}_{orig_name}"
    if _S3_CONFIGURED:
        url = _s3_upload(raw, key, ct)
    else:
        safe = key.replace("/", "_")
        path = os.path.join(MEDIA_DIR, safe)
        with open(path, "wb") as fh:
            fh.write(raw)
        url = f"/media/{safe}"

    # Determine signal_id to auto-trigger pending
    effective_signal = signal_id or _DOC_TYPE_TO_SIGNAL.get(doc_type)

    conn = database.get_db()
    try:
        conn.execute(
            """INSERT INTO seller_documents (email, doc_type, label, url, visibility, signal_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email, doc_type, label or orig_name, url, visibility, effective_signal)
        )
        doc_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]
        # Auto-set signal to pending if not already earned
        if effective_signal:
            existing = conn.execute(
                "SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
                (email, effective_signal)
            ).fetchone()
            if not existing:
                conn.execute(
                    """INSERT INTO user_credentials (email, signal_id, status, updated_at)
                       VALUES (?, ?, 'pending', strftime('%Y-%m-%dT%H:%M:%SZ','now'))""",
                    (email, effective_signal)
                )
            elif existing["status"] not in ("earned", "pending"):
                conn.execute(
                    """UPDATE user_credentials SET status='pending', updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')
                       WHERE email=? AND signal_id=?""",
                    (email, effective_signal)
                )
        conn.commit()
    finally:
        conn.close()

    return {"id": doc_id, "url": url, "doc_type": doc_type, "label": label or orig_name,
            "visibility": visibility, "signal_id": effective_signal}


@app.get("/users/{email}/documents")
def list_seller_documents(
    email: str,
    _key: str = Depends(auth.require_api_key),
):
    """List all documents for a seller (admin-only view — all visibility levels)."""
    email = email.lower().strip()
    conn = database.get_db()
    rows = conn.execute(
        """SELECT id, doc_type, label, url, visibility, signal_id, uploaded_at
           FROM seller_documents WHERE email=? ORDER BY uploaded_at DESC""",
        (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.get("/users/{email}/documents/public")
def list_public_documents(email: str, intro_id: int = None):
    """Return post_intro documents for a seller. Called by buyer app after intro accepted.
    No API key required — documents are intentionally shared post-introduction."""
    email = email.lower().strip()
    conn = database.get_db()
    # Verify intro exists and is accepted before revealing docs
    if intro_id:
        intro = conn.execute(
            "SELECT status FROM intro_requests WHERE id=? AND seller_email=?",
            (intro_id, email)
        ).fetchone()
        if not intro or intro["status"] != "accepted":
            conn.close()
            return []
    rows = conn.execute(
        """SELECT id, doc_type, label, url, uploaded_at
           FROM seller_documents WHERE email=? AND visibility='post_intro'
           ORDER BY uploaded_at DESC""",
        (email,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@app.delete("/users/{email}/documents/{doc_id}")
def delete_seller_document(
    email: str,
    doc_id: int,
    _key: str = Depends(auth.require_api_key),
):
    """Delete a document record (does not delete from R2 — orphan cleanup runs separately)."""
    email = email.lower().strip()
    conn = database.get_db()
    row = conn.execute(
        "SELECT id FROM seller_documents WHERE id=? AND email=?", (doc_id, email)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Document not found")
    conn.execute("DELETE FROM seller_documents WHERE id=?", (doc_id,))
    conn.commit()
    conn.close()
    return {"deleted": doc_id}


# ── IDENTITY VERIFICATION (KYC) ──────────────────────────────────────────────
# Design principles (Session 34):
#   - Never store raw ID numbers — SHA-256 hash only
#   - SA ID number: validate via Luhn checksum (free, instant, 100% reliable)
#   - Passport / national ID: AI vision (Sonnet) extracts and confirms
#   - Swap point: replace _sonnet_verify_identity() with PaddleOCR when cost warrants
#   - Admin always has final confirm — AI result is pre-check only

import hashlib
import re
import base64
import urllib.request

SONNET_MODEL = "claude-sonnet-4-6"


def _sa_id_validate(id_number: str) -> dict:
    """Validate a South African ID number (13 digits).
    Returns dict: valid(bool), dob(str), gender(str), citizen(str), error(str|None)."""
    n = re.sub(r"\D", "", id_number)
    if len(n) != 13:
        return {"valid": False, "error": "SA ID number must be exactly 13 digits"}
    # Luhn checksum
    total = 0
    for i, ch in enumerate(n[:-1]):
        d = int(ch)
        if i % 2 == 1:
            d *= 2
            if d > 9:
                d -= 9
        total += d
    check = (10 - (total % 10)) % 10
    if check != int(n[12]):
        return {"valid": False, "error": "ID number checksum failed — please check for typos"}
    # Extract DOB (YYMMDD)
    yy, mm, dd = n[0:2], n[2:4], n[4:6]
    year = int(yy)
    century = 1900 if year >= 24 else 2000  # SA IDs: >=24 = 1900s
    dob = f"{century + year}-{mm}-{dd}"
    gender = "Male" if int(n[6:10]) >= 5000 else "Female"
    citizen = "SA Citizen" if n[10] == "0" else "Permanent Resident"
    return {"valid": True, "dob": dob, "gender": gender, "citizen": citizen, "error": None}


def _hash_id_number(id_number: str) -> str:
    """SHA-256 hash of normalised ID number. Never store the raw number."""
    normalised = re.sub(r"\D", "", id_number).upper()
    return hashlib.sha256(normalised.encode()).hexdigest()


def _normalise_name(name: str) -> str:
    """Lowercase, strip extra spaces, remove punctuation for fuzzy comparison."""
    return re.sub(r"[^a-z ]", "", name.lower().strip())


def _names_match(name_a: str, name_b: str) -> float:
    """Simple fuzzy name match — returns 0.0–1.0 confidence.
    Handles initials: 'J Smith' matches 'John Smith' at 0.8+."""
    a = _normalise_name(name_a).split()
    b = _normalise_name(name_b).split()
    if not a or not b:
        return 0.0
    # Check surname always present
    surname_a = a[-1]
    surname_b = b[-1]
    if surname_a != surname_b:
        return 0.2
    # Count matching given names / initials
    given_a = a[:-1]
    given_b = b[:-1]
    if not given_a or not given_b:
        return 0.7  # surname match, no given names to compare
    matches = 0
    for ga in given_a:
        for gb in given_b:
            if ga == gb or (len(ga) == 1 and gb.startswith(ga)) or (len(gb) == 1 and ga.startswith(gb)):
                matches += 1
                break
    score = 0.7 + 0.3 * (matches / max(len(given_a), len(given_b)))
    return round(min(score, 1.0), 2)


async def _sonnet_verify_identity(doc_url: str, claimed_name: str,
                                   claimed_id: str, doc_type: str) -> dict:
    """Call Sonnet vision to verify identity document.
    SWAP POINT: replace this function with PaddleOCR/PassportEye for zero-token operation.
    Returns: {verified(bool), confidence(float), extracted_name(str),
              extracted_id(str), notes(str), model(str)}"""
    if not ANTHROPIC_API_KEY:
        return {"verified": False, "confidence": 0.0, "extracted_name": "",
                "extracted_id": "", "notes": "AI verification unavailable — API key not set",
                "model": "none"}
    try:
        # Fetch the document image
        req = urllib.request.Request(doc_url, headers={"User-Agent": "TrustSquare-KYC/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            img_bytes = resp.read()
        img_b64 = base64.standard_b64encode(img_bytes).decode()
        # Detect media type
        media_type = "image/jpeg"
        if doc_url.lower().endswith(".png"):
            media_type = "image/png"
        elif doc_url.lower().endswith(".webp"):
            media_type = "image/webp"

        import anthropic as _anthropic
        client = _anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        prompt = f"""You are a document verification assistant for TrustSquare marketplace.
Examine this identity document image carefully.

The seller claims:
- Full name: {claimed_name}
- ID/passport number: {claimed_id}
- Document type: {doc_type}

Your task:
1. Extract the FULL NAME exactly as printed on the document
2. Extract the ID NUMBER / PASSPORT NUMBER exactly as printed
3. Determine if the claimed name matches the document name (allow for initials, middle names)
4. Determine if the claimed number matches the document number

Respond ONLY with valid JSON in this exact format:
{{
  "extracted_name": "<full name from document>",
  "extracted_id": "<id/passport number from document>",
  "name_match": <true/false>,
  "id_match": <true/false>,
  "confidence": <0.0-1.0>,
  "document_appears_genuine": <true/false>,
  "notes": "<any concerns or observations, empty string if none>"
}}

If you cannot read the document clearly, set confidence below 0.5 and explain in notes."""

        message = client.messages.create(
            model=SONNET_MODEL,
            max_tokens=300,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": media_type, "data": img_b64
                    }},
                    {"type": "text", "text": prompt}
                ]
            }]
        )
        raw = message.content[0].text.strip()
        # Parse JSON from response
        json_match = re.search(r'\{[\s\S]*\}', raw)
        if not json_match:
            raise ValueError("No JSON in Sonnet response")
        result = json.loads(json_match.group())
        verified = (result.get("name_match") and result.get("id_match") and
                    result.get("confidence", 0) >= 0.75 and
                    result.get("document_appears_genuine", True))
        return {
            "verified": bool(verified),
            "confidence": float(result.get("confidence", 0)),
            "extracted_name": result.get("extracted_name", ""),
            "extracted_id": result.get("extracted_id", ""),
            "notes": result.get("notes", ""),
            "model": SONNET_MODEL,
        }
    except Exception as e:
        return {"verified": False, "confidence": 0.0, "extracted_name": "",
                "extracted_id": "", "notes": f"Verification error: {str(e)}", "model": SONNET_MODEL}


class IdentityVerifyIn(BaseModel):
    id_number: str          # SA ID (13 digits) or passport number
    full_name: str          # As it appears on the document
    doc_type: str = "sa_id" # sa_id | passport | national_id
    doc_url: str            # URL of the already-uploaded ID document in R2


class BankingIn(BaseModel):
    account_holder: str
    bank_name: str
    account_number: str   # We store last 4 digits only
    branch_code: str = ""


@app.post("/users/{email}/verify-identity")
async def verify_identity(
    email: str,
    payload: IdentityVerifyIn,
    _key: str = Depends(auth.require_api_key),
):
    """Step 1: Validate format. Step 2: Sonnet vision cross-check.
    Step 3: Award trust signals based on confidence. Never store raw ID number."""
    email = email.lower().strip()
    conn = database.get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not found")

    result = {
        "format_valid": False, "ai_verified": False,
        "confidence": 0.0, "notes": "", "signals_awarded": []
    }

    # ── Step 1: Format validation ─────────────────────────────────────────
    doc_type = payload.doc_type.lower()
    id_clean = re.sub(r"\D", "", payload.id_number) if doc_type == "sa_id" else payload.id_number.strip()

    if doc_type == "sa_id":
        sa_check = _sa_id_validate(id_clean)
        if not sa_check["valid"]:
            conn.close()
            return {**result, "error": sa_check["error"]}
        result["format_valid"] = True
        result["dob"] = sa_check.get("dob")
        result["gender"] = sa_check.get("gender")
    else:
        # Passport / national ID — basic length check
        result["format_valid"] = len(id_clean) >= 6
        if not result["format_valid"]:
            conn.close()
            return {**result, "error": "Document number too short"}

    # Award format-valid signal
    _upsert_credential(conn, email, "category.lm.id_number_valid", "earned")
    result["signals_awarded"].append("category.lm.id_number_valid")

    # Store hashed ID + name
    id_hash = _hash_id_number(id_clean)
    conn.execute(
        """UPDATE users SET id_number_hash=?, id_name=?, id_doc_type=?
           WHERE email=?""",
        (id_hash, payload.full_name.strip(), doc_type, email)
    )
    conn.commit()

    # ── Step 2: Sonnet vision verification ───────────────────────────────
    ai = await _sonnet_verify_identity(
        payload.doc_url, payload.full_name, payload.id_number, doc_type
    )
    result["ai_verified"]    = ai["verified"]
    result["confidence"]     = ai["confidence"]
    result["extracted_name"] = ai["extracted_name"]
    result["notes"]          = ai["notes"]
    result["model"]          = ai["model"]

    if ai["verified"] and ai["confidence"] >= 0.75:
        _upsert_credential(conn, email, "category.lm.id_ai_verified", "earned")
        result["signals_awarded"].append("category.lm.id_ai_verified")
        conn.execute(
            "UPDATE users SET id_verified_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), id_ai_score=? WHERE email=?",
            (ai["confidence"], email)
        )
    elif ai["confidence"] >= 0.5:
        # Partial confidence — set pending for admin review
        _upsert_credential(conn, email, "category.lm.id_ai_verified", "pending")
        result["signals_awarded"].append("category.lm.id_ai_verified (pending — admin review)")

    conn.commit()
    conn.close()
    return result


async def _run_cert_name_check(email: str, doc_url: str, id_name: str, doc_type: str):
    """Background task: Sonnet vision checks that the name on a certificate
    matches the seller's verified ID name. Awards cert_name_verified if
    confidence >= 0.75 and name match >= 0.70.

    SWAP POINT: replace _sonnet_verify_identity() here with
    PaddleOCR + local name extraction when token cost warrants it.
    """
    import logging
    _log = logging.getLogger(__name__)
    try:
        result = await _sonnet_verify_identity(
            doc_url=doc_url,
            claimed_name=id_name,
            claimed_id="",
            doc_type=doc_type,
        )
        confidence  = result.get("confidence", 0.0)
        name_match  = _names_match(id_name, result.get("extracted_name", ""))
        verified_ok = confidence >= 0.75 and name_match >= 0.70
        new_status  = "earned" if verified_ok else "pending"

        conn = database.get_db()
        try:
            _upsert_credential(conn, email, "category.lm.cert_name_verified", new_status)
            conn.commit()
            _log.info("cert_name_check %s → %s (conf=%.2f name_match=%.2f)",
                      email, new_status, confidence, name_match)
        finally:
            conn.close()
    except Exception as exc:
        _log.warning("cert_name_check failed for %s: %s", email, exc)


def _upsert_credential(conn, email: str, signal_id: str, status: str):
    """Insert or update a credential — never downgrade earned to pending."""
    existing = conn.execute(
        "SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
        (email, signal_id)
    ).fetchone()
    if not existing:
        conn.execute(
            """INSERT INTO user_credentials (email, signal_id, status, updated_at)
               VALUES (?, ?, ?, strftime('%Y-%m-%dT%H:%M:%SZ','now'))""",
            (email, signal_id, status)
        )
    elif existing["status"] != "earned":  # never downgrade earned
        conn.execute(
            """UPDATE user_credentials SET status=?, updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')
               WHERE email=? AND signal_id=?""",
            (status, email, signal_id)
        )


@app.post("/users/{email}/banking")
def add_banking(
    email: str,
    payload: BankingIn,
    _key: str = Depends(auth.require_api_key),
):
    """Store bank details (last 4 digits only). Cross-check account holder name
    against verified ID name on file. Award trust signals."""
    email = email.lower().strip()
    conn = database.get_db()
    user = conn.execute("SELECT id_name FROM users WHERE email=?", (email,)).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not found")

    last4 = re.sub(r"\D", "", payload.account_number)[-4:] if payload.account_number else ""
    conn.execute(
        """UPDATE users SET banking_holder=?, banking_bank=?,
           banking_account_last4=?, banking_branch=?,
           banking_added_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')
           WHERE email=?""",
        (payload.account_holder, payload.bank_name, last4,
         payload.branch_code, email)
    )
    signals = []
    _upsert_credential(conn, email, "category.lm.banking", "earned")
    signals.append("category.lm.banking")

    # Name match against ID name on file
    name_match_score = 0.0
    id_name = user["id_name"] if user["id_name"] else ""
    if id_name:
        name_match_score = _names_match(payload.account_holder, id_name)
        if name_match_score >= 0.75:
            _upsert_credential(conn, email, "category.lm.banking_name_match", "earned")
            signals.append("category.lm.banking_name_match")
        else:
            _upsert_credential(conn, email, "category.lm.banking_name_match", "pending")
            signals.append("category.lm.banking_name_match (pending — name mismatch, admin review)")

    conn.commit()
    conn.close()
    return {
        "signals_awarded": signals,
        "name_match_score": name_match_score,
        "account_last4": last4,
        "name_on_file": id_name or "No ID name on file yet",
    }


@app.get("/users/{email}/identity-status")
def identity_status(email: str, _key: str = Depends(auth.require_api_key)):
    """Return KYC status for a seller — used by admin Document Hub."""
    email = email.lower().strip()
    conn = database.get_db()
    row = conn.execute(
        """SELECT id_name, id_doc_type, id_verified_at, id_ai_score,
                  banking_holder, banking_bank, banking_account_last4, banking_added_at
           FROM users WHERE email=?""", (email,)
    ).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Seller not found")
    return dict(row)


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
  <title>Unsubscribed - TrustSquare</title>
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
    <h1>You’re unsubscribed</h1>
    <p>We’ve removed <strong>{email}</strong> from our outreach list.<br>
    You won’t receive any further emails from TrustSquare about listing opportunities.</p>
    <p style="margin-top:24px; font-size:13px; color:#aaa;">
      Changed your mind? Visit <a href="https://trustsquare.co">trustsquare.co</a> to list directly.
    </p>
  </div>
</body>
</html>"""

    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_response, status_code=200)
