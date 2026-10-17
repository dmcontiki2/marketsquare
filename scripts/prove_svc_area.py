#!/usr/bin/env python3
"""prove_svc_area.py -- SVC-AREA-1 (RUL-237, 17 Oct 2026): EXECUTE the service-area lane against the real bea_main.py,
imported with a throwaway SQLite file (never the live database). OpenStreetMap is a stand-in: bea_main.svc_area.geocode and
.street_lines answer from a fixture (Witch Hazel Avenue's real line through Technopark, Centurion), so the run
needs no network.

What it proves:
  A  only the person who listed it can set where they work; the area files the advert under the suburbs it touches
  B  LOCKED: the feed and the Zoom funnel hide the advert from a stranger we do not know to be inside; a buyer who picked
     a suburb the area touches, or whose phone is inside, sees it; the owner always sees it; a direct link always opens
  C  the area check answers inside / how far outside, for a point or an address
  D  LOCKED: a request for work outside the stretch, or with no place given, is refused BEFORE anything is held
     (no intro row, no ledger row); a request inside passes the area gate
  E  UNLOCKED: the advert shows city-wide again and an outside request is not refused by the area gate
Run: python3 scripts/prove_svc_area.py
"""
import os, sys, json, tempfile
from datetime import datetime, timedelta, timezone
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO); sys.path.insert(0, REPO)
os.environ.setdefault("MS_API_KEY", "k"); os.environ.setdefault("MS_ADMIN_KEY", "adm")
os.environ.setdefault("MS_JWT_SECRET", "test-only-" + os.urandom(8).hex())
for k in ("RESEND_API_KEY", "PAYSTACK_WEBHOOK_SECRET", "GMAIL_APP_PASSWORD", "PAYSTACK_SECRET_KEY"):
    os.environ.pop(k, None)
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k["check_dir"] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
import database
DB = os.path.join(tempfile.mkdtemp(), "svcarea.db"); database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(os.path.dirname(DB), "flights.db")
# Witch Hazel Avenue, NE end -> SW end (OSM ways 4935722 .. 157112936, thinned)
WH = [[-25.87377, 28.18948], [-25.87241, 28.18842], [-25.87375, 28.18236], [-25.87556, 28.18084], [-25.87709, 28.18033],
      [-25.87811, 28.17784], [-25.87788, 28.17573], [-25.87858, 28.17343], [-25.87962, 28.17242], [-25.88106, 28.17131],
      [-25.88212, 28.17058], [-25.884, 28.1697], [-25.88523, 28.16935], [-25.88704, 28.17071], [-25.88791, 28.17258],
      [-25.88968, 28.17405]]
PLACES = {"technopark, centurion": (-25.8721, 28.1852), "witch hazel avenue 75, pretoria": (-25.8740, 28.1830),
          "irene village mall, pretoria": (-25.8836, 28.2196)}
def _geo(q, cc="ZA"):
    k = (q or "").strip().lower()
    for name, pt in PLACES.items():
        if k.startswith(name) or k == name:
            return pt[0], pt[1], name
    return None, None, ""
def _lines(street, lat, lng, r):
    if "hazel" not in (street or "").lower():
        return []
    keep = r + svc_area.CENTRE_SLACK_M + 40
    out, cur = [], []
    # densify so the cut is fair
    pts = []
    for a, b in zip(WH, WH[1:]):
        for i in range(10):
            t = i / 10.0; pts.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
    pts.append(WH[-1])
    for p in pts:
        if svc_area.haversine_m(p[0], p[1], lat, lng) <= keep: cur.append([round(p[0], 5), round(p[1], 5)])
        elif cur: out.append(cur); cur = []
    if cur: out.append(cur)
    return out
import bea_main as b
svc_area = b.svc_area          # SVC-AREA-1 lives inside main.py
svc_area.geocode = _geo
svc_area.street_lines = _lines
from fastapi.testclient import TestClient
import jwt as _jwt
NOW = datetime.now(timezone.utc)
b._send_system_email = lambda *a, **k: "sent"
b._push_to_seller = lambda *a, **k: 1
fails = []
def check(ok, msg):
    print(("  [OK] " if ok else "  [X]  ") + msg)
    if not ok: fails.append(msg)
def q(sql, *p):
    c = database.get_db(); r = c.execute(sql, p).fetchall(); c.close(); return r
def x(sql, *p):
    c = database.get_db(); c.execute(sql, p); c.commit(); c.close()
def cols(t):
    return [r["name"] for r in q("PRAGMA table_info(%s)" % t)]
