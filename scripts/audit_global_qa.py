#!/usr/bin/env python3
"""audit_global_qa.py — TrustSquare global-launch QA audit (v1, 11 Jul 2026, David-approved).
Machine-checkable sweep of the LIVE app + local repo for exactly the launch-killers David
named: dead ends, wrong linking, missing info, demo integrity, locale wrongness, deploy drift.
Sandbox-runnable: stdlib only, no ssh. Findings -> AUDIT_GLOBAL_QA/findings-<date>.json + LATEST.md.
Exit 0 always (reporting tool, never blocks). Run:  python3 scripts/audit_global_qa.py
"""
import json, re, os, sys, time, hashlib, urllib.request, urllib.parse, datetime

BASE = "https://trustsquare.co"
UA = {"User-Agent": "TrustSquare-QA-Audit/1.0 (dmcontiki2@gmail.com)"}
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTDIR = os.path.join(REPO, "AUDIT_GLOBAL_QA")
FINDINGS = []

def add(sev, area, fid, msg):
    FINDINGS.append({"sev": sev, "area": area, "id": fid, "msg": msg})

def get(url, timeout=20, binary=False):
    req = urllib.request.Request(url, headers=UA)
    d = urllib.request.urlopen(req, timeout=timeout).read()
    return d if binary else d.decode("utf-8", errors="replace")

def head_ok(url, timeout=12):
    try:
        req = urllib.request.Request(url, headers=UA, method="HEAD")
        r = urllib.request.urlopen(req, timeout=timeout)
        return 200 <= r.status < 400
    except Exception:
        try:  # some hosts refuse HEAD
            req = urllib.request.Request(url, headers=UA)
            r = urllib.request.urlopen(req, timeout=timeout)
            return 200 <= r.status < 400
        except Exception:
            return False

# ── 1 · endpoint pulse ───────────────────────────────────────────────────────
def audit_endpoints():
    for ep in ("/health", "/ai/health", "/demo-listings", "/demo-sellers", "/support"):
        try:
            get(BASE + ep)
        except Exception as e:
            add("CRITICAL", "endpoints", f"EP-{ep}", f"{ep} unreachable: {e}")

# ── 2 · demo integrity (lister wiring, placeholders, missing info) ──────────
def audit_demo():
    try:
        dl = json.loads(get(BASE + "/demo-listings"))["listings"]
        ds = json.loads(get(BASE + "/demo-sellers"))["sellers"]
    except Exception as e:
        add("CRITICAL", "demo", "DEMO-FETCH", f"demo feeds unreadable: {e}"); return
    by_idx = {}
    for s in ds:
        if "idx" in s: by_idx[s["idx"]] = s
    unindexed = sum(1 for s in ds if "idx" not in s)
    if unindexed:
        add("HIGH", "demo", "DEMO-SELLER-SCHEMA",
            f"{unindexed}/{len(ds)} sellers have NO idx field (schema drift: credentials/ stats-object style) — "
            "position-based lookups mis-resolve; FEA v284 resolves by idx field, but the data should be repaired too")
    used = {}
    for l in dl:
        si = l.get("sellerIdx")
        if si is None: continue
        used[si] = used.get(si, 0) + 1
        s = by_idx.get(si)
        if s is None:
            add("HIGH", "demo", f"DEMO-LISTER-MISSING-{si}",
                f"sellerIdx {si} used by listings but no seller with that idx field exists")
        else:
            lc = str(l.get("cat") or l.get("category") or "").lower().replace("_","").replace("localmarket","local_market".replace("_",""))
            sc = str(s.get("cat") or "").lower().replace("_","")
            # adventures subcats (experiences/accommodation) share the Adventures sellers by design
            if lc.startswith("adventures"): lc = "adventures"
            if sc.startswith("adventures"): sc = "adventures"
            if lc and sc and lc != sc:
                add("MEDIUM", "demo", f"DEMO-CROSSWIRE-{l.get('id')}",
                    f"listing {l.get('id')} cat={l.get('cat') or l.get('category')} -> seller idx {si} cat={s.get('cat')} (category cross-wire)")
    for si, n in sorted(used.items()):
        if si not in by_idx:
            pass  # already flagged
    ph = [l for l in dl if "coming soon" in str(l.get("title","")).lower()]
    if ph:
        add("INFO", "demo", "DEMO-PLACEHOLDERS", f"{len(ph)} 'coming soon' placeholder listings present (by design; verify they stay out of counts)")
    props = [l for l in dl if str(l.get("cat") or l.get("category","")).lower().startswith("prop")]
    nop = [l.get("id") for l in props if not l.get("nearby_pois") and not str(l.get("id","")).startswith("ph_")]  # ph_ placeholders exempt, same as missing-info sweep
    if nop and props:
        add("MEDIUM", "demo", "DEMO-POIS-MISSING", f"{len(nop)}/{len(props)} property listings missing nearby_pois (e.g. {nop[:4]})")
    # missing-info sweep: fields every sellable card needs
    for f in ("title", "price"):
        miss = [l.get("id") for l in dl if not str(l.get(f,"")).strip() and not str(l.get("id","")).startswith("ph_")]
        if miss:
            add("HIGH", "demo", f"DEMO-MISSING-{f.upper()}", f"{len(miss)} listings missing {f}: {miss[:5]}")

