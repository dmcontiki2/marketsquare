"""
squire2_engine.py -- SQUIRE-2 Phase 1 pure logic (SQUIRE_2_BUILD_BRIEF.md, 9 Oct 2026; built 10 Oct 2026)
=========================================================================================================
Squire becomes the full personal assistant. This module is the DETERMINISTIC half: rules, price
advice, the property crux report, the reality-check, learning from reactions, urgency routing,
the monthly report and the Pro PA quote. No database, no network, no AI call -- every number a
user sees is computed here in plain Python so it is auditable and unit-testable.

It is a LAYER over Squire v1 (bea_main.py "SQUIRE --" block). It never matches listings itself:
candidates always come from the existing Zoom/Squire matcher (_zoom_candidates / _squire_shortlist);
this module only judges a candidate against the user's own rules.

Boundaries carried from SQUIRE_SPEC s3 (unchanged): price ADVICE is allowed, price NEGOTIATION is
not; Squire never touches money except the Tuppence ledger; seller identity never enters here
(rows arrive already stripped); no AI model is named anywhere (a function is not a model name).
"""
from __future__ import annotations

import math
import re
import statistics
from typing import Iterable, Optional

BRIEF_KINDS = ("buy", "sell", "watch")
MAX_CARD_LINES = 100
CLOSE_CALL_PCT = 10.0          # s3.10: "close calls (within 10% of a rule)"
TREND_DAYS = 30                # s3.3: MTGJSON 30-day trend
CRIME_HIGH = 500               # street crimes within ~1 mile in one month (a busy city centre reads ~1 700)
CRIME_LOW = 100
REALITY_DAYS = 90              # s3.7: "how many listings in the last 90 days would have met the rules"

# s4 -- David's wording intent, mandatory before approval. Shown verbatim by the API and the app.
PA_CAUTION_TEXT = (
    "Before you approve: the monthly data-subscription part of this quote is due every month, even in a "
    "month when no matching sellers or listings appear. In those months you still receive your monthly "
    "report — close calls, near-misses, market movement and whatever else applies to your brief. "
    "Each result still follows our rule: no report, no charge. It runs until you cancel. If your Tuppence "
    "runs out, the brief pauses and asks you to top up — nothing is lost."
)

_FEEDBACK_REASONS = {
    "too_far": "Too far away",
    "not_suburb": "Not that suburb",
    "too_expensive": "Too expensive",
    "wrong_type": "Not the right type",
    "condition": "Condition not good enough",
}


