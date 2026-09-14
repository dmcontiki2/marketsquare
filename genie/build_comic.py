#!/usr/bin/env python3
"""Build the eight-category comic from the harness's own data tables.

One engine, eight stories. The taps, the advert, the scores and the buzz facts
are computed from CATS / COMMS / CRED exactly as HARNESS.html computes them, so
adding a category here is a data row, never a new page.
"""
import html as H
import json
import re

import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'HARNESS.html')
raw = open(SRC, encoding='utf-8', errors='replace').read()
PH = json.loads(re.search(r'var PH = (\{.*?\});', raw, re.S).group(1))
CATS = json.loads(re.search(r'var CATS = (\[.*?\]);\n', raw, re.S).group(1))

# ---------------------------------------------------------------- transcribed
# COMMS and CRED are JS object literals with concatenated strings, so they are
# transcribed verbatim rather than parsed. Source: HARNESS.html, 14 Sep build.
COMMS = {
 'homehelp': dict(ruled=True, a='Thandi Mokoena', b='Mrs Nkosi', bRole='your employer, Menlyn',
   met='You brought her — she joined from your own link.',
   pay='Free, always. You brought this connection, so there is nothing to sell.',
   many='One pair per job. As many pairs as you have employers.',
   sample='Running late, the taxi is stuck at Solomon Mahlangu',
   card='One tap on your phone buzzes your employer, with your name on it.'),
 'property': dict(ruled=True, a='Anna Pretorius', b='Bekker Properties',
   bRole='the agency holding your listing',
   met='They asked for your details and paid for the introduction.',
   pay='The AGENCY paid. You never pay to be found — you are the lead.',
   many='ONE agency at a time. Close it and the next one may take a turn.',
   sample='Can you come at 4? The gate code is 1180',
   card='One line to the agency holding your place — viewings, offers, show days.'),
 'cars': dict(ruled=False, a='Lerato Mokoena', b='Sipho Dlamini', bRole='the buyer who asked',
   met='He paid for the introduction to your car.',
   pay='He paid. Answering him costs you nothing.',
   many='Many buyers, one car — and it ENDS the day it sells.',
   sample='Still available? I can view at 5',
   card='One line to the people asking about your car — until it is sold.',
   note='This is the one category where closing is the normal ending, not a complaint. '
        'When the car is sold, close them all — that is the feature working, not failing.'),
 'tutors': dict(ruled=False, a='Nomsa Khumalo', b='Mr Ncube', bRole='your child’s tutor',
   met='The platform introduced you, and then it repeats every week.',
   pay='You paid the introduction. The weekly rhythm after it is free.',
   many='One pair per child, standing for a school term.',
   sample='Can we move to Thursday? She has exams',
   card='One line to the tutor — a moved lesson, an exam week, a late child.',
   note='A third person is in this one — the child. Nothing about her goes through a buzz; '
        'this is the two adults arranging their own diary.'),
 'services': dict(ruled=False, a='Hannes Roux', b='Piet Grobler', bRole='the plumber you called',
   met='Either — the platform found him, or he was already your man.',
   pay='A stranger cost a Tuppence. Your own regulars are free.',
   many='Many, and repeating. A tradesman carries dozens of standing customers.',
   sample='On my way, need to fetch a part first',
   card='One line to the trade you use — on my way, running late, job done.'),
 'collectors': dict(ruled=False, a='Johan de Wet', b='Marie Fourie', bRole='a collector you dealt with',
   met='One introduction, years ago. You have traded ever since.',
   pay='Paid once, at the first introduction. Everything after is yours.',
   many='Many, and long-lived — collectors keep the same people for decades.',
   sample='Got the 1947 penny. Swap for your duplicate?',
   card='One line to the collectors you trade with.'),
 'adventures': dict(ruled=False, a='Kagiso Sithole', b='Kruger Gate Lodge',
   bRole='one of the places you asked',
   met='You asked several places at once — they all answered.',
   pay='You paid one introduction. Talking to all of them is included.',
   many='MANY at once. Three quotes is the point — exclusivity would be absurd.',
   sample='We land at 6, is that too late to check in?',
   card='One line to every place you asked — dates, late arrivals, one more bed.'),
 'localmarket': dict(ruled=False, a='Grace Sibanda', b='Zanele Dube', bRole='two streets over',
   met='She lives around the corner. You probably already knew her.',
   pay='Usually nothing — at these amounts an introduction rarely applies.',
   many='Many, casual, short.',
   sample='At the gate, bring change if you can',
   card='One line to your neighbour — at the gate, sold out, bring change.'),
}
CRED = {
 'collectors': [('Third-party authentication certificate', 8), ('Item provenance documentation', 8),
                ('Collector association membership', 3)],
 'cars':       [('Vehicle ownership (NATIS)', 10), ('Roadworthy certificate', 6)],
 'tutors':     [('SACE registration', 12), ('Safety clearances (PCC + child protection)', 10)],
 'homehelp':   [('Police clearance / background check', 10), ('Any NQF qualification or short course', 8)],
 'services':   [('Police clearance / background check', 10), ('Formal trade certificate', 8)],
 'adventures': [('Activity-specific guide certificate', 12), ('Current first aid', 6)],
}
AREA_ASK = {'homehelp': 'Say which area you work in', 'services': 'Say which area you work in',
            'tutors': 'Say which area you teach in', 'property': 'Say which suburb it is in',
            'cars': 'Say where the car can be seen', 'collectors': 'Say where it can be collected',
            'adventures': 'Say where the trip starts', 'localmarket': 'Say where it can be collected'}
REQ = {'property': ['prop_type', 'beds', 'baths', 'listing_type'],
       'cars': ['make', 'model', 'vehicle_year', 'mileage_km', 'transmission'],
       'tutors': ['subject', 'level', 'mode'], 'services': ['service_type']}
FIELD_FROM = {'property': {'prop_type': 'what', 'listing_type': 'deal', 'beds': 'beds'},
              'cars': {'make': 'make', 'vehicle_year': 'year'},
              'tutors': {'subject': 'what', 'level': 'level', 'mode': 'mode'},
              'services': {'service_type': 'what'}}
