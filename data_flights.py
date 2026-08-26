#!/usr/bin/env python3
"""data_flights.py — the indicative-fare lane (TP-FARES-1, 25 Aug 2026).

WHAT THIS IS FOR
----------------
MarketSquare gives travellers FREE pre-information so they can plan, and then
hands the plan to a real agency — that handoff IS the Tuppence introduction.
This module supplies one piece of that pre-information: an indicative "from
R x,xxx" for a route, so a journey map can say what a trip roughly costs
before anyone talks to anybody.

It is deliberately NOT a booking engine, NOT live availability, and NOT a
quote. MarketSquare never replaces a travel agency and says so on the surface.

THE DOCTRINE THIS OBEYS (David, 1 Aug 2026 — written after the Amadeus and
Google burns, and it is the reason this file is shaped the way it is)
--------------------------------------------------------------------
"No travel-data supplier may ever be load-bearing. The app reads ONLY our own
fare cache in our own schema; suppliers are swappable adapters behind it. The
cache is a parachute: supplier loss just ages the data."

So there are two completely separate paths and they never touch:

  READ PATH   get_indicative()  -> our SQLite fare_cache. Never calls a
              supplier. Cannot be slowed, rate-limited, billed or broken by
              anyone else's outage. If the cache is empty it says so and the
              surface falls back to the agency card.

  WRITE PATH  refresh()         -> the ONLY code that talks to a supplier.
              Runs on a schedule, never on a customer request. If the supplier
              is gone, yesterday's cache still serves, labelled with its age.

COST (David's question, 25 Aug 2026): ZERO, and structurally so.
  * Travelpayouts' flight DATA API is token-only and free. The 50k-MAU gate
    people quote applies to their SEARCH API, which we do not use.
  * No per-query billing, so no bill can run away the way Google's ~$360 did.
  * The only external cost shapes David's 1 Aug pricing rule permits are flat
    and cappable. This one is flat at zero. Duffel search ($0.005/query, hard
    monthly cap) remains the STANDBY adapter and is not wired.
  * Commission flows IN if a traveller books through a link-out. That is
    income, not a variable cost — the rule bars variable costs, not income.
  * Politeness cap: MAX_REFRESH_CALLS per refresh run, so even a buggy loop
    cannot hammer them. Their courtesy is the thing being protected here,
    since there is no bill to protect.

HONESTY RULES BAKED IN, NOT LEFT TO THE COPY
  * Every cached fare carries found_at + fetched_at, and get_indicative()
    returns its AGE. A surface that cannot show the age must not show a price.
  * A supplier returning nothing is a NORMAL answer, recorded as status='none'
    (the 1 Aug dry run found CPT-GRJ empty — thin routes genuinely have no
    cached fare). It is never an error and never an empty price on screen.
  * Stale beyond STALE_DAYS is not served as a price at all.
"""
import json, os, sqlite3, time, urllib.parse, urllib.request
from datetime import datetime, timezone

TOKEN = os.environ.get("TRAVELPAYOUTS_TOKEN", "")
MARKER = os.environ.get("TRAVELPAYOUTS_MARKER", "758984")
ACTIVE = os.environ.get("FARES_ADAPTER", "travelpayouts")
DEFAULT_CURRENCY = "zar"
STALE_DAYS = 21                 # older than this is history, not a price
MAX_REFRESH_CALLS = 40          # politeness cap per refresh run
TIMEOUT = 20

# Route table for the journey maps. origin -> destination, per map slug.
# Hubs, not every airport: a map says "getting there from Johannesburg costs
# about X", which is exactly the grain of pre-information we promise.
MAP_ROUTES = {
    "za":      ("JNB", "CPT"),
    "reserve": ("JNB", "CPT"),
    "c2c":     ("JNB", "CAI"),
    "na":      ("JNB", "WDH"),
    "bw":      ("JNB", "GBE"),
    "mz":      ("JNB", "MPM"),
    "ke":      ("JNB", "NBO"),
    "uk":      ("JNB", "LHR"),
    "gb":      ("JNB", "LHR"),
    "gb_rail": ("JNB", "LHR"),
    "de":      ("JNB", "FRA"),
    "us":      ("JNB", "JFK"),
    "us_rail": ("JNB", "JFK"),
    "au":      ("JNB", "SYD"),
    "au_rail": ("JNB", "SYD"),
}

