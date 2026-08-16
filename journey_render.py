#!/usr/bin/env python3
"""journey_render.py — the ONE journey renderer (Planner Lane Phase A, 16 Aug 2026).

Extracted from build_journey.py so the SAME rendering serves both worlds:
  media="embed" — the CLI showcases: photos from disk become data URIs (as always)
  media="url"   — server-side personal maps: photos stay URLs (media-as-URL doctrine),
                  pages land well under 300 KB and open instantly on a phone.
Both modes share journey_template.html, so PIN-SPREAD and every future template
improvement applies to showcases AND personal maps alike (RG-0096 pattern).

Also home to the Heritage Planner's pure logic (assemble + validate): the AI never
writes coordinates — it picks wonder IDs and words; assemble_heritage_spec() builds
the spec from the wonders dataset rows, so geography cannot be hallucinated.
Stdlib only (Pillow optional for embed mode).
"""
import base64, io, json, os

MAX_W, JPEG_Q = 640, 72

TYPE_BG = {"start": "#2e7d32", "finish": "#b91c1c", "over": "#0c1a2e",
           "sight": "#1f6f52", "food": "#C8873A", "view": "#3b5ba5"}

DEFAULT_OV = {"ends": "🚩 Start &amp; finish", "over": "🛏️ Overnight stays",
              "food": "🍽️ Food &amp; dishes", "view": "🏔️ Viewpoints",
              "sight": "📍 Sights", "route": "〰️ Route", "towns": "◉ Towns", "her": "🏛️ Heritage sites"}

DAY_COLORS = ["#2e7d32", "#3b5ba5", "#C8873A", "#7b4fa6", "#b3362e"]


def _esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def placeholder(stop):
    """A styled 'photo pending' tile so the map works before images exist."""
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


def embed_photo(path):
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


def render_spec(spec, template_html, media="embed", photo_dir=None):
    """Render a journey spec against the template. Returns (html, found, missing).
    Does not mutate the caller's spec."""
    spec = json.loads(json.dumps(spec))
    found = missing = 0
    for day in spec["days"]:
        for stop in day["stops"]:
            fn = stop.pop("photo", None)
            url = stop.pop("photo_url", None)
            if media == "url":
                if url:
                    stop["ph"] = url; found += 1
                else:
                    stop["ph"] = placeholder(stop); missing += 1
            else:
                p = os.path.join(photo_dir, fn) if (fn and photo_dir) else None
                if p and os.path.exists(p) and os.path.getsize(p) > 0:
                    stop["ph"] = embed_photo(p); found += 1
                else:
                    stop["ph"] = placeholder(stop); missing += 1

    data = {"days": spec["days"], "towns": spec.get("towns", []), "her": spec.get("heritage", [])}
    cfg = {
        "unit": spec.get("unit", "Day"),
        "s1": spec.get("stat1_icon", "🥾"),
        "s2": spec.get("stat2_icon", "↗"),
        "routeSummary": spec["route_summary"],
        "legend": spec["legend"],
        "ov": {**DEFAULT_OV, **spec.get("overlays", {})},
    }

    html = template_html
    for token, value in (("{{TITLE}}", spec["title"]), ("{{PILL}}", spec["pill"]),
                         ("{{H1}}", spec["h1"]), ("{{SUB}}", spec["sub"]),
                         ("{{CAP}}", spec["cap"]),
                         ("{{DATA}}", json.dumps(data, ensure_ascii=False)),
                         ("{{CFG}}", json.dumps(cfg, ensure_ascii=False))):
        assert html.count(token) == 1, f"token {token} appears {html.count(token)}x"
        html = html.replace(token, value)
    assert "{{" not in html, "unfilled token remains"
    return html, found, missing


# ── Heritage Planner pure logic (Phase A) ────────────────────────────────────

def validate_heritage_plan(plan, candidate_ids, want_days):
    """The AI's answer must be: {"title","sub","days":[{"title","summary","stop_ids":[...]}]}.
    Raises ValueError with a reason; returns the plan dict on success."""
    if not isinstance(plan, dict):
        raise ValueError("plan is not an object")
    days = plan.get("days")
    if not isinstance(days, list) or len(days) != want_days:
        raise ValueError(f"expected {want_days} days")
    seen = set()
    cids = set(candidate_ids)
    for d in days:
        ids = d.get("stop_ids")
        if not isinstance(ids, list) or not (2 <= len(ids) <= 6):
            raise ValueError("each day needs 2-6 stop_ids")
        for sid in ids:
            if sid not in cids:
                raise ValueError(f"unknown site id {sid!r}")
            if sid in seen:
                raise ValueError(f"site {sid!r} used twice")
            seen.add(sid)
        if not (d.get("title") or "").strip():
            raise ValueError("day missing title")
    return plan


def assemble_heritage_spec(country, plan, wonders_by_id):
    """Build a renderable journey spec from a VALIDATED plan + the wonders dataset.
    Coordinates and photos come only from the dataset — never from the model."""
    n_days = len(plan["days"])
    days_out, total = [], 0
    for i, d in enumerate(plan["days"]):
        stops = []
        ids = d["stop_ids"]
        for j, sid in enumerate(ids):
            w = wonders_by_id[sid]
            typ = ("start" if (i == 0 and j == 0)
                   else "finish" if (i == n_days - 1 and j == len(ids) - 1) else "sight")
            icon = {"start": "🚩", "finish": "🏁"}.get(typ, "🏛️")
            blurb = (d.get("blurbs") or {}).get(sid) or (w.get("description") or "")[:170]
            stops.append({"lat": float(w["lat"]), "lng": float(w["lon"]), "type": typ,
                          "icon": icon, "name": w["name"], "blurb": blurb,
                          "photo_url": w.get("photo") or None})
        total += len(stops)
        days_out.append({"day": i + 1, "title": (d.get("title") or f"Day {i+1}")[:60],
                         "dist": "", "ascent": "", "mode": "drive",
                         "color": DAY_COLORS[i % len(DAY_COLORS)],
                         "summary": (d.get("summary") or "")[:220],
                         "seg": [[s["lat"], s["lng"]] for s in stops],
                         "stops": stops})
    title = (plan.get("title") or f"{country} — a heritage journey")[:80]
    return {"id": "planner", "title": title, "pill": "★ MY HERITAGE JOURNEY",
            "h1": title, "sub": (plan.get("sub") or "A personal heritage route, planned for you")[:180],
            "cap": "", "unit": "Day", "stat1_icon": "🏛️", "stat2_icon": "📍",
            "route_summary": f"{total} heritage sites · {n_days} day(s) · tap a day, then the pins",
            "legend": "", "overlays": {}, "towns": [], "heritage": [], "days": days_out}
