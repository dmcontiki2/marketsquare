#!/usr/bin/env python3
"""dashboard_provenance.py -- PROVENANCE-1 (22 Aug 2026).

THE INVENTORY. Enumerates every surface on the dashboard that asserts a STATE
to the reader, and proves each one is actually fed by something.

WHY THIS EXISTS
---------------
David, 22 Aug 2026: "the dashboard becomes a liability if it either shows
stagnant information or the worst case is wrong information ... it feels as if
I am the Automator and need to remember what changed?"

He is describing a real architectural hole, not a mood. A provenance audit that
day found 141 asserted surfaces on dashboard.server.html: 65 live-fed, 8 parsed
from docs, and 68 HAND-TYPED. The same server was costed at EUR 4.51/mo in one
panel and EUR 22.07/mo in another, both hand-typed, neither reconciled against
canon.yml -- which no endpoint served. Six green chips ("kill switches armed",
"nightly backup", "routing on", "scheduled daily", "no-AI default",
"per-use AI") were painted green in the HTML and wired to nothing at all.

The root cause is NOT that people typed values in. It is that:

  (a) NOTHING ENUMERATED THEM. There was no list of what the dashboard claims,
      so the only index was David's memory. That is exactly why he felt like
      the automator -- he WAS the inventory.
  (b) PROVENANCE WAS INVISIBLE. A live chip and a hand-typed chip render
      identically, so a wrong one can only be caught by contradiction against
      something the reader already knows.
  (c) EVERY PRIOR FIX WAS INSTANCE-SCOPED. RG-0133 and RG-0153 each named
      specific element ids. 68 hand-typed surfaces survived both because
      nobody had the list.

THE INVERSION
-------------
Un-fed used to be silent and invisible. Now it is loud by default:

  * A chip carrying a HEALTH COLOUR (green/amber/red) with no id can never be
    repainted by anything -- it asserts a state nothing measured. It must
    either be wired, be demoted to the honest not-wired style, or be REGISTERED
    in DASHBOARD_PROVENANCE.json with a reason and a review date.
  * A chip WITH an id that no JavaScript ever writes to is orphaned -- it shows
    whatever the HTML says, forever. Always a defect, never registrable.
  * Registered static entries EXPIRE. A review date in the past is a failure,
    so "declared static" can never become a permanent hiding place.

Adding a new hand-painted panel now trips this red the same day. David never
has to be the one who remembers.

USAGE
    python3 scripts/dashboard_provenance.py            # full report
    python3 scripts/dashboard_provenance.py --check    # exit 1 on any defect
    python3 scripts/dashboard_provenance.py --json     # machine-readable
"""
import json
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
REGISTRY = os.path.join(REPO, "DASHBOARD_PROVENANCE.json")

PAGES = ["dashboard.server.html"]

# A chip in one of these classes paints a health verdict.
HEALTH_CLASSES = {"g": "green", "a": "amber", "r": "red"}
# ...and this one is the honest "not wired" style -- dashed, no verdict.
NOT_WIRED = "nw"

SPAN_OPEN_RE = re.compile(r'<span\b[^>]*>', re.IGNORECASE)
SPAN_ANY_RE = re.compile(r'<span\b[^>]*>|</span>', re.IGNORECASE)
CHIP_OPEN_RE = re.compile(r'<span class="om-chip (?P<cls>[a-z]+)"(?P<attrs>[^>]*)>')
ID_RE = re.compile(r'id="([^"]+)"')
TAG_RE = re.compile(r"<[^>]+>")


def _chip_spans(html):
    """Yield (cls, attrs, inner_html, line) for each om-chip, depth-aware.

    A chip nests <span class="om-dot"> and often <span class="om-v">, so a plain
    non-greedy regex either stops at the first </span> or swallows the next chip.
    Both failure modes silently under-report, which is precisely the disease this
    script exists to cure -- so the scanner counts depth instead of guessing.
    """
    for m in CHIP_OPEN_RE.finditer(html):
        depth = 1
        pos = m.end()
        while depth and pos < len(html):
            nxt = SPAN_ANY_RE.search(html, pos)
            if not nxt:
                break
            depth += 1 if nxt.group(0).lower().startswith("<span") else -1
            pos = nxt.end()
        inner = html[m.end():pos - len("</span>")] if depth == 0 else html[m.end():pos]
        yield (m.group("cls"), m.group("attrs"), inner,
               html.count("\n", 0, m.start()) + 1)


def _text(html_fragment):
    return " ".join(TAG_RE.sub(" ", html_fragment).split())


def load_registry():
    if not os.path.exists(REGISTRY):
        return {}
    with open(REGISTRY, encoding="utf-8") as fh:
        data = json.load(fh)
    return {e["slug"]: e for e in data.get("static_surfaces", [])}


