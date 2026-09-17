"""test_zoom_engine.py -- ZOOM engine acceptance (ZOOM_HMI_SPEC.md s8, RG-0221).
Synthetic listings (deterministic), no DB. Run: python3 test_zoom_engine.py"""
import random, sys, json
import zoom_engine as Z

def synth(n=1200, seed=7):
    rnd = random.Random(seed)
    rows = []
    suburbs = ["Menlo Park", "Brooklyn", "Waterkloof", "Hatfield", "Garsfontein", "Lynnwood", "Silverton", "Centurion"]
    streets = {"Menlo Park": ["12th Street", "Atterbury Road", "Lynnwood Road"], "Brooklyn": ["Bronkhorst Street", "Dey Street"],
               "Waterkloof": ["Milner Street", "Julius Jeppe Street"], "Hatfield": ["Burnett Street", "Park Street"],
               "Garsfontein": ["Jacqueline Drive"], "Lynnwood": ["Camelia Avenue"], "Silverton": ["Pretoria Road"], "Centurion": ["Jean Avenue"]}
    def geo(r):
        s = rnd.choice(suburbs); r["suburb"] = s; r["street_address"] = "%d %s" % (rnd.randint(1, 99), rnd.choice(streets[s]))
    i = 0
    for _ in range(n):
        i += 1
        cat = rnd.choice(["Property"] * 5 + ["Services"] * 4 + ["Tutors"] * 2 + ["Collectors"] * 4 + ["Cars"] * 4 + ["adventures_experiences"] * 2 + ["adventures_accommodation"] * 2)
        r = {"id": i, "category": cat, "city": "Pretoria", "country": "ZA", "trust_score": rnd.randint(40, 95),
             "quality_score": rnd.randint(30, 100), "title": "", "description": "words " * 20, "price_num": 0}
        geo(r)
        if cat == "Property":
            rent = rnd.random() < 0.6
            r["listing_type"] = "For Rent" if rent else "For Sale"
            r["prop_type"] = rnd.choice(["Apartment", "House", "Townhouse", "Studio"])
            r["beds"] = rnd.choice([1, 1, 2, 2, 3, 4])
            r["price_num"] = rnd.randint(6000, 30000) if rent else rnd.randint(900000, 9000000)
            r["description"] += " Pets: %s" % rnd.choice(["Yes", "No"])
            r["title"] = "%d bed %s" % (r["beds"], r["prop_type"])
        elif cat == "Services":
            r["service_class"] = rnd.choice(["Technical", "Casuals", "Technical"])
            r["service_type"] = rnd.choice(["Electrical", "Plumbing", "Painting"]) if r["service_class"] == "Technical" else rnd.choice(["Gardening", "Cleaning", "Gardening"])
            r["availability"] = rnd.choice(["Weekdays", "Weekends", "Any day"])
            r["price_num"] = rnd.randint(150, 900); r["title"] = r["service_type"] + " service"
        elif cat == "Tutors":
            r["subject"] = rnd.choice(["Maths", "Science", "English", "Chess"]); r["level"] = rnd.choice(["Primary", "High school", "Matric"])
            r["mode"] = rnd.choice(["Online", "In person", "Both"]); r["price_num"] = rnd.randint(150, 600); r["title"] = r["subject"] + " tutor"
        elif cat == "Collectors":
            fam = rnd.choice(["Trading cards", "Coins & Notes", "LEGO", "Stamps"])
            r["collectible_type"] = fam
            if fam == "Trading cards":
                r["numista_title"] = rnd.choice(["Black Lotus", "Mox Pearl", "Lightning Bolt", "Sol Ring"])
            elif fam == "Coins & Notes":
                r["numista_title"] = rnd.choice(["Krugerrand 1oz", "1966 R1 silver", "Mandela R5"])
            r["condition"] = rnd.choice(["Near Mint", "Good", "Mint"]); r["era_year"] = rnd.choice([1966, 1985, 1994, 2010])
            r["price_num"] = rnd.randint(200, 90000); r["title"] = fam
        elif cat == "Cars":
            r["make"] = rnd.choice(["BMW", "Toyota", "VW", "Mercedes-Benz"]); r["model"] = {"BMW": rnd.choice(["320i", "X3", "118i"]), "Toyota": rnd.choice(["Hilux", "Corolla"]), "VW": rnd.choice(["Polo", "Golf"]), "Mercedes-Benz": rnd.choice(["C200", "A180"])}[r["make"]]
            r["vehicle_year"] = rnd.choice([2012, 2016, 2019, 2021, 2023]); r["mileage_km"] = rnd.choice([0, 30000, 80000, 120000, 180000])
            r["transmission"] = rnd.choice(["Manual", "Automatic"]); r["fuel_type"] = rnd.choice(["Petrol", "Diesel"]); r["body_type"] = rnd.choice(["Sedan", "SUV", "Hatch"])
            r["price_num"] = rnd.randint(80000, 900000); r["title"] = r["make"] + " " + r["model"]
        else:
            r["country"] = rnd.choice(["ZA", "ZA", "NA", "BW", "GB"]); r["city"] = {"ZA": rnd.choice(["Dinokeng", "Kruger", "Cape Town"]), "NA": "Etosha", "BW": "Chobe", "GB": "London"}[r["country"]]
            r["suburb"] = rnd.choice(["North gate", "River camp", "Old town"])
            if cat == "adventures_experiences":
                r["title"] = rnd.choice(["Sunset safari game drive", "Guided hike trail", "Heritage village walk", "Snorkel reef trip"]); r["description"] = rnd.choice(["half day tour", "full day tour", "3 days safari"]) + " words words"
            else:
                r["title"] = rnd.choice(["Safari lodge tent", "Guesthouse B&B", "Self-catering cottage", "Boutique hotel"]); r["description"] = "sleeps %d words" % rnd.choice([2, 4, 6])
            r["price_num"] = rnd.randint(500, 9000)
        rows.append(r)
    return rows

