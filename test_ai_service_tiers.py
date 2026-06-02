"""
Tests + launch-matrix proof for ai_service_tiers.

Run:  python3 test_ai_service_tiers.py
Proves the Tiered Value Selector works WITHOUT a LOOM contract, and that the
ZA premium tier appears the moment ANY premium provider (LOOM *or* Lightstone)
goes live.
"""
import copy
from ai_service_tiers import (
    available_tiers, chips_payload, service_available, DEFAULT_PROVIDERS,
    FREE, VERIFIED, PREMIUM,
)


def tiers(*a, **k):
    return [t["tier"] for t in available_tiers(*a, **k)]


# ── 1. LAUNCH: paid off, LOOM off, no internal-comp depth yet ────────────────
def test_launch_without_loom():
    p = dict(DEFAULT_PROVIDERS)            # loom=False, all paid providers False
    assert p["loom"] is False              # the premise of David's question

    # ZA property still serves the FREE area guide — service is NOT dark.
    assert tiers("fair_price", "property", "ZA", providers=p,
                 paid_enabled=False, comp_count=0) == [FREE]
    assert service_available("fair_price", "property", "ZA", providers=p) is True

    # Cards work at 1T (Scryfall is free & already live).
    assert tiers("fair_price", "cards", "ZA", providers=p) == [VERIFIED]

    # UK property is 1T at launch (Land Registry free & commercial).
    assert tiers("fair_price", "property", "UK", providers=p) == [VERIFIED]

    # US property shows the free area guide at launch (assessor public).
    assert tiers("fair_price", "property", "US", providers=p, comp_count=0) == [FREE]

    # AU property is HIDDEN — gov data is non-commercial, paid feeds off.
    assert tiers("fair_price", "property", "AU", providers=p) == []
    assert service_available("fair_price", "property", "AU", providers=p) is False

    # Vehicles HIDDEN at launch — no free price feed, comps not deep enough.
    assert tiers("fair_price", "vehicles", "ZA", providers=p, comp_count=0) == []

    # Yield: UK & US run at 1T on free public rent data; ZA on the free guide.
    assert tiers("yield", "property", "UK", providers=p) == [VERIFIED]
    assert tiers("yield", "property", "US", providers=p) == [VERIFIED]
    assert tiers("yield", "property", "ZA", providers=p) == [FREE]
    assert tiers("yield", "property", "AU", providers=p) == []


# ── 2. ZA premium tier needs only a provider — LOOM OR Lightstone ────────────
def test_za_premium_lights_up_with_either_provider():
    # Lightstone signed, LOOM still absent, paid switched on:
    p = dict(DEFAULT_PROVIDERS); p["lightstone"] = True
    assert tiers("fair_price", "property", "ZA", providers=p,
                 paid_enabled=True) == [FREE, PREMIUM]

    # LOOM signed instead, Lightstone absent — identical result:
    p = dict(DEFAULT_PROVIDERS); p["loom"] = True
    assert tiers("fair_price", "property", "ZA", providers=p,
                 paid_enabled=True) == [FREE, PREMIUM]

    # paid_enabled off => premium hidden even with a provider live (launch rule).
    assert tiers("fair_price", "property", "ZA", providers=p,
                 paid_enabled=False) == [FREE]


# ── 3. Internal comps unlock the 1T tier once sample is deep enough ───────────
def test_internal_comps_gate():
    p = dict(DEFAULT_PROVIDERS)
    assert tiers("fair_price", "property", "US", providers=p, comp_count=3) == [FREE]
    assert tiers("fair_price", "property", "US", providers=p,
                 comp_count=12) == [FREE, VERIFIED]
    # Vehicles become available at 1T once comps are deep — no contract needed.
    assert tiers("fair_price", "vehicles", "UK", providers=p,
                 comp_count=12) == [VERIFIED]


# ── 4. Full revenue state: everything contracted + comps deep ────────────────
def test_full_state():
    p = {k: True for k in DEFAULT_PROVIDERS}
    assert tiers("fair_price", "property", "ZA", providers=p,
                 paid_enabled=True, comp_count=20) == [FREE, VERIFIED, PREMIUM]
    assert tiers("fair_price", "property", "AU", providers=p,
                 paid_enabled=True, comp_count=20) == [VERIFIED, PREMIUM]  # FREE still NC-blocked


# ── 5. chips_payload is FEA-ready ────────────────────────────────────────────
def test_chips_payload_shape():
    chips = chips_payload("fair_price", "property", "ZA", providers=DEFAULT_PROVIDERS)
    assert chips == [{
        "tier": "0T", "tuppence": 0, "color": "green",
        "name": "Area guide",
        "desc": "Suburb benchmark (PayProp/TPN). Indicative, not property-specific.",
    }]


# ── pretty launch-matrix printout (the visual proof) ─────────────────────────
def _print_launch_matrix():
    p = dict(DEFAULT_PROVIDERS)  # LAUNCH: paid off, LOOM off, comps shallow
    combos = [
        ("fair_price", "cards", "ZA"), ("fair_price", "lego", "ZA"),
        ("fair_price", "coins", "ZA"), ("fair_price", "comics", "ZA"),
        ("fair_price", "property", "UK"), ("fair_price", "property", "US"),
        ("fair_price", "property", "ZA"), ("fair_price", "property", "AU"),
        ("fair_price", "vehicles", "ZA"),
        ("yield", "property", "UK"), ("yield", "property", "US"),
        ("yield", "property", "ZA"), ("yield", "property", "AU"),
    ]
    print("\n  LAUNCH MATRIX  (paid_enabled=False, loom=False, comp_count=0)")
    print("  " + "-" * 58)
    for svc, cat, ctry in combos:
        ch = chips_payload(svc, cat, ctry, providers=p, paid_enabled=False, comp_count=0)
        shown = "  ".join(f"{c['tier']}·{c['name']}" for c in ch) or "— HIDDEN —"
        print(f"  {svc:11} {cat:9} {ctry:3} ->  {shown}")
    print("  " + "-" * 58)
    print("  Nothing here needs LOOM. ZA serves a free guide; AU & vehicles hide.\n")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn(); passed += 1
        print(f"  PASS  {fn.__name__}")
    print(f"\n  {passed}/{len(fns)} tests passed.")
    _print_launch_matrix()
