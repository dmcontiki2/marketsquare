#!/usr/bin/env python3
"""gen_destination_pictures.py -- DEST-PICS-1 (David 25 Sep 2026: "I selected a Game Lodge, but this screen is showing suburb information?") Destination pictures for the Adventures WHERE step. Derived from gen_collector_pictures.py -- COL-PICS-1 (David 25 Sep 2026: "I selected 'Cards' here and the generic
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
STYLE = ("Photorealistic travel photograph, square 1:1, golden-hour light, wide landscape view. "
         "NO readable text, NO signs, NO logos, NO brand names, NO faces (people only far away or from behind). ")
PICS = {
 "kruger": "Kruger National Park: open bushveld savanna with elephants at a waterhole and a marula tree.",
 "pilanesberg": "Pilanesberg: a green volcanic crater valley with rolling hills, a lake and zebra grazing.",
 "waterberg": "Waterberg: red sandstone cliffs above dense bushveld and a winding river valley.",
 "madikwe": "Madikwe: dry golden grassland with scattered camelthorn trees and a pair of giraffe at dusk.",
 "zululand": "Zululand: lush green hills of Hluhluwe with white rhino grazing and misty valleys.",
 "addo": "Addo, Eastern Cape: thick green spekboom thicket with a herd of elephants on a red dirt track.",
 "cape_town": "Cape Town: Table Mountain with its flat top above the city bowl and the ocean at sunset, seen from afar.",
 "garden_route": "Garden Route: an indigenous forest meeting a lagoon and golden beach on the southern Cape coast.",
 "drakensberg": "Drakensberg: towering basalt mountain walls above green grassland and a mountain stream.",
 "cradle": "Cradle of Humankind: rolling highveld grassland with a limestone cave entrance among trees.",
 "soweto": "Soweto: a lively street of neat township homes with colourful walls and big sky at sunset, people far away.",
 "mapungubwe": "Mapungubwe: huge baobab trees among sandstone koppies above the Limpopo river valley.",
 "panorama": "Panorama Route, Mpumalanga: a deep green canyon with round rock towers and a waterfall.",
 "wild_coast": "Wild Coast: green hills rolling down to a rocky shore with a natural rock arch in the sea.",
 "karoo": "Karoo: vast flat semi-desert plains with a lone windmill and flat-topped koppies at dusk.",
 "namaqualand": "Namaqualand: a valley carpeted in orange and white spring wildflowers under blue sky.",
 "victoria_falls": "Victoria Falls: the wide curtain of the falls with spray and a rainbow above the gorge.",
 "durban": "Durban: golden beach and warm Indian Ocean waves with palm trees along the promenade, people far away.",
 "vaal_dam": "Vaal Dam: a wide calm dam at sunrise with a small fishing boat and reeds on the shore.",
 "hartbeespoort": "Hartbeespoort Dam: calm water below the Magaliesberg mountains with a fishing jetty.",
 "jozini": "Lake Jozini: a long blue lake between the Lebombo mountains with a fishing boat.",
 "sodwana": "Sodwana Bay: a turquoise bay with a white sand beach and a ski-boat pulled up on the sand.",
 "orange_river": "Orange River: a wide river through rugged desert canyon rock with a canoe on the bank.",
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only")
    a = ap.parse_args(); prov = "higgsfield"
    todo = {k: v for k, v in PICS.items() if not a.only or k.startswith(a.only)}
    print("%d destination pictures, estimated US$%.2f" % (len(todo), len(todo) * g.EST_USD[prov]))
    if not a.go: print("DRY RUN -- add --go"); return 0
    key = g.key_for(prov)
    if not key: print("NO KEY"); return 2
    manp = os.path.join(OUT, "app_pictures_manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    for slug, subj in todo.items():
        dst = os.path.join(OUT, "dest_%s.jpg" % slug)
        if os.path.exists(dst): print("  have", slug); continue
        try:
            raw = g.generate(prov, g.DEFAULT_MODEL[prov], key, STYLE + subj)
        except Exception as e:
            print("  FAIL %s %s" % (slug, str(e)[:160])); continue
        im = Image.open(io.BytesIO(raw)).convert("RGB"); w, h = im.size; s = min(w, h)
        im.crop(((w-s)//2, (h-s)//2, (w-s)//2+s, (h-s)//2+s)).resize((300, 300), Image.LANCZOS).save(dst, "JPEG", quality=84)
        os.makedirs(os.path.join(OUT, "_full"), exist_ok=True)
        im2 = Image.open(io.BytesIO(raw)).convert("RGB"); im2.thumbnail((1024, 1024))
        im2.save(os.path.join(OUT, "_full", "dest_%s.jpg" % slug), "JPEG", quality=88)
        man["dest_" + slug] = {"made": datetime.datetime.utcnow().isoformat() + "Z", "provider": prov,
                              "prompt": STYLE + subj, "ruling": "RUL-164 / DEST-PICS-1"}
        json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        print("  made", slug)
    return 0
if __name__ == "__main__": sys.exit(main())
