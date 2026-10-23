#!/usr/bin/env python3
"""door_route_proof.py -- ONE-DOOR-1 (DOOR_BRIEF.md U2): proves the door's server logic on a THROWAWAY copy of the database,
without FastAPI (lifts the ONE-DOOR-1 block out of bea_main.py by its markers and runs it against real sqlite + stubs).
Asserts:
  1. switch OFF -> every door route 404
  2. signed out -> empty answer; POST /door/last stores nothing
  3. a user with no history and no prospect row -> no interest (general gallery)
  4. a CityLauncher prospect row (email_hash) -> interest from 'prospect'
  5. primary_category -> interest from 'history'; an introduction (_door_note_interest) goes FIRST, max 3, no duplicates
  6. last app stored and read back; an unknown app refused (400)
  7. Pro tier read; /pa redirects a non-Pro to /pa/about and serves pa.html to Pro
  8. /app.webmanifest: same id '/', Snap's share target only while the switch is ON
Usage: python3 scripts/door_route_proof.py <path to a COPY of marketsquare.db named *door_proof*.db>   (never the live file)
"""
import hashlib, json, os, sqlite3, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = sys.argv[1] if len(sys.argv) > 1 else ""
assert DB and os.path.exists(DB) and "door_proof" in os.path.basename(DB), "give the path of a throwaway COPY named *door_proof*.db"
SRC = open(os.path.join(HERE, "bea_main.py"), encoding="utf-8").read()
def cut(a, b):
    i = SRC.index(a); j = SRC.index(b, i); return SRC[i:j]
block = cut("# ── ONE-DOOR-1 (DOOR_BRIEF.md", "# ── QUICK-PASS-1 (David, 25 Sep 2026")
norm = cut("def _demand_norm_category(raw):", "EULA_CURRENT_VERSION")

class HTTPException(Exception):
    def __init__(self, status_code, detail=""): self.status_code, self.detail = status_code, detail
class _App:
    def get(self, *a, **k): return lambda f: f
    def post(self, *a, **k): return lambda f: f
def Cookie(default=None): return default
class BaseModel:
    def __init__(self, **k): self.__dict__.update(k)
class _DB:
    @staticmethod
    def get_db():
        c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c
def _bit_flag(name, default):
    c = _DB.get_db()
    try:
        r = c.execute("SELECT %s AS v FROM launch_switches WHERE id=1" % name).fetchone()
        return default if (r is None or r["v"] is None) else bool(r["v"])
    except Exception:
        return default
    finally:
        c.close()
SESS = {}
def _session_email(tok): return SESS.get(tok)
def _seller_tier_of(conn, email):
    u = conn.execute("SELECT seller_tier FROM users WHERE LOWER(email)=?", (email,)).fetchone()
    return ((u["seller_tier"] if u else "") or "free").lower()
import types
class FileResponse:
    def __init__(self, path, media_type=None, headers=None): self.path, self.kind = path, "file"
class RedirectResponse:
    def __init__(self, url, status_code=302): self.url, self.status_code, self.kind = url, status_code, "redirect"
class JSONResponse:
    def __init__(self, content, media_type=None, headers=None): self.content, self.kind = content, "json"
_fr = types.ModuleType("fastapi.responses"); _fr.FileResponse = FileResponse; _fr.RedirectResponse = RedirectResponse; _fr.JSONResponse = JSONResponse
_fa = types.ModuleType("fastapi"); _fa.responses = _fr
sys.modules.setdefault("fastapi", _fa); sys.modules["fastapi.responses"] = _fr
_ffm = types.ModuleType("feature_flags"); _ffm.squire_pro_pa_on = lambda: False; sys.modules["feature_flags"] = _ffm

g = {"json": json, "HTTPException": HTTPException, "app": _App(), "Cookie": Cookie, "BaseModel": BaseModel,
     "database": _DB, "_bit_flag": _bit_flag, "_session_email": _session_email, "_seller_tier_of": _seller_tier_of}
exec(compile(norm, "norm", "exec"), g)
exec(compile(block, "door", "exec"), g)

ok = 0
def check(cond, what):
    global ok
    assert cond, "FAIL: " + what
    ok += 1; print("  PASS", what)
def expect_status(fn, code, what, *a, **k):
    try:
        fn(*a, **k)
    except HTTPException as e:
        check(e.status_code == code, what); return
    check(False, what)

