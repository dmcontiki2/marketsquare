#!/usr/bin/env python3
"""
human_view_verify.py - Orchestration v2 . the "see what the human sees" gate.

WHY THIS EXISTS
---------------
The recurring pain (heritage broken link + video non-conformance taking 5+ AI<->human
iterations) has ONE root cause: the fix loop verifies at the SOURCE layer (file edited,
server returns the new bytes), but the human checks the SCREEN layer (the page Cloudflare
serves into the browser, after caching). Between those two layers sit the CDN cache and the
browser/render. A fix can be byte-correct at the source AND still look broken on screen,
because a stale CDN copy is being served. The loop honestly reports "fixed"; David honestly
sees "still broken"; round and round. THAT gap is the iterations.

THE RULE THIS ENFORCES
----------------------
A fix is not "done" when the file is right. A fix is "done" when the LIVE, PURGED, rendered
result a human would load is right. So this verifier:

  1. PURGES the CDN cache first (so a correct fix can never be masked by a stale copy).
  2. FETCHES through the live CDN exactly as a browser does (not the origin, not the file).
  3. ASSERTS on the fetched result the same thing the human's eyes assert:
        - link  : the href resolves to 200 + real content (not a 404/410/parked page).
        - asset : the css/js/video/image URL returns 200 + the expected content-type & size.
        - text  : the expected string is actually present in the served HTML.
        - render: (tier 2, optional) the element is present/plays in a real browser.
  4. On RED, CAPTURES EVIDENCE (the live HTTP facts, a saved copy of the served body) so the
     human gets a 5-second yes/no with proof attached - not a hunt, not another round trip.

TIERING (the "most complete, but not slow on every item" design)
  tier 1  HTTP-through-CDN   - cheap, runs on EVERY fault. Catches the stale-cache/dead-link
                               failure mode that is causing today's iterations.
  tier 2  headless render    - auto-used for video/visual faults when a browser is available
                               (Claude-in-Chrome on David's machine is the ideal tier-2 host).
                               Optional by design: the loop never DEPENDS on a sandbox browser.

This module is deterministic and zero-token. It changes nothing on the server except issuing
the cache purge it is explicitly asked to issue.

USAGE
  # a heritage link fix - is the live link really good now, after purge?
  human_view_verify.py --purge --check link --url https://trustsquare.co/... \
      --expect-status 200 --expect-contains "Robben Island"

  # a video/asset fix - is the live asset really served, right type, non-trivial size?
  human_view_verify.py --purge --check asset --url https://trustsquare.co/static/intro.mp4 \
      --expect-status 200 --expect-content-type video/mp4 --min-bytes 10000

  # a page-text fix - does the served HTML actually contain the corrected string?
  human_view_verify.py --purge --check text --url https://trustsquare.co/ \
      --expect-contains 'ms.js?v=179'

  # batch: a JSON list of checks (used by the fix loop) -> one GREEN/RED verdict + evidence
  human_view_verify.py --batch checks.json

Exit code 0 = GREEN (every check passed at the human's layer). Non-zero = RED (with evidence).
"""
import argparse, json, os, sys, time, datetime, urllib.request, urllib.error, ssl

PURGE_ENDPOINT = "https://trustsquare.co/admin/purge-cache"   # POST-only (CLAUDE.md: GET fails)
TIMEOUT = 12
RETRIES = 2
EVIDENCE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_evidence")
DEAD = {404, 410}
# A page that returns 200 but is actually a soft-404 / parked / error shell. Cheap heuristics
# so "200 but the human sees nothing" can't pass as green.
SOFT_FAIL_MARKERS = ("page not found", "404", "not found", "error 410", "this listing is no longer",
                     "domain is parked", "account suspended")


def now():
    return datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ctx():
    # honour normal verification; do not silently accept broken TLS
    return ssl.create_default_context()


