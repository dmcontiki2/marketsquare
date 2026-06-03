"""
value_benchmarks.py — versioned, dated public-data benchmarks (FREE/owned only)
===============================================================================
STEP 3 data layer for the Tiered Value Selector.

Holds the *aggregate, area-level* benchmark figures the FREE (0T) and some
FREE-feed (1T) resolvers read. Every figure here is from a free / open / public
licence source, is dated, and carries its provenance so the buyer always sees
where the number came from. NOTHING here is per-property and nothing is from a
paid/consumption API (B7-safe).

  * ZA  — PayProp Rental Index + TPN aggregate benchmarks (free published reports)
  * US  — HUD Fair Market Rents (public domain)
  * UK  — ONS / VOA private-rental statistics (Open Government Licence)
  * NET-COST BANDS — replaces the old flat ``NET_COST_PCT = 3.0`` magic number
    with a transparent, dated, per-region band (rates, levies, management,
    vacancy/maintenance).

Editing without a deploy
------------------------
Embedded ``_DEFAULTS`` is the always-works baseline. If ``value_benchmarks.json``
sits next to this module it is overlaid (mtime-cached), so David can refresh a
benchmark on the server without a code redeploy. A malformed file is ignored.

These are INDICATIVE area benchmarks, not valuations. Re-confirm against the
source's latest release before relying on them; bump ``updated`` when you do.
"""

from __future__ import annotations

import json
import os
import threading
import time

VERSION = "2026-06-03"  # benchmark snapshot date — bump when figures refreshed

# ── Embedded baseline (always works even with no JSON) ─────────────────────────
# All monetary figures are *typical area* levels with a low–high band, not a
# property-specific number. Sources + dates are surfaced to the buyer verbatim.
_DEFAULTS: dict = {
    "version": VERSION,

    # Per-region net operating-cost band, subtracted from gross to estimate net
    # yield. Transparent + dated; shown to the buyer as an assumption, never
    # hidden. Bands follow the yield data-sourcing spec (§8 / H7b).
    "net_cost_bands": {
        "ZA": {"low": 2.0, "typical": 3.0, "high": 3.5,
               "components": "rates & taxes, levies, management (~10%), vacancy & maintenance",
               "source": "PayProp/TPN published management & vacancy norms (aggregate)",
               "updated": "2026 Q1"},
        "UK": {"low": 2.0, "typical": 3.5, "high": 5.0,
               "components": "council tax voids, service charge/ground rent, management (~10%), maintenance",
               "source": "ONS/VOA + letting-agency norms (aggregate)",
               "updated": "2026 Q1"},
        "US": {"low": 3.0, "typical": 4.5, "high": 6.0,
               "components": "property tax, insurance, management (~8-10%), vacancy & maintenance",
               "source": "HUD/Census + management norms (aggregate)",
               "updated": "2026 Q1"},
        "AU": {"low": 2.5, "typical": 4.0, "high": 5.5,
               "components": "council & water rates, strata, management (~7%), vacancy & maintenance",
               "source": "REIA/agency norms (aggregate)",
               "updated": "2026 Q1"},
        "DEFAULT": {"low": 2.0, "typical": 3.0, "high": 4.0,
                    "components": "rates/taxes, management, vacancy & maintenance",
                    "source": "aggregate market norms",
                    "updated": "2026 Q1"},
    },

    # ZA aggregate benchmarks — PayProp Rental Index + TPN (free published).
    # rent_pm = typical residential monthly rent (ZAR); ppsqm = typical
    # residential asking price per m² (ZAR). Bands are area-level, indicative.
    "za": {
        "source": "PayProp Rental Index + TPN Residential Rental Monitor (aggregate, published)",
        "licence": "free published aggregate benchmark",
        "updated": "2026 Q1",
        "cities": {
            "pretoria":      {"rent_pm": 8600,  "rent_lo": 6500,  "rent_hi": 13500, "ppsqm": 12000, "ppsqm_lo": 9000,  "ppsqm_hi": 16000},
            "tshwane":       {"rent_pm": 8600,  "rent_lo": 6500,  "rent_hi": 13500, "ppsqm": 12000, "ppsqm_lo": 9000,  "ppsqm_hi": 16000},
            "johannesburg":  {"rent_pm": 9100,  "rent_lo": 6800,  "rent_hi": 15000, "ppsqm": 13000, "ppsqm_lo": 9500,  "ppsqm_hi": 18000},
            "cape town":     {"rent_pm": 11200, "rent_lo": 8000,  "rent_hi": 20000, "ppsqm": 22000, "ppsqm_lo": 14000, "ppsqm_hi": 38000},
            "durban":        {"rent_pm": 8300,  "rent_lo": 6000,  "rent_hi": 13000, "ppsqm": 11500, "ppsqm_lo": 8500,  "ppsqm_hi": 15500},
            "gqeberha":      {"rent_pm": 7400,  "rent_lo": 5500,  "rent_hi": 11000, "ppsqm": 10500, "ppsqm_lo": 8000,  "ppsqm_hi": 14000},
            "port elizabeth":{"rent_pm": 7400,  "rent_lo": 5500,  "rent_hi": 11000, "ppsqm": 10500, "ppsqm_lo": 8000,  "ppsqm_hi": 14000},
            "bloemfontein":  {"rent_pm": 7000,  "rent_lo": 5200,  "rent_hi": 10500, "ppsqm": 9500,  "ppsqm_lo": 7000,  "ppsqm_hi": 12500},
        },
        "default": {"rent_pm": 8500, "rent_lo": 6000, "rent_hi": 14000, "ppsqm": 12000, "ppsqm_lo": 8500, "ppsqm_hi": 17000},
    },

    # US HUD Fair Market Rents — 2-bedroom monthly (USD), public domain.
    "us": {
        "source": "HUD Fair Market Rents (2-bedroom)",
        "licence": "public domain (US federal)",
        "updated": "FY2026",
        "areas": {
            "new york":     {"rent_pm": 2730},
            "los angeles":  {"rent_pm": 2480},
            "chicago":      {"rent_pm": 1680},
            "houston":      {"rent_pm": 1490},
            "phoenix":      {"rent_pm": 1750},
            "miami":        {"rent_pm": 2360},
            "atlanta":      {"rent_pm": 1740},
            "dallas":       {"rent_pm": 1620},
            "seattle":      {"rent_pm": 2240},
            "denver":       {"rent_pm": 1980},
        },
        "default": {"rent_pm": 1700},
    },

    # UK ONS / VOA private-rental statistics — median monthly (GBP), OGL.
    "uk": {
        "source": "ONS / VOA private rental statistics (median)",
        "licence": "Open Government Licence v3.0",
        "updated": "2026 Q1",
        "regions": {
            "london":          {"rent_pm": 2120},
            "south east":      {"rent_pm": 1320},
            "south west":      {"rent_pm": 1150},
            "east of england": {"rent_pm": 1180},
            "west midlands":   {"rent_pm": 950},
            "east midlands":   {"rent_pm": 880},
            "north west":      {"rent_pm": 850},
            "north east":      {"rent_pm": 720},
            "yorkshire":       {"rent_pm": 830},
            "scotland":        {"rent_pm": 980},
            "wales":           {"rent_pm": 820},
        },
        "default": {"rent_pm": 1100},
    },
}

