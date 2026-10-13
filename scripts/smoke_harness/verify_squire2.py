"""verify_squire2.py -- SQUIRE-2 Phase 1 acceptance (SQUIRE_2_BUILD_BRIEF.md s5) against the REAL BEA.

Boots bea_main on a THROWAWAY database (RIG_DIR = a copy of the app whose /var/www paths were rewritten to a
scratch root, the same rig-only rewrite rig_sync.sh does for BEA_URL) and drives it over HTTP with real session
cookies, so the security gate, the Pro gate and the flag-dark switch all run. The free data feeds are replaced by
fixed fakes (no network): the point is what Squire DOES with data, not whether a public API is up today.

Run:  RIG_DIR=~/rig RIG_DB=~/rigroot/var/www/marketsquare/marketsquare.db python3 verify_squire2.py
Exit 0 = every acceptance item holds.  The rendered half is verify_squire2_render.mjs.
"""
import asyncio, json, os, sys, time, tempfile

os.environ.setdefault("MS_API_KEY", "rigapikey_rig")
os.environ.setdefault("MS_REVIEW_SECRET", "rigsecret_rigsecret_rigsecret_rigsecret")
os.environ.setdefault("MS_JWT_SECRET", "rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt")
os.environ.setdefault("MS_ADMIN_KEY", "rigadminkey")
os.environ["SQUIRE_WATCH_ENABLED"] = "0"; os.environ["SQUIRE2_JOBS_ENABLED"] = "0"
RIG = os.path.expanduser(os.environ.get("RIG_DIR", "~/rig"))
sys.path.insert(0, RIG); os.chdir(RIG)
FLAGS = os.path.join(tempfile.mkdtemp(), "feature_flags.json")
os.environ["FEATURE_FLAGS_PATH"] = FLAGS
json.dump({"paid_tiers_enabled": False}, open(FLAGS, "w"))          # the shipped default: squire_pro_pa OFF
import database
DB = os.path.expanduser(os.environ.get("RIG_DB", "~/rigroot/var/www/marketsquare/marketsquare.db"))
if os.path.exists(DB) and os.environ.get("RIG_KEEP_DB") != "1":
    os.remove(DB)
database.DB_PATH = DB
import bea_main as B
import jwt
import feature_flags
from fastapi.testclient import TestClient

FAILS = []
def check(c, m):
    if not c:
        FAILS.append(m); print("  FAIL:", m)
def tok(em):
    return jwt.encode({"scope": "user", "sub": em, "exp": int(time.time()) + 86400}, os.environ["MS_JWT_SECRET"], algorithm="HS256")
REVIEW = jwt.encode({"scope": "review", "exp": int(time.time()) + 86400}, os.environ["MS_REVIEW_SECRET"], algorithm="HS256")
c = TestClient(B.app, base_url="http://127.0.0.1")
def call(method, path, em=None, body=None, admin=False):
    c.cookies.clear(); c.cookies.set("ts_review", REVIEW)
    if em:
        c.cookies.set("ts_user", tok(em))
    h = {"X-Admin-Key": "rigadminkey"} if admin else {}
    r = c.request(method, path, json=body, headers=h)
    try:
        return r.status_code, r.json()
    except Exception:
        return r.status_code, None

PRO, STARTER, SELLER, SELLER2, BUYER2 = "pro@rig.test", "starter@rig.test", "seller@rig.test", "seller2@rig.test", "want@rig.test"
conn = database.get_db()
B._squire_ensure(conn)
for em, tier in ((PRO, "pro"), (STARTER, "starter"), (SELLER, "free"), (SELLER2, "free"), (BUYER2, "free")):
    conn.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (em,))
    conn.execute("UPDATE users SET seller_tier=?, eula_accepted_at=CURRENT_TIMESTAMP, slot_limit=30, buyer_token=? WHERE email=?", (tier, "bt_" + em.split("@")[0], em))
