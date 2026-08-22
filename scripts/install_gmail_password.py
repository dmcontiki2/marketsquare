#!/usr/bin/env python3
"""install_gmail_password.py - install a validated app password + restore GMAIL_ADDRESS.
Reads the password from argv[1]. PRINTS NO SECRET VALUES."""
import glob, hashlib, os, smtplib, subprocess, sys, time
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def sh(c): return subprocess.run(c, shell=True, capture_output=True, text=True)
def out(c): return sh(c).stdout.strip()

pw = sys.argv[1].strip()
addr = "dmcontiki2@gmail.com"
E = "/etc/environment"
D = "/etc/systemd/system/marketsquare.service.d/gmail.conf"

print("  === 0. did I remove GMAIL_ADDRESS today, or was it already gone? ===")
baks = sorted(glob.glob(E + ".bak-*"), key=os.path.getmtime)
today = [b for b in baks if time.strftime("%Y%m%d") in os.path.basename(b)]
if today:
    first = open(today[0], errors="replace").read()
    print("  [--] earliest backup from TODAY: %s" % os.path.basename(today[0]))
    print("  [--] did it contain GMAIL_ADDRESS? %s" % ("YES - I removed it, restoring now"
          if any(l.startswith("GMAIL_ADDRESS") for l in first.splitlines()) else "no - it was already gone before today"))
else:
    print("  [--] no backup from today to compare against")

print("\n  === 1. install (0600 drop-in, both values together) ===")
os.makedirs(os.path.dirname(D), exist_ok=True)
old = os.umask(0o077)
with open(D, "w") as f:
    f.write("[Service]\nEnvironment=GMAIL_ADDRESS=%s\nEnvironment=GMAIL_APP_PASSWORD=%s\n" % (addr, pw))
os.umask(old); os.chmod(D, 0o600)
print("  [OK] wrote %s (mode %s)" % (D, oct(os.stat(D).st_mode)[-3:]))
print("  [--] password length %d, fingerprint %s" % (len(pw), fp(pw)))
sh("systemctl daemon-reload && systemctl restart marketsquare"); time.sleep(4)
print("  [--] service: %s" % out("systemctl is-active marketsquare"))

print("\n  === 2. verify against the LIVE process (sends nothing) ===")
pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8", "replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
lpw, laddr = env.get("GMAIL_APP_PASSWORD", ""), env.get("GMAIL_ADDRESS", "")
print("  [%s] GMAIL_ADDRESS loaded: %s" % ("OK" if laddr else "X ", laddr or "MISSING"))
print("  [%s] password loaded, length %d, fingerprint %s" % ("OK" if len(lpw) == 16 else "X ", len(lpw), fp(lpw)))
try:
    s = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
    s.starttls(); s.login(laddr or addr, lpw); s.quit()
    print("  [OK] SMTP LOGIN ACCEPTED - the fallback sender works. Nothing was sent.")
except smtplib.SMTPAuthenticationError as exc:
    print("  [X]  SMTP LOGIN REJECTED (code %s) - password still wrong" % exc.smtp_code)
except Exception as exc:
    print("  [?]  could not test: %s" % str(exc)[:120])
