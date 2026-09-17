"""zoom_engine.py -- ZOOM, the narrowing funnel. The engine behind GET /zoom/next.

RUL-076 (30 Aug 2026), RUL-089 (tutors lane), RUL-097 (genie = front door, not a second
engine). Build spec: ZOOM_HMI_SPEC.md s3. Ledger: RG-0221.

Pure functions over listing rows (plain dicts). No DB, no HTTP, no app import -- bea_main.py
builds the reach-scoped candidate set (the SAME rows the list shows) and calls next_step().
Because counts and ids come out of ONE call over ONE row set, a facet count and the result
count can never disagree (spec rule 2, acceptance 2).

Engine rules carried here (each was found by BUILDING the prototype, not by design):
  3.1  information gain picks the question (normalised entropy x coverage x weight)
  3.2  a dependency graph keeps it coherent -- a facet is askable only when its `dep`
       parent is answered; dropping a parent drops its children (drop_chip)
  3.3  geography never opens the funnel (x0.18 until a non-geo chip exists, then +0.30) and
       its DEPTH is per category (GEO_LEVELS); a Free buyer's city is never an askable level
  3.4  travel inverts: geography is DESTINATION and starts at COUNTRY
  3.5  arrival at <=24 rows or no question left; relaxation = the one chip whose removal
       returns the most rows
  3.6  singleton auto-collapse: a facet whose EVERY row carries the same single value is
       applied silently (lossless) and shown in the rail, never asked
  rule 2: zero-count options do not exist -- an option is a value some row in the set holds
  rule 4: typing is a shortcut THROUGH the funnel (apply_text) -- it fills chips
  6.1  result order = Ranking Score at listing level, 0.5*quality + 0.5*trust, super_example
       pinned first (SUPER-PIN-1), freshness only as the tiebreak
"""
from __future__ import annotations

import math
import re

ARRIVE_AT = 24          # spec 3.5: the set fits a screen
MAX_OPTIONS = 6         # spec s5: a phone never renders more than 6 options
GEO_SUPPRESS = 0.18     # spec 3.3
GEO_BONUS = 0.30

# ── category normalisation (mirrors the FEA's normCat) ──────────────────────────────────
def norm_cat(raw: str) -> str:
    c = (raw or "").strip().lower()
    if c.startswith("adventure") or c in ("tours", "heritage", "accommodation", "experiences", "guides"):
        return "Travel"
    return {"property": "Property", "cars": "Cars", "tutors": "Tutors", "services": "Services",
            "housekeeping": "Services", "collectors": "Collectors", "collectables": "Collectors",
            "local_market": "Local Market", "local market": "Local Market"}.get(c, "Local Market")

# ── value extractors ────────────────────────────────────────────────────────────────────
def _s(v):
    return str(v).strip() if v not in (None, "") else ""

def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None

_SUBJECT_WORDS = [
    ("Maths", r"\bmaths?\b|mathematic|trig|calculus|algebra"),
    ("Science", r"\bscience\b|physics|chemistry|biology|life science"),
    ("English", r"\benglish\b"), ("Afrikaans", r"afrikaans"),
    ("Chess", r"\bchess\b"), ("Music", r"\bpiano\b|\bguitar\b|\bviolin\b|\bmusic\b|\bsinging\b|\bdrums?\b"),
    ("Coding", r"\bcoding\b|programming|python|computer"),
    ("Accounting", r"accounting|bookkeep"), ("Languages", r"\bfrench\b|\bgerman\b|\bzulu\b|\bspanish\b|\bmandarin\b|isizulu|sepedi|setswana"),
    ("Sport", r"\bswim|\btennis\b|\bgolf\b|\bcricket\b|\brugby\b|\bsoccer\b|\byoga\b|\bfitness\b|\bcoach\b"),
    ("Driving", r"\bdriving\b|\bk53\b"), ("Exam prep", r"matric|exam prep|\bieb\b|\bcaps\b"),
]
def _subject(r):
    v = _s(r.get("subject"))
    if v:
        return v
    t = (_s(r.get("title")) + " " + _s(r.get("description"))[:400]).lower()
    for label, rx in _SUBJECT_WORDS:
        if re.search(rx, t):
            return label
    return ""

