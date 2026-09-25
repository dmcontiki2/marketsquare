#!/usr/bin/env python3
"""TRIP-TYPE-1 + DEEPLINK-FETCH-1 (David 25 Sep 2026, with screenshots: "i selected Treinrit ... the next option was
not a train option and only took me to the front page ... 1. For the selected type only that type should be
viewable, 2. All options must pull through to the trip but only for the right type, 3. This may be a global fix").
 * Quick's find results for a trip kind search that kind (rail*, not the last word 'journey*') and keep only
   adverts of that kind: a lodge is a stay, every other trip is an experience, and the words must match.
 * GLOBAL: the app opened ?listing=<id> only if that advert was already loaded for the viewer's own city, so
   any cross-city or cross-category link fell back to the front page. openDetail now fetches the advert it
   cannot find and opens it (Quick, wishlist, showcase, e-mail links all benefit).
Idempotent; asserts every anchor."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8").write(s); assert rd(p) == s, p
def rep(s, a, b, name):
    if b in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)
q = rd("quick.html")
q = rep(q, "  window.qTerm=qterm;\n",
 "  window.qTerm=qterm;\n"
 "  /* TRIP-TYPE-1 (David 25 Sep 2026): \"For the selected type only that type should be viewable\" */\n"
 "  var TYPE_Q={'Rail journey':'rail*','Game lodge':'lodge*','Safari':'safari*','Guided tour':'tour*','Self-drive':'drive*','Fishing':'fish*'};\n"
 "  var TYPE_RX={'Game lodge':/lodge|game reserve|bush camp/i,'Safari':/safari|game drive/i,'Guided tour':/guided|\\btour/i,\n"
 "               'Self-drive':/self[- ]?drive|road ?trip|4x4/i,'Rail journey':/\\brail|\\btrain/i,'Fishing':/\\bfish|angling/i};\n"
 "  function typeFilter(list){ var w=roleLabel(), rx=TYPE_RX[w]; if(!rx || cat().key!=='adventures') return list;\n"
 "    var want = w==='Game lodge' ? /accommodation/ : /experiences/;\n"
 "    return list.filter(function(l){ return want.test(String(l.category||'')) && rx.test((l.title||'')+' '+(l.description||'')); }); }\n",
 "typeFilter")
q = rep(q, "    var url='/listings?city='+encodeURIComponent(city)+'&category='+encodeURIComponent(co.category)+'&page_size=5'\n"
           "           +(qterm(what)?'&q='+encodeURIComponent(qterm(what)):'');",
           "    var qt=(cat().key==='adventures' && TYPE_Q[what]) || qterm(what);\n"
           "    var url='/listings?city='+encodeURIComponent(city)+'&category='+encodeURIComponent(co.category)+'&page_size=20'\n"
           "           +(qt?'&q='+encodeURIComponent(qt):'');", "url")
q = rep(q, "      .then(function(j){ paint(Array.isArray(j)?j:(j&&(j.listings||j.items))||[], false); })",
           "      .then(function(j){ paint(typeFilter(Array.isArray(j)?j:(j&&(j.listings||j.items))||[]), false); })", "paint filter")
KB = """
/* TRIP-TYPE-1: each trip kind wears its own picture (tour, rail and fishing wore a safari's). */
(function(){ var K={'Guided tour':'advk_guided_tour','Self-drive':'advk_self_drive','Rail journey':'advk_rail_journey','Fishing':'advk_fishing'};
  Object.keys(K).forEach(function(n){ PH[K[n]]=PH_BASE+K[n]+'.jpg'; });
  CATS.forEach(function(c){ if(c.key!=='adventures') return; ['sell','find'].forEach(function(side){ ((c[side]||{}).steps||[]).forEach(function(s){
    if(s.key==='what') (s.tiles||[]).forEach(function(t){ if(K[t.t]) t.p=K[t.t]; }); }); }); }); })();
"""
if "TRIP-TYPE-1: each trip kind wears its own picture" not in q:
    q = rep(q, "\ndrawDoor();\n</script>", KB + "\ndrawDoor();\n</script>", "trip pics")
wr("quick.html", q)

m = rd("ms.js")
m = rep(m, "  if (!l) {\n    console.warn('openDetail: no listing for id', id);",
 "  if (!l) {\n"
 "    /* DEEPLINK-FETCH-1 (David 25 Sep 2026: \"All options must pull through ... This may be a global fix\"): an advert\n"
 "       outside the loaded city/category is FETCHED and opened, never dropped to the front page. Once per tap. */\n"
 "    const _raw = String(id).replace(/^bea_/, '');\n"
 "    if (/^\\d+$/.test(_raw) && window._msDetailFetching !== _raw) {\n"
 "      window._msDetailFetching = _raw;\n"
 "      fetch(BEA_URL + '/listings/' + _raw, {credentials:'include'}).then(r => r.ok ? r.json() : null).then(row => {\n"
 "        if (row && row.id != null) {\n"
 "          if (!findListing('bea_' + row.id)) { try { LISTINGS.push(_msMapBeaListing(row)); } catch(e){} }\n"
 "          if (findListing('bea_' + row.id)) { try { goTo('browse'); } catch(e){} openDetail('bea_' + row.id); window._msDetailFetching = null; return; }\n"
 "        }\n"
 "        window._msDetailFetching = null;\n"
 "        if (typeof showToast === 'function') showToast('That listing is not available any more.');\n"
 "      }).catch(() => { window._msDetailFetching = null; if (typeof showToast === 'function') showToast('That listing is not in view right now — try Browse.'); });\n"
 "      return;\n"
 "    }\n"
 "    console.warn('openDetail: no listing for id', id);", "openDetail")
m = rep(m, "      } else if(tries > 0){\n        setTimeout(function(){ _openDeepLink(tries - 1); }, 400);\n      }\n    })(25);",
 "      } else if(tries > 0 && !(typeof LISTINGS !== 'undefined' && LISTINGS && LISTINGS.length && tries < 22)){\n"
 "        setTimeout(function(){ _openDeepLink(tries - 1); }, 400);\n"
 "      } else {\n"
 "        /* DEEPLINK-FETCH-1: loaded and still not here -- another city or category. Fetch it and open it. */\n"
 "        try{ goTo('browse'); }catch(e){}\n"
 "        try{ openDetail('bea_' + _dlId); }catch(e){}\n"
 "      }\n    })(25);", "deeplink")
wr("ms.js", m)
print("TRIP-TYPE-1 + DEEPLINK-FETCH-1 applied")
