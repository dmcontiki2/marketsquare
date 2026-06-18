import json, math, time, urllib.request, urllib.parse, sys

IDS=set(sys.argv[1:])   # process only these listing IDs

_POI_CATEGORIES = {
    "schools":      [("amenity","school"),("amenity","college")],
    "universities": [("amenity","university")],
    "shopping":     [("shop","supermarket"),("shop","grocery"),("shop","convenience"),("shop","mall"),("amenity","marketplace")],
    "hospitals":    [("amenity","hospital")],
    "police":       [("amenity","police")],
}
_R=15000; _SHOP_R=3000
_GENERIC={'school','school ground','college','university','hospital','police','police station','bus stop','park','shopping mall'}
MIRRORS=['https://overpass-api.de/api/interpreter','https://overpass.kumi.systems/api/interpreter']

def hav(a,b,c,d):
    R=6371; dlat=math.radians(c-a); dlon=math.radians(d-b)
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
        except Exception as e:
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
        rec={'name':name,'dist_km':dist,'lat':elat,'lon':elon}
        if am in ('school','college'):
            lvl=''; isced=t.get('isced:level','')
            nl=name.lower()
            if 'primary' in nl or 'laerskool' in nl or 'primary' in isced: lvl='Primary'
            elif any(w in nl for w in ['high','secondary','hoërskool','hoerskool','college']): lvl='Secondary'
            rec['_lvl']=lvl; cr['schools'].append(rec)
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
        kept=dedup(cr[cat])[:5]; final=[]
        for p in kept:
            o={'name':p['name'],'dist_km':p['dist_km']}
            if cat=='schools' and p.get('_lvl'): o['type']=p['_lvl']
            final.append(o)
        if final: out[cat]=final
    return out

data=json.load(open('demo_listings.json'))
L=data['listings']
props=[l for l in L if (l.get('cat') or '').lower()=='property' and l.get('id')!='ph_property']
batch=[l for l in props if l['id'] in IDS]
results=[]
for l in batch:
    lat,lon=l.get('listing_lat'),l.get('listing_lng')
    res=query(lat,lon)
    if not res:
        results.append((l['id'],'FAIL',None)); continue
    pois=categorise(res,lat,lon)
    l['nearby_pois']=pois
    json.dump(data,open('demo_listings.json','w'),ensure_ascii=False,indent=1)  # save after EACH (timeout-safe)
    print(l['id'],'OK',{k:len(v) for k,v in pois.items()}); sys.stdout.flush()
    time.sleep(0.4)
