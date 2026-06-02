"""
ai_service_tiers.py  —  Tiered Value Selector: config + availability resolver
=============================================================================
Single source of truth for WHICH price/value tiers (0T / 1T / 2T) are offered
for the "Is this a fair price?" and "Investor Yield" AI services, per
(service x category x country).

Design (see AdvertAgent/PROJECT_TieredValueSelector_UX.html):
  * Tiers differ by PRECISION/provenance, never by truthfulness.
        0T (free)     -> honest, non-specific area/market guide
        1T (verified) -> item/property-specific, from FREE or OWNED data
        2T (premium)  -> item/property-specific, from a CONTRACTED/PAID feed
  * "Hide where we can't deliver": if no tier survives gating, the service
    button is not shown at all (available_tiers() returns []).
  * Free-only at launch: PAID tiers are gated behind `paid_enabled` AND a live
    provider AND a cost ceiling.
  * LOOM is NOT required. It is merely one of the interchangeable premium
    providers for ZA property; with it off, the free tier still serves ZA and
    the gold tier simply does not render until LOOM *or* Lightstone is live.

This module is PURE (no I/O, no deps) so it is trivially unit-testable and can
be imported by bea_main.py without changing any request path until wired in.
"""

from __future__ import annotations
from typing import Iterable

# ── Tier identifiers ─────────────────────────────────────────────────────────
FREE     = "0T"   # green  · honest area/general guide
VERIFIED = "1T"   # blue   · specific, from free/owned data
PREMIUM  = "2T"   # gold   · specific, from a contracted/paid feed

_TIER_RANK = {FREE: 0, VERIFIED: 1, PREMIUM: 2}
TIER_COLOR = {FREE: "green", VERIFIED: "blue", PREMIUM: "gold"}
TIER_TUPPENCE = {FREE: 0, VERIFIED: 1, PREMIUM: 2}


# ── Provider registry ────────────────────────────────────────────────────────
# `True`  = data source is live and licensed for our commercial use *now*.
# `False` = not yet available (no contract / not built / B7 not approved).
#
# Flip a provider to True only after: contract signed (if any), B7 ceiling set,
# and a CHANGELOG "Cost model impact:" line written.
#
# >>> Note LOOM is False. The whole point: nothing below breaks because of it. <<<
DEFAULT_PROVIDERS: dict[str, bool] = {
    # --- free / open / owned (live at launch) ---
    "scryfall":        True,   # MTG cards (already live in bea_main.py)
    "bricklink":       True,   # LEGO, free OAuth feed
    "numista":         True,   # coins, free community feed
    "justtcg_free":    True,   # TCG free tier
    "land_registry":   True,   # UK sold prices, OGL (free, commercial OK)
    "ons_voa":         True,   # UK rents, OGL
    "hud_fmr":         True,   # US rents, public domain
    "us_assessor":     True,   # US county assessor / FHFA, public
    "payprop_tpn":     True,   # ZA aggregate rent/price benchmarks (free reports)
    "internal_comps":  True,   # our own marketplace comps (still needs sample!)

    # --- paid / contract (OFF until revenue + B7 + contract) ---
    "pricecharting":   False,  # collectibles multi-category (flat sub)
    "pcgs":            False,  # graded US coins
    "gocollect":       False,  # comics
    "watchcharts":     False,  # watches
    "propertydata":    False,  # UK property depth
    "rentcast":        False,  # US rent + AVM
    "attom":           False,  # US AVM
    "loom":            False,  # <── ZA property AVM (no contract) — interchangeable with lightstone
    "lightstone":      False,  # ZA property AVM (paid API) — the LOOM alternative
    "domain":          False,  # AU property/rent
    "corelogic":       False,  # AU property
    "sqm":             False,  # AU rent
    "caphpi":          False,  # UK vehicle book value
    "redbook":         False,  # AU vehicle book value
    "transunion_auto": False,  # ZA vehicle book value
}


# ── Tier definitions ─────────────────────────────────────────────────────────
# Each row is a CANDIDATE tier. It is offered to the buyer only if it survives
# gating in available_tiers().
#
#   providers   : any-of — at least one must be live for the tier to show
#   licence_ok  : False = data licence forbids our commercial use (e.g. AU gov
#                 CC BY-NC-ND) -> tier is dropped until a commercial licence
#   paid        : True  = a PREMIUM tier, gated by `paid_enabled` + ceiling
#   min_comps   : internal-comps tiers need at least this many comparable
#                 listings before they are trustworthy (cold-start guard)
def _t(tier, name, desc, providers, *, licence_ok=True, paid=False, min_comps=0):
    return {
        "tier": tier, "color": TIER_COLOR[tier], "tuppence": TIER_TUPPENCE[tier],
        "name": name, "desc": desc, "providers": tuple(providers),
        "licence_ok": licence_ok, "paid": paid, "min_comps": min_comps,
    }