c = _DB.get_db()
for ddl in ("ALTER TABLE launch_switches ADD COLUMN one_door INTEGER NOT NULL DEFAULT 0",
            "ALTER TABLE users ADD COLUMN interest_categories TEXT", "ALTER TABLE users ADD COLUMN last_app TEXT"):
    try: c.execute(ddl)
    except Exception: pass
c.execute("UPDATE launch_switches SET one_door=0 WHERE id=1"); c.commit()
# 1
for fn, a in ((g["door_page"], ()), (g["pa_about_page"], ()), (g["door_me"], ()), (g["pa_page"], ())):
    expect_status(fn, 404, "switch OFF: %s answers 404" % fn.__name__, *a)
expect_status(g["door_last"], 404, "switch OFF: door_last answers 404", BaseModel(app="quick"))
check("share_target" not in g["door_app_manifest"]().content and g["door_app_manifest"]().content["id"] == "/", "switch OFF: TrustSquare manifest has no share target, same id")
c.execute("UPDATE launch_switches SET one_door=1 WHERE id=1"); c.commit()
check(g["door_app_manifest"]().content.get("share_target", {}).get("action", "").startswith("/quick/share-in?p=snap"), "switch ON: TrustSquare manifest hands a shared photo to Snap")
# 2
r = g["door_me"](None); check(r["signed_in"] is False and r["interest"] == [], "signed out -> empty answer")
r = g["door_last"](BaseModel(app="snap"), None); check(r["stored"] is False, "signed out -> last app not stored")
# make three throwaway users
def mk(em, tier="free", prim=None):
    c.execute("DELETE FROM users WHERE LOWER(email)=?", (em,))
    cols = [r[1] for r in c.execute("PRAGMA table_info(users)")]
    vals = {"email": em, "seller_tier": tier, "primary_category": prim}
    if "name" in cols: vals["name"] = "Proof"
    keys = [k for k in vals if k in cols]
    c.execute("INSERT INTO users (%s) VALUES (%s)" % (",".join(keys), ",".join("?" * len(keys))), [vals[k] for k in keys]); c.commit()
A, B, P = "door-proof-a@example.invalid", "door-proof-b@example.invalid", "door-proof-pro@example.invalid"
mk(A); mk(B); mk(P, "pro", "Cars")
SESS.update({"ta": A, "tb": B, "tp": P})
# 3
r = g["door_me"]("ta"); check(r["signed_in"] and r["interest"] == [] and r["via"] is None, "no history, no prospect -> general gallery")
# 4
h = hashlib.sha256(B.encode()).hexdigest()[:32]
c.execute("INSERT INTO demand_prospects (email_hash, category, app_category, source) VALUES (?,?,?,?)", (h, "coin dealer", "Collectors", "door_proof")); c.commit()
r = g["door_me"]("tb"); check(r["interest"] == ["Collectors"] and r["via"] == "prospect", "prospect row -> Collectors via prospect")
# 5
r = g["door_me"]("tp"); check(r["interest"] == ["Cars"] and r["via"] == "history" and r["pro"] is True, "primary_category Cars -> history; Pro read")
for cat in ("property", "adventures_experiences", "Property", "local_market"):
    g["_door_note_interest"](c, P, cat)
c.commit()
r = g["door_me"]("tp"); check(r["interest"] == ["Local Market", "Property", "Adventures"], "introductions: most recent first, max 3, no duplicates")
# 6
r = g["door_last"](BaseModel(app="pa"), "tp"); check(r["stored"], "last app stored")
check(g["door_me"]("tp")["last_app"] == "pa", "last app read back")
expect_status(g["door_last"], 400, "unknown app refused", BaseModel(app="zzz"), "tp")
# 7
r = g["pa_page"]("ta"); check(getattr(r, "kind", "") == "redirect" and r.url == "/pa/about", "non-Pro -> /pa/about")
r = g["pa_page"](None); check(getattr(r, "kind", "") == "redirect", "signed out -> /pa/about")
r = g["pa_page"]("tp"); check(getattr(r, "kind", "") == "file" and r.path.endswith("pa.html"), "Pro -> pa.html")
r = g["door_page"](); check(r.path.endswith("door.html"), "/door serves door.html")
c.close()
print("door_route_proof: %d/%d PASS" % (ok, ok))