DISCLAIMER = ("Indicative only — a recently seen fare, not a quote and not live availability. "
              "Confirm with a travel agency before you plan around it.")


def _db():
    return sqlite3.connect(os.environ.get("MS_DB", "marketsquare.db"), timeout=10)


def init_schema():
    with _db() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS fare_cache (
                         origin      TEXT NOT NULL,
                         destination TEXT NOT NULL,
                         currency    TEXT NOT NULL,
                         status      TEXT NOT NULL DEFAULT 'ok',   -- ok | none
                         price       INTEGER,
                         airline     TEXT,
                         gate        TEXT,
                         depart_date TEXT,
                         deeplink    TEXT,
                         found_at    TEXT,
                         fetched_at  INTEGER NOT NULL,
                         source      TEXT NOT NULL,
                         PRIMARY KEY (origin, destination, currency))""")


def flag_on():
    """launch_switches.data_flights — David's switch, read fresh every time."""
    try:
        with _db() as c:
            row = c.execute("SELECT data_flights FROM launch_switches WHERE id=1").fetchone()
        return bool(row and row[0])
    except Exception:
        return False            # fail dark: a flag we cannot read is a flag that is off


# ---------------------------------------------------------------------------
# WRITE PATH — the only place a supplier is contacted.
# ---------------------------------------------------------------------------
def _tp_fetch(origin, destination, currency):
    """Travelpayouts (Aviasales) flight DATA API. Returns dict or None.

    Endpoint and response shape PROBED live 25 Aug 2026 with the project token:
    v3 prices_for_dates returns a `link` — a relative Aviasales search path —
    which is the ONLY honest source of a deep link for this program. We do not
    invent affiliate URL formats (RG-0181).
    """
    if not TOKEN:
        return None
    q = urllib.parse.urlencode({
        "origin": origin, "destination": destination, "currency": currency,
        "sorting": "price", "limit": 1, "one_way": "true",
    })
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates?" + q
    req = urllib.request.Request(url, headers={
        "X-Access-Token": TOKEN,                 # header, never the query string
        "User-Agent": "TrustSquare-Fares/1.0",
    })
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        body = json.loads(r.read().decode("utf-8", "replace"))
    rows = body.get("data") or []
    if not rows:
        return None                               # thin route: a normal answer
    it = rows[0]
    price = it.get("price") or it.get("value")
    if not price:
        return None
    return {
        "price": int(price),
        "airline": (it.get("airline") or "")[:8],
        "gate": (it.get("gate") or "")[:40],
        "depart_date": (it.get("departure_at") or it.get("depart_date") or "")[:10],
        "deeplink": it.get("link") or "",
        "found_at": (it.get("found_at") or datetime.now(timezone.utc).isoformat())[:19],
    }


ADAPTERS = {"travelpayouts": _tp_fetch}
# Standby by doctrine, deliberately unwired: duffel (search $0.005 hard-capped),
# then signed-agency fare cards (irrevocable). Adding one is an adapter, not a rewrite.


def refresh(routes=None, currency=DEFAULT_CURRENCY):
    """Populate the cache. Scheduled only — never called on a request path."""
    init_schema()
    fetch = ADAPTERS.get(ACTIVE)
    if not fetch:
        return {"ok": 0, "none": 0, "error": "no adapter named %r" % ACTIVE}
    pairs = sorted(set(routes or MAP_ROUTES.values()))[:MAX_REFRESH_CALLS]
    ok = none = failed = 0
    for origin, dest in pairs:
        try:
            row = fetch(origin, dest, currency)
        except Exception:
            failed += 1
            continue                              # supplier trouble never wipes the cache
        now = int(time.time())
        with _db() as c:
            if row:
                c.execute("""INSERT INTO fare_cache
                             (origin,destination,currency,status,price,airline,gate,depart_date,
                              deeplink,found_at,fetched_at,source)
                             VALUES (?,?,?,'ok',?,?,?,?,?,?,?,?)
                             ON CONFLICT(origin,destination,currency) DO UPDATE SET
                               status='ok', price=excluded.price, airline=excluded.airline,
                               gate=excluded.gate, depart_date=excluded.depart_date,
                               deeplink=excluded.deeplink, found_at=excluded.found_at,
                               fetched_at=excluded.fetched_at, source=excluded.source""",
                          (origin, dest, currency, row["price"], row["airline"], row["gate"],
                           row["depart_date"], row["deeplink"], row["found_at"], now, ACTIVE))
                ok += 1
            else:
                c.execute("""INSERT INTO fare_cache
                             (origin,destination,currency,status,fetched_at,source)
                             VALUES (?,?,?,'none',?,?)
                             ON CONFLICT(origin,destination,currency) DO UPDATE SET
                               status='none', fetched_at=excluded.fetched_at""",
                          (origin, dest, currency, now, ACTIVE))
                none += 1
        time.sleep(0.25)                          # be a good neighbour
    return {"ok": ok, "none": none, "failed": failed, "adapter": ACTIVE}


