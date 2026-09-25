#!/usr/bin/env python3
"""gen_kind_fit_pictures.py -- KIND-FIT-1 (David 25 Sep 2026: "add photo generic types with the right categories"; 14 approved, ~US$0.84). Derived from gen_goods_pictures.py.\nOriginal note: GOODS-FIT-1 (David 25 Sep 2026: Plants showed a house). Tile pictures for Local Market, Cars and Property kinds that wore another kind's picture. Derived from gen_collector_pictures.py -- COL-PICS-1 (David 25 Sep 2026: "I selected 'Cards' here and the generic
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
 "svc_plumber": "A plumber's gloved hands fitting a chrome tap under a kitchen sink with a pipe wrench and new copper pipes, no face visible.",
 "svc_handyman": "A handyman's open toolbox with a cordless drill, spirit level, tape measure and screws on a wooden workbench, a shelf half-mounted on the wall behind.",
 "svc_painter": "A freshly painted interior wall in a warm colour with a paint roller, tray and brushes on a drop cloth, masking tape along the skirting board.",
 "svc_pool": "A sparkling blue backyard swimming pool being cleaned with a leaf net and brush on long poles, a basket of pool chemicals beside it, no people.",
 "lm_crafts": "Handmade crafts on a market table: beaded jewellery, woven baskets, small carved wooden animals and glazed pottery bowls.",
 "tut_english": "A learner's desk with an open English novel, a stack of paperback classics, a notebook with tiny unreadable handwriting, a pencil and a reading lamp.",
 "tut_afrikaans": "A school exercise book, a thick bilingual dictionary and a pencil case on a desk beside a window with purple jacaranda trees outside, a language lesson.",
 "tut_accounting": "An accounting study desk: a ledger workbook with ruled columns, a calculator, a few receipts and a highlighter, no readable text.",
 "tut_coding": "A laptop showing blurred colourful lines of code on a tidy study desk with a notebook and a cup of tea, a coding lesson at home.",
 "hh_cleaning": "Cleaning supplies - a mop and bucket, spray bottles and cloths - on a freshly cleaned, shining tiled kitchen floor in a family home, no people.",
 "hh_laundry": "A neat pile of freshly ironed shirts and folded towels beside an iron on an ironing board in a sunny laundry room, no people.",
 "hh_cooking": "A home-cooked South African meal being prepared on a stove: a pot of stew, fresh vegetables and a wooden spoon on the kitchen counter, no people.",
 "hh_childminding": "A tidy children's play corner in a family home with wooden building blocks, picture books and a soft play mat, sunny window, no people.",
 "hh_office": "An open-plan office after cleaning: a vacuum cleaner and a cleaning trolley beside tidy desks and shining floors, evening light, no people.",
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only")
    a = ap.parse_args(); prov = "higgsfield"
    todo = {k: v for k, v in PICS.items() if not a.only or k.startswith(a.only)}
    print("%d kind pictures, estimated US$%.2f" % (len(todo), len(todo) * g.EST_USD[prov]))
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
                              "prompt": STYLE + subj, "ruling": "RUL-164 / KIND-FIT-1"}
        json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        print("  made", slug)
    return 0
if __name__ == "__main__": sys.exit(main())
