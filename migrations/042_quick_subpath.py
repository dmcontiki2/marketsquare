#!/usr/bin/env python3
"""042_quick_subpath.py -- QUICK-PATH-1 (RUL-125(a), 17 Sep 2026).

RUL-125(a): the Quick app lives on the SAME ORIGIN at a sub-path -- working path /quick/. It has
been served at /quick.html since QUICK-TILE-1 / QUICK-LIVE-1 (14-15 Sep); /quick/ answered 404.
This adds the ruled path as a second door onto the SAME file (no redirect away from /quick.html:
the installed tile's start_url and the address printed in outreach both keep working).

Same discipline as 033: write, nginx -t, reload, then PROVE it from the response; restore the
backup and exit 1 if the served path does not answer 200.
"""
import os, re, shutil, subprocess, sys
from datetime import datetime, timezone
APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
VHOST = "/etc/nginx/sites-enabled/marketsquare"
BAK_DIR = "/root/nginx-backups"
BLOCK = """    # QUICK-PATH-1 (RUL-125(a), 17 Sep 2026): the ruled sub-path onto the same file as /quick.html.
    location = /quick { return 301 /quick/; }
    location /quick/ {
        root /var/www/marketsquare;
        try_files /quick.html =404;
        add_header Cache-Control "public, max-age=300" always;
    }
"""

def _origin_status(path):
    """Status the ORIGIN serves for `path` on :443 -- loopback TCP, trustsquare.co SNI + Host.

    QUICK-PATH-2 (17 Sep 2026): the first cut of this migration probed http://127.0.0.1/quick/
    and let urllib follow the answer. Port 80 is Certbot's `return 301 https://...` block, so
    the probe measured a redirect and then followed it OUT through Cloudflare, which served the
    404 it had cached moments before the reload. The vhost was right; the instrument was wrong
    (the exact CSP-SCRIPT-SRC-7 trap 033 documents). Never follow redirects here; never leave
    the box.
    """
    import http.client, socket, ssl as _ssl
    ctx = _ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = _ssl.CERT_NONE
    try:
        conn = http.client.HTTPSConnection("127.0.0.1", 443, timeout=10, context=ctx)
        raw = socket.create_connection(("127.0.0.1", 443), timeout=10)
        conn.sock = ctx.wrap_socket(raw, server_hostname="trustsquare.co")
        conn.request("GET", path, headers={"Host": "trustsquare.co", "User-Agent": "TrustSquare-Migration/042"})
        r = conn.getresponse(); r.read(); conn.close()
        return r.status
    except Exception as ex:
        return repr(ex)

def main():
    if not os.path.exists(VHOST):
        print("042: %s not found -- not this box; nothing to do" % VHOST); return 0
    src = open(VHOST, encoding="utf-8").read()
    if "location /quick/ {" in src:
        print("042: /quick/ already served -- nothing to do"); return 0
    anchor = "    location = /q { return 301 /q/; }"
    if anchor not in src:
        print("042: anchor (the /q door) not found in the vhost -- refusing to guess a place"); return 1
    new = src.replace(anchor, BLOCK + anchor, 1)
    print("042: would add the /quick/ location before the /q door%s" % ("" if APPLY else "  [dry]"))
    if not APPLY:
        return 0
    os.makedirs(BAK_DIR, exist_ok=True)
    bak = os.path.join(BAK_DIR, "marketsquare.%s.bak-quickpath" % TS)
    shutil.copy2(VHOST, bak); print("042: backup -> %s" % bak)
    open(VHOST, "w", encoding="utf-8").write(new)
    t = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if t.returncode != 0:
        shutil.copy2(bak, VHOST); print("042: nginx -t FAILED, restored:\n" + t.stderr[-600:]); return 1
    subprocess.run(["systemctl", "reload", "nginx"], check=False)
    code = _origin_status("/quick/")
    if code != 200:
        shutil.copy2(bak, VHOST); subprocess.run(["systemctl", "reload", "nginx"], check=False)
        print("042: /quick/ did not answer 200 after reload (%r) -- restored" % (code,)); return 1
    print("042: PROVED -- /quick/ answers 200 on the box. Rollback: cp %s %s && systemctl reload nginx" % (bak, VHOST))
    return 0

if __name__ == "__main__":
    sys.exit(main())
