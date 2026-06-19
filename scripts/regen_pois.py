#!/usr/bin/env python3
"""regen_pois.py — THE canonical generator for demo property `nearby_pois`.

WHY THIS EXISTS / HARD RULE
  Demo property amenities must NEVER be hand-edited. They were once hand-seeded with
  fabricated distances, which let one city's POIs leak onto a listing 100km away (the
  Bela-Bela farm showing Pretoria schools — POI-CONTAM-18JUN). The only correct source
  of truth is real geography. This script regenerates `nearby_pois` for every demo
  property by querying OpenStreetMap (Overpass) against each listing's real
  listing_lat/listing_lng — the SAME pipeline the BEA uses for live listings
  (bea_main.py _overpass_query_pois). $0, no API key, public mirrors.

  To change demo amenities: run THIS script. Do not type POIs by hand.

OUTPUT SHAPE
  Each POI keeps {name, dist_km, type?, lat, lon}. lat/lon are RETAINED so the
  regression guard (scripts/validate_demo_pois.py) can recompute the true distance and
  catch any wrong entry — not just gross >16km impossibilities. The FEA ignores lat/lon
  (renders name/type/dist_km only), so this is invisible to users.

USAGE
  python3 scripts/regen_pois.py                 # all demo properties (slow; run in batches if timing out)
  python3 scripts/regen_pois.py <id> [<id>...]  # only these listing ids (timeout-safe; saves after each)
"""
import json, math, time, urllib.request, urllib.parse, sys, os

HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH=os.path.join(HERE,'demo_listings.json')

_POI_CATEGORIES = {
    "schools":      [("amenity","school"),("amenity","college")],
    "universities": [("amenity","university")],
    "shopping":     [("shop","supermarket"),("shop","grocery"),("shop","convenience"),("shop","mall"),("amenity","marketplace")],
    "hospitals":    [("amenity","hospital")],
    "police":       [("amenity","police")],
}
_R=15000; _SHOP_R=3000
_GENERIC={'school','school ground','college','university','hospital','police','police station','bus stop','park','shopping mall'}
MIRRORS=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter','https://overpass.openstreetmap.fr/api/interpreter']

def hav(a,b,c,d):
    R=6371.0; dlat=math.radians(c-a); dlon=math.radians(d-b)
    x=math.sin(dlat/2)**2+math.cos(math.radians(a))*math.cos(math.radians(c))*math.sin(dlon/2)**2
    return round(R*2*math.asin(math.sqrt(x)),2)

def query(lat,lon):
    parts=[]
    for cat,tags in _POI_CATEGORIES.items():
        r=_SHOP_R if cat=='shopping' else _R
        for k,v in tags:
            parts.append(f'node["{k}"="{v}"](around:{r},{lat},{lon});')
            parts.append(f'way["{k}"="{v}"](around:{r},{lat},{lon});')
    q='[out:json][timeout:20];(\n'+'\n'.join(parts)+'\n);out center 80;'
    for url in MIRRORS:
        try:
            data=urllib.parse.urlencode({'data':q}).encode()
            req=urllib.request.Request(url,data=data,headers={'User-Agent':'TrustSquare/1.0 (contact@trustsquare.co)','Content-Type':'application/x-www-form-urlencoded'})
            with urllib.request.urlopen(req,timeout=18) as resp:
                return json.load(resp)
        except Exception:
            continue
    return None

def categorise(result, lat, lon):
    cr={k:[] for k in _POI_CATEGORIES}
    for el in result.get('elements',[]):
        t=el.get('tags',{}); name=t.get('name') or t.get('name:en')
        if not name or name.lower().strip() in _GENERIC: continue
        if el.get('type')=='node': elat,elon=el.get('lat'),el.get('lon')
        else: c=el.get('center',{}); elat,elon=c.get('lat'),c.get('lon')
        if not elat or not elon: continue
        dist=hav(lat,lon,elat,elon); am=t.get('amenity',''); shop=t.get('shop','')
        rec={'name':name,'dist_km':dist,'lat':round(elat,5),'lon':round(elon,5)}
        if am in ('school','college'):
            nl=name.lower(); isced=t.get('isced:level',''); lvl=''
            if 'primary' in nl or 'laerskool' in nl or 'primary' in isced: lvl='Primary'
            elif any(w in nl for w in ['high','secondary','hoërskool','hoerskool','college']): lvl='Secondary'
            if lvl: rec['type']=lvl
            cr['schools'].append(rec)
        elif am=='university': cr['universities'].append(rec)
        elif shop in ('mall','supermarket','grocery','convenience') or am=='marketplace': cr['shopping'].append(rec)
        elif am=='hospital': cr['hospitals'].append(rec)
        elif am=='police': cr['police'].append(rec)
    def dedup(items):
        seen=[]
        for it in items:
            if not any(hav(it['lat'],it['lon'],s['lat'],s['lon'])<0.2 for s in seen): seen.append(it)
        return seen
    out={}
    for cat in cr:
        cr[cat].sort(key=lambda x:x['dist_km'])
        kept=dedup(cr[cat])[:5]
        if kept: out[cat]=kept   # KEEP lat/lon (guard needs them; FEA ignores them)
    return out

def main():
    ids=set(sys.argv[1:])
    data=json.load(open(PATH,encoding='utf-8')); L=data['listings']
    props=[l for l in L if (l.get('cat') or '').lower()=='property' and l.get('id')!='ph_property']
    batch=[l for l in props if (not ids or l['id'] in ids)]
    for l in batch:
        lat,lon=l.get('listing_lat'),l.get('listing_lng')
        if not lat or not lon: continue
        res=query(lat,lon)
        if not res:
            print(l['id'],'FAIL (all mirrors)'); sys.stdout.flush(); continue
        l['nearby_pois']=categorise(res,lat,lon)
        json.dump(data,open(PATH,'w',encoding='utf-8'),ensure_ascii=False,indent=1)  # save after each (timeout-safe)
        print(l['id'],'OK',{k:len(v) for k,v in l['nearby_pois'].items()}); sys.stdout.flush()
        time.sleep(0.4)

if __name__=='__main__':
    main()
