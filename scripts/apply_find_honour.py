#!/usr/bin/env python3
"""FIND-HONOUR-1 (David 4 Oct 2026). A townhouse David listed TO SELL in Rietvalleirand came up in Quick's Find under
"Renting", and under every area she could pick. Cause: Find turned her FIRST answer into one search word and used her
area only to choose the city -- every other answer (to buy or to rent, the area itself, the price band, the school level,
the day, the trip length) was dropped without a word, in every category. The principle fixed here, for all eight doors:

  * every Find question is DECLARED in FIND_FROM: a test a result must pass, 'text' (the existing search word / group /
    role match), or 'ask' (nothing on an advert can state it -- it travels in her message only);
  * a result whose own fields or words CONTRADICT an answer is never shown; an advert silent on that thing is not hidden;
  * the area is a test like the others: "Yes" counts only adverts in her area (by name, or within that area's reach);
  * where nothing real fits, AI example cards built on the category's generated photos fill the shelf, marked as examples;
  * write side: Quick stores the platform's words for a deal ('For Sale' / 'For Rent'), never its chip wording.

RG-0817 (scripts/regression_ledger.py) fails the deploy when a Find step exists without a declaration here.
Idempotent; asserts every anchor. Copies quick.html over genie/HARNESS.html (the two are kept identical)."""
import io, os
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def rd(p): return io.open(os.path.join(R, p), encoding="utf-8", newline="").read()
def wr(p, s):
    io.open(os.path.join(R, p), "w", encoding="utf-8", newline="").write(s); assert rd(p) == s, p
def rep(s, a, b, name, done_marker=None):
    if (done_marker or b) in s: return s
    assert s.count(a) == 1, "anchor %s: %d" % (name, s.count(a)); return s.replace(a, b)

