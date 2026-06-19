#!/usr/bin/env python3
"""validate_demo_pois.py — regression guard against demo POI corruption.

Guards the bug where a listing's `nearby_pois` contained a place from the wrong city
at a fabricated distance (Pretoria schools on the Bela-Bela farm — POI-CONTAM-18JUN).

Because POIs are now generated from OpenStreetMap WITH their real coordinates retained
(scripts/regen_pois.py), this guard can recompute ground truth and verify EVERY entry —
not just gross impossibilities. A POI whose stored coordinates aren't actually near the
listing, or whose stored dist_km disagrees with the true haversine, is flagged.

CHECKS
  A  truth-distance: recompute haversine(listing, poi.lat/lon). Must be within the
     query radius (15km; 16 with slack). A wrong-city POI lands here immediately.
  B  honest-distance: stored dist_km must match the recomputed distance (±0.3km).
     Catches fabricated/typo'd distances even when the named place is plausible.
  C  has-coords: every POI must carry lat/lon (else it's a legacy hand-seed and
     unverifiable — reject so it can't slip past the truth checks).
  D  legacy-shape: no 'transit' key (that category never comes from the OSM pipeline).

Exit 0 = clean, exit 1 = problems (offenders printed). Zero network, zero cost.
"""
import json, math, sys, os

HERE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PATH=os.path.join(HERE,'demo_listings.json')
RADIUS_KM=16.0      # OSM query radius 15km + 1km haversine slack
DIST_TOL_KM=0.35    # stored dist_km vs recomputed truth

def hav(a,b,c,d):
    R=6371.0; p1,p2=math.radians(a),math.radians(c); dp,dl=math.radians(c-a),math.radians(d-b)
    x=math.sin(dp/2)**2+math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return R*2*math.atan2(math.sqrt(x),math.sqrt(1-x))

def main():
    data=json.load(open(PATH,encoding='utf-8')); L=data['listings']
    props=[l for l in L if (l.get('cat') or '').lower()=='property' and l.get('id')!='ph_property']
    fails=[]
    for l in props:
        llat,llon=l.get('listing_lat'),l.get('listing_lng')
        p=l.get('nearby_pois') or {}
        if isinstance(p,str): p=json.loads(p)
        if 'transit' in p:
            fails.append(f"[D legacy-shape] {l['id']} has a 'transit' key (hand-seeded, not OSM)")
        for cat,items in p.items():
            for it in items:
                nm=it.get('name','?')
                if 'lat' not in it or 'lon' not in it:
                    fails.append(f"[C no-coords] {l['id']} {cat} {nm!r} missing lat/lon (unverifiable)")
                    continue
                if not (llat and llon):
                    fails.append(f"[C no-coords] {l['id']} has no listing coords")
                    continue
                true_km=hav(llat,llon,it['lat'],it['lon'])
                if true_km>RADIUS_KM:
                    fails.append(f"[A far-poi] {l['id']} {cat} {nm!r} is {true_km:.1f}km away (> {RADIUS_KM}km) — wrong location")
                stored=it.get('dist_km')
                if stored is not None and abs(stored-true_km)>DIST_TOL_KM:
                    fails.append(f"[B bad-dist] {l['id']} {cat} {nm!r} stored {stored}km but true {true_km:.2f}km")
    if fails:
        print("DEMO-POI VALIDATION: FAIL (%d issue(s))"%len(fails))
        for f in fails[:60]: print("  -",f)
        if len(fails)>60: print("  ... and %d more"%(len(fails)-60))
        return 1
    npoi=sum(len(v) for l in props for v in ((l.get('nearby_pois') or {}) if not isinstance(l.get('nearby_pois'),str) else json.loads(l['nearby_pois'])).values())
    print("DEMO-POI VALIDATION: PASS — %d properties, %d POIs, every coordinate & distance verified."%(len(props),npoi))
    return 0

if __name__=='__main__':
    sys.exit(main())