# ── Numbers ───────────────────────────────────────────────────────────────────
def to_num(v) -> Optional[float]:
    """'R 1 250 000', '$12.50', '12,5', 1250 -> float. None when there is no number."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v) if math.isfinite(float(v)) else None
    s = str(v).strip()
    if not s:
        return None
    s = re.sub(r"[^\d.,\-]", "", s.replace(" ", ""))
    if not s or s in ("-", ".", ","):
        return None
    if "," in s and "." in s:
        s = s.replace(",", "")
    elif s.count(",") == 1 and len(s.split(",")[1]) <= 2:
        s = s.replace(",", ".")
    else:
        s = s.replace(",", "")
    try:
        return float(s)
    except ValueError:
        return None


def pct(a: float, b: float) -> float:
    """Percentage a is above (+) or below (-) b."""
    return (a - b) / b * 100.0


def _fmt_money(v: Optional[float], cur: str = "USD") -> str:
    if v is None:
        return "-"
    sym = {"USD": "$", "GBP": "£", "ZAR": "R", "EUR": "€"}.get((cur or "").upper(), "")
    if v >= 1000:
        return "%s%s" % (sym, "{:,.0f}".format(v))
    return "%s%.2f" % (sym, v)


# ── Rules ─────────────────────────────────────────────────────────────────────
_RULE_KEYS_NUM = ("sell_margin_pct", "buy_discount_pct", "max_price", "min_price", "min_yield_pct",
                  "max_age_years", "max_distance_km", "min_bedrooms")
_CONDITIONS = ("NM", "LP", "MP", "HP", "DMG")


def clean_rules(raw) -> dict:
    """Coerce an untrusted rules dict to the known shape. Unknown keys are dropped."""
    out: dict = {}
    if not isinstance(raw, dict):
        return out
    for k in _RULE_KEYS_NUM:
        v = to_num(raw.get(k))
        if v is not None and v >= 0:
            out[k] = v
    mc = str(raw.get("min_condition") or "").strip().upper()
    if mc in ("NEAR MINT", "NEAR-MINT"):
        mc = "NM"
    if mc in _CONDITIONS:
        out["min_condition"] = mc
    for k in ("exclude_suburbs", "exclude_types"):
        v = raw.get(k)
        if isinstance(v, (list, tuple)):
            vals = sorted({str(x).strip() for x in v if str(x).strip()}, key=str.lower)[:40]
            if vals:
                out[k] = vals
    return out


def _norm(s) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", str(s or "").lower())).strip()


def passes_rules(rules: dict, row: dict) -> tuple[bool, list[str]]:
    """Judge ONE candidate (already matched by the Squire/Zoom matcher) against the user's own rules.
    Returns (inside_rules, list of plain reasons it failed). Rules with no data on the row do not fail
    it -- they are simply not proven, and that is said in the reason list with a 'not known' prefix."""
    fails: list[str] = []
    price = to_num(row.get("price_num", row.get("price")))
    if "max_price" in rules and price is not None and price > rules["max_price"]:
        fails.append("price %s is above your maximum %s" % (_fmt_money(price, row.get("currency")), _fmt_money(rules["max_price"], row.get("currency"))))
    if "min_price" in rules and price is not None and price < rules["min_price"]:
        fails.append("price is below your minimum")
    y = to_num(row.get("gross_yield_pct"))
    if "min_yield_pct" in rules and y is not None and y < rules["min_yield_pct"]:
        fails.append("gross yield %.1f%% is under your %.1f%%" % (y, rules["min_yield_pct"]))
    sub = _norm(row.get("suburb"))
    if sub and any(_norm(x) == sub for x in rules.get("exclude_suburbs", [])):
        fails.append("%s is a suburb you excluded" % row.get("suburb"))
    typ = _norm(row.get("property_type") or row.get("type") or row.get("subcategory"))
    if typ and any(_norm(x) == typ for x in rules.get("exclude_types", [])):
        fails.append("%s is a type you excluded" % (row.get("property_type") or row.get("type") or row.get("subcategory")))
    d = to_num(row.get("distance_km"))
    if "max_distance_km" in rules and d is not None and d > rules["max_distance_km"]:
        fails.append("%.0f km away, beyond your %.0f km" % (d, rules["max_distance_km"]))
    age = to_num(row.get("age_years"))
    if "max_age_years" in rules and age is not None and age > rules["max_age_years"]:
        fails.append("built about %.0f years ago, older than your %.0f" % (age, rules["max_age_years"]))
    beds = to_num(row.get("bedrooms"))
    if "min_bedrooms" in rules and beds is not None and beds < rules["min_bedrooms"]:
        fails.append("%d bedrooms, fewer than your %d" % (beds, rules["min_bedrooms"]))
    return (not fails), fails


def close_call(rules: dict, row: dict, within_pct: float = CLOSE_CALL_PCT) -> Optional[str]:
    """s3.10: a candidate that FAILS only numeric rules, each by no more than `within_pct`. Returns the
    plain sentence for the monthly report, or None."""
    ok, _ = passes_rules(rules, row)
    if ok:
        return None
    misses = []
    price = to_num(row.get("price_num", row.get("price")))
    if "max_price" in rules and price is not None and price > rules["max_price"]:
        over = pct(price, rules["max_price"])
        if over > within_pct:
            return None
        misses.append("%.0f%% over your maximum price" % over)
    y = to_num(row.get("gross_yield_pct"))
    if "min_yield_pct" in rules and y is not None and y < rules["min_yield_pct"]:
        short = -pct(y, rules["min_yield_pct"])
        if short > within_pct:
            return None
        misses.append("yield %.1f%% against your %.1f%%" % (y, rules["min_yield_pct"]))
    # a non-numeric failure (excluded suburb/type) is never a close call
    strict = dict(rules)
    for k in ("max_price", "min_yield_pct"):
        strict.pop(k, None)
    if not passes_rules(strict, row)[0] or not misses:
        return None
    return "; ".join(misses)


# ── Bulk card lists (s3.2) ────────────────────────────────────────────────────
_QTY_RX = re.compile(r"^\s*(\d{1,3})\s*[xX]?\s+(.+)$")
_SET_PAREN_RX = re.compile(r"\(([A-Za-z0-9]{2,6})\)")


def parse_card_list(raw) -> tuple[list[dict], list[dict]]:
    """Accept up to MAX_CARD_LINES lines. Each line: 'Name | SET | price | qty' or '2x Name (SET) 12.50'
    or a dict {name, set, price, quantity}. Returns (lines, rejected). Never guesses: a line with no
    readable name is rejected with a reason; identification against the card database is the caller's."""
    items = raw if isinstance(raw, list) else str(raw or "").splitlines()
    lines, rejected = [], []
    for i, it in enumerate(items):
        if len(lines) >= MAX_CARD_LINES:
            rejected.append({"line": i + 1, "text": str(it)[:120], "reason": "over the %d-card limit for one brief" % MAX_CARD_LINES})
            continue
        if isinstance(it, dict):
            name = str(it.get("name") or "").strip()
            set_code = str(it.get("set") or it.get("set_code") or "").strip().upper()
            price = to_num(it.get("price") or it.get("user_price"))
            qty = int(to_num(it.get("quantity") or it.get("qty")) or 1)
            text = name
        else:
            text = str(it or "").strip()
            if not text or text.startswith("#"):
                continue
            set_code, price, qty = "", None, 1
            if "|" in text:
                parts = [p.strip() for p in text.split("|")]
                name = parts[0]
                set_code = (parts[1] if len(parts) > 1 else "").upper()
                price = to_num(parts[2]) if len(parts) > 2 else None
                qty = int(to_num(parts[3]) or 1) if len(parts) > 3 else 1
            else:
                m = _QTY_RX.match(text)
                body = text
                if m:
                    qty, body = int(m.group(1)), m.group(2)
                ms = _SET_PAREN_RX.search(body)
                if ms:
                    set_code = ms.group(1).upper()
                    body = body[:ms.start()] + body[ms.end():]
                mp = re.search(r"(?:[$£R€]\s*)?(\d+(?:[.,]\d{1,2})?)\s*$", body)
                if mp and re.search(r"[A-Za-z]", body[:mp.start()]):
                    price = to_num(mp.group(1))
                    body = body[:mp.start()]
                name = body.strip(" -–,;:")
        name = re.sub(r"\s{2,}", " ", name).strip()
        if not re.search(r"[A-Za-z]", name or ""):
            rejected.append({"line": i + 1, "text": text[:120], "reason": "could not identify — check name/set"})
            continue
        lines.append({"name": name[:120], "set_code": set_code[:8], "user_price": price,
                      "quantity": max(1, min(qty, 999))})
    return lines, rejected


