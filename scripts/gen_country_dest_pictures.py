#!/usr/bin/env python3
"""gen_country_dest_pictures.py -- COUNTRY-PACK-1 (David 25 Sep 2026: "we need to ... also fix the other countries
for these fixes"; picture budget chosen: "Destinations only (~US$7)"). One picture per destination in the
lodge / tour / self-drive lists of each non-ZA country pack (roles/quick_country_packs.json); rail and fishing
reuse them where they overlap and show as labelled buttons otherwise. Application pictures (RUL-164).
Dry run by default; --go spends (~US$0.06 each). --par N generates N at once. Output
assets/quick_ph/dest_<cc>_<slug>.jpg 300x300."""
import argparse, io, json, os, re, sys, datetime, unicodedata
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_role_pictures as g
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "quick_ph")
STYLE = ("Photorealistic travel photograph, square 1:1, golden-hour light, wide landscape view that is typical of the "
         "place. NO readable text, NO signs, NO logos, NO brand names, NO faces (people only far away or from behind). ")
def slug(n):
    n = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", n.lower()).strip("_")
def todo_list(only=None):
    P = json.load(io.open(os.path.join(ROOT, "roles", "quick_country_packs.json"), encoding="utf-8"))
    out = []
    for cc, p in P.items():
        if cc == "ZA" or not p.get("dest") or (only and cc != only): continue
        seen = set()
        for k in ("lodge", "tour", "drive"):
            for n in p["dest"][k]:
                if n in seen: continue
                seen.add(n)
                out.append((cc, n, "dest_%s_%s" % (cc.lower(), slug(n)), p["name"]))
    return out
def one(item, key):
    cc, name, fn, country = item
    dst = os.path.join(OUT, fn + ".jpg")
    if os.path.exists(dst): return fn, "have"
    try:
        raw = g.generate("higgsfield", g.DEFAULT_MODEL["higgsfield"], key,
                         STYLE + "%s, %s: a characteristic view of this destination for a traveller." % (name, country))
    except Exception as e:
        return fn, "FAIL " + str(e)[:120]
    im = Image.open(io.BytesIO(raw)).convert("RGB"); w, h = im.size; s = min(w, h)
    im.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s)).resize((300, 300), Image.LANCZOS).save(dst, "JPEG", quality=84)
    return fn, "made"
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--cc")
    ap.add_argument("--par", type=int, default=4); ap.add_argument("--max", type=int, default=999)
    a = ap.parse_args()
    items = [i for i in todo_list(a.cc) if not os.path.exists(os.path.join(OUT, i[2] + ".jpg"))][:a.max]
    print("%d to make, estimated US$%.2f" % (len(items), len(items) * g.EST_USD["higgsfield"]))
    if not a.go: return 0
    key = g.key_for("higgsfield")
    with ThreadPoolExecutor(a.par) as ex:
        for fn, st in ex.map(lambda i: one(i, key), items): print(" ", st, fn)
    manp = os.path.join(OUT, "app_pictures_manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    for i in todo_list(a.cc):
        if os.path.exists(os.path.join(OUT, i[2] + ".jpg")) and i[2] not in man:
            man[i[2]] = {"made": datetime.datetime.utcnow().isoformat() + "Z", "provider": "higgsfield", "ruling": "RUL-164 / COUNTRY-PACK-1"}
    json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
    return 0
if __name__ == "__main__": sys.exit(main())
