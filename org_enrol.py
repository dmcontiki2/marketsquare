"""org_enrol.py -- ORG-ENROL-1 (RUL-150, QUICK_LISTING_SPEC s12/12a; CASUALS_REACH_PROPOSALS s1).

THE EMPLOYER DOOR. One conversation with an organisation (an estate gate desk, a college, a mine, a
cleaning company) enrols its current and former workers. Each person gets HER OWN private link:

    employer's admin sends the list (name + role + language)  ->  POST /agencies/{id}/enrol
      -> each row mints HER OWN key account (RUL-167 link key: no e-mail, no phone held)
         and a membership of that organisation, and NOTHING ELSE
      -> a printable sheet of slips (name, role, QR, link) that the employer hands out -- we send nothing
      -> she opens /e/<secret>: signed in, the Quick door opens on her role, in her language
         (/q/services?role=<role>&lang=<lang>&src=org<id>)
      -> she builds her own advert and publishes it BY HER OWN HAND, behind the app's EULA gate
      -> a VERIFIED organisation's enrolment is its confirmation: universal.employer_confirmed (12 pts)
         is already on her account when she publishes

THE HARD LINE (s12a, asserted by the ledger, not by code review): THIS MODULE CANNOT CREATE A
LISTING. It writes three tables only -- users (the key account), agency_members (the membership),
org_enrolments (the slip) -- plus user_credentials for a verified organisation's confirmation. It
imports nothing that creates or publishes adverts, and it only ever READS the listings table (to
count what she published herself).

Her link never lapses (David's no-lapse rule, 18 Sep): it is the same key /k/<secret> honours. The
secret leaves the server exactly once, on the sheet; only its hash is stored.
"""
import hashlib
import html
import io
import base64
import json
import os
import re
import secrets
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Cookie, Header, HTTPException, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

import database

router = APIRouter()

MAX_ROWS = 500
LANGS = ("en", "zu", "xh", "af", "nso")
_HERE = os.path.dirname(os.path.abspath(__file__))

# ── Injected seams (bea_main.configure) ───────────────────────────────────────
_S = {"key_hash": None, "new_identity": None, "establish_session": None,
      "agency_admin": None, "trust_recompute": None, "app_url": "https://trustsquare.co",
      "session_email": None, "admin_key_ok": None}


def configure(**kw):
    for k, v in kw.items():
        if k in _S and v is not None:
            _S[k] = v