def _mode(r):
    m = _s(r.get("mode")).lower()
    if not m:
        return ""
    if "online" in m and ("person" in m or "both" in m):
        return "Online or in person"
    if "online" in m:
        return "Online"
    return "In person"

def _prop_mode(r):
    lt = _s(r.get("listing_type")).lower()
    if lt:
        return "Rent" if re.search(r"rent|let", lt) else "Buy"
    d = (_s(r.get("description")) + " " + _s(r.get("price"))).lower()
    if re.search(r"for rent|per month|/month|/mo\b|to let|rental", d):
        return "Rent"
    if re.search(r"for sale|asking price|selling", d):
        return "Buy"
    return ""

_PROP_TYPE_MAP = {"apartment / flat": "Apartment", "flat": "Apartment", "apartment": "Apartment",
                  "bachelor / studio": "Studio", "vacant land": "Land / Plot", "land / plot": "Land / Plot"}
def _prop_type(r):
    v = _s(r.get("prop_type"))
    return _PROP_TYPE_MAP.get(v.lower(), v) if v else ""

def _beds(r):
    n = _num(r.get("beds"))
    if not n or n <= 0:
        return ""
    n = int(n)
    return "4+" if n >= 4 else str(n)

def _pets(r):
    m = re.search(r"pets?:\s*(yes|no|negotiable)", _s(r.get("description")), re.I)
    return m.group(1).capitalize() if m else ""

def _year_band(r):
    y = _num(r.get("vehicle_year"))
    if not y:
        return ""
    y = int(y)
    return "2020 or newer" if y >= 2020 else "2015-2019" if y >= 2015 else "2010-2014" if y >= 2010 else "Before 2010"

def _mileage_band(r):
    k = _num(r.get("mileage_km"))
    if k is None:
        return ""
    return "Under 50 000 km" if k < 50000 else "50-100 000 km" if k < 100000 else "100-150 000 km" if k < 150000 else "Over 150 000 km"

def _car_condition(r):
    k = _num(r.get("mileage_km"))
    c = _s(r.get("condition")).lower()
    if c in ("new", "demo"):
        return "New / demo"
    if k is not None:
        return "New / demo" if k < 500 else "Used"
    return ""

def _era_band(r):
    y = _num(r.get("era_year"))
    if not y:
        return ""
    return "Pre-1900" if y < 1900 else "1900-1950" if y <= 1950 else "1950-2000" if y <= 2000 else "Post-2000"

def _collect_condition(r):
    v = _s(r.get("ai_grade")) or _s(r.get("condition"))
    return v

def _collect_line(r):
    # the LINE inside a family: the catalogue title a matcher stamped (numista / scryfall), else nothing
    return _s(r.get("numista_title")) or _s(r.get("set_name")) or ""

def _travel_lane(r):
    c = (_s(r.get("category"))).lower()
    if "accommodation" in c or c in ("stays", "accommodation"):
        return "Stays"
    if "guide" in c:
        return "Guides"
    return "Tours"

_TOUR_TYPE_WORDS = [("Safari / wildlife", r"safari|game drive|big five|wildlife|lion|elephant|rhino|bison|elk"),
                    ("Walking / hiking", r"\bhik|\bwalk|trail|trek"), ("Water", r"\bdiv|snorkel|reef|kayak|boat|whale|coral|turtle"),
                    ("Heritage / culture", r"heritage|history|histor|museum|castle|village|culture|stone|avebury"),
                    ("Rail / road", r"\brail|\btrain|road trip|drive"), ("Food & wine", r"\bwine|\bfood|culinary|dinner")]
