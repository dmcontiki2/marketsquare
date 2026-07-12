"""
test_demand_loop.py — unit tests for the DEMAND-LOOP-1 realness filter.
Runs standalone (python3 test_demand_loop.py) or under pytest. No DB, no I/O.
"""
from __future__ import annotations

import demand_loop as dl

# A fixed config so tests don't depend on the live JSON (defaults == JSON here).
CFG = dl._merged({})            # canonical defaults, enabled False
CFG_ON = dl._merged({"enabled": True})


def ev(q, cat=None, **kw):
    kw.setdefault("result_count", 0)
    kw.setdefault("config", CFG)
    return dl.evaluate(q, cat, **kw)


def test_strong_car_query_qualifies():
    e = ev("bmw 2015 320d", "cars")
    assert e.is_miss and e.qualifies, e
    assert e.score >= e.threshold
    # make+year+model+3 tokens+hv should be well clear of the bar
    assert e.score >= 8, e.score


def test_vague_single_word_rejected():
    e = ev("phone")
    assert not e.qualifies, e
    assert e.score < e.threshold


def test_hit_never_qualifies():
    # same strong query, but supply already exists -> not a miss
    e = ev("bmw 2015 320d", "cars", result_count=5)
    assert not e.is_miss and not e.qualifies, e
    assert e.score == 0


def test_unknown_result_count_rejected():
    e = ev("bmw 2015 320d", "cars", result_count=None)
    assert not e.is_miss and not e.qualifies, e


def test_small_change_price_floor_suppresses():
    # a cheap 'other' item below the floor is small change, never triggers
    e = ev("phone charger", "other", price_max=50)
    assert not e.floor_ok and not e.qualifies, e


def test_price_above_floor_not_suppressed():
    e = ev("omega seamaster 2018", "watches", price_max=45000)
    assert e.floor_ok and e.qualifies, e


def test_repeat_pushes_borderline_over():
    base = ev("iphone 13 pro max", "electronics")            # 4 tokens = 4 < 5
    assert not base.qualifies, base
    boosted = ev("iphone 13 pro max", "electronics", repeat_count=1)  # +2
    assert boosted.qualifies, boosted


def test_session_depth_boost():
    base = ev("dining table oak", "furniture")               # 3 tokens = 3
    assert not base.qualifies, base
    boosted = ev("dining table oak", "furniture", session_depth=2)    # +2 = 5
    assert boosted.qualifies, boosted


def test_brand_two_word_query_qualifies():
    e = ev("rolex submariner", "watches")   # tokens_2(2)+brand(2)+hv(1)=5
    assert e.qualifies, e


def test_specific_property_qualifies():
    e = ev("3 bedroom house lynnwood", "property")  # 4 tokens(4)+hv(1)=5
    assert e.qualifies, e


def test_generic_property_word_rejected():
    e = ev("house", "property")   # 1 token(0)+hv(1)=1
    assert not e.qualifies, e


def test_single_branded_word_stays_cautious():
    e = ev("pokemon", "collectables")   # 1 token(0)+brand(2)+hv(1)=3 < 5
    assert not e.qualifies, e


def test_would_act_follows_enabled_flag():
    off = ev("bmw 2015 320d", "cars")
    assert off.qualifies and not off.would_act and not off.enabled, off
    on = ev("bmw 2015 320d", "cars", config=CFG_ON)
    assert on.qualifies and on.would_act and on.enabled, on


def test_failsafe_broken_config_disables():
    # a broken/empty file -> defaults, enabled must be False
    assert dl._merged({}).get("enabled") is False
    assert dl._merged({"enabled": "yes"}).get("enabled") is False
    assert dl._merged({"enabled": 1}).get("enabled") is False
    assert dl._merged({"enabled": True}).get("enabled") is True


def test_similarity_and_history():
    assert dl.query_similarity("bmw 320d", "bmw 320d touring") >= 0.5
    assert dl.query_similarity("bmw 320d", "toyota hilux") == 0.0
    rows = [
        {"buyer_token": "b1", "raw_text": "bmw 320d", "created_at": "2026-07-06 08:00:00"},
        {"buyer_token": "b1", "raw_text": "bmw 320d touring", "created_at": "2026-07-06 09:00:00"},
        {"buyer_token": "b1", "raw_text": "toaster", "created_at": "2026-07-06 09:30:00"},
        {"buyer_token": "b2", "raw_text": "bmw 320d", "created_at": "2026-07-06 09:40:00"},
    ]
    from datetime import datetime, timezone
    now = datetime(2026, 7, 6, 10, 0, 0, tzinfo=timezone.utc)
    rep, depth = dl.history_signals(rows, "b1", "bmw 320d", 72, now=now)
    assert rep == 2 and depth == 3, (rep, depth)


def _run():
    import sys
    fns = [(n, f) for n, f in sorted(globals().items())
           if n.startswith("test_") and callable(f)]
    passed = 0
    for n, f in fns:
        try:
            f(); passed += 1; print(f"PASS  {n}")
        except AssertionError as e:
            print(f"FAIL  {n}: {e}"); 
        except Exception as e:
            print(f"ERROR {n}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{len(fns)} passed")
    sys.exit(0 if passed == len(fns) else 1)


if __name__ == "__main__":
    _run()