# ── Price history and market (s3.3) ───────────────────────────────────────────
def trend(history: Iterable[tuple[str, float]], days: int = TREND_DAYS) -> Optional[dict]:
    """history: (YYYY-MM-DD, price) rows, any order. Compares the latest price with the earliest price
    inside the last `days`. None with fewer than two points."""
    pts = sorted((str(d)[:10], float(p)) for d, p in history if p is not None and float(p) > 0)
    if len(pts) < 2:
        return None
    last_d, last_p = pts[-1]
    from datetime import date, timedelta
    try:
        cutoff = (date.fromisoformat(last_d) - timedelta(days=days)).isoformat()
    except ValueError:
        return None
    window = [p for p in pts if p[0] >= cutoff]
    if len(window) < 2:
        return None
    first_d, first_p = window[0]
    ch = pct(last_p, first_p)
    word = "rising" if ch > 3 else "falling" if ch < -3 else "flat"
    return {"from_date": first_d, "to_date": last_d, "from": first_p, "to": last_p,
            "change_pct": round(ch, 1), "direction": word, "points": len(window)}


def market_reference(today: Optional[dict], hist_trend: Optional[dict], nm: Optional[dict]) -> Optional[dict]:
    """Combine the three free sources into one market line.
    today = {'usd': float} (card database, today's price, not condition-specific)
    nm    = {'value': float, 'currency': 'USD'} (condition-specific Near Mint price) or None
    The reference used for rules is the Near Mint price when one exists, otherwise today's price
    with `condition_verified=False`. None when there is no price at all (no advice, no charge)."""
    if nm and to_num(nm.get("value")):
        return {"value": float(nm["value"]), "currency": nm.get("currency") or "USD", "basis": "Near Mint price",
                "condition_verified": True, "today": (today or {}).get("usd"), "trend": hist_trend}
    if today and to_num(today.get("usd")):
        return {"value": float(today["usd"]), "currency": "USD", "basis": "today's market price (condition not verified)",
                "condition_verified": False, "today": float(today["usd"]), "trend": hist_trend}
    if hist_trend:
        return {"value": float(hist_trend["to"]), "currency": "USD", "basis": "latest daily price (condition not verified)",
                "condition_verified": False, "today": None, "trend": hist_trend}
    return None


