"""
launch_redemption.py — Founders Badge redemption side + monthly Tuppence allocation.

Canon: Canon_Addendum_1_FoundersBadge.docx rev 3 (15 Jun 2026) — the $2 anchor,
6/10/20/50 T monthly allocations, 20%-rounded-up Founders bonus (8/12/24/60),
Pro-only minting during the launch window (rev 3, 15 Jun 2026 — supersedes rev 2's
Business/Elite, which the Simpler Model retired to legacy), one badge per human, forever.

Issuing side (CityLauncher/emailer/launch_codes.py) is mirrored EXACTLY here:
code format TSL-XXXX-XXXX-CCCC, Crockford base32 body (8 chars), 4-char
HMAC-SHA256 tag over the body keyed by LAUNCH_CODE_SECRET. The database is the
only authority — the HMAC is a cheap offline forgery/typo reject.

POPIA: the badge binds to a SALTED hash of the already-hashed verified ID
(HMAC-SHA256(FOUNDERS_ID_SALT, users.id_number_hash)). The raw ID number is
never stored in programme tables, and programme rows cannot be joined back to
users.id_number_hash without the salt. Lifetime uniqueness enforced on the hash.

Env (all OFF by default — nothing fires until explicitly enabled):
  LAUNCH_REDEMPTION_ENABLED = 1           # gates POST /launch/redeem
  LAUNCH_CODE_SECRET        = <hex>       # shared with CityLauncher issuing side
  LAUNCH_SPECIAL_DEADLINE   = 2026-08-01  # hard close — never extended
  FOUNDERS_ID_SALT          = <hex>       # programme-table salt (required to mint)
  TUPPENCE_MONTHLY_ENABLED  = 1           # gates monthly allocation grants
  LISTING_VELOCITY_ENABLED  = 1           # gates per-day new-listing flood control
  LISTING_VELOCITY_LIMITS   = free:2,standard:5,professional:10,business:20,elite:50
  LAUNCH_REGISTRY_SOURCE    = /var/www/citylauncher/data/prospects.db

Scale-shape invariants respected: standard SQL only; money-touching writes
transactional (BEGIN IMMEDIATE); no process-memory state (the attempt throttle
is DB-backed); ledger reads authoritative.
"""

import hashlib
import hmac
import os
import sqlite3
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

import database
import auth

router = APIRouter()

# ── Canon allocations (Addendum 1 rev 2: price ÷ 2, the restored $2 anchor) ──
# Simpler Model (adopted 9-10 Jun 2026): Starter $5 → 2T/mo, Pro $20 → 10T/mo.
# Legacy tiers retained for existing users until migration.
# PRICING AUTHORITY — see MarketSquare/PRICING_CANON.md; run scripts/check_pricing_canon.py after any change.
TIER_TUPPENCE_MONTHLY = {"starter": 2, "pro": 10,
                         "standard": 6, "professional": 10, "business": 20, "elite": 50}
# NOTE: "starter" was once a legacy alias for "standard" (6T). It is now the canon
# $5 Starter tier (2T). Any pre-Simpler-Model user whose DB row says 'starter'
# must be migrated to 'standard' BEFORE this grants — see existing-user migration map.
_LEGACY_TIER_MAP = {"premium": "professional"}  # legacy keys → canon
_TIER_LABELS = {"starter": "Starter", "pro": "Pro",
                "standard": "Standard", "professional": "Professional",
                "business": "Business", "elite": "Elite"}
QUALIFYING_TIERS = ("pro",)  # the ONLY minting tier ($20 Pro) — rev 3, supersedes rev 2 Business/Elite

# Crockford base32 — no I, L, O, U. Mirror of CityLauncher emailer/launch_codes.py.
_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

_DEFAULT_VELOCITY = {"free": 2, "starter": 5, "standard": 5, "premium": 10,
                     "professional": 10, "business": 20, "elite": 50}


# ── env helpers ──────────────────────────────────────────────────────────────

