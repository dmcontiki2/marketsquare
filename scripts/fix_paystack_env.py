#!/usr/bin/env python3
"""fix_paystack_env.py - find EVERY definition of the Paystack key on this box and
put them all on the canonical new value. PRINTS NO SECRET VALUES - fingerprints only."""
import hashlib, os, re, glob, shutil, subprocess, time

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8]
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()

KEYS = ("PAYSTACK_SECRET_KEY", "PAYSTACK_WEBHOOK_SECRET")
DROPIN = "/etc/systemd/system/marketsquare.service.d"
STAMP = time.strftime("%Y%m%d-%H%M%S")

canon_file = os.path.join(DROPIN, "paystack.conf")
m = re.search(r'PAYSTACK_SECRET_KEY=(.+)', open(canon_file).read())
canon = m.group(1).strip()
print("  canonical (just pasted) fingerprint %s" % fp(canon))

targets = []
frag = sh("systemctl show -p FragmentPath --value marketsquare")
if frag and os.path.isfile(frag): targets.append(frag)
targets += sorted(glob.glob(os.path.join(DROPIN, "*.conf")))

envfiles = []
for t in list(targets):
    for line in open(t, errors="replace"):
        mm = re.match(r'\s*EnvironmentFile\s*=\s*-?(\S+)', line)
        if mm and os.path.isfile(mm.group(1)): envfiles.append(mm.group(1))
targets += envfiles
for extra in ("/var/www/marketsquare/.env", "/etc/marketsquare/secrets.env"):
    if os.path.isfile(extra) and extra not in targets: targets.append(extra)

print("\n  --- every file that defines a Paystack key ---")
changed = []
for t in targets:
    try: src = open(t, errors="replace").read()
    except Exception: continue
    hits = [(k, v.strip()) for k in KEYS for v in re.findall(r'%s=(.*)' % k, src)]
    if not hits: continue
    for k, v in hits:
        mark = "MATCHES" if v == canon else "STALE  "
        print("  [%s] %-58s %s  %s" % (mark, t, k, fp(v)))
    if any(v != canon for _, v in hits):
        shutil.copy(t, "%s.bak-%s" % (t, STAMP))
        out = src
        for k in KEYS:
            out = re.sub(r'(?m)^(\s*(?:Environment=)?%s=).*$' % k, lambda mo: mo.group(1) + canon, out)
        open(t, "w").write(out)
        changed.append(t)

if not changed:
    print("\n  Nothing stale on disk - the old value is coming from somewhere else.")
else:
    print("\n  Updated %d file(s) (backups .bak-%s):" % (len(changed), STAMP))
    for c in changed: print("    " + c)

print("\n  --- reload + restart ---")
sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  service: %s" % sh("systemctl is-active marketsquare"))

pid = sh("systemctl show -p MainPID --value marketsquare")
live = ""
try:
    env = open("/proc/%s/environ" % pid, "rb").read().decode("utf8", "replace").split("\0")
    for e in env:
        if e.startswith("PAYSTACK_SECRET_KEY="): live = e.split("=", 1)[1]
except Exception as exc:
    print("  could not read process env: %s" % exc)
print("  live process fingerprint %s  -> %s" % (fp(live) if live else "NONE",
      "MATCHES canonical" if live == canon else "STILL WRONG"))

code = sh('curl -s -o /dev/null -w "%%{http_code}" https://api.paystack.co/transaction/totals -H "Authorization: Bearer ' + live + '"')
print("  Paystack replied HTTP %s  -> %s" % (code, "AUTH PASSED - payments are back up" if code == "200"
      else "STILL REJECTED" if code == "401" else "unexpected"))