def advise_line(line: dict, kind: str, rules: dict, market: Optional[dict]) -> dict:
    """s3.3 / acceptance 1-2: one advice line per card. status: pass | warn | unverified | unresolved | info.
    A buy line with min_condition NM is NEVER 'pass' unless the market price is condition-verified."""
    name = line.get("name") or "card"
    if not line.get("resolved", True):
        return {"status": "unresolved", "reason": "could not identify — check name/set", "market": None}
    if not market:
        return {"status": "unverified", "reason": "no verified market price today, so no advice (and no charge)", "market": None}
    m = market["value"]; cur = market.get("currency") or "USD"
    up = to_num(line.get("user_price"))
    tr = market.get("trend")
    tr_txt = (" Trend over %d days: %s %+.1f%%." % (TREND_DAYS, tr["direction"], tr["change_pct"])) if tr else ""
    out = {"market": round(m, 2), "currency": cur, "basis": market["basis"], "trend": tr,
           "condition_verified": bool(market.get("condition_verified")), "user_price": up}
    if kind == "sell":
        margin = rules.get("sell_margin_pct")
        if margin is None:
            out.update(status="info", reason="Market %s (%s).%s Set a sell rule (e.g. market +20%%) to get a pass/warn." % (_fmt_money(m, cur), market["basis"], tr_txt))
            return out
        target = m * (1 + margin / 100.0)
        out["target"] = round(target, 2)
        if up is None:
            out.update(status="warn", reason="No price given. Your rule (market +%g%%) points to %s." % (margin, _fmt_money(target, cur)))
        elif up >= target - 1e-9:
            out.update(status="pass", reason="Your %s is %+.0f%% on market %s — meets your +%g%% rule.%s" % (_fmt_money(up, cur), pct(up, m), _fmt_money(m, cur), margin, tr_txt))
        else:
            out.update(status="warn", reason="Your %s is only %+.0f%% on market %s; your rule asks +%g%% (%s).%s" % (_fmt_money(up, cur), pct(up, m), _fmt_money(m, cur), margin, _fmt_money(target, cur), tr_txt))
        return out
    if kind == "buy":
        disc = rules.get("buy_discount_pct")
        need_nm = rules.get("min_condition") == "NM"
        if disc is None:
            out.update(status="info", reason="Market %s (%s).%s Set a buy rule (e.g. market −20%%) to get a pass/warn." % (_fmt_money(m, cur), market["basis"], tr_txt))
            return out
        target = m * (1 - disc / 100.0)
        out["target"] = round(target, 2)
        if need_nm and not market.get("condition_verified"):
            out.update(status="unverified", reason="Your rule needs Near Mint, and today's price for this card is not condition-verified — so it is never marked met. Market %s (condition not verified).%s" % (_fmt_money(m, cur), tr_txt))
            return out
        if up is None:
            out.update(status="warn", reason="No price given. Your rule (market −%g%%) means paying %s or less." % (disc, _fmt_money(target, cur)))
        elif up <= target + 1e-9:
            out.update(status="pass", reason="Paying up to %s is %+.0f%% on market %s — inside your −%g%% rule.%s" % (_fmt_money(up, cur), pct(up, m), _fmt_money(m, cur), disc, tr_txt))
        else:
            out.update(status="warn", reason="Paying %s is %+.0f%% on market %s; your rule asks −%g%% (%s or less).%s" % (_fmt_money(up, cur), pct(up, m), _fmt_money(m, cur), disc, _fmt_money(target, cur), tr_txt))
        return out
    out.update(status="info", reason="Market %s (%s).%s" % (_fmt_money(m, cur), market["basis"], tr_txt))
    return out


