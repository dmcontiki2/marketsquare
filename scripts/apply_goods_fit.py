#!/usr/bin/env python3
"""GOODS-FIT-1 (David 25 Sep 2026: Local Market "Plants" showed a house; "the referral and buzz need to be topic specific
like you fixed this morning, but here also"; "This was a listing to sell a plot, showing a property with a house ... And
then the photo advert ... does not show it as a demo").
 * Every Local Market, Cars and Property kind wears its own picture (15 new, prepaid, RUL-164).
 * The draft (and the arrival card) mark the picture: EXAMPLE PHOTO -- add your own in the app. The picture is never
   sent with the advert; it only illustrates the draft.
 * Reference card: goods sellers are vouched for by people who BOUGHT from them (RUL-169 extended).
 * Buzz card on the seller's draft speaks from the seller's side for Local Market, Cars and Collectables.
 * A plot or a commercial property is not asked for bedrooms; bedrooms read "3 bedrooms"; goods say Price, not Rate.
Idempotent; asserts every anchor."""
import io, os, json
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
q = rd("quick.html")
# reference wording for goods (vouchWho)
q = rep(q, "  if(k==='adventures') return {subj:'A guest you have hosted', demo:'You have stayed with them'};",
           "  if(k==='adventures') return {subj:'A guest you have hosted', demo:'You have stayed with them'};\n"
           "  if(k==='localmarket' || k==='cars') return {subj:'Someone who has bought from you', demo:'You have bought from them'};   /* GOODS-FIT-1 */\n"
           "  if(k==='collectors') return {subj:'A collector you have dealt with', demo:'You have dealt with them'};\n"
           "  if(k==='property') return {subj:'Someone who has rented or bought from you', demo:'You have rented or bought from them'};", "vouchWho goods")
# Buzz seller-side cards
for a, b in (("card:'One line to the people asking about your car - until it is sold.'", "card:'One line to the people asking about your car - until it is sold.',\n    sellCard:'One line to each buyer asking about your car - until it is sold.'"),
             ("card:'One line to the collectors you trade with.'", "card:'One line to the collectors you trade with.',\n    sellCard:'One line to the collectors who buy from you - a new piece, a swap, a price.'"),
             ("card:'One line to your neighbour - at the gate, sold out, bring change.'", "card:'One line to your neighbour - at the gate, sold out, bring change.',\n    sellCard:'One line to the people who buy from you - fresh today, sold out, at the gate.'")):
    q = rep(q, a, b, a[:30])
# English advert body: bedrooms + price word
q = rep(q, "             .map(function(p){ return p.label; });\n  if(rest.length) s.push(rest.join(', ')+'.');",
           "             .map(function(p){ return p.key==='beds' ? p.label+' bedrooms' : p.label; });   /* GOODS-FIT-1 */\n  if(rest.length) s.push(rest.join(', ')+'.');", "en beds")
q = rep(q, "  if(price) s.push('Rate: '+priceWithBasis(c.key, price.label)+'.');",
           "  if(price) s.push(({cars:1,collectors:1,localmarket:1,property:1,adventures:1}[c.key]?'Price: ':'Rate: ')+priceWithBasis(c.key, price.label)+'.');", "en price")
q = rep(q, "               .map(function(p){ return T(p.label); });\n    if(rest.length) s.push(rest.join(', ')+'.');",
           "               .map(function(p){ return p.key==='beds' ? T(p.label)+' '+T('bedrooms') : T(p.label); });   /* GOODS-FIT-1 */\n    if(rest.length) s.push(rest.join(', ')+'.');", "lang beds")
q = rep(q, "    if(price) s.push(A.rate+priceWithBasis(c.key, price.label)+'.');",
           "    var PW={en:'Price: ',af:'Prys: ',zu:'Intengo: ',xh:'Ixabiso: ',nso:'Theko: ',st:'Theko: '};   /* GOODS-FIT-1: goods have a price, not a rate */\n"
           "    if(price) s.push(({cars:1,collectors:1,localmarket:1,property:1,adventures:1}[c.key]?(PW[QLANG]||PW.en)+T(priceWithBasis(c.key, price.label)):A.rate+priceWithBasis(c.key, price.label))+'.');", "lang price")
