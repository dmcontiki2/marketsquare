#!/usr/bin/env python3
"""QL-BOARD-10OCT (David, 10 Oct 2026: "with our latest changes to the Quick app we should update the Flowboard in Ops
Dashboard"). Brings genie/QUICK_LISTING_ORCH.html (/orchestrator/quick_listing.html) from 25 Sep up to 10 Oct:
the SERVICES lane redrawn from roles/role_registry.json (Casuals + Technical only -- the Trainers live in Tutors and get
their own section), the five taps' rate step and the lane words the 26 Sep - 10 Oct rulings changed (RUL-191..218), a new
'Sport & fitness door' section with all 47 sports in their 8 groups, and the ruled / built / next panel.
Re-runnable: every block is replaced, never appended twice."""
import io, os, re, json, math, collections, html
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(R, "genie", "QUICK_LISTING_ORCH.html")
s = io.open(P, encoding="utf-8").read()
reg = json.load(io.open(os.path.join(R, "roles", "role_registry.json"), encoding="utf-8"))
E = lambda t: html.escape(t, quote=False)
NEW = {"pool_cleaner", "window_cleaner", "pet_sitter_dog_walker", "carpet_washer", "au_pair", "tree_cutter",
       "garden_waste_removal", "griller_braai", "hotel_porter", "lodge_staff", "caterer", "bodyguard"}
SHORT = {"Pet sitter / dog walker": "Pets / dog walker", "Plant operator (TLB / excavator)": "Plant operator",
 "Code 10 / Code 14 driver": "Code 10/14 driver", "Taxi / shuttle driver": "Taxi / shuttle",
 "Air-con & refrigeration technician": "Air-con & fridge", "Borehole & pump technician": "Borehole & pump",
 "CCTV / alarm installer": "CCTV / alarm", "Gate & garage-door technician": "Gates & garage",
 "Garden waste removal": "Garden waste", "Builder's assistant": "Builder's asst.", "Seamstress / tailor": "Seamstress/tailor",
 "Solar PV installer": "Solar PV", "Trades-adjacent & informal": "Beauty, sewing & more"}

# ---- 1. SERVICES lane: Casuals + Technical only ------------------------------------------------------------
g = collections.OrderedDict()
for x in reg["roles"]:
    if x["status"] == "in" and x.get("service_class") != "Trainers": g.setdefault(x["group"], []).append(x)
