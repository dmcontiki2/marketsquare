#!/usr/bin/env python3
"""
JOURNEY-1 — walk the PROSPECT's own path as a stranger.

Born 1 Sep 2026 from CTA-URL-1: three days of outreach went out behind a link
nobody had ever clicked. There were ~230 ledger assertions and not one of them
stood at the front door. Every check faced inward at the machinery.

This faces outward. It is deliberately dumb and end-to-end: build the link the
way the emailer builds it, follow it, and read what a stranger would see.

  python3 scripts/journey_check.py          # exit 0 = journey whole, 1 = broken
  python3 scripts/journey_check.py --json
"""
import json, sys, urllib.parse, urllib.request, urllib.error

BASE = "https://trustsquare.co"
UA   = {"User-Agent": "Mozilla/5.0 (TrustSquare journey-check)"}

# What a real prospect row produces, via emailer.build_magic_link()
PROSPECT = {"magic": "1", "name": "Journey Check", "email": "journey@example.com",
            "cat": "Tutors", "city": "Bloemfontein", "suburb": "Test Street",
            "src": "journey-check"}

# Markers that prove the SELLER flow rendered — not the admin console, not a gate.
WANT_ANY = ["STEP 1 OF 6", "LISTING QUALITY", "Photos"]
# Discriminate by TITLE, not by stray strings. The app carries dormant admin-gate
# markup ("Enter password or PIN") in its HTML that never renders for a visitor --
# PROBED 1 Sep in a clean browser: trustsquare.co shows the live marketplace. An
# earlier version of this check treated that markup as fatal and cried wolf, which
# is its own kind of failure: a check that false-alarms gets ignored, and then it
# is not a check at all.
ADMIN_TITLE = "TrustSquare \u00b7 Admin"   # admin.html's title -- must NEVER be what a prospect lands on


def get(url):
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), (e.read().decode("utf-8", "replace") if e.fp else "")


def main():
    out, fails = [], []
    link = BASE + "/?" + urllib.parse.urlencode(PROSPECT)
    # JOURNEY-2 (2 Sep 2026): the synthetic link above is what David's and the
    # testers' rows produce -- rows with NO stored magic_link. CTA-URL-1 lived in
    # the 3,526 SCRAPED rows whose stored link pointed at /admin.html, and no test
    # ever used one, which is why "it worked under test" for a month. So: pull a
    # real scraped row that STILL stores the broken form and run it through the
    # emailer's own build_magic_link(); if the read-time normaliser ever rots,
    # this leg goes red on real data, not on a fixture.
    try:
        import sqlite3, pathlib
        cl = pathlib.Path(__file__).resolve().parents[2] / "CityLauncher"
        sys.path.insert(0, str(cl / "emailer"))
        import emailer as _E
        con = sqlite3.connect(f"file:{cl / 'data' / 'prospects.db'}?mode=ro", uri=True)
        con.row_factory = sqlite3.Row
        row = con.execute("SELECT * FROM prospects WHERE magic_link LIKE '%/admin.html?%' "
                          "ORDER BY id LIMIT 1").fetchone()
        if row:
            real = _E.build_magic_link(dict(row), BASE + "/launch-api")
            out.append(("REAL_ROW", f"id={row['id']} -> {real[:90]}"))
            if "/admin.html" in real:
                fails.append("a REAL scraped row still yields an /admin.html CTA through "
                             "build_magic_link() -- the read-time repair has rotted (CTA-URL-1)")
            link = real   # walk the journey on the real row's link, not the fixture
        else:
            out.append(("REAL_ROW", "no scraped row stores /admin.html any more -- fixture only"))
    except Exception as e:  # the leg must never mask the rest of the journey
        out.append(("REAL_ROW", f"skipped: {e}"))
    out.append(("LINK", link))

    # LEG 1 — the CTA must never point at the admin console.
    if "/admin.html" in link:
        fails.append("the CTA points at /admin.html — the ADMIN CONSOLE (CTA-URL-1)")

    # LEG 2 — a stranger must be able to open it.
    code, hdrs, body = get(link)
    out.append(("HTTP", code))
    if code >= 400:
        fails.append("CTA returns HTTP %d to an anonymous prospect" % code)
    if any(h.lower() == "www-authenticate" for h in hdrs):
        fails.append("CTA answers with WWW-Authenticate — a browser password popup")

    # LEG 3 — what renders must be the SELLER flow, and nothing admin or gated.
    if ADMIN_TITLE in body or "TrustSquare · Admin" in body:
        fails.append("landing page is the ADMIN CONSOLE, not the seller flow (CTA-URL-1)")
    if "DELETE AN EXISTING LISTING" in body:
        fails.append("landing page exposes the admin delete control")
    if code < 400 and not any(w in body for w in WANT_ANY):
        fails.append("landing page shows none of %s — the seller form did not render"
                     % ", ".join(repr(w) for w in WANT_ANY))
    out.append(("SELLER_FORM", any(w in body for w in WANT_ANY)))

    if "--json" in sys.argv:
        print(json.dumps({"ok": not fails, "checks": dict(out), "fails": fails}, indent=1))
    else:
        print("JOURNEY-1 — the prospect's own path")
        for k, v in out:
            print("  %-12s %s" % (k, str(v)[:88]))
        print()
        if fails:
            for f in fails:
                print("  FAIL  " + f)
            print("\n  JOURNEY BROKEN — outreach must not send.")
        else:
            print("  OK — link, door and first form step all whole.")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