def _flag(name: str) -> bool:
    return (os.getenv(name) or "").strip().lower() in ("1", "true", "yes", "on")


def _secret() -> str:
    return (os.getenv("LAUNCH_CODE_SECRET") or "").strip()


def _id_salt() -> str:
    return (os.getenv("FOUNDERS_ID_SALT") or "").strip()


def _deadline():
    raw = (os.getenv("LAUNCH_SPECIAL_DEADLINE") or "").strip()
    if not raw:
        return None
    try:
        return datetime.fromisoformat(raw).date()
    except ValueError:
        return None


def redemption_enabled() -> bool:
    """Master gate: explicit flag AND secret AND salt AND a parseable deadline."""
    return bool(_flag("LAUNCH_REDEMPTION_ENABLED") and _secret() and _id_salt() and _deadline())


# ── schema (idempotent, called lazily — import does no DB work) ──────────────

_SCHEMA = """
CREATE TABLE IF NOT EXISTS founders_badges (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    id_hash       TEXT NOT NULL UNIQUE,          -- salted hash — one badge per human, forever
    email         TEXT NOT NULL,                 -- account email at mint (display/join key)
    code          TEXT NOT NULL,                 -- the TSL number redeemed
    code_type     TEXT NOT NULL,                 -- individual | agency
    tier_at_mint  TEXT NOT NULL,
    minted_at     TEXT DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS launch_codes (
    code              TEXT PRIMARY KEY,
    code_type         TEXT NOT NULL,
    email             TEXT NOT NULL,
    category          TEXT,
    city              TEXT,
    issued_at         TEXT,
    expires_at        TEXT NOT NULL,
    status            TEXT NOT NULL DEFAULT 'issued',
    allocated_id_hash TEXT,
    allocated_at      TEXT
);
CREATE TABLE IF NOT EXISTS tuppence_monthly_grants (
    email        TEXT NOT NULL,
    period       TEXT NOT NULL,                  -- 'YYYY-MM' (UTC)
    amount       INTEGER NOT NULL,               -- base allocation credited
    badge_bonus  INTEGER NOT NULL DEFAULT 0,     -- founders bonus credited on top
    granted_at   TEXT DEFAULT (datetime('now')),
    PRIMARY KEY (email, period)
);
CREATE TABLE IF NOT EXISTS launch_redeem_attempts (
    email        TEXT NOT NULL,
    attempted_at TEXT DEFAULT (datetime('now'))
);
"""

_schema_done = False


def _ensure_schema(conn) -> None:
    """Idempotent, cheap after first call. NEVER executescript when the tables
    already exist — executescript commits any pending transaction, which would
    break the caller's transactional contract (e.g. the subscription-apply hook).
    Production tables are pre-created at deploy; this is the belt-and-braces."""
    global _schema_done
    if _schema_done:
        return
    row = conn.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name='founders_badges'"
    ).fetchone()
    if not row:
        conn.executescript(_SCHEMA)
    _schema_done = True


# ── code validation (exact mirror of the issuing side) ───────────────────────

def _tag(body: str) -> str:
    digest = hmac.new(_secret().encode(), body.encode(), hashlib.sha256).digest()
    n = int.from_bytes(digest[:4], "big")
    return "".join(_ALPHABET[(n >> (5 * i)) & 31] for i in range(4))


def looks_valid(code: str) -> bool:
    """Offline structural + HMAC check. The launch_codes row stays the authority."""
    parts = (code or "").strip().upper().split("-")
    if len(parts) != 4 or parts[0] != "TSL":
        return False
    body = parts[1] + parts[2]
    if len(body) != 8 or any(c not in _ALPHABET for c in body + parts[3]):
        return False
    return hmac.compare_digest(_tag(body), parts[3])


def _salted_id_hash(id_number_hash: str) -> str:
    """Programme-table identity key: salted re-hash of the KYC-verified ID hash."""
    return hmac.new(_id_salt().encode(), id_number_hash.encode(), hashlib.sha256).hexdigest()