def _tour_type(r):
    t = (_s(r.get("title")) + " " + _s(r.get("description"))[:500]).lower()
    for label, rx in _TOUR_TYPE_WORDS:
        if re.search(rx, t):
            return label
    return ""

def _duration(r):
    t = (_s(r.get("title")) + " " + _s(r.get("description"))[:500]).lower()
    if re.search(r"half[- ]day|\b[2-5] ?hours?\b|\bhours\b", t):
        return "Half day"
    if re.search(r"full[- ]day|\b1 day\b|\bday tour\b|\bday trip\b", t):
        return "Full day"
    m = re.search(r"\b(\d+)[- ]?(days?|nights?)\b", t)
    if m:
        n = int(m.group(1))
        return "2-3 days" if n <= 3 else "4-7 days" if n <= 7 else "Over a week"
    return ""

def _stay_kind(r):
    t = (_s(r.get("title")) + " " + _s(r.get("description"))[:300]).lower()
    for label, rx in [("Lodge / camp", r"lodge|camp|tent|safari"), ("Guesthouse / B&B", r"guest ?house|b&b|bed and breakfast"),
                      ("Self-catering", r"self[- ]catering|cottage|villa|apartment"), ("Hotel", r"hotel|inn\b|resort")]:
        if re.search(rx, t):
            return label
    return ""

def _sleeps(r):
    t = (_s(r.get("title")) + " " + _s(r.get("description"))[:400]).lower()
    m = re.search(r"sleeps?\s*(\d+)|(\d+)\s*(?:guests|people|persons)", t)
    if not m:
        return ""
    n = int(m.group(1) or m.group(2))
    return "1-2" if n <= 2 else "3-4" if n <= 4 else "5+"

def _price_band_factory(rows):
    """Dynamic budget bands for THIS set (nice numbers, 2-4 bands). Returns (fn, options)."""
    vals = sorted(v for v in (_num(r.get("price_num")) for r in rows) if v and v > 0)
    if len(vals) < 2 or vals[0] == vals[-1]:
        return (lambda r: ""), []
    def nice(x):
        if x <= 0:
            return 0
        mag = 10 ** int(math.floor(math.log10(x)))
        for m in (1, 2, 2.5, 5, 10):
            if m * mag >= x:
                return m * mag
        return 10 * mag
    n = len(vals)
    cuts = []
    for q in (0.33, 0.66):
        c = nice(vals[min(n - 1, int(n * q))])
        if c and (not cuts or c > cuts[-1]) and c > vals[0]:
            cuts.append(c)
    if not cuts:
        return (lambda r: ""), []
    def fmt(v):
        v = int(v)
        return ("%s" % f"{v:,}").replace(",", " ")
    labels = []
    prev = None
    for c in cuts:
        labels.append(("Under %s" % fmt(c)) if prev is None else ("%s - %s" % (fmt(prev), fmt(c))))
        prev = c
    labels.append("Over %s" % fmt(prev))
    def fn(r):
        v = _num(r.get("price_num"))
        if not v or v <= 0:
            return ""
        for i, c in enumerate(cuts):
            if v < c:
                return labels[i]
        return labels[-1]
    return fn, labels

# ── the facet map (spec s4 + s10) ───────────────────────────────────────────────────────
# Each facet: id, question, extractor, weight, dep, depVal. Order is NOT the ask order --
# information gain orders them; the graph only forbids incoherent orders.
def _F(fid, question, fn, weight=1.0, dep=None, dep_val=None):
    return {"id": fid, "q": question, "fn": fn, "w": weight, "dep": dep, "dep_val": dep_val}

