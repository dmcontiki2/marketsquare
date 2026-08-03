#!/usr/bin/env python3
"""
test_ai_scoreboard.py — SCOREBOARD-1 guard suite (3 Aug 2026).

Runs with pytest OR plain python (house rule, same as test_trust_evidence_true.py):
    python3 test_ai_scoreboard.py [project_dir]

Covers the class-level rules that must never regress:
  1. Quality is a GATE, not a weight — an ungated lane can never be RANKED.
  2. 'unconfigured' is configuration, not outage — DISABLED, excluded from availability.
  3. Ranking order: availability band -> cost -> p95 latency.
  4. Flag off = zero probes sent (spend stays David's click).
  5. Window filtering: rows older than the window never count.
  6. A probe round stores one row per configured provider x task.
"""
import os, sys, json, sqlite3, tempfile
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) > 1 and os.path.isdir(sys.argv[1]):
    sys.path.insert(0, sys.argv[1])

import ai_scoreboard as sb


class FakeResult:
    def __init__(self, ok=True, text="OK 12 good red", error_kind="", in_t=20, out_t=5):
        self.ok, self.text, self.error_kind = ok, text, error_kind
        self.in_tokens, self.out_tokens = in_t, out_t
        self.provider, self.model, self.status = "", "", 200


def fresh_conn(scoreboard_enabled=None):
    """Mirrors the REAL launch_switches shape: singleton wide table, id=1.
    scoreboard_enabled=None simulates the pre-enable state (column absent)."""
    conn = sqlite3.connect(":memory:")
    conn.executescript(sb.SCHEMA)
    if scoreboard_enabled is None:
        conn.execute("CREATE TABLE launch_switches (id INTEGER PRIMARY KEY CHECK (id=1), mode TEXT)")
        conn.execute("INSERT INTO launch_switches (id, mode) VALUES (1, 'launch')")
    else:
        conn.execute("CREATE TABLE launch_switches (id INTEGER PRIMARY KEY CHECK (id=1), "
                     "mode TEXT, scoreboard_enabled INTEGER NOT NULL DEFAULT 0)")
        conn.execute("INSERT INTO launch_switches (id, mode, scoreboard_enabled) VALUES (1, 'launch', ?)",
                     (1 if scoreboard_enabled else 0,))
    return conn


