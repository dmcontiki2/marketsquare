#!/usr/bin/env python3
"""043_quick_me_route.py -- QUICK-ME-ROUTE-1 (18 Sep 2026).

Migration 042 (QUICK-PATH-1) added `location /quick/ { try_files /quick.html }`. That prefix also
swallowed the app's API endpoint GET /quick/me (QUICK-ME-1): the origin answered it with the HTML
page, so a stranger arriving by e-mail link never received the identity/key the Quick page needs
(regression ledger RG-0386 red, 18 Sep 2026: JSONDecodeError on /quick/me). An exact-match
location outranks any prefix in nginx, so /quick/me is handed back to the app here.

Same discipline as 042: write, nginx -t, reload, PROVE from the response (JSON, not HTML) on the
origin over TLS loopback; restore the backup and exit 1 otherwise.
"""
import os, shutil, subprocess, sys
from datetime import datetime, timezone
APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
VHOST = "/etc/nginx/sites-enabled/marketsquare"
BAK_DIR = "/root/nginx-backups"
BLOCK = """    # QUICK-ME-ROUTE-1 (18 Sep 2026): the app's /quick/me API must not fall into the /quick/ page door.
    location = /quick/me {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
"""

def _origin_body(path):
    import http.client, socket, ssl as _ssl
    ctx = _ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = _ssl.CERT_NONE
    try:
        conn = http.client.HTTPSConnection("127.0.0.1", 443, timeout=10, context=ctx)
        raw = socket.create_connection(("127.0.0.1", 443), timeout=10)
        conn.sock = ctx.wrap_socket(raw, server_hostname="trustsquare.co")
        conn.request("GET", path, headers={"Host": "trustsquare.co", "User-Agent": "TrustSquare-Migration/043"})
        r = conn.getresponse(); body = r.read(); conn.close()
        return r.status, body[:200]
    except Exception as ex:
        return repr(ex), b""

def _is_json(body):
    return body.lstrip()[:1] in (b"{", b"[")

def main():
    if not os.path.exists(VHOST):
        print("043: %s not found -- not this box; nothing to do" % VHOST); return 0
    src = open(VHOST, encoding="utf-8").read()
    if "location = /quick/me {" in src:
        print("043: /quick/me already routed to the app -- nothing to do"); return 0
    anchor = "    location = /quick { return 301 /quick/; }"
    if src.count(anchor) != 1:
        print("043: anchor (the /quick door from 042) not found exactly once -- refusing to guess a place"); return 1
    new = src.replace(anchor, BLOCK + anchor, 1)
    print("043: would route /quick/me to the app ahead of the /quick/ page door%s" % ("" if APPLY else "  [dry]"))
    if not APPLY:
        return 0
    os.makedirs(BAK_DIR, exist_ok=True)
    bak = os.path.join(BAK_DIR, "marketsquare.%s.bak-quickme" % TS)
    shutil.copy2(VHOST, bak); print("043: backup -> %s" % bak)
    open(VHOST, "w", encoding="utf-8").write(new)
    t = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    if t.returncode != 0:
        shutil.copy2(bak, VHOST); print("043: nginx -t FAILED, restored:\n" + t.stderr[-600:]); return 1
    subprocess.run(["systemctl", "reload", "nginx"], check=False)
    import time
    st, body = None, b""
    for _ in range(30):
        st, body = _origin_body("/quick/me")
        if _is_json(body) and _origin_body("/quick/")[0] == 200:
            break
        time.sleep(0.5)
    if not _is_json(body):
        shutil.copy2(bak, VHOST); subprocess.run(["systemctl", "reload", "nginx"], check=False)
        print("043: /quick/me still not answered by the app (%r %r) -- restored" % (st, body[:40])); return 1
    print("043: PROVED -- /quick/me answers JSON (%s) and /quick/ still serves the page. Rollback: cp %s %s && systemctl reload nginx" % (st, bak, VHOST))
    return 0

if __name__ == "__main__":
    sys.exit(main())
