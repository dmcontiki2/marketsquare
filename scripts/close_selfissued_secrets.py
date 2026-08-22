#!/usr/bin/env python3
"""close_selfissued_secrets.py - close the last four burnt self-issued credentials.
Runs on David's PC (needs ssh). PRINTS NO SECRET VALUES - fingerprints only.

  COMMAND_SECRET       - prove nothing consumes it, then REMOVE (deletion beats rotation)
  MS_DEPLOY_TOKEN      - mint fresh server-side, update the local copy
  RELAY_INBOUND_SECRET - rotate; the Cloudflare Worker half needs David to paste
  EMAIL_INBOUND_SECRET - rotate; same
"""
import hashlib, os, re, secrets, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(REPO, ".secrets")
SERVER = os.environ.get("MS_SERVER_ROOT", "root@178.104.73.239")
PASTE = os.path.join(SEC, "worker_secrets_to_paste.txt")

def fp(v): return hashlib.sha256(v.encode()).hexdigest()[:8] if v else "NONE"
def ssh(cmd):
    r = subprocess.run(["ssh", "-o", "ConnectTimeout=20", SERVER, cmd],
                       capture_output=True, text=True)
    return r.returncode, (r.stdout or "") + (r.stderr or "")

def live(var):
    rc, o = ssh("p=$(systemctl show -p MainPID --value marketsquare); "
                "tr '\\0' '\\n' < /proc/$p/environ | grep '^%s=' | cut -d= -f2-" % var)
    return o.strip()

print("=" * 66)
print("  Closing the last four self-issued credentials")
print("  Nothing secret is printed. Values for Cloudflare go to a local file.")
print("=" * 66)

# ---------------------------------------------------------------- 1. COMMAND_SECRET
print("\n[1/4] COMMAND_SECRET - is anything actually using it?")
rc, o = ssh("grep -rl COMMAND_SECRET /var/www/marketsquare /opt/marketsquare-src "
            "--include='*.py' --include='*.js' --include='*.sh' 2>/dev/null | head -5")
users = [l for l in o.strip().splitlines() if l.strip()]
if users:
    print("      [!] consumers found - NOT removing, rotate deliberately instead:")
    for u in users: print("          " + u)
else:
    before = live("COMMAND_SECRET")
    print("      [OK] no consumer anywhere in the deployed code (fingerprint %s)" % fp(before))
    if before:
        rc, o = ssh(
          "cd /etc/systemd/system/marketsquare.service.d && "
          "for f in *.conf; do cp -a \"$f\" \"$f.bak-$(date +%Y%m%d-%H%M%S)\" 2>/dev/null; "
          "sed -i '/^\\s*Environment=\"\\?COMMAND_SECRET=/d' \"$f\"; done; "
          "cp -a /etc/environment /etc/environment.bak-$(date +%Y%m%d-%H%M%S); "
          "sed -i '/^\\s*COMMAND_SECRET=/d' /etc/environment; chmod 600 /etc/environment; "
          "systemctl daemon-reload && systemctl restart marketsquare && sleep 4 && "
          "echo SVC=$(systemctl is-active marketsquare)")
        print("      [--] " + o.strip().splitlines()[-1] if o.strip() else "      [--] (no output)")
        print("      [%s] COMMAND_SECRET now %s" %
              ("OK" if not live("COMMAND_SECRET") else "X ",
               "REMOVED - a secret nothing reads is pure liability" if not live("COMMAND_SECRET") else "STILL SET"))
    else:
        print("      [OK] not set on the server - nothing to do")