NICE = {'prop_type': 'property type', 'listing_type': 'for sale or to rent', 'beds': 'number of bedrooms',
        'baths': 'number of bathrooms', 'make': 'make', 'model': 'model', 'vehicle_year': 'year',
        'mileage_km': 'mileage', 'transmission': 'transmission', 'subject': 'subject', 'level': 'level',
        'mode': 'in person or online', 'service_type': 'what you do'}
PRICE_NOTE = {'collectors': 'This is your asking price. TrustSquare can look up a verified market price '
              'for cards, coins and LEGO from free public sources, so you can see where yours sits — '
              'it never changes what you asked.'}
PRICE_ANY = 'This is your asking price — buyers see it as asked, not as a valuation.'

# ------------------------------------------------------------- authored per category
# The email is the only invented screen on the page: waves 2-5 have no date, and
# LAUNCH_EMAILS rule 3 says an email is built when its wave has one. These are the
# SHAPE, marked as such on every panel.
STORY = {
 'homehelp': dict(
   subject='Work near you. Four taps, no CV.',
   b1='If you clean, cook, iron, mind children or help in a garden, you can put yourself on the board '
      'in about a minute. No CV, no interview, no fee.',
   b2='Say what you do, where you work, which days you are open and what you charge. You see your own '
      'advert before anything is published.',
   cta='Put me on the board', path='q/homehelp',
   lister='the housekeeper', audience='casual and day workers',
   pairline='She sends her own link to the employer she already has.'),
 'property': dict(
   subject='Your place, in front of the agencies that work your street.',
   b1='Put your house or flat up in four taps. Agencies near you see it and ask for the lead — you do '
      'not pay to be found.',
   b2='One agency holds it at a time, and the window ends on your word.',
   cta='Show the agencies', path='q/property',
   lister='the private seller', audience='private sellers',
   pairline='The agency asks for the lead and pays for it.'),
 'cars': dict(
   subject='Selling the bakkie? Four taps and it is listed.',
   b1='Make, year, price and where it can be seen. That is the whole advert, and you see it before it '
      'goes anywhere.',
   b2='Buyers pay to be introduced to you. Answering them costs you nothing.',
   cta='List my car', path='q/cars',
   lister='the car seller', audience='private car sellers',
   pairline='A buyer pays for the introduction to the car.'),
 'tutors': dict(
   subject='Tutoring this term? Put your subjects on the board.',
   b1='Subject, level, online or in person, and your hourly rate. Parents near you see it ordered by '
      'trust, not by who paid.',
   b2='SACE registration and clearances lift your trust score on every listing you ever make.',
   cta='Offer tutoring', path='q/tutors',
   lister='the tutor', audience='tutors and teachers',
   pairline='A parent pays once for the introduction; the weekly rhythm after it is free.'),
 'services': dict(
   subject='Your trade, on the board in four taps.',
   b1='Electrician, plumber, gardener, painter, handyman or pool care — say what you do, where you '
      'work and what you charge.',
   b2='Your own regulars stay free. Strangers pay to be introduced to you.',
   cta='Put my trade up', path='q/services',
   lister='the tradesman', audience='trades and pros',
   pairline='Either — the platform found him, or he was already your man.'),
 'collectors': dict(
   subject='Is it there? Ask in one question.',
   b1='Coins, stamps, cards, militaria, watches or art. Ask and you get five answers near you, or a '
      'straight no.',
   b2='A straight no is worth something too — the next person who lists one is told you asked.',
   cta='Ask the board', path='q/collectors',
   lister='the collector', audience='collectors and dealers',
   pairline='One introduction, years ago, and they have traded ever since.'),
 'adventures': dict(
   subject='Your lodge, in front of people already planning the trip.',
   b1='What you offer, how long, what it costs a night and the best season. Four taps and the card is '
      'written for you.',
   b2='Travellers ask several places at once — three quotes is the point.',
   cta='List the trip', path='q/adventures',
   lister='the operator', audience='lodges, guides and operators',
   pairline='A traveller pays one introduction and talks to all of them.'),
 'localmarket': dict(
   subject='Selling at the gate this weekend?',
   b1='Honey, plants, crafts, furniture or tools. Say what it is, where you are and what it costs.',
   b2='At these amounts an introduction rarely applies — this is your street, not a marketplace fee.',
   cta='Sell something', path='q/localmarket',
   lister='the neighbour', audience='home producers and neighbours',
   pairline='She lives around the corner. You probably already knew her.'),
}
# Which lane the free pair is opened BY. worker = the lister brings the other party
# in on her own link (the ruled free lane); platform = TrustSquare made the match.
BROUGHT = {'homehelp': 'worker', 'services': 'worker', 'property': 'platform', 'cars': 'platform',
           'tutors': 'platform', 'collectors': 'platform', 'adventures': 'platform',
           'localmarket': 'platform'}

# ------------------------------------------------------------------ scoring, as the app scores
def pick_for(step):
    """One plausible answer per step: the first tile, the middle chip, three days."""
    tiles = step['tiles']
    if step['kind'] == 'week':
        days = ['Mon', 'Wed', 'Fri']
        return dict(label=', '.join(days), photo=None, key=step['key'], taps=len(days) + 1)
    if step['kind'] == 'chip':
        t = tiles[min(2, len(tiles) - 1)]
        return dict(label=t['t'], photo=None, key=step['key'], taps=1)
    t = tiles[0] if step['key'] != 'where' else tiles[3]
    return dict(label=t['t'], photo=t.get('p'), key=step['key'], taps=1)

