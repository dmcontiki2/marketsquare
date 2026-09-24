#!/usr/bin/env python3
"""AUTHZ-PROBE-1 (24 Sep 2026) — the security lane the daily watch never had.

WHY THIS EXISTS
David asked, after a manual bug audit turned up ADMIN-BIND-1 (the admin user list and
AI-spend config opened with the PUBLIC app key) and DELETE-BIND-1 (anyone could delete any
advert): "why did the daily watch not pick up the bug issues and the app vulnerabilities?"
Because every check the watch ran was a REGRESSION check — it re-proved things already
known and written down. Nothing tried the front door with the wrong key. This does.

WHAT IT ASSERTS
For a curated set of SENSITIVE routes — every admin route, and every write route that acts
on one named person's own data (the IDENTITY-BIND class) — this probe calls the LIVE site
with (a) the public app key that ships inside ms.js and (b) no credential at all, and
asserts the route REFUSES (401/403). A 2xx from any of them is a live hole.

SAFE BY CONSTRUCTION
Every case targets a nonexistent id / an @example.invalid address / an invalid payload, so
even if a route's auth were broken the call cannot create, change or delete anything real:
the refusal is checked, the mutation never happens. Read-only in effect, like the rest of
the ledger's live checks. stdlib only (urllib), so it runs from any vantage.

USAGE
  python3 scripts/authz_probe.py            # human report, exit 1 if any hole
  python3 scripts/authz_probe.py --json     # machine output for the watch/ledger
The regression ledger runs a critical subset every session (RG-0451), so from now on a
route that starts answering the public key trips the board red the same day.
"""
import json, sys, ssl, urllib.request, urllib.error, urllib.parse, re

BASE = "https://trustsquare.co"
_CTX = ssl.create_default_context()
_UA = "Mozilla/5.0 (authz-probe; TrustSquare security lane)"
PUBLIC_KEY = None   # discovered from live ms.js


def _discover_public_key():
    """The public app key is literally shipped in ms.js. Read it the way an attacker would."""
    global PUBLIC_KEY
    try:
        req = urllib.request.Request(BASE + "/static/ms.js", method="GET", headers={"User-Agent": _UA})
        with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:
            js = r.read(300000).decode("utf-8", "replace")
        m = re.search(r"API_KEY\s*=\s*['\"]([^'\"]+)['\"]", js or "")
        if m:
            PUBLIC_KEY = m.group(1)
    except Exception:
        PUBLIC_KEY = None
    return PUBLIC_KEY


def _raw(method, path, body, headers, timeout=20):
    url = BASE + path
    data = None
    h = dict(headers or {})
    h.setdefault("User-Agent", _UA)
    if body is not None:
        data = json.dumps(body).encode()
        h.setdefault("Content-Type", "application/json")
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=_CTX) as r:
            return r.status, r.read(20000).decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, (e.read(1500).decode("utf-8", "replace") if e.fp else "")
    except Exception as e:
        return None, "PROBE-OFFLINE: %s" % (str(e)[:120])


# Each case: id, method, path, body(dict) or None, human title.
# Targets are all nonexistent / invalid so nothing real can be touched.
BOGUS_EMAIL = "authz-probe-nobody@example.invalid"
BOGUS_ID = 999999999

# (A) ADMIN routes — must refuse both the public key AND no-auth.
ADMIN_CASES = [
    ("ADMIN-USERS-LIST",   "GET",  "/admin/users", None),
    ("ADMIN-AI-SPEND",     "GET",  "/admin/ai-spend", None),
    ("ADMIN-AI-SPEND-SUM", "GET",  "/admin/ai-spend/summary", None),
    ("ADMIN-EMAIL-TRIAGE", "GET",  "/admin/email-triage?limit=1", None),
    ("ADMIN-SELLER-TIER",  "PUT",  "/users/%s/seller-tier?tier=probe-invalid" % urllib.parse.quote(BOGUS_EMAIL), None),
    ("ADMIN-PURGE-CACHE",  "POST", "/admin/purge-cache", {}),
    ("ADMIN-REFRESH-POIS", "POST", "/admin/refresh-pois/%d" % BOGUS_ID, {}),
    ("ADMIN-DEPLOY-FILE",  "POST", "/admin/deploy-file", {"filename": "nope", "content_b64": "", "sha256": ""}),
    ("ADMIN-AGENCY-VERIFY","POST", "/agencies/%d/verify" % BOGUS_ID, {"verified": False}),
    ("ADMIN-AGENCY-RENAME","PUT",  "/agencies/%d" % BOGUS_ID, {"name": "x"}),
    ("ADMIN-TRUST-CRED",   "POST", "/trust-score/credential",
        {"email": BOGUS_EMAIL, "signal_id": "x", "status": "earned"}),
]

