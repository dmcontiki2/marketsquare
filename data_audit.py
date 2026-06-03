# TrustSquare wonder data-integrity audit (READ-ONLY). Verifies name/country vs Wikidata,
# finds duplicate entries. Deterministic, zero-token by default. Writes JSON + styled HTML.
#
# v2 (Jun 2026): country check upgraded from "is the country word in Wikidata's one-line
# blurb?" to a determination+validation pipeline:
#   1. fetch candidate entities; keep PLACE candidates (those carrying Wikidata country P17)
#   2. AUTHORITATIVE country = P17 of the most-notable candidate (max sitelinks = fame proxy),
#      so "Babylon" resolves to the ancient city (Iraq), not Babylon, New York.
#   3. validate stored country against authoritative + all candidates; bucket the verdict.
#   4. contested-sovereignty sites never auto-confirm a side -> POLICY review for a human.
# Optional AI adjudication of the small residual runs ONLY if env WONDER_AI_KEY is set
# (otherwise skipped cleanly -> identical zero-token behaviour). Never edits wonders.json.
import sys,json,re,time,datetime,html,os,requests
from collections import defaultdict
WPATH="/var/www/marketsquare/wonders.json"; ODIR="/var/www/marketsquare/orchestrator"
API="https://www.wikidata.org/w/api.php"
UA={"User-Agent":"TrustSquareBot/2.0 (https://trustsquare.co; read-only data audit)"}
SESS=requests.Session(); SESS.headers.update(UA)
LIMIT=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else None

# --- country normalisation (synonyms / political variants) ---
SYN={"usa":"united states","us":"united states","united states of america":"united states",
 "u.s.":"united states","america":"united states","united states":"united states",
 "uk":"united kingdom","great britain":"united kingdom","britain":"united kingdom",
 "england":"united kingdom","scotland":"united kingdom","wales":"united kingdom",
 "northern ireland":"united kingdom","united kingdom":"united kingdom",
 "turkey":"turkey","turkiye":"turkey","türkiye":"turkey",
 "taiwan":"taiwan","republic of china":"taiwan","chinese taipei":"taiwan",
 "china":"china","people's republic of china":"china","prc":"china",
 "czech republic":"czechia","czechia":"czechia",
 "democratic republic of congo":"democratic republic of the congo",
 "democratic republic of the congo":"democratic republic of the congo",
 "dr congo":"democratic republic of the congo","drc":"democratic republic of the congo",
 "macedonia":"north macedonia","north macedonia":"north macedonia",
 "republic of north macedonia":"north macedonia","swaziland":"eswatini","eswatini":"eswatini",
 "bosnia":"bosnia and herzegovina","bosnia and herzegovina":"bosnia and herzegovina",
 "south korea":"south korea","republic of korea":"south korea","korea":"south korea",
 "russia":"russia","russian federation":"russia","vietnam":"vietnam","viet nam":"vietnam",
 "myanmar":"myanmar","burma":"myanmar","state of palestine":"palestine","palestine":"palestine"}
def norm(c):
    if not c: return ""
    c=c.strip().lower()
    if c.startswith("the "): c=c[4:]
    return SYN.get(c,c)
def sset(s): return set(norm(p) for p in s.replace("&","/").split("/") if norm(p))

# sites whose sovereignty is internationally disputed: never auto-confirm a side
CONTESTED=["jerusalem","taipei","taiwan","crimea","western sahara","nagorno","kashmir","tibet"]
def is_contested(name): 
    n=name.lower(); return any(k in n for k in CONTESTED)

def _get(params,timeout=30,tries=5):
    for t in range(tries):
        try:
            r=SESS.get(API,params=params,timeout=timeout)
            if r.status_code==200: return r.json()
            if r.status_code in (429,500,502,503,504): time.sleep(1.5*(t+1)); continue
            return None
        except Exception: time.sleep(1.5*(t+1))
    return None
def search(name,limit=7):
    j=_get({"action":"wbsearchentities","search":name,"language":"en","type":"item","format":"json","limit":limit})
    return None if j is None else [h["id"] for h in j.get("search",[])]
def getents(ids,props):
    out={}
    for i in range(0,len(ids),40):
        j=_get({"action":"wbgetentities","ids":"|".join(ids[i:i+40]),"props":props,"languages":"en","format":"json"})
        if j: out.update(j.get("entities",{}))
        time.sleep(0.25)
    return out
def claim_ids(ent,prop):
    v=[]
    for c in ent.get("claims",{}).get(prop,[]):
        try: v.append(c["mainsnak"]["datavalue"]["value"]["id"])
        except Exception: pass
    return v