def story_of(cat):
    k = cat['key']
    name_key = cat['name'].lower()
    steps = cat['sell']['steps']
    picks = [pick_for(s) for s in steps]
    by = {p['key']: p for p in picks}
    taps = sum(p['taps'] for p in picks)
    title = picks[0]['label'] + ' — ' + picks[1]['label']
    body = ('Written from your %d taps. ' % len(picks)
            + ', '.join(p['label'] for p in picks)
            + '. Change any word of it before it goes up.')
    req = REQ.get(name_key, [])
    frm = FIELD_FROM.get(name_key, {})
    score, missing = 0, [dict(pts=40, t='Add your own photos')]
    per = 50.0 / (len(req) + 1)
    for f in req:
        if frm.get(f) and by.get(frm[f]):
            score += per
        else:
            missing.append(dict(pts=per, t='Add the ' + NICE.get(f, f)))
    if len(body.split()) >= 15:
        score += per
    else:
        missing.append(dict(pts=per, t='Write 15 words or more'))
    if by.get('price'):
        score += 6
    else:
        missing.append(dict(pts=6, t='Put a price on it — asking for a quote scores nothing'))
    if by.get('where'):
        score += 4
    else:
        missing.append(dict(pts=4, t=AREA_ASK[k]))
    missing.sort(key=lambda m: -m['pts'])
    ls = int(round(score))
    headroom = int(round(sum(m['pts'] for m in missing)))
    hero = None
    for p in reversed(picks):
        if p['photo']:
            hero = p['photo']
            break
    return dict(picks=picks, by=by, taps=taps, title=title, body=body, ls=ls,
                headroom=headroom, missing=missing, fields=len(req),
                hero=hero or cat['hero'][0], rs=round(0.5 * ls, 1))

def e(s):
    return H.escape(str(s), quote=False)

def img(key, cls='', alt=''):
    return '<img %ssrc="@@%s@@" alt="%s">' % (('class="%s" ' % cls) if cls else '', key, alt)

# --------------------------------------------------------------------- panels
def panel(stream, num, caption, phone, pip, pipcls, note):
    return ('<article class="panel p-%s"><div class="cap"><span class="num">%s</span><p>%s</p></div>'
            '<div class="stagebox">%s</div>'
            '<div class="foot"><span class="pip %s">%s</span><em>%s</em></div></article>'
            % (stream, num, caption, phone, pipcls, pip, note))

def bar(steps_html='', lock=None):
    mid = ('<span class="lockup"><span class="m">TS</span><span class="t">%s</span></span>' % lock
           ) if lock else ('<span class="steps">%s</span>' % steps_html)
    return '<div class="bar"><span class="ic">&#8249;</span>%s<span class="ic">&#8962;</span></div>' % mid

def dots(n, cur):
    return ''.join('<i class="%s"></i>' % ('done' if i < cur else ('on' if i == cur else ''))
                   for i in range(n))

def trail_of(picks, upto):
    out = []
    for p in picks[:upto]:
        out.append(img(p['photo'], alt=p['label']) if p['photo'] else '<span>%s</span>' % e(p['label']))
    return ('<div class="trail">%s</div>' % ''.join(out)) if out else ''