BLOCK = r'''  /* ---------------- FIND-HONOUR-1 (David 4 Oct 2026) ----------------
     "David put this up for sale, and now it is showing as a rental" + "listed under Rietvalleirand, and it is being
     advertised in all suburbs". Find used her first answer as a search word and her area only to pick the city; every
     other answer was dropped. Every Find question is now DECLARED below -- a test the advert must pass, 'text' (the
     search word / group / role match above), or 'ask' (no advert can state it; it goes in her message). An advert that
     CONTRADICTS an answer is never shown; one that is silent on it is not hidden. RG-0817 refuses an undeclared step. */
  var FIND_FROM={
    property:   {what:'prop_type', deal:'deal', where:'area'},
    cars:       {what:'text', price:'price', where:'area'},
    tutors:     {what:'text', level:'level', where:'area'},
    services:   {group:'text', what:'text', where:'area', when:'ask'},
    homehelp:   {group:'text', what:'text', where:'area', when:'ask', day:'day'},
    collectors: {what:'text', price:'price', rare:'ask'},
    adventures: {what:'text', len:'len', when:'ask', where:'place', kind:'kind'},
    localmarket:{what:'text', where:'area', price:'price'}};
  window.FIND_FROM=FIND_FROM;
  function fStep(k){ var f=null; try{ f=flow(); }catch(e){} var st=(f&&f.steps)||[];
    for(var i=0;i<st.length;i++) if(st[i] && st[i].key===k) return st[i]; return null; }
  function fIdx(k,label){ var s=fStep(k), t=(s&&s.tiles)||[]; for(var j=0;j<t.length;j++) if(t[j].t===label) return j; return -1; }
  function fTxt(l){ return String(l.title||'')+' '+String(l.description||''); }
  function akey(s){ return keyOf(s).replace(/[^a-z0-9]/g,''); }
  /* one reading of sale-or-rent for every word the platform has ever stored (For Sale, To sell, For Rent, To Rent,
     To let, For Hire / Rental, Commercial Rental) -- the same reading the app's Browse filter makes */
  function qDealOf(l){
    var lt=String(l.listing_type||'');
    if(/rent|\blet\b|hire|lease/i.test(lt)) return 'rent';
    if(/sale|sell/i.test(lt)) return 'sale';
    var d=String(l.description||'');
    if(/for rent|per month|monthly rent|to let|to-let|rental/i.test(d)) return 'rent';
    if(/for sale|asking price|selling price/i.test(d)) return 'sale';
    /* a home whose advert names neither reads its own price: no home in the bands we serve sells for under R100 000,
       and none lets for R250 000 a month (listing 329: R23 990, 'fully furnished', no type -- a rental) */
    var p=+l.price_num; if(/^property$/i.test(String(l.category||'')) && p>0){ if(p<100000) return 'rent'; if(p>=250000) return 'sale'; }
    return '';
  }
  window.qDealOf=qDealOf;
  /* the six property tiles, in tile order: House, Flat, Townhouse, Plot, Farm, Commercial */
  var PT_RX=[/^(?![\s\S]*town\s?house)[\s\S]*\b(house|home|villa|cottage|bungalow|homestead)/i,
             /\b(flat|apartment|penthouse|studio|loft|bachelor)/i,
             /town\s?house|\bcluster|duplex|simplex|sectional/i,
             /\b(plot|vacant|stand|erf)\b|vacant land/i,
             /\b(farm|smallholding|small holding|agricultural|holding)/i,
             /\b(commercial|office|retail|shop|industrial|warehouse|factory)/i];
  function ptOf(s){ var h=[]; for(var i=0;i<PT_RX.length;i++) if(PT_RX[i].test(s)) h.push(i); return h; }
  /* school levels in tile order (the words may be the country pack's -- the position is what counts) */
  var LV_RX=[/primary|foundation|junior|elementary|grade\s?[1-7]\b|gr\.?\s?[1-7]\b|all levels|any level/i,
             /high|secondary|grade\s?(8|9|1[0-2])\b|gr\.?\s?(8|9|1[0-2])\b|gcse|middle school|all levels|any level/i,
             /matric|grade\s?12|gr\.?\s?12|nsc|ieb|sixth form|senior|a.level|high|secondary|all levels|any level/i,
             /universit|tertiary|college|varsity|degree|undergrad|post.?grad|all levels|any level/i];
  var DAYS=['mon','tue','wed','thu','fri','sat','sun'], DAYW='(mon|tue|wed|thu|fri|sat|sun)(?:[a-z]*day|s|rs)?\\b';
  function qNums(s){ var m, out=[], rx=/(\d+(?:[ ,\u00a0\u202f]\d{3})*(?:\.\d+)?)\s*([kKmM](?![a-z]))?/g;
    while((m=rx.exec(String(s||'')))){ var n=parseFloat(m[1].replace(/[ ,\u00a0\u202f]/g,'')); if(m[2]) n*=(/k/i.test(m[2])?1e3:1e6); out.push(n); }
    return out; }
  function qKm(a,b,c,d){ var r=Math.PI/180, x=(d-b)*r*Math.cos((a+c)*r/2), y=(c-a)*r; return 6371*Math.sqrt(x*x+y*y); }
  /* an area that is a district, not one suburb, reaches further (km); a suburb from the city's own list reaches 3 km */
  var AREA_R={'pretoria east':[-25.790,28.310,7],'centurion':[-25.859,28.186,8],'midrand':[-25.990,28.125,7],'sandton':[-26.108,28.057,5]};
  var FIND_TEST={
    deal:function(l,pk){ var i=fIdx('deal',pk.label); if(i<0) return true;
      var want=(i===0?'sale':'rent'), got=qDealOf(l); return !got || got===want; },
    prop_type:function(l,pk){ var i=fIdx('what',pk.label);
      if(i<0){ var w=String(qterm(pk.label)).replace('*',''); return !w || new RegExp(w,'i').test(String(l.prop_type||'')+' '+fTxt(l)); }
      var st=ptOf(String(l.prop_type||'')); if(!st.length) st=ptOf(String(l.title||''));
      return !st.length || st.indexOf(i)>=0; },
    area:function(l,pk,c,A){
      if(c.key==='tutors' && /online|both/i.test(String(l.mode||''))) return true;      /* she can be taught from anywhere */
      var asks=(pk.areas||String(pk.label||'').split(',')).map(akey).filter(Boolean); if(!asks.length) return true;
      var mine=[l.suburb].concat(String(l.area||'').split(',')).map(akey).filter(Boolean);
      for(var i=0;i<asks.length;i++) if(mine.indexOf(asks[i])>=0) return true;
      var la=+(l.suburb_lat||l.listing_lat), ln=+(l.suburb_lng||l.listing_lng); if(!la || !ln) return false;
      for(var j=0;j<asks.length;j++){ var a=(A||{})[asks[j]]; if(a && qKm(a[0],a[1],la,ln)<=a[2]) return true; }
      return false; },
    place:function(l,pk){ var asks=(pk.areas||String(pk.label||'').split(',')).map(function(x){ return keyOf(x); }).filter(Boolean);
      if(!asks.length) return true;
      var hay=(String(l.suburb||'')+' '+String(l.area||'')+' '+String(l.city||'')+' '+fTxt(l)).toLowerCase();
      for(var i=0;i<asks.length;i++) if(hay.indexOf(asks[i])>=0) return true; return false; },
    price:function(l,pk){ var i=fIdx('price',pk.label), b=qNums(pk.label); if(!b.length) return true;
      var lo=0, hi=Infinity; if(b.length>=2){ lo=b[0]; hi=b[1]; } else if(i===0 || /under|below|less|up to/i.test(pk.label)) hi=b[0]; else lo=b[0];
      var p=+l.price_num; if(!(p>0)){ var pn=qNums(l.price); p=pn.length?pn[0]:0; }
      return !(p>0) || (p>=lo && p<=hi); },
    level:function(l,pk){ var i=fIdx('level',pk.label), s=String(l.level||''); if(!s || i<0 || !LV_RX[i]) return true; return LV_RX[i].test(s); },
    day:function(l,pk){ var i=fIdx('day',pk.label); if(i<0 || i>6) return true;          /* 'Any day' */
      var d=String(l.description||''), m=/available:\s*([^.]+)\./i.exec(d), s=(String(l.availability||'')+' '+(m?m[1]:'')).toLowerCase();
      if(/every day|daily|7 days|any day/i.test(s+' '+d)) return true;
      var on={}, any=false, x, rr=new RegExp(DAYW+'\\s*(?:-|\u2013|to)\\s*'+DAYW,'g');
      while((x=rr.exec(s))){ any=true; var p=DAYS.indexOf(x[1]), q=DAYS.indexOf(x[2]); for(var k=p, n=0; n<7; k=(k+1)%7, n++){ on[k]=1; if(k===q) break; } }
      DAYS.forEach(function(dd,k){ if(new RegExp('\\b'+dd+'(?:[a-z]*day|s|rs)?\\b').test(s)){ any=true; on[k]=1; } });
      return !any || !!on[i]; },
    len:function(l,pk){ var s=fStep('len'), t=(s&&s.tiles)||[], x=fTxt(l).toLowerCase(), st=[];
      t.forEach(function(tt,k){ if(x.indexOf(String(tt.t).toLowerCase())>=0) st.push(k); });
      var i=fIdx('len',pk.label); return i<0 || !st.length || st.indexOf(i)>=0; },
    kind:function(l,pk){ var s=akey(l.prop_type||''); return !s || s===akey(pk.label); }
  };
  window.FIND_TEST=FIND_TEST;
  /* her city's own suburb list gives each area a point; one request per city, kept for the visit */
  var _anch={};
  function qAnchors(city){
    if(_anch[city]) return _anch[city];
    var base={}; for(var k in AREA_R) base[akey(k)]=AREA_R[k];
    var cc=(window.QCC||'ZA')==='UK'?'GB':(window.QCC||'ZA');
    var p=fetch('/geo/cities?country='+encodeURIComponent(cc)).then(function(r){ return r.ok?r.json():[]; })
      .then(function(cs){ var id=null; (cs||[]).forEach(function(x){ if(x && keyOf(x.name)===keyOf(city)) id=x.id; });
        return id ? fetch('/geo/suburbs?city_id='+id).then(function(r){ return r.ok?r.json():[]; }) : []; })
      .then(function(ss){ var m={}; (ss||[]).forEach(function(s){ if(s && +s.lat && +s.lng) m[akey(s.name)]=[+s.lat,+s.lng,3]; });
        for(var k2 in base) m[k2]=base[k2]; return m; })
      .catch(function(){ return base; });
    _anch[city]=p; return p;
  }
  window.qAnchors=qAnchors;
  function qFindHonour(list, A){
    var c=cat(), dec=FIND_FROM[c.key]||{}, tests=[];
    picks.forEach(function(pk){ if(!pk || !pk.key) return; var d=dec[pk.key];
      if(d===undefined){ try{ console.error('FIND-HONOUR-1: Find step "'+pk.key+'" in '+c.key+' is not declared'); qTrack('q_find_undeclared', {cat:c.key, step:pk.key}); }catch(e){} return; }
      if(d==='text' || d==='ask') return;
      if(FIND_TEST[d]) tests.push([FIND_TEST[d], pk]); });
    return (list||[]).filter(function(l){ for(var i=0;i<tests.length;i++) if(!tests[i][0](l, tests[i][1], c, A)) return false; return true; });
  }
  window.qFindHonour=qFindHonour;
  /* nothing real and no AI example fits: example cards on the category's own generated photos, marked AI EXAMPLE,
     built only from her answers (the kind she asked for, to buy or to rent, her area) -- never tappable as a real advert */
  function qLocalExamples(c, where, city){
    var w=pickOf('what'), d=pickOf('deal'), seen={}, pool=[];
    [(w&&w.photo)].concat(c._adp||[], c.hero||[]).forEach(function(p){ if(p && PH[p] && !seen[p]){ seen[p]=1; pool.push(p); } });
    var di=d ? fIdx('deal', d.label) : -1;
    var title=(w ? w.label : c.name)+(di===0 ? ' \u2014 '+T('To sell') : (di===1 ? ' \u2014 '+T('To let') : ''));
    var sub=where ? String((where.areas&&where.areas[0])||where.label).split(',')[0] : '';
    /* no two cards on one shelf may read the same: the 2nd and 3rd carry one of the category's own example details */
    var det=((typeof DETAIL!=='undefined' && DETAIL[c.key])||[]).filter(function(x){ return x.indexOf('%')<0; });
    return pool.slice(0,3).map(function(p,i){ return {_local:1, demo_example:1, title:title+((i && det[i-1]) ? ' \u00b7 '+det[i-1] : ''),
      suburb:sub, city:city, thumb_url:PH[p], price:''}; });
  }
  window.qLocalExamples=qLocalExamples;
  /* FIND-AREAS-LIVE-1 (David 4 Oct 2026, looking for Maroushka's live flats: "it appears as a single unit (Brooklyn) but
     also in all suburbs, while there was no option for Brooklyn"). Beside the fixed areas, the area question offers the
     suburbs where a live advert that fits her answers so far actually is -- so a real advert can always be reached. */
  var _liveCache={}, _inLive=false;
  function qLiveList(){
    var c=cat(), co=catOut(c), city=window.QCITY||LOC.city||'Pretoria', k=city+'|'+co.category;
    if(_liveCache[k]) return _liveCache[k].list;
    _liveCache[k]={list:null};
    if(!LIVE) return null;
    fetch('/listings?city='+encodeURIComponent(city)+'&category='+encodeURIComponent(co.category)+'&page_size=200',{credentials:'include'})
      .then(function(r){ return r.ok?r.json():[]; })
      .then(function(j){ _liveCache[k].list=Array.isArray(j)?j:((j&&(j.listings||j.items))||[]); })
      .catch(function(){ _liveCache[k].list=[]; });
    return null;
  }
  var _flLive=flow;
  flow=function(){
    var f=_flLive(); if(_inLive || !f || !f.steps || mode!=='find') return f;
    var list=null; try{ list=qLiveList(); }catch(e){}
    if(!list || !list.length) return f;
    return {steps:f.steps.map(function(s){
      if(!s || s.key!=='where') return s;
      var ok=[]; _inLive=true;
      try{
        var real=list.filter(function(l){ return !(l.demo_example || +l.super_example || +l.is_demo); });
        var stem=String(qterm(roleLabel())).replace('*','');
        if((FIND_FROM[cat().key]||{}).what==='text' && stem && !groupRx())
          real=real.filter(function(l){ return new RegExp(stem,'i').test(fTxt(l)+' '+(l.service_type||'')+' '+(l.subject||'')+' '+(l.body_type||'')+' '+(l.collectible_type||'')); });
        ok=qFindHonour(typeFilter(real), {});
      }catch(e){ ok=[]; }
      _inLive=false;
      var have={}; (s.tiles||[]).forEach(function(t){ have[akey(t.t)]=1; });
      var n={}, name={};
      ok.forEach(function(l){ var sb=String(l.suburb||'').trim(), k=akey(sb); if(!k || have[k]) return; n[k]=(n[k]||0)+1; if(!name[k]) name[k]=sb; });
      var add=Object.keys(n).sort(function(a,b){ return n[b]-n[a]; }).slice(0,4).map(function(k){ return {t:name[k]}; });
      if(!add.length) return s;
      var tiles=(s.tiles||[]).concat(add), pics=tiles.every(function(t){ return !!t.p; });
      return {q:s.q, key:s.key, kind:pics?s.kind:'chip', free:s.free, freeHint:s.freeHint,
              tiles:pics?tiles:tiles.map(function(t){ return {t:t.t, wide:false}; })};
    })};
  };
'''

