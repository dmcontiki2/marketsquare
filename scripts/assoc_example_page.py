#!/usr/bin/env python3
"""
assoc_example_page.py -- generate a worked-example page for a membership body.

SPORTS-CLUBS-1 / ASSOC-EXAMPLE-1 (4 Sep 2026). David built one of these by hand for
SABIO (bee removals) and observed that the same page exists for every association:
chess tutors, judo clubs, dance teachers, plumbers, guides. So it is a generator, not
fifty hand-made pages.

The page is the thing a secretary is sent a LINK to. The cold email stays short --
a volunteer will not read a brochure -- and the link carries the detail.

HONESTY RULE, inherited from David's SABIO page and non-negotiable here: every
credential is labelled LIVE (already a scored signal in bea_main._TRUST_SIGNALS /
_CATEGORY_SIGNALS) or PROPOSED (would need adding, points are an opening suggestion).
A page that blurs the two is a page that promises a badge we cannot issue.

  python assoc_example_page.py --specs specs.json --out ./pages
  python assoc_example_page.py --specs specs.json --only chess
"""
from __future__ import annotations
import argparse, html, json, os, sys

BASE = 40   # every seller starts here (Established) -- AGENT_BRIEFING.md

# THE CANONICAL FORMULA. Mirrors bea_main._trust_math(), which its own docstring calls
# "THE ONLY PLACE THIS FORMULA MAY LIVE". It is duplicated here for ONE reason: a page
# that draws a Trust Score ladder must draw the score the product will actually show.
#   score = min(100, 40 + min(30,universal) + min(30,track) + min(40,category))
# The group caps are the whole point (TRUST-GENEROUS-1, David 4 Sep 2026): category
# credentials can carry a seller from 40 to 80 and NO FURTHER. The last 20 points come
# only from verified identity and completed introductions -- things no certificate buys.
# That is why rating a task-specific credential generously is SAFE: it lets an
# experienced person reach the category ceiling with fewer documents, and it can never
# let a faker past 80.
UNIVERSAL_CAP, TRACK_CAP, CATEGORY_CAP = 30, 30, 40


def trust_math(universal: int, track: int, category: int) -> int:
    return min(100, BASE + min(UNIVERSAL_CAP, universal)
               + min(TRACK_CAP, track) + min(CATEGORY_CAP, category))


def band(score: int) -> tuple[str, str]:
    if score >= 90: return "Highly Trusted", "#1c7c4a"
    if score >= 70: return "Trusted", "#2a6fb5"
    if score >= 40: return "Established", "#7a6a2a"
    return "New", "#8a8a8a"


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def card(c: str) -> str:
    b, col = band(int(c["score"]))
    badges = "".join(
        f'<span class="bdg">{esc(x)}</span>' for x in c["badges"])
    return f"""
      <div class="card">
        <div class="card-top">
          <div class="card-title">{esc(c['title'])}</div>
          <div class="score" style="background:{col}">★ {int(c['score'])}</div>
        </div>
        <div class="card-meta">{esc(c['meta'])}</div>
        <div class="badges">{badges}</div>
        <div class="card-foot"><b>{esc(c['price'])}</b><span class="intro">Request introduction · 1T</span></div>
      </div>"""


def ladder(live, proposed) -> str:
    """Draw the ladder the PRODUCT would draw -- group caps and all.

    Signals are split into universal (identity/profile, cap 30) and category
    credentials (cap 40) by name, because that is how bea_main groups them."""
    UNIVERSAL_NAMES = ("id verified", "government-issued id", "complete profile", "referral")

    def is_universal(name):
        n = name.lower()
        return any(u in n for u in UNIVERSAL_NAMES)

    rows = []
    uni = cat = 0
    rows.append(f'<tr><td>Everyone starts here</td><td class="c">—</td>'
                f'<td class="c"><b>{BASE}</b></td><td class="c tag-live">base</td></tr>')
    for name, pts, tag in ([(n, p, "live") for n, p in live] +
                           [(n, p, "prop") for n, p in proposed]):
        if is_universal(name):
            uni += pts
        else:
            cat += pts
        running = trust_math(uni, 0, cat)
        label = "LIVE" if tag == "live" else "PROPOSED"
        rows.append(f'<tr><td>{esc(name)}</td><td class="c">+{pts}</td>'
                    f'<td class="c"><b>{running}</b></td>'
                    f'<td class="c tag-{tag}">{label}</td></tr>')

    final = trust_math(uni, 0, cat)
    fb, col = band(final)
    over = ""
    if cat > CATEGORY_CAP:
        over = (f' Their certificates are worth {cat} points on paper; the category group '
                f'caps at {CATEGORY_CAP}, so the surplus is headroom rather than score — '
                f'which is exactly why holding more of them is never wasted effort, and '
                f'why a generous rating costs the ranking nothing.')
    return f"""
      <table class="ladder">
        <tr><th>Signal</th><th>Points</th><th>Running</th><th>Status</th></tr>
        {''.join(rows)}
      </table>
      <p class="note">A member holding all of the above sits at
      <b style="color:{col}">{final} — {fb}</b>, before they have taken a single job.{over}
      The remaining points to 100 come only from a verified identity and a real track
      record on the platform — completed introductions, none ignored. No certificate buys
      those, which is why somebody who merely <i>claims</i> the work cannot reach the top.</p>"""