def build_category(cat):
    k = cat['key']
    st = story_of(cat)
    S = STORY[k]
    C = COMMS[k]
    A, B = C['a'], C['b']
    nsteps = len(cat['sell']['steps'])
    P = []
    n = 0

    def add(*a):
        P.append(panel(*a))

    # ---- ACT I
    n += 1
    mail = ('<div class="phone mail tall"><div class="mbar"><span class="dot"></span> Inbox &middot; 07:04</div>'
            '<div class="mhead"><h3>%s</h3><div class="mfrom"><span class="av">TS</span>'
            '<span><b>TrustSquare</b><span>david@mail.trustsquare.co</span></span><u>07:04</u></div></div>'
            '<div class="mbody"><p>%s</p><p>%s</p><span class="cta">%s</span>'
            '<div class="link">trustsquare.co/%s</div>'
            '<div class="optout">You are receiving this once. Unsubscribe &middot; TrustSquare (Pty) Ltd, Pretoria</div>'
            '</div></div>' % (e(S['subject']), e(S['b1']), e(S['b2']), e(S['cta']), S['path']))
    add('mail', n, 'The email lands with %s, and the link in it is the Quick Listing, not the app.'
        % e(S['audience']), mail,
        'wave shape &middot; not built', 'note',
        'The email is the only invented screen here &mdash; this wave has no date, so there is no sent copy.')

    n += 1
    door = ('<div class="phone tall">%s<div class="scr mid">'
            '<div class="orb">%s</div>'
            '<div class="catrow"><span class="arw">&#8249;</span><span class="catname">%s</span>'
            '<span class="arw">&#8250;</span></div><div class="dots">%s</div>'
            '<div class="acts"><span class="btn ghost">%s</span><span class="btn solid">%s</span></div>'
            '<div class="dswitch"><i></i>New here &mdash; asked once, at the very end</div></div></div>'
            % (bar(lock='TrustSquare'), img(cat['hero'][0]), e(cat['name']),
               ''.join('<i class="%s"></i>' % ('on' if c['key'] == k else '')
                       for c in CATS),
               e(cat['findLabel']), e(cat['sellLabel'])))
    add('mail', n, 'The link opens the same door for every category &mdash; eight on a swipe, '
        'the brand said once and then out of the way.', door,
        'built &middot; harness', 'built',
        'One renderer, eight categories. A ninth category is a data row, not a new screen.')

    # ---- ACT II : the taps
    for i, step in enumerate(cat['sell']['steps']):
        n += 1
        p = st['picks'][i]
        if step['kind'] == 'week':
            order = [t['t'] for t in step['tiles']]
            on = set(p['label'].split(', '))
            cells = ''.join('<div class="wd%s%s"><b>%s</b><i>%s</i></div>'
                            % (' wend' if d in ('Sat', 'Sun') else '',
                               ' on' if d in on else '', d,
                               'open' if d in on else ('weekend' if d in ('Sat', 'Sun') else 'free?'))
                            for d in order)
            inner = ('<div class="week">%s</div><div class="wkline">Open <b>%s</b>.</div>'
                     '<span class="chip" style="margin:0 auto">Every day</span>'
                     '<div style="padding-top:14px"><span class="btn solid">Next &mdash; %d days open</span></div>'
                     % (cells, ' &middot; '.join(sorted(on, key=order.index)), len(on)))
            cls = 'scr mid'
            note = 'A week of work is not one day &mdash; the old single row made her lie about two of them.'
            pip, pipcls = 'ruled 14 Sep', 'ruled'
        elif step['kind'] == 'chip':
            inner = '<div class="chips">%s</div>' % ''.join(
                '<span class="chip%s">%s</span>' % (' on' if t['t'] == p['label'] else '', e(t['t']))
                for t in step['tiles'])
            cls = 'scr mid'
            note = 'Tap-only. Nothing on this screen is typed.'
            pip, pipcls = 'built &middot; harness', 'built'
        else:
            inner = '<div class="tiles">%s</div>' % ''.join(
                '<div class="tile%s">%s<b>%s</b></div>'
                % (' sel' if t['t'] == p['label'] else '', img(t['p']), e(t['t']))
                for t in step['tiles'])
            cls = 'scr'
            note = 'Photographs, not a word list &mdash; the tiles are the same component in all eight.'
            pip, pipcls = 'built &middot; harness', 'built'
        ph = ('<div class="phone tall">%s<div class="%s"><div class="q">%s</div>%s%s</div></div>'
              % (bar(dots(nsteps + 1, i)), cls, e(step['q']), trail_of(st['picks'], i), inner))
        add('work', n, 'Tap %d: %s' % (i + 1, e(step['q'].lower().rstrip('?')) + '.'), ph, pip, pipcls, note)

    # ---- ACT III : the advert
    n += 1
    top = st['missing'][0]
    jobs = ''.join('<div><span class="plus">+</span>%s<b>+%d</b></div>' % (e(m['t']), round(m['pts']))
                   for m in st['missing'][1:])
    jobs += ('<div><span class="plus">+</span>Check the wording</div>'
             '<div><span class="plus">+</span>Confirm your number</div>')
    credrow = ''
    if k in CRED:
        credrow = ('<div class="cred"><b>%s &mdash; what lifts the other half</b><div class="credlist">%s</div></div>'
                   % (e(cat['name']), ''.join('<span>%s<i>+%d</i></span>' % (e(t), p) for t, p in CRED[k])))
    fieldnote = ''
    if st['fields'] >= 4:
        fieldnote = ('<div class="gate" style="margin-top:8px">%s listings ask for more than most &mdash; %d '
                     'details rather than one &mdash; so they start lower and climb further. None of it is a '
                     'penalty for what the quick form did not ask.</div>' % (e(cat['name']), st['fields']))
    card = ('<div class="phone">%s<div class="scr"><div class="q">Here is your advert</div>'
            '<div class="draftflag"><span>&#9998;</span> Draft &mdash; %d things left to finish</div>'
            '<div class="card">%s<div class="pad"><h3>%s</h3><p>%s</p><div class="facts">%s</div></div></div>'
            '<div class="scores"><h4>Your three scores</h4>'
            '<p class="yours">Only you see these. Buyers see the star alone.</p>'
            '<div class="scrow">'
            '<div class="sc"><b style="color:var(--br)">%s</b><i>RS</i><u>ranking</u></div>'
            '<div class="sc"><b style="color:#6B7280">0</b><i>TS</i><u>new</u></div>'
            '<div class="sc"><b style="color:var(--c)">%d</b><i>LS</i><u>+%d available</u></div></div>'
            '<div class="coach"><div class="big"><em>+%d</em><div>%s'
            '<span>Worth more than anything else you can do right now.</span></div></div></div>%s'
            '<div class="gate" style="margin-top:8px">%s</div>%s'
            '<div class="gate">Ranking is half trust, half listing quality. Your trust score opens when '
            'somebody outside vouches for you, or you pass an ID check.</div></div>'
            '<div class="todolab">Each of these adds to your listing score</div>'
            '<div class="todo">%s</div>'
            '<div style="padding-top:12px"><span class="btn solid">Publish it</span>'
            '<div class="hint">%d taps to get here</div></div></div></div>'
            % (bar(dots(nsteps + 1, nsteps)), len(st['missing']) + 2,
               img(st['hero'], cls='hero'), e(st['title']), e(st['body']),
               ''.join('<span>%s</span>' % e(p['label']) for p in st['picks']),
               st['rs'], st['ls'], st['headroom'], round(top['pts']), e(top['t']),
               credrow, e(PRICE_NOTE.get(k, PRICE_ANY)), fieldnote, jobs, st['taps']))
    add('work', n, 'The advert, written from the taps, with all three of her own scores and the one '
        'biggest win named.', card, 'built &middot; harness', 'built',
        'LS %d with +%d still on the table &mdash; the server&rsquo;s own scorer, mirrored so the number does not move on hand-over.'
        % (st['ls'], st['headroom']))

    n += 1
    ask = ('<div class="phone tall">%s<div class="scr"><div class="q">Here is your advert</div>'
           '<div class="joinbox"><b>One thing, once.</b>'
           '<div class="inrow"><span class="fld ph">you@example.com</span><button>Publish</button></div>'
           '<p>Publishing accepts the TrustSquare terms, including Buzz exactly as it is &mdash; a doorbell '
           'between two people, not a messaging service, with an off switch on both sides. This is the only '
           'thing this screen ever asks you, and it will not ask you again on any device you are signed in '
           'on.</p></div>'
           '<div class="hres"><b>&#10003; Handed over.</b> Draft #4127 is in TrustSquare. Finish onboarding '
           'there to go live.</div>'
           '<div class="bznote">The Quick app has no database and no scorer of its own &mdash; it posts the '
           'draft to the same listings the live app reads. One server, one rulebook.</div></div></div>'
           % bar(dots(nsteps + 1, nsteps)))
    add('work', n, 'Only now is anything asked, and it is one line, once, never again on any device.',
        ask, 'built &middot; harness', 'built',
        'A stranger made to sign up before he has seen anything leaves; going through it makes him a member.')

    # ---- ACT IV : into TrustSquare
    n += 1
    onb = ('<div class="phone ts tall">%s<div class="scr">'
           '<div class="sec"><h5>Terms<span class="rl">accepted</span></h5>'
           '<div class="rung on"><span class="tick">&#10003;</span> TrustSquare terms &amp; EULA</div>'
           '<div class="rung on"><span class="tick">&#10003;</span> Draft #4127 attached to your account</div></div>'
           '<div class="sec"><h5>Buzz &mdash; switched on here, once</h5>'
           '<div class="perm"><span>Let TrustSquare buzz <b>this</b> phone</span><span class="sw on"></span></div>'
           '<div class="perm"><span>Let <b>%s</b> buzz me</span><span class="sw on"></span></div>'
           '<p class="fine">%s answers the same two. Only the people you are paired with can buzz you '
           '&mdash; a buzz is never open to strangers.</p></div>'
           '<div class="bznote">Push first, free and self-hosted; email catches it when push is off. '
           'No SMS &mdash; a per-message cost is out.</div></div></div>'
           % (bar(lock='Onboarding'), e(B), e(B)))
    add('plat', n, 'Onboarding is where the two Buzz permissions are switched on &mdash; once by each '
        'side, and never inside the conversation.', onb, 'ruled 14 Sep', 'ruled',
        'Identical in all eight categories. The flow may vary per category; the consent model never forks.')

    n += 1
    rungs = ('<div class="rung on"><span class="tick">&#10003;</span> Phone number confirmed <small>+8</small></div>'
             '<div class="rung on"><span class="tick">&#10003;</span> Listing complete <small>+30</small></div>')
    if BROUGHT[k] == 'worker':
        rungs += ('<div class="rung off"><span class="tick"></span> An employer confirms you <small>+35</small></div>'
                  '<div class="rung off"><span class="tick"></span> 3 years with that employer <small>+12</small></div>')
    for t, p in CRED.get(k, []):
        rungs += '<div class="rung off"><span class="tick"></span> %s <small>+%d</small></div>' % (e(t), p)
    rungs += '<div class="rung off"><span class="tick"></span> ID checked <small>+15</small></div>'
    if BROUGHT[k] == 'worker':
        lock = ('<div class="locked"><div class="lk">&#128274;</div><h3>Not on strangers&rsquo; screens yet</h3>'
                '<p>Until one employer confirms you, or your ID is checked, only the people you have sent '
                'your own link to can reach you.</p></div>')
        locknote = 'Where the PERSON is the product, the listing is held back until somebody outside vouches.'
    else:
        lock = ('<div class="locked"><div class="lk">&#9733;</div><h3>Listed, at a new seller&rsquo;s trust</h3>'
                '<p>The listing is on the shelf, ordered below sellers who carry proof. Trust opens on an ID '
                'check or a credential above &mdash; and it then counts on every listing you ever make.</p></div>')
        locknote = 'Where the ITEM is the product the listing shows at once; only its place in the order is earned.'
    prov = ('<div class="phone ts tall">%s<div class="scr">'
            '<div class="tsbig"><b style="color:#E0AE4E">38</b><i>trust score</i></div>'
            '<div class="sec"><h5>What is proved about you</h5>%s</div>%s</div></div>'
            % (bar(lock='My listing'), rungs, lock))
    add('plat', n, 'Her listing exists, and what it is worth in the order is decided by what has been '
        'proved about her &mdash; not by what she said.', prov,
        'built &middot; VEL ladder', 'built', locknote)

    # ---- ACT V : the pair
    n += 1
    pairsc = ('<div class="phone ts tall">%s<div class="scr">'
              '<div class="q" style="font-size:13px">How this pair is made</div>'
              '<div class="sec"><h5>%s<span class="rl" style="%s">%s</span></h5>'
              '<dl class="bzfacts"><dt>Who</dt><dd>%s &harr; %s<span>%s</span></dd>'
              '<dt>How you met</dt><dd>%s</dd>'
              '<dt>Who paid</dt><dd class="pay">%s</dd>'
              '<dt>How many</dt><dd>%s</dd></dl>%s</div>'
              '<div class="bznote">Connections the lister brings are free. Connections the platform makes '
              'cost a Tuppence. The free lane is the <b>pair</b>, not the person.</div></div></div>'
              % (bar(lock='The pair'), e(cat['name']),
                 '' if C['ruled'] else 'border-color:#E0AE4E;color:#f0cc8a',
                 'ruled' if C['ruled'] else 'not ruled yet',
                 e(A), e(B), e(C['bRole']), e(C['met']), e(C['pay']), e(C['many']),
                 ('<p class="fine">%s</p>' % e(C['note'])) if C.get('note') else ''))
    add('emp', n, e(S['pairline']), pairsc,
        'ruled' if C['ruled'] else 'Claude&rsquo;s read &middot; not ruled',
        'ruled' if C['ruled'] else 'note',
        'Four lines are all a category changes. Everything protecting the pair is written once, below them.'
        if C['ruled'] else
        'Built so you can argue with a screen instead of a paragraph &mdash; this row is not ruled.')

    n += 1
    if BROUGHT[k] == 'worker':
        other = ('<div class="phone ts tall"><div class="urlbar">trustsquare.co/t/%s</div>'
                 '<div class="scr" style="padding-top:12px"><div class="empcard">'
                 '<h3>%s asks you to confirm</h3>'
                 '<p>She says she has worked for you for <b>9 years</b>, on <b>Mondays and Tuesdays</b>. '
                 'You are not signing anything and you are not paying anything. You are saying she is who '
                 'she says she is.</p>'
                 '<span class="btn solid">Yes, she works for me</span>'
                 '<span class="btn ghost">I would rather not</span>'
                 '<p class="empnote">If you would rather not, nothing happens to her listing.</p></div>'
                 '<div class="okbox"><b>Thank you.</b> Her trust score went from 38 to 85, and she is now '
                 'visible to people looking in %s.</div></div></div>'
                 % (A.split()[0].lower(), e(A.split()[0]), 'Menlyn'))
        cap = 'One tap from %s turns a listing nobody can see into a listing everybody can.' % e(B)
        note = 'The confirmer&rsquo;s name is never published &mdash; only that it happened.'
        pip, pipcls = 'built &middot; homehelp bot', 'built'
    else:
        other = ('<div class="phone ts tall">%s<div class="scr">'
                 '<div class="empcard"><h3>%s asks to be introduced</h3>'
                 '<p>%s You decide, and nothing moves until you do.</p>'
                 '<span class="btn solid">Accept the introduction</span>'
                 '<span class="btn ghost">Not now</span></div>'
                 '<div class="blk"><h4>What they get, and when</h4>'
                 '<div class="tier t-pub"><i></i><span>What is listed, where it is, the price, the star</span></div>'
                 '<div class="tier t-int"><i></i><span>Your name, your number, where it can be seen '
                 '&mdash; when you accept</span></div>'
                 '<div class="tier t-nev"><i></i><span>Your ID document, and who vouched for you '
                 '&mdash; never published</span></div></div>'
                 '<div class="bznote">%s</div></div></div>'
                 % (bar(lock='Introduction'), e(B), e(C['met']), e(C['pay'])))
        cap = '%s' % e(C['met'])
        note = 'Hold model: the Tuppence is committed on request and burns only on delivery.'
        pip, pipcls = 'ruled &middot; hold model', 'ruled'
    add('emp', n, cap, other, pip, pipcls, note)

    # ---- ACT VI : two streams
    n += 1
    pubcard = ('<div class="phone ts">%s<div class="scr">'
               '<div class="avrow"><span class="av">%s</span>'
               '<span><h3>%s</h3><p>%s</p></span>'
               '<span class="tsc"><b>85</b><i>TRUST</i></span></div>'
               '<div class="vouch">&#10003; %s<small>name not shown</small></div>'
               '<div class="doesit">%s</div>'
               '<div class="rate"><b>%s</b><small>Paid to them, not to us. Nothing but the introduction '
               'goes through TrustSquare.</small></div>'
               '<div class="blk"><h4>What you get, and when</h4>'
               '<div class="tier t-pub"><i></i><span>What is listed, where, the price, the star</span></div>'
               '<div class="tier t-int"><i></i><span>Name, number and address &mdash; when they accept</span></div>'
               '<div class="tier t-nev"><i></i><span>ID document, and who vouched &mdash; never published</span></div></div>'
               '<div style="padding-top:10px"><span class="btn solid">Ask to be introduced &mdash; 1 Tuppence</span>'
               '<div class="hint">%s</div></div></div></div>'
               % (bar(lock='Browse'), img(st['hero']),
                  e(A.split()[0] + ' ' + A.split()[-1][0] + '.'), e(cat['name'] + ' &middot; ' + st['picks'][0]['label']),
                  'Confirmed by an employer of 3 years' if BROUGHT[k] == 'worker'
                  else 'Verified on the evidence ladder',
                  ''.join('<span>%s</span>' % e(p['label']) for p in st['picks'][:3]),
                  e(st['by']['price']['label'] if st['by'].get('price') else 'POA'),
                  'The paired party pays nothing for the same thing.'))
    add('work', n, 'Her stream: the public card, where the star is the only score shown and a stranger '
        'pays to be introduced.', pubcard, 'built &middot; homehelp bot', 'built',
        'One mechanism for every category &mdash; the three scores decide, never a per-category gate.')

    n += 1
    free = ('<div class="phone ts tall">%s<div class="scr">'
            '<div class="empcard"><h3>%s</h3><p>%s<span class="freebadge">%s</span></p>'
            '<span class="btn ghost">%s</span>'
            '<p class="empnote">A stranger asking for the same thing pays <b>1 Tuppence</b>. %s</p></div>'
            '<div class="bznote">%s</div></div></div>'
            % (bar(lock=B.split()[0]),
               'Need another day?' if BROUGHT[k] == 'worker' else 'You two are connected',
               e(C['card']), 'Free' if BROUGHT[k] == 'worker' else 'Paid once',
               'Ask for an open day' if BROUGHT[k] == 'worker' else 'Open the line',
               'You do not, because there is nothing left to introduce.',
               e(C['many'])))
    add('emp', n, 'The other side of the pair, where the till has already rung &mdash; or never will.',
        free, 'ruled' if C['ruled'] else 'Claude&rsquo;s read &middot; not ruled',
        'ruled' if C['ruled'] else 'note',
        'How many pairs, and whether they end, is the one thing that really differs by category.')

    # ---- ACT VII : buzz
    n += 1
    compose = ('<div class="phone tall">%s<div class="scr"><div class="q">Buzz</div>'
               '<div class="bzlede">One line, straight to the other phone, with your name on it. '
               'No thread, no history, nothing to scroll.</div>'
               '<div class="sec"><h5>Send a buzz</h5>'
               '<div class="dirs"><span class="on">You &rarr; %s</span><span>%s &rarr; you</span></div>'
               '<div class="inrow"><span class="fld">%s</span><button>Buzz</button></div>'
               '<div class="bzleft">%d left</div></div>'
               '<div class="bznote">%s</div></div></div>'
               % (bar(), e(B.split()[0]), e(B.split()[0]), e(C['sample']),
                  120 - len(C['sample']), e(C['card'])))
    add('buzz', n, 'The same panel in every category: one free line, no canned messages, nothing else '
        'on the screen to do.', compose, 'ruled 14 Sep', 'ruled',
        'Universally usable by design &mdash; it can be pointed at any two paired people in the platform.')

    n += 1
    ini = ''.join(w[0] for w in A.split()[:2]).upper()
    land = ('<div class="phone tall">%s<div class="scr">'
            '<div class="onphone">On %s&rsquo;s phone, right now</div>'
            '<div class="push"><div class="who"><span class="avi">%s</span>%s<u>now &middot; 07:12</u></div>'
            '<div class="msg">%s</div>'
            '<div class="rep"><span>Buzz %s back</span></div>'
            '<div class="rec">Delivered to <b>%s&rsquo;s</b> phone.</div></div>'
            '<div class="bznote">If push is off it goes to email instead. No SMS: a per-message cost '
            'breaks the zero-cost rule.</div>'
            '<div class="bznote warn">Either of you can close it at any time: closing it closes it for '
            'both, the other person is told plainly, and whoever closed it can open it again.</div>'
            '</div></div>' % (bar(), e(B), ini, e(A), e(C['sample']), e(A.split()[0]), e(B)))
    add('buzz', n, 'It lands as a push, free and self-hosted, with the sender&rsquo;s name already on it.',
        land, 'built &middot; harness + server', 'built',
        'Same endpoint the live app uses; delivered is push, email or none &mdash; and it says which.')

    # -------------------------------------------------------------- assemble
    acts = [('I', 'The send-out', 'The spreader link goes in the email instead of the app.', 'mail', 2),
            ('II', 'The taps', 'Nothing is typed, and nothing is asked until the advert exists.', 'work', nsteps),
            ('III', 'The advert', 'Their own three scores, and the single biggest thing they can do next.', 'work', 2),
            ('IV', 'Into TrustSquare', 'Terms, the two Buzz switches, and what has actually been proved.', 'plat', 2),
            ('V', 'The pair', 'Who the other person is, how they met, and who paid.', 'emp', 2),
            ('VI', 'Two streams', 'From here they are two users of one app, and the till rings on one side.', 'both', 2),
            ('VII', 'The buzz', 'One line, one name on it, the same button on both phones.', 'buzz', 2)]
    out, i = [], 0
    for num, name, blurb, stream, count in acts:
        body = ''.join(P[i:i + count])
        i += count
        out.append('<section class="act a-%s"><div class="actbar"><span class="n">ACT %s</span>'
                   '<h2>%s</h2><p>%s</p></div><div class="strip">%s</div></section>'
                   % (stream, num, e(name), e(blurb), body))
    tally = ('<section class="act"><div class="actbar" style="border-left-color:var(--ink)">'
             '<span class="n">THE TALLY</span><h2>What this one email bought</h2>'
             '<p>%s</p></div><div class="tally">'
             '<div><b style="color:var(--work)">%d</b><span>taps from the email to a finished draft advert</span></div>'
             '<div><b style="color:var(--plat)">%d</b><span>listing score, with +%d still on the table</span></div>'
             '<div><b style="color:var(--emp)">2</b><span>users out of one send &mdash; the lister, and the '
             'person they are paired with</span></div>'
             '<div><b style="color:var(--buzz)">R0</b><span>per message, for ever &mdash; push first, email '
             'backup, never SMS</span></div></div></section>'
             % (e(C['pay']), st['taps'], st['ls'], st['headroom']))
    return ('<div class="cat" id="cat-%s" data-c="%s" data-bg="%s" data-panel="%s" data-line="%s" '
            'data-bright="%s" hidden>%s%s</div>'
            % (k, cat['c'], cat['bg'], cat['panel'], cat['line'], cat['bright'],
               ''.join(out), tally))

