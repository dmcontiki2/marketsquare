#!/usr/bin/env python3
"""gen_ny_example_pictures.py -- NY-EX-PICS-1 (David 24 Oct 2026: "all of them").
Five example photos for each of 17 New York example-advert groups ("Your listing here", RUL-249), filling the
gaps beside the five NY foothold groups. Same lane as the trainer/collector pictures: Higgsfield API key,
prepaid balance, its default model (~US$0.06 a photo). Generated imagery only (SO-1, SO-2, PHOTO-ANON-1):
no faces, no logos, no readable text, clean well-kept clothing for everyone.
Dry run by default; --go spends. Output assets/ny_ex/<group>_<n>.jpg (longest side 1024). Resumes: skips files present."""
import argparse, io, json, os, sys, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_role_pictures as g
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "ny_ex")
STYLE = ("Photorealistic marketplace advert photograph, natural light. Neutral setting that could be in any country: NO recognisable city skyline, NO famous landmarks or bridges, NO country-specific signs. "
         "Clean, well-kept clothing with sleeves and long trousers; nobody identifiable, no faces, no bare arms, shoulders or legs; NO readable text, NO dates or numbers, NO logos, "
         "NO brand names or badges, NO signage, NO number plates. ")
G = {
 "adv_kayak": ["Two sit-on kayaks resting on a wooden dock on a wide calm river at morning, wooded hills on the far bank, paddles and life jackets laid beside them.",
   "Kayakers seen from behind at a distance paddling on a broad calm river, wooded cliffs on the far bank.",
   "Close-up of a kayak bow cutting through calm water, paddle blade dipping, soft morning light.",
   "A row of colourful kayaks on a rack beside a riverside boathouse, life jackets hanging.",
   "Instructor's hands fitting a life jacket buckle on a paddler, seen from behind, on a dock."],
 "adv_hike": ["A forest hiking trail climbing through autumn trees in rolling mountains, morning light.",
   "Two hikers seen from behind at a distance on a rocky ridge overlooking forested valleys.",
   "Hiking boots, trekking poles and a backpack resting on a rock beside a trail.",
   "A waterfall in a mountain gorge seen from a wooden footbridge.",
   "Map and compass on a backpack beside a mountain trail, unreadable map."],
 "adv_cabin": ["Exterior of a single cosy timber cabin standing alone among pine trees on a lakeshore, warm light in its windows at dusk, no other buildings, no people.",
   "A single photograph of a cabin living room: a stone fireplace with a log fire, two armchairs and a wool throw, warm evening light.",
   "Cabin bedroom with a wooden bed, white linen and a window onto pine forest.",
   "A covered porch with two rocking chairs looking out over a calm lake.",
   "A small wooden jetty on the lake in front of the cabin at sunrise, mist on the water."],
 "adv_cycle": ["Hybrid bicycles and helmets lined up beside a riverside cycle path, morning light.",
   "Cyclists seen from behind at a distance riding a tree-lined riverside path.",
   "Close-up of a bicycle handlebar with a bell and a phone mount, path blurred ahead.",
   "Bikes leaning on a wooden railing at a river viewpoint, open countryside beyond.",
   "Close-up of gloved hands adjusting a bicycle seat height with a quick-release lever, on a quiet riverside path, no other people."],
 "lm_produce": ["Wooden crates of red and green apples at an outdoor farmers' market stall.",
   "Baskets of fresh vegetables: tomatoes, peppers, squash and leafy greens on a market table.",
   "Jars of golden local honey stacked on a wooden market table, plain unlabeled lids.",
   "Hands passing a paper bag of fresh peaches across a market stall.",
   "A farmers' market stall table under a canvas awning with seasonal produce, autumn morning."],
 "lm_bakes": ["Freshly baked sourdough loaves cooling on a wire rack on a kitchen counter.",
   "A tray of chocolate chip cookies on a baking sheet, flour dusted wooden board.",
   "A layered homemade cake with berries on a cake stand in a bright kitchen.",
   "Hands boxing cupcakes into a plain white bakery box, no text.",
   "Cinnamon rolls in a baking dish fresh from the oven, warm light."],
 "lm_crafts": ["Hand-knitted scarves and beanies folded on a craft-market table.",
   "Handmade glazed pottery mugs and bowls on a wooden shelf.",
   "Hand-poured candles in plain glass jars on a linen cloth.",
   "Hands shaping a clay bowl on a potter's wheel, seen close-up.",
   "A craft-fair stall table with jewellery, pottery and knitted goods, soft daylight."],
 "col_vinyl": ["Close-up of hands flipping through a wooden crate of vinyl records with plain abstract sleeves, no words anywhere, no signs.",
   "A turntable playing a black vinyl record, tonearm down, warm lamp light.",
   "A shelf wall of vinyl records seen from the side, spines unreadable.",
   "Close-up of a vinyl record's grooves catching the light.",
   "A stack of records with invented abstract-art sleeves on a wooden table."],
 "col_comics": ["Comics in clear plastic bags with backing boards in a long white storage box, invented abstract covers.",
   "A single bagged comic with an invented abstract colourful cover, held by gloved hands.",
   "Rows of comic storage boxes on a shelf in a tidy collector's room.",
   "Close-up of comic pages edges and corners showing near-mint condition, no readable text.",
   "A tidy wooden table with a row of comic books in clear protective sleeves, plain colourful abstract covers, and a magnifying glass beside them."],
 "col_coins": [
   "An open coin album page of old silver and copper coins in plastic slots, seen at an angle so every coin face is soft and its design, lettering and date are unreadable.",
   "A loupe and tweezers beside a single heavily worn old silver coin on navy velvet; the coin's face is smooth and worn flat, with no date, no lettering and no legible inscription.",
   "Coins in clear holders laid out on a dark walnut desk, shot from a low angle with shallow focus so no coin shows any readable date, numbers or lettering.",
   "A collector's white cotton glove holding a worn copper coin edge-on, showing only the reeded rim, no face, date or writing visible.",
   "A small wooden coin cabinet with shallow drawers, one drawer open showing rows of coins from above, coin faces too small and soft to read any date or lettering."],
 "tut_uni": ["Desk detail: a spiral notebook with handwritten calculus working blurred and unreadable, a scientific calculator and a mug, an adult's hands holding a pencil, window light.",
   "Two adults at a library table seen from behind, one pointing at an open textbook, laptops and notes, warm light.",
   "A whiteboard photographed at a steep angle so the equations are softly out of focus and unreadable, a marker in an adult hand.",
   "A quiet study room with a round table, two chairs, textbooks and a laptop, afternoon light.",
   "Close-up of a laptop showing a blurred graph beside printed notes, an adult hand with a highlighter."],
 "fit_trainer": ["Gym floor detail: kettlebells, a resistance band and a clipboard, an adult's hands adjusting a dumbbell.",
   "A personal trainer seen from behind spotting an adult client on a bench press in a bright gym.",
   "Outdoor training in a park: exercise mats, cones and a kettlebell on the grass, morning light.",
   "Close-up of hands in fingerless gloves gripping a rowing machine handle.",
   "A tidy private training studio with racks of dumbbells, a mirror wall angled so no reflection shows a person."],
 "adv_climb": ["Indoor climbing wall seen from below with colourful holds, a climber seen from behind at a distance wearing a helmet.",
   "A coiled climbing rope, harness and chalk bag on a wooden bench.",
   "An instructor's hands checking a climber's harness buckle, seen close-up.",
   "An outdoor rock face with a climber seen from behind at a distance, belayer at the base, both in helmets.",
   "Climbing shoes and a chalk bag beside a bouldering mat."],
 "adv_cave": ["Inside a limestone cave passage lit by headlamps, two cavers seen from behind at a distance in helmets and coveralls.",
   "Caving helmets with headlamps and gloves laid out on a rock at a cave entrance.",
   "A caver seen from behind crouching through a low passage, headlamp beam on wet rock.",
   "Stalactites lit by a headlamp in a large cave chamber.",
   "A forest path leading to a cave entrance, a small group seen from behind at a distance in helmets."],
 "tut_chess": ["Close-up of a wooden chess board mid-game, an adult hand moving a knight, a chess clock beside it.",
   "Two adults seen from the side at a chess table in a club room, faces out of frame, hands over the pieces.",
   "A demonstration chess board on a stand in a club room, rows of tables with boards set up.",
   "A chess clock and a scoresheet with unreadable handwriting beside a board.",
   "Chess pieces set up on a board on a park table, autumn leaves, no people."],
 "tut_music": ["Close-up of hands on piano keys in a bright home music room.",
   "An acoustic guitar on a stand beside a music stand with sheet music, notes unreadable.",
   "A piano lesson seen from above: a teacher's hand and a student's hand side by side on the black and white keys of an upright piano, sheet music blurred.",
   "A violin and bow resting on an open case in warm window light.",
   "A home music room with an upright piano, a guitar and two chairs."],
 "tut_lang": ["A desk with open language textbooks, flashcards and a laptop, no readable words.",
   "Hands writing in a notebook beside a cup of coffee, text blurred and unreadable.",
   "A small table set for one-to-one tutoring, two chairs, books and a tablet.",
   "A globe and a stack of dictionaries on a desk in a bright study room, spines unreadable.",
   "Video-call tutoring setup: laptop, headset and notebook on a tidy desk."],
 "svc_dog": ["A dog walker seen from behind walking three happy dogs on leashes in a leafy park.",
   "Close-up of a hand holding several dog leashes, dogs blurred ahead on a park path.",
   "A golden retriever sitting patiently on a park path, leash held by a hand.",
   "Dog treats, a water bowl and poop bags clipped to a backpack on a park bench.",
   "Two dogs playing on autumn grass in a park, walker standing at a distance."],
 "svc_handy": ["A paint roller rolling fresh white paint on a living-room wall, hands only.",
   "A neat toolbox open on a drop cloth: screwdrivers, a level, a drill.",
   "Gloved hands adjusting the hinge of a white kitchen cupboard door with a screwdriver.",
   "Masking tape along a window frame ready for painting, drop cloths on the floor.",
   "A freshly painted bright room with a ladder folded against the wall."],
 "svc_elec": ["Hands in insulated gloves installing a white light switch on a cream wall.",
   "A tidy residential electrical panel opened for inspection, tester in hand, no labels readable.",
   "Electrician's tool belt with pliers, wire strippers and a voltage tester.",
   "Hands fitting a modern ceiling light fixture, seen from below, ladder edge visible.",
   "Coiled electrical cable and a box of connectors on a workbench."],
 "car_pickup": ["A clean dark blue full-size pickup truck parked on a suburban driveway, three-quarter view, no badges or plates.",
   "Interior of the pickup: clean dashboard and front seats, no readable screens.",
   "The pickup's open load bed with a bed liner, tidy and empty.",
   "Close-up of the pickup's wheel and all-terrain tyre.",
   "The pickup truck parked on a country road with autumn trees, side view, no badges or plates."],
 "car_moto": ["A clean naked-style motorcycle parked on a quiet city street, side view, no badges or plates.",
   "Close-up of the motorcycle's gauges and handlebars, no readable numbers.",
   "Close-up of a polished motorcycle engine and exhaust, plain engine covers with no emblem, badge or lettering.",
   "Motorcycle seat and tank seen from above, no logos.",
   "Close-up of the motorcycle front tyre and disc brake."],
}
def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--go", action="store_true"); ap.add_argument("--only"); ap.add_argument("--max", type=int, default=999); ap.add_argument("--provider", default="atlas"); ap.add_argument("--par", type=int, default=8)
    a = ap.parse_args(); prov = a.provider; os.makedirs(OUT, exist_ok=True)
    todo = [(k, i + 1, p) for k, ps in G.items() if not a.only or k.startswith(a.only) for i, p in enumerate(ps)]
    left = [t for t in todo if not os.path.exists(os.path.join(OUT, "%s_%d.jpg" % (t[0], t[1])))]
    print("%d photos, %d left, estimated US$%.2f" % (len(todo), len(left), len(left) * g.EST_USD[prov]))
    if not a.go: print("DRY RUN -- add --go"); return 0
    key = g.key_for(prov)
    if not key: print("NO KEY"); return 2
    manp = os.path.join(OUT, "manifest.json")
    man = json.load(open(manp, encoding="utf-8")) if os.path.exists(manp) else {}
    import concurrent.futures as cf, threading
    lock = threading.Lock()
    def one(t):
        slug, n, subj = t; name = "%s_%d" % (slug, n); dst = os.path.join(OUT, name + ".jpg")
        try: raw = g.generate(prov, g.DEFAULT_MODEL[prov], key, STYLE + subj)
        except Exception as e: return "  FAIL %s %s" % (name, str(e)[:160])
        im = Image.open(io.BytesIO(raw)).convert("RGB"); im.thumbnail((1024, 1024)); im.save(dst, "JPEG", quality=88)
        with lock:
            man[name] = {"made": datetime.datetime.utcnow().isoformat() + "Z", "provider": prov, "model": g.DEFAULT_MODEL[prov],
                         "quality": os.environ.get("ATLAS_QUALITY", "low") if prov == "atlas" else "", "prompt": STYLE + subj, "ruling": "RUL-249 / NY-EX-PICS-1"}
            json.dump(man, open(manp, "w", encoding="utf-8"), indent=1)
        return "  made " + name
    with cf.ThreadPoolExecutor(a.par) as ex:
        for r in ex.map(one, left[:a.max]): print(r, flush=True)
    return 0
if __name__ == "__main__": sys.exit(main())
