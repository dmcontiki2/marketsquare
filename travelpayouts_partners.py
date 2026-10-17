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

# RUL-236 (David, 17 Oct 2026, "Please switch it on"): the lane is LIVE by ruling.
# TP_LINKOUT_ENABLED stays as the KILL SWITCH. The systemd unit does not export the
# app's .env, so the switch is read from the process env first and then from the
# app's own .env file. Set TP_LINKOUT_ENABLED=0 in either place and every route
# 404s again on the next restart; leave it unset and the ruling decides.
LINKOUT_ON_BY_RULING = True


def _env_flag(name):
    v = os.environ.get(name)
    if v is not None:
        return v
    for path in ("/var/www/marketsquare/.env", ".env"):
        try:
            for line in open(path, encoding="utf-8", errors="replace"):
                if line.strip().startswith(name + "="):
                    return line.split("=", 1)[1].strip().strip("\"'")
        except Exception:
            continue
    return None


_FLAG = _env_flag("TP_LINKOUT_ENABLED")
ENABLED = (LINKOUT_ON_BY_RULING if _FLAG in (None, "")
           else str(_FLAG).strip().lower() in ("1", "true", "yes", "on"))

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
    # LINKOUT-ON-1 (17 Oct 2026): Travelpayouts' own SHORT-LINK redirector, one
    # exact host per brand. These are LINKS (an HTTP 302 to the brand, carrying
    # partner ID 758984), never scripts. Each host is listed exactly -- no
    # wildcard -- so a link to a brand we did not generate is still refused.
    "tpx.lv",
    "klook.tpx.lv", "tiqets.tpx.lv", "wegotrip.tpx.lv", "kkday.tpx.lv", "gocity.tpx.lv",
    "kiwitaxi.tpx.lv", "gettransfer.tpx.lv", "intui.tpx.lv", "localrent.tpx.lv",
    "getrentacar.tpx.lv", "economybookings.tpx.lv", "qeeq.tpx.lv", "autoeurope.tpx.lv",
    "bikesbooking.tpx.lv", "radicalstorage.tpx.lv", "airhelp.tpx.lv", "compensair.tpx.lv",
    "ektatraveling.tpx.lv", "airalo.tpx.lv", "yesim.tpx.lv", "gigsky.tpx.lv",
    "saily.tpx.lv", "drimsim.tpx.lv", "kiwi.tpx.lv",
}

# Short links carry the partner ID INSIDE the link (Travelpayouts resolves it to
# the brand with marker 758984 attached). We pass them through untouched: adding
# ?marker= or ?u= to a short link is meaningless at best and breaks it at worst.
SHORTLINK_HOSTS = {h for h in ALLOWED_HOSTS if h == "tpx.lv" or h.endswith(".tpx.lv")}

