"""
Tests for squire2_engine (SQUIRE-2 Phase 1, SQUIRE_2_BUILD_BRIEF.md s5; RG-0224 extended).

Run:  python3 test_squire2.py
Pure logic only -- no database, no network. The API/DB/rendered half of the acceptance list is proven by
scripts/smoke_harness/verify_squire2.py (boots the real BEA on a throwaway database).
"""
import os
import re

import squire2_engine as E


def _card_text(n, prefix="Card"):
    return "\n".join("%s %02d | M10 | %.2f | 1" % (prefix, i, 1.0 + i) for i in range(n))


# ── acceptance 1: 30-card sell and buy lists, one advice line each, pass/warn on the user's own rule ──
def test_thirty_card_lists_one_line_each():
    lines, rej = E.parse_card_list(_card_text(30))
    assert len(lines) == 30 and not rej
    market = {"value": 10.0, "currency": "USD", "basis": "today's market price (condition not verified)", "condition_verified": False}
    sell = [E.advise_line({**l, "user_price": 12.5 if i % 2 else 11.0}, "sell", {"sell_margin_pct": 20}, market) for i, l in enumerate(lines)]
    assert len(sell) == 30
    assert {a["status"] for a in sell} == {"pass", "warn"}
    assert all(a["target"] == 12.0 for a in sell)
    buy = [E.advise_line({**l, "user_price": 7.5 if i % 2 else 9.0}, "buy", {"buy_discount_pct": 20}, market) for i, l in enumerate(lines)]
    assert len(buy) == 30 and {a["status"] for a in buy} == {"pass", "warn"}
    assert all(a["target"] == 8.0 for a in buy)
    # every line carries a one-sentence reason with the market and the rule
    assert all("market" in a["reason"].lower() for a in sell + buy)


def test_unresolved_returned_never_guessed():
    lines, rej = E.parse_card_list("Lightning Bolt | M10 | 2.50 | 4\n12345 | XX | 3\n   \n2x Counterspell (MH2) 1.20")
    assert [l["name"] for l in lines] == ["Lightning Bolt", "Counterspell"]
    assert lines[1]["quantity"] == 2 and lines[1]["set_code"] == "MH2" and lines[1]["user_price"] == 1.2
    assert len(rej) == 1 and "could not identify" in rej[0]["reason"]
    a = E.advise_line({"name": "Lightnin Blot", "resolved": False}, "buy", {"buy_discount_pct": 20}, None)
    assert a["status"] == "unresolved" and "check name/set" in a["reason"]


def test_limit_100_lines():
    lines, rej = E.parse_card_list(_card_text(105))
    assert len(lines) == 100 and len(rej) == 5


# ── acceptance 2: a NM rule is never 'met' from a price that is not condition-verified ──
def test_nm_rule_never_met_unverified():
    rules = {"buy_discount_pct": 20, "min_condition": "NM"}
    unver = E.market_reference({"usd": 10.0}, None, None)
    assert unver["condition_verified"] is False
    a = E.advise_line({"name": "X", "user_price": 1.0}, "buy", rules, unver)
    assert a["status"] == "unverified"
    assert E.buy_line_met({"name": "X"}, rules, unver, 1.0) is False
    ver = E.market_reference({"usd": 10.0}, None, {"value": 9.0, "currency": "USD"})
    assert ver["condition_verified"] is True and ver["value"] == 9.0
    assert E.advise_line({"name": "X", "user_price": 7.0}, "buy", rules, ver)["status"] == "pass"
    assert E.buy_line_met({"name": "X"}, rules, ver, 7.0) is True


def test_trend_30_days():
    hist = [("2026-08-01", 5.0), ("2026-09-10", 10.0), ("2026-09-25", 11.0), ("2026-10-09", 12.0)]
    t = E.trend(hist)
    assert t["from_date"] == "2026-09-10" and t["change_pct"] == 20.0 and t["direction"] == "rising"
    assert E.trend([("2026-10-09", 1.0)]) is None


# ── acceptance 5: crux report has comps n, yield, EPC, crime, flood, risks, advantages, verdict; none without data ──
def test_crux_report_fields_and_no_data_no_report():
    comps = {"value": 250000.0, "n": 60, "provenance": "HM Land Registry"}
    rep = E.crux_report(asking=210000, currency="GBP", comps=comps, rent={"value": 1100, "provenance": "ONS/VOA"},
                        epc={"rating": "C", "floor_area": 78, "age_band": "1950-1966"}, crime={"count": 80},
                        flood={"in_area": False}, rate={"pct": 3.75}, rules={"min_yield_pct": 5})
    labels = {n["label"] for n in rep["numbers"]}
    assert rep["comps_n"] == 60 and rep["gross_yield_pct"] == round(1100 * 12 / 210000 * 100, 2)
    assert {"Energy rating", "Flood area", "Gross yield", "Sold median nearby", "Finance line"} <= labels
    assert any("Street crimes" in l for l in labels)
    assert len(rep["risks"]) == 3 and len(rep["advantages"]) == 3 and rep["verdict"].startswith("Bargain")
    assert E.crux_report(asking=210000, currency="GBP", comps=None) is None
    assert E.crux_report(asking=210000, currency="GBP", comps={"value": 1, "n": 2}) is None
    assert E.crux_report(asking=None, currency="GBP", comps=comps) is None


