#!/usr/bin/env python3
"""fix_demand_from.py - RUNS ON THE SERVER. Repair the unquoted Environment= line in
demand.conf so DEMAND_FROM_EMAIL carries the full display-name address.

systemd splits Environment= on whitespace, so
    Environment=DEMAND_FROM_EMAIL=TrustSquare <hello@mail.trustsquare.co>
set the variable to the single word "TrustSquare" and discarded the address as a
malformed second assignment. Quoting the whole assignment fixes it.
"""
import os, re, shutil, subprocess, time
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

CONF = "/etc/systemd/system/marketsquare.service.d/demand.conf"
VAR = "DEMAND_FROM_EMAIL"
WANT = "TrustSquare <hello@mail.trustsquare.co>"

def live():
    pid = out("systemctl show -p MainPID --value marketsquare")
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if e.startswith(VAR + "="): return e.split("=", 1)[1]
    except Exception: pass
    return "(unset)"

print("  [--] before: %s = %r" % (VAR, live()))
if not os.path.isfile(CONF):
    print("  [X] %s not found" % CONF); raise SystemExit(1)

src = open(CONF).read()
shutil.copy2(CONF, "%s.bak-%s" % (CONF, time.strftime("%Y%m%d-%H%M%S")))

lines, fixed = [], False
for ln in src.splitlines():
    s = ln.strip()
    # the broken forms: an assignment with no var name, or our var unquoted with a space
    if s.startswith("Environment=") and re.match(r'Environment=<[^>]*@[^>]*>\s*$', s):
        continue                                   # the orphaned fragment - drop it
    if s.startswith("Environment=%s=" % VAR) and not s.startswith('Environment="'):
        lines.append('Environment="%s=%s"' % (VAR, WANT)); fixed = True; continue
    if s.startswith('Environment="%s=' % VAR):
        lines.append('Environment="%s=%s"' % (VAR, WANT)); fixed = True; continue
    lines.append(ln)
if not fixed:
    lines.append('Environment="%s=%s"' % (VAR, WANT))
    print("  [--] no existing %s line found - adding one" % VAR)

open(CONF, "w").write("\n".join(lines) + "\n")
os.chmod(CONF, 0o600)
print("  [OK] rewrote %s with the assignment QUOTED" % os.path.basename(CONF))

v = sh("systemd-analyze verify marketsquare.service 2>&1 | grep -i 'invalid environment' | head -3")
if v.stdout.strip():
    print("  [X]  systemd still reports an invalid assignment:")
    for l in v.stdout.strip().splitlines(): print("       " + l[:130])
else:
    print("  [OK] systemd-analyze reports NO invalid environment assignments in any drop-in")

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
got = live()
print("  [--] service: %s | /health %s" % (out("systemctl is-active marketsquare"),
      out("curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health")))
print("  [%s] after: %s = %r" % ("OK" if got == WANT else "X ", VAR, got))
print("  %s" % ("     the configured sender is now actually in effect (it was the word "
                "'TrustSquare' alone, rescued only by the _safe_from fallback)"
                if got == WANT else "     STILL WRONG - tell Claude"))
