#!/usr/bin/env python3
"""relay_secret_install.py — INTRO-RELAY-1 rail, server half (v2 after the bat's
quoting failure). Reuses the EXISTING .secrets\relay_inbound_secret.txt if present
(so the clipboard/Cloudflare copy stays valid); generates only if missing. Installs
to the server .env (replace-not-duplicate), restarts the BEA, then VERIFIES:
exactly one env line present, service active, health 200 on localhost.
Prints statuses only — never the secret value."""
import os, secrets, subprocess, sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KEYF = os.path.join(REPO, ".secrets", "relay_inbound_secret.txt")
SERVER = os.environ.get("MS_SERVER_ROOT", "root@178.104.73.239")

def main():
    os.makedirs(os.path.dirname(KEYF), exist_ok=True)
    if os.path.exists(KEYF) and open(KEYF).read().strip():
        v = open(KEYF).read().strip()
        print("Using the existing local secret (clipboard/Cloudflare copies stay valid).")
    else:
        v = "rls_" + secrets.token_urlsafe(32)
        open(KEYF, "w").write(v)
        print("Generated a new secret into .secrets\\relay_inbound_secret.txt")
    try:
        subprocess.run(["clip"], input=v.encode(), check=True)
        print("Secret copied to clipboard (never shown on screen).")
    except Exception:
        print("(clipboard copy unavailable — the .secrets file holds it)")
    remote = ("sed -i '/^RELAY_INBOUND_SECRET=/d' /var/www/marketsquare/.env && "
              "printf 'RELAY_INBOUND_SECRET=%s\n' '" + v + "' >> /var/www/marketsquare/.env && "
              "systemctl restart marketsquare && sleep 4 && "
              "echo VERIFY-COUNT=$(grep -c '^RELAY_INBOUND_SECRET=' /var/www/marketsquare/.env) && "
              "echo VERIFY-SVC=$(systemctl is-active marketsquare) && "
              "echo VERIFY-HEALTH=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health)")
    r = subprocess.run(["ssh", SERVER, remote], capture_output=True, text=True)
    out = (r.stdout or "") + (r.stderr or "")
    shown = "\n".join(ln for ln in out.splitlines() if "RELAY_INBOUND_SECRET=" not in ln)
    print(shown.strip())
    ok = ("VERIFY-COUNT=1" in out and "VERIFY-SVC=active" in out and "VERIFY-HEALTH=200" in out)
    if r.returncode != 0 or not ok:
        print("\nINSTALL NOT PROVEN — check the ssh output above (is your key loaded?).")
        sys.exit(1)
    print("\nPROVEN: one env line, service active, health 200. The server half is live —")
    print("refresh the Launch Switch page: the relay row should read 'Cloudflare rail: configured'.")

if __name__ == "__main__":
    main()
