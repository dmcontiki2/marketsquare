#!/usr/bin/env python3
"""install_anthropic_key.py - install a new ANTHROPIC_API_KEY across EVERY holder.
Reads the key from argv[1]. PRINTS NO SECRET VALUES."""
import hashlib, json, os, re, subprocess, sys, time, urllib.request
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

new = sys.argv[1].strip()
KEY = "ANTHROPIC_API_KEY"
DROPIN = "/etc/systemd/system/marketsquare.service.d/anthropic.conf"
ENVFILE = "/etc/environment"
APPENV = "/var/www/marketsquare/.env"     # ai_provider.envkey's fallback - a real second holder
STAMP = time.strftime("%Y%m%d-%H%M%S")

def live():
    pid = out("systemctl show -p MainPID --value marketsquare")
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if e.startswith(KEY + "="): return e.split("=",1)[1]
    except Exception: pass
    return ""

print("  === before ===")
print("  [--] live process : %s" % fp(live()))
for f in (ENVFILE, APPENV):
    if os.path.isfile(f):
        m = re.search(r'(?m)^\s*%s=(.*)$' % KEY, open(f, errors="replace").read())
        print("  [--] %-32s %s" % (f, fp(m.group(1).strip()) if m else "not present"))

print("\n  === install ===")
old = os.umask(0o077)
with open(DROPIN, "w") as f:
    f.write("[Service]\nEnvironment=%s=%s\n" % (KEY, new))
os.umask(old); os.chmod(DROPIN, 0o600)
print("  [OK] wrote %s (0600)" % DROPIN)

for f in (ENVFILE, APPENV):
    if not os.path.isfile(f): continue
    src = open(f, errors="replace").read()
    if not re.search(r'(?m)^\s*%s=' % KEY, src): continue
    import shutil; shutil.copy2(f, "%s.bak-%s" % (f, STAMP))
    if f == ENVFILE:
        open(f, "w").write(re.sub(r'(?m)^\s*%s=.*\n?' % KEY, "", src)); os.chmod(f, 0o600)
        print("  [OK] removed %s from %s (box-wide file, now 0600)" % (KEY, f))
    else:
        open(f, "w").write(re.sub(r'(?m)^(\s*%s=).*$' % KEY, lambda m: m.group(1) + new, src))
        print("  [OK] updated %s in %s (envkey fallback - kept in step, not stranded)" % (KEY, f))

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

print("\n  === verify at the point of USE (RG-0147) ===")
l = live()
print("  [%s] live process fingerprint %s %s" % ("OK" if l == new else "X ", fp(l),
      "- matches what we installed" if l == new else "- MISMATCH, another holder is winning"))
try:
    req = urllib.request.Request("https://api.anthropic.com/v1/models",
          headers={"x-api-key": l or new, "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=25) as r:
        n = len(json.loads(r.read().decode()).get("data", []))
    print("  [OK] AUTH PASSED - Anthropic answered 200 (%d models listed). No tokens spent." % n)
except urllib.error.HTTPError as e:
    print("  [X]  Anthropic rejected the key: HTTP %s" % e.code)
except Exception as e:
    print("  [?]  could not test: %s" % str(e)[:120])
