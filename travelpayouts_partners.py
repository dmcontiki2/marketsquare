#!/usr/bin/env python3
"""travelpayouts_partners.py — TP-LINKOUT-1 (24 Aug 2026).

THE SAFE SHAPE OF AN AFFILIATE INTEGRATION, and the reason it exists.

On 2 Aug 2026 a Travelpayouts "Drive" loader went into the <head> of the index
and 9 adventures maps. It pulled remote code from tp-em.com into the same
document that renders the SA Smart ID / passport upload flow, POSTed to
/collect and /collect_batch on every load, and called /link-switch/v1/convert
with the visited URL — all from a page whose pre-launch "gate" was a client-side
overlay, so it ran for every visitor, bot and scanner regardless of password.
David's ruling, 3 Aug: no third-party code on the app at all. Ledger RG-0025.

The breach did not happen because anyone was careless. It happened because the
EASY path was their script and there was no house-built alternative on disk.
This module is that alternative, so "no" stays cheap the next time their
dashboard offers +25% rewards to switch Drive back on (it is doing exactly that
today, 24 Aug, expiring today, on the very programs we most want).

HOW THIS DIFFERS FROM DRIVE, IN ONE LINE EACH
  Drive: their JS runs in our page.        Here: no JS. Server-side 302 only.
  Drive: rewrites our outbound links.      Here: we author every link, in data.
  Drive: opens offers in a background tab. Here: the user clicks, and knows.
  Drive: reports clicks to them first.     Here: we record the click, then redirect.
  Drive: new hosts arrive without asking.  Here: a hard host allowlist, or 404.

FAILS CLOSED, DELIBERATELY
  * A program with no `deeplink` cannot be linked to. It 404s. The registry
    below carries brand facts PROBED from the partner dashboard on 24 Aug 2026,
    and `deeplink=None` everywhere, because the per-brand link formats have NOT
    been read yet and this module will not invent one. Filling a deeplink is a
    small dated act per program, done by reading that program's own link tool.
  * A deeplink whose host is not in ALLOWED_HOSTS is refused even if someone
    puts it in the registry — belt and braces against a future paste.
  * The whole lane is dark unless TP_LINKOUT_ENABLED is truthy in the server
    env. Off = every route 404s. Nothing customer-visible changes by merely
    deploying this file.

MODEL CONSTRAINT THIS RESPECTS (David, 1 Aug 2026)
  MarketSquare is an INTRODUCTORY service. Nothing flows through its till except
  Tuppence, and it is NEVER merchant of record for third-party goods or travel.
  A link-out is model-compatible precisely because the traveller pays the partner
  directly and we are never in the money path. Commission flowing IN is fine;
  the rule bars variable COSTS, not variable income (PRICING_CANON, 1 Aug).
"""
import os, sqlite3, time
from urllib.parse import urlsplit, urlencode, parse_qsl, urlunsplit

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse

router = APIRouter(prefix="/go", tags=["partners"])

MARKER = os.environ.get("TRAVELPAYOUTS_MARKER", "758984")   # partner ID 758984
ENABLED = str(os.environ.get("TP_LINKOUT_ENABLED", "")).strip().lower() in ("1", "true", "yes", "on")

# Every host any deeplink is allowed to point at. A host not here is refused
# even from inside our own registry. tp.media is Travelpayouts' own redirector,
# which is a LINK, not a script — it never executes in our page.
ALLOWED_HOSTS = {
    "tp.media",
    "www.aviasales.com", "aviasales.com",
    "www.klook.com", "klook.com",
    "www.tiqets.com", "tiqets.com",
    "www.getyourguide.com",          # blocked program today; host pre-allowed, deeplink stays None
    "wegotrip.com", "www.wegotrip.com",
    "www.kkday.com", "kkday.com",
    "gocity.com", "www.gocity.com",
    "welcomepickups.com", "www.welcomepickups.com",
}

