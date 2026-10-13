"""
feature_flags.py — server-readable feature/provider flag store
===============================================================
STEP 5 of the Tiered Value Selector build.

Replaces the hardcoded ``PAID_TIERS_ENABLED`` constant and the per-provider
booleans (previously baked into ``ai_service_tiers.DEFAULT_PROVIDERS``) with a
small store the BEA *reads at request time*, so enabling a paid provider later
is a **config change, not a code edit** — David edits ``feature_flags.json`` on
the server (or via a future admin endpoint) and the change is picked up without
a redeploy.

Design / safety
---------------
* Source of truth: ``feature_flags.json`` next to this module
  (override path with env ``FEATURE_FLAGS_PATH``).
* **Fail-safe defaults**: if the file is missing, unreadable, or malformed we
  fall back to the safe baseline — ``paid_tiers_enabled = False`` and every
  PAID/contract provider OFF, every FREE/open/owned provider ON. A broken file
  can therefore never *enable* a paid provider; it can only be ignored.
* mtime-cached: the file is re-read only when it changes on disk, so this is
  cheap to call on every request and live-editable without a restart.
* Pure-ish: no third-party deps, no DB. Trivially unit-testable.

The two gates in ai_service_tiers.available_tiers() still apply on top of this:
a PREMIUM (2T) tier shows only if ``paid_tiers_enabled`` is True **and** at
least one of its providers is live here. This store just supplies those flags.
"""

from __future__ import annotations

import json
import os
import threading
import time

# ── Provider classification (mirrors ai_service_tiers.DEFAULT_PROVIDERS) ───────
# FREE = zero marginal cost, no contract, no consumption API → ON by default.
FREE_PROVIDERS: tuple[str, ...] = (
    "scryfall",        # MTG cards (live)
    "bricklink",       # LEGO — free OAuth feed
    "numista",         # coins — free community feed
    "justtcg_free",    # TCG — free tier
    "land_registry",   # UK sold prices — OGL, keyless SPARQL
    "ons_voa",         # UK rents — OGL
    "hud_fmr",         # US rents — public domain
    "us_assessor",     # US county assessor / FHFA — public
    "payprop_tpn",     # ZA aggregate rent/price benchmarks — free reports
    "internal_comps",  # our own marketplace comps
    "web_comps",       # FAIR-PRICE-WEB-1: asking prices read on named shop pages. EBAY-DROP-1 (30 Sep 2026): eBay removed
    # SQUIRE-2 Phase 1 (10 Oct 2026, SQUIRE_2_BUILD_BRIEF.md s2) -- all free, no per-request cost:
    "mtgjson",         # MTGJSON daily price file -> card_price_history (nightly, no per-request calls)
    "epc_register",    # UK EPC open data (free registration key, held server-side only)
    "police_uk",       # data.police.uk street-level crime counts (free, keyless)
    "ea_flood",        # Environment Agency flood areas (free, keyless)
    "boe_rate",        # Bank of England Bank Rate (published)
    "sarb_rate",       # SARB repo rate (published)
)

# PAID = billed per-request / contract / consumption API → OFF until David
# enables (B7: explicit approval + a hard cost ceiling).  These MUST stay False
# for this build (PAID_TIERS_ENABLED also stays False).
PAID_PROVIDERS: tuple[str, ...] = (
    "pricecharting", "pcgs", "gocollect", "watchcharts",
    "propertydata", "rentcast", "attom", "loom", "lightstone",
    "domain", "corelogic", "sqm", "caphpi", "redbook", "transunion_auto",
)

ALL_PROVIDERS: tuple[str, ...] = FREE_PROVIDERS + PAID_PROVIDERS

_DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "feature_flags.json")


# SQUIRE-2 (10 Oct 2026): product switches that are NOT providers. Every one defaults OFF and a
# broken/missing file can never turn one on. `squire_pro_pa` arms the Pro PA monthly-Tuppence quote
# and its recurring charge (SQUIRE_2_BUILD_BRIEF.md s4) -- arming is David's act, never a code default.
SWITCHES: tuple[str, ...] = ("squire_pro_pa",)

# SQUIRE-2 s4: what a premium feed costs us per month (USD), set by David when he approves a feed.
# A feed with no cost here can never be quoted -- the machinery refuses rather than guessing a price.
# The two Pro PA pricing knobs live beside it (USD per brief per month for the AI run, and the margin).
_PA_PRICING_DEFAULTS = {"ai_usd_month": 1.0, "margin_pct": 30.0}


def _safe_defaults() -> dict:
    """The fail-safe baseline: paid master switch off, free on, paid off, every switch off."""
    providers = {p: True for p in FREE_PROVIDERS}
    providers.update({p: False for p in PAID_PROVIDERS})
    return {"paid_tiers_enabled": False, "providers": providers,
            "switches": {k: False for k in SWITCHES},
            "feed_costs_usd_month": {}, "pa_pricing": dict(_PA_PRICING_DEFAULTS)}


