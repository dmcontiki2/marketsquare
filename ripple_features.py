"""ripple_features.py -- RIPPLE-2 (David, 27 Sep 2026): the Ripple stories must work as advertised.

Two doors that share one page (join.html, served at /join/<token>):

  * TESTER-INVITE-1 -- "the moment he gives his email then you give him his 200T credit".
    An admin mints a single-use invite link for a named tester (Jacques, Kate). The person
    opens it, signs in with the 6-digit code on that page, and 200T lands at once as a
    tester_grant -- which also makes the account a tester under RUL-189 (every paid AI
    feature on any plan). One link = one person; a second claimer is told it is used.

  * BUZZ-JOIN-1 -- "the someone you worked for is not mandatory and never was".
    A seller's OWN Buzz link for her regulars. A regular taps it, signs in by code, ticks
    the Buzz terms (s3.8) and is connected -- no employer reference. Making the link is her
    consent that people who join from it may buzz her; joining is his consent that she may
    buzz him. Each switch stays per person (RUL-132(d)/133(f)) and either side can still
    turn theirs off or close Buzz. Her regulars limit applies (RUL-179(e)); she owns the
    connection (circle_owner). A new link retires the old one.

Mounted from bea_main.py with build_router(globals()) so every helper is the app's own
(one identity lane, one Buzz consent model, one admin gate) -- nothing is re-implemented.
"""
from datetime import datetime, timezone
import secrets as _secrets

from fastapi import APIRouter, Cookie, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional

TESTER_INVITE_T = 200


class _InviteIn(BaseModel):
    label: str
    amount: Optional[int] = TESTER_INVITE_T


class _AttachIn(BaseModel):
    job_id: Optional[str] = ""          # "" detaches


_REPORT_FNS = {"collectables_advert": "Collectables market report", "property_dossier": "Property dossier",
               "car_dossier": "Car dossier", "collection_liquidation": "Liquidation plan",
               "offer_advisor": "Offer strategy"}


def _range_from(text):
    """REPORT-ATTACH-1: the ONE market range the report itself gives -- its 'Likely achieved range' when it
    states one (Collectables), else the first money range written right after the first ESTIMATE in the
    body (Property / Car dossiers). The opening '>' notice is skipped. Exactly as the report wrote it,
    normalised to rands; None when the report gives no range (the listing then says only that a report
    is attached). Never adds, averages or invents a figure."""
    import re
    body = "\n".join(l for l in (text or "").splitlines() if not l.lstrip().startswith(">"))
    n = r"(\d{1,3}(?:[ ,]\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?)"
    rng = re.compile(r"R\s?" + n + r"\s*(k|m|million)?\s*(?:\u2013|\u2014|-|to)\s*R?\s?" + n + r"\s*(k|m|million)?(?![\w])", re.I)
    unit = {"": 1, "k": 1e3, "m": 1e6, "million": 1e6}
    def conv(v, u):
        v = v.replace(" ", "").replace(",", "")
        return float(v) * unit[(u or "").lower()]
    spots = []
    m = re.search(r"likely achieved range", body, re.I)
    if m:
        spots.append(body[m.end(): m.end() + 160])
    m = re.search(r"ESTIMATE", body)
    if m:
        spots.append(body[m.start(): m.start() + 260])
    for seg in spots:
        r = rng.search(seg)
        if not r:
            continue
        try:
            lo = conv(r.group(1), r.group(2) or r.group(4))
            hi = conv(r.group(3), r.group(4) or r.group(2))
        except Exception:
            continue
        if lo > 0 and hi >= lo:
            f = lambda v: "R" + format(int(round(v)), ",")
            return "%s\u2013%s" % (f(lo), f(hi))
    return None


class _ClaimIn(BaseModel):
    token: str
    accept_buzz: Optional[bool] = False   # the s3.8 tick on the join page (same words as the Buzz screen)


