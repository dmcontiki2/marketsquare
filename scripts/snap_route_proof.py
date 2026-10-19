#!/usr/bin/env python3
"""snap_route_proof.py -- QUICK-SNAP-1 (QUICK_SNAP_BRIEF.md §8 U2): proves POST /listings/snap-draft's logic on a THROWAWAY
copy of the database, without FastAPI and without the AI reader (neither is installed where this runs, and no listing may
ever be made on the live site by this lane).

What it does: lifts the QUICK-SNAP-1 block and the fast-find splitter out of bea_main.py by their markers, runs them against
real stubs (sqlite3 on the DB copy; a canned vision answer in the exact shape vision_draft returns), and asserts:
  1. the cleaner sentence  -> Housekeeping door, role Home cleaner, area Mamelodi (a real suburb row), Tue + Thu, R350 a day, nothing missing
  2. a card photo          -> Collectors door, Cards, Near mint, 'Not yet' authenticated, R2 300, nothing missing (one tap)
  3. photo + sentence      -> the sentence wins on price and area
  4. 'Honey, Pretoria East, R80' on the Local Market door -> item Honey, Pretoria East, R80, Collect, nothing missing
  5. an unreadable photo, no sentence -> outcome 'unread' + the one line (Quick lands on normal step 1)
  6. a sentence the reader cannot place -> 'missing' names the steps (Quick lands on the first of them)
  7. switch OFF -> 404; the counter rows landed in quick_snap_log; the stats shape
Usage: python3 scripts/snap_route_proof.py <path to a COPY of marketsquare.db>   (never the live file)
"""
import asyncio, os, re, sqlite3, sys, types, json, logging
from datetime import datetime, timezone, timedelta

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = sys.argv[1] if len(sys.argv) > 1 else ""
assert DB and os.path.exists(DB) and "snap_proof" in os.path.basename(DB), "give the path of a throwaway COPY named *snap_proof*.db"
SRC = open(os.path.join(HERE, "bea_main.py"), encoding="utf-8").read()

def cut(a, b):
    i = SRC.index(a); j = SRC.index(b, i)
    return SRC[i:j]

block = cut("# ══ QUICK-SNAP-1", "# ══ end QUICK-SNAP-1 ══")
qf = cut("_QF_PRICE_MAX_RE = re.compile", "def _qf_parse_ai(q):")

# ---- stubs for what the block reaches in bea_main ----
class HTTPException(Exception):
    def __init__(self, status_code, detail=""):
        self.status_code, self.detail = status_code, detail
class _App:
    def post(self, *a, **k): return lambda f: f
    def get(self, *a, **k): return lambda f: f
def File(default=None, **k): return default
def Form(default=None, **k): return default
def Depends(x): return None
class UploadFile:
    def __init__(self, filename, data): self.filename, self._d = filename, data
    async def read(self): return self._d
class _DB:
    @staticmethod
    def get_db():
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
def _bit_flag(name, default):
    try:
        c = _DB.get_db(); r = c.execute("SELECT %s AS v FROM launch_switches WHERE id=1" % name).fetchone(); c.close()
        return default if (r is None or r["v"] is None) else bool(r["v"])
    except Exception:
        return default
def _utc_now(): return datetime.now(timezone.utc).isoformat(timespec="seconds")
def _sql_since(days=0, hours=0):
    return (datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(days=days, hours=hours)).isoformat(sep=" ", timespec="seconds")
def _check_cost_ceiling(email): return None
def _log_ai_spend(*a, **k): return None
CARD = {"draft": {"category": "collectors", "title": "Savannah Dual Land, 4th Edition", "description_draft": "A single Savannah dual land card from the 4th Edition set, near mint with clean edges and a bright face. Sold as pictured.",
                  "suggested_price": 2300, "currency_prefix": "R", "collectible_type": "Trading cards", "condition": "Excellent",
                  "category_confidence": 0.93, "price_confidence": 0.6}, "warnings": [], "model_used": "x"}
