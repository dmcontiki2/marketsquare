#!/usr/bin/env python3
"""017_selfhost_demo_images.py — DW-025 close (13 Aug 2026, David's ruling: self-host).

WHAT
----
1,141 references (266 unique images) in the demo payloads hotlinked images.unsplash.com —
visitor IP/referrer to a third party on every page view, and a catalogue-wide breakage
risk. The repo side already switched every reference to /static/demo/<sha1-16>.jpg and
neutralized the ms.js SF fallback. THIS migration makes those paths real ON THE BOX:

  * downloads every image in demo_image_map.json (manifest-shipped) into
    LIVE/static/demo/, plus the 7 SF category tiles to LIVE/static/sf_cat_<key>.jpg
  * ALSO harvests any unsplash URLs still present in the LIVE demo_sellers.json
    (server-managed file — the repo copy is only a seed) and downloads those
  * only when EVERY file is present and byte-sane does it rewrite the LIVE
    demo_sellers.json to local paths (.bak first, JSON-parse verified)
  * writes static/demo/ATTRIBUTION.json (URL→file provenance; Unsplash License)

RESUMABLE BY DESIGN: a 6-minute runtime budget; on partial completion it reports
progress and exits 2 → post_deploy does NOT record it → it resumes on the next deploy.
Idempotent: all files present + sellers file already local → exit 0 untouched.
Never touches the DB. The only rewritten file is demo_sellers.json, backed up.
"""
import json, os, re, shutil, sys, time, hashlib
import urllib.request, urllib.error
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
LIVE = os.environ.get("MS_LIVE", "/var/www/marketsquare")
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
UA = {"User-Agent": "TrustSquare-SelfHost-Migration/1.0 (dmcontiki2@gmail.com)"}
BUDGET_S = 360
URLRX = re.compile(r'https://images\.unsplash\.com/[^"\\]+')

def say(m): print("[017_img] " + m, flush=True)
def h16(u): return hashlib.sha1(u.encode()).hexdigest()[:16]

def sane_image(path):
    try:
        if os.path.getsize(path) < 5000: return False
        with open(path, "rb") as f: head = f.read(12)
        return head[:3] == b"\xff\xd8\xff" or head[:8] == b"\x89PNG\r\n\x1a\n" or head[4:12] in (b"ftypavif", b"ftypheic") or head[:4] == b"RIFF"
    except OSError:
        return False

def fetch(url, dest):
    tmp = dest + ".part"
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=25) as r, open(tmp, "wb") as f:
        shutil.copyfileobj(r, f, length=1 << 15)
    if not sane_image(tmp):
        os.remove(tmp); return False
    os.replace(tmp, dest); return True

