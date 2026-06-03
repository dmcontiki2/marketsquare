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
        # comics / watches: no free specific feed yet -> nothing ready (FILE)
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
    """Coin catalogue price via Numista. None unless NUMISTA_API_KEY is set."""
    key = os.environ.get("NUMISTA_API_KEY")
    if not key or not query:
        return None
    try:
        import httpx
        async with httpx.AsyncClient(timeout=timeout, headers={
            "Numista-API-Key": key, "User-Agent": "TrustSquare/1.0"}) as c:
            r = await c.get("https://api.numista.com/api/v3/coins",
                            params={"q": query, "count": 1})
            if r.status_code != 200:
                return None
            items = (r.json() or {}).get("coins") or []
            if not items:
                return None
            return {"value": None, "ref": items[0].get("id"),
                    "source": "numista", "provenance": "Numista catalogue match",
                    "date": "live", "specificity": "catalogue reference"}
    except Exception:
        return None


async def justtcg_price(query: str, *, timeout: float = 8.0) -> Optional[dict]:
    """TCG price via JustTCG free tier. None unless JUSTTCG_API_KEY is set."""
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
            price = (items[0].get("price") if items else None)
            if not price:
                return None
            return {"value": float(price), "currency": "USD", "source": "justtcg",
                    "provenance": "JustTCG free-tier market price", "date": "live",
                    "specificity": "card-specific"}
    except Exception:
        return None
