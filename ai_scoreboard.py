#!/usr/bin/env python3
"""
ai_scoreboard.py — the silent scoreboard agent (SCOREBOARD-1, 3 Aug 2026).

David's ruling (24 Jul session, design layer agreed): the BREAKER handles the FAST
signals (an outage or 429 is answered per-call, in seconds). This module handles the
SLOW signals: every night it probes EVERY configured lane x task tier through the seam's
direct probe mode, keeps the history, and computes a rolling (default 90-day) ranking of
uptime, latency and cost per capability — the table that first RECOMMENDS and, once
trusted, becomes the flip DETERMINANT.

Design rules (inherited, binding):
- QUALITY IS A GATE, NOT A WEIGHT. A lane with no golden-set pass on record can never
  rank eligible, no matter how cheap/fast/available it probes. Probes prove transport,
  auth and model liveness; QUALITY remains the golden-set eval's job (P2 design §6).
- Probes go through ai_provider.complete(probe=True): direct, no fallback, so the
  outcome is unambiguously the target's (Peer blocker #3), and the breaker sees the
  probe result through its own record() hook — one truth, two consumers.
- 'unconfigured' is configuration, not an outage (P2 design §3): recorded for the
  DISABLED display, excluded from availability maths, never alarms.
- Spend is bounded by design: 3 lanes x 4 tasks x ~60 max_tokens nightly ≈ well under
  one US cent. The enable flag (launch_switches.scoreboard_enabled) defaults OFF —
  turning probes on is David's explicit click (enable_scoreboard.bat), the same
  key-stays-with-David pattern as add_openai_key.bat (RG-0016 spirit).

CLI (run from the project/server folder):
    python3 ai_scoreboard.py --probe            # one probe round now (respects flag)
    python3 ai_scoreboard.py --probe --force    # one round, ignore the enable flag (attended test)
    python3 ai_scoreboard.py --report           # print the rolling ranking table
    python3 ai_scoreboard.py --report --json ai_scoreboard.json
    python3 ai_scoreboard.py --window 30 --report

Nightly wiring: bea_main.py runs run_nightly() from its startup loop (SCOREBOARD-1
wiring); standalone cron works identically. All state lives in the primary DB, so the
history rides the existing backup lanes for free.
"""
import os, sys, json, time, sqlite3, argparse
from datetime import datetime, timedelta, timezone

from ai_provider import complete, TASK_MODEL, ADAPTERS

TASKS = ("haiku", "sonnet", "vision", "triage")
MIN_SAMPLES = 5            # below this a lane shows INSUFFICIENT DATA, never a rank
DEFAULT_WINDOW_DAYS = 90   # David's 3-month history window
PROBE_MAX_TOKENS = 60

# --- probe prompts: tiny, fixed, deterministic-ish; sanity regex proves the reply is
# --- non-degenerate. Sanity is a liveness check, NOT quality (quality = golden set).
_PNG_1x1_RED = ("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4"
                "2mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==")
PROBES = {
    "haiku":  {"messages": [{"role": "user", "content": "Reply with exactly: OK"}],
               "sanity": lambda t: "ok" in t.lower()},
    "sonnet": {"messages": [{"role": "user", "content": "What is 7+5? Reply with the number only."}],
               "sanity": lambda t: "12" in t},
    "triage": {"messages": [{"role": "user", "content":
               "Classify the sentiment of this review as GOOD or BAD, one word only: 'excellent service, highly recommended'"}],
               "sanity": lambda t: "good" in t.lower()},
    "vision": {"messages": [{"role": "user", "content": [
                   {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                                                "data": _PNG_1x1_RED}},
                   {"type": "text", "text": "Reply with one word: is this image mostly red, green or blue?"}]}],
               "sanity": lambda t: "red" in t.lower()},
}

# --- price table: $/Mtok (input, output). Loaded from ai_price_card.json when present
# --- (the maintained source, 1 Aug 2026); the embedded fallback covers a fresh box.
# --- Fallback sources: OpenAI verified 31 Jul vs vendor docs (seam comment); Anthropic
# --- published list; Scaleway mistral-medium marked APPROX — the price card corrects it.
FALLBACK_PRICE = {
    ("anthropic", "claude-haiku-4-5-20251001"): (1.00, 5.00),
    ("anthropic", "claude-sonnet-4-6"):         (3.00, 15.00),
    ("openai",    "gpt-5.6-luna"):              (0.20, 1.20),
    ("openai",    "gpt-5.6-terra"):             (2.00, 12.00),
    ("scaleway",  "mistral-medium-3.5-128b"):   (0.40, 2.00),   # APPROX until price card read
}
# typical production call shape used for the cost-per-call ranking metric
TYPICAL_IN_TOK, TYPICAL_OUT_TOK = 400, 300