# ── allocation maths (canon: ×1.2 rounded UP — 6→8, 10→12, 20→24, 50→60) ─────

def monthly_allocation(tier: str, has_badge: bool) -> int:
    t = _LEGACY_TIER_MAP.get(tier, tier)
    base = TIER_TUPPENCE_MONTHLY.get(t, 0)
    if base and has_badge:
        return (base * 12 + 9) // 10  # integer ceil(base × 1.2)
    return base


def _badge_row_for_email(conn, email: str):
    """Badge lookup: by salted ID-hash (authoritative) with email fallback so the
    benefit survives even if a verified ID is re-checked later. Tolerates the
    table not existing yet (returns None)."""
    try:
        _ensure_schema(conn)
        row = conn.execute(
            "SELECT id_number_hash FROM users WHERE LOWER(email)=?", (email.lower(),)
        ).fetchone()
        if row and row["id_number_hash"] and _id_salt():
            b = conn.execute(
                "SELECT * FROM founders_badges WHERE id_hash=?",
                (_salted_id_hash(row["id_number_hash"]),)
            ).fetchone()
            if b:
                return b
        return conn.execute(
            "SELECT * FROM founders_badges WHERE LOWER(email)=?", (email.lower(),)
        ).fetchone()
    except sqlite3.Error:
        return None


def founders_email_set(conn) -> set:
    """Lowercased emails of all badge holders — for marking listings. Cheap (the
    cohort is closed and small); tolerates a missing table."""
    try:
        _ensure_schema(conn)
        return {r["email"].lower() for r in
                conn.execute("SELECT email FROM founders_badges").fetchall()}
    except sqlite3.Error:
        return set()


def grant_monthly_tuppence(conn, email: str, tier: str, period: str = None):
    """Credit the month's allocation (+ Founders bonus) on the CALLER'S open
    transaction — does not commit, mirrors _deduct_tuppence's contract.
    Idempotent per (email, period). Env-gated OFF; returns None when skipped.
    The bonus is one private wallet-history line: 'Founders bonus +XT'."""
    if not _flag("TUPPENCE_MONTHLY_ENABLED"):
        return None
    email = (email or "").lower().strip()
    canon_tier = _LEGACY_TIER_MAP.get(tier, tier)
    base = TIER_TUPPENCE_MONTHLY.get(canon_tier, 0)
    if not email or base <= 0:
        return None  # free tier: no allocation — the badge waits (canon)
    _ensure_schema(conn)
    period = period or datetime.now(timezone.utc).strftime("%Y-%m")
    badge = _badge_row_for_email(conn, email) is not None
    total = monthly_allocation(canon_tier, badge)
    bonus = total - base
    cur = conn.execute(
        "INSERT OR IGNORE INTO tuppence_monthly_grants (email, period, amount, badge_bonus) "
        "VALUES (?, ?, ?, ?)", (email, period, base, bonus))
    if cur.rowcount == 0:
        return None  # already granted this period
    label = _TIER_LABELS.get(canon_tier, canon_tier.title())
    conn.execute(
        "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
        (email, "monthly_allocation", base, f"Monthly Tuppence · {label}"))
    if bonus > 0:
        conn.execute(
            "INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
            (email, "founders_bonus", bonus, f"Founders bonus +{bonus}T"))
    return {"period": period, "amount": base, "badge_bonus": bonus}


# ── per-day new-listing velocity limit (flood control on top of slot caps) ───

