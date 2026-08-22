#!/usr/bin/env python3
"""verify_gmail_password.py - can the app password the server holds log in to Gmail SMTP?
Sends NOTHING. Prints no secret values."""
import hashlib, smtplib, subprocess
def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def out(c): return subprocess.run(c, shell=True, capture_output=True, text=True).stdout.strip()
pid = out("systemctl show -p MainPID --value marketsquare")
env = {}
for e in open("/proc/%s/environ" % pid, "rb").read().decode("utf8","replace").split("\0"):
    if "=" in e:
        k, v = e.split("=", 1); env[k] = v
addr, pw = env.get("GMAIL_ADDRESS", ""), env.get("GMAIL_APP_PASSWORD", "")
print("  [--] account   : %s" % (addr or "NOT SET"))
print("  [--] app pw    : fingerprint %s (length %d)" % (fp(pw), len(pw)))
if not pw:
    print("  [X]  no app password loaded - SMTP fallback is dark"); raise SystemExit(1)
try:
    s = smtplib.SMTP("smtp.gmail.com", 587, timeout=20)
    s.starttls(); s.login(addr, pw); s.quit()
    print("  [OK] SMTP LOGIN ACCEPTED - the new app password works. Nothing was sent.")
except smtplib.SMTPAuthenticationError:
    print("  [X]  SMTP LOGIN REJECTED - wrong or revoked app password")
except Exception as exc:
    print("  [?]  could not test: %s" % str(exc)[:120])
