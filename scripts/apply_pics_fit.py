#!/usr/bin/env python3
"""COL-PICS-1 + DEST-WHERE-1 (David 25 Sep 2026):
 * "I selected 'Cards' here and the generic photos shows coins" -- each Collectables kind now has its own two
   example pictures (assets/quick_ph/col_<kind>_<n>.jpg), and the example adverts use only that kind's pictures.
 * "I selected a Game Lodge, but this screen is showing suburb information? I would expect ... a province, a
   nature reserve, a heritage site" -- the Adventures WHERE step offers destinations that fit the kind of trip,
   each with its own picture (assets/quick_ph/dest_<slug>.jpg). 'Another option' still takes any place typed.
Runtime overrides appended once, marked COL-PICS-1 / DEST-WHERE-1. Idempotent; asserts every anchor."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
q = rd("quick.html")
q = rep(q, "    var pool=[what&&what.photo?what.photo:c._adp[0]].concat(c._adp);",
           "    var pool=[what&&what.photo?what.photo:c._adp[0]].concat(c._adp);\n"
           "    if(what && /^col_[a-z]+_1$/.test(String(what.photo||''))) pool=[what.photo, what.photo.replace(/_1$/,'_2')];   /* COL-PICS-1: only this kind's pictures */",
           "ad pool")
BLOCK = r"""
/* ===========================================================================
   COL-PICS-1 + DEST-WHERE-1 (David 25 Sep 2026). Collectables: each kind wears its own example pictures
   (Cards showed coins). Adventures: WHERE is a destination that fits the trip (a game lodge was offered
   suburbs). Pictures are application pictures (RUL-164); a picture that did not load falls back to a chip.
   ------------------------------------------------------------------------- */
(function(){
  var KIND={Stamps:'stamps',Cards:'cards',Militaria:'militaria',Watches:'watches',Art:'art'};
  Object.keys(KIND).forEach(function(n){ [1,2].forEach(function(i){ var k='col_'+KIND[n]+'_'+i; PH[k]=PH_BASE+k+'.jpg'; }); });
  CATS.forEach(function(c){ if(c.key!=='collectors') return;
    ['sell','find'].forEach(function(side){ ((c[side]||{}).steps||[]).forEach(function(s){
      if(s.key==='what') (s.tiles||[]).forEach(function(t){ if(KIND[t.t]) t.p='col_'+KIND[t.t]+'_1'; }); }); }); });

  var WILD=['Kruger','Pilanesberg','Waterberg','Madikwe','Zululand','Addo'];
  var DEST={'Game lodge':WILD, 'Safari':WILD,
    'Guided tour':['Cape Town','Garden Route','Drakensberg','Cradle of Humankind','Soweto','Mapungubwe'],
    'Self-drive':['Garden Route','Panorama Route','Wild Coast','Karoo','Namaqualand','Drakensberg'],
    'Rail journey':['Cape Town','Victoria Falls','Durban','Karoo','Garden Route','Kruger'],
    'Fishing':['Vaal Dam','Hartbeespoort','Lake Jozini','Sodwana Bay','Wild Coast','Orange River']};
  var MIX=['Kruger','Cape Town','Garden Route','Drakensberg','Pilanesberg','Wild Coast'];
  var SLUG={'Cape Town':'cape_town','Garden Route':'garden_route','Cradle of Humankind':'cradle','Panorama Route':'panorama',
    'Wild Coast':'wild_coast','Victoria Falls':'victoria_falls','Vaal Dam':'vaal_dam','Lake Jozini':'jozini',
    'Sodwana Bay':'sodwana','Orange River':'orange_river'};
  var DEST_PIC={};
  var all={}; Object.keys(DEST).forEach(function(k){ DEST[k].forEach(function(n){ all[n]=1; }); }); MIX.forEach(function(n){ all[n]=1; });
  Object.keys(all).forEach(function(n){ var k='dest_'+(SLUG[n]||n.toLowerCase()); PH[k]=PH_BASE+k+'.jpg';
    var im=new Image(); im.onload=function(){ DEST_PIC[n]=k; }; im.src=PH[k]; });
  window.QUICK_DEST=DEST;
  var _flD=flow;
  flow=function(){
    var f=_flD(); if(!f || !f.steps || cat().key!=='adventures') return f;
    var w=pickOf('what'), list=(w && DEST[w.label]) || MIX;
    return {steps:f.steps.map(function(s){
      if(!s || s.key!=='where') return s;
      var pics=list.every(function(n){ return !!DEST_PIC[n]; });
      return pics ? {q:s.q, key:'where', kind:'tile', free:s.free, freeHint:s.freeHint, tiles:list.map(function(n){ return {t:n, p:DEST_PIC[n]}; })}
                  : {q:s.q, key:'where', kind:'chip', free:s.free, freeHint:s.freeHint, tiles:list.map(function(n){ return {t:n}; })};
    })};
  };
  var _hpD=heroPhoto;   /* a destination picture never becomes the advert's picture */
  heroPhoto=function(){ var h=_hpD(); if(String(h).indexOf('dest_')===0){
      for(var i=picks.length-1;i>=0;i--) if(picks[i].photo && String(picks[i].photo).indexOf('dest_')!==0 && String(picks[i].photo).indexOf('place_')!==0) return picks[i].photo;
      return cat().hero[0]; } return h; };
})();
"""
if "DEST-WHERE-1 (David 25 Sep 2026)" not in q:
    q = rep(q, "\ndrawDoor();\n</script>", BLOCK + "\ndrawDoor();\n</script>", "tail")
wr("quick.html", q)
print("COL-PICS-1 + DEST-WHERE-1 applied")
