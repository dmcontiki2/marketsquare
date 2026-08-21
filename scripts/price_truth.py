#!/usr/bin/env python3
"""PRICE TRUTH — the value router's eyes (Live-Values Doctrine, David 31 Jul 2026).

Reads ai_price_card.json (the ONLY legal source of AI prices in this project) and
ai_provider.py's TASK_MODEL, then reports, per task tier and lane:

  effective USD cost per call (low/high token shapes, FX-buffered for EUR lanes)
  the DECISION FUNNEL (Addendum 8): VALUE SCORE = AA-index points per (USD per 1k calls,
    mid shape) proposes the order; the golden-set GATE disposes (production >
    golden-set-passed > pending — pending lanes are shown but never eligible);
    the ANTI-JITTER materiality check compares the winner to the sitting model:
    a procurement switch needs >= the card's min_cost_delta_pct, sustained across
    >= min_card_refreshes (>= min_sustained_days). Failover (T1-T3) is exempt — ops,
    not procurement.

The ranking ADVISES. Switching stays governed by the standing rules (Addendum 3:
measured failure / forced exit, golden-set gate, stability over price-chasing).
This tool exists so that whenever a switch IS decided, the numbers are current —
never a July decision on a June price again.

USAGE
    python3 scripts/price_truth.py            # full report
    python3 scripts/price_truth.py --check    # quiet freshness/coverage check (ledger/housekeep)
    python3 scripts/price_truth.py --days-max 45
    python3 scripts/price_truth.py --snapshot   # also emit ai_funnel_snapshot.json for the +1 card
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

# GOLDEN-AUTHORITY-1 (21 Aug 2026) -- ai_price_card.json and ai_scoreboard.GOLDEN_PASS
# disagreed about openai for three weeks: the card said gate "golden-set-passed" (citing
# GS-OAI-V1, which ran on the SANDBOX key with raw vendor calls) while GOLDEN_PASS excluded
# openai by design because the server-key run (RG-0016) was never done. The +1 card's funnel
# rendered the optimistic one, so the page told David every tier was golden-set-passed on a
# lane that had never been golden-run in production. The scoreboard is the gate of RECORD;
# the price card's golden_set block is EVIDENCE. A provider absent from GOLDEN_PASS can never
# be published as passed, whatever the card claims.
def _production_golden_pass():
    """Providers whose PRODUCTION golden run is on record. Empty set on import failure
    would silently re-open the hole, so a failure is loud."""
    try:
        sys.path.insert(0, REPO)
        from ai_scoreboard import GOLDEN_PASS
        return set(GOLDEN_PASS)
    except Exception as e:
        raise SystemExit("GOLDEN-AUTHORITY-1: cannot read ai_scoreboard.GOLDEN_PASS (%s) -- "
                         "refusing to publish gate labels from the price card alone" % e)

def _gate_reconciled(prov, gate_eff):
    """Downgrade any 'passed/production' claim for a provider the production gate does not list."""
    if gate_eff in ("production", "golden-set-passed") and prov not in _production_golden_pass():
        return "pending-golden-set"
    return gate_eff
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

    if not card.get("active_lane"):
        problems.append("card has no active_lane — RG-0019 cannot compare it to the live switch")
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
            tier_gate = (e.get("gate_by_tier", {}).get(tier) or {}).get("status")
            gate_eff = {"production": "production", "passed": "golden-set-passed",
                        "pending": "pending-golden-set"}.get(tier_gate, e.get("gate"))
            gate_eff = _gate_reconciled(prov, gate_eff)
            pi, po = usd(e, card)
            lo = il / 1e6 * pi + ol / 1e6 * po
            hi = ih / 1e6 * pi + oh / 1e6 * po
            lanes.append((prov, model, lo, hi, gate_eff, ""))
        # VALUE PROPOSES: rank by value score (aa points per $/1k, mid shape), all lanes
        scored = []
        for prov, model, lo, hi, gate, note in lanes:
            if lo is None:
                scored.append((0, prov, model, lo, hi, gate, None, note)); continue
            mid1k = (lo + hi) / 2 * 1000
            e = entry_of.get((prov, model), {})
            ax = e.get("aa_index") or {}
            aa = ax.get("score")
            vs = (aa / mid1k) if (aa and mid1k) else None
            mm = "" if ax.get("effort_matched") else "*"
            scored.append((vs or 0, prov, model, lo, hi, gate, aa, mm))
        scored.sort(key=lambda x: -x[0])
        print(f"## {tier}  (shapes: {il}/{ol} low, {ih}/{oh} high tokens)")
        winner = None
        for i, (vs, prov, model, lo, hi, gate, aa, note) in enumerate(scored, 1):
            if lo is None:
                print(f"  {i}. {prov:10s} {model:28s} {note}"); continue
            ok = gate in GATE_ELIGIBLE
            verdict = {"production": "GATE: production-proven",
                       "golden-set-passed": "GATE: passed",
                       "pending-golden-set": "GATE: NOT RUN — ineligible"}.get(gate, gate)
            print(f"  {i}. {prov:10s} {model:28s} value {vs:6.2f}{note} · AA {aa if aa is not None else '—'}{note} · "
                  f"${lo*1000:.2f}–${hi*1000:.2f}/1k · {verdict}")
            if ok and winner is None:
                winner = (vs, prov, model, lo, hi, aa)
        # FITNESS DISPOSES + ANTI-JITTER: compare eligible winner to the sitting model
        active = card.get("active_lane")
        sitting = next((x for x in scored if x[1] == active and x[3] is not None), None)
        if winner and sitting and winner[1] != active:
            w_mid = (winner[3] + winner[4]) / 2 * 1000
            s_mid = (sitting[3] + sitting[4]) / 2 * 1000
            delta = (s_mid - w_mid) / s_mid * 100
            aj = card.get("policy", {}).get("anti_jitter", {})
            bar = aj.get("min_cost_delta_pct", 30)
            verdict = ("MEETS the %d%% materiality bar — hold for %s card refreshes (>=%s days), then convene the funnel"
                       % (bar, aj.get("min_card_refreshes", 2), aj.get("min_sustained_days", 30))
                       ) if delta >= bar else f"below the {bar}% bar — jitter, no move"
            floor = aj.get("min_net_saving_usd_90d")
            print(f"  -> eligible winner {winner[2]} vs sitting {sitting[2]}: {delta:+.0f}% cost delta · {verdict}")
            if floor:
                print(f"     AND absolute floor: net >= ${floor}/90d after switch costs — needs spend-log "
                      f"volume data to compute; formally UNMET until volumes exist (Correction 5)")
        elif winner:
            print(f"  -> sitting model {winner[2]} IS the eligible winner — no action")
        best_gated = next((x for x in scored if x[5] == "pending-golden-set" and x[0] > (winner[0] if winner else 0)), None)
        if best_gated:
            print(f"  -> PRIZE BEHIND THE GATE: {best_gated[2]} (value {best_gated[0]:.2f} vs winner "
                  f"{winner[0]:.2f}) — run its golden set to unlock")
        print()

    if "--snapshot" in sys.argv:
        snap = {"card_version": card["version"], "generated": card["verified_at"], "tiers": {}}
        for tier in SHAPES:
            rows = []
            for prov, row in task_model.items():
                model = row.get(tier); e = entry_of.get((prov, model)) or {}
                mid = None
                if e:
                    pi, po = usd(e, card)
                    il, ol, ih, oh = SHAPES[tier]
                    mid = ((il/1e6*pi + ol/1e6*po) + (ih/1e6*pi + oh/1e6*po)) / 2 * 1000
                aa = (e.get("aa_index") or {}).get("score")
                g = (e.get("gate_by_tier", {}).get(tier) or {}).get("status") or e.get("gate")
                g_eff = {"production":"production","passed":"golden-set-passed",
                         "pending":"pending"}.get(g, g)
                g_eff = _gate_reconciled(prov, g_eff)      # GOLDEN-AUTHORITY-1
                rows.append(((aa/mid) if (aa and mid) else 0, prov,
                             {"provider": prov, "gate": g_eff}))
            snap["tiers"][tier] = [x[2] for x in sorted(rows, key=lambda x: -x[0])]
        sp = os.path.join(REPO, "ai_funnel_snapshot.json")
        json.dump(snap, open(sp, "w", encoding="utf-8"), indent=1)
        print("snapshot written:", sp, "(order + gate types only — the +1 card's funnel strip)")

    print("* = AA score's effort mode differs from production mode — INDICATIVE only, not decision-grade")
    print("    (Correction 1: a switch needs an effort-matched golden set + token profile first).")
    print("Funnel = value proposes, gate disposes, materiality restrains. It ADVISES; switches follow the "
          "standing rules (golden-set, stability, no price-chasing). Verify EUR lanes on "
          "the vendor console before acting — a pricing page is a claim, an invoice is a fact.")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
