#!/usr/bin/env python3
"""ai_breaker.py — P2a circuit breaker for the AI provider seam (1 Aug 2026).

Design: AI_AUTO_FAILOVER_P2_DESIGN.md v1.2 · trip taxonomy AI_SWAP_ARCHITECTURE §2 ·
recovery doctrine = David's ruling 31 Jul 2026: DROPOUTS (T1 outage / T2 degradation)
AUTO-RECOVER behind anti-flap hysteresis; BANS (T3 account action) go READY and wait
for a MANUAL restore — a ban has a reason, and the operator considers it first.

Wiring: the seam (ai_provider.complete) calls allows()/record()/claim_probe(); the BEA
injects the DB at startup via attach(database.get_db). UNATTACHED = FAIL-OPEN: every
gate answers "allowed", records are dropped — standalone scripts (peer review, golden
set, price truth) import the seam with zero breaker coupling, and a breaker fault can
never take the platform down harder than no breaker at all.

State per (provider, task): closed | tripped | half_open | ready.
  closed    normal — lane eligible
  tripped   excluded; probe_after schedules the next trial
  half_open ONE atomically-claimed trial call in flight
  ready     T3 lane proven healthy by probes — STILL excluded until manual restore()
"""
import datetime as _dt
import json as _json
import os as _os

# Trip rules (design §4) — env-tunable, defaults per the signed-off design
T1_CONSEC = int(_os.getenv("AI_BREAKER_T1_CONSEC", "3"))
T1_WINDOW_S = int(_os.getenv("AI_BREAKER_T1_WINDOW_S", "120"))
T2_MIN_CALLS = int(_os.getenv("AI_BREAKER_T2_MIN_CALLS", "10"))
T2_FAIL_PCT = float(_os.getenv("AI_BREAKER_T2_FAIL_PCT", "20"))
T2_WINDOW_MIN = int(_os.getenv("AI_BREAKER_T2_WINDOW_MIN", "10"))
PROBE_AFTER_S = int(_os.getenv("AI_BREAKER_PROBE_AFTER_S", "300"))      # T1/T2: 5 min
PROBE_AFTER_T3_S = int(_os.getenv("AI_BREAKER_PROBE_T3_S", "3600"))    # T3: hourly
RECOVER_STREAK = int(_os.getenv("AI_BREAKER_RECOVER_STREAK", "3"))      # hysteresis
RECOVER_SPAN_S = int(_os.getenv("AI_BREAKER_RECOVER_SPAN_S", "300"))    # ≥5 min apart
PROBE_LEASE_S = 90                                                       # half_open lease

T1_KINDS = ("timeout", "connection", "http_5xx")
T3_KINDS = ("unauthorized", "credit_exhausted")
# rate_limited -> T2 only. invalid_request -> OUR bug, never trips a lane.
# unconfigured -> nothing: a lane without a key is configuration, not an outage.

_get_db = None            # injected by bea at startup: attach(database.get_db)
_alert = None             # optional alert hook: fn(payload dict)