# ---------------------------------------------------------------------------
# READ PATH — our cache only. No network. No supplier. No surprises.
# ---------------------------------------------------------------------------
def get_indicative(origin, destination, currency=DEFAULT_CURRENCY):
    try:
        with _db() as c:
            c.row_factory = sqlite3.Row
            row = c.execute("""SELECT * FROM fare_cache
                               WHERE origin=? AND destination=? AND currency=?""",
                            (origin, destination, currency)).fetchone()
    except Exception:
        row = None
    if not row or row["status"] != "ok" or not row["price"]:
        return {"available": False, "fallback": "agency",
                "reason": "no indicative fare cached for this route"}
    age_days = (int(time.time()) - int(row["fetched_at"])) / 86400.0
    if age_days > STALE_DAYS:
        return {"available": False, "fallback": "agency",
                "reason": "cached fare is %d days old — too stale to show as a price" % age_days}
    return {
        "available": True,
        "origin": row["origin"], "destination": row["destination"],
        "price": row["price"], "currency": (row["currency"] or "").upper(),
        "airline": row["airline"], "depart_date": row["depart_date"],
        "age_days": round(age_days, 1),
        "found_at": row["found_at"],
        "deeplink_path": row["deeplink"] or "",
        "disclaimer": DISCLAIMER,
    }


def route_for_map(slug):
    return MAP_ROUTES.get((slug or "").lower())


def selftest():
    """Offline. Proves the READ path never reaches the network and fails safe."""
    import tempfile as _tf   # HARNESS-TMPDIR-1: never a shared, possibly-stale path
    os.environ["MS_DB"] = os.path.join(_tf.mkdtemp(prefix="fares_selftest_"), "fares_selftest.db")
    try:
        os.remove(os.environ["MS_DB"])
    except OSError:
        pass
    init_schema()
    checks = [
        ("empty cache -> unavailable, agency fallback",
         get_indicative("JNB", "CPT")["available"] is False),
        ("unknown map slug -> no route", route_for_map("atlantis") is None),
        ("known map slug -> a route", route_for_map("c2c") == ("JNB", "CAI")),
        ("flag reads OFF when the table is absent (fails dark)", flag_on() is False),
    ]
    with _db() as c:
        c.execute("""INSERT INTO fare_cache (origin,destination,currency,status,price,fetched_at,source)
                     VALUES ('JNB','CPT','zar','ok',2264,?, 'selftest')""",
                  (int(time.time()) - 60 * 60 * 24 * 400,))
    checks.append(("a 400-day-old fare is refused, not shown",
                   get_indicative("JNB", "CPT")["available"] is False))
    with _db() as c:
        c.execute("UPDATE fare_cache SET fetched_at=? WHERE origin='JNB'", (int(time.time()),))
    fresh = get_indicative("JNB", "CPT")
    checks.append(("a fresh fare is served WITH its age and disclaimer",
                   fresh["available"] and "age_days" in fresh and bool(fresh["disclaimer"])))
    with _db() as c:
        c.execute("UPDATE fare_cache SET status='none', price=NULL WHERE origin='JNB'")
    checks.append(("a thin route ('none') is a normal answer, not an error",
                   get_indicative("JNB", "CPT")["fallback"] == "agency"))
    ok = True
    for label, passed in checks:
        print("  [%s] %s" % ("OK" if passed else "X ", label))
        ok = ok and passed
    return 0 if ok else 1


if __name__ == "__main__":
    import sys
    if "--refresh" in sys.argv:
        print(json.dumps(refresh(), indent=2))
        sys.exit(0)
    print("TP-FARES-1 selftest (offline, read path only)")
    sys.exit(selftest())