conn.execute("INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'grant', 20, 'rig')", (PRO,))
if not conn.execute("SELECT 1 FROM geo_cities WHERE LOWER(name)='leeds'").fetchone():
    conn.execute("INSERT OR IGNORE INTO geo_countries (iso2, name) VALUES ('GB', 'United Kingdom')") if conn.execute("SELECT name FROM sqlite_master WHERE name='geo_countries'").fetchone() else None
    rid = conn.execute("INSERT INTO geo_regions (name, country_iso2) VALUES ('West Yorkshire', 'GB')").lastrowid
    conn.execute("INSERT INTO geo_cities (name, region_id, country_iso2) VALUES ('Leeds', ?, 'GB')", (rid,))
def listing(title, price, cat, city, seller, suburb=None, status="live", country=None):
    cur = conn.execute("INSERT INTO listings (title, price, category, city, seller_email, listing_status, published_at, trust_score) VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP,60)",
                       (title, str(price), cat, city, seller, status))
    lid = cur.lastrowid
    cols = {r[1] for r in conn.execute("PRAGMA table_info(listings)").fetchall()}
    if "price_num" in cols:
        conn.execute("UPDATE listings SET price_num=? WHERE id=?", (float(price), lid))
    if suburb and "suburb" in cols:
        conn.execute("UPDATE listings SET suburb=? WHERE id=?", (suburb, lid))
    if country and "country" in cols:
        conn.execute("UPDATE listings SET country=? WHERE id=?", (country, lid))
    return lid
# 30 card names for the lists; listings of a few of them
CARDS = {("Card %02d" % i): ("sf-%02d" % i, 10.0) for i in range(30)}
CARDS["Lightning Bolt"] = ("sf-bolt", 4.0)
NM = {"Card 00": 9.0}                      # only Card 00 has a condition-verified Near Mint price
bolt_l = listing("Lightning Bolt M10 near mint", 3.0, "collectables", "Pretoria", SELLER)
listing("Card 01 foil", 15.0, "collectables", "Pretoria", SELLER)
prop_ids = [listing("3-bed house, Headingley", p, "property", "Leeds", SELLER, suburb=s, country="United Kingdom")
            for p, s in ((260000, "Headingley"), (240000, "Hyde Park"), (300000, "Roundhay"))]
# demand: an explicit want-list and a Zoom Watch for Card 05 (the sell list will hear about it)
conn.execute("INSERT INTO wishlist_signals (buyer_token, signal_type, raw_text, category, expires_at) VALUES ('bt_want','explicit','Card 05 for my deck','collectables','2099-01-01 00:00:00')")
conn.execute("CREATE TABLE IF NOT EXISTS zoom_watches (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT NOT NULL, category TEXT NOT NULL, city TEXT, path TEXT NOT NULL, label TEXT, created_at TEXT NOT NULL, UNIQUE(email, category, city, path))")
conn.execute("INSERT INTO zoom_watches (email, category, city, path, label, created_at) VALUES (?, 'Collectors', 'Pretoria', 'q:Card%2006', 'Card 06', '2026-10-01T00:00:00Z')", (BUYER2,))
conn.commit()

# fakes for every network lane
async def f_lookup(name, set_code=""):
    v = CARDS.get(name)
    return {"id": v[0], "name": name, "set": (set_code or "M10").upper(), "usd": v[1]} if v else None
async def f_price(sid):
    for n, (i, usd) in CARDS.items():
        if i == sid:
            return {"usd": usd, "name": n}
    return None
async def f_nm(name, set_code=""):
    return {"value": NM[name], "currency": "USD"} if name in NM else None
async def f_lr(town, **kw):
    return {"value": 280000.0, "n": 64, "provenance": "HM Land Registry Price Paid - 64 sold in Leeds (median)"} if town.lower() == "leeds" else None