# ---------------------------------------------------------------------------
# THE REGISTRY. Brand facts PROBED from app.travelpayouts.com on 24 Aug 2026,
# project "Trustsquare" (ID 758984), tab "My Programs -> Available 26".
# reward/cookie are recorded so a page can be honest about what it is doing
# without a session having to go and look them up again.
# ---------------------------------------------------------------------------
PROGRAMS = {
    # slug:            (brand,              category,              reward,        cookie,   deeplink)
    "aviasales":       ("Aviasales",        "Flights",             "40%",         "30 days", None),
    "kiwi":            ("Kiwi.com",         "Flights",             "3%",          "30 days", None),
    "klook":           ("Klook",            "Tours & Activities",  "2–5%",        "7–30 days", None),
    "tiqets":          ("Tiqets",           "Tours & Activities",  "3.5–8%",      "30 days", None),
    "wegotrip":        ("WeGoTrip",         "Tours & Activities",  "6.64–41.5%",  "30 days", None),
    "kkday":           ("KKday",            "Tours & Activities",  "1–5%",        "30 days", None),
    "gocity":          ("Go City",          "Tours & Activities",  "3.4–6%",      "90 days", None),
    "welcomepickups":  ("Welcome Pickups",  "Transfers",           "8–9%",        "45 days", None),
    "kiwitaxi":        ("Kiwitaxi",         "Transfers",           "9–11%",       "30 days", None),
    "gettransfer":     ("GetTransfer.com",  "Transfers",           "4–25%",       "30 days", None),
    "intui":           ("intui.travel",     "Transfers",           "10%",         "35 days", None),
    "localrent":       ("Localrent.com",    "Car rental",          "7.5–12%",     "30 days", None),
    "getrentacar":     ("GetRentacar.com",  "Car rental",          "10%",         "90 days", None),
    "economybookings": ("Economybookings",  "Car rental",          "3–8%",        "30 days", None),
    "qeeq":            ("QEEQ",             "Car rental",          "5–10%",       "30 days", None),
    "autoeurope":      ("AutoEurope (EU/UK)", "Car rental",        "4.4–8%",      "30 days", None),
    "bikesbooking":    ("BikesBooking.com", "Bike rental",         "4%",          "30 days", None),
    "radicalstorage":  ("Radical Storage",  "Luggage storage",     "8%",          "30 days", None),
    "airhelp":         ("AirHelp",          "Flight compensation", "15–16.6%",    "45 days", None),
    "compensair":      ("Compensair",       "Flight compensation", "€5–12 fixed", "30 days", None),
    "ekta":            ("EKTA",             "Travel insurance",    "25%",         "30 days", None),
    "airalo":          ("Airalo",           "eSIM",                "12%",         "30 days", None),
    "yesim":           ("Yesim",            "eSIM",                "18%",         "90 days", None),
    "gigsky":          ("GigSky",           "eSIM",                "20%",         "30 days", None),
    "saily":           ("Saily",            "eSIM",                "15%",         "30 days", None),
    "drimsim":         ("Drimsim",          "eSIM",                "€8 fixed",    "90 days", None),
}

# Programs Travelpayouts still BLOCKS for this project as at 24 Aug 2026, with
# the reason they give verbatim: "Your website is currently under development or
# not yet ready. Please complete setting up your site and re-submit your Project
# for review." Recorded here so no session re-discovers it by surprise.
BLOCKED = ("Booking.com", "Viator", "GetYourGuide", "Expedia", "Agoda", "Trip.com",
           "Tripadvisor – Experiences", "DiscoverCars", "Hotels.com", "Vrbo", "Omio",
           "12Go", "Hostelworld", "Busbud", "Traveloka", "Ticketmaster", "Vio.com",
           "Rakuten Travel", "VisitorsCoverage", "Insubuy")

DISCLOSURE = ("You are leaving TrustSquare for a partner site. We may earn a commission "
              "if you book. It costs you nothing extra, and we are not the seller — "
              "your booking and your money are between you and them.")


def _db():
    return sqlite3.connect(os.environ.get("MS_DB", "marketsquare.db"), timeout=10)


def init_schema():
    """Click-outs are recorded by US, before the partner ever hears about it."""
    try:
        with _db() as c:
            c.execute("""CREATE TABLE IF NOT EXISTS partner_clickouts (
                             id        INTEGER PRIMARY KEY AUTOINCREMENT,
                             slug      TEXT NOT NULL,
                             target    TEXT,
                             ref       TEXT,
                             ts        INTEGER NOT NULL)""")
            c.execute("CREATE INDEX IF NOT EXISTS idx_clickouts_slug ON partner_clickouts(slug, ts)")
    except Exception:
        pass          # a monitor must never break the app (same rule as predeploy_check)


