#!/usr/bin/env python3
"""prove_csp_settle.py — CSP-SCRIPT-SRC-6 (26 Aug 2026).

WHY THIS HARNESS EXISTS
-----------------------
Migration 033 has now failed FOUR deploys in a row, each failure a different
bug in the same organ -- not in the rewrite it performs, but in the way it
MEASURES whether the rewrite took:

    CSP-SCRIPT-SRC-3  it could not SEE the emitting file      (discovery)
    CSP-SCRIPT-SRC-4  it compared prose, not directives       (staleness)
    CSP-SCRIPT-SRC-5  it measured a 301, not the page         (vantage)
    CSP-SCRIPT-SRC-6  it polled for a STABLE answer, not the  (settling)
                      EXPECTED one                              <- this one

The 26 Aug 04:05Z failure: the settle loop's exit condition was "the value
stopped changing". A stale nginx worker still serving the OLD policy answers
with the SAME value every time, so the loop was satisfied on its second read,
~1 second after the reload -- and returned exactly the value it had been asked
to wait for the reload to replace. `settle=15` bought nothing at all. The
migration then restored a correct rewrite and jammed the chain (RG-0125 red).

CLASS -- and this is the point of the harness, not the instance:
POLL FOR THE EXPECTED STATE, NEVER FOR A STABLE ONE. A steady wrong answer is
indistinguishable from a settled right one, so "it stopped changing" can never
be the exit condition of a verification poll. Any future poll written anywhere
in this project inherits that rule.

Second half, same failure: the one line naming the measured value was line -4
of 033's output, and post_deploy.sh captured `tail -n 3 | cut -c1-300`. So the
evidence existed and the report structurally could not carry it -- four reports
that all said "something else is emitting the header" and none that said what
was actually served. A failure that cannot be diagnosed from its own report is
a defect in the report (POSTDEPLOY-EYES-3).

WHAT THIS PROVES
    - the OLD settle loop returns the STALE value while the reload is still
      landing (the 26 Aug failure, reproduced deterministically)
    - the NEW loop keeps polling and returns the policy once it appears
    - it does NOT burn the whole settle window when the answer is right first read
    - it still fails LOUDLY on a redirect (CSP-SCRIPT-SRC-5 is not regressed)
    - the failure message LEADS with the measured value, and post_deploy.sh's
      capture window is wide enough to carry it

Run:  python3 scripts/prove_csp_settle.py      (exit 0 = proven)
Stdlib only. Calls no network, touches no nginx config, reads no server.
Ledger RG-0191.
"""
import importlib.util
import os
import re
import sys
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = os.path.join(REPO, "migrations", "033_csp_verify_served.py")
POST_DEPLOY = os.path.join(REPO, "ops", "autodeploy", "post_deploy.sh")

OLD_CSP = "frame-ancestors 'self'"
NEW_CSP = ("default-src 'self'; script-src 'self' 'unsafe-inline' "
           "https://unpkg.com; frame-ancestors 'self'")

fails = []


def check(label, ok):
    print(("  PASS  " if ok else "  FAIL  ") + label)
    if not ok:
        fails.append(label)


def load_migration():
    spec = importlib.util.spec_from_file_location("mig033", MIG)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def scripted(seq):
    """A fake _csp_once that yields `seq` values, repeating the last forever."""
    calls = {"n": 0}

    def _fake(port, use_tls):
        i = min(calls["n"], len(seq) - 1)
        calls["n"] += 1
        v = seq[i]
        if isinstance(v, int):          # an int means "answer with this HTTP status"
            return v, ""
        return 200, v
    return _fake, calls


def old_settle_loop(csp_once, settle):
    """The 25 Aug implementation, verbatim in behaviour. The subject of the proof."""
    deadline = time.time() + settle
    last = None
    while True:
        status, val = csp_once(443, True)
        if 300 <= status < 400:
            return "ERROR:https-also-redirected(%d)" % status
        if val and val != last:
            last = val
            if time.time() < deadline:
                time.sleep(0.05)
                continue
        return val