# ── Optional live overlay (edit-without-deploy) ────────────────────────────────
_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "value_benchmarks.json")
_LOCK = threading.Lock()
_CACHE: dict = {"data": None, "mtime": None, "checked": 0.0}
_RECHECK_S = 5.0


def _deep_overlay(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in (over or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_overlay(out[k], v)
        else:
            out[k] = v
    return out


def data() -> dict:
    """Embedded defaults overlaid with value_benchmarks.json if present."""
    now = time.time()
    path = os.environ.get("VALUE_BENCHMARKS_PATH") or _PATH
    with _LOCK:
        if _CACHE["data"] is not None and (now - _CACHE["checked"]) < _RECHECK_S:
            return _CACHE["data"]
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None
        if _CACHE["data"] is None or _CACHE["mtime"] != mtime:
            merged = _DEFAULTS
            if mtime is not None:
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        merged = _deep_overlay(_DEFAULTS, json.load(fh))
                except Exception:
                    merged = _DEFAULTS
            _CACHE.update(data=merged, mtime=mtime, checked=now)
        else:
            _CACHE["checked"] = now
        return _CACHE["data"]


# ── Lookups (pure) ─────────────────────────────────────────────────────────────
def _norm(s) -> str:
    return str(s or "").strip().lower()


def net_cost_band(country_iso2: str) -> dict:
    bands = data()["net_cost_bands"]
    return bands.get((country_iso2 or "").upper(), bands["DEFAULT"])


def za_city(city: str) -> dict:
    za = data()["za"]
    rec = za["cities"].get(_norm(city), za["default"])
    return {**rec, "source": za["source"], "licence": za["licence"], "updated": za["updated"]}


def us_area(area: str) -> dict:
    us = data()["us"]
    rec = us["areas"].get(_norm(area), us["default"])
    return {**rec, "source": us["source"], "licence": us["licence"], "updated": us["updated"]}


def uk_region(region: str) -> dict:
    uk = data()["uk"]
    rec = uk["regions"].get(_norm(region), uk["default"])
    return {**rec, "source": uk["source"], "licence": uk["licence"], "updated": uk["updated"]}