def buy_line_met(line: dict, rules: dict, market: Optional[dict], listing_price: Optional[float]) -> bool:
    """Is a LISTING inside a buy line's rule? Same NM guard as advise_line (acceptance 2)."""
    if not market or listing_price is None:
        return False
    if rules.get("min_condition") == "NM" and not market.get("condition_verified"):
        return False
    disc = rules.get("buy_discount_pct")
    if disc is None:
        up = to_num(line.get("user_price"))
        return up is not None and listing_price <= up
    return listing_price <= market["value"] * (1 - disc / 100.0) + 1e-9


def card_name_matches(line_name: str, listing_title: str) -> bool:
    """Whole-name containment on normalised words (identity check for a card line against a listing
    the matcher already returned). 'Lightning Bolt' matches 'Lightning Bolt (M10) NM' but not 'Bolt'."""
    a, b = _norm(line_name), _norm(listing_title)
    if not a or not b:
        return False
    return (" %s " % a) in (" %s " % b)


# ── Property crux report (s3.6 / acceptance 5) ────────────────────────────────
def crux_report(*, asking: Optional[float], currency: str, comps: Optional[dict], rent: Optional[dict] = None,
                epc: Optional[dict] = None, crime: Optional[dict] = None, flood: Optional[dict] = None,
                rate: Optional[dict] = None, rules: Optional[dict] = None) -> Optional[dict]:
    """The bargain report. Returns None -- no report, and so no charge -- unless there is an asking price
    AND verified sold comparables. Every other source is optional and is reported as 'not available'
    rather than guessed."""
    rules = rules or {}
    if not asking or asking <= 0 or not comps or not to_num(comps.get("value")) or int(comps.get("n") or 0) < 5:
        return None
    med = float(comps["value"]); n = int(comps["n"])
    vs = pct(asking, med)
    risks, advs, numbers = [], [], []
    numbers.append({"label": "Asking", "value": _fmt_money(asking, currency)})
    numbers.append({"label": "Sold median nearby", "value": "%s (n=%d)" % (_fmt_money(med, currency), n)})
    numbers.append({"label": "Price vs market", "value": "%+.0f%%" % vs})
    if vs <= -10:
        advs.append("Asking is %.0f%% under the median of %d nearby sales." % (-vs, n))
    elif vs >= 10:
        risks.append("Asking is %.0f%% over the median of %d nearby sales." % (vs, n))
    gy = None
    if rent and to_num(rent.get("value")):
        gy = to_num(rent["value"]) * 12.0 / asking * 100.0
        numbers.append({"label": "Gross yield", "value": "%.1f%%" % gy})
        numbers.append({"label": "Rent used", "value": "%s/month (%s)" % (_fmt_money(to_num(rent["value"]), currency), rent.get("provenance") or "area median")})
        miny = rules.get("min_yield_pct")
        if miny is not None:
            (advs if gy >= miny else risks).append("Gross yield %.1f%% is %s your %.1f%% rule." % (gy, "at or above" if gy >= miny else "under", miny))
    else:
        numbers.append({"label": "Gross yield", "value": "not available (no verified rent)"})
    if epc:
        rating = str(epc.get("rating") or "").upper()[:1]
        if epc.get("floor_area"):
            numbers.append({"label": "Floor area", "value": "%s m²" % epc["floor_area"]})
        if epc.get("age_band"):
            numbers.append({"label": "Age band", "value": str(epc["age_band"])})
        if rating:
            numbers.append({"label": "Energy rating", "value": rating})
            if rating in "ABC":
                advs.append("Energy rating %s — lower running costs and no near-term upgrade duty." % rating)
            elif rating in "EFG":
                risks.append("Energy rating %s — budget for efficiency upgrades before letting." % rating)
    else:
        numbers.append({"label": "Energy certificate", "value": "not available"})
    if crime and crime.get("count") is not None:
        c = int(crime["count"])
        numbers.append({"label": "Street crimes (latest month, ~1 mile)", "value": str(c)})
        if c >= CRIME_HIGH:
            risks.append("%d street-level crimes reported nearby in the latest month." % c)
        elif c <= CRIME_LOW:
            advs.append("Low reported street crime nearby (%d in the latest month)." % c)
    else:
        numbers.append({"label": "Street crime", "value": "not available"})
    if flood is not None and flood.get("in_area") is not None:
        numbers.append({"label": "Flood area", "value": "yes" if flood["in_area"] else "no"})
        if flood["in_area"]:
            risks.append("Inside or beside a mapped flood area (%s)." % (flood.get("label") or "Environment Agency"))
        else:
            advs.append("Not in a mapped flood area.")
    else:
        numbers.append({"label": "Flood area", "value": "not available"})
    if rate and to_num(rate.get("pct")):
        r = to_num(rate["pct"]); loan = asking * 0.75; interest = loan * (r + 2.0) / 100.0
        numbers.append({"label": "Finance line", "value": "%s/yr interest on a 75%% loan at %.2f%% + 2%%" % (_fmt_money(interest, currency), r)})
        if gy is not None:
            rent_y = to_num(rent["value"]) * 12.0
            if interest > rent_y * 0.8:
                risks.append("Interest at today's rate would take %.0f%% of the rent." % (interest / rent_y * 100))
            else:
                advs.append("Rent covers interest at today's rate (%.0f%% of rent)." % (interest / rent_y * 100))
    while len(risks) < 3:
        risks.append("No further risk shown by the data checked.")
    while len(advs) < 3:
        advs.append("No further advantage shown by the data checked.")
    flood_bad = bool(flood and flood.get("in_area"))
    if vs <= -10 and not flood_bad and (gy is None or rules.get("min_yield_pct") is None or gy >= rules["min_yield_pct"]):
        verdict = "Bargain — worth an introduction"
    elif vs >= 10 or flood_bad:
        verdict = "Overpriced or risky — only with a strong reason"
    else:
        verdict = "Fair price — decide on fit, not price"
    return {"asking": asking, "currency": currency, "comps_median": med, "comps_n": n,
            "price_vs_market_pct": round(vs, 1), "gross_yield_pct": (round(gy, 2) if gy is not None else None),
            "numbers": numbers, "risks": risks[:3], "advantages": advs[:3], "verdict": verdict,
            "sources": [comps.get("provenance") or "sold comparables"] + [x.get("provenance") for x in (rent, epc, crime, flood, rate) if x and x.get("provenance")]}


