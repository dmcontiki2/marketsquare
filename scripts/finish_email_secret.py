#!/usr/bin/env python3
"""finish_email_secret.py - mint ONE value, install it everywhere, record it for the Worker."""
import hashlib, os, secrets, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(REPO, ".secrets")
PASTE = os.path.join(SEC, "worker_secrets_to_paste.txt")
SERVER = os.environ.get("MS_SERVER_ROOT", "root@178.104.73.239")

val = "eis_" + secrets.token_urlsafe(32)
print("  minting one fresh value and installing it in every location...")
subprocess.run(["scp", "-q", os.path.join(REPO, "scripts", "set_email_secret.py"),
                SERVER + ":/tmp/set_email_secret.py"], check=False)
r = subprocess.run(["ssh", SERVER, "python3 /tmp/set_email_secret.py '%s'; rm -f /tmp/set_email_secret.py" % val],
                   capture_output=True, text=True)
sys.stdout.write((r.stdout or "") + (r.stderr or ""))

# rewrite the paste file: keep the relay entry, replace the email one
relay_val = ""
if os.path.exists(PASTE):
    for ln in open(PASTE):
        if ln.strip().startswith("value:") and "rls_" in ln:
            relay_val = ln.split("value:", 1)[1].strip()
with open(PASTE, "w") as f:
    f.write("PASTE THESE INTO THE CLOUDFLARE WORKERS, THEN DELETE THIS FILE\n")
    f.write("=" * 62 + "\n\n")
    if relay_val:
        f.write("RELAY_INBOUND_SECRET\n  Worker: intro-relay\n"
                "  Settings > Variables and Secrets > RELAY_INBOUND_SECRET\n  value: %s\n\n" % relay_val)
    f.write("EMAIL_INBOUND_SECRET\n  Worker: trustsquare-email-triage\n"
            "  Settings > Variables and Secrets > EMAIL_INBOUND_SECRET\n  value: %s\n\n" % val)
    f.write("Until both are pasted, inbound email and the intro relay reject calls.\n")
print("\n  .secrets\\worker_secrets_to_paste.txt rewritten with the value now installed.")