def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def init_schema(conn=None):
    own = conn is None
    conn = conn or database.get_db()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS org_enrolments (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            agency_id   INTEGER NOT NULL,
            identity    TEXT NOT NULL UNIQUE,
            name        TEXT,
            role        TEXT,
            lang        TEXT,
            former      INTEGER NOT NULL DEFAULT 0,
            created_at  TEXT NOT NULL,
            created_by  TEXT,
            claimed_at  TEXT,
            confirmed_at TEXT
        )""")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_org_enrol_agency ON org_enrolments(agency_id)")
        conn.commit()
    finally:
        if own:
            conn.close()


# ── the role slate is data (roles/role_registry.json), never a list typed here ──
_ROLES = None


def roles():
    global _ROLES
    if _ROLES is None:
        _ROLES = {}
        for p in (os.path.join(_HERE, "roles", "role_registry.json"), os.path.join(_HERE, "role_registry.json")):
            try:
                with open(p, encoding="utf-8") as fh:
                    for r in json.load(fh).get("roles", []):
                        if r.get("status") == "in" and r.get("key"):
                            _ROLES[r["key"]] = r
                break
            except Exception:
                continue
    return _ROLES


def role_label(key, lang="en"):
    r = roles().get(key) or {}
    lab = r.get("label") or {}
    if isinstance(lab, dict):
        return lab.get(lang) or lab.get("en") or key.replace("_", " ").capitalize()
    return str(lab or key)


def _org_admin(agency_id, ts_user, x_admin_key, ctx):
    """Who may enrol or read an organisation's people: ops with the admin key, or THAT organisation's
    own admin, proven by session. Enforced here as well as by the shared agency seam, so the kill
    switch that can put the agency lane into shadow mode can never open this door -- enrolment
    mints accounts and can carry a 12-point confirmation."""
    _S["agency_admin"](agency_id, ts_user, x_admin_key, ctx)
    if _S["admin_key_ok"] and _S["admin_key_ok"](x_admin_key):
        return "admin-key"
    sess = (_S["session_email"](ts_user) if _S["session_email"] else None) or ""
    if not sess:
        raise HTTPException(status_code=401, detail="Please sign in to do that.")
    conn = database.get_db()
    try:
        row = conn.execute("SELECT 1 FROM agencies WHERE id=? AND LOWER(admin_email)=?",
                           (agency_id, sess.strip().lower())).fetchone()
    finally:
        conn.close()
    if not row:
        raise HTTPException(status_code=403, detail="Only this organisation's admin can do that.")
    return "agency-admin:%d" % int(agency_id)


class EnrolRow(BaseModel):
    name: str
    role: str
    lang: Optional[str] = None
    former: Optional[bool] = False


class EnrolIn(BaseModel):
    rows: List[EnrolRow]
    lang: Optional[str] = "en"


def _clean_rows(rows, default_lang):
    if not rows:
        raise HTTPException(status_code=400, detail="The list is empty.")
    if len(rows) > MAX_ROWS:
        raise HTTPException(status_code=400, detail="At most %d people per list -- split it." % MAX_ROWS)
    known = roles()
    out, bad = [], []
    for i, r in enumerate(rows, 1):
        name = re.sub(r"\s+", " ", (r.name or "")).strip()[:60]
        role = (r.role or "").strip().lower()
        lang = (r.lang or default_lang or "en").strip().lower()
        lang = "nso" if lang == "st" else lang            # RUL-162
        if not name:
            bad.append("row %d: no name" % i)
        elif known and role not in known:
            bad.append("row %d: unknown role '%s'" % (i, role[:30]))
        elif not re.match(r"^[a-z0-9_]{2,40}$", role):
            bad.append("row %d: role must be a role key" % i)
        elif lang not in LANGS:
            bad.append("row %d: language must be one of %s" % (i, ", ".join(LANGS)))
        else:
            out.append({"name": name, "role": role, "lang": lang, "former": bool(r.former)})
    if bad:
        raise HTTPException(status_code=422, detail="; ".join(bad[:12]))
    return out


def _confirm(conn, identity, agency_id, actor):
    """A VERIFIED organisation's enrolment is its employer confirmation (12 pts, once). Never re-earns a
    confirmation ops has rejected; never stacks on one she already holds."""
    ag = conn.execute("SELECT verified FROM agencies WHERE id=?", (agency_id,)).fetchone()
    if not ag or not ag["verified"]:
        return False
    prev = conn.execute("SELECT status FROM user_credentials WHERE email=? AND signal_id='universal.employer_confirmed'",
                        (identity,)).fetchone()
    if prev:
        return False
    who = hashlib.sha256((actor or "admin").encode("utf-8")).hexdigest()[:12]
    conn.execute(
        "INSERT INTO user_credentials (email, signal_id, status, points, notes, verified_at, verified_by, listing_category) "
        "VALUES (?, 'universal.employer_confirmed', 'earned', 12, ?, ?, ?, NULL) "
        "ON CONFLICT(email, signal_id) DO NOTHING",
        (identity, "Confirmed by a verified employer that enrolled her (ORG-ENROL-1). The employer is never published.",
         _now(), "org:%d|by:%s" % (int(agency_id), who)))
    conn.execute("UPDATE org_enrolments SET confirmed_at=? WHERE identity=? AND confirmed_at IS NULL", (_now(), identity))
    return True


def enrol_rows(conn, agency_id, rows, actor=""):
    """Mint one key account + one membership + one slip per row. Returns [{name, role, lang, link, confirmed}].
    Writes users, agency_members, org_enrolments, user_credentials -- and nothing that is an advert."""
    init_schema(conn)
    if not conn.execute("SELECT id FROM agencies WHERE id=?", (agency_id,)).fetchone():
        raise HTTPException(status_code=404, detail="Organisation not found")
    out = []
    for r in rows:
        secret = secrets.token_urlsafe(24)
        ident = _S["new_identity"]()
        conn.execute("INSERT INTO users (email, name, key_hash, aa_free_used, aa_sessions_remaining) VALUES (?,?,?,0,0)",
                     (ident, r["name"], _S["key_hash"](secret)))
        conn.execute("INSERT INTO agency_members (agency_id, agent_email, listing_cap, status, agent_name, role) "
                     "VALUES (?,?,?, 'invited', ?, 'agent') ON CONFLICT(agency_id, agent_email) DO NOTHING",
                     (agency_id, ident, 3, r["name"]))
        conn.execute("INSERT INTO org_enrolments (agency_id, identity, name, role, lang, former, created_at, created_by) "
                     "VALUES (?,?,?,?,?,?,?,?)",
                     (agency_id, ident, r["name"], r["role"], r["lang"], 1 if r["former"] else 0, _now(), (actor or "")[:80]))
        confirmed = _confirm(conn, ident, agency_id, actor)
        out.append({"name": r["name"], "role": r["role"], "lang": r["lang"], "former": r["former"],
                    "link": _S["app_url"] + "/e/" + secret, "confirmed": confirmed})
    conn.commit()
    return out


def _qr_data_uri(text, px=220):
    try:
        import qrcode
        q = qrcode.QRCode(border=1, box_size=8)
        q.add_data(text)
        q.make(fit=True)
        img = q.make_image(fill_color="black", back_color="white").convert("RGB").resize((px, px))
        buf = io.BytesIO()
        img.save(buf, "PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")
    except Exception:
        return ""


_SLIP_LINE = {
    "en": "Scan or tap: your own TrustSquare advert, in four taps. Your name and number stay private.",
    "af": "Skandeer of tik: jou eie TrustSquare-advertensie, in vier tikke. Jou naam en nommer bly privaat.",
    "zu": "Skena noma uthephe: isikhangiso sakho se-TrustSquare, ngokuthepha okune. Igama nenombolo yakho kuhlala kuyimfihlo.",
    "xh": "Skena okanye ucofe: intengiso yakho ye-TrustSquare, ngokucofa kane. Igama nenombolo yakho zihlala ziyimfihlo.",
    "nso": "Skena goba o kgotle: papatšo ya gago ya TrustSquare, ka go kgotla ga bone. Leina le nomoro ya gago di dula e le sephiri.",
}


def sheet_html(org_name, people):
    e = html.escape
    slips = []
    for p in people:
        slips.append(
            "<div class='slip'><img src='%s' alt=''><div><b>%s</b><span class='role'>%s</span>"
            "<p>%s</p><code>%s</code><small>%s</small></div></div>"
            % (_qr_data_uri(p["link"]), e(p["name"]), e(role_label(p["role"], p["lang"])),
               e(_SLIP_LINE.get(p["lang"], _SLIP_LINE["en"])), e(p["link"]),
               e("From %s%s" % (org_name, " · employer confirmation attached" if p.get("confirmed") else ""))))
    return ("<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
            "<title>Enrolment slips</title><style>"
            "body{font-family:system-ui,sans-serif;margin:16px;color:#10231c}"
            "h1{font-size:20px;margin:0 0 4px}.note{color:#52665e;font-size:13px;margin:0 0 14px}"
            ".slip{display:flex;gap:14px;align-items:center;border:2px dashed #1aa37a;border-radius:14px;padding:12px;margin:0 0 12px;page-break-inside:avoid}"
            ".slip img{width:120px;height:120px;flex:none}.slip b{font-size:18px;display:block}"
            ".role{display:inline-block;background:#e3f6ee;color:#0c6b4f;border-radius:99px;padding:2px 10px;font-size:13px;margin:4px 0}"
            ".slip p{margin:4px 0;font-size:14px}.slip code{font-size:11px;word-break:break-all;color:#0c6b4f}"
            ".slip small{display:block;color:#52665e;font-size:12px;margin-top:4px}"
            "@media print{.note{display:none}}</style></head><body>"
            "<h1>%s — %d enrolment slip%s</h1>"
            "<p class='note'>Cut along the dashes and hand each person her own slip. Each link is shown once and is "
            "her key: keep this page private and print it; nobody can create an advert for her.</p>%s</body></html>"
            % (e(org_name), len(people), "" if len(people) == 1 else "s", "".join(slips)))


@router.post("/agencies/{agency_id}/enrol")
def enrol(agency_id: int, body: EnrolIn, format: str = Query(default="json"),
          ts_user: str = Cookie(default=None), x_admin_key: str = Header(default=None)):
    """The importer. The organisation's own admin (or ops with the admin key) enrols a list of people.
    It creates their key accounts and memberships and CANNOT create an advert."""
    actor = _org_admin(agency_id, ts_user, x_admin_key, "org-enrol")
    rows = _clean_rows(body.rows, (body.lang or "en").lower())
    conn = database.get_db()
    try:
        org = conn.execute("SELECT name FROM agencies WHERE id=?", (agency_id,)).fetchone()
        people = enrol_rows(conn, agency_id, rows, actor=actor)
    finally:
        conn.close()
    if format == "sheet":
        return HTMLResponse(sheet_html((org["name"] if org else "Your employer"), people),
                            headers={"Cache-Control": "no-store"})
    return {"ok": True, "agency_id": agency_id, "enrolled": len(people), "people": people}


@router.get("/agencies/{agency_id}/enrolments")
def enrolments(agency_id: int, ts_user: str = Cookie(default=None), x_admin_key: str = Header(default=None)):
    """The organisation sees its own people: enrolled, opened, confirmed, published. No links, no secrets."""
    _org_admin(agency_id, ts_user, x_admin_key, "org-enrolments")
    conn = database.get_db()
    try:
        init_schema(conn)
        rows = conn.execute("SELECT identity, name, role, lang, former, created_at, claimed_at, confirmed_at "
                            "FROM org_enrolments WHERE agency_id=? ORDER BY id", (agency_id,)).fetchall()
        live = {}
        for r in rows:
            c = conn.execute("SELECT COUNT(*) AS n FROM listings WHERE LOWER(seller_email)=? AND listing_status='LIVE'",
                             (r["identity"],)).fetchone()   # a READ -- the count she earned herself
            live[r["identity"]] = int(c["n"] if c else 0)
    finally:
        conn.close()
    people = [{"name": r["name"], "role": r["role"], "lang": r["lang"], "former": bool(r["former"]),
               "enrolled": r["created_at"], "opened": r["claimed_at"], "confirmed": r["confirmed_at"],
               "live_adverts": live.get(r["identity"], 0)} for r in rows]
    return {"agency_id": agency_id, "enrolled": len(people),
            "opened": sum(1 for p in people if p["opened"]),
            "published": sum(1 for p in people if p["live_adverts"]), "people": people}


@router.get("/e/{secret}")
def open_enrolment(secret: str):
    """Her slip. Signs her in (the key never lapses) and opens the Quick door on her role, in her
    language -- or the app, once she has an advert of her own."""
    conn = database.get_db()
    try:
        init_schema(conn)
        u = conn.execute("SELECT email FROM users WHERE key_hash=? AND closed_at IS NULL",
                         (_S["key_hash"](secret or ""),)).fetchone()
        en = conn.execute("SELECT agency_id, role, lang, claimed_at FROM org_enrolments WHERE identity=?",
                          ((u["email"] if u else ""),)).fetchone() if u else None
        if not u or not en:
            return HTMLResponse("<!doctype html><meta name='viewport' content='width=device-width'>"
                                "<body style='font-family:system-ui;padding:24px'><h2>This link is not active</h2>"
                                "<p>Ask the person who gave you the slip for a new one, or start your own advert at "
                                "<a href='/q/services'>trustsquare.co/q/services</a>.</p></body>", status_code=404)
        ident = u["email"]
        if not en["claimed_at"]:
            conn.execute("UPDATE org_enrolments SET claimed_at=? WHERE identity=?", (_now(), ident))
        _confirm(conn, ident, en["agency_id"], "claim")          # an organisation verified since the import
        conn.commit()
        has_advert = conn.execute("SELECT 1 FROM listings WHERE LOWER(seller_email)=? LIMIT 1", (ident,)).fetchone()
    finally:
        conn.close()
    if has_advert:
        target = "/"
    else:
        target = "/q/services?role=%s&lang=%s&src=org%d" % (en["role"], en["lang"] or "en", int(en["agency_id"]))
    resp = RedirectResponse(url=target, status_code=303)
    _S["establish_session"](ident, resp)                          # also turns the membership 'active'
    resp.headers["Cache-Control"] = "no-store"
    resp.headers["Referrer-Policy"] = "no-referrer"
    try:
        if _S["trust_recompute"]:
            _S["trust_recompute"](ident)
    except Exception:
        pass
    return resp
