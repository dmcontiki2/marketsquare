# RULINGS row
p="RULINGS.md"; s=open(p,encoding="utf-8").read()
row = ("| RUL-211 | 2026-10-07 | **THE APP FOLLOWS WHERE SHE IS -- AUTOMATICALLY -- AND ONLY HER OWN CHOICE OVERRIDES IT.** David, 7 Oct 2026, "
"on learning that every visitor started in South Africa / Pretoria whatever their location: *\"I would prefer it to switch automatically, still asking "
"which country they are from for the vpn users. Then it will only be wrong by the users selections. This is important for many reasons, including "
"languages, distances, locations, suburbs etc.\"* RULED (CTO execution): **(a)** until she picks a place herself, the app sets her country and city "
"automatically -- her phone's location when she allows it (nearest covered city within 150 km, any covered country; this beats a VPN), otherwise her "
"network's country (Cloudflare) and its main city; **(b)** Home says once what it chose and from what, with **Change country** for VPN users and "
"travellers; **(c)** her own pick always wins and is never overridden; the detected place is kept apart from her pick and re-checked every visit; "
"**(d)** a country we do not cover yet is named (\"TrustSquare isn't in France yet\") instead of silently showing South Africa. Supersedes "
"ABROAD-NUDGE-1 (ask-first, 6 Oct). Cost: nothing; no schema change; the network country is read per visit and never stored. Languages: not yet "
"automatic -- the app's language still follows the EN button (next). | RG-0911 · ms.js msGeoAuto / msGeoFromGps / msGeoBanner |\n")
a="| RUL-210 | 2026-10-06 |"; i=s.index(a); j=s.index("\n",i)+1
assert "RUL-211" not in s; s=s[:j]+row+s[j:]; open(p,"w",encoding="utf-8").write(s)
# rulings_check
p="scripts/rulings_check.py"; s=open(p,encoding="utf-8").read()
ent='''"RUL-211": [
   ("RULINGS.md", ["THE APP FOLLOWS WHERE SHE IS -- AUTOMATICALLY -- AND ONLY HER OWN CHOICE OVERRIDES IT"], []),
   ("ms.js", ["async function msGeoAuto(", "async function msGeoFromGps(", "function msGeoBanner(", "msGeoAuto();   // GEO-AUTO-1", "localStorage.removeItem('ms_user_city'); localStorage.removeItem('ms_user_country');"], ["function msAbroadNudge("]),
 ],
 '''
a=' "RUL-208": ['; assert s.count(a)==1; s=s.replace(a,' '+ent+'"RUL-208": [',1); open(p,"w",encoding="utf-8").write(s)
# ledger
p="scripts/regression_ledger.py"; s=open(p,encoding="utf-8").read()
i=s.index('@entry("RG-0910"'); j=s.index("def rg_abroad_nudge_1():"); k=s.index("\n@entry(",j) if "\n@entry(" in s[j:] else None
k=s.index("def _server_vantage_wrap():", j) if k is None or k> s.index("def _server_vantage_wrap():", j) else k
new='''@entry("RG-0910", "ABROAD-NUDGE-1 (Goal run 31, 6 Oct 2026) -- SUPERSEDED 7 Oct by GEO-AUTO-1 (RUL-211): the ask-first nudge is gone, the app switches by itself",
       LOCKED, fixed_on="2026-10-07",
       scope="ms.js carries no msAbroadNudge (two location questions would fight); RG-0911 holds the replacement",
       ref="David 7 Oct 2026: 'I would prefer it to switch automatically, still asking which country they are from for the vpn users.'")
def rg_abroad_nudge_1():
    js = repo_file("ms.js")
    if js is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    if "function msAbroadNudge(" in js or "setTimeout(msAbroadNudge" in js:
        return [(FAIL, "the old ask-first abroad nudge is back next to GEO-AUTO-1")]
    return [(INFO, "superseded by GEO-AUTO-1")]

@entry("RG-0911", "GEO-AUTO-1 (RUL-211, David 7 Oct 2026): country and city follow where she is -- phone location, else network country -- until she picks her own",
       LOCKED, fixed_on="2026-10-07",
       scope="ms.js msGeoAuto (network, /quick/me geo + /geo/countries), msGeoFromGps (nearest covered city <=150 km), msGeoBanner (Change country), "
             "ms_auto_city/ms_auto_country kept apart from ms_user_city; boot restores the auto pair",
       ref="Goal run 31: an en-GB phone on a US network got South Africa / Pretoria, rand prices and the SA legal card. David asked why, then ruled RUL-211.")
def rg_geo_auto_1():
    js = repo_file("ms.js")
    if js is None:
        return [(INFO, "NOT EVALUATED - repo not readable from here")]
    bad = []
    need = {"async function msGeoAuto(": "network detection is gone",
            "async function msGeoFromGps(": "the phone's location no longer places her (a VPN would move her)",
            "msGeoAuto();   // GEO-AUTO-1": "detection is never started",
            "try{ msGeoFromGps(buyerLat, buyerLng); }catch(_){}": "the phone's fix is no longer handed to GEO-AUTO-1",
            "if(name==='home'){ loadHomeWonders(); try{ msGeoBanner(); }catch(_){} }": "Home no longer says what it chose",
            "openLocPanel('country')": "the banner lost its Change country door",
            "localStorage.removeItem('ms_user_city'); localStorage.removeItem('ms_user_country');": "an automatic choice is saved as HER pick (detection would stop for good)",
            "const _ac = localStorage.getItem('ms_auto_city')": "a return visit no longer opens where she was detected"}
    for k, why in need.items():
        if k not in js:
            bad.append(why)
    i = js.find("function _msGeoApply(")
    if i < 0 or "_msGeoOwnPick()" not in js[i:i+200]:
        bad.append("an automatic switch can override her own pick")
    return [(FAIL, "; ".join(bad))] if bad else [(INFO, "place follows the phone, then the network, never over her own pick")]

'''
s=s[:i]+new+s[k:] if s[k:].startswith("def _server_vantage_wrap") else None
assert s and "RG-0911" in s
open(p,"w",encoding="utf-8").write(s); print("ok")
