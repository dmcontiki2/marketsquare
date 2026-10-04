#!/usr/bin/env python3
"""FIND-BANDS-1 (David 4 Oct 2026, after FIND-HONOUR-1 shipped): "Let us then stick to our set up rule with these new
fixes" -- RUL-118 stands: the shelf starts in HER area and fills local-first, from the rest of her city, labelled as bands,
RS -> TS -> LS inside each band. So the area answer is no longer a gate (RUL-200(c) withdrawn) but the first band; every
other answer (to buy or to rent, the kind, the price band, the level, the day, the length, the destination) stays a gate
-- a townhouse to sell still never shows under Renting. 'Yes -- N on TrustSquare' counts only adverts in her area; when
her area has none and the city has, the head says 'Yes -- N near you' and the cards sit under a 'Nearby' label.
Idempotent; asserts every anchor. Then run sync_quick_roles.py (the 'Nearby' word) and copy quick.html over HARNESS."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8", newline="").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8", newline="").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
q = rd("quick.html")
q = rep(q, "      if(FIND_TEST[d]) tests.push([FIND_TEST[d], pk]); });\n"
           "    return (list||[]).filter(function(l){ for(var i=0;i<tests.length;i++) if(!tests[i][0](l, tests[i][1], c, A)) return false; return true; });\n  }",
           "      if(FIND_TEST[d]) tests.push([FIND_TEST[d], pk, d]); });\n"
           "    /* FIND-BANDS-1 (RUL-118, David 4 Oct 2026: \"stick to our set up rule with these new fixes\"): the area is the FIRST\n"
           "       BAND, not a gate -- her area, then the rest of her city, labelled. Every other answer stays a gate. RS -> TS -> LS\n"
           "       orders inside each band (RS = 0.5 LS + 0.5 TS, never shown). */\n"
           "    var out=[];\n"
           "    (list||[]).forEach(function(l){ var band=0;\n"
           "      for(var i=0;i<tests.length;i++){ if(tests[i][0](l, tests[i][1], c, A)) continue;\n"
           "        if(tests[i][2]==='area'){ band=1; continue; } return; }\n"
           "      l._band=band; out.push(l); });\n"
           "    var ts=function(l){ return +l.trust_score||0; }, ls=function(l){ return +l.quality_score||0; };\n"
           "    out.sort(function(a,b){ return (a._band-b._band) || ((0.5*ls(b)+0.5*ts(b))-(0.5*ls(a)+0.5*ts(a))) || (ts(b)-ts(a)) || (ls(b)-ls(a)); });\n"
           "    return out;\n  }",
        "bands")
q = rep(q, "      var nEx=five.filter(isEx).length, nReal=five.length-nEx;\n",
           "      var nEx=five.filter(isEx).length, nReal=five.length-nEx;\n"
           "      var n0=five.filter(function(l){ return !isEx(l) && !l._band; }).length, n1=nReal-n0;   /* FIND-BANDS-1 */\n"
           "      var lab=function(l,i){ if(!n1 || isEx(l) || (i>0 && !isEx(five[i-1]) && five[i-1]._band===l._band)) return '';\n"
           "        return '<div class=\"lkband\" style=\"grid-column:1/-1;font:800 11px/1.2 system-ui,sans-serif;letter-spacing:.06em;text-transform:uppercase;opacity:.75;margin:6px 2px -3px\">'\n"
           "          +E(l._band ? T('Nearby') : placeName)+'</div>'; };\n",
        "n0 n1")
q = rep(q, "        return '<div class=\"ad\"'+(l._local?",
           "        return lab(l,i)+'<div class=\"ad\"'+(l._local?",
        "band label")
q = rep(q, "               : (nReal ? T('Yes')+' — '+nReal+' '+T('on TrustSquare') : (nEx ? T('Only examples so far') : T('Not listed yet')));",
           "               : (nReal ? (n0 ? T('Yes')+' — '+n0+' '+T('on TrustSquare') : T('Yes — '+n1+' near you'))   /* FIND-BANDS-1: 'Yes' counts her area only */\n"
           "                        : (nEx ? T('Only examples so far') : T('Not listed yet')));",
        "head")
assert q.rstrip().endswith("</html>"), "TRUNCATED"
wr("quick.html", q)
print("FIND-BANDS-1 applied; %d bytes" % len(q.encode("utf-8")))