def main():
    m = load_migration()

    print("THE BUG: a stale worker answers the same wrong value every time")
    # Four reads of the OLD policy, then the reload finally lands.
    seq = [OLD_CSP, OLD_CSP, OLD_CSP, OLD_CSP, NEW_CSP]
    fake, _ = scripted(seq)
    got = old_settle_loop(fake, settle=5)
    check("old loop returns the STALE policy -- 'stopped changing' fired on read 2",
          got == OLD_CSP and "script-src" not in got)

    print("\nTHE FIX: poll for the EXPECTED state")
    fake, calls = scripted(seq)
    m._csp_once = fake
    t0 = time.time()
    got = m.served_csp(settle=20)
    check("new loop waits out the stale reads and returns the real policy",
          "script-src" in got)
    check("it kept reading until the value ARRIVED (>=5 reads, not 2)",
          calls["n"] >= 5)
    check("and it did not sit out the whole settle window once it had the answer",
          time.time() - t0 < 15)

    print("\nIT DOES NOT WASTE THE WINDOW WHEN THE ANSWER IS RIGHT FIRST READ")
    fake, calls = scripted([NEW_CSP])
    m._csp_once = fake
    t0 = time.time()
    got = m.served_csp(settle=30)
    check("returns immediately on a first-read hit", "script-src" in got)
    check("one read, no sleeping", calls["n"] == 1 and time.time() - t0 < 2)

    print("\nCSP-SCRIPT-SRC-5 IS NOT REGRESSED: a redirect still fails loudly")
    fake, _ = scripted([301])
    m._csp_once = fake
    got = m.served_csp(settle=0)
    check("a 3xx is reported as an ERROR, never measured as if it were the page",
          got.startswith("ERROR:") and "redirect" in got)

    print("\nTHE MEASUREMENT PATH ACTUALLY RUNS (CSP-SCRIPT-SRC-7)")
    # The operative cause of ALL FOUR 033 failures: HTTPSConnection was handed a
    # `server_hostname=` keyword it does not accept, so every :443 attempt died on the
    # CONSTRUCTOR before a packet moved, fell through to the :80 fallback, and measured the
    # very 301 the previous fix existed to stop measuring. Two days invisible, because the
    # report window cut the line that named it. CLASS: a call signature is only proven by
    # CALLING it -- point the real function at a dead port and demand a CONNECTION error.
    # A TypeError there means the code cannot work anywhere, on any server, ever.
    import http.client as _hc, inspect as _inspect
    params = list(_inspect.signature(_hc.HTTPSConnection.__init__).parameters)
    check("HTTPSConnection genuinely has no server_hostname parameter (the trap is real)",
          "server_hostname" not in params)
    # COMMENT-VS-CODE, the THIRD instance of this class today (after the nginx CSP comment
    # in 033 and the REM line in add_secret.bat): the comment above the fix quotes the very
    # call it removed, and a naive search matched the explanation instead of the code. Strip
    # comment lines and assert against CODE only -- that is what the claim is about.
    src_mig = "\n".join(ln for ln in open(MIG, encoding="utf-8").read().splitlines()
                        if not ln.lstrip().startswith("#"))
    check("033 no longer passes server_hostname to the HTTPSConnection constructor",
          not re.search(r"HTTPSConnection\([^)]*server_hostname", src_mig, re.S))
    m2 = load_migration()
    errs = {}
    for tls in (True, False):
        try:
            m2._csp_once(44399, tls)      # nothing listens here
            errs[tls] = "unexpected-success"
        except TypeError as ex:
            errs[tls] = "TypeError:" + str(ex)[:60]
        except (ConnectionError, OSError):
            errs[tls] = "connection-error"
    check("the TLS measurement path constructs cleanly (connection error, never TypeError)",
          errs[True] == "connection-error")
    check("the plain path constructs cleanly too", errs[False] == "connection-error")

    print("\nTHE FAILURE IS DIAGNOSABLE FROM ITS OWN REPORT")
    src = open(MIG, encoding="utf-8").read()
    check("the raise LEADS with the measured value (survives a head-truncated window)",
          re.search(r'raise RuntimeError\(\s*"MEASURED=%r', src) is not None)
    check("the stale-exit condition is gone from the shipped migration",
          "value changed -- let the reload finish settling" not in src)
    sh = open(POST_DEPLOY, encoding="utf-8").read()
    # anchor on the FAILING step -- the succeeding step also runs a tail|cut and a
    # loose regex matches that one first (tail -n 1 | cut -c1-200) and proves nothing.
    mm = re.search(r'CHAIN JAMMED HERE.*?tail -n (\d+) "\$MOUT".*?cut -c1-(\d+)', sh)
    check("post_deploy.sh captures >=12 lines and >=1200 chars of a failing migration",
          mm is not None and int(mm.group(1)) >= 12 and int(mm.group(2)) >= 1200)
    check("post_deploy.sh strips backslashes as well as quotes (JSON safety)",
          mm is not None and re.search(r"tr -d '\"\\\\'", sh) is not None)

    total = 15
    print("\n%d/%d passed" % (total - len(fails), total))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