def attach(get_db, alert=None):
    """BEA startup: inject the DB factory (and optional alert hook), create tables."""
    global _get_db, _alert
    _get_db, _alert = get_db, alert
    conn = get_db()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS ai_breaker (
            provider TEXT NOT NULL, task TEXT NOT NULL,
            state TEXT NOT NULL DEFAULT 'closed',
            trip_reason TEXT, tripped_at TEXT, probe_after TEXT,
            consec_fails INTEGER NOT NULL DEFAULT 0,
            first_fail_at TEXT,
            probe_ok_streak INTEGER NOT NULL DEFAULT 0,
            first_probe_ok_at TEXT,
            last_error TEXT, last_error_at TEXT, last_ok_at TEXT,
            restored_by TEXT, restored_at TEXT,
            PRIMARY KEY (provider, task))""")
        conn.execute("""CREATE TABLE IF NOT EXISTS ai_breaker_stats (
            provider TEXT NOT NULL, task TEXT NOT NULL,
            bucket_minute TEXT NOT NULL,
            attempts INTEGER NOT NULL DEFAULT 0,
            failures INTEGER NOT NULL DEFAULT 0,
            PRIMARY KEY (provider, task, bucket_minute))""")
        conn.commit()
    finally:
        conn.close()


def _now():
    return _dt.datetime.utcnow()


def _iso(dt=None):
    return (dt or _now()).isoformat(timespec="seconds")


def drill_banned():
    """AI_DRILL_BAN overlay — NON-PERSISTENT, evaluated per call (design §8): named lanes
    are excluded exactly as if T3-tripped, but NO state is written and unsetting the env
    ends the drill instantly."""
    raw = _os.getenv("AI_DRILL_BAN", "")
    return {p.strip() for p in raw.split(",") if p.strip()}


def allows(provider, task):
    """May this lane serve a NORMAL call right now? Fail-open when unattached/broken."""
    if provider in drill_banned():
        return False
    if _get_db is None:
        return True
    try:
        conn = _get_db()
        try:
            row = conn.execute("SELECT state FROM ai_breaker WHERE provider=? AND task=?",
                               (provider, task)).fetchone()
        finally:
            conn.close()
        return (row is None) or (row["state"] == "closed")
    except Exception:
        return True   # breaker fault must never be worse than no breaker


def claim_probe(provider, task):
    """Atomically claim the single half-open trial for an eligible lane (design §5).
    Returns True exactly once per probe window, under any concurrency."""
    if _get_db is None or provider in drill_banned():
        return False
    try:
        conn = _get_db()
        try:
            cur = conn.execute(
                "UPDATE ai_breaker SET state='half_open', probe_after=? "
                "WHERE provider=? AND task=? AND state IN ('tripped','half_open') "
                "AND (probe_after IS NULL OR probe_after <= ?)",
                (_iso(_now() + _dt.timedelta(seconds=PROBE_LEASE_S)), provider, task, _iso()))
            conn.commit()
            return cur.rowcount == 1
        finally:
            conn.close()
    except Exception:
        return False


def record(provider, task, ok, error_kind="unknown", detail="", probe=False):
    """Record one adapter ATTEMPT's outcome (attribution is per invocation, never per
    chain — Peer cost review). Drives trips, hysteresis recovery, and T3 ready state.
    Drill-banned lanes are never recorded (overlay writes no state)."""
    if _get_db is None or provider in drill_banned():
        return
    try:
        now = _now()
        conn = _get_db()
        try:
            conn.execute("INSERT INTO ai_breaker (provider, task) VALUES (?,?) "
                         "ON CONFLICT(provider, task) DO NOTHING", (provider, task))
            # rolling stats — T2 needs a denominator; unconfigured attempts are NOT
            # demand (a keyless lane is configuration) so they stay out of the buckets
            if error_kind != "unconfigured":
                bucket = now.strftime("%Y-%m-%dT%H:%M")
                conn.execute(
                    "INSERT INTO ai_breaker_stats (provider, task, bucket_minute, attempts, failures) "
                    "VALUES (?,?,?,1,?) ON CONFLICT(provider, task, bucket_minute) "
                    "DO UPDATE SET attempts=attempts+1, failures=failures+?",
                    (provider, task, bucket, 0 if ok else 1, 0 if ok else 1))
                conn.execute("DELETE FROM ai_breaker_stats WHERE bucket_minute < ?",
                             ((now - _dt.timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M"),))
            row = dict(conn.execute("SELECT * FROM ai_breaker WHERE provider=? AND task=?",
                                    (provider, task)).fetchone())
            if ok:
                _record_ok(conn, provider, task, row, now)
            else:
                _record_fail(conn, provider, task, row, now, error_kind, detail)
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass   # never let bookkeeping break serving


def _record_ok(conn, provider, task, row, now):
    if row["state"] == "closed":
        conn.execute("UPDATE ai_breaker SET consec_fails=0, first_fail_at=NULL, last_ok_at=? "
                     "WHERE provider=? AND task=?", (_iso(now), provider, task))
        return
    streak = row["probe_ok_streak"] + 1
    first = row["first_probe_ok_at"] or _iso(now)
    span_ok = (now - _dt.datetime.fromisoformat(first)).total_seconds() >= RECOVER_SPAN_S
    if streak >= RECOVER_STREAK and span_ok:
        if row["trip_reason"] in ("T3_account", None) and row["trip_reason"] == "T3_account":
            # BAN: proven healthy -> READY, but routing stays excluded until manual restore
            conn.execute("UPDATE ai_breaker SET state='ready', probe_ok_streak=?, last_ok_at=? "
                         "WHERE provider=? AND task=?", (streak, _iso(now), provider, task))
            _fire({"event": "ready_to_restore", "provider": provider, "task": task})
        else:
            # DROPOUT: hysteresis met -> auto-recover (David's ruling)
            conn.execute("UPDATE ai_breaker SET state='closed', trip_reason=NULL, tripped_at=NULL, "
                         "probe_after=NULL, consec_fails=0, first_fail_at=NULL, "
                         "probe_ok_streak=0, first_probe_ok_at=NULL, last_ok_at=? "
                         "WHERE provider=? AND task=?", (_iso(now), provider, task))
            _fire({"event": "recovered", "provider": provider, "task": task})
    else:
        conn.execute("UPDATE ai_breaker SET probe_ok_streak=?, first_probe_ok_at=?, "
                     "probe_after=?, state=CASE state WHEN 'half_open' THEN 'tripped' ELSE state END, "
                     "last_ok_at=? WHERE provider=? AND task=?",
                     (streak, first, _iso(now + _dt.timedelta(seconds=PROBE_AFTER_S)),
                      _iso(now), provider, task))


def _record_fail(conn, provider, task, row, now, kind, detail):
    detail = (detail or "")[:200]   # sanitized upstream; bounded here regardless
    sets = {"last_error": f"{kind}: {detail}"[:200], "last_error_at": _iso(now),
            "probe_ok_streak": 0, "first_probe_ok_at": None}
    trip = None
    if kind in T3_KINDS:
        trip = ("T3_account", PROBE_AFTER_T3_S)
    elif kind in T1_KINDS:
        first = row["first_fail_at"]
        fresh = first and (now - _dt.datetime.fromisoformat(first)).total_seconds() <= T1_WINDOW_S
        consec = (row["consec_fails"] + 1) if fresh or row["consec_fails"] == 0 else 1
        sets["consec_fails"] = consec
        sets["first_fail_at"] = first if (fresh and row["consec_fails"] > 0) else _iso(now)
        if consec >= T1_CONSEC:
            trip = ("T1_outage", PROBE_AFTER_S)
    # rate_limited / unknown -> T2 evaluation below; invalid_request/unconfigured never trip
    if trip is None and kind not in ("invalid_request", "unconfigured") and row["state"] == "closed":
        cut = (now - _dt.timedelta(minutes=T2_WINDOW_MIN)).strftime("%Y-%m-%dT%H:%M")
        st = conn.execute("SELECT COALESCE(SUM(attempts),0) a, COALESCE(SUM(failures),0) f "
                          "FROM ai_breaker_stats WHERE provider=? AND task=? AND bucket_minute>=?",
                          (provider, task, cut)).fetchone()
        if st["a"] >= T2_MIN_CALLS and (st["f"] / st["a"]) * 100.0 >= T2_FAIL_PCT:
            trip = ("T2_degraded", PROBE_AFTER_S)
    if trip and row["state"] in ("closed", "half_open", "tripped"):
        reason, delay = trip
        if row["state"] == "closed" or (reason == "T3_account" and row["trip_reason"] != "T3_account"):
            sets.update(state="tripped", trip_reason=reason, tripped_at=_iso(now),
                        probe_after=_iso(now + _dt.timedelta(seconds=delay)))
            _fire({"event": "trip", "provider": provider, "task": task, "reason": reason,
                   "loud": reason == "T3_account", "detail": sets["last_error"]})
        else:   # failed probe on an already-tripped lane -> push the window out
            sets.update(state="tripped",
                        probe_after=_iso(now + _dt.timedelta(seconds=delay)))
    elif row["state"] == "half_open":
        sets.update(state="tripped",
                    probe_after=_iso(now + _dt.timedelta(seconds=PROBE_AFTER_S)))
    cols = ", ".join(f"{k}=?" for k in sets)
    conn.execute(f"UPDATE ai_breaker SET {cols} WHERE provider=? AND task=?",
                 (*sets.values(), provider, task))


def restore(provider, task=None, who="admin"):
    """MANUAL restore — the only path back to traffic for a T3/ban lane. Closes the
    breaker for one task or all tasks of a provider. Returns rows affected."""
    if _get_db is None:
        return 0
    conn = _get_db()
    try:
        q = ("UPDATE ai_breaker SET state='closed', trip_reason=NULL, tripped_at=NULL, "
             "probe_after=NULL, consec_fails=0, first_fail_at=NULL, probe_ok_streak=0, "
             "first_probe_ok_at=NULL, restored_by=?, restored_at=? WHERE provider=?")
        args = [who, _iso(), provider]
        if task:
            q += " AND task=?"; args.append(task)
        cur = conn.execute(q, args)
        conn.commit()
        return cur.rowcount
    finally:
        conn.close()


def snapshot():
    """Breaker state for /flags (P2b card lights) — sanitized rows only."""
    if _get_db is None:
        return None
    try:
        conn = _get_db()
        try:
            rows = conn.execute("SELECT provider, task, state, trip_reason, tripped_at, "
                                "probe_after, last_error FROM ai_breaker "
                                "WHERE state != 'closed'").fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()
    except Exception:
        return None


def _fire(payload):
    if _alert is None:
        return
    try:
        _alert(payload)
    except Exception:
        pass
