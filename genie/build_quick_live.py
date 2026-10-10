#!/usr/bin/env python3
"""build_quick_live.py -- QL-LIVE-1 (David, 10 Oct 2026: "with our latest changes to the Quick app we should update ...
the comics and emails").

The comic (genie/EMAIL_TO_TWO_USERS.html -> /orchestrator/quick_comic.html) and the email strip
(genie/email_strip/*_strip.html, PREVIEW.html, ORCH_PREVIEW.html -> /orchestrator/quick_emails.html) were built on
14 Sep from the HARNESS mock-up: eight categories with Housekeeping as its own door, harness phones instead of the app.
Quick now has seven doors (Housekeeping is Services' Home & care, RUL-159) and a Sport & fitness door inside Tutors
(RUL-217). Both visuals are now drawn from the walked How guides (stories/<type>.json): the same steps, words, payer
chips and REAL screens the help pages show (served publicly from /help/img/), one story per door plus Sport & fitness.
Re-run after a guide changes:   python3 genie/build_quick_live.py
"""
import html as H, io, json, os, re

ROOT = os.environ.get("MS_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ST = os.path.join(ROOT, "stories")
GEN = os.path.join(ROOT, "genie")
OUT = os.path.join(GEN, "email_strip")
IMG = "https://trustsquare.co/help/img"

# key, door name, the walked guide, colour (Quick's own door colour)
DOORS = [
 ("services",    "Services · Home & care", "home_cleaner",               "#B4441F"),
 ("property",    "Property",               "property_house",             "#2E86E0"),
 ("cars",        "Cars",                   "cars_bakkie",                "#5B4BD6"),
 ("tutors",      "Tutors",                 "tutors_maths",               "#4FA83F"),
 ("trainers",    "Sport & fitness",        "soccer_coach",               "#4FA83F"),
 ("collectors",  "Collectors",             "collectors_coins",           "#C98A2E"),
 ("adventures",  "Adventures",             "adventures_guest_house",     "#12A5A5"),
 ("localmarket", "Local Market",           "localmarket_food_preserves", "#D8447E"),
]
# Sport & fitness: every step whose screen is the coach's own (Quick r_*, TrustSquare t_*, and the shared generic ones).
TRAINER_OK = ("r_", "t_", "f5_01_door", "f5_10_terms", "f5_13_buzz_link", "f5_14_join", "f5_15_buzz_sent", "f2_16")

# ---- the three email panels: (step image, alt text, caption); a None image = a screen captured for the email itself
EMAIL = {
 "services": dict(heading="Five taps, and you have an advert", cta="Put me on the board", href="https://trustsquare.co/q/services",
   p=[("home_cleaner/h2_03_roles", "Screen one: 'Which one are you?' with a photo for each kind of work: home cleaner, housekeeper, nanny, caregiver, cook, chef, gardener, pool cleaner.",
       "Tap your kind of work, the areas you work in, your days and your day rate."),
      ("home_cleaner/q_email_draft", "Screen two: your listing before it is saved: 'Home cleaner, Menlyn, Pretoria East', your days and your rate, with an example photo you can swap for your own.",
       "You see your own advert before anything is saved or published."),
      ("home_cleaner/h_29_detail", "Screen three: your advert as a new customer sees it: Home cleaner, R350 per day, Monday to Friday, your trust score, and a button to ask for an introduction.",
       "A new customer asks to be introduced. Your name and number stay private until you accept.")]),
 "property": dict(heading="Six taps, and buyers can find your house", cta="List my place", href="https://trustsquare.co/q/property",
   p=[("property_house/f6_02_what", "Screen one: 'What are you listing?' with photo tiles: house, flat, townhouse, plot, farm, commercial.",
       "Tap what it is, to sell or to let, the bedrooms, the area and your asking price."),
      ("property_house/f6_07_draft", "Screen two: your listing before it is saved: 'House, to sell' in Centurion, 3 bedrooms, R2 450 000.",
       "You see the listing before anything is published."),
      ("property_house/f6_17_detail", "Screen three: your house as a buyer sees it in TrustSquare: a 3-bedroom family house in Centurion at R2 450 000, with a Request introduction button.",
       "A buyer asks to be introduced. One buyer at a time, and you decide.")]),
 "cars": dict(heading="Six taps, and the car is listed", cta="List my car", href="https://trustsquare.co/q/cars",
   p=[("cars_bakkie/f8_02_what", "Screen one: 'What are you selling?' with photo tiles: bakkie, sedan, SUV, hatchback, double cab, bike.",
       "Tap what it is, the make, roughly the year, your price and where it is."),
      ("cars_bakkie/f8_07_draft", "Screen two: your advert before it is saved: 'Bakkie, Toyota', 2015 to 2019, R219 000, Pretoria East.",
       "You see the advert before anything is published."),
      ("cars_bakkie/f8_23_detail", "Screen three: your bakkie as a buyer sees it: R219 000, mileage, gearbox and fuel, and the buyer's own Car Purchase Dossier.",
       "A buyer pays to be introduced. Answering him costs you nothing.")]),
 "tutors": dict(heading="Six taps, and parents can find you", cta="Offer tutoring", href="https://trustsquare.co/q/tutors",
   p=[("tutors_maths/f5_02_what", "Screen one: 'What do you teach?' with photo tiles: maths, science, English, accounting, Afrikaans, coding.",
       "Tap your subject, the level, online or in person, your rate and your areas."),
      ("tutors_maths/f5_07_draft", "Screen two: your listing before it is saved: 'Maths, High school', Menlyn and Pretoria East, R280 an hour.",
       "You see your listing before anything is published."),
      ("tutors_maths/f5_20_detail", "Screen three: your listing as a parent sees it: Maths, high school, R280 an hour, online and in person, with your trust score.",
       "A parent asks to be introduced. You accept or decline.")]),
 "trainers": dict(heading="Coach a sport? Five taps to your advert", cta="List me as a coach", href="https://trustsquare.co/q/tutors",
   p=[("soccer_coach/r_what", "Screen one: 'Which one do you coach?' with a real coaching photo for each sport: soccer, rugby, cricket, hockey, netball, basketball, volleyball, baseball.",
       "Tap Sport & fitness, your sport, your price per session and your areas."),
      ("soccer_coach/r_draft", "Screen two: your listing before it is saved: 'Soccer coach, Menlyn, Pretoria East', R250 a session.",
       "You see your advert before anything is saved. Coaching has no wage floor: your price, your call."),
      ("soccer_coach/r_results", "Screen three: what a parent finds when she looks for a soccer coach in her area.",
       "Someone who needs a coach finds you, and asks to be introduced.")]),
 "collectors": dict(heading="Seven taps, and collectors can see your piece", cta="Sell a piece", href="https://trustsquare.co/q/collectors",
   p=[("collectors_coins/f10_02_what", "Screen one: 'What are you selling?' with photo tiles: coins, stamps, cards, militaria, watches, art.",
       "Tap what it is, its condition, whether it is authenticated, your price and your area."),
      ("collectors_coins/f10_07b_item", "Screen two: your listing before it is saved: '2000 Krugerrand, 1 oz gold, Near mint', R72 900.",
       "Say exactly what it is, and see the advert before anything is published."),
      ("collectors_coins/f10_24_detail", "Screen three: your coin as a collector sees it: R72 900, your trust score, and a button to ask for an introduction.",
       "A collector asks to be introduced, and can check your price first.")]),
 "adventures": dict(heading="Six taps, and guests can find your place", cta="List my place to stay", href="https://trustsquare.co/q/adventures",
   p=[("adventures_guest_house/f12q_02_what", "Screen one: 'What are you offering?' with photo tiles: place to stay, game lodge, safari, guided tour, self-drive, rail journey, fishing.",
       "Tap what you offer, what kind of place, your price per room per night and where it is."),
      ("adventures_guest_house/f12q_07_draft", "Screen two: your listing before it is saved: 'Guest house, Wilderness', R950 a room a night.",
       "You see your listing before anything is published."),
      ("adventures_guest_house/f12q_17_detail", "Screen three: your guest house as a guest sees it: from R950 a night in Wilderness, your trust score, and a button to ask for an introduction.",
       "A guest asks to be introduced, and you answer her question.")]),
 "localmarket": dict(heading="Five taps, and the neighbours can buy", cta="Sell something", href="https://trustsquare.co/q/localmarket",
   p=[("localmarket_food_preserves/lm_02_what", "Screen one: 'What are you selling?' with photo tiles: food and preserves, crafts, furniture, plants, clothes, tools.",
       "Tap what you sell, your area, your price and how they get it."),
      ("localmarket_food_preserves/q_email_draft", "Screen two: your listing before it is saved: 'Food and preserves, Pretoria East', with 'Raw honey, 500 g jar' typed in as exactly what it is.",
       "Say exactly what it is, and see the advert before anything is published."),
      ("localmarket_food_preserves/lm_20_detail", "Screen three: your honey as a neighbour sees it, with your trust score and a Request introduction button that is free for buyers.",
       "A buyer asks for free. You pay 1T only when you accept your first buyer.")]),
}

def load(t):
    return json.load(io.open(os.path.join(ST, t + ".json"), encoding="utf-8"))

def btn(t):
    t = H.escape(t)
    return re.sub(r"\[\[(.+?)\]\]", r"<b>&ldquo;\1&rdquo;</b>", t)

# ======================================================================== the email strip
CELL = ('<td width="176" valign="top" style="width:176px;padding:0 6px;">'
        '<img src="{src}" width="176" alt="{alt}" style="width:100%;max-width:176px;display:block;border:0;outline:none;'
        'text-decoration:none;border-radius:10px;">'
        '<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation" style="margin-top:9px;"><tr>'
        '<td valign="top" width="24" style="width:24px;padding:1px 8px 0 0;">'
        '<table cellpadding="0" cellspacing="0" border="0" role="presentation"><tr>'
        '<td align="center" bgcolor="{c}" width="20" height="20" style="width:20px;height:20px;border-radius:50%;'
        'font-family:sans-serif;font-size:11px;font-weight:700;color:#ffffff;line-height:20px;text-align:center;'
        'mso-line-height-rule:exactly;">{n}</td></tr></table></td>'
        '<td valign="top" style="font-family:sans-serif;font-size:13px;color:#555555;line-height:1.45;">{cap}</td>'
        '</tr></table></td>')

def strip(key, name, colour):
    d = EMAIL[key]
    cells = "".join(CELL.format(src="%s/%s.jpg" % (IMG, p), alt=H.escape(a), c=colour, n=i + 1, cap=H.escape(c))
                    for i, (p, a, c) in enumerate(d["p"]))
    return ('<!-- TrustSquare Quick strip - %s (QL-LIVE-1, real Quick screens from the walked How guide). Three hosted\n'
            '     images; the alt text carries the whole message when images are blocked. -->\n'
            '<table width="100%%" cellpadding="0" cellspacing="0" border="0" role="presentation" style="margin:10px 0 22px;">\n'
            '  <tr><td style="font-family:sans-serif;font-size:17px;font-weight:700;color:#1a1a2e;padding:0 6px 12px;">%s</td></tr>\n'
            '  <tr><td><table width="100%%" cellpadding="0" cellspacing="0" border="0" role="presentation"><tr>%s</tr></table></td></tr>\n'
            '  <tr><td align="center" style="padding:20px 6px 0;"><table cellpadding="0" cellspacing="0" border="0" role="presentation"><tr>\n'
            '    <td align="center" bgcolor="%s" style="border-radius:999px;"><a href="%s" style="display:inline-block;padding:14px 30px;'
            'font-family:sans-serif;font-size:16px;font-weight:700;color:#ffffff;text-decoration:none;">%s</a></td>\n'
            '  </tr></table></td></tr>\n'
            '  <tr><td align="center" style="font-family:sans-serif;font-size:12px;color:#8a938f;padding:10px 6px 0;">'
            'Free to list. You see everything before it is published.</td></tr>\n'
            '</table>' % (H.escape(name), H.escape(d["heading"]), cells, colour, d["href"], H.escape(d["cta"])))

PAGE_CSS = """:root{--paper:#EDF0EC;--paper2:#fff;--ink:#0F1417;--ink2:#4E5A5E;--rule:#0F1417;--hair:#C9D1CA}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#0B0E10;--paper2:#141A1C;--ink:#E8EFEA;--ink2:#9BAAA2;--rule:#33414A;--hair:#232D31}}
:root[data-theme="dark"]{--paper:#0B0E10;--paper2:#141A1C;--ink:#E8EFEA;--ink2:#9BAAA2;--rule:#33414A;--hair:#232D31}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.55 "Archivo",Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:30px 16px 60px}h1{font-size:clamp(24px,5vw,38px);line-height:1.05;margin:0 0 10px;letter-spacing:-.02em}
.lede{max-width:70ch;color:var(--ink2);margin:0 0 6px}.note{border-left:4px solid #16A97C;background:rgba(22,169,124,.1);padding:10px 12px;margin:16px 0 0;font-size:13.5px;max-width:80ch}
"""

def emails():
    os.makedirs(OUT, exist_ok=True)
    rows = []
    for key, name, t, colour in DOORS:
        live = strip(key, name, colour)
        io.open(os.path.join(OUT, "%s_strip.html" % key), "w", encoding="utf-8", newline="\n").write(live)
        blind = re.sub(r'src="[^"]+"', 'src="data:,"', live)
        rows.append('<section class="cat"><h2><i style="background:%s"></i>%s</h2><div class="two">'
                    '<div class="col"><h3>As it arrives, images on</h3><div class="mail">%s</div></div>'
                    '<div class="col"><h3>Images blocked &mdash; what most first-time readers see</h3><div class="mail blind">%s</div></div>'
                    '</div><details><summary>The HTML to paste into the wave template</summary><pre>%s</pre></details></section>'
                    % (colour, H.escape(name), live, blind, H.escape(live)))
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Quick Email Strip</title><style>' + PAGE_CSS +
            'section.cat{border:3px solid var(--rule);background:var(--paper2);margin-top:26px;padding:16px}'
            'section.cat h2{display:flex;align-items:center;gap:10px;font-size:19px;margin:0 0 14px;text-transform:uppercase}'
            'section.cat h2 i{width:16px;height:16px;border:2px solid var(--rule);display:block}.two{display:flex;flex-wrap:wrap;gap:18px}'
            '.col{flex:1 1 320px;min-width:0}.col h3{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);margin:0 0 8px}'
            '.mail{background:#fff;border:1px solid var(--hair);padding:16px;max-width:600px;color:#222;overflow-x:auto}'
            '.mail.blind img{border:1px dashed #bbb;background:#f4f4f4;min-height:60px}details{margin-top:14px}'
            'summary{cursor:pointer;font-size:13px;font-weight:600;color:var(--ink2)}pre{overflow-x:auto;background:var(--paper);border:1px solid var(--hair);'
            'padding:12px;font-size:11px;line-height:1.45;white-space:pre-wrap;word-break:break-word;margin-top:10px}</style></head><body><div class="wrap">'
            '<h1>The three panels that go in an email</h1>'
            '<p class="lede">The comic is the whole story; this is the part an email can carry: three hosted images, a numbered line under each, '
            'one button. Tables and inline styles only, because Outlook renders with Word and Gmail clips a body over about 102&nbsp;KB.</p>'
            '<p class="lede">Updated 10 Oct 2026: every panel is now a real Quick or TrustSquare screen from the walked How guide for that door '
            '(Housekeeping is Services&rsquo; Home &amp; care; Sport &amp; fitness is new inside Tutors). The images are served from '
            '<code>/help/img/</code>, so a strip is ready to send the day its wave is dated.</p>'
            '<div class="note"><b>Not sent yet, deliberately.</b> An email is built into a wave only when the wave has a date. '
            'The right-hand column is the one that matters: most first-time readers have images off, so the alt text carries the message.</div>'
            + "".join(rows) + "</div></body></html>")
    for fn in ("PREVIEW.html", "ORCH_PREVIEW.html"):
        io.open(os.path.join(OUT, fn), "w", encoding="utf-8", newline="\n").write(page)

