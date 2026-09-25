#!/usr/bin/env python3
"""EXAMPLE-MARK-1 (David 25 Sep 2026: "The demos adverts are showing and that is good until we have some real
adverts, but they do need to be marked very clearly as adverts [examples]. currently they get showed as real
adverts inside the quick launcher but does show as example/demo adverts inside the trustsquare app. This will
then be a global fix?").
 * Quick's find results: every AI example advert (super_example / is_demo) wears the app's own red
   "AI EXAMPLE ADVERT" ribbon; the heading and the count line stop calling examples "real adverts".
 * GLOBAL: the outreach letters (CityLauncher/emailer/templates) showed the same example adverts under
   "... already live on TrustSquare"; they now say they are AI-made examples.
Idempotent; asserts every anchor."""
import io, os, glob, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(p, encoding="utf-8").read()
def wr(p, s):
    io.open(p, "w", encoding="utf-8").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
qp = os.path.join(R, "quick.html"); q = rd(qp)
q = rep(q, "      var five=(list||[]).slice(0,5);\n",
           "      var five=(list||[]).slice(0,5);\n"
           "      /* EXAMPLE-MARK-1: an AI example advert is never presented as a real one */\n"
           "      var isEx=function(l){ return !!(+l.super_example || +l.is_demo); };\n"
           "      var nEx=five.filter(isEx).length, nReal=five.length-nEx;\n", "five")
q = rep(q, "        return '<div class=\"ad\" data-lid=\"'+E(String(l.id).replace(/^bea_/,''))+'\" style=\"animation-delay:'+(i*25)+'ms\"><img src=\"'+E(ph)+'\" alt=\"\">'",
           "        return '<div class=\"ad\" data-lid=\"'+E(String(l.id).replace(/^bea_/,''))+'\" style=\"animation-delay:'+(i*25)+'ms;position:relative\">'"
           "+(isEx(l)?'<div class=\"exrib\">'+E(T('AI EXAMPLE ADVERT'))+'</div>':'')+'<img src=\"'+E(ph)+'\" alt=\"\">'", "card")
q = rep(q, "               : (five.length ? T('Yes')+' — '+five.length+' '+T('on TrustSquare') : T('Not listed yet'));",
           "               : (nReal ? T('Yes')+' — '+nReal+' '+T('on TrustSquare') : (nEx ? T('Only examples so far') : T('Not listed yet')));", "head")
q = rep(q, "          ? '<div class=\"count\"><span style=\"font-size:11.5px\">'+E(city)+' &middot; '+E(T('real adverts'))+' &middot; &#9733; '+E(T('is trust'))+'</span></div><div class=\"grid\">'+cards+'</div>'",
           "          ? '<div class=\"count\"><span style=\"font-size:11.5px\">'+E(city)+' &middot; '+E(nEx ? (nReal ? T('real adverts and AI examples') : T('AI examples of what an advert looks like')) : T('real adverts'))+' &middot; &#9733; '+E(T('is trust'))+'</span></div><div class=\"grid\">'+cards+'</div>'", "count")
q = rep(q, "   '.ad[data-lid]{cursor:pointer}'",
           "   '.ad[data-lid]{cursor:pointer}',\n"
           "   '.exrib{position:absolute;top:0;left:0;z-index:3;background:#e63946;color:#fff;font:800 9px/1.2 system-ui,sans-serif;letter-spacing:.03em;padding:4px 9px;border-radius:14px 0 10px 0;box-shadow:0 2px 6px rgba(0,0,0,.3)}'", "css")
wr(qp, q)
ip = os.path.join(R, "roles", "quick_i18n.json"); d = json.loads(rd(ip))
W = {"AI EXAMPLE ADVERT": ["KI-VOORBEELD","ISIBONELO SE-AI","MOHLALA WA AI","UMZEKELO WE-AI","MOHLALA WA AI"],
     "Only examples so far": ["Tot dusver net voorbeelde","Izibonelo kuphela okwamanje","Mehlala feela hajoale","Imizekelo kuphela okwangoku","Mehlala fela go fihla bjale"],
     "real adverts and AI examples": ["regte advertensies en KI-voorbeelde","izikhangiso zangempela nezibonelo ze-AI","dipapatso tsa nnete le mehlala ya AI","izibhengezo zokwenyani nemizekelo ye-AI","dipapatšo tša nnete le mehlala ya AI"],
     "AI examples of what an advert looks like": ["KI-voorbeelde van hoe 'n advertensie lyk","izibonelo ze-AI zokuthi isikhangiso sibukeka kanjani","mehlala ya AI ya hore papatso e shebahala jwang","imizekelo ye-AI yendlela isibhengezo esikhangeleka ngayo","mehlala ya AI ya ka moo papatšo e bonagalago ka gona"],
     "real adverts": ["regte advertensies","izikhangiso zangempela","dipapatso tsa nnete","izibhengezo zokwenyani","dipapatšo tša nnete"],
     "on TrustSquare": ["op TrustSquare","ku-TrustSquare","ho TrustSquare","kwiTrustSquare","go TrustSquare"],
     "Yes": ["Ja","Yebo","E","Ewe","Ee"], "is trust": ["is vertroue","ukwethenjwa","ke tshepo","kukuthembeka","ke go tshepega"],
     "Tap one to ask for an introduction — it opens in TrustSquare, where introductions and Tuppence live.":
       ["Tik een om 'n voorstelling te vra — dit maak oop in TrustSquare, waar voorstellings en Tuppence woon.","","","",""]}
for k, v in W.items(): d["w"].setdefault(k, v)
wr(ip, json.dumps(d, ensure_ascii=False, indent=1))
# GLOBAL: the outreach letters
n = 0
for f in sorted(glob.glob(os.path.join(R, "..", "CityLauncher", "emailer", "templates", "*.html"))):
    s = rd(f); s0 = s
    import re as _re
    s = _re.sub(r">([A-Z][a-z]+) already live on TrustSquare<",
                r">\1 on TrustSquare &mdash; AI-made example adverts, so you can see what yours will look like<", s)
    s = s.replace(" — live on TrustSquare\"", " — an AI-made example advert on TrustSquare\"")
    if s != s0: wr(f, s); n += 1
print("EXAMPLE-MARK-1 applied; letters changed:", n)