def facets_for(cat: str):
    if cat == "Property":
        return [_F("mode", "Renting or buying?", _prop_mode, 1.5),
                _F("prop_type", "What kind of place?", _prop_type, 1.0),
                _F("beds", "How many bedrooms?", _beds, 1.0, dep="mode"),
                _F("budget", "What is your budget?", None, 0.9, dep="mode"),
                _F("pets", "Pets?", _pets, 0.5, dep="mode")]
    if cat == "Services":
        return [_F("service_class", "What kind of work?", lambda r: _s(r.get("service_class")), 1.4),
                _F("service_type", "Which trade?", lambda r: _s(r.get("service_type")), 1.1, dep="service_class"),
                _F("availability", "When do you need it?", lambda r: _s(r.get("availability")), 0.7),
                _F("budget", "What rate suits you?", None, 0.7)]
    if cat == "Tutors":
        return [_F("subject", "What subject?", _subject, 1.4),
                _F("level", "What level?", lambda r: _s(r.get("level")), 1.0, dep="subject"),
                _F("mode", "Online or in person?", _mode, 0.8),
                _F("near_institution", "Near which school?", lambda r: _s(r.get("near_institution")), 1.0),
                _F("budget", "What rate suits you?", None, 0.7)]
    if cat == "Collectors":
        return [_F("family", "What do you collect?", lambda r: _s(r.get("collectible_type")), 1.5),
                _F("line", "Which line?", _collect_line, 1.1, dep="family"),
                _F("condition", "What condition?", _collect_condition, 0.8, dep="family"),
                _F("era", "Which era?", _era_band, 0.8, dep="family"),
                _F("budget", "What is your budget?", None, 0.8)]
    if cat == "Cars":
        return [_F("make", "Which make?", lambda r: _s(r.get("make")), 1.5),
                _F("model", "Which model?", lambda r: _s(r.get("model")), 1.2, dep="make"),
                _F("car_condition", "New or used?", _car_condition, 0.9),
                _F("year", "How old?", _year_band, 0.9),
                _F("mileage", "How many kilometres?", _mileage_band, 0.9, dep="car_condition", dep_val="Used"),
                _F("transmission", "Manual or automatic?", lambda r: _s(r.get("transmission")), 0.7),
                _F("fuel", "Petrol or diesel?", lambda r: _s(r.get("fuel_type")), 0.6),
                _F("body", "What body?", lambda r: _s(r.get("body_type")), 0.7),
                _F("budget", "What is your budget?", None, 0.9)]
    if cat == "Travel":
        return [_F("lane", "What are you after?", _travel_lane, 1.6),
                _F("tour_type", "What kind of tour?", _tour_type, 1.1, dep="lane", dep_val="Tours"),
                _F("duration", "How long?", _duration, 0.9, dep="lane", dep_val="Tours"),
                _F("stay_kind", "What kind of place?", _stay_kind, 1.1, dep="lane", dep_val="Stays"),
                _F("sleeps", "How many people?", _sleeps, 0.9, dep="lane", dep_val="Stays"),
                _F("expertise", "A guide for what?", _tour_type, 1.1, dep="lane", dep_val="Guides"),
                _F("budget", "What is your budget?", None, 0.8, dep="lane")]
    # Local Market and anything unmapped: the universal facets only
    return [_F("condition", "New or used?", lambda r: _s(r.get("condition")), 0.9),
            _F("budget", "What is your budget?", None, 1.0)]

# spec 3.3 table: levels a category may ask, in order. The first level is where the chip
# STARTS (already known for non-travel: the buyer's city).
GEO_LEVELS = {
    "Property":     ["city", "suburb", "street"],
    "Services":     ["city", "suburb", "street"],
    "Tutors":       ["city", "suburb"],
    "Cars":         ["city", "suburb"],
    "Collectors":   ["city"],            # never asked below city
    "Local Market": ["city", "suburb"],
    "Travel":       ["country", "city", "suburb"],   # destination: country first
}
GEO_QUESTION = {"country": "Which country?", "city": "Which city or region?",
                "suburb": "Which part of town?", "street": "Which street?"}
GEO_COL = {"country": "country", "city": "city", "suburb": "suburb", "street": "street_address"}

