#!/usr/bin/env python3
"""prove_audit_b3.py -- AUDIT-4OCT Batch 3 (4 Oct 2026): EXECUTE the remaining High server fixes against the real
bea_main.py on a throwaway SQLite file. Run: MS_API_KEY=k MS_ADMIN_KEY=adm python3 scripts/prove_audit_b3.py
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
DB = os.path.join(tempfile.mkdtemp(), "b3.db"); database.DB_PATH = DB
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


import io, re
from fastapi.testclient import TestClient
TC = TestClient(b.app)
def tok_for(email):
    _r = Response(); b._establish_user_session(email, _r)
    return re.search(r"ts_user=([^;]+)", _r.headers.get("set-cookie", "")).group(1)
for _t, _c, _ty in (("listings", "listing_status", "TEXT"), ("listings", "block_cause", "TEXT"), ("users", "id_name", "TEXT"),
                    ("listings", "status_changed_at", "TEXT"), ("listings", "auto_paused_intro_id", "INTEGER")):
    addcol(_t, _c, _ty)
from PIL import Image
_png = io.BytesIO(); Image.new("RGB", (64, 64), (200, 50, 50)).save(_png, "PNG"); PNG = _png.getvalue()

print("AUD-004 -- a photo with no advert needs a signed-in seller; scans are billed per account/draft")
r = TC.post("/listings/photo", files={"file": ("p.png", PNG, "image/png")}, headers={"X-Api-Key": "k"})
check(r.status_code == 401, "anonymous upload with only the app key is refused 401 (got %s)" % r.status_code)
class _Req:
    headers = {"x-forwarded-for": "9.9.9.1"}; client = None
check(b._photo_bill_who("me@x.test", "", None, _Req()) == "me@x.test", "a signed-in caller pays from her own allowance")
check(b._photo_bill_who(None, "victim@x.test", 77, _Req()) == "draft:77", "a draft-token composer is billed to the draft, not the typed address")
b._PHOTO_IP_LOG.clear(); codes = []
for _ in range(b._PHOTO_IP_MAX_PER_HOUR + 1):
    try:
        b._photo_bill_who(None, "", 77, _Req()); codes.append(200)
    except HTTPException as e:
        codes.append(e.status_code)
check(codes[-1] == 429 and codes.count(200) == b._PHOTO_IP_MAX_PER_HOUR, "token-only uploads are capped per IP per hour")
import inspect
check(not inspect.iscoroutinefunction(b.upload_listing_photo) and not inspect.iscoroutinefunction(b.upload_seller_document),
      "AUD-032: the upload handlers are plain functions (run in the threadpool, off the event loop)")

print("AUD-005 -- web comparables are capped per caller")
import asyncio
b._WEBCOMP_TRIES.clear(); b._WEBCOMP_MISS.clear()
b._WEBCOMP_MISS["odd thing"] = __import__("time").time()
check(asyncio.run(b._web_comps_band("Odd thing", "Pretoria", "ZA", "u@x.test")) is None, "an item that found nothing is not searched again for 6 hours")
b._WEBCOMP_TRIES["u@x.test"] = [__import__("time").time()] * b._WEBCOMP_DAILY_PER_USER
check(asyncio.run(b._web_comps_band("Another item", "Pretoria", "ZA", "u@x.test")) is None, "a caller past 8 searches today gets none")
check("_log_ai_spend(who or \"\", \"/listings/price-check#web-comps\"" in open("bea_main.py", encoding="utf-8").read(), "the spend is logged against the caller")

print("AUD-006 -- publish moves drafts (and resting/faded) only")
x("INSERT INTO users (email, eula_accepted_at, eula_version) VALUES ('pub@x.test', ?, '1.20')", now.isoformat())
for lid, st in ((8801, "blocked"), (8802, "archived"), (8803, "paused")):
    x("INSERT INTO listings (id, title, price, category, city, seller_email, listing_status) VALUES (?, 'T', 'R1', 'Collectors', 'Pretoria', 'pub@x.test', ?)", lid, st)
res = {}
for lid in (8801, 8802, 8803):
    try:
        b.publish_listing(lid, "pub@x.test"); res[lid] = 200
    except HTTPException as e:
        res[lid] = e.status_code
check(all(v in (403, 409) for v in res.values()), "blocked / archived / paused cannot be republished here (%s)" % res)
check(all(r["listing_status"] != "live" for r in q("SELECT listing_status FROM listings WHERE id IN (8801,8802,8803)")), "none of them went live")
x("INSERT INTO listings (id, title, price, category, city, seller_email, listing_status) VALUES (8804, 'D', 'R1', 'Collectors', 'Pretoria', 'pub@x.test', 'draft')")
try:
    b.publish_listing(8804, "pub@x.test"); r4 = 200
except HTTPException as e:
    r4 = e.status_code
check(r4 == 403, "while one advert is blocked, a draft cannot go live either (got %s)" % r4)

print("AUD-007 -- every agent gate credential waits for a person")
from estate_agents import VERTICALS
check(all(v["gate_signal"] in b._LEGAL_SIGNALS for v in VERTICALS.values()), "all %d go-live gate signals are in _LEGAL_SIGNALS" % len(VERTICALS))
check("category.travel.asata" not in b._LEGAL_SIGNALS and "category.services.trade_licence" not in b._LEGAL_SIGNALS, "the two misspelt ids are gone")

print("AUD-009 -- sign-in links live as long as their own expiry")
check("> 72 * 3600" not in open("bea_main.py", encoding="utf-8").read(), "no hard-coded 72-hour test left")

print("AUD-010 -- the comparables queries run")
x("INSERT INTO listings (id, title, price, category, city, seller_email, listing_status) VALUES (8810, 'Toyota Corolla 2018', 'R180 000', 'cars', 'Pretoria', 'a@x.test', 'live')")
x("INSERT INTO listings (id, title, price, category, city, seller_email, listing_status) VALUES (8811, 'Toyota Corolla 2019', 'R190 000', 'cars', 'Pretoria', 'b@x.test', 'live')")
x("INSERT INTO listings (id, title, price, category, city, seller_email, listing_status, is_demo) VALUES (8812, 'Toyota Corolla 2018', 'R1', 'cars', 'Pretoria', 'ex@trustsquare.co', 'live', 1)")
amts = b._comp_amounts("cars", "Pretoria", 9999)
check(sorted(amts) == [180000, 190000], "live real adverts are counted, examples are not (got %s)" % amts)

print("AUD-011 -- a vertical change takes an agent off live")
c = database.get_db(); estate_agents.init_schema(c)
c.execute("INSERT INTO agent_profiles (agent_email, anon_ref, headline, profile_status, vertical, created_at, updated_at) VALUES ('ag@x.test','R1','h','live','cars',?,?)", (now.isoformat(), now.isoformat()))
c.commit()
estate_agents._upsert_profile(c, estate_agents.AgentProfileIn(email="ag@x.test", vertical="institution")); c.commit()
st = c.execute("SELECT profile_status, vertical FROM agent_profiles WHERE agent_email='ag@x.test'").fetchone(); c.close()
check(st["profile_status"] == "draft" and st["vertical"] == "institution", "car dealer -> institution is back to draft (%s/%s)" % (st["profile_status"], st["vertical"]))
c = database.get_db()
check(not [a for a in estate_agents._rank_agents(c, "", "", 10, "institution") if a.get("anon_ref") == "R1"], "and is not offered as a live tutor"); c.close()

print("AUD-013 -- an invitation changes nobody's plan")
x("INSERT INTO agencies (id, name, admin_email, verified, api_key) VALUES (61, 'B', 'adm2@x.test', 0, 'k61')")
x("INSERT INTO users (email, seller_tier, slot_limit, billing_period_end) VALUES ('payer@x.test','pro',30,'2099-01-01T00:00:00Z')")
b.invite_agent(61, b._AgentInvite(email="payer@x.test", listing_cap=20))
u = q("SELECT seller_tier, slot_limit FROM users WHERE email='payer@x.test'")[0]
check((u["seller_tier"], u["slot_limit"]) == ("pro", 30), "a paying Pro seller invited by an agency keeps her plan (%s/%s)" % (u["seller_tier"], u["slot_limit"]))
b.invite_agent(61, b._AgentInvite(email="newbie@x.test", listing_cap=20))
u = q("SELECT slot_limit FROM users WHERE email='newbie@x.test'")[0]
check(u["slot_limit"] == 10, "a brand-new invitee gets the free seat's 10 (RUL-048), not 20 (got %s)" % u["slot_limit"])

print("AUD-014 -- the gate keeps a JSON photo list")
import security_gate as g
check(json.loads(g._url_field('["https://a.co/1.jpg","javascript:alert(1)","/media/x.jpg"]')) == ["https://a.co/1.jpg", "/media/x.jpg"], "good links kept, a script link dropped")

print("AUD-033 / AUD-034 -- no push or AI work under the write lock")
src = open("bea_main.py", encoding="utf-8").read()
check("_pushes.append((buyer_token, new_match_id))" in src and "for _bt, _mid in _pushes:" in src, "pushes go out after the match job commits")
check("conn.commit()   # AUD-034" in src, "the agency import commits per advert")

print("\n" + "=" * 70)
if fails:
    print("RESULT: %d CHECK(S) FAILED" % len(fails)); sys.exit(1)
print("RESULT: every Batch 3 server fix holds on a throwaway database"); sys.exit(0)