q = rd("quick.html")
q = rep(q, "  drawLookup=function(){\n    atSub=null;", BLOCK + "  drawLookup=function(){\n    atSub=null;", "block", "FIND-HONOUR-1 (David 4 Oct 2026) ----")
q = rep(q, "var where=pickOf('where'), city=(where&&cityOf(where.label))||LOC.city||'Pretoria', what=roleLabel();",
           "var where=pickOf('where'), city=(where&&cityOf(where.label))||LOC.city||'Pretoria', what=roleLabel();\n"
           "    var placeLabel=where ? String(where.label)+' \\u00b7 '+city : city, placeName=where ? String(where.label) : city;   /* FIND-HONOUR-1 */",
        "placeLabel")
q = rep(q, "      var _all=(list||[]), _exAll=_all.filter(isEx);",
           "      var _all=(list||[]), _exAll=_all.filter(isEx);\n"
           "      if(!_all.length && !failed) _exAll=qLocalExamples(c, where, city);   /* FIND-HONOUR-1: the generated photos fill an empty shelf, marked */",
        "local examples")
q = rep(q, "return '<div class=\"ad\" data-lid=\"'+E(String(l.id).replace(/^bea_/,''))+'\" style=",
           "return '<div class=\"ad\"'+(l._local?'':' data-lid=\"'+E(String(l.id).replace(/^bea_/,''))+'\"')+' style=",
        "card lid")
