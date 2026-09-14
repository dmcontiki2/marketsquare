#!/usr/bin/env python3
"""Build the three-panel strip that goes IN an email, per category.

Constraints this respects, because email is not a browser:
  * tables and inline styles only - no flex, no grid, no <style> blocks
  * hosted images, never data URIs - Gmail clips a body over ~102 KB
  * every image carries alt text that says the whole thing on its own,
    because images are blocked by default for most first-time recipients
  * 600px wrapper, three 176px cells - the same shape agency_outreach.html
    already uses for its phone cards
"""
import html as H
import os

BASE = 'https://trustsquare.co/static/qstrip'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'email_strip')

CATS = [
 ('homehelp', 'Housekeeping', '#16A97C'),
 ('property', 'Property', '#2E86E0'),
 ('cars', 'Cars', '#5B4BD6'),
 ('tutors', 'Tutors', '#4FA83F'),
 ('services', 'Services', '#B4441F'),
 ('collectors', 'Collectors', '#C98A2E'),
 ('adventures', 'Adventures', '#12A5A5'),
 ('localmarket', 'Local Market', '#D8447E'),
]

S = {
 'homehelp': dict(
   cta='Put me on the board',
   heading='Four taps, and you have an advert',
   c1='Tap what you do, where you work, which days you are open and what you charge.',
   c2='You see your own advert, with your own score on it, before anything is published.',
   c3='Someone who needs you asks for an introduction - they pay, you accept or decline.',
   a1='Screen one: the question "What work do you do?" with six photo tiles - cleaning, laundry and '
      'ironing, cooking, childminding, office cleaning, garden help.',
   a2='Screen two: the finished advert - "Cleaning, Menlyn", the days open, R350 a day - marked draft, '
      'with a listing score of 60 out of 100.',
   a3='Screen three: your public card as a client sees it - what you do, the days you are free, '
      'your day rate and your trust star, with an Ask to be introduced button that costs them, not you.'),
 'property': dict(
   cta='Show the agencies',
   heading='Four taps, and the agencies can see it',
   c1='Tap what it is, to sell or to let, how many bedrooms and which suburb.',
   c2='You see the card, with its own score, before anything is published.',
   c3='An agency asks for the lead and pays for it. One agency at a time, and it ends on your word.',
   a1='Screen one: the question "What are you listing?" with photo tiles - house, flat, townhouse, '
      'plot, farm, commercial.',
   a2='Screen two: the finished card - "House, to let" in your suburb - marked draft, with its listing '
      'score and what would lift it.',
   a3='Screen three: an agency asking to be introduced to you, with Accept and Not now. The agency '
      'pays; you never do.'),
 'cars': dict(
   cta='List my car',
   heading='Four taps, and the car is listed',
   c1='Tap what it is, the make, roughly the year and what you are asking.',
   c2='You see the advert, with its own score, before anything is published.',
   c3='A buyer pays to be introduced to you. Answering him costs you nothing, and it ends when it sells.',
   a1='Screen one: the question "What are you selling?" with photo tiles - bakkie, sedan, SUV, '
      'hatchback, double cab, bike.',
   a2='Screen two: the finished advert - "Bakkie, Ford" with the year and the asking price - marked '
      'draft, with its listing score.',
   a3='Screen three: a buyer asking to be introduced, with Accept and Not now. He pays one Tuppence; '
      'you pay nothing.'),
 'tutors': dict(
   cta='Offer tutoring',
   heading='Four taps, and parents can find you',
   c1='Tap what you teach, which level, online or in person, and your hourly rate.',
   c2='You see your card, with your own score, before anything is published.',
   c3='A parent pays once to be introduced. Every lesson after that is between the two of you.',
   a1='Screen one: the question "What do you teach?" with photo tiles - maths, science, English, '
      'accounting, Afrikaans, coding.',
   a2='Screen two: the finished card - "Maths, matric" with the hourly rate - marked draft, with its '
      'listing score and what would lift it.',
   a3='Screen three: a parent asking to be introduced, with Accept and Not now. SACE registration and '
      'clearances lift your trust score on every listing.'),
 'services': dict(
   cta='Put my trade up',
   heading='Four taps, and your trade is on the board',
   c1='Tap your trade, where you work, how you charge and what the call-out is.',
   c2='You see your card, with your own score, before anything is published.',
   c3='A stranger pays to be introduced to you; you accept or decline every one.',
   a1='Screen one: the question "What is your trade?" with photo tiles - electrician, plumber, '
      'gardener, painter, handyman, pool care.',
   a2='Screen two: the finished card - "Electrician, Menlyn" with the call-out fee - marked draft, '
      'with its listing score.',
   a3='Screen three: your public card as a customer sees it - your trade, your area, your call-out '
      'fee and your trust star, with an Ask to be introduced button that costs them, not you.'),
 'collectors': dict(
   cta='Ask the board',
   heading='One question, five answers, or a straight no',
   c1='Tap what you are hunting, what you can spend and how rare it must be.',
   c2='Five near you, ordered by trust, and nothing else. No paging, no sorting, no map.',
   c3='Nothing listed is worth knowing too - the next person who lists one is told you asked.',
   a1='Screen one: the question "What are you hunting?" with photo tiles - coins, stamps, cards, '
      'militaria, watches, art.',
   a2='Screen two: five results near you, each with an asking price and a trust star, and nothing else.',
   a3='Screen three: the seller being asked for an introduction, with Accept and Not now. Paid once, '
      'then the two of you trade for years.'),
 'adventures': dict(
   cta='List the trip',
   heading='Four taps, and the trip is on the shelf',
   c1='Tap what you offer, how long it runs, the price a night and the best season.',
   c2='You see the card, with its own score, before anything is published.',
   c3='A traveller pays one introduction and talks to every place they asked. Three quotes is the point.',
   a1='Screen one: the question "What are you offering?" with photo tiles - game lodge, safari, guided '
      'tour, self-drive, rail journey, fishing.',
   a2='Screen two: the finished card - "Game lodge, a week" with the nightly rate - marked draft, with '
      'its listing score.',
   a3='Screen three: a traveller asking to be introduced, with Accept and Not now. They pay once and '
      'may ask several places at the same time.'),
 'localmarket': dict(
   cta='Sell something',
   heading='Four taps, and your neighbours can see it',
   c1='Tap what it is, where you are, what it costs and how they get it.',
   c2='You see the card, with its own score, before anything is published.',
   c3='At these amounts an introduction rarely applies. This is your street, not a marketplace fee.',
   a1='Screen one: the question "What are you selling?" with photo tiles - food and preserves, crafts, '
      'furniture, plants, clothes, tools.',
   a2='Screen two: the finished card - "Food and preserves" with the price and how it is collected - '
      'marked draft, with its listing score.',
   a3='Screen three: a neighbour two streets over, connected to you at no cost, with one line each way.'),
}