# ── Reality-check (s3.7 / acceptance 6) ───────────────────────────────────────
def reality_check(rules: dict, rows: list[dict], *, days: int = REALITY_DAYS) -> dict:
    """rows: the candidates the matcher returned for this brief over the last `days`. Counts how many met
    the rules; at zero, proposes numbered relaxations with the count each would have produced."""
    met = [r for r in rows if passes_rules(rules, r)[0]]
    out = {"days": days, "seen": len(rows), "met": len(met), "realistic": bool(met), "alternatives": []}
    if met:
        out["line"] = "%d listing%s in the last %d days met your rules." % (len(met), "" if len(met) == 1 else "s", days)
        return out
    if not rows:
        out["line"] = ("Nothing in your reach has matched this brief in the last %d days, at any price. "
                       "Squire keeps watching; widening the area or category is the nearest real change." % days)
        out["alternatives"].append({"n": 1, "change": "widen the area or category", "would_have_matched": 0})
        return out
    alts = []
    prices = sorted(p for p in (to_num(r.get("price_num", r.get("price"))) for r in rows) if p is not None)
    if "max_price" in rules and prices:
        base = dict(rules); base.pop("max_price")
        ok_rows = [r for r in rows if passes_rules(base, r)[0]]
        okp = sorted(p for p in (to_num(r.get("price_num", r.get("price"))) for r in ok_rows) if p is not None)
        if okp:
            new = okp[0]
            alts.append({"rule": "max_price", "from": rules["max_price"], "to": new,
                         "relax_pct": round(pct(new, rules["max_price"]), 1),
                         "change": "raise your maximum price to %s" % _fmt_money(new, rows[0].get("currency")),
                         "would_have_matched": sum(1 for p in okp if p <= new)})
    if "min_yield_pct" in rules:
        base = dict(rules); base.pop("min_yield_pct")
        ys = sorted((y for y in (to_num(r.get("gross_yield_pct")) for r in rows if passes_rules(base, r)[0]) if y is not None), reverse=True)
        if ys:
            new = ys[0]
            alts.append({"rule": "min_yield_pct", "from": rules["min_yield_pct"], "to": round(new, 2),
                         "relax_pct": round(-pct(new, rules["min_yield_pct"]), 1),
                         "change": "accept a gross yield of %.1f%%" % new,
                         "would_have_matched": sum(1 for y in ys if y >= new)})
    if rules.get("exclude_suburbs"):
        base = dict(rules); base.pop("exclude_suburbs")
        n = sum(1 for r in rows if passes_rules(base, r)[0])
        if n:
            alts.append({"rule": "exclude_suburbs", "relax_pct": 100.0, "change": "allow the suburbs you excluded",
                         "would_have_matched": n})
    alts.sort(key=lambda a: (a["relax_pct"], -a["would_have_matched"]))
    for i, a in enumerate(alts, 1):
        a["n"] = i
    out["alternatives"] = alts
    if alts:
        a = alts[0]
        out["line"] = ("None of the %d listings Squire saw in the last %d days met all your rules. Nearest real "
                       "alternative: %s — that would have given %d match%s." % (len(rows), days, a["change"], a["would_have_matched"], "" if a["would_have_matched"] == 1 else "es"))
    else:
        out["line"] = "None of the %d listings in the last %d days met your rules, and no single change would fix it." % (len(rows), days)
    return out


