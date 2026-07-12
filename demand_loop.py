"""
demand_loop.py — DEMAND-LOOP-1 · Piece 1: the Realness Filter
=============================================================
David's spark (6 Jul 2026), design in DEMAND_LOOP_DESIGN.docx.

A buyer searches for something we don't have. Most misses are noise. THIS
module is the gate that decides whether a search-MISS is a *real*, "more-than-
small-change" demand event worth opening a demand ticket for (which later
recruits a matching seller with a coded, anonymity-safe invite).

Design constraints honoured here
--------------------------------
* Deterministic, NO AI  — same ethos as the search engine. Every point of the
  score is explainable; the report prints the reasons.
* NO side effects       — no emails, no writes, no Tuppence. Pure scoring plus
  a strictly READ-ONLY dry-run report over wishlist_signals.
* Env-gated OFF         — demand_loop.json, fail-safe: a missing/broken/empty
  config can only DISABLE the loop, never enable it (mirrors feature_flags.py).
* Import-safe           — no DB access at import time; safe to import anywhere.

The four signals (from DEMAND_LOOP_DESIGN.docx §2)
--------------------------------------------------
1. Structured terms  — specificity: token count, a model year, a model code
   (letters+digits e.g. "320d"), a known high-value brand. "bmw 2015 320d"
   beats "phone".
2. Repeat search     — the same buyer repeating a similar query in the window
   (demonstrated, not idle, demand).
3. Session depth     — an engaged buyer (several searches), not a bouncer.
4. Category price floor — "small change" categories/items never trigger; a
   signal whose known price is below the category floor is hard-suppressed.

Hard gate: it must be a MISS. result_count == 0 is required. A hit (supply
already exists) or an unknown result_count never qualifies.

`qualifies` is decided purely on MERIT (miss + floor + score >= threshold) so
the dry-run report shows what WOULD fire even while the loop is disabled.
`would_act` = qualifies AND config.enabled — the single flip David controls.

CLI:  python3 demand_loop.py --report [--db PATH] [--hours 168] [--limit 50]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import threading
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta, timezone
from typing import Iterable, Optional

_CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         "demand_loop.json")

# ── Fail-safe defaults ────────────────────────────────────────────────────────
# If demand_loop.json is missing/broken these apply, and `enabled` stays False,
# so a broken file can never switch the loop on (feature_flags.py doctrine).
_DEFAULTS: dict = {
    "enabled": False,                 # the ONE flip that lets the loop act
    "score_threshold": 5,             # merit needed to open a demand ticket
    "require_miss": True,             # only result_count == 0 qualifies
    "repeat_window_hours": 72,        # window for repeat / session-depth signals
    "currency": "ZAR",
    "default_price_floor": 500,       # "small change" below this (unknown cat)
    "weights": {
        "tokens_2": 2,                # specificity tiers by meaningful-token count
        "tokens_3": 3,
        "tokens_4plus": 4,
        "has_year": 2,                # a model year (1950-2049)
        "model_code": 2,              # a letters+digits token, e.g. 320d, rx100
        "known_brand": 2,            # a recognised high-value brand token
        "high_value_category": 1,     # cars / property / watches / ...
        "repeat_each": 2,             # per prior similar search by this buyer
        "repeat_cap": 3,              # ... capped at this many
        "depth_each": 1,              # per other search this session
        "depth_cap": 2,
    },
    "high_value_categories": [
        "cars", "property", "watches", "jewellery", "collectables", "art",
    ],
    # Per-category "small change" floor. A signal with a known price below its
    # floor is suppressed. Currency = config.currency (ZAR by default).
    "category_price_floors": {
        "cars": 20000, "property": 150000, "watches": 3000, "jewellery": 2000,
        "art": 1500, "collectables": 250, "electronics": 800, "furniture": 800,
        "appliances": 600, "local_market": 150, "services": 0, "tutors": 0,
        "property_rental": 3000, "other": 500,
    },
    # Recognised high-value brands (lowercase; multi-word matched as substring).
    "known_brands": [
        "bmw", "audi", "mercedes", "merc", "land rover", "landrover", "toyota",
        "vw", "volkswagen", "porsche", "ferrari", "lamborghini", "jaguar",
        "lexus", "tesla", "nissan", "ford", "mazda", "hyundai", "kia", "volvo",
        "isuzu", "mitsubishi", "subaru", "rolex", "omega", "tag heuer", "tudor",
        "cartier", "patek", "audemars", "seiko", "breitling", "pokemon",
        "charizard", "krugerrand", "magic the gathering", "mtg", "lego",
    ],
}

# ── mtime-cached, fail-safe config loader (feature_flags.py pattern) ───────────
_LOCK = threading.Lock()
_CACHE: dict = {"state": None, "mtime": None, "checked": 0.0}
_RECHECK_S = 5.0


def _merged(raw: dict) -> dict:
    """Overlay a (possibly partial) file on defaults; weights merged key-wise."""
    cfg = dict(_DEFAULTS)
    if isinstance(raw, dict):
        for k, v in raw.items():
            if k == "weights" and isinstance(v, dict):
                w = dict(_DEFAULTS["weights"]); w.update(v); cfg["weights"] = w
            else:
                cfg[k] = v
    # enabled must be a real bool; anything odd => False (fail-safe)
    cfg["enabled"] = (cfg.get("enabled") is True)
    return cfg


def load_config(path: Optional[str] = None) -> dict:
    """Return the live config, re-reading the file only when it changes."""
    p = path or _CFG_PATH
    now = time.time()
    with _LOCK:
        if path is None and _CACHE["state"] is not None and \
                (now - _CACHE["checked"]) < _RECHECK_S:
            return _CACHE["state"]
        try:
            mtime = os.path.getmtime(p)
            if path is None and _CACHE["state"] is not None and \
                    mtime == _CACHE["mtime"]:
                _CACHE["checked"] = now
                return _CACHE["state"]
            with open(p, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            state = _merged(raw)
        except Exception:
            state = _merged({})          # fail-safe: defaults, enabled False
            mtime = None
        if path is None:
            _CACHE.update(state=state, mtime=mtime, checked=now)
        return state


# ── Text analysis ─────────────────────────────────────────────────────────────
_STOPWORDS = {
    "the", "a", "an", "for", "sale", "cheap", "need", "want", "wanted",
    "looking", "any", "new", "used", "in", "on", "and", "or", "to", "of",
    "me", "my", "near", "with", "please", "urgent", "second", "hand",
}
_YEAR_RE = re.compile(r"\b(19[5-9]\d|20[0-4]\d)\b")
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_HAS_ALPHA = re.compile(r"[a-z]")
_HAS_DIGIT = re.compile(r"\d")


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", (text or "").lower())).strip()


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall((text or "").lower())


def _meaningful(tokens: Iterable[str]) -> list[str]:
    # keep non-stopword tokens of length >= 2, PLUS bare numbers (bedroom
    # counts, sizes, and other numeric specifics like the '3' in '3 bedroom')
    out: list[str] = []
    for t in tokens:
        if t in _STOPWORDS:
            continue
        if len(t) >= 2 or t.isdigit():
            out.append(t)
    return out


def _is_model_code(tok: str) -> bool:
    # letters+digits in one token, but not a bare model year
    return bool(_HAS_ALPHA.search(tok) and _HAS_DIGIT.search(tok)) and not _YEAR_RE.fullmatch(tok)


def query_similarity(a: str, b: str) -> float:
    """Jaccard overlap of meaningful token sets — used for 'repeat search'."""
    sa, sb = set(_meaningful(_tokens(a))), set(_meaningful(_tokens(b)))
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


# ── The evaluation result ─────────────────────────────────────────────────────
@dataclass
class Evaluation:
    query: str
    category: Optional[str]
    score: int
    threshold: int
    is_miss: bool
    floor_ok: bool
    qualifies: bool          # merit only (miss + floor + score >= threshold)
    would_act: bool          # qualifies AND config.enabled
    enabled: bool
    reasons: list[str] = field(default_factory=list)
    signals: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return asdict(self)


# ── The realness filter ───────────────────────────────────────────────────────
def evaluate(query: str,
             category: Optional[str] = None,
             *,
             result_count: Optional[int] = None,
             price_min: Optional[float] = None,
             price_max: Optional[float] = None,
             repeat_count: int = 0,
             session_depth: int = 0,
             config: Optional[dict] = None) -> Evaluation:
    """Score a single search-miss. Pure: no I/O, no side effects."""
    cfg = config or load_config()
    w = cfg["weights"]
    thr = int(cfg["score_threshold"])
    cat = (category or "").strip().lower() or None
    reasons: list[str] = []

    toks = _tokens(query)
    meaningful = _meaningful(toks)
    n = len(meaningful)

    # ── hard gate 1: must be a confirmed MISS ────────────────────────────────
    is_miss = (result_count == 0)
    if cfg.get("require_miss", True) and not is_miss:
        why = ("result_count unknown — not a confirmed miss"
               if result_count is None else
               f"{result_count} result(s) already exist — supply is present")
        return Evaluation(query, cat, 0, thr, is_miss, True, False, False,
                          cfg["enabled"], [why],
                          {"tokens": n, "result_count": result_count})

    # ── hard gate 2: category price floor ("small change") ───────────────────
    floors = cfg["category_price_floors"]
    floor = floors.get(cat, cfg["default_price_floor"]) if cat else cfg["default_price_floor"]
    known_price = price_max if price_max is not None else price_min
    floor_ok = True
    if known_price is not None and floor and known_price < floor:
        floor_ok = False
        return Evaluation(
            query, cat, 0, thr, is_miss, False, False, False, cfg["enabled"],
            [f"price {known_price:.0f} below {cat or 'default'} floor "
             f"{floor:.0f} {cfg.get('currency', '')} — small change"],
            {"tokens": n, "floor": floor, "known_price": known_price})

    # ── specificity: token-count tier ────────────────────────────────────────
    score = 0
    if n >= 4:
        score += w["tokens_4plus"]; reasons.append(f"{n} specific terms (+{w['tokens_4plus']})")
    elif n == 3:
        score += w["tokens_3"]; reasons.append(f"3 specific terms (+{w['tokens_3']})")
    elif n == 2:
        score += w["tokens_2"]; reasons.append(f"2 specific terms (+{w['tokens_2']})")
    else:
        reasons.append("only 1 meaningful term (+0)")

    # ── specificity: year / model-code / brand ───────────────────────────────
    if _YEAR_RE.search(query or ""):
        score += w["has_year"]; reasons.append(f"model year (+{w['has_year']})")
    if any(_is_model_code(t) for t in meaningful):
        score += w["model_code"]; reasons.append(f"model code (+{w['model_code']})")
    norm = " " + _normalize(query) + " "
    brand_hit = next((b for b in cfg["known_brands"] if (" " + b + " ") in norm), None)
    if brand_hit:
        score += w["known_brand"]; reasons.append(f"brand '{brand_hit}' (+{w['known_brand']})")

    # ── high-value category ──────────────────────────────────────────────────
    if cat and cat in set(cfg["high_value_categories"]):
        score += w["high_value_category"]; reasons.append(f"high-value category (+{w['high_value_category']})")

    # ── repeat search + session depth ────────────────────────────────────────
    if repeat_count > 0:
        r = min(int(repeat_count), int(w["repeat_cap"])) * int(w["repeat_each"])
        score += r; reasons.append(f"repeated {repeat_count}x (+{r})")
    if session_depth > 0:
        d = min(int(session_depth), int(w["depth_cap"])) * int(w["depth_each"])
        score += d; reasons.append(f"session depth {session_depth} (+{d})")

    qualifies = is_miss and floor_ok and score >= thr
    would_act = qualifies and cfg["enabled"]
    if qualifies and not cfg["enabled"]:
        reasons.append("WOULD open a ticket — loop currently OFF (dry-run)")

    return Evaluation(
        query, cat, score, thr, is_miss, floor_ok, qualifies, would_act,
        cfg["enabled"], reasons,
        {"tokens": n, "repeat_count": repeat_count, "session_depth": session_depth,
         "brand": brand_hit, "floor": floor})


# ── History helpers (for the report; pure, list-driven so they're testable) ───
def history_signals(rows: list[dict], buyer_token: str, query: str,
                    window_hours: int, now: Optional[datetime] = None,
                    sim_threshold: float = 0.5) -> tuple[int, int]:
    """From this buyer's prior search rows, return (repeat_count, session_depth).

    repeat_count  = prior searches whose query is similar to `query`
    session_depth = prior distinct searches by the buyer in the window
    """
    now = now or datetime.now(timezone.utc)
    cutoff = now - timedelta(hours=window_hours)
    repeat = depth = 0
    for r in rows:
        if r.get("buyer_token") != buyer_token:
            continue
        ts = _parse_ts(r.get("created_at"))
        if ts is not None and ts < cutoff:
            continue
        depth += 1
        if query_similarity(query, r.get("raw_text") or "") >= sim_threshold:
            repeat += 1
    return repeat, depth


def _parse_ts(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S.%f"):
        try:
            return datetime.strptime(s[:26], fmt).replace(tzinfo=timezone.utc)
        except Exception:
            pass
    return None


def _default_db_path() -> str:
    try:
        import database  # noqa: local module; only defines DB_PATH + helpers
        return getattr(database, "DB_PATH", "/var/www/marketsquare/marketsquare.db")
    except Exception:
        return "/var/www/marketsquare/marketsquare.db"


# ── READ-ONLY dry-run report ──────────────────────────────────────────────────
def run_report(db_path: Optional[str] = None, window_hours: int = 168,
               limit: int = 50) -> int:
    """Score live search-MISSES and print what WOULD open a ticket. No writes."""
    cfg = load_config()
    path = db_path or _default_db_path()
    print("=" * 72)
    print("DEMAND LOOP · realness filter · DRY-RUN report (read-only, $0)")
    print(f"loop enabled: {cfg['enabled']}   threshold: {cfg['score_threshold']}"
          f"   window: {window_hours}h   db: {path}")
    print("=" * 72)
    if not os.path.exists(path):
        print(f"(no database at {path} — nothing to score here. On the server "
              f"this reads the live misses accumulating since Phase 0.)")
        return 0
    try:
        conn = sqlite3.connect(path)
        conn.row_factory = sqlite3.Row
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=window_hours)) \
            .strftime("%Y-%m-%d %H:%M:%S")
        hist = [dict(r) for r in conn.execute(
            "SELECT buyer_token, raw_text, created_at FROM wishlist_signals "
            "WHERE signal_type='browse_search' AND created_at >= ?", (cutoff,))]
        misses = [dict(r) for r in conn.execute(
            "SELECT buyer_token, raw_text, category, price_min, price_max, "
            "created_at FROM wishlist_signals WHERE signal_type='browse_search' "
            "AND result_count = 0 AND created_at >= ? ORDER BY created_at DESC "
            "LIMIT ?", (cutoff, int(limit)))]
    except Exception as e:
        print(f"(could not read wishlist_signals: {e})")
        return 0

    if not misses:
        print("No search-misses in the window yet.")
        return 0

    evals = []
    for m in misses:
        rc, sd = history_signals(hist, m["buyer_token"], m["raw_text"] or "",
                                 int(cfg["repeat_window_hours"]))
        rc = max(0, rc - 1)  # exclude the miss itself from its own repeat count
        sd = max(0, sd - 1)
        evals.append(evaluate(m["raw_text"] or "", m.get("category"),
                              result_count=0, price_min=m.get("price_min"),
                              price_max=m.get("price_max"), repeat_count=rc,
                              session_depth=sd, config=cfg))
    evals.sort(key=lambda e: e.score, reverse=True)
    q = sum(1 for e in evals if e.qualifies)
    for e in evals:
        mark = "✓ TICKET" if e.qualifies else "·       "
        print(f"{mark}  score {e.score:>2}/{e.threshold}  "
              f"[{(e.category or '—')[:12]:<12}]  {e.query[:44]:<44}  "
              f"{'; '.join(e.reasons)}")
    print("-" * 72)
    print(f"{len(evals)} miss(es) scored · {q} WOULD open a ticket · "
          f"loop is {'ON' if cfg['enabled'] else 'OFF (nothing sent)'}")
    return q


def _cli() -> None:
    ap = argparse.ArgumentParser(description="Demand-loop realness filter (dry-run report).")
    ap.add_argument("--report", action="store_true", help="score live misses, print what would fire")
    ap.add_argument("--db", default=None, help="sqlite db path (default: server marketsquare.db)")
    ap.add_argument("--hours", type=int, default=168, help="lookback window (default 168h/7d)")
    ap.add_argument("--limit", type=int, default=50, help="max misses to show")
    args = ap.parse_args()
    if args.report:
        run_report(args.db, args.hours, args.limit)
    else:
        cfg = load_config()
        print(f"demand_loop config: enabled={cfg['enabled']} "
              f"threshold={cfg['score_threshold']} "
              f"floors={len(cfg['category_price_floors'])} cats. "
              f"Use --report to score live misses.")


if __name__ == "__main__":
    _cli()
