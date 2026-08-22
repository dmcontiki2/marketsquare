#!/usr/bin/env python3
"""rotate_jwt_secret.py - rotate MS_JWT_SECRET and move it out of the box-wide file.
PRINTS NO SECRET VALUES. Automatic rollback if the service does not come back."""
import hashlib, os, re, secrets, shutil, subprocess, time, urllib.request

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

ENVFILE = "/etc/environment"
SECRETS = "/etc/marketsquare/secrets.env"
STAMP = time.strftime("%Y%m%d-%H%M%S")
KEY = "MS_JWT_SECRET"

def live_val(name):
    pid = out("systemctl show -p MainPID --value marketsquare")
    try:
        for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
            if e.startswith(name + "="): return e.split("=",1)[1]
    except Exception: pass
    return ""

def healthy(tries=8):
    for _ in range(tries):
        try:
            with urllib.request.urlopen("http://127.0.0.1:8000/health", timeout=5) as r:
                if r.status == 200: return True
        except Exception: pass
        time.sleep(3)
    return False

print("  === 0. guard: does the msdeploy read-only DB path still work? ===")
r = sh("sudo -u msdeploy -H bash -lc 'command -v sqlite3 >/dev/null && echo SQLITE-OK || echo SQLITE-MISSING; "
       "ls /var/www/marketsquare/*.db >/dev/null 2>&1 && echo DB-READABLE || echo DB-UNREADABLE'")
for line in (r.stdout or r.stderr or "no answer").splitlines(): print("      " + line.strip())
print("      (this is the /TSL gate's transport - it must survive the 600 change)")

print("\n  === 1. rotate ===")
before = live_val(KEY)
print("  [--] current live fingerprint %s" % fp(before))
new = secrets.token_hex(32)

backups = []
for f in (ENVFILE, SECRETS):
    if os.path.isfile(f):
        b = "%s.bak-%s" % (f, STAMP); shutil.copy2(f, b); backups.append((f, b))

# strip from the box-wide file
if os.path.isfile(ENVFILE):
    src = open(ENVFILE).read()
    stripped = re.sub(r'(?m)^\s*%s=.*\n?' % KEY, "", src)
    open(ENVFILE, "w").write(stripped)
    os.chmod(ENVFILE, 0o600)
    print("  [OK] removed %s from %s (now %s)" % (KEY, ENVFILE, oct(os.stat(ENVFILE).st_mode)[-3:]))

# write into the 0600 secrets file
os.makedirs(os.path.dirname(SECRETS), exist_ok=True)
cur = open(SECRETS).read() if os.path.isfile(SECRETS) else ""
if re.search(r'(?m)^\s*%s=' % KEY, cur):
    cur = re.sub(r'(?m)^\s*%s=.*$' % KEY, "%s=%s" % (KEY, new), cur)
else:
    if cur and not cur.endswith("\n"): cur += "\n"
    cur += "%s=%s\n" % (KEY, new)
open(SECRETS, "w").write(cur); os.chmod(SECRETS, 0o600)
print("  [OK] wrote %s into %s (0600)" % (KEY, SECRETS))

sh("systemctl daemon-reload && systemctl restart marketsquare")
time.sleep(3)

print("\n  === 2. verify ===")
if not healthy():
    print("  [X]  SERVICE DID NOT COME BACK - ROLLING BACK")
    for f, b in backups: shutil.copy2(b, f)
    sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
    print("  [--] after rollback: service %s, health %s" % (out("systemctl is-active marketsquare"),
          "200" if healthy(4) else "STILL DOWN - tell Claude immediately"))
    raise SystemExit(1)

after = live_val(KEY)
print("  [--] service: %s   /health: 200" % out("systemctl is-active marketsquare"))
print("  [--] new live fingerprint %s (was %s)" % (fp(after), fp(before)))
print("  [OK] SECRET CHANGED - old tokens can no longer be forged" if after and after != before
      else "  [X]  fingerprint did not change - the old value is still winning somewhere")
print("  [--] %s still present in %s? %s" % (KEY, ENVFILE,
      "YES - PROBLEM" if re.search(r'(?m)^\s*%s=' % KEY, open(ENVFILE).read()) else "no (good)"))
print("\n  NOTE: every existing sign-in is now invalid - that is the point. Sign in again")
print("  with the password in .secrets\\rotated_secrets.txt.")
