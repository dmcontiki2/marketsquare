#!/usr/bin/env python3
"""gen_trip_kind_pictures.py -- TRIP-TYPE-1: tile pictures for the Adventures kinds that wore another kind's picture (tour, rail, fishing, self-drive). Derived from gen_collector_pictures.py -- COL-PICS-1 (David 25 Sep 2026: "I selected 'Cards' here and the generic
photos shows coins, can we add related photos, to be generated in Higgsfield"). Example pictures for the
Collectables kinds that had none (stamps, cards, militaria, watches, art), two each, so an example advert
shows the kind of thing she picked. Application pictures under RUL-164 -- never a user's own photos.
No readable text, no logos, no brands, no real card-game artwork, no real insignia.
Dry run by default; --go spends (~US$0.06 each, prepaid). Output assets/quick_ph/col_<kind>_<n>.jpg 300x300."""
import argparse, io, json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_role_pictures as g
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "quick_ph")
STYLE = ("Photorealistic travel photograph, square 1:1, golden-hour light. NO readable text, NO signs, NO logos, "
         "NO brand names, NO faces (people only far away or from behind). ")
PICS = {
 "guided_tour": "A small group of travellers seen from behind following a guide along a scenic heritage trail with a view over mountains.",
 "rail_journey": "A classic vintage passenger train with dark green carriages winding through a golden African landscape at sunset, no lettering on the train.",
 "fishing": "A fly-fishing angler seen from behind standing in a calm river at sunrise, mist over the water, rod arched.",
 "self_drive": "A dusty off-road vehicle with a rooftop tent parked on a gravel road in wide open savanna at sunset, no badges or brand marks.",
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only")
    a = ap.parse_args(); prov = "higgsfield"
    todo = {k: v for k, v in PICS.items() if not a.only or k.startswith(a.only)}
    print("%d trip-kind pictures, estimated US$%.2f" % (len(todo), len(todo) * g.EST_USD[prov]))
    if not a.go: print("DRY RUN -- add --go"); return 0
    key = g.key_for(prov)
    if not key: print("NO KEY"); return 2
    manp = os.path.join(OUT, "app_pictures_manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    for slug, subj in todo.items():
        dst = os.path.join(OUT, "advk_%s.jpg" % slug)
        if os.path.exists(dst): print("  have", slug); continue
        try:
            raw = g.generate(prov, g.DEFAULT_MODEL[prov], key, STYLE + subj)
        except Exception as e:
            print("  FAIL %s %s" % (slug, str(e)[:160])); continue
        im = Image.open(io.BytesIO(raw)).convert("RGB"); w, h = im.size; s = min(w, h)
        im.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s)).resize((300, 300), Image.LANCZOS).save(dst, "JPEG", quality=84)
        os.makedirs(os.path.join(OUT, "_full"), exist_ok=True)
        im2 = Image.open(io.BytesIO(raw)).convert("RGB"); im2.thumbnail((1024, 1024))
        im2.save(os.path.join(OUT, "_full", "advk_%s.jpg" % slug), "JPEG", quality=88)
        man["advk_" + slug] = {"made": datetime.datetime.utcnow().isoformat() + "Z", "provider": prov,
                              "prompt": STYLE + subj, "ruling": "RUL-164 / TRIP-TYPE-1"}
        json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        print("  made", slug)
    return 0
if __name__ == "__main__": sys.exit(main())