def build_url(slug, target=None):
    """Return the outbound URL for a program, or None if it cannot be built SAFELY.

    Never invents a link. Never emits a host outside ALLOWED_HOSTS. Appends our
    marker as a query parameter, which is all Travelpayouts attribution needs —
    no script, no cookie written by us, no link rewriting.
    """
    row = PROGRAMS.get(slug)
    if not row:
        return None
    deeplink = row[4]
    if not deeplink:
        return None                      # honest gap: no format read yet -> no link
    parts = urlsplit(deeplink if "//" in deeplink else "https://" + deeplink)
    if parts.scheme != "https" or parts.netloc.lower() not in ALLOWED_HOSTS:
        return None                      # refuses even our own registry if it drifts
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q.setdefault("marker", MARKER)
    if target:
        t = urlsplit(target if "//" in target else "https://" + target)
        if t.scheme == "https" and t.netloc.lower() in ALLOWED_HOSTS:
            q["u"] = urlunsplit(t)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), parts.fragment))


@router.get("/partners")
def list_partners():
    """What we could link to, and — just as importantly — what we cannot."""
    if not ENABLED:
        raise HTTPException(status_code=404, detail="partner lane is dark")
    return JSONResponse({
        "marker": MARKER,
        "disclosure": DISCLOSURE,
        "linkable": sorted(s for s in PROGRAMS if PROGRAMS[s][4]),
        "awaiting_deeplink": sorted(s for s in PROGRAMS if not PROGRAMS[s][4]),
        "blocked_by_partner": list(BLOCKED),
        "note": "no third-party script is served by this lane, by design (RG-0025)",
    })


@router.get("/partner/{slug}")
def clickout(slug: str, request: Request, u: str = None):
    if not ENABLED:
        raise HTTPException(status_code=404, detail="partner lane is dark")
    url = build_url(slug, u)
    if not url:
        raise HTTPException(status_code=404, detail="no safe link for that partner")
    try:
        with _db() as c:
            c.execute("INSERT INTO partner_clickouts (slug, target, ref, ts) VALUES (?,?,?,?)",
                      (slug, u or "", (request.headers.get("referer") or "")[:300], int(time.time())))
    except Exception:
        pass                              # recording must never block the customer
    r = RedirectResponse(url, status_code=302)
    r.headers["Referrer-Policy"] = "no-referrer"     # partner learns nothing about the page
    return r


def selftest():
    """Prove the refusals actually refuse. Run: python3 travelpayouts_partners.py"""
    ok = True
    checks = [
        ("unknown slug refused",            build_url("not-a-partner") is None),
        ("no-deeplink program refused",     build_url("klook") is None),
        ("every registry deeplink is None or allowlisted", all(
            (not r[4]) or urlsplit("https://" + r[4].split("//")[-1]).netloc.lower() in ALLOWED_HOSTS
            for r in PROGRAMS.values())),
        ("no host in the allowlist is a Travelpayouts SCRIPT host", not (
            ALLOWED_HOSTS & {"tp-em.com", "emrld.cc"})),
        ("registry size matches the 26 probed on 24 Aug 2026", len(PROGRAMS) == 26),
        ("blocked list holds the 20 the partner refuses", len(BLOCKED) == 20),
    ]
    for label, passed in checks:
        print("  [%s] %s" % ("OK" if passed else "X ", label))
        ok = ok and passed
    # a deliberately bad deeplink must be refused
    PROGRAMS["__probe"] = ("Probe", "test", "", "", "https://tp-em.com/NTU3Mzkx.js")
    bad = build_url("__probe")
    del PROGRAMS["__probe"]
    print("  [%s] a tp-em.com deeplink is refused even from inside the registry"
          % ("OK" if bad is None else "X "))
    return 0 if (ok and bad is None) else 1


if __name__ == "__main__":
    import sys
    print("TP-LINKOUT-1 selftest (lane is %s)" % ("ON" if ENABLED else "DARK"))
    sys.exit(selftest())
