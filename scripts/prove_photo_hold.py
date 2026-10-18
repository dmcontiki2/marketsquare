#!/usr/bin/env python3
"""prove_photo_hold.py -- PHOTO-KIND-1 (RUL-239, David 18 Oct 2026): EXECUTE the private photo hold against the real
bea_main.py, imported with a throwaway SQLite file (never the live database), no AI spend (the gate is stood in by a
_PhotoHeld raise), photos stored to a temp folder, mail captured.
What it proves:
  A  a photo the gate cannot clear is NOT refused: /listings/photo answers 200 held=True with the seller message, and
     the draft door does the same; the file sits outside the web root, mode 600, and no listing row changed
  B  David is alerted once (not once per photo) inside 30 minutes; the alert carries counts only
  C  the admin list shows it with a preview; a non-admin is refused (route policy)
  D  Approve -> the photo becomes the advert cover (thumb_url, photo_urls, [photos:] prefix), the private file is gone,
     the seller gets the "on your advert" mail; deciding twice changes nothing
  E  Blur & approve -> the marked spot is changed in the stored photo; Decline -> nothing reaches the advert, seller mailed
  F  a photo uploaded before the advert existed lands on the seller's advert created after it
Run: python3 scripts/prove_photo_hold.py
"""
import os, sys, json, tempfile, io
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(REPO); sys.path.insert(0, REPO)
os.environ["MS_API_KEY"] = "k"; os.environ["MS_ADMIN_KEY"] = "adm"
os.environ["MS_JWT_SECRET"] = "test-only-" + os.urandom(8).hex()
for k in ("RESEND_API_KEY", "PAYSTACK_WEBHOOK_SECRET", "GMAIL_APP_PASSWORD", "PAYSTACK_SECRET_KEY", "HETZNER_S3_ENDPOINT",
          "HETZNER_S3_BUCKET", "HETZNER_S3_ACCESS_KEY", "HETZNER_S3_SECRET_KEY"):
    os.environ.pop(k, None)
TMP = tempfile.mkdtemp()
os.environ["PHOTO_HOLD_DIR"] = os.path.join(TMP, "holds")
_mk = os.makedirs
os.makedirs = lambda p, *a, **k: None if str(p).startswith("/var/www") else _mk(p, *a, **k)
import starlette.staticfiles as _sf
_i = _sf.StaticFiles.__init__
def _i2(self, *a, **k):
    k["check_dir"] = False; return _i(self, *a, **k)
_sf.StaticFiles.__init__ = _i2
import database
DB = os.path.join(TMP, "hold.db"); database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(TMP, "flights.db")
import bea_main as b, storage
from fastapi.testclient import TestClient
from PIL import Image
import jwt as _pyjwt, time, threading

FAIL = []
def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg); (None if cond else FAIL.append(msg))

stored = {}
def _up(data, name, ct="image/jpeg"):
    p = os.path.join(TMP, "media_" + name); open(p, "wb").write(data); stored[name] = p
    return "https://trustsquare.co/media/" + name
storage.upload_photo = _up
b._S3_CONFIGURED = False
mails = []
b._send_system_email = lambda to, subj, html: (mails.append((to, subj, html)), "sent")[1]
_thr_start = threading.Thread.start
def _sync_start(self):          # alerts run inline so the test can see them
    if self.name == "photo-hold-alert":
        return self.run()
    return _thr_start(self)
threading.Thread.start = _sync_start
b._check_cost_ceiling = lambda who: None
REG = [(400, 400, 600, 600, "service company name")]
def _gate(img, category, who, is_primary=False):
    raise b._PhotoHeld(img, "the blurred words could not be confirmed", "service company name", REG, category)
b._seller_photo_anon_gate = _gate

c = TestClient(b.app)
ADM = _pyjwt.encode({"sub": "master", "scope": "admin", "exp": int(time.time()) + 3600, "iat": int(time.time())},
                    b._JWT_SECRET, algorithm=b._JWT_ALGO)
conn = database.get_db()
def mk_listing(title, status="live", email="qa-hold@example.com"):
    cur = conn.execute("INSERT INTO listings (title, category, city, seller_email, listing_status, description) VALUES (?,?,?,?,?,?)",
                       (title, "Services", "Pretoria", email, status, "Fire extinguisher maintenance."))
    conn.commit(); return cur.lastrowid
try:
    conn.execute("ALTER TABLE listings ADD COLUMN photo_urls TEXT"); conn.commit()
except Exception:
    pass
L1 = mk_listing("Fire Extinguisher Maintenance - QA")
def jpg(color=(200, 30, 30)):
    im = Image.new("RGB", (800, 800), color)
    for x in range(380, 620):
        for y in range(380, 620, 8):
            im.putpixel((x, y), (255, 255, 255))
    bb = io.BytesIO(); im.save(bb, format="JPEG"); return bb.getvalue()
H = {"X-Api-Key": "k", "X-Admin-Key": "adm"}

# A
r = c.post("/listings/photo", headers=H, files={"file": ("p.jpg", jpg(), "image/jpeg")},
           data={"listing_id": str(L1), "is_primary": "true"})
j = r.json() if r.headers.get("content-type", "").startswith("application/json") else {}
check(r.status_code == 200 and j.get("held") is True and "waiting for a quick check" in (j.get("message") or ""),
      "A1 a held photo answers 200 held=True with the seller message (got %s %s)" % (r.status_code, str(j)[:120]))