async def f_crime(lat, lng, **kw): return {"count": 90, "provenance": "data.police.uk"}
async def f_flood(lat, lng, **kw): return {"in_area": False, "provenance": "Environment Agency"}
async def f_epc(pc, hint="", **kw): return {"rating": "C", "floor_area": 92, "age_band": "1930-1949", "provenance": "UK EPC register"}
async def f_rate(**kw): return {"pct": 3.75, "provenance": "Bank of England Bank Rate"}
PUSHES, MAILS = [], []
B._squire2_lookup_card = f_lookup; B.scryfall_price_by_id = f_price; B._squire2_nm_price = f_nm
B.tier_resolvers.uk_land_registry_median = f_lr
B.tier_resolvers.uk_market_rent = lambda region: {"value": 1250.0, "provenance": "ONS/VOA private-rental median"}
B._sq2f.police_crime_count = f_crime; B._sq2f.ea_flood_area = f_flood; B._sq2f.epc_lookup = f_epc; B._sq2f.boe_bank_rate = f_rate
B._suburb_point_for_listing = lambda lid, write=True: (53.82, -1.58)
B._push_to_seller = lambda conn, em, t, b, timeout=8: (PUSHES.append((em, t)) or 1)
B._send_system_email = lambda to, subj, html: (MAILS.append((to, subj, html)) or "sent")
B._sq2f._get_bytes = lambda url, timeout=60.0: None          # no MTGJSON download in the harness

def arm(v):
    conn.execute("UPDATE launch_switches SET baseline_q4=? WHERE id=1", (v,)); conn.commit()
    try:
        B._bit_cache_clear()
    except Exception:
        pass
    time.sleep(1.2)

print("0. dark: everything 404 until baseline_q4")
arm(0)
s, _ = call("GET", "/squire/brief/1/advice?email=" + PRO, PRO)
check(s == 404, "advice answered %s while dark" % s)
arm(1)
check(B._squire_on(), "baseline_q4 armed but _squire_on() is False")

print("1. Pro-only: Starter refused")
s, _ = call("POST", "/squire/brief", STARTER, {"email": STARTER, "kind": "sell", "cards": "Card 01 | M10 | 12 | 1"})
check(s == 403, "Starter got a card brief: %s" % s)

print("1. 30-card SELL list + 30-card BUY list -> one advice line each, pass/warn on the user's own rule")
sell_txt = "\n".join("Card %02d | M10 | %s | 1" % (i, "12.50" if i % 2 else "11.00") for i in range(30)) + "\nLightnin Blot | M10 | 3 | 1"
s, d = call("POST", "/squire/brief", PRO, {"email": PRO, "kind": "sell", "rules": {"sell_margin_pct": 20}, "cards": sell_txt})
check(s == 200 and d.get("lines") == 31, "sell brief not created: %s %s" % (s, str(d)[:200]))
sell_id = d["brief_id"]
adv = d["advice"]
check(len(adv) == 31, "advice lines %d != 31" % len(adv))
st = {a["status"] for a in adv[:30]}
check(st == {"pass", "warn"}, "sell advice statuses %s" % st)
check(any(u["text"].startswith("Lightnin") for u in d["unresolved"]), "the unidentifiable card was not returned: %s" % d.get("unresolved"))
check(all(a["status"] == "unresolved" for a in adv if a["name"].startswith("Lightnin")), "an unidentifiable card was guessed")
buy_txt = "\n".join("Card %02d | M10 | %s | 1" % (i, "7.00" if i % 2 else "9.50") for i in range(30))
s, d = call("POST", "/squire/brief", PRO, {"email": PRO, "kind": "buy", "rules": {"buy_discount_pct": 20, "min_condition": "NM"}, "cards": buy_txt + "\nLightning Bolt | M10 | 3.50 | 1"})
check(s == 200 and len(d.get("advice", [])) == 31, "buy brief advice %s" % (str(d)[:200]))
buy_id = d["brief_id"]
by = {a["name"]: a for a in d["advice"]}
print("   sell:", {k: sum(1 for a in adv if a["status"] == k) for k in ("pass", "warn", "unresolved")},
      "| buy:", {k: sum(1 for a in d["advice"] if a["status"] == k) for k in ("pass", "warn", "unverified")})
