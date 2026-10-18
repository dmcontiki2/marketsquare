#!/usr/bin/env python3
"""prove_photo_kind.py -- PHOTO-KIND-1 (RUL-239, David 18 Oct 2026): run the REAL seller photo gate
(_seller_photo_anon_gate) from bea_main over a folder of photos, with a throwaway SQLite file (never the
live database), and report per photo: passed / blurred (what) / held for a check / refused (why).
Writes <out>/<name>.out.jpg (what a buyer would see) and <out>/report.json.
Run on the server with the AI keys in the environment:
    python3 scripts/prove_photo_kind.py --dir /root/phototest --out /root/phototest/out --category Services
"""
import argparse, json, os, sys, tempfile, time
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
DB = os.path.join(tempfile.mkdtemp(), "photokind.db"); database.DB_PATH = DB
os.environ["MS_DB"] = os.path.join(os.path.dirname(DB), "flights.db")
import bea_main as b
from fastapi import HTTPException
from PIL import Image, ImageOps

ap = argparse.ArgumentParser()
ap.add_argument("--dir", required=True); ap.add_argument("--out", required=True)
ap.add_argument("--category", default="Services"); ap.add_argument("--only", default="")
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
b._check_cost_ceiling = lambda who: None          # QA run: the test spends, it is not a user
rep = []
for fn in sorted(os.listdir(a.dir)):
    if not fn.lower().endswith((".jpg", ".jpeg", ".png")) or fn.startswith(("sheet", "out")):
        continue
    if a.only and a.only not in fn:
        continue
    img = ImageOps.exif_transpose(Image.open(os.path.join(a.dir, fn))).convert("RGB")
    t0 = time.time(); rec = {"file": fn}
    try:
        res = b._seller_photo_anon_gate(img, a.category, "qa-photo-kind", is_primary=True)
        out, note = res[0], res[1]
        rec["outcome"] = "held" if str(note).startswith("held") else ("blurred" if str(note).startswith("redacted") else "passed")
        rec["note"] = note
        if out is not None:
            out.save(os.path.join(a.out, fn.rsplit(".", 1)[0] + ".out.jpg"), quality=85)
    except HTTPException as e:
        if hasattr(b, "_PhotoHeld") and isinstance(e, b._PhotoHeld):
            rec["outcome"] = "HELD"; rec["note"] = e.reason + (" | " + e.labels if e.labels else "")
            e.img.save(os.path.join(a.out, fn.rsplit(".", 1)[0] + ".held.jpg"), quality=85)
        else:
            rec["outcome"] = "REFUSED %s" % e.status_code; rec["note"] = str(e.detail)
    rec["s"] = round(time.time() - t0, 1)
    print("%-42s %-12s %s" % (fn[:42], rec["outcome"], str(rec["note"])[:160]), flush=True)
    rep.append(rec)
json.dump(rep, open(os.path.join(a.out, "report.json"), "w"), indent=1)
