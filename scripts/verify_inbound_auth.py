#!/usr/bin/env python3
"""verify_inbound_auth.py - RUNS ON THE SERVER. Prove both inbound doors accept the NEW
secret and reject a wrong one. Sends nothing outward. PRINTS NO SECRET VALUES."""
import hashlib, json, subprocess, urllib.error, urllib.request
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def out(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()

pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8", "replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v

def post(path, headers, body):
    req = urllib.request.Request("http://127.0.0.1:8000" + path,
                                 data=json.dumps(body).encode(),
                                 headers=dict(headers, **{"Content-Type": "application/json"}),
                                 method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return "ERR:" + str(e)[:60]

for label, path, header, var, body in (
    ("inbound email", "/email/inbound", "X-Inbound-Secret", "EMAIL_INBOUND_SECRET",
     {"from": "probe@example.invalid", "to": "x@trustsquare.co", "subject": "probe", "text": ""}),
    ("intro relay",   "/intro/relay",   "X-Relay-Secret",   "RELAY_INBOUND_SECRET",
     {"to": "intro-000000@relay.trustsquare.co", "from": "probe@example.invalid", "text": ""}),
):
    secret = env.get(var, "")
    print("\n  === %s (%s = %s) ===" % (label, var, fp(secret)))
    if not secret:
        print("  [X]  the server holds no %s - the door is shut to everyone" % var); continue
    bad = post(path, {header: "definitely-not-the-secret"}, body)
    good = post(path, {header: secret}, body)
    print("  [%s] wrong secret -> HTTP %s %s"
          % ("OK" if bad in (401, 403) else "X ", bad,
             "(rejected, as it must be)" if bad in (401, 403) else "(SHOULD have been 401/403)"))
    print("  [%s] new secret   -> HTTP %s %s"
          % ("OK" if good not in (401, 403) else "X ", good,
             "(accepted - auth passed; any 4xx here is the empty probe payload, not the key)"
             if good not in (401, 403) else "(REJECTED - the door does not know this secret)"))
