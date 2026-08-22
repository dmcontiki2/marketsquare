#!/usr/bin/env python3
"""diag_env_var.py VARNAME - where does the running process get this value from?
Walks the unit, every drop-in IN SYSTEMD ORDER, and every EnvironmentFile they name.
PRINTS NO SECRET VALUES."""
import glob, hashlib, os, re, subprocess, sys
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def out(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
KEY = sys.argv[1]
frag = out("systemctl show -p FragmentPath --value marketsquare")
drops = sorted(glob.glob("/etc/systemd/system/marketsquare.service.d/*.conf"))
print("  systemd applies these IN THIS ORDER (later wins):")
order = ([frag] if frag else []) + drops
envfiles = []
for f in order:
    if not os.path.isfile(f): continue
    txt = open(f, errors="replace").read()
    m = re.search(r'(?m)^\s*Environment=\"?%s=([^\"]*)\"?\s*$' % KEY, txt)
    tag = "  <== defines %s (%s)" % (KEY, fp(m.group(1).strip())) if m else ""
    print("    %-62s%s" % (os.path.basename(f), tag))
    for mm in re.finditer(r'(?m)^\s*EnvironmentFile\s*=\s*-?(\S+)', txt):
        envfiles.append((os.path.basename(f), mm.group(1)))
print("\n  EnvironmentFile directives (their contents are applied where the directive sits):")
if not envfiles: print("    (none)")
for owner, path in envfiles:
    if os.path.isfile(path):
        m = re.search(r'(?m)^\s*(?:export\s+)?%s=([^\"]*)\"?\s*$' % KEY, open(path, errors="replace").read())
        print("    %-40s (from %s) %s" % (path, owner,
              "<== defines %s (%s)" % (KEY, fp(m.group(1).strip())) if m else ""))
    else:
        print("    %-40s (from %s) [file absent]" % (path, owner))
pid = out("systemctl show -p MainPID --value marketsquare")
live = ""
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if e.startswith(KEY + "="): live = e.split("=", 1)[1]
print("\n  RUNNING PROCESS holds: %s   (started %s)" % (fp(live),
      out("systemctl show -p ActiveEnterTimestamp --value marketsquare")))