PAGE = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{trade} on TrustSquare — for {assoc}</title>
<style>
 body{{font-family:'Segoe UI',system-ui,-apple-system,sans-serif;background:#f4f6f9;color:#12263f;margin:0;padding:26px}}
 .wrap{{max-width:960px;margin:0 auto}}
 h1{{color:#123a6b;font-size:27px;margin:0 0 6px}}
 .sub{{color:#5b6b80;font-size:14px;margin-bottom:8px}}
 .hook{{font-size:17px;color:#2a3f5a;line-height:1.55;margin:14px 0 22px;border-left:4px solid #2a6fb5;padding-left:14px}}
 .card-box{{background:#fff;border-radius:10px;padding:20px 24px;margin-bottom:18px;box-shadow:0 1px 4px rgba(18,38,63,.10)}}
 h2{{color:#123a6b;font-size:17px;margin:0 0 14px;border-bottom:2px solid #e3e8ef;padding-bottom:8px}}
 .steps{{display:flex;gap:12px;flex-wrap:wrap}}
 .step{{flex:1;min-width:186px;background:#f8fafc;border-left:4px solid #2a6fb5;border-radius:0 7px 7px 0;padding:13px 15px}}
 .step b{{display:block;color:#123a6b;font-size:14px;margin-bottom:5px}}
 .step span{{font-size:13px;color:#41556e;line-height:1.5}}
 .step .who{{display:block;margin-top:7px;font-size:11px;color:#7d8ea3;text-transform:uppercase;letter-spacing:.4px}}
 .phone{{max-width:390px;margin:0 auto;background:#eef1f5;border-radius:14px;padding:14px}}
 .search{{background:#fff;border-radius:8px;padding:9px 13px;font-size:13px;color:#5b6b80;margin-bottom:11px}}
 .card{{background:#fff;border-radius:9px;padding:13px 15px;margin-bottom:10px}}
 .card-top{{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}}
 .card-title{{font-weight:600;font-size:14px;color:#12263f;line-height:1.35}}
 .score{{color:#fff;font-size:12px;font-weight:700;padding:3px 8px;border-radius:11px;white-space:nowrap}}
 .card-meta{{font-size:12px;color:#7d8ea3;margin:5px 0 8px}}
 .badges{{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:9px}}
 .bdg{{background:#eaf0fa;color:#2a4a75;font-size:11px;padding:3px 7px;border-radius:4px}}
 .card-foot{{display:flex;justify-content:space-between;align-items:center;font-size:13px;color:#12263f;border-top:1px solid #eef1f5;padding-top:8px}}
 .intro{{font-size:11px;color:#7d8ea3}}
 table.ladder{{border-collapse:collapse;width:100%;font-size:13.5px;margin-top:4px}}
 .ladder th{{background:#123a6b;color:#fff;text-align:left;padding:8px 11px}}
 .ladder td{{padding:7px 11px;border-bottom:1px solid #e6eaf0}}
 .ladder td.c{{text-align:center}}
 .tag-live{{color:#1c7c4a;font-weight:700;font-size:11px}}
 .tag-prop{{color:#b8860b;font-weight:700;font-size:11px}}
 .two{{display:flex;gap:18px;flex-wrap:wrap}}
 .two>div{{flex:1;min-width:250px}}
 ul{{margin:6px 0 0 18px;padding:0}} li{{font-size:13.5px;color:#3a4d63;line-height:1.6;margin-bottom:6px}}
 .yes li::marker{{color:#1c7c4a}} .no li::marker{{color:#c0392b}}
 .win{{margin-bottom:14px}} .win b{{color:#123a6b;display:block;font-size:14px;margin-bottom:3px}}
 .win span{{font-size:13.5px;color:#41556e;line-height:1.6}}
 .note{{font-size:13px;color:#5b6b80;line-height:1.6;margin-top:11px}}
 .honest{{background:#fff8ec;border-left:4px solid #c55a11;border-radius:0 7px 7px 0;padding:14px 16px;font-size:13.5px;color:#5a4a33;line-height:1.65}}
 .foot{{text-align:center;font-size:12px;color:#8a99ab;margin-top:20px;line-height:1.6}}
</style></head><body><div class="wrap">
<h1>{trade} on TrustSquare</h1>
<div class="sub">Prepared for {assoc} · {date}</div>
<div class="hook">{hook}</div>

<div class="card-box"><h2>How it would reach your members</h2>
<p class="note">Four steps, and {assoc} only does the first one. No lists change hands:
{assoc} sends us no member's details, and we never ask for them.</p>
<div class="steps">
 <div class="step"><b>1 · {assoc} passes the word</b><span>One note down the channels that already exist — the newsletter, the mailing list, the WhatsApp groups.</span><span class="who">{assoc} · one email</span></div>
 <div class="step"><b>2 · A {noun} lists themselves</b><span>Free. A few minutes on a phone. What they do, the areas they cover, what they charge, and a photo or two.</span><span class="who">The {noun} · 5 minutes</span></div>
 <div class="step"><b>3 · Certificates become badges</b><span>They upload what they hold. Each one is checked, and each one lifts the Trust Score the public sees.</span><span class="who">The {noun} · once a year</span></div>
 <div class="step"><b>4 · The public finds them</b><span>Somebody searching their suburb pays a small fee to ask for an introduction — and the {noun} decides whether to take it.</span><span class="who">Automatic</span></div>
</div></div>

<div class="card-box"><h2>What it looks like on a phone</h2>
<p class="note">Someone in {city} searches “{search}”. These are mock-ups with invented examples.
Notice what is <b>not</b> on the cards: no business name, no address, no phone number.
The certificates are visible; the person is not.</p>
<div class="phone"><div class="search">🔍 {search}</div>{cards}</div>
<p class="note">Ranked by trust and by how complete the advert is — never by who paid.</p></div>

<div class="card-box"><h2>What the certificates are actually worth</h2>
{ladder}</div>

<div class="card-box"><h2>What the public sees, and what is never published</h2>
<div class="two">
 <div><b style="color:#1c7c4a">✓ Shown</b><ul class="yes">
  <li>What the {noun} does, and the areas they work in — suburb or town, never a street address</li>
  <li>Their Trust Score and the badges they have earned</li>
  <li>A price guide and photos of the work</li></ul></div>
 <div><b style="color:#c0392b">✕ Never published</b><ul class="no">
  <li>Their name and their business name</li>
  <li>Their phone number and email address</li>
  <li>Their home or yard address</li></ul></div>
</div>
<p class="note">These are exchanged at one moment only: when somebody asks for an introduction
and the {noun} accepts it. Then the two of them deal with each other directly.
TrustSquare takes nothing from the job itself.</p></div>

<div class="card-box"><h2>What is in it for {assoc}</h2>{wins}</div>

<div class="card-box"><h2>Being straight about what is live and what is not</h2>
<div class="honest">{honest}</div>
<p class="note">{trade} is not a category of its own. It sits under <b>{app_category}</b>,
the same place a {noun} sits alongside every other {app_category_l} listing.</p></div>

<div class="foot">TrustSquare · trustsquare.co · prepared for {assoc}, {date}<br>
Listings shown are mock-ups with invented examples. No real member or business appears on this page.<br>
Nothing has been sent to anybody. This is a proposal for {assoc} to look at first.</div>
</div></body></html>"""


def build(spec: dict, date: str) -> str:
    live, prop = spec["live"], spec["proposed"]
    if prop:
        honest = (f"<b>Live today:</b> free listings, the Trust Score and its bands, "
                  f"ID verification, and " + ", ".join(esc(n).lower() for n, _ in live[1:]) +
                  " as scored signals — plus the anonymity and the paid introduction.<br><br>"
                  f"<b>Not built yet:</b> " + ", ".join(esc(n) for n, _ in prop) +
                  " are <b>not</b> on our credential list. They are marked PROPOSED above, and the "
                  "points shown are our opening suggestion, not a decision. What they should be "
                  f"worth is exactly where {esc(spec['assoc'])}'s view would carry more weight than ours.")
    else:
        honest = ("<b>Everything above is live today.</b> Every credential in the table is already "
                  "a scored signal on TrustSquare — nothing has to be built, and nothing waits on us. "
                  "A member could list tonight and rank correctly in the morning.")
    if spec.get("extra"):
        honest += "<br><br>" + esc(spec["extra"])
    wins = "".join(f'<div class="win"><b>{esc(t)}</b><span>{esc(b)}</span></div>'
                   for t, b in spec["assoc_wins"])
    return PAGE.format(
        trade=esc(spec["trade"]), assoc=esc(spec["assoc"]), date=date,
        hook=esc(spec["hook"]), noun=esc(spec["noun"]), city=esc(spec["city"]),
        search=esc(spec["search"]), app_category=esc(spec["app_category"]),
        app_category_l=esc(spec["app_category"]).lower(),
        cards="".join(card(c) for c in spec["cards"]),
        ladder=ladder(live, prop), wins=wins, honest=honest)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", required=True)
    ap.add_argument("--out", default="./assoc_pages")
    ap.add_argument("--only")
    a = ap.parse_args()
    specs = json.load(open(a.specs, encoding="utf-8"))
    os.makedirs(a.out, exist_ok=True)
    date = "4 September 2026"
    n = 0
    for key, spec in specs.items():
        if a.only and key != a.only:
            continue
        p = os.path.join(a.out, f"assoc_{key}.html")
        open(p, "w", encoding="utf-8", newline="").write(build(spec, date))
        live_n, prop_n = len(spec["live"]), len(spec["proposed"])
        flag = "ALL LIVE" if not prop_n else f"{prop_n} proposed"
        print(f"  {key:11} -> {os.path.basename(p):26} {live_n} live signals, {flag}")
        n += 1
    print(f"\n  {n} page(s) written to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