# service -> category -> country("*" = any) -> [candidate tiers]
TIER_MATRIX: dict = {
    "fair_price": {
        # ---- collectibles ----
        "cards": {"*": [
            _t(VERIFIED, "Verified price", "Live market price for this exact card.",
               ["scryfall"]),
        ]},
        "lego": {"*": [
            _t(VERIFIED, "Verified price", "Live set/part price from BrickLink.",
               ["bricklink"]),
            _t(PREMIUM, "Premium price", "Deeper graded/sealed pricing.",
               ["pricecharting"], paid=True),
        ]},
        "coins": {"*": [
            _t(VERIFIED, "Verified price", "Catalogue price from Numista.",
               ["numista"]),
            _t(PREMIUM, "Graded value", "Graded US coin value (PCGS).",
               ["pcgs", "pricecharting"], paid=True),
        ]},
        "tcg": {"*": [
            _t(VERIFIED, "Verified price", "Condition-specific TCG price.",
               ["justtcg_free", "scryfall"]),
            _t(PREMIUM, "Premium price", "Deeper multi-condition pricing.",
               ["pricecharting"], paid=True),
        ]},
        "comics": {"*": [
            _t(FREE, "Title guide", "General read for this title. Indicative, not grade-specific.",
               ["internal_comps", "payprop_tpn"]),  # falls back to honest 'cannot assess' if neither
            _t(PREMIUM, "Graded value", "Grade-specific value (GoCollect).",
               ["gocollect"], paid=True),
        ]},
        "watches": {"*": [
            _t(FREE, "Model guide", "General market read for this model. Indicative.",
               ["internal_comps"]),
            _t(PREMIUM, "Market value", "Model/ref-specific value (WatchCharts).",
               ["watchcharts"], paid=True),
        ]},
        # ---- property (sale price) ----
        "property": {
            "UK": [
                _t(VERIFIED, "Verified comps", "Exact sold comparables (HM Land Registry).",
                   ["land_registry"]),
                _t(PREMIUM, "Premium estimate", "Property-specific depth (PropertyData).",
                   ["propertydata"], paid=True),
            ],
            "US": [
                _t(FREE, "Area guide", "Neighbourhood benchmark from public records. Indicative.",
                   ["us_assessor"]),
                _t(VERIFIED, "Verified comps", "Comparable listings on TrustSquare.",
                   ["internal_comps"], min_comps=8),
                _t(PREMIUM, "Premium estimate", "Property-specific AVM (RentCast/ATTOM).",
                   ["rentcast", "attom"], paid=True),
            ],
            "ZA": [
                _t(FREE, "Area guide", "Suburb benchmark (PayProp/TPN). Indicative, not property-specific.",
                   ["payprop_tpn"]),
                _t(VERIFIED, "Verified comps", "Comparable listings on TrustSquare.",
                   ["internal_comps"], min_comps=8),
                _t(PREMIUM, "Premium estimate", "Property-specific AVM (LOOM/Lightstone).",
                   ["loom", "lightstone"], paid=True),
            ],
            "AU": [
                # Free gov sales data is CC BY-NC-ND -> NOT licensed for our commercial use.
                _t(FREE, "Area guide", "Suburb benchmark.", ["us_assessor"], licence_ok=False),
                _t(VERIFIED, "Verified comps", "Comparable listings on TrustSquare.",
                   ["internal_comps"], min_comps=8),
                _t(PREMIUM, "Premium estimate", "Property-specific AVM (Domain/CoreLogic).",
                   ["domain", "corelogic"], paid=True),
            ],
        },
        # ---- vehicles (all markets: no free price feed anywhere) ----
        "vehicles": {"*": [
            _t(VERIFIED, "Verified comps", "Comparable make/model/year listings on TrustSquare.",
               ["internal_comps"], min_comps=8),
            _t(PREMIUM, "Book value", "Trade/retail book value (CAP HPI/RedBook/TransUnion).",
               ["caphpi", "redbook", "transunion_auto"], paid=True),
        ]},
    },

    "yield": {
        "property": {
            "UK": [
                _t(VERIFIED, "Verified yield", "ONS/VOA rent + Land Registry price.",
                   ["ons_voa", "land_registry"]),
                _t(PREMIUM, "Premium yield", "Property-specific rent + AVM (PropertyData).",
                   ["propertydata"], paid=True),
            ],
            "US": [
                _t(VERIFIED, "Verified yield", "HUD market rent + assessor price.",
                   ["hud_fmr", "us_assessor"]),
                _t(PREMIUM, "Premium yield", "Property-specific rent + AVM (RentCast).",
                   ["rentcast"], paid=True),
            ],
            "ZA": [
                _t(FREE, "Area yield", "Suburb rent/price benchmark (PayProp/TPN) or your figures.",
                   ["payprop_tpn"]),
                _t(VERIFIED, "Verified yield", "Comparable listings on TrustSquare.",
                   ["internal_comps"], min_comps=8),
                _t(PREMIUM, "Premium yield", "Property-specific (LOOM/Lightstone).",
                   ["loom", "lightstone"], paid=True),
            ],
            "AU": [
                _t(FREE, "Area yield", "Suburb benchmark.", ["sqm"], licence_ok=False),
                _t(PREMIUM, "Premium yield", "Property-specific (Domain/SQM/CoreLogic).",
                   ["domain", "sqm", "corelogic"], paid=True),
            ],
        },
    },
}

