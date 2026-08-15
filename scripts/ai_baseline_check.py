#!/usr/bin/env python3
"""ai_baseline_check.py -- the fixed baseline holds, or this goes red.

David's ruling, 14 Aug 2026: AI model selection cannot be automated when a silent
change can move profit from good to very bad with no control or accountability.
So there is a fixed baseline -- a KNOWN cost figure -- and only equivalent swaps.

The thing this file exists to catch is subtler than "someone changed the model".
A pure model-id register would have passed every day while cost drifted, because
the biggest cost movers are not model ids at all:

  * an image cap or a probe resolution (896 -> 1344 on 11 Jul 2026 raised
    anon-scan input tokens ~2.2x across four call sites, recorded as a code comment)
  * a max_tokens literal buried in a 17,945-line file
  * a failover that lands on a lane nobody priced
  * a second model table that disagrees with the first and only wins when an
    import fails

So the baseline pins the model AND ITS COST ENVELOPE, and this checker walks the
live source to prove both still hold.

Exit 0 = the baseline holds.  1 = drift.  2 = baseline or price card unreadable.

    python3 scripts/ai_baseline_check.py
    python3 scripts/ai_baseline_check.py --known-ok   (mute drift already logged
                                                       in the baseline, so NEW
                                                       drift stands out)
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
BASELINE = os.path.join(REPO, "AI_BASELINE.json")
CARD = os.path.join(REPO, "ai_price_card.json")

FAIL, WARN, INFO = "FAIL", "WARN", "INFO"


def _load(path, what):
    if not os.path.exists(path):
        print("AI BASELINE CHECK: %s missing at %s" % (what, path))
        sys.exit(2)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except Exception as exc:  # noqa: BLE001
        print("AI BASELINE CHECK: %s unreadable -- %s" % (what, exc))
        sys.exit(2)


def _src(rel):
    p = os.path.join(REPO, rel)
    if not os.path.exists(p):
        return None
    with open(p, "r", encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _dict_literal(src, name):
    """Pull a top-level dict literal out of source without importing it -- importing
    ai_provider would pick up env and DB state and defeat the point."""
    m = re.search(r"^%s\s*=\s*\{" % re.escape(name), src, re.M)
    if not m:
        return None
    i = src.index("{", m.start())
    depth, j = 0, i
    while j < len(src):
        if src[j] == "{":
            depth += 1
        elif src[j] == "}":
            depth -= 1
            if depth == 0:
                break
        j += 1
    body = src[i:j + 1]
    body = re.sub(r"#[^\n]*", "", body)          # strip comments
    try:
        return eval(body, {"__builtins__": {}}, {})   # noqa: S307 - literal only
    except Exception:
        return None


def check_task_model(base):
    """The approved model per lane and tier has not moved."""
    out = []
    src = _src("ai_provider.py")
    if src is None:
        return [(FAIL, "ai_provider.py unreadable -- the seam cannot be verified")]
    live = _dict_literal(src, "TASK_MODEL")
    if live is None:
        return [(FAIL, "could not parse TASK_MODEL out of ai_provider.py")]
    for tier, td in base["tiers"].items():
        for lane, ld in td["lanes"].items():
            want, got = ld["model"], live.get(lane, {}).get(tier)
            if got is None:
                out.append((FAIL, "TASK_MODEL[%s][%s] has GONE -- baseline expects %s"
                            % (lane, tier, want)))
            elif got != want:
                out.append((FAIL, "MODEL DRIFT: TASK_MODEL[%s][%s] is %s, baseline says %s"
                            % (lane, tier, got, want)))
    for lane, tiers in live.items():
        for tier, model in tiers.items():
            if lane not in base["tiers"].get(tier, {}).get("lanes", {}):
                out.append((FAIL, "TASK_MODEL[%s][%s]=%s is not in the baseline at all -- "
                                  "an unapproved lane/tier" % (lane, tier, model)))
    if not out:
        out.append((INFO, "all %d lane/tier model ids match the baseline"
                    % sum(len(t["lanes"]) for t in base["tiers"].values())))
    return out


def check_second_model_table(base):
    """bea_main carries its own model map used only when `import ai_provider` fails.
    A disagreement here is a silent price change that appears only under fault."""
    out = []
    src = _src("bea_main.py")
    ap = _src("ai_provider.py")
    if src is None or ap is None:
        return [(FAIL, "bea_main.py or ai_provider.py unreadable")]
    m = re.search(r"_TS_AI_MODELS\s*=\s*\{(.*?)\}", src, re.S)
    if not m:
        return [(WARN, "could not find _TS_AI_MODELS in bea_main.py")]
    fallback = dict(re.findall(r'"(\w+)"\s*:\s*"([^"]+)"', m.group(1)))
    live = _dict_literal(ap, "TASK_MODEL") or {}
    primary = live.get(base["baseline_lane"], {})
    # Grade this honestly. On the SUCCESS path bea_main already derives _TS_AI_MODELS from
    # TASK_MODEL, so the literal below only applies when `import ai_provider` throws -- at which
    # point no lane is reachable through the seam at all. Reporting that as FAIL overstates it,
    # and a control that cries wolf is a control that gets muted. It is a real inconsistency
    # (the ids name a vendor the platform is no longer based on) so it is a WARN, not silence.
    if "_ts_ai.TASK_MODEL.get(" not in src:
        out.append((FAIL, "_TS_AI_MODELS no longer derives from the seam on the success path -- "
                          "two model tables with no link between them"))
    off = [(t, m) for t, m in fallback.items() if t in primary and m != primary[t]]
    if off:
        out.append((WARN, "the import-failure fallback names %s where the base lane (%s) uses %s. "
                          "It bites only if `import ai_provider` throws, when no lane is reachable "
                          "anyway -- but the ids name a vendor the platform is no longer based on. "
                          "One-line fix: drop the literal and let the AI endpoints refuse via "
                          "any_lane_configured()"
                    % (", ".join("%s=%s" % (t, m) for t, m in off), base["baseline_lane"],
                       ", ".join("%s=%s" % (t, primary[t]) for t, _ in off))))
    if not out:
        out.append((INFO, "the import-failure fallback table agrees with the seam"))
    return out


def check_prices_against_card(base):
    """Every price stated in code matches the register. A wrong price is worse than
    no price: the ceilings are computed from it, so they silently loosen."""
    out = []
    card = _load(CARD, "price card")
    if card.get("version") != base.get("price_card_version"):
        out.append((WARN, "baseline was cut against price card %s, live card is %s -- "
                          "re-verify the envelope costs"
                    % (base.get("price_card_version"), card.get("version"))))
    flat = {}
    for prov, pd in card.get("providers", {}).items():
        for model, md in pd.get("models", {}).items():
            flat[model] = (md.get("in"), md.get("out"), md.get("ccy", "USD"))

    src = _src("bea_main.py")
    if src:
        mp = _dict_literal(src, "_MODEL_PRICE")
        if mp:
            tier_model = {t: base["tiers"][t]["lanes"][base["baseline_lane"]]["model"]
                          for t in base["tiers"]}
            for key, pair in mp.items():
                model = tier_model.get(key)
                if not model or model not in flat:
                    continue
                want_in, want_out, ccy = flat[model]
                if ccy == "USD" and (abs(pair[0] - want_in) > 1e-9 or abs(pair[1] - want_out) > 1e-9):
                    out.append((FAIL, "PRICE DRIFT: _MODEL_PRICE[%r] = (%.2f, %.2f) but the card "
                                      "says %s is (%.2f, %.2f). ai_spend_log and every daily "
                                      "ceiling are computed from this table, so the rails are "
                                      "off by the same margin"
                                % (key, pair[0], pair[1], model, want_in, want_out)))
    for tier, td in base["tiers"].items():
        for lane, ld in td["lanes"].items():
            if ld["model"] not in flat:
                out.append((FAIL, "%s is in the baseline but has NO price-card entry -- "
                                  "no price, no swap" % ld["model"]))
    if not out:
        out.append((INFO, "code price tables agree with the register"))
    return out


def check_envelope_constants(base):
    """The non-model cost drivers. This is the section a model-id register misses."""
    out = []
    src = _src("bea_main.py")
    if src is None:
        return [(FAIL, "bea_main.py unreadable")]
    pinned = base["pinned_constants"]

    n1344 = len(re.findall(r"thumbnail\(\(1344,\s*1344\)", src))
    if n1344 == 0:
        out.append((FAIL, "the 1344px vision probe size has changed or gone -- input tokens per "
                          "image scale with the SQUARE of this number"))
    if re.search(r"thumbnail\(\((\d+),\s*\1\)", src):
        sizes = sorted({int(x) for x in re.findall(r"thumbnail\(\((\d+),\s*\d+\)", src)})
        allowed = {pinned["vision_probe_max_px"], pinned["orient_probe_max_px"]}
        for s in sizes:
            if s not in allowed:
                out.append((FAIL, "UNPINNED PROBE SIZE %dpx found -- baseline pins %s. An image "
                                  "dimension change is a cost change with no model change"
                            % (s, sorted(allowed))))
    for label, pat, want in (
            ("vision_draft_max_side", r"MAX_SIDE\s*=\s*(\d+)", pinned["vision_draft_max_side"]),
            ("vision_draft_max_photos", r"if\s+len\(photos\)\s*>\s*(\d+)", pinned["vision_draft_max_photos"]),
            ("batch_cards_max_images", r"req\.images\[:(\d+)\]", pinned["batch_cards_max_images"]),
            ("anon_refine_max_regions", r"list\(regions\)\[:(\d+)\]", pinned["anon_refine_max_regions"])):
        m = re.search(pat, src)
        if not m:
            out.append((WARN, "%s: could not locate the constant to verify" % label))
        elif int(m.group(1)) != want:
            out.append((FAIL, "ENVELOPE DRIFT: %s is %s, baseline pins %d -- cost moved without "
                              "any model changing" % (label, m.group(1), want)))

    for tier, td in base["tiers"].items():
        cap = td["envelope"]["max_out_tokens"]
        over = [int(t) for t in re.findall(
            r'task\s*=\s*"%s"[^)]*?max_tokens\s*=\s*(\d+)' % tier, src, re.S)]
        over += [int(t) for t in re.findall(
            r'max_tokens\s*=\s*(\d+)[^)]*?task\s*=\s*"%s"' % tier, src, re.S)]
        for v in over:
            if v > cap:
                out.append((FAIL, "max_tokens=%d on a %r call exceeds the baseline envelope of %d"
                            % (v, tier, cap)))
    if not out:
        out.append((INFO, "image caps, probe sizes and max_tokens all inside the envelope"))
    return out


def check_failover_affordability(base):
    """An outage must not silently re-price the platform."""
    out = []
    tol = base["failover_cost_tolerance"]
    blocked = []
    exempt = {k for k, v in base.get("lane_roles", {}).items() if v.get("cost_exempt")}
    for tier, td in base["tiers"].items():
        for lane, ld in td["lanes"].items():
            if lane == td["baseline_lane"]:
                continue
            if lane in exempt:
                continue          # a last resort is reached when the alternative is being down
            if ld["multiple_of_baseline"] > tol:
                blocked.append((tier, lane, ld["multiple_of_baseline"]))
    ap = _src("ai_provider.py")
    if ap:
        body = ap[ap.find("def complete("):] if "def complete(" in ap else ""
        end = body.find("\ndef ", 10)
        body = body[:end] if end > 0 else body
        # strip docstrings and comments -- a docstring that MENTIONS cost is not a cost check
        body = re.sub(r'"""..*?"""', "", body, flags=re.S)
        body = re.sub(r"#[^\n]*", "", body)
        if not re.search(r"price|cost|budget|afford|baseline", body, re.I):
            out.append((FAIL, "complete() consults NO cost input when building the fallback "
                              "chain -- the order is the ADAPTERS dict insertion order, so an "
                              "outage picks the next lane with nothing asking its price"))
    for tier, lane, mult in blocked:
        out.append((WARN, "%s is %.2fx baseline on the %r tier (tolerance %.2fx) -- it must NOT "
                          "be an automatic failover target for that tier; a deliberate R2 "
                          "decision only" % (lane, mult, tier, tol)))
    for lane in sorted(exempt):
        mx = max(td["lanes"][lane]["multiple_of_baseline"] for td in base["tiers"].values())
        out.append((INFO, "%s is COST-EXEMPT by role (last resort, peaks at %.2fx base) -- the tolerance "
                          "does not gate it, but reaching it must ALERT and be time-boxed" % (lane, mx)))
    if not blocked:
        out.append((INFO, "every cost-gated lane is inside the continuity tolerance"))
    return out


def check_change_is_recorded(base):
    """A change nobody can see afterwards is not governed."""
    out = []
    src = _src("bea_main.py")
    if src is None:
        return [(FAIL, "bea_main.py unreadable")]
    m = re.search(r"def set_flags\(.*?(?=\n@app\.|\ndef )", src, re.S)
    if not m:
        out.append((WARN, "could not locate set_flags to verify auditing"))
    else:
        blk = m.group(0)
        if "ai_active" in blk and not re.search(r"_log\.(warning|info)", blk):
            out.append((FAIL, "POST /admin/flags changes the live lane for every AI feature and "
                              "writes NO log line -- its neighbour /admin/ai-restore does. A lane "
                              "change is currently undetectable after the fact"))
    if not re.search(r"CREATE TABLE[^;]*admin_audit", src, re.I):
        out.append((WARN, "no admin_audit table exists -- prior value, actor and reason are not "
                          "recorded for any lane change"))
    if not out:
        out.append((INFO, "lane changes are logged and audited"))
    return out


def main():
    known_ok = "--known-ok" in sys.argv
    base = _load(BASELINE, "baseline")
    known = {d["what"][:48] for d in base.get("known_drift_at_creation", [])} if known_ok else set()

    groups = (
        ("approved models (TASK_MODEL)", check_task_model(base)),
        ("import-failure shadow table", check_second_model_table(base)),
        ("prices vs the register", check_prices_against_card(base)),
        ("cost envelope: images, probes, max_tokens", check_envelope_constants(base)),
        ("failover affordability", check_failover_affordability(base)),
        ("change is recorded", check_change_is_recorded(base)),
    )
    fails = warns = muted = 0
    print("AI BASELINE CHECK -- MarketSquare")
    print("baseline v%s against price card %s" % (base["version"], base["price_card_version"]))
    print("=" * 78)
    for title, results in groups:
        print("\n[%s]" % title)
        shown = False
        for level, msg in results:
            if level == FAIL and any(k[:30] in msg or msg[:30] in k for k in known):
                muted += 1
                continue
            shown = True
            print("  %-5s %s" % (level, msg))
            if level == FAIL:
                fails += 1
            elif level == WARN:
                warns += 1
        if not shown:
            print("  INFO  clear (or muted by --known-ok)")

    print("\n" + "=" * 78)
    worst = max(t["baseline_worst_case_usd"] for t in base["tiers"].values())
    print("Baseline worst case, any tier, one call: $%.5f   with one retry: $%.5f" % (worst, worst * 2))
    print("%d FAIL, %d WARN%s" % (fails, warns, ", %d muted as known" % muted if muted else ""))
    if fails:
        print("RESULT: the baseline has DRIFTED. Cost is no longer the known figure.")
        return 1
    print("RESULT: baseline holds -- model, envelope and price are the approved ones.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
