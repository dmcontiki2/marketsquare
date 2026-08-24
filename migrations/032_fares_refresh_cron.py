#!/usr/bin/env python3
"""032_fares_refresh_cron.py — TP-FARES-1 (25 Aug 2026).

Installs the DAILY fare refresh and does the first fill, so the cache is warm
BEFORE David flips launch_switches.data_flights rather than empty on the day.

WHY A CRON AND NOT A REQUEST-TIME FETCH
---------------------------------------
Supplier-fallback doctrine (David, 1 Aug 2026, written after the Amadeus death
and the silent ~$360 Google bill): the app reads ONLY our own fare cache;
suppliers are swappable adapters behind it. So no traveller request may ever
reach a supplier. This cron is the ONLY thing on the box that talks to
Travelpayouts, and if it stops, the cache simply ages — ts_fares.js refuses to
show a fare older than 21 days and the surface falls back to the agency card.

DAILY, not hourly. Cached fares move slowly, the card prints the fare's age
next to the price, and a quiet integration is a good neighbour. The adapter
also carries its own politeness cap (MAX_REFRESH_CALLS) so even a broken loop
cannot hammer them.

COST: zero. The Travelpayouts flight DATA API is token-only and free — the
50k-MAU gate people quote is on their SEARCH API, which we do not use. There is
no per-query billing here, which is exactly why this lane was chosen over
Google (uncapped, burned ~$360 silently) and Duffel ($0.005/query, kept as a
capped standby adapter and NOT wired).

IDEMPOTENT: rewrites the cron file; the first fill is an upsert.
REVERSING IT:  rm /etc/cron.d/marketsquare-fares && (cache simply ages out)
VERIFY:        curl -s 'https://trustsquare.co/flights/indicative?map=za'
                 -> 404 while the flag is off (correct)
                 -> {"available":true,"price":...} once David flips it
Ledger RG-0182 asserts the whole lane, dark and lit.
"""
import os, subprocess, sys

CRON = "/etc/cron.d/marketsquare-fares"
LINE = ("20 6 * * * root cd /var/www/marketsquare && "
        "python3 data_flights.py --refresh >> /var/log/fares_refresh.log 2>&1\n")


def say(m):
    print("[032_fares] " + m, flush=True)


def load_env_token():
    """The first fill needs the token; cron gets it from the service env later.

    Reads the app's OWN .env on the box. The value is never printed, logged or
    returned — only placed into this process's environment.
    """
    if os.environ.get("TRAVELPAYOUTS_TOKEN"):
        return True
    for path in ("/var/www/marketsquare/.env", ".env"):
        if not os.path.isfile(path):
            continue
        try:
            for line in open(path, encoding="utf-8", errors="replace"):
                if line.strip().startswith("TRAVELPAYOUTS_TOKEN="):
                    os.environ["TRAVELPAYOUTS_TOKEN"] = line.split("=", 1)[1].strip().strip('"\'')
                    return True
        except Exception:
            pass
    return False


def main():
    if "--apply" not in sys.argv:
        say("dry: would write %s and run the first fare fill" % CRON)
        return 0

    with open(CRON, "w") as f:
        f.write("# TP-FARES-1 - daily indicative fare refresh (migrations/032)\n" + LINE)
    os.chmod(CRON, 0o644)
    open("/var/log/fares_refresh.log", "a").close()
    say("installed " + CRON)

    if not load_env_token():
        say("NOTE: TRAVELPAYOUTS_TOKEN not found in the environment or .env — cron is "
            "installed, but the first fill is skipped. The lane stays dark and empty, "
            "which is the safe state; provision the token and the 06:20 run fills it.")
        return 0

    try:
        import data_flights
        data_flights.init_schema()
        result = data_flights.refresh()
        say("first fill: %s" % result)
        if not result.get("ok"):
            say("NOTE: no route returned a fare. Not fatal — the surface shows nothing "
                "rather than something wrong, which is the designed behaviour.")
    except Exception as ex:
        say("first fill failed (%r) — cron installed, cache stays empty, surface stays "
            "silent. Not fatal." % ex)
    return 0


if __name__ == "__main__":
    sys.exit(main())