# ---------------------------------------------------------------------------
# THE REGISTRY. Brand facts PROBED from app.travelpayouts.com on 24 Aug 2026,
# project "Trustsquare" (ID 758984), tab "My Programs -> Available 26".
# reward/cookie are recorded so a page can be honest about what it is doing
# without a session having to go and look them up again.
# ---------------------------------------------------------------------------
PROGRAMS = {
    # slug:            (brand,              category,              reward,        cookie,   deeplink)
    # DEEPLINK FILLED 25 Aug 2026 — READ from the live API, not invented (RG-0181).
    # v3 prices_for_dates returns a relative `link` such as /search/JNB1309CPT1?t=...
    # which is the program's own search URL; prefixed with the brand host and carrying
    # our marker it is a valid affiliate deep link. Probed JNB-CPT R1,187 the same day.
    # LINKOUT-ON-1 (17 Oct 2026): the other 25 deeplinks were GENERATED in the
    # Travelpayouts link tool (project Trustsquare, partner 758984) -- 23 with
    # "Generate link", Kiwi.com and GigSky from "Ready-made by brands" (UK main
    # page / Main page). Each was PROBED the same day: the short link 302s to the
    # brand with 758984 in the tracking parameter. Not typed from memory (RG-0181).
    "aviasales":       ("Aviasales",        "Flights",             "40%",         "30 days", "https://www.aviasales.com/"),
    "kiwi":            ("Kiwi.com",         "Flights",             "3%",          "30 days", "https://kiwi.tpx.lv/50VBvgTq"),
    "klook":           ("Klook",            "Tours & Activities",  "2–5%",        "7–30 days", "https://klook.tpx.lv/4Lo80fpa"),
    "tiqets":          ("Tiqets",           "Tours & Activities",  "3.5–8%",      "30 days", "https://tiqets.tpx.lv/alspsYmN"),
    "wegotrip":        ("WeGoTrip",         "Tours & Activities",  "6.64–41.5%",  "30 days", "https://wegotrip.tpx.lv/sgnKxmxt"),
    "kkday":           ("KKday",            "Tours & Activities",  "1–5%",        "30 days", "https://kkday.tpx.lv/s3NXelwz"),
    "gocity":          ("Go City",          "Tours & Activities",  "3.4–6%",      "90 days", "https://gocity.tpx.lv/yZHNXGaw"),
    "welcomepickups":  ("Welcome Pickups",  "Transfers",           "8–9%",        "45 days", "https://tpx.lv/4FS1Xc0U"),
    "kiwitaxi":        ("Kiwitaxi",         "Transfers",           "9–11%",       "30 days", "https://kiwitaxi.tpx.lv/92Cr68RL"),
    "gettransfer":     ("GetTransfer.com",  "Transfers",           "4–25%",       "30 days", "https://gettransfer.tpx.lv/fszaw9cC"),
    "intui":           ("intui.travel",     "Transfers",           "10%",         "35 days", "https://intui.tpx.lv/m1jzvydp"),
    "localrent":       ("Localrent.com",    "Car rental",          "7.5–12%",     "30 days", "https://localrent.tpx.lv/4ZE8BS8U"),
    "getrentacar":     ("GetRentacar.com",  "Car rental",          "10%",         "90 days", "https://getrentacar.tpx.lv/Oz8FkMQf"),
    "economybookings": ("Economybookings",  "Car rental",          "3–8%",        "30 days", "https://economybookings.tpx.lv/jhezSf5S"),
    "qeeq":            ("QEEQ",             "Car rental",          "5–10%",       "30 days", "https://qeeq.tpx.lv/Xh2V87kP"),
    "autoeurope":      ("AutoEurope (EU/UK)", "Car rental",        "4.4–8%",      "30 days", "https://autoeurope.tpx.lv/voa3RuXX"),
    "bikesbooking":    ("BikesBooking.com", "Bike rental",         "4%",          "30 days", "https://bikesbooking.tpx.lv/ZWFC3rqi"),
    "radicalstorage":  ("Radical Storage",  "Luggage storage",     "8%",          "30 days", "https://radicalstorage.tpx.lv/nNddPAoB"),
    "airhelp":         ("AirHelp",          "Flight compensation", "15–16.6%",    "45 days", "https://airhelp.tpx.lv/PWhiQezv"),
    "compensair":      ("Compensair",       "Flight compensation", "€5–12 fixed", "30 days", "https://compensair.tpx.lv/NDw8yPrH"),
    "ekta":            ("EKTA",             "Travel insurance",    "25%",         "30 days", "https://ektatraveling.tpx.lv/TDk3BqJw"),
    "airalo":          ("Airalo",           "eSIM",                "12%",         "30 days", "https://airalo.tpx.lv/q018JQHi"),
    "yesim":           ("Yesim",            "eSIM",                "18%",         "90 days", "https://yesim.tpx.lv/5bIGEPRO"),
    "gigsky":          ("GigSky",           "eSIM",                "20%",         "30 days", "https://gigsky.tpx.lv/QQvSu1kS"),
    "saily":           ("Saily",            "eSIM",                "15%",         "30 days", "https://saily.tpx.lv/LRj6vkLN"),
    "drimsim":         ("Drimsim",          "eSIM",                "€8 fixed",    "90 days", "https://drimsim.tpx.lv/5cshdXOn"),
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
    if parts.netloc.lower() in SHORTLINK_HOSTS:
        return urlunsplit(parts)         # partner ID is inside the short link; pass through untouched
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
        # LINKOUT-ON-1: what a page needs to draw an honest list -- brand and
        # category only. Reward rates are deliberately NOT exposed to customers.
        "programs": [{"slug": s, "brand": PROGRAMS[s][0], "category": PROGRAMS[s][1]}
                     for s in sorted(PROGRAMS) if build_url(s)],
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


def build_fare_url(path):
    """Turn the relative `link` a fare carries into a safe, marked affiliate URL.

    ALL outbound URL construction for this program goes through here so the host
    allowlist is enforced in exactly one place. A path that is not a relative
    path — anyone trying to smuggle an absolute URL through the fare cache —
    is refused outright rather than sanitised into something that looks fine.
    """
    if not path or not isinstance(path, str) or not path.startswith("/") or path.startswith("//"):
        return None
    host = "www.aviasales.com"
    if host not in ALLOWED_HOSTS:
        return None
    joined = "https://" + host + path
    parts = urlsplit(joined)
    q = dict(parse_qsl(parts.query, keep_blank_values=True))
    q["marker"] = MARKER
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(q), ""))


def _probe_none_refused():
    PROGRAMS["__none"] = ("Probe", "test", "", "", None)
    try:
        return build_url("__none") is None
    finally:
        del PROGRAMS["__none"]


def selftest():
    """Prove the refusals actually refuse. Run: python3 travelpayouts_partners.py"""
    ok = True
    checks = [
        ("unknown slug refused",            build_url("not-a-partner") is None),
        ("no-deeplink program refused",     _probe_none_refused()),
        ("every one of the 26 programs now builds a safe link", all(build_url(s) for s in PROGRAMS)),
        ("a short link passes through untouched (no marker/u appended)",
         build_url("klook", "https://www.klook.com/x") == "https://klook.tpx.lv/4Lo80fpa"),
        ("every registry deeplink is None or allowlisted", all(
            (not r[4]) or urlsplit("https://" + r[4].split("//")[-1]).netloc.lower() in ALLOWED_HOSTS
            for r in PROGRAMS.values())),
        ("no host in the allowlist is a Travelpayouts SCRIPT host", not (
            ALLOWED_HOSTS & {"tp-em.com", "emrld.cc"})),
        ("registry size matches the 26 probed on 24 Aug 2026", len(PROGRAMS) == 26),
        ("a relative fare path becomes a marked affiliate URL",
         (build_fare_url("/search/JNB1309CPT1?t=abc") or "").startswith("https://www.aviasales.com/search/")
         and "marker=" in (build_fare_url("/search/JNB1309CPT1?t=abc") or "")),
        ("an ABSOLUTE url smuggled through the fare cache is refused",
         build_fare_url("https://tp-em.com/x") is None and build_fare_url("//tp-em.com/x") is None),
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
