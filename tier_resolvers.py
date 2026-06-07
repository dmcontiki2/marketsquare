"""
tier_resolvers.py - FREE / owned data resolvers for the Tiered Value Selector
=============================================================================
STEP 3 resolver layer. Turns a listing + chosen tier into a REAL number with
provenance, using only zero-cost / no-contract / no-consumption-API sources:

  * internal_comps_estimate()  - median of comparable TrustSquare listings (owned)
  * UK property               - HM Land Registry Price Paid (keyless SPARQL, OGL)
  * US / UK rent              - HUD FMR / ONS-VOA area benchmarks (public / OGL)
  * ZA area guide             - PayProp/TPN aggregate benchmark (free, 0T)
  * collectibles (lego/coins/tcg) - BrickLink / Numista / JustTCG free feeds,
                                    CREDENTIAL-GATED: never called without a key
  * net_cost_band()           - versioned per-region net-yield cost band

Hard rule (mirrors the price-integrity model): the number comes from a feed or
arithmetic, NEVER from a language model. The LLM only narrates. Where no real
number exists, the resolver returns None and the caller charges nothing.

B7 (no paid/consumption API) is preserved structurally: the only network call
made here without a credential is the keyless, OGL-licensed UK Land Registry
SPARQL endpoint. Collectible feeds requiring a key short-circuit to None when
the key is absent, so an unconfigured feed is never hit.
"""

from __future__ import annotations

import os
import statistics
from typing import Iterable, Optional

import value_benchmarks as _vb


def served_tiers(service: str, tierkey: str, country: str,
                 *, creds: Optional[dict] = None) -> dict:
    """Map {tier: True} for tiers we can actually SERVE right now. A tier absent
    from this map (or False) means 'config-only' -> the FEA hides that chip."""
    creds = creds or {}
    country = (country or "").upper()
    out: dict = {}                                 # only tiers we can SERVE are listed
    if service == "fair_price":
        if tierkey in ("cards", "tcg"):
            out["1T"] = True                       # Scryfall (MTG); others free-fall
        elif tierkey == "lego":
            if creds.get("bricklink"):
                out["1T"] = True                   # dark without a key (B7)
        elif tierkey == "coins":
            if creds.get("numista"):
                out["1T"] = True
        elif tierkey == "property":
            if country == "ZA":
                out["0T"] = True                   # PayProp/TPN area guide (ZA only)
            out["1T"] = True                       # UK=Land Registry / US,ZA,AU=comps
        elif tierkey == "vehicles":
            out["1T"] = True                       # internal comps
        # S130: official eBay Browse asking-price band (free tier) lights ALL
        # collectible tierkeys incl. comics/watches once EBAY_APP_ID/EBAY_CERT_ID
        # are set; honest asking-not-sold wording enforced at the consumer.
        if tierkey in ("lego", "coins", "tcg", "cards", "comics", "watches") \
                and creds.get("ebay"):
            out["1T"] = True
    elif service == "yield":
        if tierkey == "property":
            if country == "ZA":
                out["0T"] = True                   # PayProp/TPN area benchmark
            if country in ("UK", "US", "ZA"):
                out["1T"] = True                   # ONS / HUD / internal comps
    return out


def creds_from_env() -> dict:
    """Which credentialled FREE feeds are configured (keys read from env only)."""
    return {
        "bricklink": bool(os.environ.get("BRICKLINK_TOKEN")
                          or os.environ.get("BRICKLINK_OAUTH_TOKEN")),
        "numista":   bool(os.environ.get("NUMISTA_API_KEY")),
        "justtcg":   bool(os.environ.get("JUSTTCG_API_KEY")),
        "ebay":      bool(os.environ.get("EBAY_APP_ID")
                          and os.environ.get("EBAY_CERT_ID")),
    }


def net_cost_band(country_iso2: str) -> dict:
    """Versioned, dated per-region net operating-cost band."""
    return _vb.net_cost_band(country_iso2)


def internal_comps_estimate(amounts: Iterable[float], *, min_n: int = 8,
                            label: str = "comparable TrustSquare listings") -> Optional[dict]:
    """Median of comparable listing amounts (price OR rent), gated on min sample."""
    vals = sorted(float(a) for a in amounts if a is not None and float(a) > 0)
    if len(vals) < max(1, int(min_n)):
        return None
    med = statistics.median(vals)
    return {
        "value": med, "n": len(vals), "low": vals[0], "high": vals[-1],
        "source": "internal_comps",
        "provenance": f"TrustSquare comps (n={len(vals)}) - median of {label}",
        "date": "live",
        "specificity": "comparable listings (not this exact item)",
    }