q = rep(q, "? '<div class=\"count\"><span style=\"font-size:11.5px\"><span>'+E(city)+'</span>",
           "? '<div class=\"count\"><span style=\"font-size:11.5px\"><span>'+E(placeLabel)+'</span>",
        "count place")
q = rep(q, "(T('Nobody has listed this in')+' '+city+' '+T('yet.'))",
           "(T('Nobody has listed this in')+' '+placeName+' '+T('yet.'))",
        "empty place")
OLD_FETCH = """    var grp=groupRx();                                    /* LM-GROUP-FIND-1: a group asks for the whole category, then filters */
    var qt=grp ? '' : ((cat().key==='adventures' && TYPE_Q[what]) || qterm(what));
    var url='/listings?city='+encodeURIComponent(city)+'&category='+encodeURIComponent(co.category)+'&page_size='+(grp?200:20)
           +(qt?'&q='+encodeURIComponent(qt):'');
    fetch(url,{credentials:'include'}).then(function(r){ return r.ok?r.json():Promise.reject(r.status); })
      .then(function(j){ paint(typeFilter(Array.isArray(j)?j:(j&&(j.listings||j.items))||[]), false); })
      .catch(function(){ paint([], true); });"""
NEW_FETCH = """    var grp=groupRx();                                    /* LM-GROUP-FIND-1: a group asks for the whole category, then filters */
    /* FIND-HONOUR-1: a property's kind is its prop_type, not a word ("Flat" never found an Apartment) -- the whole
       category is asked for and every declared answer is tested on the adverts themselves */
    var qt=(grp || cat().key==='property') ? '' : ((cat().key==='adventures' && TYPE_Q[what]) || qterm(what));
    var url='/listings?city='+encodeURIComponent(city)+'&category='+encodeURIComponent(co.category)+'&page_size=200'
           +(qt?'&q='+encodeURIComponent(qt):'');
    Promise.all([fetch(url,{credentials:'include'}).then(function(r){ return r.ok?r.json():Promise.reject(r.status); }), qAnchors(city)])
      .then(function(rs){ var j=rs[0]; paint(qFindHonour(typeFilter(Array.isArray(j)?j:(j&&(j.listings||j.items))||[]), rs[1]), false); })
      .catch(function(){ paint([], true); });"""
