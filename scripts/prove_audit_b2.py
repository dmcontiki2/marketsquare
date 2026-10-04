#!/usr/bin/env python3
"""prove_audit_b2.py -- AUDIT-4OCT Batch 2 (4 Oct 2026): EXECUTE the money/privacy/security fixes against the real
bea_main.py, imported with a throwaway SQLite file (never the live database, never the network for money).

Run: MS_API_KEY=k MS_ADMIN_KEY=adm python3 scripts/prove_audit_b2.py      (needs fastapi, boto3, pyjwt, pillow)
"""
import os, sys, json, tempfile, sqlite3
from datetime import datetime, timedelta, timezone
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO); sys.path.insert(0, REPO)
os.environ.setdefault("MS_API_KEY", "k"); os.environ.setdefault("MS_ADMIN_KEY", "adm"); os.environ.setdefault("MS_JWT_SECRET", "test-only-" + os.urandom(8).hex())
os.environ["TUPPENCE_MONTHLY_ENABLED"] = "1"
for k in ("RESEND_API_KEY", "PAYSTACK_SECRET_KEY", "PAYSTACK_WEBHOOK_SECRET"):
    os.environ.pop(k, None)
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k["check_dir"] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
import database
DB = os.path.join(tempfile.mkdtemp(), "b2.db"); database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(os.path.dirname(DB), "flights.db")   # data_flights opens MS_DB (default: ./marketsquare.db on the mount)
import bea_main as b, account_closure, launch_redemption, estate_agents, payments
from fastapi import Response, HTTPException

fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok: fails.append(msg)
def q(sql, *p):
    c = database.get_db(); r = c.execute(sql, p).fetchall(); c.close(); return r
def x(sql, *p):
    c = database.get_db(); c.execute(sql, p); c.commit(); c.close()
def bal(e):
    return q("SELECT COALESCE(SUM(amount),0) AS b FROM transactions WHERE user_email=?", e)[0]["b"]
now = datetime.now(timezone.utc)
def addcol(t, col, typ):
    try:
        x("ALTER TABLE %s ADD COLUMN %s %s" % (t, col, typ))
    except sqlite3.OperationalError:
        pass
# columns the server adds through migrations/ (not at import)
for _t, _c, _ty in (("intro_requests", "tuppence_held", "INTEGER DEFAULT 0"), ("intro_requests", "hold_released_at", "TEXT"),
                    ("listings", "street_address", "TEXT"), ("listings", "listing_lat", "REAL"), ("listings", "listing_lng", "REAL"),
                    ("users", "closed_at", "TEXT"), ("users", "billing_period_end", "TEXT"), ("users", "pending_downgrade_tier", "TEXT")):
    addcol(_t, _c, _ty)

print("AUD-015 / AUD-018 -- retained Tuppence comes back once, at sign-in")
c = database.get_db(); account_closure.ensure_schema(c); c.close()
try:
    x("ALTER TABLE users ADD COLUMN closed_at TEXT")
except sqlite3.OperationalError:
    pass
x("INSERT INTO users (email) VALUES ('ret@x.test')")
x("INSERT INTO account_closures (email, closed_at, closure_type, cause, retained_tuppence, forfeited) VALUES ('ret@x.test', ?, 'user', 'test', 5, 0)",
  now.strftime("%Y-%m-%dT%H:%M:%SZ"))
x("UPDATE users SET closed_at=? WHERE email='ret@x.test'", now.isoformat())
b._establish_user_session("ret@x.test", Response())
b._establish_user_session("ret@x.test", Response())
c = database.get_db(); second = account_closure.restore_on_return(c, "ret@x.test"); c.close()
check(bal("ret@x.test") == 5, "two sign-ins + a direct call restore 5T exactly once (balance %s)" % bal("ret@x.test"))
check(second is None, "the third call finds nothing to restore")
check(q("SELECT closed_at FROM users WHERE email='ret@x.test'")[0]["closed_at"] is None, "the account is open again")

print("AUD-018 -- POST /users on an existing row: name kept, welcome sessions once")
x("INSERT INTO users (email) VALUES ('nm@x.test')")
U = b.User(email="nm@x.test", name="Lerato", ai_sessions=3)
b.create_user(U); b.create_user(U)
r = q("SELECT name, aa_sessions_remaining FROM users WHERE email='nm@x.test'")[0]
check(r["name"] == "Lerato", "the name sent by the sell flow is saved on an existing row")
check(r["aa_sessions_remaining"] == 3, "welcome sessions granted once, not per call (got %s)" % r["aa_sessions_remaining"])