def za_area_price_guide(city: str, *, floor_area: Optional[float] = None) -> Optional[dict]:
    """ZA suburb/city price guide (R/m2 band). Aggregate, NOT property-specific."""
    rec = _vb.za_city(city)
    ppsqm, lo, hi = rec.get("ppsqm"), rec.get("ppsqm_lo"), rec.get("ppsqm_hi")
    if not ppsqm:
        return None
    out = {
        "ppsqm": ppsqm, "ppsqm_lo": lo, "ppsqm_hi": hi,
        "source": rec["source"], "date": rec["updated"], "licence": rec["licence"],
        "specificity": "area benchmark - not specific to this property",
        "range_text": f"R{lo:,.0f}-R{hi:,.0f} per m2 (typical R{ppsqm:,.0f}/m2)",
    }
    if floor_area and float(floor_area) > 0:
        fa = float(floor_area)
        out["implied_value"] = ppsqm * fa
        out["implied_low"] = (lo or ppsqm) * fa
        out["implied_high"] = (hi or ppsqm) * fa
    return out


def za_area_rent(city: str) -> Optional[dict]:
    """ZA suburb/city monthly-rent benchmark (aggregate PayProp/TPN)."""
    rec = _vb.za_city(city)
    rent = rec.get("rent_pm")
    if not rent:
        return None
    return {
        "value": rent, "low": rec.get("rent_lo"), "high": rec.get("rent_hi"),
        "source": rec["source"], "date": rec["updated"], "licence": rec["licence"],
        "specificity": "area benchmark - not specific to this property",
        "provenance": f"PayProp/TPN area rent benchmark ({rec['updated']})",
    }


def us_market_rent(area: str) -> Optional[dict]:
    rec = _vb.us_area(area)
    rent = rec.get("rent_pm")
    if not rent:
        return None
    return {"value": rent, "currency": "USD", "source": rec["source"],
            "date": rec["updated"], "licence": rec["licence"],
            "provenance": f"HUD Fair Market Rent, {rec['updated']}",
            "specificity": "area FMR (2-bed) - not property-specific"}


def uk_market_rent(region: str) -> Optional[dict]:
    rec = _vb.uk_region(region)
    rent = rec.get("rent_pm")
    if not rent:
        return None
    return {"value": rent, "currency": "GBP", "source": rec["source"],
            "date": rec["updated"], "licence": rec["licence"],
            "provenance": f"ONS/VOA private-rental median, {rec['updated']}",
            "specificity": "area median - not property-specific"}


_LR_ENDPOINT = "https://landregistry.data.gov.uk/landregistry/query"


def _lr_sparql(town: str, limit: int = 60) -> str:
    town_uc = str(town or "").strip().upper().replace('"', "")
    return (
        "PREFIX lrppi: <http://landregistry.data.gov.uk/def/ppi/>\n"
        "PREFIX lrcommon: <http://landregistry.data.gov.uk/def/common/>\n"
        "SELECT ?amount ?date WHERE {\n"
        "  ?txn lrppi:propertyAddress ?addr ;\n"
        "       lrppi:pricePaid ?amount ;\n"
        "       lrppi:transactionDate ?date .\n"
        f'  ?addr lrcommon:town "{town_uc}" .\n'
        "}\n"
        f"ORDER BY DESC(?date) LIMIT {int(limit)}"
    )


async def uk_land_registry_median(town: str, *, timeout: float = 8.0) -> Optional[dict]:
    """Median recent sold price for a town from HM Land Registry Price Paid
    (England & Wales), keyless SPARQL (OGL v3.0). Fails safe (None) on problem."""
    if not town:
        return None
    try:
        import httpx
        q = _lr_sparql(town)
        async with httpx.AsyncClient(timeout=timeout, headers={
            "User-Agent": "TrustSquare/1.0",
            "Accept": "application/sparql-results+json",
        }) as c:
            r = await c.get(_LR_ENDPOINT, params={"query": q})
            if r.status_code != 200:
                return None
            rows = (r.json().get("results", {}) or {}).get("bindings", []) or []
        amounts, latest = [], None
        for b in rows:
            try:
                amounts.append(float(b["amount"]["value"]))
            except Exception:
                continue
            d = (b.get("date") or {}).get("value")
            if d and (latest is None or d > latest):
                latest = d
        amounts = [a for a in amounts if a > 0]
        if len(amounts) < 5:
            return None
        amounts.sort()
        med = statistics.median(amounts)
        return {
            "value": med, "n": len(amounts), "low": amounts[0], "high": amounts[-1],
            "source": "land_registry",
            "provenance": (f"HM Land Registry Price Paid - {len(amounts)} sold in "
                           f"{town.title()} (median); latest {(latest or '')[:10]}"),
            "date": (latest or "")[:10] or "recent",
            "specificity": "town-level sold comparables (not this exact property)",
            "currency": "GBP",
        }
    except Exception:
        return None