# ------------------------------------------------------------------ page shell
CSS = open(os.path.join(HERE, 'comic.css'), encoding='utf-8').read()

EXTRA = """
/* ---------- category rail ---------- */
.rail{display:flex;flex-wrap:wrap;gap:8px;margin-top:16px}
.rail button{display:flex;align-items:center;gap:7px;border:2px solid var(--rule);background:var(--paper2);
  color:var(--ink);font:inherit;font-size:12.5px;font-weight:700;padding:8px 12px 8px 9px;cursor:pointer;
  transition:transform .12s}
.rail button:hover{transform:translateY(-1px)}
.rail button i{width:13px;height:13px;border:2px solid var(--rule);flex:0 0 auto}
.rail button[aria-pressed="true"]{color:var(--paper2);background:var(--ink)}
.rail button[aria-pressed="true"] i{border-color:var(--paper2)}
.rail button:focus-visible{outline:3px solid var(--plat);outline-offset:2px}
.railnote{font-size:12px;color:var(--ink2);margin-top:9px}
.cat[hidden]{display:none}
.nowcat{display:flex;align-items:center;gap:10px;margin-top:22px;border:3px solid var(--rule);
  background:var(--paper2);padding:10px 14px}
.nowcat i{width:18px;height:18px;border:2px solid var(--rule);flex:0 0 auto}
.nowcat b{font-family:"Archivo Black",Impact,sans-serif;font-size:15px;text-transform:uppercase;letter-spacing:.01em}
.nowcat span{font-size:12.5px;color:var(--ink2)}
"""

