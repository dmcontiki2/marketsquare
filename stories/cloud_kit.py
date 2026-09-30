#!/usr/bin/env python3
"""
cloud_kit.py -- QA-CLOUD-1 / CLOUD-SHIP-1 (30 Sep 2026): the few things a Claude Code cloud session
needs to walk a story on trustsquare.co with no Gmail, no admin token and no SSH.

The session never holds the QA key: the environment's API credential makes the cloud proxy add
X-QA-Key to every request for trustsquare.co. So these calls just work from the cloud, and answer
404 anywhere else.

    python3 stories/cloud_kit.py ping                      # {"ok": true, "qa_key": true} -> the key arrives
    python3 stories/cloud_kit.py grant qa-thandi 3 "F2 walk: intro"
    python3 stories/cloud_kit.py image nanny_caregiver f2_01_door shot.png
    python3 stories/cloud_kit.py ship-status               # what the server did with your [ship] commit

In Playwright:
    from cloud_kit import signin_context
    await signin_context(ctx, "qa-thandi", "Thandi", review=True)   # ctx is now signed in (+ tester cookie)
"""
import json, os, ssl, sys, urllib.request, urllib.error, base64, io
from http.cookies import SimpleCookie

BASE = os.environ.get("TS_BASE", "https://trustsquare.co").rstrip("/")


def _ctx():
    ca = os.environ.get("SSL_CERT_FILE") or os.environ.get("REQUESTS_CA_BUNDLE")
    return ssl.create_default_context(cafile=ca) if ca and os.path.isfile(ca) else ssl.create_default_context()


def _call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(BASE + path, data=data, method=method,
                                 headers={"Content-Type": "application/json", "User-Agent": "ts-cloud-walk"})
    try:
        with urllib.request.urlopen(req, context=_ctx(), timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}"), r.headers.get_all("Set-Cookie") or []
    except urllib.error.HTTPError as e:
        try:
            det = json.loads(e.read() or b"{}")
        except Exception:
            det = {}
        return e.code, det, []


def qa_email(who):
    """'qa-thandi' or 'thandi' -> dmcontiki2+qa-thandi@gmail.com (the only addresses the QA routes serve)."""
    w = who.split("@")[0].replace("dmcontiki2+", "")
    return "dmcontiki2+%s@gmail.com" % (w if w.startswith("qa-") else "qa-" + w)


def ping():
    return _call("GET", "/qa/ping")[:2]


def signin_cookies(who, name="", review=False):
    """Signs a QA address in; returns Playwright cookie dicts for trustsquare.co."""
    st, js, raw = _call("POST", "/qa/signin", {"email": qa_email(who), "name": name, "review": review})
    if st != 200:
        raise SystemExit("qa/signin %s: %s" % (st, js))
    host = BASE.split("://", 1)[1].split("/")[0]
    out = []
    for h in raw:
        c = SimpleCookie(); c.load(h)
        for k, m in c.items():
            out.append({"name": k, "value": m.value, "domain": host, "path": m["path"] or "/",
                        "httpOnly": True, "secure": True, "sameSite": "Lax"})
    return out


async def signin_context(ctx, who, name="", review=False):
    await ctx.add_cookies(signin_cookies(who, name, review))


def grant(who, amount=1, reason=""):
    return _call("POST", "/qa/grant", {"email": qa_email(who), "amount": int(amount), "reason": reason})[:2]


def help_image(type_key, name, path):
    """Any screenshot -> JPEG (<400 KB, 780 px wide as the phone screens are) -> /help/img/<type>/<name>.jpg,
    and a local copy in stories/img/<type>/ so build_help.py --check passes here too."""
    raw = open(path, "rb").read()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw)).convert("RGB")
        if im.width > 780:
            im = im.resize((780, int(im.height * 780 / im.width)))
        q = 82
        while True:
            b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True); raw = b.getvalue()
            if len(raw) < 380_000 or q <= 40:
                break
            q -= 8
    except ImportError:
        if raw[:3] != b"\xff\xd8\xff":
            raise SystemExit("pip install pillow (or pass a JPEG)")
    here = os.path.dirname(os.path.abspath(__file__))
    d = os.path.join(here, "img", type_key); os.makedirs(d, exist_ok=True)
    open(os.path.join(d, name + ".jpg"), "wb").write(raw)
    return _call("POST", "/qa/help-image", {"type": type_key, "name": name,
                                            "jpeg_b64": base64.b64encode(raw).decode()})[:2]


def ship_status():
    return _call("GET", "/qa/ship-status")[:2]


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    if a[0] == "ping":
        print(ping())
    elif a[0] == "grant":
        print(grant(a[1], int(a[2]) if len(a) > 2 else 1, " ".join(a[3:])))
    elif a[0] == "image":
        print(help_image(a[1], a[2], a[3]))
    elif a[0] == "ship-status":
        st, js = ship_status(); print(st); print("\n".join(js.get("lines", [])) if isinstance(js, dict) else js)
    elif a[0] == "signin":
        print(len(signin_cookies(a[1], a[2] if len(a) > 2 else "", True)), "cookie(s)")
    else:
        print(__doc__)
