#!/usr/bin/env python3
"""
TrustSquare Post-Deploy Smoke Test
Run: python3 smoke_test.py
All checks must pass before closing a session.
"""
import sys, json, subprocess, re

OK   = "[OK]"
FAIL = "[FAIL]"
failures = []

def check(name, ok, detail=""):
    if ok:
        print(f"  {OK} {name}")
    else:
        d = (": " + detail) if detail else ""
        print(f"  {FAIL} {name}{d}")
        failures.append(name)

def ssh(cmd, stdin=None, timeout=25):
    r = subprocess.run(["ssh", "root@178.104.73.239", cmd],
                       input=stdin, capture_output=True, timeout=timeout)
    return r.stdout.decode("utf-8", errors="replace")

def ssh_json(cmd):
    try: return json.loads(ssh(cmd))
    except: return None

def node_eval(js_bytes, probe):
    full = js_bytes + b"\n" + probe.encode()
    subprocess.run(["ssh", "root@178.104.73.239", "cat > /tmp/smoke_probe.js"],
                   input=full, capture_output=True, timeout=20)
    r = subprocess.run(["ssh", "root@178.104.73.239", "node /tmp/smoke_probe.js"],
                       capture_output=True, timeout=20)
    return r.returncode, r.stdout.decode(), r.stderr.decode()

NODE_STUB = (
    b"const window={location:{search:'',href:''},addEventListener:()=>{}};\n"
    b"const document={getElementById:()=>null,querySelector:()=>null,"
    b"querySelectorAll:()=>[],addEventListener:()=>{}};\n"
    b"const localStorage={getItem:()=>null,setItem:()=>{}};\n"
    b"const sessionStorage={getItem:()=>null,setItem:()=>{}};\n"
)

print("\n=== TrustSquare Smoke Test ===")

# 0. Fetch HTML
print("\n[0] Fetching live HTML...")
ssh("curl -s --max-time 15 'https://trustsquare.co' > /tmp/smoke_index.html", timeout=30)
size = int(ssh("wc -c < /tmp/smoke_index.html").strip() or "0")
check(f"HTML fetched ({size:,} bytes)", size > 500000, f"only {size}")
html = ssh("cat /tmp/smoke_index.html", timeout=20)

# 1. HTML structure
print("\n[1] HTML structure")
check("Ends with </html>",      html.rstrip().endswith("</html>"))
check("ms-data block present",  'id="ms-data"'  in html)
check("ms-logic block present", 'id="ms-logic"' in html)

# 2. JS syntax
print("\n[2] JavaScript syntax")
for block in ("ms-data", "ms-logic"):
    m = re.search(rf'<script id="{block}"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        check(f"{block} found", False)
        continue
    subprocess.run(["ssh", "root@178.104.73.239", f"cat > /tmp/smoke_{block}.js"],
                   input=m.group(1).encode(), capture_output=True, timeout=20)
    r = subprocess.run(["ssh", "root@178.104.73.239",
                        f"node --check /tmp/smoke_{block}.js"],
                       capture_output=True, timeout=20)
    check(f"{block} syntax valid", r.returncode == 0,
          r.stderr.decode()[:120].strip())

# 3. LISTINGS -- now served from BEA /demo-listings (Session 66 hollowing)
print("\n[3] LISTINGS (BEA /demo-listings)")
dl = ssh_json("curl -s --max-time 10 'http://localhost:8000/demo-listings'")
if dl:
    n    = dl.get("count", 0)
    cats = list({l["cat"] for l in dl.get("listings", [])})
    check(f"demo-listings endpoint ({n} entries)", n >= 200)
    for cat in ["Property", "Adventures", "Collectors", "Cars"]:
        check(f"  cat:{cat}", cat in cats)
else:
    check("demo-listings endpoint reachable", False)
check("LISTINGS not bundled in HTML", "const LISTINGS = [" not in html)

# 4. BEA API
print("\n[4] BEA API")
h = ssh_json("curl -s --max-time 5 'http://localhost:8000/health'")
check("BEA /health ok", bool(h and h.get("status") == "ok"))
items = ssh_json("curl -s --max-time 5 'http://localhost:8000/listings?city_id=47&limit=10'")
if isinstance(items, dict):
    items = items.get("listings", items.get("items", []))
n_items = len(items) if items else 0
check(f"BEA live listings ({n_items})", bool(items and n_items >= 1))
if items:
    wp = [l for l in items if l.get("photo_urls") or l.get("medium_url")]
    check(f"Live listing has photos ({len(wp)})", len(wp) >= 1)

# 5. Heritage -- now served from BEA /wonders (Session 66 hollowing)
print("\n[5] World Heritage (BEA /wonders)")
wonders = ssh_json("curl -s --max-time 10 'http://localhost:8000/wonders'")
if wonders:
    n_w = wonders.get("count", 0)
    check(f"BEA /wonders endpoint ({n_w} sites)", n_w >= 100)
else:
    check("BEA /wonders endpoint reachable", False)
check("WONDERS_BUNDLED not in HTML", "const WONDERS_BUNDLED" not in html)
check("FEA fetches wonders from BEA", "BEA_URL+'/wonders'" in html)

# 6. Critical functions
print("\n[6] Critical functions")
for fn in ["openSellerCV", "openBEASellerProfile", "renderCatCounts",
           "renderGrid", "loadLiveListings", "msSellerSignIn",
           "elConfirmDeleteListing", "loadHomeWonders", "initLMHomeTile"]:
    check(f"  {fn}()", f"function {fn}" in html)

# 7. Demo bleed guards
print("\n[7] Demo bleed guards")
check("renderCatCounts filter", "!DEMO_MODE && String(l.id).startsWith('demo_')" in html)
check("renderGrid filter",      "!DEMO_MODE && String(l.id).startsWith('demo_')" in html)
check("initLMHomeTile guard",   "DEMO_MODE ? LISTINGS.filter" in html)

# 8. Seller profile safety
print("\n[8] Seller profile safety")
check("No bare cvScore ref",       "${cvScore}" not in html)
check("sellerIdx null-safe IIFE",  "(function(){var sidStr=" in html)
check("openBEASellerProfile trust","l.trust" in html)

# Summary
print("\n=== Result ===")
if failures:
    print(f"  {FAIL} {len(failures)} check(s) failed:")
    for f in failures:
        print(f"     - {f}")
    print()
    sys.exit(1)
else:
    print(f"  {OK} All checks passed -- safe to close session.")
    sys.exit(0)