async def bricklink_price(query: str, *, timeout: float = 8.0) -> Optional[dict]:
    """LEGO guide price via BrickLink. None unless creds configured (B7-safe)."""
    tok = os.environ.get("BRICKLINK_TOKEN") or os.environ.get("BRICKLINK_OAUTH_TOKEN")
    if not tok or not query:
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers={
            "Authorization": tok, "User-Agent": "TrustSquare/1.0"}) as c:
            r = await c.get("https://api.bricklink.com/api/store/v1/items/SET/"
                            f"{query}/price", params={"guide_type": "sold", "new_or_used": "U"})
            if r.status_code != 200:
                return None
            d = (r.json() or {}).get("data") or {}
            avg = d.get("avg_price")
            if not avg:
                return None
            return {"value": float(avg), "currency": d.get("currency_code", "USD"),
                    "source": "bricklink", "provenance": "BrickLink sold price guide",
                    "date": "live", "specificity": "set-specific"}
    except Exception:
        return None


async def numista_price(query: str, *, timeout: float = 8.0) -> Optional[dict]:
    """Coin price via Numista v3 catalogue estimates (S130 fix: the v3 endpoint
    is /types, not /coins — the original stub 404'd and could never price).
    Chain: /types?q -> /types/{id}/issues (year-matched from the query when
    possible, else latest) -> /issues/{id}/prices?currency=USD. Returns the
    mid-grade (VF) estimate with the full g->unc band. Catalogue estimates are
    collector references, NOT sale prices — the provenance says so. None
    unless NUMISTA_API_KEY is set (B7-safe). ~3 calls/check (quota 2k/month)."""
    key = os.environ.get("NUMISTA_API_KEY")
    if not key or not query:
        return None
    try:
        import re as _re
        import httpx
        hdrs = {"Numista-API-Key": key, "User-Agent": "TrustSquare/1.0"}
        async with httpx.AsyncClient(timeout=timeout, headers=hdrs) as c:
            r = await c.get("https://api.numista.com/api/v3/types",
                            params={"q": query, "count": 3, "lang": "en"})
            if r.status_code != 200:
                return None
            types = (r.json() or {}).get("types") or []
            if not types:
                return None
            t = types[0]
            tid = t.get("id")
            title = t.get("title") or "matched type"
            r = await c.get(f"https://api.numista.com/api/v3/types/{tid}/issues")
            if r.status_code != 200:
                return None
            issues = r.json() or []
            if not issues:
                return None
            chosen = None
            m = _re.search(r"\b(1[89]\d\d|20\d\d)\b", query)
            if m:
                want = int(m.group(1))
                for i in issues:
                    if i.get("gregorian_year") == want or i.get("year") == want:
                        chosen = i
                        break
            issue = chosen or issues[-1]
            r = await c.get(("https://api.numista.com/api/v3/types/"
                             f"{tid}/issues/{issue['id']}/prices"),
                            params={"currency": "USD"})
            if r.status_code != 200:
                return None
            prices = (r.json() or {}).get("prices") or []
        by_grade = {p.get("grade"): p.get("price")
                    for p in prices if p.get("price")}
        if not by_grade:
            return None
        vals = sorted(v for v in by_grade.values() if v)
        val = by_grade.get("vf") or by_grade.get("f") or by_grade.get("xf") \
            or vals[len(vals) // 2]
        iy = issue.get("gregorian_year") or issue.get("year") or ""
        return {"value": float(val), "low": vals[0], "high": vals[-1],
                "currency": "USD", "source": "numista", "ref": tid,
                "provenance": ("Numista catalogue estimate - " + str(title)
                               + (f" ({iy})" if iy else "")
                               + ", grade VF - collector reference, not a sale price"),
                "date": "live",
                "specificity": ("catalogue estimate for the matched type/issue "
                                "- verify exact variety")}
    except Exception:
        return None


async def justtcg_price(query: str, *, timeout: float = 8.0) -> Optional[dict]:
    """TCG price via JustTCG free tier (S130 fix: prices live per-VARIANT
    (condition x printing), not at card level — the original stub read a
    nonexistent top-level price and always returned None). Baseline = the
    CHEAPEST Near Mint printing (conservative "from" price for the common
    printing); the disclosed band spans ALL conditions/printings, because a
    1st-edition NM can be 50x the unlimited NM. None unless JUSTTCG_API_KEY
    is set (B7-safe)."""
    key = os.environ.get("JUSTTCG_API_KEY")
    if not key or not query:
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers={
            "x-api-key": key, "User-Agent": "TrustSquare/1.0"}) as c:
            r = await c.get("https://api.justtcg.com/v1/cards", params={"q": query})
            if r.status_code != 200:
                return None
            items = (r.json() or {}).get("data") or []
        if not items:
            return None
        card = items[0]
        variants = [v for v in (card.get("variants") or [])
                    if v.get("price") and float(v["price"]) > 0]
        if not variants:
            return None
        allp = sorted(float(v["price"]) for v in variants)
        nm = sorted(float(v["price"]) for v in variants
                    if (v.get("condition") or "").lower() == "near mint")
        val = nm[0] if nm else allp[len(allp) // 2]
        name = card.get("name") or "matched card"
        setn = card.get("set_name") or ""
        num = card.get("number") or ""
        basis = ("cheapest Near Mint printing" if nm
                 else "median across conditions/printings")
        return {"value": float(val), "low": allp[0], "high": allp[-1],
                "currency": "USD", "source": "justtcg", "ref": card.get("id"),
                "provenance": (f"JustTCG market price - {name}"
                               + (f", {setn}" if setn else "")
                               + (f" #{num}" if num else "")
                               + f"; baseline = {basis}; band spans all "
                                 "conditions/printings"),
                "date": "live",
                "specificity": ("card-specific; match YOUR printing + condition "
                                "- 1st-edition/graded copies trade far above "
                                "the baseline")}
    except Exception:
        return None


# ── eBay Browse API (official, free tier) — S130 quick-win ──────────────────
# ASKING-price band from live listings. Credential-gated (B7-safe): no key, no
# call. Number = median/percentile arithmetic over API results; LLM narrates.

_EBAY_TOKEN: dict = {"val": None, "exp": 0.0}


async def _ebay_token(timeout: float = 8.0) -> Optional[str]:
    app_id = os.environ.get("EBAY_APP_ID")
    cert = os.environ.get("EBAY_CERT_ID")
    if not app_id or not cert:
        return None
    import time as _t
    if _EBAY_TOKEN["val"] and _t.time() < _EBAY_TOKEN["exp"] - 60:
        return _EBAY_TOKEN["val"]
    try:
        import base64
        import httpx
        basic = base64.b64encode(f"{app_id}:{cert}".encode()).decode()
        async with httpx.AsyncClient(timeout=timeout) as c:
            r = await c.post(
                "https://api.ebay.com/identity/v1/oauth2/token",
                headers={"Authorization": "Basic " + basic,
                         "Content-Type": "application/x-www-form-urlencoded"},
                data={"grant_type": "client_credentials",
                      "scope": "https://api.ebay.com/oauth/api_scope"})
            if r.status_code != 200:
                return None
            d = r.json() or {}
            tok = d.get("access_token")
            if not tok:
                return None
            _EBAY_TOKEN["val"] = tok
            _EBAY_TOKEN["exp"] = _t.time() + float(d.get("expires_in", 7200))
            return tok
    except Exception:
        return None


async def ebay_asking_band(query: str, *, timeout: float = 8.0) -> Optional[dict]:
    """ASKING-price band (p10-p90 + median) of live eBay listings matching the
    query, via the official Browse API free tier. These are asking prices of
    currently-listed comparable items — NEVER sold prices; the consumer must
    keep that wording. None unless EBAY_APP_ID + EBAY_CERT_ID are set."""
    if not query:
        return None
    tok = await _ebay_token(timeout=timeout)
    if not tok:
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers={
                "Authorization": "Bearer " + tok,
                "User-Agent": "TrustSquare/1.0"}) as c:
            r = await c.get(
                "https://api.ebay.com/buy/browse/v1/item_summary/search",
                params={"q": query, "limit": 50})
            if r.status_code != 200:
                return None
            items = (r.json() or {}).get("itemSummaries") or []
        vals = []
        for it in items:
            try:
                p = it.get("price") or {}
                if (p.get("currency") or "USD") == "USD":
                    v = float(p.get("value"))
                    if v > 0:
                        vals.append(v)
            except Exception:
                continue
        if len(vals) < 5:
            return None
        vals.sort()
        med = statistics.median(vals)
        lo = vals[max(0, int(len(vals) * 0.1))]
        hi = vals[min(len(vals) - 1, int(len(vals) * 0.9))]
        return {"value": med, "n": len(vals), "low": lo, "high": hi,
                "currency": "USD", "source": "ebay_browse",
                "provenance": (f"eBay live-listing ASKING-price band "
                               f"(official Browse API, n={len(vals)})"),
                "date": "live",
                "specificity": ("asking prices of comparable items currently "
                                "listed (NOT sold prices)")}
    except Exception:
        return None
