#!/usr/bin/env python3
"""AI-FAILOVER-PROOF-1 (DW-054, 21 Aug 2026) — does the breaker fail OVER, or only open?

DW-054's finding, in its own words: "No MarketSquare impact observed ... but the failover
has still never been exercised." Ten Anthropic incidents 12-19 Aug 2026, eight consecutive
days without a clear one, and a failover nobody had ever seen work. A breaker that only
OPENS is a breaker that turns a vendor outage into OUR outage.

WHY THIS IS A HARNESS AND NOT A LIVE FAULT INJECTION: proving it against the real vendor
means either spending on a real call or deliberately breaking the live lane eight days
before launch (RUL-001). Neither is justified. The seam makes it unnecessary -- the
decision under test lives entirely in ai_provider.complete(): given a lane that fails,
does it move to the next configured lane and RETURN THAT LANE'S ANSWER? So we substitute
the ADAPTERS (the vendor HTTP calls) and exercise the REAL complete(), the REAL chain
construction, the REAL cost-approved fallback ranking and the REAL breaker recording.
Nothing about the decision is stubbed; only the sockets are.

Run:  python3 scripts/prove_ai_failover.py       (exit 0 = failover proven)
"""
import os, sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import ai_provider as ap

RESULTS = []


def _check(name, got, want, detail=""):
    ok = (got == want)
    RESULTS.append((ok, name, got, want, detail))
    print(("  PASS  " if ok else "  FAIL  ") + name)
    if not ok or detail:
        print("          got=%r want=%r %s" % (got, want, detail))
    return ok


def _fake(provider, ok, error_kind="", status=None, text=""):
    def adapter(messages, model, max_tokens, system, timeout=30):
        calls.append(provider)
        return ap.AIResult(text or ("answer from " + provider), 10, 10, provider, model,
                           ok=ok, status=status, error_kind=error_kind)
    return adapter


def scenario(title, wiring, **kw):
    """Swap ADAPTERS for one call, keep everything else real."""
    global calls
    calls = []
    saved = dict(ap.ADAPTERS)
    try:
        for prov, ad in wiring.items():
            ap.ADAPTERS[prov] = ad
        # Only lanes we wired may take part, so the outcome is unambiguous.
        for prov in list(ap.ADAPTERS):
            if prov not in wiring:
                ap.ADAPTERS.pop(prov)
        print("\n" + title)
        return ap.complete([{"role": "user", "content": "ping"}], **kw)
    finally:
        ap.ADAPTERS.clear()
        ap.ADAPTERS.update(saved)


print("AI-FAILOVER-PROOF-1 — exercising the real ai_provider.complete()\n"
      "active lane: %s · task tier: sonnet" % ap.AI_ACTIVE)

# ── 1. Vendor 5xx on the active lane ─────────────────────────────────────────
r = scenario("1. active lane returns HTTP 5xx (the 16 Aug outage shape)",
             {"anthropic": _fake("anthropic", False, "http_5xx", 503),
              "openai":    _fake("openai", True)},
             task="sonnet", provider="anthropic")
_check("failover happened: answer came from the SECOND lane", r.provider, "openai")
_check("caller sees SUCCESS, not an outage", r.ok, True)
_check("both lanes were actually called, in order", calls, ["anthropic", "openai"])

# ── 2. Vendor auth failure (the 16 Aug incident began as auth) ───────────────
r = scenario("2. active lane returns 401 unauthorized (revoked/expired key)",
             {"anthropic": _fake("anthropic", False, "unauthorized", 401),
              "openai":    _fake("openai", True)},
             task="sonnet", provider="anthropic")
_check("auth failure fails OVER, it does not fail the request", r.provider, "openai")
_check("caller sees SUCCESS", r.ok, True)

# ── 3. Rate limit ───────────────────────────────────────────────────────────
r = scenario("3. active lane returns 429 rate_limited",
             {"anthropic": _fake("anthropic", False, "rate_limited", 429),
              "openai":    _fake("openai", True)},
             task="sonnet", provider="anthropic")
_check("429 fails OVER", r.provider, "openai")

# ── 4. EVERY lane down — the honest-failure case ────────────────────────────
r = scenario("4. every lane down (must fail honestly, never silently succeed)",
             {"anthropic": _fake("anthropic", False, "http_5xx", 503),
              "openai":    _fake("openai", False, "http_5xx", 503)},
             task="sonnet", provider="anthropic")
_check("reports failure", r.ok, False)
_check("reports the REQUESTED lane's failure, not the last one tried", r.provider, "anthropic")
_check("every lane was tried before giving up", sorted(calls), ["anthropic", "openai"])

# ── 5. probe=True must NOT fail over ────────────────────────────────────────
r = scenario("5. probe mode is unambiguous — a probe's outcome is the TARGET's",
             {"anthropic": _fake("anthropic", False, "http_5xx", 503),
              "openai":    _fake("openai", True)},
             task="sonnet", provider="anthropic", probe=True)
_check("probe did not fall through to another lane", r.provider, "anthropic")
_check("probe reports the target's failure", r.ok, False)
_check("only the target lane was called", calls, ["anthropic"])

# ── 6. allow_fallback=False must NOT fail over ──────────────────────────────
r = scenario("6. allow_fallback=False is honoured",
             {"anthropic": _fake("anthropic", False, "http_5xx", 503),
              "openai":    _fake("openai", True)},
             task="sonnet", provider="anthropic", allow_fallback=False)
_check("no failover when the caller forbade it", r.provider, "anthropic")

failed = [r for r in RESULTS if not r[0]]
print("\n%d checks · %d passed · %d failed" % (len(RESULTS), len(RESULTS) - len(failed), len(failed)))
if failed:
    print("FAILOVER NOT PROVEN — the breaker opens but does not fail over.")
    sys.exit(1)
print("FAILOVER PROVEN: a vendor 5xx, a 401 and a 429 each move the request to the next\n"
      "configured lane and return that lane's answer; an all-lanes-down case still fails\n"
      "honestly; probe and allow_fallback=False are both respected.")
sys.exit(0)
