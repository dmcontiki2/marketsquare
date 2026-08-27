#!/usr/bin/env python3
"""prove_posture_redaction.py — POSTURE-REDACT-1 harness (27 Aug 2026).

Ledger RG-0144. Proves, offline and without importing the app, that
/dashboard/summary's redaction actually removes the defence posture from an
ANONYMOUS payload — and, just as importantly, that it leaves everything else alone.

Why a repo-side harness when RG-0144 already probes the live site: the live half
reads whatever is DEPLOYED, so between writing the fix and shipping it the entry
says "still leaking" and cannot tell "not written" from "not shipped". This half
answers "is the fix in the source", which is the question a pre-deploy session needs.

The fixture is the real leak, verbatim from the live endpoint on 27 Aug 2026.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The ledger's own pattern set. Duplicated deliberately and asserted to match, so a
# widened ledger pattern cannot silently outrun the redactor (drift is a failure here).
PATTERNS = (
    r"\bWAF\b", r"allow[\s\-_]?list", r"\bfirewall\b", r"bot\s*management",
    r"only\s+guard", r"sole\s+(?:guard|control)", r"GATE[\s\-_]?ENFORCE",
    r"\bunprotected\b", r"\bdisabled\b.{0,40}\b(?:WAF|gate|guard|firewall)\b",
    r"origin\s+(?:gate|token).{0,30}\b(?:only|sole)\b",
)

LIVE_LEAK = (
    "BEA v1.3.1 · FastAPI + SQLite · Hetzner CPX32 (8GB RAM) + 100GB volume · "
    "trustsquare.co · **104 live listings · 59 sellers** · World Heritage layer 332 sites · "
    "pre-launch: Cloudflare WAF allowlist DISABLED (WAF-OPEN-1), origin gate GATE-ENFORCE-1 "
    "the only guard · **SOFT-to-PUBLIC Fri 29 Aug 2026**"
)

checks = []
def ok(cond, label):
    checks.append((bool(cond), label))
    print(("  [OK] " if cond else "  [!!] ") + label)


def load_redactor():
    """Pull _POSTURE_RE.._redact_posture out of bea_main.py and exec it in isolation.
    No app import: this must run on a machine with no fastapi and no database."""
    src = io.open(os.path.join(ROOT, "bea_main.py"), encoding="utf-8").read()
    try:
        i = src.index("_POSTURE_RE = re.compile(")
        j = src.index("def _summary_caller_is_admin")
    except ValueError:
        print("  [!!] bea_main.py no longer defines the POSTURE-REDACT-1 block")
        sys.exit(1)
    ns = {"re": re}
    exec(src[i:j], ns)
    return ns["_redact_posture"], src


def hits(text):
    return sorted({p for p in PATTERNS if re.search(p, text, flags=re.I)})


def main():
    redact, src = load_redactor()

    print("\nTHE REAL LEAK IS REMOVED")
    ok(len(hits(LIVE_LEAK)) >= 4, "fixture reproduces the live leak (%d patterns)" % len(hits(LIVE_LEAK)))
    cleaned = redact(LIVE_LEAK)
    ok(hits(cleaned) == [], "no posture pattern survives redaction")
    ok("WAF" not in cleaned and "GATE-ENFORCE" not in cleaned, "neither control is named")

    print("\nEVERYTHING ELSE SURVIVES")
    for keep in ("BEA v1.3.1", "Hetzner CPX32", "104 live listings",
                 "World Heritage layer 332 sites", "SOFT-to-PUBLIC Fri 29 Aug 2026"):
        ok(keep in cleaned, "kept: %s" % keep)

    print("\nIT RECURSES — A NEW FIELD CANNOT LEAK BY BEING ADDED LATER")
    payload = {"liveState": LIVE_LEAK,
               "nested": {"deep": ["fine", "the WAF is disabled"]},
               "stats": {"sellers": 59},
               "future_field": "origin gate is the only guard"}
    red = redact(payload)
    ok(hits(json.dumps(red, ensure_ascii=False)) == [], "no posture anywhere in a nested payload")
    ok(red["stats"]["sellers"] == 59, "non-string values pass through untouched")
    ok("fine" in red["nested"]["deep"], "clean list entries are kept")

    print("\nCLEAN TEXT IS NOT MANGLED")
    clean = "BEA v1.3.1 · 104 live listings · 59 sellers"
    ok(redact(clean) == clean, "a payload with no posture is returned byte-identical")

    print("\nTHE WIRING IS PRESENT")
    ok("_redact_posture(_payload)" in src, "the summary route actually calls the redactor")
    ok("_summary_caller_is_admin(x_admin_key, x_admin_token)" in src,
       "an authenticated caller still gets the unredacted text")
    ok('"redacted": "posture"' in src or '_payload["redacted"] = "posture"' in src,
       "the response says it was redacted rather than pretending to be complete")

    print("\nTHE LEDGER'S PATTERNS AND THIS HARNESS HAVE NOT DRIFTED")
    led = io.open(os.path.join(ROOT, "scripts", "regression_ledger.py"), encoding="utf-8").read()
    missing = [p for p in PATTERNS if p not in led]
    ok(not missing, "every pattern here is still in the ledger (%d)" % len(PATTERNS))

    bad = [l for c, l in checks if not c]
    print("\n%d/%d passed" % (len(checks) - len(bad), len(checks)))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
