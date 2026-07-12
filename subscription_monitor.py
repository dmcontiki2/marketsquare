#!/usr/bin/env python3
"""
subscription_monitor.py - TrustSquare dependency / subscription health monitor.
Deterministic, zero-token, zero-paid-call (RM-4 tiering: sensing -> Python/shell).

Enumerates every external dependency (grouped into David's categories: AI, Cars, Coins,
Stamps, Cards/Collectibles, Properties, Maps, Regulations, Forex, Servers, Payments, Email,
CDN, Storage) and records per item: status today (UP/DEGRADED/DOWN/HELD/STANDBY/PLANNED),
reachability, key state, enabled (from feature_flags.json), billing, rolling uptime over the
last N daily samples, and last-downtime date.

HONESTY RULES (so a red always means something):
  * Provider enable/disable is READ from feature_flags.json - the app's own registry.
  * Reachability uses UNAUTHENTICATED HEAD/GET; 401/403/404 == reachable (no paid quota burnt).
  * RED (DOWN/DEGRADED) is driven ONLY by reachability + service/infra health, NEVER by a key.
  * Keys are annotated ok / unverified. msdeploy cannot read root-only *.conf drop-ins, so an
    unfound key is 'unverified' (may live in a root conf), NOT 'missing' - it never forces a red.
  * Paid/contract providers switched off in feature_flags = HELD (intentional). Dormant failover
    (OpenAI when AI_ACTIVE=anthropic) or optional keys = STANDBY. Neither counts as an outage.

Writes orchestrator/subscription_status.json (+ appends subscription_history.json for uptime).
--json prints the snapshot for folding into findings/report.
"""
import os, sys, json, ssl, socket, subprocess, datetime, urllib.request, urllib.error

ORCH = "/var/www/marketsquare/orchestrator"
FLAGS = "/var/www/marketsquare/feature_flags.json"
DOTENV = "/var/www/marketsquare/.env"
STATUS_OUT = os.path.join(ORCH, "subscription_status.json")
HISTORY = os.path.join(ORCH, "subscription_history.json")
TODAY = datetime.date.today().isoformat()
NOW = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
UA = {"User-Agent": "trustsquare-submon/1.0"}
OPTIONAL_IDS = {"openai", "wonder_ai"}   # dormant failover / optional - unverified key => STANDBY not red

def ping(url, timeout=6):
    if not url:
        return ("PLANNED", "no endpoint")
    ctx = ssl.create_default_context()
    last = "unreachable"
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as r:
                return ("UP", "HTTP %s" % r.status)
        except urllib.error.HTTPError as e:
            return ("DEGRADED" if e.code >= 500 else "UP", "HTTP %s" % e.code)
        except urllib.error.URLError as e:
            last = str(getattr(e, "reason", e)); continue
        except Exception as e:
            last = str(e); continue
    return ("DOWN", last)

def svc_active(name):
    try:
        return subprocess.run(["systemctl", "is-active", name],
                              capture_output=True, text=True, timeout=8).stdout.strip() or "unknown"
    except Exception:
        return "unknown"

def local_http(port, path="/health"):
    return ping("http://127.0.0.1:%s%s" % (port, path), timeout=5)

def redis_ok():
    try:
        return subprocess.run(["redis-cli", "ping"], capture_output=True, text=True, timeout=6).stdout.strip() == "PONG"
    except Exception:
        return False

def ssl_days(host="trustsquare.co", port=443):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.create_connection((host, port), timeout=8), server_hostname=host) as s:
            na = s.getpeercert()["notAfter"]
        exp = datetime.datetime.strptime(na, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=datetime.timezone.utc)
        return (exp - datetime.datetime.now(datetime.timezone.utc)).days
    except Exception:
        return None

def disk_free_pct(path="/"):
    try:
        import shutil
        t, u, f = shutil.disk_usage(path)
        return round(100.0 * f / t, 1)
    except Exception:
        return None

def all_env_keys(*services):
    """Union every env-var NAME visible to msdeploy: own environ + inline Environment= of the
    services + names in the readable .env. Root-only *.conf drop-ins are invisible by design ->
    keys that live only there read as 'unverified', never 'missing'."""
    keys = set(os.environ.keys())
    for svc in services:
        try:
            out = subprocess.run(["systemctl", "show", svc, "-p", "Environment"],
                                 capture_output=True, text=True, timeout=8).stdout
            body = out.split("=", 1)[1] if "=" in out else ""
            for tok in body.split():
                if "=" in tok:
                    keys.add(tok.split("=", 1)[0])
        except Exception:
            pass
    try:
        if os.access(DOTENV, os.R_OK):
            for line in open(DOTENV):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    keys.add(line.split("=", 1)[0])
    except Exception:
        pass
    return keys