# ── 3 · locale / currency sanity per demo city ───────────────────────────────
CITY_CCY = {"new york": "$", "london": "£", "sydney": "A$"}
def audit_locale():
    try:
        dl = json.loads(get(BASE + "/demo-listings"))["listings"]
    except Exception:
        return
    bad = []
    for l in dl:
        city = str(l.get("city","")).lower()
        price = str(l.get("price",""))
        for c, sym in CITY_CCY.items():
            if c in city and price and sym not in price and not price.strip().isdigit():
                if "R " in price or price.startswith("R"):
                    bad.append((l.get("id"), city, price[:20]))
    if bad:
        add("HIGH", "locale", "LOCALE-CCY", f"{len(bad)} international demo listings priced in Rand: {bad[:5]}")

# ── 4 · dead ends: goTo() targets vs screens in the shipped HTML ─────────────
def audit_deadends():
    try:
        html = open(os.path.join(REPO, "marketsquare.html"), encoding="utf-8").read()
        js = open(os.path.join(REPO, "ms.js"), encoding="utf-8").read()
    except Exception as e:
        add("MEDIUM", "deadends", "SRC-READ", f"local sources unreadable: {e}"); return
    screens = set(re.findall(r"id=\"screen-([a-z0-9\-_]+)\"", html)) | set(re.findall(r"id='screen-([a-z0-9\-_]+)'", html))
    screens |= set(re.findall(r"id=\"screen-([a-z0-9\-_]+)\"", js)) | set(re.findall(r"id='screen-([a-z0-9\-_]+)'", js))
    targets = set(re.findall(r"goTo\('([a-z0-9\-_]+)'\)", js))
    dyn = set(t for t in targets if "$" in t or "+" in t)
    missing = sorted(t for t in targets - dyn if t not in screens)
    if missing:
        add("HIGH", "deadends", "NAV-DEADEND", f"goTo() targets with no screen-<id> found: {missing}")

# ── 5 · wrong/dead links: hardcoded externals in FEA + demo data ─────────────
def audit_links(cap=25):
    try:
        js = open(os.path.join(REPO, "ms.js"), encoding="utf-8").read()
    except Exception:
        return
    urls = sorted(set(re.findall(r"https?://[a-zA-Z0-9./_%\-?=&#]+", js)))
    urls = [u for u in urls if "trustsquare.co" not in u and "localhost" not in u
            and not any(s in u for s in ("openstreetmap.org/{", "{z}", "unsplash", "w3.org", "images."))]
    dead = []
    for u in urls[:cap]:
        if not head_ok(u):
            dead.append(u)
        time.sleep(0.3)
    if dead:
        add("MEDIUM", "links", "LINKS-DEAD", f"{len(dead)} hardcoded external links failing (checked {min(len(urls),cap)}): {dead[:6]}")

