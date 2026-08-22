#!/usr/bin/env python3
"""set_email_secret.py VALUE - RUNS ON THE SERVER. Write ONE value to EVERY location that
defines EMAIL_INBOUND_SECRET, so precedence cannot matter. PRINTS NO SECRET VALUES."""
import glob, hashlib, os, re, shutil, subprocess, sys, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

VAL = sys.argv[1]
VAR = "EMAIL_INBOUND_SECRET"
DROPDIR = "/etc/systemd/system/marketsquare.service.d"
CANON = os.path.join(DROPDIR, "zz-inbound.conf")
STAMP = time.strftime("%Y%m%d-%H%M%S")

def live():
    pid = out("systemctl show -p MainPID --value marketsquare")
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if e.startswith(VAR + "="): return e.split("=", 1)[1]
    except Exception: pass
    return ""

print("  [--] before: process %s" % fp(live()))
print("  [--] target : %s (one value, everywhere)" % fp(VAL))

# 1. every drop-in and the unit: strip, then write ours into the canonical one
files = sorted(glob.glob(os.path.join(DROPDIR, "*.conf")))
frag = out("systemctl show -p FragmentPath --value marketsquare")
if frag and os.path.isfile(frag): files.append(frag)
for f in files:
    if os.path.abspath(f) == os.path.abspath(CANON): continue
    src = open(f, errors="replace").read()
    if re.search(r'(?m)^\s*Environment="?%s=' % VAR, src):
        shutil.copy2(f, "%s.bak-%s" % (f, STAMP))
        open(f, "w").write(re.sub(r'(?m)^\s*Environment="?%s=.*\n?' % VAR, "", src))
        print("  [OK] stripped from %s" % os.path.basename(f))

relay = ""
if os.path.isfile(CANON):
    m = re.search(r'(?m)^\s*Environment=RELAY_INBOUND_SECRET=(.*)$', open(CANON).read())
    relay = m.group(1).strip() if m else ""
old = os.umask(0o077)
with open(CANON, "w") as f:
    f.write("[Service]\n")
    f.write("Environment=%s=%s\n" % (VAR, VAL))
    if relay: f.write("Environment=RELAY_INBOUND_SECRET=%s\n" % relay)
os.umask(old); os.chmod(CANON, 0o600)
print("  [OK] wrote %s (relay line preserved: %s)" % (os.path.basename(CANON), bool(relay)))

# 2. /etc/environment  3. the app .env
for path in ("/etc/environment", "/var/www/marketsquare/.env"):
    if not os.path.isfile(path): continue
    src = open(path, errors="replace").read()
    shutil.copy2(path, "%s.bak-%s" % (path, STAMP))
    if re.search(r'(?m)^\s*%s=' % VAR, src):
        src = re.sub(r'(?m)^\s*%s=.*$' % VAR, "%s=%s" % (VAR, VAL), src)
    else:
        src = src.rstrip("\n") + "\n%s=%s\n" % (VAR, VAL)
    open(path, "w").write(src)
    if path == "/etc/environment": os.chmod(path, 0o600)
    print("  [OK] set in %s" % path)

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(5)
got = live()
print("  [--] service: %s | /health %s" % (out("systemctl is-active marketsquare"),
      out("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health")))
print("  [%s] process now holds %s %s" % ("OK" if got == VAL else "X ", fp(got),
      "- matches, and every location agrees" if got == VAL else "- STILL WRONG"))
print("  [--] what restarted the service recently:")
for ln in out("journalctl -u marketsquare --since '-20 min' | grep -i 'Stopped\\|Started\\|Scheduled restart' | tail -4").splitlines():
    print("       " + ln[:140])