C = TestClient(b.app, raise_server_exceptions=False)
H = {"X-Api-Key": "k"}
def cookie(email):
    return {"ts_user": _jwt.encode({"scope": "user", "sub": email, "iat": NOW, "exp": NOW + timedelta(hours=2)},
                                   b._JWT_SECRET, algorithm=b._JWT_ALGO)}
SELLER, BUYER, OTHER = "worker@x.test", "office@x.test", "stranger@x.test"
# geography: Pretoria (47) and the suburbs round Witch Hazel Avenue, plus one far away
if "country" not in cols("listings"):   # live has it (added outside init); the feed's nationwide branch reads it
    x("ALTER TABLE listings ADD COLUMN country TEXT")
PRE = q("SELECT id FROM geo_cities WHERE name = 'Pretoria' LIMIT 1")[0]["id"]   # the init seeds ZA geography itself
have = {r["name"] for r in q("SELECT name FROM geo_suburbs WHERE city_id = ?", PRE)}
for name, la, ln in (("Zwartkop", -25.8698, 28.18027), ("Highveld", -25.8817, 28.19315), ("Centurion", -25.85891, 28.18577),
                     ("Lynnwood", -25.7611, 28.2636)):   # as on the live box
    if name in have:
        x("UPDATE geo_suburbs SET lat = ?, lng = ? WHERE name = ? AND city_id = ?", la, ln, name, PRE)
    else:
        x("INSERT INTO geo_suburbs (name, city_id, active, lat, lng) VALUES (?,?,?,?,?)", name, PRE, 1, la, ln)
for em in (SELLER, BUYER, OTHER):
    x("INSERT INTO users (email, eula_accepted_at) VALUES (?, ?)", em, NOW.strftime("%Y-%m-%dT%H:%M:%SZ"))
x("INSERT INTO listings (title, price, category, city, area, suburb, geo_city_id, description, seller_email, listing_status, "
  "is_demo, service_type, trust_score) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
  "Hand car wash at your workplace", "R80", "Services", "Pretoria", "Pretoria", "Pretoria", PRE, "Washed by hand.", SELLER,
  "live", 0, "Car washer", 80)
LID = q("SELECT id FROM listings WHERE seller_email = ?", SELLER)[0]["id"]
def feed(email=None, **kw):
    p = {"city": "Pretoria", "category": "Services"}; p.update(kw)
    r = C.get("/listings", params=p, headers=H, cookies=cookie(email) if email else None)
    rows = r.json() if r.status_code == 200 else []
    rows = rows.get("items", rows) if isinstance(rows, dict) else rows
    return [z for z in rows if z.get("id") == LID]
def zoom_ids(**kw):
    p = {"category": "Services", "city": "Pretoria"}; p.update(kw)
    r = C.get("/zoom/next", params=p, headers=H)
    return (r.json() or {}).get("ids", []) if r.status_code == 200 else None
INSIDE = (-25.8745, 28.1828)       # an office a few doors from the centre, on the street
DOWN = (-25.8897, 28.1741)         # the same street, 2 km down (Petrus cannot walk there)
FAR = (-25.8836, 28.2196)          # Irene, another suburb

print("A  setting the area")
r = C.post("/listings/%d/service-area" % LID, json={"street": "Witch-Hazel Avenue", "place": "Technopark, Centurion",
           "lat": -25.87425, "lng": 28.18358, "radius_m": 700, "lock": True}, headers=H, cookies=cookie(OTHER))
check(r.status_code == 403, "a stranger cannot set someone else's area (%s)" % r.status_code)
r = C.post("/listings/%d/service-area" % LID, json={"street": "Witch-Hazel Avenue", "place": "Technopark, Centurion",
           "lat": -25.87425, "lng": 28.18358, "radius_m": 700, "lock": True}, headers=H, cookies=cookie(SELLER))
a = (r.json() or {}).get("area") or {}
check(r.status_code == 200 and a.get("kind") == "street" and a.get("lock") is True, "the owner sets street + stretch + lock (%s)" % r.status_code)
check("Highveld" in (a.get("suburbs") or []) and "Lynnwood" not in (a.get("suburbs") or []), "files under the suburbs it touches: %s" % a.get("suburbs"))
check(a.get("label") == "Witch-Hazel Avenue, Technopark, Centurion", "label reads %r" % a.get("label"))
row = q("SELECT suburb, area, area_lock FROM listings WHERE id = ?", LID)[0]
check(row["area_lock"] == 1 and row["suburb"] in a["suburbs"], "listing row: suburb %s, area %s, lock %s" % (row["suburb"], row["area"], row["area_lock"]))
r = C.post("/listings/%d/service-area" % LID, json={"street": "Nowhere Road", "place": "Technopark, Centurion", "radius_m": 500},
           headers=H, cookies=cookie(SELLER))
