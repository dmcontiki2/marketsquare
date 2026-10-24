#!/usr/bin/env python3
"""build_generic_examples.py -- GEN-EX-1 (David, 24 Oct 2026): "the prices will reflect correct for different countries,
ZA Rand, US Dollar, UK Pounds etc. And to be used generic the location should also change to where it gets advertised".

One set of example adverts ("Your listing here", RUL-249) for EVERY city: each carries a local price per country (a real
local price, not an exchange-rate conversion) and no location of its own -- door.html shows the visitor's own city.
A country with no price here shows the example WITHOUT a price (DOOR-MONEY-1: never another country's money).

Writes: assets/ex/<group>_<n>.jpg (door size, from assets/ny_ex/) -> media_push [1g] -> /static/ex/
        the GEX block inside door.html (between /*GEX*/ and /*END-GEX*/), read by the door's example pool.
"""
import json, os, re, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "assets", "ny_ex"); OUT = os.path.join(ROOT, "assets", "ex"); DOOR = os.path.join(ROOT, "door.html")
# group: (category, sub, title, unit, {US, GB, ZA, AU, KE}) -- a number or a (low, high) range, or "from" prefix via unit
G = {
 "adv_kayak":   ("Adventures","Experiences","Kayak hire · half-day guided paddle","/ person",{"US":65,"GB":45,"ZA":450,"AU":85,"KE":3500}),
 "adv_hike":    ("Adventures","Experiences","Guided mountain day hike","/ person",{"US":55,"GB":40,"ZA":400,"AU":75,"KE":3000}),
 "adv_cabin":   ("Adventures","Stays","Lakeside cabin · sleeps 4","/ night",{"US":180,"GB":140,"ZA":1500,"AU":240,"KE":9000}),
 "adv_cycle":   ("Adventures","Experiences","Guided river cycle tour · bikes included","/ person",{"US":50,"GB":35,"ZA":350,"AU":70,"KE":2500}),
 "adv_climb":   ("Adventures","Experiences","Intro to climbing · half-day course","/ person",{"US":120,"GB":70,"ZA":650,"AU":140,"KE":5000}),
 "adv_cave":    ("Adventures","Experiences","First caving trip · guided, gear supplied","/ person",{"US":95,"GB":60,"ZA":550,"AU":120,"KE":4500}),
 "lm_produce":  ("Local Market","","Farm-fresh fruit & veg box","/ box",{"US":35,"GB":25,"ZA":250,"AU":45,"KE":1500}),
 "lm_bakes":    ("Local Market","","Home-baked sourdough & cakes · to order","from",{"US":8,"GB":6,"ZA":60,"AU":10,"KE":500}),
 "lm_crafts":   ("Local Market","","Handmade pottery, knitwear & candles","from",{"US":15,"GB":12,"ZA":120,"AU":20,"KE":800}),
 "col_cards":   ("Collectors","Trading cards","Trading-card singles · sleeved rares","each",{"US":(4,60),"GB":(3,50),"ZA":(50,900),"AU":(6,90),"KE":(400,6000)}),
 "col_vinyl":   ("Collectors","Vinyl records","Vinyl records · crates of LPs, graded","each",{"US":(8,40),"GB":(6,30),"ZA":(80,400),"AU":(12,60),"KE":(500,3000)}),
 "col_comics":  ("Collectors","Comics","Comics · bagged and boarded runs","each",{"US":(5,50),"GB":(4,40),"ZA":(60,600),"AU":(8,75),"KE":(400,4000)}),
 "col_coins":   ("Collectors","Coins","Coin collection · albums and loose coins","each",{"US":(5,200),"GB":(4,150),"ZA":(50,2500),"AU":(8,300),"KE":(400,15000)}),
 "tut_uni":     ("Tutors","Maths","University maths & statistics · one-to-one","/ hour",{"US":75,"GB":45,"ZA":400,"AU":80,"KE":2500}),
 "tut_music":   ("Tutors","Music","Piano & guitar lessons · all levels","/ hour",{"US":60,"GB":40,"ZA":350,"AU":70,"KE":2000}),
 "tut_lang":    ("Tutors","Languages","Language tutoring · conversation & exam prep","/ hour",{"US":45,"GB":32,"ZA":280,"AU":55,"KE":1500}),
 "tut_chess":   ("Tutors","Chess","Chess coaching · beginners to club level","/ hour",{"US":60,"GB":35,"ZA":300,"AU":60,"KE":1500}),
 "fit_trainer": ("Tutors","Personal trainer","Personal training · strength & mobility","/ session",{"US":85,"GB":50,"ZA":400,"AU":90,"KE":2500}),
 "svc_dog":     ("Services","Dog walker","Dog walking · solo or small group","/ walk",{"US":25,"GB":15,"ZA":120,"AU":30,"KE":800}),
 "svc_handy":   ("Services","Handyman","Handyman & painter · small jobs","/ hour",{"US":60,"GB":40,"ZA":350,"AU":70,"KE":1500}),
 "svc_elec":    ("Services","Electrician","Licensed electrician · switches, lights & panels","call-out",{"US":120,"GB":80,"ZA":650,"AU":130,"KE":3000}),
 "car_pickup":  ("Cars","Pickup","Double-cab pickup · one owner, serviced","",{"US":32000,"GB":26000,"ZA":485000,"AU":52000,"KE":4800000}),
 "car_moto":    ("Cars","Motorbike","Naked motorbike · low mileage","",{"US":6500,"GB":5200,"ZA":95000,"AU":9500,"KE":900000}),
}
# countries priced by rule from a sibling (same economy / pegged currency)
DERIVE = {"NA": ("ZA", 1.0), "BW": ("ZA", 0.75), "MZ": ("ZA", 3.5), "NZ": ("AU", 1.1), "CA": ("US", 1.35)}
EURO = ["DE","AT","NL","BE","FR","IE","IT","ES","PT","FI","LU","GR"]   # euro countries: from the UK price x 1.15
for _c in EURO: DERIVE[_c] = ("GB", 1.15)
SYM = {**{c: "\u20ac" for c in ["DE","AT","NL","BE","FR","IE","IT","ES","PT","FI","LU","GR"]}, "ZA":"R","US":"$","GB":"£","AU":"A$","KE":"KSh ","NA":"N$","NZ":"NZ$","CA":"C$","BW":"P","MZ":"MT "}   # door.html SYM + the euro
SPACE_SEP = {"ZA","NA","BW","MZ"}
def nice(v):
    if v >= 1000000: step = 10000
    elif v >= 100000: step = 5000
    elif v >= 10000: step = 1000
    elif v >= 1000: step = 50
    elif v >= 100: step = 10
    else: step = 1
    return int(round(v / step) * step)