q = rep(q, OLD_FETCH, NEW_FETCH, "fetch")
q = rep(q, "      body[f]=(f==='beds'||f==='baths'||f==='vehicle_year') ? parseInt(pk.label,10)||null : pk.label;\n    });\n  return {body:body, ls:ls};",
           "      body[f]=(f==='beds'||f==='baths'||f==='vehicle_year') ? parseInt(pk.label,10)||null : pk.label;\n    });\n"
           "  /* FIND-HONOUR-1 (write side): one meaning, one stored word -- the platform's 'For Sale' / 'For Rent' (Edit's, Browse's\n"
           "     and every import's words), never Quick's chip wording 'To sell' / 'To let' */\n"
           "  if(body.listing_type) body.listing_type=/\\blet\\b|rent|hire/i.test(body.listing_type) ? 'For Rent' : (/sell|sale/i.test(body.listing_type) ? 'For Sale' : body.listing_type);\n"
           "  return {body:body, ls:ls};",
        "write canon")
q = rep(q, """            +'<div class="lknote">'+E(T('Tap one to ask for an introduction \\u2014 it opens in TrustSquare.'))+'</div>'""",
           """            +(five.some(function(l){ return !l._local; }) ? '<div class="lknote">'+E(T('Tap one to ask for an introduction \\u2014 it opens in TrustSquare.'))+'</div>' : '')   /* FIND-HONOUR-1: an example card is not tappable */""",
        "lknote")
assert q.rstrip().endswith("</html>"), "TRUNCATED"
wr("quick.html", q)
wr("genie/HARNESS.html", q)
print("FIND-HONOUR-1 applied; genie/HARNESS.html = quick.html; %d bytes" % len(q.encode("utf-8")))
