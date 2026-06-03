"""Tests for the Tiered Value Selector STEP 3/5 modules:
   feature_flags, value_benchmarks, tier_resolvers.  Run: python3 test_tier_resolvers.py"""
import asyncio, json, os, tempfile
import feature_flags as ff
import value_benchmarks as vb
import tier_resolvers as tr


def test_flags_safe_defaults():
    os.environ.pop("FEATURE_FLAGS_PATH", None); ff.reload()
    assert ff.paid_tiers_enabled() is False
    p = ff.providers()
    for free in ("scryfall","land_registry","internal_comps","payprop_tpn","hud_fmr"):
        assert p.get(free) is True, free
    for paid in ("loom","lightstone","rentcast","pricecharting","caphpi"):
        assert p.get(paid) is False, paid


def test_flags_malformed_ignored():
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        fh.write("{ not valid json ,,,"); bad = fh.name
    try:
        os.environ["FEATURE_FLAGS_PATH"] = bad; ff.reload()
        assert ff.paid_tiers_enabled() is False
        assert ff.providers().get("loom") is False
        assert ff.providers().get("scryfall") is True
    finally:
        os.environ.pop("FEATURE_FLAGS_PATH", None); os.unlink(bad); ff.reload()


def test_flags_overlay():
    cfg = {"paid_tiers_enabled": True, "providers": {"loom": True, "bogus": True}}
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as fh:
        json.dump(cfg, fh); path = fh.name
    try:
        os.environ["FEATURE_FLAGS_PATH"] = path; ff.reload()
        assert ff.paid_tiers_enabled() is True
        assert ff.is_provider_live("loom") is True
        assert "bogus" not in ff.providers()
    finally:
        os.environ.pop("FEATURE_FLAGS_PATH", None); os.unlink(path); ff.reload()


def test_net_cost_bands():
    za = vb.net_cost_band("ZA")
    assert 2.0 <= za["typical"] <= 3.5 and za["components"]
    assert vb.net_cost_band("US")["typical"] >= vb.net_cost_band("ZA")["typical"]


def test_benchmark_lookups():
    pta = vb.za_city("Pretoria")
    assert pta["rent_pm"] > 0 and pta["ppsqm"] > 0 and "PayProp" in pta["source"]
    assert vb.za_city("Nowhere")["rent_pm"] > 0
    assert vb.us_area("New York")["rent_pm"] > 0 and "HUD" in vb.us_area("x")["source"]
    assert vb.uk_region("London")["rent_pm"] > 0 and "ONS" in vb.uk_region("x")["source"]


def test_internal_comps_gate():
    assert tr.internal_comps_estimate([100,200,300], min_n=8) is None
    out = tr.internal_comps_estimate([100,200,300,400,500,600,700,800,900], min_n=8)
    assert out and out["n"] == 9 and out["value"] == 500 and out["source"] == "internal_comps"
    assert tr.internal_comps_estimate([0,None,-5], min_n=1) is None


def test_served_tiers_launch():
    nc = {}
    assert tr.served_tiers("fair_price","cards","ZA",creds=nc) == {"1T": True}
    assert tr.served_tiers("fair_price","tcg","ZA",creds=nc).get("1T") is True
    assert not tr.served_tiers("fair_price","lego","ZA",creds=nc).get("1T")
    assert not tr.served_tiers("fair_price","coins","ZA",creds=nc).get("1T")
    assert tr.served_tiers("fair_price","lego","ZA",creds={"bricklink":True})["1T"] is True
    assert tr.served_tiers("fair_price","property","ZA")["0T"] is True
    assert not tr.served_tiers("fair_price","property","UK").get("0T")
    assert tr.served_tiers("fair_price","property","UK")["1T"] is True
    assert tr.served_tiers("fair_price","property","US")["1T"] is True
    assert tr.served_tiers("fair_price","vehicles","ZA")["1T"] is True
    assert tr.served_tiers("yield","property","UK")["1T"] is True
    assert tr.served_tiers("yield","property","US")["1T"] is True
    assert tr.served_tiers("yield","property","ZA")["0T"] is True
    assert tr.served_tiers("yield","property","AU") == {}


def test_area_guides():
    g = tr.za_area_price_guide("Pretoria", floor_area=100)
    assert g and g["implied_value"] > 0 and "m2" in g["range_text"]
    r = tr.za_area_rent("Pretoria")
    assert r and r["value"] > 0 and "PayProp" in r["provenance"]
    assert tr.us_market_rent("New York")["currency"] == "USD"
    assert tr.uk_market_rent("London")["currency"] == "GBP"
    assert tr.net_cost_band("ZA")["typical"] > 0


def test_feeds_dark_without_creds():
    for v in ("BRICKLINK_TOKEN","BRICKLINK_OAUTH_TOKEN","NUMISTA_API_KEY","JUSTTCG_API_KEY"):
        os.environ.pop(v, None)
    assert tr.creds_from_env() == {"bricklink": False, "numista": False, "justtcg": False}
    loop = asyncio.new_event_loop()
    assert loop.run_until_complete(tr.bricklink_price("10295")) is None
    assert loop.run_until_complete(tr.numista_price("krugerrand")) is None
    assert loop.run_until_complete(tr.justtcg_price("Charizard")) is None
    loop.close()


if __name__ == "__main__":
    fns = [v for k,v in sorted(globals().items()) if k.startswith("test_")]
    p = 0
    for fn in fns:
        fn(); p += 1; print(f"  PASS  {fn.__name__}")
    print(f"\n  {p}/{len(fns)} tests passed.")
