#!/usr/bin/env python3
"""numista_match.py — N#-REFERRAL-1: ONE catalogue search per listing, nothing stored.

The whole point of this module is what it does NOT do. It returns candidates for a human
to choose from and never persists a response body, never caches a price, and never runs
on a page view. Numista's licence forbids storing catalogue data; storing the N# is
explicitly permitted, so the caller keeps the identifier and links out from then on.

Quota: the free plan allows 2,000 requests per calendar month. Because search happens only
at listing creation, that is 2,000 NEW COIN LISTINGS a month — a visitor cannot cause a
request. The cap below is belt and braces: on cap we degrade to "no candidates", so the
listing still publishes with no link. Never an error, never an overspend.
"""
import json
import os
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone

API = "https://api.numista.com/api/v3/types"
CATALOGUE_URL = "https://en.numista.com/catalogue/pieces%s.html"
MONTHLY_CAP = int(os.environ.get("NUMISTA_MONTHLY_CAP", "1800"))   # under the 2,000 free ceiling
STATE = os.environ.get("NUMISTA_COUNTER_PATH", "/var/www/marketsquare/.numista_counter.json")

# Required by Numista's terms wherever a catalogue result is shown.
SOURCE_CREDIT = "Catalogue data and price: Numista"


def _period():
    return datetime.now(timezone.utc).strftime("%Y-%m")


def _counter_read():
    try:
        with open(STATE) as fh:
            d = json.load(fh)
        if d.get("period") == _period():
            return int(d.get("count", 0))
    except Exception:
        pass
    return 0


def _counter_bump():
    n = _counter_read() + 1
    try:
        tmp = STATE + ".tmp"
        with open(tmp, "w") as fh:
            json.dump({"period": _period(), "count": n}, fh)
        os.replace(tmp, STATE)
    except Exception:
        pass
    return n


def quota_state():
    """(used, cap, remaining) for this calendar month - for the dashboard, no API call."""
    used = _counter_read()
    return {"used": used, "cap": MONTHLY_CAP, "remaining": max(0, MONTHLY_CAP - used),
            "period": _period()}


def catalogue_url(numista_id):
    return CATALOGUE_URL % numista_id


def search(query, *, lang="en", timeout=8.0, limit=8):
    """Return candidate matches for a HUMAN to choose from.

    Returns {"candidates": [...], "capped": bool, "credit": str}. Each candidate carries
    only id / title / issuer / years / url -- identifiers and labels, never a price. If a
    price ever appears in this return value, N#-REFERRAL-1 has been broken.
    """
    key = os.environ.get("NUMISTA_API_KEY")
    out = {"candidates": [], "capped": False, "credit": SOURCE_CREDIT}
    if not key or not query or not query.strip():
        return out

    if _counter_read() >= MONTHLY_CAP:
        out["capped"] = True          # degrade to "no candidates" - the listing still publishes
        return out

    url = "%s?%s" % (API, urllib.parse.urlencode({"q": query.strip(), "lang": lang}))
    req = urllib.request.Request(url, headers={
        "Numista-API-Key": key, "User-Agent": "TrustSquare/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = json.loads(r.read().decode("utf-8", "replace"))
    except Exception:
        return out                     # a dead feed is never a blocked listing
    finally:
        _counter_bump()                # count the attempt, not the success - quota is spent either way

    for t in (body.get("types") or [])[:limit]:
        tid = t.get("id")
        if not tid:
            continue
        out["candidates"].append({
            "id": tid,
            "title": t.get("title") or "",
            "issuer": ((t.get("issuer") or {}).get("name") or ""),
            "years": t.get("min_year") and ("%s-%s" % (t.get("min_year"), t.get("max_year") or "")) or "",
            "url": catalogue_url(tid),
        })
    return out
