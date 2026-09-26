#!/usr/bin/env python3
"""EDGE-STATUS-BLIND-1 (26 Sep 2026) -- red on the pre-fix source, green on the fix.

What was broken: scripts/regression_ledger.py's _get() has told a Cloudflare edge refusal
from an app answer since EDGE-BLIND-1 (18 Sep), but _status(), _post_status() and
_headers() did not. Each handed Cloudflare's own 403 back as though the APP had answered.
Two-sided damage, both proven below:

  (a) FALSE CONVICTION  -- an entry asserting "/health must answer 200" reads 403 and
      prints "previously-fixed issue HAS COME BACK. Do not deploy over this" over a
      healthy site. RG-0028 did exactly this on the 25 Sep board.
  (b) FALSE ACQUITTAL   -- an entry asserting "this admin route must refuse anonymous
      callers" reads the edge's 403 and PASSES without the app ever being reached, which
      is the same hole QA-GATE-BLIND-1 found in the deploy gate a day earlier.

RG-0401 (LOCKED, 18 Sep 2026) already rules this: an edge refusal is BLIND, never
REGRESSED. This test asserts the rule now holds on all four readers, and that a 401/403
the APP produced is still returned unchanged, so no negative entry is weakened.

Run:  python3 scripts/test_edge_status_blind1.py
"""
import io
import os
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

FAILS = []


def check(name, ok, detail=""):
    print(("  PASS  " if ok else "  FAIL  ") + name + (("  -- " + detail) if detail and not ok else ""))
    if not ok:
        FAILS.append(name)


class FakeErr(urllib.error.HTTPError):
    def __init__(self, code, body=b"", server=None):
        hdrs = {}
        if server:
            hdrs["Server"] = server
        urllib.error.HTTPError.__init__(self, "https://trustsquare.co/x", code, "err", hdrs, None)
        self._body = body

    def read(self):
        return self._body


def main():
    src = io.open(os.path.join(HERE, "regression_ledger.py"), encoding="utf-8").read()

    print("EDGE-STATUS-BLIND-1")
    print("source shape (the fix must exist as ONE writer, not four copies):")
    check("_edge_refused() exists", "def _edge_refused(" in src)
    check("_status() consults it", src.count("blind = _edge_refused(e)") >= 3,
          "found %d call sites, want >=3 (_status, _post_status, _headers)"
          % src.count("blind = _edge_refused(e)"))

    if FAILS:
        # Do not stop at the shape -- SHOW the damage on this source, in its own words,
        # so the entry cannot be waved away as a style preference.
        print("\nPRE-FIX SOURCE -- the damage, measured on this very file:")
        import regression_ledger as rl
        saved = urllib.request.urlopen

        def fake_open(req, timeout=None):
            raise FakeErr(403, b"error code: 1010\n", server="cloudflare")

        urllib.request.urlopen = fake_open
        try:
            rl._cache.clear()
            try:
                print("    _status('/health') with Cloudflare refusing the client -> %r"
                      % (rl._status("/health"),))
                print("      (a) FALSE CONVICTION: an entry asserting /health == 200 now FAILs "
                      "and the board prints 'Do not deploy over this' over a healthy site.")
            except Exception as ex:
                print("    _status('/health') raised %r" % (ex,))
            try:
                print("    _post_status('/admin/flags') with the same refusal -> %r"
                      % (rl._post_status("/admin/flags"),))
                print("      (b) FALSE ACQUITTAL: an entry asserting this route refuses "
                      "anonymous callers PASSES without the app ever being reached.")
            except Exception as ex:
                print("    _post_status('/admin/flags') raised %r" % (ex,))
        finally:
            urllib.request.urlopen = saved
            rl._cache.clear()
        print("\nRED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1

    import regression_ledger as rl

    print("behaviour:")

    # 1. A Cloudflare-signed 403 is BLIND, not a status code.
    edge = FakeErr(403, b"error code: 1010\n", server="cloudflare")
    check("Cloudflare-signed 403 reads BLIND", bool(rl._edge_refused(edge)))

    # 2. An APP 403 carries no edge marker and is returned unchanged.
    app403 = FakeErr(403, b'{"detail":"Admin credentials required.","code":"admin_required"}')
    check("app 403 is NOT called blind (negative entries keep their teeth)",
          rl._edge_refused(app403) == "")

    # 3. An app 401 likewise.
    app401 = FakeErr(401, b'{"detail":"Sign-in required."}')
    check("app 401 is NOT called blind", rl._edge_refused(app401) == "")

    # 4. Origin 5xx stays OUT of this helper -- UPSTREAM-BLIND-1 keeps it in _get() alone,
    #    so "this endpoint must not 5xx" entries are untouched.
    check("origin 502 not swallowed here", rl._edge_refused(FakeErr(502, b"bad gateway")) == "")

    # 5. The whole point: _status() must RAISE on a signed edge refusal, so the caller
    #    cannot turn it into a verdict.
    saved = urllib.request.urlopen

    def fake_open(req, timeout=None):
        raise FakeErr(403, b"error code: 1010\n", server="cloudflare")

    urllib.request.urlopen = fake_open
    try:
        rl._cache.clear()
        try:
            got = rl._status("/health")
            check("_status() raises ProbeOffline on an edge refusal", False,
                  "returned %r instead of raising -- this is the false conviction" % got)
        except rl.ProbeOffline:
            check("_status() raises ProbeOffline on an edge refusal", True)
        try:
            got = rl._post_status("/admin/flags")
            check("_post_status() raises ProbeOffline on an edge refusal", False,
                  "returned %r -- this is the false acquittal" % got)
        except rl.ProbeOffline:
            check("_post_status() raises ProbeOffline on an edge refusal", True)
        try:
            rl._cache.clear()
            got = rl._headers("/health")
            check("_headers() raises ProbeOffline on an edge refusal", False,
                  "returned %r" % (got,))
        except rl.ProbeOffline:
            check("_headers() raises ProbeOffline on an edge refusal", True)
    finally:
        urllib.request.urlopen = saved
        rl._cache.clear()

    # 6. An APP 403 still comes back as 403 from _status() -- not weakened.
    def fake_app403(req, timeout=None):
        raise FakeErr(403, b'{"code":"admin_required"}')

    urllib.request.urlopen = fake_app403
    try:
        check("_status() still returns 403 for an APP refusal", rl._status("/dashboard/bit") == 403)
    except rl.ProbeOffline as ex:
        check("_status() still returns 403 for an APP refusal", False, "went blind: %s" % ex)
    finally:
        urllib.request.urlopen = saved

    print("")
    if FAILS:
        print("RED: %d check(s) failed -- %s" % (len(FAILS), ", ".join(FAILS)))
        return 1
    print("GREEN: an edge refusal is BLIND on all four readers; an app 401/403 and an "
          "origin 5xx are unchanged.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