# ── 6 · deploy drift: served asset bytes vs repo bytes ───────────────────────
def audit_drift():
    try:
        idx = get(BASE + "/")
    except Exception as e:
        add("CRITICAL", "drift", "INDEX-FETCH", f"live index unreachable: {e}"); return
    m = re.search(r"static/ms\.js\?v=(\d+)", idx)
    mc = re.search(r"static/ms\.css\?v=(\d+)", idx)
    if not m:
        add("HIGH", "drift", "INDEX-NOJS", "live index has no static/ms.js?v= reference"); return
    v = m.group(1)
    try:
        live = get(f"{BASE}/static/ms.js?v={v}", binary=True)
        local = open(os.path.join(REPO, "ms.js"), "rb").read()
        if hashlib.md5(live).hexdigest() != hashlib.md5(local).hexdigest():
            add("INFO", "drift", "MSJS-DRIFT",
                f"live ms.js (v{v}, {len(live)}B) != repo ms.js ({len(local)}B) — expected while a deploy is staged; "
                "CRITICAL if it persists after deploying")
    except Exception as e:
        add("MEDIUM", "drift", "MSJS-FETCH", f"served ms.js unreadable: {e}")
    lv = re.search(r"ms\.js\?v=(\d+)", open(os.path.join(REPO, "marketsquare.html"), encoding="utf-8").read())
    if lv and lv.group(1) != v:
        add("INFO", "drift", "VERSION-KEY", f"repo html pins ms.js v{lv.group(1)}, live pins v{v} (deploy pending)")

# ── run + report ─────────────────────────────────────────────────────────────
def main():
    t0 = time.time()
    for fn in (audit_endpoints, audit_demo, audit_locale, audit_deadends, audit_links, audit_drift):
        try:
            fn()
        except Exception as e:
            add("MEDIUM", "harness", f"HARNESS-{fn.__name__}", f"auditor crashed (audit itself, not the app): {e}")
    os.makedirs(OUTDIR, exist_ok=True)
    day = datetime.date.today().isoformat()
    out = {"date": day, "took_s": round(time.time()-t0,1), "findings": FINDINGS}
    prev_path = os.path.join(OUTDIR, "findings-latest.json")
    prev_ids = set()
    if os.path.exists(prev_path):
        try: prev_ids = {f["id"] for f in json.load(open(prev_path))["findings"]}
        except Exception: pass
    new = [f for f in FINDINGS if f["id"] not in prev_ids]
    json.dump(out, open(os.path.join(OUTDIR, f"findings-{day}.json"), "w"), indent=1)
    json.dump(out, open(prev_path, "w"), indent=1)
    sev_rank = {"CRITICAL":0,"HIGH":1,"MEDIUM":2,"INFO":3}
    lines = [f"# Global QA audit — {day} ({out['took_s']}s)", "",
             f"**{len(FINDINGS)} findings** ({len(new)} new vs previous run)", ""]
    for f in sorted(FINDINGS, key=lambda x: sev_rank.get(x["sev"],9)):
        tag = "🆕 " if f["id"] in {n["id"] for n in new} else ""
        lines.append(f"- **{f['sev']}** [{f['area']}] {tag}`{f['id']}` — {f['msg']}")
    if not FINDINGS:
        lines.append("- ✅ clean run — no findings")
    open(os.path.join(OUTDIR, "LATEST.md"), "w", encoding="utf-8").write("\n".join(lines)+"\n")
    print("\n".join(lines))

if __name__ == "__main__":
    main()
