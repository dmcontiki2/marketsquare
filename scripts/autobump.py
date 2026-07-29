#!/usr/bin/env python3
"""autobump.py — deploy-time cache-buster bumping (29 Jul 2026, David: 'fix the bump').
Removes the last human step from fix -> every user has it: any tracked static whose
CONTENT changed since the last deploy gets its ?v= reference bumped automatically.

Tracked (child file -> the file holding its ?v= reference):
  adventures_*_map.html, ranking_explainer.html  -> ms.js
  ms.js, ms.css                                  -> marketsquare.html
Order matters: children first (their bumps edit ms.js), then ms.js itself is hashed
POST-edit so a map bump alone also refreshes ms.js for every browser.

State: scripts/static_versions.json (content hashes at last deploy). First run
baselines silently — no mass bump. Idempotent: unchanged files are never touched.
Exit 0 always (a bump helper must never block a deploy); prints every action.
"""
import glob, hashlib, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = os.path.join(HERE, "static_versions.json")

def sha(p):
    with open(p, "rb") as f: return hashlib.sha1(f.read()).hexdigest()

def bump_ref(host_path, fname):
    src = open(host_path, encoding="utf-8").read()
    pat = re.compile(re.escape(fname) + r"\?v=(\d+)")
    m = pat.search(src)
    if m:
        new = pat.sub(fname + "?v=" + str(int(m.group(1)) + 1), src)
        ver = int(m.group(1)) + 1
    elif "'" + fname + "'" in src or '"' + fname + '"' in src or "/" + fname in src:
        new = src.replace(fname, fname + "?v=2", 1); ver = 2
    else:
        return None
    open(host_path, "w", encoding="utf-8").write(new)
    return ver

def main():
    try:
        manifest = json.load(open(MANIFEST)) if os.path.isfile(MANIFEST) else None
    except Exception:
        manifest = None
    first_run = manifest is None
    manifest = manifest or {}
    children = sorted(glob.glob(os.path.join(ROOT, "adventures_*_map.html"))) + \
               [os.path.join(ROOT, "ranking_explainer.html")]
    bumped = 0
    for p in children:
        if not os.path.isfile(p): continue
        name = os.path.basename(p); h = sha(p)
        if manifest.get(name) != h:
            if not first_run:
                v = bump_ref(os.path.join(ROOT, "ms.js"), name)
                if v: print(f"  [autobump] {name} changed -> ms.js ref ?v={v}"); bumped += 1
            manifest[name] = h
    for name in ("ms.js", "ms.css"):
        p = os.path.join(ROOT, name)
        if not os.path.isfile(p): continue
        h = sha(p)   # post-child-edit hash
        if manifest.get(name) != h:
            if not first_run:
                v = bump_ref(os.path.join(ROOT, "marketsquare.html"), name)
                if v: print(f"  [autobump] {name} changed -> marketsquare.html ref ?v={v}"); bumped += 1
            manifest[name] = h
    json.dump(manifest, open(MANIFEST, "w"), indent=1, sort_keys=True)
    print(f"  [autobump] {'baseline recorded' if first_run else str(bumped) + ' reference(s) bumped'}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