def card_reality(line: dict, rules: dict, market: Optional[dict], listing_prices: list[float]) -> Optional[dict]:
    """Reality-check for one buy line: listings of this card in the window vs the rule's target price."""
    if not market or rules.get("buy_discount_pct") is None:
        return None
    target = market["value"] * (1 - rules["buy_discount_pct"] / 100.0)
    met = [p for p in listing_prices if p <= target]
    if met or not listing_prices:
        return {"met": len(met), "seen": len(listing_prices)}
    best = min(listing_prices)
    need = -pct(best, market["value"])
    return {"met": 0, "seen": len(listing_prices),
            "line": "%s: nothing at −%g%% in %d days; the cheapest was %s (%+.0f%% on market)." % (
                line.get("name"), rules["buy_discount_pct"], REALITY_DAYS, _fmt_money(best, market.get("currency")), -need),
            "alternative": {"n": 1, "change": "buy at market %+.0f%%" % (-need), "would_have_matched": 1}}


# ── Learning (s3.8) ───────────────────────────────────────────────────────────
def apply_feedback(rules: dict, reason: str, row: dict) -> tuple[dict, str]:
    """A thumbs-down reason becomes a stored rule change, shown back to the user."""
    rules = dict(rules or {})
    reason = (reason or "").strip().lower()
    if reason not in _FEEDBACK_REASONS:
        raise ValueError("unknown reason")
    if reason in ("too_far", "not_suburb"):
        sub = str(row.get("suburb") or "").strip()
        d = to_num(row.get("distance_km"))
        if reason == "too_far" and d:
            new = max(1.0, round(d * 0.8, 1))
            rules["max_distance_km"] = min(rules.get("max_distance_km", new), new)
            return rules, "I'll keep within %.0f km from now on." % rules["max_distance_km"]
        if not sub:
            return rules, "Noted — but this listing has no suburb on record, so nothing to exclude."
        ex = set(rules.get("exclude_suburbs", [])); ex.add(sub)
        rules["exclude_suburbs"] = sorted(ex, key=str.lower)
        return rules, "I won't show you %s again." % sub
    if reason == "too_expensive":
        p = to_num(row.get("price_num", row.get("price")))
        if not p:
            return rules, "Noted — this listing has no price on record, so the maximum is unchanged."
        new = round(p * 0.95, 2)
        rules["max_price"] = min(rules.get("max_price", new), new)
        return rules, "Your maximum price is now %s." % _fmt_money(rules["max_price"], row.get("currency"))
    if reason == "wrong_type":
        t = str(row.get("property_type") or row.get("type") or row.get("subcategory") or "").strip()
        if not t:
            return rules, "Noted — this listing has no type on record, so nothing to exclude."
        ex = set(rules.get("exclude_types", [])); ex.add(t)
        rules["exclude_types"] = sorted(ex, key=str.lower)
        return rules, "I won't show you %s listings again." % t
    rules["min_condition"] = "NM"
    return rules, "From now on I only count Near Mint, condition-verified prices."


