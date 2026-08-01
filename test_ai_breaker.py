#!/usr/bin/env python3
"""P2a mandatory test matrix (design v1.2 §9) — 12 cases. Stdlib + sqlite3 only."""
import datetime, importlib, os, sqlite3, sys, tempfile, unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ai_breaker as brk
import ai_provider as ap

DB = tempfile.mktemp(suffix=".db")
def get_db():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row; return c

def reset():
    for t in ("ai_breaker", "ai_breaker_stats"):
        c = get_db(); c.execute(f"DELETE FROM {t}"); c.commit(); c.close()

def state(p, t):
    c = get_db()
    r = c.execute("SELECT * FROM ai_breaker WHERE provider=? AND task=?", (p, t)).fetchone()
    c.close(); return dict(r) if r else None

def backdate(p, t, **cols):
    c = get_db()
    sets = ", ".join(f"{k}=?" for k in cols)
    c.execute(f"UPDATE ai_breaker SET {sets} WHERE provider=? AND task=?", (*cols.values(), p, t))
    c.commit(); c.close()

ALERTS = []
brk.attach(get_db, alert=ALERTS.append)

class T(unittest.TestCase):
    def setUp(self): reset(); ALERTS.clear(); os.environ.pop("AI_DRILL_BAN", None)

    def test_01_t1_consecutive_trips(self):
        for _ in range(3): brk.record("anthropic", "haiku", False, "timeout")
        s = state("anthropic", "haiku")
        self.assertEqual((s["state"], s["trip_reason"]), ("tripped", "T1_outage"))
        self.assertFalse(brk.allows("anthropic", "haiku"))

    def test_02_success_resets_t1_counter(self):
        brk.record("anthropic", "haiku", False, "timeout")
        brk.record("anthropic", "haiku", False, "timeout")
        brk.record("anthropic", "haiku", True)
        brk.record("anthropic", "haiku", False, "timeout")
        self.assertEqual(state("anthropic", "haiku")["state"], "closed")

    def test_03_t2_rolling_denominator(self):
        for _ in range(8): brk.record("scaleway", "haiku", True)
        brk.record("scaleway", "haiku", False, "rate_limited")   # 1/9 — no trip
        self.assertEqual(state("scaleway", "haiku")["state"], "closed")
        brk.record("scaleway", "haiku", False, "rate_limited")   # 2/10 = 20% -> trip
        self.assertEqual(state("scaleway", "haiku")["trip_reason"], "T2_degraded")

    def test_04_t3_immediate_and_loud(self):
        brk.record("openai", "haiku", False, "unauthorized")
        s = state("openai", "haiku")
        self.assertEqual((s["state"], s["trip_reason"]), ("tripped", "T3_account"))
        self.assertTrue(any(a.get("loud") for a in ALERTS))

    def test_05_invalid_request_and_unconfigured_never_trip(self):
        for _ in range(6):
            brk.record("anthropic", "haiku", False, "invalid_request")
            brk.record("openai", "haiku", False, "unconfigured")
        self.assertEqual(state("anthropic", "haiku")["state"], "closed")
        self.assertEqual(state("openai", "haiku")["state"], "closed")
        c = get_db()
        n = c.execute("SELECT COALESCE(SUM(attempts),0) a FROM ai_breaker_stats "
                      "WHERE provider='openai'").fetchone()["a"]
        c.close()
        self.assertEqual(n, 0, "unconfigured attempts must not pollute T2 stats")

    def test_06_atomic_probe_claim(self):
        for _ in range(3): brk.record("anthropic", "haiku", False, "timeout")
        backdate("anthropic", "haiku", probe_after="2020-01-01T00:00:00")
        self.assertTrue(brk.claim_probe("anthropic", "haiku"))
        self.assertFalse(brk.claim_probe("anthropic", "haiku"), "second claim inside lease must fail")

    def test_07_dropout_auto_recovers_with_hysteresis(self):
        for _ in range(3): brk.record("anthropic", "haiku", False, "timeout")
        brk.record("anthropic", "haiku", True); brk.record("anthropic", "haiku", True)
        self.assertNotEqual(state("anthropic", "haiku")["state"], "closed", "2 probes must not close")
        backdate("anthropic", "haiku",
                 first_probe_ok_at=(datetime.datetime.utcnow()-datetime.timedelta(seconds=400)).isoformat(timespec="seconds"))
        brk.record("anthropic", "haiku", True)
        self.assertEqual(state("anthropic", "haiku")["state"], "closed", "3rd probe past span auto-recovers (David: dropouts auto)")
        self.assertTrue(any(a.get("event") == "recovered" for a in ALERTS))

    def test_08_ban_goes_ready_never_auto(self):
        brk.record("openai", "haiku", False, "unauthorized")
        for _ in range(2): brk.record("openai", "haiku", True)
        backdate("openai", "haiku",
                 first_probe_ok_at=(datetime.datetime.utcnow()-datetime.timedelta(seconds=400)).isoformat(timespec="seconds"))
        brk.record("openai", "haiku", True)
        s = state("openai", "haiku")
        self.assertEqual(s["state"], "ready", "a BAN must wait for the operator (David's ruling)")
        self.assertFalse(brk.allows("openai", "haiku"))
        self.assertEqual(brk.restore("openai", "haiku", who="david"), 1)
        self.assertTrue(brk.allows("openai", "haiku"))

    def test_09_drill_is_stateless_overlay(self):
        os.environ["AI_DRILL_BAN"] = "anthropic"
        self.assertFalse(brk.allows("anthropic", "haiku"))
        brk.record("anthropic", "haiku", False, "timeout")   # drill lanes never write state
        self.assertIsNone(state("anthropic", "haiku"))
        del os.environ["AI_DRILL_BAN"]
        self.assertTrue(brk.allows("anthropic", "haiku"), "unset env = drill over instantly")

    def test_10_seam_skips_tripped_lane_and_attributes_per_attempt(self):
        calls = []
        def fake(name, ok):
            def f(msgs, model, mt, sys_, timeout=30):
                calls.append(name)
                return ap.AIResult("x" if ok else "", 1, 1, name, model, ok=ok,
                                   error_kind="" if ok else "http_5xx", status=200 if ok else 500)
            return f
        old = dict(ap.ADAPTERS)
        try:
            ap.ADAPTERS.update(anthropic=fake("anthropic", False), openai=fake("openai", True),
                               scaleway=fake("scaleway", True))
            r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
            self.assertTrue(r.ok and r.provider == "openai")
            s = state("anthropic", "haiku")
            self.assertEqual(s["consec_fails"], 1, "failure recorded against the lane that failed")
            for _ in range(2): ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
            self.assertEqual(state("anthropic", "haiku")["state"], "tripped")
            calls.clear()
            ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
            self.assertNotIn("anthropic", calls, "tripped lane must not receive normal calls")
        finally:
            ap.ADAPTERS.update(old)

    def test_11_probe_mode_no_fallback(self):
        old = dict(ap.ADAPTERS)
        try:
            ap.ADAPTERS.update(anthropic=lambda *a, **k: ap.AIResult("",None,None,"anthropic","m",ok=False,error_kind="timeout"),
                               openai=lambda *a, **k: ap.AIResult("ok",1,1,"openai","m",ok=True))
            r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic", probe=True)
            self.assertFalse(r.ok, "a probe must NEVER be answered by another lane (Peer blocker #3)")
            self.assertEqual(r.provider, "anthropic")
        finally:
            ap.ADAPTERS.update(old)

    def test_12_all_lanes_down_honest_failure(self):
        old = dict(ap.ADAPTERS)
        try:
            dead = lambda *a, **k: ap.AIResult("",None,None,"x","m",ok=False,error_kind="connection")
            ap.ADAPTERS.update(anthropic=dead, openai=dead, scaleway=dead)
            r = ap.complete([{"role":"user","content":"hi"}], task="haiku", provider="anthropic")
            self.assertFalse(r.ok)
        finally:
            ap.ADAPTERS.update(old)

if __name__ == "__main__":
    unittest.main(verbosity=1)