def fmt(cc, v):
    s = "{:,}".format(nice(v)); s = s.replace(",", " ") if cc in SPACE_SEP else s
    return SYM[cc] + s
def price(cc, val, unit):
    p = (fmt(cc, val[0]) + " – " + fmt(cc, val[1])) if isinstance(val, tuple) else fmt(cc, val)
    if unit == "from": return "from " + p
    if unit == "call-out": return p + " call-out"
    return (p + " " + unit).strip()
def main():
    os.makedirs(OUT, exist_ok=True); ex = []
    for g, (cat, sub, title, unit, base) in G.items():
        prices = {}
        for cc, v in base.items(): prices[cc] = price(cc, v, unit)
        for cc, (frm, k) in DERIVE.items():
            v = base[frm]; v = (v[0]*k, v[1]*k) if isinstance(v, tuple) else v*k
            prices[cc] = price(cc, v, unit)
        imgs = []
        for n in range(1, 6):
            src = os.path.join(SRC, "%s_%d.jpg" % (g, n))
            if not os.path.exists(src): sys.exit("MISSING photo %s" % src)
            im = Image.open(src).convert("RGB"); im.thumbnail((720, 720)); im.save(os.path.join(OUT, "%s_%d.jpg" % (g, n)), "JPEG", quality=80)
            imgs.append("%s_%d" % (g, n))
        ex.append({"g": g, "cat": cat, "sub": sub, "title": title, "img": imgs, "price": prices})
    blob = json.dumps(ex, ensure_ascii=False, separators=(",", ":"))
    s = open(DOOR, encoding="utf-8").read()
    if "/*GEX*/" not in s: sys.exit("door.html has no /*GEX*/ anchor")
    s2 = re.sub(r"/\*GEX\*/.*?/\*END-GEX\*/", lambda m: "/*GEX*/" + blob + "/*END-GEX*/", s, count=1, flags=re.S)
    open(DOOR, "w", encoding="utf-8").write(s2)
    print("%d generic examples, %d photos, %d countries priced; GEX block %d bytes" % (len(ex), 5*len(ex), len(ex[0]["price"]), len(blob)))
if __name__ == "__main__": main()
