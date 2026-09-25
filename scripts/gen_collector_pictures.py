#!/usr/bin/env python3
"""gen_collector_pictures.py -- COL-PICS-1 (David 25 Sep 2026: "I selected 'Cards' here and the generic
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
STYLE = ("Photorealistic product photograph for a collectors' marketplace, square 1:1, warm soft studio light, "
         "dark walnut wood or navy velvet surface, shallow depth of field, a collector's white cotton glove or loupe "
         "may appear. NO readable text, NO words, NO numbers, NO logos, NO brand names, NO faces. ")
PICS = {
 "stamps_1": "An open stamp album page of old colourful postage stamps with plain unreadable designs of birds, flowers and landscapes, held with tweezers.",
 "stamps_2": "A small stack of vintage postage stamps and a magnifying loupe on dark wood, stamps with plain pictorial designs and no readable lettering.",
 "cards_1": "Collectible trading cards in clear protective graded plastic slabs, laid out in a row, card fronts show abstract colourful fantasy-style artwork with no characters from any real game and no readable text.",
 "cards_2": "A binder of collectible trading cards in plastic sleeves, cards show abstract colourful original artwork, a gloved hand turning a page, no readable text.",
 "militaria_1": "Several old bronze and silver service medals with striped ribbons laid on navy velvet, plain generic designs, no symbols, no text.",
 "militaria_2": "A vintage leather dispatch case with brass buttons, an old compass and a medal with a striped ribbon on dark wood, no insignia, no text.",
 "watches_1": "A classic gold pocket watch with an open lid and chain on navy velvet, plain dial with simple hour marks and no brand name.",
 "watches_2": "Three vintage wristwatches with leather straps in an open wooden watch box, plain dials with simple hour marks, no brand names.",
 "art_1": "A small framed original oil painting of a highveld landscape at sunset leaning on an easel in a quiet room, ornate gold frame.",
 "art_2": "A small bronze sculpture of an antelope beside a framed watercolour of acacia trees on a dark wood table, gallery lighting.",
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only")
    a = ap.parse_args(); prov = "higgsfield"
    todo = {k: v for k, v in PICS.items() if not a.only or k.startswith(a.only)}
    print("%d collector pictures, estimated US$%.2f" % (len(todo), len(todo) * g.EST_USD[prov]))
    if not a.go: print("DRY RUN -- add --go"); return 0
    key = g.key_for(prov)
    if not key: print("NO KEY"); return 2
    manp = os.path.join(OUT, "app_pictures_manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    for slug, subj in todo.items():
        dst = os.path.join(OUT, "col_%s.jpg" % slug)
        if os.path.exists(dst): print("  have", slug); continue
        try:
            raw = g.generate(prov, g.DEFAULT_MODEL[prov], key, STYLE + subj)
        except Exception as e:
            print("  FAIL %s %s" % (slug, str(e)[:160])); continue
        im = Image.open(io.BytesIO(raw)).convert("RGB"); w, h = im.size; s = min(w, h)
        im.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s)).resize((300, 300), Image.LANCZOS).save(dst, "JPEG", quality=84)
        os.makedirs(os.path.join(OUT, "_full"), exist_ok=True)
        im2 = Image.open(io.BytesIO(raw)).convert("RGB"); im2.thumbnail((1024, 1024))
        im2.save(os.path.join(OUT, "_full", "col_%s.jpg" % slug), "JPEG", quality=88)
        man["col_" + slug] = {"made": datetime.datetime.utcnow().isoformat() + "Z", "provider": prov,
                              "prompt": STYLE + subj, "ruling": "RUL-164 / COL-PICS-1"}
        json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        print("  made", slug)
    return 0
if __name__ == "__main__": sys.exit(main())
