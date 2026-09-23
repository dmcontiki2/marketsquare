"""BIT-EDGE-BLIND-1 (23 Sep 2026) -- proof that a CLOUDFLARE REFUSAL makes the BIT board
report NOT MEASURED, while a real 403 FROM THE APP still fails its marker.

WHAT WENT WRONG
---------------
The 23 Sep 19:00Z stand-up ran bit/bit_runner.py and got:

    [FAIL] S1 B-BEA-HEALTH   (functional) HTTP 403
    [FAIL] S2 B-BEA-DEMODATA (functional) HTTP 403
    ... 7 marker(s) need attention. Worst severity exit=2.

Measured in the same minute, from the same machine:
    curl  https://trustsquare.co/health          -> 200 {"status":"ok",...}
    urllib (this runner's client)                -> 403, Server: cloudflare,
                                                    body "error code: 1010"

Cloudflare error 1010 is its bad-User-Agent refusal and it fires on the default
"Python-urllib/3.x". The app was healthy the entire time. Every check in the runner
opens `if st != 200: return False, f"HTTP {st}"`, so one edge refusal became seven
convictions -- including an S1 -- and exit=2, which is a gate that blocks a deploy.

Swapping the UA for curl's, a browser's, or "TrustSquare-BIT" all returned 200. Only
the default was refused.

FOURTH INSTANCE OF ONE SHAPE, AND THIS FILE HAD NEVER INHERITED IT
------------------------------------------------------------------
RG-0187           an instrument that cannot RUN reads UNVERIFIED, never REGRESSION
RG-0401           a Cloudflare refusal is BLIND, never REGRESSED   (EDGE-BLIND-1/2)
RG-0420           an origin 502 makes a leg blind                  (UPSTREAM-BLIND-1)
LEDGER-VANTAGE-BLIND-1   an unmounted sibling project is blind     (same day)

THE TWO HALVES THIS TEST PINS
-----------------------------
1. Edge refuses (cloudflare + 1010)  -> NOT MEASURED, exit 3, no marker convicted.
2. App itself answers 403            -> still FAIL, exit 1/2, verdict intact.

Half 2 is the one that matters. A fix that made every 403 "blind" would pass half 1
and be strictly worse than the bug: the board would go quiet on a genuinely broken,
genuinely forbidden endpoint. So the test stands up a server that returns a PLAIN 403
and requires the convictions to survive it.

Run:  python3 scripts/test_bit_edge_blind1.py      (exit 0 = pass)
"""
import os, subprocess, sys, threading, json
from http.server import BaseHTTPRequestHandler, HTTPServer

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUNNER = os.path.join(REPO, "bit", "bit_runner.py")

SEEN_UA = []


def _handler(mode):
    class H(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.0"

        def log_message(self, *a):
            pass

        def do_GET(self):
            SEEN_UA.append(self.headers.get("User-Agent", ""))
            if mode == "cloudflare":
                body = (b"<html><head><title>Access denied</title></head><body>"
                        b"error code: 1010</body></html>")
                self.send_response(403)
                self.send_header("Server", "cloudflare")
                self.send_header("CF-RAY", "deadbeefcafe-JNB")
                self.send_header("Content-Type", "text/html")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            else:  # a real, app-issued 403 -- no cloudflare anywhere
                body = b'{"detail":"Forbidden"}'
                self.send_response(403)
                self.send_header("Server", "nginx")
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
    return H


def serve(mode):
    srv = HTTPServer(("127.0.0.1", 0), _handler(mode))
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, "http://127.0.0.1:%d" % srv.server_address[1]


def run_board(base):
    r = subprocess.run([sys.executable, RUNNER, "--base", base, "--json"],
                       capture_output=True, text=True, timeout=180, cwd=REPO)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main():
    bad = []

    # -- half 1: the edge refuses -> NOT MEASURED, never a conviction ------------------
    srv, base = serve("cloudflare")
    try:
        del SEEN_UA[:]
        code, out = run_board(base)
        if code != 3:
            bad.append("half 1: a cloudflare 1010 refusal exited %d, not 3 (NOT MEASURED). "
                       "The board is still converting its own blindness into a verdict. "
                       "output: %s" % (code, out.replace("\n", " ")[:220]))
        if "NOT MEASURED" not in out:
            bad.append("half 1: the board did not SAY it was not measured -- a silent skip "
                       "reads as news nobody has. output: %s" % out.replace("\n", " ")[:200])
        if '"state": "FAIL"' in out or "[FAIL]" in out:
            bad.append("half 1: markers were convicted on a read that never reached the app")
        # (a) the UA must not be the one Cloudflare refuses
        if any(ua.lower().startswith("python-urllib") for ua in SEEN_UA):
            bad.append("half 1: the runner still sends the default Python-urllib UA, which is "
                       "exactly what Cloudflare 1010 refuses")
        if not any("TrustSquare" in ua for ua in SEEN_UA):
            bad.append("half 1: the runner does not identify itself (no TrustSquare UA seen)")
    finally:
        srv.shutdown()

    # -- half 2: the APP says 403 -> still a real failure -----------------------------
    srv, base = serve("app403")
    try:
        code, out = run_board(base)
        if code == 3:
            bad.append("half 2: a plain app 403 was treated as an edge refusal -- the fix is "
                       "hiding real faults, which is worse than the bug it replaced")
        if code == 0:
            bad.append("half 2: a plain app 403 passed the board -- the markers were silenced")
        if "NOT MEASURED" in out:
            bad.append("half 2: an app-issued 403 reported NOT MEASURED")
        try:
            j = json.loads(out)
            if not [r for r in j.get("results", []) if r.get("state") == "FAIL"]:
                bad.append("half 2: no marker FAILed against a server that 403s everything")
        except Exception:
            pass
    finally:
        srv.shutdown()

    if bad:
        print("BIT-EDGE-BLIND-1: %d problem(s)" % len(bad))
        for b in bad:
            print("  FAIL  " + b)
        return 1
    print("BIT-EDGE-BLIND-1 ok -- a cloudflare refusal reports NOT MEASURED (exit 3) and names "
          "itself; an app-issued 403 still convicts its marker")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
