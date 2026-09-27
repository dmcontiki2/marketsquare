"""CIRCLE-CAPS-1 + KEEP-CHOICE-1 (RUL-176 standard) behaviour test on a TEMP database -- never the live one.
Run from anywhere:  MS_API_KEY=test JWT_SECRET=test python3 scripts/test_circle_caps.py
Needs the BEA's pip deps (fastapi, boto3, pywebpush, PyJWT, httpx). It chdirs into a temp folder
first, because importing bea_main opens some side databases by RELATIVE path -- run from the repo
root it once left a 0-byte marketsquare.db + journal on the Projects mount (27 Sep 2026)."""
import os, sys, tempfile, sqlite3
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _REPO)
os.chdir(tempfile.mkdtemp(prefix="circle_test_"))
_tmp = tempfile.mkstemp(suffix=".db")[1]
import database; database.DB_PATH = _tmp
_mk = os.makedirs
def _mk2(p, *a, **k):
    if str(p).startswith("/var/www"): return None
    return _mk(p, *a, **k)
os.makedirs = _mk2
import starlette.staticfiles as _sf
_orig = _sf.StaticFiles.__init__
def _init(self, *a, **k):
    k["check_dir"] = False; return _orig(self, *a, **k)
_sf.StaticFiles.__init__ = _init
import bea_main as B
from fastapi import HTTPException
B._buzz_who = lambda ts, passed, ctx="", require_accept=True: (passed or "").lower()
B._actor = lambda ts, passed, ctx="", admin_key=None: (passed or "").lower()
B._push_to_seller = lambda *a, **k: 1
def q(sql, args=()):
    k = sqlite3.connect(_tmp); k.row_factory = sqlite3.Row
    r = k.execute(sql, args).fetchall(); k.commit(); k.close(); return r
SUE = "sue@x.co"
q("INSERT OR IGNORE INTO users (email) VALUES (?)", (SUE,))
q("UPDATE users SET seller_tier='free', slot_limit=2 WHERE email=?", (SUE,))
q("INSERT OR IGNORE INTO launch_switches (id) VALUES (1)")
def setflag(v):
    before = q("SELECT circle_caps FROM launch_switches WHERE id=1")[0]["circle_caps"]
    q("UPDATE launch_switches SET circle_caps=? WHERE id=1", (v,))
    if v and not before:          # what POST /admin/flags does on arming
        k = database.get_db(); B._circle_grandfather_all(k); k.commit(); k.close()
def pair(i, owner=SUE):
    r = B.buzz_pair_create(B.BuzzPairReq(from_email=owner, to_email="c%d@x.co" % i), _key="k", ts_user=None)
    q("UPDATE buzz_pairs SET a_allows=1, b_allows=1")      # both switched on, as in real use
    return r
def st():
    k = database.get_db(); r = B._circle_status(k, SUE); k.close(); return r
def send(frm, to):
    return B.buzz_send(B.BuzzSendReq(from_email=frm, to_email=to, text="hi"), B.BackgroundTasks(), _key="k", ts_user=None)
def refused(fn):
    try: fn(); return None
    except HTTPException as e: return e.detail