VISION = {"answer": CARD, "calls": []}
async def vision_draft(request, background_tasks, photos, category_hint, seller_email, city, country_iso2):
    data = [await p.read() for p in photos]
    VISION["calls"].append({"n": len(photos), "hint": category_hint, "bytes": [len(d) for d in data]})
    assert all(data), "empty photo reached the reader"
    if isinstance(VISION["answer"], Exception):
        raise VISION["answer"]
    return VISION["answer"]

g = {"re": re, "os": os, "json": json, "asyncio": asyncio, "datetime": datetime, "timezone": timezone, "timedelta": timedelta,
     "HTTPException": HTTPException, "app": _App(), "File": File, "Form": Form, "Depends": Depends, "UploadFile": UploadFile,
     "Request": object, "BackgroundTasks": object, "database": _DB, "_bit_flag": _bit_flag, "_utc_now": _utc_now,
     "_sql_since": _sql_since, "_log": logging.getLogger("snap"), "_require_admin": None, "vision_draft": vision_draft,
     "_check_cost_ceiling": _check_cost_ceiling, "_log_ai_spend": _log_ai_spend, "__file__": os.path.join(HERE, "bea_main.py"),
     "list": list}
exec(compile(qf, "qf", "exec"), g)
exec(compile(block, "snap", "exec"), g)

# ---- the throwaway DB gets the switch column, ON ----
c = sqlite3.connect(DB)
try:
    c.execute("ALTER TABLE launch_switches ADD COLUMN quick_snap INTEGER NOT NULL DEFAULT 0")
except Exception:
    pass
c.execute("UPDATE launch_switches SET quick_snap=1 WHERE id=1"); c.commit(); c.close()

PNG = bytes.fromhex("89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c4890000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082")
def run(**kw):
    kw.setdefault("photos", []); kw.setdefault("sentence", ""); kw.setdefault("category_hint", "")
    kw.setdefault("city", "Pretoria"); kw.setdefault("country_iso2", "ZA"); kw.setdefault("seller_email", "")
    return asyncio.get_event_loop().run_until_complete(g["snap_draft"](None, None, **kw))

ok = []
def check(name, cond, detail=""):
    ok.append(bool(cond)); print(("PASS " if cond else "FAIL ") + name + (("  -- " + str(detail)[:200]) if detail else ""))

