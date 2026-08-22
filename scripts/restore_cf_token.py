#!/usr/bin/env python3
"""restore_cf_token.py - put the previous working CF token back as the single definition."""
import glob, hashlib, json, os, re, subprocess, time, urllib.request, urllib.error
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()
VAR = "CF_CACHE_TOKEN"
CANON = "/etc/systemd/system/marketsquare.service.d/cloudflare.conf"
DROPDIR = "/etc/systemd/system/marketsquare.service.d"

old = ""
for b in sorted(glob.glob(os.path.join(DROPDIR, "*.bak-*")), key=os.path.getmtime, reverse=True):
    m = re.search(r'(?m)^\s*Environment=%s=(.*)$' % VAR, open(b, errors="replace").read())
    if m:
        old = m.group(1).strip()
        print("  [OK] recovered previous token from %s (%s)" % (os.path.basename(b), fp(old)))
        break
if not old:
    print("  [X] no backup carries the previous token"); raise SystemExit(1)

u = os.umask(0o077)
with open(CANON, "w") as f:
    f.write("[Service]\nEnvironment=%s=%s\n" % (VAR, old))
os.umask(u); os.chmod(CANON, 0o600)
sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)

pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
tok = env.get(VAR, "")
print("  [--] service: %s | live fingerprint %s" % (out("systemctl is-active marketsquare"), fp(tok)))
def cf(url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    return json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
try:
    print("  [OK] CACHE PURGE WORKING AGAIN - token status '%s'"
          % cf("https://api.cloudflare.com/client/v4/user/tokens/verify")["result"]["status"])
    print("  [OK] zone: %s" % cf("https://api.cloudflare.com/client/v4/zones/" + env.get("CF_ZONE_ID",""))["result"]["name"])
except Exception as e:
    print("  [X]  still failing: %s" % str(e)[:120])