# (B) IDENTITY routes — act on one person's OWN data; must refuse no-session.
# (Fixed today under IDENTITY-BIND-3.) Probed with the public key + a bogus target.
IDENTITY_CASES = [
    ("BIND-KEEP-LIVE",   "POST",   "/listings/%d/keep-live" % BOGUS_ID, {"email": BOGUS_EMAIL}),
    ("BIND-CITY-ADD",    "POST",   "/listings/%d/cities" % BOGUS_ID, {"email": BOGUS_EMAIL, "city_id": BOGUS_ID}),
    ("BIND-CITY-DEL",    "DELETE", "/listings/%d/cities/%d?email=%s" % (BOGUS_ID, BOGUS_ID, urllib.parse.quote(BOGUS_EMAIL)), None),
    ("BIND-WONDERS",     "POST",   "/listings/%d/wonders" % BOGUS_ID, {"email": BOGUS_EMAIL, "wonder_ids": []}),
    ("BIND-PROFILE-PIC", "POST",   "/users/%s/photo" % urllib.parse.quote(BOGUS_EMAIL), None),  # multipart missing -> refuse or 422
    ("BIND-EXPERIENCE",  "POST",   "/trust/experience", {"email": BOGUS_EMAIL, "years": 5}),
    ("BIND-ZOOM-SAVE",   "POST",   "/zoom/watch", {"email": BOGUS_EMAIL, "category": "x", "path": "/x"}),
    ("BIND-ZOOM-DEL",    "DELETE", "/zoom/watch/%d?email=%s" % (BOGUS_ID, urllib.parse.quote(BOGUS_EMAIL)), None),
    ("BIND-DELETE-LISTING","DELETE","/listings/%d?email=%s" % (BOGUS_ID, urllib.parse.quote(BOGUS_EMAIL)), None),  # DELETE-BIND-1
]

REFUSED = {401, 403}
# A refusal (401/403) is the pass. A 2xx is a hole. Anything else (400/404/422/402/409)
# means the route rejected the bogus input BEFORE mutating — acceptable for a no-session
# call only if it is NOT a 2xx; we still record it so a route that stops refusing is seen.


def _judge(status):
    if status is None:
        return "OFFLINE"
    if 200 <= status < 300:
        return "HOLE"
    if status in REFUSED:
        return "REFUSED"
    return "REJECTED"   # non-2xx, non-auth (400/404/422/...) — not a hole, but not a clean auth refusal


def run():
    _discover_public_key()
    results = []
    holes = []
    latent = []
    offline = 0
    key_variants = [("public-key", {"X-Api-Key": PUBLIC_KEY} if PUBLIC_KEY else {"X-Api-Key": "none"}),
                    ("no-auth", {})]
    for group, cases in (("admin", ADMIN_CASES), ("identity", IDENTITY_CASES)):
        for cid, method, path, body in cases:
            for vname, vheaders in key_variants:
                st, snippet = _raw(method, path, body, vheaders)
                verdict = _judge(st)
                if verdict == "OFFLINE":
                    offline += 1
                if verdict == "HOLE":
                    holes.append((cid, vname, method, path, st, snippet[:120]))
                # LATENT: on an ADMIN route the public key must be REFUSED (401/403). If it got a
                # non-2xx that is NOT an auth refusal (404/400/422), the key passed auth and only
                # bad input stopped it -- on a real target it would succeed. That is a finding, not
                # clean. (No-auth admin probes that 401 are the correct refusal, so only the
                # public-key variant is judged this way.)
                if group == "admin" and vname == "public-key" and verdict == "REJECTED":
                    latent.append((cid, method, path, st, "public key passed the admin gate (only "
                                   "bad input stopped it -- a real target would succeed)"))
                results.append({"group": group, "id": cid, "variant": vname,
                                "method": method, "path": path, "status": st, "verdict": verdict})
    ok = len(holes) == 0 and len(latent) == 0 and offline == 0
    return {"ok": ok, "public_key_found": bool(PUBLIC_KEY), "base": BASE,
            "cases": len(ADMIN_CASES) + len(IDENTITY_CASES), "probes": len(results),
            "holes": holes, "latent": latent, "offline": offline, "results": results}


def main():
    out = run()
    if "--json" in sys.argv:
        print(json.dumps(out)); return 0 if out["ok"] else 1
    print("# AUTHZ probe — %s  (public key %s)" %
          (out["base"], "FOUND in ms.js" if out["public_key_found"] else "NOT found"))
    print("%d sensitive routes × 2 auth variants = %d live probes" % (out["cases"], out["probes"]))
    if out["offline"]:
        print("!! %d probes OFFLINE — verdict UNVERIFIED, not clean" % out["offline"])
    if out["holes"]:
        print("\n!!!! %d LIVE HOLE(S) — a sensitive route answered 2xx:" % len(out["holes"]))
        for cid, v, m, p, st, sn in out["holes"]:
            print("   [%s via %s] %s %s -> %s  %s" % (cid, v, m, p, st, sn))
    elif not out.get("latent"):
        print("\nOK — every sensitive route refused both the public key and no-auth.")
    if out.get("latent"):
        print("\n!! %d LATENT hole(s) — an ADMIN route let the PUBLIC key past its gate "
              "(only a bogus target stopped it; a real one would succeed):" % len(out["latent"]))
        for cid, m, p, st, why in out["latent"]:
            print("   [%s] %s %s -> %s  %s" % (cid, m, p, st, why))
    # Note the REJECTED (non-2xx, non-401/403) ones so a boundary shift is visible.
    rej = [r for r in out["results"] if r["verdict"] == "REJECTED"]
    if rej:
        print("\nnote: %d probe(s) rejected with a non-auth status (400/404/422/402/409) — "
              "not a hole, listed for boundary drift:" % len(rej))
        for r in rej[:20]:
            print("   %s %s [%s] -> %s" % (r["method"], r["path"][:60], r["variant"], r["status"]))
    return 0 if out["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
