# TrustSquare wonder data-integrity audit (READ-ONLY). Verifies name/country vs Wikidata,
# finds duplicate entries. Deterministic, zero-token. Writes JSON + styled HTML report.
import sys,json,re,time,datetime,html,os,requests
WPATH="/var/www/marketsquare/wonders.json"; ODIR="/var/www/marketsquare/orchestrator"
UA={"User-Agent":"TrustSquareBot/1.0 (https://trustsquare.co; data audit)"}
LIMIT=int(sys.argv[1]) if len(sys.argv)>1 and sys.argv[1].isdigit() else None
def wd(name):
    try:
        r=requests.get("https://www.wikidata.org/w/api.php",params={"action":"wbsearchentities","search":name,"language":"en","type":"item","format":"json","limit":1},headers=UA,timeout=25)
        s=r.json().get("search",[]); return ({"label":s[0].get("label"),"desc":s[0].get("description","") or ""} if s else None)
    except Exception: return None
data=json.load(open(WPATH)); full=data if isinstance(data,list) else data.get("wonders"); arr=full[:LIMIT] if LIMIT else full
from collections import defaultdict
bn=defaultdict(list); bc=defaultdict(list)
for w in full:
    bn[(w.get("name") or "").strip().lower()].append(w.get("name"))
    la,lo=w.get("lat"),w.get("lon")
    if isinstance(la,(int,float)) and isinstance(lo,(int,float)): bc[(round(la,2),round(lo,2))].append(w.get("name"))
dupn=[v for v in bn.values() if len(v)>1]; dupc=[v for v in bc.values() if len(v)>1]
review=[]; ok=0
for w in arr:
    nm=w.get("name"); ctry=(w.get("country") or "").strip(); s=wd(nm); time.sleep(0.3)
    if not s: review.append({"name":nm,"country":ctry,"flag":"NOT FOUND on Wikidata","wd":""}); continue
    if ctry and ctry.lower() in s["desc"].lower(): ok+=1
    else: review.append({"name":nm,"country":ctry,"flag":"country not confirmed","wd":(s["label"] or "")+" — "+s["desc"]})
gen=datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
rep={"generated":gen,"checked":len(arr),"total":len(full),"country_confirmed":ok,"to_review":len(review),"dup_name_groups":dupn,"dup_coord_groups":dupc,"review":review}
os.makedirs(ODIR,exist_ok=True); json.dump(rep,open(ODIR+"/wonder_audit.json","w"),indent=2)
def e(x): return html.escape("" if x is None else str(x))
rows="".join("<tr><td>%s</td><td>%s</td><td><span class=p>%s</span></td><td>%s</td></tr>"%(e(r['name']),e(r['country']),e(r['flag']),e(r.get('wd',''))) for r in review)
dn="".join("<li><b>%s</b></li>"%e(" = ".join(g)) for g in dupn) or "<li>None ✓</li>"
dc="".join("<li>%s</li>"%e(" / ".join(g)) for g in dupc) or "<li>None ✓</li>"
H="<!DOCTYPE html><html><head><meta charset=utf-8><meta name=viewport content='width=device-width,initial-scale=1'><title>Wonder Data Audit</title><style>body{font:14px/1.6 Inter,system-ui,sans-serif;color:#1f2937;max-width:1000px;margin:0 auto;padding:28px}h1{color:#15314e}h2{color:#15314e;border-bottom:2px solid #eef2f6;padding-bottom:5px;margin-top:26px}.s{display:inline-block;background:#f4f6f9;border:1px solid #e1e6ec;border-radius:10px;padding:9px 15px;margin:3px}.s b{font-size:21px;color:#15314e;display:block}table{border-collapse:collapse;width:100%;font-size:13px}th{background:#15314e;color:#fff;text-align:left;padding:8px}td{padding:8px;border-bottom:1px solid #e6ebf0;vertical-align:top}.p{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:#fbf2dd;color:#b07d12}.m{color:#6b7280;font-size:12px}</style></head><body>"
H+="<h1>TrustSquare — Wonder Data Audit</h1><p class=m>%s · checked %d of %d vs Wikidata · READ-ONLY (no data changed)</p>"%(gen,len(arr),len(full))
H+="<div><span class=s><b>%d</b>country confirmed</span><span class=s><b>%d</b>to review</span><span class=s><b>%d</b>dup-name groups</span><span class=s><b>%d</b>dup-coord groups</span></div>"%(ok,len(review),len(dupn),len(dupc))
H+="<h2>Duplicate entries — by name</h2><ul>"+dn+"</ul><h2>Duplicate entries — by coordinates</h2><ul>"+dc+"</ul>"
H+="<h2>Country not auto-confirmed (needs a human glance)</h2><table><tr><th>Wonder</th><th>Our country</th><th>Flag</th><th>Wikidata</th></tr>"+rows+"</table>"
H+="<p class=m>'Country not confirmed' just means the country wasn't in Wikidata's one-line description — many are fine (terse), some are genuine mismatches.</p></body></html>"
open(ODIR+"/wonder_audit.html","w").write(H)
print(json.dumps({"checked":len(arr),"confirmed":ok,"to_review":len(review),"duplicate_name_groups":dupn,"duplicate_coord_group_count":len(dupc)},indent=2)[:2000])