def check_listing_velocity(seller_email) -> None:
    """Raise 429 when a seller has hit their per-day new-listing limit.
    Env-gated OFF by default. Opens/closes its own connection."""
    if not _flag("LISTING_VELOCITY_ENABLED") or not seller_email:
        return
    limits = dict(_DEFAULT_VELOCITY)
    raw = (os.getenv("LISTING_VELOCITY_LIMITS") or "").strip()
    if raw:
        for part in raw.split(","):
            if ":" in part:
                k, _, v = part.partition(":")
                try:
                    limits[k.strip().lower()] = int(v)
                except ValueError:
                    pass
    conn = database.get_db()
    try:
        row = conn.execute(
            "SELECT seller_tier FROM users WHERE LOWER(email)=?",
            (seller_email.lower(),)).fetchone()
        tier = (row["seller_tier"] if row else "free") or "free"
        limit = limits.get(tier, limits["free"])
        count = conn.execute(
            "SELECT COUNT(*) AS n FROM listings WHERE LOWER(seller_email)=? "
            "AND created_at >= datetime('now','-1 day')",
            (seller_email.lower(),)).fetchone()["n"]
    finally:
        conn.close()
    if count >= limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily listing limit reached ({limit}/day on your plan) — try again tomorrow.")


# ── redemption ───────────────────────────────────────────────────────────────

class RedeemReq(BaseModel):
    email: str
    code: str