def purge_cdn():
    """Issue the BEA cache purge so the next fetch can't be served a stale copy."""
    try:
        req = urllib.request.Request(PURGE_ENDPOINT, method="POST", data=b"",
                                     headers={"User-Agent": "human-view-verify"})
        code = urllib.request.urlopen(req, timeout=TIMEOUT, context=_ctx()).status
        # give the edge a beat to evict before we re-fetch
        time.sleep(2.0)
        return {"purged": code in (200, 204), "status": code}
    except Exception as e:
        return {"purged": False, "error": e.__class__.__name__ + ": " + str(e)}


def fetch(url, method="GET"):
    """Fetch THROUGH the live CDN, as a browser would. Cache-busting request headers so we
    read what is actually published, never an intermediary's stale copy."""
    last = None
    for attempt in range(RETRIES + 1):
        try:
            req = urllib.request.Request(url, method=method, headers={
                "User-Agent": "Mozilla/5.0 (human-view-verify)",
                "Cache-Control": "no-cache", "Pragma": "no-cache"})
            r = urllib.request.urlopen(req, timeout=TIMEOUT, context=_ctx())
            body = r.read() if method == "GET" else b""
            return {"status": r.status, "headers": dict(r.headers), "body": body,
                    "cf_cache": r.headers.get("CF-Cache-Status", "")}
        except urllib.error.HTTPError as e:
            # a real permanent code is a real answer - return it, don't retry
            if e.code in DEAD or e.code < 500:
                return {"status": e.code, "headers": dict(e.headers or {}),
                        "body": (e.read() if method == "GET" else b""), "cf_cache": ""}
            last = e.code
        except Exception as e:
            last = e.__class__.__name__
        time.sleep(0.6 * (attempt + 1))
    return {"status": None, "error": last, "headers": {}, "body": b"", "cf_cache": ""}


def _soft_failed(body_text):
    low = body_text[:4000].lower()
    return next((m for m in SOFT_FAIL_MARKERS if m in low), None)


def check_one(c):
    """Run a single check at the human's layer. Returns a verdict dict with evidence."""
    kind = c.get("check", "link")
    url = c["url"]
    want_status = c.get("expect_status", 200)
    res = fetch(url, method="GET")
    status = res.get("status")
    body = res.get("body", b"") or b""
    try:
        text = body.decode("utf-8", "replace")
    except Exception:
        text = ""
    reasons, ok = [], True

    if status != want_status:
        ok = False
        reasons.append("status %s (wanted %s)" % (status, want_status))

    if status == want_status and want_status == 200:
        soft = _soft_failed(text)
        if soft and kind in ("link", "text"):
            ok = False
            reasons.append("200 but soft-fail marker present: %r (human would see an error page)" % soft)

    need = c.get("expect_contains")
    if need:
        if need not in text:
            ok = False
            reasons.append("served body is MISSING expected text %r (the fix is not on the live page)" % need)

    nope = c.get("expect_absent")
    if nope and nope in text:
        ok = False
        reasons.append("served body STILL contains %r (the broken content is still live)" % nope)

    if kind == "asset":
        ct = res.get("headers", {}).get("Content-Type", "")
        want_ct = c.get("expect_content_type")
        if want_ct and want_ct not in ct:
            ok = False
            reasons.append("content-type %r (wanted %r)" % (ct, want_ct))
        min_b = c.get("min_bytes")
        n = len(body)
        if min_b and n < min_b:
            ok = False
            reasons.append("only %d bytes (wanted >= %d - likely an error stub, not the real asset)" % (n, min_b))

    verdict = {
        "label": c.get("label", url),
        "check": kind, "url": url,
        "result": "GREEN" if ok else "RED",
        "live_status": status,
        "cf_cache": res.get("cf_cache", ""),
        "content_type": res.get("headers", {}).get("Content-Type", ""),
        "bytes": len(body),
        "reasons": reasons,
        "needs_render_tier2": kind in ("video", "render"),
    }
    if not ok:
        verdict["evidence"] = _save_evidence(c.get("label", url), url, res, text)
    return verdict


