#!/usr/bin/env python3
"""make_super_prompt_pack.py — SUPER-AFRICA-1 (10 Aug 2026).

Generates SUPER_LADDER_PROMPTS.md — the Higgsfield prompt pack for the 3-tier
super-advert ladders — FROM the TIERS spec in seed_super_ladder_global.py (read
via ast, never executed, so no DB is needed). Do not hand-edit the output; edit
the seeder spec and re-run, so prompts and adverts can never drift apart.

Filenames follow the ladder glob:  sup_<cc>_<catkey>_<tier>_<n>_<slug>.jpg
Photo counts per tier: advexp/advacc 8 · property 6 · cars 4 · others 3.
Brand rules: PHOTO-ANON-1 (no faces/logos/text/plates) · Nano Banana Pro · 3:2.

    python3 scripts/make_super_prompt_pack.py
"""
import ast, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC  = os.path.join(HERE, "seed_super_ladder_global.py")
DEST = os.path.join(REPO, "SUPER_LADDER_PROMPTS.md")

tree = ast.parse(open(SRC, encoding="utf-8").read())
ns = {}
for node in tree.body:
    if isinstance(node, ast.Assign) and len(node.targets) == 1 \
       and isinstance(node.targets[0], ast.Name) \
       and node.targets[0].id in ("TIERS", "CAT_KEY", "COUNTRIES"):
        ns[node.targets[0].id] = ast.literal_eval(node.value)
TIERS, CAT_KEY, COUNTRIES = ns["TIERS"], ns["CAT_KEY"], ns["COUNTRIES"]
CITY = {cc: city for cc, iso2, cname, city, *_ in COUNTRIES}
CNAME = {cc: cname for cc, iso2, cname, city, *_ in COUNTRIES}

# Per-category shot lists: (slug, shot instruction). {T}=title-derived subject, tier prose woven in.
SHOTS = {
 "advexp": [
  ("hero",    "Hero landscape of the experience at its most dramatic — wide, deep, golden light."),
  ("wildlife","Signature wildlife or action moment, telephoto feel, subject sharp, background melted."),
  ("guests",  "Guests experiencing it — photographed from behind or in silhouette only, leaning into the moment."),
  ("guide",   "The guide at work in silhouette or from behind — gesture, binoculars or wheel, expertise visible without a face."),
  ("golden",  "Golden-hour scene — sundowner, long shadows, warm dust or water light."),
  ("detail",  "Characterful close detail that says 'you are here' — texture, equipment, nature."),
  ("moment",  "A second signature sight or moment unique to this experience."),
  ("finale",  "Closing vista — sense of scale and journey's reward, small or no human figures."),
 ],
 "advacc": [
  ("exterior","Exterior at dusk, lamplight glowing, setting doing the talking."),
  ("room",    "The room — inviting, textured, warm light, no people."),
  ("bed",     "Bed detail — linen, net or throw, tactile close shot."),
  ("view",    "The view from the deck, verandah or window — the reason to stay."),
  ("bath",    "Bathroom or outdoor shower detail — stone, brass, greenery."),
  ("dining",  "Dining or fireside scene — set table or fire, hands at most."),
  ("setting", "The grounds or setting — garden, riverbank or lawn in context."),
  ("sunrise", "Sunrise or night shot — the magic hour that sells the stay."),
 ],
 "property": [
  ("front",   "Front exterior, straight-on or gentle angle, best light of day."),
  ("living",  "Living area — bright, styled, no people."),
  ("kitchen", "Kitchen — clean lines, natural light."),
  ("bedroom", "Main bedroom — calm, made up, soft light."),
  ("outside", "Garden, pool or outdoor living space."),
  ("context", "Street or elevated context shot — the neighbourhood feel, no readable signage."),
 ],
 "cars": [
  ("front34", "Three-quarter front view, clean background, no number plate visible."),
  ("side",    "Full side profile, level lens, even light, no plate."),
  ("interior","Interior — dash and front seats, condition honest and clean."),
  ("rear34",  "Three-quarter rear view, no plate, setting neutral."),
 ],
 "tutors": [
  ("desk",    "Still life of the study desk — books, notes, calculator or laptop, warm lamp."),
  ("session", "Tutoring in progress — hands, pen and page only, or from behind; no faces."),
  ("space",   "The teaching space or materials spread — organised, inviting."),
 ],
 "lm": [
  ("hero",    "Product hero shot — styled, textured background, natural light."),
  ("hands",   "Making-of — the maker's hands at work, craft in progress, no face."),
  ("display", "Market display or grouped arrangement — abundance and colour."),
 ],
 "collect": [
  ("hero",    "The item — macro hero shot, raking light, every surface detail readable EXCEPT text/lettering kept soft."),
  ("spread",  "The collection spread out or arranged — depth, order, care."),
  ("detail",  "Provenance-style detail — sleeve, holder, edge or grain close-up."),
 ],
 "svc": [
  ("action",  "The work in action — hands and tools only, no face."),
  ("kit",     "The professional kit laid out — order, quality, readiness."),
  ("result",  "The finished result — clean, sharp, satisfying."),
 ],
}

