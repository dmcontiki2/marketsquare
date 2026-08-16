#!/usr/bin/env python3
"""build_journey.py — CLI: build showcase journey maps from specs (embed mode).

Phase A refactor (16 Aug 2026): the rendering itself moved to journey_render.py so
the server can render personal maps from the SAME template (media-as-URL mode).
This wrapper keeps the exact CLI behaviour:

    python3 scripts/build_journey.py journeys/namibia.json
    python3 scripts/build_journey.py                         # build them all
"""
import glob, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "journey_template.html")
sys.path.insert(0, REPO)
import journey_render


def build(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    jid = spec["id"]
    photo_dir = os.path.join(REPO, spec.get("photo_dir", f"assets/journey/{jid}"))
    out_path = os.path.join(REPO, spec.get("out", f"{jid}_journey.html"))
    template = open(TEMPLATE, encoding="utf-8").read()

    html, found, missing = journey_render.render_spec(
        spec, template, media="embed", photo_dir=photo_dir)

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)
    stops = sum(len(d["stops"]) for d in spec["days"])
    print(f"  {os.path.basename(out_path):32} {len(html)//1024:>5} KB · "
          f"{len(spec['days'])} {spec.get('unit','Day').lower()}s · {stops} stops · "
          f"photos {found} embedded / {missing} pending")
    return out_path


def main(argv):
    specs = []
    for a in argv or [os.path.join(REPO, "journeys", "*.json")]:
        specs.extend(sorted(glob.glob(a)))
    if not specs:
        print("no spec files matched"); return 1
    print(f"building {len(specs)} journey map(s)")
    for s in specs:
        build(s)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