def build_router(g):
    database = g["database"]
    jwt = g["_pyjwt"]
    SECRET, ALGO = g["_JWT_SECRET"], g["_JWT_ALGO"]
    APP_URL = g["APP_URL"]
    session_email = g["_session_email"]
    require_admin = g["_require_admin"]
    buzz_accepted = g["_buzz_accepted"]
    buzz_key = g["_buzz_key"]
    buzz_pair = g["_buzz_pair"]
    circle_status = g["_circle_status"]
    circle_full_detail = g["_circle_full_detail"]
    buzz_name = g["_buzz_name"]
    log = g["_log"]
    wallet_lock = g["_wallet_lock"]

    r = APIRouter()

    def _ensure(conn):
        conn.execute("""CREATE TABLE IF NOT EXISTS tester_invites (
            nonce TEXT PRIMARY KEY, label TEXT NOT NULL, amount INTEGER NOT NULL,
            created_by TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            claimed_by TEXT, claimed_at TEXT)""")
        conn.execute("""CREATE TABLE IF NOT EXISTS buzz_links (
            email TEXT PRIMARY KEY, nonce TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")

    def _decode(token):
        try:
            c = jwt.decode(token or "", SECRET, algorithms=[ALGO])
        except Exception:
            raise HTTPException(status_code=400, detail="That link is not valid.")
        if c.get("purpose") not in ("tester_invite", "buzz_join"):
            raise HTTPException(status_code=400, detail="That link is not valid.")
        return c

    def _first(name, email):
        n = (name or "").strip() or (email or "").split("@")[0]
        return n.split(" ")[0]

    # ── TESTER-INVITE-1 ──────────────────────────────────────────────────────
    @r.post("/admin/tester-invite")
    def tester_invite(body: _InviteIn, admin=Depends(require_admin)):
        label = (body.label or "").strip()[:60]
        amt = int(body.amount or TESTER_INVITE_T)
        if not label or amt < 1 or amt > 1000:
            raise HTTPException(status_code=400, detail="A name and an amount of 1-1000 are needed.")
        nonce = _secrets.token_urlsafe(9)
        conn = database.get_db()
        try:
            _ensure(conn)
            conn.execute("INSERT INTO tester_invites (nonce, label, amount, created_by) VALUES (?,?,?,?)",
                         (nonce, label, amt, str(admin)[:80]))
            conn.commit()
        finally:
            conn.close()
        tok = jwt.encode({"purpose": "tester_invite", "n": nonce}, SECRET, algorithm=ALGO)   # no expiry (18 Sep rule)
        return {"url": APP_URL + "/join/" + tok, "label": label, "amount": amt}

    # ── BUZZ-JOIN-1: her own link ────────────────────────────────────────────
    @r.get("/buzz/my-link")
    def buzz_my_link(new: int = 0, ts_user: str = Cookie(default=None)):
        me = (session_email(ts_user) or "").strip().lower()
        if "@" not in me:
            raise HTTPException(status_code=401, detail="Please sign in first.")
        if not buzz_accepted(me):
            raise HTTPException(status_code=403, detail="Accept the Buzz terms (s3.8) first - one tick, no ID.")
        conn = database.get_db()
        try:
            _ensure(conn)
            row = conn.execute("SELECT nonce FROM buzz_links WHERE email=?", (me,)).fetchone()
            if row and not new:
                nonce = row["nonce"]
            else:
                nonce = _secrets.token_urlsafe(9)
                conn.execute("INSERT INTO buzz_links (email, nonce) VALUES (?,?) ON CONFLICT(email) DO UPDATE "
                             "SET nonce=excluded.nonce, created_at=CURRENT_TIMESTAMP", (me, nonce))
                conn.commit()
            name = buzz_name(conn, me)
        finally:
            conn.close()
        tok = jwt.encode({"purpose": "buzz_join", "e": me, "n": nonce}, SECRET, algorithm=ALGO)
        return {"url": APP_URL + "/join/" + tok, "name": name}

    # ── shared page: who is asking, and what the link does ───────────────────
    @r.get("/trust/join-who")
    def join_who(token: str):
        c = _decode(token)
        conn = database.get_db()
        try:
            _ensure(conn)
            if c["purpose"] == "tester_invite":
                row = conn.execute("SELECT label, amount, claimed_by FROM tester_invites WHERE nonce=?",
                                   (c.get("n"),)).fetchone()
                if not row:
                    raise HTTPException(status_code=400, detail="That invitation is not valid.")
                return {"kind": "tester", "name": _first(row["label"], ""), "amount": int(row["amount"]),
                        "used": bool(row["claimed_by"])}
            em = (c.get("e") or "").lower()
            row = conn.execute("SELECT nonce FROM buzz_links WHERE email=?", (em,)).fetchone()
            if not row or row["nonce"] != c.get("n"):
                raise HTTPException(status_code=400, detail="This link has been replaced by a newer one - ask for the new link.")
            return {"kind": "buzz", "name": _first(buzz_name(conn, em), em)}
        finally:
            conn.close()

    @r.post("/trust/join-claim")
    def join_claim(body: _ClaimIn, ts_user: str = Cookie(default=None)):
        me = (session_email(ts_user) or "").strip().lower()
        if "@" not in me:
            from fastapi.responses import JSONResponse
            return JSONResponse(status_code=401, content={"detail": "Please sign in first.", "code": "signin_required"})
        c = _decode(body.token)
        conn = database.get_db()
        try:
            _ensure(conn)
            if c["purpose"] == "tester_invite":
                wallet_lock(conn)   # BEGIN IMMEDIATE unless a transaction is already open: one claimer wins
                row = conn.execute("SELECT label, amount, claimed_by FROM tester_invites WHERE nonce=?",
                                   (c.get("n"),)).fetchone()
                if not row:
                    conn.rollback()
                    raise HTTPException(status_code=400, detail="That invitation is not valid.")
                if row["claimed_by"]:
                    conn.rollback()
                    if row["claimed_by"] == me:
                        return {"kind": "tester", "granted": 0, "already": True}
                    raise HTTPException(status_code=409, detail="This invitation has already been used.")
                amt = int(row["amount"])
                conn.execute("INSERT INTO users (email) VALUES (?) ON CONFLICT(email) DO NOTHING", (me,))
                conn.execute("UPDATE tester_invites SET claimed_by=?, claimed_at=? WHERE nonce=?",
                             (me, datetime.now(timezone.utc).isoformat(), c.get("n")))
                conn.execute("INSERT INTO transactions (user_email, type, amount, description) VALUES (?,?,?,?)",
                             (me, "tester_grant", amt,
                              "Tester grant - %dT to test freely, with thanks (invitation for %s)" % (amt, row["label"])))
                conn.commit()
                bal = conn.execute("SELECT COALESCE(SUM(amount),0) AS b FROM transactions WHERE user_email=?",
                                   (me,)).fetchone()["b"]
                log.info("TESTER-INVITE-1 %s claimed by %s (%dT)", row["label"], me, amt)
                return {"kind": "tester", "granted": amt, "balance": int(bal or 0)}

            # buzz_join
            seller = (c.get("e") or "").lower()
            row = conn.execute("SELECT nonce FROM buzz_links WHERE email=?", (seller,)).fetchone()
            if not row or row["nonce"] != c.get("n"):
                raise HTTPException(status_code=400, detail="This link has been replaced by a newer one - ask for the new link.")
            if seller == me:
                raise HTTPException(status_code=400, detail="This is your own Buzz link - send it to your regulars.")
            if not buzz_accepted(me):
                if not body.accept_buzz:
                    raise HTTPException(status_code=403, detail="Tick the Buzz terms first.")
                # the tick on this page IS the acceptance moment (same s3.8 words as the Buzz screen);
                # it records Buzz only and never the full Terms (E2E-HMI-1 rule, as POST /buzz/accept)
                conn.execute("INSERT INTO users (email) VALUES (?) ON CONFLICT(email) DO NOTHING", (me,))
                conn.execute("UPDATE users SET buzz_accepted_at = COALESCE(buzz_accepted_at, CURRENT_TIMESTAMP) "
                             "WHERE email = ?", (me,))
            a, b = buzz_key(seller, me)
            pair = buzz_pair(conn, a, b)
            if pair and pair["closed_at"]:
                raise HTTPException(status_code=409, detail="Buzz between you two was closed. Only the person who closed it can open it again.")
            if not pair:
                st = circle_status(conn, seller)
                if st["full"]:
                    raise HTTPException(status_code=403, detail="%s's list of regulars is full right now - ask her to make room." % _first(buzz_name(conn, seller), seller))
                conn.execute("""INSERT INTO buzz_pairs (a_email, b_email, a_allows, b_allows, created_by, source, circle_owner)
                                VALUES (?,?,1,1,?,?,?) ON CONFLICT(a_email, b_email) DO NOTHING""",
                             (a, b, me, "regular-link", seller))
            else:
                conn.execute("UPDATE buzz_pairs SET a_allows=1, b_allows=1 WHERE id=?", (pair["id"],))
            conn.commit()
            log.info("BUZZ-JOIN-1 %s joined %s's regulars", me, seller)
            return {"kind": "buzz", "connected": True, "name": _first(buzz_name(conn, seller), seller)}
        finally:
            conn.close()

    # ── REPORT-ATTACH-1: Jacques attaches his own delivered report to his own listing ──────────
    def _ensure_listing_cols(conn):
        have = {r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()}
        for col in ("ai_report_job", "ai_report_fn", "ai_report_at", "ai_range_text"):
            if col not in have:
                conn.execute("ALTER TABLE listings ADD COLUMN %s TEXT" % col)

    @r.post("/listings/{listing_id}/attach-report")
    def attach_report(listing_id: int, body: _AttachIn, ts_user: str = Cookie(default=None)):
        import httpx
        me = (session_email(ts_user) or "").strip().lower()
        if "@" not in me:
            raise HTTPException(status_code=401, detail="Please sign in first.")
        conn = database.get_db()
        try:
            _ensure_listing_cols(conn)
            row = conn.execute("SELECT seller_email FROM listings WHERE id=?", (listing_id,)).fetchone()
            if not row or (row["seller_email"] or "").strip().lower() != me:
                raise HTTPException(status_code=404, detail="That is not one of your listings.")
            jid = (body.job_id or "").strip()
            if not jid:
                conn.execute("UPDATE listings SET ai_report_job=NULL, ai_report_fn=NULL, ai_report_at=NULL, "
                             "ai_range_text=NULL WHERE id=?", (listing_id,))
                conn.commit()
                return {"attached": False}
            if not jid.startswith("ai_"):
                raise HTTPException(status_code=400, detail="Only a report you paid for can be attached.")
            try:
                jr = httpx.get("http://127.0.0.1:8002/ai/jobs/" + jid, cookies={"ts_user": ts_user or ""}, timeout=10)
            except Exception:
                raise HTTPException(status_code=503, detail="The reports service did not answer - try again in a minute.")
            if jr.status_code != 200:
                raise HTTPException(status_code=404, detail="That report was not found in your account.")
            j = jr.json()
            if j.get("status") != "delivered":
                raise HTTPException(status_code=409, detail="That report has not been delivered.")
            fn = j.get("function_id") or ""
            rng = _range_from(j.get("result") or "")
            when = (j.get("finished_at") or j.get("created_at") or "")[:10]
            conn.execute("UPDATE listings SET ai_report_job=?, ai_report_fn=?, ai_report_at=?, ai_range_text=? WHERE id=?",
                         (jid, _REPORT_FNS.get(fn, "AI report"), when, rng, listing_id))
            conn.commit()
            log.info("REPORT-ATTACH-1 %s attached %s to listing %s (range %s)", me, jid, listing_id, rng)
            return {"attached": True, "range": rng, "report": _REPORT_FNS.get(fn, "AI report"), "date": when}
        finally:
            conn.close()

    return r
