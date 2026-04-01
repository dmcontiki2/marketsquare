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

    conn.commit()


def seed_suburbs(conn):
    """Seed suburbs table from suburbs_seed.json on first run."""
    count = conn.execute("SELECT COUNT(*) FROM suburbs").fetchone()[0]
    if count > 0:
        return
    seed_path = os.path.join(os.path.dirname(__file__), "suburbs_seed.json")
    if not os.path.exists(seed_path):
        return
    with open(seed_path) as f:
        suburbs = json.load(f)
    conn.executemany(
        "INSERT INTO suburbs (name, city, country) VALUES (?, ?, ?)",
        [(s["name"], s["city"], s["country"]) for s in suburbs]
    )
    conn.commit()


_startup_conn = database.get_db()
run_migrations(_startup_conn)
seed_suburbs(_startup_conn)
_startup_conn.close()

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
    # Services / Help Wanted fields
    service_type: Optional[str] = None
    availability: Optional[str] = None

class User(BaseModel):
    email: str
    name: Optional[str] = None

class IntroRequest(BaseModel):
    listing_id: int
    buyer_email: str
    message: Optional[str] = None

# ── HEALTH ───────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "MarketSquare BEA", "version": "1.1.0"}

# ── LISTINGS (public read, protected write) ──────────────────

@app.get("/listings")
def get_listings(city: str = "Pretoria", category: Optional[str] = None, suburb: Optional[str] = None):
    conn = database.get_db()
    clauses = ["city = ?"]
    params: list = [city]
    if category:
        clauses.append("category = ?")
        params.append(category)
    if suburb:
        clauses.append("suburb = ?")
        params.append(suburb)
    where = " AND ".join(clauses)
    rows = conn.execute(
        f"SELECT * FROM listings WHERE {where} ORDER BY created_at DESC LIMIT 50",
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
           (title, price, category, city, area, suburb, description, thumb_url, medium_url)
           VALUES (?,?,?,?,?,?,?,?,?)""",
        (listing.title, listing.price, listing.category, listing.city,
         listing.area, listing.suburb, listing.description, listing.thumb_url, listing.medium_url)
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

# ── SUBURBS & CITIES ─────────────────────────────────────────

@app.get("/suburbs")
def get_suburbs(city: str = "Pretoria"):
    conn = database.get_db()
    rows = conn.execute(
        "SELECT name FROM suburbs WHERE city = ? AND active = 1 ORDER BY name ASC",
        (city,)
    ).fetchall()
    conn.close()
    return [r["name"] for r in rows]

@app.get("/cities")
def get_cities(country: Optional[str] = None):
    conn = database.get_db()
    if country:
        rows = conn.execute(
            "SELECT DISTINCT city FROM suburbs WHERE country = ? AND active = 1 ORDER BY city ASC",
            (country,)
        ).fetchall()
        conn.close()
        return [r["city"] for r in rows]
    # Group by country
    rows = conn.execute(
        "SELECT DISTINCT city, country FROM suburbs WHERE active = 1 ORDER BY country, city ASC"
    ).fetchall()
    conn.close()
    grouped: dict = {}
    for r in rows:
        grouped.setdefault(r["country"], []).append(r["city"])
    return grouped

@app.post("/cities")
def add_city(
    city: str,
    country: str,
    background_tasks: BackgroundTasks,
    _key: str = Depends(auth.require_api_key)
):
    # Insert a placeholder row so the city appears immediately
    conn = database.get_db()
    existing = conn.execute(
        "SELECT id FROM suburbs WHERE city = ? AND country = ?", (city, country)
    ).fetchone()
    if not existing:
        conn.execute(
            "INSERT INTO suburbs (name, city, country) VALUES (?, ?, ?)",
            ("Central", city, country)
        )
        conn.commit()
    conn.close()
    background_tasks.add_task(_fetch_geonames_suburbs, city, country)
    return {"message": f"City '{city}' added. Fetching suburbs in background."}
    # FLAG: GEONAMES_USERNAME must be set in /var/www/marketsquare/.env


async def _fetch_geonames_suburbs(city: str, country: str):
    """Background task: fetch suburbs from GeoNames and seed the suburbs table."""
    username = os.getenv("GEONAMES_USERNAME")
    if not username:
        return  # Skip silently — no credentials configured
    url = f"http://api.geonames.org/searchJSON?q={city}&featureClass=P&country={country}&maxRows=100&username={username}"
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(url)
            data = resp.json()
        names = [g["name"] for g in data.get("geonames", []) if g.get("name")]
        if not names:
            return
        conn = database.get_db()
        for name in names:
            existing = conn.execute(
                "SELECT id FROM suburbs WHERE name = ? AND city = ? AND country = ?",
                (name, city, country)
            ).fetchone()
            if not existing:
                conn.execute(
                    "INSERT INTO suburbs (name, city, country) VALUES (?, ?, ?)",
                    (name, city, country)
                )
        conn.commit()
        conn.close()
    except Exception:
        pass  # Best-effort — failure is non-fatal


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
        "INSERT INTO intro_requests (listing_id, buyer_email, message) VALUES (?,?,?)",
        (intro.listing_id, intro.buyer_email, intro.message)
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
def accept_intro(intro_id: int, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    conn.execute(
        "UPDATE intro_requests SET status = 'accepted', tuppence_charged = 1 WHERE id = ?",
        (intro_id,)
    )
    conn.commit()
    conn.close()
    return {"message": "Introduction accepted — 1T charged"}

@app.put("/intros/{intro_id}/decline")
def decline_intro(intro_id: int, _key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    conn.execute(
        "UPDATE intro_requests SET status = 'declined' WHERE id = ?",
        (intro_id,)
    )
    conn.commit()
    conn.close()
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