# A yield can ALWAYS be computed from the buyer's own figures — this baseline is
# offered in addition to whatever the matrix returns (it never makes the service
# "available" on its own UI button, but it is always a valid path once opened).
USER_SUPPLIED_TIER = _t(
    FREE, "Your figures",
    "Enter the missing number (rent or price) and we compute the real yield.",
    ["internal_comps"],  # provider irrelevant; always allowed
)
USER_SUPPLIED_TIER = {**USER_SUPPLIED_TIER, "providers": (), "user_supplied": True}


# ── Core resolver ────────────────────────────────────────────────────────────
def _norm_country(country: str | None) -> str:
    if not country:
        return "*"
    return str(country).strip().upper()[:2] or "*"


def _lookup_rows(service: str, category: str, country: str) -> list[dict]:
    svc = TIER_MATRIX.get(service, {})
    cat = svc.get((category or "").strip().lower(), {})
    if not cat:
        return []
    # country-specific first, else the wildcard bucket
    return cat.get(country) or cat.get("*") or []


def available_tiers(
    service: str,
    category: str,
    country: str | None = None,
    *,
    providers: dict[str, bool] | None = None,
    paid_enabled: bool = False,
    comp_count: int = 0,
    ceiling_ok: bool = True,
) -> list[dict]:
    """Return the list of tier chips to render for this (service, category,
    country), already gated and sorted 0T -> 1T -> 2T.

    An empty list means: HIDE the service entry point — we have nothing true to
    offer here.

    Gating, in order, per candidate tier:
      1. licence_ok       — drop data we may not use commercially here
      2. paid flag        — premium tiers require paid_enabled (+ ceiling_ok)
      3. provider live    — at least one of the tier's providers is True
      4. min_comps        — internal-comps tiers need enough sample
    """
    prov = providers or DEFAULT_PROVIDERS
    country = _norm_country(country)
    out: list[dict] = []
    for row in _lookup_rows(service, category, country):
        if not row["licence_ok"]:
            continue
        if row["paid"] and (not paid_enabled or not ceiling_ok):
            continue
        if row["providers"] and not any(prov.get(p, False) for p in row["providers"]):
            continue
        if row["min_comps"] and comp_count < row["min_comps"]:
            continue
        out.append(row)
    out.sort(key=lambda r: _TIER_RANK[r["tier"]])
    return out


def service_available(service: str, category: str, country: str | None = None, **kw) -> bool:
    """Convenience: should the service button show at all?"""
    return len(available_tiers(service, category, country, **kw)) > 0


def chips_payload(service: str, category: str, country: str | None = None, **kw) -> list[dict]:
    """UI-ready chip list (what the BEA sends to the FEA). Trimmed to display
    fields + the machine-readable tier so the FEA stays rules-free."""
    return [
        {
            "tier": r["tier"],
            "tuppence": r["tuppence"],
            "color": r["color"],
            "name": r["name"],
            "desc": r["desc"],
        }
        for r in available_tiers(service, category, country, **kw)
    ]
