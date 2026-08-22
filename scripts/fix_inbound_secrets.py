#!/usr/bin/env python3
"""fix_inbound_secrets.py - repair the two inbound secrets and finish COMMAND_SECRET.

Lesson being applied: a variable must be placed where THE CODE READS IT.
  EMAIL_INBOUND_SECRET  -> plain os.getenv() at module level  -> needs PROCESS ENV
  RELAY_INBOUND_SECRET  -> ai_provider.envkey()               -> process env OR /var/www/.env
Both get a drop-in that sorts last, so either reader finds them.

Runs on David's PC. Secret values are written ONLY to a local paste file, never printed
(this script's stdout is logged).
"""
import hashlib, os, re, secrets, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(REPO, ".secrets")
PASTE = os.path.join(SEC, "worker_secrets_to_paste.txt")
SERVER = os.environ.get("MS_SERVER_ROOT", "root@178.104.73.239")
DROPIN = "/etc/systemd/system/marketsquare.service.d/zz-inbound.conf"
ENVF = "/var/www/marketsquare/.env"

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def ssh(cmd):
    r = subprocess.run(["ssh", "-o", "ConnectTimeout=20", SERVER, cmd],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def in_process(var):
    _, o = ssh("p=$(systemctl show -p MainPID --value marketsquare); "
               "tr '\\0' '\\n' < /proc/$p/environ | grep '^%s=' | cut -d= -f2-" % var)
    return o.strip()

def in_envfile(var):
    _, o = ssh("grep '^%s=' %s 2>/dev/null | head -1 | cut -d= -f2- | tr -d '\"'" % (var, ENVF))
    return o.strip()

print("=" * 66)
print("  Repairing the inbound secrets (placed where the CODE reads them)")
print("=" * 66)

print("\n[1/3] COMMAND_SECRET - finish the removal")
_, o = ssh("grep -c '^COMMAND_SECRET=' /etc/environment 2>/dev/null || echo 0")
if o.strip().startswith("0"):
    print("      [OK] not present in /etc/environment either - fully gone")
else:
    ssh("cp -a /etc/environment /etc/environment.bak-$(date +%Y%m%d-%H%M%S); "
        "sed -i '/^COMMAND_SECRET=/d' /etc/environment; chmod 600 /etc/environment")
    _, o2 = ssh("grep -c '^COMMAND_SECRET=' /etc/environment 2>/dev/null || echo 0")
    print("      [%s] removed from /etc/environment (a burnt secret nothing reads is pure liability)"
          % ("OK" if o2.strip().startswith("0") else "X "))

print("\n[2/3] Reading each variable the way the CODE reads it")
state = {}
for var in ("EMAIL_INBOUND_SECRET", "RELAY_INBOUND_SECRET"):
    p, e = in_process(var), in_envfile(var)
    state[var] = (p, e)
    print("      %-22s process=%s  .env=%s" % (var, fp(p), fp(e)))

print("\n[3/3] Placing both in a last-sorting drop-in AND the env file")
vals = {}
# EMAIL: keep whatever we already rotated to (it is in .env); if absent, mint one.
ev = state["EMAIL_INBOUND_SECRET"][1] or state["EMAIL_INBOUND_SECRET"][0] or ("eis_" + secrets.token_urlsafe(32))
# RELAY: genuinely burnt and never rotated - mint a fresh one now.
rv = "rls_" + secrets.token_urlsafe(32)
vals["EMAIL_INBOUND_SECRET"], vals["RELAY_INBOUND_SECRET"] = ev, rv

body = "[Service]\\n" + "".join("Environment=%s=%s\\n" % (k, v) for k, v in vals.items())
cmd = ("umask 077 && printf '%s' > %s && chmod 600 %s && " % (body, DROPIN, DROPIN))
for k, v in vals.items():
    cmd += ("sed -i '/^%s=/d' %s 2>/dev/null; printf '%s=%s\\n' >> %s && " % (k, ENVF, k, v, ENVF))
cmd += ("systemctl daemon-reload && systemctl restart marketsquare && sleep 4 && "
        "echo SVC=$(systemctl is-active marketsquare) "
        "HEALTH=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health)")
rc, o = ssh(cmd)
print("      %s" % (o.strip().splitlines()[-1] if o.strip() else "no output"))

ok = True
for var, want in vals.items():
    got = in_process(var)
    good = got == want
    ok = ok and good
    print("      [%s] %-22s now in PROCESS env as %s" % ("OK" if good else "X ", var, fp(got)))

with open(PASTE, "w") as f:
    f.write("PASTE THESE INTO THE CLOUDFLARE WORKERS, THEN DELETE THIS FILE\\n")
    f.write("=" * 62 + "\\n\\n")
    f.write("RELAY_INBOUND_SECRET\\n  Worker: intro-relay\\n"
            "  Settings > Variables and Secrets > edit RELAY_INBOUND_SECRET\\n  value: %s\\n\\n" % rv)
    f.write("EMAIL_INBOUND_SECRET\\n  Worker: trustsquare-email-triage\\n"
            "  Settings > Variables and Secrets > edit EMAIL_INBOUND_SECRET\\n  value: %s\\n\\n" % ev)
    f.write("Until both are pasted, inbound email and the intro relay will reject calls.\\n")
print("\\n      >>> .secrets\\\\worker_secrets_to_paste.txt now holds BOTH values.")
print("      >>> Paste each into its Worker, then delete the file.")
print("\\n  RESULT: %s" % ("both secrets are where the code reads them" if ok
                          else "SOMETHING IS STILL WRONG - tell Claude"))