HEAD = """<title>One Email, Two Users</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Archivo:wght@400;500;600;700&display=swap">
<style>%s%s</style>
""" % (CSS, EXTRA)

rail = ''.join('<button type="button" data-k="%s" aria-pressed="%s"><i style="background:%s"></i>%s</button>'
               % (c['key'], 'true' if c['key'] == 'homehelp' else 'false', c['c'], e(c['name']))
               for c in CATS)

MAST = """
<div class="wrap">
<header class="mast">
  <div class="kick">TrustSquare &middot; Quick Listing &rarr; the app &middot; all eight categories</div>
  <h1>One email,<br>two users</h1>
  <p>The whole loop on the phone, panel by panel &mdash; an email lands, the taps make an advert,
     TrustSquare takes the draft, a second person is brought in, and the two of them end up buzzing each
     other. Pick a category: the panels are generated from the app&rsquo;s own tables, so every story is
     the same engine with different data, exactly as the product is built.</p>
  <div class="legend">
    <span class="key k-mail"><i></i><b>The send-out</b><span>&mdash; outside the app</span></span>
    <span class="key k-work"><i></i><b>The lister's stream</b><span>&mdash; whoever the email reached</span></span>
    <span class="key k-plat"><i></i><b>TrustSquare</b><span>&mdash; onboarding, scores, hand-over</span></span>
    <span class="key k-emp"><i></i><b>The other party</b><span>&mdash; the second user</span></span>
    <span class="key k-buzz"><i></i><b>Buzz</b><span>&mdash; the comms, both ways</span></span>
  </div>
  <div class="rail">%s</div>
  <p class="railnote">Eight categories, one renderer. The screens are identical; four lines change &mdash;
     who the other person is, how they met, who paid, and how many pairs there are.</p>
  <p class="footnote">In every pair both names come from the same naming tradition, which is the
     14 September rule for every example in this product.</p>
  <div class="rule"></div>
</header>
<div class="nowcat"><i id="nowdot"></i><b id="nowname">Housekeeping</b>
  <span id="nowsub">the only lane that is built &mdash; the rest are the same engine, run on their own data</span></div>
""" % rail

