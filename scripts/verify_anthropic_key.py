#!/usr/bin/env python3
"""verify_anthropic_key.py - the live key still authenticates after the deletions."""
import hashlib, json, subprocess, urllib.request, urllib.error
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
pid = subprocess.run("systemctl show -p MainPID --value marketsquare", shell=True,
                     capture_output=True, text=True).stdout.strip()
k = ""
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if e.startswith("ANTHROPIC_API_KEY="): k = e.split("=",1)[1]
print("  [--] live process key fingerprint: %s" % fp(k))
if not k:
    print("  [X]  no key loaded"); raise SystemExit(1)
try:
    req = urllib.request.Request("https://api.anthropic.com/v1/models",
          headers={"x-api-key": k, "anthropic-version": "2023-06-01"})
    with urllib.request.urlopen(req, timeout=25) as r:
        print("  [OK] AUTH PASSED - %d models listed. The surviving key is the right one."
              % len(json.loads(r.read().decode()).get("data", [])))
except urllib.error.HTTPError as e:
    print("  [X]  REJECTED: HTTP %s - a needed key was deleted" % e.code)
except Exception as e:
    print("  [?]  could not test: %s" % str(e)[:120])