def load_flags():
    try:
        d = json.load(open(FLAGS))
        return d.get("providers", {}), bool(d.get("paid_tiers_enabled", False))
    except Exception:
        return {}, False

# id, category, name, why, url(safe ping / "" if none), auth_env, billing, flag(feature_flags id or None=core)
CATALOG = [
  ("anthropic","AI","Anthropic (Claude)","Primary LLM - every AI feature (coach, vision, dossiers)","https://api.anthropic.com/v1/models","ANTHROPIC_API_KEY","paid-metered",None),
  ("openai","AI","OpenAI (failover)","LLM failover seam (ai_provider AI_ACTIVE)","https://api.openai.com/v1/models","OPENAI_API_KEY","paid-metered",None),
  ("wonder_ai","AI","Wonder/Heritage AI","Optional heritage-enrichment AI key","","WONDER_AI_KEY","paid-metered",None),
  ("transunion_auto","Cars","TransUnion Auto (ZA)","Vehicle valuation/verification data","https://www.transunion.co.za/","","paid-contract","transunion_auto"),
  ("redbook","Cars","RedBook","Vehicle price guide","","","paid-contract","redbook"),
  ("numista","Coins","Numista","Coin & banknote catalogue","https://api.numista.com/","NUMISTA_API_KEY","free-key","numista"),
  ("pcgs","Coins","PCGS","Graded-coin price guide","","","paid-contract","pcgs"),
  ("scryfall","Cards/Collectibles","Scryfall","MTG card catalogue & pricing","https://api.scryfall.com/","","free","scryfall"),
  ("justtcg_free","Cards/Collectibles","JustTCG (free)","Trading-card pricing","https://api.justtcg.com/","JUSTTCG_API_KEY","free-key","justtcg_free"),
  ("bricklink","Cards/Collectibles","BrickLink","LEGO catalogue & price guide","https://api.bricklink.com/","","free-oauth","bricklink"),
  ("ebay_browse","Cards/Collectibles/Stamps","eBay Browse","Sold-comps for collectibles/stamps/coins","https://api.ebay.com/","","free-oauth","ebay_browse"),
  ("pricecharting","Cards/Collectibles","PriceCharting","Collectible price guide","","","paid-contract","pricecharting"),
  ("gocollect","Cards/Collectibles","GoCollect","Comics/collectibles pricing","","","paid-contract","gocollect"),
  ("watchcharts","Cards/Collectibles","WatchCharts","Watch price data","","","paid-contract","watchcharts"),
  ("land_registry","Properties","UK Land Registry","UK sold-price open data","http://landregistry.data.gov.uk/","","open","land_registry"),
  ("ons_voa","Properties","ONS / VOA","UK rents & valuation open data","https://www.ons.gov.uk/","","open","ons_voa"),
  ("hud_fmr","Properties","HUD FMR","US fair-market-rent open data","https://www.huduser.gov/","","open","hud_fmr"),
  ("us_assessor","Properties","US Assessor","US county assessor data","","","open","us_assessor"),
  ("payprop_tpn","Properties","PayProp / TPN","ZA rental payment data","","","paid-contract","payprop_tpn"),
  ("internal_comps","Properties","Internal comps","Own listing comparables","","","owned","internal_comps"),
  ("lightstone","Properties","Lightstone","ZA property (& auto) data","","","paid-contract","lightstone"),
  ("propertydata","Properties","PropertyData","UK property analytics","","","paid-contract","propertydata"),
  ("rentcast","Properties","RentCast","US rent estimates","","","paid-contract","rentcast"),
  ("attom","Properties","ATTOM","US property data","","","paid-contract","attom"),
  ("domain","Properties","Domain","AU property data","","","paid-contract","domain"),
  ("corelogic","Properties","CoreLogic","AU/US property data","","","paid-contract","corelogic"),
  ("sqm","Properties","SQM Research","AU rental data","","","paid-contract","sqm"),
  ("caphpi","Properties","Cap HPI","Property/asset index","","","paid-contract","caphpi"),
  ("loom","Properties","Loom","Property data","","","paid-contract","loom"),
  ("overpass","Maps","OSM Overpass","Points-of-interest for listings","https://overpass-api.de/api/status","","free",None),
  ("nominatim","Maps","OSM Nominatim","Geocoding / address lookup","https://nominatim.openstreetmap.org/","","free",None),
  ("geonames","Maps","GeoNames","Country/region/city/suburb hierarchy","http://api.geonames.org/","GEONAMES_USERNAME","free-key",None),
  ("wikidata","Regulations/Heritage","Wikidata","World-heritage & site reference data","https://www.wikidata.org/","","free",None),
  ("reg_compliance","Regulations/Heritage","Reg-compliance feed","POPIA/FSCA/CPA/SATMS monitoring - no data subscription yet (legal-counsel track)","","","planned",None),
  ("frankfurter","Forex","Frankfurter (ECB)","Currency conversion rates","https://api.frankfurter.dev/v1/latest","","free",None),
  ("er_api","Forex","ExchangeRate-API (open)","Currency conversion fallback","https://open.er-api.com/v6/latest/USD","","free",None),
  ("paystack","Payments","Paystack","Checkout & Tuppence top-ups (TEST mode pre-CIPC)","https://api.paystack.co/","PAYSTACK_SECRET_KEY","paid-per-txn",None),
  ("resend","Email","Resend","Transactional & magic-link email","https://api.resend.com/","RESEND_API_KEY","paid-metered",None),
  ("cloudflare","CDN","Cloudflare","CDN + cache purge for trustsquare.co","https://api.cloudflare.com/client/v4/","CF_CACHE_TOKEN","free-tier",None),
  ("r2","Storage","Cloudflare R2","Media object storage (photos/videos)","https://pub-3c51d058a6494b93af4d242d07bdc4da.r2.dev/","HETZNER_S3_ACCESS_KEY","paid-metered",None),
  ("github","Servers","GitHub mirror","Off-box code backup","https://github.com/dmcontiki2/marketsquare","","free",None),
]