SUB = {
 'homehelp': 'the built lane &mdash; a worker brings her own employer in free',
 'property': 'ruled 14 Sep &mdash; the agency pays, one agency at a time',
 'cars': 'Claude&rsquo;s read &mdash; many buyers, one car, and the pair ends when it sells',
 'tutors': 'Claude&rsquo;s read &mdash; one pair per child, standing for a term',
 'services': 'Claude&rsquo;s read &mdash; strangers pay, your own regulars are free',
 'collectors': 'Claude&rsquo;s read &mdash; paid once, then traded for decades',
 'adventures': 'Claude&rsquo;s read &mdash; one introduction, many places answering',
 'localmarket': 'Claude&rsquo;s read &mdash; the amounts are too small for an introduction to apply',
}

FOOT = """
<section class="act">
  <div class="rules">
    <h3>Why this is one page and not eight</h3>
    <ol>
      <li><b>The screens do not differ</b> &mdash; the door, the four taps, the advert, the scores, the
          onboarding and the buzz panel are one renderer running on a data table.</li>
      <li><b>Four lines differ</b> &mdash; who the other person is, how they met, who paid, and how many
          pairs there are. That is the whole category difference, and it already lives in one table.</li>
      <li><b>So a ninth category is a row, not a comic</b> &mdash; and a change to the flow lands in all
          eight at once instead of going stale in seven of them.</li>
      <li><b>Two rows are ruled</b> (housekeeping and property); the other six are marked on the panel as
          a read, not a decision &mdash; argue with the screen, and the row changes.</li>
    </ol>
  </div>
  <p class="src">Generated from <code>genie/HARNESS.html</code> &mdash; its CATS table (categories, steps,
    tiles, photographs), its COMMS table (who, how you met, who paid, how many) and its listing scorer,
    which mirrors the server&rsquo;s. The employer-confirmation screens come from
    <code>genie/bots/homehelp/BOT_HOMEHELP.html</code>. Only the email panel is invented, because no wave
    after the first has a date yet.</p>
</section>
</div>
<script>
(function(){
  var PH = %s;
  var imgs = document.querySelectorAll('img[src^="@@"]');
  for (var i = 0; i < imgs.length; i++) {
    var k = imgs[i].getAttribute('src').replace(/@/g, '');
    if (PH[k]) imgs[i].src = PH[k];
  }
  var SUB = %s;
  var rail = document.querySelectorAll('.rail button');
  var dot = document.getElementById('nowdot');
  var nm  = document.getElementById('nowname');
  var sub = document.getElementById('nowsub');
  function show(k){
    var cats = document.querySelectorAll('.cat');
    for (var i = 0; i < cats.length; i++) cats[i].hidden = (cats[i].id !== 'cat-' + k);
    for (var j = 0; j < rail.length; j++){
      var on = rail[j].getAttribute('data-k') === k;
      rail[j].setAttribute('aria-pressed', on ? 'true' : 'false');
      if (on){ nm.textContent = rail[j].textContent.trim();
               dot.style.background = rail[j].querySelector('i').style.background; }
    }
    sub.innerHTML = SUB[k] || '';
    var el = document.getElementById('cat-' + k);
    var s = el.dataset;
    el.style.setProperty('--c', s.c);
    document.documentElement.style.setProperty('--phc', s.c);
    var phones = el.querySelectorAll('.phone');
    for (var p = 0; p < phones.length; p++){
      if (phones[p].classList.contains('mail')) continue;
      phones[p].style.setProperty('--c', s.c);
      phones[p].style.setProperty('--br', s.bright);
      if (!phones[p].classList.contains('ts')){
        phones[p].style.setProperty('--bg', s.bg);
        phones[p].style.setProperty('--pn', s.panel);
        phones[p].style.setProperty('--ln', s.line);
      }
    }
  }
  for (var r = 0; r < rail.length; r++){
    rail[r].addEventListener('click', function(){
      show(this.getAttribute('data-k'));
      document.querySelector('.nowcat').scrollIntoView({block:'start', behavior:'smooth'});
    });
  }
  show('homehelp');
})();
</script>
"""

body = MAST + ''.join(build_category(c) for c in CATS) + (
    FOOT % (json.dumps({k: v for k, v in PH.items()}), json.dumps(SUB)))
page = HEAD + body
page = re.sub(r'@@([a-z0-9_]+)@@', lambda m: '@@' + m.group(1) + '@@', page)  # left for JS
open(os.path.join(HERE, 'comic_body.html'), 'w', encoding='utf-8').write(page)  # artifact form

head, rest = page.split('</style>', 1)
standalone = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
              '<meta name="viewport" content="width=device-width,initial-scale=1">\n'
              + head + '</style>\n</head>\n<body style="margin:0">\n' + rest + '\n</body>\n</html>\n')
open(os.path.join(HERE, 'EMAIL_TO_TWO_USERS.html'), 'w', encoding='utf-8').write(standalone)
print('categories:', len(CATS), 'bytes:', len(standalone))
for c in CATS:
    s = story_of(c)
    print('  %-12s taps=%-3d LS=%-3d +%-3d  %s' % (c['key'], s['taps'], s['ls'], s['headroom'], s['title']))
