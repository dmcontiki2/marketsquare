"""
failover/eval_golden_set.py - run the 16-call golden set against a backend.

Default is a $0 dry-run (no network, no tokens) that proves the harness and the
call/tier wiring end to end. Use --live to hit the configured backend and check
that real responses come back in the expected shape (the parity gate before you
trust the failover for any call).

    python -m failover.eval_golden_set                 # $0 dry-run
    AI_BACKEND=failover FAILOVER_BASE_URL=http://host:8000 \
        python -m failover.eval_golden_set --live      # live parity check

Exit code 0 = all passed, 1 = at least one failure (CI-friendly).
"""
import argparse
import json
import sys

from failover import ai_backends as ai
from failover.golden_set import GOLDEN


def schema_ok(expected, got):
    if isinstance(expected, dict):
        return isinstance(got, dict) and all(k in got for k in expected)
    if isinstance(expected, list):
        return isinstance(got, list)
    return True


def run(live=False):
    rows = []
    passed = 0
    for item in GOLDEN:
        msgs = [{"role": "user", "content": "[golden-set fixture] " + item["name"]}]
        try:
            r = ai.ai_call(item["name"], item["tier"], msgs, max_tokens=256,
                           dry_run=not live, dry_run_payload=item["schema"])
            text = (r.get("text") or "").strip()
            parsed = json.loads(text) if text[:1] in ("{", "[") else {}
            ok = schema_ok(item["schema"], parsed)
            backend = r.get("backend")
        except Exception as e:  # noqa: BLE001
            ok, backend = False, "error:" + str(e)[:24]
        passed += 1 if ok else 0
        rows.append((item["name"], item["tier"], backend, "PASS" if ok else "FAIL"))

    w = max(len(r[0]) for r in rows)
    print("%-*s  %-13s %-10s %s" % (w, "call", "tier", "backend", "result"))
    print("-" * (w + 34))
    for name, tier, backend, res in rows:
        print("%-*s  %-13s %-10s %s" % (w, name, tier, str(backend), res))
    print("-" * (w + 34))
    print("%d/%d passed  (mode: %s)" % (passed, len(GOLDEN), "LIVE" if live else "dry-run $0"))
    return 0 if passed == len(GOLDEN) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="hit the configured backend instead of dry-run")
    sys.exit(run(ap.parse_args().live))