CELL = ('<td width="176" valign="top" style="width:176px;padding:0 6px;">'
        '<img src="{src}" width="176" alt="{alt}" '
        'style="width:100%;max-width:176px;display:block;border:0;outline:none;text-decoration:none;'
        'border-radius:10px;">'
        '<table width="100%" cellpadding="0" cellspacing="0" border="0" role="presentation" '
        'style="margin-top:9px;"><tr>'
        '<td valign="top" width="24" style="width:24px;padding:1px 8px 0 0;">'
        '<table cellpadding="0" cellspacing="0" border="0" role="presentation"><tr>'
        '<td align="center" bgcolor="{c}" width="20" height="20" style="width:20px;height:20px;'
        'border-radius:50%;font-family:sans-serif;font-size:11px;font-weight:700;color:#ffffff;'
        'line-height:20px;text-align:center;mso-line-height-rule:exactly;">{n}</td>'
        '</tr></table></td>'
        '<td valign="top" style="font-family:sans-serif;font-size:13px;color:#555555;line-height:1.45;">'
        '{cap}</td></tr></table></td>')


def block(key, name, colour, base=BASE, heading_tag='h3'):
    d = S[key]
    cells = ''.join(CELL.format(src='%s/%s_%s.jpg' % (base, key, part), alt=H.escape(d[alt]),
                                c=colour, n=i + 1, cap=H.escape(d[cap]))
                    for i, (part, alt, cap) in enumerate(
                        [('taps', 'a1', 'c1'), ('advert', 'a2', 'c2'), ('other', 'a3', 'c3')]))
    return (
      '<!-- TrustSquare Quick Listing strip - %s. Three hosted images, alt text carries the whole\n'
      '     message when images are blocked. Drop between the intro copy and the CTA. -->\n'
      '<table width="100%%" cellpadding="0" cellspacing="0" border="0" role="presentation" '
      'style="margin:10px 0 22px;">\n'
      '  <tr><td style="font-family:sans-serif;font-size:17px;font-weight:700;color:#1a1a2e;'
      'padding:0 6px 12px;">%s</td></tr>\n'
      '  <tr><td>\n'
      '    <table width="100%%" cellpadding="0" cellspacing="0" border="0" role="presentation">\n'
      '      <tr>%s</tr>\n'
      '    </table>\n'
      '  </td></tr>\n'
      '  <tr><td align="center" style="padding:20px 6px 0;">\n'
      '    <table cellpadding="0" cellspacing="0" border="0" role="presentation"><tr>\n'
      '      <td align="center" bgcolor="%s" style="border-radius:999px;">\n'
      '        <a href="https://trustsquare.co/q/%s" style="display:inline-block;padding:14px 30px;'
      'font-family:sans-serif;font-size:16px;font-weight:700;color:#ffffff;text-decoration:none;">%s</a>\n'
      '      </td>\n'
      '    </tr></table>\n'
      '  </td></tr>\n'
      '  <tr><td align="center" style="font-family:sans-serif;font-size:12px;color:#8a938f;'
      'padding:10px 6px 0;">No CV, no interview, no fee. You see everything before it is published.</td></tr>\n'
      '</table>' % (name, H.escape(d['heading']), cells, colour, key, H.escape(d['cta'])))


