#!/usr/bin/env python3
"""ai_challenger_board.py -- automatic CHALLENGE, manual DECISION.

David's ruling of 14 Aug 2026 forbids automating the model SWITCH. It does not
forbid automating the CHALLENGE -- and that distinction is the whole point of
this file.

If the switch is manual AND the review is manual, then doing nothing is a
decision that gets taken by default every single day, and the incumbent wins by
inertia rather than by merit. This board never switches anything. It computes
the value case per tier from the price card, states plainly where the baseline is
being beaten, names what is structurally BLOCKED from even being compared, and
puts the numbers in front of David so that silence stops being an answer.

Value = AA index points per USD of worst-case cost inside the tier's envelope.
Capability floor and the golden set remain binary gates -- value only ever
proposes, it never disposes. That is the price card's own funnel, applied.

    python3 scripts/ai_challenger_board.py
    python3 scripts/ai_challenger_board.py --json
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BASELINE = os.path.join(REPO, "AI_BASELINE.json")
CARD = os.path.join(REPO, "ai_price_card.json")
SCOREBOARD = os.path.join(REPO, "ai_scoreboard.py")

# The price card's own procurement bar (anti_jitter.min_cost_delta_pct).
MIN_SAVING = 0.30


def _load(p, what):
    if not os.path.exists(p):
        print("CHALLENGER BOARD: %s missing at %s" % (what, p))
        sys.exit(2)
    with open(p, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _usd(md, fxm):
    ccy = md.get("ccy", "USD")
    return (md["in"] * fxm, md["out"] * fxm) if ccy == "EUR" else (md["in"], md["out"])


def _img_tok(px):
    return (px * px * 0.75) / 750.0


def _live_golden_pass():
    """Which lanes may even ENTER the ranking. A lane absent here cannot be
    compared at all, however cheap or capable it is."""
    src = ""
    if os.path.exists(SCOREBOARD):
        with open(SCOREBOARD, "r", encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    m = re.search(r"GOLDEN_PASS\s*=\s*\{(.*?)\n\}", src, re.S)
    body = m.group(1) if m else ""
    return {k for k in re.findall(r'^\s*"(\w+)"\s*:', body, re.M)}


def build(base, card):
    fxm = card["fx"]["EUR_USD"] * (1 + card["fx"]["buffer_pct"] / 100.0)
    models = {}
    for prov, pd in card.get("providers", {}).items():
        for name, md in pd.get("models", {}).items():
            aa = md.get("aa_index") or {}
            gs = md.get("golden_set") or {}
            models[(prov, name)] = {
                "usd": _usd(md, fxm),
                "aa": aa.get("score"),
                "aa_effort_matched": aa.get("effort_matched"),
                "aa_caveat": aa.get("caveat"),
                "gate": md.get("gate"),
                "golden": gs.get("status"),
                "golden_detail": (gs.get("detail") or "")[:90],
            }
    entrants = _live_golden_pass()
    board = {}
    for tier, td in base["tiers"].items():
        env = td["envelope"]
        tin = env["max_in_tokens"] + env["max_images"] * _img_tok(env["max_image_px"])
        rows = []
        for lane, ld in td["lanes"].items():
            key = (lane, ld["model"])
            m = models.get(key)
            if not m:
                rows.append({"lane": lane, "model": ld["model"], "status": "UNREGISTERED",
                             "note": "not on the price card -- cannot be considered"})
                continue
            pin, pout = m["usd"]
            cost = tin / 1e6 * pin + env["max_out_tokens"] / 1e6 * pout
            rows.append({
                "lane": lane, "model": ld["model"], "cost": round(cost, 6),
                "aa": m["aa"], "value": round(m["aa"] / cost, 1) if (m["aa"] and cost) else None,
                "gate": m["gate"], "golden": m["golden"],
                "effort_matched": m["aa_effort_matched"], "caveat": m["aa_caveat"],
                "can_enter": lane in entrants,
                "is_baseline": lane == td["baseline_lane"],
            })
        base_row = next(r for r in rows if r.get("is_baseline"))
        for r in rows:
            if r.get("is_baseline") or "cost" not in r:
                continue
            cheaper = 1 - r["cost"] / base_row["cost"]
            better = (r["aa"] or 0) >= (base_row["aa"] or 0)
            r["saving_pct"] = round(cheaper * 100, 1)
            r["capability_ge_baseline"] = better
            if not r["can_enter"]:
                r["status"] = "BLOCKED BY PROCESS"
            elif cheaper >= MIN_SAVING and better:
                r["status"] = "CHALLENGER"
            elif cheaper >= MIN_SAVING and not better:
                r["status"] = "cheaper, weaker"
            elif cheaper < 0:
                r["status"] = "dearer"
            else:
                r["status"] = "no material saving"
        base_row["status"] = "BASELINE"
        board[tier] = {"envelope": env, "rows": sorted(
            rows, key=lambda r: -(r.get("value") or 0))}
    return board, entrants


def lockins(card, entrants):
    """Why the incumbent cannot currently be displaced. Each clause is individually
    reasonable; together they compose into a lock nobody chose."""
    aj = card.get("policy", {}).get("anti_jitter", {})
    funnel = " ".join(card.get("policy", {}).get("funnel", []))
    out = []
    if "formally UNMET" in (aj.get("rule") or ""):
        out.append(("HELD", "The absolute switch floor (min_net_saving_usd_90d = $%s) is by the "
                            "card's own words 'formally UNMET' -- it needs spend-log volume that "
                            "does not exist. A floor that cannot be computed cannot be cleared."
                    % aj.get("min_net_saving_usd_90d")))
    if "not re-auditioned continuously" in funnel:
        out.append(("HELD", "Funnel step 4: 'sitting models are not re-auditioned continuously'. "
                            "The incumbent never takes the test, so it can never fail it."))
    src = ""
    if os.path.exists(os.path.join(REPO, "bea_main.py")):
        with open(os.path.join(REPO, "bea_main.py"), "r", encoding="utf-8", errors="replace") as fh:
            src = fh.read()
    if re.search(r"ai_scoreboard\.run_nightly\(\)", src) and not re.search(
            r"=\s*ai_scoreboard\.run_nightly\(\)", src):
        out.append(("HELD", "The scoreboard is the only thing that ranks lanes by cost, and its "
                            "return value is discarded at the single call site. Nothing reads it."))
    missing = [p for p in ("openai", "scaleway", "anthropic") if p not in entrants]
    if missing:
        out.append(("HELD", "Lane(s) %s are absent from GOLDEN_PASS and therefore cannot enter the "
                            "ranking at all -- however cheap or capable they are."
                    % ", ".join(missing)))
    return out


def main():
    base = _load(BASELINE, "baseline")
    card = _load(CARD, "price card")
    board, entrants = build(base, card)

    if "--json" in sys.argv:
        print(json.dumps({"board": board, "entrants": sorted(entrants)}, indent=2))
        return 0

    print("AI CHALLENGER BOARD -- automatic challenge, manual decision")
    print("price card %s  ·  procurement bar: >=%d%% saving at equal-or-better capability"
          % (card.get("version"), MIN_SAVING * 100))
    print("=" * 96)
    challengers = 0
    blocked = 0
    for tier, td in board.items():
        e = td["envelope"]
        print("\n[%s]  envelope %s in / %s out / %s img @ %spx"
              % (tier, e["max_in_tokens"], e["max_out_tokens"], e["max_images"], e["max_image_px"]))
        print("  %-30s %10s %7s %9s %9s  %s"
              % ("model", "worst $", "AA idx", "value", "vs base", "status"))
        for r in td["rows"]:
            if "cost" not in r:
                print("  %-30s %10s %7s %9s %9s  %s"
                      % (r["model"][:30], "-", "-", "-", "-", r["status"]))
                continue
            sv = ("%+.0f%%" % r["saving_pct"]) if "saving_pct" in r else "--"
            print("  %-30s %10.5f %7s %9s %9s  %s"
                  % (r["model"][:30], r["cost"], r["aa"], r["value"], sv, r["status"]))
            if r["status"] == "CHALLENGER":
                challengers += 1
            if r["status"] == "BLOCKED BY PROCESS":
                blocked += 1

    print("\n" + "=" * 96)
    print("WHY THE INCUMBENT CANNOT CURRENTLY BE DISPLACED")
    print("=" * 96)
    for state, why in lockins(card, entrants):
        print("  %-5s %s" % (state, why))
    print("\n  Each clause above is individually sensible. Together they compose into permanent")
    print("  incumbency -- an outcome none of them intended, and the same shape of failure as")
    print("  two optimising systems meeting without anyone modelling the interaction.")

    print("\n" + "=" * 96)
    print("%d challenger(s) on merit, %d lane/tier(s) BLOCKED BY PROCESS rather than by merit."
          % (challengers, blocked))
    if blocked:
        print("RESULT: the board cannot give an honest answer while a lane is excluded by process.")
        return 1
    if challengers:
        print("RESULT: a challenger beats the baseline. This is DAVID'S decision, not the board's.")
        return 1
    print("RESULT: baseline is the best available buy on the registered field.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