row = conn.execute("SELECT thumb_url, photo_urls FROM listings WHERE id=?", (L1,)).fetchone()
check(not row["thumb_url"], "A2 nothing reached the advert while the photo is held")
hd = os.environ["PHOTO_HOLD_DIR"]; files = os.listdir(hd)
check(len(files) == 1 and oct(os.stat(os.path.join(hd, files[0])).st_mode)[-3:] == "600" and not hd.startswith("/var/www"),
      "A3 the held photo is one private file (600) outside the web root")
L2 = mk_listing("Draft QA", status="draft")
r2 = c.post("/listings/%d/photo/draft?email=qa-hold@example.com" % L2, headers=H, files={"file": ("p.jpg", jpg(), "image/jpeg")})
check(r2.status_code == 200 and r2.json().get("held") is True, "A4 the draft door holds too (got %s)" % r2.status_code)

# B
alerts = [m for m in mails if "waiting for your check" in m[1]]
check(len(alerts) == 1, "B1 David alerted ONCE for two held photos inside 30 minutes (got %d)" % len(alerts))
check(alerts and "qa-hold@example.com" not in alerts[0][2] and "Fire Extinguisher" not in alerts[0][2],
      "B2 the alert carries counts only - no seller, no advert text")

# C
r = c.get("/admin/photo-holds", headers={"X-Admin-Token": ADM}); j = r.json()
check(r.status_code == 200 and j.get("pending") == 2 and all((h.get("preview") or "").startswith("data:image/jpeg") for h in j["holds"]),
      "C1 the admin list shows both, each with a preview")
check(c.get("/admin/photo-holds").status_code in (401, 403), "C2 no admin token -> refused")
h1 = [h for h in j["holds"] if h["listing_id"] == L1][0]
check(h1["regions"] and h1["reason"], "C3 the list says why and where the scan pointed")

# D
r = c.post("/admin/photo-holds/%d/decide" % h1["id"], headers={"X-Admin-Token": ADM}, json={"action": "approve"}); j = r.json()
row = conn.execute("SELECT thumb_url, medium_url, photo_urls, description FROM listings WHERE id=?", (L1,)).fetchone()
check(r.status_code == 200 and j.get("status") == "approved" and row["thumb_url"] and json.loads(row["photo_urls"])[0] == row["medium_url"]
      and row["description"].startswith("[photos:" + row["medium_url"]), "D1 approve -> cover, gallery and photo strip all carry it")
check(len(os.listdir(hd)) == 1, "D2 the private original is gone once decided")
check(any(m[0] == "qa-hold@example.com" and "on your" in m[1] for m in mails), "D3 the seller is told her photo is on her advert")
r = c.post("/admin/photo-holds/%d/decide" % h1["id"], headers={"X-Admin-Token": ADM}, json={"action": "decline"})
check(r.json().get("already") is True and r.json().get("status") == "approved", "D4 deciding twice changes nothing")

# E
c.post("/listings/photo", headers=H, files={"file": ("p.jpg", jpg(), "image/jpeg")}, data={"listing_id": str(L1)})
hs = c.get("/admin/photo-holds", headers={"X-Admin-Token": ADM}).json()["holds"]
he = [h for h in hs if h["listing_id"] == L1][0]
before = set(stored)
r = c.post("/admin/photo-holds/%d/decide" % he["id"], headers={"X-Admin-Token": ADM}, json={"action": "blur"})
new = [stored[k] for k in set(stored) - before if "medium" in k]
ok = False
if new:
    im = Image.open(new[0]).convert("L"); px = [im.getpixel((x, 500)) for x in range(420, 580)]
    ok = (max(px) - min(px)) < 60          # the white stripes inside the marked spot are smeared away
check(r.json().get("how") == "blurred+approved" and ok, "E1 blur & approve smears the marked spot in the stored photo")
row = conn.execute("SELECT photo_urls FROM listings WHERE id=?", (L1,)).fetchone()
check(len(json.loads(row["photo_urls"])) == 2, "E2 a second (non-cover) photo joins the end of the gallery")
hd2 = [h for h in hs if h["listing_id"] == L2][0]
n0 = len(mails)
r = c.post("/admin/photo-holds/%d/decide" % hd2["id"], headers={"X-Admin-Token": ADM}, json={"action": "decline"})
row = conn.execute("SELECT thumb_url FROM listings WHERE id=?", (L2,)).fetchone()
check(r.json().get("status") == "declined" and not row["thumb_url"] and any("another photo" in m[1] for m in mails[n0:]),
      "E3 decline -> nothing on the advert, the seller is asked for another photo")

# F
b._session_email = lambda tok: "qa-early@example.com"
c.post("/listings/photo", headers={"X-Api-Key": "k"}, files={"file": ("p.jpg", jpg(), "image/jpeg")}, cookies={"ts_user": "x"})
time.sleep(1.1)
L3 = mk_listing("Published after the photo", email="qa-early@example.com")
hs = c.get("/admin/photo-holds", headers={"X-Admin-Token": ADM}).json()["holds"]
hf = [h for h in hs if h["seller"] == "qa-early@example.com"]
check(hf and hf[0]["listing_id"] == L3, "F1 a photo held before the advert existed is tied to the advert she published after it")

print("\n%s - %d failure(s)" % ("ALL PASS" if not FAIL else "FAILED", len(FAIL)))
sys.exit(1 if FAIL else 0)
