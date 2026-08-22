#!/usr/bin/env python3
"""purge_gmail_password.py - remove the mistakenly-stored account password. NO VALUES PRINTED."""
import hashlib, os, subprocess, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()
D = "/etc/systemd/system/marketsquare.service.d/gmail.conf"
ADDR = "dmcontiki2@gmail.com"

pid = out("systemctl show -p MainPID --value marketsquare")
before = ""
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if e.startswith("GMAIL_APP_PASSWORD="): before = e.split("=",1)[1]
print("  [--] currently loaded password fingerprint: %s" % fp(before))

# keep the address, drop the password entirely
old = os.umask(0o077)
with open(D, "w") as f:
    f.write("[Service]\nEnvironment=GMAIL_ADDRESS=%s\n" % ADDR)
os.umask(old); os.chmod(D, 0o600)
print("  [OK] rewrote %s - address kept, password REMOVED" % D)

sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
pid = out("systemctl show -p MainPID --value marketsquare")
after = ""
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if e.startswith("GMAIL_APP_PASSWORD="): after = e.split("=",1)[1]
print("  [--] service: %s" % out("systemctl is-active marketsquare"))
print("  [%s] password now loaded: %s" % ("OK" if not after else "X ", fp(after) if after else "NONE - gone"))

# scrub any backup files that captured it, and shell history
n = 0
for root, _, files in os.walk("/etc/systemd/system/marketsquare.service.d"):
    for fn in files:
        p = os.path.join(root, fn)
        if p == D: continue
        try:
            s = open(p, errors="replace").read()
            if before and before in s:
                os.remove(p); n += 1; print("  [OK] deleted backup containing it: %s" % p)
        except Exception: pass
print("  [--] %d stale file(s) removed" % n)
for h in ("/root/.bash_history",):
    try:
        if before and os.path.isfile(h):
            lines = [l for l in open(h, errors="replace") if before not in l]
            open(h, "w").writelines(lines); print("  [OK] scrubbed %s" % h)
    except Exception: pass
print("\n  SMTP fallback is now dark by design. Resend remains the sender.")