def classify(item, providers, env_keys):
    pid, cat, name, why, url, auth, billing, flag = item
    enabled = bool(providers.get(flag, False)) if flag is not None else True
    key_needed = bool(auth)
    key_state = "n/a" if not key_needed else ("ok" if auth in env_keys else "unverified")
    base = dict(id=pid, category=cat, name=name, why=why, enabled=enabled,
                key_needed=key_needed, key_state=key_state, billing=billing, optional=pid in OPTIONAL_IDS)
    # paid/contract provider deliberately OFF -> HELD (intentional, not a fault)
    if flag is not None and not enabled:
        base.update(status="HELD", detail="off in feature_flags (paid/contract - awaits B7 sign-off)"); return base
    if billing == "planned":
        base.update(status="PLANNED", detail="no subscription/endpoint yet"); return base
    if not url:
        # internal/owned, or key-only surface with nothing to ping
        if pid in OPTIONAL_IDS and key_state != "ok":
            base.update(status="STANDBY", detail="optional - key %s" % key_state)
        else:
            base.update(status="UP", detail=("internal/owned" if not key_needed else "key %s" % key_state))
        return base
    state, detail = ping(url)                    # reachability drives red, never the key
    if state == "UP" and pid in OPTIONAL_IDS and key_state != "ok":
        state, detail = "STANDBY", "%s; optional key %s" % (detail, key_state)
    elif key_needed:
        detail = "%s; key %s" % (detail, key_state)
    base.update(status=state, detail=detail); return base

