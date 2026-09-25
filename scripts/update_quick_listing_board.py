#!/usr/bin/env python3
"""QL-BOARD-25SEP (David 25 Sep 2026: "is the following visual still up to date? ... If not please update it").
Brings genie/QUICK_LISTING_ORCH.html (served as /orchestrator/quick_listing.html) up to 25 Sep: the status panel,
the lede, the five taps of the Services door (RUL-159), and the SERVICES lane redrawn from roles/role_registry.json --
every live role as a chip, colour-coded: live before 25 Sep, added 25 Sep (RUL-172). Re-runnable: the lane is always
redrawn from the registry, so the board cannot drift from what Quick carries."""
import io, os, re, json, math, collections, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "genie", "QUICK_LISTING_ORCH.html")
s = io.open(P, encoding="utf-8").read()
reg = json.load(io.open(os.path.join(R, "roles", "role_registry.json"), encoding="utf-8"))
NEW = {"pool_cleaner", "window_cleaner", "pet_sitter_dog_walker", "carpet_washer", "au_pair", "tree_cutter",
       "garden_waste_removal", "griller_braai", "hotel_porter", "lodge_staff", "caterer", "bodyguard"}
SHORT = {"Pet sitter / dog walker": "Pets / dog walker", "Plant operator (TLB / excavator)": "Plant operator",
 "Code 10 / Code 14 driver": "Code 10/14 driver", "Taxi / shuttle driver": "Taxi / shuttle",
 "Air-con & refrigeration technician": "Air-con & fridge", "Borehole & pump technician": "Borehole & pump",
 "CCTV / alarm installer": "CCTV / alarm", "Gate & garage-door technician": "Gates & garage",
 "Garden waste removal": "Garden waste", "Builder's assistant": "Builder's asst.", "Seamstress / tailor": "Seamstress/tailor",
 "Solar PV installer": "Solar PV", "Trades-adjacent & informal": "Beauty, sewing & more"}
E = lambda t: html.escape(t, quote=False)
g = collections.OrderedDict()
for x in reg["roles"]:
    if x["status"] == "in": g.setdefault(x["group"], []).append(x)
n_live = sum(len(v) for v in g.values()); n_new = sum(1 for v in g.values() for x in v if x["key"] in NEW)

# ---- 1. the SERVICES lane: drop the old chips and group headers, draw the registry --------------------------
s = re.sub(r'<rect x="[\d.]+" y="[\d.]+" width="126" height="24" rx="12" class="chip[^"]*" />', "", s)
s = re.sub(r'<text x="[\d.]+" y="[\d.]+" class="ct" text-anchor="middle" >[^<]*</text>', "", s)
s = re.sub(r'<text x="36" y="(\d+)" class="gt" text-anchor="start" >[^<]*</text>',
           lambda m: "" if 80 <= int(m.group(1)) <= 700 else m.group(0), s)
s = re.sub(r'<text x="36" y="6[68]\d" class="note" text-anchor="start" >[^<]*</text>', "", s)
s = re.sub(r'<g id="svc-roster">.*?</g><!--/svc-roster-->', "", s, flags=re.S)
out = ['<g id="svc-roster">']
y = 86; W, GAP, H, STEP = 91, 5, 18, 22
for grp, xs in g.items():
    out.append('<text x="36" y="%d" class="gt" text-anchor="start" >%s · %d</text>' % (y + 9, E(SHORT.get(grp, grp)).upper(), len(xs)))
    y += 14
    for i, x in enumerate(xs):
        col, row = i % 4, i // 4
        cx = 36 + col * (W + GAP); cy = y + row * STEP
        cls = "chip chip-new" if x["key"] in NEW else "chip chip-live"
        lab = x["label"]["en"]; short = SHORT.get(lab, lab)
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" class="%s"><title>%s</title></rect>' % (cx, cy, W, H, cls, E(lab)))
        out.append('<text x="%.1f" y="%d" class="ct ct-s" text-anchor="middle" >%s</text>' % (cx + W / 2, cy + 13, E(short)))
    y += math.ceil(len(xs) / 4) * STEP + 4
y += 4
out.append('<rect x="36" y="%d" width="14" height="10" rx="5" class="chip chip-live" /><text x="56" y="%d" class="bs" text-anchor="start" >live before 25 Sep (%d)</text>' % (y, y + 9, n_live - n_new))
out.append('<rect x="206" y="%d" width="14" height="10" rx="5" class="chip chip-new" /><text x="226" y="%d" class="bs" text-anchor="start" >added 25 Sep, RUL-172 (%d)</text>' % (y, y + 9, n_new))
out.append('<text x="36" y="%d" class="note" text-anchor="start" >Every role: five taps, one picture of the work (never a person), its own words</text>' % (y + 30))
out.append('<text x="36" y="%d" class="note" text-anchor="start" >and its own search match. House sitter + 15 more wait on the LATER register.</text>' % (y + 45))
out.append('</g><!--/svc-roster-->')
assert y + 45 < 858, "roster overruns the HER EMPLOYERS box (y=%d)" % (y + 45)
a = '<text x="36" y="70" class="sub" text-anchor="start" >'
i = s.index(a); j = s.index("</text>", i) + 7
s = s[:i] + a + "one category · %d roles in %d groups</text>" % (n_live, len(g)) + "".join(out) + s[j:]
css = (".chip-live{stroke:var(--brand);stroke-width:1.4;fill:rgba(34,197,94,.10)}"
       ".chip-new{stroke:var(--gold);stroke-width:2;fill:rgba(224,176,74,.20)}"
       ".ct-s{font:500 10px Barlow,sans-serif}")
