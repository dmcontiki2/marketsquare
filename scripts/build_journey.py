#!/usr/bin/env python3
"""build_journey.py — build a MarketSquare interactive journey map from a spec.

Why: bavaria_journey.html and adventures_reserve_map.html were each hand-built. Four
more journeys (and every one after) should not be. This takes a JSON spec plus a photo
folder and emits a self-contained map in the house look, with the reserve map's
tick-box layer control folded in so a viewer can switch stop types on and off.

    python3 scripts/build_journey.py journeys/namibia.json
    python3 scripts/build_journey.py journeys/*.json          # build them all

Photos: each stop names a file in the spec's photo_dir. A missing file becomes a
styled placeholder tile, so the map is fully working before any image exists and the
real photo drops in later with no other change. Re-run the build after generating.

Output: <spec.out> in the repo root (default: <id>_journey.html).
Stdlib only; uses Pillow to shrink photos when available, otherwise embeds as-is.
"""
import base64, glob, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
TEMPLATE = os.path.join(HERE, "journey_template.html")

MAX_W, JPEG_Q = 640, 72

# Fallback tile colours per stop type — matches COL in the template.
TYPE_BG = {"start": "#2e7d32", "finish": "#b91c1c", "over": "#0c1a2e",
           "sight": "#1f6f52", "food": "#C8873A", "view": "#3b5ba5"}


def placeholder(stop):
    """A styled 'photo pending' tile so the map works before images are generated."""
    bg = TYPE_BG.get(stop.get("type"), "#0c1a2e")
    icon = stop.get("icon", "📍")
    name = (stop.get("name") or "")[:40]
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="380">'
        f'<defs><linearGradient id="g" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0%" stop-color="{bg}"/><stop offset="100%" stop-color="#0c1a2e"/>'
        '</linearGradient></defs>'
        '<rect width="640" height="380" fill="url(#g)"/>'
        f'<text x="320" y="176" font-size="86" text-anchor="middle">{icon}</text>'
        f'<text x="320" y="236" font-size="21" fill="#e8eef7" text-anchor="middle" '
        f'font-family="Georgia,serif">{_esc(name)}</text>'
        '<text x="320" y="266" font-size="13" fill="#93a4bd" text-anchor="middle" '
        'font-family="Helvetica,Arial,sans-serif">photo pending</text></svg>'
    )
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode()


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def embed(path):
    """Read an image, shrink it if Pillow is around, return a data URI."""
    raw = open(path, "rb").read()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        im = im.convert("RGB")
        if im.width > MAX_W:
            im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=JPEG_Q, optimize=True)
        raw = buf.getvalue()
    except ImportError:
        pass          # no Pillow — embed the original bytes
    except Exception as e:
        print(f"    ! could not process {os.path.basename(path)} ({e}); embedding raw")
    return "data:image/jpeg;base64," + base64.b64encode(raw).decode()


DEFAULT_OV = {"ends": "🚩 Start &amp; finish", "over": "🛏️ Overnight stays",
              "food": "🍽️ Food &amp; dishes", "view": "🏔️ Viewpoints",
              "sight": "📍 Sights", "route": "〰️ Route", "towns": "◉ Towns"}


def build(spec_path):
    spec = json.load(open(spec_path, encoding="utf-8"))
    jid = spec["id"]
    photo_dir = os.path.join(REPO, spec.get("photo_dir", f"assets/journey/{jid}"))
    out_path = os.path.join(REPO, spec.get("out", f"{jid}_journey.html"))

    found = missing = 0
    for day in spec["days"]:
        for stop in day["stops"]:
            fn = stop.pop("photo", None)
            p = os.path.join(photo_dir, fn) if fn else None
            if p and os.path.exists(p) and os.path.getsize(p) > 0:
                stop["ph"] = embed(p)
                found += 1
            else:
                stop["ph"] = placeholder(stop)
                missing += 1

    data = {"days": spec["days"], "towns": spec.get("towns", [])}
    cfg = {
        "unit": spec.get("unit", "Day"),
        "s1": spec.get("stat1_icon", "🥾"),
        "s2": spec.get("stat2_icon", "↗"),
        "routeSummary": spec["route_summary"],
        "legend": spec["legend"],
        "ov": {**DEFAULT_OV, **spec.get("overlays", {})},
    }

    html = open(TEMPLATE, encoding="utf-8").read()
    for token, value in (("{{TITLE}}", spec["title"]), ("{{PILL}}", spec["pill"]),
                         ("{{H1}}", spec["h1"]), ("{{SUB}}", spec["sub"]),
                         ("{{CAP}}", spec["cap"]),
                         ("{{DATA}}", json.dumps(data, ensure_ascii=False)),
                         ("{{CFG}}", json.dumps(cfg, ensure_ascii=False))):
        assert html.count(token) == 1, f"{spec_path}: token {token} appears {html.count(token)}x"
        html = html.replace(token, value)

    assert "{{" not in html, f"{spec_path}: unfilled token remains"
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(html)

    stops = sum(len(d["stops"]) for d in spec["days"])
    print(f"  {os.path.basename(out_path):32} {len(html)//1024:>5} KB · "
          f"{len(spec['days'])} {cfg['unit'].lower()}s · {stops} stops · "
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
