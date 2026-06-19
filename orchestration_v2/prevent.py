#!/usr/bin/env python3
"""
prevent.py - Orchestration v2 . Phase 4 (Prevent). Deterministic, zero-token.

A GUARD re-flags a fixed defect the instant it regresses; a MONITOR watches a weak point we
don't control. Any guard FAIL is written as a Detect-schema finding (findings_prevent.json) so
it re-enters Triage -> Fix - the loop closes on itself. Prevent changes nothing; it only watches.

Guards (against the deployed ms.js - each protects a shipped fix):
  G-DEMO6  renderAdvGrid honours l.per          (must contain 'const _advPer = l.per')
  G-DEMO7  renderCatCounts excludes l.paused    (>= 2 paused guards, both count paths)
  G-PHOTO  card photo source == detail          (>= 4 of (l.photos&&l.photos[0])||l.photo)
  G-PUBLISH guided listing reaches live          (dashPublish wired + go-live-before-exit guard)
Monitors:
  M-IMG    demo-image link-health               (gentle low-concurrency HEAD; reports DEAD gallery URLs)

Usage: prevent.py --check [--ms ms.js] [--demo-listings <url|file>] [--img-limit N] [--out DIR]
Cron-ready (Phase 5 schedules it); --img-limit 0 checks every gallery URL (unbounded nightly run).
"""
import argparse, datetime, json, os, sys, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

DEAD = {404, 410}
WORKERS = 5      # gentle - never hammer (the 5 Jun detect_verify lesson)
TIMEOUT = 8
RETRIES = 2


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def probe(url):
    last = None
    for i in range(RETRIES + 1):
        try:
            code = urllib.request.urlopen(
                urllib.request.Request(url, method="HEAD",
                    headers={"User-Agent": "Mozilla/5.0 (prevent-monitor)"}),
                timeout=TIMEOUT).status
            if code == 200:
                return "OK"
            if code in DEAD:
                return "DEAD"
            last = code
        except urllib.error.HTTPError as e:
            if e.code in DEAD:
                return "DEAD"
            last = e.code
        except Exception as e:
            last = e.__class__.__name__
        time.sleep(0.5 * (i + 1))
    return "TRANSIENT"   # never a clean 200 or a permanent code -> NOT counted dead


def load_demo(src):
    if not src:
        return None
    try:
        if src.startswith("http"):
            return json.loads(urllib.request.urlopen(src, timeout=12).read().decode("utf-8", "replace"))
        return json.load(open(src, encoding="utf-8"))
    except Exception as e:
        return {"_err": str(e)}


def guards(ms):
    out = []

    def g(gid, fixed, desc, ok, detail, protects):
        out.append({"id": gid, "kind": "guard", "protects": protects, "fixed_in": fixed,
                    "desc": desc, "status": "PASS" if ok else "FAIL", "detail": detail})

    c_adv = "const _advPer = l.per" in ms
    g("G-DEMO6", "S125", "renderAdvGrid honours the data's per field", c_adv,
      "found 'const _advPer = l.per'" if c_adv else "MISSING - renderAdvGrid may have reverted to a hardcoded suffix",
      "DEMO-6")
    c_pause = ms.count("DEMO-7: a paused demo listing must not inflate")
    g("G-DEMO7", "S125", "renderCatCounts excludes paused listings from tile counts", c_pause >= 2,
      "%d/2 paused guards present" % c_pause, "DEMO-7")
    c_photo = ms.count("(l.photos&&l.photos[0])||l.photo")
    g("G-PHOTO", "S123", "card photo source matches the detail view (poka-yoke)", c_photo >= 4,
      "%d card-site poka-yokes present (floor 4)" % c_photo, "S123 P2#2")
    c_pub = ("function dashPublish" in ms) and ("PREVENT-PUBLISH: go-live-before-exit" in ms)
    g("G-PUBLISH", "S138/S139", "guided listings can reach live (publish wiring + go-live-before-exit guard)", c_pub,
      "dashPublish wiring + go-live-before-exit handoff present" if c_pub else "MISSING - guided listings may strand as drafts (GUIDED-PUBLISH-1 regression)",
      "GUIDED-PUBLISH-1")
    return out