# --- quality gate registry: golden-set passes on record. A lane absent here is GATED.
# --- Overridable/extendable via golden_pass.json next to the DB (written when a new
# --- golden run passes) so a new pass never needs a code change.
GOLDEN_PASS = {
    "anthropic": "production baseline (incumbent lane)",
    "scaleway":  "golden set 18 Jul 2026 — 7/7 text, 2/2 vision (ONE-MODEL STANDBY)",
    # "openai": absent by design — GS-OAI-V1 ran on the sandbox key; the production
    # gate needs the server-key golden run (RG-0016). Add via golden_pass.json.
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS ai_scoreboard_probes (
  ts TEXT NOT NULL,              -- ISO UTC
  provider TEXT NOT NULL,
  task TEXT NOT NULL,
  ok INTEGER NOT NULL,           -- transport+auth+model liveness (AIResult.ok)
  sane INTEGER,                  -- reply passed the sanity regex (NULL if not ok)
  error_kind TEXT,               -- seam taxonomy; '' on success
  latency_ms INTEGER,
  in_tokens INTEGER, out_tokens INTEGER,
  est_cost_usd REAL
);
CREATE INDEX IF NOT EXISTS idx_sb_ptt ON ai_scoreboard_probes (provider, task, ts);
"""


def db_path():
    p = os.environ.get("MS_DB")
    if p:
        return p
    for cand in ("/var/www/marketsquare/marketsquare.db", "marketsquare.db"):
        if os.path.exists(cand):
            return cand
    return "marketsquare.db"


def _connect(path=None):
    conn = sqlite3.connect(path or db_path())
    conn.executescript(SCHEMA)
    return conn


def is_enabled(conn):
    """launch_switches.scoreboard_enabled — defaults OFF (spend is David's click).
    launch_switches is the SINGLETON WIDE table (id=1, one column per switch — same
    shape ai_active uses); a missing column or table simply means OFF."""
    try:
        row = conn.execute(
            "SELECT scoreboard_enabled FROM launch_switches WHERE id=1").fetchone()
        return bool(row) and str(row[0]).strip() in ("1", "true", "on", "yes")
    except sqlite3.OperationalError:
        return False   # column/table not there yet (dev box or pre-enable) -> stay off


def _price(provider, model):
    card = _load_price_card()
    key = f"{provider}:{model}"
    if key in card:
        return card[key]
    return FALLBACK_PRICE.get((provider, model), (1.00, 5.00))  # conservative default


_PRICE_CARD_CACHE = None
def _load_price_card():
    """ai_price_card.json (maintained 1 Aug 2026) -> {'provider:model': (in,out)}.
    Tolerant of shape: accepts {'provider:model': {'in': x, 'out': y}} or nested
    {'provider': {'model': {'input_usd_mtok': x, 'output_usd_mtok': y}}}."""
    global _PRICE_CARD_CACHE
    if _PRICE_CARD_CACHE is not None:
        return _PRICE_CARD_CACHE
    out = {}
    for cand in (os.path.join(os.path.dirname(db_path()), "ai_price_card.json"),
                 "ai_price_card.json"):
        try:
            with open(cand, encoding="utf-8") as f:
                raw = json.load(f)
            for k, v in raw.items():
                if isinstance(v, dict) and ("in" in v or "input_usd_mtok" in v):
                    out[k] = (float(v.get("in", v.get("input_usd_mtok"))),
                              float(v.get("out", v.get("output_usd_mtok"))))
                elif isinstance(v, dict):
                    for m, pv in v.items():
                        if isinstance(pv, dict) and ("in" in pv or "input_usd_mtok" in pv):
                            out[f"{k}:{m}"] = (float(pv.get("in", pv.get("input_usd_mtok"))),
                                               float(pv.get("out", pv.get("output_usd_mtok"))))
            break
        except Exception:
            continue
    _PRICE_CARD_CACHE = out
    return out


def golden_gate(provider):
    """Quality gate: golden-set pass on record? File overrides/extends the registry."""
    merged = dict(GOLDEN_PASS)
    for cand in (os.path.join(os.path.dirname(db_path()), "golden_pass.json"),
                 "golden_pass.json"):
        try:
            with open(cand, encoding="utf-8") as f:
                merged.update(json.load(f))
            break
        except Exception:
            continue
    note = merged.get(provider)
    return (note is not None and note is not False), note


def probe_once(provider, task, timeout=45):
    """One direct probe through the seam. Returns the row dict (not yet stored)."""
    spec = PROBES[task]
    t0 = time.perf_counter()
    r = complete(spec["messages"], task=task, max_tokens=PROBE_MAX_TOKENS,
                 provider=provider, timeout=timeout, probe=True)
    ms = int((time.perf_counter() - t0) * 1000)
    sane = None
    if r.ok:
        sane = 1 if spec["sanity"](r.text or "") else 0
    pin, pout = _price(provider, TASK_MODEL.get(provider, {}).get(task, ""))
    cost = ((r.in_tokens or 0) * pin + (r.out_tokens or 0) * pout) / 1e6 if r.ok else 0.0
    return {"ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "provider": provider, "task": task, "ok": 1 if r.ok else 0, "sane": sane,
            "error_kind": r.error_kind or "", "latency_ms": ms,
            "in_tokens": r.in_tokens or 0, "out_tokens": r.out_tokens or 0,
            "est_cost_usd": round(cost, 8)}


def run_probe_round(conn, log=print):
    """Probe every provider x task in TASK_MODEL. Stores every outcome, including
    'unconfigured' (needed for the DISABLED display; excluded from availability)."""
    rows = []
    for provider in ADAPTERS:
        for task in TASKS:
            if not TASK_MODEL.get(provider, {}).get(task):
                continue
            row = probe_once(provider, task)
            rows.append(row)
            conn.execute(
                "INSERT INTO ai_scoreboard_probes VALUES (?,?,?,?,?,?,?,?,?,?)",
                (row["ts"], row["provider"], row["task"], row["ok"], row["sane"],
                 row["error_kind"], row["latency_ms"], row["in_tokens"],
                 row["out_tokens"], row["est_cost_usd"]))
    conn.commit()
    spent = sum(r["est_cost_usd"] for r in rows)
    log(f"scoreboard: probe round done — {len(rows)} probes, est ${spent:.5f}")
    return rows


def _pctl(sorted_vals, p):
    if not sorted_vals:
        return None
    i = min(len(sorted_vals) - 1, max(0, int(round(p / 100.0 * (len(sorted_vals) - 1)))))
    return sorted_vals[i]


def ranking(conn, window_days=DEFAULT_WINDOW_DAYS):
    """The rolling table. Per task: eligible lanes ranked by availability band
    (>=99.5 A, >=98 B, else C), then typical-call cost, then p95 latency.
    Gated / disabled / insufficient-data lanes are listed with the reason, unranked."""
    since = (datetime.now(timezone.utc) - timedelta(days=window_days)
             ).strftime("%Y-%m-%dT%H:%M:%SZ")
    out = {"window_days": window_days, "since_utc": since, "tasks": {}}
    for task in TASKS:
        lanes = []
        for provider in ADAPTERS:
            model = TASK_MODEL.get(provider, {}).get(task)
            if not model:
                continue
            rows = conn.execute(
                "SELECT ok, sane, error_kind, latency_ms, est_cost_usd "
                "FROM ai_scoreboard_probes WHERE provider=? AND task=? AND ts>=?",
                (provider, task, since)).fetchall()
            configured = [r for r in rows if r[2] != "unconfigured"]
            pin, pout = _price(provider, model)
            cost_call = (TYPICAL_IN_TOK * pin + TYPICAL_OUT_TOK * pout) / 1e6
            gate_ok, gate_note = golden_gate(provider)
            lane = {"provider": provider, "model": model, "samples": len(configured),
                    "cost_per_typical_call_usd": round(cost_call, 6),
                    "golden_gate": "PASS" if gate_ok else "GATED",
                    "golden_note": gate_note or "no golden-set pass on record"}
            if rows and not configured:
                lane.update(status="DISABLED", reason="no key configured (lane is configuration, not outage)")
            elif len(configured) < MIN_SAMPLES:
                lane.update(status="INSUFFICIENT DATA",
                            reason=f"{len(configured)} probes in window (< {MIN_SAMPLES})")
            else:
                oks = [r for r in configured if r[0] == 1]
                lat = sorted(r[3] for r in oks) or [0]
                sane_fails = sum(1 for r in oks if r[1] == 0)
                avail = 100.0 * len(oks) / len(configured)
                lane.update(status="RANKED" if gate_ok else "GATED",
                            availability_pct=round(avail, 2),
                            band="A" if avail >= 99.5 else ("B" if avail >= 98.0 else "C"),
                            p50_ms=_pctl(lat, 50), p95_ms=_pctl(lat, 95),
                            sanity_fails=sane_fails)
            lanes.append(lane)
        ranked = [l for l in lanes if l.get("status") == "RANKED"]
        ranked.sort(key=lambda l: (l["band"], l["cost_per_typical_call_usd"], l["p95_ms"]))
        for i, l in enumerate(ranked, 1):
            l["rank"] = i
        out["tasks"][task] = {"ranked": ranked,
                              "unranked": [l for l in lanes if l.get("status") != "RANKED"]}
    return out


def render_report(rank):
    lines = [f"AI SCOREBOARD — rolling {rank['window_days']}-day ranking "
             f"(since {rank['since_utc']})",
             "quality is a GATE, not a weight: no golden-set pass -> never ranked", ""]
    for task, block in rank["tasks"].items():
        lines.append(f"[{task}]")
        for l in block["ranked"]:
            lines.append(f"  #{l['rank']} {l['provider']:<10} {l['model']:<28} "
                         f"band {l['band']}  avail {l['availability_pct']}%  "
                         f"p95 {l['p95_ms']}ms  ~${l['cost_per_typical_call_usd']}/call"
                         + (f"  ({l['sanity_fails']} sanity fails)" if l.get("sanity_fails") else ""))
        for l in block["unranked"]:
            lines.append(f"  --  {l['provider']:<10} {l['model']:<28} "
                         f"{l['status']}: {l.get('reason', l.get('golden_note', ''))}")
        lines.append("")
    return "\n".join(lines)


def run_nightly(conn=None, log=print, json_out=None):
    """The scheduled entry point (BEA startup loop or cron). Flag-gated; never raises."""
    try:
        own = conn is None
        conn = conn or _connect()
        try:
            if not is_enabled(conn):
                log("scoreboard: disabled (launch_switches.scoreboard_enabled != 1) — no probes sent")
                return None
            run_probe_round(conn, log=log)
            rank = ranking(conn)
            path = json_out or os.path.join(os.path.dirname(db_path()) or ".",
                                            "ai_scoreboard.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(rank, f, indent=1)
            log(f"scoreboard: ranking written -> {path}")
            return rank
        finally:
            if own:
                conn.close()
    except Exception as e:           # a scoreboard hiccup must never hurt the app
        log(f"scoreboard: ERROR {type(e).__name__}: {e}")
        return None


def main(argv=None):
    ap = argparse.ArgumentParser(description="TrustSquare AI scoreboard agent")
    ap.add_argument("--probe", action="store_true", help="run one probe round now")
    ap.add_argument("--force", action="store_true", help="probe even if the flag is off (attended test)")
    ap.add_argument("--report", action="store_true", help="print the rolling ranking")
    ap.add_argument("--json", metavar="FILE", help="also write the ranking JSON here")
    ap.add_argument("--window", type=int, default=DEFAULT_WINDOW_DAYS)
    ap.add_argument("--db", help="database path override (else MS_DB / server default)")
    a = ap.parse_args(argv)
    conn = _connect(a.db)
    try:
        if a.probe:
            if is_enabled(conn) or a.force:
                run_probe_round(conn)
            else:
                print("scoreboard: disabled — enable via enable_scoreboard.bat "
                      "(launch_switches.scoreboard_enabled=1) or use --force for one attended round")
        if a.report or a.json:
            rank = ranking(conn, a.window)
            print(render_report(rank))
            if a.json:
                with open(a.json, "w", encoding="utf-8") as f:
                    json.dump(rank, f, indent=1)
                print(f"json -> {a.json}")
        if not (a.probe or a.report or a.json):
            ap.print_help()
    finally:
        conn.close()


if __name__ == "__main__":
    main()