@router.post("/launch/redeem")
def redeem_launch_code(req: RedeemReq):
    """Validate a TSL launch number and mint the Founders Badge.
    Individual codes: exactly one redemption. Agency codes: one redemption per
    distinct agent ID. One badge per human, forever. Idempotent. Transactional."""
    if not redemption_enabled():
        raise HTTPException(status_code=503, detail="The launch special is not open.")
    email = (req.email or "").lower().strip()
    code = (req.code or "").strip().upper()
    if not email:
        raise HTTPException(status_code=400, detail="email is required")

    today = datetime.now(timezone.utc).date()
    if today > _deadline():
        raise HTTPException(status_code=410,
                            detail="The launch window has closed — the Founders Badge is never minted again.")

    conn = database.get_db()
    try:
        _ensure_schema(conn)
        # DB-backed attempt throttle (stateless across processes)
        conn.execute("INSERT INTO launch_redeem_attempts (email) VALUES (?)", (email,))
        conn.commit()
        attempts = conn.execute(
            "SELECT COUNT(*) AS n FROM launch_redeem_attempts "
            "WHERE email=? AND attempted_at >= datetime('now','-1 hour')", (email,)
        ).fetchone()["n"]
        if attempts > 8:
            raise HTTPException(status_code=429, detail="Too many attempts — try again in an hour.")

        if not looks_valid(code):
            raise HTTPException(status_code=400, detail="That launch number is not valid.")

        user = conn.execute(
            "SELECT id_number_hash, seller_tier, billing_period_end FROM users WHERE LOWER(email)=?",
            (email,)).fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="No account found for that email.")
        if not user["id_number_hash"]:
            raise HTTPException(status_code=403,
                                detail="Verify your ID first — the badge binds to your verified identity.")
        tier = (user["seller_tier"] or "free").lower()
        if tier not in QUALIFYING_TIERS:
            raise HTTPException(status_code=403,
                                detail="The launch special requires an active Business ($40) or Elite ($100) subscription.")
        bpe = user["billing_period_end"]
        if bpe:
            try:
                if datetime.fromisoformat(bpe.replace("Z", "+00:00")) < datetime.now(timezone.utc):
                    raise HTTPException(status_code=403,
                                        detail="Your subscription has lapsed — renew before redeeming.")
            except ValueError:
                pass

        row = conn.execute(
            "SELECT * FROM launch_codes WHERE code=? AND status='issued'", (code,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="That launch number is not in the registry.")
        try:
            if datetime.fromisoformat(str(row["expires_at"]).replace("Z", "+00:00")).date() < today:
                raise HTTPException(status_code=410, detail="That launch number has expired.")
        except ValueError:
            pass

        id_hash = _salted_id_hash(user["id_number_hash"])

        # Money-touching path: explicit write transaction (scale-shape invariant 2)
        conn.execute("BEGIN IMMEDIATE")
        mine = conn.execute(
            "SELECT * FROM founders_badges WHERE id_hash=?", (id_hash,)).fetchone()
        if mine:
            conn.execute("ROLLBACK")
            if mine["code"] == code:
                return {"status": "already_minted", "minted_at": mine["minted_at"],
                        "monthly_allocation": monthly_allocation(tier, True)}
            raise HTTPException(status_code=409, detail="One badge per person — yours is already minted.")
        if row["code_type"] == "individual":
            taken = conn.execute(
                "SELECT COUNT(*) AS n FROM founders_badges WHERE code=?", (code,)).fetchone()["n"]
            if taken:
                conn.execute("ROLLBACK")
                raise HTTPException(status_code=409, detail="That launch number has already been redeemed.")
        conn.execute(
            "INSERT INTO founders_badges (id_hash, email, code, code_type, tier_at_mint) "
            "VALUES (?,?,?,?,?)", (id_hash, email, code, row["code_type"], tier))
        conn.execute(
            "UPDATE launch_codes SET allocated_id_hash=COALESCE(allocated_id_hash, ?), "
            "allocated_at=datetime('now') WHERE code=?", (id_hash, code))
        conn.commit()
        return {"status": "minted", "tier": tier,
                "monthly_allocation": monthly_allocation(tier, True),
                "line": "Founders Badge · minted at launch 2026 — never minted again"}
    finally:
        conn.close()


# ── registry sync (one-way: CityLauncher prospects.db → BEA, INSERT OR IGNORE) ─

@router.post("/launch/sync-registry")
def sync_registry(_key: str = Depends(auth.require_api_key)):
    src = (os.getenv("LAUNCH_REGISTRY_SOURCE") or "/var/www/citylauncher/data/prospects.db").strip()
    if not os.path.exists(src):
        raise HTTPException(status_code=404, detail=f"Registry source not found: {src}")
    try:
        s = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
        s.row_factory = sqlite3.Row
        rows = s.execute(
            "SELECT code, code_type, email, category, city, issued_at, expires_at, status "
            "FROM launch_codes").fetchall()
        s.close()
    except sqlite3.Error as e:
        raise HTTPException(status_code=502, detail=f"Could not read registry source: {e}")
    conn = database.get_db()
    try:
        _ensure_schema(conn)
        imported = 0
        for r in rows:
            cur = conn.execute(
                "INSERT OR IGNORE INTO launch_codes "
                "(code, code_type, email, category, city, issued_at, expires_at, status) "
                "VALUES (?,?,?,?,?,?,?,?)",
                (r["code"], r["code_type"], r["email"], r["category"], r["city"],
                 r["issued_at"], r["expires_at"], r["status"]))
            imported += cur.rowcount
        conn.commit()
        total = conn.execute("SELECT COUNT(*) AS n FROM launch_codes").fetchone()["n"]
    finally:
        conn.close()
    return {"imported": imported, "source_rows": len(rows), "registry_total": total}


# ── status + holder lookup ───────────────────────────────────────────────────

@router.get("/launch/status")
def launch_status(_key: str = Depends(auth.require_api_key)):
    conn = database.get_db()
    try:
        _ensure_schema(conn)
        badges = conn.execute("SELECT COUNT(*) AS n FROM founders_badges").fetchone()["n"]
        codes = conn.execute("SELECT COUNT(*) AS n FROM launch_codes").fetchone()["n"]
        grants = conn.execute("SELECT COUNT(*) AS n FROM tuppence_monthly_grants").fetchone()["n"]
    finally:
        conn.close()
    return {"redemption_enabled": redemption_enabled(),
            "monthly_allocation_enabled": _flag("TUPPENCE_MONTHLY_ENABLED"),
            "velocity_limit_enabled": _flag("LISTING_VELOCITY_ENABLED"),
            "deadline": str(_deadline() or ""),
            "badges_minted": badges, "registry_codes": codes, "monthly_grants": grants}


@router.get("/launch/mine")
def my_badge(email: str):
    """Holder check for the FEA (boolean only — no perks UI anywhere, canon §2)."""
    conn = database.get_db()
    try:
        badge = _badge_row_for_email(conn, (email or "").lower().strip())
    finally:
        conn.close()
    return {"founders": badge is not None}