def infra_section():
    rows = []
    for s in ["marketsquare", "citylauncher", "advertagent", "nginx", "redis-server"]:
        st = svc_active(s)
        rows.append(dict(id=s, category="Servers", name=s, why="systemd service",
                         status="UP" if st == "active" else "DOWN", detail="systemctl:%s" % st,
                         enabled=True, key_needed=False, key_state="n/a", billing="owned", optional=False))
    for label, port, pth in [("BEA:8000", 8000, "/health"), ("CityLauncher:8001", 8001, "/health"), ("AdvertAgent:8002", 8002, "/")]:
        state, detail = local_http(port, pth)
        rows.append(dict(id=label, category="Servers", name=label, why="app HTTP port", status=state,
                         detail=detail, enabled=True, key_needed=False, key_state="n/a", billing="owned", optional=False))
    rows.append(dict(id="redis", category="Servers", name="Redis", why="cache/session store",
                     status="UP" if redis_ok() else "DOWN", detail="PONG" if redis_ok() else "no ping",
                     enabled=True, key_needed=False, key_state="n/a", billing="owned", optional=False))
    days = ssl_days(); dfp = disk_free_pct()
    rows.append(dict(id="ssl_cert", category="Servers", name="TLS cert (trustsquare.co)", why="HTTPS certificate",
                     status=("UP" if (days or 0) > 14 else "DEGRADED" if (days or 0) > 0 else "DOWN"),
                     detail=("%s days left" % days) if days is not None else "probe failed",
                     enabled=True, key_needed=False, key_state="n/a", billing="owned", optional=False))
    rows.append(dict(id="disk", category="Servers", name="Server disk (/)", why="Hetzner box free space",
                     status=("UP" if (dfp or 0) > 10 else "DEGRADED"),
                     detail=("%s%% free" % dfp) if dfp is not None else "unknown",
                     enabled=True, key_needed=False, key_state="n/a", billing="owned", optional=False))
    return rows

NON_OUTAGE = ("UP", "HELD", "PLANNED", "STANDBY")
def rolling(history, pid, today_status):
    samples = [(rec.get("date"), rec["results"][pid]) for rec in history[-30:] if pid in rec.get("results", {})]
    samples.append((TODAY, today_status))
    up = sum(1 for _, s in samples if s in NON_OUTAGE)
    downs = [d for d, s in samples if s not in NON_OUTAGE]
    return dict(samples=len(samples), uptime_pct=round(100.0 * up / len(samples), 1), last_downtime=(downs[-1] if downs else None))

def main():
    providers, paid_on = load_flags()
    env_keys = all_env_keys("marketsquare", "advertagent", "citylauncher")
    results = [classify(it, providers, env_keys) for it in CATALOG] + infra_section()

    try:
        history = json.load(open(HISTORY)) if os.path.exists(HISTORY) else []
    except Exception:
        history = []
    history = [h for h in history if h.get("date") != TODAY]

    for r in results:
        r["rolling"] = rolling(history, r["id"], r["status"])

    counts = {}
    for r in results:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    issues = ["%s (%s): %s" % (r["name"], r["category"], r["detail"]) for r in results if r["status"] in ("DOWN", "DEGRADED")]
    unverified = sorted({r["name"] for r in results if r.get("key_state") == "unverified"})

    snapshot = {"generated_at": NOW, "date": TODAY, "paid_tiers_enabled": paid_on, "counts": counts,
                "issues": issues, "keys_unverified": unverified, "items": results}
    json.dump(snapshot, open(STATUS_OUT, "w"), indent=2)
    history.append({"date": TODAY, "results": {r["id"]: r["status"] for r in results}})
    json.dump(history[-60:], open(HISTORY, "w"), indent=2)

    if "--json" in sys.argv:
        print(json.dumps(snapshot, indent=2)); return

    order = ["AI","Cars","Coins","Cards/Collectibles","Cards/Collectibles/Stamps","Properties","Maps","Regulations/Heritage","Forex","Payments","Email","CDN","Storage","Servers"]
    icon = {"UP":"[UP ]","DEGRADED":"[DEG]","DOWN":"[DOWN]","HELD":"[HELD]","STANDBY":"[STBY]","PLANNED":"[PLAN]"}
    print("TrustSquare subscription/dependency monitor - %s" % TODAY)
    print("counts:", ", ".join("%s=%s" % (k, v) for k, v in sorted(counts.items())))
    print("ISSUES:", (" | ".join(issues) if issues else "none - no outages"))
    if unverified:
        print("keys unverified (may live in root-only conf; not an outage):", ", ".join(unverified))
    print("-" * 98)
    seen = set()
    for cat in order + sorted({r["category"] for r in results}):
        if cat in seen: continue
        seen.add(cat)
        rows = [r for r in results if r["category"] == cat]
        if not rows: continue
        print("### %s" % cat)
        for r in rows:
            rr = r["rolling"]
            print("  %s %-26s %-9s %-40s uptime %s%% (%sd)%s" % (
                icon.get(r["status"], "[?]"), r["name"], r["status"], r["detail"][:40],
                rr["uptime_pct"], rr["samples"], (" last-down %s" % rr["last_downtime"]) if rr["last_downtime"] else ""))
    print("-" * 98)
    print("wrote %s (+ history)" % STATUS_OUT)

if __name__ == "__main__":
    main()
