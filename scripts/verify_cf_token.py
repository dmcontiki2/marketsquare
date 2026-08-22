#!/usr/bin/env python3
"""verify_cf_token.py - does the token the process holds work, and reach the zone?"""
import hashlib, json, subprocess, urllib.request, urllib.error
def out(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8", "replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
tok, zone = env.get("CF_CACHE_TOKEN", ""), env.get("CF_ZONE_ID", "")
print("  [--] live token fingerprint: %s" % (hashlib.sha256(tok.encode()).hexdigest()[:8] if tok else "NONE"))
if not tok:
    print("  [X]  no token loaded"); raise SystemExit(1)
def cf(url):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok})
    return json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
try:
    print("  [OK] TOKEN VALID - Cloudflare reports status '%s'"
          % cf("https://api.cloudflare.com/client/v4/user/tokens/verify")["result"]["status"])
except urllib.error.HTTPError as e:
    print("  [X]  token REJECTED: HTTP %s" % e.code); raise SystemExit(1)
try:
    print("  [OK] ZONE ACCESS OK - %s (cache purge will work)"
          % cf("https://api.cloudflare.com/client/v4/zones/" + zone)["result"]["name"])
except Exception as e:
    print("  [X]  valid token but no zone access - purge would fail: %s" % str(e)[:100])
