#!/usr/bin/env python3
"""gen_goods_pictures.py -- GOODS-FIT-1 (David 25 Sep 2026: Plants showed a house). Tile pictures for Local Market, Cars and Property kinds that wore another kind's picture. Derived from gen_collector_pictures.py -- COL-PICS-1 (David 25 Sep 2026: "I selected 'Cards' here and the generic
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
STYLE = ("Photorealistic product/marketplace photograph, square 1:1, natural warm light, South African setting. "
         "NO readable text, NO logos, NO brand names or badges, NO number plates, NO faces. ")
PICS = {
 "lm_plants": "Potted succulents, herbs and flowering plants in clay pots on a wooden table at a sunny weekend garden market.",
 "lm_furniture": "A restored solid-wood kitchen dresser and two wooden chairs in a bright workshop, handmade furniture for sale.",
 "lm_clothes": "Neatly folded handmade clothing and knitted jerseys on a market stall table, colourful fabrics.",
 "lm_tools": "Second-hand hand tools laid out on a canvas cloth at a flea market: hammers, spanners, a hand saw, a drill.",
 "car_sedan": "A clean silver family sedan parked on a leafy suburban street, side view, no badges or plates.",
 "car_suv": "A dark grey SUV parked on a gravel driveway in front of a garden, three-quarter view, no badges or plates.",
 "car_hatch": "A small red hatchback parked on a quiet street, three-quarter view, no badges or plates.",
 "car_bakkie": "A white single-cab pickup bakkie with a load bin parked on a farm road, no badges or plates.",
 "car_dcab": "A double-cab pickup parked beside a dirt road in the bushveld, four doors visible, no badges or plates.",
 "car_bike": "A motorcycle parked on a quiet road at golden hour, side view, no badges or plates.",
 "prop_townhouse": "A row of modern double-storey townhouses in a secure complex with small gardens, exterior view.",
 "prop_flat": "A modern low-rise block of apartments with balconies and trees, exterior street view.",
 "prop_farm": "A farmhouse with a red roof, a windmill and green fields under a big highveld sky.",
 "prop_plot": "An empty vacant residential plot of land with grass, a few trees and boundary pegs in a quiet suburb, no house on it.",
 "prop_commercial": "A small modern commercial building with shopfronts and parking bays, exterior view, no signage text.",
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only")
    a = ap.parse_args(); prov = "higgsfield"
    todo = {k: v for k, v in PICS.items() if not a.only or k.startswith(a.only)}
    print("%d goods pictures, estimated US$%.2f" % (len(todo), len(todo) * g.EST_USD[prov]))
    if not a.go: print("DRY RUN -- add --go"); return 0
    key = g.key_for(prov)
    if not key: print("NO KEY"); return 2
    manp = os.path.join(OUT, "app_pictures_manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    for slug, subj in todo.items():
        dst = os.path.join(OUT, "%s.jpg" % slug)
        if os.path.exists(dst): print("  have", slug); continue
        try:
            raw = g.generate(prov, g.DEFAULT_MODEL[prov], key, STYLE + subj)
        except Exception as e:
            print("  FAIL %s %s" % (slug, str(e)[:160])); continue
        im = Image.open(io.BytesIO(raw)).convert("RGB"); w, h = im.size; s = min(w, h)
        im.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s)).resize((300, 300), Image.LANCZOS).save(dst, "JPEG", quality=84)
        os.makedirs(os.path.join(OUT, "_full"), exist_ok=True)
        im2 = Image.open(io.BytesIO(raw)).convert("RGB"); im2.thumbnail((1024, 1024))
        im2.save(os.path.join(OUT, "_full", "%s.jpg" % slug), "JPEG", quality=88)
        man[slug] = {"made": datetime.datetime.utcnow().isoformat() + "Z", "provider": prov,
                              "prompt": STYLE + subj, "ruling": "RUL-164 / GOODS-FIT-1"}
        json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        print("  made", slug)
    return 0
if __name__ == "__main__": sys.exit(main())
