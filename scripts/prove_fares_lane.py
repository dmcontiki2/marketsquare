#!/usr/bin/env python3
"""prove_fares_lane.py — TP-FARES-1 harness (25 Aug 2026).

Proves the fare lane behaves correctly DARK and LIT, offline, against a
throwaway database. No network, no live site, no supplier.

The point is the DARK case. A lane that only gets tested lit is a lane whose
"off" is a hope. David flips launch_switches.data_flights himself, so the two
states either side of his switch are the thing that must be proven, and the
expensive failure is the one where the surface leaks a price before he flips.
"""
import os, sqlite3, sys, time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB = "/tmp/prove_fares.db"
os.environ["MS_DB"] = DB
os.environ.setdefault("TRAVELPAYOUTS_MARKER", "758984")
for f in (DB,):
    try:
        os.remove(f)
    except OSError:
        pass

import data_flights as F
import travelpayouts_partners as P


def endpoint(map_slug):
    """Mirrors bea_main's /flights/indicative body. 404 is expressed as None."""
    if not F.flag_on():
        return None
    route = F.route_for_map(map_slug)
    if not route:
        return None
    out = F.get_indicative(route[0], route[1])
    if out.get("available") and out.get("deeplink_path"):
        out["book_url"] = P.build_fare_url(out.pop("deeplink_path"))
        out["disclosure"] = P.DISCLOSURE
    else:
        out.pop("deeplink_path", None)
    return out


def set_flag(on):
    with sqlite3.connect(DB) as c:
        c.execute("CREATE TABLE IF NOT EXISTS launch_switches "
                  "(id INTEGER PRIMARY KEY CHECK (id=1), data_flights INTEGER NOT NULL DEFAULT 0)")
        c.execute("INSERT INTO launch_switches (id, data_flights) VALUES (1, ?) "
                  "ON CONFLICT(id) DO UPDATE SET data_flights=excluded.data_flights", (1 if on else 0,))


def seed_fare(deeplink="/search/JNB1309CPT1?t=abc123"):
    F.init_schema()
    with sqlite3.connect(DB) as c:
        c.execute("""INSERT INTO fare_cache (origin,destination,currency,status,price,airline,
                                             depart_date,deeplink,found_at,fetched_at,source)
                     VALUES ('JNB','CPT','zar','ok',1187,'FA','2026-09-13',?,?,?,'travelpayouts')
                     ON CONFLICT(origin,destination,currency) DO UPDATE SET
                       status='ok', price=1187, deeplink=excluded.deeplink,
                       fetched_at=excluded.fetched_at""",
                  (deeplink, "2026-08-21T18:54:49", int(time.time())))


checks = []


def check(label, passed):
    checks.append((label, bool(passed)))
    print("  [%s] %s" % ("OK" if passed else "X ", label))


print("TP-FARES-1 — proving the lane DARK, then LIT\n")

print("DARK (data_flights = 0) — David has not flipped it")
F.init_schema(); set_flag(False); seed_fare()
check("endpoint refuses even though a real fare IS cached", endpoint("za") is None)
check("every map slug is refused while dark",
      all(endpoint(s) is None for s in list(F.MAP_ROUTES)[:6]))

print("\nLIT (data_flights = 1) — after David's flip")
set_flag(True)
r = endpoint("za")
check("a cached fare is now served", bool(r and r.get("available")))
check("the price is the cached one, not a live fetch", r and r.get("price") == 1187)
check("the fare's AGE ships with it — a price without age is never shown",
      r and "age_days" in r)
check("the indicative disclaimer is present and non-empty",
      r and "Indicative" in (r.get("disclaimer") or ""))
check("commission disclosure ships with the link", r and bool(r.get("disclosure")))
check("book_url points at the brand host and carries our marker",
      r and (r.get("book_url") or "").startswith("https://www.aviasales.com/search/")
      and "marker=758984" in (r.get("book_url") or ""))

print("\nLIT but the data is bad — the surface must still say nothing")
with sqlite3.connect(DB) as c:
    c.execute("UPDATE fare_cache SET fetched_at=? WHERE origin='JNB'",
              (int(time.time()) - 60 * 60 * 24 * 400,))
check("a 400-day-old fare is withheld, not shown stale", not endpoint("za").get("available"))
with sqlite3.connect(DB) as c:
    c.execute("UPDATE fare_cache SET fetched_at=?, status='none', price=NULL WHERE origin='JNB'",
              (int(time.time()),))
check("a thin route falls back to the agency, with no price",
      endpoint("za").get("fallback") == "agency" and "price" not in endpoint("za"))
seed_fare(deeplink="https://tp-em.com/NTU3Mzkx.js")
r = endpoint("za")
check("a poisoned deeplink in the cache yields NO link rather than a bad one",
      r.get("available") and not r.get("book_url"))
check("an unknown map is refused", endpoint("atlantis") is None)

print("\nNO SUPPLIER IS REACHED ON A READ")
src = open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                        "data_flights.py"), encoding="utf-8").read()
read_path = src.split("def get_indicative", 1)[1].split("\ndef ", 1)[0]
check("get_indicative contains no urlopen/request — it is cache-only",
      "urlopen" not in read_path and "urllib" not in read_path)

bad = [l for l, ok in checks if not ok]
print("\n%d/%d passed" % (len(checks) - len(bad), len(checks)))
if bad:
    print("FAILED: " + "; ".join(bad))
sys.exit(1 if bad else 0)
