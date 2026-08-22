#!/usr/bin/env python3
"""darken_justtcg.py - unset JUSTTCG_API_KEY so the TCG price lane cannot serve.
Licence compliance, not a rotation. PRINTS NO SECRET VALUES."""
import glob, hashlib, os, re, shutil, subprocess, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()
KEY = "JUSTTCG_API_KEY"
DROPDIR = "/etc/systemd/system/marketsquare.service.d"
STAMP = time.strftime("%Y%m%d-%H%M%S")

def live():
    pid = out("systemctl show -p MainPID --value marketsquare")
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if e.startswith(KEY + "="): return e.split("=", 1)[1]
    except Exception: pass
    return ""

print("  [--] before: %s = %s" % (KEY, fp(live())))
targets = []
frag = out("systemctl show -p FragmentPath --value marketsquare")
if frag and os.path.isfile(frag): targets.append(frag)
targets += sorted(glob.glob(os.path.join(DROPDIR, "*.conf")))
for t in list(targets):
    for m in re.finditer(r'(?m)^\s*EnvironmentFile\s*=\s*-?(\S+)', open(t, errors="replace").read()):
        if os.path.isfile(m.group(1)) and m.group(1) not in targets: targets.append(m.group(1))
n = 0
for t in targets:
    src = open(t, errors="replace").read()
    if not re.search(r'(?m)^\s*(?:Environment=)?"?%s=' % KEY, src): continue
    shutil.copy2(t, "%s.bak-%s" % (t, STAMP))
    open(t, "w").write(re.sub(r'(?m)^\s*(?:Environment=)?"?%s=.*\n?' % KEY, "", src))
    print("  [OK] removed from %s (backup kept - re-adding is one paste)" % os.path.basename(t))
    n += 1
sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s | /health %s" % (out("systemctl is-active marketsquare"),
      out("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health")))
after = live()
print("  [%s] %s now %s -- the TCG price lane is DARK and inside the free licence"
      % ("OK" if not after else "X ", KEY, "unset" if not after else fp(after)))
