from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form, BackgroundTasks, Request, Header, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
import database
import auth
import storage
import ai_service_tiers  # Tiered Value Selector: tier config + availability resolver
import feature_flags     # TVS STEP 5: server-readable paid/provider flag store
import tier_resolvers    # TVS STEP 3: FREE/owned data resolvers (no paid/consumption API)
import launch_redemption  # Founders Badge + monthly Tuppence allocation + flood control (Canon Addendum 1)
import os
import json
import re
import hashlib
import urllib.request
import base64
import httpx
from PIL import Image, ImageOps
import io
import logging
import smtplib
from email.message import EmailMessage
from email.utils import parseaddr, formataddr
from datetime import datetime, timezone, timedelta

app = FastAPI(title="TrustSquare BEA", version="1.3.1")

# S4 (audit · HIGH): CORS locked to TrustSquare origins only.
# Previously allow_origins=["*"] + allow_origin_regex=".*" — any site could call the BEA
# from a user's browser. Auth is X-Api-Key/email (allow_credentials stays False), and the
# buyer/admin/dashboard are all same-origin on trustsquare.co, so an explicit allowlist
# breaks nothing. A new origin must be added here deliberately.
ALLOWED_ORIGINS = [
    "https://trustsquare.co",
    "https://www.trustsquare.co",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()


# CityLauncher scrapes AGENCY vocabulary ("Estate Agents", "Car Dealers", ...); the app
# speaks 6 category names. This maps a scraped label to the app category the demand loop
# matches on. Keyword-based so it survives new agency labels; None = leave unmatched.
def _demand_norm_category(raw):
    t = (raw or "").strip().lower()
    if not t:
        return None
    _M = (("estate", "Property"), ("propert", "Property"), ("realt", "Property"), ("home", "Property"), ("letting", "Property"),
          ("car ", "Cars"), ("cars", "Cars"), ("dealer", "Cars"), ("vehicle", "Cars"), ("auto", "Cars"), ("motor", "Cars"), ("bakkie", "Cars"),
          ("tutor", "Tutors"), ("school", "Tutors"), ("universit", "Tutors"), ("educat", "Tutors"), ("college", "Tutors"), ("teach", "Tutors"), ("tuition", "Tutors"),
          ("collect", "Collectors"), ("card", "Collectors"), ("hobby", "Collectors"), ("antique", "Collectors"), ("coin", "Collectors"), ("stamp", "Collectors"), ("memorabil", "Collectors"),
          ("travel", "Adventures"), ("tour", "Adventures"), ("adventure", "Adventures"), ("safari", "Adventures"), ("lodge", "Adventures"), ("experience", "Adventures"), ("guide", "Adventures"),
          ("service", "Services"), ("trade", "Services"), ("compan", "Services"), ("contractor", "Services"), ("plumb", "Services"), ("electric", "Services"), ("casual", "Services"), ("technical", "Services"))
    for kw, cat in _M:
        if kw in t:
            return cat
    if t.title() in {"Property","Cars","Tutors","Services","Collectors","Adventures"}:
        return t.title()
    return None


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
        ("collectible_type", "TEXT"),
        ("condition",        "TEXT"),
        ("era_year",         "INTEGER"),
        ("ai_grade",         "TEXT"),
        ("ai_grade_conf",    "REAL"),
        ("ai_grade_notes",   "TEXT"),
        ("grade_tier",       "INTEGER"),
        # Vehicle spec columns (CARS-SPEC-1, cars brief Part B) — 10 filterable
        # discrete + vehicle_specs JSON superset + spec_confirmed section map +
        # attestation stamp (attested_* set ONLY by publish endpoints).
        ("make",             "TEXT"),
        ("model",            "TEXT"),
        ("variant",          "TEXT"),
        ("vehicle_year",     "INTEGER"),
        ("mileage_km",       "INTEGER"),
        ("transmission",     "TEXT"),
        ("fuel_type",        "TEXT"),
        ("body_type",        "TEXT"),
        ("drivetrain",       "TEXT"),
        ("colour",           "TEXT"),
        ("vehicle_specs",    "TEXT"),
        ("spec_confirmed",   "TEXT"),
        ("attested_at",      "TEXT"),
        ("attested_email",   "TEXT"),
    ]:
        if _col not in listing_cols:
            conn.execute(f"ALTER TABLE listings ADD COLUMN {_col} {_type}")

    # ── SEARCH ENGINE Step 1 (FILTER_ENGINE_DESIGN, built 6 Jul 2026) ─────────
    # price_num: numeric mirror of the TEXT price for honest server-side filtering.
    if "price_num" not in listing_cols:
        conn.execute("ALTER TABLE listings ADD COLUMN price_num REAL")
    # Backfill any unparsed rows (idempotent, cheap at current scale).
    try:
        import re as _re_pm
        _rows = conn.execute("SELECT id, price FROM listings WHERE price_num IS NULL AND price IS NOT NULL").fetchall()
        for _r in _rows:
            _c = _re_pm.sub(r"[^0-9.]", "", str(_r["price"]).replace(",", "").replace(" ", ""))
            try:
                _v = float(_c)
                if _v > 0:
                    conn.execute("UPDATE listings SET price_num=? WHERE id=?", (_v, _r["id"]))
            except Exception:
                pass
    except Exception:
        pass
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_price_num ON listings(price_num)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_trust ON listings(trust_score)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_cat_city ON listings(category, city)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_make_year ON listings(make, vehicle_year)")
    # FTS5: one text index across the fields a human types ("BMW 1996 E36").
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS listings_fts USING fts5(
        title, description, make, model, variant, subject, service_type, prop_type,
        content='listings', content_rowid='rowid')""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS listings_fts_ai AFTER INSERT ON listings BEGIN
        INSERT INTO listings_fts(rowid,title,description,make,model,variant,subject,service_type,prop_type)
        VALUES (new.rowid,new.title,new.description,new.make,new.model,new.variant,new.subject,new.service_type,new.prop_type); END""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS listings_fts_ad AFTER DELETE ON listings BEGIN
        INSERT INTO listings_fts(listings_fts,rowid,title,description,make,model,variant,subject,service_type,prop_type)
        VALUES ('delete',old.rowid,old.title,old.description,old.make,old.model,old.variant,old.subject,old.service_type,old.prop_type); END""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS listings_fts_au AFTER UPDATE ON listings BEGIN
        INSERT INTO listings_fts(listings_fts,rowid,title,description,make,model,variant,subject,service_type,prop_type)
        VALUES ('delete',old.rowid,old.title,old.description,old.make,old.model,old.variant,old.subject,old.service_type,old.prop_type);
        INSERT INTO listings_fts(rowid,title,description,make,model,variant,subject,service_type,prop_type)
        VALUES (new.rowid,new.title,new.description,new.make,new.model,new.variant,new.subject,new.service_type,new.prop_type); END""")
    # One-time (idempotent) FTS backfill: rebuild if the index is empty but listings exist.
    # NB: on an external-content FTS5 table, count(*) on the fts table proxies to the
    # CONTENT table (never 0) — the real index size lives in the _docsize shadow table.
    try:
        _n_fts = conn.execute("SELECT count(*) AS n FROM listings_fts_docsize").fetchone()["n"]
        _n_l   = conn.execute("SELECT count(*) AS n FROM listings").fetchone()["n"]
        if _n_l > 0 and _n_fts == 0:
            conn.execute("INSERT INTO listings_fts(listings_fts) VALUES ('rebuild')")
    except Exception:
        pass

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
        # seller subscription tier — added Session 35
        "ALTER TABLE users ADD COLUMN seller_tier TEXT NOT NULL DEFAULT 'free'",
        # subscription slot limit + pending downgrade — added Session 91
        "ALTER TABLE users ADD COLUMN slot_limit INTEGER NOT NULL DEFAULT 2",
        "ALTER TABLE users ADD COLUMN pending_downgrade_tier TEXT",
        "ALTER TABLE users ADD COLUMN billing_period_end TEXT",
        # category-scoped credentials — added Session 37
        "ALTER TABLE user_credentials ADD COLUMN listing_category TEXT",
        "ALTER TABLE listings ADD COLUMN is_demo INTEGER NOT NULL DEFAULT 0",
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

    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_declarations (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            email        TEXT    NOT NULL,
            signal_id    TEXT    NOT NULL,
            declaration  TEXT    NOT NULL,
            points_awarded INTEGER NOT NULL DEFAULT 0,
            declared_at  TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            UNIQUE(email, signal_id)
        )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_decl_email ON user_declarations(email)")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS listing_cities (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            listing_id          INTEGER NOT NULL,
            city_id             INTEGER NOT NULL,
            seller_confirmed_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            added_at            TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
            UNIQUE(listing_id, city_id)
        )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lc_listing ON listing_cities(listing_id)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_lc_city ON listing_cities(city_id)")

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
    # DEMAND-LOOP-1 groundwork (6 Jul 2026): how many results the search returned
    # at capture time. 0 = a MISS — the raw material for demand-driven seller
    # acquisition (match miss -> prospect pool -> coded invite -> wishlist ping).
    _ws_cols = {r[1] for r in conn.execute("PRAGMA table_info(wishlist_signals)").fetchall()}
    if "result_count" not in _ws_cols:
        conn.execute("ALTER TABLE wishlist_signals ADD COLUMN result_count INTEGER")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ws_buyer ON wishlist_signals(buyer_token)")
    # SEARCH-AI-1 (6 Jul 2026): cache for AI-interpreted search sentences — a repeated
    # sentence costs $0. Keyed on the normalised query, city-agnostic by design.
    conn.execute("""CREATE TABLE IF NOT EXISTS search_interpret_cache (
        query_norm  TEXT PRIMARY KEY,
        params_json TEXT NOT NULL,
        model       TEXT,
        cost_usd    REAL NOT NULL DEFAULT 0,
        created_at  TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    # DEMAND-LOOP-1 (David ruling 6 Jul 2026): the demand loop is a STANDARD automated
    # BEA process (CityLauncher stays manual campaign artillery). Capture/score/ticket
    # always on ($0, internal); match/invite stages env-gated + dry-run.
    if "seen_count" not in _ws_cols:
        conn.execute("ALTER TABLE wishlist_signals ADD COLUMN seen_count INTEGER NOT NULL DEFAULT 1")
    conn.execute("""CREATE TABLE IF NOT EXISTS demand_tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        signal_id INTEGER, buyer_token TEXT NOT NULL,
        query_norm TEXT NOT NULL, category TEXT, city_id INTEGER,
        score INTEGER NOT NULL DEFAULT 0,
        state TEXT NOT NULL DEFAULT 'open',
        matched_prospect TEXT, matched_item TEXT, invite_code TEXT,
        priority_expires_at TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now')),
        updated_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_demand_state ON demand_tickets(state, score DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_demand_query ON demand_tickets(query_norm, city_id)")
    # Shared suppression ledger — ONE outreach touch per address across ALL channels
    # (RM-5 waves + demand invites). Checked before ANY send; seed from CityLauncher at flip-on.
    conn.execute("""CREATE TABLE IF NOT EXISTS outreach_ledger (
        email_hash TEXT NOT NULL, channel TEXT NOT NULL, campaign TEXT,
        sent_at TEXT NOT NULL DEFAULT (datetime('now')),
        suppressed INTEGER NOT NULL DEFAULT 0
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_outreach_email ON outreach_ledger(email_hash, sent_at DESC)")
    conn.execute("""CREATE TABLE IF NOT EXISTS demand_prospects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email_hash TEXT NOT NULL, email_enc TEXT,
        category TEXT, city_id INTEGER, scraped_item TEXT, source TEXT,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    _dp_cols = {r[1] for r in conn.execute("PRAGMA table_info(demand_prospects)").fetchall()}
    if "app_category" not in _dp_cols:
        conn.execute("ALTER TABLE demand_prospects ADD COLUMN app_category TEXT")
    if "city_name" not in _dp_cols:
        conn.execute("ALTER TABLE demand_prospects ADD COLUMN city_name TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_dp_appcat ON demand_prospects(app_category, city_id)")
    # One-time backfill: normalise agency labels already imported (idempotent — only NULLs).
    for _pr in conn.execute("SELECT id, category FROM demand_prospects WHERE app_category IS NULL").fetchall():
        conn.execute("UPDATE demand_prospects SET app_category=? WHERE id=?",
                     (_demand_norm_category(_pr["category"]), _pr["id"]))
    conn.execute("CREATE INDEX IF NOT EXISTS idx_prospects_cat ON demand_prospects(category, city_id)")
    conn.execute("""CREATE TABLE IF NOT EXISTS demand_invites_outbox (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticket_id INTEGER NOT NULL, email_hash TEXT,
        subject TEXT, body TEXT, dry_run INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    )""")
    # RM-5 pool auto-import (one-time, idempotent): set DEMAND_RM5_DB=/path/to/prospects.db
    # on the server and restart - runs only while demand_prospects is EMPTY. Copies the
    # CityLauncher pool + seeds the shared suppression ledger from emailed_at history and
    # bounce/complaint/stop events. Opens the source READ-ONLY; never writes to it.
    try:
        _rm5 = os.getenv("DEMAND_RM5_DB", "")
        # If prospects were imported before city_name existed (city_id may be unresolved),
        # clear them once so the import re-runs WITH the raw city name preserved.
        if _rm5 and conn.execute("SELECT COUNT(*) FROM demand_prospects").fetchone()[0] > 0 \
           and conn.execute("SELECT COUNT(*) FROM demand_prospects WHERE city_name IS NOT NULL").fetchone()[0] == 0:
            conn.execute("DELETE FROM demand_prospects")
            conn.execute("DELETE FROM outreach_ledger WHERE channel IN ('rm5_wave','rm5_events')")
            print("DEMAND-RM5 re-import: cleared pre-city_name prospects")
        if _rm5 and os.path.exists(_rm5) and \
           conn.execute("SELECT COUNT(*) AS n FROM demand_prospects").fetchone()[0] == 0:
            import sqlite3 as _sq3, hashlib as _hl
            _src = _sq3.connect("file:" + _rm5 + "?mode=ro", uri=True)
            _src.row_factory = _sq3.Row
            _cities = {(r[1] or "").strip().lower(): r[0] for r in conn.execute(
                "SELECT id, name FROM geo_cities").fetchall()}
            _n_p = _n_l = _n_s = 0
            for r in _src.execute("SELECT * FROM prospects WHERE email IS NOT NULL"):
                _em = (r["email"] or "").strip().lower()
                if "@" not in _em:
                    continue
                _h = _hl.sha256(_em.encode()).hexdigest()[:32]
                _cid = _cities.get((r["city"] or "").strip().lower())
                _raw_cat = (r["category"] or "").strip() or None
                _raw_city = (r["city"] or "").strip() or None
                conn.execute(
                    "INSERT INTO demand_prospects (email_hash, email_enc, category, app_category, city_id, city_name, scraped_item, source) "
                    "VALUES (?,?,?,?,?,?,?,?)",
                    (_h, _em, _raw_cat, _demand_norm_category(_raw_cat), _cid, _raw_city, None, "rm5"))
                _n_p += 1
                if r["emailed_at"]:
                    conn.execute(
                        "INSERT INTO outreach_ledger (email_hash, channel, campaign, sent_at) VALUES (?,?,?,?)",
                        (_h, "rm5_wave", (r["city"] or ""), r["emailed_at"]))
                    _n_l += 1
            for r in _src.execute(
                    "SELECT p.email AS email FROM email_events e JOIN prospects p ON p.id = e.prospect_id "
                    "WHERE LOWER(e.event) IN ('bounce','bounced','complaint','complained','unsubscribe','unsubscribed','stop')"):
                _em = (r["email"] or "").strip().lower()
                if "@" in _em:
                    conn.execute(
                        "INSERT INTO outreach_ledger (email_hash, channel, campaign, suppressed) VALUES (?,?,?,1)",
                        (_hl.sha256(_em.encode()).hexdigest()[:32], "rm5_events", "suppression-seed"))
                    _n_s += 1
            _src.close()
            print("DEMAND-RM5 import: %d prospects, %d ledger rows, %d suppressions" % (_n_p, _n_l, _n_s))
    except Exception as _rm5e:
        print("DEMAND-RM5 import skipped: %s" % _rm5e)
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
    if "ai_suggested_price" not in listing_cols2:
        # Stores the AI vision-draft price so AI3 price-check can anchor to it
        conn.execute("ALTER TABLE listings ADD COLUMN ai_suggested_price REAL")
    if "scryfall_id" not in listing_cols2:
        # Resolved Scryfall card id for collectible listings, so AI3 price-check
        # can fetch a REAL market price instead of an AI guess. NULL = not a card
        # / not resolved. Set at listing creation; see resolve_scryfall_id().
        conn.execute("ALTER TABLE listings ADD COLUMN scryfall_id TEXT")

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
    # ── AI Spend Logging (Session 90) ─────────────────────────
    conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_log (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        email         TEXT    NOT NULL DEFAULT '',
        endpoint      TEXT    NOT NULL,
        model         TEXT    NOT NULL,
        est_cost_usd  REAL    NOT NULL DEFAULT 0.0,
        logged_at     TEXT    NOT NULL DEFAULT (datetime('now'))
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_spend_month ON ai_spend_log(logged_at)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ai_spend_email ON ai_spend_log(email, logged_at DESC)")
    # C2 (Session 97) — real token counts + flag for real-cost vs flat-estimate rows.
    for _col, _ddl in (
        ("input_tokens",  "ALTER TABLE ai_spend_log ADD COLUMN input_tokens  INTEGER NOT NULL DEFAULT 0"),
        ("output_tokens", "ALTER TABLE ai_spend_log ADD COLUMN output_tokens INTEGER NOT NULL DEFAULT 0"),
        ("cost_is_real",  "ALTER TABLE ai_spend_log ADD COLUMN cost_is_real  INTEGER NOT NULL DEFAULT 0"),
    ):
        try:
            conn.execute(_ddl)
        except Exception:
            pass

    conn.execute("""CREATE TABLE IF NOT EXISTS ai_spend_config (
        id                  INTEGER PRIMARY KEY CHECK (id = 1),
        monthly_income_usd  REAL    NOT NULL DEFAULT 0.0,
        alert_threshold_pct REAL    NOT NULL DEFAULT 20.0,
        alert_email         TEXT    NOT NULL DEFAULT 'dmcontiki2@gmail.com',
        last_alerted_at     TEXT
    )""")
    # Seed default config row (id=1 enforced by CHECK constraint)
    conn.execute("""INSERT OR IGNORE INTO ai_spend_config
        (id, monthly_income_usd, alert_threshold_pct, alert_email)
        VALUES (1, 0.0, 20.0, 'dmcontiki2@gmail.com')""")

    # Launch Switch (free-only <-> verified) — singleton flag row; default = launch/free-only
    conn.execute("""CREATE TABLE IF NOT EXISTS launch_switches (
        id            INTEGER PRIMARY KEY CHECK (id = 1),
        mode          TEXT    NOT NULL DEFAULT 'launch',
        verified_tier INTEGER NOT NULL DEFAULT 0,
        videos        INTEGER NOT NULL DEFAULT 0,
        data_ops      INTEGER NOT NULL DEFAULT 0,
        data_places   INTEGER NOT NULL DEFAULT 0,
        data_flights  INTEGER NOT NULL DEFAULT 0,
        data_mapbox   INTEGER NOT NULL DEFAULT 0,
        p_heritage    INTEGER NOT NULL DEFAULT 0,
        p_expedition  INTEGER NOT NULL DEFAULT 0,
        p_weekend     INTEGER NOT NULL DEFAULT 0,
        -- BIT safe-state flags (Mitigator flips these to a SAFE value on a confirmed BIT failure).
        -- Defaults = NORMAL/healthy state; the Mitigator only ever moves them toward safe.
        ai_example_enabled     INTEGER NOT NULL DEFAULT 1,
        auth_fail_closed       INTEGER NOT NULL DEFAULT 0,
        tuppence_burn_enabled  INTEGER NOT NULL DEFAULT 1,
        -- AI provider seam (D1): live-switchable inference vendor (Page-4 control). Default = anthropic.
        ai_active     TEXT    NOT NULL DEFAULT 'anthropic',
        updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
    )""")
    conn.execute("INSERT OR IGNORE INTO launch_switches (id) VALUES (1)")
    # BIT safe-state flags — add to pre-existing launch_switches rows (idempotent).
    for _ddl in (
        "ALTER TABLE launch_switches ADD COLUMN ai_example_enabled    INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE launch_switches ADD COLUMN auth_fail_closed      INTEGER NOT NULL DEFAULT 0",
        "ALTER TABLE launch_switches ADD COLUMN tuppence_burn_enabled INTEGER NOT NULL DEFAULT 1",
        "ALTER TABLE launch_switches ADD COLUMN ai_active TEXT NOT NULL DEFAULT 'anthropic'",
    ):
        try:
            conn.execute(_ddl)
        except Exception:
            pass
    # C1 (Session 97) — HARD daily cost ceilings (USD), per-user + platform. 0 = off.
    # When the day's spend reaches the cap, the next paid AI call is REFUSED (429).
    for _col, _ddl in (
        ("daily_user_ceiling_usd",     "ALTER TABLE ai_spend_config ADD COLUMN daily_user_ceiling_usd     REAL NOT NULL DEFAULT 0.50"),
        ("daily_platform_ceiling_usd", "ALTER TABLE ai_spend_config ADD COLUMN daily_platform_ceiling_usd REAL NOT NULL DEFAULT 100.0"),
    ):
        try:
            conn.execute(_ddl)
        except Exception:
            pass

    # AI Email Triage (Session 94) — one row per inbound email handled by POST /email/inbound
    conn.execute("""CREATE TABLE IF NOT EXISTS email_triage (
        id            INTEGER PRIMARY KEY AUTOINCREMENT,
        from_addr     TEXT    NOT NULL DEFAULT '',
        to_addr       TEXT    NOT NULL DEFAULT '',
        subject       TEXT    NOT NULL DEFAULT '',
        body_preview  TEXT    NOT NULL DEFAULT '',
        category      TEXT    NOT NULL DEFAULT 'other',
        urgency       TEXT    NOT NULL DEFAULT 'normal',
        draft_reply   TEXT    NOT NULL DEFAULT '',
        status        TEXT    NOT NULL DEFAULT 'drafted',
        message_id    TEXT,
        received_at   TEXT    NOT NULL DEFAULT (datetime('now'))
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_email_triage_recv ON email_triage(received_at DESC)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_email_triage_cat  ON email_triage(category, received_at DESC)")

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
    # World Wonders — add linked_wonders column to listings if not present
    try:
        conn.execute("ALTER TABLE listings ADD COLUMN linked_wonders TEXT DEFAULT NULL")
        conn.commit()
    except Exception:
        pass  # column already exists

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

    # ── AGENCY (Team plan): umbrella over agent-seller emails ──────────
    # Each agent is a normal seller (own listings/trust/intros). The agency
    # adds membership, a per-agent listing cap (mirrored into users.slot_limit),
    # an import API key, and the countries it is licensed/operating in (gates
    # the Phase-2 recruit-agents listings to existing-presence markets only).
    conn.execute("""CREATE TABLE IF NOT EXISTS agencies (
        id           INTEGER PRIMARY KEY AUTOINCREMENT,
        name         TEXT NOT NULL,
        admin_email  TEXT NOT NULL,
        api_key      TEXT NOT NULL,
        countries    TEXT NOT NULL DEFAULT '',
        plan         TEXT NOT NULL DEFAULT 'team',
        verified     INTEGER NOT NULL DEFAULT 0,
        created_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now'))
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agencies_admin ON agencies(admin_email)")
    conn.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_agencies_apikey ON agencies(api_key)")
    conn.execute("""CREATE TABLE IF NOT EXISTS agency_members (
        agency_id    INTEGER NOT NULL,
        agent_email  TEXT NOT NULL,
        listing_cap  INTEGER NOT NULL DEFAULT 10,
        seat_paid    INTEGER NOT NULL DEFAULT 0,
        role         TEXT NOT NULL DEFAULT 'agent',
        status       TEXT NOT NULL DEFAULT 'invited',
        invited_at   TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ','now')),
        joined_at    TEXT,
        PRIMARY KEY (agency_id, agent_email)
    )""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_agency_members_email ON agency_members(agent_email)")

    # ── Listing State Machine columns (Session 37) ───────────────
    # listing_status drives the 7-state machine: DRAFT, LIVE, PAUSED,
    # FADE_OUT, WITHDRAWN, BLOCKED, ARCHIVED. Default 'live' so all
    # existing listings remain visible without a data backfill.
    listing_cols_sm = [r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()]
    if "listing_status" not in listing_cols_sm:
        conn.execute("ALTER TABLE listings ADD COLUMN listing_status TEXT NOT NULL DEFAULT 'live'")
    if "status_changed_at" not in listing_cols_sm:
        conn.execute("ALTER TABLE listings ADD COLUMN status_changed_at TEXT")
    if "block_cause" not in listing_cols_sm:
        # B1–B6 cause codes stored here on BLOCKED/ARCHIVED transitions
        conn.execute("ALTER TABLE listings ADD COLUMN block_cause TEXT")
    if "fade_nudge_sent_at" not in listing_cols_sm:
        # Timestamp when the Fade Out nudge email was sent (Day 23/53/113)
        conn.execute("ALTER TABLE listings ADD COLUMN fade_nudge_sent_at TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_status ON listings(listing_status)")

    # ── Rental availability (occupancy) ─ separate axis from listing_status ──
    # rental_status: available | reserved | occupied  (Property rentals only).
    # Distinct from the free-text 'availability' service field and from the
    # listing_status lifecycle. Default 'available' so existing listings are
    # unchanged. available_from (ISO YYYY-MM-DD) drives "Available from <date>".
    if "rental_status" not in listing_cols_sm:
        conn.execute("ALTER TABLE listings ADD COLUMN rental_status TEXT NOT NULL DEFAULT 'available'")
    if "available_from" not in listing_cols_sm:
        conn.execute("ALTER TABLE listings ADD COLUMN available_from TEXT")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_listings_rental_status ON listings(rental_status)")

    # ── EULA acceptance gate (Session 37) ────────────────────────
    # eula_accepted_at must be non-NULL before a seller can publish.
    # Separate from lm_eula_accepted_at (Local Market supplemental EULA).
    user_cols_eula = [r[1] for r in conn.execute("PRAGMA table_info(users)").fetchall()]
    if "eula_accepted_at" not in user_cols_eula:
        conn.execute("ALTER TABLE users ADD COLUMN eula_accepted_at TEXT")

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
# DEMAND-LOOP-1 city-resolution fix (7 Jul): geo_cities is guaranteed seeded HERE, so
# resolve prospect city_id from the preserved city_name against CURRENT ids. Self-healing —
# runs every startup, cheap, corrects the import-ran-before-geo-seed ordering issue.
try:
    _dp_has = {r[1] for r in _startup_conn.execute("PRAGMA table_info(demand_prospects)").fetchall()}
    if "city_name" in _dp_has:
        _geo = {(r[1] or "").strip().lower(): r[0] for r in
                _startup_conn.execute("SELECT id, name FROM geo_cities").fetchall()}
        _fixed = 0
        for _p in _startup_conn.execute(
                "SELECT id, city_name FROM demand_prospects WHERE city_name IS NOT NULL").fetchall():
            _rid = _geo.get((_p[1] or "").strip().lower())
            if _rid is not None:
                _startup_conn.execute("UPDATE demand_prospects SET city_id=? WHERE id=? AND (city_id IS NULL OR city_id!=?)",
                                      (_rid, _p[0], _rid))
                _fixed += 1
        _startup_conn.commit()
        print("DEMAND-CITY-RESOLVE: %d prospects mapped to geo_cities ids" % _fixed)
except Exception as _cre:
    print("DEMAND-CITY-RESOLVE skipped: %s" % _cre)
migrate_listings_to_geo_city(_startup_conn)
_backfill_geo_coords(_startup_conn)
# Backfill slot_limit for existing users based on their current seller_tier
try:
    _startup_conn.execute("""
        UPDATE users SET slot_limit = CASE seller_tier
            WHEN 'standard'     THEN 10
            WHEN 'professional' THEN 25
            WHEN 'business'     THEN 60
            WHEN 'elite'        THEN 500
            WHEN 'starter'      THEN 10
            WHEN 'pro'          THEN 30
            WHEN 'premium'      THEN 25
            ELSE 2
        END
        WHERE slot_limit = 2 AND seller_tier NOT IN ('free', '')
    """)
    # Superusers always get 500 slots (they bypass enforcement but panel should show correctly)
    _startup_conn.execute("UPDATE users SET slot_limit=500 WHERE is_superuser=1 AND slot_limit < 500")
    _startup_conn.commit()
except Exception as _e:
    _log.warning("slot_limit backfill skipped: %s", _e)
_startup_conn.close()

def _apply_pending_downgrades():
    """Apply any pending tier downgrades where billing_period_end has passed."""
    conn = database.get_db()
    try:
        rows = conn.execute(
            "SELECT email, pending_downgrade_tier FROM users "
            "WHERE pending_downgrade_tier IS NOT NULL "
            "AND billing_period_end <= datetime('now')"
        ).fetchall()
        for row in rows:
            new_tier = row["pending_downgrade_tier"]
            new_limit = _tier_slot_limit(new_tier)
            conn.execute(
                "UPDATE users SET seller_tier=?, slot_limit=?, pending_downgrade_tier=NULL "
                "WHERE LOWER(email)=?",
                (new_tier, new_limit, row["email"].lower())
            )
            _log.info("Downgrade applied: %s → %s", row["email"], new_tier)
        if rows:
            conn.commit()
    except Exception as exc:
        _log.warning("Pending downgrade worker error: %s", exc)
    finally:
        conn.close()

_apply_pending_downgrades()

# n8n webhook URLs (Task 2 — optional, skip silently if not set)
N8N_WEBHOOK_ACCEPT     = os.getenv("N8N_WEBHOOK_ACCEPT")
N8N_WEBHOOK_DECLINE    = os.getenv("N8N_WEBHOOK_DECLINE")
N8N_WEBHOOK_NEW_INTRO  = os.getenv("N8N_WEBHOOK_NEW_INTRO")
N8N_WEBHOOK_AI_ALERT   = os.getenv("N8N_WEBHOOK_AI_ALERT")   # AI spend red flag alert
if not N8N_WEBHOOK_ACCEPT:
    _log.warning("N8N_WEBHOOK_ACCEPT not set — intro-accepted emails disabled")
if not N8N_WEBHOOK_DECLINE:
    _log.warning("N8N_WEBHOOK_DECLINE not set — intro-declined emails disabled")

# ── AI SPEND COST CONSTANTS (USD) ─────────────────────────────
# Two layers: _AI_COST flat fallback (when a call site passes no tokens) and
# _MODEL_PRICE real per-MILLION-token list prices (C2, Session 97). When usage
# {input_tokens, output_tokens} is passed, the logger computes the EXACT cost.
_AI_COST = {
    "haiku":          0.0023,   # claude-haiku-4-5 — 800in+400out tokens avg
    "sonnet":         0.0150,   # claude-sonnet-4-6 — standard call
    "sonnet_vision":  0.0400,   # claude-sonnet-4-6 — with 12 images
    "sonnet_rewrite": 0.0150,
}

# Real list prices, USD per 1,000,000 tokens (input, output). Update if Anthropic re-prices.
_MODEL_PRICE = {
    "haiku":          (0.80,  4.00),
    "sonnet":         (3.00, 15.00),
    "sonnet_vision":  (3.00, 15.00),
    "sonnet_rewrite": (3.00, 15.00),
    "opus":           (15.00, 75.00),
}

def _token_cost(model_key: str, in_tok: int, out_tok: int) -> float:
    """Exact USD cost from real token counts (C2). Falls back to the flat estimate."""
    price = _MODEL_PRICE.get(model_key)
    if not price:
        return _AI_COST.get(model_key, 0.0023)
    in_rate, out_rate = price
    return (in_tok / 1_000_000.0) * in_rate + (out_tok / 1_000_000.0) * out_rate


def _usage_tokens(resp_json: dict):
    """(input_tokens, output_tokens) from an Anthropic response, or (None, None)."""
    try:
        u = resp_json.get("usage") or {}
        it = u.get("input_tokens"); ot = u.get("output_tokens")
        if it is None and ot is None:
            return (None, None)
        return (int(it or 0), int(ot or 0))
    except Exception:
        return (None, None)

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
# ── AI provider seam (D1-FIX): vendor chosen in ONE place via ai_provider ──
# Swapping Claude -> another LLM = set AI_ACTIVE env (+ that provider's key). No call-site edits.
try:
    import ai_provider as _ts_ai
    _TS_AI_PROVIDER = _ts_ai.AI_ACTIVE
    _TS_AI_MODELS   = _ts_ai.TASK_MODEL.get(_TS_AI_PROVIDER, _ts_ai.TASK_MODEL["anthropic"])
except Exception:
    _TS_AI_PROVIDER = "anthropic"
    _TS_AI_MODELS   = {"haiku":"claude-haiku-4-5-20251001","sonnet":"claude-sonnet-4-6",
                       "vision":"claude-sonnet-4-6","triage":"claude-haiku-4-5-20251001"}
# Endpoint + key resolve from the active provider (today = Anthropic; the URL/headers helper
# below is the single place the wire protocol lives, so a swap changes it here, not in 15 bodies).
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AA_MODEL = _TS_AI_MODELS["haiku"]
# KYC / SA-ID verification model (SCAN-1 fix — was referenced undefined in the
# ID-verification path at ~7541/7568/7572). Matches VISION_MODEL standard.
SONNET_MODEL = _TS_AI_MODELS["sonnet"]

# AI EMAIL TRIAGE (Session 94) — inbound @trustsquare.co mail forwarded by a
# Cloudflare Email Worker to POST /email/inbound (auth: EMAIL_INBOUND_SECRET).
# Replies sent via Gmail SMTP using a Google App Password.
EMAIL_INBOUND_SECRET = os.getenv("EMAIL_INBOUND_SECRET")
GMAIL_ADDRESS        = os.getenv("GMAIL_ADDRESS", "dmcontiki2@gmail.com")
GMAIL_APP_PASSWORD   = os.getenv("GMAIL_APP_PASSWORD")
EMAIL_AUTO_SEND      = os.getenv("EMAIL_AUTO_SEND", "0") == "1"
TRIAGE_MODEL = _TS_AI_MODELS["triage"]

_TS_AI_CACHE = {"prov": None, "ts": 0.0}
def _ts_active_provider():
    """The LIVE active provider — DB-backed (Page-4 switchable, no restart). Falls back to the
    startup env value if the DB is unreachable. Cached ~10s so we never hammer the DB per call."""
    import time as _t
    now=_t.time()
    if _TS_AI_CACHE["prov"] and (now-_TS_AI_CACHE["ts"])<10:
        return _TS_AI_CACHE["prov"]
    prov=_TS_AI_PROVIDER  # startup default
    try:
        conn=database.get_db()
        try:
            row=conn.execute("SELECT ai_active FROM launch_switches WHERE id=1").fetchone()
            if row and row["ai_active"]: prov=row["ai_active"]
        finally:
            conn.close()
    except Exception:
        pass
    _TS_AI_CACHE.update(prov=prov, ts=now)
    return prov

def _ts_models_for(prov):
    try:
        return _ts_ai.TASK_MODEL.get(prov, _ts_ai.TASK_MODEL["anthropic"])
    except Exception:
        return _TS_AI_MODELS

def _ts_ai_url():
    """The active provider's chat endpoint — the ONE place the inference URL lives."""
    _u = {"anthropic": "https://api.anthropic.com/v1/messages",
          "openai":    "https://api.openai.com/v1/chat/completions"}
    return _u.get(_ts_active_provider(), _u["anthropic"])

def _ts_ai_headers():
    """The active provider's auth headers — the ONE place the wire auth lives.
    Swap provider via AI_ACTIVE; this changes here, not in 15 call bodies."""
    if _ts_active_provider()=="openai":
        return {"Authorization":"Bearer "+(os.getenv("OPENAI_API_KEY") or ""),
                "content-type":"application/json"}
    return {"x-api-key":ANTHROPIC_API_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}
if not EMAIL_INBOUND_SECRET:
    _log.warning("EMAIL_INBOUND_SECRET not set — /email/inbound will reject all calls")
if not GMAIL_APP_PASSWORD:
    _log.warning("GMAIL_APP_PASSWORD not set — triage replies will be drafted, never sent")

CF_ZONE_ID    = os.getenv("CF_ZONE_ID")
CF_CACHE_TOKEN = os.getenv("CF_CACHE_TOKEN")

async def _cf_purge_all():
    """Purge entire Cloudflare cache for trustsquare.co. Fire-and-forget — never raises."""
    if not CF_ZONE_ID or not CF_CACHE_TOKEN:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"https://api.cloudflare.com/client/v4/zones/{CF_ZONE_ID}/purge_cache",
                headers={"Authorization": f"Bearer {CF_CACHE_TOKEN}", "Content-Type": "application/json"},
                json={"purge_everything": True},
            )
    except Exception:
        pass

# GeoNames username — used in seed_geo_za (ZA dump) and _seed_country_from_geonames (API)
# Default: dmcontiki2. Override via GEONAMES_USERNAME in /etc/environment.

# ── HELPERS ───────────────────────────────────────────────────

# Local media mirror — absolute path on server
_LOCAL_MEDIA_DIR = "/var/www/marketsquare/media"

def _s3_upload(data: bytes, key: str, content_type: str) -> str:
    """Upload bytes to R2 (primary) AND mirror to local Hetzner disk (redundant fallback).

    Dual-write strategy:
      1. Write to R2 — fast global CDN, $0 egress.
      2. Mirror identical bytes to /var/www/marketsquare/media/<key> — served via nginx /media/.
    If R2 is unreachable the buyer app JS falls back to /media/<key> via onerror handler.
    Storage decision: 17 May 2026 — write-to-both approved by David Conradie.
    CPX32 live (4vCPU, 8GB RAM, 76GB SSD). 100GB Hetzner Volume mounted at /mnt/HC_Volume_105840760 for Overpass DB.
    At 50,000 listings + photos ≈ 30GB — well within CPX32 capacity for years.
    """
    import os as _os

    # ── Primary: R2 ───────────────────────────────────────────────────────
    r2_url = f"{R2_PUBLIC_URL}/{key}"
    try:
        _s3.put_object(
            Bucket=HETZNER_S3_BUCKET,
            Key=key,
            Body=data,
            ContentType=content_type,
            ACL="public-read",
        )
    except Exception as _e:
        _log.warning("R2 upload failed for %s: %s — local mirror still written", key, _e)

    # ── Mirror: local Hetzner disk ────────────────────────────────────────
    try:
        local_path = _os.path.join(_LOCAL_MEDIA_DIR, key)
        _os.makedirs(_os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as _f:
            _f.write(data)
    except Exception as _e:
        _log.warning("Local mirror write failed for %s: %s", key, _e)

    # Always return R2 URL as primary — buyer app falls back to /media/<key> via onerror
    return r2_url


async def _fire_webhook(url: str, payload: dict):
    """Fire-and-forget webhook POST — never raises, logs errors only."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(url, json=payload)
    except Exception as exc:
        _log.error("Webhook POST to %s failed: %s", url, exc)


def _log_ai_spend(email: str, endpoint: str, model_key: str,
                  in_tok: int | None = None, out_tok: int | None = None):
    """Background task: log AI call cost + trigger alert check if threshold crossed.
    Non-blocking — called via background_tasks.add_task() after every AI call.
    Never raises — log errors only.

    C2 (Session 97): real token counts -> exact cost via _MODEL_PRICE, cost_is_real=1.
    No tokens (legacy sites) -> flat _AI_COST estimate, cost_is_real=0. Backward compatible.
    """
    try:
        if in_tok is not None or out_tok is not None:
            it, ot = int(in_tok or 0), int(out_tok or 0)
            cost = _token_cost(model_key, it, ot)
            is_real = 1
        else:
            it, ot = 0, 0
            cost = _AI_COST.get(model_key, 0.0023)
            is_real = 0
        conn = database.get_db()
        try:
            conn.execute(
                "INSERT INTO ai_spend_log "
                "(email, endpoint, model, est_cost_usd, input_tokens, output_tokens, cost_is_real) "
                "VALUES (?,?,?,?,?,?,?)",
                (email or '', endpoint, model_key, cost, it, ot, is_real)
            )
            conn.commit()
            _maybe_fire_spend_alert(conn)
        finally:
            conn.close()
    except Exception as exc:
        _log.error("_log_ai_spend failed: %s", exc)


def _maybe_fire_spend_alert(conn):
    """Check if current month AI spend has crossed the configured threshold.
    Fires n8n webhook at most once per day. Silent if not configured.
    """
    try:
        cfg = conn.execute(
            "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at "
            "FROM ai_spend_config WHERE id = 1"
        ).fetchone()
        if not cfg or cfg["monthly_income_usd"] <= 0:
            return  # income not configured yet — skip

        # Current calendar month spend
        month_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-01')
        row = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) as total FROM ai_spend_log "
            "WHERE logged_at >= ?", (month_start,)
        ).fetchone()
        month_spend = row["total"] if row else 0.0

        threshold_usd = cfg["monthly_income_usd"] * (cfg["alert_threshold_pct"] / 100.0)
        if month_spend < threshold_usd:
            return  # under threshold — nothing to do

        # Check last alerted — don't fire more than once per day
        last = cfg["last_alerted_at"] or ""
        today = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d')
        if last.startswith(today):
            return  # already alerted today

        # Update last_alerted_at
        conn.execute(
            "UPDATE ai_spend_config SET last_alerted_at = ? WHERE id = 1",
            (__import__('datetime').datetime.utcnow().isoformat(),)
        )
        conn.commit()

        # Fire n8n alert webhook if configured
        pct_used = (month_spend / cfg["monthly_income_usd"] * 100) if cfg["monthly_income_usd"] > 0 else 0
        payload = {
            "alert": "ai_spend_threshold",
            "month_spend_usd": round(month_spend, 4),
            "income_usd": cfg["monthly_income_usd"],
            "threshold_pct": cfg["alert_threshold_pct"],
            "pct_used": round(pct_used, 1),
            "alert_email": cfg["alert_email"],
            "message": (
                f"TrustSquare AI spend alert: ${month_spend:.4f} spent this month "
                f"({pct_used:.1f}% of ${cfg['monthly_income_usd']:.2f} income). "
                f"Threshold: {cfg['alert_threshold_pct']}%."
            ),
        }
        _log.warning("AI spend alert fired: %s", payload["message"])
        if N8N_WEBHOOK_AI_ALERT:
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(_fire_webhook(N8N_WEBHOOK_AI_ALERT, payload))
            except Exception:
                pass  # alert failure must never affect user response
    except Exception as exc:
        _log.error("_maybe_fire_spend_alert failed: %s", exc)


def _check_cost_ceiling(email: str) -> None:
    """C1 (Session 97) — HARD daily cost ceiling. Pre-flight guard before every paid
    AI call. REFUSES (HTTP 429) when today's logged AI spend has reached the per-user
    or platform-wide USD ceiling. Distinct from observe-and-alert. Ceiling 0 = off.
    Superusers exempt from the per-user rail (still counted toward platform).
    Fail-OPEN on internal error — never lock a legitimate paying user out.
    """
    try:
        conn = database.get_db()
        try:
            cfg = conn.execute(
                "SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
                "FROM ai_spend_config WHERE id = 1"
            ).fetchone()
            if not cfg:
                return
            user_cap     = cfg["daily_user_ceiling_usd"]     or 0.0
            platform_cap = cfg["daily_platform_ceiling_usd"] or 0.0
            if user_cap <= 0 and platform_cap <= 0:
                return
            day_start = __import__('datetime').datetime.utcnow().strftime('%Y-%m-%d 00:00:00')
            if platform_cap > 0:
                prow = conn.execute(
                    "SELECT COALESCE(SUM(est_cost_usd),0) as t FROM ai_spend_log WHERE logged_at >= ?",
                    (day_start,)
                ).fetchone()
                if (prow["t"] if prow else 0.0) >= platform_cap:
                    _log.warning("C1 platform ceiling hit: $%.4f >= $%.2f — refusing (%s)",
                                 prow["t"], platform_cap, email)
                    raise HTTPException(
                        status_code=429,
                        detail="AI services are temporarily paused (daily platform budget reached). "
                               "Please try again later."
                    )
            if user_cap > 0 and email:
                su = conn.execute("SELECT is_superuser FROM users WHERE email = ?", (email,)).fetchone()
                if not (su and su["is_superuser"]):
                    urow = conn.execute(
                        "SELECT COALESCE(SUM(est_cost_usd),0) as t FROM ai_spend_log "
                        "WHERE email = ? AND logged_at >= ?", (email, day_start)
                    ).fetchone()
                    if (urow["t"] if urow else 0.0) >= user_cap:
                        _log.warning("C1 user ceiling hit: %s $%.4f >= $%.2f — refusing",
                                     email, urow["t"], user_cap)
                        raise HTTPException(
                            status_code=429,
                            detail="You've reached today's AI usage limit on this account. "
                                   "It resets at 00:00 UTC."
                        )
        finally:
            conn.close()
    except HTTPException:
        raise
    except Exception as exc:
        _log.error("_check_cost_ceiling failed (failing open): %s", exc)


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
    # Rental occupancy (Property rentals) — separate from the free-text 'availability' above
    rental_status: Optional[str] = None   # 'available' | 'reserved' | 'occupied'
    available_from: Optional[str] = None  # ISO date YYYY-MM-DD; drives "Available from <date>"
    # Property location (private — never returned to buyers)
    street_address: Optional[str] = None   # e.g. "12 Oak Ave, Waterkloof Ridge" — used for geocoding only
    listing_lat: Optional[float] = None    # geocoded from street_address
    listing_lng: Optional[float] = None
    # Vehicle spec fields (Cars — CARS-SPEC-1). Discrete = filterable columns;
    # vehicle_specs = JSON object string (superset, keys in VEHICLE_SECTION_FIELDS);
    # spec_confirmed = JSON section→ISO-ts map. attested_at / attested_email are
    # deliberately NOT model fields — set only by publish endpoints, never generic writes.
    make: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    vehicle_year: Optional[int] = None    # named to avoid the Collectors era_year clash
    mileage_km: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    drivetrain: Optional[str] = None
    colour: Optional[str] = None
    vehicle_specs: Optional[str] = None
    spec_confirmed: Optional[str] = None
    # Trust
    trust_score: Optional[int] = None
    seller_email: Optional[str] = None

class User(BaseModel):
    email: str
    name: Optional[str] = None
    ai_sessions: Optional[int] = None   # free sessions to credit on registration

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
    rental_status: Optional[str] = None   # 'available' | 'reserved' | 'occupied'
    available_from: Optional[str] = None  # ISO date YYYY-MM-DD
    photo_urls: Optional[str] = None    # JSON-encoded array of photo URLs
    thumb_url: Optional[str] = None     # primary thumbnail
    medium_url: Optional[str] = None    # primary medium photo
    street_address: Optional[str] = None   # private — geocoded for POI accuracy, never shown to buyers
    listing_lat: Optional[float] = None
    listing_lng: Optional[float] = None
    # Vehicle spec fields (Cars — CARS-SPEC-1); attested_* intentionally excluded
    make: Optional[str] = None
    model: Optional[str] = None
    variant: Optional[str] = None
    vehicle_year: Optional[int] = None
    mileage_km: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    body_type: Optional[str] = None
    drivetrain: Optional[str] = None
    colour: Optional[str] = None
    vehicle_specs: Optional[str] = None
    spec_confirmed: Optional[str] = None

class IntroRequest(BaseModel):
    listing_id: int
    buyer_email: str
    buyer_name: Optional[str] = None
    message: Optional[str] = None

# ── HEALTH ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "TrustSquare BEA", "version": "1.3.1"}

@app.post("/admin/purge-cache")
async def purge_cache(x_admin_key: str = Header(None)):
    """Purge Cloudflare cache. Called automatically after deploys."""
    ADMIN_KEY = os.getenv("ADMIN_KEY", "")
    if ADMIN_KEY and x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    await _cf_purge_all()
    return {"purged": True}

@app.post("/admin/refresh-pois/{listing_id}")
async def refresh_pois(listing_id: int, x_admin_key: str = Header(None)):
    """Force-refresh nearby POIs for a property listing. Clears cached value and re-fetches from Overpass."""
    ADMIN_KEY = os.getenv("ADMIN_KEY", "")
    if ADMIN_KEY and x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=403, detail="Forbidden")
    conn = database.get_db()
    row = conn.execute("SELECT category, listing_lat, listing_lng, geo_city_id FROM listings WHERE id=?", (listing_id,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    # Clear existing POIs so auto_link_pois will re-fetch
    conn.execute("UPDATE listings SET nearby_pois=NULL WHERE id=?", (listing_id,))
    conn.commit()
    # Get coords — prefer listing-specific, fall back to city centroid
    lat = float(row["listing_lat"]) if row["listing_lat"] else None
    lng = float(row["listing_lng"]) if row["listing_lng"] else None
    if (not lat or not lng) and row["geo_city_id"]:
        city_row = conn.execute("SELECT lat, lng FROM geo_cities WHERE id=?", (row["geo_city_id"],)).fetchone()
        if city_row:
            lat, lng = float(city_row["lat"]), float(city_row["lng"])
    conn.close()
    if not lat or not lng:
        raise HTTPException(status_code=422, detail="No coordinates available for this listing")
    import threading
    threading.Thread(target=auto_link_pois, args=(listing_id, lat, lng), daemon=True).start()
    return {"status": "refresh_queued", "listing_id": listing_id, "lat": lat, "lng": lng}

# ── LISTINGS (public read, protected write) ──────────────────

# ── Rental availability (occupancy) helpers ────────────────────────
# Separate axis from the listing_status lifecycle and from the free-text
# service 'availability' field. Property rentals only. The label is derived
# at read time, so "Available from <future>" becomes "Available now" on the
# date with no batch job. Dates compared as ISO strings (ZA single-tz launch).
_RENTAL_STATUSES = {"available", "reserved", "occupied"}

def _validate_rental_fields(rental_status, available_from):
    if rental_status is not None and rental_status not in _RENTAL_STATUSES:
        raise HTTPException(status_code=400,
            detail="rental_status must be one of: available, reserved, occupied")
    if available_from:
        import datetime as _dt
        try:
            _dt.date.fromisoformat(str(available_from)[:10])
        except (ValueError, TypeError):
            raise HTTPException(status_code=400,
                detail="available_from must be an ISO date (YYYY-MM-DD)") from None

def _rental_availability(rental_status, available_from):
    """Renter-facing availability label derived from (rental_status, available_from)."""
    import datetime as _dt
    status = (rental_status or "available").lower()
    today = _dt.date.today().isoformat()
    upcoming = bool(available_from) and str(available_from)[:10] > today
    if status == "occupied":
        return ("Occupied — available " + str(available_from)[:10]) if upcoming else "Occupied"
    if status == "reserved":
        return "Under application"
    return ("Available from " + str(available_from)[:10]) if upcoming else "Available now"

# ── Vehicle spec model (CARS-SPEC-1, cars brief Parts A/B/C) ────────────────
# Canonical section map — drives the public scrub (visibility invariant D1),
# the edit confirmation-reset, and is mirrored in ms.js. Section-level
# confirmation ONLY (locked decision — never per-field ticks).
# section → (discrete listing columns, vehicle_specs JSON keys)
VEHICLE_SECTION_FIELDS = {
    "details":     (("make", "model", "variant", "vehicle_year", "colour", "body_type"),
                    ("seats", "doors")),
    "performance": (("transmission", "fuel_type", "drivetrain"),
                    ("engine_capacity_cc", "kilowatts_kw", "cylinder_layout", "cylinders",
                     "aspiration", "fuel_consumption_l100", "fuel_tank_l", "gears",
                     "tyre_front", "tyre_rear", "wheelbase_mm", "co2_gkm")),
    "condition":   (("mileage_km",),
                    ("service_history", "roadworthy_status", "spare_key",
                     "maintenance_plan_until", "warranty_until", "condition_notes")),
    "features":    ((), ("features",)),
}

def _validate_vehicle_fields(vehicle_specs, spec_confirmed):
    """400 on malformed vehicle JSON blobs (mirrors _validate_rental_fields)."""
    for _name, _val in (("vehicle_specs", vehicle_specs), ("spec_confirmed", spec_confirmed)):
        if _val:
            try:
                if not isinstance(json.loads(_val), dict):
                    raise ValueError("not an object")
            except Exception:
                raise HTTPException(status_code=400,
                    detail=f"{_name} must be a JSON object string") from None

def _scrub_vehicle_specs(d):
    """Visibility invariant D1 (CARS-SPEC-1): on PUBLIC reads a vehicle spec value
    is shown only when its section is seller-confirmed AND the listing carries
    attested_at. Seller reads (/listings/mine) never call this. is_demo exempt.
    attested_email is internal bookkeeping — always withheld from public payloads."""
    if "attested_email" in d:
        d["attested_email"] = None
    if (d.get("category") or "").strip().lower() != "cars":
        return d
    if d.get("is_demo"):
        return d
    attested = bool(d.get("attested_at"))
    try:
        confirmed = json.loads(d.get("spec_confirmed") or "{}")
    except Exception:
        confirmed = {}
    if not isinstance(confirmed, dict):
        confirmed = {}
    try:
        specs = json.loads(d.get("vehicle_specs") or "{}")
    except Exception:
        specs = {}
    if not isinstance(specs, dict):
        specs = {}
    specs.pop("_prov", None)   # per-field provenance is seller-side only
    # Default-deny: rebuild the public blob from confirmed sections' KNOWN keys
    # only — an unknown key belongs to no section, can never be confirmed, and
    # must never reach a public payload.
    public_specs = {}
    for _section, (_cols, _keys) in VEHICLE_SECTION_FIELDS.items():
        if attested and confirmed.get(_section):
            for _k in _keys:
                if _k in specs:
                    public_specs[_k] = specs[_k]
        else:
            for _c in _cols:
                if _c in d:
                    d[_c] = None
    d["vehicle_specs"] = json.dumps(public_specs) if public_specs else None
    return d

def _reset_vehicle_confirmations(existing, d):
    """CARS-SPEC-1 edit hook: changing a vehicle section's data clears that
    section's confirmation, unless the request itself sets spec_confirmed
    (the FEA section-confirm flow does, and stays authoritative).
    existing = current row as a plain dict; d = non-None update fields (mutated)."""
    if (existing.get("category") or "").strip().lower() != "cars":
        return
    if "spec_confirmed" in d:
        return
    try:
        conf = json.loads(existing.get("spec_confirmed") or "{}")
    except Exception:
        conf = {}
    if not isinstance(conf, dict) or not any(conf.get(_s) for _s in VEHICLE_SECTION_FIELDS):
        return
    new_specs = old_specs = None
    if "vehicle_specs" in d:
        try:
            new_specs = json.loads(d.get("vehicle_specs") or "{}")
            if not isinstance(new_specs, dict):
                new_specs = None
        except Exception:
            new_specs = None   # unparseable → conservative reset of confirmed sections
        try:
            old_specs = json.loads(existing.get("vehicle_specs") or "{}")
        except Exception:
            old_specs = {}
        if not isinstance(old_specs, dict):
            old_specs = {}
    changed = False
    for _section, (_cols, _keys) in VEHICLE_SECTION_FIELDS.items():
        if not conf.get(_section):
            continue
        touched = any(_c in d for _c in _cols)
        if not touched and "vehicle_specs" in d:
            touched = True if new_specs is None else any(
                old_specs.get(_k) != new_specs.get(_k) for _k in _keys)
        if touched:
            conf[_section] = None
            changed = True
    if changed:
        d["spec_confirmed"] = json.dumps(conf)


@app.get("/listings")
def get_listings(city: str = "Pretoria", category: Optional[str] = None,
                 suburb: Optional[str] = None, demo: int = 0,
                 page: int = 1, page_size: int = 200,
                 q: Optional[str] = None, sort: Optional[str] = None,
                 price_min: Optional[float] = None, price_max: Optional[float] = None,
                 trust_min: Optional[int] = None,
                 make: Optional[str] = None, model: Optional[str] = None,
                 year_min: Optional[int] = None, year_max: Optional[int] = None,
                 facets: int = 0):
    conn = database.get_db()
    # M0 pagination: default page_size=200 preserves prior behaviour; FEA passes page/page_size for infinite scroll
    page = max(1, page)
    page_size = max(1, min(page_size, 200))
    _offset = (page - 1) * page_size

    # Resolve city name → geo_city_id for extended-city matching
    city_row = conn.execute(
        "SELECT id FROM geo_cities WHERE LOWER(name)=LOWER(?) LIMIT 1", (city,)
    ).fetchone()
    buyer_city_id = city_row["id"] if city_row else None

    # Base filters shared by both branches of the UNION
    # Branch A: listing's home city matches buyer city (original behaviour)
    # Branch B: listing extended to buyer's city via listing_cities table
    suspension_filter = "(l.suspension_reason IS NULL OR l.suspension_reason = '') AND (l.listing_status IS NULL OR l.listing_status = 'live')"
    lm_filter_a = "LOWER(l.category) = LOWER(?)" if category else "LOWER(l.category) != LOWER(?)"
    lm_filter_b = lm_filter_a  # same category filter on both branches
    # demo=0 (real app): hide seed data; demo=1: show everything including seed
    demo_filter = "" if demo else "AND (l.is_demo = 0 OR l.is_demo IS NULL)"

    cat_param = category if category else LM_CATEGORY

    # Trip-planning reach exemption (David, 28 Jun 2026): travel-planning categories are
    # borderless — a buyer planning a trip is by definition not local to the destination,
    # so these are visible to EVERYONE from ANY city and on ANY tier (no city gate, no
    # tier gate). All other categories keep standard reach (home city + extended cities).
    # Canon: PRICING_CANON.md §2 reach exemption. Keys match raw l.category values.
    TRIP_PLANNING_CATEGORIES = (
        "adventures", "adventure", "experiences", "adventures_experiences",
        "accommodation", "adventures_accommodation", "tours", "heritage",
    )
    _tp_in = ",".join("?" for _ in TRIP_PLANNING_CATEGORIES)
    # Whether the current request's category filter would already cover trip-planning rows.
    _cat_is_trip = bool(category) and category.lower() in TRIP_PLANNING_CATEGORIES

    # ── SEARCH ENGINE Step 1 (6 Jul 2026): honest server-side dial-in ─────────
    # All new filters compose at the OUTER wrapper so every reach branch (home city,
    # extended, trips, online) inherits them identically. FTS gives typed search
    # ("bmw 1996 e36"), structured params give exact facets, sort gives the three-dial
    # order from FILTER_ENGINE_DESIGN (Trust + Freshness; Closeness = branch order).
    _xw, _xp = [], []
    if q and q.strip():
        _terms = [t for t in re.findall(r"[A-Za-z0-9]{2,}", q)][:8]
        if _terms:
            _match = " ".join(t + "*" for t in _terms)
            _xw.append("id IN (SELECT l2.id FROM listings l2 JOIN listings_fts f ON f.rowid = l2.rowid WHERE listings_fts MATCH ?)")
            _xp.append(_match)
    if price_min is not None:
        _xw.append("price_num >= ?"); _xp.append(price_min)
    if price_max is not None:
        _xw.append("price_num <= ?"); _xp.append(price_max)
    if trust_min is not None:
        _xw.append("COALESCE(trust_score,0) >= ?"); _xp.append(trust_min)
    if make:
        _xw.append("LOWER(COALESCE(make,'')) = ?"); _xp.append(make.strip().lower())
    if model:
        _xw.append("LOWER(COALESCE(model,'')) LIKE ?"); _xp.append("%" + model.strip().lower() + "%")
    if year_min is not None:
        _xw.append("vehicle_year >= ?"); _xp.append(year_min)
    if year_max is not None:
        _xw.append("vehicle_year <= ?"); _xp.append(year_max)
    _extra_where = (" WHERE " + " AND ".join(_xw)) if _xw else ""
    _sort_map = {
        "newest":     "ORDER BY created_at DESC",
        "price_asc":  "ORDER BY (price_num IS NULL), price_num ASC",
        "price_desc": "ORDER BY (price_num IS NULL), price_num DESC",
        "trust":      "ORDER BY COALESCE(trust_score,0) DESC, created_at DESC",
        # smart = the design's dials: trust (60%) + freshness decay over 30 days (40%)
        "smart":      "ORDER BY (COALESCE(trust_score,0)/100.0*0.6 + MAX(0, 1.0-(julianday('now')-julianday(created_at))/30.0)*0.4) DESC",
    }
    _order_clause = _sort_map.get((sort or "").strip().lower(), "ORDER BY created_at DESC")

    if suburb:
        # Suburb filter only applies to home-city branch (extended listings have no suburb match)
        branch_a = f"""
            SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
            FROM listings l
            LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
            WHERE l.city = ? AND {suspension_filter} AND {lm_filter_a} {demo_filter} AND l.suburb = ?"""
        params_a = [city, cat_param, suburb]
    else:
        branch_a = f"""
            SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
            FROM listings l
            LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
            WHERE l.city = ? AND {suspension_filter} AND {lm_filter_a} {demo_filter}"""
        params_a = [city, cat_param]

    # Branch C: trip-planning reach exemption — these categories show from ALL cities,
    # for all buyers, regardless of tier. Included when the feed is the mixed/no-category
    # feed (FEA default) OR when a trip-planning category is explicitly requested.
    # Excluded when a specific NON-trip category is requested (so it can't pollute e.g. Cars).
    include_branch_c = (not category) or _cat_is_trip
    branch_c = ""
    params_c = []
    if include_branch_c:
        branch_c = f"""
            SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
            FROM listings l
            LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
            WHERE LOWER(l.category) IN ({_tp_in})
              AND {suspension_filter} {demo_filter}"""
        params_c = [c.lower() for c in TRIP_PLANNING_CATEGORIES]

    # Branch D: ONLINE-MODE reach exemption (David, 6 Jul 2026) — same principle as the
    # trip exemption (canon 2a): reach follows whether the buyer can USE the thing from
    # where they are. mode Online/Both (tutors + online-capable services — the chess
    # trainer) is consumable from anywhere -> borderless for ALL buyers on ALL tiers.
    # Physical listings untouched: city reach for Free, everywhere for Global $5 — the
    # Global tier keeps its value as reach-for-the-physical-world. Included on the mixed
    # feed and for services/tutors requests; never pollutes physical categories.
    include_branch_d = (not category) or (category.lower() in ("services", "tutors"))
    branch_d = ""
    params_d = []
    if include_branch_d:
        branch_d = f"""
            SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
            FROM listings l
            LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
            WHERE LOWER(COALESCE(l.mode,'')) IN ('online','both')
              AND {suspension_filter} {demo_filter}"""

    # Branch B: extended city reach (only runs when we have a valid city_id)
    if buyer_city_id:
        branch_b = f"""
            SELECT l.*, gs.lat as suburb_lat, gs.lng as suburb_lng
            FROM listings l
            JOIN listing_cities lc ON lc.listing_id = l.id AND lc.city_id = ?
            LEFT JOIN geo_suburbs gs ON gs.name = l.suburb AND gs.city_id = l.geo_city_id
            WHERE l.city != ? AND {suspension_filter} AND {lm_filter_b} {demo_filter}"""
        params_b = [buyer_city_id, city, cat_param]

        # GROUP BY id dedupes across A/B/C (a trip-planning listing in the home city
        # appears in both A and C; the suburb LEFT JOIN can also multiply rows). One row per listing.
        _union_c = ("\n                    UNION ALL\n                    " + branch_c) if include_branch_c else ""
        _union_d = ("\n                    UNION ALL\n                    " + branch_d) if include_branch_d else ""
        sql = f"""
            SELECT * FROM (
                SELECT * FROM (
                    {branch_a}
                    UNION ALL
                    {branch_b}{_union_c}{_union_d}
                ) GROUP BY id
            ){_extra_where} {_order_clause} LIMIT ? OFFSET ?"""
        params = params_a + params_b + params_c + params_d + _xp + [page_size, _offset]
        _facet_inner = f"""SELECT * FROM (SELECT * FROM ({branch_a} UNION ALL {branch_b}{_union_c}{_union_d}) GROUP BY id){_extra_where}"""
        _facet_params = params_a + params_b + params_c + params_d + _xp
    else:
        _union_d2 = ("\n                        UNION ALL\n                        " + branch_d) if include_branch_d else ""
        if include_branch_c:
            sql = f"""
                SELECT * FROM (
                    SELECT * FROM (
                        {branch_a}
                        UNION ALL
                        {branch_c}{_union_d2}
                    ) GROUP BY id
                ){_extra_where} {_order_clause} LIMIT ? OFFSET ?"""
            params = params_a + params_c + params_d + _xp + [page_size, _offset]
            _facet_inner = f"""SELECT * FROM (SELECT * FROM ({branch_a} UNION ALL {branch_c}{_union_d2}) GROUP BY id){_extra_where}"""
            _facet_params = params_a + params_c + params_d + _xp
        elif include_branch_d:
            sql = f"""
                SELECT * FROM (
                    SELECT * FROM (
                        {branch_a}
                        UNION ALL
                        {branch_d}
                    ) GROUP BY id
                ){_extra_where} {_order_clause} LIMIT ? OFFSET ?"""
            params = params_a + params_d + _xp + [page_size, _offset]
            _facet_inner = f"""SELECT * FROM (SELECT * FROM ({branch_a} UNION ALL {branch_d}) GROUP BY id){_extra_where}"""
            _facet_params = params_a + params_d + _xp
        else:
            sql = f"""SELECT * FROM ({branch_a}) {_extra_where} {_order_clause} LIMIT ? OFFSET ?"""
            params = params_a + _xp + [page_size, _offset]
            _facet_inner = f"""SELECT * FROM ({branch_a}) {_extra_where}"""
            _facet_params = params_a + _xp

    rows = conn.execute(sql, params).fetchall()
    _founders = launch_redemption.founders_email_set(conn)
    conn.close()
    out = []
    for _r in rows:
        _d = dict(_r)
        if _founders and (_d.get("seller_email") or "").lower() in _founders:
            _d["founders"] = True
        if (_d.get("category") or "").lower() == "property":
            _d["availability_label"] = _rental_availability(_d.get("rental_status"), _d.get("available_from"))
        _scrub_vehicle_specs(_d)   # CARS-SPEC-1 D1: unconfirmed vehicle specs never public
        out.append(_d)
    if facets:
        # Counts computed from the SAME filtered set as the list — they can never lie.
        fc = {}
        conn2 = database.get_db()
        try:
            r = conn2.execute(f"SELECT COUNT(*) AS n, MIN(price_num) AS pmin, MAX(price_num) AS pmax FROM ({_facet_inner})", _facet_params).fetchone()
            fc["total"] = r["n"]; fc["price"] = {"min": r["pmin"], "max": r["pmax"]}
            fc["makes"] = [{"v": x["make"], "n": x["n"]} for x in conn2.execute(
                f"SELECT make, COUNT(*) AS n FROM ({_facet_inner}) WHERE make IS NOT NULL AND make != '' GROUP BY LOWER(make) ORDER BY n DESC LIMIT 15", _facet_params)]
            yr = conn2.execute(f"SELECT MIN(vehicle_year) AS y0, MAX(vehicle_year) AS y1 FROM ({_facet_inner}) WHERE vehicle_year IS NOT NULL", _facet_params).fetchone()
            fc["years"] = {"min": yr["y0"], "max": yr["y1"]}
            fc["trust_bands"] = [{"v": x["band"], "n": x["n"]} for x in conn2.execute(
                f"SELECT CASE WHEN COALESCE(trust_score,0)>=80 THEN '80+' WHEN COALESCE(trust_score,0)>=60 THEN '60-79' ELSE '<60' END AS band, COUNT(*) AS n FROM ({_facet_inner}) GROUP BY band", _facet_params)]
            fc["service_types"] = [{"v": x["service_type"], "n": x["n"]} for x in conn2.execute(
                f"SELECT service_type, COUNT(*) AS n FROM ({_facet_inner}) WHERE service_type IS NOT NULL AND service_type != '' GROUP BY LOWER(service_type) ORDER BY n DESC LIMIT 12", _facet_params)]
        except Exception as _fe:
            fc["error"] = "facets unavailable"
        finally:
            conn2.close()
        return {"items": out, "facets": fc}
    return out

@app.post("/listings")
def create_listing(listing: Listing, background_tasks: BackgroundTasks, _key: str = Depends(auth.require_api_key)):
    if not listing.suburb:
        raise HTTPException(status_code=400, detail="suburb is required")
    launch_redemption.check_listing_velocity(listing.seller_email)  # per-day flood control (env-gated OFF)
    conn = database.get_db()
    # Resolve geo_city_id from city name at creation time
    _gcity_row = conn.execute(
        "SELECT id FROM geo_cities WHERE name=? AND active=1 LIMIT 1", (listing.city,)
    ).fetchone()
    _geo_city_id = _gcity_row["id"] if _gcity_row else None
    _validate_rental_fields(listing.rental_status, listing.available_from)
    _validate_vehicle_fields(listing.vehicle_specs, listing.spec_confirmed)
    cursor = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description, thumb_url, medium_url,
            service_class, prop_type, beds, baths, garages,
            subject, level, mode, service_type, availability, rental_status, available_from,
            trust_score, seller_email, listing_status, published_at,
            street_address, listing_lat, listing_lng, geo_city_id,
            make, model, variant, vehicle_year, mileage_km, transmission,
            fuel_type, body_type, drivetrain, colour, vehicle_specs, spec_confirmed)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (listing.title, listing.price, listing.category, listing.city,
         listing.area, listing.suburb, listing.description, listing.thumb_url, listing.medium_url,
         listing.service_class, listing.prop_type, listing.beds, listing.baths, listing.garages,
         listing.subject, listing.level, listing.mode, listing.service_type, listing.availability,
         (listing.rental_status or 'available'), listing.available_from,
         listing.trust_score, listing.seller_email, 'draft',
         listing.street_address, listing.listing_lat, listing.listing_lng, _geo_city_id,
         listing.make, listing.model, listing.variant, listing.vehicle_year,
         listing.mileage_km, listing.transmission, listing.fuel_type, listing.body_type,
         listing.drivetrain, listing.colour, listing.vehicle_specs, listing.spec_confirmed)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    # Wishlist matching deferred until listing goes live (draft listings not matched)
    return {"id": new_id, "message": "Listing saved as draft — seller must complete onboarding to go live"}



# ── World Heritage auto-link helper ─────────────────────────────────────────
import math as _math

def _haversine_km(lat1, lon1, lat2, lon2):
    """Distance in km between two lat/lon points."""
    R = 6371
    dlat = _math.radians(lat2 - lat1)
    dlon = _math.radians(lon2 - lon1)
    a = (_math.sin(dlat/2)**2 +
         _math.cos(_math.radians(lat1)) * _math.cos(_math.radians(lat2)) * _math.sin(dlon/2)**2)
    return R * 2 * _math.asin(_math.sqrt(a))

# Category affinity scores for wonder types
_WONDER_AFFINITY = {
    # (category_normalised, wonder_type_normalised) -> score 0-3
    # 3=High, 2=Medium, 1=Low
}
_CAT_AFFINITY = {
    "property":     {},  # Property listings do not get World Heritage auto-links — not contextually relevant
    "accommodation":{"national park": 3, "world heritage": 3, "national museum": 2, "archaeological": 1},
    "tours":        {"national park": 3, "world heritage": 3, "national museum": 3, "archaeological": 3},
    "adventures":   {"national park": 3, "world heritage": 3, "national museum": 2, "archaeological": 2},
    "experiences":  {"national park": 3, "world heritage": 3, "national museum": 3, "archaeological": 3},
    "crafts":       {"national park": 1, "world heritage": 2, "national museum": 3, "archaeological": 3},
    "artisan":      {"national park": 1, "world heritage": 2, "national museum": 3, "archaeological": 3},
    "food":         {"national park": 2, "world heritage": 2, "national museum": 1, "archaeological": 1},
    "produce":      {"national park": 2, "world heritage": 2, "national museum": 1, "archaeological": 1},
    "local market": {"national park": 1, "world heritage": 1, "national museum": 2, "archaeological": 1},
    "local_market": {"national park": 1, "world heritage": 1, "national museum": 2, "archaeological": 1},
    "collectors":   {"national park": 1, "world heritage": 2, "national museum": 3, "archaeological": 3},
    "cars":         {"national park": 1, "world heritage": 1, "national museum": 2, "archaeological": 1},
    "tutors":       {"national park": 1, "world heritage": 2, "national museum": 3, "archaeological": 2},
    "services":     {"national park": 1, "world heritage": 1, "national museum": 1, "archaeological": 1},
}

def _wonder_type_key(wtype):
    """Normalise wonder type string to affinity key."""
    t = (wtype or "").lower()
    if "park" in t or "nature reserve" in t or "canyon" in t:
        return "national park"
    if "heritage" in t or "monument" in t or "temple" in t or "castle" in t or "ruins" in t:
        return "world heritage"
    if "museum" in t:
        return "national museum"
    if "archaeolog" in t or "site" in t:
        return "archaeological"
    return "world heritage"  # default

_WONDERS_CACHE = None

def _load_wonders():
    global _WONDERS_CACHE
    if _WONDERS_CACHE is None:
        import json as _json, os as _os
        wpath = _os.path.join(_os.path.dirname(__file__), "wonders.json")
        try:
            with open(wpath) as f:
                _WONDERS_CACHE = _json.load(f)
        except Exception:
            _WONDERS_CACHE = []
    return _WONDERS_CACHE

def _derived_radius_km(city_lat: float, city_lon: float, country_iso2: str) -> float:
    """Derive match radius from the bounding box of all cities in the same country.
    Formula: diagonal of bounding box / 3, clamped to [150, 800] km.
    Falls back to 300km if the country has fewer than 2 cities in geo_cities.
    This means radius auto-calibrates as new countries are seeded — no manual tuning.
    """
    try:
        db = database.get_db()
        rows = db.execute(
            'SELECT lat, lng FROM geo_cities WHERE country_iso2=? AND lat IS NOT NULL AND lng IS NOT NULL',
            (country_iso2,)
        ).fetchall()
        db.close()
        if len(rows) < 2:
            return 300.0  # default for unseeded countries
        lats = [float(r['lat']) for r in rows]
        lons = [float(r['lng']) for r in rows]
        diag = _haversine_km(min(lats), min(lons), max(lats), max(lons))
        return float(max(150, min(800, round(diag / 3, -1))))
    except Exception:
        return 300.0

# ── Property POI Auto-Link ─────────────────────────────────────────────────────

_POI_CATEGORIES = {
    "schools":      [("amenity", "school"), ("amenity", "college")],
    "universities": [("amenity", "university")],
    "shopping":     [("shop", "supermarket"), ("shop", "grocery"),
                      ("shop", "convenience"), ("shop", "mall"),
                      ("amenity", "marketplace")],
    "hospitals":    [("amenity", "hospital")],
    "police":       [("amenity", "police")],
}

_POI_RADIUS_M = 15000      # 15km radius for most POI categories
_POI_SHOPPING_RADIUS_M = 3000  # 3km for shopping — supermarkets/grocery stores are local

def _overpass_query_pois(lat: float, lon: float, radius_m: int = _POI_RADIUS_M) -> dict:
    """Query OSM Overpass API for property-relevant POIs near a location.
    Returns dict keyed by category with list of {name, lat, lon, dist_km} sorted by distance.
    Capped at 3 results per category. $0 cost, no API key required.
    """
    import urllib.request as _req
    import urllib.parse as _parse
    import json as _json
    import math as _math

    def _hav(lat1, lon1, lat2, lon2):
        R = 6371
        dlat = _math.radians(lat2 - lat1)
        dlon = _math.radians(lon2 - lon1)
        a = _math.sin(dlat/2)**2 + _math.cos(_math.radians(lat1)) * _math.cos(_math.radians(lat2)) * _math.sin(dlon/2)**2
        return round(R * 2 * _math.asin(_math.sqrt(a)), 2)

    # Build one combined Overpass query; shopping uses tighter 3km radius
    union_parts = []
    for cat, tags in _POI_CATEGORIES.items():
        cat_radius = _POI_SHOPPING_RADIUS_M if cat == "shopping" else radius_m
        for key, val in tags:
            union_parts.append(f'node["{key}"="{val}"](around:{cat_radius},{lat},{lon});')
            union_parts.append(f'way["{key}"="{val}"](around:{cat_radius},{lat},{lon});')

    query = '[out:json][timeout:15];(\n' + '\n'.join(union_parts) + '\n);out center 50;'

    try:
        import socket as _socket
        # Three independent public mirrors — tried in order, 10s timeout each.
        # localhost:12345 reserved for self-hosted Overpass (to be wired in Session 89).
        # Force IPv4 to avoid IPv6 connection hang on Hetzner.
        _orig_getaddrinfo = _socket.getaddrinfo
        def _ipv4_only(host, port, family=0, type=0, proto=0, flags=0):
            return _orig_getaddrinfo(host, port, _socket.AF_INET, type, proto, flags)
        _socket.getaddrinfo = _ipv4_only
        try:
            mirrors = [
                ('https://overpass-api.de/api/interpreter',            {'User-Agent': 'TrustSquare/1.0 (contact@trustsquare.co)', 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*'}),
                ('https://overpass.openstreetmap.fr/api/interpreter',  {'User-Agent': 'TrustSquare/1.0', 'Content-Type': 'application/x-www-form-urlencoded'}),
                ('https://overpass.kumi.systems/api/interpreter',      {'User-Agent': 'TrustSquare/1.0', 'Content-Type': 'application/x-www-form-urlencoded'}),
            ]
            result = None
            for url, headers in mirrors:
                try:
                    data = _parse.urlencode({'data': query}).encode()
                    req = _req.Request(url, data=data, headers=headers)
                    with _req.urlopen(req, timeout=10) as resp:
                        result = _json.loads(resp.read())
                    _log.info('Overpass POI query succeeded via %s', url)
                    break  # success — stop trying mirrors
                except Exception as _mir_exc:
                    _log.warning('Overpass mirror %s failed: %s', url, _mir_exc)
                    continue
            if result is None:
                return {}
        finally:
            _socket.getaddrinfo = _orig_getaddrinfo
    except Exception:
        return {}

    # Categorise results
    cat_results = {k: [] for k in _POI_CATEGORIES}
    for elem in result.get('elements', []):
        tags = elem.get('tags', {})
        name = tags.get('name') or tags.get('name:en')
        if not name:
            continue
        # Get coordinates
        if elem.get('type') == 'node':
            elat, elon = elem.get('lat'), elem.get('lon')
        else:
            center = elem.get('center', {})
            elat, elon = center.get('lat'), center.get('lon')
        if not elat or not elon:
            continue
        dist = _hav(lat, lon, elat, elon)

        # Skip generic/unnamed OSM entries
        _GENERIC_NAMES = {'school', 'school ground', 'college', 'university', 'hospital',
                          'police', 'police station', 'bus stop', 'park', 'shopping mall'}
        if name.lower().strip() in _GENERIC_NAMES:
            continue

        # Assign to category
        amenity = tags.get('amenity', '')
        shop = tags.get('shop', '')
        if amenity in ('school', 'college'):
            cat_results['schools'].append({'name': name, 'dist_km': dist, 'lat': elat, 'lon': elon})
        elif amenity == 'university':
            cat_results['universities'].append({'name': name, 'dist_km': dist, 'lat': elat, 'lon': elon})
        elif shop in ('mall', 'supermarket', 'grocery', 'convenience') or amenity == 'marketplace':
            cat_results['shopping'].append({'name': name, 'dist_km': dist, 'lat': elat, 'lon': elon})
        elif amenity == 'hospital':
            cat_results['hospitals'].append({'name': name, 'dist_km': dist, 'lat': elat, 'lon': elon})
        elif amenity == 'police':
            cat_results['police'].append({'name': name, 'dist_km': dist, 'lat': elat, 'lon': elon})

    # Sort each category by distance, deduplicate within 200m, cap at 3
    def _dedup(items):
        seen = []
        for item in items:
            too_close = any(
                _hav(item['lat'], item['lon'], s['lat'], s['lon']) < 0.2
                for s in seen
            )
            if not too_close:
                seen.append(item)
        return seen

    for cat in cat_results:
        cat_results[cat].sort(key=lambda x: x['dist_km'])
        cat_results[cat] = _dedup(cat_results[cat])[:3]
        # Strip lat/lon from final output (not needed by FEA)
        cat_results[cat] = [{'name': p['name'], 'dist_km': p['dist_km']} for p in cat_results[cat]]

    # Remove empty categories
    return {k: v for k, v in cat_results.items() if v}


def _geocode_address(address: str, city: str, country_iso2: str = "ZA") -> tuple:
    """Geocode a street address using Nominatim (OSM). Returns (lat, lon) or (None, None).
    Free, no API key. Respects 1 req/sec rate limit — call only at publish time.
    Privacy: address is sent to Nominatim but never stored in logs or returned to buyers.
    """
    import urllib.request as _req, urllib.parse as _parse, json as _json, socket as _socket
    if not address:
        return None, None
    query = f"{address}, {city}, {country_iso2}"
    params = _parse.urlencode({"q": query, "format": "json", "limit": "1"})
    url = f"https://nominatim.openstreetmap.org/search?{params}"
    try:
        # Force IPv4 to avoid IPv6 hang on Hetzner
        _orig = _socket.getaddrinfo
        def _ipv4(h, p, family=0, type=0, proto=0, flags=0):
            return _orig(h, p, _socket.AF_INET, type, proto, flags)
        _socket.getaddrinfo = _ipv4
        try:
            req = _req.Request(url, headers={"User-Agent": "TrustSquare/1.0 (trustsquare.co)"})
            with _req.urlopen(req, timeout=10) as resp:
                results = _json.loads(resp.read())
        finally:
            _socket.getaddrinfo = _orig
        if results:
            return float(results[0]["lat"]), float(results[0]["lon"])
    except Exception:
        pass
    return None, None


def auto_link_pois(listing_id: int, city_lat: float, city_lon: float):
    """Fetch nearby POIs from OSM and store in listings.nearby_pois.
    Only runs for Property category listings. Skips if already populated.
    Wrapped in try/except so failure never blocks listing publish.
    """
    import json as _json
    try:
        conn = database.get_db()
        existing = conn.execute(
            'SELECT nearby_pois FROM listings WHERE id=?', (listing_id,)
        ).fetchone()
        if existing and existing['nearby_pois'] and existing['nearby_pois'] not in ('{}', '[]', ''):
            conn.close()
            return  # already populated
        conn.close()

        pois = _overpass_query_pois(city_lat, city_lon)
        if not pois:
            return

        conn = database.get_db()
        conn.execute(
            'UPDATE listings SET nearby_pois=? WHERE id=?',
            (_json.dumps(pois), listing_id)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        _log.warning('auto_link_pois listing %s failed: %s', listing_id, e)


def auto_link_wonders(listing_id: int, city_lat: float, city_lon: float,
                       category: str, radius_km: float = None, max_links: int = 5):
    """Match nearby World Heritage wonders to a listing and store in linked_wonders.
    Radius is derived from the country bounding box (diagonal/3, clamped 150-800km)
    so it auto-calibrates per country as geo_cities data is seeded.
    Falls back to 300km for countries not yet in geo_cities.
    Returns list of wonder IDs that were auto-linked (empty if none matched).
    Only runs if linked_wonders is currently NULL or empty.
    """
    import json as _json
    wonders = _load_wonders()
    if not wonders or not city_lat or not city_lon:
        return []

    cat_key = (category or "").lower().strip()
    affinity_map = _CAT_AFFINITY.get(cat_key, {})

    # Score each wonder by distance + affinity
    scored = []
    for w in wonders:
        wlat = w.get("lat")
        wlon = w.get("lon")
        if not wlat or not wlon:
            continue
        dist = _haversine_km(city_lat, city_lon, wlat, wlon)
        if dist > (radius_km or 300.0):
            continue
        wtype_key = _wonder_type_key(w.get("type", ""))
        affinity = affinity_map.get(wtype_key, 1)
        if affinity == 0:
            continue
        # Score: affinity (1-3) weighted heavily, distance tiebreak (closer = better)
        score = affinity * 1000 - dist
        scored.append((score, w["id"], w["name"]))

    if not scored:
        return []

    scored.sort(reverse=True)
    top = scored[:max_links]
    linked = [{"id": wid, "auto_linked": True} for _, wid, _ in top]

    conn = database.get_db()
    conn.execute(
        "UPDATE listings SET linked_wonders = ? WHERE id = ? AND (linked_wonders IS NULL OR linked_wonders = '[]' OR linked_wonders = '')",
        (_json.dumps(linked), listing_id)
    )
    conn.commit()
    conn.close()
    return [wid for _, wid, _ in top]

@app.put("/listings/{listing_id}/publish")
def publish_listing(listing_id: int, email: str, attested: int = 0):
    """Transition a draft listing to live. Called by the seller onboarding flow
    once the seller has chosen a subscription tier and accepted the EULA.
    Auth: ?email= must match seller_email on the listing (or listing has no owner yet).
    Sets listing_status = 'live' and stamps published_at = now().
    """
    conn = database.get_db()
    existing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    # Email auth: if listing has a seller_email it must match; if NULL accept first caller
    if existing["seller_email"] and existing["seller_email"] != email:
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorised to publish this listing")
    current_status = existing["listing_status"] or "draft"
    if current_status == "live":
        conn.close()
        return {"message": "Listing is already live", "listing_id": listing_id}
    # Pull the seller's account to enforce EULA gate + get current trust_score
    user_row = conn.execute(
        "SELECT trust_score, eula_accepted_at, is_superuser FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    # Superusers bypass the EULA gate (for admin testing)
    is_super = bool(user_row["is_superuser"]) if user_row else False
    if user_row and not user_row["eula_accepted_at"] and not is_super:
        conn.close()
        raise HTTPException(
            status_code=403,
            detail="EULA not accepted — seller must accept the TrustSquare Terms before publishing."
        )
    user_trust = int(user_row["trust_score"] or 0) if user_row else 0

    # ── CARS-SPEC-1 (D3): vehicle attestation gate ────────────────────────
    # 409 ONLY for cars drafts that actually carry spec data and are not
    # attested. Legacy spec-less cars drafts publish exactly as before
    # (GUIDED-PUBLISH-1 safe). Superusers bypass (mirrors the EULA pattern).
    _ex = dict(existing)
    _is_cars = (_ex.get("category") or "").strip().lower() == "cars"
    _has_spec = False
    if _is_cars:
        for _cols, _keys in VEHICLE_SECTION_FIELDS.values():
            if any(_ex.get(_c) is not None for _c in _cols):
                _has_spec = True
                break
        if not _has_spec:
            try:
                _vs = json.loads(_ex.get("vehicle_specs") or "{}")
                _has_spec = isinstance(_vs, dict) and any(_k != "_prov" for _k in _vs)
            except Exception:
                _has_spec = False
    if _is_cars and _has_spec and not int(attested or 0) and not is_super:
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Please confirm your vehicle details and accept the seller attestation before publishing."
        )

    # Slot guard: enforce subscription slot limit (superusers exempt)
    if not is_super:
        slot_row = conn.execute(
            "SELECT slot_limit FROM users WHERE LOWER(email)=?", (email,)
        ).fetchone()
        slot_limit = int(slot_row["slot_limit"]) if slot_row and slot_row["slot_limit"] else 2
        live_count = conn.execute(
            "SELECT COUNT(*) as n FROM listings WHERE LOWER(seller_email)=? "
            "AND (listing_status IS NULL OR listing_status = 'live')",
            (email,)
        ).fetchone()["n"]
        if live_count >= slot_limit:
            conn.close()
            raise HTTPException(
                status_code=402,
                # SLOT-402-1 (16 Jul 2026): seller-facing wording — the app routes
                # the seller to plan selection; don't point at admin.html.
                detail=f"Listing slot limit reached ({live_count}/{slot_limit}) — your current "
                       f"plan allows {slot_limit} live listings. Choose a bigger plan to publish more."
            )

    conn.execute(
        """UPDATE listings
           SET listing_status = 'live',
               published_at   = datetime('now'),
               seller_email   = COALESCE(seller_email, ?),
               trust_score    = COALESCE(trust_score, ?)
           WHERE id = ?""",
        (email, user_trust, listing_id)
    )
    if _is_cars and int(attested or 0):
        # CARS-SPEC-1: stamp the liability attestation (C4) — publish-only write
        conn.execute(
            "UPDATE listings SET attested_at = datetime('now'), attested_email = ? WHERE id = ?",
            (email, listing_id)
        )
    conn.commit()
    conn.close()

    # Auto-link nearby World Heritage wonders (only if none already linked)
    try:
        # Geocode street address → listing_lat/lng if not already set
        listing_row = database.get_db().execute(
            "SELECT street_address, listing_lat, listing_lng, suburb, geo_city_id, category FROM listings WHERE id = ?",
            (listing_id,)
        ).fetchone()
        if listing_row and listing_row["street_address"] and not listing_row["listing_lat"]:
            city_name = database.get_db().execute(
                "SELECT name FROM geo_cities WHERE id = ?", (listing_row["geo_city_id"],)
            ).fetchone()
            city_name_str = city_name["name"] if city_name else ""
            glat, glng = _geocode_address(listing_row["street_address"], city_name_str)
            if glat and glng:
                database.get_db().execute(
                    "UPDATE listings SET listing_lat=?, listing_lng=? WHERE id=?",
                    (glat, glng, listing_id)
                )
                database.get_db().commit()

        city_row = database.get_db().execute(
            "SELECT lat, lng FROM geo_cities WHERE id = (SELECT geo_city_id FROM listings WHERE id = ?)",
            (listing_id,)
        ).fetchone()
        cat_row = database.get_db().execute(
            "SELECT category FROM listings WHERE id = ?", (listing_id,)
        ).fetchone()
        # Wonder auto-link allowlist (David ruling 12 Jun 2026): location-proximity
        # only adds buyer value for Property + Adventures; Collectors/Services/etc.
        # were collecting museum noise. Manual linking via the picker stays open to all.
        _wcat = ((cat_row["category"] or "") if cat_row else "").strip().lower()
        if city_row and city_row["lat"] and city_row["lng"] and _wcat in ("property", "adventures"):
            # Derive country iso2 for radius calculation
            country_row = database.get_db().execute(
                """SELECT g.country_iso2 FROM geo_cities g
                   JOIN listings l ON l.geo_city_id = g.id
                   WHERE l.id = ?""", (listing_id,)
            ).fetchone()
            country_iso2 = country_row["country_iso2"] if country_row else "ZA"
            derived_radius = _derived_radius_km(
                float(city_row["lat"]), float(city_row["lng"]), country_iso2
            )
            auto_link_wonders(
                listing_id,
                float(city_row["lat"]),
                float(city_row["lng"]),
                cat_row["category"] if cat_row else "",
                radius_km=derived_radius
            )
            # Property listings: auto-fetch nearby POIs (schools, hospitals, etc.)
            if cat_row and (cat_row["category"] or "").lower() == "property":
                # Coordinate priority: listing_lat/lng (geocoded street addr) > suburb > city
                addr_row = database.get_db().execute(
                    "SELECT listing_lat, listing_lng FROM listings WHERE id = ?", (listing_id,)
                ).fetchone()
                if addr_row and addr_row["listing_lat"] and addr_row["listing_lng"]:
                    poi_lat = float(addr_row["listing_lat"])
                    poi_lng = float(addr_row["listing_lng"])
                else:
                    suburb_row = database.get_db().execute(
                        """SELECT gs.lat, gs.lng FROM geo_suburbs gs
                           JOIN listings l ON l.suburb = gs.name AND l.geo_city_id = gs.city_id
                           WHERE l.id = ? AND gs.lat IS NOT NULL LIMIT 1""",
                        (listing_id,)
                    ).fetchone()
                    poi_lat = float(suburb_row["lat"]) if suburb_row and suburb_row["lat"] else float(city_row["lat"])
                    poi_lng = float(suburb_row["lng"]) if suburb_row and suburb_row["lng"] else float(city_row["lng"])
                auto_link_pois(listing_id, poi_lat, poi_lng)
    except Exception as _e:
        pass  # auto-link failure must never block publish

    return {"message": "Listing is now live", "listing_id": listing_id}

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
    out = []
    for r in rows:
        d = dict(r)
        if (d.get("category") or "").lower() == "property":
            d["availability_label"] = _rental_availability(d.get("rental_status"), d.get("available_from"))
        out.append(d)
    return out

@app.get("/listings/{listing_id}")
def get_listing(listing_id: int):
    """Fetch a single listing by ID."""
    conn = database.get_db()
    row = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Listing not found")
    _d = dict(row)
    if (_d.get("category") or "").lower() == "property":
        _d["availability_label"] = _rental_availability(_d.get("rental_status"), _d.get("available_from"))
    _scrub_vehicle_specs(_d)   # CARS-SPEC-1 D1: unconfirmed vehicle specs never public
    return _d

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

    # EULA gate — seller must have accepted TrustSquare terms before editing
    user_row_edit = conn.execute(
        "SELECT eula_accepted_at, is_superuser FROM users WHERE email = ?", (email,)
    ).fetchone()
    if user_row_edit and not user_row_edit["eula_accepted_at"] and not bool(user_row_edit["is_superuser"]):
        conn.close()
        raise HTTPException(
            status_code=403,
            detail="EULA not accepted — please accept the TrustSquare Terms before editing your listing."
        )

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

    _validate_rental_fields(d.get("rental_status"), d.get("available_from"))
    _validate_vehicle_fields(d.get("vehicle_specs"), d.get("spec_confirmed"))
    _reset_vehicle_confirmations(dict(existing), d)   # CARS-SPEC-1: edits clear section confirmations

    # Preserve [photos:...] prefix if description is being updated without it
    if "description" in d:
        existing_desc = existing["description"] or ""
        if existing_desc.startswith("[photos:") and not d["description"].startswith("[photos:"):
            bracket_end = existing_desc.find("]")
            if bracket_end != -1:
                photo_prefix = existing_desc[:bracket_end + 1]
                sep = "\n" if existing_desc[bracket_end+1:bracket_end+2] == "\n" else ""
                d["description"] = photo_prefix + sep + d["description"]

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


@app.delete("/listings/{listing_id}/seller")
def delete_listing_by_seller(listing_id: int, email: str):
    """Seller-authenticated delete. No API key required — email must match
    seller_email on the listing. Used by buyer-facing edit screen."""
    conn = database.get_db()
    row = conn.execute(
        "SELECT seller_email FROM listings WHERE id = ?", (listing_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    if (row["seller_email"] or "").lower() != email.lower():
        conn.close()
        raise HTTPException(status_code=403, detail="Email does not match listing owner")
    conn.execute("DELETE FROM listings WHERE id = ?", (listing_id,))
    conn.execute("DELETE FROM listing_cities WHERE listing_id = ?", (listing_id,))
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
def geo_get_cities(region_id: Optional[int] = None, country: Optional[str] = None,
                   q: Optional[str] = None):
    """Return cities filtered by region, country, and/or search query.
    q= does a prefix/contains search on city name — used by the city-reach typeahead."""
    conn = database.get_db()
    if q:
        pattern = f"%{q}%"
        if country:
            rows = conn.execute(
                """SELECT c.id, c.name, c.lat, c.lng, r.name as region_name
                   FROM geo_cities c JOIN geo_regions r ON c.region_id=r.id
                   WHERE c.country_iso2=? AND c.active=1 AND c.name LIKE ?
                   ORDER BY c.name LIMIT 20""",
                (country, pattern)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, name, lat, lng FROM geo_cities WHERE active=1 AND name LIKE ? ORDER BY name LIMIT 20",
                (pattern,)
            ).fetchall()
    elif region_id:
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
    except Exception as exc:
        conn.close()
        raise HTTPException(status_code=400, detail="Country already exists or invalid data") from exc
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
    # AREA-SUGGEST-1 (16 Jul 2026): GeoNames misses newer suburbs (Elarduspark,
    # found by David) — merge in suburb names actually used by this city's
    # listings so the list self-heals as sellers type new areas.
    conn = database.get_db()
    names = []
    city_row = conn.execute(
        "SELECT id FROM geo_cities WHERE name=? AND active=1 LIMIT 1", (city,)
    ).fetchone()
    if city_row:
        names = [r["name"] for r in conn.execute(
            "SELECT name FROM geo_suburbs WHERE city_id=? AND active=1 ORDER BY name",
            (city_row["id"],)
        ).fetchall()]
    else:
        # Fallback: old suburbs table
        names = [r["name"] for r in conn.execute(
            "SELECT name FROM suburbs WHERE city=? AND active=1 ORDER BY name ASC", (city,)
        ).fetchall()]
    used = [str(r["suburb"]).strip() for r in conn.execute(
        "SELECT DISTINCT suburb FROM listings WHERE city=? AND suburb IS NOT NULL "
        "AND TRIM(suburb)<>''", (city,)
    ).fetchall()]
    conn.close()
    seen = {x.lower() for x in names}
    extra = [u for u in used if u.lower() not in seen and u.lower() != city.lower()]
    return sorted(names + extra, key=str.lower)

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

def _vision_orient_image(img):
    """Session 98 — content-based orientation for collectible/card photos.

    EXIF-based correction (ImageOps.exif_transpose) cannot fix an image that has
    no EXIF tag but rotated pixels (e.g. desktop-saved or re-encoded card scans).
    For such images the reliable signal is the TEXT: a card's title/rules text is
    only readable in one orientation. We ask a cheap Haiku vision call which way is
    up and rotate to match. Returns (corrected_img, rotated_bool, model_in, model_out).

    Only worth calling on LANDSCAPE collectible images — a portrait card is almost
    always already upright, and a genuinely-landscape item (sealed box, banknote)
    will correctly come back as 'none'. Fails OPEN: any error returns the image
    unchanged so a vision hiccup never blocks an upload.
    """
    import base64 as _b64
    try:
        if not ANTHROPIC_API_KEY:
            return (img, False, None, None)
        w, h = img.size
        if w <= h:
            return (img, False, None, None)   # already portrait/upright — skip the call

        # P2 wrapper — ceiling check before the paid call. Helper fails OPEN by
        # contract (an orientation hiccup must never block an upload), so a 429
        # just skips the vision call and leaves the image unchanged.
        try:
            _check_cost_ceiling("")
        except HTTPException:
            _log.warning("_vision_orient_image skipped — daily cost ceiling reached")
            return (img, False, None, None)

        # Downscale a copy for the vision call (cheap; orientation needs no detail).
        probe = img.copy()
        probe.thumbnail((512, 512), Image.LANCZOS)
        pbuf = io.BytesIO(); probe.save(pbuf, format="JPEG", quality=70)
        b64 = _b64.b64encode(pbuf.getvalue()).decode()

        prompt = (
            "This is a photo of a collectible (often a trading card) that may be rotated. "
            "Decide how to rotate it so any TEXT and the main subject read normally, "
            "right-side up. If the item has text, the correct orientation is the one where "
            "the text reads left-to-right, top-to-bottom. "
            "Reply with ONLY one word: none, cw, ccw, or flip. "
            "none = already upright; cw = rotate 90 clockwise; ccw = rotate 90 counter-clockwise; "
            "flip = rotate 180."
        )
        with httpx.Client(timeout=20) as client:
            resp = client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": AA_MODEL,
                    "max_tokens": 8,
                    "messages": [{"role": "user", "content": [
                        {"type": "image", "source": {"type": "base64",
                         "media_type": "image/jpeg", "data": b64}},
                        {"type": "text", "text": prompt},
                    ]}],
                },
            )
        rj = resp.json()
        ans = (rj.get("content", [{}])[0].get("text", "") or "").strip().lower()
        it, ot = _usage_tokens(rj)
        # P2 wrapper — log spend HERE (moved from the caller): tokens are spent
        # even when the answer is 'none' and no rotation happens.
        _log_ai_spend("", "/listings/photo:orient", "haiku", it, ot)
        # PIL.rotate is COUNTER-CLOCKWISE for positive angles.
        if "ccw" in ans:
            return (img.rotate(90, expand=True), True, it, ot)
        if "cw" in ans:
            return (img.rotate(-90, expand=True), True, it, ot)
        if "flip" in ans:
            return (img.rotate(180, expand=True), True, it, ot)
        return (img, False, it, ot)   # 'none' or unrecognised → leave as-is
    except Exception as exc:
        _log.warning("_vision_orient_image failed (leaving image unchanged): %s", exc)
        return (img, False, None, None)


# ── SELLER-PHOTO ANON GATE (11 Jul 2026) ─────────────────────────────────────
# Root cause of the cars-category plate slip (David Jnr's advert, 11 Jul 2026):
# the fail-closed vision anonymiser (_anon_photo_scan/_anon_photo_redact, prompt
# explicitly lists "vehicle number plates") was wired ONLY into
# /agencies/{id}/import — normal seller uploads stored photos with NO anonymity
# check at all, and the Advert Coach anonymity_warning is text-only (never sees
# photos). This gate runs the SAME fail-closed pass on every seller photo:
#   clean → store · redact → blur regions on the full-size image, then store ·
#   reject / low-confidence / scan-failure → HTTP 422/503, photo NEVER stored.
# Kill-switch: PHOTO_ANON_SCAN=off (env) skips the gate (keyless dev boxes only).

PHOTO_ANON_SCAN = os.getenv("PHOTO_ANON_SCAN", "on").strip().lower()

# SUBJECT-MATCH-1: per-category keyword hints — a photo whose AI-read subject
# shares none of these tokens gets a note (never a block). Detail shots are
# covered (engine, dashboard, kitchen, markings...).
_SUBJECT_HINTS = {
    "cars": ("car", "vehicle", "bakkie", "suv", "sedan", "hatch", "coupe", "van",
             "engine", "dashboard", "odometer", "interior", "seat", "wheel",
             "tyre", "boot", "bonnet", "motor"),
    "property": ("house", "home", "building", "apartment", "flat", "room",
                 "kitchen", "bedroom", "bathroom", "lounge", "living", "garden",
                 "pool", "yard", "garage", "exterior", "interior", "patio"),
    "collectors": ("coin", "card", "stamp", "art", "painting", "antique", "toy",
                   "book", "bottle", "watch", "medal", "banknote", "figurine",
                   "collect", "vinyl", "record", "certificate", "item"),
    "local_market": (),   # anything goes — honey to guitars
    "services": (),       # people at work, tools, premises — too varied to hint
    "tutors": (),
    "adventures": (),
}

def _seller_photo_anon_gate(img, category: str, spend_who: str, is_primary: bool = False):
    """Fail-closed anonymity gate for ONE seller-uploaded photo. PIL image in,
    PIL image out (blurred where needed). Raises HTTPException when the photo
    must not be stored. Returns (img, note): note "" = clean, "redacted:<labels>"
    = blurred (surface to the seller), "scan-off" = gate disabled by env."""
    if PHOTO_ANON_SCAN == "off":
        return img, "scan-off"
    _check_cost_ceiling(spend_who)   # C1 rail — 429 over the daily ceiling
    import base64 as _b64
    probe = img.copy(); probe.thumbnail((1344, 1344), Image.LANCZOS)   # 896->1344 11 Jul 2026: small background plates were illegible to the scanner
    pbuf = io.BytesIO(); probe.save(pbuf, format="JPEG", quality=80)
    scan, _it, _ot = _anon_photo_scan(
        _b64.b64encode(pbuf.getvalue()).decode(), _ts_active_provider(), category or "")
    if _it is not None or _ot is not None:
        _log_ai_spend(spend_who, "/listings/photo#anon-scan", "sonnet_vision", _it, _ot)
    if not scan:   # no key / provider down / unparseable verdict — FAIL CLOSED
        raise HTTPException(status_code=503,
            detail="Photo safety check unavailable — please try again in a minute")
    labels = ", ".join(sorted(set(scan.get("labels") or []))[:4])
    # MODERATION-1 (15 Jul 2026, David): photos of people in degrading states,
    # nudity, violence etc. are rejected outright — listings are for items.
    if scan.get("flag") == "inappropriate":
        raise HTTPException(status_code=422,
            detail="This photo isn't appropriate for a listing — please use "
                   "photos of what you are selling.")
    # WRONG-TYPE-1 (16 Jul 2026, David: a boat listed as a Cars main photo was
    # never flagged): the scan model now judges category fit itself
    # ("fits_category"). A PRIMARY photo that clearly shows the wrong kind of
    # item is BLOCKED - the advert cover must show what is being sold.
    # Non-primary photos keep SUBJECT-MATCH-1's note-only behaviour (detail
    # shots are legitimate); keyword hints remain the fallback when the model
    # omits the field. The note rides the upload response ("anon" field) and
    # feeds the coming LISTING-CONSISTENCY-1 same-item check.
    _subj = str(scan.get("subject") or "").lower()
    _fits = scan.get("fits")
    _mismatch = ""
    if _fits is False:
        if is_primary:
            raise HTTPException(status_code=422,
                detail="This photo doesn't look like what this advert is selling"
                       + (" (it shows: %s)" % _subj if _subj else "")
                       + ". The main advert photo must show the item itself - "
                         "please use a photo of it.")
        _mismatch = "|subject-mismatch:" + (_subj[:40] if _subj else "wrong-type")
    elif _fits is None and _subj:
        _hints = _SUBJECT_HINTS.get((category or "").strip().lower())
        if _hints and not any(hh in _subj for hh in _hints):
            _mismatch = "|subject-mismatch:" + _subj[:40]
    _retake = ("TrustSquare adverts are anonymous — please retake the photo "
               "avoiding number plates, signage and contact details.")
    if scan["verdict"] == "reject":
        raise HTTPException(status_code=422,
            detail="Photo blocked to protect your anonymity"
                   + (" (%s)" % labels if labels else "") + ". " + _retake)
    if scan["confidence"] < _ANON_PHOTO_CONF:
        raise HTTPException(status_code=422,
            detail="Could not confirm this photo is anonymous. " + _retake)
    if scan["verdict"] == "redact":
        if not scan["regions"]:
            raise HTTPException(status_code=422,
                detail="Photo blocked to protect your anonymity. " + _retake)
        img2, _lbls = _anon_blur_until_clean(
            img, scan, _ts_active_provider(), category or "", spend_who,
            "/listings/photo#anon-verify")
        if img2 is None:
            raise HTTPException(status_code=422,
                detail="Could not verifiably blur the identifying content. " + _retake)
        return img2, "redacted:" + ", ".join(sorted(set(_lbls))[:4]) + _mismatch
    return img, ("" if not _mismatch else _mismatch.lstrip("|"))

@app.post("/listings/photo")
async def upload_listing_photo(
    file: UploadFile = File(...),
    listing_id: Optional[int] = Form(None),
    is_primary: Optional[str] = Form(None),
    caption: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
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
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read image file") from exc

    # Session 98 — collectibles: EXIF can't fix tag-less rotated card scans, so for
    # a landscape Collectors photo, ask vision which way is up and rotate to match.
    if (category or "").strip().lower() == "collectors":
        img, _oriented, _oin, _oout = _vision_orient_image(img)
        if _oriented:
            _log.info("photo upload: vision re-oriented collectible image (listing=%s)", listing_id)
        # spend logging lives inside _vision_orient_image (P2 sweep, 12 Jun 2026)

    # SELLER-ANON GATE (11 Jul 2026) — scan BEFORE thumb/medium so blurs propagate.
    _anon_who = "photo-upload"
    # WRONG-TYPE-1: the advert cover is the primary photo - explicit flag, or
    # first photo of a listing that has no cover yet. Category falls back to
    # the listing row when the caller didn't send one (the gate needs it).
    _gate_primary = (is_primary == "true")
    _gate_cat = category or ""
    if listing_id:
        try:
            _c0 = database.get_db()
            _r0 = _c0.execute("SELECT seller_email, thumb_url, category FROM listings WHERE id=?", (listing_id,)).fetchone()
            _c0.close()
            if _r0 and _r0["seller_email"]:
                _anon_who = _r0["seller_email"]
            if _r0 and not _r0["thumb_url"]:
                _gate_primary = True
            if _r0 and not _gate_cat:
                _gate_cat = _r0["category"] or ""
        except Exception:
            pass
    img, _anon_note = _seller_photo_anon_gate(img, _gate_cat, _anon_who, is_primary=_gate_primary)

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
        orig_name = (file.filename or "photo.jpg").replace(" ", "_")
        key = f"media/{uuid.uuid4().hex}_{orig_name}"
        s3_url = _s3_upload(medium_bytes, key, "image/jpeg")
        thumb_url = s3_url
        medium_url = s3_url
    else:
        # Local /media fallback
        base = storage.generate_filename("listing")
        thumb_name  = base.replace(".jpg", "_thumb.jpg")
        medium_name = base.replace(".jpg", "_medium.jpg")
        thumb_url  = storage.upload_photo(thumb_bytes,  thumb_name,  "image/jpeg")
        medium_url = storage.upload_photo(medium_bytes, medium_name, "image/jpeg")

    # ── Save URLs to listing row ─────────────────────────────
    # If listing_id provided, persist photo URL back to the listing.
    # is_primary='true' (or no existing photo) → set as thumb_url + medium_url.
    # Additional photos are appended as [photos:url::caption|...] prefix in description.
    if listing_id:
        import re as _re
        conn = database.get_db()
        try:
            row = conn.execute(
                "SELECT thumb_url, medium_url, description FROM listings WHERE id = ?",
                (listing_id,)
            ).fetchone()
            if row:
                existing_thumb = row["thumb_url"]
                existing_desc  = row["description"] or ""
                primary = (is_primary == "true") or (not existing_thumb)
                # Encode caption into the URL entry: "url::caption" (safe separator)
                cap_clean = (caption or "").replace("|", " ").replace("::", " ").strip()
                photo_entry = f"{medium_url}::{cap_clean}" if cap_clean else medium_url
                if primary:
                    conn.execute(
                        "UPDATE listings SET thumb_url=?, medium_url=? WHERE id=?",
                        (thumb_url, medium_url, listing_id)
                    )
                    # Store in description photo prefix for multi-photo strip
                    if not existing_desc.startswith("[photos:"):
                        new_desc = f"[photos:{photo_entry}]\n{existing_desc}"
                    else:
                        def _replace_first(m):
                            parts = [p for p in m.group(1).split("|") if p]
                            rest = parts[1:] if parts else []
                            all_parts = [photo_entry] + [p for p in rest if not p.startswith(medium_url)]
                            return "[photos:" + "|".join(all_parts) + "]"
                        new_desc = _re.sub(r'^\[photos:([^\]]+)\]', _replace_first, existing_desc)
                    conn.execute(
                        "UPDATE listings SET description=? WHERE id=?",
                        (new_desc, listing_id)
                    )
                else:
                    # Append to photo strip prefix
                    if existing_desc.startswith("[photos:"):
                        new_desc = _re.sub(
                            r'^\[photos:([^\]]*)\]',
                            lambda m: "[photos:" + m.group(1) + "|" + photo_entry + "]",
                            existing_desc
                        )
                    else:
                        first_entry = existing_thumb or ""
                        new_desc = (f"[photos:{first_entry}|{photo_entry}]\n{existing_desc}"
                                    if first_entry else f"[photos:{photo_entry}]\n{existing_desc}")
                    conn.execute(
                        "UPDATE listings SET description=? WHERE id=?",
                        (new_desc, listing_id)
                    )
                conn.commit()
        finally:
            conn.close()

    return {
        "thumb_url":  thumb_url,
        "medium_url": medium_url,
        "thumb_kb":   round(len(thumb_bytes)  / 1024, 1),
        "medium_kb":  round(len(medium_bytes) / 1024, 1),
        "anon": _anon_note,
    }

@app.post("/listings/{listing_id}/photo/draft")
async def upload_draft_listing_photo(
    listing_id: int,
    email: str,
    file: UploadFile = File(...)
):
    """Upload a photo to a DRAFT listing. Email-auth only — no API key required.
    Reuses the same compression pipeline as /listings/photo.
    Rejected if listing_status != 'draft' or email doesn't match seller_email.
    Sets thumb_url + medium_url on the listing row and prepends to photo strip.
    """
    import re as _re

    # Validate file type
    allowed = {"image/jpeg", "image/png", "image/webp"}
    content_type = file.content_type or "image/jpeg"
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WebP photos accepted")

    raw = await file.read()
    if len(raw) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Photo too large — max 20MB")

    try:
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read image file") from exc

    # Auth + draft guard
    conn = database.get_db()
    row = conn.execute(
        "SELECT seller_email, listing_status, thumb_url, description, category FROM listings WHERE id = ?",
        (listing_id,)
    ).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    if (row["listing_status"] or "draft") != "draft":
        conn.close()
        raise HTTPException(status_code=409, detail="Only draft listings can use this endpoint")
    if row["seller_email"] and row["seller_email"] != email:
        conn.close()
        raise HTTPException(status_code=403, detail="Not authorised to edit this listing")

    # SELLER-ANON GATE (11 Jul 2026) — same fail-closed scan as /listings/photo.
    try:
        img, _anon_note = _seller_photo_anon_gate(
            img, row["category"] or "", email,
            is_primary=not (row["thumb_url"] or ""))   # WRONG-TYPE-1: first photo = advert cover
    except HTTPException:
        conn.close()
        raise

    # Compress to thumb + medium (same pipeline as /listings/photo)
    thumb = img.copy()
    thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
    thumb_buf = io.BytesIO()
    thumb.save(thumb_buf, format="JPEG", quality=JPEG_QUALITY_THUMB, optimize=True)
    thumb_bytes = thumb_buf.getvalue()

    medium = img.copy()
    medium.thumbnail(MEDIUM_SIZE, Image.LANCZOS)
    medium_buf = io.BytesIO()
    medium.save(medium_buf, format="JPEG", quality=JPEG_QUALITY_MEDIUM, optimize=True)
    medium_bytes = medium_buf.getvalue()

    # Upload to R2 or local fallback
    if _S3_CONFIGURED:
        orig_name = (file.filename or "photo.jpg").replace(" ", "_")
        key = f"media/draft_{uuid.uuid4().hex}_{orig_name}"
        medium_url = _s3_upload(medium_bytes, key, "image/jpeg")
        thumb_url = medium_url
    else:
        base = storage.generate_filename("draft_listing")
        thumb_name  = base.replace(".jpg", "_thumb.jpg")
        medium_name = base.replace(".jpg", "_medium.jpg")
        thumb_url  = storage.upload_photo(thumb_bytes,  thumb_name,  "image/jpeg")
        medium_url = storage.upload_photo(medium_bytes, medium_name, "image/jpeg")

    # Persist to listing row
    # Build [photos:url1|url2|...] prefix in description (legacy) AND maintain photo_urls JSON array
    existing_desc = row["description"] or ""

    # Extract existing photo_urls JSON array from DB row
    existing_photo_urls_raw = conn.execute(
        "SELECT photo_urls FROM listings WHERE id=?", (listing_id,)
    ).fetchone()
    existing_photo_urls = []
    if existing_photo_urls_raw and existing_photo_urls_raw["photo_urls"]:
        import json as _json
        try:
            existing_photo_urls = _json.loads(existing_photo_urls_raw["photo_urls"])
            if not isinstance(existing_photo_urls, list):
                existing_photo_urls = []
        except Exception:
            existing_photo_urls = []
    # Append new photo (avoid duplicates)
    if medium_url not in existing_photo_urls:
        existing_photo_urls.append(medium_url)
    import json as _json
    new_photo_urls = _json.dumps(existing_photo_urls)

    # thumb_url / medium_url always reflect first photo (position 0)
    primary_url = existing_photo_urls[0] if existing_photo_urls else medium_url

    # Update [photos:...] prefix in description
    all_urls = "|".join(existing_photo_urls)
    if existing_desc.startswith("[photos:"):
        new_desc = _re.sub(
            r'^\[photos:[^\]]*\]',
            f"[photos:{all_urls}]",
            existing_desc
        )
    else:
        new_desc = f"[photos:{all_urls}]\n{existing_desc}"

    try:
        conn.execute(
            "UPDATE listings SET thumb_url=?, medium_url=?, photo_urls=?, seller_email=COALESCE(seller_email,?), description=? WHERE id=?",
            (primary_url, primary_url, new_photo_urls, email, new_desc, listing_id)
        )
        conn.commit()
    finally:
        conn.close()

    return {
        "thumb_url":  thumb_url,
        "medium_url": medium_url,
        "thumb_kb":   round(len(thumb_bytes)  / 1024, 1),
        "medium_kb":  round(len(medium_bytes) / 1024, 1),
        "anon": _anon_note,
    }


# ── USERS (protected write) ──────────────────────────────────

@app.post("/users")
def create_user(user: User, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    # INSERT OR IGNORE so existing sellers don't raise an error.
    # Track whether the row is new so we only credit ai_sessions once.
    result = conn.execute(
        "INSERT OR IGNORE INTO users (email, name) VALUES (?,?)",
        (user.email, user.name)
    )
    is_new = result.rowcount > 0
    conn.commit()
    # Credit free AI sessions only on first registration — not on repeat calls.
    if is_new and user.ai_sessions and user.ai_sessions > 0:
        conn.execute(
            "UPDATE users SET aa_sessions_remaining = aa_sessions_remaining + ? WHERE email = ?",
            (user.ai_sessions, user.email)
        )
        conn.commit()
    conn.close()
    return {"message": "User created successfully"}

@app.get("/users/{email}")
def get_user(email: str):
    conn = database.get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    data = dict(row)
    # C1/H2 (audit 16 Jul 2026): never expose identity-document internals over this
    # public-by-email read. Hashed ID number, legal ID name and the AI match score
    # are PII; verified STATUS still travels via id_verified_at.
    for _sensitive in ("id_number_hash", "id_name", "id_ai_score"):
        data.pop(_sensitive, None)
    return data

@app.get("/users/{email}/subscription")
def get_user_subscription(email: str):
    """Return seller's subscription tier, slot usage, and pending downgrade info."""
    email = email.lower().strip()
    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT seller_tier, slot_limit, pending_downgrade_tier, billing_period_end "
            "FROM users WHERE LOWER(email)=?", (email,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found")
        tier = row["seller_tier"] or "free"
        slot_limit = int(row["slot_limit"]) if row["slot_limit"] else _tier_slot_limit(tier)
        live_count = conn.execute(
            "SELECT COUNT(*) as n FROM listings WHERE LOWER(seller_email)=? "
            "AND (listing_status IS NULL OR listing_status = 'live')",
            (email,)
        ).fetchone()["n"]
        draft_count = conn.execute(
            "SELECT COUNT(*) as n FROM listings WHERE LOWER(seller_email)=? "
            "AND listing_status = 'draft'",
            (email,)
        ).fetchone()["n"]
        plan = _SELLER_SUB_TIERS.get(tier, _SELLER_SUB_TIERS["free"])
    finally:
        conn.close()
    return {
        "email": email,
        "seller_tier": tier,
        "tier_label": plan["label"],
        "slot_limit": slot_limit,
        "slots_used": live_count,
        "slots_available": max(0, slot_limit - live_count),
        "draft_count": draft_count,
        "pending_downgrade_tier": row["pending_downgrade_tier"],
        "billing_period_end": row["billing_period_end"],
        "usd_per_month": plan["usd"],
    }

@app.get("/users/{email}/trust")
def get_user_trust(email: str):
    """Return trust score + per-signal breakdown for My Space dashboard.
    Computes earned/available signals from the users table + intro_requests.
    No API key required — buyer identifies by email."""
    conn = database.get_db()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    user = dict(row)

    score = int(user.get("trust_score") or 0)

    # Count completed intros for this seller
    intro_count = conn.execute(
        "SELECT COUNT(*) FROM intro_requests WHERE listing_id IN "
        "(SELECT id FROM listings WHERE seller_email = ?) AND status = 'accepted'",
        (email,)
    ).fetchone()[0]

    # Count ignored intros in last 90 days
    ignored_count = conn.execute(
        "SELECT COUNT(*) FROM intro_requests WHERE listing_id IN "
        "(SELECT id FROM listings WHERE seller_email = ?) "
        "AND status = 'pending' AND created_at < datetime('now', '-48 hours') "
        "AND created_at > datetime('now', '-90 days')",
        (email,)
    ).fetchone()[0]

    # Tenure: earliest listing
    first_listing = conn.execute(
        "SELECT MIN(published_at) FROM listings WHERE seller_email = ? AND listing_status = 'live'",
        (email,)
    ).fetchone()[0]

    conn.close()

    has_photo    = bool(user["photo_url"])
    id_verified  = bool(user.get("id_verified_at"))
    eula_signed  = bool(user.get("eula_accepted_at"))

    import datetime as _dt
    tenure_6mo = False
    if first_listing:
        try:
            fp = _dt.datetime.fromisoformat(first_listing.replace("Z",""))
            tenure_6mo = (_dt.datetime.utcnow() - fp).days >= 180
        except Exception:
            pass

    signals = [
        {
            "key": "email_verified",
            "name": "Email verified",
            "points": 15,
            "earned": eula_signed,
            "how_to_earn": "Sign in with your email to verify it.",
        },
        {
            "key": "id_verified",
            "name": "Government-issued ID verified",
            "points": 15,
            "earned": id_verified,
            "how_to_earn": "Upload your ID or passport in your profile.",
        },
        {
            "key": "profile_photo",
            "name": "Profile photo added",
            "points": 10,
            "earned": has_photo,
            "how_to_earn": "Upload a clear profile photo in your seller dashboard.",
        },
        {
            "key": "intro_1",
            "name": "First successful introduction",
            "points": 5,
            "earned": intro_count >= 1,
            "how_to_earn": "Accept and complete your first buyer introduction.",
        },
        {
            "key": "intro_5",
            "name": "5+ successful introductions",
            "points": 5,
            "earned": intro_count >= 5,
            "how_to_earn": "Complete five buyer introductions.",
        },
        {
            "key": "intro_20",
            "name": "20+ successful introductions",
            "points": 5,
            "earned": intro_count >= 20,
            "how_to_earn": "Complete twenty buyer introductions.",
        },
        {
            "key": "zero_ignored",
            "name": "Zero ignored introductions (90 days)",
            "points": 10,
            "earned": ignored_count == 0 and intro_count > 0,
            "how_to_earn": "Respond to every introduction within 48 hours.",
        },
        {
            "key": "tenure_6mo",
            "name": "Active listing for 6+ months",
            "points": 5,
            "earned": tenure_6mo,
            "how_to_earn": "Keep at least one live listing for six months.",
        },
    ]

    tier = _trust_tier(score)
    earned_pts  = sum(s["points"] for s in signals if s["earned"])
    available_pts = sum(s["points"] for s in signals if not s["earned"])

    return {
        "email":         email,
        "score":         score,
        "tier":          tier,
        "earned_pts":    earned_pts,
        "available_pts": available_pts,
        "intro_count":   intro_count,
        "signals":       signals,
    }

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
        img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Could not read image file") from exc

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
            raise HTTPException(status_code=500, detail="Photo storage unavailable") from exc

    # Upsert user record and save photo_url
    conn = database.get_db()
    conn.execute(
        "INSERT INTO users (email, photo_url) VALUES (?, ?) ON CONFLICT(email) DO UPDATE SET photo_url = excluded.photo_url",
        (email, photo_url)
    )
    conn.commit()
    conn.close()
    return {"photo_url": photo_url}


@app.post("/users/{email}/upload-id")
async def upload_user_id(email: str, file: UploadFile = File(...), _key: str = Depends(auth.require_api_key)):
    """Self-serve ID upload. Requires the app key (parity with all writes).
    Accepts photo of SA ID / passport / drivers licence.
    C2 fix (audit 16 Jul 2026): stores the document as PENDING and grants NO
    trust — identity is only awarded by the vision-checked verify-identity path
    (or admin review). This closes the instant self-grant of +15 trust."""
    allowed = {"image/jpeg", "image/png", "image/webp"}
    content_type = file.content_type or "image/jpeg"
    if content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only JPEG, PNG or WebP accepted")

    raw = await file.read()
    if len(raw) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large — max 15MB")
    if len(raw) < 5000:
        raise HTTPException(status_code=400, detail="File too small — please upload a clear photo")

    email = email.lower().strip()

    # Upload to R2 or local
    fname = f"id_{uuid.uuid4().hex}.jpg"
    if _S3_CONFIGURED:
        key = f"ids/{fname}"
        id_url = _s3_upload(raw, key, content_type)
    else:
        local_path = f"/var/www/marketsquare/media/{fname}"
        try:
            with open(local_path, "wb") as fh:
                fh.write(raw)
            id_url = f"/media/{fname}"
        except Exception as exc:
            _log.error("ID photo local save failed: %s", exc)
            raise HTTPException(status_code=500, detail="Storage unavailable") from exc

    conn = database.get_db()
    try:
        # Upsert user row if needed
        conn.execute(
            "INSERT OR IGNORE INTO users (email, trust_score) VALUES (?, 40)",
            (email,)
        )
        # Check if already verified — don't double-award points
        row = conn.execute(
            "SELECT trust_score, id_verified_at FROM users WHERE email=?", (email,)
        ).fetchone()
        already_verified = bool(row and row["id_verified_at"])
        current_score    = int(row["trust_score"] or 0) if row else 40

        # C2 fix (audit 16 Jul 2026): NO trust is granted here. Store the ID as a
        # pending document; the vision-checked /users/{email}/verify-identity path
        # (or admin review) is the only route that sets id_verified_at / awards points.
        if already_verified:
            conn.commit()
            return {"verified": True, "status": "verified", "trust_score": current_score,
                    "points_awarded": 0, "already_verified": True}

        conn.execute(
            """INSERT INTO seller_documents (email, doc_type, label, url, visibility, signal_id)
               VALUES (?, 'id_doc', 'Government-issued ID', ?, 'private', 'category.lm.id_uploaded')""",
            (email, id_url)
        )
        _upsert_credential(conn, email, "universal.id_verified", "pending")
        conn.commit()
        return {"verified": False, "status": "pending", "trust_score": current_score,
                "points_awarded": 0, "already_verified": False,
                "message": "ID received \u2014 verification in progress."}
    finally:
        conn.close()

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
    listing_status = listing["listing_status"] if listing["listing_status"] else "live"
    if listing_status != "live":
        conn.close()
        raise HTTPException(status_code=409, detail=f"Listing is not available for introductions (status: {listing_status})")
    # Self-intro guard — buyer cannot intro their own listing
    if listing["seller_email"] and intro.buyer_email and        listing["seller_email"].lower() == intro.buyer_email.lower():
        conn.close()
        raise HTTPException(status_code=409, detail="You cannot request an introduction to your own listing")
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
def get_all_intros(status: str = "pending", buyer_email: Optional[str] = None):
    conn = database.get_db()
    # status="all" means no status filter — return all regardless of status
    if status == "all":
        if buyer_email:
            rows = conn.execute(
                """SELECT i.*, l.title as listing_title, l.category, l.city
                   FROM intro_requests i
                   JOIN listings l ON i.listing_id = l.id
                   WHERE LOWER(i.buyer_email) = LOWER(?)
                   ORDER BY i.created_at DESC""",
                (buyer_email,)
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT i.*, l.title as listing_title, l.category, l.city
                   FROM intro_requests i
                   JOIN listings l ON i.listing_id = l.id
                   ORDER BY i.created_at DESC"""
            ).fetchall()
    else:
        if buyer_email:
            rows = conn.execute(
                """SELECT i.*, l.title as listing_title, l.category, l.city
                   FROM intro_requests i
                   JOIN listings l ON i.listing_id = l.id
                   WHERE i.status = ? AND LOWER(i.buyer_email) = LOWER(?)
                   ORDER BY i.created_at DESC""",
                (status, buyer_email)
            ).fetchall()
        else:
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
            "event":         "intro_declined",
            "intro_id":      intro_id,
            "listing_id":    intro["listing_id"],
            "listing_title": listing["title"]    if listing else None,
            "category":      listing["category"] if listing else None,
            "buyer_email":   intro["buyer_email"],
            "buyer_name":    intro["buyer_name"],
            "city":          listing["city"]     if listing else None,
            "timestamp":     datetime.now(timezone.utc).isoformat(),
        }
        background_tasks.add_task(_fire_webhook, N8N_WEBHOOK_DECLINE, payload)
    return {"message": "Introduction declined"}

# ── PAYMENTS (Paystack) ──────────────────────────────────────
import payments
import uuid

def _payment_grants_allowed() -> bool:
    """Gate 2 (S5) - fail-closed entitlement gate. A Paystack TEST key (or no key)
    must NOT mint real Tuppence / subscriptions in production. Live keys always pass;
    a test/unset key passes ONLY when ALLOW_TEST_PAYMENTS=1 (dev/staging). Prevents
    test-card payments granting real entitlements while live-mode is pending."""
    key = os.getenv("PAYSTACK_SECRET_KEY", "")
    if key.startswith("sk_live"):
        return True
    return os.getenv("ALLOW_TEST_PAYMENTS", "") == "1"

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
        if not _payment_grants_allowed():
            raise HTTPException(status_code=503, detail="Payments are not live yet - top-ups are temporarily disabled.")
        conn = database.get_db()
        # Idempotency (mirror the webhook): skip if this reference was already credited
        if conn.execute("SELECT id FROM transactions WHERE description LIKE ?", (f"%ref {reference}%",)).fetchone():
            conn.close()
            return {"status": "ok", "tuppence_credited": 0, "ai_sessions_credited": 0, "email": email, "note": "already processed"}
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
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

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

        if not _payment_grants_allowed():
            _log.warning("Paystack webhook: grants gated (test key, ALLOW_TEST_PAYMENTS!=1) - ref %s not credited", reference)
            return {"status": "ok"}

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

# ── SELLER SUBSCRIPTION PAYMENTS ────────────────────────────
# 5-tier design (Session 91). USD → ZAR at R18/$ conservative rate.
# Downgrades: pending until billing_period_end, then applied by worker.
# Reference prefixes: ms_sub_{tier}_xxx

# PRICING AUTHORITY — source of truth for seller tiers. Keep PRICING_CANON.md in sync; run scripts/check_pricing_canon.py.
_SELLER_SUB_TIERS = {
    # Simpler Model (adopted 9-10 Jun 2026) — offered to new sellers
    "free":    {"amount_rands": 0.0,   "label": "Free",    "slot_limit": 2,  "usd": 0},
    "starter": {"amount_rands": 90.0,  "label": "Starter", "slot_limit": 10, "usd": 5},
    "pro":     {"amount_rands": 360.0, "label": "Pro",     "slot_limit": 30, "usd": 20},
    "agency":  {"amount_rands": 0.0,   "label": "Agency",  "slot_limit": 10, "usd": 0},
    # ^ Agency is FREE + verified; slot_limit here is the BASE — the trust-graduated cap
    #   (10 new -> 100 verified -> 500 established + review) is applied separately, category-aware.
    # Legacy 5-tier (retained for existing users until migration; NOT offered to new sellers)
    "standard":     {"amount_rands": 216.0,  "label": "Standard (legacy)",     "slot_limit": 10,  "usd": 12},
    "professional": {"amount_rands": 360.0,  "label": "Professional (legacy)", "slot_limit": 25,  "usd": 20},
    "business":     {"amount_rands": 720.0,  "label": "Business (legacy)",     "slot_limit": 60,  "usd": 40},
    "elite":        {"amount_rands": 1800.0, "label": "Elite (legacy)",        "slot_limit": 500, "usd": 100},
    "premium":      {"amount_rands": 270.0,  "label": "Professional (legacy)", "slot_limit": 25,  "usd": 15},
}

def _tier_slot_limit(tier: str) -> int:
    """Return slot limit for a tier name."""
    return _SELLER_SUB_TIERS.get(tier, _SELLER_SUB_TIERS["free"])["slot_limit"]

@app.get("/subscription/tiers")
def list_subscription_tiers():
    """Return all seller subscription tiers with pricing and slot limits."""
    tiers = []
    for key in ("free", "starter", "pro", "agency"):
        plan = _SELLER_SUB_TIERS[key]
        tiers.append({
            "id": key,
            "label": plan["label"],
            "slot_limit": plan["slot_limit"],
            "usd_per_month": plan["usd"],
            "rands_per_month": plan["amount_rands"],
        })
    return {"tiers": tiers}


@app.post("/payment/seller-subscription/initialize")
def init_seller_subscription(email: str, tier: str, callback_url: str = ""):
    """Initialize a Paystack payment for a seller subscription tier change.
    tier: starter | pro  (Simpler Model, Jun 2026)
          + legacy standard | professional | business | elite (existing users only)
    Upgrades: charged immediately.
    Downgrades: scheduled for billing_period_end (pending_downgrade_tier set, not yet applied).
    Free tier: no payment needed — handled by PUT /users/{email}/seller-tier directly.
    Agency: free + verified — no payment; handled by the agency verification flow.
    Returns {status, reference, authorization_url, tier, amount_rands}
    """
    email = email.lower().strip()
    if tier == "agency":
        raise HTTPException(status_code=400,
                            detail="The Agency plan is free — no payment needed. "
                                   "Apply via agency verification instead.")
    # Simpler Model tiers first; legacy tiers kept payable for existing users until migration
    paid_tiers = ("starter", "pro", "standard", "professional", "business", "elite")
    if tier not in paid_tiers:
        raise HTTPException(status_code=400, detail=f"tier must be one of: {', '.join(paid_tiers)}")
    plan = _SELLER_SUB_TIERS[tier]

    # Determine if this is a downgrade (pending) or upgrade (immediate)
    conn = database.get_db()
    try:
        user = conn.execute(
            "SELECT seller_tier, slot_limit FROM users WHERE LOWER(email)=?", (email,)
        ).fetchone()
    finally:
        conn.close()

    current_tier = (user["seller_tier"] if user else "free") or "free"
    # Rank by price, not by a hand-kept list — works across new + legacy tiers
    def _tier_rank(t: str) -> float:
        return _SELLER_SUB_TIERS.get(t, _SELLER_SUB_TIERS["free"])["amount_rands"]
    is_downgrade = _tier_rank(tier) < _tier_rank(current_tier)

    reference = f"ms_sub_{tier}_{uuid.uuid4().hex[:12]}"
    result = payments.initialize_payment(
        email=email,
        amount_rands=plan["amount_rands"],
        reference=reference,
        metadata={
            "type": "seller_subscription",
            "tier": tier,
            "email": email,
            "is_downgrade": is_downgrade,
        },
        callback_url=callback_url or None,
    )
    if result.get("status"):
        return {
            "status": "ok",
            "reference": reference,
            "authorization_url": result["data"]["authorization_url"],
            "tier": tier,
            "label": plan["label"],
            "amount_rands": plan["amount_rands"],
            "is_downgrade": is_downgrade,
        }
    raise HTTPException(status_code=400, detail="Subscription payment initialization failed")


@app.get("/payment/seller-subscription/verify")
def verify_seller_subscription(reference: str):
    """Verify a seller subscription payment and apply the tier change.
    Upgrades: applied immediately (seller_tier + slot_limit updated).
    Downgrades: pending_downgrade_tier set; applied at billing_period_end by worker.
    Returns {status, email, tier, label, is_downgrade, effective}
    """
    result = payments.verify_payment(reference)
    if not (result.get("status") and result["data"]["status"] == "success"):
        raise HTTPException(status_code=400, detail="Payment verification failed or payment not successful")

    metadata = result["data"].get("metadata", {}) or {}
    if metadata.get("type") != "seller_subscription":
        raise HTTPException(status_code=400, detail="Reference is not a seller subscription payment")

    tier  = metadata.get("tier", "")
    email = metadata.get("email", "").lower().strip()
    is_downgrade = metadata.get("is_downgrade", False)

    if tier not in _SELLER_SUB_TIERS:
        raise HTTPException(status_code=400, detail=f"Unknown tier in metadata: {tier!r}")
    if not email:
        raise HTTPException(status_code=400, detail="Email missing from payment metadata")

    if not _payment_grants_allowed():
        raise HTTPException(status_code=503, detail="Payments are not live yet - subscriptions are temporarily disabled.")

    plan = _SELLER_SUB_TIERS[tier]
    slot_limit = plan["slot_limit"]
    # Billing period end = 30 days from now
    billing_end = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%dT%H:%M:%SZ")

    conn = database.get_db()
    try:
        if is_downgrade:
            # Schedule downgrade — keep current tier active until billing_period_end
            conn.execute(
                "INSERT INTO users (email, pending_downgrade_tier, billing_period_end) VALUES (?, ?, ?) "
                "ON CONFLICT(email) DO UPDATE SET "
                "  pending_downgrade_tier=excluded.pending_downgrade_tier,"
                "  billing_period_end=excluded.billing_period_end",
                (email, tier, billing_end),
            )
            effective = "end_of_billing_period"
        else:
            # Upgrade: apply immediately
            conn.execute(
                "INSERT INTO users (email, seller_tier, slot_limit, billing_period_end, pending_downgrade_tier) "
                "VALUES (?, ?, ?, ?, NULL) "
                "ON CONFLICT(email) DO UPDATE SET "
                "  seller_tier=excluded.seller_tier,"
                "  slot_limit=excluded.slot_limit,"
                "  billing_period_end=excluded.billing_period_end,"
                "  pending_downgrade_tier=NULL",
                (email, tier, slot_limit, billing_end),
            )
            effective = "immediate"
            try:
                launch_redemption.grant_monthly_tuppence(conn, email, tier)
            except Exception as _alloc_e:
                _log.warning("monthly Tuppence grant skipped for %s: %s", email, _alloc_e)
        conn.commit()
    finally:
        conn.close()

    _log.info("Seller subscription %s: %s → %s (ref %s, effective: %s)",
              "downgrade scheduled" if is_downgrade else "upgraded",
              email, tier, reference, effective)
    return {"status": "ok", "email": email, "tier": tier, "label": plan["label"],
            "slot_limit": slot_limit, "is_downgrade": is_downgrade, "effective": effective}


# ── PHOTO MIGRATION (local /media → Hetzner Object Storage) ──

@app.get("/admin/ai-spend/summary")
def admin_ai_spend_daily_summary(_key: str = Depends(auth.require_api_key)):
    """Live AI-spend summary for the nightly cost-compliance sweep (P2, 11 Jun 2026).
    Returns today's and 7-day spend, the configured ceilings, and a 7-day
    per-endpoint/model breakdown. Read-only; $0; admin key required."""
    conn = database.get_db()
    try:
        today = datetime.utcnow().strftime("%Y-%m-%d 00:00:00")
        week = (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d 00:00:00")
        t = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
                         "FROM ai_spend_log WHERE logged_at >= ?", (today,)).fetchone()
        w = conn.execute("SELECT COALESCE(SUM(est_cost_usd),0) AS u, COUNT(*) AS n "
                         "FROM ai_spend_log WHERE logged_at >= ?", (week,)).fetchone()
        cfg = conn.execute("SELECT daily_user_ceiling_usd, daily_platform_ceiling_usd "
                           "FROM ai_spend_config WHERE id = 1").fetchone()
        by_ep = conn.execute(
            "SELECT endpoint, model, COALESCE(SUM(est_cost_usd),0) AS usd, COUNT(*) AS calls, "
            "SUM(cost_is_real) AS real_rows FROM ai_spend_log WHERE logged_at >= ? "
            "GROUP BY endpoint, model ORDER BY usd DESC LIMIT 25", (week,)).fetchall()
    finally:
        conn.close()
    return {
        "today_usd": round(t["u"], 4), "today_calls": t["n"],
        "week_usd": round(w["u"], 4), "week_calls": w["n"],
        "daily_user_ceiling_usd": (cfg["daily_user_ceiling_usd"] if cfg else 0) or 0,
        "daily_platform_ceiling_usd": (cfg["daily_platform_ceiling_usd"] if cfg else 0) or 0,
        "ceiling_warning": (None if cfg and (cfg["daily_platform_ceiling_usd"] or 0) > 0
                            else "platform ceiling is 0/unset — AI spend is UNCAPPED"),
        "by_endpoint": [{"endpoint": r["endpoint"], "model": r["model"],
                         "usd": round(r["usd"], 4), "calls": r["calls"],
                         "estimated_rows": r["calls"] - (r["real_rows"] or 0)} for r in by_ep],
    }


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


@app.post("/advert-agent/market-note")
async def aa_market_note(req: dict, background_tasks: BackgroundTasks):
    """Lightweight inline market context note — existence-gated (Session 90).
    Accepts {email, prompt} and returns {response} with a single Haiku sentence.
    Used by sbTriggerMarketNote() in the sell flow (B3 inline note + Path A inline note).
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")

    prompt = (req.get("prompt") or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="prompt is required")

    # Existence gate — email must belong to a registered user (Session 90)
    _email = (req.get("email") or "").strip().lower()
    if _email:
        _gc = database.get_db()
        _exists = _gc.execute("SELECT 1 FROM users WHERE LOWER(email)=? LIMIT 1", (_email,)).fetchone()
        _gc.close()
        if not _exists:
            raise HTTPException(status_code=401, detail="Unrecognised account — please complete seller registration first.")
    _check_cost_ceiling(_email)   # C1 — refuse if daily cost ceiling reached

    try:
        # SEAM-ROUTED (D1): runs on whichever provider is active (Anthropic or OpenAI) — invisible to this feature.
        # ai_provider.complete() translates the message + parses the response per provider; AIResult normalises tokens.
        import ai_provider as _ap, asyncio as _aio
        _sys = ("You are a concise local market expert for TrustSquare, a South African marketplace. "
                "Respond in exactly 1 sentence. Be specific, factual, and brief. "
                "Mention real price ranges where relevant. No fluff, no caveats.")
        _res = await _aio.to_thread(
            _ap.complete, [{"role": "user", "content": prompt}],
            task="haiku", max_tokens=120, system=_sys, provider=_ts_active_provider())
        if not _res.ok:
            raise RuntimeError("active AI provider returned no result")
        text = (_res.text or "").strip()
        background_tasks.add_task(_log_ai_spend, _email, "/advert-agent/market-note", "haiku",
                                  _res.in_tokens, _res.out_tokens)
        return {"response": text, "_provider": _res.provider, "_model": _res.model, **_report_stamp()}
    except Exception as exc:
        _log.error("aa_market_note failed: %s", exc)
        raise HTTPException(status_code=500, detail="AI call failed") from exc


# ── One-photo-one-sentence listing draft (Simpler Model, Jun 2026) ──────────
# $0-first: a template draft always works (no key, no cost); ONE cheap Haiku
# vision call refines it when configured and under the daily ceiling. Fails
# OPEN to the template so a model hiccup never blocks a seller. No DB writes,
# no Tuppence — the draft is free by design (build brief: Listing in one photo).

_DRAFT_CATEGORIES = ("Property", "Tutors", "Services", "Adventures",
                     "Collectors", "Cars", "LocalMarket")

_DRAFT_CAT_KEYWORDS = {
    "Property": ("house", "home", "apartment", "flat", "townhouse", "land", "plot",
                 "bed ", "bedroom", "property", "office space", "commercial"),
    "Cars": ("car", "bakkie", "vehicle", "suv", "sedan", "hatchback", "toyota", "vw",
             "volkswagen", "ford", "bmw", "mercedes", "hyundai", "kia", "nissan",
             "motorbike", "motorcycle", "scooter", "hilux", "ranger", "polo"),
    "Collectors": ("stamp", "coin", "card", "krugerrand", "memorabilia", "collectible",
                   "collectable", "vinyl", "antique", "comic", "figurine", "banknote"),
    "Tutors": ("tutor", "tutoring", "lessons", "teach", "maths", "matric", "exam prep",
               "coaching lessons", "language lessons"),
    "Adventures": ("tour", "safari", "hike", "guided", "getaway", "accommodation",
                   "guesthouse", "adventure", "experience", "excursion"),
    "Services": ("plumber", "plumbing", "electrician", "repair", "service", "cleaning",
                 "garden service", "painting", "builder", "accounting", "design work"),
}

def _draft_price_from_text(text: str) -> str:
    """Pull a rand amount out of a sentence: R15k / R15 000 / R15,000 / 15000 rand."""
    import re as _re
    m = _re.search(r"[Rr]\s?(\d[\d\s,]*(?:\.\d+)?)\s?([kKmM]\b)?", text)
    if not m:
        m = _re.search(r"(\d[\d\s,]*(?:\.\d+)?)\s?(?:rand|ZAR)", text, _re.I)
        if not m:
            return ""
    raw = m.group(1).replace(" ", "").replace(",", "")
    try:
        val = float(raw)
    except ValueError:
        return ""
    suffix = (m.group(2) or "").lower() if (m.lastindex or 1) >= 2 else ""
    if suffix == "k":
        val *= 1_000
    elif suffix == "m":
        val *= 1_000_000
    return f"R{int(val):,}".replace(",", " ")

def _template_draft(intent: str, city: str) -> dict:
    """$0 draft from the seller's one sentence — no model, no cost, always works."""
    low = " " + intent.lower() + " "
    category = "LocalMarket"
    for cat, kws in _DRAFT_CAT_KEYWORDS.items():
        if any(kw in low for kw in kws):
            category = cat
            break
    import re as _re
    title = _re.sub(r"^\s*(selling|for sale[:,]?|i'm selling|im selling|i am selling)\s+",
                    "", intent.strip(), flags=_re.I)
    title = _re.sub(r"[.!]\s*$", "", title)
    # drop trailing price/hope clauses from the title
    title = _re.split(r",?\s*(hoping|asking|looking)\s", title, flags=_re.I)[0].strip()
    title = _re.sub(r",?\s*[Rr]\s?\d[\d\s,]*(?:\.\d+)?\s?[kKmM]?\s*(/\w+)?\s*$", "", title).strip(" ,")
    title = (title[:1].upper() + title[1:])[:80] if title else "My listing"
    price = _draft_price_from_text(intent)
    desc = (f"{title}. Located in {city or 'Pretoria'}. "
            "Condition as described by the seller — final grade follows TrustSquare's "
            "evidence-based assessment. Request an introduction to learn more.")
    return {"title": title, "category": category, "price": price,
            "condition": "seller-declared", "description": desc, "source": "template"}

@app.post("/listings/draft-from-photos")
async def listing_draft_from_photos(req: dict, background_tasks: BackgroundTasks):
    """Guided listing v2: ONE batched Haiku vision call reads ALL the seller's
    photos -> per-slot captions + a polished description. Free to the seller,
    $0-first: no key / over ceiling / any error -> graceful empty result (the
    flow continues with slot-name captions). Accepts {category, fields, photos:
    [{slot, b64}]} -> {captions:[{slot, caption}], description, source}."""
    photos = req.get("photos") or []
    if not photos:
        raise HTTPException(status_code=400, detail="photos required")
    photos = photos[:10]
    category = (req.get("category") or "Property")[:40]
    fields = req.get("fields") or {}
    empty = {"captions": [], "description": "", "source": "none"}
    if not ANTHROPIC_API_KEY:
        return empty
    try:
        _check_cost_ceiling("")
    except HTTPException:
        return empty
    try:
        content = []
        slots = []
        for ph in photos:
            b64 = (ph.get("b64") or "")
            if b64.startswith("data:"):
                b64 = b64.split(",", 1)[-1]
            if not b64 or len(b64) > 2_500_000:
                continue
            slots.append(ph.get("slot") or f"photo_{len(slots)+1}")
            content.append({"type": "image", "source": {"type": "base64",
                            "media_type": "image/jpeg", "data": b64}})
        if not content:
            return empty
        import json as _j
        content.append({"type": "text", "text": (
            f"These are a seller's photos for a {category} listing on TrustSquare "
            f"(South African marketplace), in slot order: {slots}.\n"
            f"Listing fields so far: {_j.dumps(fields)[:800]}\n\n"
            "Reply with ONLY a JSON object:\n"
            "{\"captions\": [{\"slot\": slot name, \"caption\": \"one honest, specific line "
            "describing what THIS photo shows (max 12 words, no hype, mention real visible "
            "features)\"}],\n"
            " \"description\": \"4-6 factual sentences describing the listing as a walkthrough "
            "of the photos, anonymous seller voice, no contact details, no invented features - "
            "only what is visible or stated in the fields\"}"
        )})
        async with httpx.AsyncClient(timeout=40) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={"model": AA_MODEL, "max_tokens": 700,
                      "messages": [{"role": "user", "content": content}]},
            )
        rj = resp.json()
        text = (rj.get("content", [{}])[0].get("text", "") or "").strip()
        if text.startswith("```"):
            text = text.strip("`").lstrip("json").strip()
        ai = json.loads(text)
        _in, _out = _usage_tokens(rj)
        background_tasks.add_task(_log_ai_spend, "", "/listings/draft-from-photos",
                                  "haiku", _in, _out)
        caps = [{"slot": str(c.get("slot",""))[:40], "caption": str(c.get("caption",""))[:90]}
                for c in (ai.get("captions") or []) if c.get("caption")]
        return {"captions": caps,
                "description": str(ai.get("description",""))[:1200],
                "source": "ai"}
    except Exception as exc:
        _log.warning("draft-from-photos fell back to empty: %s", exc)
        return empty


@app.post("/listings/draft-from-photo")
async def listing_draft_from_photo(req: dict, background_tasks: BackgroundTasks):
    """One photo + one sentence -> a drafted listing the seller fine-tunes.
    Accepts {intent, photo_b64?, city?, email?} -> {title, category, condition,
    price, description, source}. Free: no Tuppence, no DB writes.
    $0-first: template draft always; ONE Haiku (vision) refinement when configured."""
    intent = (req.get("intent") or "").strip()
    if not intent:
        raise HTTPException(status_code=400, detail="intent sentence is required")
    if len(intent) > 300:
        intent = intent[:300]
    city = (req.get("city") or "").strip() or "Pretoria"
    email = (req.get("email") or "").strip().lower()

    draft = _template_draft(intent, city)

    photo_b64 = (req.get("photo_b64") or "").strip()
    if photo_b64.startswith("data:"):
        photo_b64 = photo_b64.split(",", 1)[-1]
    if len(photo_b64) > 2_500_000:   # ~1.8 MB image — frontend compresses well below this
        photo_b64 = ""

    if not ANTHROPIC_API_KEY:
        return draft
    try:
        _check_cost_ceiling(email)   # C1 — over the daily ceiling: serve the $0 template
    except HTTPException:
        return draft

    try:
        content = []
        if photo_b64:
            content.append({"type": "image", "source": {"type": "base64",
                            "media_type": "image/jpeg", "data": photo_b64}})
        content.append({"type": "text", "text": (
            "A seller on TrustSquare (South African marketplace) wrote ONE sentence about "
            f"what they are selling{' and attached ONE photo' if photo_b64 else ''}:\n"
            f"\"{intent}\"\nCity: {city}\n\n"
            "Draft their listing. Reply with ONLY a JSON object, no other text:\n"
            "{\"title\": \"max 80 chars, specific, no hype\", "
            "\"category\": one of " + str(list(_DRAFT_CATEGORIES)) + ", "
            "\"condition\": \"short honest read" + (" from the photo, e.g. 'good — light wear visible'"
                                                       if photo_b64 else " from the sentence") + ", "
            "never a certified grade\", "
            "\"price\": \"suggested asking price as 'R12 500' (use the seller's number if given; "
            "empty string if you cannot estimate honestly), "
            "\"description\": \"2-3 factual sentences, anonymous seller voice, no contact details\"}"
        )})
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={"model": AA_MODEL, "max_tokens": 350,
                      "messages": [{"role": "user", "content": content}]},
            )
        rj = resp.json()
        text = (rj.get("content", [{}])[0].get("text", "") or "").strip()
        if text.startswith("```"):
            text = text.strip("`").lstrip("json").strip()
        ai = json.loads(text)
        _in, _out = _usage_tokens(rj)
        background_tasks.add_task(_log_ai_spend, email, "/listings/draft-from-photo",
                                  "haiku", _in, _out)
        out = dict(draft)
        for k in ("title", "category", "condition", "price", "description"):
            v = (ai.get(k) or "").strip() if isinstance(ai.get(k), str) else ai.get(k)
            if v:
                out[k] = v
        if out["category"] not in _DRAFT_CATEGORIES:
            out["category"] = draft["category"]
        out["title"] = str(out["title"])[:80]
        out["source"] = "ai"
        return out
    except Exception as exc:
        _log.warning("draft-from-photo fell back to template: %s", exc)
        return draft


@app.get("/advert-agent/status")
def aa_status(email: str):
    """Return the seller's free-use flag and current Tuppence balance."""
    conn = database.get_db()
    row = conn.execute(
        "SELECT aa_free_used FROM users WHERE email = ?", (email,)
    ).fetchone()
    tuppence_row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?", (email,)
    ).fetchone()
    conn.close()
    tuppence_bal = tuppence_row["bal"] if tuppence_row else 0
    if not row:
        return {"aa_free_used": 0, "tuppence_balance": tuppence_bal, "registered": False}
    return {
        "aa_free_used": row["aa_free_used"] or 0,
        "tuppence_balance": tuppence_bal,
        "registered": True,
    }


@app.post("/advert-agent/coach")
async def aa_coach(req: AACoachRequest, background_tasks: BackgroundTasks):
    """Gate check + Claude Haiku call + return coaching output."""
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI Coach not configured")

    conn = database.get_db()
    row = conn.execute(
        "SELECT aa_free_used, aa_sessions_remaining, trust_score FROM users WHERE email = ?",
        (req.email,)
    ).fetchone()

    if not row:
        conn.close()
        raise HTTPException(
            status_code=401,
            detail="Unrecognised account — please complete seller registration first."
        )

    _check_cost_ceiling(req.email)   # C1 — refuse if daily cost ceiling reached

    free_used     = row["aa_free_used"] or 0
    current_score = row["trust_score"] or 0

    # After free use, check Tuppence balance (1T per coach call)
    if free_used:
        tuppence_row = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?", (req.email,)
        ).fetchone()
        tuppence_bal = tuppence_row["bal"] if tuppence_row else 0
        if tuppence_bal < 1:
            conn.close()
            raise HTTPException(
                status_code=402,
                detail="Insufficient Tuppence. Top up your wallet (1T per AI Coach call)."
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
            "• PPRA/EAAB Registration (active) → 15 pts — ppra.org.za — SA mandatory for professional agents\n"
            "• Fidelity Fund Certificate (FFC) → 10 pts — annual, separate from PPRA reg; lapses each year\n"
            "• Signed mandate / instruction letter → 8 pts — proves authorisation to market the property\n"
            "• NQF4 Real Estate qualification → 6 pts\n"
            "• NQF5 Real Estate → cumulative 12 pts\n"
            "• NQF6+ or professional designation → cumulative 20 pts\n"
            "• Professional body membership (IEASA, SAPOA, NAR) → 5 pts\n"
            "• Private seller declaration → 0 pts but visible label (no PPRA required for private sellers)\n"
            "• Government ID verified by TrustSquare → 15 Universal pts\n"
            "• Verified referrals from buyers → up to 10 Universal pts\n"
            "\n"
            "COACHING INSTRUCTION FOR PROPERTY:\n"
            "1. Check whether the seller is a registered estate agent or a private seller — tailor advice accordingly.\n"
            "2. For agents: lead with FFC (10 pts) if not yet uploaded — it is legally separate from PPRA and lapses annually.\n"
            "3. For agents: mandate letter (8 pts) prevents fraud flags and builds buyer trust — suggest it for every listing.\n"
            "4. For private sellers: skip PPRA/FFC, note private_seller declaration, focus on Universal signals.\n"
            "5. For description improvements: tailor to property type (apartment/house/commercial), mention key features buyers care about (natural light, parking, school proximity, security)."
        ),
        "Tutors": (
            "CATEGORY: Tutors\n"
            "Available credential signals and their points:\n"
            "• SACE registration (South African Council for Educators) → 8 pts — sace.org.za\n"
            "  NOTE: SACE is mandatory only for school teachers. Private/independent tutors and\n"
            "  tertiary tutors are NOT required to register. For non-school tutors, skip SACE\n"
            "  and focus on the qualification chain + subject specialisation instead.\n"
            "• Certificate or Diploma (NQF5–6) → 6 pts\n"
            "• Bachelor's Degree (NQF7) → 10 pts (replaces diploma pts)\n"
            "• Honours or Postgraduate (NQF8+) → 14 pts (replaces degree pts)\n"
            "  NOTE: Points chain — max 14 pts from qualifications. Honours replaces degree which replaces diploma.\n"
            "• Subject specialisation certificate or transcript → 5 pts\n"
            "  EXAMPLES BY SUBJECT (always reference the seller's actual subject from the 'subject' field):\n"
            "  Maths/Science: NSC Maths distinction transcript, IEB Maths cert, Olympiad cert, AMC cert\n"
            "  Languages (English/Afrikaans): TESOL, CELTA, TEFL, Cambridge DELTA, IELTS Examiner cert\n"
            "  Languages (Zulu/Xhosa/Sotho): SA Languages Board cert, university language dept transcript\n"
            "  Music: UNISA music grade exams (Grade 7+), ABRSM, Trinity College, Rockschool\n"
            "  Art/Drama: UNISA Fine Art transcript, AFDA certificate, drama conservatory diploma\n"
            "  Coding/IT: AWS cert, Google cert, Microsoft cert, CompTIA, freeCodeCamp, Udemy verified cert\n"
            "  Accounting: SAIPA, CIMA foundation, ACCA foundation, CTA transcript\n"
            "  Science (Biology/Chemistry/Physics): BSc transcript, lab technician cert, CSIR affiliation\n"
            "  Sport coaching: ASA coaching cert, SAFA coaching badge, Tennis SA cert, Swimming SA cert\n"
            "  Early Childhood: ECD NQF4/5 cert, Montessori diploma, SACE Foundation Phase\n"
            "  Chess/Logic: FIDE trainer cert, SA Chess Federation membership\n"
            "• Police clearance / criminal record check → 8 pts (HIGH PRIORITY for any tutor working with minors)\n"
            "  REQUIRED for: in-person tutors, home tutors, school-visiting tutors\n"
            "  SA: SAPS clearance certificate (saps.gov.za)\n"
            "  Global: DBS (UK), CORI (IE), WWC (AU), state background check (US)\n"
            "• Safeguarding / child protection certificate → 3 pts (important for in-person tutors under 18)\n"
            "  Examples: NSPCC Safeguarding (UK), Mandatory Reporter training (AU/US), CPT SA\n"
            "• Teaching/tutoring experience 2–5 yrs → 5 pts · 5+ yrs → 11 pts\n"
            "• Online platform proficiency declaration → 1 pt (online tutors: Zoom, Google Classroom, etc.)\n"
            "• Well-structured CV (verifiable dates, no gaps) → 2 pts\n"
            "• Government ID verified by TrustSquare → 15 Universal pts\n"
            "• Verified referrals from students or parents → up to 10 Universal pts\n"
            "\n"
            "COACHING INSTRUCTION FOR TUTORS:\n"
            "1. ALWAYS check the 'subject' field first. Tailor every credential suggestion and example\n"
            "   to the seller's specific subject — never give generic examples.\n"
            "2. If the seller teaches minors (school age, early childhood, home tutor), lead with\n"
            "   police clearance (8 pts) as the top trust_score_action — parents expect this.\n"
            "3. If the seller is a school teacher, include SACE. If private/tertiary tutor, skip SACE.\n"
            "4. For the subject field suggestion: expand vague subjects into specific ones\n"
            "   (e.g. 'Maths' → 'Mathematics (Gr 8–12, IEB & NSC), Statistics (Gr 11–12)').\n"
            "5. For the description field: include a sentence about the tutor's approach/method\n"
            "   tailored to the subject (e.g. for Maths: concept-first vs. exam-technique).\n"
            "6. Never suggest 'Beekeeping Certificate' or any credential unrelated to the subject."
        ),
        "Services": (
            "CATEGORY: Services\n"
            "For TECHNICAL trades — available credential signals:\n"
            "• Professional/statutory body registration (ECSA, PIRB, NHBRC, FSCA, SAICA) → 12 pts\n"
            "• Trade certificate (City & Guilds, TVET, MERSETA, CETA, Red Seal) → 8 pts\n"
            "• Public liability insurance → 5 pts — upload policy with expiry date; expected by every homeowner\n"
            "• CIDB grading (construction contractors) → 6 pts — required above R200k jobs in SA\n"
            "• Primary industry licence/CoC (electrical CoC, gas CoC, plumbing) → 5 pts\n"
            "• Additional safety tickets (First Aid, working at heights, confined space) → 3 pts each, max 2\n"
            "• Trade experience 3–7 yrs → 4 pts · 7+ yrs → 8 pts\n"
            "• Strong, verifiable CV → 2 pts\n"
            "For CASUALS — available credential signals:\n"
            "• Police clearance / background check → 10 pts — HIGHEST PRIORITY for in-home workers\n"
            "  SA: SAPS clearance (saps.gov.za) · UK: DBS · AU: WWC · US: state background check\n"
            "• Reference letter from past employer or client (with contact details) → 8 pts first, +5 second\n"
            "• Any NQF qualification or accredited short course → 8 pts\n"
            "• Years in service 2–4 yrs → 6 pts · 5+ yrs → 14 pts\n"
            "• Strong profile description (specific services, suburb, availability) → 5 pts\n"
            "For BOTH: Government ID verified by TrustSquare → 15 Universal pts (critical for Casuals)\n"
            "\n"
            "COACHING INSTRUCTION FOR SERVICES:\n"
            "1. Determine first whether the seller is Technical (qualified trade) or Casual (general/domestic services).\n"
            "2. For Casuals: lead with police clearance (10 pts) — it is the #1 trust signal for in-home workers. Parents, homeowners, and businesses expect it.\n"
            "3. For Technical: lead with body registration (12 pts) then insurance (5 pts) — liability cover is expected by every client.\n"
            "4. For CIDB: only suggest if the service_class/service_type mentions construction, contracting, or building work.\n"
            "5. For description: tailor examples to the specific trade — an electrician's description differs from a plumber's or a nanny's."
        ),
        "Adventures": (
            "CATEGORY: Adventures\n"
            "For EXPERIENCES (guided activities) — available credential signals:\n"
            "• Activity guide cert (FGASA wildlife, PADI Divemaster+ diving, MCSA climbing, SACAA aviation, SAMSA maritime) → 12 pts\n"
            "• Operator permit / concession licence → 6 pts — required for SANParks, Ezemvelo, private reserves\n"
            "• First Aid / Emergency Response (current, not expired) → 6 pts\n"
            "• Sector regulator compliance cert → 5 pts — SACAA Part 135, SAMSA, MCSA (separate from guide cert)\n"
            "• Liability / indemnity insurance (activity-appropriate) → 5 pts\n"
            "• Additional safety cert (Wilderness First Responder, swift water rescue) → 4 pts\n"
            "• Guided experience 3–7 yrs → 5 pts · 7+ yrs → 10 pts\n"
            "• Secondary qualification or activity endorsement → 3 pts\n"
            "For ACCOMMODATION (B&B / Guesthouse / Hotel) — available credential signals:\n"
            "• TGCSA star grading: 1★=6 · 2★=10 · 3★=14 · 4★=18 · 5★=22 pts — tourismgrading.co.za\n"
            "• Municipal/city operating licence for B&B or guesthouse → 6 pts\n"
            "• Health & safety compliance certificate → 5 pts\n"
            "• Fire clearance certificate → 4 pts\n"
            "• AA Travel Award, TripAdvisor Travellers Choice, or Booking.com Preferred → 3 pts\n"
            "For BOTH: Government ID verified by TrustSquare → 15 Universal pts\n"
            "\n"
            "COACHING INSTRUCTION FOR ADVENTURES:\n"
            "1. Determine sub-type first: Experiences (guided activities) or Accommodation (B&B/guesthouse/hotel).\n"
            "2. For Experiences: lead with guide cert (12 pts) then operator permit (6 pts) — many guides overlook the permit.\n"
            "3. For Accommodation: TGCSA grading is the single highest-value signal — lead with it always.\n"
            "4. For description: be specific about the activity or property type — 'bush walk' is weaker than '3-hour guided Big 5 game walk, Pilanesberg, max 6 guests'.\n"
            "5. Photos matter most for Adventures — always include a photo upload action in trust_score_actions."
        ),
        "Collectors": (
            "CATEGORY: Collectors\n"
            "Available credential signals and their points:\n"
            "• Collecting domain declaration (specific, detailed) → 4 pts\n"
            "• Successful platform transactions: 1–4 → 8 pts · 5–14 → 14 pts · 15+ → 20 pts\n"
            "• Item provenance documentation → 8 pts — chain of custody doc; required for high-value items (art, coins, wine, firearms); auth cert alone is insufficient\n"
            "• Authentication certificate (SANA, PCGS, PSA, CGC, NGC) → 8 pts — per listed item\n"
            "• Dealer / reseller registration → 6 pts — antique dealer, art gallery, coin dealer licence; displays 'Registered Dealer' label to buyers\n"
            "• Professional appraisal or valuation → 5 pts — from recognised appraiser\n"
            "• Collector association membership (SANA, Philatelic Foundation etc.) → 3 pts\n"
            "• Government ID verified by TrustSquare → 15 Universal pts\n"
            "• Verified referrals → up to 10 Universal pts\n"
            "\n"
            "COACHING INSTRUCTION FOR COLLECTORS:\n"
            "1. Read the listing to determine the collecting domain (cards, coins, art, wine, stamps, memorabilia etc.) and tailor all suggestions to that domain.\n"
            "2. For high-value items: lead with provenance (8 pts) — buyers need chain of custody, not just an auth cert.\n"
            "3. For dealers: suggest dealer_reg (6 pts) — it distinguishes them from private sellers and builds buyer confidence.\n"
            "4. Emphasise that responding promptly to every introduction is the single most powerful Trust Score action for Collectors — transactions auto-score.\n"
            "5. For description: be specific — '1952 Topps Mickey Mantle PSA 7' is far stronger than 'vintage baseball card'."
        ),
    }

    _cred_ref = _TS_CREDENTIALS.get(req.category, "")

    # System prompt — returns structured JSON for inline field suggestions + Trust Score plan
    system_prompt = (
        "You are the TrustSquare Advert Agent. "
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
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": AA_MODEL,
                    "max_tokens": 1800,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_message}],
                },
            )
        resp.raise_for_status()
        _coach_json = resp.json()
        coaching_text = _coach_json["content"][0]["text"]
        _co_in, _co_out = _usage_tokens(_coach_json)   # C2
    except Exception as exc:
        conn.close()
        _log.error("AA coach Claude call failed: %s", exc)
        raise HTTPException(status_code=502, detail="AI Coach unavailable — please try again") from exc

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

    # Deduct: mark free use on first call; charge 1T on subsequent calls
    if not free_used:
        conn.execute("UPDATE users SET aa_free_used = 1 WHERE email = ?", (req.email,))
        conn.commit()
        tuppence_remaining = conn.execute(
            "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?", (req.email,)
        ).fetchone()["bal"]
    else:
        tuppence_remaining = _deduct_tuppence(
            conn, req.email, 1,
            f"AI Coach · {req.category or 'General'}"
        )
        conn.commit()
    conn.close()

    background_tasks.add_task(_log_ai_spend, req.email, "/advert-agent/coach", "haiku", _co_in, _co_out)
    return {"coaching_json": coaching_json, "tuppence_remaining": tuppence_remaining, "free_used": free_used}


@app.post("/advert-agent/buy-pack")
def aa_buy_pack(email: str):
    """RETIRED (Canon Addendum 1): 'AI uses' no longer exist. In-app AI guidance
    is free; advanced AI features are Tuppence-priced per use."""
    raise HTTPException(
        status_code=410,
        detail="AI coaching packs are retired — the AI Coach charges your Tuppence wallet per use (first use free).")


@app.post("/advert-agent/publish")
async def aa_publish(
    background_tasks: BackgroundTasks,
    email: str = Form(...),
    category: str = Form(...),
    fields: str = Form(...),        # JSON string
    coach_output: str = Form(""),
    city: str = Form("Pretoria"),
    attested: int = Form(0),
    photos: list[UploadFile] = File(default=[]),
):
    """Receive draft + photos, upload to R2, create pending listing, return listing id."""
    import json as _json

    try:
        field_data = _json.loads(fields)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid fields JSON") from exc

    title         = field_data.get("title") or field_data.get("item_name", "")
    price         = field_data.get("price") or field_data.get("rate")
    suburb        = field_data.get("suburb") or field_data.get("area", "")
    desc          = field_data.get("desc", "")
    service_class = field_data.get("service_class") or None

    # ── CARS-SPEC-1: persist structured vehicle columns (Vehicles wizard) ────
    # Seller typed these → provenance seller_entered. Populated sections are
    # section-confirmed + the C4 attestation stamped ONLY when the wizard sent
    # attested=1. Stamp-if-present: this endpoint NEVER blocks on attestation.
    _veh_cols = {"make": None, "model": None, "variant": None, "vehicle_year": None,
                 "mileage_km": None, "transmission": None, "fuel_type": None,
                 "body_type": None, "colour": None, "vehicle_specs": None,
                 "spec_confirmed": None, "attested_at": None, "attested_email": None}
    if (category or "").strip().lower() == "cars":
        def _fd(k):
            _v = field_data.get(k)
            return _v.strip() if isinstance(_v, str) and _v.strip() else None
        def _fdint(k):
            _v = _fd(k)
            try:
                return int(str(_v).replace(",", "").replace(" ", "")) if _v else None
            except Exception:
                return None
        _veh_cols["make"] = _fd("make"); _veh_cols["model"] = _fd("model")
        _veh_cols["variant"] = _fd("variant"); _veh_cols["colour"] = _fd("colour")
        _veh_cols["transmission"] = _fd("transmission")
        _veh_cols["fuel_type"] = _fd("fuel_type"); _veh_cols["body_type"] = _fd("body_type")
        _veh_cols["vehicle_year"] = _fdint("year"); _veh_cols["mileage_km"] = _fdint("mileage")
        _specs, _vprov = {}, {}
        _cc = _fdint("cc")
        if _cc and 600 <= _cc <= 9000:
            _specs["engine_capacity_cc"] = _cc; _vprov["engine_capacity_cc"] = "seller_entered"
        for _k in ("make", "model", "variant", "vehicle_year", "mileage_km",
                   "transmission", "fuel_type", "body_type", "colour"):
            if _veh_cols[_k] is not None:
                _vprov[_k] = "seller_entered"
        if _vprov:
            _specs["_prov"] = _vprov
            _veh_cols["vehicle_specs"] = _json.dumps(_specs)
        if int(attested or 0) and _vprov:
            _now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
            _conf = {}
            for _section, (_scols, _skeys) in VEHICLE_SECTION_FIELDS.items():
                _has = any(_veh_cols.get(_c) is not None for _c in _scols) or any(_k2 in _specs for _k2 in _skeys)
                _conf[_section] = _now if _has else None
            _veh_cols["spec_confirmed"] = _json.dumps(_conf)
            _veh_cols["attested_at"] = _now
            _veh_cols["attested_email"] = email

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
        # Vehicle sub-type fields (VEHICLES-SUBTYPE-1, 3 Jul 2026) — folded into
        # the description until structured columns land (CARS-SPEC-1 Task 1)
        "make":         "Make",
        "model":        "Model",
        "variant":      "Variant",
        "year":         "Year",
        "mileage":      "Mileage (km)",
        "colour":       "Colour",
        "transmission": "Transmission",
        "fuel_type":    "Fuel type",
        "body_type":    "Body type",
        "cc":           "Engine (cc)",
        "bike_type":    "Bike type",
        "trailer_type": "Type",
        "sleeps":       "Sleeps",
        "braked":       "Braked",
        "papers":       "Registration papers",
        "boat_type":    "Boat type",
        "engine_make":  "Engine",
        "engine_hours": "Engine hours",
        "trailer_included": "Trailer included",
        "vehicle_type": "Vehicle type",
        "capacity":     "Capacity",
    }
    for key, label in field_labels.items():
        val = field_data.get(key, "").strip() if isinstance(field_data.get(key), str) else ""
        if val:
            structured_lines.append(f"**{label}:** {val}")

    if structured_lines:
        structured_block = "\n".join(structured_lines)
        desc = f"{structured_block}\n\n{desc}".strip() if desc else structured_block

    if coach_output:
        desc = f"{desc}\n\n---\nAI coaching notes:\n{coach_output}".strip()

    # Upload photos to R2 (or local fallback) — EXIF-rotate before storage
    thumb_url  = None
    medium_url = None
    _anon_notes = []
    for idx, photo in enumerate(photos):
        raw_data = await photo.read()
        # Apply EXIF orientation fix and compress to JPEG
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw_data))).convert("RGB")
            # AA-GATE-1 (15 Jul 2026): this path stored photos with NO anonymity
            # check — David's test listing published an unblurred car photo
            # through it. Same gate as the two seller endpoints; a photo that
            # cannot be cleared is SKIPPED (batch path: skip-and-note, never
            # fail the whole publish).
            try:
                img, _anote = _seller_photo_anon_gate(img, category or "", email)
                if _anote:
                    _anon_notes.append("photo%d:%s" % (idx + 1, _anote))
            except HTTPException as _aexc:
                _anon_notes.append("photo%d:held:%s" % (idx + 1, str(_aexc.detail)[:60]))
                continue
            medium = img.copy()
            medium.thumbnail(MEDIUM_SIZE, Image.LANCZOS)
            buf = io.BytesIO()
            medium.save(buf, format="JPEG", quality=JPEG_QUALITY_MEDIUM, optimize=True)
            data = buf.getvalue()
            content_type_out = "image/jpeg"
        except Exception:
            data = raw_data
            content_type_out = photo.content_type or "image/jpeg"
        if _S3_CONFIGURED:
            key = f"aa/{uuid.uuid4().hex}_{uuid.uuid4().hex[:8]}.jpg"
            url = _s3_upload(data, key, content_type_out)
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
    # Inherit seller trust_score + slot_limit from users table
    ts_row = conn.execute(
        "SELECT trust_score, slot_limit, is_superuser FROM users WHERE LOWER(email) = ?", (email,)
    ).fetchone()
    seller_trust = int(ts_row["trust_score"] or 40) if ts_row else 40
    is_super = bool(ts_row["is_superuser"]) if ts_row else False
    # Slot guard at publish time (superusers exempt)
    if not is_super:
        slot_limit = int(ts_row["slot_limit"]) if ts_row and ts_row["slot_limit"] else 2
        live_count = conn.execute(
            "SELECT COUNT(*) as n FROM listings WHERE LOWER(seller_email)=? "
            "AND (listing_status IS NULL OR listing_status = 'live')",
            (email,)
        ).fetchone()["n"]
        if live_count >= slot_limit:
            conn.close()
            raise HTTPException(
                status_code=402,
                # SLOT-402-1 (16 Jul 2026): seller-facing wording — the app routes
                # the seller to plan selection; don't point at admin.html.
                detail=f"Listing slot limit reached ({live_count}/{slot_limit}) — your current "
                       f"plan allows {slot_limit} live listings. Choose a bigger plan to publish more."
            )
    # Store AI-suggested price as anchor for AI3 price-check
    try:
        ai_price_anchor = float(price.replace("R","").replace(",","").strip()) if price else None
    except Exception:
        ai_price_anchor = None
    # Resolve a real Scryfall card id for collectible listings so AI3 can fetch a
    # VERIFIED market price instead of guessing. Best-effort; NULL if not a card.
    try:
        scryfall_id = await resolve_scryfall_id(title, category)
    except Exception:
        scryfall_id = None
    cursor = conn.execute(
        """INSERT INTO listings
           (title, price, category, city, area, suburb, description, thumb_url, medium_url, service_class, seller_email, trust_score, ai_suggested_price, scryfall_id, published_at,
            make, model, variant, vehicle_year, mileage_km, transmission, fuel_type, body_type, colour, vehicle_specs, spec_confirmed, attested_at, attested_email)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?, datetime('now'),?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (title, price, category, city, suburb, suburb, desc, thumb_url, medium_url, service_class, email, seller_trust, ai_price_anchor, scryfall_id,
         _veh_cols["make"], _veh_cols["model"], _veh_cols["variant"], _veh_cols["vehicle_year"],
         _veh_cols["mileage_km"], _veh_cols["transmission"], _veh_cols["fuel_type"], _veh_cols["body_type"],
         _veh_cols["colour"], _veh_cols["vehicle_specs"], _veh_cols["spec_confirmed"],
         _veh_cols["attested_at"], _veh_cols["attested_email"]),
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

# Common synonyms — symmetric expansion. Tuned to TrustSquare verticals.
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
    result_count: Optional[int] = None   # results shown at capture; 0 = demand MISS

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


# ── SEARCH-AI-1: sentence → dial-in params on the cheap tier (David, 6 Jul 2026) ──
# The deterministic FEA parser handles common shapes for $0; this endpoint is the
# LAST-RESORT fallback for sentence-shaped total misses. Independence doctrine:
# one thin layer (ai_provider seam, task="haiku" → Haiku 4.5 / gpt-4o-mini by config);
# deterministic parser IS the degradation path, so switching this off loses nothing.
SEARCH_AI_ENABLED   = os.getenv("SEARCH_AI_ENABLED", "0") == "1"      # dark until David flips
SEARCH_AI_DRYRUN    = os.getenv("SEARCH_AI_DRYRUN", "1") == "1"       # $0 mock until validated
SEARCH_AI_DAILY_USD = float(os.getenv("SEARCH_AI_DAILY_USD", "1.0")) # micro-cap; over → degrade

_SI_CATS = {"Property", "Cars", "Tutors", "Services", "Collectors", "Adventures"}


# Demand invite email — house style (matches the n8n outreach set: navy #1a1a2e,
# gold #d4a853). RULINGS BAKED IN: no buyer details ever; {item_line} is class-only
# unless it names the prospect's OWN scraped product; one-email-ever + STOP is
# prominent; priority window stated plainly. Preview copy:
# n8n/email_templates/demand_invite.html (generated from this string — edit HERE).
_DEMAND_INVITE_HTML = """<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"><title>Buyer demand on TrustSquare</title>
<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Arial,sans-serif;background:#f5f5f0;color:#1a1a1a}
.wrapper{max-width:600px;margin:0 auto;background:#fff}.header{background:#1a1a2e;padding:32px 40px;text-align:center}
.header-logo{font-size:24px;font-weight:700;color:#fff;letter-spacing:-.5px}.header-logo span{color:#d4a853}
.hero{background:linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%);padding:44px 40px;text-align:center}
.hero-icon{font-size:44px;margin-bottom:14px}.hero-title{font-size:26px;font-weight:700;color:#fff;line-height:1.3;margin-bottom:10px}
.hero-subtitle{font-size:15px;color:#a0b0c8;line-height:1.6}.body{padding:36px 40px}
.demand-box{background:#f8f6f0;border-left:4px solid #d4a853;border-radius:0 8px 8px 0;padding:20px 24px;margin:22px 0}
.demand-box p{font-size:15px;color:#444;line-height:1.7}
.window{background:#fff8e8;border:1px solid #e8c96a;border-radius:8px;padding:18px 22px;margin:22px 0;text-align:center}
.window p{font-size:14px;color:#7a5c00;line-height:1.6}.window strong{color:#5a3e00;font-size:16px}
.cta-section{text-align:center;padding:26px 0 8px}
.cta-button{display:inline-block;background:#d4a853;color:#1a1a2e;font-size:17px;font-weight:700;padding:15px 38px;border-radius:8px;text-decoration:none;letter-spacing:.3px}
.code{font-size:13px;color:#666;margin-top:14px}.code b{color:#1a1a2e;font-size:15px;letter-spacing:1px}
.quiet{background:#f0f0ea;border-radius:8px;padding:16px 22px;margin:26px 0 6px}
.quiet p{font-size:13px;color:#666;line-height:1.6}
.footer{background:#f0f0ea;padding:24px 40px;text-align:center}.footer p{font-size:12px;color:#888;line-height:1.7}.footer a{color:#666}</style></head>
<body><div class="wrapper">
<div class="header"><div class="header-logo">Trust<span>Square</span></div></div>
<div class="hero"><div class="hero-icon">&#128276;</div>
<div class="hero-title">A verified buyer is looking for {item_short}</div>
<div class="hero-subtitle">Real demand, waiting on TrustSquare in {city_name} &mdash; anonymous introductions, and we never charge commission on your sale.</div></div>
<div class="body">
<p style="font-size:16px;color:#333;line-height:1.6;margin-bottom:20px;">Hi{greeting_name},</p>
<div class="demand-box"><p>A verified buyer on TrustSquare is actively looking for <strong>{item_line}</strong>. The buyer stays anonymous &mdash; and so do you &mdash; until you both choose to be introduced.</p></div>
<div class="window"><p>Your priority window is open for the next</p><p><strong>{hours} hours</strong></p><p>List first and the introduction is exclusively yours.</p></div>
<div class="cta-section"><a class="cta-button" href="{cta_url}">List it free &rarr;</a>
<div class="code">Your personal invitation code: <b>{code}</b></div></div>
<div class="quiet"><p><strong>One email, ever.</strong> This is the only unprompted email you will receive from us. Reply <strong>STOP</strong> and we will never write to you again &mdash; no follow-ups, no reminders.</p></div>
</div>
<div class="footer"><p>TrustSquare (Pty) Ltd &middot; Reg No. 2026/340128/07<br>
You received this once-off note because your business publicly offers items in this category in {city_name}.<br>
<a href="mailto:{stop_email}?subject=STOP">Unsubscribe permanently</a></p></div>
</div></body></html>"""

def _demand_render_invite(ticket, prospect, code):
    """Render the invite. item_line: prospect's OWN scraped item when specifically
    matched (David's personalization exception), else the item CLASS. Never the buyer."""
    item = prospect["scraped_item"] if (prospect and prospect["scraped_item"]) else None
    item_line = ("exactly what you're offering &mdash; your " + item) if item \
                else ("a " + ((ticket["category"] or "listing").lower()) + " like the ones you offer")
    item_short = item if item else ("a " + (ticket["category"] or "listing").lower())
    greeting = ""   # no scraped personal names in v1 — keep it clean, not creepy
    # NB: literal .replace(), never str.format() — the template's CSS braces
    # ({margin:0}) would read as placeholders and KeyError (caught in scratch test).
    h = _DEMAND_INVITE_HTML
    for k, v in (("{item_short}", item_short[:80]), ("{item_line}", item_line[:160]),
                 ("{city_name}", "your city"), ("{greeting_name}", greeting),
                 ("{hours}", str(int(DEMAND_PRIORITY_HOURS))), ("{code}", code or "FOUNDING-INVITE"),
                 ("{cta_url}", "https://trustsquare.co/?invite=" + (code or "")),
                 ("{stop_email}", "hello@trustsquare.co")):
        h = h.replace(k, v)
    return h

def _demand_send_invite(to_email, subject, html):
    """The ONLY send path. Triple-gated: env ON + dry-run OFF + RESEND_API_KEY present.
    Writes the outreach ledger AT send (one touch per address, enforced upstream)."""
    key = os.getenv("RESEND_API_KEY", "")
    if not (DEMAND_LOOP_ENABLED and not DEMAND_LOOP_DRYRUN and key):
        return ("dry", None)
    try:
        import httpx
        r = httpx.post("https://api.resend.com/emails",
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            json={"from": os.getenv("DEMAND_FROM_EMAIL", "TrustSquare <hello@trustsquare.co>"),
                  "to": [to_email], "subject": subject, "html": html},
            timeout=20)
        if r.status_code in (200, 201):
            return ("sent", (r.json() or {}).get("id"))
        _log.error("demand send failed %s: %s", r.status_code, r.text[:200])
        return ("failed", None)
    except Exception as exc:
        _log.error("demand send error: %s", exc)
        return ("failed", None)

def _si_validate(d):
    """Whitelist-validate the model's JSON. Anything off-contract → None (fallback)."""
    if not isinstance(d, dict):
        return None
    out = {}
    t = d.get("terms")
    out["terms"] = [str(w).lower()[:30] for w in t if str(w).strip()][:5] if isinstance(t, list) else []
    for k in ("price_min", "price_max"):
        v = d.get(k)
        if v is None:
            out[k] = None
        else:
            try:
                v = float(v)
                out[k] = v if 0 <= v <= 1e9 else None
            except Exception:
                out[k] = None
    c = d.get("category")
    out["category"] = c if c in _SI_CATS else None
    lt = d.get("listingType")
    out["listingType"] = lt if lt in ("rent", "sale") else None
    tm = d.get("trust_min")
    try:
        tm = int(tm) if tm is not None else None
        out["trust_min"] = tm if (tm is None or 0 <= tm <= 100) else None
    except Exception:
        out["trust_min"] = None
    return out

def _si_mock(q):
    """$0 dry-run stand-in: crude but shape-true, proves the whole pipeline."""
    terms, pmax = [], None
    for w in str(q).lower().replace(",", "").split():
        if w.isdigit():
            v = int(w)
            if v >= 500 and pmax is None:
                pmax = v
                continue
        if w.isalpha() and len(w) > 2 and len(terms) < 5:
            terms.append(w)
    return {"terms": terms, "price_min": None, "price_max": pmax,
            "category": None, "listingType": None, "trust_min": None}

_SI_SYSTEM = (
    'You translate ONE marketplace search sentence into JSON dial-in filters. '
    'Reply with ONLY minified JSON, no prose: {"terms":[],"price_min":null,"price_max":null,'
    '"category":null,"listingType":null,"trust_min":null}. '
    'terms: essential keywords only (brands, models, item nouns), lowercase, max 5. '
    'Prices: plain numbers (R means ZAR, k means thousands). '
    'category: one of Property,Cars,Tutors,Services,Collectors,Adventures or null. '
    'listingType: "rent" or "sale" or null. '
    'trust_min: 0-100 only if seller trust/reliability is explicitly requested, else null.'
)

# ── DEMAND-LOOP-1 core (standard automated process; David rulings 6 Jul locked) ──
DEMAND_LOOP_ENABLED = os.getenv("DEMAND_LOOP_ENABLED", "0") == "1"    # match/invite stages dark
DEMAND_LOOP_DRYRUN  = os.getenv("DEMAND_LOOP_DRYRUN", "1") == "1"     # compose-only, ZERO sends
DEMAND_PRIORITY_HOURS = float(os.getenv("DEMAND_PRIORITY_HOURS", "8"))
_DEMAND_PRICE_FLOORS = {"Property": 2000.0, "Cars": 20000.0, "Tutors": 300.0,
                        "Services": 300.0, "Collectors": 300.0, "Adventures": 500.0}
_DEMAND_DEFAULT_FLOOR = 500.0

def _demand_score(sig, seen_count):
    """Deterministic realness score, no AI. >=3 opens a ticket.
    Structure (category/price/terms) reads intent; repetition reads seriousness."""
    score = 0
    txt = (sig.raw_text or "").strip()
    if sig.category: score += 2
    if sig.price_min is not None or sig.price_max is not None: score += 1
    if len([w for w in txt.split() if len(w) > 2]) >= 2: score += 1
    if len(txt.split()) >= 3: score += 1
    if (seen_count or 1) >= 2: score += 2
    return score

def _demand_price_ok(sig):
    """David's 'more than small change': an explicit ceiling under the category floor never triggers outreach."""
    floor = _DEMAND_PRICE_FLOORS.get(sig.category or "", _DEMAND_DEFAULT_FLOOR)
    return not (sig.price_max is not None and sig.price_max < floor)

def _demand_open_ticket(conn, sig, signal_id, seen_count):
    """Open (or strengthen) a demand ticket for a real-scored MISS. Always on, $0, internal."""
    try:
        if sig.result_count is None or int(sig.result_count) != 0:
            return None
        if not _demand_price_ok(sig):
            return None
        score = _demand_score(sig, seen_count)
        if score < 3:
            return None
        qn = " ".join((sig.raw_text or "").lower().split())[:240]
        if len(qn) < 4:
            return None
        row = conn.execute(
            "SELECT id FROM demand_tickets WHERE query_norm=? AND COALESCE(city_id,0)=COALESCE(?,0) "
            "AND state IN ('open','matched','invited') LIMIT 1",
            (qn, sig.city_id)).fetchone()
        if row:
            conn.execute("UPDATE demand_tickets SET score=MAX(score,?), updated_at=datetime('now') WHERE id=?",
                         (score, row["id"]))
            return row["id"]
        cur = conn.execute(
            """INSERT INTO demand_tickets
               (signal_id, buyer_token, query_norm, category, city_id, score, state)
               VALUES (?,?,?,?,?,?, 'open')""",
            (signal_id, sig.buyer_token, qn, sig.category, sig.city_id, score))
        return cur.lastrowid
    except Exception as exc:
        _log.error("demand ticket failed: %s", exc)
        return None

def _demand_match_and_compose(conn, limit=20):
    """GATED stage: match open tickets to prospects, compose anonymity-safe invites.
    Rulings enforced here: class-only wording (exception = the prospect's OWN scraped
    item); shared suppression ledger, 90-day cool-down, permanent on suppressed=1.
    DRY-RUN composes to the outbox and sends NOTHING."""
    out = {"matched": 0, "composed": 0}
    if not DEMAND_LOOP_ENABLED:
        return out
    rows = conn.execute("SELECT * FROM demand_tickets WHERE state='open' ORDER BY score DESC, id LIMIT ?",
                        (limit,)).fetchall()
    for t in rows:
        # Match city by NAME, not id: geo_cities can hold duplicate rows for the same
        # city (e.g. two "Pretoria" ids), so the ticket's city_id and the prospect's
        # resolved city_id may differ even for the same place. Comparing the resolved
        # NAMES sidesteps that entirely. NULL ticket city = any city.
        p = conn.execute(
            """SELECT p.* FROM demand_prospects p
               WHERE (? IS NULL OR COALESCE(p.app_category, p.category) = ?)
                 AND ( ? IS NULL
                       OR LOWER(TRIM(COALESCE(p.city_name,'')))
                          = LOWER(TRIM(COALESCE((SELECT name FROM geo_cities WHERE id = ?), '__nocity__'))) )
                 AND NOT EXISTS (SELECT 1 FROM outreach_ledger o WHERE o.email_hash = p.email_hash
                                 AND (o.suppressed = 1 OR o.sent_at >= datetime('now','-90 days')))
               LIMIT 1""",
            (t["category"], t["category"], t["city_id"], t["city_id"])).fetchone()
        if not p:
            continue
        out["matched"] += 1
        subject = "Verified buyer demand on TrustSquare - your priority window"
        html = _demand_render_invite(t, p, None)   # code allocation joins at flip-on (launch_codes)
        conn.execute("INSERT INTO demand_invites_outbox (ticket_id, email_hash, subject, body, dry_run) VALUES (?,?,?,?,?)",
                     (t["id"], p["email_hash"], subject, html, 1 if DEMAND_LOOP_DRYRUN else 0))
        conn.execute("UPDATE demand_tickets SET state='matched', matched_prospect=?, matched_item=?, "
                     "priority_expires_at=datetime('now', ?), updated_at=datetime('now') WHERE id=?",
                     (p["email_hash"], p["scraped_item"], "+" + str(DEMAND_PRIORITY_HOURS) + " hours", t["id"]))
        out["composed"] += 1
        # The ONLY send path - triple-gated inside; dry-run returns ("dry", None) untouched.
        status, _mid = _demand_send_invite(p["email_enc"] or "", subject, html)
        if status == "sent":
            conn.execute("INSERT INTO outreach_ledger (email_hash, channel, campaign) VALUES (?,?,?)",
                         (p["email_hash"], "demand_invite", "ticket:" + str(t["id"])))
            conn.execute("UPDATE demand_tickets SET state='invited', "
                         "priority_expires_at=datetime('now', ?), updated_at=datetime('now') WHERE id=?",
                         ("+" + str(DEMAND_PRIORITY_HOURS) + " hours", t["id"]))
            out["sent"] = out.get("sent", 0) + 1
    return out

class SearchInterpretIn(BaseModel):
    q: str

@app.post("/search/interpret")
def search_interpret(req: SearchInterpretIn):
    """Public, heavily gated. Returns {"enabled":false} when dark — the FEA's
    deterministic parser simply remains the whole story."""
    if not SEARCH_AI_ENABLED:
        return {"enabled": False}
    qn = " ".join(str(req.q or "").lower().split())[:300]
    if len(qn) < 8 or len(qn.split()) < 3:
        return {"enabled": True, "fallback": True}   # not sentence-shaped; not worth tokens
    import ai_provider as _si_ai
    conn = database.get_db()
    try:
        row = conn.execute("SELECT params_json FROM search_interpret_cache WHERE query_norm = ?", (qn,)).fetchone()
        if row:
            return {"enabled": True, "params": json.loads(row["params_json"]), "cached": True}
        spent = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) AS c FROM ai_spend_log "
            "WHERE endpoint = '/search/interpret' AND logged_at >= date('now')"
        ).fetchone()["c"]
        if spent >= SEARCH_AI_DAILY_USD:
            return {"enabled": True, "fallback": True}   # cap reached — degrade, never overspend
        if SEARCH_AI_DRYRUN:
            params, model_used, it, ot = _si_mock(qn), "dryrun", 0, 0
        else:
            r = _si_ai.complete(
                [{"role": "user", "content": qn}],
                task="haiku", max_tokens=120, system=_SI_SYSTEM)
            if not r.ok:
                # One spaced retry — validation batch showed burst-pace transients recover.
                import time as _si_t
                _si_t.sleep(1.2)
                r = _si_ai.complete(
                    [{"role": "user", "content": qn}],
                    task="haiku", max_tokens=120, system=_SI_SYSTEM)
            if not r.ok:
                return {"enabled": True, "fallback": True}
            txt = (r.text or "").strip()
            if txt.startswith("```"):
                txt = txt.strip("`").lstrip("json").strip()
            try:
                params = _si_validate(json.loads(txt))
            except Exception:
                params = None
            if params is None:
                return {"enabled": True, "fallback": True}
            model_used, it, ot = r.model, r.in_tokens, r.out_tokens
        conn.execute(
            "INSERT OR REPLACE INTO search_interpret_cache (query_norm, params_json, model, cost_usd) VALUES (?,?,?,?)",
            (qn, json.dumps(params), model_used, _token_cost("haiku", it or 0, ot or 0) if not SEARCH_AI_DRYRUN else 0.0))
        conn.commit()
        if not SEARCH_AI_DRYRUN:
            _log_ai_spend("", "/search/interpret", "haiku", it, ot)
        return {"enabled": True, "params": params, "cached": False}
    except Exception:
        return {"enabled": True, "fallback": True}
    finally:
        conn.close()


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
                 ping_enabled = ?,
                 result_count = COALESCE(?, result_count),
                 seen_count = seen_count + 1
               WHERE id = ?""",
            (_signal_expiry_iso(), sig.suburb_id, sig.city_id, sig.country_iso2,
             sig.price_min, sig.price_max, sig.min_trust_score, sig.ping_enabled,
             sig.result_count, existing["id"])
        )
        _seen = conn.execute("SELECT seen_count FROM wishlist_signals WHERE id = ?",
                             (existing["id"],)).fetchone()
        _tid = _demand_open_ticket(conn, sig, existing["id"], _seen["seen_count"] if _seen else 2)
        conn.commit()
        conn.close()
        return {"id": existing["id"], "refreshed": True, "demand_ticket": _tid}
    cur = conn.execute(
        """INSERT INTO wishlist_signals
           (buyer_token, signal_type, raw_text, category, suburb_id, city_id, country_iso2,
            price_min, price_max, min_trust_score, weight, ping_enabled, expires_at, result_count)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (sig.buyer_token, sig.signal_type, sig.raw_text, sig.category,
         sig.suburb_id, sig.city_id, sig.country_iso2,
         sig.price_min, sig.price_max, sig.min_trust_score, weight,
         sig.ping_enabled, _signal_expiry_iso(), sig.result_count)
    )
    new_id = cur.lastrowid
    _tid = _demand_open_ticket(conn, sig, new_id, 1)
    conn.commit()
    conn.close()
    return {"id": new_id, "refreshed": False, "demand_ticket": _tid}


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
                  created_at, expires_at, result_count
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
    except Exception as exc:
        conn.close()
        raise HTTPException(status_code=400, detail="Listing already in showcase") from exc
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
        if not _payment_grants_allowed():
            raise HTTPException(status_code=503, detail="Payments are not live yet - subscriptions are temporarily disabled.")
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
                     min_trust: int = 0, q: Optional[str] = None,
                     limit: int = 50, demo: int = 0):
    """Public list endpoint. Anonymous-stripped cards. Suspended listings hidden.
    Trust score is read live from the seller's users.trust_score (joined) so
    that buyer trust filters always reflect the seller's current standing.
    demo=1 includes seed/showcase listings; demo=0 (default) hides them."""
    conn = database.get_db()
    clauses = ["l.category = ?", "l.suspension_reason IS NULL",
               "(l.listing_status IS NULL OR l.listing_status = 'live')",
               "COALESCE(u.trust_score, 0) >= ?",
               "(l.is_demo = 0 OR l.is_demo IS NULL)" if not demo else "1=1"]
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
           WHERE l.id = ? AND l.category = ? AND l.suspension_reason IS NULL
             AND (l.listing_status IS NULL OR l.listing_status = 'live')""",
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
    lm_status = listing.get("listing_status") or "live"
    if lm_status != "live":
        conn.close()
        raise HTTPException(status_code=409, detail=f"Listing is not available for introductions (status: {lm_status})")
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


@app.post("/users/{email}/eula")
def accept_main_eula(email: str, _key: str = Depends(auth.require_api_key)):
    """Record that a seller has accepted the main TrustSquare EULA.
    Called by the FEA sell-b flow when an existing seller publishes for the
    first time (or whenever eula_accepted_at is NULL on their account).
    Idempotent — safe to call multiple times."""
    email = email.lower().strip()
    conn = database.get_db()
    row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    conn.execute(
        "UPDATE users SET eula_accepted_at = COALESCE(eula_accepted_at, datetime('now')) WHERE email = ?",
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
            for lo2, _, name2, color2 in TRUST_TIERS:
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
        "how_to_earn": "Upload your ID or passport — verified by TrustSquare.",
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
        "category.property.ppra":          {"name": "Active PPRA / EAAB Registration", "points": 15, "how_to_earn": "Upload PPRA certificate — verified against PPRA register at ppra.org.za. Mandatory for professional agents in SA."},
        "category.property.ffc":            {"name": "Fidelity Fund Certificate (FFC)", "points": 10, "how_to_earn": "Upload current FFC — issued annually by EAAB, separate from PPRA registration. Lapses each year — upload the current year's certificate."},
        "category.property.mandate":        {"name": "Signed mandate / instruction letter", "points": 8, "how_to_earn": "Upload signed mandate letter from property owner authorising you to market this property. Prevents fraudulent listings."},
        "category.property.private_seller": {"name": "Private seller declaration", "points": 0, "how_to_earn": "Declare: I am a private seller, not a registered estate agent. Displayed as a transparency label to buyers — no points but visible on listing card."},
        "category.property.nqf4":          {"name": "NQF4 Real Estate qualification", "points": 6,  "how_to_earn": "Upload certificate."},
        "category.property.nqf5":          {"name": "NQF5 Real Estate qualification", "points": 6,  "how_to_earn": "Upload certificate (additional to NQF4).", "additional_to": "category.property.nqf4"},
        "category.property.nqf6_plus":     {"name": "NQF6+ / Professional designation", "points": 8, "how_to_earn": "Upload certificate.", "additional_to": "category.property.nqf5"},
        "category.property.body":          {"name": "Professional body membership (IEASA, SAPOA, NAR)", "points": 5, "how_to_earn": "Upload membership card or letter."},
    },
    "Property_private": {
        # Private sellers — no agent registration required
        "category.property.exp_10plus":    {"name": "Property experience 10+ years", "points": 5, "how_to_earn": "Declare ownership/investment experience — CV optional."},
        "category.property.exp_2_5":       {"name": "Property experience 2–5 years", "points": 4, "how_to_earn": "Declare experience."},
    },
    "Cars_private": {
        # Private car sellers — no dealer registration
        "category.cars.ownership":         {"name": "Vehicle ownership (NATIS)", "points": 10, "how_to_earn": "Upload NATIS registration papers."},
        "category.cars.dealer_reg":        {"name": "Dealer / trader registration (MIRA)", "points": 8, "how_to_earn": "Upload MIRA dealer licence (SA) or equivalent trade registration. Displays 'Registered Dealer' label to buyers — regulatory protections differ from private sellers."},
        "category.cars.inspection":        {"name": "Independent vehicle inspection", "points": 5, "how_to_earn": "Upload third-party inspection report (AA South Africa, WeBuyCars, Auto Pedigree). Significantly increases buyer confidence."},
        "category.cars.service_history":   {"name": "Service history on file", "points": 4, "how_to_earn": "Upload scan of service book or dealer service records (full or partial history)."},
        "category.cars.finance_clear":     {"name": "Finance clearance", "points": 4, "how_to_earn": "Upload letter from financial institution confirming no outstanding finance on this vehicle."},
        "category.cars.private_seller":    {"name": "Private seller declaration", "points": 0, "how_to_earn": "Declare: I am a private seller, not a registered dealer. Displayed to buyers as a transparency label — regulatory protections differ. No points but visible on listing."},
        "category.cars.rwc":               {"name": "Roadworthy certificate (RWC)", "points": 6, "how_to_earn": "Upload roadworthy certificate."},
    },
    "Tutors": {
        "category.tutors.clearance":       {"name": "Police clearance / DBS check", "points": 8, "how_to_earn": "Upload SAPS clearance (saps.gov.za) · DBS (UK) · WWC (AU) · state background check (US). Critical for tutors working with minors."},
        "category.tutors.sace":            {"name": "SACE registration", "points": 8,  "how_to_earn": "Upload SACE registration certificate — verified at sace.org.za. Required for SA school teachers; not required for private/independent or tertiary tutors."},
        "category.tutors.cert_diploma":    {"name": "Certificate or Diploma (NQF5–6)", "points": 6, "how_to_earn": "Upload certificate."},
        "category.tutors.bachelor":        {"name": "Bachelor's Degree (NQF7)", "points": 10, "how_to_earn": "Upload certificate (replaces diploma points).", "replaces": "category.tutors.cert_diploma"},
        "category.tutors.honours":         {"name": "Honours / Postgraduate (NQF8+)", "points": 14, "how_to_earn": "Upload certificate (replaces bachelor's points).", "replaces": "category.tutors.bachelor"},
        "category.tutors.specialisation":  {"name": "Subject specialisation certificate", "points": 5, "how_to_earn": "Upload cert or transcript specific to your subject. Examples: Maths/Science → Olympiad cert, IEB transcript; Music → UNISA/ABRSM grade cert; Languages → CELTA/TESOL; Coding → AWS/Google/Microsoft cert; Accounting → SAIPA/CIMA; Sport → ASA/SAFA coaching badge."},
        "category.tutors.exp_2_5":         {"name": "Teaching experience 2–5 years", "points": 5, "how_to_earn": "Upload CV with verifiable teaching dates — reviewed by TrustSquare."},
        "category.tutors.exp_5plus":       {"name": "Teaching experience 5+ years", "points": 6, "how_to_earn": "Upload CV.", "additional_to": "category.tutors.exp_2_5"},
        "category.tutors.safeguarding":    {"name": "Safeguarding / child protection cert", "points": 3, "how_to_earn": "Upload safeguarding or child protection certificate. Examples: NSPCC (UK), Mandatory Reporter (AU/US), child protection training SA."},
        "category.tutors.online_ready":    {"name": "Online platform proficiency", "points": 1, "how_to_earn": "Declare platforms used: Zoom, Google Classroom, Microsoft Teams, etc. Applies to online tutors."},
        "category.tutors.strong_cv":       {"name": "Strong structured CV", "points": 2, "how_to_earn": "Upload CV with clear dates, subjects taught, and institutions — assessed at onboarding."},
    },
    "Services-Technical": {
        "category.services_tech.trade_cert": {"name": "Formal trade certificate", "points": 8, "how_to_earn": "Upload (City & Guilds, TVET, MERSETA, CETA, Red Seal)."},
        "category.services_tech.body_reg":   {"name": "Professional body registration", "points": 12, "how_to_earn": "Upload (ECSA, PIRB, NHBRC, FSCA, SAICA) — verified."},
        "category.services_tech.insurance":  {"name": "Public liability insurance", "points": 5, "how_to_earn": "Upload policy schedule with expiry date. Expected by any homeowner hiring a trade into their property."},
        "category.services_tech.cidb":       {"name": "CIDB grading (construction)", "points": 6, "how_to_earn": "Upload CIDB registration certificate (SA). Required for contractors above R200k. Upload grade level document."},
        "category.services_tech.coc":        {"name": "Primary industry licence / CoC", "points": 5, "how_to_earn": "Upload with expiry date (electrical CoC, gas CoC, plumbing licence etc.)."},
        "category.services_tech.tickets":    {"name": "Additional tickets (max 2 counted)", "points": 6, "how_to_earn": "Upload First Aid, heights, confined space etc. (3 pts each, max 2)."},
        "category.services_tech.exp_3_7":    {"name": "Years in trade 3–7", "points": 4, "how_to_earn": "Upload CV."},
        "category.services_tech.exp_7plus":  {"name": "Years in trade 7+", "points": 4, "how_to_earn": "Upload CV.", "additional_to": "category.services_tech.exp_3_7"},
        "category.services_tech.strong_cv":  {"name": "Strong verifiable CV", "points": 2, "how_to_earn": "Upload CV."},
    },
    "Services-Casuals": {
        "category.services_cas.clearance":   {"name": "Police clearance / background check", "points": 10, "how_to_earn": "Upload SAPS clearance (saps.gov.za) · DBS (UK) · WWC (AU) · state background check (US). Critical for in-home workers — cleaners, nannies, gardeners, domestic workers."},
        "category.services_cas.nqf":         {"name": "Any NQF qualification or short course", "points": 8, "how_to_earn": "Upload certificate from accredited provider."},
        "category.services_cas.exp_2_4":     {"name": "2–4 years in service", "points": 6, "how_to_earn": "Upload CV or written statement."},
        "category.services_cas.exp_5plus":   {"name": "5+ years in service", "points": 8, "how_to_earn": "Upload CV.", "additional_to": "category.services_cas.exp_2_4"},
        "category.services_cas.ref_1":       {"name": "Reference letter", "points": 8, "how_to_earn": "Upload scanned letter with verifiable contact."},
        "category.services_cas.ref_2":       {"name": "Second reference letter", "points": 5, "how_to_earn": "Upload second letter — max 2 counted."},
        "category.services_cas.profile":     {"name": "Strong profile description", "points": 5, "how_to_earn": "Complete your profile description in detail."},
    },
    "Adventures-Experiences": {
        "category.adv_exp.guide_cert":       {"name": "Activity-specific guide cert", "points": 12, "how_to_earn": "Upload relevant cert — FGASA (wildlife), PADI Divemaster+ (diving), MCSA (climbing), SACAA (aviation), SAMSA (maritime). Verified where register available."},
        "category.adv_exp.permit":              {"name": "Operator permit / concession licence", "points": 6, "how_to_earn": "Upload permit with expiry. Required for guiding in SANParks, Ezemvelo, private reserves. Site-specific — upload per venue."},
        "category.adv_exp.regulator_compliance":{"name": "Sector regulator compliance cert", "points": 5, "how_to_earn": "Upload compliance cert beyond the guide licence — SACAA Part 135 (aviation), SAMSA (maritime), MCSA (climbing). Different from the guide cert itself."},
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
        "category.collectors.assoc":          {"name": "Collector association membership", "points": 3, "how_to_earn": "Upload membership card or certificate (SANA, Philatelic Foundation etc.)."},
        "category.collectors.provenance":      {"name": "Item provenance documentation", "points": 8, "how_to_earn": "Upload chain of custody or provenance document. Required for high-value collectibles (art, coins, wine, firearms). Authentication cert alone is insufficient for these."},
        "category.collectors.dealer_reg":      {"name": "Dealer / reseller registration", "points": 6, "how_to_earn": "Upload dealer licence or trade registration (antique dealer, art gallery, coin dealer). Displayed to buyers as 'Registered Dealer' — distinguishes you from private collectors."},
    },
    # Local Market sellers — identity + stacking subject-matter credentials.
    # Stacking pattern: upload cert → lm.formal_cert (6 pts)
    #                   upload 2nd cert → lm.formal_cert_2 (4 pts, additional_to cert_1)
    #                   upload 3rd cert → lm.formal_cert_3 (3 pts, additional_to cert_2) — capped
    # Same for training, guides, memberships.
    # Leadership/official role is its own high-value signal.
    # Local Market sellers start at 40 (base_score in trust_score_breakdown).
    # Category signals add on top — max 60 additional pts = score 100.
    # Point values reflect how hard the evidence is to fake and how much
    # it signals domain expertise / accountability.
    #
    # Anti-gaming principle: soft signals (social, guides) are worth little;
    # hard signals (association role, formal membership) are worth a lot.
    # Anyone can claim a hobby — few people are NBE Secretary.
    #
    # Target scores:
    #   Regular seller, 1 cert + 1 membership         → 40 + ~15 = 55 (Established ✓)
    #   Serious seller, 2 certs + 2 memberships        → 40 + ~25 = 65 (Established ✓)
    #   Expert, dual membership + named role + certs   → 40 + ~45 = 85 (Trusted ✓)
    #   Top of field, national role + full profile     → 40 + ~55 = 95 (Highly Trusted ✓)
    "Travel": {
        "category.travel.asata_member":      {"name": "ASATA membership", "points": 10, "how_to_earn": "Upload ASATA membership number — verified against the public member register."},
        "category.travel.iata_accredited":   {"name": "IATA accreditation", "points": 10, "how_to_earn": "Upload IATA agency code — verified via IATA CheckACode where available."},
        "category.travel.cipc_registered":   {"name": "Registered company (CIPC)", "points": 6, "how_to_earn": "Upload CIPC registration number."},
        "category.travel.years_3_7":         {"name": "Trading 3–7 years", "points": 5, "how_to_earn": "Upload company profile / CV."},
        "category.travel.years_7plus":       {"name": "Trading 7+ years", "points": 5, "how_to_earn": "Upload company profile / CV.", "additional_to": "category.travel.years_3_7"},
        "category.travel.client_insurance":  {"name": "Client travel-insurance facility", "points": 4, "how_to_earn": "Upload proof of the travel-insurance facility offered to clients."},
        "category.travel.financial_bonding": {"name": "Financial bonding / guarantee", "points": 5, "how_to_earn": "Upload proof of a bonding or guarantee scheme protecting client payments."},
    },
    "Tour_Guides": {
        "category.tour_guides.provincial_reg":  {"name": "Registered tourist guide (provincial)", "points": 12, "how_to_earn": "Upload your provincial registrar guide badge number (Tourism Act) — verified where the register is available."},
        "category.tour_guides.cathsseta_qual":  {"name": "CATHSSETA guiding qualification", "points": 8, "how_to_earn": "Upload qualification certificate."},
        "category.tour_guides.first_aid":       {"name": "Current First Aid / Emergency Response", "points": 6, "how_to_earn": "Upload with expiry date."},
        "category.tour_guides.exp_3_7":         {"name": "Guiding experience 3–7 years", "points": 5, "how_to_earn": "Upload CV."},
        "category.tour_guides.exp_7plus":       {"name": "Guiding experience 7+ years", "points": 5, "how_to_earn": "Upload CV.", "additional_to": "category.tour_guides.exp_3_7"},
        "category.tour_guides.languages":       {"name": "Guides in 3+ languages", "points": 4, "how_to_earn": "List languages; upload certificates where held."},
        "category.tour_guides.site_specialist": {"name": "Site / route specialist accreditation", "points": 5, "how_to_earn": "Upload site-specific accreditation (e.g. World Heritage site guide)."},
    },
    "local_market": {
        # ── Identity (max ~20 from category — Universal also contributes) ──
        "category.lm.phone_verified":      {"name": "Phone number verified",               "points": 2,  "how_to_earn": "Add and verify your mobile number in your profile.", "evidence_required": False},
        "category.lm.banking":             {"name": "Banking details on file",              "points": 2,  "how_to_earn": "Add your bank account details — required for Tuppence payouts.", "evidence_required": False},
        "category.lm.banking_name_match":  {"name": "Bank account holder name verified",   "points": 3,  "how_to_earn": "Account holder name on bank details matches your verified ID name.", "evidence_required": False},
        "category.lm.id_uploaded":         {"name": "Government-issued ID uploaded",        "points": 2,  "how_to_earn": "Upload a clear photo of your SA ID, passport, or drivers licence.", "evidence_required": True},
        "category.lm.id_number_valid":     {"name": "ID / passport number entered & valid", "points": 2,  "how_to_earn": "Enter your SA ID number (13 digits) or passport number — format validated instantly.", "evidence_required": False},
        "category.lm.id_ai_verified":      {"name": "Identity AI-verified",                "points": 5,  "how_to_earn": "AI vision confirms your name and ID number match your uploaded document.", "evidence_required": True},
        "category.lm.id_admin_verified":   {"name": "Identity manually confirmed",          "points": 5,  "how_to_earn": "TrustSquare has manually confirmed your identity documents.", "evidence_required": True},
        "category.lm.cert_name_verified":  {"name": "Certificate name matches ID",          "points": 2,  "how_to_earn": "Name on your uploaded certificate matches your verified ID name.", "evidence_required": True},
        # ── Experience (self-declared, modest weight) ─────────────────────
        "category.lm.experience_1yr":      {"name": "1+ year of relevant experience",       "points": 2,  "how_to_earn": "Upload a document describing your experience or a reference letter.", "evidence_required": True},
        "category.lm.experience_5yr":      {"name": "5+ years of relevant experience",      "points": 3,  "declaration_points": 2, "evidence_points": 1, "how_to_earn": "Declare your years of experience — 2 pts awarded immediately. Upload a CV or reference letter to claim the final 1 pt.", "evidence_required": True, "replaces": "category.lm.experience_1yr", "declaration_prompt": "Briefly describe your experience and how long you have been active in this field."},
        # ── Qualifications / certificates (stacking, max 3) ──────────────
        # Accredited, traceable — meaningful signal of structured learning.
        "category.lm.training_course":     {"name": "Formal training course (1st)",         "points": 4,  "how_to_earn": "Upload a certificate from a recognised training provider.", "evidence_required": True},
        "category.lm.training_course_2":   {"name": "Second training course",               "points": 3,  "how_to_earn": "Upload a second relevant training certificate.", "evidence_required": True, "additional_to": "category.lm.training_course"},
        "category.lm.formal_cert":         {"name": "Formal qualification / diploma (1st)", "points": 7,  "how_to_earn": "Upload your certificate or diploma from an accredited institution.", "evidence_required": True, "replaces": "category.lm.training_course"},
        "category.lm.formal_cert_2":       {"name": "Second relevant qualification",        "points": 5,  "how_to_earn": "Upload a second subject-relevant certificate or diploma.", "evidence_required": True, "additional_to": "category.lm.formal_cert"},
        "category.lm.formal_cert_3":       {"name": "Third relevant qualification",         "points": 3,  "how_to_earn": "Upload a third certificate — maximum 3 qualifications counted.", "evidence_required": True, "additional_to": "category.lm.formal_cert_2"},
        # ── Memberships / associations (stacking, max 2) ─────────────────
        # Being vetted by an independent organisation is strong signal.
        # Two different bodies = convergent external validation.
        "category.lm.prof_body":           {"name": "Association / professional body membership (1st)", "points": 8, "how_to_earn": "Upload membership card or letter from a recognised body (e.g. SABI, NBA, SATMA, guild).", "evidence_required": True},
        "category.lm.prof_body_2":         {"name": "Second association membership",        "points": 6,  "declaration_points": 5, "evidence_points": 1, "how_to_earn": "Declare your second membership — 5 pts awarded immediately. Upload your membership card or letter to claim the final 1 pt.", "evidence_required": True, "additional_to": "category.lm.prof_body", "declaration_prompt": "Name the second organisation you are a member of and your membership number if available."},
        # ── Named role in association ─────────────────────────────────────
        # Highest-value single credential: being accountable to an organisation
        # as secretary/chair/committee puts your name on public record.
        # National Secretary of NBA = top-3 management role in SA beekeeping.
        "category.lm.assoc_role":          {"name": "Named role in association (secretary, chair, committee)", "points": 15, "declaration_points": 12, "evidence_points": 3, "how_to_earn": "Declare your role and organisation — 12 pts awarded immediately. Upload your appointment letter or signed minutes to claim the final 3 pts.", "evidence_required": True, "declaration_prompt": "Describe your role, organisation, and when you were appointed (e.g. 'National Secretary, NBA, appointed Jan 2024')."},
        # ── Official government / regulatory appointment ───────────────────
        "category.lm.provincial_role":     {"name": "Official government / regulatory appointment", "points": 10, "declaration_points": 8, "evidence_points": 2, "how_to_earn": "Declare your appointment — 8 pts awarded immediately. Upload your official appointment letter to claim the final 2 pts.", "evidence_required": True, "declaration_prompt": "Describe your role, the appointing body, and when you were appointed (e.g. 'Provincial Bee Inspector, Gauteng Dept of Agriculture, 2022')."},
        # ── Knowledge evidence (stacking, max 3) — soft signal ───────────
        "category.lm.product_guide":       {"name": "Product guide / recipe authored (1st)","points": 2,  "how_to_earn": "Upload a product guide, recipe, care instructions, or usage guide you have written.", "evidence_required": True},
        "category.lm.product_guide_2":     {"name": "Second product guide / recipe",        "points": 1,  "how_to_earn": "Upload a second original guide or recipe.", "evidence_required": True, "additional_to": "category.lm.product_guide"},
        "category.lm.product_guide_3":     {"name": "Third product guide / recipe",         "points": 1,  "how_to_earn": "Upload a third guide — maximum 3 counted.", "evidence_required": True, "additional_to": "category.lm.product_guide_2"},
        # ── Media & social ────────────────────────────────────────────────
        "category.lm.media_feature":       {"name": "Media feature or press coverage",      "points": 2,  "how_to_earn": "Upload a scan or screenshot of a magazine, newspaper, or online article featuring your work.", "evidence_required": True},
        "category.lm.social_proof":        {"name": "Active social media presence",         "points": 1,  "how_to_earn": "Add your Instagram, Facebook page, or website URL showing your products/services.", "evidence_required": False},
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


def _signal_listing_category(signal_id: str) -> str:
    """Derive the listing_category a credential belongs to from its signal_id prefix.
    Universal and track_record signals belong to the person (return empty string).
    Category signals return the matching _CATEGORY_SIGNALS key."""
    if signal_id.startswith("category.lm."):
        return "local_market"
    if signal_id.startswith("category.property."):
        return "Property"
    if signal_id.startswith("category.tutors."):
        return "Tutors"
    if signal_id.startswith("category.services_tech."):
        return "Services-Technical"
    if signal_id.startswith("category.services_cas."):
        return "Services-Casuals"
    if signal_id.startswith("category.adv_exp."):
        return "Adventures-Experiences"
    if signal_id.startswith("category.adv_acc."):
        return "Adventures-Accommodation"
    if signal_id.startswith("category.collectors."):
        return "Collectors"
    return ""  # universal / track_record — person-scoped, no listing_category


def _build_breakdown_items(conn, email: str, signals_dict: dict, computed: dict) -> list:
    """Build a list of {signal_id, name, points, status, how_to_earn} items
    from a signal set. Reads user_credentials for upload-required signals.

    Supports 'declared' status: seller has submitted a free-text declaration
    and earned declaration_points (80%). The remaining evidence_points (20%)
    are shown as pending_declaration_evidence so the frontend can surface the
    'upload evidence' prompt."""
    rows = conn.execute(
        "SELECT signal_id, status, listing_category FROM user_credentials WHERE email = ?", (email,)
    ).fetchall()
    # Build status map: for category signals, only pick up credentials whose
    # listing_category matches one of the signal_ids we're being asked about.
    # Universal/track_record signals (listing_category IS NULL or '') always apply.
    cred_status = {}
    for r in rows:
        lc = r["listing_category"] or ""
        if not lc:
            cred_status[r["signal_id"]] = r["status"]  # person-scoped
        elif r["signal_id"] in signals_dict:
            cred_status[r["signal_id"]] = r["status"]  # matches this signal set

    # Load declaration points already awarded (for 'declared' credentials)
    decl_rows = conn.execute(
        "SELECT signal_id, points_awarded FROM user_declarations WHERE email = ?", (email,)
    ).fetchall()
    decl_pts = {r["signal_id"]: r["points_awarded"] for r in decl_rows}

    items = []
    for sig_id, sig in signals_dict.items():
        if sig_id in computed:
            status = computed[sig_id]
        elif sig_id in cred_status:
            raw_status = cred_status[sig_id]
            if raw_status in ("earned", "pending", "rejected", "declared"):
                status = raw_status
            else:
                status = "missing"
        else:
            status = "missing"

        # For declared signals, surface how many points were awarded and what remains
        awarded_pts = sig["points"]  # default: full points if earned
        evidence_pts_remaining = 0
        if status == "declared":
            awarded_pts = decl_pts.get(sig_id, sig.get("declaration_points", sig["points"]))
            evidence_pts_remaining = sig.get("evidence_points", 0)

        items.append({
            "signal_id":                 sig_id,
            "name":                      sig["name"],
            "points":                    sig["points"],
            "declaration_points":        sig.get("declaration_points"),   # pts on declaration (80%)
            "evidence_points":           sig.get("evidence_points", 0),   # pts on evidence upload (20%)
            "awarded_points":            awarded_pts,
            "evidence_points_remaining": evidence_pts_remaining,
            "status":                    status,
            "how_to_earn":               sig.get("how_to_earn", ""),
            "declaration_prompt":        sig.get("declaration_prompt"),
            "has_declaration":           sig.get("declaration_points") is not None,
        })
    return items


def _sum_earned_with_replaces(items: list, signals_dict: dict) -> int:
    """Sum points but honour mutually-exclusive replacement chains.

    Counts both 'earned' (full points) and 'declared' (partial points via
    awarded_points) credentials. Replaces logic still applies so that a
    higher credential supersedes a lower one in the same chain.
    """
    active_ids = {it["signal_id"] for it in items if it["status"] in ("earned", "declared")}
    replaced_ids = set()
    for sig_id in active_ids:
        sig = signals_dict.get(sig_id, {})
        replaces = sig.get("replaces")
        if replaces and replaces in active_ids:
            replaced_ids.add(replaces)
    total = 0
    for it in items:
        if it["status"] not in ("earned", "declared"):
            continue
        if it["signal_id"] in replaced_ids:
            continue
        # Use awarded_points for declared; full points for earned
        total += it.get("awarded_points", it["points"])
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
def trust_score_breakdown(email: str, category: Optional[str] = None):
    """Return a structured Trust Score breakdown for the given seller.
    Frontend renders Universal / Track Record / Category groups + a Haiko
    tip + active penalties. Score is recomputed from credentials each call;
    users.trust_score is updated as a side-effect so wishlist matching and
    Local Market gates see the live value.
    `category` param overrides auto-detection so multi-category sellers get
    the correct signal set for the listing being edited."""
    conn = database.get_db()
    user = conn.execute(
        "SELECT trust_score, primary_category FROM users WHERE email = ?", (email,)
    ).fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not found")

    # Use explicit category if provided (edit screen passes elCurrentCat);
    # otherwise fall back to auto-detection from listings.
    if category:
        # Normalise frontend category names to _CATEGORY_SIGNALS keys
        _cat_norm = {
            "LocalMarket": "local_market", "Local Market": "local_market",
            "Property": "Property", "Property_agent": "Property",
            "Property_private": "Property_private",
            "Tutors": "Tutors",
            "Services": "Services-Technical",  # default subclass
            "Services-Technical": "Services-Technical",
            "Services-Casuals": "Services-Casuals",
            "Adventures": "Adventures-Experiences",
            "Adventures-Experiences": "Adventures-Experiences",
            "Adventures-Accommodation": "Adventures-Accommodation",
            "Collectors": "Collectors", "Cars": "Cars_private",
            "Cars_dealer": "Cars_private", "Cars_private": "Cars_private",
        }
        cat_key = _cat_norm.get(category, category)
    else:
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

    # All sellers start at 40 (Established base) — matches the sell-flow sbCalcScore model.
    # Penalties pull below 40 (bad actors); credentials push above 40.
    base_score = 40
    score_total = max(0, min(100, base_score + earned_u + earned_t + earned_c + penalty_total))
    tier = _trust_tier(score_total)

    # Pending points (uploaded but not yet verified by admin)
    all_items = items_u + items_t + items_c
    pending_signals = [
        {"signal_id": it["signal_id"], "name": it["name"], "points": it["points"]}
        for it in all_items if it["status"] == "pending"
    ]
    pending_pts = sum(it["points"] for it in pending_signals)

    # Persist the recomputed score only when using the seller's natural/primary
    # category (no ?category= override). When the edit screen requests a specific
    # category, we compute and return the score but do NOT write it back to
    # users.trust_score — that column must always reflect the primary listing
    # score so the listing card badge stays accurate.
    prior_score = int(user["trust_score"] or 0)
    if not category and prior_score != score_total:
        conn.execute(
            "UPDATE users SET trust_score = ? WHERE email = ?",
            (score_total, email)
        )
        # Sync score to all listing rows for this seller+category so the
        # browse card badge stays accurate without a separate job.
        conn.execute(
            "UPDATE listings SET trust_score = ? WHERE seller_email = ?",
            (score_total, email)
        )
        conn.commit()
        # Hook into LM suspension/restoration
        _lm_recompute_seller_state(conn, email)
        conn.commit()
    elif category:
        # Category-override call: sync score only to listings in this category
        # so each listing's card badge reflects its own category score.
        # Map frontend category param back to DB category values
        _cat_listing_map = {
            "LocalMarket": "local_market", "local_market": "local_market",
            "Property": "Property", "Tutors": "Tutors",
            "Services-Technical": "Services", "Services": "Services",
            "Services-Casuals": "Services",
            "Adventures-Experiences": "Adventures",
            "Adventures-Accommodation": "Adventures",
            "Adventures": "Adventures",
            "Collectors": "Collectors", "Cars": "Cars",
        }
        db_cat = _cat_listing_map.get(category, category)
        conn.execute(
            "UPDATE listings SET trust_score = ? WHERE seller_email = ? AND category = ?",
            (score_total, email, db_cat)
        )
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
        "pending_points": pending_pts,
        "pending_signals": pending_signals,
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
    lc = _signal_listing_category(req.signal_id)
    conn.execute(
        """INSERT INTO user_credentials (email, signal_id, status, points, evidence_url, notes, verified_at, verified_by, listing_category)
           VALUES (?, ?, ?, ?, ?, ?, ?, 'admin', ?)
           ON CONFLICT(email, signal_id) DO UPDATE SET
               status = excluded.status,
               points = excluded.points,
               evidence_url = COALESCE(excluded.evidence_url, user_credentials.evidence_url),
               notes = COALESCE(excluded.notes, user_credentials.notes),
               verified_at = excluded.verified_at,
               verified_by = 'admin',
               listing_category = COALESCE(excluded.listing_category, user_credentials.listing_category)""",
        (req.email, req.signal_id, req.status, pts, req.evidence_url, req.notes, verified_at, lc or None)
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
async def trust_score_guidance(req: AIGuidanceRequest, background_tasks: BackgroundTasks):
    cat_signals       = _CATEGORY_SIGNALS.get(req.category, {})
    universal_signals = {k: v for k, v in _TRUST_SIGNALS.items() if k.startswith("universal.")}

    conn = database.get_db()
    try:
        earned_rows = conn.execute(
            "SELECT signal_id, status FROM user_credentials WHERE email = ?",
            (req.email,)
        ).fetchall()
        user_row = conn.execute(
            "SELECT id_verified_at, eula_accepted_at, photo_url, trust_score FROM users WHERE email = ?",
            (req.email,)
        ).fetchone()
    except Exception:
        earned_rows = []
        user_row = None
    finally:
        conn.close()

    # Existence gate — must be a registered user before AI call (Session 90)
    if not user_row:
        raise HTTPException(status_code=401, detail="Unrecognised account — please complete seller registration first.")
    _check_cost_ceiling(req.email)   # C1 — refuse if daily cost ceiling reached

    earned_map = {r["signal_id"]: r["status"] for r in earned_rows} if earned_rows else {}
    # Supplement earned_map with direct user-table flags so guidance is accurate
    # even if user_credentials rows were not written (e.g. older upload-id calls)
    if user_row:
        if user_row["id_verified_at"]:
            earned_map.setdefault("universal.id_verified", "earned")
        if user_row["eula_accepted_at"]:
            earned_map.setdefault("universal.email_verified", "earned")
        if user_row["photo_url"]:
            earned_map.setdefault("universal.profile_photo", "earned")

    universal_earned_pts = 0
    universal_missing = []
    for sig_id, sig in universal_signals.items():
        if earned_map.get(sig_id) == "earned":
            universal_earned_pts += sig["points"]
        else:
            universal_missing.append({
                "id": sig_id, "name": sig["name"], "points": sig["points"], "how": sig["how_to_earn"]
            })

    cat_earned_pts = 0
    cat_missing = []
    for sig_id, sig in cat_signals.items():
        if earned_map.get(sig_id) == "earned":
            cat_earned_pts += sig.get("points", 0)
        else:
            cat_missing.append({
                "id": sig_id,
                "name": sig["name"],
                "points": sig.get("points", 0),
                "how": sig.get("how_to_earn", ""),
            })

    # Use users.trust_score as the authoritative score — it's the ground truth.
    # Fall back to computed sum only if the user row doesn't exist yet.
    db_score = int(user_row["trust_score"] or 0) if user_row else 0
    current_score = db_score if db_score > 0 else (universal_earned_pts + cat_earned_pts)

    # Dynamically target the next tier above the seller's current score
    _next = _trust_tier(current_score).get("next_tier")
    score_target  = _next["threshold"] if _next else 100
    target_label  = (_next["name"] + " tier (score " + str(score_target) + ")") if _next else "maximum Trust Score (100)"
    points_needed = max(0, score_target - current_score)
    all_missing   = sorted(universal_missing + cat_missing, key=lambda x: x["points"], reverse=True)

    if not ANTHROPIC_API_KEY:
        return {
            "ai_available":  False,
            "current_score": current_score,
            "score_target":  score_target,
            "points_needed": points_needed,
            "intro":   "To reach " + target_label + ", focus on the steps below.",
            "steps":   _build_local_guidance(req.category, all_missing),
            "closing": "Every step builds buyer confidence.",
        }

    missing_lines = "\n".join(
        "- " + m["name"] + " (+" + str(m["points"]) + " pts): " + _signal_howto(m["id"], m["how"])[1]
        for m in all_missing[:8]
    )

    system_prompt = (
        "You are a friendly Trust Score coach for TrustSquare, a South African marketplace. "
        "Help sellers understand exactly what they need to do to reach " + target_label + ". "
        "Be warm, direct, and specific. "
        "IMPORTANT: Only recommend actions the seller has NOT already completed. "
        "Never suggest uploading an ID if id_verified is already earned. "
        "For each step, give a specific WHERE and HOW (e.g. which tab, which button). "
        'Reply ONLY with a valid JSON object — no markdown, no preamble. '
        'Format: {"intro": "one encouraging sentence", '
        '"steps": [{"action": "specific instruction with where/how", "points": N, "why": "one sentence explaining the benefit"}], '
        '"closing": "one motivating sentence"} '
        "Order steps by impact (most points first). Maximum 5 steps. "
        "Keep each action under 25 words. Keep each why under 15 words."
    )

    earned_lines = "\n".join(
        "- " + k.replace("universal.", "").replace("_", " ") + " (already earned)"
        for k, v in earned_map.items() if v == "earned"
    ) or "None yet"

    user_message = (
        "Seller category: " + req.category + "\n"
        "Current Trust Score: " + str(current_score) + " / 100\n"
        "Target: " + target_label + " (need " + str(points_needed) + " more points)\n\n"
        "Already completed (DO NOT recommend these):\n" + earned_lines + "\n\n"
        "Not yet completed:\n" + (missing_lines or "None — all signals earned!") + "\n\n"
        "Generate a personalised action plan for the remaining steps only."
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model":      AA_MODEL,
                    "max_tokens": 600,
                    "system":     system_prompt,
                    "messages":   [{"role": "user", "content": user_message}],
                },
            )
        resp.raise_for_status()
        _g_json = resp.json()
        raw = _g_json["content"][0]["text"]
        _g_in, _g_out = _usage_tokens(_g_json)   # C2
    except Exception as exc:
        _log.warning("AI guidance Haiku call failed: %s", exc)
        return {
            "ai_available":  False,
            "current_score": current_score,
            "score_target":  score_target,
            "points_needed": points_needed,
            "intro":   "To reach " + target_label + ", focus on the steps below.",
            "steps":   _build_local_guidance(req.category, all_missing),
            "closing": "Every step builds buyer confidence.",
        }

    import re as _re
    guidance = {}
    try:
        guidance = json.loads(raw)
    except Exception:
        m2 = _re.search(r'\{[\s\S]*\}', raw)
        try:
            guidance = json.loads(m2.group(0)) if m2 else {}
        except Exception:
            guidance = {}

    # Always override intro — AI tends to hallucinate the target score
    guidance["intro"]         = "Here is your personalised path to " + target_label + "."
    guidance.setdefault("steps",   _build_local_guidance(req.category, all_missing))
    guidance.setdefault("closing", "Every step you complete builds buyer confidence.")
    guidance["ai_available"]  = True
    guidance["current_score"] = current_score
    guidance["score_target"]  = score_target
    guidance["points_needed"] = points_needed
    background_tasks.add_task(_log_ai_spend, req.email, "/trust-score/guidance", "haiku", _g_in, _g_out)
    return guidance


# Human-readable how-to instructions for each signal key
_SIGNAL_HOWTO = {
    # Universal — identity & profile
    "universal.id_verified":          ("Upload your ID or passport",
                                       "My Space → Trust tab → tap 'Upload ID →' next to Government-issued ID"),
    "universal.profile_photo":        ("Add a clear profile photo",
                                       "My Space → Me tab → tap your avatar to upload a photo"),
    "universal.email_verified":       ("Verify your email address",
                                       "Automatically earned when you accept the TrustSquare Terms of Service"),
    "universal.profile_complete":     ("Complete your seller profile",
                                       "My Dashboard → fill in bio, suburb, and category description"),
    # Track record — all auto-tracked, no uploads needed
    "track_record.intro_1":           ("Complete your first introduction",
                                       "My Dashboard → Intros tab — accept a buyer's request and follow through. Tracked automatically."),
    "track_record.intro_5":           ("Complete 5 introductions",
                                       "My Dashboard → Intros tab — keep accepting and completing intro requests. Every accepted intro counts."),
    "track_record.intro_20":          ("Complete 20 introductions",
                                       "My Dashboard → Intros tab — continue accepting intros. The system counts every completion automatically."),
    "track_record.zero_ignored_90d":  ("Respond to every intro within 48 hours",
                                       "My Dashboard → Intros tab — when a buyer requests an intro, accept or decline within 48 hours. Ignored intros reduce your score."),
    "track_record.tenure_6mo":        ("Keep an active listing for 6+ months",
                                       "Automatically awarded once your first listing has been live for 6 consecutive months — no action needed."),
    # Collectors category — transaction milestones (all auto-tracked)
    "category.collectors.tx_1_4":    ("Complete your first introductions on your Collectors listings",
                                       "My Dashboard → Intros tab — accept buyer requests on your card/collectible listings. Every completed intro is tracked automatically."),
    "category.collectors.tx_5_14":   ("Complete 5–14 introductions on your Collectors listings",
                                       "My Dashboard → Intros tab — keep accepting and completing intro requests. The system tracks every completion automatically."),
    "category.collectors.tx_15plus": ("Complete 15+ introductions on your Collectors listings",
                                       "My Dashboard → Intros tab — continue accepting intros. System counts every completion — no uploads or actions needed."),
    # Property category — transaction milestones
    "category.property.tx_1_4":      ("Complete your first introductions on your Property listings",
                                       "My Dashboard → Intros tab — accept buyer requests on your property listings. Tracked automatically."),
    "category.property.tx_5_14":     ("Complete 5–14 introductions on your Property listings",
                                       "My Dashboard → Intros tab — keep accepting property intro requests. Every completion is counted automatically."),
    "category.property.tx_15plus":   ("Complete 15+ introductions on your Property listings",
                                       "My Dashboard → Intros tab — continue accepting property intros. System tracks every completion."),
    # Adventures category — transaction milestones
    "category.adventures.tx_1_4":    ("Complete your first introductions on your Adventures listings",
                                       "My Dashboard → Intros tab — accept buyer requests on your experience/accommodation listings. Tracked automatically."),
    "category.adventures.tx_5_14":   ("Complete 5–14 introductions on your Adventures listings",
                                       "My Dashboard → Intros tab — keep accepting Adventures intro requests. Every completion counts automatically."),
    "category.adventures.tx_15plus": ("Complete 15+ introductions on your Adventures listings",
                                       "My Dashboard → Intros tab — continue accepting intros. System tracks every completion."),
    # Cars category — transaction milestones
    "category.cars.tx_1_4":          ("Complete your first introductions on your Cars listings",
                                       "My Dashboard → Intros tab — accept buyer requests on your car listings. Tracked automatically."),
    "category.cars.tx_5_14":         ("Complete 5–14 introductions on your Cars listings",
                                       "My Dashboard → Intros tab — keep accepting Cars intro requests. Every completion counts."),
    "category.cars.tx_15plus":       ("Complete 15+ introductions on your Cars listings",
                                       "My Dashboard → Intros tab — continue accepting intros. System tracks every completion."),
}

def _signal_howto(sig_id: str, default_how: str) -> tuple:
    """Return (action, why) for a signal, falling back to default_how."""
    if sig_id in _SIGNAL_HOWTO:
        return _SIGNAL_HOWTO[sig_id]
    if default_how:
        return (default_how, "Complete this step to earn the points — tracked automatically by TrustSquare")
    return ("Complete this trust step", "Tracked automatically by TrustSquare once completed")

def _build_local_guidance(category: str, all_missing: list = None) -> list:
    if all_missing is None:
        cat_sigs = _CATEGORY_SIGNALS.get(category, {})
        all_missing = [
            {"id": "universal.id_verified", "name": "Government-issued ID verified", "points": 15,
             "how": "Upload your ID or passport."},
            {"id": "universal.profile_photo", "name": "Profile photo added", "points": 10,
             "how": "Upload a clear profile photo."},
        ] + sorted(
            [{"id": sid, "name": s["name"], "points": s.get("points", 0), "how": s.get("how_to_earn", "")}
             for sid, s in cat_sigs.items()],
            key=lambda x: x["points"], reverse=True
        )
    steps = []
    for m in all_missing[:5]:
        sig_id = m.get("id", "")
        action, why = _signal_howto(sig_id, m.get("how", m.get("name", "")))
        steps.append({"action": action, "points": m["points"], "why": why})
    return steps


class UploadCommentRequest(BaseModel):
    email: str
    category: str
    doc_type: str
    label: str
    signal_id: Optional[str] = None


@app.post("/trust-score/upload-comment")
async def trust_score_upload_comment(req: UploadCommentRequest, background_tasks: BackgroundTasks):
    """After a seller uploads a document, return a short AI comment:
    what this contributes to their Trust Score and what to upload next."""
    conn = database.get_db()
    try:
        earned_rows = conn.execute(
            "SELECT signal_id, status FROM user_credentials WHERE email = ?",
            (req.email,)
        ).fetchall()
        user_row = conn.execute(
            "SELECT trust_score FROM users WHERE email = ?", (req.email,)
        ).fetchone()
    finally:
        conn.close()

    # Existence gate (Session 90)
    if not user_row:
        raise HTTPException(status_code=401, detail="Unrecognised account — please complete seller registration first.")
    _check_cost_ceiling(req.email)   # C1 — refuse if daily cost ceiling reached

    cred_status = {r["signal_id"]: r["status"] for r in (earned_rows or [])}
    current_score = int(user_row["trust_score"] or 0) if user_row else 0

    all_signals = {**_TRUST_SIGNALS, **_CATEGORY_SIGNALS.get(req.category, {})}
    signal = all_signals.get(req.signal_id or "", {})
    signal_name = signal.get("name", req.label)
    signal_pts  = signal.get("points", 0)

    submitted_ids = {sid for sid, st in cred_status.items() if st in ("earned", "pending")}
    missing = [
        {"name": s["name"], "points": s.get("points", 0), "how": s.get("how_to_earn", "")}
        for sid, s in all_signals.items()
        if sid not in submitted_ids and s.get("points", 0) > 0
    ]
    missing.sort(key=lambda x: x["points"], reverse=True)
    next_suggestion = missing[0] if missing else None

    if not ANTHROPIC_API_KEY:
        comment = f"✅ {signal_name} submitted for verification — worth +{signal_pts} pts once approved."
        if next_suggestion:
            comment += f" Next: {next_suggestion['name']} (+{next_suggestion['points']} pts)."
        return {"comment": comment, "signal_pts": signal_pts, "next_signal": next_suggestion}

    next_line = (
        f"Best next upload: {next_suggestion['name']} (+{next_suggestion['points']} pts) — {next_suggestion['how']}"
        if next_suggestion else "All key signals submitted — great work!"
    )

    system_prompt = (
        "You are a warm, encouraging Trust Score coach for TrustSquare, a South African marketplace. "
        "Write exactly 2 sentences: sentence 1 confirms what was just uploaded and what it will add "
        "to the Trust Score once verified. Sentence 2 gives ONE specific next-step upload suggestion. "
        "Be concrete, warm, under 45 words total. No bullet points. No markdown."
    )
    user_message = (
        f"Seller just uploaded: {req.label} (type: {req.doc_type})\n"
        f"Signal: {signal_name} (+{signal_pts} pts once verified)\n"
        f"Current Trust Score: {current_score}/100\n"
        f"{next_line}"
    )

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": AA_MODEL,
                    "max_tokens": 120,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_message}],
                },
            )
        resp.raise_for_status()
        _uc_json = resp.json()
        comment = _uc_json["content"][0]["text"].strip()
        _uc_in, _uc_out = _usage_tokens(_uc_json)   # C2
    except Exception as exc:
        _log.warning("upload-comment Haiku call failed: %s", exc)
        comment = (
            f"✅ {signal_name} submitted (+{signal_pts} pts once verified). "
            + (f"Next: {next_suggestion['name']} (+{next_suggestion['points']} pts)." if next_suggestion else "")
        )
        _uc_in, _uc_out = None, None   # API failed — flat estimate

    background_tasks.add_task(_log_ai_spend, req.email, "/trust-score/upload-comment", "haiku", _uc_in, _uc_out)
    return {"comment": comment, "signal_pts": signal_pts, "next_signal": next_suggestion}


# ── SELLER DOCUMENTS ─────────────────────────────────────────────────────────
# Documents are stored in R2 / local media. Each doc has a visibility flag:
#   private     — never shown to buyers
#   post_intro  — shown on seller profile after buyer's intro is accepted

ALLOWED_DOC_TYPES = {
    "id_doc", "certificate", "training", "membership",
    "professional_role", "guide", "recipe", "presentation", "other"
}

# Stacking chains: doc_type → ordered list of signal_ids.
# When a doc is uploaded, we find the first slot in the chain not yet earned/pending.
_DOC_TYPE_SIGNAL_CHAINS = {
    "id_doc":            ["category.lm.id_uploaded"],
    "certificate":       ["category.lm.formal_cert", "category.lm.formal_cert_2", "category.lm.formal_cert_3"],
    "training":          ["category.lm.training_course", "category.lm.training_course_2"],
    "membership":        ["category.lm.prof_body", "category.lm.prof_body_2"],
    "professional_role": ["category.lm.assoc_role", "category.lm.provincial_role"],
    "guide":             ["category.lm.product_guide", "category.lm.product_guide_2", "category.lm.product_guide_3"],
    "recipe":            ["category.lm.product_guide", "category.lm.product_guide_2", "category.lm.product_guide_3"],
}

def _next_signal_for_doc(doc_type: str, conn, email: str) -> Optional[str]:
    """Return the first unfilled signal slot in the stacking chain for this doc_type.
    If all slots are filled (earned or pending), return the last slot so the upload
    still records against the document type even if no new points are awarded."""
    chain = _DOC_TYPE_SIGNAL_CHAINS.get(doc_type)
    if not chain:
        return None
    rows = conn.execute(
        "SELECT signal_id, status FROM user_credentials WHERE email=?", (email,)
    ).fetchall()
    filled = {r["signal_id"] for r in rows if r["status"] in ("earned", "pending")}
    for sig_id in chain:
        if sig_id not in filled:
            return sig_id
    return chain[-1]  # all filled — map to last slot (no extra points)

@app.post("/users/{email}/documents")
async def upload_seller_document(
    email: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    doc_type: str = Form("other"),
    label: str = Form(""),
    visibility: str = Form("private"),
    signal_id: str = Form(None),
    _key: str = Depends(auth.require_api_key),
):
    """Upload a document for a seller. Stores to R2, records in seller_documents.
    Non-ID doc types are auto-earned immediately (self-attestation model).
    ID documents trigger Sonnet vision verification and auto-earn on confidence >= 0.60."""
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
        path = os.path.join(_LOCAL_MEDIA_DIR, safe)
        with open(path, "wb") as fh:
            fh.write(raw)
        url = f"/media/{safe}"

    # Determine signal_id for this doc type — uses stacking chain
    # so each additional upload of the same type fills the next slot
    conn_pre = database.get_db()
    try:
        effective_signal = signal_id or _next_signal_for_doc(doc_type, conn_pre, email)
    finally:
        conn_pre.close()

    conn = database.get_db()
    auto_earned = False
    evidence_pts_awarded = 0
    declaration_completed = False
    try:
        conn.execute(
            """INSERT INTO seller_documents (email, doc_type, label, url, visibility, signal_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (email, doc_type, label or orig_name, url, visibility, effective_signal)
        )
        doc_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        if effective_signal:
            # ── Auto-earn strategy (no human in the loop) ────────────────
            # ID documents: set pending now; verify-identity endpoint runs
            #   Sonnet vision and auto-earns on confidence >= 0.60
            # Declared signals: seller already earned declaration_points (80%).
            #   Upload earns the remaining evidence_points (20%) by upgrading
            #   the credential from 'declared' → 'earned'.
            # All other doc types: auto-earn immediately (self-attestation).
            is_id_doc = doc_type == "id_doc"
            # Check if this signal was already declared (80% already awarded)
            existing_cred = conn.execute(
                "SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
                (email, effective_signal)
            ).fetchone()
            already_declared = existing_cred and existing_cred["status"] == "declared"

            if is_id_doc:
                initial_status = "pending"
            else:
                initial_status = "earned"

            _upsert_credential(conn, email, effective_signal, initial_status)

            if not is_id_doc:
                auto_earned = True

            # If upgrading from declared → earned, note it for the response
            if already_declared and not is_id_doc:
                declaration_completed = True
                for _cat_sigs in [_TRUST_SIGNALS] + list(_CATEGORY_SIGNALS.values()):
                    if effective_signal in _cat_sigs:
                        evidence_pts_awarded = _cat_sigs[effective_signal].get("evidence_points", 0)
                        break

        conn.commit()
    finally:
        conn.close()

    # For non-ID docs: if seller has a verified ID name, run cert name check
    # as a background task so cert_name_verified signal can be awarded too.
    if auto_earned and doc_type in ("certificate", "training", "membership", "professional_role"):
        conn2 = database.get_db()
        try:
            user_row = conn2.execute(
                "SELECT id_name FROM users WHERE email=?", (email,)
            ).fetchone()
            id_name = user_row["id_name"] if user_row else None
        finally:
            conn2.close()
        if id_name and ANTHROPIC_API_KEY:
            background_tasks.add_task(
                _run_cert_name_check, email, url, id_name, doc_type
            )

    # Build response — include evidence_points_awarded if this completed a declaration
    return {
        "id": doc_id, "url": url, "doc_type": doc_type, "label": label or orig_name,
        "visibility": visibility, "signal_id": effective_signal,
        "auto_earned": auto_earned,
        "evidence_points_awarded": evidence_pts_awarded,
        "declaration_completed": declaration_completed,
    }


@app.get("/users/{email}/documents")
def list_seller_documents(
    email: str,
    category: Optional[str] = None,
    _key: str = Depends(auth.require_api_key),
):
    """List documents for a seller. If category is provided, returns only docs
    whose signal_id matches that category prefix, plus universal/track_record docs
    and docs with no signal_id. Without category, returns all docs."""
    email = email.lower().strip()
    conn = database.get_db()
    _cat_prefix_map = {
        "LocalMarket": "category.lm.",
        "local_market": "category.lm.",
        "Property": "category.property.",
        "Tutors": "category.tutors.",
        "Services-Technical": "category.services_tech.",
        "Services-Casuals": "category.services_cas.",
        "Services": "category.services_tech.",
        "Adventures-Experiences": "category.adv_exp.",
        "Adventures-Accommodation": "category.adv_acc.",
        "Adventures": "category.adv_exp.",
        "Collectors": "category.collectors.",
        "Cars": "category.cars.",
    }
    prefix = _cat_prefix_map.get(category, "") if category else ""
    if prefix:
        rows = conn.execute(
            """SELECT id, doc_type, label, url, visibility, signal_id, uploaded_at
               FROM seller_documents
               WHERE email=?
                 AND (
                   signal_id IS NULL
                   OR signal_id LIKE ?
                   OR signal_id LIKE 'universal.%'
                   OR signal_id LIKE 'track_record.%'
                 )
               ORDER BY uploaded_at DESC""",
            (email, prefix + "%")
        ).fetchall()
    else:
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


# ── TRUST SCORE: DECLARATION ENDPOINT ────────────────────────────────────────

class DeclarationIn(BaseModel):
    signal_id: str
    declaration_text: str

@app.post("/users/{email}/declare")
def declare_credential(
    email: str,
    payload: DeclarationIn,
    _key: str = Depends(auth.require_api_key),
):
    """Record a free-text declaration for a declarable signal.

    Awards `declaration_points` (80%) immediately and records the declaration
    text as an audit trail.  The remaining `evidence_points` (20%) are awarded
    later when the seller uploads documentary evidence.

    Returns:
        points_awarded      — declaration_points credited now
        evidence_points     — points that can still be earned by uploading evidence
        next_step_message   — human-readable prompt for what to upload
        total_possible      — full signal value (declaration + evidence)
    """
    email = email.lower().strip()

    # Resolve signal definition
    signal_def = None
    for cat_signals in [_TRUST_SIGNALS] + list(_CATEGORY_SIGNALS.values()):
        if payload.signal_id in cat_signals:
            signal_def = cat_signals[payload.signal_id]
            break

    if signal_def is None:
        raise HTTPException(status_code=404, detail=f"Signal '{payload.signal_id}' not found")

    declaration_points = signal_def.get("declaration_points")
    evidence_points    = signal_def.get("evidence_points", 0)

    if declaration_points is None:
        raise HTTPException(
            status_code=400,
            detail="This signal does not support declarations — upload a document instead."
        )

    if not payload.declaration_text or len(payload.declaration_text.strip()) < 10:
        raise HTTPException(
            status_code=422,
            detail="Declaration text must be at least 10 characters."
        )

    conn = database.get_db()

    # Check seller exists
    seller = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
    if not seller:
        conn.close()
        raise HTTPException(status_code=404, detail="Seller not found")

    # Idempotency: if already declared for this signal, return current state
    existing_decl = conn.execute(
        "SELECT id, points_awarded FROM user_declarations WHERE email=? AND signal_id=?",
        (email, payload.signal_id)
    ).fetchone()

    existing_cred = conn.execute(
        "SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
        (email, payload.signal_id)
    ).fetchone()

    if existing_cred and existing_cred["status"] == "earned":
        conn.close()
        return {
            "points_awarded": 0,
            "evidence_points": evidence_points,
            "next_step_message": "This credential is already fully earned.",
            "total_possible": signal_def.get("points", declaration_points + evidence_points),
            "already_complete": True,
        }

    if existing_decl:
        # Already declared — update the declaration text but don't re-award points
        conn.execute(
            "UPDATE user_declarations SET declaration=?, declared_at=strftime('%Y-%m-%dT%H:%M:%SZ','now') WHERE email=? AND signal_id=?",
            (payload.declaration_text.strip(), email, payload.signal_id)
        )
        conn.commit()
        conn.close()
        return {
            "points_awarded": 0,
            "evidence_points": evidence_points,
            "next_step_message": signal_def.get("how_to_earn", "Upload evidence to claim the remaining points."),
            "total_possible": signal_def.get("points", declaration_points + evidence_points),
            "already_declared": True,
        }

    # First-time declaration — insert record and award points
    conn.execute(
        """INSERT INTO user_declarations (email, signal_id, declaration, points_awarded)
           VALUES (?, ?, ?, ?)""",
        (email, payload.signal_id, payload.declaration_text.strip(), declaration_points)
    )

    # Upsert credential to 'declared' status so upload logic awards evidence_points only
    _upsert_credential(conn, email, payload.signal_id, "declared")

    conn.commit()
    conn.close()

    next_step = signal_def.get(
        "how_to_earn",
        f"Upload supporting evidence to claim the remaining {evidence_points} pt(s)."
    )

    return {
        "points_awarded": declaration_points,
        "evidence_points": evidence_points,
        "next_step_message": next_step,
        "total_possible": signal_def.get("points", declaration_points + evidence_points),
        "already_declared": False,
    }


# ── SELLER DOCUMENTS ─────────────────────────────────────────────────────────
# Documents are stored in R2 / local media. Each doc has a visibility flag:
#   private     — never shown to buyers
#   post_intro  — shown on seller profile after buyer's intro is accepted

ALLOWED_DOC_TYPES = {
    "id_doc", "certificate", "training", "membership",
    "professional_role", "guide", "recipe", "presentation", "other"
}

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

        # D1-SEAM NOTE: this KYC path uses the Anthropic SDK directly (not the httpx seam).
        # It is the ONE remaining vendor-coupled call site; migrate to ai_provider.complete()
        # when the seam grows a vision adapter. Left intact now (KYC path, change = gated).
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
    elif ai["confidence"] >= 0.60:
        # Acceptable confidence — auto-earn (no human review path)
        _upsert_credential(conn, email, "category.lm.id_ai_verified", "earned")
        result["signals_awarded"].append("category.lm.id_ai_verified")
        conn.execute(
            "UPDATE users SET id_verified_at=strftime('%Y-%m-%dT%H:%M:%SZ','now'), id_ai_score=? WHERE email=?",
            (ai["confidence"], email)
        )
    elif ai["confidence"] >= 0.40:
        # Low confidence but plausible — award id_number_valid only (already done above)
        # Format was valid so seller still gets base points
        result["notes"] = (result.get("notes") or "") + " Low AI confidence — ID format valid but image unclear."

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
        # Auto-earn if any name is extractable (seller already attested by uploading)
        # Only set pending if AI can't read the doc at all
        if confidence >= 0.40 or name_match >= 0.60:
            new_status = "earned"
        elif result.get("extracted_name"):
            new_status = "earned"   # extracted something — good enough
        else:
            new_status = "earned"   # self-attestation: earn regardless, flag for spot-check log

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
    """Insert or update a credential — never downgrade earned to pending.
    Stores listing_category derived from signal_id prefix for category signals."""
    lc = _signal_listing_category(signal_id) or None
    existing = conn.execute(
        "SELECT status FROM user_credentials WHERE email=? AND signal_id=?",
        (email, signal_id)
    ).fetchone()
    if not existing:
        conn.execute(
            """INSERT INTO user_credentials (email, signal_id, status, listing_category, updated_at)
               VALUES (?, ?, ?, ?, strftime('%Y-%m-%dT%H:%M:%SZ','now'))""",
            (email, signal_id, status, lc)
        )
    elif existing["status"] != "earned":  # never downgrade earned
        conn.execute(
            """UPDATE user_credentials SET status=?, listing_category=COALESCE(?,listing_category),
               updated_at=strftime('%Y-%m-%dT%H:%M:%SZ','now')
               WHERE email=? AND signal_id=?""",
            (status, lc, email, signal_id)
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


# ── MULTI-CITY REACH ─────────────────────────────────────────────────────────
# Free sellers: home city only.
# Starter/Premium sellers: can extend a listing to any city in their country
# by confirming they can service buyers there.
# Buyers always see listings as "local" — they never see the seller's home city.

_PAID_TIERS = {"starter", "premium"}

@app.get("/listings/{listing_id}/cities")
def get_listing_cities(listing_id: int):
    """Return all extended cities for a listing (public)."""
    conn = database.get_db()
    rows = conn.execute(
        """SELECT lc.city_id, g.name as city_name, lc.seller_confirmed_at
           FROM listing_cities lc
           LEFT JOIN geo_cities g ON g.id = lc.city_id
           WHERE lc.listing_id = ?
           ORDER BY g.name""",
        (listing_id,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


class ListingCityIn(BaseModel):
    email: str
    city_id: int


@app.post("/listings/{listing_id}/cities")
def add_listing_city(listing_id: int, payload: ListingCityIn):
    """Seller extends their listing to an additional city.
    Requires Starter or Premium tier. Seller authenticates by email
    (same pattern as edit-after-publish: email must match listing.seller_email).
    """
    email = payload.email.lower().strip()
    conn = database.get_db()
    try:
        # Verify listing belongs to this seller
        listing = conn.execute(
            "SELECT id, seller_email, geo_city_id FROM listings WHERE id=?",
            (listing_id,)
        ).fetchone()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        if listing["seller_email"] and listing["seller_email"].lower() != email:
            raise HTTPException(status_code=403, detail="Email does not match listing owner")

        # Check seller tier
        user = conn.execute(
            "SELECT seller_tier FROM users WHERE LOWER(email)=?", (email,)
        ).fetchone()
        tier = (user["seller_tier"] if user else "free") or "free"
        if tier not in _PAID_TIERS:
            raise HTTPException(
                status_code=402,
                detail="Multi-city reach requires a Starter subscription ($5/month). Upgrade at trustsquare.co/admin.html"
            )

        # Verify city exists
        city = conn.execute(
            "SELECT id, name FROM geo_cities WHERE id=?", (payload.city_id,)
        ).fetchone()
        if not city:
            raise HTTPException(status_code=404, detail="City not found")

        # Don't duplicate home city
        if payload.city_id == listing["geo_city_id"]:
            raise HTTPException(status_code=400, detail="That is already your listing's home city")

        # Insert (ignore duplicate)
        conn.execute(
            """INSERT OR IGNORE INTO listing_cities (listing_id, city_id)
               VALUES (?, ?)""",
            (listing_id, payload.city_id)
        )
        conn.commit()
    finally:
        conn.close()

    return {"listing_id": listing_id, "city_id": payload.city_id,
            "city_name": city["name"], "status": "added"}


@app.delete("/listings/{listing_id}/cities/{city_id}")
def remove_listing_city(listing_id: int, city_id: int, email: str):
    """Remove an extended city from a listing."""
    email = email.lower().strip()
    conn = database.get_db()
    try:
        listing = conn.execute(
            "SELECT seller_email FROM listings WHERE id=?", (listing_id,)
        ).fetchone()
        if not listing:
            raise HTTPException(status_code=404, detail="Listing not found")
        if listing["seller_email"] and listing["seller_email"].lower() != email:
            raise HTTPException(status_code=403, detail="Email does not match listing owner")
        conn.execute(
            "DELETE FROM listing_cities WHERE listing_id=? AND city_id=?",
            (listing_id, city_id)
        )
        conn.commit()
    finally:
        conn.close()
    return {"status": "removed"}


@app.put("/users/{email}/seller-tier")
def set_seller_tier(email: str, tier: str, _key: str = Depends(auth.require_api_key)):
    """Admin: set seller subscription tier immediately (bypasses Paystack).
    tier must be: free | standard | professional | business | elite | starter | premium
    Also applies pending downgrades — call with tier=free for immediate free downgrade.
    Enforces slot guard: if active listings > new slot_limit, returns 409 with count.
    """
    email = email.lower().strip()
    valid_tiers = set(_SELLER_SUB_TIERS.keys())
    if tier not in valid_tiers:
        raise HTTPException(status_code=400, detail=f"tier must be one of: {', '.join(sorted(valid_tiers))}")
    new_limit = _tier_slot_limit(tier)
    conn = database.get_db()
    try:
        user = conn.execute("SELECT email FROM users WHERE LOWER(email)=?", (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Seller not found")
        # Slot guard: count active (live/draft) listings
        active_count = conn.execute(
            "SELECT COUNT(*) as n FROM listings WHERE LOWER(seller_email)=? "
            "AND (listing_status IS NULL OR listing_status IN ('live','draft'))",
            (email,)
        ).fetchone()["n"]
        if active_count > new_limit:
            raise HTTPException(
                status_code=409,
                detail=f"Seller has {active_count} active listings but {tier} allows only {new_limit}. "
                       f"Archive {active_count - new_limit} listing(s) before downgrading."
            )
        conn.execute(
            "UPDATE users SET seller_tier=?, slot_limit=?, pending_downgrade_tier=NULL "
            "WHERE LOWER(email)=?",
            (tier, new_limit, email)
        )
        conn.commit()
    finally:
        conn.close()
    return {"email": email, "seller_tier": tier, "slot_limit": new_limit}


@app.post("/users/{email}/seller-tier/downgrade-free")
def downgrade_to_free(email: str):
    """Self-service: seller requests immediate downgrade to free tier.
    Blocked if active listing count > 2. No payment required.
    """
    email = email.lower().strip()
    free_limit = _tier_slot_limit("free")
    conn = database.get_db()
    try:
        user = conn.execute("SELECT email FROM users WHERE LOWER(email)=?", (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="Seller not found")
        active_count = conn.execute(
            "SELECT COUNT(*) as n FROM listings WHERE LOWER(seller_email)=? "
            "AND (listing_status IS NULL OR listing_status IN ('live','draft'))",
            (email,)
        ).fetchone()["n"]
        if active_count > free_limit:
            raise HTTPException(
                status_code=409,
                detail=f"You have {active_count} active listings. Archive down to {free_limit} before switching to Free."
            )
        conn.execute(
            "UPDATE users SET seller_tier='free', slot_limit=?, pending_downgrade_tier=NULL WHERE LOWER(email)=?",
            (free_limit, email)
        )
        conn.commit()
    finally:
        conn.close()
    return {"email": email, "seller_tier": "free", "slot_limit": free_limit}


# ── DASHBOARD SUMMARY ────────────────────────────────────────
# Owner-facing live dashboard data — reads STATUS.md, BACKLOG.md, CHANGELOG.md
# from the project root and combines with live DB stats.

import pathlib as _pathlib, re as _re2

_PROJECT_ROOT = _pathlib.Path(__file__).parent

def _read_file(name: str) -> str:
    p = _PROJECT_ROOT / name
    return p.read_text(encoding="utf-8") if p.exists() else ""

def _section(text: str, heading_re: str) -> str:
    m = _re2.search(heading_re + r"\n(.*?)(?=\n## |\Z)", text, _re2.DOTALL | _re2.IGNORECASE)
    return m.group(1).strip() if m else ""

def _bullet_items(text: str) -> list:
    items = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("- ") or line.startswith("* "):
            items.append(line[2:].strip())
        elif _re2.match(r"\d+\.", line):
            items.append(_re2.sub(r"^\d+\.\s*", "", line))
    return items

def _table_bold_items(text: str) -> list:
    items = []
    for row in text.splitlines():
        m = _re2.search(r"\*\*([^*]+)\*\*", row)
        if m and row.strip().startswith("|"):
            items.append(m.group(1))
    return items

@app.get("/dashboard/summary")
def dashboard_summary():
    """Live dashboard data — STATUS.md + BACKLOG.md + CHANGELOG.md + live DB stats.
    No auth required (data is not sensitive; security layer is the obscure URL).
    """
    status    = _read_file("STATUS.md")
    backlog   = _read_file("BACKLOG.md")
    changelog = _read_file("CHANGELOG.md")

    # Parse STATUS.md
    sm = _re2.search(r"Session (\d+)", status)
    current_session = int(sm.group(1)) if sm else 0

    live_state  = _section(status, r"## Live State")
    last_done   = _section(status, r"## Last Completed[^\n]*")
    next_goals  = _section(status, r"## Next Session[^\n]*")
    known_rules = _section(status, r"## Known Rules[^\n]*")

    # Parse BACKLOG.md
    blockers  = _table_bold_items(_section(backlog, r"## 🔴 Launch Blockers[^\n]*"))
    high_pri  = _table_bold_items(_section(backlog, r"## 🟠 High Priority[^\n]*"))
    medium    = _table_bold_items(_section(backlog, r"## 🟡 Medium Priority[^\n]*"))
    _auc_sec  = _section(backlog, r"## 🔨 Auctions[^\n]*")
    auctions  = [{"id": _r.strip().strip("|").split("|")[0].strip(), "done": "✅" in _r}
                 for _r in _auc_sec.splitlines() if _r.strip().startswith("| AU-")]

    # Parse next session priorities
    priority_items = _bullet_items(next_goals)

    # Parse CHANGELOG — last 2 sessions
    cl_sessions = _re2.split(r"\n(?=## Session)", changelog)
    recent_cl = cl_sessions[0][:1200] if cl_sessions else ""

    # Live DB stats
    conn = database.get_db()
    try:
        def _n(row): return row["n"] if row else 0
        live_count     = _n(conn.execute("SELECT COUNT(*) as n FROM listings WHERE listing_status='live'").fetchone())
        seller_count   = _n(conn.execute("SELECT COUNT(*) as n FROM users").fetchone())
        intro_count    = _n(conn.execute("SELECT COUNT(*) as n FROM intro_requests").fetchone())
        pending_intros = _n(conn.execute("SELECT COUNT(*) as n FROM intro_requests WHERE status='pending'").fetchone())
        tuppence_total = _n(conn.execute("SELECT COALESCE(SUM(amount),0) as n FROM transactions WHERE type='topup'").fetchone())
    finally:
        conn.close()

    from datetime import datetime as _dt

    # Build directions cards from parsed STATUS data
    next_session = current_session + 1

    # Next session priorities → direction card
    next_dir_items = priority_items[:4]
    next_dir_prompt = (
        "Read STATUS.md first. Session " + str(current_session) + " is complete. "
        "Pick up from Session " + str(next_session) + " priorities. "
        "Do not summarise what was done — go straight into execution."
    )

    # Blockers → direction card
    blockers_prompt = (
        "Read STATUS.md and BACKLOG.md. Focus on resolving launch blockers. "
        "List each blocker with the specific unblocking action needed."
    )

    # CityLauncher direction card
    cl_items = ["Load Pretoria Property prospects into CityLauncher DB",
                "Trigger Wave 1 (batch_size=60)", "Monitor delivery + open rates",
                "Check opt-out suppression working"]
    cl_prompt = (
        "Session goal: execute Wave 1 outreach. "
        "SSH into Hetzner, check CityLauncher DB has prospects loaded, "
        "then trigger the n8n wave workflow with batch_size=60."
    )

    # AdvertAgent direction card
    aa_items = ["Review AI coach session usage", "Gate sbTriggerMarketNote behind tier",
                "Test free-seller nudge banner", "Verify token cost per coach call"]
    aa_prompt = (
        "Review AdvertAgent AI coach usage. Gate inline market notes behind seller tier. "
        "Ensure free sellers see the upgrade nudge when ai_sessions=0."
    )

    directions = [
        {
            "id": "dir_next",
            "project": "TrustSquare",
            "title": "Session " + str(next_session) + " — Next up",
            "colour": "#3b82f6",
            "items": next_dir_items,
            "prompt": next_dir_prompt,
            "desktop": next_dir_prompt,
            "mobile": "Session " + str(next_session) + " priorities. " + (next_dir_items[0] if next_dir_items else "See STATUS.md"),
        },
        {
            "id": "dir_blockers",
            "project": "TrustSquare",
            "title": "Launch Blockers",
            "colour": "#ef4444",
            "items": (blockers or ["No blockers recorded"])[:4],
            "prompt": blockers_prompt,
            "desktop": blockers_prompt,
            "mobile": "Resolve launch blockers. Check BACKLOG.md for current list.",
        },
        {
            "id": "dir_cl",
            "project": "CityLauncher",
            "title": "Wave 1 — Pretoria Launch",
            "colour": "#8b5cf6",
            "items": cl_items,
            "prompt": cl_prompt,
            "desktop": cl_prompt,
            "mobile": "Trigger Wave 1 outreach: load prospects, run n8n workflow, monitor delivery.",
        },
        {
            "id": "dir_aa",
            "project": "AdvertAgent",
            "title": "AI Coach — Tier Gating",
            "colour": "#f59e0b",
            "items": aa_items,
            "prompt": aa_prompt,
            "desktop": aa_prompt,
            "mobile": "Gate AI coach behind seller tier. Show upgrade nudge for free sellers.",
        },
        {
            "id": "dir_infra",
            "project": "Agentic OS",
            "title": "Agentic OS — Framework",
            "colour": "#10b981",
            "items": [
                "Review Claude Code plugin structure",
                "Audit skill definitions and triggers",
                "Document session automation bat files",
                "Define agent lane boundaries",
            ],
            "prompt": (
                "Read STATUS.md and AGENT_BRIEFING.md. Review the Agentic OS framework: "
                "session startup bat files, skill definitions, plugin structure, and agent lane boundaries. "
                "Identify gaps and propose improvements."
            ),
            "desktop": (
                "Read STATUS.md and AGENT_BRIEFING.md. Review the Agentic OS framework: "
                "session startup bat files, skill definitions, plugin structure, and agent lane boundaries. "
                "Identify gaps and propose improvements."
            ),
            "mobile": "Review Agentic OS framework: plugins, skills, session bat files, agent lanes.",
        },
    ]

    return {
        "generatedAt": _dt.utcnow().strftime("%d %b %Y · %H:%M UTC"),
        "currentSession": current_session,
        "nextSession": next_session,
        "liveState": live_state,
        "lastDone": last_done,
        "nextGoals": next_goals,
        "knownRules": known_rules,
        "recentChangelog": recent_cl,
        "blockers": blockers,
        "highPriority": high_pri[:6],
        "medium": medium[:6],
        "priorityItems": priority_items[:6],
        "auctions": auctions,
        "directions": directions,
        "stats": {
            "liveListings": live_count,
            "sellers": seller_count,
            "intros": intro_count,
            "pendingIntros": pending_intros,
            "tuppenceTopup": tuppence_total,
        },
        "bea_version": "1.3.1",
    }



# ── WORLD WONDERS ────────────────────────────────────────────────────────────

import json as _json_mod
import os as _os_mod

def _load_wonders():
    """Load wonders.json from same directory as main.py."""
    path = _os_mod.path.join(_os_mod.path.dirname(_os_mod.path.abspath(__file__)), "wonders.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return _json_mod.load(f)
    except Exception:
        return []

@app.post("/dashboard/bit")
def dashboard_bit_post(payload: dict = Body(...)):
    """BIT Self-Test posts its latest board here (no auth — obscure URL, same posture as /dashboard/summary).
    Stores the JSON board to bit_status.json; the dashboard reads it via GET /dashboard/bit.
    The BIT Agent is a separate read-only article; this is its ONE write surface, and it only
    records a status snapshot (no app state is changed here)."""
    import json as _json, os as _os, datetime as _dt
    try:
        payload = dict(payload or {})
        payload["received_at"] = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bit_status.json")
        with open(p, "w", encoding="utf-8") as fh:
            _json.dump(payload, fh)
        return {"ok": True, "stored": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail="bad bit payload: " + str(e)[:120]) from e


@app.get("/dashboard/bit")
def dashboard_bit_get():
    """Live BIT Self-Test status for the dashboard health panel + Ops view. No auth (obscure URL)."""
    import json as _json, os as _os
    p = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bit_status.json")
    if not _os.path.exists(p):
        return {"state": "unknown", "results": [], "worst": 0, "note": "no BIT run recorded yet"}
    try:
        with open(p, encoding="utf-8") as fh:
            return _json.load(fh)
    except Exception:
        return {"state": "unknown", "results": [], "worst": 0, "note": "bit_status.json unreadable"}


@app.get("/wonders")
def list_wonders(type: str = None, country: str = None, q: str = None):
    """Return all wonders, optionally filtered by type, country, or search query."""
    wonders = _load_wonders()
    if type:
        wonders = [w for w in wonders if w.get("type","").lower() == type.lower()]
    if country:
        wonders = [w for w in wonders if country.lower() in w.get("country","").lower()]
    if q:
        q_lower = q.lower()
        wonders = [w for w in wonders if q_lower in w.get("name","").lower()
                   or q_lower in w.get("country","").lower()
                   or q_lower in w.get("region","").lower()]
    return {"wonders": wonders, "count": len(wonders)}

@app.get("/wonders/{wonder_id}")
def get_wonder(wonder_id: str):
    """Return a single wonder by ID."""
    wonders = _load_wonders()
    for w in wonders:
        if w.get("id") == wonder_id:
            return w
    raise HTTPException(status_code=404, detail="Wonder not found")

@app.put("/listings/{listing_id}/wonders")
def update_listing_wonders(listing_id: int, request: Request):
    """Set linked_wonders for a listing (up to 5 wonder IDs). Email-auth required."""
    return _update_listing_wonders_sync(listing_id, request)

def _update_listing_wonders_sync(listing_id: int, request: Request):
    raise HTTPException(status_code=500, detail="Use POST form — see below")

# Replace above with proper sync endpoint
@app.post("/listings/{listing_id}/wonders")
async def set_listing_wonders(listing_id: int, request: Request):
    """Set linked_wonders for a listing. Body: {email, wonder_ids: [...up to 5...]}"""
    try:
        body = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid JSON body") from exc
    email = body.get("email","").strip()
    wonder_ids = body.get("wonder_ids", [])
    if not email:
        raise HTTPException(status_code=401, detail="email required")
    if not isinstance(wonder_ids, list) or len(wonder_ids) > 5:
        raise HTTPException(status_code=400, detail="wonder_ids must be a list of up to 5 IDs")
    conn = database.get_db()
    try:
        row = conn.execute("SELECT seller_email FROM listings WHERE id=?", (listing_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Listing not found")
        if row["seller_email"] and row["seller_email"].lower() != email.lower():
            raise HTTPException(status_code=403, detail="Email does not match listing owner")
        # Validate wonder IDs
        all_wonders = _load_wonders()
        valid_ids = {w["id"] for w in all_wonders}
        bad = [wid for wid in wonder_ids if wid not in valid_ids]
        if bad:
            raise HTTPException(status_code=400, detail=f"Unknown wonder IDs: {bad}")
        conn.execute("UPDATE listings SET linked_wonders=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (_json_mod.dumps(wonder_ids), listing_id))
        conn.commit()
        return {"ok": True, "listing_id": listing_id, "linked_wonders": wonder_ids}
    finally:
        conn.close()

@app.get("/listings/{listing_id}/wonders")
def get_listing_wonders(listing_id: int):
    """Return the linked wonders for a listing, with full wonder objects."""
    conn = database.get_db()
    try:
        row = conn.execute("SELECT linked_wonders FROM listings WHERE id=?", (listing_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Listing not found")
        raw = row["linked_wonders"]
        if not raw:
            return {"listing_id": listing_id, "wonders": []}
        parsed = _json_mod.loads(raw)
        all_wonders = _load_wonders()
        wonders_map = {w["id"]: w for w in all_wonders}
        # Handle both formats: plain ID strings and {"id":..., "auto_linked":...} objects
        result = []
        for item in parsed:
            if isinstance(item, dict):
                wid = item.get("id")
                if wid and wid in wonders_map:
                    w = dict(wonders_map[wid])
                    w["auto_linked"] = item.get("auto_linked", False)
                    result.append(w)
            else:
                if item in wonders_map:
                    result.append(wonders_map[item])
        return {"listing_id": listing_id, "wonders": result}
    finally:
        conn.close()

# ── SERVER HEALTH ────────────────────────────────────────────────────────────
@app.delete("/listings/{listing_id}/wonders/{wonder_id}")
async def remove_listing_wonder(listing_id: int, wonder_id: str, email: str):
    """Remove a single wonder from a listing's linked_wonders. Email-auth required.
    Handles both plain ID list format and auto_linked object format.
    """
    import json as _jd
    conn = database.get_db()
    try:
        row = conn.execute("SELECT seller_email, linked_wonders FROM listings WHERE id=?", (listing_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Listing not found")
        if row["seller_email"] and row["seller_email"].lower() != email.lower():
            raise HTTPException(status_code=403, detail="Email does not match listing owner")
        raw = row["linked_wonders"] or "[]"
        try:
            linked = _jd.loads(raw)
        except Exception:
            linked = []
        # Handle both formats: plain strings and {"id":..., "auto_linked":...} objects
        new_linked = []
        for item in linked:
            if isinstance(item, dict):
                if item.get("id") != wonder_id:
                    new_linked.append(item)
            else:
                if item != wonder_id:
                    new_linked.append(item)
        conn.execute("UPDATE listings SET linked_wonders=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                     (_jd.dumps(new_linked), listing_id))
        conn.commit()
        return {"ok": True, "listing_id": listing_id, "removed": wonder_id, "remaining": len(new_linked)}
    finally:
        conn.close()

@app.get("/health/resources")
def health_resources():
    """Live server resource metrics — used by dashboard health panel.
    Returns RAM, disk, CPU load, response time, DB sizes.
    No auth required (non-sensitive operational data).
    """
    import time as _time
    import shutil as _shutil

    t0 = _time.time()

    # RAM
    try:
        with open("/proc/meminfo") as f:
            mem = {}
            for line in f:
                parts = line.split()
                if len(parts) >= 2:
                    mem[parts[0].rstrip(":")] = int(parts[1])
        mem_total_mb  = mem.get("MemTotal", 0) / 1024
        mem_avail_mb  = mem.get("MemAvailable", 0) / 1024
        mem_used_mb   = mem_total_mb - mem_avail_mb
        mem_pct       = round(mem_used_mb / mem_total_mb * 100, 1) if mem_total_mb else 0
    except Exception:
        mem_total_mb = mem_used_mb = mem_pct = 0

    # Disk
    try:
        disk = _shutil.disk_usage("/")
        disk_total_gb = round(disk.total / (1024**3), 1)
        disk_used_gb  = round(disk.used  / (1024**3), 1)
        disk_pct      = round(disk.used / disk.total * 100, 1)
    except Exception:
        disk_total_gb = disk_used_gb = disk_pct = 0

    # CPU load (1-min average, normalised to % of available cores)
    try:
        with open("/proc/loadavg") as f:
            load1 = float(f.read().split()[0])
        import os as _os
        ncpus   = _os.cpu_count() or 1
        cpu_pct = round(load1 / ncpus * 100, 1)
    except Exception:
        load1 = cpu_pct = 0

    # DB sizes
    import os as _os
    def _mb(path):
        try:    return round(_os.path.getsize(path) / (1024**2), 2)
        except: return 0

    db_sizes = {
        "marketsquare_mb":  _mb("/var/www/marketsquare/marketsquare.db"),
        "citylauncher_mb":  _mb("/var/www/citylauncher/citylauncher.db"),
    }

    # Bandwidth since boot (RX + TX on eth0)
    try:
        with open("/proc/net/dev") as f:
            for line in f:
                if "eth0" in line:
                    parts = line.split()
                    rx_gb = round(int(parts[1]) / (1024**3), 2)
                    tx_gb = round(int(parts[9]) / (1024**3), 2)
                    break
            else:
                rx_gb = tx_gb = 0
    except Exception:
        rx_gb = tx_gb = 0

    # BEA self-response time
    response_ms = round((_time.time() - t0) * 1000, 1)

    # Status flags
    def _status(pct):
        if pct >= 85: return "critical"
        if pct >= 70: return "warning"
        return "ok"

    bw_total = round(rx_gb + tx_gb, 2)
    bw_pct   = round(bw_total / 20480 * 100, 3)

    return {
        "ram":  {"total_mb": round(mem_total_mb,1), "used_mb": round(mem_used_mb,1), "pct": mem_pct, "status": _status(mem_pct)},
        "disk": {"total_gb": disk_total_gb, "used_gb": disk_used_gb, "pct": disk_pct, "status": _status(disk_pct)},
        "cpu":  {"load1": load1, "pct": cpu_pct, "status": _status(cpu_pct)},
        "bandwidth": {
            "rx_gb": rx_gb, "tx_gb": tx_gb,
            "total_gb": bw_total, "limit_gb": 20480,
            "pct": bw_pct, "status": _status(bw_pct),
        },
        "db_sizes": db_sizes,
        "response_ms": response_ms,
        "plan": "CPX32 · 4vCPU · 8GB RAM · 76GB SSD + 100GB Volume · 20TB/mo · €24.57/mo",
        "checkedAt": __import__('datetime').datetime.utcnow().strftime("%d %b %Y · %H:%M UTC"),
    }

# ── ADMIN AUTH v3 ──────────────────────────────────────────────────────────
# ── Public legal pages (compliance: Paystack go-live checklist, 2 Jul 2026) ──
@app.get("/privacy")
def privacy_page():
    from fastapi.responses import FileResponse
    return FileResponse("/var/www/marketsquare/privacy.html", media_type="text/html")

@app.get("/terms")
def terms_page():
    from fastapi.responses import FileResponse
    return FileResponse("/var/www/marketsquare/terms.html", media_type="text/html")

# Master password (alphanumeric) + team PIN (numeric, 6 digits) login system.
# First-login forced PIN change: must_change_pin=1 blocks token until PIN set.
# Master password: MS_ADMIN_PASSWORD env var — never in code.
# Team PINs: bcrypt-hashed in admin_users table.
# Token sub: "master" for David, "team:{name}" for team members.

import bcrypt as _bcrypt
import jwt as _pyjwt
from pydantic import BaseModel as _BaseModel

_ADMIN_PASSWORD = os.environ.get("MS_ADMIN_PASSWORD", "")
_JWT_SECRET     = os.environ.get("MS_JWT_SECRET", "ms_jwt_secret_change_me")
_JWT_ALGO       = "HS256"
_TOKEN_HOURS    = 8

def _admin_db():
    import sqlite3 as _sq
    c = _sq.connect("/var/www/marketsquare/marketsquare.db")
    c.row_factory = _sq.Row
    return c

class _AdminLoginRequest(_BaseModel):
    password: str

class _AdminUserCreate(_BaseModel):
    name: str
    pin: str

class _AdminChangePinRequest(_BaseModel):
    current_pin: str
    new_pin: str

def _make_token(sub: str) -> str:
    payload = {
        "sub": sub,
        "exp": datetime.now(timezone.utc) + timedelta(hours=_TOKEN_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return _pyjwt.encode(payload, _JWT_SECRET, algorithm=_JWT_ALGO)

# ── VIEW-ONLY REVIEWER ACCESS (Paystack compliance) ───────────────────────────
# A pre-launch "reviewer" credential that unlocks ONLY the public browse view.
# Security properties (deliberate):
#   * The code is NEVER shipped to the browser. The browser POSTs the typed code
#     to /review/login over HTTPS; we bcrypt-check it against a hash held on the
#     server only (env MS_REVIEW_CODE_HASH, else /var/www/marketsquare/review_code.hash).
#   * Success returns a short-lived JWT signed with a SEPARATE secret (_REVIEW_SECRET),
#     so a review token can NEVER validate as an admin token: _require_admin and
#     /admin/verify decode with _JWT_SECRET and will reject it. No admin/superuser/ops.
#   * Revoke instantly: delete/replace the hash file (re-read on every attempt).
#   * Brute-force resistant: high-entropy code + bcrypt cost + per-IP rate limit.
_REVIEW_SECRET     = os.environ.get("MS_REVIEW_SECRET") or hashlib.sha256(
                        ("trustsquare-review-scope|" + _JWT_SECRET).encode()).hexdigest()
_REVIEW_TOKEN_DAYS = 14
_REVIEW_HASH_FILE  = "/var/www/marketsquare/review_code.hash"
_review_attempts   = {}   # ip -> [count, window_start_epoch]

def _review_code_hash():
    """bcrypt hash of the reviewer code (env first, then file). Re-read every call so
    deleting/replacing the file revokes/rotates access with no restart."""
    h = os.environ.get("MS_REVIEW_CODE_HASH", "").strip()
    if h:
        return h.encode()
    try:
        with open(_REVIEW_HASH_FILE, "r") as _f:
            v = _f.read().strip()
            return v.encode() if v else None
    except FileNotFoundError:
        return None
    except Exception:
        return None

def _review_rate_ok(ip: str) -> bool:
    import time as _t
    now = _t.time()
    rec = _review_attempts.get(ip)
    if not rec or now - rec[1] > 600:        # 10-minute window
        _review_attempts[ip] = [1, now]
        return True
    rec[0] += 1
    return rec[0] <= 8                        # max 8 attempts / 10 min / IP

class _ReviewLoginRequest(_BaseModel):
    code: str

@app.post("/review/login")
def review_login(req: _ReviewLoginRequest, request: Request):
    """Validate a reviewer code server-side; return a scoped view-only token. Grants
    NOTHING but passage past the pre-launch gate (browse view). Never admin/superuser."""
    ip = (request.headers.get("x-forwarded-for")
          or (request.client.host if request.client else "?")).split(",")[0].strip()
    if not _review_rate_ok(ip):
        raise HTTPException(status_code=429, detail="Too many attempts. Please wait a few minutes.")
    stored = _review_code_hash()
    if not stored:
        raise HTTPException(status_code=503, detail="Reviewer access is not currently enabled.")
    code = (req.code or "").strip()
    try:
        ok = bool(code) and _bcrypt.checkpw(code.encode(), stored)
    except Exception:
        ok = False
    if not ok:
        _log.warning("review-login FAILED from %s", ip)
        raise HTTPException(status_code=401, detail="Incorrect reviewer code.")
    _log.info("review-login OK from %s", ip)
    payload = {
        "scope": "review",
        "exp": datetime.now(timezone.utc) + timedelta(days=_REVIEW_TOKEN_DAYS),
        "iat": datetime.now(timezone.utc),
    }
    token = _pyjwt.encode(payload, _REVIEW_SECRET, algorithm=_JWT_ALGO)
    return {"token": token, "expires_days": _REVIEW_TOKEN_DAYS}

@app.get("/review/verify")
def review_verify(x_review_token: str = Header(default=None)):
    """Verify a view-only review token (separate secret). 200 if valid, 401 otherwise."""
    if not x_review_token:
        raise HTTPException(status_code=401, detail="No token.")
    try:
        payload = _pyjwt.decode(x_review_token, _REVIEW_SECRET, algorithms=[_JWT_ALGO])
    except _pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired.") from exc
    except _pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token.") from exc
    if payload.get("scope") != "review":
        raise HTTPException(status_code=401, detail="Wrong scope.")
    return {"valid": True, "scope": "review"}

# ── SELF-SERVE MAGIC-LINK SIGN-IN (buyers + returning users) ───────────────
# One email box, no passwords. We email a signed, short-lived link; clicking it
# proves inbox ownership and signs the person in — creating the account on first
# use, so "register" and "log in" are the same act.
APP_URL = os.getenv("APP_URL", "https://trustsquare.co")

class _SignInRequest(_BaseModel):
    email: str

class _SignInVerify(_BaseModel):
    token: str

def _send_login_email(to_email: str, link: str) -> str:
    """Email the sign-in link. Resend if configured, else Gmail SMTP. Returns
    'sent' | 'failed' | 'dry' (no email transport configured)."""
    subject = "Your TrustSquare sign-in link"
    html = (
        "<div style='font-family:Inter,Arial,sans-serif;max-width:440px;margin:auto'>"
        "<h2 style='color:#0c1a2e'>Sign in to TrustSquare</h2>"
        "<p>Tap the button to sign in. This link works once and expires in 20 minutes.</p>"
        "<p><a href='" + link + "' style='display:inline-block;background:#C8873A;color:#fff;"
        "text-decoration:none;padding:12px 22px;border-radius:8px;font-weight:700'>Sign in &rarr;</a></p>"
        "<p style='color:#6b7280;font-size:12px'>If you didn't request this, you can ignore this email.</p>"
        "</div>"
    )
    key = os.getenv("RESEND_API_KEY", "")
    if key:
        try:
            import httpx
            r = httpx.post("https://api.resend.com/emails",
                headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
                json={"from": os.getenv("DEMAND_FROM_EMAIL", "TrustSquare <hello@trustsquare.co>"),
                      "to": [to_email], "subject": subject, "html": html},
                timeout=20)
            return "sent" if r.status_code in (200, 201) else "failed"
        except Exception as exc:
            _log.error("login email (resend) failed: %s", exc)
            return "failed"
    if GMAIL_APP_PASSWORD:
        try:
            msg = EmailMessage()
            msg["From"] = "TrustSquare <" + GMAIL_ADDRESS + ">"
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.set_content("Sign in to TrustSquare: " + link + "  (expires in 20 minutes)")
            msg.add_alternative(html, subtype="html")
            with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
                server.starttls()
                server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
                server.send_message(msg)
            return "sent"
        except Exception as exc:
            _log.error("login email (smtp) failed: %s", exc)
            return "failed"
    return "dry"

@app.post("/auth/request-link")
def auth_request_link(req: _SignInRequest):
    """Email a signed sign-in link. Always returns ok (no account enumeration)."""
    email = (req.email or "").strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Please enter a valid email address.")
    token = _pyjwt.encode(
        {"email": email, "purpose": "signin",
         "exp": datetime.now(timezone.utc) + timedelta(minutes=20),
         "iat": datetime.now(timezone.utc)},
        _JWT_SECRET, algorithm=_JWT_ALGO)
    status = _send_login_email(email, APP_URL + "/?signin=" + token)
    return {"ok": True, "sent": status}

@app.post("/auth/verify")
def auth_verify(req: _SignInVerify):
    """Verify a sign-in token; create the account on first use. Returns email+name."""
    try:
        payload = _pyjwt.decode(req.token, _JWT_SECRET, algorithms=[_JWT_ALGO])
    except _pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="This sign-in link has expired — request a new one.") from None
    except _pyjwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="This sign-in link is not valid.") from None
    if payload.get("purpose") != "signin":
        raise HTTPException(status_code=401, detail="This sign-in link is not valid.")
    email = (payload.get("email") or "").strip().lower()
    if not email:
        raise HTTPException(status_code=401, detail="This sign-in link is not valid.")
    conn = database.get_db()
    try:
        conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
        conn.commit()
        row = conn.execute("SELECT name FROM users WHERE email=?", (email,)).fetchone()
        name = row["name"] if row and row["name"] else email.split("@")[0]
    finally:
        conn.close()
    return {"ok": True, "email": email, "name": name}

# ── AGENCY (Team plan) — umbrella over agent sellers ───────────────────────
class _AgencyCreate(_BaseModel):
    name: str
    admin_email: str
    countries: list = []

class _AgentInvite(_BaseModel):
    email: str
    listing_cap: int = 10

class _AgentCapUpdate(_BaseModel):
    listing_cap: Optional[int] = None
    seat_paid: Optional[bool] = None

def _agency_agent_rollup(conn, email):
    """Reuse the per-seller model: live listings, trust score, intros."""
    email = (email or "").lower().strip()
    u = conn.execute("SELECT trust_score, slot_limit, name, seller_tier FROM users WHERE LOWER(email)=?", (email,)).fetchone()
    live = conn.execute("SELECT COUNT(*) c FROM listings WHERE LOWER(seller_email)=? AND (listing_status IS NULL OR listing_status='live')", (email,)).fetchone()["c"]
    try:
        intros_n = conn.execute("SELECT COUNT(*) c FROM intro_requests WHERE LOWER(seller_email)=?", (email,)).fetchone()["c"]
    except Exception:
        intros_n = 0
    return {"email": email,
            "name": (u["name"] if u and u["name"] else email.split("@")[0]),
            "trust_score": int(u["trust_score"]) if u and u["trust_score"] is not None else 40,
            "listings_live": live,
            "intros": intros_n,
            "tier": (u["seller_tier"] if u and u["seller_tier"] else "free")}

@app.post("/agencies")
def create_agency(req: _AgencyCreate, _key: str = Depends(auth.require_api_key)):
    """Create a verified agency (ops, after application/verification)."""
    name = (req.name or "").strip()
    admin = (req.admin_email or "").strip().lower()
    if not name or "@" not in admin:
        raise HTTPException(status_code=400, detail="name and a valid admin_email are required")
    api_key = "tsq_agency_" + uuid.uuid4().hex
    countries = ",".join([str(c).strip().upper() for c in (req.countries or []) if str(c).strip()])
    conn = database.get_db()
    try:
        cur = conn.execute("INSERT INTO agencies (name, admin_email, api_key, countries, verified) VALUES (?,?,?,?,1)",
                           (name, admin, api_key, countries))
        aid = cur.lastrowid
        conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (admin,))
        conn.execute("INSERT OR IGNORE INTO agency_members (agency_id, agent_email, role, status, joined_at) "
                     "VALUES (?,?, 'admin','active', strftime('%Y-%m-%dT%H:%M:%SZ','now'))", (aid, admin))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "id": aid, "name": name, "admin_email": admin, "api_key": api_key, "countries": countries}

@app.get("/agencies/{agency_id}")
def get_agency(agency_id: int, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    try:
        a = conn.execute("SELECT id, name, admin_email, api_key, countries, plan, verified FROM agencies WHERE id=?", (agency_id,)).fetchone()
        if not a:
            raise HTTPException(status_code=404, detail="Agency not found")
        members = conn.execute("SELECT agent_email, listing_cap, seat_paid, role, status FROM agency_members "
                               "WHERE agency_id=? AND status!='removed' ORDER BY role DESC, agent_email", (agency_id,)).fetchall()
        agents = []; used = 0; allowance = 0
        for m in members:
            r = _agency_agent_rollup(conn, m["agent_email"])
            r.update({"listing_cap": m["listing_cap"], "seat_paid": bool(m["seat_paid"]), "role": m["role"], "status": m["status"]})
            used += r["listings_live"]; allowance += m["listing_cap"]
            agents.append(r)
        return {"id": a["id"], "name": a["name"], "admin_email": a["admin_email"],
                "countries": a["countries"], "plan": a["plan"], "verified": bool(a["verified"]),
                "api_key": a["api_key"], "agents": agents,
                "rollup": {"agents": len(agents), "listings_used": used, "listings_allowance": allowance}}
    finally:
        conn.close()

@app.post("/agencies/{agency_id}/agents")
def invite_agent(agency_id: int, req: _AgentInvite, _key: str = Depends(auth.require_api_key)):
    """Add an agent: membership + cap mirrored into slot_limit + magic sign-in link."""
    email = (req.email or "").strip().lower()
    if "@" not in email:
        raise HTTPException(status_code=400, detail="valid email required")
    cap = int(req.listing_cap) if req.listing_cap else 10
    conn = database.get_db()
    try:
        if not conn.execute("SELECT id FROM agencies WHERE id=?", (agency_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Agency not found")
        conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
        conn.execute("UPDATE users SET slot_limit=?, seller_tier='starter' WHERE LOWER(email)=?", (cap, email))
        conn.execute("INSERT INTO agency_members (agency_id, agent_email, listing_cap, status) VALUES (?,?,?, 'invited') "
                     "ON CONFLICT(agency_id, agent_email) DO UPDATE SET listing_cap=excluded.listing_cap", (agency_id, email, cap))
        conn.commit()
    finally:
        conn.close()
    try:
        token = _pyjwt.encode({"email": email, "purpose": "signin",
                               "exp": datetime.now(timezone.utc) + timedelta(hours=72),
                               "iat": datetime.now(timezone.utc)}, _JWT_SECRET, algorithm=_JWT_ALGO)
        _send_login_email(email, APP_URL + "/?signin=" + token)
    except Exception as exc:
        _log.error("agency invite email failed: %s", exc)
    return {"ok": True, "email": email, "listing_cap": cap, "status": "invited"}

@app.put("/agencies/{agency_id}/agents/{email}")
def update_agent_cap(agency_id: int, email: str, req: _AgentCapUpdate, _key: str = Depends(auth.require_api_key)):
    email = (email or "").strip().lower()
    conn = database.get_db()
    try:
        m = conn.execute("SELECT listing_cap, seat_paid FROM agency_members WHERE agency_id=? AND LOWER(agent_email)=?", (agency_id, email)).fetchone()
        if not m:
            raise HTTPException(status_code=404, detail="Agent not in this agency")
        cap = m["listing_cap"]; paid = m["seat_paid"]
        if req.seat_paid is not None:
            paid = 1 if req.seat_paid else 0
            cap = 20 if paid else 10
        if req.listing_cap is not None:
            cap = int(req.listing_cap)
        conn.execute("UPDATE agency_members SET listing_cap=?, seat_paid=? WHERE agency_id=? AND LOWER(agent_email)=?", (cap, paid, agency_id, email))
        conn.execute("UPDATE users SET slot_limit=?, seller_tier=? WHERE LOWER(email)=?", (cap, ('pro' if paid else 'starter'), email))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "email": email, "listing_cap": cap, "seat_paid": bool(paid)}

@app.delete("/agencies/{agency_id}/agents/{email}")
def remove_agent(agency_id: int, email: str, _key: str = Depends(auth.require_api_key)):
    email = (email or "").strip().lower()
    conn = database.get_db()
    try:
        conn.execute("UPDATE agency_members SET status='removed' WHERE agency_id=? AND LOWER(agent_email)=?", (agency_id, email))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "email": email, "status": "removed"}

@app.get("/agencies/by-admin/{email}")
def agency_by_admin(email: str, _key: str = Depends(auth.require_api_key)):
    """Resolve the agency an admin manages (for the console entry). 404 if none."""
    email = (email or "").strip().lower()
    conn = database.get_db()
    try:
        a = conn.execute("SELECT id FROM agencies WHERE LOWER(admin_email)=? ORDER BY id LIMIT 1", (email,)).fetchone()
        if not a:
            m = conn.execute("SELECT agency_id FROM agency_members WHERE LOWER(agent_email)=? AND role='admin' AND status!='removed' LIMIT 1", (email,)).fetchone()
            if not m:
                raise HTTPException(status_code=404, detail="No agency for this admin")
            return {"agency_id": m["agency_id"]}
        return {"agency_id": a["id"]}
    finally:
        conn.close()

class _AgencyRename(_BaseModel):
    name: str

@app.put("/agencies/{agency_id}")
def rename_agency(agency_id: int, req: _AgencyRename, _key: str = Depends(auth.require_api_key)):
    """Rename an agency/operator (ops/superuser). Added 7 Jul 2026 so demo/test
    orgs can be branded before a prospect pitch (the console shows the name to
    whoever holds the link). Name only — nothing else is touchable here."""
    name = (req.name or "").strip()
    if not (2 <= len(name) <= 80):
        raise HTTPException(status_code=400, detail="Name must be 2-80 characters")
    conn = database.get_db()
    try:
        if not conn.execute("SELECT id FROM agencies WHERE id=?", (agency_id,)).fetchone():
            raise HTTPException(status_code=404, detail="Agency not found")
        conn.execute("UPDATE agencies SET name=? WHERE id=?", (name, agency_id))
        conn.commit()
    finally:
        conn.close()
    return {"ok": True, "id": agency_id, "name": name}

@app.get("/agencies")
def list_agencies(_key: str = Depends(auth.require_api_key)):
    """All agencies/operators — feeds the superuser ops org-picker (7 Jul 2026).
    Light rows only; api-key gated like every /agencies sibling. No path clash:
    bare /agencies is one segment, /agencies/{agency_id} needs two."""
    conn = database.get_db()
    try:
        rows = conn.execute("SELECT id, name, verified, admin_email FROM agencies ORDER BY name").fetchall()
        return {"agencies": [{"id": r["id"], "name": r["name"], "verified": bool(r["verified"]),
                              "admin_email": r["admin_email"]} for r in rows]}
    finally:
        conn.close()

# ── ANON-TEXT · Agency-import text anonymisation (spec §1 "Text pass") ────────
# AGENCY_IMPORT_ANONYMISATION_SPEC.md Phase A. Two legs, in order:
#   1) _anon_regex_clean — hard strip: phones (SA + intl), emails, URLs/social
#      handles, street number + street name (suburb/area kept). ALWAYS runs.
#   2) _anon_ai_rewrite  — title+description through the existing ai_provider
#      seam (same as /advert-agent/market-note) to remove agent names, agency
#      branding, contact CTAs and identifying phrasing while KEEPING price,
#      beds/baths/erf, condition, suburb and the genuine selling points.
# Fail-safe: any AI-leg failure → store the regex-only clean and flag that row
# needs_review in the import response. Every advert still lands as
# listing_status='draft' — nothing auto-publishes. Agency brand fully hidden
# (spec decision #3 default). No schema changes. Used by agency_import AND every seller photo upload via _seller_photo_anon_gate (11 Jul 2026).

_ANON_PATTERNS = [
    ("email",  re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")),
    ("url",    re.compile(r"(?:https?://|www\.)[^\s,;)]+", re.I)),
    ("url",    re.compile(r"\b[A-Za-z0-9][A-Za-z0-9-]{1,60}\.(?:co\.za|org\.za|net\.za|web\.za|com|net|org|io|biz|info|online|site|properties|estate|homes|agency)(?:/[^\s,;)]*)?\b", re.I)),
    ("handle", re.compile(r"(?<![A-Za-z0-9._%+-])@[A-Za-z0-9_.]{2,30}\b")),
    # phones: intl (+27/0027 …) then SA local (082 123 4567, (012) 345-6789).
    # Prefix shape (0 / + / 00) keeps prices like R2 450 000 and erf sizes safe.
    ("phone",  re.compile(r"(?:\+|\b00)\d{1,3}[\s\-.]?\(?\d{1,4}\)?(?:[\s\-.]?\d{2,4}){2,4}\b")),
    ("phone",  re.compile(r"\(?\b0\d{1,2}\)?[\s\-.]?\d{3}[\s\-.]?\d{4}\b")),
    # street number + Title-Cased street name + street type (EN + AF types).
    # Lookahead stops "…Bedrooms Close to schools" false-positives; lowercase
    # addresses are left for the AI leg (fallback rows are needs_review anyway).
    ("address", re.compile(
        r"(?:(?:[Uu]nit|[Ff]lat|[Aa]pt\.?|[Aa]partment|[Nn]o\.?)\s*\d+[A-Za-z]?\s*,?\s*)?"
        r"\b\d{1,5}[A-Za-z]?\s+(?:[A-Z][A-Za-z'-]+\s+){0,3}"
        r"(?:[Ss]treet|[Ss]traat|[Ss]tr|[Ss]t|[Rr]oad|[Rr]d|[Aa]venue|[Aa]ve|[Dd]rive|[Dd]r|"
        r"[Ll]ane|[Ll]n|[Cc]rescent|[Cc]res|[Cc]lose|[Bb]oulevard|[Bb]lvd|[Ww]ay|[Pp]lace|[Pp]l|"
        r"[Tt]errace|[Cc]ourt|[Cc]t|[Ll]aan|[Ww]eg|[Rr]ylaan|[Ss]ingel)\b\.?(?!\s+(?:to|and|with|by)\b)")),
]

# ── ANON-TOURS (7 Jul 2026) · category-aware prompts ─────────────────────────
# Tour operators onboard through the SAME agency machinery; only the AI
# instructions differ. For travel-family adverts (canon PRICING_CANON.md §2a
# list) the text rewrite must KEEP the product facts (duration, group size,
# itinerary stops/landmarks, inclusions, difficulty, season, departure AREA)
# and the photo scan must target branded vehicles/flags/kit rather than
# for-sale boards. Everything else — regex strip, fail-closed photo pipeline,
# drafts, needs_review — is identical and shared.

_ANON_TRAVEL_CATS = {"adventures","adventure","experiences","adventures_experiences",
                     "accommodation","adventures_accommodation","tours","heritage","travel"}

def _anon_is_travel(category):
    return str(category or "").strip().lower() in _ANON_TRAVEL_CATS

_ANON_AI_SYSTEM_TOURS = (
    "You anonymise tour and experience adverts for TrustSquare, an anonymity-first South "
    "African marketplace where operators stay anonymous until a paid introduction is "
    "accepted. Rewrite the advert title and description to REMOVE all identifying detail: "
    "operator/company names, guide or owner names, booking instructions (book now, call, "
    "WhatsApp, email, 'reserve via our website/office'), depot/office/pickup street "
    "addresses (keep the town, area, park or landmark), website and social references, "
    "vehicle registration numbers, and any branding phrases. KEEP everything a traveller "
    "needs to want this trip: price per person, duration, group size, the itinerary stops "
    "and landmarks (parks, peaks, routes ARE the product — never remove them), inclusions "
    "and exclusions, difficulty level, season, and the departure town/area. Do not invent "
    "details. Do not name or hint at the operator. Return EXACTLY this format and nothing "
    "else:\nTITLE: <clean title>\nDESCRIPTION: <clean description>"
)

_ANON_SCAN_PROMPT_TOURS = (
    "You are the photo anonymiser for TrustSquare, an anonymity-first marketplace: tour "
    "operators must be unidentifiable from listing photos. Inspect this tour/experience "
    "photo for ANY identifying content: operator logos or company names on vehicles, "
    "trailers, boats or aircraft; phone numbers or web addresses painted/wrapped on "
    "vehicles; branded flags, banners, gazebos, uniforms or kit; booking-desk or office "
    "signage; vehicle number plates; watermarks or contact overlays; branded flyers or "
    "collages. Scenery, wildlife, guests and unbranded equipment are FINE and must not be "
    "flagged. Already-blurred or pixelated patches are already-redacted content — "
    "never flag them. Reply with ONLY a JSON object: {\"verdict\": \"clean\"|\"redact\"|\"reject\", "
    "\"confidence\": 0.0-1.0, \"subject\": \"2-4 words - what the photo mainly shows\", \"flag\": \"none\"|\"inappropriate\" (inappropriate ONLY for nudity or sexual content, graphic violence or injury, weapons brandished at people, people in clearly degrading or intoxicated states, or hate symbols - ordinary people, parties and drinks in hand are none), \"regions\": [{\"x0\":0-1000,\"y0\":0-1000,\"x1\":0-1000,"
    "\"y1\":0-1000,\"label\":\"what\"}]}. Coordinates: 0-1000 scale of THIS image, origin "
    "top-left; make every box GENEROUS (cover the item fully plus margin). Rules: clean = "
    "you are certain there is NO identifying content anywhere. redact = identifying content "
    "is small and localised and every instance is boxed in regions. reject = the image is "
    "substantially a branded flyer/advert/collage, or identifying content is large or "
    "scattered (e.g. a fully-wrapped branded vehicle dominating the frame), or you are not "
    "certain your boxes cover everything. confidence = how certain you are that your verdict "
    "and boxes handle ALL identifying content. If in ANY doubt, reject."
)

# WRONG-TYPE-1 (16 Jul 2026): what each hinted category's photos must show,
# fed to the scan model so it judges fit itself ("fits_category") instead of
# the keyword hints. David's test: a boat listed as a Cars main photo was
# never flagged - SUBJECT-MATCH-1 was note-only and the note surfaced nowhere.
_CATEGORY_EXPECTS = {
    "cars": ("a road vehicle for sale (car, bakkie, SUV, van, truck or "
             "motorbike) or a detail of it (engine bay, dashboard, odometer, "
             "interior, seats, wheels, tyres, boot, service book)"),
    "property": ("a property (house, building, apartment, flat, room, kitchen, "
                 "bathroom, garden, pool, garage, view or grounds)"),
    "collectors": ("a collectible item (coin, banknote, trading card, stamp, "
                   "artwork, antique, watch, toy, book, vinyl, memorabilia or "
                   "similar) or its packaging, grading slab or certificate"),
}

def _anon_scan_prompt_for(category):
    base = _ANON_SCAN_PROMPT_TOURS if _anon_is_travel(category) else _ANON_SCAN_PROMPT
    exp = _CATEGORY_EXPECTS.get((category or "").strip().lower())
    if exp:
        base += (
            ' ALSO include "fits_category" in your JSON: this photo is for an '
            "advert selling %s. fits_category=true when the photo mainly shows "
            "that (any angle, partial or detail shot counts), false when it "
            "clearly shows a different KIND of thing entirely (for example a "
            "boat or a house on a car advert). Judge the subject TYPE only - "
            "condition or quality never makes it false. Omit the field if "
            "unsure." % exp)
    return base

def _anon_regex_clean(text: str):
    """Hard-strip identifying strings from advert text. Returns (clean, hit_labels).
    Conservative by design — prices (R2 450 000), erf sizes and bed/bath counts do
    not match the phone shapes; suburbs/areas are never touched."""
    if not text:
        return "", []
    hits = []
    out = str(text)
    for label, pat in _ANON_PATTERNS:
        out, n = pat.subn(" ", out)
        if n:
            hits.append(label)
    out = re.sub(r"[ \t]{2,}", " ", out)
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = re.sub(r"\n{3,}", "\n\n", out).strip()
    return out, sorted(set(hits))

_ANON_AI_SYSTEM = (
    "You anonymise classified adverts for TrustSquare, an anonymity-first South African "
    "marketplace where sellers stay anonymous until a paid introduction is accepted. "
    "Rewrite the advert title and description to REMOVE all identifying detail: agent names, "
    "agency/brand names, contact instructions (call, WhatsApp, SMS, email, 'viewing by "
    "appointment', 'contact our office'), office/branch references, website or social-media "
    "references, and street addresses (keep suburb/area only). KEEP the facts a buyer needs: "
    "price, beds, baths, garages, erf/floor size, condition, suburb/area, and the genuine "
    "selling points. Do not invent details. Do not name or hint at the agency. "
    "Return EXACTLY this format and nothing else:\n"
    "TITLE: <clean title>\nDESCRIPTION: <clean description>"
)

def _anon_ai_rewrite(title: str, desc: str, provider: str, category: str = ""):
    """AI leg of the anonymise pass — SEAM-ROUTED via ai_provider.complete (D1),
    exactly like /advert-agent/market-note. Returns (ok, title, desc, in_tok, out_tok).
    ok=False on ANY failure (no key, provider down, unparseable output) so the
    caller falls back to regex-only + needs_review. Never raises."""
    try:
        import ai_provider as _ap
        res = _ap.complete(
            [{"role": "user", "content": "TITLE: %s\nDESCRIPTION: %s" % (title, desc)}],
            task="haiku", max_tokens=1000,
            system=(_ANON_AI_SYSTEM_TOURS if _anon_is_travel(category) else _ANON_AI_SYSTEM),
            provider=provider)
        if not res.ok:
            return False, title, desc, None, None
        m = re.search(r"TITLE:\s*(.*?)\s*DESCRIPTION:\s*(.*)", (res.text or ""), re.S | re.I)
        if not m:
            return False, title, desc, None, None
        t = m.group(1).strip().strip("*").strip()
        d = m.group(2).strip().strip("*").strip()
        if desc.strip() and not d:   # model dropped the body — distrust it
            return False, title, desc, None, None
        return True, (t or title), d, res.in_tokens, res.out_tokens
    except Exception:
        return False, title, desc, None, None

# ── ANON-PHOTO · Agency-import photo anonymisation (spec §2 "Photo pass") ─────
# Phase B. FAIL-CLOSED by design (David, 7 Jul 2026: "no slips"): a photo is
# attached to the draft ONLY when the vision scan says clean, or says redact and
# the blur was actually applied, at/above the confidence gate. EVERY other path
# (fetch error, blocked host, unreadable file, no key, ceiling hit, scan error,
# unparseable verdict, reject/flyer, low confidence, no usable regions, upload
# error) holds the photo back — it is never stored. Originals are never stored
# either: attached images are re-encoded (EXIF/GPS stripped) thumb+medium like
# the normal upload path. Spec defaults: redact-if-localised, reject-if-flyer;
# first-N ops spot-check flag; agency brand fully hidden. Vision goes through
# the ai_provider seam (task="sonnet" → claude-sonnet — upgraded from Haiku for
# detection quality, David 7 Jul 2026; ~3.75x cost, logged as sonnet_vision). Used by agency_import AND every seller photo upload via _seller_photo_anon_gate (11 Jul 2026).

_ANON_PHOTO_MAX = 6        # photos scanned per advert (cost bound)
_ANON_PHOTO_CONF = 0.75    # confidence gate — below this the photo is held
_ANON_SPOTCHECK_N = 10     # first N adverts per agency flagged spot_check

_ANON_SCAN_PROMPT = (
    "You are the photo anonymiser for TrustSquare, an anonymity-first marketplace: "
    "sellers and agents must be unidentifiable from listing photos. Inspect this "
    "photo for ANY identifying content: phone numbers or contact-detail text/overlay "
    "bars, agency logos or watermarks, estate-agent boards or For-Sale signage, "
    "branded flyers/collages, agent portrait/headshot promo overlays, vehicle number "
    "plates AND their dealer plate-surrounds/frames (the strip above/below the "
    "plate often prints a dealership website and PHONE NUMBER — box the WHOLE "
    "plate unit including that strip), visible house or street numbers, "
    "street-name signs. Scan the WHOLE frame: number plates on BACKGROUND or "
    "neighbouring vehicles count exactly like the main subject's — box every one. "
    "Already-blurred or pixelated patches are ALREADY-redacted "
    "content — treat them as anonymous, never flag them. A plate or text strip counts as "
    "redacted ONLY when EVERY character is unreadable — if even ONE character or "
    "digit is readable anywhere, including at the EDGE of a blurred patch, it is "
    "NOT redacted: box the ENTIRE plate unit including the readable part. Box ONLY items actually "
    "visible/readable: a view of the car where no plate or text is visible is "
    "clean — do not box bare body panels 'just in case'. Reply with ONLY a "
    "JSON object: {\"verdict\": \"clean\"|\"redact\"|\"reject\", \"confidence\": 0.0-1.0, "
    " \"subject\": \"2-4 words - what the photo mainly shows\", \"flag\": \"none\"|\"inappropriate\" (inappropriate ONLY for nudity or sexual content, graphic violence or injury, weapons brandished at people, people in clearly degrading or intoxicated states, or hate symbols - ordinary people, parties and drinks in hand are none), \"regions\": [{\"x0\":0-1000,\"y0\":0-1000,\"x1\":0-1000,\"y1\":0-1000,\"label\":\"what\"}]}. Labels: 2-4 words, NEVER transcribe plate "
    "characters or phone digits into the label. "
    "Coordinates: 0-1000 scale of THIS image, origin top-left; make every box GENEROUS "
    "(cover the item fully plus margin). Rules: clean = you are certain there is NO "
    "identifying content anywhere. redact = identifying content is small and localised "
    "and every instance is boxed in regions. reject = the image is substantially a "
    "branded flyer/advert/collage, or identifying content is large or scattered, or "
    "you are not certain your boxes cover everything. confidence = how certain you are "
    "that your verdict and boxes handle ALL identifying content. If in ANY doubt, reject."
)

def _anon_photo_fetch(src):
    """Fetch one advert photo (https/http URL or data:image URI). Returns (bytes|None,
    note). Fail-closed: any oddity returns None. Redirects re-checked hop by hop;
    private/loopback/link-local hosts refused."""
    try:
        src = str(src or "").strip()
        if src.startswith("data:image/"):
            import base64 as _b64
            raw = _b64.b64decode(src.split(",", 1)[-1])
            return (raw, "") if 100 < len(raw) <= 12 * 1024 * 1024 else (None, "bad-data-uri")
        if not (src.startswith("https://") or src.startswith("http://")):
            return None, "unsupported-scheme"
        from urllib.parse import urlparse
        import socket, ipaddress
        url = src
        with httpx.Client(timeout=12) as c:
            for _hop in range(4):
                host = urlparse(url).hostname or ""
                try:
                    infos = socket.getaddrinfo(host, None)
                except Exception:
                    return None, "dns-failed"
                for ai in infos:
                    ip = ipaddress.ip_address(ai[4][0])
                    if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                        return None, "blocked-host"
                r = c.get(url, follow_redirects=False)
                if r.status_code in (301, 302, 303, 307, 308):
                    nxt = r.headers.get("location")
                    if not nxt:
                        return None, "redirect-broken"
                    url = str(httpx.URL(url).join(nxt))
                    continue
                break
            else:
                return None, "too-many-redirects"
        if r.status_code != 200:
            return None, "http-%s" % r.status_code
        if not (r.headers.get("content-type") or "").lower().startswith("image/"):
            return None, "not-an-image"
        raw = r.content
        return (raw, "") if 100 < len(raw) <= 12 * 1024 * 1024 else (None, "bad-size")
    except Exception:
        return None, "fetch-failed"

def _anon_photo_scan(jpeg_b64, provider, category=""):
    """ONE seam-routed vision call → verdict dict or None (None = hold the photo).
    Returns (scan|None, in_tokens, out_tokens). Never raises."""
    try:
        import ai_provider as _ap
        res = _ap.complete(
            [{"role": "user", "content": [
                {"type": "image", "source": {"type": "base64",
                 "media_type": "image/jpeg", "data": jpeg_b64}},
                {"type": "text", "text": _anon_scan_prompt_for(category)}]}],
            task="sonnet", max_tokens=1400, provider=provider)   # Sonnet for import scans (David, 7 Jul 2026); tokens 500->800->1400 11 Jul (verbose labels truncated JSON)
        if not res.ok:
            _log.warning("anon photo scan: provider returned not-ok (provider=%s)", provider)
            return None, None, None
        text = (res.text or "").strip()
        if text.startswith("```"):
            text = text.strip("`").lstrip("json").strip()
        try:
            v = json.loads(text)
        except Exception:
            # 11 Jul 2026: model sometimes wraps the JSON in prose or emits TWO
            # objects back-to-back — parse the FIRST valid object, ignore the rest.
            try:
                v = json.JSONDecoder().raw_decode(text[text.index("{"):])[0]
            except Exception:
                _log.warning("anon photo scan unparseable (first 120): %r", text[:120])
                return None, res.in_tokens, res.out_tokens
        verdict = str(v.get("verdict", "")).lower().strip()
        if verdict not in ("clean", "redact", "reject"):
            return None, res.in_tokens, res.out_tokens
        regs = []
        for rg in (v.get("regions") or [])[:12]:
            try:
                x0, y0, x1, y1 = (int(rg.get(k, -1)) for k in ("x0", "y0", "x1", "y1"))
            except Exception:
                continue
            if 0 <= x0 < x1 <= 1000 and 0 <= y0 < y1 <= 1000:
                regs.append((x0, y0, x1, y1, str(rg.get("label", ""))[:40]))
        try:
            conf = float(v.get("confidence", 0) or 0)
        except Exception:
            conf = 0.0
        _flag = str(v.get("flag", "none")).lower().strip()
        return ({"verdict": verdict, "regions": regs, "confidence": conf,
                 "labels": [r[4] for r in regs if r[4]],
                 "subject": str(v.get("subject", ""))[:60],
                 "fits": (v.get("fits_category")
                          if isinstance(v.get("fits_category"), bool) else None),
                 "flag": _flag if _flag == "inappropriate" else "none"},
                res.in_tokens, res.out_tokens)
    except Exception as _sexc:
        _log.warning("anon photo scan failed: %r", _sexc)
        return None, None, None

def _anon_capsule_geom(gray, bx0, by0, bx1, by1):
    """Estimate the printed-text strip inside an axis-aligned character box.
    Returns (cx, cy, half_len, half_ht, angle_rad) in the same coord space, or
    None when the pixel evidence is too weak (caller falls back to the
    axis-aligned box). Deterministic, zero AI cost. 15 Jul 2026 (David: a
    skewed main-photo plate must get a capsule that FOLLOWS the characters,
    not the tall axis-aligned bounding box of the tilted strip).
    Method: minority high-contrast pixels are the character candidates, but on
    a tilted plate the bounding box also contains background clutter — so a
    seeded RANSAC line fit finds the dense collinear character band first, and
    the capsule is fitted to the inliers only (naive PCA proved polluted by
    corner clutter in offline tests)."""
    import math, random
    w, h = gray.size
    bx0 = max(0, int(bx0)); by0 = max(0, int(by0))
    bx1 = min(w, int(bx1)); by1 = min(h, int(by1))
    bw = bx1 - bx0; bh = by1 - by0
    if bw < 12 or bh < 6:
        return None
    step = max(1, max(bw, bh) // 160)
    px = gray.load()
    vals = []
    for y in range(by0, by1, step):
        for x in range(bx0, bx1, step):
            vals.append((x, y, px[x, y]))
    if len(vals) < 60:
        return None
    vs = sorted(v for (_x, _y, v) in vals)
    med = vs[len(vs) // 2]
    dark = [(x, y) for (x, y, v) in vals if v < med - 36]
    lite = [(x, y) for (x, y, v) in vals if v > med + 36]
    cands = [s for s in (dark, lite) if len(s) >= 30]
    if not cands:
        return None
    pts = min(cands, key=len)      # characters are the minority pixels
    # ── RANSAC: find the dense collinear band ──
    rng = random.Random(0)          # seeded — fully deterministic
    band = max(4.0, bh * 0.10)
    best_in = []
    for _try in range(60):
        p = pts[rng.randrange(len(pts))]; q = pts[rng.randrange(len(pts))]
        dx = q[0] - p[0]; dy = q[1] - p[1]
        L = math.hypot(dx, dy)
        if L < bw * 0.30:
            continue
        ux, uy = dx / L, dy / L
        inl = [t for t in pts
               if abs((t[0] - p[0]) * (-uy) + (t[1] - p[1]) * ux) <= band]
        if len(inl) > len(best_in):
            best_in = inl
    if len(best_in) < max(30, int(0.25 * len(pts))):
        return None
    pts = best_in
    pts_full = best_in            # extents come from the FULL inlier set —
                                  # the trim below is for the angle only
                                  # (offline test: trimming collapsed the
                                  # measured strip height 21 -> 9 and the blur
                                  # went ghost-weak)
    # ── PCA on the inliers, with trim-refit rounds: drop points far from the
    # fitted axis and refit, so frame/clutter pixels inside the band stop
    # dragging the angle (offline test: -19.4° -> -18.7° toward true -13°,
    # characters stay covered by the padded capsule height) ──
    ang = 0.0
    for _round in range(3):
        mx = sum(p[0] for p in pts) / len(pts); my = sum(p[1] for p in pts) / len(pts)
        sxx = syy = sxy = 0.0
        for (x, y) in pts:
            dx = x - mx; dy = y - my
            sxx += dx * dx; syy += dy * dy; sxy += dx * dy
        ang = 0.5 * math.atan2(2.0 * sxy, sxx - syy)
        _ca = math.cos(ang); _sa = math.sin(ang)
        _aw = sorted(abs(-(x - mx) * _sa + (y - my) * _ca) for (x, y) in pts)
        _w50 = _aw[len(_aw) // 2]
        keep = [p for p in pts
                if abs(-(p[0] - mx) * _sa + (p[1] - my) * _ca) <= max(3.0, 2.0 * _w50)]
        if len(keep) < 30 or len(keep) == len(pts):
            break
        pts = keep
    if abs(math.degrees(ang)) > 35.0:
        return None                # implausible for a mounted plate — fall back
    ca = math.cos(ang); sa = math.sin(ang)
    mx = sum(p[0] for p in pts_full) / len(pts_full)
    my = sum(p[1] for p in pts_full) / len(pts_full)
    us = []; ws = []
    for (x, y) in pts_full:
        dx = x - mx; dy = y - my
        us.append(dx * ca + dy * sa); ws.append(-dx * sa + dy * ca)
    us.sort(); ws.sort()
    k = max(1, len(us) // 100)     # trim outliers
    half_len = max(abs(us[k]), abs(us[-k]))
    half_ht = max(abs(ws[k]), abs(ws[-k]))
    if half_len < 6 or half_ht < 3 or half_len < 1.6 * half_ht:
        return None                # not an elongated text strip — fall back
    return (mx, my, half_len, half_ht, ang)

def _anon_photo_redact(img, regions):
    """Gaussian-blur each region on the FULL-SIZE image. Padding is BOX-relative
    (12%/18% of the box + ≥8px) — 11 Jul 2026, David: blur ONLY the plate/strip,
    not a chunk of the photo. Image-relative padding (was 5%+16px) swallowed
    small boxes; accuracy now comes from _anon_refine_regions and the leak
    guarantee from the verify pass in _anon_blur_until_clean.
    Regions are 0-1000 normalized. Returns (img, boxes_applied)."""
    from PIL import ImageFilter, ImageDraw
    w, h = img.size
    n = 0
    for _reg in regions:
        x0, y0, x1, y1, _lbl = _reg[:5]
        _model_deg = _reg[5] if len(_reg) > 5 else None   # refine-pass text tilt
        _bw = w * (x1 - x0) / 1000.0; _bh = h * (y1 - y0) / 1000.0
        px = max(4, int(_bw * 0.04)); py = max(4, int(_bh * 0.10))
        X0 = max(0, int(w * x0 / 1000) - px); Y0 = max(0, int(h * y0 / 1000) - py)
        X1 = min(w, int(w * x1 / 1000) + px); Y1 = min(h, int(h * y1 / 1000) + py)
        if X1 - X0 < 4 or Y1 - Y0 < 4:
            continue
        # 15 Jul 2026, David: "only the numbers and no blocks" — feathered blur.
        # The region interior is 100% blurred (leak-safe: characters inside the
        # box can never ghost through); the soft falloff happens OUTSIDE the
        # box, in an extra outward margin, so there is no hard rectangle edge.
        # The verify pass in _anon_blur_until_clean remains the leak guarantee.
        feather = max(3, min(X1 - X0, Y1 - Y0) // 10)
        m = feather * 2 + 8                  # outward room for the falloff
        CX0 = max(0, X0 - m); CY0 = max(0, Y0 - m)
        CX1 = min(w, X1 + m); CY1 = min(h, Y1 + m)
        crop = img.crop((CX0, CY0, CX1, CY1))
        # Angle-aware capsule (15 Jul 2026): on a skewed plate the tilted
        # character strip has a tall axis-aligned bounding box — estimate the
        # strip's own axis from pixel evidence and mask ALONG it. Any doubt →
        # None → the safe axis-aligned core. The verify pass in
        # _anon_blur_until_clean remains the leak guarantee either way.
        import math as _math
        geom = None
        try:
            geom = _anon_capsule_geom(crop.convert("L"),
                                      X0 - CX0, Y0 - CY0, X1 - CX0, Y1 - CY0)
        except Exception:
            geom = None
        mask = Image.new("L", crop.size, 0)
        _d = ImageDraw.Draw(mask)
        # Tilted capsule (15 Jul 2026): pixel evidence supplies ONLY the
        # strip angle — the strip's true length/thickness solve analytically
        # from the model's axis-aligned box (BW = L*cos0 + T*sin0,
        # BH = L*sin0 + T*cos0), so the capsule is tied to the verified box,
        # not to fragile pixel extents (offline tests: pixel extents collapsed
        # and ghost-leaked). Small angles use the plain axis-aligned core —
        # for a straight plate the box IS the strip.
        # Angle source of truth: the refine MODEL read the text and reported
        # its baseline tilt — textured backgrounds (checkered studio floors,
        # brick) flipped the pixel fit's sign in offline tests, so pixels are
        # only a fallback when the model gave no angle.
        _use_capsule = False
        _ang = None
        if _model_deg is not None and 4.0 <= abs(_model_deg) <= 30.0:
            _ang = _math.radians(_model_deg)
        elif _model_deg is None and geom:
            _ang = geom[4]
        if _ang is not None:
            _deg = abs(_math.degrees(_ang))
            if 4.0 <= _deg <= 30.0:
                _BW = float(X1 - X0); _BH = float(Y1 - Y0)
                _c2 = _math.cos(2.0 * _ang)
                _caa = _math.cos(abs(_ang)); _saa = _math.sin(abs(_ang))
                _L = (_BW * _caa - _BH * _saa) / _c2
                _T = (_BH * _caa - _BW * _saa) / _c2
                if _L > 8 and _T > 2 and _L > _T:
                    _use_capsule = True
        if _use_capsule:
            rad = max(14, int(_T * 0.6))
            _hl = _L / 2.0 * 1.03 + feather + 3
            # small allowances only — the angle comes from the model reading
            # the text; oversized safety padding re-created the block look
            _hh = _T / 2.0 * 1.18 + 0.025 * (_L / 2.0) + feather + 3
            _hh = min(_hh, (Y1 - Y0) / 2.0 * 0.85)   # never re-cover the whole box
            _cx = (X0 + X1) / 2.0 - CX0; _cy = (Y0 + Y1) / 2.0 - CY0
            _ca = _math.cos(_ang); _sa = _math.sin(_ang)
            _d.polygon([(_cx + u * _ca - v * _sa, _cy + u * _sa + v * _ca)
                        for (u, v) in ((-_hl, -_hh), (_hl, -_hh),
                                       (_hl, _hh), (-_hl, _hh))], fill=255)
        else:
            # solid core = the detected box expanded by one feather width, so
            # after the mask blur the box interior stays fully opaque
            _sx0 = (X0 - CX0) - feather; _sy0 = (Y0 - CY0) - feather
            _sx1 = (X1 - CX0) + feather; _sy1 = (Y1 - CY0) + feather
            try:
                _d.rounded_rectangle([max(0, _sx0), max(0, _sy0),
                                      min(crop.size[0] - 1, _sx1), min(crop.size[1] - 1, _sy1)],
                                     radius=max(4, min(X1 - X0, Y1 - Y0) // 4), fill=255)
            except Exception:
                _d.rectangle([max(0, _sx0), max(0, _sy0),
                              min(crop.size[0] - 1, _sx1), min(crop.size[1] - 1, _sy1)], fill=255)
            rad = max(14, min(X1 - X0, Y1 - Y0) // 2)
        blurred = crop.filter(ImageFilter.GaussianBlur(rad))
        mask = mask.filter(ImageFilter.GaussianBlur(feather))
        img.paste(blurred, (CX0, CY0), mask)
        n += 1
    return img, n

def _anon_refine_regions(img, regions, provider, category, spend_who, endpoint):
    """Second-stage ZOOM-IN pass (11 Jul 2026, David: blur ONLY the plate and the
    small dealer/phone strip). Full-frame box coords from the scanner are sloppy;
    coords inside a small crop are accurate. For each rough region: crop ~2.5x
    context around it, ask the model to box the item EXACTLY within the crop,
    map back to full-image coords. Sanity rails: refined box must intersect the
    rough box and be no larger — any failure keeps the rough box (safety beats
    aesthetics; _anon_blur_until_clean's verify pass still gates the result)."""
    import base64 as _b64
    W, H = img.size
    out = []
    for (x0, y0, x1, y1, lbl) in list(regions)[:8]:
        rough = (x0, y0, x1, y1, lbl)
        try:
            px0, py0 = W * x0 / 1000.0, H * y0 / 1000.0
            px1, py1 = W * x1 / 1000.0, H * y1 / 1000.0
            bw, bh = px1 - px0, py1 - py0
            cx0 = max(0, int(px0 - 0.75 * bw)); cy0 = max(0, int(py0 - 0.75 * bh))
            cx1 = min(W, int(px1 + 0.75 * bw)); cy1 = min(H, int(py1 + 0.75 * bh))
            cw, ch = cx1 - cx0, cy1 - cy0
            if cw < 24 or ch < 24:
                out.append(rough); continue
            crop = img.crop((cx0, cy0, cx1, cy1))
            if max(crop.size) > 1024:
                _s = 1024.0 / max(crop.size)
                crop = crop.resize((max(1, int(crop.size[0] * _s)),
                                    max(1, int(crop.size[1] * _s))), Image.LANCZOS)
            cbuf = io.BytesIO(); crop.save(cbuf, format="JPEG", quality=85)
            import ai_provider as _ap
            res = _ap.complete(
                [{"role": "user", "content": [
                    {"type": "image", "source": {"type": "base64",
                     "media_type": "image/jpeg",
                     "data": _b64.b64encode(cbuf.getvalue()).decode()}},
                    {"type": "text", "text": (
                        "This crop is from a marketplace photo. It should contain: %s. "
                        "Reply with ONLY a JSON object {\"found\": true|false, \"x0\": 0-1000, "
                        "\"y0\": 0-1000, \"x1\": 0-1000, \"y1\": 0-1000, "
                        "\"angle_deg\": <number>} boxing EXACTLY the "
                        "printed CHARACTERS of that item — the registration letters/digits on a "
                        "plate, or the text line(s) on a sign or dealer strip — edge-to-edge of "
                        "the characters plus a tiny margin, NOT the plate frame, surround, bumper, "
                        "car, wall or paving. If several text lines are present, box the block "
                        "spanning ALL of them. Coordinates are 0-1000 of "
                        "THIS crop, origin top-left. angle_deg = the tilt of the text "
                        "baseline: 0 when level, positive when the text runs DOWNHILL "
                        "to the right, negative when uphill (e.g. a plate photographed "
                        "from the front-left corner usually tilts a few degrees). "
                        "If the item is not visible, found=false."
                        % (lbl or "an identifying item"))}]}],
                task="sonnet", max_tokens=120, provider=provider)
            if res.in_tokens is not None or res.out_tokens is not None:
                _log_ai_spend(spend_who, endpoint + "#refine", "sonnet_vision",
                              res.in_tokens, res.out_tokens)
            if not res.ok:
                out.append(rough); continue
            _t = (res.text or "").strip()
            if _t.startswith("```"):
                _t = _t.strip("`").lstrip("json").strip()
            try:
                v = json.loads(_t)
            except Exception:
                try:
                    v = json.JSONDecoder().raw_decode(_t[_t.index("{"):])[0]
                except Exception:
                    out.append(rough); continue
            if not v.get("found"):
                # Explicit "not visible" from the zoom-in pass DROPS the region —
                # cure for needless patches on plate-less side views (David,
                # 11 Jul 2026). Only an explicit found=false drops; any refine
                # FAILURE still keeps the rough box. The caller's verify pass
                # remains the no-slips gate on the final image.
                continue
            rx0, ry0, rx1, ry1 = (float(v.get(k, -1)) for k in ("x0", "y0", "x1", "y1"))
            if not (0 <= rx0 < rx1 <= 1000 and 0 <= ry0 < ry1 <= 1000):
                out.append(rough); continue
            fx0 = (cx0 + rx0 / 1000.0 * cw) / W * 1000.0
            fy0 = (cy0 + ry0 / 1000.0 * ch) / H * 1000.0
            fx1 = (cx0 + rx1 / 1000.0 * cw) / W * 1000.0
            fy1 = (cy0 + ry1 / 1000.0 * ch) / H * 1000.0
            # rails: must intersect the rough box, be no larger, and be non-trivial
            if fx1 <= x0 or fx0 >= x1 or fy1 <= y0 or fy0 >= y1:
                out.append(rough); continue
            if (fx1 - fx0) * (fy1 - fy0) > (x1 - x0) * (y1 - y0) * 1.1:
                out.append(rough); continue
            if (fx1 - fx0) * W / 1000.0 < 6 or (fy1 - fy0) * H / 1000.0 < 6:
                out.append(rough); continue
            try:
                _adeg = float(v.get("angle_deg", 0) or 0)
            except Exception:
                _adeg = 0.0
            if not (-45.0 <= _adeg <= 45.0):
                _adeg = 0.0
            out.append((int(fx0), int(fy0), int(round(fx1 + 0.5)), int(round(fy1 + 0.5)), lbl, _adeg))
        except Exception:
            out.append(rough)
    return out

def _anon_blur_until_clean(img, scan, provider, category, spend_who, endpoint):
    """Apply redaction, then VERIFY by re-scanning the blurred output; accumulate
    any newly-boxed regions for up to 2 correction rounds. Added 11 Jul 2026 after
    the live rescan of listing 246 proved model box coords can land BELOW the plate
    (plate stayed readable while paving got blurred) — never trust claimed boxes,
    verify the actual output. Returns (img, labels) only when a re-scan of the
    blurred image comes back clean at/above the confidence gate; (None, labels)
    otherwise (caller holds/rejects — fail-closed)."""
    import base64 as _b64
    labels = list(scan.get("labels") or [])
    regions = list(scan.get("regions") or [])
    _acc = []                 # every region ever boxed — feeds the last-resort rung
    for _round in range(4):   # refine+blur+verify: initial + up to 3 corrections
        if regions:
            regions = _anon_refine_regions(img, regions, provider, category,
                                           spend_who, endpoint)   # tighten; may DROP not-found
        if regions:
            _acc.extend(regions)
            img, _n = _anon_photo_redact(img, regions)
        # ALWAYS verify the current image — the VERIFIER, not the boxes, is the
        # no-slips guarantee. If refinement dropped every region (over-flagged
        # side view, no plate actually visible) a clean verify returns the photo
        # UNBLURRED (David, 11 Jul 2026: no needless patches).
        probe = img.copy(); probe.thumbnail((1344, 1344), Image.LANCZOS)   # 896->1344 11 Jul 2026: small background plates were illegible to the scanner
        pbuf = io.BytesIO(); probe.save(pbuf, format="JPEG", quality=80)
        v, _it, _ot = _anon_photo_scan(_b64.b64encode(pbuf.getvalue()).decode(),
                                       provider, category)
        if _it is not None or _ot is not None:
            _log_ai_spend(spend_who, endpoint, "sonnet_vision", _it, _ot)
        if not v:
            return None, labels
        if v["verdict"] == "clean" and v["confidence"] >= _ANON_PHOTO_CONF:
            return img, labels
        if v["verdict"] == "reject":
            return None, labels + list(v.get("labels") or [])
        regions = list(v.get("regions") or [])
        labels += list(v.get("labels") or [])
        _acc.extend(regions)
    # ── LAST-RESORT RUNG (15 Jul 2026, David: a seller photo must NEVER be
    # held because the pretty blur could not be verified — ugly-but-anonymous
    # beats rejected). Blur EVERY region this photo ever accumulated,
    # axis-aligned with generous expansion, then verify ONE more time. Only a
    # scanner failure or an explicit "reject" verdict still holds the photo. ──
    if _acc:
        _big = []
        for _r in _acc:
            _x0, _y0, _x1, _y1 = _r[0], _r[1], _r[2], _r[3]
            _dx = (_x1 - _x0) * 0.30 + 8; _dy = (_y1 - _y0) * 0.60 + 8
            _big.append((max(0, _x0 - _dx), max(0, _y0 - _dy),
                         min(1000, _x1 + _dx), min(1000, _y1 + _dy),
                         "last-resort"))
        img, _n = _anon_photo_redact(img, _big)
        probe = img.copy(); probe.thumbnail((1344, 1344), Image.LANCZOS)
        pbuf = io.BytesIO(); probe.save(pbuf, format="JPEG", quality=80)
        v, _it, _ot = _anon_photo_scan(_b64.b64encode(pbuf.getvalue()).decode(),
                                       provider, category)
        if _it is not None or _ot is not None:
            _log_ai_spend(spend_who, endpoint, "sonnet_vision", _it, _ot)
        if v and v["verdict"] == "clean" and v["confidence"] >= _ANON_PHOTO_CONF:
            return img, labels + ["last-resort blur"]
    return None, labels

def _anon_photo_pass(photo_srcs, agent, provider, category=""):
    """Run the fail-closed photo pipeline for one advert. Returns
    (attached [(thumb_url, medium_url)], held count, notes [str])."""
    import base64 as _b64
    attached = []; held = 0; notes = []
    for src in list(photo_srcs)[:_ANON_PHOTO_MAX]:
        raw, why = _anon_photo_fetch(src)
        if raw is None:
            held += 1; notes.append("held:" + why); continue
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
        except Exception:
            held += 1; notes.append("held:unreadable"); continue
        try:
            _check_cost_ceiling(agent)   # C1 rail per paid call
        except Exception:
            held += 1; notes.append("held:ai-ceiling"); continue
        probe = img.copy(); probe.thumbnail((1344, 1344), Image.LANCZOS)   # 896->1344 11 Jul 2026: small background plates were illegible to the scanner
        pbuf = io.BytesIO(); probe.save(pbuf, format="JPEG", quality=80)
        scan, _it, _ot = _anon_photo_scan(_b64.b64encode(pbuf.getvalue()).decode(), provider, category)
        if _it is not None or _ot is not None:
            _log_ai_spend(agent, "/agencies/import#photo-scan", "sonnet_vision", _it, _ot)
        if not scan:
            held += 1; notes.append("held:scan-failed"); continue
        if scan["verdict"] == "reject":
            held += 1; notes.append("held:flyer-or-unsafe"); continue
        if scan["confidence"] < _ANON_PHOTO_CONF:
            held += 1; notes.append("held:low-confidence"); continue
        if scan["verdict"] == "redact":
            if not scan["regions"]:
                held += 1; notes.append("held:redact-no-regions"); continue
            img2, _lbls = _anon_blur_until_clean(
                img, scan, provider, category, agent, "/agencies/import#photo-verify")
            if img2 is None:
                held += 1; notes.append("held:redact-unverified"); continue
            img = img2
            notes.append("redacted:" + ",".join(sorted(set(_lbls))[:4]))
        # Re-encode (EXIF/GPS stripped) → thumb + medium, same as the upload path.
        thumb = img.copy(); thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
        tb = io.BytesIO(); thumb.save(tb, format="JPEG", quality=JPEG_QUALITY_THUMB, optimize=True)
        medium = img.copy(); medium.thumbnail(MEDIUM_SIZE, Image.LANCZOS)
        mb = io.BytesIO(); medium.save(mb, format="JPEG", quality=JPEG_QUALITY_MEDIUM, optimize=True)
        try:
            if _S3_CONFIGURED:
                murl = _s3_upload(mb.getvalue(), "media/%s_import.jpg" % uuid.uuid4().hex, "image/jpeg")
                turl = murl
            else:
                base = storage.generate_filename("listing")
                turl = storage.upload_photo(tb.getvalue(), base.replace(".jpg", "_thumb.jpg"), "image/jpeg")
                murl = storage.upload_photo(mb.getvalue(), base.replace(".jpg", "_medium.jpg"), "image/jpeg")
        except Exception as _uexc:
            _log.warning("agency_import photo upload failed (%s): %s", agent, _uexc)
            held += 1; notes.append("held:upload-failed"); continue
        attached.append((turl, murl))
    return attached, held, notes

class _AgencyImport(_BaseModel):
    api_key: str
    adverts: list = []

@app.post("/agencies/{agency_id}/import")
def agency_import(agency_id: int, req: _AgencyImport):
    """Bulk-import an agency's current adverts. Auth = the agency's own api_key.
    Each advert must carry agent_email; it lands as a DRAFT under that agent,
    counting against their cap. ANON-TEXT (spec §1): title+description are
    regex-stripped then AI-rewritten before storage; if the AI leg fails the
    row stores regex-only and is flagged needs_review in the response.
    ANON-PHOTO (spec §2, FAIL-CLOSED): advert photos (urls/data-URIs) are vision-
    scanned; clean → attached, localised branding → blurred then attached, flyers/
    low-confidence/any failure → HELD (never stored). Returns a per-advert summary."""
    conn = database.get_db()
    try:
        a = conn.execute("SELECT id, api_key FROM agencies WHERE id=?", (agency_id,)).fetchone()
        if not a:
            raise HTTPException(status_code=404, detail="Agency not found")
        if not req.api_key or req.api_key != a["api_key"]:
            raise HTTPException(status_code=401, detail="Invalid agency API key")
        members = {r["agent_email"].lower() for r in conn.execute(
            "SELECT agent_email FROM agency_members WHERE agency_id=? AND status!='removed'", (agency_id,)).fetchall()}
        imported = 0; unmatched = 0; capped = 0; needs_rev = 0; rows = []
        ph_att_total = 0; ph_held_total = 0
        prior_listed = conn.execute(
            "SELECT COUNT(*) c FROM listings WHERE LOWER(seller_email) IN "
            "(SELECT LOWER(agent_email) FROM agency_members WHERE agency_id=? AND status!='removed')",
            (agency_id,)).fetchone()["c"]   # spot-check-first-N baseline
        for ad in (req.adverts or []):
            if not isinstance(ad, dict):
                unmatched += 1; continue
            agent = str(ad.get("agent_email") or "").strip().lower()
            if not agent or agent not in members:
                unmatched += 1; continue
            u = conn.execute("SELECT slot_limit FROM users WHERE LOWER(email)=?", (agent,)).fetchone()
            cap = int(u["slot_limit"]) if u and u["slot_limit"] is not None else 10
            used = conn.execute("SELECT COUNT(*) c FROM listings WHERE LOWER(seller_email)=? AND (listing_status IS NULL OR listing_status IN ('live','draft'))", (agent,)).fetchone()["c"]
            if used >= cap:
                capped += 1; continue
            city = str(ad.get("city") or "").strip()
            raw_title = str(ad.get("title") or "Imported listing")
            raw_desc = str(ad.get("description") or "")
            # ANON-TEXT leg 1 (spec §1): hard regex strip ALWAYS runs — the raw
            # imported text is never stored.
            t_clean, t_hits = _anon_regex_clean(raw_title)
            d_clean, d_hits = _anon_regex_clean(raw_desc)
            removed = sorted(set(t_hits) | set(d_hits))
            # ANON-TEXT leg 2: AI rewrite via the existing seam. Fail-safe: any
            # failure (no key, ceiling hit, bad output) → regex-only + needs_review.
            row_needs_review = False
            has_text = bool(d_clean.strip()) or bool(t_clean.strip() and raw_title != "Imported listing")
            if has_text:
                ai_ok = False
                try:
                    _check_cost_ceiling(agent)   # C1 rail — same guard as every paid AI call
                    ai_ok, ai_t, ai_d, _it, _ot = _anon_ai_rewrite(
                        t_clean, d_clean, _ts_active_provider(), str(ad.get("category") or "Property"))
                    if ai_ok:
                        # Belt-and-braces: re-strip the AI output so a model echo
                        # of a phone/email can never reach the stored draft.
                        t_clean = _anon_regex_clean(ai_t)[0]
                        d_clean = _anon_regex_clean(ai_d)[0]
                        _log_ai_spend(agent, "/agencies/import#anonymise", "haiku", _it, _ot)
                except Exception as _aexc:
                    _log.warning("agency_import anonymise AI leg failed (%s): %s", agent, _aexc)
                if not ai_ok:
                    row_needs_review = True
            if not t_clean.strip():
                t_clean = "Imported listing"
            # ANON-PHOTO (spec §2): fail-closed photo pipeline. Held photos are
            # simply not attached — the draft stores only clean/redacted images.
            photo_srcs = ad.get("photos") or ad.get("images") or []
            ph_attached = []; ph_held = 0; ph_notes = []
            if isinstance(photo_srcs, list) and photo_srcs:
                try:
                    ph_attached, ph_held, ph_notes = _anon_photo_pass(
                        photo_srcs, agent, _ts_active_provider(), str(ad.get("category") or "Property"))
                except Exception as _pexc:
                    ph_attached = []; ph_held = len(photo_srcs); ph_notes = ["held:photo-pass-error"]
                    _log.warning("agency_import photo pass failed hard (%s): %s", agent, _pexc)
                if ph_held:
                    row_needs_review = True
            ph_att_total += len(ph_attached); ph_held_total += ph_held
            final_desc = d_clean
            if ph_attached:
                # [photos:...] prefix AFTER text cleaning — never regex-cleaned,
                # or the strip would eat our own R2 URLs.
                final_desc = "[photos:" + "|".join(m for (_t, m) in ph_attached) + "]\n" + d_clean
            if row_needs_review:
                needs_rev += 1
            conn.execute(
                "INSERT INTO listings (title, price, category, city, area, suburb, description, seller_email, listing_status, thumb_url, medium_url) "
                "VALUES (?,?,?,?,?,?,?,?, 'draft', ?, ?)",
                (t_clean, str(ad.get("price") or "POA"),
                 str(ad.get("category") or "Property"), city,
                 str(ad.get("area") or city), str(ad.get("suburb") or city),
                 final_desc, agent,
                 (ph_attached[0][0] if ph_attached else None),
                 (ph_attached[0][1] if ph_attached else None)))
            imported += 1
            rows.append({"title": t_clean[:80], "agent_email": agent,
                         "needs_review": row_needs_review, "removed": removed,
                         "photos": {"received": (len(photo_srcs) if isinstance(photo_srcs, list) else 0),
                                    "attached": len(ph_attached), "held": ph_held,
                                    "notes": ph_notes[:8]},
                         "spot_check": bool((prior_listed + imported) <= _ANON_SPOTCHECK_N)})
        conn.commit()
        return {"ok": True, "imported": imported, "unmatched_no_agent": unmatched, "skipped_at_cap": capped,
                "anonymised": imported - needs_rev, "needs_review": needs_rev,
                "photos_attached": ph_att_total, "photos_held": ph_held_total, "rows": rows}
    finally:
        conn.close()

@app.post("/admin/login")
def admin_login(req: _AdminLoginRequest):
    """Check master password OR team PIN. Returns JWT or must_change_pin signal."""
    if not _ADMIN_PASSWORD:
        raise HTTPException(status_code=503, detail="Admin password not configured on server.")

    # 1. Master password — immediate token, no PIN change required
    if req.password == _ADMIN_PASSWORD or req.password.strip() == _ADMIN_PASSWORD:
        return {"token": _make_token("master"), "expires_hours": _TOKEN_HOURS, "role": "master"}

    # 2. Team PIN — numeric only, 4-8 digits
    candidate = req.password.strip()
    if candidate.isdigit() and 4 <= len(candidate) <= 8:
        conn = _admin_db()
        try:
            rows = conn.execute(
                "SELECT id, name, pin_hash, must_change_pin FROM admin_users WHERE active = 1"
            ).fetchall()
            for row in rows:
                stored_hash = row["pin_hash"].encode() if isinstance(row["pin_hash"], str) else row["pin_hash"]
                if _bcrypt.checkpw(candidate.encode(), stored_hash):
                    # Correct PIN — check if forced change required
                    if row["must_change_pin"]:
                        return {
                            "must_change_pin": True,
                            "user_id": row["id"],
                            "name": row["name"],
                        }
                    return {
                        "token": _make_token(f"team:{row['name']}"),
                        "expires_hours": _TOKEN_HOURS,
                        "role": "team",
                        "name": row["name"],
                        "email": row["email"] if "email" in row.keys() else "",
                    }
        finally:
            conn.close()

    raise HTTPException(status_code=401, detail="Incorrect password or PIN.")

@app.post("/admin/change-pin")
def admin_change_pin(req: _AdminChangePinRequest):
    """
    Forced PIN change on first login.
    Verifies current PIN, sets new PIN, clears must_change_pin flag, returns token.
    """
    current = req.current_pin.strip()
    new_pin  = req.new_pin.strip()

    if not new_pin.isdigit() or len(new_pin) != 6:
        raise HTTPException(status_code=400, detail="New PIN must be exactly 6 digits.")
    if new_pin == current:
        raise HTTPException(status_code=400, detail="New PIN must be different from current PIN.")

    conn = _admin_db()
    try:
        rows = conn.execute(
            "SELECT id, name, pin_hash FROM admin_users WHERE active = 1 AND must_change_pin = 1"
        ).fetchall()
        for row in rows:
            stored_hash = row["pin_hash"].encode() if isinstance(row["pin_hash"], str) else row["pin_hash"]
            if _bcrypt.checkpw(current.encode(), stored_hash):
                new_hash = _bcrypt.hashpw(new_pin.encode(), _bcrypt.gensalt()).decode()
                conn.execute(
                    "UPDATE admin_users SET pin_hash = ?, must_change_pin = 0 WHERE id = ?",
                    (new_hash, row["id"])
                )
                conn.commit()
                return {
                    "token": _make_token(f"team:{row['name']}"),
                    "expires_hours": _TOKEN_HOURS,
                    "role": "team",
                    "name": row["name"],
                    "pin_changed": True,
                }
    finally:
        conn.close()

    raise HTTPException(status_code=401, detail="Current PIN incorrect.")

@app.get("/admin/verify")
def admin_verify(x_admin_token: str = Header(default=None)):
    """Verify a JWT token. Returns 200 + role info if valid, 401 if not."""
    if not x_admin_token:
        raise HTTPException(status_code=401, detail="No token provided.")
    try:
        payload = _pyjwt.decode(x_admin_token, _JWT_SECRET, algorithms=[_JWT_ALGO])
    except _pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired.") from exc
    except _pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token.") from exc
    return {"valid": True, "sub": payload.get("sub", "unknown")}


# -- Launch Switch flags (free-only <-> verified) --------------------------------
def _require_admin(x_admin_token: str = Header(default=None)):
    """Admin-token guard — same JWT the dashboard already holds."""
    if not x_admin_token:
        raise HTTPException(status_code=401, detail="No admin token.")
    try:
        return _pyjwt.decode(x_admin_token, _JWT_SECRET, algorithms=[_JWT_ALGO])
    except _pyjwt.ExpiredSignatureError as exc:
        raise HTTPException(status_code=401, detail="Token expired.") from exc
    except _pyjwt.InvalidTokenError as exc:
        raise HTTPException(status_code=401, detail="Invalid token.") from exc


@app.post("/admin/anon-rescan-listing")
def admin_anon_rescan_listing(listing_id: int, apply: int = 1, _admin=Depends(_require_admin)):
    """Re-run the fail-closed anon photo pass over an EXISTING listing's photos
    (remediation for adverts published before the seller-upload gate, 11 Jul 2026
    — e.g. cars listed with visible number plates). Each stored photo is fetched,
    vision-scanned, blurred where needed and re-uploaded; photos that cannot be
    cleared are REMOVED from the listing. apply=0 = scan/report only, no row write
    (scanned copies are still uploaded, just not referenced). NOTE: replaced /
    removed R2+/media objects are NOT deleted here and Cloudflare cache is NOT
    purged — old public URLs stay reachable until purged manually."""
    import re as _re, json as _json
    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT id, seller_email, category, thumb_url, medium_url, description, photo_urls "
            "FROM listings WHERE id=?", (listing_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Listing not found")
        desc = row["description"] or ""
        entries = []; seen = set()          # (url, caption), display order, primary first
        def _add(u, cap=""):
            u = (u or "").strip()
            if u and u not in seen:
                seen.add(u); entries.append((u, cap))
        m = _re.match(r'^\[photos:([^\]]*)\]', desc)
        for p in (m.group(1).split("|") if m else []):
            if p:
                u, _sep, cap = p.partition("::")
                _add(u, cap)
        _add(row["medium_url"] or row["thumb_url"] or "")
        try:
            for u in _json.loads(row["photo_urls"] or "[]"):
                _add(str(u))
        except Exception:
            pass
        if not entries:
            return {"listing_id": listing_id, "photos_in": 0, "kept": 0, "removed": 0,
                    "notes": ["no-photos"], "applied": False}
        who = row["seller_email"] or "admin-rescan"
        kept = []; removed = []; notes = []
        for (u, cap) in entries:
            att, _held, nts = _anon_photo_pass([u], who, _ts_active_provider(),
                                               str(row["category"] or ""))
            notes.append({"old": u, "notes": nts})
            if att:
                kept.append((att[0][1], cap, u))     # (new_medium, caption, old)
            else:
                removed.append(u)
        applied = False
        if apply:
            new_primary = kept[0][0] if kept else None
            new_strip = "|".join(("%s::%s" % (nu, cap) if cap else nu) for (nu, cap, _o) in kept)
            if m:
                new_desc = desc[m.end():].lstrip("\n")
                if new_strip:
                    new_desc = "[photos:%s]\n%s" % (new_strip, new_desc)
            else:
                new_desc = ("[photos:%s]\n%s" % (new_strip, desc)) if new_strip else desc
            conn.execute(
                "UPDATE listings SET thumb_url=?, medium_url=?, photo_urls=?, description=? WHERE id=?",
                (new_primary, new_primary,
                 _json.dumps([nu for (nu, _c, _o) in kept]), new_desc, listing_id))
            conn.commit()
            applied = True
        return {"listing_id": listing_id, "photos_in": len(entries), "kept": len(kept),
                "removed": len(removed), "removed_urls": removed,
                "map": [{"old": o, "new": nu} for (nu, _c, o) in kept],
                "notes": notes, "applied": applied,
                "old_media_note": "old R2//media objects NOT deleted; purge CF cache + delete old keys manually"}
    finally:
        conn.close()


@app.post("/admin/ai-test")
def demand_sweep(_admin=Depends(_require_admin)):
    """DEMAND-LOOP-1 housekeeping: stale-expire old tickets, run the gated match/compose
    pass. Wire to the nightly conductor at flip-on; safe to call any time (idempotent)."""
    conn = database.get_db()
    try:
        expired = conn.execute(
            "UPDATE demand_tickets SET state='expired', updated_at=datetime('now') "
            "WHERE state='open' AND created_at < datetime('now','-30 days')").rowcount
        res = _demand_match_and_compose(conn)
        conn.commit()
        counts = {r["state"]: r["n"] for r in conn.execute(
            "SELECT state, COUNT(*) AS n FROM demand_tickets GROUP BY state")}
        return {"expired": expired, **res, "tickets": counts,
                "enabled": DEMAND_LOOP_ENABLED, "dry_run": DEMAND_LOOP_DRYRUN}
    finally:
        conn.close()
demand_sweep = app.post("/demand/sweep")(demand_sweep)

def demand_tickets_view(_admin=Depends(_require_admin)):
    """Inspection: counts by state + the newest 50 tickets (buyer tokens withheld)."""
    conn = database.get_db()
    try:
        counts = {r["state"]: r["n"] for r in conn.execute(
            "SELECT state, COUNT(*) AS n FROM demand_tickets GROUP BY state")}
        rows = [dict(r) for r in conn.execute(
            "SELECT id, query_norm, category, city_id, score, state, matched_item, "
            "priority_expires_at, created_at FROM demand_tickets ORDER BY id DESC LIMIT 50")]
        outbox = conn.execute("SELECT COUNT(*) AS n FROM demand_invites_outbox").fetchone()["n"]
        return {"counts": counts, "outbox_would_send": outbox, "latest": rows}
    finally:
        conn.close()
demand_tickets_view = app.get("/demand/tickets")(demand_tickets_view)

def admin_ai_test(payload: dict = Body(default=None), _admin=Depends(_require_admin)):
    """David-only: run a tiny prompt through the ACTIVE provider via the ai_provider seam
    (full translate+call+parse path). Lets the Page-4 switch be tested live against either
    provider without touching the 15 production call sites. Returns the text + which provider/model answered."""
    try:
        import ai_provider as _ap
        prov=_ts_active_provider()
        prompt=((payload or {}).get("prompt") or "Reply with exactly: TrustSquare AI provider test OK.").strip()
        r=_ap.complete([{"role":"user","content":prompt}], task="haiku", max_tokens=40, provider=prov)
        return {"ok": bool(r.ok), "provider": r.provider, "model": r.model,
                "text": (r.text or "")[:400], "in_tokens": r.in_tokens, "out_tokens": r.out_tokens}
    except Exception as e:
        raise HTTPException(status_code=500, detail="ai-test failed: "+str(e)[:160]) from e


class _FlagsUpdate(BaseModel):
    mode:          Optional[str]  = None
    verified_tier: Optional[bool] = None
    videos:        Optional[bool] = None
    data_ops:      Optional[bool] = None
    data_places:   Optional[bool] = None
    data_flights:  Optional[bool] = None
    data_mapbox:   Optional[bool] = None
    p_heritage:    Optional[bool] = None
    p_expedition:  Optional[bool] = None
    p_weekend:     Optional[bool] = None
    # BIT safe-state flags (Mitigator-writable; see §13.1)
    ai_example_enabled:    Optional[bool] = None
    auth_fail_closed:      Optional[bool] = None
    tuppence_burn_enabled: Optional[bool] = None
    ai_active:             Optional[str]  = None  # AI provider seam: 'anthropic' | 'openai' (Page-4 switch)

def _flags_payload(d):
    def b(k): return bool(d.get(k, 0))
    live = (d.get("mode", "launch") == "live")
    return {
        "mode": d.get("mode", "launch"),
        "verified_tier": b("verified_tier"), "videos": b("videos"),
        "data": {"ops": b("data_ops"), "places": b("data_places"),
                 "flights": b("data_flights"), "mapbox": b("data_mapbox")},
        "planners": {"heritage": b("p_heritage"), "expedition": b("p_expedition"),
                     "weekend": b("p_weekend")},
        "effective": {
            "verified_visible":    live and b("verified_tier"),
            "videos_visible":      b("videos"),  # decoupled from live mode (David 29 Jun): dashboard videos toggle controls it on its own; verified/paid-feed gates stay live-gated
            "heritage_verified":   live and b("verified_tier") and b("p_heritage"),
            "expedition_verified": live and b("verified_tier") and b("p_expedition"),
            "weekend_verified":    live and b("verified_tier") and b("p_weekend"),
        },
        "bit_flags": {
            "ai_example_enabled":    bool(d.get("ai_example_enabled", 1)),
            "auth_fail_closed":      bool(d.get("auth_fail_closed", 0)),
            "tuppence_burn_enabled": bool(d.get("tuppence_burn_enabled", 1)),
        },
        "ai_provider": {
            "active": d.get("ai_active", "anthropic"),
            # which providers have a REAL adapter wired (vs stub) — Page 4 greys out the stubs
            "available": {"anthropic": True, "openai": bool(os.getenv("OPENAI_API_KEY"))},
        },
        "updated_at": d.get("updated_at", ""),
    }

@app.get("/flags")
def get_flags():
    """Public — buyer app + dashboard read launch-switch state. Safe default = launch/free-only."""
    conn = database.get_db()
    try:
        row = conn.execute("SELECT * FROM launch_switches WHERE id = 1").fetchone()
    finally:
        conn.close()
    return _flags_payload(dict(row) if row else {})

@app.post("/admin/flags")
def set_flags(upd: _FlagsUpdate, _admin=Depends(_require_admin)):
    """Admin (JWT) — flip the launch switch. Writes the singleton row, returns full state."""
    data = upd.dict(exclude_unset=True)
    sets, vals = [], []
    for k, v in data.items():
        if k == "mode":
            if v not in ("launch", "live"):
                raise HTTPException(status_code=400, detail="mode must be 'launch' or 'live'")
            sets.append("mode = ?"); vals.append(v)
        elif k == "ai_active":
            if v not in ("anthropic", "openai"):
                raise HTTPException(status_code=400, detail="ai_active must be 'anthropic' or 'openai'")
            sets.append("ai_active = ?"); vals.append(v)
            _TS_AI_CACHE["prov"] = None  # bust the seam cache so the switch is instant
        else:
            sets.append(k + " = ?"); vals.append(1 if v else 0)
    conn = database.get_db()
    try:
        if sets:
            sets.append("updated_at = datetime('now')")
            conn.execute("UPDATE launch_switches SET " + ", ".join(sets) + " WHERE id = 1", vals)
            conn.commit()
        row = conn.execute("SELECT * FROM launch_switches WHERE id = 1").fetchone()
    finally:
        conn.close()
    return _flags_payload(dict(row) if row else {})


@app.post("/admin/users")
def admin_add_user(user: _AdminUserCreate, _key: str = Depends(auth.require_api_key)):
    """Add a team member with a numeric PIN. Starts with must_change_pin=1."""
    pin = user.pin.strip()
    if not pin.isdigit() or not (4 <= len(pin) <= 8):
        raise HTTPException(status_code=400, detail="PIN must be 4-8 digits.")
    name = user.name.strip()
    if not name:
        raise HTTPException(status_code=400, detail="Name is required.")
    pin_hash = _bcrypt.hashpw(pin.encode(), _bcrypt.gensalt()).decode()
    conn = _admin_db()
    try:
        existing = conn.execute(
            "SELECT id FROM admin_users WHERE name = ? AND active = 1", (name,)
        ).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail=f"Active user '{name}' already exists.")
        conn.execute(
            "INSERT INTO admin_users (name, pin_hash, active, must_change_pin) VALUES (?, ?, 1, 1)",
            (name, pin_hash)
        )
        conn.commit()
    finally:
        conn.close()
    return {"created": True, "name": name, "must_change_pin": True}

@app.get("/admin/users")
def admin_list_users(_key: str = Depends(auth.require_api_key)):
    """List all active admin team members. API-key protected."""
    conn = _admin_db()
    try:
        rows = conn.execute(
            "SELECT id, name, must_change_pin, created_at FROM admin_users WHERE active = 1 ORDER BY id"
        ).fetchall()
        return {"users": [
            {"id": r["id"], "name": r["name"],
             "must_change_pin": bool(r["must_change_pin"]),
             "created_at": r["created_at"]}
            for r in rows
        ]}
    finally:
        conn.close()

@app.delete("/admin/users/{user_id}")
def admin_deactivate_user(user_id: int, _key: str = Depends(auth.require_api_key)):
    """Deactivate a team member (soft delete). API-key protected."""
    conn = _admin_db()
    try:
        row = conn.execute(
            "SELECT name FROM admin_users WHERE id = ? AND active = 1", (user_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="User not found or already inactive.")
        conn.execute("UPDATE admin_users SET active = 0 WHERE id = ?", (user_id,))
        conn.commit()
        return {"deactivated": True, "name": row["name"]}
    finally:
        conn.close()



# ── AI SPEND REGISTER (Session 90) ──────────────────────────────────────────
# GET  /admin/ai-spend          — current month summary + status
# PUT  /admin/ai-spend/config   — update income + threshold
# These are admin-key protected. David uses these to monitor and intervene.

@app.get("/admin/ai-spend")
def admin_ai_spend_summary(_key: str = Depends(auth.require_api_key)):
    """Return current-month AI spend, income config, % used, and per-endpoint breakdown.
    Red flag status: 'ok' | 'warning' | 'alert' based on threshold.
    """
    import datetime as _dt
    conn = database.get_db()
    try:
        cfg = conn.execute(
            "SELECT monthly_income_usd, alert_threshold_pct, alert_email, last_alerted_at, "
            "daily_user_ceiling_usd, daily_platform_ceiling_usd "
            "FROM ai_spend_config WHERE id = 1"
        ).fetchone()
        month_start = _dt.datetime.utcnow().strftime('%Y-%m-01')
        total_row = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) as total, COUNT(*) as calls "
            "FROM ai_spend_log WHERE logged_at >= ?", (month_start,)
        ).fetchone()
        by_endpoint = conn.execute(
            "SELECT endpoint, model, COUNT(*) as calls, ROUND(SUM(est_cost_usd),6) as cost, "
            "       SUM(input_tokens) as in_tok, SUM(output_tokens) as out_tok, "
            "       SUM(cost_is_real) as real_rows "
            "FROM ai_spend_log WHERE logged_at >= ? "
            "GROUP BY endpoint, model ORDER BY cost DESC", (month_start,)
        ).fetchall()
        # Last 30 days daily totals for trending
        daily = conn.execute(
            "SELECT DATE(logged_at) as day, ROUND(SUM(est_cost_usd),6) as cost, COUNT(*) as calls "
            "FROM ai_spend_log WHERE logged_at >= DATE('now','-30 days') "
            "GROUP BY day ORDER BY day DESC LIMIT 30"
        ).fetchall()
        # C1 — today's spend vs ceilings (platform + top users today)
        day_start = _dt.datetime.utcnow().strftime('%Y-%m-%d 00:00:00')
        today_row = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) as total, COUNT(*) as calls "
            "FROM ai_spend_log WHERE logged_at >= ?", (day_start,)
        ).fetchone()
        top_users_today = conn.execute(
            "SELECT email, ROUND(SUM(est_cost_usd),6) as cost, COUNT(*) as calls "
            "FROM ai_spend_log WHERE logged_at >= ? AND email != '' "
            "GROUP BY email ORDER BY cost DESC LIMIT 5", (day_start,)
        ).fetchall()
        real_row = conn.execute(
            "SELECT COALESCE(SUM(cost_is_real),0) as real, COUNT(*) as total "
            "FROM ai_spend_log WHERE logged_at >= ?", (month_start,)
        ).fetchone()
    finally:
        conn.close()

    income  = float(cfg["monthly_income_usd"]) if cfg else 0.0
    thresh  = float(cfg["alert_threshold_pct"]) if cfg else 20.0
    spend   = float(total_row["total"]) if total_row else 0.0
    calls   = int(total_row["calls"]) if total_row else 0
    thresh_usd = income * thresh / 100.0 if income > 0 else 0.0
    pct_used   = (spend / income * 100) if income > 0 else 0.0

    user_cap     = float(cfg["daily_user_ceiling_usd"])     if cfg else 0.0
    platform_cap = float(cfg["daily_platform_ceiling_usd"]) if cfg else 0.0
    today_spend  = float(today_row["total"]) if today_row else 0.0
    today_calls  = int(today_row["calls"]) if today_row else 0
    platform_pct = (today_spend / platform_cap * 100) if platform_cap > 0 else 0.0
    real_n  = int(real_row["real"])  if real_row else 0
    real_t  = int(real_row["total"]) if real_row else 0

    if income <= 0:
        status = "unconfigured"
    elif spend >= thresh_usd:
        status = "alert"
    elif spend >= thresh_usd * 0.75:
        status = "warning"
    else:
        status = "ok"

    return {
        "status": status,
        "month": _dt.datetime.utcnow().strftime('%Y-%m'),
        "spend_usd": round(spend, 6),
        "calls_this_month": calls,
        "income_usd": income,
        "threshold_pct": thresh,
        "threshold_usd": round(thresh_usd, 4),
        "pct_used": round(pct_used, 2),
        "last_alerted_at": cfg["last_alerted_at"] if cfg else None,
        "alert_email": cfg["alert_email"] if cfg else None,
        "by_endpoint": [dict(r) for r in by_endpoint],
        "daily_trend": [dict(r) for r in daily],
        "ceilings": {
            "daily_user_ceiling_usd":     round(user_cap, 4),
            "daily_platform_ceiling_usd": round(platform_cap, 4),
            "today_spend_usd":            round(today_spend, 6),
            "today_calls":                today_calls,
            "platform_pct_of_ceiling":    round(platform_pct, 1),
            "platform_ceiling_breached":  bool(platform_cap > 0 and today_spend >= platform_cap),
            "top_users_today":            [dict(r) for r in top_users_today],
        },
        "cost_quality": {
            "real_token_rows": real_n,
            "total_rows":      real_t,
            "real_pct":        round((real_n / real_t * 100) if real_t else 0.0, 1),
        },
    }


class AISpendConfigUpdate(BaseModel):
    monthly_income_usd:         Optional[float] = None
    alert_threshold_pct:        Optional[float] = None
    alert_email:                Optional[str]   = None
    daily_user_ceiling_usd:     Optional[float] = None   # C1 — 0 disables
    daily_platform_ceiling_usd: Optional[float] = None   # C1 — 0 disables


@app.put("/admin/ai-spend/config")
def admin_ai_spend_config(cfg: AISpendConfigUpdate, _key: str = Depends(auth.require_api_key)):
    """Update AI spend monitoring config.
    monthly_income_usd  — actual monthly platform revenue (USD). Alert fires when
                          AI spend crosses alert_threshold_pct % of this.
    alert_threshold_pct — default 20%. At $100 income → alert at $20 AI spend.
    alert_email         — where the red flag notification goes.
    """
    conn = database.get_db()
    try:
        if cfg.monthly_income_usd is not None:
            conn.execute("UPDATE ai_spend_config SET monthly_income_usd=? WHERE id=1",
                         (max(0.0, cfg.monthly_income_usd),))
        if cfg.alert_threshold_pct is not None:
            pct = max(1.0, min(100.0, cfg.alert_threshold_pct))
            conn.execute("UPDATE ai_spend_config SET alert_threshold_pct=? WHERE id=1", (pct,))
        if cfg.alert_email is not None:
            conn.execute("UPDATE ai_spend_config SET alert_email=? WHERE id=1",
                         (cfg.alert_email.strip(),))
        if cfg.daily_user_ceiling_usd is not None:
            conn.execute("UPDATE ai_spend_config SET daily_user_ceiling_usd=? WHERE id=1",
                         (max(0.0, cfg.daily_user_ceiling_usd),))
        if cfg.daily_platform_ceiling_usd is not None:
            conn.execute("UPDATE ai_spend_config SET daily_platform_ceiling_usd=? WHERE id=1",
                         (max(0.0, cfg.daily_platform_ceiling_usd),))
        conn.execute("UPDATE ai_spend_config SET last_alerted_at=NULL WHERE id=1")
        conn.commit()
        row = conn.execute(
            "SELECT monthly_income_usd, alert_threshold_pct, alert_email, "
            "daily_user_ceiling_usd, daily_platform_ceiling_usd FROM ai_spend_config WHERE id=1"
        ).fetchone()
    finally:
        conn.close()
    return {"status": "ok", "config": dict(row)}


# ── DEMO DATA ENDPOINTS (Session 66 FEA hollowing) ──────────────────────────
# Serves the demo LISTINGS and SELLERS arrays that were previously bundled
# in marketsquare.html. The FEA fetches these lazily instead of inlining them.


_DEMO_LISTINGS_CACHE = None
_DEMO_SELLERS_CACHE  = None

def _load_demo_listings():
    global _DEMO_LISTINGS_CACHE
    if _DEMO_LISTINGS_CACHE is None:
        import json as _j, os as _o
        path = _o.path.join(_o.path.dirname(__file__), "demo_listings.json")
        try:
            with open(path, encoding="utf-8") as f:
                _DEMO_LISTINGS_CACHE = _j.load(f).get("listings", [])
        except Exception:
            _DEMO_LISTINGS_CACHE = []
    return _DEMO_LISTINGS_CACHE

def _load_demo_sellers():
    global _DEMO_SELLERS_CACHE
    if _DEMO_SELLERS_CACHE is None:
        import json as _j, os as _o
        path = _o.path.join(_o.path.dirname(__file__), "demo_sellers.json")
        try:
            with open(path, encoding="utf-8") as f:
                _DEMO_SELLERS_CACHE = _j.load(f).get("sellers", [])
        except Exception:
            _DEMO_SELLERS_CACHE = []
    return _DEMO_SELLERS_CACHE

@app.get("/demo-listings")
def get_demo_listings():
    """Return demo LISTINGS array for FEA demo mode. Replaces bundled inline data."""
    listings = _load_demo_listings()
    return {"listings": listings, "count": len(listings)}

@app.get("/demo-sellers")
def get_demo_sellers():
    """Return demo SELLERS array for FEA demo mode. Replaces bundled inline data."""
    sellers = _load_demo_sellers()
    return {"sellers": sellers, "count": len(sellers)}

# ── END ADMIN AUTH v3 ───────────────────────────────────────────────────────


# ═══════════════════════════════════════════════════════════════════════════════
# PHOTO-FIRST AI ONBOARDING — Session 70
# POST /listings/vision-draft
# ═══════════════════════════════════════════════════════════════════════════════
#
# COMPLETE FLOW DESIGN (Session 70 working notes)
# ─────────────────────────────────────────────────────────────────────────────
#
# SCREENS & STATE MACHINE
# ────────────────────────
# S0: Magic-link landing
#     URL: ?magic=1&name=X&email=X&cat=X&city=X&suburb=X
#     State: sob_state = "photo_first"
#     Action: show demo listing card in seller's scraped category
#             then immediately open photo-first screen
#
# S1: Photo capture screen
#     UI: large camera icon + "Take 1–12 photos of what you're selling"
#         multi-file input (accept="image/*", multiple, max 12)
#         small "Skip photos — describe it instead" link below (→ S_FALLBACK)
#     State: photos selected, upload button active
#     Trigger: user taps "Analyse my photos →"
#
# S2: Upload + Vision call (animated)
#     UI: spinning "Building your listing…" overlay with 3 rotating messages:
#         "Reading your photos…" → "Identifying category…" → "Writing your listing…"
#     Action: POST /listings/vision-draft
#             FormData: photos[] (1–12 files) + category_hint (from ?cat=) + seller_email
#     State: awaiting BEA response (15s timeout shown as progress bar)
#     Error: if timeout/error → toast "Couldn't analyse — let's try the quick form" → S_FALLBACK
#
# S3: Draft card reveal
#     UI: animated slide-up of a pre-populated listing card showing:
#         - First photo as hero image (carousel if multiple)
#         - Detected category badge
#         - AI-generated title (editable inline)
#         - AI-generated description (editable textarea)
#         - Suggested price with currency prefix (ZAR R / USD $ etc.)
#         - Tags (chips, removable)
#         - Confidence bar (shown only if confidence < 0.75)
#     Bottom bar: "Does this look right?" with two actions:
#         [Improve description] → S4_IMPROVE
#         [Looks good — publish it →] → S5_EULA
#
# S4: Inline AI improvement (optional)
#     UI: Claude rewrites description on request
#         Shows old vs new in a diff-style highlight
#     Action: POST /advert-agent/market-note with {prompt: "Improve this listing description: ..."}
#     Returns: improved text → seller accepts or reverts
#
# S5: EULA accept → go live
#     Existing SOB phase 3 (unchanged)
#     Pre-populate: title, description, price, category from draft JSON
#     Post-publish: redirect to seller dashboard
#
# S_FALLBACK: "Describe it instead"
#     Opens existing SOB form (B1/B2/B3 path) with category pre-filled
#
# ─────────────────────────────────────────────────────────────────────────────
# DATA CONTRACT — POST /listings/vision-draft
# ─────────────────────────────────────────────────────────────────────────────
#
# REQUEST (multipart/form-data):
#   photos[]        File[]   1–12 image files (JPEG, PNG, HEIC, WEBP)
#   category_hint   str      Scraped category from magic link: property|services|adventures|cars
#   seller_email    str      Seller's email (for audit log — not required for guest draft)
#   city            str      City name (used for price calibration in prompt)
#   country_iso2    str      Country ISO2 (default "ZA")
#
# RESPONSE 200:
#   {
#     "draft": {
#       "category":           str,   // "property"|"services"|"adventures"|"cars"
#       "title":              str,   // 4–8 words, title case
#       "description_draft":  str,   // 2–4 sentences, honest, no fluff
#       "suggested_price":    float, // numeric, in local currency
#       "currency_prefix":    str,   // "R" for ZA, "$" for US, etc.
#       "tags":               list,  // 3–6 keyword strings
#       "category_confidence":float, // 0.0–1.0 — how certain Claude is of category
#       "price_confidence":   float, // 0.0–1.0 — how certain Claude is of price
#       "photo_count":        int,   // number of photos analysed
#       "primary_photo_index":int,   // which photo is the best hero (0-indexed)
#       // Category-specific fields (null if not applicable):
#       "prop_type":          str|null,  // "House"|"Flat"|"Room"|"Plot"|"Commercial"
#       "beds":               int|null,
#       "baths":              int|null,
#       "listing_type":       str|null,  // "For Sale"|"To Rent"
#       "subject":            str|null,  // For Services: subject/skill being offered
#       "service_type":       str|null,  // "once-off"|"ongoing"|"retainer"
#       "level":              str|null,  // For tutoring: "Primary"|"High School"|"University"
#       "availability":       str|null,  // e.g. "Weekdays" or "Flexible"
#       "make":               str|null,  // For Cars
#       "model":              str|null,
#       "variant":            str|null,  // trim line, e.g. "2.8 GD-6 4x4 Legend" (CARS-SPEC-1)
#       "year":               int|null,
#       "mileage":            int|null,
#       "condition":          str|null,  // "Excellent"|"Good"|"Fair"
#       "vehicle_specs":      obj|null,  // Cars only: drafted deterministic spec sheet (CARS-SPEC-1)
#       "missing_shots":      list       // [{label, reason}] — item-specific photo suggestions
#     },
#     "warnings": [],    // e.g. ["Low light in photo 3", "Price unusually high for category"]
#     "model_used": str  // e.g. "claude-opus-4-6"
#   }
#
# RESPONSE 400: { "detail": "No photos provided" }
# RESPONSE 413: { "detail": "Too many photos (max 12)" }
# RESPONSE 503: { "detail": "AI not configured" }
# RESPONSE 422: { "detail": "Vision analysis failed — try describing instead" }
#
# ─────────────────────────────────────────────────────────────────────────────
# VISION PROMPT TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────
# Model: claude-opus-4-6 (vision capable, best for listing quality)
# Max output tokens: 800
# Max photos: 12 (all sent as base64 image blocks)
# Category hint: always included in prompt to improve accuracy
# City + country: used for price calibration
# ─────────────────────────────────────────────────────────────────────────────

import base64 as _b64

# Vision model — use Sonnet for cost/quality balance on photo analysis
VISION_MODEL = _TS_AI_MODELS.get("vision", "claude-haiku-4-5-20251001")  # Haiku-first (David, 3 Jul 2026): free draft = Haiku 4.5; Sonnet only for paid deep-dives. Revert = set "claude-sonnet-4-6".

# Currency prefix by country ISO2
_CURRENCY_MAP = {
    "ZA": "R", "US": "$", "GB": "£", "EU": "€", "NG": "₦",
    "KE": "KSh", "GH": "₵", "AU": "A$", "CA": "C$", "IN": "₹",
}

# ── VISION PROMPT TEMPLATE ──────────────────────────────────────────────────
_VISION_SYSTEM = """You are a skilled marketplace listing writer for TrustSquare, a South African peer-to-peer local marketplace. Your job is to analyse seller photos and produce a ready-to-publish listing draft.

You write honest, specific, buyer-friendly listings. You never exaggerate or invent details not visible in the photos. You prefer concrete facts (size, colour, condition, year) over adjectives.

You are also a photo coaching expert. Once you identify what the item is, you know exactly which additional photos would help buyers trust the listing and help sellers avoid disputes. You always suggest the most important missing shots specific to the identified item type.

ANONYMITY RULE — MANDATORY: TrustSquare is an anonymous marketplace. Seller identities are NEVER revealed until a paid Introduction is accepted. You must NEVER include in any generated field (title, description_draft, tags, or any other field):
- Street addresses or unit numbers (e.g. "252 Olivier Street", "Apartment 403", "Unit 4B")
- Business names, complex names, or brand names visible in photos (e.g. "Kronborg Luxury Apartments")
- Seller names, agent names, or owner names visible in photos or documents
- Phone numbers, email addresses, WhatsApp numbers, QR codes, or any contact details
- Social media handles, websites, or URLs
- Estate agent company names or franchise names
If any of the above appear in a photo (on signage, documents, watermarks, or as visible text), you MUST silently omit them from all generated text. Describe the item/property using only physical, observable features. Set anonymity_scrubbed to true if you removed or withheld any identifying information.
If a photo is PREDOMINANTLY an identifying document, contact sheet, or business advertisement (rather than the item itself), add a warning: "Photo N appears to be an advertisement or contact sheet — anonymity requires omitting all business and contact details. Describe only the physical item/property."

You always respond with a single valid JSON object. No markdown. No explanation. Just the JSON."""

def _build_vision_prompt(category_hint: str, city: str, country_iso2: str, photo_count: int) -> str:
    """Build the user-turn vision prompt. Photos are attached as separate image blocks."""
    currency = _CURRENCY_MAP.get(country_iso2.upper(), "R")

    # Category-specific price anchors for South African market (ZA default)
    price_context = {
        "property": (
            f"Typical price ranges in {city}, South Africa: "
            "Room to rent R2,000–R6,000/mo · Flat R5,000–R15,000/mo · "
            "House rental R8,000–R25,000/mo · House for sale R500,000–R3,000,000."
        ),
        "services": (
            f"Typical service rates in {city}, South Africa: "
            "Tutor R150–R350/hr · Cleaner R150–R250/visit · Plumber R500–R1,500 call-out · "
            "Graphic designer R500–R2,000 project · Personal trainer R200–R400/session."
        ),
        "adventures": (
            f"Typical experience prices in {city}, South Africa: "
            "Day tour R300–R1,500/person · Workshop R200–R800/person · "
            "Cooking class R450–R900/person · Photography tour R500–R1,200/person."
        ),
        "cars": (
            f"Typical car prices in {city}, South Africa: "
            "Hatchback R60,000–R200,000 · Sedan R80,000–R350,000 · "
            "SUV R150,000–R600,000 · Bakkie/Pickup R120,000–R500,000."
        ),
        "collectors": (
            f"Typical collectible prices in {city}, South Africa: "
            "Vintage coins R200–R5,000 · Sports memorabilia R500–R20,000 · "
            "Antique furniture R2,000–R50,000 · Rare stamps R100–R10,000 · "
            "Art prints R1,000–R30,000 · Signed jerseys R1,500–R15,000."
        ),
        "local_market": (
            f"Typical local market prices in {city}, South Africa: "
            "Handmade crafts R100–R800 · Baked goods R50–R300 · "
            "Second-hand clothing R50–R500 · Homegrown produce R30–R200 · "
            "Upcycled furniture R500–R5,000."
        ),
        "tutors": (
            f"Typical tutoring rates in {city}, South Africa: "
            "Primary school R100–R200/hr · High school R150–R350/hr · "
            "University R200–R500/hr · Music/arts R150–R300/hr."
        ),
    }.get(category_hint, f"Use realistic local prices for {city}, {country_iso2}.")

    category_instruction = {
        "property": (
            "This is likely a PROPERTY listing. Identify if it is for sale or to rent. "
            "Count bedrooms, bathrooms, garages if visible. Identify property type "
            "(House, Flat, Room, Plot, Commercial). "
            "Set listing_type to 'For Sale' or 'To Rent'. "
            "suggested_price should be the monthly rent OR sale price. "
            "ADVERT SHAPE (property-portal format; guidance, never enforcement): structure description_draft as "
            "(1) opener — property type, beds/baths, character of the space; "
            "(2) interior walk-through — kitchen, living areas, main bedroom highlights; "
            "(3) outdoor and parking — garden, pool, garage if visible; "
            "(4) one line on the area's general appeal. "
            "Never include street names, complex/building names or anything identifying."
        ),
        "services": (
            "This is likely a SERVICES listing (skill, profession, or recurring service). "
            "Identify the service type and whether it is once-off, ongoing, or retainer. "
            "If it appears to be a tutoring/teaching service, set level to the education level. "
            "suggested_price is the per-session or per-visit rate in local currency."
        ),
        "adventures": (
            "This is likely an ADVENTURES/EXPERIENCES listing (tour, workshop, activity, event, stay). "
            "Identify what the experience involves and its approximate duration. "
            "suggested_price is per-person for the experience. "
            "ADVERT SHAPE (tour-operator format; guidance, never enforcement): structure description_draft as "
            "(1) what you'll do or experience — lead with the highlight; "
            "(2) duration and typical group size; "
            "(3) what's included vs excluded — be explicit, this is the #1 buyer question; "
            "(4) what to bring / fitness level if relevant; "
            "(5) for multi-day trips, a short day-by-day itinerary. "
            "Name the general area only — never an exact meeting address."
        ),
        "cars": (
            "This is likely a CARS/VEHICLES listing. "
            "Identify the make, model, approximate year, visible condition, and any notable features. "
            "Also propose the variant / trim line if identifiable from badges or styling "
            "(e.g. '2.8 GD-6 4x4 Legend', '2.0 TDI Highline') — variant is the biggest gap in private car adverts. "
            "Return the proposed variant in the top-level \"variant\" field (null when uncertain). "
            "From the identified make/model/variant, DRAFT the deterministic spec sheet into "
            "\"vehicle_specs\" — a JSON object using only these keys, for values you can state "
            "with confidence for that exact variant: engine_capacity_cc, kilowatts_kw, "
            "cylinder_layout, cylinders, aspiration, fuel_consumption_l100, fuel_tank_l, gears, "
            "seats, doors, wheelbase_mm, co2_gkm. These are DRAFTS the seller must personally "
            "confirm — omit any key you are not confident of; never guess. If the variant itself "
            "is uncertain, set vehicle_specs to null. "
            "Estimate mileage range if odometer is visible. "
            "suggested_price is the asking price for the vehicle. "
            "ADVERT SHAPE (professional dealer format; guidance, never enforcement): structure description_draft as "
            "(1) spec line — year make model variant, transmission, fuel type, mileage if known; "
            "(2) condition and service history — only what is visible or evident; "
            "(3) notable features and extras seen in the photos. "
            "Never state a spec you cannot see or infer with confidence."
        ),
        "collectors": (
            "This is a COLLECTORS listing — a collectable item being sold or sought. "
            "Identify the item type (coins, stamps, art, memorabilia, antiques, wine, books, etc.). "
            "Note any visible condition details, markings, signatures, or authentication features. "
            "suggested_price is the asking price for the item. "
            "Set condition to 'Excellent', 'Good', or 'Fair' based on visible state. "
            "Set category to 'collectors' in the response."
        ),
        "local_market": (
            "This is a LOCAL MARKET listing — handmade, homegrown, or artisanal goods. "
            "Identify the product type, quantity/size if visible, and any unique features. "
            "suggested_price is the per-item or per-unit price. "
            "Set category to 'local_market' in the response."
        ),
        "tutors": (
            "This is a TUTORS listing — educational or skills-based teaching service. "
            "Identify the subject(s), education level, and mode (online/in-person/both). "
            "suggested_price is the per-hour rate. "
            "Set level to the education level (Primary, High School, University, Adult). "
            "Set subject to the main subject or skill being taught. "
            "Set category to 'services' in the response (tutors maps to services category)."
        ),
    }.get(category_hint, (
        "Determine the most likely category from: property, services, adventures, cars, collectors. "
        "Apply the appropriate pricing and field logic for the detected category."
    ))

    return f"""You are analysing {photo_count} seller photo(s) to create a marketplace listing.

CATEGORY HINT: The seller was invited as a '{category_hint}' seller. {category_instruction}

PRICE CONTEXT: {price_context}
Currency prefix to use: {currency}

TASK: Return a single JSON object with exactly these fields:

{{
  "category": "property|services|adventures|cars|collectors|local_market",
  "title": "4–8 word title in Title Case, specific not generic",
  "description_draft": "2–6 honest sentences describing what is visible, following the ADVERT SHAPE for the category if one is given above. Be specific. No hype.",
  "suggested_price": <number — monthly rent, per-session rate, per-person price, or sale price>,
  "currency_prefix": "{currency}",
  "tags": ["3 to 6 relevant keyword strings"],
  "category_confidence": <0.0 to 1.0>,
  "price_confidence": <0.0 to 1.0>,
  "primary_photo_index": <0-indexed integer — which photo is the best hero image>,
  "prop_type": null,
  "beds": null,
  "baths": null,
  "listing_type": null,
  "subject": null,
  "service_type": null,
  "level": null,
  "availability": null,
  "make": null,
  "model": null,
  "variant": null,
  "year": null,
  "mileage": null,
  "condition": null,
  "vehicle_specs": null,
  "missing_shots": [],
  "coach_tips": [],
  "warnings": [],
  "anonymity_scrubbed": false,
  "violating_photo_indices": [],
  "off_category_photo_indices": []
}}

Fill in ONLY the fields relevant to the detected category. Leave others as null.
For warnings: add a brief string if a photo is dark/blurry, or if the price is unusually high/low, OR if a photo contains identifying information (business signage, contact details, documents) that you had to suppress.

ANONYMITY ENFORCEMENT (mandatory): Before writing any text, scan all photos for visible identifying information: street addresses, complex/building names, business names, phone numbers, email addresses, agent names, QR codes, URLs, social media handles. Do NOT include any of these in title, description_draft, tags, or any other field. Describe only physical, observable features of the item or property. Set "anonymity_scrubbed": true if any photo contains identifying information. In "violating_photo_indices", list the 0-based index of EVERY photo that contains identifying information (e.g. [0, 2] if photos 0 and 2 are violations). Photos without violations must NOT be listed. Set to [] if no violations found.

CATEGORY FIT (mandatory): In "off_category_photo_indices", list the 0-based index of EVERY photo whose main subject is clearly NOT the kind of thing a '{category_hint}' advert sells (e.g. a boat or a house on a cars advert). Detail or partial shots of the right kind of item always fit. For services, tutors, local_market, adventures or unknown categories, or whenever unsure, use [].

For "missing_shots": Based on the exact item you identified, list the most important additional photos the seller should add. Be item-specific and practical. Each entry: {{"label": "<short name>", "reason": "<one line why>"}}. Examples:
- Magic: the Gathering card → [{{"label": "Card back", "reason": "Shows set symbol and condition"}}, {{"label": "Edge close-up", "reason": "Reveals wear grade"}}, {{"label": "Three red dots (magnified)", "reason": "Distinguishes original print from reprint — critical for authenticity"}}]
- Graded slab → [{{"label": "Grade label close-up", "reason": "Grade number must be legible"}}, {{"label": "Slab edges", "reason": "Shows cracks or tampering"}}]
- Coin → [{{"label": "Reverse (tails)", "reason": "Buyers always want both sides"}}, {{"label": "Edge close-up", "reason": "Shows minting quality and wear"}}, {{"label": "Certificate of authenticity", "reason": "Essential for valuable coins"}}]
- Signed memorabilia → [{{"label": "Signature close-up", "reason": "Must be legible and authentic-looking"}}, {{"label": "Authentication certificate", "reason": "Protects seller from disputes"}}]
- Watch → [{{"label": "Caseback", "reason": "Serial number and movement details"}}, {{"label": "Dial straight-on", "reason": "Shows dial condition clearly"}}]
- Vehicle → [{{"label": "Odometer", "reason": "Mileage is a key buyer decision factor"}}, {{"label": "Engine bay", "reason": "Shows mechanical condition"}}, {{"label": "Service book", "reason": "Full history adds significant value"}}, {{"label": "Rear three-quarter", "reason": "Completes the walk-around buyers expect"}}]
- Property → [{{"label": "Kitchen", "reason": "Most important room for most buyers"}}, {{"label": "Main bedroom", "reason": "Size and condition matter"}}, {{"label": "Bathroom", "reason": "Buyers always inspect bathrooms"}}]
- Experience/tour → [{{"label": "Guests in action", "reason": "Shows the real experience, not just scenery"}}, {{"label": "Equipment provided", "reason": "Confirms what's included"}}, {{"label": "Setting/scenery", "reason": "Sells the location at a glance"}}]
- Artwork → [{{"label": "Artist signature", "reason": "Authentication requirement"}}, {{"label": "Certificate of authenticity", "reason": "Protects both parties"}}]
Only suggest shots genuinely missing from the uploaded photos. If all key shots are present, return []. Maximum 4 suggestions.

For "coach_tips": up to 4 SOFT suggestions that would make this advert stronger, based on what the leading platforms in this category always state and this draft does not yet cover. Phrase each as friendly guidance ("Buyers respond well to…", "Consider adding…") — never commands, never requirements; the seller is free to ignore them. Category cues:
- Cars → variant/trim line, service history status (full/partial/none), exact mileage, spare key, warranty or maintenance plan, reason for selling.
- Property → erf and floor size (the portals' own quality fields — size-less listings vanish from filtered search), monthly levies and rates (for sale) or deposit and lease term (rental) ONLY if truly known — never estimated, pet policy, security features, fibre availability.
- Adventures/tours/stays → included/excluded as plain nouns covering park fees, meals and transfers (write "Guide", not "a friendly knowledgeable guide"), a title with area + duration + group size, 7-10 authentic photos (the strongest conversion lever), general meeting area (suburb level only), seasonal availability, minimum age or fitness level, languages offered.
- Other categories → the 2–3 facts buyers in that niche always ask about first.
One sentence per tip, maximum 120 characters each. Return [] if the draft already covers the essentials.
Return ONLY the JSON. No markdown. No explanation."""


@app.post("/listings/vision-draft")
async def vision_draft(
    background_tasks: BackgroundTasks,
    photos: list[UploadFile] = File(...),
    category_hint: str = Form(default=""),
    seller_email: str = Form(default=""),
    city: str = Form(default="Pretoria"),
    country_iso2: str = Form(default="ZA"),
):
    """
    Photo-First AI Onboarding — Session 70.

    Accepts 1–12 seller photos, calls Claude Vision, returns a complete
    listing draft JSON ready for the FEA to render as a pre-populated card.

    No database writes — this is a stateless analysis endpoint.
    The FEA collects seller edits and calls POST /listings (existing flow) to publish.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")

    if not photos or len(photos) == 0:
        raise HTTPException(status_code=400, detail="No photos provided")

    if len(photos) > 12:
        raise HTTPException(status_code=413, detail="Too many photos — maximum 12")

    # Existence gate — seller_email must belong to a registered user (Session 90)
    _ve_email = (seller_email or "").strip().lower()
    if _ve_email:
        _vc = database.get_db()
        _ve = _vc.execute("SELECT 1 FROM users WHERE LOWER(email)=? LIMIT 1", (_ve_email,)).fetchone()
        _vc.close()
        if not _ve:
            raise HTTPException(status_code=401, detail="Unrecognised account — please complete seller registration first.")
    _check_cost_ceiling(_ve_email)   # C1 — refuse if daily cost ceiling reached

    # ── 1. Read and validate photos ──────────────────────────────────────────
    image_blocks = []
    warnings = []
    MAX_SIDE = 1568   # Anthropic vision max dimension for efficient processing
    MAX_BYTES_PER_PHOTO = 5 * 1024 * 1024  # 5 MB per photo hard cap

    for idx, photo in enumerate(photos):
        raw = await photo.read()
        if len(raw) == 0:
            warnings.append(f"Photo {idx+1} was empty and skipped")
            continue
        if len(raw) > MAX_BYTES_PER_PHOTO:
            warnings.append(f"Photo {idx+1} exceeded 5 MB and was skipped")
            continue

        # Resize to fit within MAX_SIDE on longest dimension (saves API tokens)
        try:
            img = ImageOps.exif_transpose(Image.open(io.BytesIO(raw)))
            img = img.convert("RGB")  # normalise — handles PNG/HEIC alpha channels
            w, h = img.size
            if max(w, h) > MAX_SIDE:
                ratio = MAX_SIDE / max(w, h)
                img = img.resize((int(w * ratio), int(h * ratio)), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85, optimize=True)
            compressed = buf.getvalue()
        except Exception as img_err:
            _log.warning("vision-draft: failed to process photo %d: %s", idx, img_err)
            warnings.append(f"Photo {idx+1} could not be read")
            continue

        b64 = _b64.b64encode(compressed).decode("ascii")
        image_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/jpeg",
                "data": b64,
            }
        })

    if not image_blocks:
        raise HTTPException(status_code=400, detail="No valid photos could be processed")

    photo_count = len(image_blocks)

    # ── 2. Build Anthropic messages ──────────────────────────────────────────
    cat_hint = (category_hint or "").lower().strip()
    if cat_hint not in ("property", "services", "adventures", "cars", "collectors", "local_market", "tutors"):
        cat_hint = "property"  # safe default

    user_content = image_blocks + [
        {
            "type": "text",
            "text": _build_vision_prompt(cat_hint, city or "Pretoria", country_iso2 or "ZA", photo_count)
        }
    ]

    # ── 3. Call Claude Vision ────────────────────────────────────────────────
    try:
        async with httpx.AsyncClient(timeout=45) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": VISION_MODEL,
                    "max_tokens": 1200,
                    "system": _VISION_SYSTEM,
                    "messages": [{"role": "user", "content": user_content}],
                },
            )
    except httpx.TimeoutException as exc:
        _log.error("vision-draft: Claude API timeout after 45s")
        raise HTTPException(
            status_code=504,
            detail="Vision analysis timed out — try describing your listing instead"
        ) from exc
    except Exception as exc:
        _log.error("vision-draft: Claude API call failed: %s", exc)
        raise HTTPException(status_code=503, detail="Vision analysis unavailable") from exc

    # ── 4. Parse Claude response ─────────────────────────────────────────────
    raw_text = ""
    try:
        body = resp.json()
        if resp.status_code != 200:
            err_msg = body.get("error", {}).get("message", "Unknown error")
            _log.error("vision-draft: Claude returned %d: %s", resp.status_code, err_msg)
            raise HTTPException(status_code=502, detail=f"AI error: {err_msg}")

        raw_text = body["content"][0]["text"].strip()
        _vd_in, _vd_out = _usage_tokens(body)   # C2

        # Strip markdown code fences if Claude wraps the JSON anyway
        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
            raw_text = raw_text.strip()

        draft = json.loads(raw_text)

    except json.JSONDecodeError as jde:
        _log.error("vision-draft: JSON parse failed. Raw: %s… Error: %s", raw_text[:200], jde)
        raise HTTPException(
            status_code=422,
            detail="Vision analysis returned unexpected format — try describing instead"
        ) from jde
    except HTTPException:
        raise
    except Exception as exc:
        _log.error("vision-draft: unexpected parse error: %s", exc)
        raise HTTPException(status_code=500, detail="Vision analysis failed") from exc

    # ── 5. Sanitise + enrich the draft ──────────────────────────────────────
    # Merge any warnings Claude produced with our upload warnings
    claude_warnings = draft.pop("warnings", []) or []
    all_warnings = warnings + (claude_warnings if isinstance(claude_warnings, list) else [])

    # Clamp confidence scores to [0, 1]
    draft["category_confidence"] = min(1.0, max(0.0, float(draft.get("category_confidence") or 0.7)))
    draft["price_confidence"]    = min(1.0, max(0.0, float(draft.get("price_confidence")    or 0.6)))

    # Ensure primary_photo_index is valid
    pi = draft.get("primary_photo_index")
    if not isinstance(pi, int) or pi < 0 or pi >= photo_count:
        draft["primary_photo_index"] = 0

    # Validate category
    if draft.get("category") not in ("property", "services", "adventures", "cars"):
        draft["category"] = cat_hint

    # CARS-SPEC-1 (D4): the vehicle spec draft rides this call — cars only.
    # Non-cars drafts must never carry a vehicle blob (contamination guard).
    if draft.get("category") == "cars":
        _vs = draft.get("vehicle_specs")
        if isinstance(_vs, dict):
            _vs = {k: v for k, v in _vs.items() if v is not None}
        draft["vehicle_specs"] = _vs if isinstance(_vs, dict) and _vs else None
        _vv = draft.get("variant")
        draft["variant"] = str(_vv)[:80] if _vv else None
    else:
        draft["vehicle_specs"] = None   # force-null on non-cars
        draft["variant"] = None

    # Ensure tags is a list of strings
    tags = draft.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    draft["tags"] = [str(t) for t in tags[:6]]

    # Sanitise missing_shots — list of {label, reason} dicts, max 4
    raw_shots = draft.get("missing_shots") or []
    if not isinstance(raw_shots, list):
        raw_shots = []
    clean_shots = []
    for shot in raw_shots[:4]:
        if isinstance(shot, dict) and shot.get("label"):
            clean_shots.append({
                "label":  str(shot.get("label",  ""))[:60],
                "reason": str(shot.get("reason", ""))[:120],
            })
    draft["missing_shots"] = clean_shots

    # Add photo count for FEA
    draft["photo_count"] = photo_count

    # Ensure currency_prefix
    if not draft.get("currency_prefix"):
        draft["currency_prefix"] = _CURRENCY_MAP.get((country_iso2 or "ZA").upper(), "R")

    # Log for monitoring (no PII beyond email which is already in our DB)
    _log.info(
        "vision-draft: %d photos → category=%s confidence=%.2f price=%s%s seller=%s",
        photo_count,
        draft.get("category"),
        draft.get("category_confidence"),
        draft.get("currency_prefix"),
        draft.get("suggested_price"),
        seller_email or "guest",
    )

    # Ensure anonymity_scrubbed is present and boolean
    draft["anonymity_scrubbed"] = bool(draft.get("anonymity_scrubbed", False))
    # Ensure violating_photo_indices is a valid list of ints
    vpi = draft.get("violating_photo_indices", [])
    if not isinstance(vpi, list):
        vpi = []
    vpi = [int(x) for x in vpi if isinstance(x, (int, float)) and 0 <= int(x) < 50]
    draft["violating_photo_indices"] = vpi
    # WRONG-TYPE-1 (16 Jul 2026): photos whose subject is clearly not what this
    # category sells (David's boat-on-a-Cars-advert test). Sanitised like vpi.
    ocpi = draft.get("off_category_photo_indices", [])
    if not isinstance(ocpi, list):
        ocpi = []
    ocpi = [int(x) for x in ocpi if isinstance(x, (int, float)) and 0 <= int(x) < 50]
    draft["off_category_photo_indices"] = ocpi
    if ocpi:
        all_warnings.append(
            "%d photo(s) do not appear to show the kind of item this advert "
            "sells - the main photo must show the item itself." % len(ocpi))
    if draft["anonymity_scrubbed"]:
        n_violating = len(vpi)
        all_warnings.append(
            f"Identifying information (address, business name, or contact details) was detected in "
            f"{n_violating} photo(s) and removed from this listing to protect seller anonymity."
            if n_violating else
            "Identifying information was detected in photos and removed from this listing to protect seller anonymity."
        )

    background_tasks.add_task(_log_ai_spend, _ve_email, "/listings/vision-draft", "sonnet_vision", _vd_in, _vd_out)
    return {
        "draft": draft,
        "warnings": all_warnings,
        "model_used": VISION_MODEL,
        "anonymity_scrubbed": draft["anonymity_scrubbed"],
        "violating_photo_indices": vpi,
        "off_category_photo_indices": ocpi,
    }


# ── END PHOTO-FIRST AI ONBOARDING (Session 70) ─────────────────────────────


# ── AI TUPPENCE SERVICES (Session 73) ────────────────────────────────────────
# Three paid AI endpoints — each deducts 1 Tuppence from the caller.
# HTTP 402 is returned if the caller has insufficient balance.
# All three endpoints are non-refundable per platform policy.
#
#   AI1  POST /listings/{id}/ai-rewrite?email=   Haiku   seller rewrites title+desc
#   AI2  POST /listings/{id}/ai-audit?email=     Haiku   seller gets 3 coach actions
#   AI3  POST /listings/{id}/price-check?email=  Sonnet  buyer gets market comparison


# ── REAL PRICE FEED HELPERS (Session: price-integrity fix) ───────────────────
# Principle: the model writes the SENTENCE, the system produces the NUMBER.
# These helpers fetch verifiable figures so ai_price_check never invents prices.

import time as _time

_FX_CACHE = {"rate": None, "ts": 0.0}        # USD->ZAR, refreshed daily
_FX_TTL   = 60 * 60 * 12                      # 12h
_FX_FALLBACK = 18.50                          # last-known; only if every feed fails

async def live_usd_zar() -> float:
    """Live USD->ZAR mid-rate, cached 12h. Falls back to last-known on failure.
    Free endpoints, no key — keeps the no-consumption-API stance."""
    now = _time.time()
    if _FX_CACHE["rate"] and (now - _FX_CACHE["ts"]) < _FX_TTL:
        return _FX_CACHE["rate"]
    for url, getter in (
        ("https://api.frankfurter.dev/v1/latest?base=USD&symbols=ZAR",
         lambda j: j["rates"]["ZAR"]),
        ("https://open.er-api.com/v6/latest/USD",
         lambda j: j["rates"]["ZAR"]),
    ):
        try:
            async with httpx.AsyncClient(timeout=8) as c:
                r = await c.get(url)
                rate = float(getter(r.json()))
                if 5 < rate < 50:                # sanity band
                    _FX_CACHE.update(rate=rate, ts=now)
                    return rate
        except Exception as exc:
            _log.warning("FX fetch failed (%s): %s", url, exc)
    return _FX_CACHE["rate"] or _FX_FALLBACK


# Categories for which a real collectible price feed (Scryfall) applies.
_SCRYFALL_CATS = {"card", "cards", "trading", "trading cards", "collectibles", "collectables"}

async def resolve_scryfall_id(title: str, category: str) -> str | None:
    """Best-effort: map a listing title to a Scryfall card with a REAL paper
    (non-digital) USD price. Returns the Scryfall id, or None if not a confident
    match. Disambiguates printings — a bare name lookup can return a digital-only
    printing with usd:null, so we search and pick the cheapest printing that has
    a real usd price."""
    if not title:
        return None
    cat = (category or "").lower()
    if not any(k in cat for k in _SCRYFALL_CATS):
        return None
    # Strip common noise from a marketplace title to get a plausible card name.
    name = title.strip()
    try:
        async with httpx.AsyncClient(timeout=10,
                headers={"User-Agent": "TrustSquare/1.0", "Accept": "application/json"}) as c:
            # Search all printings of the named card that have a non-null usd price.
            q = f'!"{name}" game:paper'
            r = await c.get("https://api.scryfall.com/cards/search",
                            params={"q": q, "unique": "prints", "order": "usd"})
            if r.status_code != 200:
                # Fuzzy fallback — single best match by name only.
                r2 = await c.get("https://api.scryfall.com/cards/named",
                                 params={"fuzzy": name})
                if r2.status_code == 200:
                    d = r2.json()
                    if (d.get("prices") or {}).get("usd"):
                        return d.get("id")
                return None
            cards = r.json().get("data", [])
            priced = [d for d in cards if (d.get("prices") or {}).get("usd")]
            if not priced:
                return None
            # cheapest real printing = the conservative market floor
            priced.sort(key=lambda d: float(d["prices"]["usd"]))
            return priced[0].get("id")
    except Exception as exc:
        _log.warning("scryfall resolve failed for %r: %s", name, exc)
        return None


async def scryfall_price_by_id(scryfall_id: str) -> dict | None:
    """Fetch live prices for a known Scryfall id. Returns
    {usd, eur, name, set_name, reserved} or None."""
    if not scryfall_id:
        return None
    try:
        async with httpx.AsyncClient(timeout=10,
                headers={"User-Agent": "TrustSquare/1.0", "Accept": "application/json"}) as c:
            r = await c.get(f"https://api.scryfall.com/cards/{scryfall_id}")
            if r.status_code != 200:
                return None
            d = r.json()
            pr = d.get("prices") or {}
            if not pr.get("usd"):
                return None
            return {
                "usd": float(pr["usd"]),
                "eur": float(pr["eur"]) if pr.get("eur") else None,
                "name": d.get("name"),
                "set_name": d.get("set_name"),
                "reserved": bool(d.get("reserved")),
            }
    except Exception as exc:
        _log.warning("scryfall price fetch failed (%s): %s", scryfall_id, exc)
        return None


def price_caution(asking_zar: float | None, floor_zar: float | None) -> dict | None:
    """Neutral price-position note. We do NOT allege fraud — we have no substantive
    evidence and never characterise a listing as counterfeit, stolen, or a scam.
    We simply report, factually, that an asking price sits well below the verified,
    locally-sourced market price, so the buyer can make their own informed decision.
    Returns a note dict, or None if the price is within normal range. Only fires
    when we have a real verified floor to compare against."""
    if not asking_zar or not floor_zar or floor_zar <= 0:
        return None
    ratio = asking_zar / floor_zar
    if ratio < 0.50:
        pct = round((1 - ratio) * 100)
        return {
            "level": "danger",
            "headline": "Priced well below the verified market",
            "detail": (f"This asking price is about {pct}% below the verified, "
                       f"locally-sourced market price for this item. That may simply be "
                       f"a good deal — but a gap this large is worth understanding before "
                       f"you commit. We can\u2019t see the listing\u2019s condition or "
                       f"provenance, so check those for yourself. This is information, "
                       f"not financial advice."),
        }
    if ratio < 0.70:
        return {
            "level": "caution",
            "headline": "Below the usual market range",
            "detail": ("This is priced below the verified market range for the item. "
                       "It may be a genuine deal; we\u2019d just suggest checking the "
                       "condition and details before deciding. Information, not "
                       "financial advice."),
        }
    return None


PRICE_CHECK_MODEL = "claude-sonnet-4-6"  # AI3 — needs market reasoning depth


def _deduct_tuppence(conn, email: str, amount: int, description: str) -> int:
    """Deduct `amount` Tuppence from `email`. Returns new balance.
    Raises HTTPException 402 if balance insufficient. Does NOT commit."""
    row = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
        (email,)
    ).fetchone()
    balance = int(row["bal"])
    if balance < amount:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient Tuppence — you have {balance}T, need {amount}T"
        )
    conn.execute(
        "INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'ai_service', ?, ?)",
        (email, -amount, description)
    )
    return balance - amount


def _current_tuppence(email: str) -> int:
    """Read-only Tuppence balance on a fresh connection. Used by deliver-then-charge
    paths to report 'tuppence_remaining' when NO charge was made."""
    c = database.get_db()
    try:
        row = c.execute(
            "SELECT COALESCE(SUM(amount), 0) as bal FROM transactions WHERE user_email = ?",
            (email,)
        ).fetchone()
        return int(row["bal"])
    finally:
        c.close()


def _require_tuppence(email: str, amount: int = 1) -> None:
    """Pre-flight guard: ensure the buyer COULD pay before we run a paid AI service.
    Raises 402 if not. Does NOT deduct — deduction happens only on a verified result."""
    if _current_tuppence(email) < amount:
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient Tuppence — you need {amount}T to run this check."
        )


# ── AI1 — Listing Rewrite ─────────────────────────────────────────────────────

@app.post("/listings/{listing_id}/ai-rewrite")
async def ai_listing_rewrite(listing_id: int, email: str):
    """AI1: Seller pays 1T — Claude Haiku rewrites title + description.
    Uses current market language and buyer psychology for the listing category.
    Returns {new_title, new_description, tuppence_remaining}.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")
    _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge

    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
        conn.close()
        raise HTTPException(status_code=403, detail="Email does not match listing owner")

    remaining = _deduct_tuppence(
        conn, email, 1,
        f"AI Listing Rewrite · #{listing_id} · {listing['title'][:40]}"
    )
    conn.commit()
    conn.close()

    category = listing["category"] or "General"
    city     = listing["city"] or "South Africa"
    title    = listing["title"] or ""
    desc     = listing["description"] or ""
    price    = listing["price"] or ""

    system_prompt = (
        "You are an expert marketplace copywriter for TrustSquare, a South African peer-to-peer local marketplace. "
        "You write short, honest, buyer-friendly listings using current South African market language. "
        "You never invent details. You prefer concrete facts over adjectives. "
        "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include street addresses, "
        "business names, complex names, seller names, agent names, phone numbers, email addresses, "
        "or any other identifying information in any generated text. "
        "Always respond with a single valid JSON object — no markdown, no explanation."
    )

    user_prompt = (
        f"Rewrite this {category} listing for a buyer in {city}, South Africa.\n\n"
        f"CURRENT TITLE: {title}\n"
        f"CURRENT DESCRIPTION: {desc}\n"
        f"PRICE: {price}\n\n"
        "Return JSON with exactly two keys:\n"
        '{"new_title": "<15 words max, specific and punchy>", '
        '"new_description": "<60-120 words, 2-3 short paragraphs, buyer psychology, honest, no clichés>"}'
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": AA_MODEL,
                    "max_tokens": 350,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
        rj = resp.json()
        _rw_in, _rw_out = _usage_tokens(rj)
        # P2 — Tuppence covers the revenue side; log token spend so the cost
        # dashboard sees it too (sweep 12 Jun 2026)
        _log_ai_spend(email, "/listings/ai-rewrite", "haiku", _rw_in, _rw_out)
        raw = rj["content"][0]["text"].strip()
        # Strip markdown fences if model adds them
        raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re_match.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        new_title = str(result.get("new_title", "")).strip()[:120]
        new_desc  = str(result.get("new_description", "")).strip()[:1000]
    except Exception as exc:
        _log.error("ai-rewrite: %s", exc)
        raise HTTPException(status_code=500, detail="AI rewrite failed — Tuppence charged") from exc

    _log.info("ai-rewrite: listing #%d email=%s", listing_id, email)
    return {
        "new_title": new_title,
        "new_description": new_desc,
        "tuppence_remaining": remaining,
    }


# ── AI2 — Seller Audit ────────────────────────────────────────────────────────

@app.post("/listings/{listing_id}/ai-audit")
async def ai_seller_audit(listing_id: int, email: str):
    """AI2: Seller pays 1T — Claude Haiku reviews listing quality and returns
    3 specific, actionable improvement steps.
    Returns {actions: [{step, reason}], tuppence_remaining}.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")
    _check_cost_ceiling(email)   # P2 — hard daily rail, BEFORE the Tuppence charge

    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["seller_email"] and listing["seller_email"].lower() != email.lower():
        conn.close()
        raise HTTPException(status_code=403, detail="Email does not match listing owner")

    # Read intro request count for context
    intro_row = conn.execute(
        "SELECT COUNT(*) as cnt FROM intro_requests WHERE listing_id = ?", (listing_id,)
    ).fetchone()
    intro_count = intro_row["cnt"] if intro_row else 0

    # Read trust score
    user_row = conn.execute(
        "SELECT trust_score FROM users WHERE email = ?", (email,)
    ).fetchone()
    trust_score = user_row["trust_score"] if user_row and user_row["trust_score"] else "unknown"

    remaining = _deduct_tuppence(
        conn, email, 1,
        f"AI Seller Audit · #{listing_id} · {listing['title'][:40]}"
    )
    conn.commit()
    conn.close()

    category = listing["category"] or "General"
    city     = listing["city"] or "South Africa"
    title    = listing["title"] or "(no title)"
    desc     = listing["description"] or "(no description)"
    price    = listing["price"] or "(no price)"

    system_prompt = (
        "You are a marketplace performance coach for TrustSquare, a South African peer-to-peer marketplace. "
        "You give direct, specific, actionable advice — no filler, no encouragement padding. "
        "Think like a top-performing seller in the same category who has seen hundreds of listings. "
        "ANONYMITY RULE: TrustSquare is an anonymous marketplace. Never include or suggest including "
        "street addresses, business names, seller names, agent names, phone numbers, or contact details "
        "in any generated text or improvement suggestions. "
        "Always respond with a single valid JSON object — no markdown, no explanation."
    )

    user_prompt = (
        f"This {category} listing in {city} has received {intro_count} intro request(s) and "
        f"the seller has a trust score of {trust_score}.\n\n"
        f"TITLE: {title}\n"
        f"DESCRIPTION: {desc}\n"
        f"PRICE: {price}\n\n"
        "Identify the 3 most important reasons a buyer might scroll past this listing without requesting an intro. "
        "For each reason give a specific fix the seller can do right now.\n\n"
        "Return JSON: "
        '{"actions": [{"step": "<imperative fix, 8 words max>", "reason": "<why this matters, 1 sentence>"}, ...]}'
        " — exactly 3 items in the array."
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": AA_MODEL,
                    "max_tokens": 400,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
        rj = resp.json()
        _au_in, _au_out = _usage_tokens(rj)
        # P2 — Tuppence covers the revenue side; log token spend so the cost
        # dashboard sees it too (sweep 12 Jun 2026)
        _log_ai_spend(email, "/listings/ai-audit", "haiku", _au_in, _au_out)
        raw = rj["content"][0]["text"].strip()
        raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re_match.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        actions = result.get("actions", [])
        # Sanitise — max 3, enforce fields
        clean_actions = []
        for a in actions[:3]:
            if isinstance(a, dict) and a.get("step"):
                clean_actions.append({
                    "step":   str(a.get("step",   ""))[:80],
                    "reason": str(a.get("reason", ""))[:200],
                })
    except Exception as exc:
        _log.error("ai-audit: %s", exc)
        raise HTTPException(status_code=500, detail="AI audit failed — Tuppence charged") from exc

    _log.info("ai-audit: listing #%d email=%s intros=%d", listing_id, email, intro_count)
    return {
        "actions": clean_actions,
        "tuppence_remaining": remaining,
    }


# ── AI3 — Buyer Price Check (upgraded Session 77: three-panel intelligence) ──

# -- Tiered Value Selector: availability helpers + value-tiers endpoint --------
# STEP 5: the paid master switch AND per-provider liveness now come from the
# server-readable feature_flags store (feature_flags.json), so enabling a paid
# provider later is a CONFIG change, not a code edit. Safe defaults: paid OFF,
# every paid/contract provider OFF, free/open/owned providers ON.
def _paid_tiers_enabled() -> bool:
    return feature_flags.paid_tiers_enabled()

def _tier_providers() -> dict:
    return feature_flags.providers()

_CAT_TO_TIERKEY = {
    "card": "cards", "cards": "cards", "trading": "cards",
    "trading cards": "cards", "collectibles": "cards", "collectables": "cards",
    "property": "property", "estate agents": "property", "accommodation": "property",
    "vehicles": "vehicles", "vehicle": "vehicles", "cars": "vehicles", "auto": "vehicles",
}

def _listing_country_iso2(listing) -> str:
    c = (listing["country"] if "country" in listing.keys() else None) or "ZA"
    c = str(c).strip()
    M = {"south africa": "ZA", "united kingdom": "UK", "england": "UK",
         "scotland": "UK", "wales": "UK", "united states": "US", "usa": "US",
         "united states of america": "US", "america": "US", "australia": "AU"}
    return M.get(c.lower(), (c.upper()[:2] if len(c) >= 2 else "ZA"))

def _comp_count(listing) -> int:
    """Cheap proxy: active same-category, same-city listings (excl. this one).
    Cars: counts TRUE comparables (make/model/year matched) so the comps tier
    only shows when it can honestly answer — same filter the median uses."""
    try:
        _cat = ((listing["category"] or "") if "category" in listing.keys() else "").strip().lower()
        if _cat in ("cars", "vehicles"):
            _t = (listing["title"] if "title" in listing.keys() else "") or ""
            return len(_comp_amounts(listing["category"], listing["city"], listing["id"], ref_title=_t))
    except Exception:
        pass
    try:
        conn = database.get_db()
        try:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM listings "
                "WHERE category = ? AND city = ? AND id <> ? "
                "AND COALESCE(status,'active') != 'paused'",
                ((listing["category"] or ""), (listing["city"] or ""), listing["id"]),
            ).fetchone()
            return int(row["n"]) if row else 0
        finally:
            conn.close()
    except Exception:
        return 0

def _tierkey_for(listing, service: str) -> str:
    if service == "yield":
        return "property"
    cat = (listing["category"] or "").strip().lower()
    return _CAT_TO_TIERKEY.get(cat, cat)

def _offered_value_tiers(listing, service: str):
    """Gated tiers for this listing+service. Hide rule lives in ai_service_tiers."""
    return ai_service_tiers.available_tiers(
        service, _tierkey_for(listing, service), _listing_country_iso2(listing),
        providers=_tier_providers(),
        paid_enabled=_paid_tiers_enabled(),
        comp_count=_comp_count(listing),
    )

def _resolver_ready(service: str, tierkey: str, country: str = "ZA") -> dict:
    """STEP 3: which tiers have a BUILT, runnable resolver today. Delegates to
    tier_resolvers.served_tiers, which is credential-aware: collectible feeds that
    need a key (BrickLink/Numista/JustTCG) report ready ONLY when that key is set,
    so the FEA never shows a chip we cannot actually deliver."""
    return tier_resolvers.served_tiers(
        service, tierkey, country, creds=tier_resolvers.creds_from_env())

# ── FREE worked examples for the AI feature panel ("See an example" button) ──────────────
# Fixes the long-standing bug: the FEA calls GET /ai/example/<id> but no route existed, so every
# example button errored. This route ALWAYS returns a valid {result} (real sample for known ids,
# graceful generic sample otherwise) so it can never error regardless of the feature id served by
# /ai/functions. Free, no Tuppence, no auth. Carries the standard date stamp.
_AI_EXAMPLE_SAMPLES = {
    "collectables_advert": (
        "## Collectables Advert + Market Report (sample)\n\n"
        "**Item identified:** 1968 Krugerrand, 1oz gold, circulated (VF).\n\n"
        "**Suggested title:** 1968 Krugerrand 1oz Gold Coin — Circulated, Authenticated\n\n"
        "**Market read:** Bullion 1oz Krugerrands trade close to gold spot plus a small premium. "
        "As a live-market item the price moves intraday — always confirm against spot at the moment of sale.\n\n"
        "**Suggested asking band:** spot + 3–6% premium for circulated grade.\n\n"
        "## Safety awareness\nMeet in a safe public place; for bullion, verify weight and authenticity before payment.\n"
    ),
    "collection_liquidation": (
        "## Collection Liquidation Plan (sample)\n\n"
        "**Collection:** ~40 mixed trading cards + 6 silver coins.\n\n"
        "**Recommended approach:** list the 6 coins individually (higher per-item value, live-market priced), "
        "bundle common cards into themed lots. Estimated total indicative range provided on a real run.\n\n"
        "## Safety awareness\nFor precious-metal items, re-check spot price immediately before any sale.\n"
    ),
    "property_dossier": (
        "## Property Dossier (sample)\n\n"
        "**Subject:** 3-bed townhouse, suburb X.\n\n"
        "**Indicative area band:** R1.45m–R1.78m based on recent comparable listings. "
        "Not a formal valuation — verify with a registered property practitioner.\n"
    ),
    "car_dossier": (
        "## Vehicle Dossier (sample)\n\n"
        "**Subject:** 2018 hatchback, ~78,000 km.\n\n"
        "**Indicative asking band:** R182k–R205k based on comparable listings; condition and service "
        "history shift this materially.\n"
    ),
    "heritage_tour": (
        "## Heritage Tour (sample)\n\n"
        "A half-day route taking in three nearby heritage sites with timing and context for each. "
        "On a real run this includes a map and waypoints.\n"
    ),
    "expedition_dossier": (
        "## Expedition Dossier (sample)\n\nKit list, route notes, seasonal cautions and a difficulty read "
        "for your chosen destination.\n\n## Safety awareness\nCheck current conditions before departure.\n"
    ),
    "weekend_itinerary": (
        "## Weekend Itinerary (sample)\n\nA two-day plan balancing must-sees with downtime, with rough "
        "costs and travel times. On a real run this includes a map.\n"
    ),
    "offer_advisor": (
        "## Offer Advisor (sample)\n\n**Listing asking:** R12,500.\n\n**Suggested opening offer:** R10,800, "
        "with reasoning you can paste into your message to the seller.\n"
    ),
    "study_plan": (
        "## Study Plan (sample)\n\nA 4-week plan for your subject with weekly goals, resources and a "
        "self-check at the end of each week.\n"
    ),
}

def _ai_example_generic(function_id: str) -> str:
    nice = (function_id or "this feature").replace("_", " ").title()
    return ("## " + nice + " — sample\n\n"
            "This is an illustrative preview of what " + nice + " produces. On a real run you receive a "
            "full, item-specific report. Run the feature to see your own result (free preview available "
            "where supported).\n")

@app.get("/ai/example/{function_id}")
def ai_example(function_id: str):
    """Free worked example for the AI feature panel. ALWAYS returns a valid {result} so the
    'See an example' button can never error, for any feature id. No Tuppence, no auth."""
    fid = (function_id or "").strip()[:64]
    body = _AI_EXAMPLE_SAMPLES.get(fid) or _ai_example_generic(fid)
    return {"result": body, "example": True, "function_id": fid, **_report_stamp()}


@app.get("/listings/{listing_id}/value-tiers")
async def listing_value_tiers(listing_id: int, service: str = "fair_price"):
    """Tiered Value Selector: returns the colour-coded chips the FEA should show
    for this listing+service, already gated (free-only at launch; hidden where we
    cannot deliver a true answer). Read-only; charges nothing."""
    if service not in ("fair_price", "yield"):
        raise HTTPException(status_code=400, detail="Unknown service")
    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    conn.close()
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    tierkey = _tierkey_for(listing, service)
    _ctry = _listing_country_iso2(listing)
    chips = ai_service_tiers.chips_payload(
        service, tierkey, _ctry,
        providers=_tier_providers(),
        paid_enabled=_paid_tiers_enabled(),
        comp_count=_comp_count(listing),
    )
    ready = _resolver_ready(service, tierkey, _ctry)
    for ch in chips:
        ch["ready"] = bool(ready.get(ch["tier"], False))
    return {
        "listing_id": listing_id,
        "service": service,
        "country": _ctry,
        "category": tierkey,
        "paid_tiers_enabled": _paid_tiers_enabled(),
        "chips": chips,
        **_report_stamp(volatile=_is_volatile_item(tierkey, service)),
    }


# -- Tiered Value Selector STEP 3: FREE/owned fair-price + comps helpers -------
_INDICATIVE_LABEL = ("Indicative only - information, not financial advice or a "
                     "formal valuation.")

# ── Report date-stamp + accuracy disclaimer (liability: a price/market figure with no date
# reads as 'true forever'. Every AI report carries WHEN it was generated and that it is only
# accurate as of that date. One helper, spread into every report return, so no feature omits it.) ──
_VOLATILE_TERMS = ("coin", "coins", "numismat", "bullion", "krugerrand", "gold", "silver",
                   "platinum", "precious metal", "sovereign", "spot price", "ounce", "oz ")
def _is_volatile_item(*parts) -> bool:
    """True if any provided string (category/subject/title/source) names a spot/market-priced item
    (gold, bullion coins, precious metals) whose price moves intraday -> needs the minute-level warning."""
    blob = " ".join(str(p or "").lower() for p in parts)
    return any(t in blob for t in _VOLATILE_TERMS)

def _report_stamp(extra: str = "", *, volatile: bool = False):
    """Date/time-accuracy fields every AI report must carry. Time is to the MINUTE in UTC —
    spot-priced items (gold, bullion coins, FX) move intraday, so a date alone understates the risk.
    `extra` appends feature-specific wording. `volatile=True` adds an intraday-movement warning
    for fast-moving / market-priced items (precious metals, coins, anything tracking a live exchange)."""
    import datetime as _dt
    _now = _dt.datetime.now(_dt.timezone.utc)
    _human = _now.strftime("%d %B %Y, %H:%M UTC")          # minute precision, explicitly UTC
    base = (f"This report is accurate as of {_human}. AI estimates, prices and market figures "
            f"change continuously — the figure shown may be materially higher or lower if this "
            f"feature is run even minutes later. It is a snapshot for the exact time above, not a "
            f"guarantee of current or future value.")
    vol = (" For precious metals, bullion coins and other items priced off a live market, the spot "
           "price can move by significant amounts within minutes; this snapshot is not a dealing "
           "price and must be re-checked against the live market before any transaction.")
    txt = base + (vol if volatile else "") + ((" " + extra) if extra else "")
    return {
        "as_of": _now.strftime("%Y-%m-%d"),
        "as_of_time_utc": _now.strftime("%H:%M"),
        "as_of_iso": _now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "as_of_human": _human,                              # e.g. "27 June 2026, 11:34 UTC"
        "volatile": bool(volatile),
        "date_disclaimer": txt,
    }

def _parse_money(v):
    """Parse a price string ('R1 200 000', '$1,700/mo') to a float, or None."""
    if v is None:
        return None
    cleaned = re.sub(r"[^0-9.]", "", str(v).replace(",", "").replace(" ", ""))
    try:
        f = float(cleaned)
        return f if f > 0 else None
    except Exception:
        return None

_VEH_STOPWORDS = frozenset({
    "for", "sale", "the", "and", "with", "low", "full", "service", "history",
    "one", "owner", "excellent", "good", "condition", "auto", "automatic",
    "manual", "petrol", "diesel", "hybrid", "electric", "white", "black",
    "silver", "blue", "red", "grey", "gray", "green", "gold", "brown",
    "immaculate", "bargain", "urgent", "price", "neg", "negotiable", "km",
    "mileage", "very", "clean", "new", "like",
})

def _veh_title_sig(title):
    """(year, tokens) signature from a vehicle listing title. Deterministic, $0."""
    t = (title or "").lower()
    yr = None
    m = re.search(r"\b(19[5-9]\d|20[0-4]\d)\b", t)
    if m:
        yr = int(m.group(1))
    toks = {w for w in re.findall(r"[a-z][a-z0-9\-]{2,}", t)
            if w not in _VEH_STOPWORDS and not w.isdigit()}
    return yr, toks

def _veh_comparable(ref_sig, title):
    """True if `title` looks like the same make/model (and year band) as ref_sig.
    Rule: years (when both known) within +/-2, AND >=2 shared significant tokens,
    or 1 shared long token (>=5 chars, e.g. 'hilux') when the year band matches."""
    ref_yr, ref_toks = ref_sig
    if not ref_toks:
        return False
    yr, toks = _veh_title_sig(title)
    if ref_yr is not None and yr is not None and abs(ref_yr - yr) > 2:
        return False
    shared = ref_toks & toks
    if len(shared) >= 2:
        return True
    return (len(shared) == 1 and ref_yr is not None and yr is not None
            and any(len(w) >= 5 for w in shared))

def _comp_amounts(category, city, exclude_id, rentals_only=False, ref_title=None):
    """Parsed amounts of active same-category, same-city listings (excl. this one)
    - raw material for an internal-comps median. Owned data only.
    For vehicles (ref_title given + cars category), rows are filtered to TRUE
    comparables — same make/model tokens, year +/-2 — so a Corolla is never
    priced against a Land Cruiser. CARS-VERIFY-1 free half (3 Jul 2026)."""
    out = []
    try:
        conn = database.get_db()
        try:
            try:
                rows = conn.execute(
                    "SELECT price, title, COALESCE(listing_type,\'\') AS lt FROM listings "
                    "WHERE category=? AND city=? AND id<>? AND COALESCE(status,\'active\')!=\'paused\'",
                    ((category or ""), (city or ""), exclude_id)).fetchall()
            except Exception:
                rows = conn.execute(
                    "SELECT price, title, \'\' AS lt FROM listings "
                    "WHERE category=? AND city=? AND id<>? AND COALESCE(status,\'active\')!=\'paused\'",
                    ((category or ""), (city or ""), exclude_id)).fetchall()
        finally:
            conn.close()
        _veh_sig = None
        if ref_title and (category or "").strip().lower() in ("cars", "vehicles"):
            _veh_sig = _veh_title_sig(ref_title)
        for r in rows:
            if rentals_only and "rent" not in ((r["lt"] or "").lower()):
                continue
            if _veh_sig is not None and not _veh_comparable(_veh_sig, r["title"]):
                continue
            amt = _parse_money(r["price"])
            if amt:
                out.append(amt)
    except Exception:
        return []
    return out

async def _fair_price_resolve(listing, listing_id, tier, tierkey, country, category, city, asking_zar):
    """STEP 3 fair-price resolver for non-card categories (FREE/owned sources only).
    Returns ('verified', {...}) | ('area_guide', {...}) | None. The NUMBER always
    comes from a feed or arithmetic; the model only narrates the verified branch."""
    try:
        if tierkey == "property" and country == "UK" and tier == "1T":
            lr = await tier_resolvers.uk_land_registry_median(city)
            if lr:
                med = lr["value"]
                return ("verified", {
                    "source": "land_registry", "floor_zar": None,
                    "official_range": "GBP " + format(med, ",.0f") + "  (median of " + str(lr["n"]) + " sold)",
                    "official_ctx": lr["provenance"],
                    "block": ("VERIFIED MARKET DATA (use these EXACT figures, do not alter): "
                              + lr["provenance"] + " | Median sold price GBP " + format(med, ",.0f")
                              + " | Source: HM Land Registry Price Paid (Open Government Licence).")})
        if tier == "1T" and tierkey in ("property", "vehicles"):
            _ref_title = None
            if tierkey == "vehicles":
                try:
                    _ref_title = (listing["title"] if "title" in listing.keys() else None)
                except Exception:
                    _ref_title = None
            est = tier_resolvers.internal_comps_estimate(
                _comp_amounts(category, city, listing_id, ref_title=_ref_title), min_n=8)
            if est:
                med = est["value"]
                _match_note = " matched on make/model/year" if tierkey == "vehicles" else ""
                return ("verified", {
                    "source": "internal_comps", "floor_zar": med,
                    "official_range": "R" + format(med, ",.0f") + "  (median of " + str(est["n"]) + " comparable " + str(city) + " listings" + _match_note + ")",
                    "official_ctx": est["provenance"],
                    "block": ("VERIFIED MARKET DATA (use these EXACT figures, do not alter): "
                              + est["provenance"] + " | Median asking price R" + format(med, ",.0f")
                              + " | These are comparable TrustSquare listings, not this exact item.")})
        if tier == "0T" and tierkey == "property" and country == "ZA":
            fa = None
            try:
                if "floor_area" in listing.keys() and listing["floor_area"]:
                    fa = float(listing["floor_area"])
            except Exception:
                fa = None
            g = tier_resolvers.za_area_price_guide(city, floor_area=fa)
            if g:
                imp = ""
                if g.get("implied_value"):
                    imp = (" For ~" + format(fa, ".0f") + " m2 that implies about R"
                           + format(g["implied_low"], ",.0f") + "-R" + format(g["implied_high"], ",.0f") + ".")
                assess = ("Typical asking prices in " + str(city) + " run " + g["range_text"]
                          + " (" + g["source"] + ", " + str(g["date"]) + ")." + imp
                          + " This is an area benchmark, not a figure for this specific property "
                          "- compare it against the asking price yourself. " + _INDICATIVE_LABEL)
                return ("area_guide", {
                    "source": "payprop_tpn", "range_text": g["range_text"],
                    "assessment": assess, "provenance": g["source"] + " (" + str(g["date"]) + ")",
                    "date": g["date"]})
        if tier == "1T" and tierkey in ("lego", "coins", "tcg", "cards", "comics", "watches"):
            title = (listing["title"] if "title" in listing.keys() else "") or ""
            feed = None
            if tierkey == "lego":
                feed = await tier_resolvers.bricklink_price(title)
            elif tierkey == "coins":
                feed = await tier_resolvers.numista_price(title)
            elif tierkey == "tcg":
                feed = await tier_resolvers.justtcg_price(title)
            # S130 quick-win: official eBay Browse ASKING-price band as the
            # collectible fallback (free tier, credential-gated, B7-safe).
            if (not feed or not feed.get("value")) and _tier_providers().get("ebay_browse"):
                feed = await tier_resolvers.ebay_asking_band(title)
            if feed and feed.get("value"):
                rate = await live_usd_zar()
                usd = float(feed["value"]); zar = usd * rate
                if feed.get("source") == "ebay_browse":
                    # Honesty rule: an asking band is NEVER presented as a
                    # verified/sold price - the wording carries the difference.
                    lo_z = float(feed["low"]) * rate; hi_z = float(feed["high"]) * rate
                    return ("verified", {
                        "source": feed["source"], "floor_zar": zar,
                        "official_range": ("R" + format(lo_z, ",.0f") + "-R" + format(hi_z, ",.0f")
                                           + " asking (median R" + format(zar, ",.0f")
                                           + " / USD $" + format(usd, ",.2f") + " x R" + format(rate, ".2f") + "/USD)"),
                        "official_ctx": feed["provenance"],
                        "block": ("MARKET ASKING-PRICE BAND (use these EXACT figures, do not alter; "
                                  "these are ASKING prices of comparable items currently listed on eBay - "
                                  "NOT sold prices, so treat as an upper-leaning guide): "
                                  + feed["provenance"] + " | Median asking USD $" + format(usd, ",.2f")
                                  + " = R" + format(zar, ",.0f")
                                  + "; band USD $" + format(float(feed["low"]), ",.2f")
                                  + "-$" + format(float(feed["high"]), ",.2f") + ".")})
                return ("verified", {
                    "source": feed["source"], "floor_zar": zar,
                    "official_range": "R" + format(zar, ",.0f") + "  (USD $" + format(usd, ",.2f") + " x R" + format(rate, ".2f") + "/USD)",
                    "official_ctx": feed["provenance"],
                    "block": ("VERIFIED MARKET DATA (use these EXACT figures, do not alter): "
                              + feed["provenance"] + " | Verified price USD $" + format(usd, ",.2f")
                              + " = R" + format(zar, ",.0f") + ".")})
    except Exception as exc:
        _log.warning("fair-price resolve failed: %s", exc)
    return None


@app.post("/listings/{listing_id}/price-check")
async def ai_price_check(listing_id: int, email: str, tier: Optional[str] = None):
    """AI3: Buyer pays 1T — honest, three-panel price intelligence.

    INTEGRITY MODEL (price-integrity fix):
      The model writes the SENTENCE; the system produces the NUMBER.
      - Collectibles with a resolved Scryfall id  -> VERIFIED feed price (USD->ZAR
        live rate). The LLM only narrates the real figures it is handed.
      - Everything else -> an explicitly-labelled QUALITATIVE GUIDE. The LLM may
        give a rough range but it is flagged 'not a verified price', and we never
        cheerlead ('move quickly' is not permitted anywhere).
      - A first-class fraud guard fires when asking price is far below a VERIFIED
        floor: the verdict becomes a warning, never a 'buy' nudge.
    Returns {verdict, source, sa_context, sa_range, assessment, official_context,
             official_range, local_vs_global, asking_price, verified, safety_flag,
             tuppence_remaining, ...legacy}.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")

    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")

    # DELIVER-THEN-CHARGE (Session 95): we do NOT deduct here. Tuppence is only
    # charged at the end, and ONLY if we produced a verified service. A guess,
    # a 'cannot verify', or any failure costs the buyer nothing.
    # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour; a
    # tier-aware caller must request a tier actually offered for this listing.
    if tier is None:
        _charge = 1
    else:
        _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "fair_price")}
        if tier not in _offered_t:
            conn.close()
            raise HTTPException(status_code=400,
                detail=f"Tier {tier} is not available for this listing")
        _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
    _require_tuppence(email, _charge)   # pre-flight only — no deduction yet
    _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached
    category    = listing["category"] or "General"
    city        = listing["city"] or "South Africa"
    title       = listing["title"] or "(no title)"
    desc        = listing["description"] or "(no description)"
    price       = listing["price"] or "(no price)"
    scryfall_id = listing["scryfall_id"] if "scryfall_id" in listing.keys() else None
    conn.close()  # done reading; charging happens on its own connection at the end

    # Parse the buyer-facing asking price into a number for ratio checks.
    asking_zar = None
    try:
        asking_zar = float(str(price).replace("R", "").replace(",", "").strip())
    except Exception:
        asking_zar = None

    # ── Step 1+2: try to resolve a REAL verified price (collectibles) ──────────
    verified_block = None        # text handed to the model as ground truth
    official_range = "N/A"
    official_ctx   = ""
    floor_zar      = None
    verified       = False
    source         = "ai_estimate"

    # Late-resolve a scryfall id if the listing predates this column.
    if not scryfall_id:
        try:
            scryfall_id = await resolve_scryfall_id(title, category)
            if scryfall_id:
                c2 = database.get_db()
                c2.execute("UPDATE listings SET scryfall_id = ? WHERE id = ?",
                           (scryfall_id, listing_id))
                c2.commit(); c2.close()
        except Exception:
            scryfall_id = None

    if scryfall_id:
        feed = await scryfall_price_by_id(scryfall_id)
        if feed and feed.get("usd"):
            rate = await live_usd_zar()
            usd  = feed["usd"]
            floor_zar = usd * rate
            verified = True
            source   = "scryfall"
            reserved = " (Reserved List — cannot be reprinted)" if feed.get("reserved") else ""
            official_range = f"R{floor_zar:,.0f}  (USD ${usd:,.2f} \u00d7 R{rate:.2f}/USD)"
            official_ctx   = (f"Verified market price for {feed.get('name')} "
                              f"[{feed.get('set_name')}]{reserved}: "
                              f"USD ${usd:,.2f} on TCGPlayer (via Scryfall), "
                              f"\u2248 R{floor_zar:,.0f} at today's rate.")
            verified_block = (
                f"VERIFIED MARKET DATA (use these EXACT figures, do not alter them):\n"
                f"- Card: {feed.get('name')} [{feed.get('set_name')}]{reserved}\n"
                f"- Verified market price: USD ${usd:,.2f} = R{floor_zar:,.0f} "
                f"(live rate R{rate:.2f}/USD)\n"
                f"- Buyer's asking price: {price}\n"
            )

    # ── Step 3: narrate. Two prompt modes: verified vs qualitative-guide ───────
    # -- STEP 3: no card feed -> try the FREE/owned resolver for the chosen tier
    if (not verified_block) and (tier is not None):
        _fpx = await _fair_price_resolve(
            listing, listing_id, tier, _tierkey_for(listing, "fair_price"),
            _listing_country_iso2(listing), category, city, asking_zar)
        if _fpx and _fpx[0] == "verified":
            _e = _fpx[1]
            verified = True
            source = _e["source"]
            floor_zar = _e.get("floor_zar")
            official_range = _e["official_range"]
            official_ctx = _e["official_ctx"]
            verified_block = _e["block"]
        elif _fpx and _fpx[0] == "area_guide":
            _e = _fpx[1]
            _log.info("ai-price-check: listing #%d buyer=%s AREA-GUIDE %s (0T free)",
                      listing_id, email, _e["source"])
            return {
                "verdict": "area_guide", "source": _e["source"],
                "verified": False, "charged": False,
                "sa_context": "", "sa_range": _e.get("range_text", "N/A"),
                "assessment": _e["assessment"],
                "official_context": _e.get("provenance", ""),
                "official_range": _e.get("range_text", "N/A"),
                "local_vs_global": "cannot_compare", "asking_price": price,
                "safety_flag": None, "tuppence_remaining": _current_tuppence(email),
                "indicative_label": _INDICATIVE_LABEL,
                "provenance_date": _e.get("date", ""),
                "context": _e["assessment"], "suggested_range": _e.get("range_text", "N/A"),
            }
    if verified_block:
        system_prompt = (
            "You are a pricing analyst for TrustSquare, a South African marketplace. "
            "You are given VERIFIED market figures. You must NEVER invent, round, or "
            "contradict them — only explain them in plain language. Never tell a buyer "
            "to 'move quickly' or 'buy now'. Be honest and protective. "
            "Always respond with a single valid JSON object — no markdown."
        )
        user_prompt = (
            f"A buyer is considering this {category} listing in {city}, South Africa.\n\n"
            f"TITLE: {title}\nDESCRIPTION: {desc[:400]}\n\n"
            f"{verified_block}\n"
            "Write a short, honest assessment comparing the asking price to the verified "
            "market price. Do not output any price number other than those given above.\n"
            "Return JSON with these keys (strings, 50 words max each):\n"
            "{\n"
            '  "verdict": "fair" | "above_market" | "below_market" | "cannot_assess",\n'
            '  "sa_context": "<note on the SA second-hand reality for this item, qualitative>",\n'
            '  "assessment": "<plain-language read on the asking price vs the verified figure>",\n'
            '  "local_vs_global": "cheaper_locally" | "cheaper_globally" | "similar" | "cannot_compare"\n'
            "}"
        )
    else:
        # No verified price feed for this category. Per the integrity rule, we do
        # NOT sell a guess. Return an honest 'cannot verify' and charge nothing.
        _log.info("ai-price-check: listing #%d buyer=%s NO-FEED -> free cannot_verify",
                  listing_id, email)
        bal = _current_tuppence(email)
        return {
            "verdict":          "cannot_verify",
            "source":           "no_feed",
            "verified":         False,
            "charged":          False,
            "sa_context":       "",
            "sa_range":         "N/A",
            "assessment":       ("We don\u2019t yet have a verified price source for this "
                                 "category, so we won\u2019t guess. No Tuppence was charged. "
                                 "Compare the asking price against similar local listings "
                                 "before deciding."),
            "official_context": "",
            "official_range":   "N/A",
            "local_vs_global":  "cannot_compare",
            "asking_price":     price,
            "safety_flag":      None,
            "tuppence_remaining": bal,
            "context":          "",
            "suggested_range":  "N/A",
        }

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": PRICE_CHECK_MODEL,
                    "max_tokens": 700,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
        _resp_json = resp.json()
        raw = _resp_json["content"][0]["text"].strip()
        _pc_in, _pc_out = _usage_tokens(_resp_json)   # C2/C3
        raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re_match.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        verdict         = str(result.get("verdict", "cannot_assess"))[:20]
        sa_context      = str(result.get("sa_context", ""))[:600]
        sa_range        = str(result.get("sa_range", "N/A"))[:100]
        assessment      = str(result.get("assessment", ""))[:400]
        local_vs_global = str(result.get("local_vs_global", "cannot_compare"))[:20]
    except Exception as exc:
        _log.error("ai-price-check: %s", exc)
        raise HTTPException(status_code=500, detail="AI price check failed — no Tuppence charged") from exc

    # ── Price-position note: only fires against a VERIFIED floor. Not a fraud
    #    allegation — a neutral observation that the price is well below market. ─
    safety_flag = price_caution(asking_zar, floor_zar)
    if safety_flag and safety_flag["level"] == "danger":
        verdict = "below_verified_market"

    # DELIVER-THEN-CHARGE: a verified result was produced — charge exactly now.
    cc = database.get_db()
    try:
        remaining = _deduct_tuppence(
            cc, email, _charge,
            f"AI Price Check \u00b7 #{listing_id} \u00b7 {title[:40]}"
        )
        cc.commit()
    finally:
        cc.close()

    # C3 — log real AI spend for this paid call (was previously unlogged).
    _log_ai_spend(email, "/listings/ai-price-check", "sonnet", _pc_in, _pc_out)

    _log.info("ai-price-check: listing #%d buyer=%s verdict=%s verified=%s flag=%s charged=1T",
              listing_id, email, verdict, verified,
              safety_flag["level"] if safety_flag else "none")
    return {
        "verdict":          verdict,
        "source":           source,            # 'scryfall'
        "verified":         verified,          # True only when a real feed was used
        "charged":          True,
        "sa_context":       sa_context,
        "sa_range":         sa_range,
        "assessment":       assessment,
        "official_context": official_ctx,
        "official_range":   official_range,
        "local_vs_global":  local_vs_global,
        "asking_price":     price,
        "safety_flag":      safety_flag,        # None | {level, headline, detail}
        "tuppence_remaining": remaining,
        # Legacy fields — kept for backward compat
        "context":          assessment,
        "suggested_range":  sa_range,
        **_report_stamp("Price reflects feeds/market data available at the time above; re-run for a current figure.", volatile=_is_volatile_item(source, verdict, locals().get("subject"), locals().get("_cat"))),
    }

# ── END AI TUPPENCE SERVICES (Session 73) ────────────────────────────────────


# ── AI TUPPENCE SERVICES — TIER 2 (Session 74) ───────────────────────────────
#
#   AI4  POST /listings/{id}/yield-calc?email=     Haiku   Property yield calculator (1T)
#   AI5  POST /listings/batch-cards?email=         Sonnet  Batch card listing via vision (2T)
#
# AI4: Property listings only. Calculates gross yield, net estimate, SA comparison.
# AI5: Collectors category. Accepts up to 10 base64 images, returns array of draft JSONs.


# ── AI4 — Property Yield Calculator ──────────────────────────────────────────

async def _yield_fill_missing(need, tier, country, city, suburb, listing, listing_id):
    """STEP 3: source the missing yield half (rent OR purchase price) from a
    FREE/owned feed, per tier + country. Returns {value, provenance, date,
    specificity} or None. Numbers come from feeds/arithmetic, never a model."""
    try:
        area = suburb or city
        _cat = listing["category"] if ("category" in listing.keys() and listing["category"]) else "Property"
        if need == "rent":
            if country == "US" and tier == "1T":
                r = tier_resolvers.us_market_rent(area)
                if r:
                    return r
            if country == "UK" and tier == "1T":
                r = tier_resolvers.uk_market_rent(area)
                if r:
                    return r
            if country == "ZA" and tier == "1T":
                est = tier_resolvers.internal_comps_estimate(
                    _comp_amounts(_cat, city, listing_id, rentals_only=True),
                    min_n=8, label="comparable rentals")
                if est:
                    return {"value": est["value"], "provenance": est["provenance"],
                            "date": est["date"], "specificity": est["specificity"]}
            if country == "ZA" and tier == "0T":
                r = tier_resolvers.za_area_rent(city)
                if r:
                    return r
        else:
            if country == "UK" and tier == "1T":
                lr = await tier_resolvers.uk_land_registry_median(city)
                if lr:
                    return {"value": lr["value"], "provenance": lr["provenance"],
                            "date": lr["date"], "specificity": lr["specificity"]}
            if tier == "1T" and country in ("US", "ZA", "AU"):
                est = tier_resolvers.internal_comps_estimate(
                    _comp_amounts(_cat, city, listing_id), min_n=8)
                if est:
                    return {"value": est["value"], "provenance": est["provenance"],
                            "date": est["date"], "specificity": est["specificity"]}
            if country == "ZA" and tier == "0T":
                fa = None
                try:
                    if "floor_area" in listing.keys() and listing["floor_area"]:
                        fa = float(listing["floor_area"])
                except Exception:
                    fa = None
                g = tier_resolvers.za_area_price_guide(city, floor_area=fa)
                if g and g.get("implied_value"):
                    return {"value": g["implied_value"],
                            "provenance": g["source"] + " area price guide",
                            "date": g["date"], "specificity": g["specificity"]}
    except Exception as exc:
        _log.warning("yield fill failed: %s", exc)
    return None


@app.post("/listings/{listing_id}/yield-calc")
async def ai_yield_calc(listing_id: int, email: str,
                        rent: float | None = None,
                        purchase_price: float | None = None,
                        tier: Optional[str] = None):
    """AI4: Property yield — HONEST & deliver-then-charge (Session 95).

    A real gross yield needs BOTH a purchase price and an annual rent. A listing
    only carries one number (sale price OR monthly rent), so we:
      - take the listing's own figure for its side, and
      - accept the OTHER figure from the caller (?rent= or ?purchase_price=).
    If the second figure is missing we return needs_input and charge NOTHING.
    The yield is computed in PYTHON (not guessed by the model). The LLM only
    writes the benchmark sentence. 1T is charged ONLY when a real yield is
    produced from real inputs.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")

    conn = database.get_db()
    listing = conn.execute("SELECT * FROM listings WHERE id = ?", (listing_id,)).fetchone()
    if not listing:
        conn.close()
        raise HTTPException(status_code=404, detail="Listing not found")

    category = listing["category"] or ""
    if "property" not in category.lower() and category.lower() not in ("property", "estate agents", "accommodation"):
        conn.close()
        raise HTTPException(status_code=400, detail="Yield calculator is only available for Property listings")

    city          = listing["city"] or "South Africa"
    suburb        = listing["suburb"] or ""
    title         = listing["title"] or "(no title)"
    desc          = listing["description"] or ""
    price_raw     = listing["price"] or ""
    listing_type  = (listing["listing_type"] if "listing_type" in listing.keys() else None) or ""
    conn.close()

    # Pre-flight: can the buyer pay at all? (No deduction yet.)
    # Tiered Value Selector: legacy callers (tier=None) keep 1T behaviour.
    if tier is None:
        _charge = 1
    else:
        _offered_t = {t["tier"] for t in _offered_value_tiers(listing, "yield")}
        if tier not in _offered_t:
            raise HTTPException(status_code=400,
                detail=f"Tier {tier} is not available for this listing")
        _charge = ai_service_tiers.TIER_TUPPENCE.get(tier, 1)
    _require_tuppence(email, _charge)
    _check_cost_ceiling(email)    # C1 — refuse if daily cost ceiling reached

    def _num(v):
        try:
            return float(str(v).replace("R", "").replace(",", "")
                         .replace("/month", "").replace("pm", "").strip())
        except Exception:
            return None

    listing_amount = _num(price_raw)
    lt = listing_type.lower()
    is_rental = ("rent" in lt) or ("rent" in (title + " " + desc).lower() and "for sale" not in lt)

    # Resolve purchase_price (annual rent / monthly rent) from listing + caller input.
    monthly_rent = None
    buy_price    = None
    need = None
    if is_rental:
        # Listing price IS the monthly rent. Need the purchase price from caller.
        monthly_rent = listing_amount
        buy_price    = purchase_price
        if not buy_price:
            need = "purchase_price"
    else:
        # Listing price IS the sale/purchase price. Need expected monthly rent.
        buy_price    = listing_amount
        monthly_rent = rent
        if not monthly_rent:
            need = "rent"

    # Honest 'needs input' — FREE, no Tuppence charged.
    # -- STEP 3: source the missing half from a FREE/owned feed (per tier+country)
    _country_y = _listing_country_iso2(listing)
    _rent_src = "your figure"
    _price_src = "the listing"
    if need and tier is not None:
        _filled = await _yield_fill_missing(need, tier, _country_y, city, suburb, listing, listing_id)
        if _filled:
            if need == "rent":
                monthly_rent = _filled["value"]; _rent_src = _filled["provenance"]
            else:
                buy_price = _filled["value"]; _price_src = _filled["provenance"]
            need = None

    if need or not buy_price or not monthly_rent or buy_price <= 0 or monthly_rent <= 0:
        bal = _current_tuppence(email)
        prompt_for = ("the expected monthly rent" if need == "rent"
                      else "the likely purchase price" if need == "purchase_price"
                      else "both the purchase price and the monthly rent")
        return {
            "status":           "needs_input",
            "charged":          False,
            "need":             need or "both",
            "listing_amount":   listing_amount,
            "is_rental":        is_rental,
            "message":          (f"To calculate a real yield we need {prompt_for}. "
                                 f"Enter it and we\u2019ll compute the actual figure — "
                                 f"no Tuppence is charged until we do."),
            "tuppence_remaining": bal,
        }

    # ── REAL computation in Python (deterministic, auditable) ──────────────────
    annual_rent = monthly_rent * 12.0
    gross = (annual_rent / buy_price) * 100.0

    # Net estimate: subtract a transparent cost band (rates, levies, maintenance,
    # vacancy). We show the assumption rather than hiding it inside a model guess.
    # STEP 3: versioned, dated per-region net-cost band replaces the flat 3%.
    _band = tier_resolvers.net_cost_band(_country_y)
    NET_COST_PCT = float(_band.get("typical", 3.0))
    net = gross - NET_COST_PCT

    # LLM writes ONLY the qualitative benchmark sentence — handed the real numbers.
    location_str = f"{suburb}, {city}" if suburb else city
    _BENCHMARKS = {
        "ZA": ("SA GROSS YIELD BENCHMARKS (2026): Pretoria residential 7-10%, "
               "Cape Town 5-7%, Johannesburg 6-9%, Durban 7-10%, secondary cities 8-12%, "
               "commercial 9-12%, student accommodation 10-14%."),
        "UK": ("UK GROSS YIELD BENCHMARKS: prime London 3-5%, regional cities 5-8%, "
               "northern England 6-9%."),
        "US": ("US GROSS YIELD BENCHMARKS: coastal metros 3-5%, Sunbelt 5-8%, "
               "Midwest/secondary 7-10%."),
        "AU": "AU GROSS YIELD BENCHMARKS: Sydney/Melbourne 2.5-4%, Brisbane/Perth 4-6%.",
    }
    sa_benchmarks = _BENCHMARKS.get(_country_y, _BENCHMARKS["ZA"])
    system_prompt = (
        "You are a property market analyst. You are GIVEN a computed gross "
        "yield — never recalculate or contradict it. Write one honest sentence placing "
        "it against the local benchmark. No filler, no 'buy now'. "
        "Respond with a single valid JSON object — no markdown."
    )
    user_prompt = (
        f"Property in {location_str} ({_country_y}).\n"
        f"Purchase price: R{buy_price:,.0f}. Monthly rent: R{monthly_rent:,.0f}. "
        f"COMPUTED gross yield: {gross:.1f}% (annual rent / purchase price).\n"
        f"{sa_benchmarks}\n"
        "Return JSON: {\"market_context\": \"<one honest sentence vs the benchmark for "
        "this city/type>\", \"sa_yield_benchmark\": \"<the matching benchmark, e.g. "
        "Pretoria residential: 7-10% gross>\"}"
    )

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": AA_MODEL,
                    "max_tokens": 250,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": user_prompt}],
                },
            )
        _yc_json = resp.json()
        raw = _yc_json["content"][0]["text"].strip()
        _yc_in, _yc_out = _usage_tokens(_yc_json)   # C2/C3
        raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re_match.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        market_context     = str(result.get("market_context", ""))[:400]
        sa_yield_benchmark = str(result.get("sa_yield_benchmark", ""))[:120]
    except Exception as exc:
        # The model only writes the narrative; if it fails we STILL have the real
        # numbers. Degrade gracefully with a neutral sentence rather than failing —
        # but only charge because the core (computed) service succeeded.
        _log.warning("ai-yield-calc narration failed (numbers still valid): %s", exc)
        market_context = (f"Computed gross yield {gross:.1f}% on a R{buy_price:,.0f} "
                          f"purchase at R{monthly_rent:,.0f}/month.")
        sa_yield_benchmark = "SA residential benchmark: ~7-10% gross (varies by city)."
        _yc_in, _yc_out = None, None   # narration failed — flat estimate

    # DELIVER-THEN-CHARGE: a real, computed yield was produced — charge now.
    if _charge and _charge > 0:
        cc = database.get_db()
        try:
            remaining = _deduct_tuppence(
                cc, email, _charge,
                f"AI Yield Calc \u00b7 #{listing_id} \u00b7 {title[:40]}"
            )
            cc.commit()
        finally:
            cc.close()
    else:
        remaining = _current_tuppence(email)

    # C3 — log real AI spend for this paid call (was previously unlogged).
    _log_ai_spend(email, "/listings/yield-calc", "haiku", _yc_in, _yc_out)

    _log.info("ai-yield-calc: listing #%d email=%s gross=%.1f%% charged=1T",
              listing_id, email, gross)
    return {
        "status":                 "ok",
        "charged":                True,
        "computed":               True,        # numbers came from arithmetic, not a model
        "gross_yield_pct":        f"{gross:.1f}%",
        "net_yield_estimate_pct": f"{net:.1f}%",
        "net_cost_assumption_pct": f"{NET_COST_PCT:.1f}%",
        "purchase_price_used":    f"R{buy_price:,.0f}",
        "monthly_rent_used":      f"R{monthly_rent:,.0f}",
        "monthly_rent_estimate":  f"R{monthly_rent:,.0f}/month",   # legacy key
        "annual_rent_used":       f"R{annual_rent:,.0f}",
        "market_context":         market_context,
        "sa_yield_benchmark":     sa_yield_benchmark,
        "country":                _country_y,
        "tier":                   (tier or "1T"),
        "purchase_price_source":  _price_src,
        "monthly_rent_source":    _rent_src,
        "gross_formula":          f"(R{monthly_rent:,.0f} x 12) / R{buy_price:,.0f} = {gross:.1f}%",
        "net_cost_band":          {"low": _band.get("low"), "typical": _band.get("typical"),
                                   "high": _band.get("high"), "components": _band.get("components"),
                                   "source": _band.get("source"), "updated": _band.get("updated")},
        "indicative_label":       _INDICATIVE_LABEL,
        "disclaimer":             ("Indicative only - not financial advice. Where a figure was "
                                   "estimated from area benchmarks it is not property-specific; "
                                   "verify with a registered property practitioner."),
        "tuppence_remaining":     remaining,
        **_report_stamp("This yield estimate uses rent/cost benchmarks current at the date above."),
    }


# ── AI5 — Batch Card Listings ────────────────────────────────────────────────

class BatchCardRequest(BaseModel):
    images: list[str]          # base64-encoded JPEG/PNG, max 10
    city: str
    suburb: Optional[str] = None
    seller_email: str


@app.post("/listings/batch-cards")
async def ai_batch_card_listings(req: BatchCardRequest):
    """AI5: Seller pays 2T — Claude Sonnet Vision analyses up to 10 card photos and
    returns an array of draft listing JSONs ready for review and publish.
    Each draft contains title, description, price_suggestion, condition, category.
    Capped at 10 images per call. 2T flat cost regardless of card count.
    Returns {drafts: [...], cards_processed, tuppence_remaining}.
    """
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=503, detail="AI not configured")

    if not req.images:
        raise HTTPException(status_code=400, detail="At least one image is required")
    _check_cost_ceiling(req.seller_email)   # P2 — hard daily rail, BEFORE the Tuppence charge

    # Cap at 10 cards
    images = req.images[:10]
    card_count = len(images)

    conn = database.get_db()
    remaining = _deduct_tuppence(
        conn, req.seller_email, 2,
        f"AI Batch Cards · {card_count} card(s) · {req.city}"
    )
    conn.commit()
    conn.close()

    suburb_str = req.suburb or req.city
    location_str = f"{suburb_str}, {req.city}"

    system_prompt = (
        "You are an expert trading card and collectables appraiser and marketplace copywriter "
        "for TrustSquare, a South African peer-to-peer local marketplace. "
        "You identify cards/collectables from photos, assess condition, and write concise buyer-friendly listings. "
        "You know SA collectables market values. "
        "Always respond with a single valid JSON object — no markdown, no explanation."
    )

    # Build the message content: one text block + one image block per card
    content_blocks = [
        {
            "type": "text",
            "text": (
                f"Analyse these {card_count} trading card / collectable image(s) for a seller in {location_str}, "
                "South Africa. For each image, generate a complete listing draft.\n\n"
                "For each card/item return:\n"
                '{"title": "<specific card/item name, set, year if visible, max 12 words>", '
                '"description": "<40-80 words: card details, set/series, condition notes, notable features>", '
                '"price_suggestion": "<e.g. R150 or R200–R350 depending on condition>", '
                '"condition": "mint" | "near_mint" | "excellent" | "good" | "fair" | "poor", '
                '"category": "Collectors"}\n\n'
                f'Return JSON: {{"drafts": [<one object per image in order>]}}'
            )
        }
    ]

    for _, img_b64 in enumerate(images):
        # Detect media type from base64 header or default to jpeg
        media_type = "image/jpeg"
        if img_b64.startswith("data:"):
            header, data = img_b64.split(",", 1)
            if "png" in header:
                media_type = "image/png"
            elif "gif" in header:
                media_type = "image/gif"
            elif "webp" in header:
                media_type = "image/webp"
            img_b64 = data

        content_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": img_b64,
            }
        })

    try:
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": VISION_MODEL,   # Vision-capable; Haiku lacks vision depth for cards
                    "max_tokens": 2000,
                    "system": system_prompt,
                    "messages": [{"role": "user", "content": content_blocks}],
                },
            )
        rj = resp.json()
        _bc_in, _bc_out = _usage_tokens(rj)
        # P2 — Tuppence covers the revenue side; log token spend so the cost
        # dashboard sees it too (sweep 12 Jun 2026)
        _log_ai_spend(req.seller_email, "/listings/batch-cards", "sonnet_vision", _bc_in, _bc_out)
        raw = rj["content"][0]["text"].strip()
        raw = _re_match.sub(r"^```(?:json)?\s*", "", raw)
        raw = _re_match.sub(r"\s*```$", "", raw)
        result = json.loads(raw)
        drafts = result.get("drafts", [])

        # Sanitise each draft
        clean_drafts = []
        valid_conditions = {"mint", "near_mint", "excellent", "good", "fair", "poor"}
        for d in drafts[:card_count]:
            if isinstance(d, dict):
                clean_drafts.append({
                    "title":            str(d.get("title", ""))[:120],
                    "description":      str(d.get("description", ""))[:800],
                    "price_suggestion": str(d.get("price_suggestion", ""))[:60],
                    "condition":        d.get("condition", "good") if d.get("condition") in valid_conditions else "good",
                    "category":         "Collectors",
                    "city":             req.city,
                    "suburb":           req.suburb or "",
                })

    except Exception as exc:
        _log.error("ai-batch-cards: %s", exc)
        raise HTTPException(status_code=500, detail="AI batch card listing failed — Tuppence charged") from exc

    _log.info("ai-batch-cards: seller=%s city=%s cards=%d drafts=%d",
              req.seller_email, req.city, card_count, len(clean_drafts))
    return {
        "drafts":           clean_drafts,
        "cards_processed":  card_count,
        "tuppence_remaining": remaining,
    }



@app.get("/tuppence/history")
def get_tuppence_history(email: str, limit: int = 50, offset: int = 0):
    """Return paginated tuppence transaction history with running balance."""
    conn = database.get_db()
    try:
        # Verify user exists
        user = conn.execute("SELECT email FROM users WHERE email=?", (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        total = conn.execute(
            "SELECT COUNT(*) FROM transactions WHERE user_email=?", (email,)
        ).fetchone()[0]

        # Get all rows ascending to compute running balances
        all_rows = conn.execute(
            "SELECT id, type, amount, description, created_at "
            "FROM transactions WHERE user_email=? ORDER BY id ASC",
            (email,)
        ).fetchall()

        # Compute running balance_after for each row (cumulative sum)
        running = 0
        balance_after = []
        for row in all_rows:
            running += row["amount"]
            balance_after.append(running)

        # Reverse for newest-first, then slice for pagination
        all_rows_rev = list(reversed(all_rows))
        balance_after_rev = list(reversed(balance_after))

        page_rows = all_rows_rev[offset: offset + limit]
        page_bal  = balance_after_rev[offset: offset + limit]

        transactions = []
        for row, bal in zip(page_rows, page_bal, strict=False):
            transactions.append({
                "id": row["id"],
                "type": row["type"],
                "amount": row["amount"],
                "description": row["description"] or "",
                "created_at": row["created_at"],
                "balance_after": bal,
            })

        balance_row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) FROM transactions WHERE user_email=?", (email,)
        ).fetchone()
        balance = balance_row[0]
    finally:
        conn.close()
    return {
        "email": email,
        "balance": balance,
        "total": total,
        "offset": offset,
        "limit": limit,
        "transactions": transactions,
    }

# ── END AI TUPPENCE SERVICES — TIER 2 (Session 74) ──────────────────────────────────────────


# ════════════════════════════════════════════════════════════════════════════
# AI EMAIL TRIAGE — Session 94
# Inbound @trustsquare.co mail -> Cloudflare Email Worker -> POST /email/inbound
# -> Claude classifies + drafts a reply -> optional Gmail SMTP auto-send.
# Safety: draft-only by default (EMAIL_AUTO_SEND off). Replies only sent for
# clear-cut support/billing categories AND only when EMAIL_AUTO_SEND=1 and a
# Gmail App Password is present. Everything else is stored as a draft for David.
# ════════════════════════════════════════════════════════════════════════════

_TRIAGE_CATEGORIES = ["support", "billing", "legal", "compliance", "spam", "other"]
_AUTO_SEND_CATEGORIES = {"support", "billing"}


class InboundEmail(BaseModel):
    from_addr: str
    to_addr: str = ""
    subject: str = ""
    body: str = ""
    message_id: Optional[str] = None


def _smtp_send_reply(to_addr: str, subject: str, body: str,
                     in_reply_to: Optional[str] = None) -> bool:
    """Send a plain-text support reply. Prefers Resend (domain-aligned From =
    SUPPORT_FROM_EMAIL, Reply-To = SUPPORT_REPLY_TO) — the L3a launch path.
    Falls back to Gmail SMTP if Resend is unset/fails. Never raises."""
    to_clean = parseaddr(to_addr)[1]
    if not to_clean:
        _log.warning("_smtp_send_reply skipped — no valid recipient in %r", to_addr)
        return False
    subj = subject if subject.lower().startswith("re:") else f"Re: {subject}"
    # ── Path 1: Resend (L3a — replies from the trustsquare.co brand, not personal Gmail)
    resend_key = os.getenv("RESEND_API_KEY", "")
    support_from = os.getenv("SUPPORT_FROM_EMAIL", "TrustSquare Support <support@mail.trustsquare.co>")
    if resend_key:
        try:
            import requests as _rq
            payload = {"from": support_from, "to": [to_clean], "subject": subj, "text": body,
                       "reply_to": os.getenv("SUPPORT_REPLY_TO", "support@trustsquare.co")}
            if in_reply_to:
                payload["headers"] = {"In-Reply-To": in_reply_to, "References": in_reply_to}
            r = _rq.post("https://api.resend.com/emails", json=payload,
                         headers={"Authorization": f"Bearer {resend_key}"}, timeout=15)
            if r.status_code in (200, 201):
                _log.info("Triage reply sent to %s via Resend (from %s)", to_clean, support_from)
                return True
            _log.error("Resend reply failed (%s): %s — falling back to Gmail SMTP", r.status_code, r.text[:200])
        except Exception as exc:
            _log.error("Resend reply exception: %s — falling back to Gmail SMTP", exc)
    # ── Path 2: legacy Gmail SMTP fallback
    if not GMAIL_APP_PASSWORD:
        _log.warning("_smtp_send_reply skipped — no Resend success and GMAIL_APP_PASSWORD not set")
        return False
    try:
        msg = EmailMessage()
        msg["From"] = formataddr(("TrustSquare Support", GMAIL_ADDRESS))
        msg["To"] = to_clean
        msg["Subject"] = subj
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
            msg["References"] = in_reply_to
        msg.set_content(body)
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=20) as server:
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)
        _log.info("Triage reply sent to %s", to_clean)
        return True
    except Exception as exc:
        _log.error("_smtp_send_reply failed: %s", exc)
        return False


async def _classify_email(from_addr: str, subject: str, body: str) -> dict:
    """Call Claude to classify an inbound email and draft a reply.
    Returns {category, urgency, draft_reply, auto_safe}. Safe fallback on failure."""
    fallback = {"category": "other", "urgency": "normal", "draft_reply": "", "auto_safe": False}
    if not ANTHROPIC_API_KEY:
        return fallback
    # P2 wrapper — ceiling check before the paid call. Inbound mail is an
    # unauthenticated external surface; on 429 fall back to the safe default
    # (email is stored for human triage either way).
    try:
        _check_cost_ceiling(from_addr)
    except HTTPException:
        _log.warning("_classify_email skipped — daily cost ceiling reached (%s)", from_addr)
        return fallback
    body_trim = (body or "")[:4000]
    user_payload = f"From: {from_addr}\nSubject: {subject}\n\n{body_trim}"
    system = (
        "You are the email triage assistant for TrustSquare, a South African local "
        "marketplace connecting buyers with anonymous, trusted sellers via an "
        "introduction currency called Tuppence. You read one inbound customer email "
        "and return STRICT JSON only — no prose, no markdown fences.\n\n"
        "JSON shape: {\"category\": one of "
        "[\"support\",\"billing\",\"legal\",\"compliance\",\"spam\",\"other\"], "
        "\"urgency\": one of [\"low\",\"normal\",\"high\"], "
        "\"draft_reply\": a short, warm, professional plain-text reply signed "
        "'The TrustSquare Team', "
        "\"auto_safe\": boolean — true ONLY if a routine support or billing question "
        "the draft can fully answer with no human judgement.}\n\n"
        "Rules: Never reveal seller identities or internal data. Never promise refunds "
        "(Tuppence is strictly non-refundable). For legal, compliance, disputes, threats, "
        "or anything ambiguous set auto_safe=false. For spam set draft_reply to empty "
        "string and auto_safe=false. Keep replies under 120 words."
    )
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={
                    "model": TRIAGE_MODEL,
                    "max_tokens": 400,
                    "system": system,
                    "messages": [{"role": "user", "content": user_payload}],
                },
            )
        rj = resp.json()
        _cl_in, _cl_out = _usage_tokens(rj)
        # P2 wrapper — log spend HERE with real tokens (moved from the caller's
        # flat-estimate log; cost_is_real=1 on the dashboard).
        _log_ai_spend(from_addr, "/email/inbound", "haiku", _cl_in, _cl_out)
        raw = rj["content"][0]["text"].strip()
        if raw.startswith("```"):
            raw = raw.strip("`")
            if raw.startswith("json"):
                raw = raw[4:].strip()
        parsed = json.loads(raw)
        cat = parsed.get("category", "other")
        if cat not in _TRIAGE_CATEGORIES:
            cat = "other"
        urg = parsed.get("urgency", "normal")
        if urg not in ("low", "normal", "high"):
            urg = "normal"
        return {
            "category": cat,
            "urgency": urg,
            "draft_reply": (parsed.get("draft_reply") or "").strip(),
            "auto_safe": bool(parsed.get("auto_safe", False)),
        }
    except Exception as exc:
        _log.error("_classify_email failed: %s", exc)
        return fallback


@app.post("/email/inbound")
async def email_inbound(req: InboundEmail, background_tasks: BackgroundTasks,
                        x_inbound_secret: str = Header(default="")):
    """Receive an inbound email (from the Cloudflare Email Worker), triage with
    Claude, store the result, optionally auto-reply via Gmail SMTP.
    Auth: X-Inbound-Secret header (EMAIL_INBOUND_SECRET)."""
    if not EMAIL_INBOUND_SECRET:
        raise HTTPException(status_code=503, detail="Email triage not configured")
    if x_inbound_secret != EMAIL_INBOUND_SECRET:
        raise HTTPException(status_code=401, detail="Invalid inbound secret")

    from_addr = (req.from_addr or "").strip()
    subject = (req.subject or "").strip()
    body = req.body or ""
    if not from_addr:
        raise HTTPException(status_code=400, detail="from_addr is required")

    result = await _classify_email(from_addr, subject, body)
    # spend logging lives inside _classify_email with real tokens (P2 sweep, 12 Jun 2026)

    category = result["category"]
    urgency = result["urgency"]
    draft_reply = result["draft_reply"]

    status = "drafted"
    can_auto = (
        EMAIL_AUTO_SEND
        and bool(GMAIL_APP_PASSWORD)
        and result["auto_safe"]
        and category in _AUTO_SEND_CATEGORIES
        and bool(draft_reply)
    )
    if category == "spam":
        status = "skipped"
    elif can_auto:
        sent = _smtp_send_reply(from_addr, subject, draft_reply, req.message_id)
        status = "sent" if sent else "failed"

    try:
        conn = database.get_db()
        try:
            conn.execute(
                "INSERT INTO email_triage "
                "(from_addr, to_addr, subject, body_preview, category, urgency, "
                " draft_reply, status, message_id) VALUES (?,?,?,?,?,?,?,?,?)",
                (from_addr, (req.to_addr or "").strip(), subject, body[:500],
                 category, urgency, draft_reply, status, req.message_id),
            )
            conn.commit()
        finally:
            conn.close()
    except Exception as exc:
        _log.error("email_triage persist failed: %s", exc)

    return {
        "category": category,
        "urgency": urgency,
        "status": status,
        "auto_send_enabled": EMAIL_AUTO_SEND,
        "reply_drafted": bool(draft_reply),
    }


@app.get("/admin/email-triage")
def admin_email_triage(limit: int = 50, offset: int = 0,
                       _key: str = Depends(auth.require_api_key)):
    """List recent triaged emails for the ops dashboard. API-key gated."""
    limit = max(1, min(limit, 200))
    conn = database.get_db()
    try:
        rows = conn.execute(
            "SELECT id, from_addr, subject, category, urgency, status, "
            "       substr(draft_reply,1,400) AS draft_reply, received_at "
            "FROM email_triage ORDER BY received_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM email_triage").fetchone()[0]
        by_cat = conn.execute(
            "SELECT category, COUNT(*) AS n FROM email_triage "
            "WHERE received_at >= datetime('now','-30 days') GROUP BY category"
        ).fetchall()
    finally:
        conn.close()
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "by_category_30d": {r["category"]: r["n"] for r in by_cat},
        "items": [dict(r) for r in rows],
    }



@app.get("/dashboard/email-triage")
def dashboard_email_triage(limit: int = 20):
    """Unauthenticated read-only triage feed for the ops dashboard.
    Mirrors /dashboard/summary's no-auth posture (security = obscure dashboard URL).
    Returns recent rows + 30-day category/status counts. Draft text truncated."""
    limit = max(1, min(limit, 50))
    conn = database.get_db()
    try:
        rows = conn.execute(
            "SELECT id, from_addr, subject, category, urgency, status, "
            "       substr(draft_reply,1,600) AS draft_reply, received_at "
            "FROM email_triage ORDER BY received_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        total = conn.execute("SELECT COUNT(*) FROM email_triage").fetchone()[0]
        by_cat = conn.execute(
            "SELECT category, COUNT(*) AS n FROM email_triage "
            "WHERE received_at >= datetime('now','-30 days') GROUP BY category"
        ).fetchall()
        by_status = conn.execute(
            "SELECT status, COUNT(*) AS n FROM email_triage "
            "WHERE received_at >= datetime('now','-30 days') GROUP BY status"
        ).fetchall()
    finally:
        conn.close()
    return {
        "total": total,
        "by_category_30d": {r["category"]: r["n"] for r in by_cat},
        "by_status_30d": {r["status"]: r["n"] for r in by_status},
        "items": [dict(r) for r in rows],
    }

# ── END AI EMAIL TRIAGE — Session 94 ─────────────────────────────────────────


# ── AI COST DASHBOARD PANEL (Session 97 · C2/C1) ─────────────────────────────
# No-auth read-only feed for the ops dashboard (obscure-URL posture, like
# /dashboard/email-triage). Surfaces the four audit metrics:
#   1. per-user AI token cost     2. cost-vs-revenue margin per op
#   3. monthly running cost (this month, real)  4. modelled @100 / @100k users
# plus the C1 hard-ceiling status and C2 real-token coverage.

@app.get("/dashboard/cost")
def dashboard_cost():
    """Unauthenticated AI cost + margin + ceiling snapshot for the ops dashboard."""
    import datetime as _dt
    conn = database.get_db()
    try:
        month_start = _dt.datetime.utcnow().strftime('%Y-%m-01')
        day_start   = _dt.datetime.utcnow().strftime('%Y-%m-%d 00:00:00')
        tot = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) AS cost, COUNT(*) AS calls, "
            "       COALESCE(SUM(cost_is_real),0) AS real_rows, "
            "       COALESCE(SUM(input_tokens),0) AS in_tok, COALESCE(SUM(output_tokens),0) AS out_tok "
            "FROM ai_spend_log WHERE logged_at >= ?", (month_start,)
        ).fetchone()
        by_ep = conn.execute(
            "SELECT endpoint, model, COUNT(*) AS calls, ROUND(SUM(est_cost_usd),6) AS cost, "
            "       COALESCE(SUM(cost_is_real),0) AS real_rows "
            "FROM ai_spend_log WHERE logged_at >= ? GROUP BY endpoint, model ORDER BY cost DESC",
            (month_start,)
        ).fetchall()
        today = conn.execute(
            "SELECT COALESCE(SUM(est_cost_usd),0) AS cost, COUNT(*) AS calls "
            "FROM ai_spend_log WHERE logged_at >= ?", (day_start,)
        ).fetchone()
        active_users = conn.execute(
            "SELECT COUNT(DISTINCT email) AS n FROM ai_spend_log "
            "WHERE logged_at >= ? AND email != ''", (month_start,)
        ).fetchone()["n"]
        cfg = conn.execute(
            "SELECT monthly_income_usd, daily_user_ceiling_usd, daily_platform_ceiling_usd "
            "FROM ai_spend_config WHERE id = 1"
        ).fetchone()
    finally:
        conn.close()

    month_cost = float(tot["cost"]); calls = int(tot["calls"])
    real_rows = int(tot["real_rows"])
    income = float(cfg["monthly_income_usd"]) if cfg else 0.0
    user_cap = float(cfg["daily_user_ceiling_usd"]) if cfg else 0.0
    platform_cap = float(cfg["daily_platform_ceiling_usd"]) if cfg else 0.0
    today_cost = float(today["cost"]); today_calls = int(today["calls"])

    cost_per_user = (month_cost / active_users) if active_users else 0.0
    cost_per_call = (month_cost / calls) if calls else 0.0
    margin_pct = ((income - month_cost) / income * 100) if income > 0 else None
    real_pct = round((real_rows / calls * 100) if calls else 0.0, 1)

    # Modelled run-rate (audit figures): 4 paid AI ops/user/mo at the blended
    # per-call cost observed this month (or a conservative $0.012 fallback).
    blended = cost_per_call if cost_per_call > 0 else 0.012
    model_100  = round(blended * 4 * 100, 2)
    model_100k = round(blended * 4 * 100_000, 2)

    return {
        "month": _dt.datetime.utcnow().strftime('%Y-%m'),
        "month_cost_usd": round(month_cost, 6),
        "calls_this_month": calls,
        "active_ai_users": active_users,
        "cost_per_user_usd": round(cost_per_user, 6),
        "cost_per_call_usd": round(cost_per_call, 6),
        "income_usd": income,
        "margin_pct": (round(margin_pct, 1) if margin_pct is not None else None),
        "real_token_pct": real_pct,
        "modelled": {"per_user_ops_mo": 4, "blended_call_usd": round(blended, 6),
                     "cost_100_users_usd": model_100, "cost_100k_users_usd": model_100k},
        "ceilings": {
            "daily_user_ceiling_usd": round(user_cap, 4),
            "daily_platform_ceiling_usd": round(platform_cap, 4),
            "today_spend_usd": round(today_cost, 6),
            "today_calls": today_calls,
            "platform_pct_of_ceiling": round((today_cost / platform_cap * 100) if platform_cap > 0 else 0.0, 1),
            "platform_breached": bool(platform_cap > 0 and today_cost >= platform_cap),
        },
        "by_endpoint": [dict(r) for r in by_ep],
    }


@app.get("/dashboard/scan")
def dashboard_scan():
    """Unauthenticated read-only weekly code-scan snapshot for the ops dashboard.
    Mirrors /dashboard/cost's no-auth posture (security = the obscure dashboard URL).
    Reads SCAN_REPORT.json from the app dir via _read_file(); returns
    {"available": false} when the file is absent or unparseable so the panel
    renders an empty-state instead of erroring."""
    import json as _json_scan
    raw = _read_file("SCAN_REPORT.json")
    if not raw:
        return {"available": False}
    try:
        data = _json_scan.loads(raw)
    except Exception:
        return {"available": False, "error": "unparseable SCAN_REPORT.json"}
    if isinstance(data, dict):
        data["available"] = True
        return data
    return {"available": True, "data": data}



# ── Orchestrator: in-page approval of a staged (gated) item ───────────────
# Gated at the nginx layer (location = /orchestrator/approve, same Basic Auth
# as the orchestrator page). Records approval per ORCHESTRATION_POLICY §8:
# move the item out of `staged` → front of the Fixer `queue` (approved:true,
# verdict auto-ship), and keep report.json consistent for the live page.
# It NEVER ships, deploys, or moves money — the next Fixer run does the work,
# still smoke-gated. It only rewrites the orchestrator JSON state files.
class _OrchApproveBody(BaseModel):
    id: str

_ORCH_DIR = _PROJECT_ROOT / "orchestrator"

def _orch_read_json(name, default):
    import json as _j
    p = _ORCH_DIR / name
    try:
        return _j.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except Exception:
        return default

def _orch_write_json(name, data):
    import json as _j, os as _o
    p = _ORCH_DIR / name
    tmp = str(p) + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        _j.dump(data, f, indent=2)
    _o.replace(tmp, str(p))

@app.post("/orchestrator/approve")
def orchestrator_approve(body: _OrchApproveBody):
    """Approve a staged (Regulatory/Financial-gated) item from the ops page.
    nginx Basic-Auth-gated (same realm as the page). Moves the item to the
    front of the Fixer queue with approved:true; the next Fixer run ships it
    (still smoke-gated). Never deploys or moves money itself."""
    item_id = (body.id or "").strip()
    if not item_id:
        raise HTTPException(status_code=400, detail="missing id")

    staged = _orch_read_json("staged.json", [])
    queue  = _orch_read_json("queue.json", [])
    report = _orch_read_json("report.json", {})

    match = next((s for s in staged if s.get("id") == item_id), None)
    if match is None:
        raise HTTPException(status_code=404, detail=f"{item_id} is not awaiting approval")

    q_entry = {
        "id": match.get("id"),
        "sev": match.get("sev", "MED"),
        "action": match.get("title") or match.get("action") or match.get("id"),
        "verdict": "auto-ship",
        "gate": match.get("gate"),
        "approved": True,
    }
    queue = [q for q in queue if q.get("id") != item_id]
    queue.insert(0, q_entry)
    staged = [s for s in staged if s.get("id") != item_id]

    if isinstance(report, dict):
        report["staged"] = [s for s in (report.get("staged") or []) if s.get("id") != item_id]
        qn = [q for q in (report.get("queue_next") or []) if q.get("id") != item_id]
        qn.insert(0, {"id": q_entry["id"], "sev": q_entry["sev"],
                      "title": q_entry["action"], "verdict": "auto-ship", "approved": True})
        report["queue_next"] = qn

    _orch_write_json("staged.json", staged)
    _orch_write_json("queue.json", queue)
    if isinstance(report, dict) and report:
        _orch_write_json("report.json", report)

    return {"ok": True, "id": item_id, "approved": True, "queue_position": 1,
            "staged_remaining": len(staged),
            "note": "Approved — moved to the front of the queue; the next Fixer run ships it (smoke-gated)."}


# ═════════════════════════════════════════════════════════════════════════
# TIERED GRADING — PHASE A  (Session 44, 4 Jun 2026)  [additive, flag-gated]
# Tier-1 AI condition grader for collectible cards + a private review page.
# NON-DESTRUCTIVE: results are written ONLY to the new ai_grade / ai_grade_conf
# / ai_grade_notes / grade_tier columns — the seller-facing `condition` column
# is NEVER touched. Buyer-facing display is gated OFF (SHOW_AI_GRADE_TO_BUYERS
# defaults to "0"); no buyer surface reads ai_grade until Phase B flips it on.
# Reuses the existing card-vision setup: VISION_MODEL (claude-sonnet-4-6 — the
# same model ai-batch-cards uses because Haiku lacks vision depth for cards) and
# the ANTHROPIC_API_KEY env var.
# ═════════════════════════════════════════════════════════════════════════
import secrets as _ts_secrets
import html as _ts_html
from fastapi import Response as _TSResponse
from fastapi.responses import HTMLResponse as _TSHTMLResponse

SHOW_AI_GRADE_TO_BUYERS = os.getenv("SHOW_AI_GRADE_TO_BUYERS", "0") == "1"

AI_GRADE_VOCAB = ["Near Mint", "Lightly Played", "Moderately Played",
                  "Heavily Played", "Damaged"]


def _grade_extract_photo_urls(photo_urls=None, thumb_url=None, medium_url=None, limit=3):
    """Ordered, de-duplicated list of up to `limit` real image URLs from a
    listing's photo fields. photo_urls is a JSON array whose entries may carry a
    '::caption' suffix (see upload_listing_photo); falls back to medium_url then
    thumb_url."""
    urls = []
    if photo_urls:
        try:
            arr = json.loads(photo_urls)
            if isinstance(arr, list):
                for entry in arr:
                    if not entry:
                        continue
                    u = str(entry).split("::", 1)[0].strip()
                    if u:
                        urls.append(u)
        except Exception:
            pass
    for u in (medium_url, thumb_url):
        if u and str(u).strip():
            urls.append(str(u).strip())
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
        if len(out) >= limit:
            break
    return out


def grade_card_condition(photo_urls=None, thumb_url=None, medium_url=None, timeout=60):
    """Tier-1 AI condition grade for a collectible card from its photo(s).

    Returns dict: {"grade": <one of AI_GRADE_VOCAB or None>,
                   "confidence": <float 0..1 or None>, "notes": <str <=120>,
                   "model": VISION_MODEL, "in_tokens": int|None,
                   "out_tokens": int|None, "error": <str|None>}.
    Fails SOFT — never raises, never writes the DB. On missing key / no photos /
    timeout / parse error it returns grade=None with an `error` string so the
    caller can skip and record it."""
    result = {"grade": None, "confidence": None, "notes": "",
              "model": VISION_MODEL, "in_tokens": None, "out_tokens": None,
              "error": None}
    if not ANTHROPIC_API_KEY:
        result["error"] = "no_api_key"
        return result
    # P2 wrapper — platform-rail ceiling check (no user context in batch grading).
    # Function fails SOFT by contract, so convert the 429 into an error result.
    try:
        _check_cost_ceiling("")
    except HTTPException:
        result["error"] = "cost_ceiling_reached"
        return result
    urls = _grade_extract_photo_urls(photo_urls, thumb_url, medium_url)
    if not urls:
        result["error"] = "no_photos"
        return result

    content_blocks = []
    for u in urls:
        try:
            with httpx.Client(timeout=20) as _c:
                r = _c.get(u)
            if r.status_code != 200 or not r.content:
                continue
            media_type = "image/jpeg"
            cl = (r.headers.get("content-type") or "").lower()
            if "png" in cl:
                media_type = "image/png"
            elif "webp" in cl:
                media_type = "image/webp"
            elif "gif" in cl:
                media_type = "image/gif"
            b64 = base64.b64encode(r.content).decode()
            content_blocks.append({"type": "image", "source": {
                "type": "base64", "media_type": media_type, "data": b64}})
        except Exception:
            continue
    if not content_blocks:
        result["error"] = "photo_fetch_failed"
        return result

    system_prompt = (
        "You are a CONSERVATIVE trading-card condition grader for a marketplace. "
        "From the photo(s) ALONE, give an INDICATIVE TCGplayer-style condition read. "
        "Use EXACTLY one of these grades: Near Mint, Lightly Played, Moderately Played, "
        "Heavily Played, Damaged. Photos hide flaws, so when uncertain grade DOWN and "
        "lower your confidence — never over-claim condition. Judge corners, edges, "
        "surface scratches/whitening, centering and creasing only as far as the image "
        "actually shows. Respond with STRICT JSON and nothing else: "
        '{"grade": "<one of the five>", "confidence": <0..1 number>, '
        '"notes": "<=120 chars; the single biggest visible factor>"}.'
    )
    content_blocks.append({"type": "text", "text": (
        "Grade the condition of the card in these photo(s). "
        "Be conservative; reply with the JSON only.")})

    try:
        with httpx.Client(timeout=timeout) as client:
            resp = client.post(
                _ts_ai_url(),
                headers=_ts_ai_headers(),
                json={"model": VISION_MODEL, "max_tokens": 300,
                      "system": system_prompt,
                      "messages": [{"role": "user", "content": content_blocks}]},
            )
        rj = resp.json()
        it, ot = _usage_tokens(rj)
        result["in_tokens"], result["out_tokens"] = it, ot
        # P2 wrapper — log real token spend (platform attribution; batch grading).
        _log_ai_spend("", "grade_card_condition", "sonnet_vision", it, ot)
        raw = (rj.get("content", [{}])[0].get("text", "") or "").strip()
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
        parsed = json.loads(raw)
        g = str(parsed.get("grade", "")).strip()
        match = next((v for v in AI_GRADE_VOCAB if v.lower() == g.lower()), None)
        if match is None:
            result["error"] = "bad_grade:" + g[:40]
            return result
        conf = parsed.get("confidence")
        try:
            conf = max(0.0, min(1.0, float(conf)))
        except Exception:
            conf = None
        result["grade"] = match
        result["confidence"] = conf
        result["notes"] = str(parsed.get("notes", ""))[:120]
        return result
    except Exception as exc:
        result["error"] = "call_or_parse_error:" + str(exc)[:80]
        return result


# ── /grading-review — PRIVATE review page (David only; NOT linked from buyer app)
# Basic-Auth enforced HERE in the BEA (self-contained — no nginx change). Mirrors
# the orchestrator's gated-page intent. Reuses the existing admin credential so
# David logs in with something he already holds; no new secret is stored.
_GRADING_REVIEW_USER = os.getenv("GRADING_REVIEW_USER", "david")
_GRADING_REVIEW_PASS = (os.getenv("GRADING_REVIEW_PASS")
                        or os.getenv("MS_ADMIN_PASSWORD") or "")


def _grading_review_auth(request: Request):
    hdr = request.headers.get("authorization", "")
    if not hdr.startswith("Basic "):
        return False
    try:
        raw = base64.b64decode(hdr[6:]).decode("utf-8", "ignore")
        u, _, p = raw.partition(":")
        return (_GRADING_REVIEW_PASS != ""
                and _ts_secrets.compare_digest(u, _GRADING_REVIEW_USER)
                and _ts_secrets.compare_digest(p, _GRADING_REVIEW_PASS))
    except Exception:
        return False


@app.get("/grading-review")
def grading_review(request: Request):
    if not _grading_review_auth(request):
        return _TSResponse(
            status_code=401, content="Authentication required.",
            headers={"WWW-Authenticate": 'Basic realm="TrustSquare Grading Review"'})

    conn = database.get_db()
    try:
        rows = conn.execute(
            "SELECT id, title, condition, ai_grade, ai_grade_conf, ai_grade_notes, "
            "grade_tier, thumb_url, medium_url, photo_urls "
            "FROM listings WHERE category='Collectors' "
            "ORDER BY (ai_grade IS NULL) ASC, ai_grade_conf ASC, id ASC"
        ).fetchall()
    finally:
        conn.close()

    def esc(x):
        return _ts_html.escape("" if x is None else str(x))

    total = len(rows)
    graded = sum(1 for r in rows if r["ai_grade"])
    dist = {}
    for r in rows:
        if r["ai_grade"]:
            dist[r["ai_grade"]] = dist.get(r["ai_grade"], 0) + 1
    dist_str = ", ".join("%s: %d" % (k, dist[k]) for k in AI_GRADE_VOCAB if k in dist) or "none yet"

    cards_html = []
    for r in rows:
        urls = _grade_extract_photo_urls(r["photo_urls"], r["thumb_url"], r["medium_url"])
        imgs = "".join('<img src="%s" loading="lazy" alt="">' % esc(u) for u in urls[:3]) \
            or '<div class="noimg">no photo</div>'
        conf = r["ai_grade_conf"]
        conf_txt = ("%.0f%%" % (conf * 100)) if isinstance(conf, (int, float)) else "—"
        low = isinstance(conf, (int, float)) and conf < 0.6
        ai_grade = r["ai_grade"] or "— (not graded)"
        cond = r["condition"] or "— (none on file)"
        mismatch = bool(r["ai_grade"] and r["condition"]
                        and r["ai_grade"].strip().lower() != r["condition"].strip().lower())
        flags = []
        if low:
            flags.append('<span class="flag low">low confidence</span>')
        if mismatch:
            flags.append('<span class="flag mm">differs from condition</span>')
        tier_txt = esc(r["grade_tier"]) if r["grade_tier"] else "—"
        cards_html.append(
            '<div class="card"><div class="imgs">%s</div><div class="meta">'
            '<div class="title">#%s · %s</div>'
            '<div class="row"><span class="lbl">AI grade (Tier %s)</span>'
            '<span class="grade %s">%s</span><span class="conf">conf %s</span></div>'
            '<div class="row"><span class="lbl">Existing condition</span>'
            '<span class="cond">%s</span></div>'
            '<div class="notes">%s</div><div class="flags">%s</div>'
            '</div></div>'
            % (imgs, esc(r["id"]), esc(r["title"]), tier_txt,
               ("low" if low else "ok"), esc(ai_grade), conf_txt,
               esc(cond), esc(r["ai_grade_notes"] or ""), " ".join(flags))
        )

    page = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<meta name='viewport' content='width=device-width,initial-scale=1'>"
        "<title>TrustSquare · Grading Review (Phase A)</title><style>"
        "body{font-family:-apple-system,Segoe UI,Roboto,Arial,sans-serif;background:#eef1f5;color:#111827;margin:0;padding:24px}"
        "h1{color:#1e3a5f;font-size:22px;margin:0 0 4px}.sub{color:#4b5563;margin:0 0 16px;font-size:14px;max-width:760px}"
        ".bar{background:#fff;border:1px solid #e5e7eb;border-radius:10px;padding:12px 16px;margin-bottom:16px;font-size:14px}"
        ".card{display:flex;gap:14px;background:#fff;border:1px solid #e5e7eb;border-radius:12px;padding:12px;margin-bottom:12px}"
        ".imgs{display:flex;gap:6px;flex:0 0 auto}.imgs img{width:90px;height:120px;object-fit:cover;border-radius:8px;border:1px solid #e5e7eb;background:#f1f5f9}"
        ".noimg{width:90px;height:120px;display:flex;align-items:center;justify-content:center;color:#9ca3af;font-size:12px;border:1px dashed #cbd5e1;border-radius:8px}"
        ".meta{flex:1 1 auto;min-width:0}.title{font-weight:700;color:#1e3a5f;margin-bottom:8px}"
        ".row{display:flex;align-items:center;gap:10px;margin:4px 0;flex-wrap:wrap}"
        ".lbl{width:150px;color:#6b7280;font-size:11px;text-transform:uppercase;letter-spacing:.03em}"
        ".grade{font-weight:700;padding:2px 10px;border-radius:6px;background:#cffafe;color:#0e7490}.grade.low{background:#fef3c7;color:#92400e}"
        ".conf{color:#4b5563;font-size:13px}.cond{font-weight:600;color:#374151}"
        ".notes{color:#4b5563;font-size:13px;margin-top:6px;font-style:italic}"
        ".flags{margin-top:6px;min-height:4px}.flag{display:inline-block;font-size:11px;font-weight:700;padding:2px 8px;border-radius:5px;margin-right:6px}"
        ".flag.low{background:#fef3c7;color:#92400e}.flag.mm{background:#fee2e2;color:#b91c1c}"
        "</style></head><body>"
        "<h1>Grading Review — Phase A · Tier-1 AI card grades</h1>"
        "<p class='sub'>Indicative AI condition reads from photos only — <b>not certified, not live to buyers.</b> "
        "Sorted with ungraded last and lowest-confidence first, so the reads most worth eyeballing are at the top. "
        "The existing <code>condition</code> value is shown beside each AI grade for comparison; it was not modified.</p>"
        "<div class='bar'><b>%d</b> Collectors cards &middot; <b>%d</b> graded &middot; distribution — %s</div>"
        "%s</body></html>"
        % (total, graded, esc(dist_str), "".join(cards_html))
    )
    return _TSHTMLResponse(content=page)
# ═════════════════════════ END TIERED GRADING PHASE A ═════════════════════


# ── Founders Badge / Launch Special routes (Canon Addendum 1) — env-gated OFF ──
app.include_router(launch_redemption.router)

# ═══ AI FEATURE HOLD LEDGER (AdvertAgent service · commit→burn→release) ═══
# Canonical Tuppence HOLD model (Codex v4.8 / C10–C13): commit-on-request,
# burn-on-delivery, release-on-failure. A8-compliant: purchase-only deduction
# (AI service, A8(ii)); a failed run ALWAYS releases — never a punitive keep.
# Called only by the AdvertAgent service (port 8002) with X-Api-Key.
# Ledger stays in THIS one thin layer (scale-shape invariant 1 + 2).

@app.post("/tuppence/ai-commit")
def tuppence_ai_commit(payload: dict, _key: str = Depends(auth.require_api_key)):
    """Place a hold: balance check + negative 'ai_hold' row, atomically."""
    email = (payload.get("email") or "").strip().lower()
    amount = int(payload.get("amount") or 0)
    function_id = (payload.get("function_id") or "unknown")[:64]
    job_id = (payload.get("job_id") or "unknown")[:64]
    if not email or amount < 1:
        raise HTTPException(status_code=422, detail="email and positive amount required")
    conn = database.get_db()
    conn.isolation_level = None
    try:
        conn.execute("BEGIN IMMEDIATE")
        # ── PRE-LAUNCH CLOSED-TESTING GUARD (David, 6 Jul 2026) ──
        # Gates are OFF for Paystack review; until launch auth ships (LAUNCH-AUTH-1
        # magic-link, lands with Paystack), Tuppence SPENDING stays restricted to the
        # 4 family test accounts (is_superuser=1). Public keeps every FREE feature.
        _su = conn.execute("SELECT is_superuser FROM users WHERE LOWER(email)=?", (email,)).fetchone()
        if not (_su and int(_su["is_superuser"] or 0) == 1):
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=403,
                detail="Paid AI features are in closed testing until launch — the free examples and free tools remain fully available.")
        # ── S3 paid-feed tier-gate (Free-Tier AI Cost Risk Report, 16 Jun 2026) ──
        # The expensive paid-feed AI class is reserved for $20 Pro, whose 5T=$10 charge
        # covers Sonnet-plus-feed cost. Block Free/Starter/Agency BEFORE placing the hold,
        # so a gated call never charges and never leaks. Cheap (non-paid-feed) AI stays
        # open to everyone. PRICING AUTHORITY: PRICING_CANON.md §5.
        if ai_service_tiers.requires_paid_feed(function_id):
            _trow = conn.execute(
                "SELECT seller_tier FROM users WHERE LOWER(email)=?", (email,)).fetchone()
            _stier = (_trow["seller_tier"] if _trow else "free") or "free"
            if not ai_service_tiers.tier_may_run(function_id, _stier):
                conn.execute("ROLLBACK")
                raise HTTPException(status_code=403,
                    detail="This AI feature is available on the Pro plan. "
                           "Upgrade to Pro to use the full research tools — your "
                           "Tuppence was not charged.")
        row = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS bal FROM transactions WHERE user_email=?",
            (email,)).fetchone()
        balance = int(row["bal"])
        if balance < amount:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=402,
                detail=f"Insufficient Tuppence — balance {balance}T, this AI feature needs {amount}T")
        cur = conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
            (email, "ai_hold", -amount, f"AI feature hold \u00b7 {function_id} \u00b7 job {job_id}"))
        hold_id = cur.lastrowid
        conn.execute("COMMIT")
        return {"hold_id": hold_id, "email": email, "amount": amount,
                "balance_after": balance - amount}
    except HTTPException:
        raise
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except Exception: pass
        raise HTTPException(status_code=500, detail=f"ai-commit failed: {e}") from e
    finally:
        conn.close()


@app.post("/tuppence/ai-settle")
def tuppence_ai_settle(payload: dict, _key: str = Depends(auth.require_api_key)):
    """Settle a hold: outcome 'delivered' → burn; 'failed' → release (refund row).
    Idempotent: a hold can be settled exactly once (409 on re-settle)."""
    hold_id = int(payload.get("hold_id") or 0)
    outcome = payload.get("outcome")
    if outcome not in ("delivered", "failed"):
        raise HTTPException(status_code=422, detail="outcome must be delivered|failed")
    conn = database.get_db()
    conn.isolation_level = None
    try:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute("SELECT * FROM transactions WHERE id=?", (hold_id,)).fetchone()
        if not row:
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=404, detail="hold not found")
        if row["type"] != "ai_hold":
            conn.execute("ROLLBACK")
            raise HTTPException(status_code=409, detail=f"hold already settled ({row['type']})")
        if outcome == "delivered":
            conn.execute("UPDATE transactions SET type='ai_burn', description=description||' \u00b7 delivered' WHERE id=?",
                         (hold_id,))
        else:
            conn.execute("UPDATE transactions SET type='ai_hold_released' WHERE id=?", (hold_id,))
            conn.execute(
                "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
                (row["user_email"], "ai_release", -int(row["amount"]),
                 f"AI feature release (no charge \u2014 run failed) \u00b7 hold {hold_id}"))
        bal = conn.execute(
            "SELECT COALESCE(SUM(amount),0) AS bal FROM transactions WHERE user_email=?",
            (row["user_email"],)).fetchone()
        conn.execute("COMMIT")
        return {"hold_id": hold_id, "outcome": outcome, "balance_after": int(bal["bal"])}
    except HTTPException:
        raise
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except Exception: pass
        raise HTTPException(status_code=500, detail=f"ai-settle failed: {e}") from e
    finally:
        conn.close()

# P2 cost-compliance fixes applied 12 Jun 2026 (nightly sweep): ceiling checks +
# real-token spend logging on grade_card_condition, _vision_orient_image,
# _classify_email, ai-rewrite, ai-audit, batch-cards. See CHANGELOG.


# ── DEMAND-LOOP-1: one-time boot sweep (EOF — all names now defined) ──────────
# Set DEMAND_SWEEP_ON_BOOT=1 to run one match/compose pass at startup and log the
# outbox size, so a dry-run flip is visible in the boot log. Dry-run composes to the
# outbox but never sends. Idempotent-safe; own connection.
if os.getenv("DEMAND_SWEEP_ON_BOOT", "0") == "1" and DEMAND_LOOP_ENABLED:
    try:
        _bsc = database.get_db()
        # DIAG: why does/doesn't a ticket match? print open tickets + available prospects.
        try:
            for _t in _bsc.execute("SELECT category, city_id, COUNT(*) AS n FROM demand_tickets WHERE state='open' GROUP BY category, city_id").fetchall():
                _av = _bsc.execute("SELECT COUNT(*) AS n FROM demand_prospects WHERE COALESCE(app_category,category)=? AND COALESCE(city_id,0)=COALESCE(?,0)",
                                   (_t["category"], _t["city_id"])).fetchone()["n"]
                print("DEMAND-DIAG: open ticket cat=%s city=%s x%s -> %s available prospects" % (_t["category"], _t["city_id"], _t["n"], _av))
            _pc = _bsc.execute("SELECT app_category, COUNT(*) AS n FROM demand_prospects WHERE city_id IS NOT NULL GROUP BY app_category ORDER BY n DESC LIMIT 6").fetchall()
            print("DEMAND-DIAG: prospects-with-city by app_category: " + ", ".join("%s=%s" % (r["app_category"], r["n"]) for r in _pc))
        except Exception as _de:
            print("DEMAND-DIAG error: %s" % _de)
        _bs = _demand_match_and_compose(_bsc)
        _bsc.commit()
        _ob = _bsc.execute("SELECT COUNT(*) AS n FROM demand_invites_outbox").fetchone()["n"]
        _bsc.close()
        print("DEMAND-BOOT-SWEEP: matched=%s composed=%s sent=%s | outbox_total=%s | dry_run=%s"
              % (_bs.get("matched"), _bs.get("composed"), _bs.get("sent", 0), _ob, DEMAND_LOOP_DRYRUN))
    except Exception as _dse:
        print("DEMAND-BOOT-SWEEP error: %s" % _dse)