print("2. NM rule never 'met' from a price that is not condition-verified")
check(by["Card 01"]["status"] == "unverified", "Card 01 (no NM price) was judged: %s" % by["Card 01"])
check(by["Card 00"]["condition_verified"] is True, "Card 00 NM price not used")
s, d = call("GET", "/squire/brief/%d/advice?email=%s" % (buy_id, PRO), PRO)
check(s == 200 and d["counts"].get("pass", 0) + d["counts"].get("warn", 0) <= 1, "advice endpoint counts wrong: %s" % d.get("counts"))
s, d = call("GET", "/squire/brief/%d/shortlist?email=%s&refresh=1" % (buy_id, PRO), PRO)
bolt = [m for m in d.get("shortlist", []) if m["listing_id"] == bolt_l]
check(bolt and "outside your rule" in bolt[0]["reasons"], "Bolt listing (no NM price) must match but never be 'inside your rule': %s" % bolt)
check(not any("seller@" in json.dumps(m) for m in d.get("shortlist", [])), "shortlist leaks seller identity")

print("3. first-in: a matching new listing alerts the buy brief within one minute of publish")
s, d = call("POST", "/squire/brief", PRO, {"email": PRO, "kind": "buy", "category": "Property", "city": "Leeds",
                                           "need_text": "3 bed house to buy in Leeds as a rental", "rules": {"max_price": 280000}})
check(s == 200, "property brief: %s %s" % (s, str(d)[:200]))
prop_brief = d["brief_id"]
new_l = listing("3-bed semi, Kirkstall", 250000, "property", "Leeds", SELLER2, suburb="Kirkstall", status="draft", country="United Kingdom")
conn.commit()
t0 = time.time()
s, d = call("PUT", "/listings/%d/publish?accepted_terms=1&email=%s" % (new_l, SELLER2), SELLER2)
check(s == 200, "publish failed: %s %s" % (s, d))
al = None
while time.time() - t0 < 60:
    al = conn.execute("SELECT * FROM squire_alerts WHERE brief_id=? AND listing_id=?", (prop_brief, new_l)).fetchone()
    if al:
        break
    time.sleep(0.5)
lat = time.time() - t0
check(al is not None and al["urgency"] == "instant" and al["sent_at"], "no instant first-in alert within 60 s: %s" % (dict(al) if al else None))
print("   first-in alert after %.1f s, urgency=%s, channel=%s" % (lat, al and al["urgency"], al and al["channel"]))
check(all(SELLER2 not in (t + str(b)) for _, t in PUSHES for b in [""]) and not any(SELLER2 in m[2] for m in MAILS if m[0] == PRO), "the alert carried the seller's identity")

print("4. sell-side: a sell line matching an open want-list / Watch alerts the seller, no identity either side")
rows = [dict(r) for r in conn.execute("SELECT * FROM squire_alerts WHERE brief_id=? AND kind='sell_side'", (sell_id,)).fetchall()]
names = {r["title"] for r in rows}
check("Someone wants Card 05" in names and "Someone wants Card 06" in names, "sell-side alerts missing: %s" % names)
check(all(BUYER2 not in (r["title"] + r["body"]) and "bt_want" not in (r["title"] + r["body"]) for r in rows), "sell-side alert leaks the buyer")
check(all(r["urgency"] == "digest" for r in rows), "sell-side alerts must be digest")

print("5. UK property crux report; no verified data -> no report and no charge")
bal0 = B._current_tuppence(PRO)
s, d = call("GET", "/squire/brief/%d/report?listing_id=%d&email=%s" % (prop_brief, new_l, PRO), PRO)
rep = (d or {}).get("report") or {}
labels = {n["label"] for n in rep.get("numbers", [])}
check(s == 200 and rep.get("comps_n") == 64 and rep.get("gross_yield_pct") and {"Energy rating", "Flood area"} <= labels
      and any("crime" in l.lower() for l in labels) and len(rep.get("risks", [])) == 3 and len(rep.get("advantages", [])) == 3 and rep.get("verdict"),
      "crux report incomplete: %s" % str(d)[:300])
