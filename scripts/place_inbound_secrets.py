#!/usr/bin/env python3
"""place_inbound_secrets.py - RUNS ON THE SERVER. Put both inbound secrets where the code
reads them, using real file writes instead of shell escaping. PRINTS NO SECRET VALUES."""
import hashlib, os, re, subprocess, time

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

DROPIN = "/etc/systemd/system/marketsquare.service.d/zz-inbound.conf"
ENVF = "/var/www/marketsquare/.env"
VARS = ("EMAIL_INBOUND_SECRET", "RELAY_INBOUND_SECRET")

def live(var):
    pid = out("systemctl show -p MainPID --value marketsquare")
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8", "replace").split("\0"):
            if e.startswith(var + "="):
                return e.split("=", 1)[1]
    except Exception:
        pass
    return ""

envtxt = open(ENVF).read() if os.path.isfile(ENVF) else ""
vals = {}
for v in VARS:
    m = re.search(r'(?m)^\s*%s=(.*)$' % v, envtxt)
    vals[v] = (m.group(1).strip().strip('"') if m else "") or live(v)
    print("  [--] %-22s taking fingerprint %s" % (v, fp(vals[v])))

missing = [v for v, x in vals.items() if not x]
if missing:
    print("  [X] no value found for: %s" % ", ".join(missing)); raise SystemExit(1)

print("\n  what the malformed file looked like:")
if os.path.isfile(DROPIN):
    raw = open(DROPIN, "rb").read()
    print("      %d byte(s), %d real line(s), literal-backslash-n present: %s"
          % (len(raw), raw.count(b"\n") + 1, b"\\n" in raw))

old = os.umask(0o077)
with open(DROPIN, "w") as f:
    f.write("[Service]\n")
    for v in VARS:
        f.write("Environment=%s=%s\n" % (v, vals[v]))
os.umask(old); os.chmod(DROPIN, 0o600)
raw = open(DROPIN, "rb").read()
print("  [OK] rewrote %s: %d real line(s), literal-backslash-n present: %s"
      % (os.path.basename(DROPIN), raw.count(b"\n"), b"\\n" in raw))

r = sh("systemd-analyze verify marketsquare.service 2>&1 | head -3")
if r.stdout.strip():
    print("  [--] unit verify: %s" % r.stdout.strip().splitlines()[0])

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s | /health %s" % (out("systemctl is-active marketsquare"),
      out("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health")))

ok = True
for v in VARS:
    got = live(v)
    good = got == vals[v]
    ok = ok and good
    print("  [%s] %-22s in PROCESS env as %s" % ("OK" if good else "X ", v, fp(got)))
print("\n  RESULT: %s" % ("both are where the code reads them - safe to paste into the Workers"
                          if ok else "STILL WRONG - tell Claude"))
