#!/usr/bin/env python3
"""make_prompt_pack.py — emit the Higgsfield prompt pack for the journey maps.

Generated FROM journeys/*.json, so the prompts can never drift from the maps they
fill. Re-run after editing any spec. Same house rules as ADVENTURES_EXPANSION_PROMPTS.md:
no identifiable faces (PHOTO-ANON-1), no readable text, no logos, 3:2.

    python3 scripts/make_prompt_pack.py            -> JOURNEY_HIGGSFIELD_PROMPTS.md
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)

STYLE = {
    "namibia": ("Photorealistic editorial travel photography, Namibia — red Sossusvlei dunes, "
                "gravel plains and Atlantic fog, hard clean desert light with long shadows, "
                "deep navy and warm amber accents (#0c1a2e / #C8873A)"),
    "botswana": ("Photorealistic editorial safari photography, Botswana — Okavango channels, "
                 "mopane woodland and white salt pan, warm golden-hour light and dust, "
                 "deep navy and warm amber accents (#0c1a2e / #C8873A)"),
    "mozambique": ("Photorealistic editorial travel photography, Mozambique Indian Ocean coast — "
                   "turquoise water, dhow sails, coral-stone and whitewash, bright tropical light "
                   "with deep navy and warm amber accents (#0c1a2e / #C8873A)"),
    "cape_cairo": ("Photorealistic editorial rail-travel photography, Africa end to end — grand "
                   "stations, sleeper-car interiors in brass and teak, Karoo, Zambezi, savanna and "
                   "Nile desert, cinematic warm light, deep navy and warm amber accents "
                   "(#0c1a2e / #C8873A)"),
}

FRAMING = {
    "start":  "Wide establishing shot with a clear sense of departure and journey ahead.",
    "finish": "Wide closing shot with a sense of arrival and completion, golden light.",
    "over":   "Warm inviting accommodation shot at dusk or night, lamplight, no people visible or "
              "only distant silhouettes.",
    "food":   "Close, appetising food photography — shallow depth of field, steam or char visible, "
              "hands only if anyone appears, natural setting behind.",
    "view":   "Wide landscape shot, strong depth, dramatic natural light, human figures tiny or absent.",
    "sight":  "Characterful detail or mid shot of the landmark or subject, strong sense of place.",
}

RULES = ("NO identifiable human faces (people from behind, in silhouette, or in shadow only), "
         "no readable text, no logos, no watermarks, aspect ratio 3:2, high detail, natural colour.")


def main():
    specs = sorted(glob.glob(os.path.join(REPO, "journeys", "*.json")))
    if not specs:
        print("no specs found"); return 1
    out = [
        "# Journey Super-Adverts — Higgsfield Prompt Pack",
        "",
        "Photos for the interactive journey maps (Namibia, Botswana, Mozambique, Cape to Cairo).",
        "GENERATED from `journeys/*.json` by `scripts/make_prompt_pack.py` — do not hand-edit;",
        "edit the spec and re-run, so the prompts and the maps can never drift apart.",
        "",
        "**Brand rule (PHOTO-ANON-1):** nobody's face is ever recognisable. Guides in silhouette,",
        "travellers from behind, cooks by their hands. Anonymous until introduced.",
        "",
        "**Consistency:** lock the seed/style after the first frame you love in a journey so the",
        "SAME vehicle / SAME train / SAME lodge carries through that whole set.",
        "",
        "**Wiring after generation:** drop the files into the `photo_dir` named below (filenames",
        "must match exactly), then re-run `python3 scripts/build_journey.py` — the builder embeds",
        "and shrinks them automatically and replaces the placeholder tiles. No other change needed.",
        "",
    ]
    grand = 0
    for sp in specs:
        spec = json.load(open(sp, encoding="utf-8"))
        jid = spec["id"]
        n = sum(len(d["stops"]) for d in spec["days"])
        grand += n
        out += ["---", "",
                f"## {spec['h1']}  ({n} photos)",
                "",
                f"- **photo_dir:** `{spec.get('photo_dir')}`",
                f"- **output:** `{spec.get('out')}`",
                "",
                "### Style block — paste FIRST into every prompt in this journey",
                f"> {STYLE.get(jid, 'Photorealistic editorial travel photography')}, "
                f"shallow depth of field where appropriate. {RULES}",
                "",
                "| File | Prompt (after style block) |",
                "|---|---|"]
        for d in spec["days"]:
            for st in d["stops"]:
                fn = st.get("photo") or ""
                blurb = st["blurb"].replace("|", "/").replace("&amp;", "&")
                name = st["name"].replace("|", "/").replace("&amp;", "&")
                frame = FRAMING.get(st["type"], "")
                prompt = f"{name} — {blurb} {frame}"
                out.append(f"| `{fn}` | {prompt} |")
        out.append("")
    out += ["---", "",
            f"**Total: {grand} photos across {len(specs)} journeys.**",
            "",
            "Suggested order — do one journey per overnight run so a bad style lock costs one set,",
            "not four. Generate, then re-run the builder and check the map before starting the next.",
            ""]
    dest = os.path.join(REPO, "JOURNEY_HIGGSFIELD_PROMPTS.md")
    open(dest, "w", encoding="utf-8").write("\n".join(out))
    print(f"wrote {dest} — {grand} prompts across {len(specs)} journeys")
    return 0


if __name__ == "__main__":
    sys.exit(main())