# ======================================================================== the comic
WHO = {"you": ("You", "#22C55E"), "customer": ("New customer", "#E0B04A"), "regular": ("Her regular", "#3BC2D9"),
       "worked": ("Someone she worked for", "#A78BFA")}
COST = {"free": "Free"}
ACTS = ["I", "II", "III", "IV", "V", "VI", "VII"]

def costlabel(c):
    if not c or c == "free": return ("Free", "free")
    m = re.match(r"(\d+)T(?:_(\w+))?", c)
    if m:
        what = {"report": " report", "check": " price check", "accept": " on accepting"}.get(m.group(2) or "", "")
        return ("%sT%s" % (m.group(1), what), "paid")
    return (c, "paid")

def comic():
    tabs, secs = [], []
    for i, (key, name, t, colour) in enumerate(DOORS):
        d = load(t); ppl = d.get("people") or {}
        chap = {c["id"]: c.get("en", c["id"]) for c in d.get("chapters", [])}
        steps = d["steps"]
        if key == "trainers":
            steps = [s for s in steps if s["img"].startswith(TRAINER_OK)]
        tabs.append('<button class="tab%s" data-k="%s" style="--c:%s"><i></i>%s</button>' % (" on" if i == 0 else "", key, colour, H.escape(name)))
        body, cur, n_act, panels = [], None, 0, []
        def flush():
            if panels: body.append('<div class="grid">%s</div>' % "".join(panels))
        for s in steps:
            if s["ch"] != cur:
                flush(); panels = []
                cur = s["ch"]; n_act += 1
                body.append('<div class="act" style="--c:%s"><span>Act %s</span><h3>%s</h3></div>' % (colour, ACTS[min(n_act, 7) - 1], H.escape(chap.get(cur, cur))))
            who, wc = WHO.get(s.get("who"), (s.get("who", ""), "#888"))
            person = ppl.get(s.get("who"), "")
            cl, ck = costlabel(s.get("cost"))
            en = s.get("en") or ["", ""]
            panels.append(
                '<figure class="panel" style="--w:%s"><figcaption><b class="n">%d</b><span class="who">%s%s</span><span class="cost %s">%s</span></figcaption>'
                '<h4>%s</h4><p>%s</p><div class="phone"><img loading="lazy" src="%s/%s/%s.jpg" alt="%s"></div></figure>'
                % (wc, s["n"], H.escape(who), (" &middot; " + H.escape(person)) if person else "", ck, H.escape(cl),
                   btn(en[0]), btn(en[1] if len(en) > 1 else ""), IMG, t, s["img"], H.escape(re.sub(r"\[\[|\]\]", "", en[0]))))
        flush()
        note = ""
        if key == "trainers":
            note = ('<p class="tnote">Sport &amp; fitness sits inside Tutors (RUL-217): every screen here is the coach&rsquo;s own, '
                    'in Quick and in TrustSquare.</p>')
        mail = ('<div class="act" style="--c:%s"><span>Act 0</span><h3>The email that brings her</h3></div>'
                '<div class="mailwrap"><div class="mail">%s</div></div>' % (colour, strip(key, name, colour)))
        secs.append('<section class="story%s" id="s-%s" style="--c:%s"><header><h2><i></i>%s</h2><p>%s &middot; walked %s &middot; '
                    '<a href="https://trustsquare.co/help/%s" target="_blank" rel="noopener">open the How guide</a></p></header>%s%s%s</section>'
                    % (" on" if i == 0 else "", key, colour, H.escape(name), H.escape(d.get("title", {}).get("en", "")),
                       H.escape(d.get("walked_on", "")), t, note, mail, "".join(body)))
    css = PAGE_CSS + """
.tabs{display:flex;flex-wrap:wrap;gap:8px;margin:18px 0 6px}.tab{display:flex;align-items:center;gap:8px;border:2px solid var(--rule);background:var(--paper2);
 color:var(--ink);font:600 13px Archivo,sans-serif;padding:7px 12px;cursor:pointer}.tab i{width:12px;height:12px;background:var(--c);display:block}
.tab.on{background:var(--ink);color:var(--paper)}.legend{display:flex;flex-wrap:wrap;gap:14px;font-size:12.5px;color:var(--ink2);margin:10px 0 0}
.legend span{display:inline-flex;align-items:center;gap:6px}.legend i{width:12px;height:12px;border-radius:3px;display:block}
.story{display:none;margin-top:22px}.story.on{display:block}.story header{border:3px solid var(--rule);background:var(--paper2);padding:14px 16px;border-left:12px solid var(--c)}
.story h2{margin:0;font-size:22px;text-transform:uppercase;letter-spacing:.01em}.story header p{margin:4px 0 0;color:var(--ink2);font-size:13.5px}
.story header a{color:var(--ink)}.tnote{border-left:4px solid var(--c);background:var(--paper2);padding:8px 12px;font-size:13.5px;margin:14px 0 0}
.act{display:flex;align-items:baseline;gap:12px;border:2px solid var(--rule);border-left:8px solid var(--c);background:var(--paper2);padding:10px 14px;margin:24px 0 12px}
.act span{font:700 11px "IBM Plex Mono",monospace;letter-spacing:.16em;text-transform:uppercase;color:var(--ink2)}.act h3{margin:0;font-size:19px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:14px}
.panel{margin:0;border:2px solid var(--rule);background:var(--paper2);padding:10px;display:flex;flex-direction:column}
.panel figcaption{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-bottom:6px}.panel .n{background:var(--ink);color:var(--paper);font-size:12px;
 min-width:22px;height:22px;display:inline-flex;align-items:center;justify-content:center}
.who{font-size:11.5px;font-weight:700;border-left:5px solid var(--w);padding-left:6px}.cost{margin-left:auto;font:600 10.5px "IBM Plex Mono",monospace;
 text-transform:uppercase;letter-spacing:.06em;padding:2px 6px;border:1.5px solid var(--hair);color:var(--ink2)}.cost.paid{border-color:#E0B04A;color:#E0B04A}
.panel h4{margin:2px 0 4px;font-size:14.5px;line-height:1.3}.panel p{margin:0 0 8px;font-size:12.5px;color:var(--ink2);line-height:1.45}
.phone{margin-top:auto;border:6px solid #11161a;border-radius:22px;overflow:hidden;background:#11161a}.phone img{display:block;width:100%;height:auto}
.mailwrap{overflow-x:auto}.mail{background:#fff;color:#222;border:1px solid var(--hair);padding:16px;max-width:620px}
@media(max-width:520px){.grid{grid-template-columns:1fr 1fr}.panel p{display:none}}
"""
    leg = "".join('<span><i style="background:%s"></i>%s</span>' % (c, H.escape(w)) for w, c in WHO.values())
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>One Email, Two Users</title><style>' + css + '</style></head><body><div class="wrap">'
            '<p class="lede" style="font:700 11px \'IBM Plex Mono\',monospace;letter-spacing:.16em;text-transform:uppercase">TrustSquare &middot; Quick Listing &rarr; the app &middot; seven doors + Sport &amp; fitness</p>'
            '<h1>One email, two users</h1>'
            '<p class="lede">The whole loop on the phone, panel by panel: the email lands, the taps make an advert, TrustSquare publishes it, '
            'a second person finds it and is introduced. Updated 10 Oct 2026: every panel is now the real screen from the walked How guide '
            'for that door, with the guide&rsquo;s own words and who pays at each step &mdash; so the comic changes when the app does.</p>'
            '<div class="tabs">' + "".join(tabs) + '</div><div class="legend">' + leg +
            '<span><i style="background:#E0B04A;border-radius:0"></i>gold price tag = a step someone pays for</span></div>'
            + "".join(secs) +
            '</div><script>document.querySelectorAll(".tab").forEach(function(b){b.onclick=function(){'
            'document.querySelectorAll(".tab,.story").forEach(function(x){x.classList.remove("on")});b.classList.add("on");'
            'document.getElementById("s-"+b.dataset.k).classList.add("on");window.scrollTo(0,0);};});</script></body></html>')
    io.open(os.path.join(GEN, "EMAIL_TO_TWO_USERS.html"), "w", encoding="utf-8", newline="\n").write(page)
    io.open(os.path.join(GEN, "comic_body.html"), "w", encoding="utf-8", newline="\n").write(page)

if __name__ == "__main__":
    emails(); comic()
    print("comic + %d email strips written from the walked How guides" % len(DOORS))