print("   verdict:", rep.get("verdict"), "| yield", rep.get("gross_yield_pct"))
B.tier_resolvers.uk_land_registry_median = (lambda *a, **k: asyncio.sleep(0, result=None))
s, d = call("GET", "/squire/brief/%d/report?listing_id=%d&email=%s" % (prop_brief, new_l, PRO), PRO)
check(s == 200 and d.get("report") is None and d.get("charged") is False, "no-data case produced a report: %s" % d)
check(B._current_tuppence(PRO) == bal0, "a report moved Tuppence")

print("6. a brief whose rules matched nothing in 90 days gets a reality-check with a numbered alternative")
s, d = call("POST", "/squire/brief", PRO, {"email": PRO, "kind": "buy", "category": "Property", "city": "Leeds",
                                           "need_text": "house to buy in Leeds, cheap", "rules": {"max_price": 150000}})
rc = (d or {}).get("reality") or {}
check(rc.get("met") == 0 and rc.get("alternatives") and rc["alternatives"][0]["n"] == 1 and rc["alternatives"][0]["would_have_matched"] >= 1,
      "reality-check missing/wrong: %s" % rc)
print("   ", rc.get("line"))
cheap_brief = d["brief_id"]

print("F. learning: 'not that suburb' changes the stored brief and the listing does not come back")
s, d = call("GET", "/squire/brief/%d/shortlist?email=%s&refresh=1" % (prop_brief, PRO), PRO)
ids = [m["listing_id"] for m in d.get("shortlist", [])]
target = prop_ids[1] if prop_ids[1] in ids else (ids[0] if ids else None)
s, d = call("POST", "/squire/brief/%d/feedback" % prop_brief, PRO, {"email": PRO, "listing_id": target, "reason": "not_suburb"})
check(s == 200 and "won't show you" in d.get("change", ""), "feedback: %s %s" % (s, d))
s, d = call("GET", "/squire/brief/%d/shortlist?email=%s&refresh=1" % (prop_brief, PRO), PRO)
check(target not in [m["listing_id"] for m in d.get("shortlist", [])], "an excluded suburb came back")

print("7. a month with zero matches still sends the monthly report")
for bid in (cheap_brief,):
    conn.execute("DELETE FROM squire_matches WHERE brief_id=?", (bid,))
conn.commit()
MAILS.clear()
s, d = call("POST", "/squire/v2/run", None, {"job": "monthly", "date": "2026-11-01"}, admin=True)
check(s == 200 and d["monthly"]["reports"] >= 4, "monthly job: %s %s" % (s, d))
r = conn.execute("SELECT body FROM squire_reports WHERE brief_id=? AND kind='monthly' AND period='2026-10'", (cheap_brief,)).fetchone()
check(r is not None and json.loads(r["body"])["matches"] == 0, "zero-match brief got no monthly report")
check(any(m[0] == PRO and "monthly report" in m[1].lower() for m in MAILS), "monthly report not e-mailed")
s, d = call("POST", "/squire/v2/run", None, {"job": "monthly", "date": "2026-11-01"}, admin=True)
check(d["monthly"]["reports"] == 0, "monthly job not idempotent: %s" % d)

print("8. squire_pro_pa OFF: no recurring charge can be created; ON: caution shown and must be accepted before the first charge")
s, d = call("POST", "/squire/pa/quote", PRO, {"email": PRO, "brief_id": prop_brief, "feeds": ["propertydata"]})
check(s == 404, "quote answered while the switch is OFF: %s" % s)
check(conn.execute("SELECT COUNT(*) FROM recurring_charges").fetchone()[0] == 0, "a recurring charge exists with the switch OFF")
json.dump({"paid_tiers_enabled": True, "providers": {"propertydata": True}, "switches": {"squire_pro_pa": True},
           "feed_costs_usd_month": {"propertydata": 30}}, open(FLAGS, "w"))