TIER_TONE = {"a": "honest, modest, entry-level — clean and real, nothing luxury",
             "b": "established and professional — well-kept, quality mid-market",
             "c": "premium, top-of-field — impeccable styling, magazine grade"}

CAT_SCENE = {
 "advexp": "safari and outdoor adventure photography",
 "advacc": "hospitality and travel accommodation photography",
 "property": "real-estate photography",
 "cars": "automotive listing photography",
 "tutors": "education lifestyle photography",
 "lm": "artisan market and food photography",
 "collect": "collectibles product photography",
 "svc": "professional services photography",
}

lines = [
 "# Super-Advert Ladders — Higgsfield Prompt Pack",
 "",
 "Photos for the 3-tier (a/b/c) super-advert ladders (SUPER-AFRICA-1).",
 "GENERATED from `scripts/seed_super_ladder_global.py` by `scripts/make_super_prompt_pack.py`",
 "— do not hand-edit; edit the seeder spec and re-run.",
 "",
 "**Brand rule (PHOTO-ANON-1):** no identifiable faces (people from behind / silhouette /",
 "hands only), no logos, no readable text, no number plates.",
 "**Model:** Nano Banana Pro · 3:2 · lock seed/style per tier so each listing's set is one",
 "coherent shoot (reference-image consistency; same vehicle / room / product throughout).",
 "",
 "**Wiring after generation:** save as `assets/super/<filename>` exactly as named below,",
 "then run `python3 scripts/seed_super_ladder_global.py` (dry-run shows each tier go live",
 "as its photos land; `--apply` on the server seeds them).",
 "",
]
grand = 0
for (cc, cat), tiers in TIERS.items():
    catkey = CAT_KEY[cat]
    shots = SHOTS[catkey]
    for (tcode, title, price, blurb, *_rest) in tiers:
        n = len(shots)
        grand += n
        lines += [f"---", "",
                  f"## {CNAME[cc]} · {cat} · tier {tcode.upper()}  ({n} photos)", "",
                  f"**Listing:** {title} — {price}", f"**Story:** {blurb}", "",
                  f"### Style block — paste FIRST into every prompt in this set",
                  f"> Photorealistic editorial {CAT_SCENE[catkey]}, {CITY[cc]}, {CNAME[cc]} — "
                  f"{TIER_TONE[tcode]}. Warm natural light, deep navy and warm amber accents "
                  f"(#0c1a2e / #C8873A), shallow depth of field where appropriate. NO identifiable "
                  f"human faces, no readable text, no logos, no watermarks, no number plates, "
                  f"aspect ratio 3:2, high detail, natural colour.", "",
                  "| File | Prompt (after style block) |", "|---|---|"]
        for i, (slug, shot) in enumerate(shots, 1):
            fn = f"sup_{cc}_{catkey}_{tcode}_{i}_{slug}.jpg"
            subject = re.sub(r"\s*—.*$", "", title)
            lines.append(f"| `{fn}` | {subject} — {shot} Context: {blurb[:140]} |")
        lines.append("")
lines += [f"**Total: {grand} photos across {sum(len(v) for v in TIERS.values())} listings.**", ""]
open(DEST, "w", encoding="utf-8").write("\n".join(lines))
print(f"wrote {DEST} — {grand} prompts, {sum(len(v) for v in TIERS.values())} listings")