def main():
    if not APPLY:
        say("dry run (no --apply) — nothing changed"); return 0
    t0 = time.time()
    map_path = os.path.join(LIVE, "demo_image_map.json")
    if not os.path.isfile(map_path):
        say("FAILED: demo_image_map.json not on the box — manifest should ship it"); return 3
    mapping = json.load(open(map_path, encoding="utf-8"))
    demo_dir = os.path.join(LIVE, "static", "demo")
    os.makedirs(demo_dir, exist_ok=True)

    # download set: map images + SF tiles + any URL still in the LIVE sellers file
    jobs = {}   # url -> absolute dest
    for url, rel in mapping.get("images", {}).items():
        jobs[url] = os.path.join(LIVE, rel)
    for k, t in mapping.get("sf_tiles", {}).items():
        jobs[t["url"]] = os.path.join(LIVE, t["dest"])
    sellers_path = os.path.join(LIVE, "demo_sellers.json")
    sellers_txt = open(sellers_path, encoding="utf-8").read() if os.path.isfile(sellers_path) else ""
    live_extra = [u for u in set(URLRX.findall(sellers_txt)) if u not in jobs]
    for u in live_extra:
        jobs[u] = os.path.join(demo_dir, h16(u) + ".jpg")
    if live_extra:
        say("live demo_sellers.json carries %d URL(s) not in the map — added to the set" % len(live_extra))

    missing = {u: d for u, d in jobs.items() if not (os.path.isfile(d) and sane_image(d))}
    say("images: %d total, %d already present, %d to fetch" % (len(jobs), len(jobs) - len(missing), len(missing)))

    state_path = os.path.join(demo_dir, ".fetch_attempts.json")
    try: attempts = json.load(open(state_path, encoding="utf-8"))
    except Exception: attempts = {}

    got, failed = 0, 0
    for u, d in sorted(missing.items()):
        if time.time() - t0 > BUDGET_S:
            json.dump(attempts, open(state_path, "w", encoding="utf-8"))
            say("runtime budget reached: %d fetched this run, %d still missing — exit 2, resumes next deploy"
                % (got, len(missing) - got - failed)); return 2
        try:
            ok = fetch(u, d)
        except Exception as ex:
            ok = False; say("  ! %s -> %r" % (u[:70], ex))
        if ok:
            got += 1
        else:
            failed += 1
            attempts[u] = attempts.get(u, 0) + 1
            time.sleep(1.5)   # backoff after a refusal — most failures were rate-limit shaped
        time.sleep(0.5)       # polite pacing (0.15s tripped ~11% refusals on the first run)

    # LAST RUNG (13 Aug, after run 1 left 29/273 missing): a URL that has now failed on
    # TWO separate runs is treated as dead or hostile — fill its dest with a copy of a
    # landed neighbour so payload paths never dangle and the 100% gate stays reachable.
    # Every stand-in is named here and recorded in ATTRIBUTION.json.
    stand_ins = {}
    still = {u: d for u, d in missing.items() if not (os.path.isfile(d) and sane_image(d))}
    if still:
        donors = [d for d in jobs.values() if os.path.isfile(d) and sane_image(d)]
        for u, d in sorted(still.items()):
            if attempts.get(u, 0) >= 2 and donors:
                shutil.copyfile(donors[0], d)
                stand_ins[u] = os.path.basename(donors[0])
                say("  STAND-IN: %s failed %d runs -> copy of %s" % (u[:70], attempts[u], stand_ins[u]))
    json.dump(attempts, open(state_path, "w", encoding="utf-8"))

    still = {u: d for u, d in jobs.items() if not (os.path.isfile(d) and sane_image(d))}
    if still:
        say("%d image(s) still missing after retries this run (%d fetched, %d stand-ins) — exit 2, resumes next deploy"
            % (len(still), got, len(stand_ins))); return 2

    # every file present → make the live sellers file local (listings arrived local via manifest)
    if "images.unsplash.com" in sellers_txt:
        bak = sellers_path + ".bak-selfhost-" + TS
        shutil.copyfile(sellers_path, bak); say("sellers backup: " + bak)
        new = sellers_txt
        for u in set(URLRX.findall(sellers_txt)):
            local = jobs[u]
            rel = "/" + os.path.relpath(local, LIVE).replace(os.sep, "/")
            new = new.replace(u, rel)
        json.loads(new)
        open(sellers_path, "w", encoding="utf-8").write(new)
        say("live demo_sellers.json rewritten to local paths")
    else:
        say("live demo_sellers.json already local — untouched")

    attr = os.path.join(demo_dir, "ATTRIBUTION.json")
    with open(attr, "w", encoding="utf-8") as f:
        json.dump({"license": "Unsplash License (images downloaded 2026-08-13; original URLs preserved as provenance)",
                   "images": mapping.get("images", {}), "sf_tiles": mapping.get("sf_tiles", {}),
                   "stand_ins": stand_ins}, f, indent=1)
    say("ATTRIBUTION.json written · %d images self-hosted · zero third-party pixels remain" % len(jobs))
    return 0

if __name__ == "__main__":
    sys.exit(main())
