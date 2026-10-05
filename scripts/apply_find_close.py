#!/usr/bin/env python3
"""apply_find_close.py -- FIND-CLOSE-1 + HOUSE-WIDE-1 (5 Oct 2026, RUL-207).

Dave jnr (5 Oct): he followed the e-mail link, searched Quick for his own townhouse in Rietvalleirand under
Properties -> Buy -> 'House', and found only AI examples. David: "if he battled then a new guy will surely also not
see the adverts?" -- and chose BOTH fixes:
  HOUSE-WIDE-1  'House' also finds townhouses, clusters, duplexes and simplexes (a townhouse is a house to a buyer);
  FIND-CLOSE-1  a search that would show only AI examples first shows the REAL adverts that miss by exactly one
                answer, under 'Close matches', each saying what differs (e.g. 'Close match - Townhouse').
Idempotent. quick.html and genie/HARNESS.html stay identical."""
import io, sys
P = ["quick.html", "genie/HARNESS.html"]
R = [
 # HOUSE-WIDE-1
 ("""      var st=ptOf(String(l.prop_type||'')); if(!st.length) st=ptOf(String(l.title||''));
      return !st.length || st.indexOf(i)>=0; },""",
  """      var st=ptOf(String(l.prop_type||'')); if(!st.length) st=ptOf(String(l.title||''));
      /* HOUSE-WIDE-1 (RUL-207(a)): 'House' also finds townhouses, clusters, duplexes, simplexes -- Dave jnr's townhouse */
      return !st.length || st.indexOf(i)>=0 || (i===0 && st.indexOf(2)>=0); },"""),
 # FIND-CLOSE-1: honour keeps the one-answer misses
 ("""    var out=[];
    (list||[]).forEach(function(l){ var band=0;
      for(var i=0;i<tests.length;i++){ if(tests[i][0](l, tests[i][1], c, A)) continue;
        if(tests[i][2]==='area'){ band=1; continue; } return; }
      l._band=band; out.push(l); });
    var ts=function(l){ return +l.trust_score||0; }, ls=function(l){ return +l.quality_score||0; };
    out.sort(function(a,b){ return (a._band-b._band) || ((0.5*ls(b)+0.5*ts(b))-(0.5*ls(a)+0.5*ts(a))) || (ts(b)-ts(a)) || (ls(b)-ls(a)); });
    return out;""",
  """    /* FIND-CLOSE-1 (RUL-207(b)): an advert that misses by exactly ONE answer (the area is a band, not a miss) is kept
       aside as a close match, with what differs -- shown only when nothing fits exactly, before any AI example. */
    var out=[], close=[];
    (list||[]).forEach(function(l){ var band=0, miss=null, nm=0;
      for(var i=0;i<tests.length;i++){ if(tests[i][0](l, tests[i][1], c, A)) continue;
        if(tests[i][2]==='area'){ band=1; continue; } nm++; miss=tests[i]; }
      l._band=band; l._cm=0; l._cmWhat='';
      if(!nm){ out.push(l); return; }
      if(nm===1 && !(l.demo_example || +l.super_example || +l.is_demo)){ l._cm=1; l._cmWhat=qCloseWhat(l, miss[2]); close.push(l); } });
    var ts=function(l){ return +l.trust_score||0; }, ls=function(l){ return +l.quality_score||0; };
    var ord=function(a,b){ return (a._band-b._band) || ((0.5*ls(b)+0.5*ts(b))-(0.5*ls(a)+0.5*ts(a))) || (ts(b)-ts(a)) || (ls(b)-ls(a)); };
    out.sort(ord); close.sort(ord); out._close=close;
    return out;"""),
 ("""  window.qFindHonour=qFindHonour;""",
  """  window.qFindHonour=qFindHonour;
  /* FIND-CLOSE-1: the one thing a close match does differently, in the advert's own words */
  function qCloseWhat(l, d){
    if(d==='prop_type' || d==='kind') return String(l.prop_type||'').trim();
    if(d==='deal'){ var g=qDealOf(l); return g==='rent' ? T('To let') : (g==='sale' ? T('To sell') : ''); }
    if(d==='level') return String(l.level||'').trim();
    return '';
  }"""),
 # paint: close matches before the examples, only when nothing fits exactly
 ("""      var five=_all.filter(function(l){ return !isEx(l); }).concat(exOn?_exAll:[]).slice(0,5);""",
  """      var _exact=_all.filter(function(l){ return !isEx(l); }), _cl=_exact.length ? [] : ((list&&list._close)||[]).slice(0,3);   /* FIND-CLOSE-1 */
      var five=_exact.concat(_cl).concat(exOn?_exAll:[]).slice(0,5);"""),
 ("""      var n0=five.filter(function(l){ return !isEx(l) && !l._band; }).length, n1=nReal-n0;   /* FIND-BANDS-1 */
      var lab=function(l,i){ if(!n1 || isEx(l) || (i>0 && !isEx(five[i-1]) && five[i-1]._band===l._band)) return '';""",
  """      var nCl=five.filter(function(l){ return !isEx(l) && l._cm; }).length;   /* FIND-CLOSE-1 */
      var n0=five.filter(function(l){ return !isEx(l) && !l._band && !l._cm; }).length, n1=nReal-n0-nCl;   /* FIND-BANDS-1 */
      var lab=function(l,i){
        if(l._cm && !isEx(l)){ if(i>0 && five[i-1]._cm) return '';
          return '<div class="lkband" style="grid-column:1/-1;font:800 11px/1.2 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;opacity:.85;margin:6px 2px -3px">'
            +E(T('Close matches'))+'<div style="font:500 12px/1.35 system-ui,sans-serif;letter-spacing:0;text-transform:none;opacity:.85;margin-top:3px">'
            +E(T('Not exactly what you asked \\u2014 the difference is shown on each.'))+'</div></div>'; }
        if(!n1 || isEx(l) || (i>0 && !isEx(five[i-1]) && five[i-1]._band===l._band)) return '';"""),
 ("""(isEx(l)?'<div class="exrib">'+E(T('AI EXAMPLE LISTING'))+'</div>':(own?'':'<div class="exph">'+E(T('EXAMPLE PHOTO'))+'</div>'))""",
  """(isEx(l)?'<div class="exrib">'+E(T('AI EXAMPLE LISTING'))+'</div>':((l._cm?'<div class="exrib" style="background:#B7791F;color:#fff">'+E(T('Close match'))+(l._cmWhat?' \\u00b7 '+E(T(l._cmWhat)):'')+'</div>':'')+(own?'':'<div class="exph">'+E(T('EXAMPLE PHOTO'))+'</div>')))"""),
 ("""               : (nReal ? (n0 ? T('Yes')+' — '+n0+' '+T('on TrustSquare') : T('Yes — '+n1+' near you'))   /* FIND-BANDS-1: 'Yes' counts her area only */""",
  """               : (nReal-nCl ? (n0 ? T('Yes')+' — '+n0+' '+T('on TrustSquare') : T('Yes — '+n1+' near you'))   /* FIND-BANDS-1: 'Yes' counts her area only */
                 : nCl ? T('Close matches')   /* FIND-CLOSE-1 */"""),
 ("""<span>'+E(nEx ? (nReal ? T('real listings and AI examples') : T('AI examples of what a listing looks like')) : T('real listings'))+'</span>""",
  """<span>'+E(nCl ? (nEx ? T('close matches and AI examples') : T('Close matches')) : (nEx ? (nReal ? T('real listings and AI examples') : T('AI examples of what a listing looks like')) : T('real listings')))+'</span>"""),
]
for p in P:
    s = io.open(p, encoding="utf-8", newline="").read()
    if "FIND-CLOSE-1 (RUL-207" in s:
        print(p, "already"); continue
    for a, b in R:
        if s.count(a) != 1:
            sys.exit("%s: anchor not found once (%d): %s" % (p, s.count(a), a[:90]))
        s = s.replace(a, b)
    io.open(p, "w", encoding="utf-8", newline="").write(s); print(p, "ok")
