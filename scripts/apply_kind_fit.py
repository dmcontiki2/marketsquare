#!/usr/bin/env python3
"""KIND-FIT-1 (David 25 Sep 2026: "it is mostly to add photo generic types with the right categories"; he approved
14 pictures, ~US$0.84 prepaid, RUL-164). Every Quick kind that still wore another kind's picture now wears its own:
Services (Plumber, Handyman, Painter, Pool care), Local Market (Crafts), Tutors (English, Afrikaans, Accounting,
Coding) and Home help (Cleaning, Laundry & ironing, Cooking, Childminding, Office cleaning).
Idempotent; asserts the anchor. Then copy quick.html over genie/HARNESS.html."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
BLOCK = r"""
/* ===========================================================================
   KIND-FIT-1 (David 25 Sep 2026). The last kinds that wore another kind's picture get their own.
   ------------------------------------------------------------------------- */
(function(){
  var K={services:{'Plumber':'svc_plumber','Handyman':'svc_handyman','Painter':'svc_painter','Pool care':'svc_pool'},
         localmarket:{'Crafts':'lm_crafts'},
         tutors:{'English':'tut_english','Afrikaans':'tut_afrikaans','Accounting':'tut_accounting','Coding':'tut_coding'},
         homehelp:{'Cleaning':'hh_cleaning','Laundry & ironing':'hh_laundry','Cooking':'hh_cooking','Childminding':'hh_childminding','Office cleaning':'hh_office'}};
  Object.keys(K).forEach(function(c){ Object.keys(K[c]).forEach(function(n){ var k=K[c][n]; PH[k]=PH_BASE+k+'.jpg'; }); });
  CATS.forEach(function(c){ var m=K[c.key]; if(!m) return; ['sell','find'].forEach(function(side){ ((c[side]||{}).steps||[]).forEach(function(s){
    if(s.key==='what') (s.tiles||[]).forEach(function(t){ if(m[t.t]) t.p=m[t.t]; }); }); }); });
})();
"""
q = rd("quick.html")
if "KIND-FIT-1 (David 25 Sep 2026). The last kinds" not in q:
    a = "\ndrawDoor();\n</script>"; assert q.count(a) == 1, "tail anchor %d" % q.count(a)
    q = q.replace(a, BLOCK + a)
wr("quick.html", q)
print("KIND-FIT-1 applied")
