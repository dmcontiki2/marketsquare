#!/usr/bin/env python3
"""diag_gmail.py - is /etc/environment intact, and does the app password really fail?
PRINTS NO SECRET VALUES."""
import glob, hashlib, os, smtplib, subprocess
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def out(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()

E = "/etc/environment"
print("  === 1. is /etc/environment intact? ===")
cur = open(E).read().splitlines()
baks = sorted(glob.glob(E + ".bak-*"))
print("  [--] current: %d line(s), mode %s" % (len(cur), oct(os.stat(E).st_mode)[-3:]))
if baks:
    old = open(baks[-1]).read().splitlines()
    print("  [--] newest backup (%s): %d line(s)" % (os.path.basename(baks[-1]), len(old)))
    oldk = {l.split("=")[0].strip() for l in old if "=" in l and not l.startswith("#")}
    curk = {l.split("=")[0].strip() for l in cur if "=" in l and not l.startswith("#")}
    lost = oldk - curk
    print("  [--] keys removed since that backup: %s" % (", ".join(sorted(lost)) if lost else "none"))
    print("  [%s] expected removals only (GMAIL_APP_PASSWORD / MS_JWT_SECRET)"
          % ("OK" if lost <= {"GMAIL_APP_PASSWORD", "MS_JWT_SECRET"} else "X "))
print("  [--] GMAIL_ADDRESS still in the file? %s" % ("yes" if any(l.startswith("GMAIL_ADDRESS") for l in cur) else "NO"))

print("\n  === 2. what does the running app actually have? ===")
pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8", "replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
pw = env.get("GMAIL_APP_PASSWORD", "")
addr = env.get("GMAIL_ADDRESS") or "dmcontiki2@gmail.com"   # the app's own fallback
print("  [--] GMAIL_ADDRESS in env : %s" % ("yes" if "GMAIL_ADDRESS" in env else "no - app falls back to the hardcoded default"))
print("  [--] address used for test: %s" % addr)
print("  [--] app password length  : %d  (Google issues 16)" % len(pw))
print("  [%s] length check" % ("OK" if len(pw) == 16 else "X "))
print("  [--] fingerprint          : %s" % fp(pw))

print("\n  === 3. SMTP login with the CORRECT address (sends nothing) ===")
if not pw:
    print("  [X]  no password loaded")
else:
    try:
        s = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
        s.starttls(); s.login(addr, pw); s.quit()
        print("  [OK] SMTP LOGIN ACCEPTED - the app password is good after all")
    except smtplib.SMTPAuthenticationError as exc:
        print("  [X]  SMTP LOGIN REJECTED - the password itself is wrong (code %s)" % exc.smtp_code)
    except Exception as exc:
        print("  [?]  could not test: %s" % str(exc)[:120])