def feedback_reasons() -> dict:
    return dict(_FEEDBACK_REASONS)


# ── Urgency (s3.9) ────────────────────────────────────────────────────────────
def urgency(kind: str, inside_rules: bool) -> str:
    """'instant' only for a BUY match inside the user's own rules; everything else goes to the digest."""
    return "instant" if (kind == "buy" and inside_rules) else "digest"


# ── Monthly report (s3.10 / acceptance 7) ─────────────────────────────────────
def monthly_report(brief: dict, period: str, *, matches: int, close_calls: list[str], movement: list[str],
                   reality_line: Optional[str]) -> dict:
    """Always produces a report -- a month with zero matches still gets one."""
    lines = []
    lines.append("%d new match%s this month." % (matches, "" if matches == 1 else "es") if matches else
                 "No new matches this month — Squire kept watching.")
    if close_calls:
        lines.append("Close calls (within %d%% of a rule):" % CLOSE_CALL_PCT)
        lines.extend("• " + c for c in close_calls[:10])
    else:
        lines.append("No close calls this month.")
    if movement:
        lines.append("Market movement:")
        lines.extend("• " + m for m in movement[:20])
    else:
        lines.append("Market movement: no verified movement data for this brief this month.")
    if reality_line:
        lines.append("Reality-check: " + reality_line)
    return {"brief_id": brief.get("id"), "period": period, "kind": brief.get("kind") or "buy",
            "category": brief.get("category"), "matches": matches, "close_calls": close_calls[:10],
            "movement": movement[:20], "reality": reality_line, "lines": lines,
            "title": "Squire monthly report — %s — %s" % (brief.get("category") or "brief", period)}


# ── Pro PA quote (s4) ─────────────────────────────────────────────────────────
def pa_quote(feeds: list[str], *, live_feeds: set, feed_costs_usd: dict, sharing: dict,
             ai_usd_month: float, margin_pct: float, usd_per_tuppence: float = 2.0) -> dict:
    """ONE option: a monthly Tuppence figure = feed cost share + AI run cost + margin.
    Raises ValueError (with a plain reason) for anything that cannot be quoted honestly: a feed that is
    not live/pre-approved, or one with no cost set. Rounds UP to whole Tuppence (no fractions, no second
    currency)."""
    feeds = sorted({str(f).strip().lower() for f in (feeds or []) if str(f).strip()})
    if not feeds:
        raise ValueError("Name at least one premium feed to quote.")
    lines, total = [], 0.0
    for f in feeds:
        if f not in live_feeds:
            raise ValueError("%s is not live, so it cannot be quoted." % f)
        cost = feed_costs_usd.get(f)
        if not cost or cost <= 0:
            raise ValueError("%s has no monthly cost set, so it cannot be quoted." % f)
        n = max(1, int(sharing.get(f, 0)) + 1)
        share = cost / n
        lines.append({"feed": f, "cost_usd_month": cost, "shared_by": n, "share_usd": round(share, 2)})
        total += share
    total += max(0.0, ai_usd_month)
    total *= (1 + max(0.0, margin_pct) / 100.0)
    t = max(1, int(math.ceil(total / usd_per_tuppence - 1e-9)))
    return {"feeds": lines, "ai_usd_month": ai_usd_month, "margin_pct": margin_pct,
            "usd_month": round(total, 2), "tuppence_per_month": t, "caution_text": PA_CAUTION_TEXT}
