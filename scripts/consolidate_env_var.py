#!/usr/bin/env python3
"""consolidate_env_var.py VAR CANONICAL_CONF - make ONE file the only definition of VAR.

Born 22 Aug 2026 after the same precedence fault bit twice: a correctly-written drop-in
lost to a later-sorting one (Paystack: production kept a revoked key and card payments
were down; CF_CACHE_TOKEN: the rotation silently did nothing). Systemd applies the unit,
then every drop-in in LEXICOGRAPHIC order, then EnvironmentFile contents where the
directive sits - last assignment wins. Writing the right value is not enough; it has to
be the LAST value. PRINTS NO SECRET VALUES."""
import glob, hashlib, os, re, shutil, subprocess, sys, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

VAR, CANON_FILE = sys.argv[1], sys.argv[2]
DROPDIR = "/etc/systemd/system/marketsquare.service.d"
STAMP = time.strftime("%Y%m%d-%H%M%S")

m = re.search(r'(?m)^\s*Environment=\"?%s=([^\"]*)\"?\s*$' % VAR, open(CANON_FILE).read())
if not m:
    print("  [X] %s does not define %s" % (CANON_FILE, VAR)); raise SystemExit(1)
canon = m.group(1).strip()
print("  canonical: %s holds %s (%s)" % (os.path.basename(CANON_FILE), VAR, fp(canon)))

targets = []
frag = out("systemctl show -p FragmentPath --value marketsquare")
if frag and os.path.isfile(frag): targets.append(frag)
targets += sorted(glob.glob(os.path.join(DROPDIR, "*.conf")))
for t in list(targets):
    for mm in re.finditer(r'(?m)^\s*EnvironmentFile\s*=\s*-?(\S+)', open(t, errors="replace").read()):
        if os.path.isfile(mm.group(1)) and mm.group(1) not in targets:
            targets.append(mm.group(1))

print("\n  stripping every OTHER definition:")
stripped = 0
for t in targets:
    if os.path.abspath(t) == os.path.abspath(CANON_FILE): continue
    src = open(t, errors="replace").read()
    if not re.search(r'(?m)^\s*(?:Environment=)?\"?%s=' % VAR, src): continue
    old = re.search(r'(?m)^\s*(?:Environment=)?\"?%s=([^\"]*)\"?\s*$' % VAR, src).group(1).strip()
    shutil.copy2(t, "%s.bak-%s" % (t, STAMP))
    open(t, "w").write(re.sub(r'(?m)^\s*(?:Environment=)?\"?%s=.*\n?' % VAR, "", src))
    os.chmod(t, 0o600 if t.startswith("/etc/environment") else os.stat(t).st_mode & 0o777)
    print("    [OK] removed from %-30s (held %s)" % (os.path.basename(t), fp(old)))
    stripped += 1
print("    (%d other definition(s) removed)" % stripped)

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
pid = out("systemctl show -p MainPID --value marketsquare")
live = ""
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if e.startswith(VAR + "="): live = e.split("=", 1)[1]
print("\n  service: %s" % out("systemctl is-active marketsquare"))
print("  [%s] RUNNING PROCESS now holds %s %s" % ("OK" if live == canon else "X ", fp(live),
      "- matches canonical" if live == canon else "- STILL WRONG"))