def seed(conn, provider, task, n_ok, n_fail=0, lat=500, days_ago=0, kind="http_5xx"):
    ts = (datetime.now(timezone.utc) - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%SZ")
    for _ in range(n_ok):
        conn.execute("INSERT INTO ai_scoreboard_probes VALUES (?,?,?,?,?,?,?,?,?,?)",
                     (ts, provider, task, 1, 1, "", lat, 20, 5, 0.0001))
    for _ in range(n_fail):
        conn.execute("INSERT INTO ai_scoreboard_probes VALUES (?,?,?,?,?,?,?,?,?,?)",
                     (ts, provider, task, 0, None, kind, 0, 0, 0, 0.0))
    conn.commit()


def test_quality_gate_blocks_ranking():
    """openai has NO golden-set pass on record -> even 100% availability stays GATED."""
    conn = fresh_conn()
    seed(conn, "openai", "haiku", 50)          # perfect record
    seed(conn, "scaleway", "haiku", 40, 10)    # worse availability, but gated PASS
    rank = sb.ranking(conn)["tasks"]["haiku"]
    ranked = {l["provider"] for l in rank["ranked"]}
    assert "openai" not in ranked, "GATE VIOLATION: ungated lane was ranked"
    gated = [l for l in rank["unranked"] if l["provider"] == "openai"]
    assert gated and gated[0]["status"] == "GATED"
    assert "scaleway" in ranked
    conn.close()


def test_unconfigured_is_disabled_not_outage():
    conn = fresh_conn()
    seed(conn, "scaleway", "sonnet", 0, 10, kind="unconfigured")
    rank = sb.ranking(conn)["tasks"]["sonnet"]
    lane = [l for l in rank["unranked"] if l["provider"] == "scaleway"][0]
    assert lane["status"] == "DISABLED", f"expected DISABLED, got {lane['status']}"
    assert "availability_pct" not in lane, "unconfigured rows polluted availability"
    conn.close()


def test_ranking_order_band_then_cost_then_latency():
    """anthropic: band A, expensive. scaleway: band A, cheap -> scaleway must rank #1.
    Then degrade scaleway to band C -> anthropic overtakes despite its price."""
    conn = fresh_conn()
    seed(conn, "anthropic", "haiku", 200, 0, lat=400)
    seed(conn, "scaleway", "haiku", 200, 0, lat=900)
    r1 = sb.ranking(conn)["tasks"]["haiku"]["ranked"]
    assert r1[0]["provider"] == "scaleway", "same band: cheaper lane must rank first"
    seed(conn, "scaleway", "haiku", 0, 20)     # push availability below 98 -> band C
    r2 = sb.ranking(conn)["tasks"]["haiku"]["ranked"]
    assert r2[0]["provider"] == "anthropic", "band beats cost: degraded lane must drop"
    conn.close()


def test_flag_off_sends_zero_probes():
    conn = fresh_conn()
    calls = []
    orig = sb.complete
    sb.complete = lambda *a, **k: (calls.append(1), FakeResult())[1]
    try:
        out = sb.run_nightly(conn, log=lambda *a: None)
    finally:
        sb.complete = orig
    assert out is None and not calls, "flag off must mean ZERO probe spend"
    n = conn.execute("SELECT COUNT(*) FROM ai_scoreboard_probes").fetchone()[0]
    assert n == 0
    conn.close()


def test_flag_on_probes_and_writes_json():
    """The mirror of flag-off: enabled -> probes stored, ranking JSON written."""
    import tempfile
    conn = fresh_conn(scoreboard_enabled=True)
    orig = sb.complete
    sb.complete = lambda *a, **k: FakeResult()
    try:
        with tempfile.TemporaryDirectory() as d:
            out = os.path.join(d, "ai_scoreboard.json")
            rank = sb.run_nightly(conn, log=lambda *a: None, json_out=out)
            assert rank is not None, "enabled flag must run the round"
            assert os.path.exists(out), "ranking JSON not written"
            with open(out) as f:
                assert "tasks" in json.load(f)
    finally:
        sb.complete = orig
    n = conn.execute("SELECT COUNT(*) FROM ai_scoreboard_probes").fetchone()[0]
    assert n > 0
    conn.close()


def test_window_filtering():
    conn = fresh_conn()
    seed(conn, "scaleway", "triage", 10, 0, days_ago=200)   # ancient history
    rank = sb.ranking(conn, window_days=90)["tasks"]["triage"]
    lane = [l for l in rank["unranked"] if l["provider"] == "scaleway"][0]
    assert lane["status"] == "INSUFFICIENT DATA", "rows outside the window must not count"
    conn.close()


def test_probe_round_covers_every_configured_lane():
    conn = fresh_conn()
    orig = sb.complete
    sb.complete = lambda *a, **k: FakeResult()
    try:
        rows = sb.run_probe_round(conn, log=lambda *a: None)
    finally:
        sb.complete = orig
    expected = sum(1 for p in sb.ADAPTERS for t in sb.TASKS
                   if sb.TASK_MODEL.get(p, {}).get(t))
    assert len(rows) == expected, f"expected {expected} probes, got {len(rows)}"
    stored = conn.execute("SELECT COUNT(*) FROM ai_scoreboard_probes").fetchone()[0]
    assert stored == expected
    conn.close()


ALL = [test_quality_gate_blocks_ranking, test_unconfigured_is_disabled_not_outage,
       test_ranking_order_band_then_cost_then_latency, test_flag_off_sends_zero_probes,
       test_flag_on_probes_and_writes_json, test_window_filtering,
       test_probe_round_covers_every_configured_lane]

if __name__ == "__main__":
    failed = 0
    for t in ALL:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failed += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(ALL) - failed}/{len(ALL)} passed")
    sys.exit(1 if failed else 0)