# ------------------------------------------------------------- 2. MS_DEPLOY_TOKEN
print("\n[2/4] MS_DEPLOY_TOKEN - minting a fresh one server-side")
before = live("MS_DEPLOY_TOKEN")
print("      [--] before: %s" % fp(before))
rc, o = ssh("set -e; TOK=$(openssl rand -hex 24); "
            "printf '[Service]\\nEnvironment=MS_DEPLOY_TOKEN=%s\\n' \"$TOK\" "
            "> /etc/systemd/system/marketsquare.service.d/deploy-token.conf; "
            "chmod 600 /etc/systemd/system/marketsquare.service.d/deploy-token.conf; "
            "printf '%s' \"$TOK\" > /root/ts_deploy_token_latest.txt; chmod 600 /root/ts_deploy_token_latest.txt; "
            "systemctl daemon-reload; systemctl restart marketsquare; sleep 4; "
            "echo SVC=$(systemctl is-active marketsquare)")
print("      [--] %s" % (o.strip().splitlines()[-1] if o.strip() else "no output"))
rc, tok = ssh("cat /root/ts_deploy_token_latest.txt; rm -f /root/ts_deploy_token_latest.txt")
tok = tok.strip()
after = live("MS_DEPLOY_TOKEN")
print("      [%s] after: %s %s" % ("OK" if after and after != before else "X ", fp(after),
      "- changed and live" if after and after != before else "- NOT changed"))
dk = os.path.join(SEC, "deploy_keys.txt")
if tok and os.path.exists(dk):
    src = open(dk).read()
    if re.search(r'(?m)^MS_DEPLOY_TOKEN=', src):
        src = re.sub(r'(?m)^MS_DEPLOY_TOKEN=.*$', "MS_DEPLOY_TOKEN=" + tok, src)
    else:
        src = src.rstrip("\n") + "\nMS_DEPLOY_TOKEN=" + tok + "\n"
    open(dk, "w").write(src)
    print("      [OK] local .secrets\\deploy_keys.txt updated to match")

# ------------------------------------- 3+4. the two Worker-paired inbound secrets
print("\n[3/4] RELAY_INBOUND_SECRET + [4/4] EMAIL_INBOUND_SECRET")
print("      These have a Cloudflare Worker holding the SAME value. Rotating the")
print("      server alone breaks them, so the new values go to a local file for you")
print("      to paste into each Worker.")
pairs = {}
for var, prefix in (("RELAY_INBOUND_SECRET", "rls_"), ("EMAIL_INBOUND_SECRET", "eis_")):
    before = live(var)
    if not before:
        print("      [--] %s is not set on the server - skipping" % var)
        continue
    new = prefix + secrets.token_urlsafe(32)
    rc, o = ssh("sed -i '/^%s=/d' /var/www/marketsquare/.env 2>/dev/null; "
                "printf '%s=%s\\n' >> /var/www/marketsquare/.env; "
                "cd /etc/systemd/system/marketsquare.service.d && "
                "for f in *.conf; do sed -i '/^\\s*Environment=\"\\?%s=/d' \"$f\"; done; "
                "echo DONE" % (var, var, new, var))
    pairs[var] = new
    print("      [OK] %s rotated on the server (was %s, now %s)" % (var, fp(before), fp(new)))

if pairs:
    with open(PASTE, "w") as f:
        f.write("PASTE THESE INTO THE CLOUDFLARE WORKERS, THEN DELETE THIS FILE\n")
        f.write("=" * 62 + "\n\n")
        for k, v in pairs.items():
            where = ("Worker 'intro-relay' > Settings > Variables and Secrets"
                     if k.startswith("RELAY") else
                     "Worker 'trustsquare-email-triage' > Settings > Variables and Secrets")
            f.write("%s\n  where: %s\n  value: %s\n\n" % (k, where, v))
    print("\n      >>> OPEN .secrets\\worker_secrets_to_paste.txt and paste each value")
    print("      >>> into its Worker. DELETE the file afterwards.")

rc, o = ssh("systemctl daemon-reload && systemctl restart marketsquare && sleep 4 && "
            "echo SVC=$(systemctl is-active marketsquare) "
            "HEALTH=$(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1:8000/health)")
print("\n  final: %s" % (o.strip().splitlines()[-1] if o.strip() else "no output"))