# --- regulars ---
setflag(0)
for i in range(12): pair(i)
s = st(); assert s["used"] == 12 and not s["full"], s
setflag(1)                                   # arming grandfathers her at 12
s = st(); assert s["allowance"] == 12 and not s["resting_ids"] and s["full"], s
assert refused(lambda: pair(99)), "added over the grandfathered allowance"
send(SUE, "c11@x.co")                        # nobody cut off by the switch
q("UPDATE buzz_pairs SET closed_by=? WHERE id IN (1,2,3)", (SUE,))
s = st(); assert s["allowance"] == 10 and s["used"] == 9, s   # grandfather only shrinks
pair(50); assert refused(lambda: pair(51)), "went above plan after grandfather shrank"
q("UPDATE users SET seller_tier='starter', slot_limit=10 WHERE email=?", (SUE,))
for i in range(60, 90): pair(i)             # 40 regulars on Starter
for i in (61, 62): send(SUE, "c%d@x.co" % i)   # recently buzzed
# downgrade to Free through the standard path: pending -> applied
q("UPDATE users SET pending_downgrade_tier='free', billing_period_end='2000-01-01T00:00:00Z' WHERE email=?", (SUE,))
out = B.buzz_keep(B.BuzzKeepReq(email=SUE, keep=["c70@x.co", "c71@x.co", "c72@x.co"]), _key="k", ts_user=None)
assert out["kept"] == 3, out
B._apply_pending_downgrades()
s = st(); assert s["tier"] == "free" and s["allowance"] == 10 and len(s["resting_ids"]) == 30, s
act = [r for r in B._circle_rows(database.get_db(), SUE)][:10]
names = [(r["b_email"] if r["a_email"] == SUE else r["a_email"]) for r in act]
assert names[:3] == sorted(names[:3]) or set(names[:3]) == {"c70@x.co", "c71@x.co", "c72@x.co"}, names
assert {"c61@x.co", "c62@x.co"} <= set(names), names          # most recently buzzed stay
rid = s["resting_ids"][-1]
rr = q("SELECT a_email, b_email FROM buzz_pairs WHERE id=?", (rid,))[0]
RST = rr["b_email"] if rr["a_email"] == SUE else rr["a_email"]
assert refused(lambda: send(SUE, RST)).startswith("Resting"), "resting could be buzzed"
send(RST, SUE)                                                  # they can still buzz her
assert refused(lambda: B.buzz_keep(B.BuzzKeepReq(email=SUE, keep=["c%d@x.co" % i for i in range(60, 71)]), _key="k", ts_user=None))
B.buzz_keep(B.BuzzKeepReq(email=SUE, keep=[RST]), _key="k", ts_user=None); send(SUE, RST)   # swap works
pl = B.buzz_pairs(email=SUE, _key="k", ts_user=None); assert sum(1 for p in pl if p["resting"]) == 30
q("UPDATE users SET seller_tier='pro', slot_limit=30 WHERE email=?", (SUE,))
assert not st()["resting_ids"], "upgrade did not wake everyone"
setflag(0); assert not st()["resting_ids"] and not st()["full"]
print("regulars OK")
# --- listings ---
T = "tia@x.co"
q("INSERT OR IGNORE INTO users (email) VALUES (?)", (T,))
q("UPDATE users SET seller_tier='starter', slot_limit=10, billing_period_end='2099-01-01T00:00:00Z' WHERE email=?", (T,))
ids = []
for i in range(8):
    k = sqlite3.connect(_tmp); c = k.execute("INSERT INTO listings (title, category, city, seller_email, listing_status, published_at) VALUES (?,?,?,?,?,?)",
        ("Advert %d" % i, "services", "Pretoria", T, "live", "2026-09-%02dT10:00:00Z" % (10 + i))); ids.append(c.lastrowid); k.commit(); k.close()
k = sqlite3.connect(_tmp); k.execute("INSERT INTO listings (title, category, city, seller_email, listing_status) VALUES ('draft', 'services', 'Pretoria', ?, 'draft')", (T,)); k.commit(); k.close()
r = B.downgrade_to_free(T); assert r.get("pending_downgrade_tier") == "free", r   # paid time left -> scheduled
assert B.listings_keep(T, B.ListingKeepReq(keep=[ids[0], ids[1]]), _key="k", ts_user=None)["applied"] is False
q("UPDATE users SET billing_period_end='2000-01-01T00:00:00Z' WHERE email=?", (T,))
B._apply_pending_downgrades()
rows = {r["id"]: r["listing_status"] for r in q("SELECT id, listing_status FROM listings WHERE seller_email=?", (T,))}
live = [i for i in ids if rows[i] == "live"]; rest = [i for i in ids if rows[i] == "resting"]
assert live == [ids[0], ids[1]] and len(rest) == 6, (live, rest)
assert "draft" in rows.values(), "draft was touched"
sub = B.get_user_subscription(T); assert sub["slots_used"] == 2 and sub["listings_resting"] == 6, sub
v = B.listings_keep_view(T, _key="k", ts_user=None); assert len(v["listings"]) == 8
x = B.listings_keep(T, B.ListingKeepReq(keep=[ids[7], ids[0]]), _key="k", ts_user=None); assert x["applied"], x   # swap
rows = {r["id"]: r["listing_status"] for r in q("SELECT id, listing_status FROM listings WHERE seller_email=?", (T,))}
assert rows[ids[7]] == "live" and rows[ids[1]] == "resting", rows
assert refused(lambda: B.listings_keep(T, B.ListingKeepReq(keep=ids[:3]), _key="k", ts_user=None))
q("UPDATE users SET seller_tier='free', slot_limit=2, billing_period_end=NULL WHERE email=?", (T,))
k = database.get_db(); B._plan_changed(k, T, "starter", lowered=False); k.commit(); k.close()
rows = {r["id"]: r["listing_status"] for r in q("SELECT id, listing_status FROM listings WHERE seller_email=?", (T,))}
assert all(rows[i] == "live" for i in ids), rows
print("listings OK")
print("flags circle:", B._flags_payload({"circle_caps": 1})["effective"]["circle_caps"], B._flags_payload({})["circle_caps"])
print("ALL OK")