# ── mtime-cached loader ────────────────────────────────────────────────────────
_LOCK = threading.Lock()
_CACHE: dict = {"state": None, "mtime": None, "path": None, "checked": 0.0}
_RECHECK_S = 5.0  # stat the file at most this often


def _path() -> str:
    return os.environ.get("FEATURE_FLAGS_PATH") or _DEFAULT_PATH


def _coerce(raw: dict) -> dict:
    """Overlay a (possibly partial / untrusted) file onto the safe defaults.

    Only known keys/providers are honoured; unknown providers are ignored;
    every value is coerced to bool. A missing 'providers' block leaves the
    safe per-provider defaults untouched.
    """
    state = _safe_defaults()
    if not isinstance(raw, dict):
        return state
    if "paid_tiers_enabled" in raw:
        state["paid_tiers_enabled"] = bool(raw.get("paid_tiers_enabled"))
    pv = raw.get("providers")
    if isinstance(pv, dict):
        for name, val in pv.items():
            if name in state["providers"]:
                state["providers"][name] = bool(val)
    sw = raw.get("switches")
    if isinstance(sw, dict):
        for name, val in sw.items():
            if name in state["switches"]:
                state["switches"][name] = (val is True)   # only a literal true arms a switch
    fc = raw.get("feed_costs_usd_month")
    if isinstance(fc, dict):
        for name, val in fc.items():
            try:
                v = float(val)
            except (TypeError, ValueError):
                continue
            if name in PAID_PROVIDERS and v > 0:
                state["feed_costs_usd_month"][name] = v
    pp = raw.get("pa_pricing")
    if isinstance(pp, dict):
        for name in _PA_PRICING_DEFAULTS:
            try:
                v = float(pp.get(name))
                if v >= 0:
                    state["pa_pricing"][name] = v
            except (TypeError, ValueError):
                pass
    return state


def _load() -> dict:
    """Return the current flag state, re-reading the file only when it changes."""
    now = time.time()
    path = _path()
    with _LOCK:
        # Cheap fast-path: same file checked very recently.
        if (_CACHE["state"] is not None and _CACHE["path"] == path
                and (now - _CACHE["checked"]) < _RECHECK_S):
            return _CACHE["state"]
        try:
            mtime = os.path.getmtime(path)
        except OSError:
            mtime = None
        # Reload only if file changed (or path changed, or first load).
        if (_CACHE["state"] is None or _CACHE["path"] != path
                or _CACHE["mtime"] != mtime):
            state = _safe_defaults()
            if mtime is not None:
                try:
                    with open(path, "r", encoding="utf-8") as fh:
                        state = _coerce(json.load(fh))
                except Exception:
                    # Malformed / unreadable → keep safe defaults (never enable paid).
                    state = _safe_defaults()
            _CACHE.update(state=state, mtime=mtime, path=path, checked=now)
        else:
            _CACHE["checked"] = now
        return _CACHE["state"]


# ── Public API (what bea_main.py calls) ────────────────────────────────────────
def paid_tiers_enabled() -> bool:
    """Master switch for every PREMIUM (2T) tier. False at launch."""
    return bool(_load().get("paid_tiers_enabled", False))


def providers() -> dict[str, bool]:
    """Full {provider: live?} map for ai_service_tiers.available_tiers()."""
    return dict(_load().get("providers", {}))


def is_provider_live(name: str) -> bool:
    return bool(_load().get("providers", {}).get(name, False))


def switch_on(name: str) -> bool:
    """A product switch (SWITCHES). Unknown names and any doubt read OFF."""
    return bool(_load().get("switches", {}).get(name, False))


def squire_pro_pa_on() -> bool:
    """SQUIRE-2 s4: the Pro PA monthly-Tuppence machinery. Default OFF; arming is David's act."""
    return switch_on("squire_pro_pa")


def feed_costs_usd_month() -> dict[str, float]:
    return dict(_load().get("feed_costs_usd_month", {}))


def pa_pricing() -> dict[str, float]:
    return dict(_load().get("pa_pricing", _PA_PRICING_DEFAULTS))


def state() -> dict:
    """Whole resolved state (for diagnostics / an admin view). Carries no secret: flags only."""
    s = _load()
    return {"paid_tiers_enabled": s["paid_tiers_enabled"],
            "providers": dict(s["providers"]),
            "switches": dict(s.get("switches", {})),
            "source": _path()}


def reload() -> dict:
    """Force a re-read on the next access (e.g. after editing the file)."""
    with _LOCK:
        _CACHE.update(state=None, mtime=None, checked=0.0)
    return state()