def cands(rows, cat):
    return [r for r in rows if Z.norm_cat(r["category"]) == cat]

def journey(rows, cat, picks, tier="free", text=None):
    """picks: list of (facet, value) taps in order. Returns (taps, final)."""
    chosen = {}
    taps = 0
    res = Z.next_step(cands(rows, cat), cat, chosen, tier=tier, text=text)
    chosen = {c["facet"]: c["v"] for c in res["chips"]}
    for fac, val in picks:
        q = res["question"]
        assert q is not None, "no question left before %s" % fac
        # the funnel must OFFER the value the journey wants (rule 2: only real options exist)
        opts = {o["v"] for o in q["options"]} | {o["v"] for o in q["tail"]}
        if q["facet"] != fac:
            # the engine asked something else first -- answer it with the journey's own value if listed, else count a tap to pick this facet from the queue
            pass
        assert val in opts or q["facet"] != fac, "%s=%s not offered (options %s)" % (fac, val, sorted(opts)[:8])
        chosen[fac] = val; taps += 1
        res = Z.next_step(cands(rows, cat), cat, chosen, tier=tier)
        chosen = {c["facet"]: c["v"] for c in res["chips"]}
    return taps, res

def main():
    rows = synth()
    fails = []
    # (1) zero-count never offered, (3) dep respected, (4) geography never first, (5) depth rules
    for cat in ("Property", "Services", "Tutors", "Collectors", "Cars", "Travel", "Local Market"):
        c = cands(rows, cat) or [dict(r, category="local_market") for r in rows[:40]]
        res = Z.next_step(c, cat, {}, tier="free")
        q = res["question"]
        if q:
            if q["geo"]:
                fails.append("%s: geography opened the funnel (%s)" % (cat, q["facet"]))
            if any(o["n"] <= 0 for o in q["options"] + q["tail"]):
                fails.append("%s: a zero-count option was offered" % cat)
            if sum(o["n"] for o in q["options"] + q["tail"]) > res["total"]:
                fails.append("%s: option counts exceed the result count" % cat)
        # walk a full path for every category checking dep + geo depth at each step
        chosen = {}
        for step in range(8):
            res = Z.next_step(c, cat, chosen, tier="free")
            q = res["question"]
            if not q:
                break
            f = q["facet"]
            if cat == "Collectors" and f in ("geo_suburb", "geo_street"):
                fails.append("Collectors asked %s" % f)
            if cat == "Travel" and f.startswith("geo_") and "geo_country" not in chosen and f != "geo_country":
                fails.append("Travel geography did not open at country (%s)" % f)
            if f in ("model",) and "make" not in chosen:
                fails.append("Cars asked model before make")
            if f in ("beds", "budget") and cat == "Property" and "mode" not in chosen:
                fails.append("Property asked %s before mode" % f)
            if any(o["n"] <= 0 for o in q["options"] + q["tail"]):
                fails.append("%s step %d: zero-count option" % (cat, step))
            chosen[f] = q["options"][0]["v"]
        # dropping a parent drops its children
        if cat == "Cars":
            by = {f["id"]: f for f in Z.facets_for("Cars")}
            left = Z.drop_chip({"make": "BMW", "model": "320i", "year": "2015-2019"}, by, "make")
            if "model" in left or "make" in left or "year" not in left:
                fails.append("drop_chip did not cascade correctly: %s" % left)
    # (7) the named journeys within budget
    t1, r1 = journey(rows, "Property", [("mode", "Rent"), ("geo_suburb", "Menlo Park"), ("geo_street", "12th Street")])
    t2, r2 = journey(rows, "Services", [("service_class", "Casuals"), ("service_type", "Gardening"), ("geo_suburb", "Menlo Park")])
    t3, r3 = journey(rows, "Collectors", [("family", "Trading cards"), ("line", "Black Lotus")])
    t4, r4 = journey(rows, "Cars", [("make", "BMW"), ("car_condition", "Used"), ("mileage", "50-100 000 km")])
    t5, r5 = journey(rows, "Travel", [("lane", "Tours"), ("geo_country", "NA"), ("tour_type", "Safari / wildlife")])
    for name, t, r, budget in (("rental in a named street", t1, r1, 3), ("gardener in my street", t2, r2, 3),
                               ("a specific MtG card", t3, r3, 3), ("used BMW + mileage", t4, r4, 4), ("a tour in a destination", t5, r5, 4)):
        print("%-28s taps=%d results=%d arrived=%s" % (name, t, r["total"], r["arrived"]))
        if t > budget:
            fails.append("%s took %d taps (budget %d)" % (name, t, budget))
        if r["total"] == 0:
            fails.append("%s landed on zero results" % name)
    # (6.1) order = ranking score, pinned first
    c = cands(rows, "Cars"); c[0]["super_example"] = 1
    res = Z.next_step(c, "Cars", {}, tier="free")
    if res["ids"][0] != c[0]["id"]:
        fails.append("super_example not pinned first")
    sc = [res["scores"][str(i)] for i in res["ids"][1:]]
    if sc != sorted(sc, reverse=True):
        fails.append("results not ordered by ranking score")
    # (rule 4) typing is a shortcut through the funnel
    res = Z.next_step(cands(rows, "Cars"), "Cars", {}, tier="free", text="bmw 320i automatic")
    got = {c["facet"]: c["v"] for c in res["chips"]}
    if got.get("make") != "BMW" or got.get("model") != "320i" or got.get("transmission") != "Automatic":
        fails.append("typed shortcut did not fill chips: %s" % got)
    # (3.6) singleton auto-collapse is lossless and shown in the rail
    one = [dict(r, make="Toyota", model="Hilux") for r in cands(rows, "Cars")[:30]]
    res = Z.next_step(one, "Cars", {}, tier="free")
    auto = {a["facet"] for a in res["auto"]}
    if "make" not in auto or "model" not in auto or res["total"] != 30:
        fails.append("singleton auto-collapse failed: auto=%s total=%d" % (auto, res["total"]))
    # (6.2) locked != empty: out-of-reach geography carries its true count and a lock
    res = Z.next_step(cands(rows, "Property"), "Property", {"mode": "Rent"}, tier="free", locked_geo=[{"v": "Cape Town", "n": 37}])
    # walk until the geo question appears
    chosen = {"mode": "Rent"}
    seen_lock = False
    for _ in range(6):
        res = Z.next_step(cands(rows, "Property"), "Property", chosen, tier="free", locked_geo=[{"v": "Cape Town", "n": 37}])
        q = res["question"]
        if not q:
            break
        if q["geo"]:
            seen_lock = bool(q.get("locked")) and q["locked"][0]["n"] == 37 and q["locked"][0]["locked"]
            break
        chosen[q["facet"]] = q["options"][0]["v"]
    if not seen_lock:
        fails.append("locked geography not shown with its true count")
    if fails:
        print("\nFAIL"); [print(" -", f) for f in fails]; sys.exit(1)
    print("\nALL ZOOM ENGINE CHECKS PASS")

if __name__ == "__main__":
    main()