def _geo_value(r, level):
    v = _s(r.get(GEO_COL[level]))
    if level == "country":
        return v.upper() if v else ""
    if level == "street" and v:
        v = re.sub(r"^\s*\d+[a-z]?\s+", "", v, flags=re.I)   # drop the house number: a street, not a door
    return v

def geo_facets(cat: str, tier: str):
    """Geo levels as dep-chained facets. Non-travel: the city level is applied by the
    candidate set (the buyer's city) so the chain starts at suburb; a GLOBAL buyer gets city
    as an askable level (spec 6.2 rule 2). Travel: country opens it (3.4)."""
    levels = GEO_LEVELS.get(cat, ["city", "suburb"])
    out, prev = [], None
    for lv in levels:
        if cat != "Travel" and lv == "city" and tier != "global":
            prev = None          # city is known, not askable -- the chain starts below it
            continue
        if cat == "Collectors" and lv != "city":
            continue
        out.append({"id": "geo_" + lv, "q": GEO_QUESTION[lv], "fn": (lambda r, _lv=lv: _geo_value(r, _lv)),
                    "w": 1.0, "dep": prev, "dep_val": None, "geo": True, "level": lv})
        prev = "geo_" + lv
    if cat == "Collectors" and tier != "global":
        return []                # a Free collector's city is known and never asked below
    return out

# ── the engine ──────────────────────────────────────────────────────────────────────────
def _entropy(counts):
    n = float(sum(counts))
    if n <= 0:
        return 0.0
    return -sum((c / n) * math.log(c / n) for c in counts if c)

def _matches(r, facet, value):
    return facet["fn"](r) == value

def _apply(rows, facets_by_id, chosen):
    out = rows
    for fid, val in chosen.items():
        f = facets_by_id.get(fid)
        if not f:
            continue
        out = [r for r in out if _matches(r, f, val)]
    return out

def drop_chip(chosen: dict, facets_by_id: dict, fid: str) -> dict:
    """Spec 3.2: dropping a parent drops its children (transitively)."""
    gone = {fid}
    changed = True
    while changed:
        changed = False
        for k in list(chosen):
            f = facets_by_id.get(k)
            if k not in gone and f and f.get("dep") in gone:
                gone.add(k); changed = True
    return {k: v for k, v in chosen.items() if k not in gone}

def rank_score(r, quality_fn=None):
    """6.1: 0.5 x listing quality + 0.5 x seller trust -- the same straight 50/50 as
    estate_agents._rank_agents. Quality from the stored column when present."""
    q = _num(r.get("quality_score"))
    if q is None and quality_fn:
        try:
            q = float(quality_fn(r))
        except Exception:
            q = None
    if q is None:
        q = 0.0
    t = _num(r.get("trust_score")) or 0.0
    return round(0.5 * min(100.0, q) + 0.5 * min(100.0, t), 1)

def order_results(rows, quality_fn=None):
    def key(r):
        pinned = 1 if (_num(r.get("super_example")) and not _num(r.get("showcase"))) else 0
        return (-pinned, -rank_score(r, quality_fn), -(_num(r.get("id")) or 0))
    return sorted(rows, key=key)