def guard_demo_pois(demo):
    """G-POI: every demo property amenity must be geographically real.
    Recomputes haversine(listing, poi.lat/lon) and checks it is within the OSM query
    radius and that the stored dist_km matches the truth. Catches the POI-CONTAM bug
    (wrong-city POIs / fabricated distances) automatically on every nightly run.
    Demo POIs carry lat/lon precisely so this check is possible; if they don't, the
    data is a legacy hand-seed and is failed as unverifiable."""
    import math as _m
    def _hav(a,b,c,d):
        R=6371.0;p1,p2=_m.radians(a),_m.radians(c);dp,dl=_m.radians(c-a),_m.radians(d-b)
        x=_m.sin(dp/2)**2+_m.cos(p1)*_m.cos(p2)*_m.sin(dl/2)**2
        return R*2*_m.atan2(_m.sqrt(x),_m.sqrt(1-x))
    if not demo or demo.get("_err"):
        return {"id":"G-POI","kind":"guard","protects":"POI-CONTAM-18JUN","fixed_in":"S140",
                "desc":"demo amenities are geographically real (true-distance verified)",
                "status":"SKIP","detail":"demo-listings unavailable: %s"%(demo.get("_err") if demo else "no source")}
    RAD=16.0; TOL=0.35; bad=[]; npoi=0
    for l in demo.get("listings",[]):
        if (l.get("cat") or "").lower()!="property" or l.get("id")=="ph_property": continue
        llat,llon=l.get("listing_lat"),l.get("listing_lng")
        p=l.get("nearby_pois") or {}
        if isinstance(p,str):
            try: p=json.loads(p)
            except Exception: p={}
        if "transit" in p: bad.append("%s legacy 'transit' key"%l.get("id"))
        for cat,items in p.items():
            for it in items:
                npoi+=1
                if "lat" not in it or "lon" not in it: bad.append("%s/%s %r no coords"%(l.get("id"),cat,it.get("name"))); continue
                if not(llat and llon): continue
                t=_hav(llat,llon,it["lat"],it["lon"])
                if t>RAD: bad.append("%s/%s %r %.0fkm away"%(l.get("id"),cat,it.get("name"),t))
                elif it.get("dist_km") is not None and abs(it["dist_km"]-t)>TOL:
                    bad.append("%s/%s %r dist %s!=%.1f"%(l.get("id"),cat,it.get("name"),it["dist_km"],t))
    ok=not bad
    return {"id":"G-POI","kind":"guard","protects":"POI-CONTAM-18JUN","fixed_in":"S140",
            "desc":"demo amenities are geographically real (true-distance verified)",
            "status":"PASS" if ok else "FAIL",
            "detail":("%d POIs verified, all real"%npoi) if ok else ("%d issue(s): "%len(bad))+"; ".join(bad[:6])}


def monitor_images(demo, limit):
    if not demo or demo.get("_err"):
        return {"id": "M-IMG", "kind": "monitor", "status": "SKIP",
                "detail": "demo-listings unavailable: %s" % (demo.get("_err") if demo else "no --demo-listings source")}
    urls = []
    for l in demo.get("listings", []):
        ph = l.get("photos") or []
        if isinstance(ph, list):
            for u in ph[1:]:
                if isinstance(u, str) and u.startswith("http"):
                    urls.append(u)
    total = len(urls)
    sample = urls[:limit] if (limit and limit > 0) else urls
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        res = list(ex.map(probe, sample))
    dead, trans, ok = res.count("DEAD"), res.count("TRANSIENT"), res.count("OK")
    return {"id": "M-IMG", "kind": "monitor", "status": "ALERT" if dead else "OK",
            "checked": len(sample), "total_gallery_urls": total, "dead": dead, "transient": trans, "ok": ok,
            "detail": "%d/%d sampled gallery URLs DEAD (gentle); %d ok, %d transient; %d gallery URLs total"
                      % (dead, len(sample), ok, trans, total)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--ms", default="ms.js")
    ap.add_argument("--demo-listings", default="")
    ap.add_argument("--img-limit", type=int, default=24)
    ap.add_argument("--out", default=os.path.dirname(os.path.abspath(__file__)))
    a = ap.parse_args()

    ms = open(a.ms, encoding="utf-8", errors="replace").read()
    checks = guards(ms)
    _demo = load_demo(a.demo_listings)
    checks.append(guard_demo_pois(_demo))
    checks.append(monitor_images(_demo, a.img_limit))
    fails = [c for c in checks if c["status"] == "FAIL"]

    report = {"schema": "prevent-v1", "generated_at": now(), "ms": a.ms,
              "summary": {"guards": sum(1 for c in checks if c["kind"] == "guard"),
                          "guards_pass": sum(1 for c in checks if c["kind"] == "guard" and c["status"] == "PASS"),
                          "guards_fail": len(fails),
                          "monitors": sum(1 for c in checks if c["kind"] == "monitor")},
              "checks": checks}
    with open(os.path.join(a.out, "prevent_checks.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2); f.write("\n")

    if fails:   # a regression -> hand it straight back to the pipeline as a Detect finding
        findings = {"detect_run": "prevent-" + now()[:10], "scope": "prevent regression guards",
                    "generated_at": now(), "engine": "Prevent v1 (Phase 4)",
                    "findings": [{"id": c["id"], "sev": "HIGH", "slice": "regression",
                                  "symptom": c["desc"] + " regressed", "root_cause": c["detail"],
                                  "file": "ms.js", "area": "fea", "root_token": c["id"].lower(),
                                  "match_terms": [c["protects"]], "proposed_lane": "green",
                                  "confidence": "confirmed"} for c in fails]}
        with open(os.path.join(a.out, "findings_prevent.json"), "w", encoding="utf-8") as f:
            json.dump(findings, f, indent=2); f.write("\n")

    s = report["summary"]
    print("prevent: %d guards (%d pass, %d FAIL), %d monitor(s)"
          % (s["guards"], s["guards_pass"], s["guards_fail"], s["monitors"]))
    for c in checks:
        print("  [%-5s] %-8s %s" % (c["status"], c["id"], c["detail"]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