print("AUD-016 -- a paid plan ends when its paid period is over")
past = (now - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ"); fut = (now + timedelta(days=5)).strftime("%Y-%m-%dT%H:%M:%SZ")
x("INSERT INTO users (email, seller_tier, slot_limit, billing_period_end) VALUES ('lapsed@x.test','pro',30,?)", past)
x("INSERT INTO users (email, seller_tier, slot_limit, billing_period_end) VALUES ('paid@x.test','starter',10,?)", fut)
x("INSERT INTO users (email, seller_tier, slot_limit, billing_period_end, is_superuser) VALUES ('su@x.test','pro',30,?,1)", past)
b._apply_pending_downgrades()
t = {r["email"]: (r["seller_tier"], r["slot_limit"]) for r in q("SELECT email, seller_tier, slot_limit FROM users WHERE email IN ('lapsed@x.test','paid@x.test','su@x.test')")}
check(t["lapsed@x.test"] == ("free", b._tier_slot_limit("free")), "a Pro plan past its period is Free again (%s)" % (t["lapsed@x.test"],))
check(t["paid@x.test"] == ("starter", 10), "a plan inside its paid period is untouched")
check(t["su@x.test"][0] == "pro", "a superuser is left alone")

print("AUD-017 -- deleting an advert closes its requests and returns the hold")
x("INSERT INTO users (email) VALUES ('sel@x.test')"); x("INSERT INTO users (email) VALUES ('buy@x.test')")
x("INSERT INTO transactions (user_email, type, amount, description) VALUES ('buy@x.test','topup',2,'seed')")
x("INSERT INTO listings (id, title, price, category, city, seller_email) VALUES (9001,'Bike','R100','Local Market','Pretoria','sel@x.test')")
x("INSERT INTO intro_requests (id, listing_id, buyer_email, status, tuppence_held) VALUES (7001, 9001, 'buy@x.test', 'pending', 1)")
x("INSERT INTO transactions (user_email, type, amount, description) VALUES ('buy@x.test','intro_hold',-1,'hold')")
b.delete_listing(9001, x_admin_key="adm")
st = q("SELECT status, hold_released_at FROM intro_requests WHERE id=7001")[0]
check(st["status"] == "expired" and st["hold_released_at"], "the request is closed and its hold released")
check(bal("buy@x.test") == 2, "the buyer has her 1T back (balance %s)" % bal("buy@x.test"))
x("INSERT INTO intro_requests (id, listing_id, buyer_email, status, tuppence_held) VALUES (7002, 99999, 'buy@x.test', 'pending', 1)")
x("INSERT INTO transactions (user_email, type, amount, description) VALUES ('buy@x.test','intro_hold',-1,'hold')")
try:
    b._lifecycle_sweep(dry_run=False, email_cap=0)
except Exception as e:
    print("     (sweep raised after its intro passes: %r)" % e)
st = q("SELECT status, hold_released_at FROM intro_requests WHERE id=7002")[0]
check(st["status"] == "expired" and st["hold_released_at"], "an ORPHAN request (advert deleted before the fix) is closed by the sweep")

print("AUD-019 -- a capitalised typed address reads the right wallet")
from fastapi.testclient import TestClient
TC = TestClient(b.app)
x("INSERT INTO users (email, eula_accepted_at, eula_version) VALUES ('thandi@x.test', ?, '1.19')", now.isoformat())
x("INSERT INTO transactions (user_email, type, amount, description) VALUES ('thandi@x.test','topup',3,'seed')")
x("INSERT INTO listings (id, title, price, category, city, seller_email, listing_status) VALUES (9200,'Sofa','R900','property','Pretoria','sel@x.test','live')")
_r = Response(); b._establish_user_session("thandi@x.test", _r)
import re as _re
TOK = _re.search(r"ts_user=([^;]+)", _r.headers.get("set-cookie", "")).group(1)
rr = TC.post("/intros", json={"listing_id": 9200, "buyer_email": "Thandi@X.test", "buyer_name": "Thandi M", "message": "hi, call 082 555 1234"},
             headers={"X-Api-Key": "k"}, cookies={"ts_user": TOK})
print("     POST /intros ->", rr.status_code, str(rr.json())[:120])
row = q("SELECT buyer_email, message FROM intro_requests WHERE listing_id=9200")
check(rr.status_code == 200 and row and row[0]["buyer_email"] == "thandi@x.test", "accepted and stored under the canonical address (got %s)" % rr.status_code)
check(row and "555" not in (row[0]["message"] or ""), "AUD-024: the stored message carries no phone number")
check(bal("thandi@x.test") == 2, "her 1T is held from the right wallet (balance %s)" % bal("thandi@x.test"))

print("AUD-020 -- the console cannot grant a Pro seat or an oversized cap (RUL-048)")
x("INSERT INTO agencies (id, name, admin_email, verified, api_key) VALUES (51, 'A', 'adm@x.test', 1, 'k51')")
x("INSERT INTO agency_members (agency_id, agent_email, listing_cap, seat_paid, status, role) VALUES (51,'ag@x.test',10,0,'active','agent')")
x("INSERT INTO users (email, seller_tier, slot_limit) VALUES ('ag@x.test','agency',10)")
_r = Response(); b._establish_user_session("adm@x.test", _r)
import re as _re
ADM = _re.search(r"ts_user=([^;]+)", _r.headers.get("set-cookie", "")).group(1)
try:
    b.update_agent_cap(51, "ag@x.test", b._AgentCapUpdate(seat_paid=True), ts_user=ADM, x_admin_key=None); r = "allowed"
except HTTPException as e:
    r = e.status_code
check(r == 403, "seat_paid from a session caller is refused 403 (got %s)" % r)
b.update_agent_cap(51, "ag@x.test", b._AgentCapUpdate(listing_cap=100000), ts_user=ADM, x_admin_key=None)
u = q("SELECT seller_tier, slot_limit FROM users WHERE email='ag@x.test'")[0]
check(u["slot_limit"] == 10 and u["seller_tier"] == "agency", "cap 100000 is clamped to the free seat's 10, tier untouched (%s/%s)" % (u["slot_limit"], u["seller_tier"]))
b.update_agent_cap(51, "ag@x.test", b._AgentCapUpdate(seat_paid=True), x_admin_key="adm")
u = q("SELECT seller_tier, slot_limit FROM users WHERE email='ag@x.test'")[0]
check(u["seller_tier"] == "pro" and u["slot_limit"] == 20, "ops (admin key) can still record a paid seat")

print("AUD-021 -- the monthly reset never removes bought Tuppence (David, 4 Oct 2026)")
c = database.get_db()
launch_redemption._ensure_schema(c)
c.execute("INSERT INTO tuppence_monthly_grants (email, period, amount, badge_bonus, granted_at) VALUES ('pro@x.test','2026-09',10,0,'2026-09-01 00:00:00')")
for typ, amt, ts in (("monthly_allocation", 10, "2026-09-01 00:00:01"), ("intro_hold", -12, "2026-09-10 10:00:00"),
                     ("topup", 10, "2026-09-11 10:00:00")):
    c.execute("INSERT INTO transactions (user_email, type, amount, description, created_at) VALUES ('pro@x.test',?,?,?,?)", (typ, amt, typ, ts))
c.commit()
launch_redemption.grant_monthly_tuppence(c, "pro@x.test", "pro", period="2026-10"); c.commit(); c.close()
sw = q("SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE user_email='pro@x.test' AND type='grant_expiry'")[0]["s"]
check(sw == 0, "grant 10T, spent 12T, bought 10T: nothing swept (old rule swept 8T; got %s)" % sw)
c = database.get_db()
c.execute("INSERT INTO tuppence_monthly_grants (email, period, amount, badge_bonus, granted_at) VALUES ('pro2@x.test','2026-09',10,0,'2026-09-01 00:00:00')")
for typ, amt, ts in (("monthly_allocation", 10, "2026-09-01 00:00:01"), ("ai_service", -3, "2026-09-10 10:00:00"), ("topup", 5, "2026-09-12 10:00:00")):
    c.execute("INSERT INTO transactions (user_email, type, amount, description, created_at) VALUES ('pro2@x.test',?,?,?,?)", (typ, amt, typ, ts))
c.commit(); launch_redemption.grant_monthly_tuppence(c, "pro2@x.test", "pro", period="2026-10"); c.commit(); c.close()
sw = q("SELECT COALESCE(SUM(amount),0) AS s FROM transactions WHERE user_email='pro2@x.test' AND type='grant_expiry'")[0]["s"]
check(sw == -7, "grant 10T, spent 3T, bought 5T: exactly the 7T unused grant is swept (got %s)" % sw)

print("AUD-022 -- the webhook check works with the secret key alone")
import hmac, hashlib
payments.PAYSTACK_SECRET_KEY = "sk_test_probe"
body = b'{"event":"charge.success"}'
sig = hmac.new(b"sk_test_probe", body, hashlib.sha512).hexdigest()
check(payments.verify_webhook_signature(body, sig), "a correctly signed webhook passes with only the secret key set")
check(not payments.verify_webhook_signature(body, "é" + sig[1:]), "a non-ASCII header is refused, not a crash")

print("AUD-023 -- Zoom never sees the private street")
check("street" not in b._zoom.GEO_LEVELS["Property"] and "street" not in b._zoom.GEO_LEVELS["Services"], "no street level for Property or Services")
x("INSERT INTO listings (id, title, price, category, city, suburb, street_address, seller_email, listing_status) VALUES (9100,'Flat','R1','property','Pretoria','Hatfield','Flat 7 Duncan Court, 1090 Prospect St','sel@x.test','live')")
c = database.get_db(); rows, _ = b._zoom_candidates(c, "Property", "Pretoria", 1, "global"); c.close()
check(rows and all("street_address" not in r and "seller_email" not in r for r in rows), "candidate rows carry no street_address or seller_email")

print("AUD-024 + RUL-202 -- before accepting, no name and no contact details")
d = b._intro_for_viewer({"buyer_email": "t@x.test", "buyer_name": "Thandi Mokoena", "message": "call me on 082 555 1234", "status": "pending"}, "sel@x.test")
check(d["buyer_name"] == "" and "555" not in d["message"] and not d["buyer_email"], "seller read, RUL-202 no name: %r / %r" % (d["buyer_name"], d["message"]))

print("AUD-026 -- Squire text loses contact details")
check("555" not in b._squire_minimise("call me on 082 555 1234", False), "the approach / answer scrub removes a phone number")

print("AUD-027 -- photo addresses")
check(b._safe_client_photo_url("/media/../.env") is None and b._safe_client_photo_url("/media/a/../../x") is None, "'..' paths are dropped")
check(b._media_file_or_none("/media/../.env") is None, "migrate-photos refuses a path outside /media")
L = b.Listing(title="t", price="R5", category="cars", city="Pretoria", suburb="<img src=x onerror=1>", thumb_url="/media/../marketsquare.db")
check(L.thumb_url is None and "<" not in (L.suburb or ""), "the Listing model drops the bad path and the markup in suburb")

print("AUD-028 -- verification results cannot be self-awarded")
check(not b._client_may_name_signal("category.lm.id_ai_verified") and not b._client_may_name_signal("category.collectors.tx_5_14")
      and not b._client_may_name_signal("category.tutors.fide_ft") and b._client_may_name_signal("category.lm.formal_cert"),
      "id_ai_verified / tx_* / claim-only refused; a real certificate signal allowed")

print("AUD-029 -- AI answers leave as plain text")
check(all(hasattr(getattr(b, f), "__wrapped__") for f in ("ai_listing_rewrite", "ai_seller_audit", "ai_price_check", "ai_yield_calc", "ai_batch_card_listings")),
      "all five AI routes are wrapped")
check(b._plain_deep({"sa_context": "<img src=x onerror=1>ok", "actions": [{"step": "<b>x</b>"}]}) == {"sa_context": "ok", "actions": [{"step": "x"}]}, "nested strings are cleaned")

print("AUD-030 -- support form: one mailbox however spelled, three mailboxes per IP a day")
check(b._support_mailbox("Vic.Tim+2@Gmail.com") == b._support_mailbox("victim@gmail.com"), "victim+2@ / v.i.c.t.i.m@ count as one")
check([b._support_ip_rcpt_ok("9.9.9.9", m) for m in ("a@x", "b@x", "c@x", "d@x")] == [True, True, True, False], "a fourth mailbox from one IP gets no mail")

print("AUD-031 / AUD-054 -- agent lead and profile text is plain")
check(estate_agents._pt_deep({"listing": {"suburb": "<img src=x onerror=1>Hatfield"}}) == {"listing": {"suburb": "Hatfield"}}, "nested listing fields cleaned")

print("\n" + "=" * 70)
if fails:
    print("RESULT: %d CHECK(S) FAILED" % len(fails)); sys.exit(1)
print("RESULT: every Batch 2 server fix holds on a throwaway database"); sys.exit(0)