feature_flags.reload()
s, q = call("POST", "/squire/pa/quote", PRO, {"email": PRO, "brief_id": prop_brief, "feeds": ["propertydata"]})
check(s == 200 and q.get("tuppence_per_month") and "every month" in q.get("caution_text", ""), "quote: %s %s" % (s, q))
s, d = call("POST", "/squire/pa/accept", PRO, {"email": PRO, "charge_id": q["charge_id"], "accept_caution": False})
check(d.get("status") == "needs_caution" and d.get("charged") is False, "accept without caution: %s" % d)
conn.execute("INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'grant', 30, 'rig')", (PRO,)); conn.commit()
bal = B._current_tuppence(PRO)
s, d = call("POST", "/squire/v2/run", None, {"job": "monthly", "date": "2026-12-01"}, admin=True)
check(B._current_tuppence(PRO) == bal, "charged before the caution was accepted")
s, d = call("POST", "/squire/pa/accept", PRO, {"email": PRO, "charge_id": q["charge_id"], "accept_caution": True})
check(d.get("status") == "active" and d.get("charged") is False and B._current_tuppence(PRO) == bal, "accept: %s" % d)
s, d = call("POST", "/squire/v2/run", None, {"job": "monthly", "date": "2027-01-01"}, admin=True)
check(B._current_tuppence(PRO) == bal - q["tuppence_per_month"], "first month not charged once: %s -> %s" % (bal, B._current_tuppence(PRO)))
check(conn.execute("SELECT COUNT(*) FROM squire_reports WHERE brief_id=? AND kind='monthly' AND period='2026-12'", (prop_brief,)).fetchone()[0] == 1,
      "charged without that month's report")
s, d = call("POST", "/squire/v2/run", None, {"job": "monthly", "date": "2027-01-01"}, admin=True)
check(B._current_tuppence(PRO) == bal - q["tuppence_per_month"], "charged twice in one month")
print("   quote %dT/month; caution required; first month charged once, after the report" % q["tuppence_per_month"])
# out of Tuppence -> brief pauses with the top-up prompt
conn.execute("INSERT INTO transactions (user_email, type, amount, description) VALUES (?, 'rig_drain', ?, 'rig')", (PRO, -B._current_tuppence(PRO)))
conn.commit()
s, d = call("POST", "/squire/v2/run", None, {"job": "monthly", "date": "2027-02-01"}, admin=True)
st = conn.execute("SELECT status FROM squire_briefs WHERE id=?", (prop_brief,)).fetchone()["status"]
check(st == "paused" and conn.execute("SELECT 1 FROM squire_alerts WHERE kind='topup' AND email=?", (PRO,)).fetchone(), "out of Tuppence did not pause with a top-up prompt")
# leave the rig back on the shipped default
json.dump({"paid_tiers_enabled": False}, open(FLAGS, "w")); feature_flags.reload()
check(feature_flags.squire_pro_pa_on() is False, "switch not back OFF")

print("C/3. Squire never grants an introduction")
check(conn.execute("SELECT COUNT(*) FROM intro_requests").fetchone()[0] == 0, "an intro_requests row appeared")

print("G. digest: everything not instant goes once a day")
s, d = call("POST", "/squire/v2/run", None, {"job": "nightly", "date": "2027-02-02"}, admin=True)
check(s == 200 and d["nightly"]["digest"]["digests"] >= 1, "digest did not send: %s" % d)
check(conn.execute("SELECT COUNT(*) FROM squire_alerts WHERE urgency='digest' AND sent_at IS NULL AND email=?", (PRO,)).fetchone()[0] == 0, "digest left alerts unsent")

if os.environ.get("RIG_LEAVE_ARMED") == "1":
    print("\n(rig left armed for the rendered check)")
else:
    arm(0)
conn.close()
if FAILS:
    print("\nFAIL (%d)" % len(FAILS)); [print(" -", f) for f in FAILS]; sys.exit(1)
print("\nALL SQUIRE-2 ACCEPTANCE CHECKS PASS (API + DB, real BEA, throwaway database)")