def _save_evidence(label, url, res, text):
    """On RED, persist the live facts + a copy of the served body so the human gets proof,
    not a request to go look again."""
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    safe = "".join(ch if ch.isalnum() else "_" for ch in label)[:60] or "evidence"
    stamp = now().replace(":", "").replace("-", "")
    base = os.path.join(EVIDENCE_DIR, "%s_%s" % (safe, stamp))
    facts = {"captured_at": now(), "url": url, "status": res.get("status"),
             "cf_cache": res.get("cf_cache", ""),
             "content_type": res.get("headers", {}).get("Content-Type", ""),
             "bytes": len(res.get("body", b"") or b"")}
    with open(base + ".json", "w", encoding="utf-8") as f:
        json.dump(facts, f, indent=2)
    # a trimmed copy of what was actually served - this is "what the human saw"
    with open(base + ".served.txt", "w", encoding="utf-8") as f:
        f.write(text[:8000])
    return {"facts": base + ".json", "served_body": base + ".served.txt"}


def run(checks, do_purge):
    out = {"schema": "human-view-verify-v1", "at": now(), "purge": None, "checks": [], "result": "GREEN"}
    if do_purge:
        out["purge"] = purge_cdn()
    for c in checks:
        v = check_one(c)
        out["checks"].append(v)
        if v["result"] == "RED":
            out["result"] = "RED"
    out["summary"] = {
        "total": len(out["checks"]),
        "green": sum(1 for v in out["checks"] if v["result"] == "GREEN"),
        "red": sum(1 for v in out["checks"] if v["result"] == "RED"),
        "render_pending": [v["label"] for v in out["checks"] if v.get("needs_render_tier2") and v["result"] == "GREEN"],
    }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--purge", action="store_true", help="purge the CDN before fetching (recommended)")
    ap.add_argument("--check", choices=["link", "asset", "text", "video", "render"], default="link")
    ap.add_argument("--url")
    ap.add_argument("--label", default="")
    ap.add_argument("--expect-status", type=int, default=200)
    ap.add_argument("--expect-contains", default="")
    ap.add_argument("--expect-absent", default="")
    ap.add_argument("--expect-content-type", default="")
    ap.add_argument("--min-bytes", type=int, default=0)
    ap.add_argument("--batch", help="path to a JSON file: a list of check objects")
    ap.add_argument("--json", action="store_true", help="emit the full verdict as JSON")
    a = ap.parse_args()

    if a.batch:
        checks = json.load(open(a.batch, encoding="utf-8"))
        if isinstance(checks, dict):
            checks = checks.get("checks", [])
    elif a.url:
        c = {"check": a.check, "url": a.url, "label": a.label or a.url, "expect_status": a.expect_status}
        if a.expect_contains: c["expect_contains"] = a.expect_contains
        if a.expect_absent: c["expect_absent"] = a.expect_absent
        if a.expect_content_type: c["expect_content_type"] = a.expect_content_type
        if a.min_bytes: c["min_bytes"] = a.min_bytes
        checks = [c]
    else:
        ap.error("give --url ... or --batch checks.json")

    out = run(checks, a.purge)

    if a.json:
        print(json.dumps(out, indent=2))
    else:
        p = out.get("purge")
        if p is not None:
            print("purge: %s" % ("OK" if p.get("purged") else "FAILED %s" % p))
        print("HUMAN-VIEW VERIFY: %s  (%d green / %d red of %d)" %
              (out["result"], out["summary"]["green"], out["summary"]["red"], out["summary"]["total"]))
        for v in out["checks"]:
            line = "  [%-5s] %-6s %s  -> live=%s cf=%s %s" % (
                v["result"], v["check"], v["label"], v["live_status"], v["cf_cache"] or "-",
                v.get("content_type", ""))
            print(line)
            for r in v["reasons"]:
                print("           - " + r)
            if v.get("evidence"):
                print("           evidence: %s" % v["evidence"]["served_body"])
        if out["summary"]["render_pending"]:
            print("  note: tier-2 render check recommended for: %s"
                  % ", ".join(out["summary"]["render_pending"]))
    return 0 if out["result"] == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
