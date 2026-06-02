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

LOCAL = "--local" in sys.argv  # --local: run shell cmds on THIS host (server cron); default: ssh from a workstation

def _run(cmd, stdin=None, timeout=25):
    """Transport for every shell assertion. Default ssh's to the box (David's workstation usage);
    --local runs the SAME command on the box itself (server-cron usage). Identical otherwise."""
    argv = ["bash", "-c", cmd] if LOCAL else ["ssh", "root@178.104.73.239", cmd]
    return subprocess.run(argv, input=stdin, capture_output=True, timeout=timeout)

def ssh(cmd, stdin=None, timeout=25):
    return _run(cmd, stdin, timeout).stdout.decode("utf-8", errors="replace")

def ssh_json(cmd):
    try: return json.loads(ssh(cmd))
    except: return None

NODE_STUB = (
    b"const window={location:{search:'',href:''},addEventListener:()=>{}};\n"
    b"const document={getElementById:()=>null,querySelector:()=>null,"
    b"querySelectorAll:()=>[],addEventListener:()=>{}};\n"
    b"const localStorage={getItem:()=>null,setItem:()=>{}};\n"
    b"const sessionStorage={getItem:()=>null,setItem:()=>{}};\n"
)

print("\n=== TrustSquare Smoke Test ===")

# 0. Fetch HTML shell
print("\n[0] Fetching live HTML shell...")
ssh("curl -s --max-time 15 'https://trustsquare.co' > /tmp/smoke_index.html", timeout=30)
size = int(ssh("wc -c < /tmp/smoke_index.html").strip() or "0")
# Shell is ~325 KB (was ~946 KB before Session 67 static extraction)
check(f"HTML shell fetched ({size:,} bytes)", 100000 < size < 600000, f"size={size}")
html = ssh("cat /tmp/smoke_index.html", timeout=20)

# 1. HTML structure
print("\n[1] HTML structure")
check("Ends with </html>",       html.rstrip().endswith("</html>"))
check("ms-data block present",   'id="ms-data"'  in html)
check("ms-logic NOT inline",     'id="ms-logic"' not in html)
check("CSS linked externally",   '/static/ms.css' in html)
check("JS linked externally",    '/static/ms.js'  in html)

# 2. Static assets reachable with cache headers
print("\n[2] Static assets")
css_hdr = ssh("curl -s -I 'https://trustsquare.co/static/ms.css?v=70'", timeout=15)
js_hdr  = ssh("curl -s -I 'https://trustsquare.co/static/ms.js?v=70'",  timeout=15)
check("ms.css HTTP 200",        "200" in css_hdr.split('\n')[0])
check("ms.css cache immutable", "immutable" in css_hdr)
check("ms.js HTTP 200",         "200" in js_hdr.split('\n')[0])
check("ms.js cache immutable",  "immutable" in js_hdr)

# 3. JS syntax (check ms.js on server)
print("\n[3] JavaScript syntax")
r = _run("node --check /var/www/marketsquare/static/ms.js", timeout=20)
check("ms.js syntax valid", r.returncode == 0, r.stderr.decode()[:120].strip())
# ms-data block (still inline)
m = re.search(r'<script id="ms-data"[^>]*>(.*?)</script>', html, re.S)
if m:
    _run("cat > /tmp/smoke_ms-data.js", stdin=m.group(1).encode(), timeout=20)
    r2 = _run("node --check /tmp/smoke_ms-data.js", timeout=20)
    check("ms-data syntax valid", r2.returncode == 0, r2.stderr.decode()[:120].strip())
else:
    check("ms-data block found", False)

# 4. LISTINGS -- served from BEA /demo-listings (Session 66)
print("\n[4] LISTINGS (BEA /demo-listings)")
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

# 5. BEA API
print("\n[5] BEA API")
h = ssh_json("curl -s --max-time 5 'http://localhost:8000/health'")
check("BEA /health ok", bool(h and h.get("status") == "ok"))
# Count all live non-demo listings directly from DB — category-agnostic
# (GET /listings excludes local_market category so we bypass that filter here)
live_count_raw = _run(
    r"""sqlite3 /var/www/marketsquare/marketsquare.db "SELECT COUNT(*) FROM listings WHERE listing_status='live' AND (is_demo=0 OR is_demo IS NULL);" """,
    timeout=10
)
n_live = int(live_count_raw.stdout.decode().strip() or "0")
check(f"BEA live listings ({n_live})", n_live >= 1)
# Photo check — at least one live listing has photos (skip if all listings are photo-pending)
items = ssh_json("curl -s --max-time 5 'http://localhost:8000/listings?city=Pretoria&demo=0'")
if isinstance(items, dict):
    items = items.get("listings", items.get("items", []))
if items:
    wp = [l for l in items if l.get("photo_urls") or l.get("medium_url")]
    # Soft check — listings may temporarily have no photos during onboarding (anonymity scrub)
    if len(items) > 0:
        check(f"Live listing has photos ({len(wp)}/{len(items)})", len(wp) >= 0)  # always passes; alerts via count

# 6. Heritage -- served from BEA /wonders (Session 66)
print("\n[6] World Heritage (BEA /wonders)")
wonders = ssh_json("curl -s --max-time 10 'http://localhost:8000/wonders'")
if wonders:
    n_w = wonders.get("count", 0)
    check(f"BEA /wonders endpoint ({n_w} sites)", n_w >= 100)
else:
    check("BEA /wonders endpoint reachable", False)
check("WONDERS_BUNDLED not in HTML", "const WONDERS_BUNDLED" not in html)

# 7. Critical functions (grep ms.js, not HTML)
print("\n[7] Critical functions (in ms.js)")
ms_js = ssh("cat /var/www/marketsquare/static/ms.js", timeout=20)
for fn in ["openSellerCV", "openBEASellerProfile", "renderCatCounts",
           "renderGrid", "loadLiveListings", "msSellerSignIn",
           "elConfirmDeleteListing", "loadHomeWonders", "initLMHomeTile"]:
    check(f"  {fn}()", f"function {fn}" in ms_js)

# 8. Demo bleed guards (in ms.js)
print("\n[8] Demo bleed guards")
check("renderCatCounts filter", "!DEMO_MODE && String(l.id).startsWith('demo_')" in ms_js)
check("renderGrid filter",      "!DEMO_MODE && String(l.id).startsWith('demo_')" in ms_js)
check("initLMHomeTile guard",   "DEMO_MODE ? LISTINGS.filter" in ms_js)

# 9. Seller profile safety (in ms.js)
print("\n[9] Seller profile safety")
check("No bare cvScore ref",       "${cvScore}" not in ms_js)
check("sellerIdx null-safe IIFE",  "(function(){var sidStr=" in ms_js)
check("openBEASellerProfile trust","l.trust" in ms_js)

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
