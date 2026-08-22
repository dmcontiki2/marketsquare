#!/usr/bin/env python3
"""install_cf_token.py - rotate CF_CACHE_TOKEN. argv[1] = new token. NO VALUES PRINTED."""
import hashlib, json, os, re, shutil, subprocess, sys, time, urllib.request, urllib.error
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()
new = sys.argv[1].strip()
KEY = "CF_CACHE_TOKEN"
DROPIN = "/etc/systemd/system/marketsquare.service.d/cloudflare.conf"
ENVFILE, APPENV = "/etc/environment", "/var/www/marketsquare/.env"
STAMP = time.strftime("%Y%m%d-%H%M%S")

def senv():
    pid = out("systemctl show -p MainPID --value marketsquare"); d = {}
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if "=" in e:
                k, v = e.split("=", 1); d[k] = v
    except Exception: pass
    return d

before = senv()
print("  === before ===")
print("  [--] live %s: %s" % (KEY, fp(before.get(KEY, ""))))
print("  [--] CF_ZONE_ID  : %s" % (before.get("CF_ZONE_ID") or "NOT SET"))

old = os.umask(0o077)
with open(DROPIN, "w") as f:
    f.write("[Service]\nEnvironment=%s=%s\n" % (KEY, new))
os.umask(old); os.chmod(DROPIN, 0o600)
print("\n  === install ===")
print("  [OK] wrote %s (0600)" % DROPIN)
for f in (ENVFILE, APPENV):
    if not os.path.isfile(f): continue
    src = open(f, errors="replace").read()
    if not re.search(r'(?m)^\s*%s=' % KEY, src): continue
    shutil.copy2(f, "%s.bak-%s" % (f, STAMP))
    if f == ENVFILE:
        open(f, "w").write(re.sub(r'(?m)^\s*%s=.*\n?' % KEY, "", src)); os.chmod(f, 0o600)
        print("  [OK] removed %s from %s" % (KEY, f))
    else:
        open(f, "w").write(re.sub(r'(?m)^(\s*%s=).*$' % KEY, lambda m: m.group(1) + new, src))
        print("  [OK] updated %s in %s" % (KEY, f))
sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

print("\n  === verify at the point of USE (RG-0147) ===")
env = senv(); tok = env.get(KEY, ""); zone = env.get("CF_ZONE_ID", "")
print("  [%s] live process fingerprint %s" % ("OK" if tok == new else "X ", fp(tok)))
def cf(url, data=None):
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + tok,
                                               "Content-Type": "application/json"},
                                 data=json.dumps(data).encode() if data else None)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read().decode())

# 1) user-level verify: informative only. A token scoped to ONE zone's Cache Purge
#    cannot call a /user/ endpoint, so a 401 here says nothing about the token.
try:
    print("  [--] /user/tokens/verify: status '%s'"
          % cf("https://api.cloudflare.com/client/v4/user/tokens/verify")["result"]["status"])
except urllib.error.HTTPError as e:
    print("  [--] /user/tokens/verify: HTTP %s (expected for a zone-scoped token - not a verdict)" % e.code)
except Exception as e:
    print("  [--] /user/tokens/verify: %s" % str(e)[:80])

# 2) THE REAL TEST: do the job the token exists to do. Purging one URL that is not
#    cached is harmless and proves the credential end to end.
try:
    r = cf("https://api.cloudflare.com/client/v4/zones/%s/purge_cache" % zone,
           {"files": ["https://trustsquare.co/__rotation_probe__"]})
    if r.get("success"):
        print("  [OK] CACHE PURGE WORKS - a real purge call succeeded. This token is good.")
    else:
        print("  [X]  purge call returned success=false: %s" % str(r.get("errors"))[:140])
except urllib.error.HTTPError as e:
    body = e.read().decode("utf8", "replace")[:200]
    print("  [X]  PURGE REJECTED: HTTP %s - %s" % (e.code, body))
except Exception as e:
    print("  [X]  could not test purge: %s" % str(e)[:120])