BLOCK = r"""
/* ===========================================================================
   GOODS-FIT-1 (David 25 Sep 2026). Each Local Market, Cars and Property kind wears its own picture; a plot or a
   commercial property is not asked for bedrooms; the draft's picture says it is an EXAMPLE PHOTO.
   ------------------------------------------------------------------------- */
(function(){
  var K={localmarket:{'Plants':'lm_plants','Furniture':'lm_furniture','Clothes':'lm_clothes','Tools':'lm_tools'},
         cars:{'Bakkie':'car_bakkie','Sedan':'car_sedan','SUV':'car_suv','Hatchback':'car_hatch','Double cab':'car_dcab','Bike':'car_bike'},
         property:{'Plot':'prop_plot','Townhouse':'prop_townhouse','Flat':'prop_flat','Farm':'prop_farm','Commercial':'prop_commercial'}};
  Object.keys(K).forEach(function(c){ Object.keys(K[c]).forEach(function(n){ var k=K[c][n]; PH[k]=PH_BASE+k+'.jpg'; }); });
  CATS.forEach(function(c){ var m=K[c.key]; if(!m) return; ['sell','find'].forEach(function(side){ ((c[side]||{}).steps||[]).forEach(function(s){
    if(s.key==='what') (s.tiles||[]).forEach(function(t){ if(m[t.t]) t.p=m[t.t]; }); }); }); });
  var _flG=flow;
  flow=function(){ var f=_flG(); if(!f || !f.steps || cat().key!=='property') return f;
    var w=pickOf('what'); if(!w || !/^(Plot|Commercial)$/.test(w.label)) return f;
    return {steps:f.steps.filter(function(s){ return !s || s.key!=='beds'; })}; };
  function mark(root){ try{ (root||document).querySelectorAll('.card img.hero, .ar-card > img').forEach(function(im){
      var p=im.parentNode; if(!p || p.querySelector('.exphoto')) return; if(getComputedStyle(p).position==='static') p.style.position='relative';
      var b=document.createElement('div'); b.className='exphoto'; b.textContent='EXAMPLE PHOTO — add your own in the app';
      p.insertBefore(b, im.nextSibling); try{ qTranslate(b); }catch(e){} }); }catch(e){} }
  var st=document.createElement('style');
  st.textContent='.exphoto{position:absolute;top:10px;left:10px;z-index:4;background:rgba(0,0,0,.72);color:#fff;font:800 10px/1.2 system-ui,sans-serif;letter-spacing:.04em;padding:5px 9px;border-radius:8px;max-width:80%}';
  document.head.appendChild(st);
  var _ddG=drawDraft; drawDraft=function(){ _ddG.apply(this, arguments); mark($('screen')); };
  try{ new MutationObserver(function(ms){ ms.forEach(function(m){ m.addedNodes.forEach(function(n){ if(n.id==='arrive') setTimeout(function(){ mark(n); },50); }); }); })
        .observe($('app'), {childList:true}); }catch(e){}
})();
"""
if "GOODS-FIT-1 (David 25 Sep 2026). Each Local Market" not in q:
    q = rep(q, "\ndrawDoor();\n</script>", BLOCK + "\ndrawDoor();\n</script>", "tail")
wr("quick.html", q)
f = "roles/quick_i18n.json"; d = json.loads(rd(f))
W = {"Someone who has bought from you says": ["Iemand wat al by jou gekoop het sê","Umuntu osake wathenga kuwe uthi","Motho ya kileng a reka ho wena o re","Umntu owakhe wathenga kuwe uthi","Motho yo a kilego a reka go wena o re"],
     "A collector you have dealt with says": ["'n Versamelaar met wie jy al te doen gehad het sê","Umqoqi osake wasebenzisana naye uthi","Mmokedi eo o kileng wa sebetsa le yena o re","Umqokeleli owakhe wasebenzisana naye uthi","Mokgobokedi yo o kilego wa šoma le yena o re"],
     "Someone who has rented or bought from you says": ["Iemand wat al by jou gehuur of gekoop het sê","Umuntu osake waqasha noma wathenga kuwe uthi","Motho ya kileng a hira kapa a reka ho wena o re","Umntu owakhe waqesha okanye wathenga kuwe uthi","Motho yo a kilego a hira goba a reka go wena o re"],
     "One line to each buyer asking about your car - until it is sold.": ["Een reël na elke koper wat oor jou motor vra - totdat dit verkoop is.","","","",""],
     "One line to the collectors who buy from you - a new piece, a swap, a price.": ["Een reël na die versamelaars wat by jou koop - 'n nuwe stuk, 'n ruil, 'n prys.","","","",""],
     "One line to the people who buy from you - fresh today, sold out, at the gate.": ["Een reël na die mense wat by jou koop - vars vandag, uitverkoop, by die hek.","","","",""],
     "One tap on your phone buzzes your employer, with your name on it.": ["Een tik op jou foon buzz jou werkgewer, met jou naam daarop.","","","",""],
     "EXAMPLE PHOTO — add your own in the app": ["VOORBEELDFOTO — voeg jou eie in die app by","ISITHOMBE SESIBONELO — engeza esakho ku-app","SETSHWANTSHO SA MOHLALA — kenya sa hao ho app","UMFANEKISO WOMZEKELO — yongeza owakho kwi-app","SEHLAKANGWA SA MOHLALA — tsenya sa gago ka go app"],
     "bedrooms": ["slaapkamers","amakamelo okulala","dikamore tsa ho robala","amagumbi okulala","diphapoši tša go robala"]}
for k, v in W.items(): d["w"].setdefault(k, v)
wr(f, json.dumps(d, ensure_ascii=False, indent=1))
print("GOODS-FIT-1 applied")