if ".chip-new{" not in s: s = s.replace(".chip-home{", css + "\n.chip-home{", 1)

# ---- 2. the five taps of the Services door (RUL-159) --------------------------------------------------------
TAPS = [("Category", "the ring · photo", "changes every tap", "Kind of work", "11 groups", "with photos"),
        ("What you do", "housekeeper,", "gardener…", "Your role", "73 roles,", "own picture"),
        ("Where", "seeded from her", "location, no ask", "Where", "her area,", "tap or type"),
        ("Openings", "her weekly", "schedule", "Days", "a full week,", "any days"),
        ("Rate + photo", "AI photo ·", "wage floor", "Rate", "typed, never", "below floor")]
for o1, o2, o3, n1, n2, n3 in TAPS:
    for o, n, cl in ((o1, n1, "tt"), (o2, n2, "bs"), (o3, n3, "bs")):
        pat = 'class="%s" text-anchor="middle" >%s</text>' % (cl, E(o))
        if pat in s: s = s.replace(pat, 'class="%s" text-anchor="middle" >%s</text>' % (cl, E(n)), 1)

# ---- 3. stale words in the lanes ----------------------------------------------------------------------------
for o, n in (("AI photo pool per worker type ·", "one picture of the work per role ·"),
             ("a different photo on every tap", "her own photos come after it"),
             ("Place snapper", "Place & country"),
             ("148-suburb seed · typo-tolerant ·", "43 live cities · her currency,"),
             ("‘Moreleta Park’ now understood", "her country's trips and names"),
             ("a rate under the floor is refused,", "a typed rate under the floor is refused,"),
             ("one employer confirms or an ID lands", "a customer or employer confirms")):
    s = s.replace(">%s<" % E(o), ">%s<" % E(n), 1).replace(">%s<" % o, ">%s<" % n, 1)
s = s.replace("A housekeeper — any of the forty-odd worker types in the first lane — taps five times in the Quick Intro app",
              "A housekeeper — or any of the %d service roles, from dog walker to diesel mechanic — taps five times in the Quick Intro app" % n_live)
s = s.replace("&nbsp;·&nbsp; opened 12 Sep 2026</div>", "&nbsp;·&nbsp; opened 12 Sep 2026 · updated 25 Sep 2026</div>")

# ---- 4. the status panel ------------------------------------------------------------------------------------
STATUS = '''<div class="status">
  <div class="st ruled"><h3>Ruled</h3><ul>
    <li><b>Five taps, no talking.</b> Services door: kind of work → role → where → days → rate; trades ask qualification and call-out instead (RUL-159).</li>
    <li><b>Seven categories.</b> Housekeeping folded into Services as Home &amp; care (RUL-159).</li>
    <li><b>One picture of the work</b> per role, never a person; her own photos come after it (RUL-157).</li>
    <li><b>Listed at once, public once verified</b> for clearance and licence roles (RUL-153, 155, 156).</li>
    <li><b>The reference comes from whoever she works for</b> — an employer, a customer, a parent, a guest (RUL-169, 172).</li>
    <li><b>The one tap saves;</b> publishing happens in TrustSquare behind the EULA (RUL-166).</li>
    <li><b>Push first, email backup, no SMS;</b> Buzz is free for good (RUL-122, 135, 171).</li>
  </ul></div>
  <div class="st built"><h3>Built · 25 Sep</h3><ul>
    <li><b>%d service roles in %d groups</b>, each with its own work picture, taps, words in five languages and search match — dog walker included.</li>
    <li><b>A search returns only the role asked for:</b> Car guard never shows Security guards (SVC-FIND-1).</li>
    <li><b>Every kind wears its own picture</b> in every category; the draft marks it EXAMPLE PHOTO.</li>
    <li><b>Six languages</b> on the door (en, af, zu, xh, nso, st), carried into TrustSquare.</li>
    <li><b>Country packs:</b> 43 live cities, local currency bands, trips and names (RUL-170).</li>
    <li><b>The seam:</b> Back, Find, city and language carry into TrustSquare; Pass Quick on to someone.</li>
  </ul></div>
  <div class="st next"><h3>Next</h3><ul>
    <li><b>L16:</b> landing in TrustSquare from Quick takes 11.8 s on weak 3G — skip the home imagery on that landing.</li>
    <li><b>L17:</b> Android shell for Quick — waits on the D-U-N-S number for the Play account.</li>
    <li><b>Language reviewer</b> pass on the 25 Sep role words (RUL-160).</li>
  </ul></div>
</div>''' % (n_live, len(g))
s = re.sub(r'<div class="status">.*?\n</div>\n', STATUS + "\n", s, count=1, flags=re.S)
io.open(P, "w", encoding="utf-8").write(s)
print("board updated: %d roles, %d new; roster ends y=%d" % (n_live, n_new, y + 45))