def next_step(rows, cat, chosen, tier="free", locked_geo=None, quality_fn=None, text=None):
    """One call answers everything the sheet needs for the current state.

    rows       -- the reach-scoped candidate set (already city-scoped for a Free buyer)
    cat        -- normalised category ('Property', ..., 'Travel')
    chosen     -- {facet_id: value} the user's chips (plus auto chips)
    tier       -- 'free' | 'global' (RUL-078: Pro resolves to global upstream)
    locked_geo -- [{'v': city, 'n': count}] out-of-reach geography with TRUE counts (6.2)
    text       -- typed shortcut (rule 4): fills chips, leftover words filter the set
    """
    base = facets_for(cat)
    fset = {"budget"}
    facets = [f for f in base if f["id"] not in fset]
    geo = geo_facets(cat, tier)
    all_f = facets + geo + [f for f in base if f["id"] in fset]
    by_id = {f["id"]: f for f in all_f}

    chosen = {k: v for k, v in (chosen or {}).items() if k in by_id}
    # dependency integrity on the way in: a child whose parent is missing is dropped
    for k in list(chosen):
        f = by_id[k]
        if f.get("dep") and f["dep"] not in chosen:
            chosen = drop_chip(chosen, by_id, k)
        elif f.get("dep_val") and chosen.get(f["dep"]) != f["dep_val"]:
            chosen = drop_chip(chosen, by_id, k)

    # budget bands are computed from the set BEFORE budget is applied (the labels must exist
    # for the chosen value to match), then re-bound to the remaining set for the question
    budget = by_id.get("budget")
    pre = _apply(rows, {k: v for k, v in by_id.items() if k != "budget"}, {k: v for k, v in chosen.items() if k != "budget"})
    if budget:
        bfn, blabels = _price_band_factory(pre if "budget" not in chosen else rows)
        budget["fn"] = bfn
    applied_text = []
    leftover = []
    if text:
        chosen, applied_text, leftover = apply_text(pre, all_f, by_id, chosen, text)
        pre = _apply(rows, {k: v for k, v in by_id.items() if k != "budget"}, {k: v for k, v in chosen.items() if k != "budget"})
        if budget and "budget" not in chosen:
            budget["fn"], _ = _price_band_factory(pre)
    remaining = _apply(rows, by_id, chosen)
    if leftover:
        toks = [t for t in leftover if len(t) >= 2]
        remaining = [r for r in remaining if all(t in (_s(r.get("title")) + " " + _s(r.get("description"))).lower() for t in toks)]
    if budget and "budget" not in chosen:
        budget["fn"], _ = _price_band_factory(remaining)

    # 3.6 singleton auto-collapse -- lossless only: every remaining row holds the one value
    auto = []
    changed = True
    while changed and remaining:
        changed = False
        for f in all_f:
            if f["id"] in chosen or not _askable(f, chosen):
                continue
            vals = {f["fn"](r) for r in remaining}
            if len(vals) == 1 and "" not in vals:
                v = vals.pop()
                chosen[f["id"]] = v
                auto.append({"facet": f["id"], "v": v, "label": _chip_label(f, v)})
                changed = True

    non_geo_chosen = any(not by_id[k].get("geo") for k in chosen)
    scored = []
    for f in all_f:
        if f["id"] in chosen or not _askable(f, chosen):
            continue
        counts = {}
        for r in remaining:
            v = f["fn"](r)
            if v:
                counts[v] = counts.get(v, 0) + 1
        if not counts:
            continue
        k = len(counts)
        if k < 2:
            continue
        cover = sum(counts.values()) / float(len(remaining))
        h = _entropy(list(counts.values())) / math.log(k)
        w = f["w"]
        if f.get("geo"):
            w = w * GEO_SUPPRESS if not non_geo_chosen else w + GEO_BONUS
        score = h * cover * w
        scored.append((score, f, counts))
    scored.sort(key=lambda x: -x[0])

    total = len(remaining)
    question = None
    arrived = total <= ARRIVE_AT or not scored
    if scored:
        score, f, counts = scored[0]
        opts = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
        question = {"facet": f["id"], "q": f["q"], "geo": bool(f.get("geo")), "level": f.get("level"),
                    "options": [{"v": v, "label": _chip_label(f, v), "n": n} for v, n in opts[:MAX_OPTIONS]],
                    "tail": [{"v": v, "label": _chip_label(f, v), "n": n} for v, n in opts[MAX_OPTIONS:]],
                    "gain": round(score, 3)}
        if f.get("geo") and locked_geo:
            # 6.2 rule 3: out-of-reach is NOT zero-count -- shown with its true count and a lock
            question["locked"] = [{"v": g["v"], "label": g["v"], "n": g["n"], "locked": True}
                                  for g in locked_geo if g.get("n")]
    # queue = what would be asked next, so the client can show "keep narrowing" after arrival
    queue = [{"facet": f["id"], "q": f["q"]} for _, f, _ in scored[1:4]]

    relax = None
    if total < 3 and chosen:
        best = None
        for k in list(chosen):
            if any(a["facet"] == k for a in auto):
                continue
            trial = drop_chip(chosen, by_id, k)
            n = len(_apply(rows, by_id, trial))
            if n > total and (best is None or n > best[1]):
                best = (k, n)
        if best:
            relax = {"facet": best[0], "label": _chip_label(by_id[best[0]], chosen[best[0]]), "n": best[1]}

    ordered = order_results(remaining, quality_fn)
    chips = [{"facet": k, "v": v, "label": _chip_label(by_id[k], v), "geo": bool(by_id[k].get("geo")),
              "level": by_id[k].get("level"), "auto": any(a["facet"] == k for a in auto)} for k, v in chosen.items()]
    return {"total": total, "chips": chips, "auto": auto, "question": question, "queue": queue,
            "arrived": arrived, "relax": relax, "tier": tier,
            "ids": [r.get("id") for r in ordered], "scores": {str(r.get("id")): rank_score(r, quality_fn) for r in ordered},
            "text_applied": applied_text, "text_leftover": leftover}

