#!/usr/bin/env python3
"""PRICE TRUTH — the value router's eyes (Live-Values Doctrine, David 31 Jul 2026).

Reads ai_price_card.json (the ONLY legal source of AI prices in this project) and
ai_provider.py's TASK_MODEL, then reports, per task tier and lane:

  effective USD cost per call (low/high token shapes, FX-buffered for EUR lanes)
  a VALUE RANKING driven by the two KPIs David named: CAPABILITY first, COST second
    gate order: production > golden-set-passed > pending-golden-set (ineligible for
    production traffic — shown, marked, never ranked eligible)

The ranking ADVISES. Switching stays governed by the standing rules (Addendum 3:
measured failure / forced exit, golden-set gate, stability over price-chasing).
This tool exists so that whenever a switch IS decided, the numbers are current —
never a July decision on a June price again.

USAGE
    python3 scripts/price_truth.py            # full report
    python3 scripts/price_truth.py --check    # quiet freshness/coverage check (ledger/housekeep)
    python3 scripts/price_truth.py --days-max 45
Exit: 0 ok · 1 stale card / coverage gap · 2 config error.  Stdlib only.
"""
import json, os, re, sys, datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CARD = os.path.join(REPO, "ai_price_card.json")
SEAM = os.path.join(REPO, "ai_provider.py")
DAYS_MAX = 45

# Token shapes per tier (chars of reality, not measurements — replace with spend-log
# p50/p95 once volume exists; the Peer's cost review documents the derivation)
SHAPES = {  # (in_low, out_low, in_high, out_high)
    "haiku":  (500, 120, 2000, 700),
    "triage": (500, 120, 2000, 700),
    "sonnet": (500, 120, 2000, 700),
    "vision": (1100 + 400, 1200, 19200 + 800, 1200),  # images + prompt text
}
GATE_ORDER = {"production": 0, "golden-set-passed": 1, "pending-golden-set": 2}
GATE_ELIGIBLE = {"production", "golden-set-passed"}


def load():
    if not os.path.exists(CARD):
        print("ai_price_card.json MISSING — the Live-Values Doctrine requires it"); sys.exit(1)
    card = json.load(open(CARD, encoding="utf-8"))
    src = open(SEAM, encoding="utf-8").read()
    rows = {}
    for prov in ("anthropic", "openai", "scaleway"):
        m = re.search('"%s"\\s*:\\s*\\{(.*?)\\}' % prov, src, re.S)
        if m:
            rows[prov] = dict(re.findall(r'"(\w+)"\s*:\s*"([^"]+)"', m.group(1)))
    return card, rows


def usd(entry, card):
    if entry["ccy"] == "USD":
        return entry["in"], entry["out"]
    fx = card["fx"]["EUR_USD"] * (1 + card["fx"].get("buffer_pct", 0) / 100.0)
    return entry["in"] * fx, entry["out"] * fx


def main():
    check = "--check" in sys.argv
    days_max = DAYS_MAX
    if "--days-max" in sys.argv:
        days_max = int(sys.argv[sys.argv.index("--days-max") + 1])
    card, task_model = load()

    problems = []
    age = (datetime.date.today()
           - datetime.date.fromisoformat(card["verified_at"])).days
    if age > days_max:
        problems.append(f"price card is {age} days old (max {days_max}) — re-verify against "
                        "live vendor pages/console and bump verified_at")
    priced = {m for p in card["providers"].values() for m in p["models"]}
    wired = {m for row in task_model.values() for m in row.values()}
    for m in sorted(wired - priced):
        problems.append(f"wired model {m!r} has NO price-card entry — a cost decision about "
                        "it would run on memory, which is the exact fault this card prevents")

    if check:
        for p in problems: print("FAIL:", p)
        print("price card: %s · verified %s (%d days) · %d models priced, %d wired"
              % ("STALE/GAPPED" if problems else "OK", card["verified_at"], age,
                 len(priced), len(wired)))
        sys.exit(1 if problems else 0)

    print(f"# Price truth — card {card['version']} · verified {card['verified_at']} "
          f"({age} days old, max {days_max})")
    for p in problems: print("  !! " + p)
    fxn = card["fx"]
    print(f"  FX: EUR->USD {fxn['EUR_USD']} +{fxn.get('buffer_pct',0)}% buffer (as of {fxn['as_of']})\n")

    entry_of = {}
    for prov, pdata in card["providers"].items():
        for model, e in pdata["models"].items():
            entry_of[(prov, model)] = e

    for tier, (il, ol, ih, oh) in SHAPES.items():
        lanes = []
        for prov, row in task_model.items():
            model = row.get(tier)
            e = entry_of.get((prov, model))
            if not e:
                lanes.append((prov, model, None, None, None, "NO PRICE ENTRY")); continue
            pi, po = usd(e, card)
            lo = il / 1e6 * pi + ol / 1e6 * po
            hi = ih / 1e6 * pi + oh / 1e6 * po
            lanes.append((prov, model, lo, hi, e["gate"], ""))
        ranked = sorted(lanes, key=lambda x: (x[4] not in GATE_ELIGIBLE if x[4] else True,
                                              GATE_ORDER.get(x[4], 9), x[3] or 9e9))
        print(f"## {tier}  (shapes: {il}/{ol} low, {ih}/{oh} high tokens)")
        for i, (prov, model, lo, hi, gate, note) in enumerate(ranked, 1):
            if lo is None:
                print(f"  {i}. {prov:10s} {model:28s} {note}"); continue
            tag = "ELIGIBLE" if gate in GATE_ELIGIBLE else "GATED-OUT (no production traffic)"
            print(f"  {i}. {prov:10s} {model:28s} ${lo:.5f}–${hi:.5f}/call "
                  f"(${lo*1000:.2f}–${hi*1000:.2f}/1k) · {gate} · {tag}")
        print()

    print("Ranking = capability gate first, then cost. It ADVISES; switches follow the "
          "standing rules (golden-set, stability, no price-chasing). Verify EUR lanes on "
          "the vendor console before acting — a pricing page is a claim, an invoice is a fact.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
