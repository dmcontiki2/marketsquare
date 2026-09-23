#!/usr/bin/env python3
"""gen_app_pictures.py -- APP-PICS-1 (RUL-164, David 23 Sep 2026): the prepaid image account makes
APPLICATION pictures and examples we show users -- never a user's own photos, never a stand-in for them.

First set: the Quick door's "Where do you work?" step. It showed house interiors (a bedroom for
Mamelodi, a bath for Menlyn) so a place read like a property for sale (audit F9). These are
street-level scenes that say "this part of town", with no faces, no readable signs, no logos and no
single identifiable landmark -- an illustration of an area, not a claim about a specific building.

Dry run by default; --go spends (~US$0.06 each). Reuses gen_role_pictures.generate() and its key
lookup, so the provider/model stay settings, never names in the app. Output: assets/quick_ph/
place_<slug>.jpg at 300x300 (door size), pushed by media_push.bat [1d]. Logged in
assets/quick_ph/app_pictures_manifest.json.
"""
import argparse, datetime, io, json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_role_pictures as g
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "quick_ph")
STYLE = ("Photorealistic, natural daylight, warm late-afternoon light, shallow depth of field, square 1:1. "
         "Street-level view of an ordinary South African suburb scene. NO people's faces (people only from "
         "behind or far away), NO readable text, NO signs with words, NO logos, NO brand names, NO single famous "
         "landmark. Calm, welcoming, true to Gauteng: jacaranda or acacia trees, highveld sky. ")
PLACES = {
 "pretoria_east": "Pretoria East: a quiet tree-lined residential street with walled family homes, lawns and a jacaranda tree.",
 "centurion": "Centurion: a neat suburban road with modern townhouses, clipped hedges and a wide highveld sky.",
 "mamelodi": "Mamelodi: a well-kept paved residential street of neat face-brick family homes with painted gates, small tended gardens and a jacaranda, the Magaliesberg ridge soft in the distance. Proud, orderly, welcoming -- the same care as any suburb.",
 "menlyn": "Menlyn: a busy modern retail and office precinct seen from a tree-lined sidewalk, glass buildings blurred in the background.",
 "midrand": "Midrand: open highveld land beside new office parks and a highway overpass in the distance, dry grass and acacia trees.",
 "sandton": "Sandton: a leafy upmarket avenue with high garden walls and tall office towers softly blurred on the skyline.",
}

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only")
    ap.add_argument("--provider", default="higgsfield"); a = ap.parse_args()
    todo = {k: v for k, v in PLACES.items() if not a.only or k == a.only}
    print("%d app pictures, estimated US$%.2f" % (len(todo), len(todo) * g.EST_USD[a.provider]))
    if not a.go:
        print("DRY RUN -- add --go"); return 0
    key = g.key_for(a.provider)
    if not key:
        print("NO KEY"); return 2
    os.makedirs(OUT, exist_ok=True)
    manp = os.path.join(OUT, "app_pictures_manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    made = 0
    for slug, place in todo.items():
        try:
            raw = g.generate(a.provider, g.DEFAULT_MODEL[a.provider], key, STYLE + place)
        except Exception as e:
            print("  FAIL %s %s" % (slug, str(e)[:160])); continue
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        w, h = im.size; s = min(w, h)
        im = im.crop(((w - s) // 2, (h - s) // 2, (w - s) // 2 + s, (h - s) // 2 + s)).resize((300, 300), Image.LANCZOS)
        im.save(os.path.join(OUT, "place_%s.jpg" % slug), "JPEG", quality=84)
        im2 = Image.open(io.BytesIO(raw)).convert("RGB"); im2.thumbnail((1024, 1024))
        os.makedirs(os.path.join(OUT, "_full"), exist_ok=True)
        im2.save(os.path.join(OUT, "_full", "place_%s.jpg" % slug), "JPEG", quality=88)
        man["place_" + slug] = {"use": "app picture (Quick 'where' step)", "made": datetime.datetime.now().isoformat(timespec="seconds"),
                                "provider": a.provider, "prompt": STYLE + place}
        json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        made += 1; print("  ok %s" % slug, flush=True)
    print("made %d of %d" % (made, len(todo)))
    return 0 if made == len(todo) else 1

if __name__ == "__main__":
    sys.exit(main())