def _askable(f, chosen):
    if f.get("dep"):
        if f["dep"] not in chosen:
            return False
        if f.get("dep_val") and chosen.get(f["dep"]) != f["dep_val"]:
            return False
    return True

def _chip_label(f, v):
    return str(v)

_STOP = {"and", "the", "for", "with", "per", "any", "all", "not", "your", "you", "our", "one"}

def apply_text(rows, all_f, by_id, chosen, text):
    """Rule 4: typing fills chips. Walk facets in dependency order; a word or phrase that
    equals / contains an option label of a facet the set still offers becomes that chip."""
    chosen = dict(chosen)
    t = " " + re.sub(r"\s+", " ", (text or "").strip().lower()) + " "
    applied = []
    changed = True
    guard = 0
    while changed and guard < 12:
        changed = False; guard += 1
        remaining = _apply(rows, by_id, chosen)
        for f in all_f:
            if f["id"] in chosen or not _askable(f, chosen):
                continue
            vals = {}
            for r in remaining:
                v = f["fn"](r)
                if v:
                    vals[v] = vals.get(v, 0) + 1
            hit = None; hit_score = 0.0; hit_toks = []
            ttoks = set(re.findall(r"[a-z0-9]+", t))
            for v in sorted(vals, key=lambda x: (-vals[x], -len(str(x)))):
                lv = " " + str(v).lower() + " "
                if len(str(v)) >= 2 and lv in t:
                    hit = v; hit_score = 2.0; hit_toks = re.findall(r"[a-z0-9]+", lv); break
                # partial: the label's meaningful tokens, at least half of them typed, one >= 4 chars
                ltoks = [w for w in re.findall(r"[a-z0-9]+", str(v).lower()) if w not in _STOP and len(w) >= 3]
                if not ltoks:
                    continue
                got = [w for w in ltoks if w in ttoks]
                if got and len(got) / float(len(ltoks)) >= 0.5 and any(len(w) >= 4 for w in got):
                    sc = len(got) / float(len(ltoks))
                    if sc > hit_score:
                        hit, hit_score, hit_toks = v, sc, got
            if hit is not None:
                chosen[f["id"]] = hit
                applied.append({"facet": f["id"], "v": hit})
                for w in hit_toks:
                    t = re.sub(r"\b%s\b" % re.escape(w), " ", t)
                t = re.sub(r"\s+", " ", t)
                changed = True
                break
    leftover = [w for w in t.split() if w]
    return chosen, applied, leftover