# ── acceptance 6: zero matches in 90 days -> reality-check with a numbered alternative ──
def test_reality_check_numbered_alternative():
    rows = [{"price_num": p, "suburb": "Arcadia", "currency": "ZAR"} for p in (1_200_000, 1_350_000, 1_500_000)]
    rc = E.reality_check({"max_price": 1_000_000}, rows)
    assert rc["met"] == 0 and rc["realistic"] is False
    assert rc["alternatives"][0]["n"] == 1 and rc["alternatives"][0]["to"] == 1_200_000
    assert rc["alternatives"][0]["would_have_matched"] == 1
    assert "Nearest real alternative" in rc["line"]
    assert E.reality_check({"max_price": 2_000_000}, rows)["met"] == 3


# ── acceptance 7: a month with zero matches still produces the report ──
def test_monthly_report_zero_matches():
    rep = E.monthly_report({"id": 1, "category": "Property"}, "2026-09", matches=0, close_calls=[], movement=[], reality_line=None)
    assert rep["lines"] and rep["lines"][0].startswith("No new matches")
    assert any("Market movement" in l for l in rep["lines"])


def test_close_call_within_10pct():
    r = {"max_price": 1_000_000}
    assert E.close_call(r, {"price_num": 1_080_000}) is not None
    assert E.close_call(r, {"price_num": 1_200_000}) is None
    assert E.close_call(r, {"price_num": 900_000}) is None   # inside the rule is a match, not a close call


# ── F learning, G urgency ──
def test_learning_changes_rules():
    rules, msg = E.apply_feedback({}, "not_suburb", {"suburb": "Sunnyside"})
    assert rules["exclude_suburbs"] == ["Sunnyside"] and "Sunnyside" in msg
    assert E.passes_rules(rules, {"suburb": "Sunnyside"})[0] is False
    rules, msg = E.apply_feedback(rules, "too_expensive", {"price_num": 100.0})
    assert rules["max_price"] == 95.0
    try:
        E.apply_feedback({}, "nope", {})
        raise AssertionError("unknown reason accepted")
    except ValueError:
        pass


def test_urgency():
    assert E.urgency("buy", True) == "instant"
    assert E.urgency("buy", False) == "digest"
    assert E.urgency("sell", True) == "digest"
    assert E.urgency("watch", True) == "digest"


# ── acceptance 8 (engine half): one quote, whole Tuppence, caution text; unquotable feeds refused ──
def test_pa_quote():
    q = E.pa_quote(["propertydata"], live_feeds={"propertydata"}, feed_costs_usd={"propertydata": 30.0},
                   sharing={"propertydata": 2}, ai_usd_month=1.0, margin_pct=30.0)
    assert q["tuppence_per_month"] == 8          # (30/3 + 1) * 1.3 = 14.3 USD -> 7.15T -> 8T
    assert "every month" in q["caution_text"] and "monthly report" in q["caution_text"]
    for bad in (dict(live_feeds=set(), feed_costs_usd={"propertydata": 30.0}),
                dict(live_feeds={"propertydata"}, feed_costs_usd={})):
        try:
            E.pa_quote(["propertydata"], sharing={}, ai_usd_month=1, margin_pct=30, **bad)
            raise AssertionError("unquotable feed was quoted")
        except ValueError:
            pass


# ── acceptance 9: no AI model name in any user-facing string, label or log category ──
_MODEL_RX = re.compile(r"\b(claude|sonnet|opus|haiku|gpt-?\d|chatgpt|openai|gemini|llama|mistral|deepseek|grok)\b", re.I)


def test_no_model_names():
    here = os.path.dirname(os.path.abspath(__file__))
    for f in ("squire2_engine.py", "squire2_feeds.py"):
        src = open(os.path.join(here, f), encoding="utf-8").read()
        assert not _MODEL_RX.search(src), (f, _MODEL_RX.search(src).group(0))
    bea = open(os.path.join(here, "bea_main.py"), encoding="utf-8").read()
    i = bea.find("# SQUIRE-2 — Squire becomes the full personal assistant"); j = bea.find("# ONE $5 TIER", i)
    assert i > 0 and j > i
    m = _MODEL_RX.search(bea[i:j])
    assert not m, m.group(0)


if __name__ == "__main__":
    n = 0
    for k, v in sorted(globals().items()):
        if k.startswith("test_") and callable(v):
            v(); n += 1; print("ok ", k)
    print("\nALL %d SQUIRE-2 ENGINE TESTS PASS" % n)