check(r.status_code == 422 and "could not find" in r.text.lower(), "an unknown street is refused with a sentence (%s)" % r.status_code)

print("B  who sees it while locked")
check(not feed(), "city-wide stranger: hidden")
check(not feed(OTHER), "signed-in stranger, no location: hidden")
check(bool(feed(suburb="Highveld")), "buyer who picked Highveld: shown")
check(bool(feed(near="%f,%f" % INSIDE)), "buyer whose phone is on the street: shown")
check(not feed(near="%f,%f" % FAR), "buyer whose phone is in Irene: hidden")
check(bool(feed(SELLER)), "the owner: shown")
z0, z1 = zoom_ids(), zoom_ids(suburb="Highveld")
check(z0 is not None and LID not in z0, "Zoom funnel, stranger: hidden")
check(z1 is not None and LID in z1, "Zoom funnel, Highveld: shown")
d = C.get("/listings/%d" % LID, headers=H)
check(d.status_code == 200 and (d.json().get("svc_area") or {}).get("lock") is True and d.json()["svc_area"].get("lines"),
      "a direct link opens and carries the area to draw")
check("seller_email" not in d.json(), "the direct link still carries no seller identity")

print("C  area check")
c1 = C.get("/listings/%d/area-check" % LID, params={"lat": INSIDE[0], "lng": INSIDE[1]}, headers=H).json()
c2 = C.get("/listings/%d/area-check" % LID, params={"lat": DOWN[0], "lng": DOWN[1]}, headers=H).json()
c3 = C.get("/listings/%d/area-check" % LID, params={"address": "Irene Village Mall"}, headers=H).json()
c4 = C.get("/listings/%d/area-check" % LID, params={"address": "somewhere unknown"}, headers=H).json()
c5 = C.get("/listings/%d/area-check" % LID, params={"address": "Technopark, Centurion 12"}, headers=H).json()
check(c5.get("found") is True, "an address with a house number OSM does not know falls back to the street")
check(c1.get("inside") is True, "office on the street: inside")
check(c2.get("inside") is False and "km" in (c2.get("outside") or ""), "2 km down the street: outside by %s" % c2.get("outside"))
check(c3.get("inside") is False, "an address in Irene: outside by %s" % c3.get("outside"))
check(c4.get("found") is False, "an address we cannot find says so")

print("D  requests while locked")
def intro(**kw):
    body = {"listing_id": LID, "buyer_email": BUYER, "buyer_name": "Office", "message": "Weekly wash please", "unverified_ack": True}
    body.update(kw)
    return C.post("/intros", json=body, headers=H, cookies=cookie(BUYER))
n0 = q("SELECT COUNT(*) AS n FROM intro_requests")[0]["n"]
r = intro(job_lat=DOWN[0], job_lng=DOWN[1])
check(r.status_code == 409 and "outside" in r.text and "Nothing was charged" in r.text, "outside the stretch: refused (%s %s)" % (r.status_code, r.text[:120]))
r = intro()
check(r.status_code == 409 and "Say where the work is" in r.text, "no place given: refused (%s)" % r.status_code)
r = intro(job_address="Irene Village Mall")
check(r.status_code == 409 and "outside" in r.text, "an outside address: refused (%s)" % r.status_code)
check(q("SELECT COUNT(*) AS n FROM intro_requests")[0]["n"] == n0, "nothing held: no introduction row was written")
r = intro(job_lat=INSIDE[0], job_lng=INSIDE[1])
check(not (r.status_code == 409 and ("outside" in r.text or "where the work is" in r.text)), "inside: passes the area gate (%s %s)" % (r.status_code, r.text[:100]))

print("E  unlocked")
r = C.post("/listings/%d/service-area" % LID, json={"lock": False}, headers=H, cookies=cookie(SELLER))
check(r.status_code == 200 and (r.json().get("area") or {}).get("lock") is False and (r.json().get("area") or {}).get("lines"),
      "switching the lock off keeps the area")
check(bool(feed()), "city-wide stranger: shown again")
r = intro(job_lat=DOWN[0], job_lng=DOWN[1])
check(not (r.status_code == 409 and "outside" in r.text), "an outside request is not refused by the area gate (%s)" % r.status_code)
r = C.post("/listings/%d/service-area" % LID, json={"clear": True}, headers=H, cookies=cookie(SELLER))
check(r.status_code == 200 and not q("SELECT svc_area FROM listings WHERE id = ?", LID)[0]["svc_area"], "clear removes the area")

print("\n%s -- %d failure(s)" % ("PASS" if not fails else "FAIL", len(fails)))
sys.exit(1 if fails else 0)