def scan_page(page):
    """Return (chips, js) for a page. chips = list of dicts."""
    path = os.path.join(REPO, page)
    if not os.path.exists(path):
        return None, None
    with open(path, encoding="utf-8", errors="replace") as fh:
        html = fh.read()
    # Everything inside <script> is the feeding logic; everything outside is markup.
    js = "\n".join(re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL))

    # Chips built INSIDE <script> are the feeding logic, not painted markup. Blank
    # the script bodies but keep every byte offset so reported line numbers stay
    # true to the real file.
    markup = list(html)
    for sm in re.finditer(r"<script[^>]*>(.*?)</script>", html, re.DOTALL):
        for i in range(sm.start(1), sm.end(1)):
            if markup[i] != "\n":
                markup[i] = " "
    markup = "".join(markup)

    chips = []
    for cls, attrs, inner, line in _chip_spans(markup):
        cid = ID_RE.search(attrs)
        # A chip with no id of its own may still be fed: the renderer commonly
        # rewrites a whole container's innerHTML. Walk back to the nearest
        # enclosing element carrying an id and treat that as the chip's feed.
        container = None
        if not cid:
            before = markup.rfind("<div", 0, markup.find(inner) if inner else 0)
            head = markup.rfind('<div class="om-chips"', 0, line)
            seg = markup[:sum(len(l) + 1 for l in markup.split("\n")[:line])]
            open_div = seg.rfind("<div")
            if open_div != -1:
                tag_end = seg.find(">", open_div)
                mid = ID_RE.search(seg[open_div:tag_end + 1]) if tag_end != -1 else None
                if mid:
                    container = mid.group(1)
        chips.append({
            "page": page,
            "line": line,
            "cls": cls,
            "id": cid.group(1) if cid else None,
            "container": container,
            "text": _text(inner)[:80],
        })
    return chips, js


def audit():
    reg = load_registry()
    problems = []      # (severity, slug, message)
    stats = {"total": 0, "fed": 0, "not_wired": 0, "registered": 0, "unfed": 0, "orphan": 0}
    seen_slugs = set()

    for page in PAGES:
        chips, js = scan_page(page)
        if chips is None:
            continue
        for c in chips:
            stats["total"] += 1
            slug = "%s#%s" % (page, c["id"] or re.sub(r"[^a-z0-9]+", "-", c["text"].lower())[:40])
            seen_slugs.add(slug)

            if c["cls"] == NOT_WIRED:
                stats["not_wired"] += 1
                continue
            if c["cls"] not in HEALTH_CLASSES:
                continue

            if c["id"]:
                # It claims a feed -- prove the JS actually writes to it.
                if re.search(r"['\"]%s['\"]" % re.escape(c["id"]), js):
                    stats["fed"] += 1
                else:
                    stats["orphan"] += 1
                    problems.append(("FAIL", slug,
                        "line %d: chip id='%s' paints %s but NO script writes to it -- it "
                        "shows '%s' forever" % (c["line"], c["id"],
                                                HEALTH_CLASSES[c["cls"]], c["text"])))
                continue

            # Fed through its container's innerHTML?
            if c.get("container") and re.search(r"['\"]%s['\"]" % re.escape(c["container"]), js):
                stats["fed"] += 1
                continue

            # No id, no fed container: nothing can ever repaint it.
            if slug in reg:
                stats["registered"] += 1
                e = reg[slug]
                rb = e.get("review_by", "")
                if rb and rb < date.today().isoformat():
                    problems.append(("FAIL", slug,
                        "line %d: registered static surface '%s' passed its review date "
                        "%s -- re-verify it or wire it" % (c["line"], c["text"], rb)))
            else:
                stats["unfed"] += 1
                problems.append(("FAIL", slug,
                    "line %d: %s chip '%s' asserts a state nothing measured and is not "
                    "registered -- wire it, demote it to the not-wired style, or register "
                    "it with a reason and a review date"
                    % (c["line"], HEALTH_CLASSES[c["cls"]], c["text"])))

    # Registry hygiene: an entry for a surface that no longer exists is dead weight.
    for slug, e in reg.items():
        if slug not in seen_slugs:
            problems.append(("WARN", slug,
                "registered static surface '%s' is no longer in the page -- drop the "
                "registry entry" % e.get("asserts", slug)))

    return stats, problems


def main(argv):
    stats, problems = audit()
    fails = [p for p in problems if p[0] == "FAIL"]

    if "--json" in argv:
        print(json.dumps({"stats": stats,
                          "problems": [{"severity": s, "slug": g, "message": m}
                                       for s, g, m in problems]}, indent=2))
        return 1 if fails else 0

    print("DASHBOARD PROVENANCE (PROVENANCE-1)")
    print("  %d chip(s) total: %d live-fed, %d honestly not-wired, %d registered static"
          % (stats["total"], stats["fed"], stats["not_wired"], stats["registered"]))
    print("  DEFECTS: %d unfed health chip(s), %d orphaned id(s)"
          % (stats["unfed"], stats["orphan"]))
    if problems:
        print()
        for sev, slug, msg in problems:
            print("  [%s] %s" % (sev, msg))
    if not fails:
        print("\n  OK -- every health colour on the page is fed, honestly dashed, or "
              "registered with a live review date.")
    return 1 if (fails and "--check" in argv) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
