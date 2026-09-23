#!/usr/bin/env python3
"""
TrustSquare BIT Runner — the working slice of the BIT architecture.
See BIT_ARCHITECTURE.md. Runs the registry of functional + negative BITs against
the live app, applies N-of-M confirm (no false-negative cry-wolf), prints a
severity-tagged board, and is QUIET-WHEN-HEALTHY (exit 0, no noise unless --verbose).

Exit codes:  0 = all PASS   1 = S2+ confirmed FAIL   2 = S1 confirmed FAIL
Usage: python3 bit/bit_runner.py [--verbose] [--json] [--base https://trustsquare.co]
This slice is READ-ONLY: it never edits, charges, or deploys. Acting on failures
(mitigate/resolve/prevent) is the BIT Agent's job per the architecture; this proves detection.
"""
import json, sys, time, urllib.request, urllib.error, os

ROOT = os.path.dirname(os.path.abspath(__file__))
REG  = json.load(open(os.path.join(ROOT, "bit_registry.json")))
BASE = REG["_meta"]["base_url"]
for i,a in enumerate(sys.argv):
    if a=="--base" and i+1<len(sys.argv): BASE=sys.argv[i+1]
VERBOSE = "--verbose" in sys.argv
AS_JSON = "--json" in sys.argv

# -- BIT-EDGE-BLIND-1 (23 Sep 2026) -----------------------------------------
# THE BOARD CONVICTED THE APP OF SEVEN BROKEN MARKERS BECAUSE CLOUDFLARE WOULD NOT
# TALK TO IT. Measured this run: `curl https://trustsquare.co/health` -> 200, and the
# same URL through this file's urllib client -> 403, "Server: cloudflare", body
# "error code: 1010" -- Cloudflare's bad-User-Agent refusal, which fires on the
# default "Python-urllib/3.x". Every check here opens `if st != 200: return False`,
# so ONE edge refusal printed S1 B-BEA-HEALTH FAIL, six more S2 FAILs and "Worst
# severity exit=2" -- a gate that blocks, against a site that was answering 200 the
# whole time.
#
# Two changes, and the second is the one that matters:
#  (a) identify ourselves. A named UA is what the integrity check wants, and an
#      instrument probing its own site should say who it is anyway. MEASURED: curl,
#      browser and "TrustSquare-BIT" UAs all return 200; only the default is refused.
#  (b) AN EDGE REFUSAL IS NOT A VERDICT. If the edge refuses us again the board stops
#      and reports NOT MEASURED (exit 3) instead of printing failures it never earned.
#      NOT WEAKENED: a real 403 FROM THE APP still fails its marker. The signature
#      tested is Cloudflare's own (cloudflare server/cf-ray plus a 1010/1020/challenge
#      body), never "any 403".
#
# FOURTH time this repo has settled this doctrine, first time this file got it:
# RG-0187 (an instrument that cannot run reads UNVERIFIED), RG-0401/EDGE-BLIND (a
# Cloudflare refusal is BLIND, never REGRESSED), RG-0420/UPSTREAM-BLIND (an origin 502
# is blind), LEDGER-VANTAGE-BLIND-1 (an unmounted sibling project is blind).
# A false red costs the same trust as a false green, and this one carried an S1.
UA = "TrustSquare-BIT/1.0 (+https://trustsquare.co; internal build-integrity board)"
EDGE_REFUSALS = []


def _is_edge_refusal(status, body, hdrs):
    """True only for the EDGE refusing to pass us through -- never for the app's own 403."""
    if status not in (403, 503, 429):
        return False
    keys = {k.lower() for k in (hdrs or {})}
    server = ""
    for k, v in (hdrs or {}).items():
        if k.lower() == "server":
            server = str(v).lower()
    if "cloudflare" not in server and "cf-ray" not in keys:
        return False
    txt = (body or b"")[:2000].decode("utf-8", "replace").lower()
    return ("error code: 1010" in txt or "error code: 1020" in txt
            or "attention required" in txt or "checking your browser" in txt
            or "just a moment" in txt or "cf-error-details" in txt)


def _get(path, headers=None, timeout=15):
    url = BASE.rstrip("/") + path
    h = {"User-Agent": UA, "Accept": "*/*"}
    h.update(headers or {})
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        body = e.read() if hasattr(e, "read") else b""
        hdrs = dict(getattr(e, "headers", {}) or {})
        if _is_edge_refusal(e.code, body, hdrs):
            EDGE_REFUSALS.append("%s -> %s (cloudflare edge refusal; the app was not reached)"
                                 % (path, e.code))
        return e.code, body
    except Exception as e:
        return None, str(e).encode()

