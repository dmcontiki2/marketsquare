#!/usr/bin/env python3
"""GEO-LAUNCH-1 (2 Sep 2026) -- generate scripts/geo_launch_cities.json from
CityLauncher/data/cities.json, the ONE source of truth for which cities we are
recruiting in (the outreach waves). The app's location picker (geo_* tables on the
server) had drifted from it: Denver, Colorado and five African/German demo
countries showed, Mossel Bay and Knysna (already emailed) did not.

Rule: a city is SHOWN in the picker when cities.json has it as `active` or
`prospect` (emailing started or armed). `planned` stays hidden until its wave
arms. Any city that carries real listings is ALSO kept visible -- that leg lives
in seed_geo_launch.py on the server, where the listings are.

Run:  python3 scripts/build_geo_launch_cities.py        (writes the JSON, prints diff)
The regression ledger (RG-0243) re-runs this in check mode every session, so a
wave that arms a city in cities.json and forgets to regenerate goes red.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(REPO), "CityLauncher", "data", "cities.json")
OUT = os.path.join(HERE, "geo_launch_cities.json")

SHOW_STATUSES = {"active", "prospect"}

# cities.json uses "UK"; the geo tables and EULA use ISO "GB".
ISO_FIX = {"UK": "GB"}
COUNTRY = {  # iso2 -> (name, region_label)
    "ZA": ("South Africa", "Province"), "US": ("United States", "State"),
    "GB": ("United Kingdom", "Region"), "AU": ("Australia", "State"),
    "NZ": ("New Zealand", "Region"), "NA": ("Namibia", "Region"),
    "AR": ("Argentina", "Province"), "FR": ("France", "Region"),
    "PT": ("Portugal", "District"),
}
# outreach name -> name as the geo seed spelt it (GeoNames ZA dump)
ALIAS = {"Port Elizabeth": "Gqeberha (Port Elizabeth)", "Nelspruit": "Mbombela (Nelspruit)"}
# region + coords for every city the waves can arm. Missing here = build fails loudly.
GEO = {
 ("ZA","Pretoria"):("Gauteng",-25.7479,28.2293), ("ZA","Johannesburg"):("Gauteng",-26.2041,28.0473),
 ("ZA","Cape Town"):("Western Cape",-33.9249,18.4241), ("ZA","Durban"):("KwaZulu-Natal",-29.8587,31.0218),
 ("ZA","Port Elizabeth"):("Eastern Cape",-33.9608,25.6022), ("ZA","Bloemfontein"):("Free State",-29.0852,26.1596),
 ("ZA","East London"):("Eastern Cape",-33.0153,27.9116), ("ZA","Polokwane"):("Limpopo",-23.9045,29.4689),
 ("ZA","Nelspruit"):("Mpumalanga",-25.4753,30.9694), ("ZA","Kimberley"):("Northern Cape",-28.7282,24.7499),
 ("ZA","Pietermaritzburg"):("KwaZulu-Natal",-29.6006,30.3794), ("ZA","Mossel Bay"):("Western Cape",-34.1831,22.1460),
 ("ZA","George"):("Western Cape",-33.9630,22.4617), ("ZA","Knysna"):("Western Cape",-34.0363,23.0471),
 ("US","New York"):("New York",40.7128,-74.0060), ("US","Los Angeles"):("California",34.0522,-118.2437),
 ("US","Chicago"):("Illinois",41.8781,-87.6298), ("US","Houston"):("Texas",29.7604,-95.3698),
 ("US","Phoenix"):("Arizona",33.4484,-112.0740), ("US","Philadelphia"):("Pennsylvania",39.9526,-75.1652),
 ("US","San Antonio"):("Texas",29.4241,-98.4936), ("US","San Diego"):("California",32.7157,-117.1611),
 ("US","Dallas"):("Texas",32.7767,-96.7970), ("US","San Jose"):("California",37.3382,-121.8863),
 ("US","Austin"):("Texas",30.2672,-97.7431), ("US","Denver"):("Colorado",39.7392,-104.9903),
 ("GB","London"):("England",51.5074,-0.1278), ("GB","Manchester"):("England",53.4808,-2.2426),
 ("GB","Birmingham"):("England",52.4862,-1.8904), ("GB","Leeds"):("England",53.8008,-1.5491),
 ("GB","Glasgow"):("Scotland",55.8642,-4.2518), ("GB","Sheffield"):("England",53.3811,-1.4701),
 ("GB","Edinburgh"):("Scotland",55.9533,-3.1883), ("GB","Liverpool"):("England",53.4084,-2.9916),
 ("GB","Bristol"):("England",51.4545,-2.5879), ("GB","Cardiff"):("Wales",51.4816,-3.1791),
 ("GB","Leicester"):("England",52.6369,-1.1398),
 ("AU","Sydney"):("New South Wales",-33.8688,151.2093), ("AU","Melbourne"):("Victoria",-37.8136,144.9631),
 ("AU","Brisbane"):("Queensland",-27.4698,153.0251), ("AU","Perth"):("Western Australia",-31.9505,115.8605),
 ("AU","Adelaide"):("South Australia",-34.9285,138.6007), ("AU","Canberra"):("Australian Capital Territory",-35.2809,149.1300),
 ("NZ","Auckland"):("Auckland",-36.8485,174.7633), ("NZ","Wellington"):("Wellington",-41.2865,174.7762),
 ("NZ","Christchurch"):("Canterbury",-43.5321,172.6362),
 ("NA","Windhoek"):("Khomas",-22.5609,17.0658), ("NA","Swakopmund"):("Erongo",-22.6784,14.5258),
 ("AR","Buenos Aires"):("Buenos Aires",-34.6037,-58.3816), ("AR","Cordoba"):("Cordoba",-31.4201,-64.1888),
 ("FR","Paris"):("Ile-de-France",48.8566,2.3522), ("FR","Lyon"):("Auvergne-Rhone-Alpes",45.7640,4.8357),
 ("FR","Marseille"):("Provence-Alpes-Cote d'Azur",43.2965,5.3698),
 ("PT","Lisbon"):("Lisbon",38.7223,-9.1393), ("PT","Porto"):("Porto",41.1579,-8.6291),
}

def build():
    cities = json.load(open(SRC, encoding="utf-8"))
    out, missing = [], []
    for c in cities:
        if c.get("status") not in SHOW_STATUSES:
            continue
        iso = ISO_FIX.get(c["country"], c["country"])
        key = (iso, c["name"])
        if key not in GEO:
            missing.append(key); continue
        region, lat, lng = GEO[key]
        cname, rlabel = COUNTRY.get(iso, (iso, "Region"))
        out.append({"iso2": iso, "country": cname, "region_label": rlabel, "region": region,
                    "name": ALIAS.get(c["name"], c["name"]), "lat": lat, "lng": lng,
                    "status": c["status"], "wave": c.get("wave")})
    if missing:
        sys.exit("build_geo_launch_cities: no region/coords for %s -- add to GEO" % missing)
    out.sort(key=lambda x: (x["iso2"], x["region"], x["name"]))
    return {"generated_from": "CityLauncher/data/cities.json", "rule": "status in active|prospect",
            "cities": out}

def main():
    doc = build()
    check = "--check" in sys.argv
    new = json.dumps(doc, indent=1, ensure_ascii=False) + "\n"
    old = open(OUT, encoding="utf-8").read() if os.path.exists(OUT) else ""
    if check:
        if old != new:
            print("STALE: scripts/geo_launch_cities.json differs from cities.json -- run build_geo_launch_cities.py")
            sys.exit(1)
        print("geo_launch_cities.json is current (%d cities)" % len(doc["cities"])); return
    open(OUT, "w", encoding="utf-8", newline="\n").write(new)
    by = {}
    for c in doc["cities"]: by.setdefault(c["iso2"], []).append(c["name"])
    for k, v in sorted(by.items()): print(k, len(v), ", ".join(v))
    print("wrote", OUT, "(%s)" % ("changed" if old != new else "unchanged"))

if __name__ == "__main__":
    main()