import math
def coord(ent):
    try:
        v=ent["claims"]["P625"][0]["mainsnak"]["datavalue"]["value"]; return (v["latitude"],v["longitude"])
    except Exception: return None
def hav(a,b):
    if not a or not b: return float("inf")
    (la1,lo1),(la2,lo2)=a,b; R=6371.0; rad=math.radians
    dla=rad(la2-la1); dlo=rad(lo2-lo1)
    x=math.sin(dla/2)**2+math.cos(rad(la1))*math.cos(rad(la2))*math.sin(dlo/2)**2
    return 2*R*math.asin(min(1,math.sqrt(x)))

# --- load data + duplicate detection (unchanged from v1) ---
data=json.load(open(WPATH)); full=data if isinstance(data,list) else data.get("wonders"); arr=full[:LIMIT] if LIMIT else full
bn=defaultdict(list); bc=defaultdict(list)
for w in full:
    bn[(w.get("name") or "").strip().lower()].append(w.get("name"))
    la,lo=w.get("lat"),w.get("lon")
    if isinstance(la,(int,float)) and isinstance(lo,(int,float)): bc[(round(la,2),round(lo,2))].append(w.get("name"))
dupn=[v for v in bn.values() if len(v)>1]; dupc=[v for v in bc.values() if len(v)>1]

# --- pass 1: candidate QIDs per wonder ---
cands={}; all_ids=set()
for w in arr:
    nm=w.get("name"); ids=search(nm) or []; cands[nm]=ids; all_ids.update(ids); time.sleep(0.35)
# --- pass 2: candidate entities (country + sitelink count as fame proxy) ---
ents=getents(sorted(all_ids),"claims|sitelinks")
cq=set()
for ent in ents.values(): cq.update(claim_ids(ent,"P17"))
clab={q:e.get("labels",{}).get("en",{}).get("value","") for q,e in getents(sorted(cq),"labels").items()}

def fame(ent): return len(ent.get("sitelinks",{}) or {})

review=[]; ok=0; verdicts=defaultdict(int)
for w in arr:
    nm=w.get("name"); ctry=(w.get("country") or "").strip(); st=sset(ctry)
    la,lo=w.get("lat"),w.get("lon")
    swc=(la,lo) if isinstance(la,(int,float)) and isinstance(lo,(int,float)) else None
    place=[]  # dicts: qid,cset,labels,fame,coord,dist
    for qid in cands.get(nm,[]):
        ent=ents.get(qid)
        if not ent: continue
        c17=claim_ids(ent,"P17")
        if not c17: continue
        labs=[clab.get(q,q) for q in c17]; cc=coord(ent)
        place.append({"qid":qid,"cset":set(norm(x) for x in labs),"labels":labs,
                      "fame":fame(ent),"coord":cc,"dist":hav(swc,cc) if swc else float("inf")})
    if is_contested(nm):
        verdicts["policy"]+=1
        review.append({"name":nm,"country":ctry,"flag":"POLICY — contested sovereignty (choose deliberately)","wd":", ".join(sorted({l for p in place for l in p["labels"]})) or "—"}); continue
    if not place:
        verdicts["unverifiable"]+=1
        review.append({"name":nm,"country":ctry,"flag":"unverifiable — no place/country found on Wikidata","wd":""}); continue
    # geo-anchor: if the wonder has coords, trust the candidate physically nearest it (<=75km)
    near=[p for p in place if p["dist"]<=75] if swc else []
    geo=bool(near)
    auth=min(near,key=lambda p:p["dist"]) if near else max(place,key=lambda p:p["fame"])
    auth_set=auth["cset"]; auth_labels=auth["labels"]
    in_auth=bool(st & auth_set); in_any=any(st & p["cset"] for p in place)
    if in_auth:
        ok+=1; verdicts["confirmed"]+=1
    elif in_any:
        verdicts["verify"]+=1
        review.append({"name":nm,"country":ctry,"flag":"VERIFY — name collision (a more-famous same-name place is elsewhere)","wd":"most-notable: "+", ".join(auth_labels)})
    elif geo or (auth["coord"] and swc and auth["dist"]<=800):
        # we have a geographically credible contradicting entity -> a real flag
        verdicts["likely_error"]+=1
        review.append({"name":nm,"country":ctry,"flag":"LIKELY ERROR — stored country matches no candidate near these coordinates","wd":"Wikidata (nearest/auth) says: "+", ".join(auth_labels)})
    else:
        # best candidate is far from the wonder's own coords -> real entity likely absent from search; do not assert
        verdicts["unverifiable"]+=1
        review.append({"name":nm,"country":ctry,"flag":"unverifiable — name too ambiguous to pin (real entity not in search results)","wd":""})

