#!/usr/bin/env python3
"""validate_demo_pois.py — regression guard against the POI cross-city contamination bug.

Root cause it guards: demo property `nearby_pois` were once hand-seeded, and entries
from one city (e.g. Pretoria's Garsfontein schools / St Albans College) leaked onto a
listing 100km away (the Bela-Bela farm) at fabricated <4km distances. POIs are now
regenerated from OpenStreetMap against each listing's REAL coordinates (mirroring the
BEA `_overpass_query_pois` pipeline), so every POI is genuinely near its listing.

This guard re-asserts that invariant so the bug can't silently return:
  CHECK A: no POI may sit further than the query radius from its listing. We can't
           recompute true distance after lat/lon are stripped, so we trust the stored
           dist_km and flag any value beyond the radius (16km guard; shopping uses 3km
           but we allow the global 16 to avoid false positives on dedup edge cases).
  CHECK B: a UNIQUELY-NAMED institution (school/university/hospital/police — i.e. NOT a
           known retail chain) must not appear on two listings that are far enough apart
           that one shared physical site is impossible. Chain retailers are exempt
           (multiple branches are legitimate). This is the check that catches a real
           wrong-city leak (Garsfontein on Bela-Bela) while ignoring "two Shoprites".
  CHECK C: no demo property may carry the legacy hand-seed shape (a 'transit' key) —
           that category never comes from the OSM pipeline, so its presence means an
           un-regenerated, hand-seeded (and therefore suspect) list slipped back in.

Exit 0 = clean; exit 1 = contamination found (prints offenders). Zero network, zero cost.
"""
import json, math, sys, os

HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH=os.path.join(HERE,'demo_listings.json')
RADIUS_KM=16.0   # OSM query radius is 15km; 1km slack for haversine rounding

# Retail/fuel chains legitimately have many branches — same name on far listings is fine.
CHAIN_TOKENS={'shoprite','spar','superspar','pick n pay','woolworths','checkers','shell',
 'engen','bp','sasol','total','caltex','quickshop','smart center','smart centre',
 'tesco','sainsbury','co-op','coop','costcutter','morrisons','waitrose','aldi','lidl','marks & spencer',
 'coles','woolworths metro','ezymart','iga','7-eleven','metro','foodworld','nisa','premier',
 'asda','budgens','londis','spar express','one stop','food lovers','superette','convenience'}

def is_chain(name):
    n=name.lower()
    return any(tok in n for tok in CHAIN_TOKENS)

def hav(a,b,c,d):
    R=6371.0;p1,p2=math.radians(a),math.radians(c);dp,dl=math.radians(c-a),math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(x),math.sqrt(1-x))

def main():
    data=json.load(open(PATH,encoding='utf-8'))
    L=data['listings']
    props=[l for l in L if (l.get('cat') or '').lower()=='property' and l.get('id')!='ph_property']
    coords={l['id']:(l.get('listing_lat'),l.get('listing_lng')) for l in props}
    fails=[]

    # CHECK C: legacy hand-seed shape
    for l in props:
        p=l.get('nearby_pois') or {}
        if isinstance(p,str): p=json.loads(p)
        if 'transit' in p:
            fails.append(f"[C legacy-shape] {l['id']} carries a 'transit' key (hand-seeded, not OSM-regenerated)")

    # CHECK A: distance within radius
    for l in props:
        p=l.get('nearby_pois') or {}
        if isinstance(p,str): p=json.loads(p)
        for cat,items in p.items():
            for it in items:
                if it.get('dist_km',0) > RADIUS_KM:
                    fails.append(f"[A far-poi] {l['id']} {cat} {it['name']!r} at {it['dist_km']}km (> {RADIUS_KM}km)")

    # CHECK B: a unique-named institution shared across impossibly-far listings
    from collections import defaultdict
    name_to=defaultdict(set)
    for l in props:
        p=l.get('nearby_pois') or {}
        if isinstance(p,str): p=json.loads(p)
        for cat,items in p.items():
            if cat=='shopping': continue   # retail: chains exempt by category
            for it in items:
                if is_chain(it['name']): continue
                name_to[(cat,it['name'])].add(l['id'])
    for (cat,name),ids in name_to.items():
        if len(ids)<2: continue
        idl=list(ids); maxd=0
        for i in range(len(idl)):
            for j in range(i+1,len(idl)):
                a,b=coords[idl[i]],coords[idl[j]]
                if all([a[0],a[1],b[0],b[1]]): maxd=max(maxd,hav(a[0],a[1],b[0],b[1]))
        # Geometric bound: both listings can be within the 15km query radius of ONE
        # POI yet be up to ~2x radius (30km) apart. Only flag BEYOND that — a genuine
        # impossibility (e.g. the original Pretoria-school-on-Bela-Bela-farm, ~100km).
        if maxd>31:
            fails.append(f"[B cross-city] {cat} {name!r} on {sorted(ids)} — {maxd:.0f}km apart (one site can't serve both)")

    if fails:
        print("DEMO-POI VALIDATION: FAIL (%d issue(s))"%len(fails))
        for f in fails: print("  -",f)
        return 1
    print("DEMO-POI VALIDATION: PASS — %d property listings, no cross-city POI contamination."%len(props))
    return 0

if __name__=='__main__':
    sys.exit(main())