n_live = sum(len(v) for v in g.values()); n_new = sum(1 for v in g.values() for x in v if x["key"] in NEW)
out = ['<g id="svc-roster">']
y = 86; W, GAP, H, STEP = 91, 5, 18, 22
for grp, xs in g.items():
    out.append('<text x="36" y="%d" class="gt" text-anchor="start" >%s · %d</text>' % (y + 9, E(SHORT.get(grp, grp)).upper(), len(xs)))
    y += 14
    for i, x in enumerate(xs):
        cx = 36 + (i % 4) * (W + GAP); cy = y + (i // 4) * STEP
        cls = "chip chip-new" if x["key"] in NEW else "chip chip-live"
        lab = x["label"]["en"]
        out.append('<rect x="%d" y="%d" width="%d" height="%d" rx="10" class="%s"><title>%s</title></rect>' % (cx, cy, W, H, cls, E(lab)))
        out.append('<text x="%.1f" y="%d" class="ct ct-s" text-anchor="middle" >%s</text>' % (cx + W / 2, cy + 13, E(SHORT.get(lab, lab))))
    y += math.ceil(len(xs) / 4) * STEP + 4
y += 4
out.append('<rect x="36" y="%d" width="14" height="10" rx="5" class="chip chip-live" /><text x="56" y="%d" class="bs" text-anchor="start" >live before 25 Sep (%d)</text>' % (y, y + 9, n_live - n_new))
out.append('<rect x="206" y="%d" width="14" height="10" rx="5" class="chip chip-new" /><text x="226" y="%d" class="bs" text-anchor="start" >added 25 Sep, RUL-172 (%d)</text>' % (y, y + 9, n_new))
out.append('<text x="36" y="%d" class="note" text-anchor="start" >Every role: its own picture, words, price way, AI example (RUL-216) and How guide.</text>' % (y + 30))
out.append('<text x="36" y="%d" class="note" text-anchor="start" >The 47 sports live in Tutors: see the Sport &amp; fitness door below.</text>' % (y + 45))
out.append('</g><!--/svc-roster-->')
assert y + 45 < 858, "roster overruns the HER EMPLOYERS box (y=%d)" % (y + 45)
s = re.sub(r'<g id="svc-roster">.*?</g><!--/svc-roster-->', "", s, flags=re.S)
a = '<text x="36" y="70" class="sub" text-anchor="start" >'
i = s.index(a); j = s.index("</text>", i) + 7
s = s[:i] + a + "one category · %d roles in %d groups</text>" % (n_live, len(g)) + "".join(out) + s[j:]

# ---- 2. words the rulings since 25 Sep changed ----------------------------------------------------------------
def sub(o, n):
    global s
    for oo in (">%s<" % E(o), ">%s<" % o):
        if oo in s:
            s = s.replace(oo, ">%s<" % E(n), 1); return
SWAPS = [("typed, never", "hour, visit, job,"), ("below floor", "car or session"),
 ("a typed rate under the floor is refused,", "only time has a floor: a visit, job,"),
 ("kindly, with the floor shown", "car or session never does (RUL-197)"),
 ("listed now · strangers see her once", "listed now · strangers see her once a"),
 ("a customer or employer confirms", "customer, employer or co-worker vouches"),
 ("43 live cities · her currency,", "follows where she is; opens where"),
 ("her country's trips and names", "she lists (RUL-211, 213, 215)"),
 ("her own photos come after it", "her own photo from the draft itself"),
 ("Local-first presenter", "Local-first Find"),
 ("in her suburb → around her city →", "every answer honoured (RUL-200) · real"),
 ("further out, in that order", "adverts → close matches → AI examples"),
 ("one link she sends to the people", "her Buzz link to the regulars"),
 ("who already hire her", "she already works for (RUL-191)"),
 ("SMS is not on the plans", "our SMS is outreach-only (RUL-192)"),
 ("magic-link auth", "in and out without a code (RUL-210)"),
 ("push is free and now works; email is the backup.", "push is free; email is the anchor and the backup."),
 ("SMS is not on the plans.", "Our SMS reaches prospects only, never app users.")]
for o, n in SWAPS: sub(o, n)
for o, n in (("adverts, then close matches, then AI examples", "adverts → close matches → AI examples"),
             ("customer, employer or co-worker says yes", "customer, employer or co-worker vouches")): sub(o, n)
s = re.sub(r'opened 12 Sep 2026 · updated [^<]*</div>', 'opened 12 Sep 2026 · updated 10 Oct 2026</div>', s, count=1)

# ---- 3. Sport & fitness door section ---------------------------------------------------------------------------
tg = collections.OrderedDict()
for x in reg["roles"]:
    if x["status"] == "in" and x.get("service_class") == "Trainers": tg.setdefault(x["group"], []).append(x)
nt = sum(len(v) for v in tg.values()); ncl = sum(1 for v in tg.values() for x in v if (x.get("gate") or {}).get("type") == "police_clearance")
grp_html = "".join('<div class="tg"><h4>%s · %d</h4><div class="tchips">%s</div></div>' % (E(k), len(v), "".join(
    '<span class="tc%s" title="%s">%s</span>' % (" tc-cl" if (x.get("gate") or {}).get("type") == "police_clearance" else "",
     "police clearance before strangers see it" if (x.get("gate") or {}).get("type") == "police_clearance" else "listed publicly at once",
     E(x["label"]["en"])) for x in v)) for k, v in tg.items())
TRN = '''<section id="trainers"><!--QL-TRAINERS-->
  <p class="sec-eyebrow">Visual 1b · the door inside Tutors (RUL-217, 218)</p>
  <h2>Sport &amp; fitness — %d sports in %d groups</h2>
  <p class="lede">Built the way Casuals were built inside Services: one <b>Sport &amp; fitness</b> tile on the Tutors door opens her sport group, then her sport (its real coaching photo, nobody recognisable), then her price per session, per month or per package — coaching is not time, so there is no wage floor — then her areas. Four taps after the door to a draft, global from day one, in every Quick language. The advert goes to TrustSquare as Tutors · Trainers, and each sport has its own AI example in Find and its own How guide with its own screens.</p>
  <div class="tpath"><span>Tutors door</span><i>→</i><span>Sport &amp; fitness</span><i>→</i><span>sport group</span><i>→</i><span>her sport</span><i>→</i><span>per session · month · package</span><i>→</i><span>her areas</span><i>→</i><span class="tp-end">draft</span></div>
  <div class="tgrid">%s</div>
  <p class="tleg"><span class="tc">listed publicly at once (%d)</span> <span class="tc tc-cl">police clearance first — sports that commonly coach children (%d)</span></p>
</section><!--/QL-TRAINERS-->
''' % (nt, len(tg), grp_html, nt - ncl, ncl)
s = re.sub(r'<section id="trainers"><!--QL-TRAINERS-->.*?</section><!--/QL-TRAINERS-->\n', "", s, flags=re.S)
s = s.replace('<section id="chain">', TRN + '\n<section id="chain">', 1)
CSS = ('/*QL-TRN-CSS*/.tpath{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:10px 0 16px;font:600 12.5px Barlow,sans-serif}'
 '.tpath span{border:1.5px solid var(--brand);border-radius:999px;padding:4px 11px;color:var(--ink)}.tpath i{color:var(--ink2);font-style:normal}'
 '.tpath .tp-end{background:var(--brand);color:#0b0d10}'
 '.tgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px}'
 '.tg{border:1px solid var(--line);border-radius:12px;padding:10px 12px;background:var(--bg2)}'
 '.tg h4{margin:0 0 8px;font:600 11.5px "IBM Plex Mono",ui-monospace,monospace;letter-spacing:.1em;text-transform:uppercase;color:var(--brand)}'
 '.tchips{display:flex;flex-wrap:wrap;gap:5px}.tc{display:inline-block;font:500 12px Barlow,sans-serif;border:1.4px solid var(--brand);'
 'background:rgba(34,197,94,.10);border-radius:999px;padding:2px 9px;color:var(--ink)}.tc-cl{border-color:var(--gold);background:rgba(224,176,74,.20)}'
 '.tleg{margin:10px 0 0;font-size:12.5px;color:var(--ink2)}.tleg .tc{margin-right:10px}/*/QL-TRN-CSS*/\n')
s = re.sub(r'/\*QL-TRN-CSS\*/.*?/\*/QL-TRN-CSS\*/\n', "", s, flags=re.S)
s = s.replace("</style>", CSS + "</style>", 1)

# ---- 4. the lede and the status panel -------------------------------------------------------------------------
s = re.sub(r'A housekeeper — or any of the \d+ service roles',
           'A housekeeper — or any of the %d service roles' % n_live, s, count=1)
STATUS = '''<div class="status">
  <div class="st ruled"><h3>Ruled</h3><ul>
    <li><b>Five taps, no talking;</b> only time has a wage floor — a visit, job, car or session never does (RUL-159, 197).</li>
    <li><b>Trainers are a door inside Tutors,</b> global from day one, each sport on a real coaching photo (RUL-217, 218).</li>
    <li><b>Every casual role has a local AI example,</b> made on the server; real adverts always come first (RUL-194, 216).</li>
    <li><b>Find honours every answer;</b> one missed answer shows as a close match, never hidden (RUL-200, 207).</li>
    <li><b>The app speaks the languages of the country she is in</b> and opens where she lists (RUL-204, 205, 211, 215).</li>
    <li><b>A customer, employer or co-worker's yes</b> unlocks a worker; a plain driving licence is shown, not a gate (RUL-198, 209).</li>
    <li><b>Our SMS is outreach-only;</b> after the first sign-up she goes in and out without a code (RUL-192, 210).</li>
  </ul></div>
  <div class="st built"><h3>Built · 10 Oct</h3><ul>
    <li><b>%d service roles in %d groups + %d sports in %d groups,</b> each with its own picture, price way and AI example.</li>
    <li><b>How in the top bar</b> opens the guide for her own role at her own step — every role and sport now shows its own screens.</li>
    <li><b>Car washer</b> per car and per kind of clean, next to the cleaners (RUL-214).</li>
    <li><b>Her own photo</b> straight from the draft card; the example photo is marked EXAMPLE.</li>
    <li><b>Buzz link</b> for her regulars; Pass Quick on to someone; Quick updates itself when idle.</li>
    <li><b>16 languages,</b> only the ones her country speaks offered (LANG-COUNTRY-1).</li>
  </ul></div>
  <div class="st next"><h3>Next</h3><ul>
    <li><b>L16:</b> landing in TrustSquare from Quick is still slow on weak 3G — skip the home imagery on that landing.</li>
    <li><b>L17:</b> Android shell for Quick — waits on the D-U-N-S number for the Play account.</li>
    <li><b>Language reviewer</b> pass on the trainer words in isiZulu, isiXhosa and Sepedi (English stands in until then).</li>
  </ul></div>
</div>''' % (n_live, len(g), nt, len(tg))
s = re.sub(r'<div class="status">.*?\n</div>\n', STATUS + "\n", s, count=1, flags=re.S)
io.open(P, "w", encoding="utf-8", newline="\n").write(s)
print("board updated to 10 Oct: %d service roles / %d groups, %d sports / %d groups; roster ends y=%d" % (n_live, len(g), nt, len(tg), y + 45))