# ---- paste-ready partials
for key, name, colour in CATS:
    open(os.path.join(OUT, '%s_strip.html' % key), 'w', encoding='utf-8').write(block(key, name, colour))

# ---- preview page (local image paths so it works straight off the disk)
def local(key, name, colour):
    return block(key, name, colour, base='.')

rows = []
for key, name, colour in CATS:
    live = local(key, name, colour)
    blind = live.replace('.jpg"', '_MISSING.jpg"')
    rows.append(
      '<section class="cat"><h2><i style="background:%s"></i>%s</h2>'
      '<div class="two">'
      '<div class="col"><h3>As it arrives, images on</h3><div class="mail">%s</div></div>'
      '<div class="col"><h3>Images blocked &mdash; what most first-time readers see</h3>'
      '<div class="mail blind">%s</div></div>'
      '</div>'
      '<details><summary>The HTML to paste into the wave template</summary><pre>%s</pre></details>'
      '</section>' % (colour, H.escape(name), live, blind, H.escape(live)))

page = ("""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quick Listing Email Strip</title>
<style>
:root{--paper:#EDF0EC;--paper2:#fff;--ink:#0F1417;--ink2:#4E5A5E;--rule:#0F1417;--hair:#C9D1CA}
@media(prefers-color-scheme:dark){:root:not([data-theme="light"]){--paper:#0B0E10;--paper2:#141A1C;
 --ink:#E8EFEA;--ink2:#9BAAA2;--rule:#33414A;--hair:#232D31}}
:root[data-theme="dark"]{--paper:#0B0E10;--paper2:#141A1C;--ink:#E8EFEA;--ink2:#9BAAA2;--rule:#33414A;--hair:#232D31}
*{box-sizing:border-box}
body{margin:0;background:var(--paper);color:var(--ink);
 font:15px/1.55 "Archivo",Helvetica,Arial,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:0 18px;padding-block:30px 60px}
h1{font-size:clamp(24px,5vw,38px);line-height:1.05;margin:0 0 10px;letter-spacing:-.02em}
.lede{max-width:66ch;color:var(--ink2);margin:0 0 6px}
.note{border-left:4px solid #16A97C;background:rgba(22,169,124,.1);padding:10px 12px;margin:16px 0 0;
 font-size:13.5px;max-width:78ch}
section.cat{border:3px solid var(--rule);background:var(--paper2);margin-top:26px;padding:16px}
section.cat h2{display:flex;align-items:center;gap:10px;font-size:19px;margin:0 0 14px;text-transform:uppercase;
 letter-spacing:.01em}
section.cat h2 i{width:16px;height:16px;border:2px solid var(--rule);display:block}
.two{display:flex;flex-wrap:wrap;gap:18px}
.col{flex:1 1 320px;min-width:0}
.col h3{font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--ink2);margin:0 0 8px}
.mail{background:#fff;border:1px solid var(--hair);padding:16px;max-width:600px;color:#222}
.mail.blind img{border:1px dashed #bbb;background:#f4f4f4;min-height:60px}
details{margin-top:14px}
summary{cursor:pointer;font-size:13px;font-weight:600;color:var(--ink2)}
pre{overflow-x:auto;background:var(--paper);border:1px solid var(--hair);padding:12px;font-size:11px;
 line-height:1.45;white-space:pre-wrap;word-break:break-word;margin-top:10px}
@media(max-width:720px){.col{flex:1 1 100%}}
</style></head><body>
<div class="wrap">
<h1>The three panels that go in an email</h1>
<p class="lede">The comic is the blueprint; this is the part an email can actually carry. Three hosted
  images, a numbered line under each, one button. Tables and inline styles only, because Outlook renders
  with Word and Gmail clips a body over about 102&nbsp;KB.</p>
<p class="lede">The right-hand column is the one that matters: most people meeting us for the first time
  have images off, so the alt text has to carry the whole message on its own.</p>
<div class="note"><b>Not sent yet, deliberately.</b> Waves 2 to 5 have no date, and the rule on disk is
  that an email is built when its wave has one. The images sit in
  <code>genie/email_strip/</code> ready to deploy to <code>/static/qstrip/</code> the day a wave is dated.</div>
~~ROWS~~
</div></body></html>""").replace("~~ROWS~~", ''.join(rows))

open(os.path.join(OUT, 'PREVIEW.html'), 'w', encoding='utf-8').write(page)
print('wrote 8 partials + PREVIEW.html')