# 1. the cleaner sentence
r = run(sentence="Home cleaner, Mamelodi, Tuesdays and Thursdays, R350 a day", category_hint="homehelp")
f = r["fields"]
check("1 say: Housekeeping door", r["cat"] == "homehelp", r["cat"])
check("1 say: role Home cleaner", f.get("what") == "Home cleaner" and f.get("r") == "home_cleaner", f)
check("1 say: area Mamelodi from the suburb table", f.get("where") == "Mamelodi")
check("1 say: Tue + Thu", f.get("days") == ["Tue", "Thu"], f.get("days"))
check("1 say: R350 a day", f.get("price") == 350 and f.get("basis") == "day" and f.get("price_label") == "R350", f)
check("1 say: nothing missing", r["missing"] == [] and r["listing"]["service_class"] == "Casuals", (r["missing"], r["listing"]))
# 1b. the same without commas, the way speech writes it
r = run(sentence="I am a home cleaner in Mamelodi Tuesdays and Thursdays 350 rand a day", category_hint="homehelp")
check("1b spoken sentence (no commas): same reading", r["cat"] == "homehelp" and r["fields"].get("r") == "home_cleaner" and r["fields"].get("where") == "Mamelodi" and r["fields"].get("days") == ["Tue", "Thu"] and r["fields"].get("price") == 350, r["fields"])
# 2. the card photo
r = run(photos=[UploadFile("card.png", PNG)], category_hint="collectors")
f = r["fields"]
check("2 snap: reader called once with the door as hint", VISION["calls"][-1] == {"n": 1, "hint": "collectors", "bytes": [len(PNG)]}, VISION["calls"][-1])
check("2 snap: Collectors / Cards / Near mint / Not yet / R2 300", r["cat"] == "collectors" and f.get("what") == "Cards" and f.get("cond") == "Near mint" and f.get("auth") == "Not yet" and f.get("price_label") == "R2 300", f)
check("2 snap: nothing missing -> one tap", r["missing"] == [] and r["photo_read"] is True and r["confidence"] >= 0.9, (r["missing"], r["confidence"]))
check("2 snap: item name + words travel", f.get("item", "").startswith("Savannah") and "4th Edition" in f.get("words", ""), f.get("item"))
# 3. photo + sentence: the sentence wins on price and area
r = run(photos=[UploadFile("card.png", PNG)], sentence="Lynnwood, R1 900", category_hint="collectors")
check("3 both: sentence wins on price and area", r["kind"] == "both" and r["fields"].get("price") == 1900 and r["fields"].get("where") == "Lynnwood" and r["fields"].get("what") == "Cards", r["fields"])
# 4. honey on the Local Market door
r = run(sentence="Honey, Pretoria East, R80", category_hint="localmarket")
f = r["fields"]
check("4 say: Honey / Pretoria East / R80 / Collect", r["cat"] == "localmarket" and f.get("what") == "Honey" and f.get("where") == "Pretoria East" and f.get("price") == 80 and f.get("ship") == "Collect" and r["missing"] == [], (f, r["missing"]))
check("4 say: listing title in the Quick shape", r["listing"]["title"] == "Honey — Pretoria East" and r["listing"]["category"] == "local_market" and r["listing"]["source"] == "quick_snap", r["listing"])
# 5. an unreadable photo, no sentence
VISION["answer"] = HTTPException(422, "Vision analysis returned unexpected format — try describing instead")
r = run(photos=[UploadFile("blur.png", PNG)], category_hint="cars")
check("5 unread photo: not a dead end", r["photo_read"] is False and r["cat"] == "cars" and r["missing"] and r["line"].startswith("We could not read"), (r["missing"], r["line"]))
VISION["answer"] = CARD
# 6. a sentence the reader cannot place
r = run(sentence="Something nice for sale", category_hint="cars")
check("6 unplaced sentence: missing names the steps, nothing guessed", r["cat"] == "cars" and r["missing"][:1] == ["what"] and "make" in r["missing"] and "price" in r["missing"] and not r["fields"].get("what") and r["confidence"] <= 0.3, (r["missing"], r["confidence"], r["fields"]))
# 6b. technical role with an hourly rate
r = run(sentence="Plumber, Centurion, R450 an hour", category_hint="services")
check("6b technical role: Services door, Per hour, qual still asked", r["cat"] == "services" and r["fields"].get("how") == "Per hour" and r["missing"] == ["qual"], (r["fields"], r["missing"]))
# 7. the empty call, the switch, the counters, the stats
try:
    run(); check("7 empty call refused", False)
except HTTPException as e:
    check("7 empty call refused 400", e.status_code == 400)
c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
rows = c.execute("SELECT kind, outcome, cat FROM quick_snap_log ORDER BY id").fetchall()
check("7 counter rows with provenance", [tuple(x) for x in rows] == [("say", "draft", "homehelp"), ("say", "draft", "homehelp"), ("snap", "draft", "collectors"), ("both", "draft", "collectors"), ("say", "draft", "localmarket"), ("snap", "unread", "cars"), ("say", "missing", "cars"), ("say", "missing", "services")], [tuple(x) for x in rows])
c.execute("UPDATE launch_switches SET quick_snap=0 WHERE id=1"); c.commit(); c.close()
try:
    run(sentence="Home cleaner, Mamelodi, R350 a day"); check("7 switch OFF -> 404", False)
except HTTPException as e:
    check("7 switch OFF -> 404", e.status_code == 404)
st = g["admin_quick_snap_stats"](30, None)
check("7 stats shape", st["switch_on"] is False and st["reads"]["say"] == 5 and st["reads"]["snap"] == 2 and st["reads"]["both"] == 1 and st["outcomes"]["unread"] == 1 and st["outcomes"]["missing"] == 2, st)
print("\nRESULT: %d/%d PASS" % (sum(ok), len(ok)))
sys.exit(0 if all(ok) else 1)