# --- optional AI adjudication of the residual (runs only if a key is provided) ---
ai_note="AI adjudication: skipped (set env WONDER_AI_KEY to enable for the residual)"
if os.environ.get("WONDER_AI_KEY") and review:
    try:
        import anthropic
        cl=anthropic.Anthropic(api_key=os.environ["WONDER_AI_KEY"])
        todo=[r for r in review if r["flag"].startswith(("VERIFY","LIKELY","POLICY"))]
        q="\n".join("%d. %s — stored: %s | evidence: %s"%(i+1,r["name"],r["country"],r["wd"]) for i,r in enumerate(todo))
        msg=cl.messages.create(model="claude-opus-4-6",max_tokens=1500,
            messages=[{"role":"user","content":"For each wonder, state the country the FAMOUS landmark of that name is in, whether the stored country is correct (yes/no/contested), and one-line why.\n"+q}])
        ai_note=msg.content[0].text
    except Exception as ex:
        ai_note="AI adjudication: error (%s)"%ex

gen=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
rep={"generated":gen,"checked":len(arr),"total":len(full),"country_confirmed":ok,
     "to_review":len(review),"verdicts":dict(verdicts),
     "dup_name_groups":dupn,"dup_coord_groups":dupc,"review":review,"ai_adjudication":ai_note}
os.makedirs(ODIR,exist_ok=True); json.dump(rep,open(ODIR+"/wonder_audit.json","w"),indent=2,ensure_ascii=False)

def e(x): return html.escape("" if x is None else str(x))
def badge(f):
    c={"POLICY":"#7c3aed","VERIFY":"#b07d12","LIKELY":"#c0392b","unver":"#6b7280"}
    k="POLICY" if f.startswith("POLICY") else "VERIFY" if f.startswith("VERIFY") else "LIKELY" if f.startswith("LIKELY") else "unver"
    return "<span class=p style='background:%s'>%s</span>"%(c[k],e(f))
rows="".join("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"%(e(r['name']),e(r['country']),badge(r['flag']),e(r.get('wd',''))) for r in review)
dn="".join("<li><b>%s</b></li>"%e(" = ".join(g)) for g in dupn) or "<li>None ✓</li>"
dc="".join("<li>%s</li>"%e(" / ".join(g)) for g in dupc) or "<li>None ✓</li>"
H="<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Wonder Data Audit</title><style>body{font:14px/1.6 Inter,system-ui,sans-serif;color:#1f2937;max-width:1000px;margin:0 auto;padding:28px}h1{color:#15314e}h2{color:#15314e;border-bottom:2px solid #eef2f6;padding-bottom:5px;margin-top:26px}.s{display:inline-block;background:#f4f6f9;border:1px solid #e1e6ec;border-radius:10px;padding:9px 15px;margin:3px}.s b{font-size:21px;color:#15314e;display:block}table{border-collapse:collapse;width:100%}th{background:#15314e;color:#fff;text-align:left;padding:8px}td{padding:8px;border-bottom:1px solid #e6ebf0;vertical-align:top;font-size:13px}.p{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;color:#fff}.m{color:#6b7280;font-size:12px}</style></head><body>"
H+="<h1>TrustSquare — Wonder Data Audit</h1><p class=m>%s · checked %d of %d vs Wikidata (country property P17, fame-ranked) · READ-ONLY</p>"%(gen,len(arr),len(full))
H+="<div><span class=s><b>%d</b>country confirmed</span><span class=s><b>%d</b>need attention</span><span class=s><b>%d</b>dup-name groups</span><span class=s><b>%d</b>dup-coord groups</span></div>"%(ok,len(review),len(dupn),len(dupc))
H+="<h2>Duplicate entries — by name (genuine faults to merge)</h2><ul>"+dn+"</ul><h2>Duplicate entries — by coordinates</h2><ul>"+dc+"</ul>"
H+="<h2>Country — needs attention (%d)</h2><p class=m>Confirmed entries are validated against the most-notable same-name place's Wikidata country; only the rows below remain.</p><table><tr><th>Wonder</th><th>Our country</th><th>Verdict</th><th>Evidence</th></tr>"%len(review)+rows+"</table>"
H+="<h2>AI adjudication</h2><pre class=m style='white-space:pre-wrap'>"+e(ai_note)+"</pre></body></html>"
open(ODIR+"/wonder_audit.html","w").write(H)
print(json.dumps({"checked":len(arr),"confirmed":ok,"need_attention":len(review),"verdicts":dict(verdicts),"duplicate_name_groups":len(dupn),"duplicate_coord_group_count":len(dupc)},indent=2)[:2000])