# ---- check implementations: each returns (ok: bool, detail: str) ----
def c_http_json(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    try: j = json.loads(body)
    except: return False, "non-JSON body"
    k, v = b["expect"]["json_key"], b["expect"]["equals"]
    return (j.get(k)==v), f"{k}={j.get(k)!r}"

def c_http_json_count(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    try: j = json.loads(body)
    except: return False, "non-JSON body"
    arr = j if isinstance(j,list) else (j.get("items") or j.get("listings") or j.get("wonders") or j.get("data") or [])
    n = len(arr); return (n >= b["expect"]["min_count"]), f"count={n}"

def c_http_shell(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    txt = body.decode("utf-8","replace"); n=len(body)
    e=b["expect"]
    if not (e["min_bytes"] < n < e["max_bytes"]): return False, f"size={n}"
    miss=[s for s in e["contains"] if s not in txt]
    return (not miss), (f"size={n} ok" if not miss else f"missing {miss}")

def c_http_status(b):
    st, _ = _get(b["path"], headers=b.get("headers"))
    return (st in b["expect"]["status_in"]), f"HTTP {st} (want {b['expect']['status_in']})"

def c_no_demo_bleed(b):
    st, body = _get(b["path"])
    if st != 200: return False, f"HTTP {st}"
    try: j=json.loads(body)
    except: return False,"non-JSON"
    arr = j if isinstance(j,list) else (j.get("items") or j.get("listings") or [])
    bleed=[str(x.get("id")) for x in arr if str(x.get("id","")).startswith(b["expect"]["no_id_prefix"])]
    return (not bleed), (f"clean ({len(arr)} live)" if not bleed else f"BLEED: {bleed[:5]}")

def _feature_ids():
    # Pull advertised AI feature ids from the live FEA bundle (ms.js / AI_FNS payload).
    # Source of truth = whatever the BEA serves to feed AI_FNS. Try /ai/functions, fall back to scraping ms.js.
    for p in ("/ai/functions","/ai-functions","/static/ms.js"):
        st, body = _get(p)
        if st==200 and body:
            txt=body.decode("utf-8","replace")
            try:
                j=json.loads(txt)
                ids=[f["id"] for f in (j if isinstance(j,list) else j.get("functions",[])) if "id" in f]
                if ids: return ids, p
            except: pass
            import re
            ids=re.findall(r'\bid["\']?\s*[:=]\s*["\']([a-z0-9_]+)["\']', txt)
            ids=[i for i in dict.fromkeys(ids) if len(i)>3][:30]
            if ids: return ids, p
    return [], None

def c_ai_example_contract(b):
    ids, src = _feature_ids()
    if not ids: return False, "could not enumerate AI feature ids"
    broken=[]
    for fid in ids:
        st,_ = _get(b["path"]+fid)
        if st != 200: broken.append(f"{fid}:{st}")
    if broken:
        return False, f"{len(broken)}/{len(ids)} example endpoints not OK -> {broken[:6]}"
    return True, f"{len(ids)} example endpoints OK (src {src})"

CHECKS={"http_json":c_http_json,"http_json_count":c_http_json_count,"http_shell":c_http_shell,
        "http_status":c_http_status,"no_demo_bleed":c_no_demo_bleed,"ai_example_contract":c_ai_example_contract}

def run_one(b):
    fn=CHECKS.get(b["check"])
    if not fn: return "ERROR", f"no check impl '{b['check']}'"
    need=b.get("confirm",1); ok_runs=0; last=""
    # N-of-M confirm: require `need` passes; a single fail that doesn't reach `need` passes is provisional.
    attempts=need+1
    for _ in range(attempts):
        ok,detail=fn(b); last=detail
        if ok: ok_runs+=1
        if ok_runs>=need: return "PASS", detail
        if not ok: time.sleep(0.4)
    return "FAIL", last

def main():
    results=[]; worst=0
    for b in REG["bits"]:
        state,detail=run_one(b)
        results.append({"id":b["id"],"sev":b["severity"],"type":b["type"],"state":state,"detail":detail,"desc":b["desc"]})
        if state=="FAIL": worst=max(worst, 2 if b["severity"]=="S1" else 1)
    fails=[r for r in results if r["state"]!="PASS"]
    # BIT-EDGE-BLIND-1: if the edge refused us at any point this board measured NOTHING.
    # Exit 3 = NOT MEASURED, deliberately neither 0 (healthy) nor 1/2 (confirmed fail), so
    # no caller and no stand-up can read a refusal as good news or as a real regression.
    if EDGE_REFUSALS:
        if AS_JSON:
            print(json.dumps({"base": BASE, "state": "NOT MEASURED",
                              "reason": "cloudflare edge refusal",
                              "refusals": EDGE_REFUSALS[:10],
                              "markers_unread": len(fails), "markers_total": len(results),
                              "note": "instrument limit, not a verdict -- the app was never "
                                      "reached. Re-run from a vantage the edge allows."},
                             indent=2))
        else:
            print("[BIT] NOT MEASURED against %s -- the Cloudflare edge refused this client "
                  "(%s). The app was never reached, so nothing here is a verdict; %d of %d "
                  "markers went unread. Re-run from a vantage the edge allows."
                  % (BASE, EDGE_REFUSALS[0], len(fails), len(results)))
        return 3
    if AS_JSON:
        print(json.dumps({"base":BASE,"worst":worst,"results":results},indent=2)); return worst
    if not fails and not VERBOSE:
        print(f"[BIT] all {len(results)} markers PASS against {BASE} — healthy (quiet)."); return 0
    print(f"\n=== TrustSquare BIT board — {BASE} ===")
    for r in results:
        if r["state"]=="PASS" and not VERBOSE: continue
        tag={"PASS":"[OK]  ","FAIL":"[FAIL]","ERROR":"[ERR] "}[r["state"]]
        print(f"  {tag} {r['sev']} {r['id']:<18} ({r['type']:<10}) {r['detail']}")
    if fails:
        print(f"\n  {len(fails)} marker(s) need attention. Worst severity exit={worst}.")
        for r in fails:
            print(f"    - {r['id']} [{r['sev']}]: {r['desc']}")
    else:
        print(f"  all {len(results)} PASS.")
    return worst

if __name__=="__main__":
    sys.exit(main())
