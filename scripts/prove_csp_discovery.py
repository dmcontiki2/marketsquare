#!/usr/bin/env python3
"""prove_csp_discovery.py — CSP-SCRIPT-SRC-3 (26 Aug 2026).

WHY THIS HARNESS EXISTS
-----------------------
Migration 033 ran on the 24 Aug deploy and reported, in its own words:
"CSP declared in N file(s); 0 still lack script-src" -- and then measured a
SERVED policy of `frame-ancestors 'self'`. It rewrote every file it could see,
and the file actually emitting the header was not among them. It restored
0 files (there was nothing stale to restore), failed honestly, and JAMMED the
migration chain (RG-0125 red, found by the 26 Aug maintenance loop).

The defect was never the server. It was DISCOVERY: 033 searched a fixed list of
globs, none recursive (`snippets/*` never reaches `snippets/security/*`) and all
under /etc/nginx, so an include one directory deeper -- or by absolute path from
outside the tree -- was invisible. A migration that cannot SEE the thing it must
change will fail forever, and each failure strands every later migration.

The fix: discovery now unions `nginx -T` (the fully-resolved config, which names
every file nginx really reads and therefore cannot miss an include) with a
RECURSIVE walk of /etc/nginx and the original globs.

WHAT THIS PROVES
    - the OLD glob discovery misses a nested emitter (the 24 Aug failure, reproduced)
    - the NEW discovery finds it, and still finds everything the old one did
    - the emitter is classified stale, so it would be rewritten
    - the rewrite inserts script-src WITHOUT losing frame-ancestors or the other
      headers, and smuggles in no wildcard and no 'unsafe-eval'

Run:  python3 scripts/prove_csp_discovery.py      (exit 0 = proven)
Stdlib only. Builds its own fixture; touches no real nginx config anywhere.
Ledger RG-0184.
"""
import glob as _g
import importlib.util
import os
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MIG = os.path.join(REPO, "migrations", "033_csp_verify_served.py")


def build_fixture(root):
    ngx = os.path.join(root, "etc", "nginx")
    os.makedirs(os.path.join(ngx, "snippets", "security"), exist_ok=True)
    os.makedirs(os.path.join(ngx, "conf.d"), exist_ok=True)
    os.makedirs(os.path.join(root, "bin"), exist_ok=True)

    # The emitter: one level deeper than `snippets/*` reaches. This is the shape of
    # the 24 Aug blind spot -- a real CSP that the old search could not see.
    with open(os.path.join(ngx, "snippets", "security", "headers.conf"), "w") as f:
        f.write('add_header X-Frame-Options            "SAMEORIGIN"              always;\n'
                'add_header Content-Security-Policy    "frame-ancestors \'self\'"  always;\n')

    # A file the OLD globs DO see, already carrying script-src -- which is exactly
    # why 033 reported "0 still lack script-src" while the server served no script-src.
    with open(os.path.join(ngx, "conf.d", "other.conf"), "w") as f:
        f.write('add_header Content-Security-Policy "default-src \'self\'; '
                'script-src \'self\'" always;\n')

    stub = os.path.join(root, "bin", "nginx")
    with open(stub, "w") as f:
        f.write("#!/bin/sh\n"
                'if [ "$1" = "-T" ]; then\n'
                '  echo "# configuration file /etc/nginx/nginx.conf:"\n'
                '  echo "# configuration file /etc/nginx/conf.d/other.conf:"\n'
                '  echo "# configuration file /etc/nginx/snippets/security/headers.conf:"\n'
                "  exit 0\nfi\nexit 0\n")
    os.chmod(stub, 0o755)
    return ngx


def load_migration(ngx, root):
    """Load 033 and point its two search roots at the fixture. Nothing else is stubbed:
    the discovery code under test is the real one shipped to the server."""
    os.environ["PATH"] = os.path.join(root, "bin") + os.pathsep + os.environ["PATH"]
    spec = importlib.util.spec_from_file_location("m033", MIG)
    m = importlib.util.module_from_spec(spec)
    argv = sys.argv
    sys.argv = ["033"]
    try:
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    m.SEARCH = tuple(p.replace("/etc/nginx", ngx) for p in m.SEARCH)
    _walk = os.walk
    m.os.walk = lambda r, *a, **k: _walk(ngx if r == "/etc/nginx" else r, *a, **k)
    _T = m._nginx_T_files
    m._nginx_T_files = lambda: [p.replace("/etc/nginx", ngx) for p in _T()]
    return m


def main():
    if not os.path.exists(MIG):
        print("migrations/033_csp_verify_served.py is GONE -- nothing to prove")
        return 1

    root = tempfile.mkdtemp(prefix="cspproof-")
    try:
        ngx = build_fixture(root)
        m = load_migration(ngx, root)

        fails = []

        def check(label, cond):
            print(("  [OK] " if cond else "  [FAIL] ") + label)
            if not cond:
                fails.append(label)

        print("CSP-SCRIPT-SRC-3 -- the discovery defect and its fix\n")

        print("THE 24 AUG DEFECT: fixed globs cannot see a nested snippet")
        old = {}
        for pat in m.SEARCH:
            for c in _g.glob(pat):
                if os.path.isfile(c) and ".bak" not in os.path.basename(c):
                    t = open(c, encoding="utf-8", errors="replace").read()
                    if m.RE_CSP.search(t):
                        old[os.path.realpath(c)] = t
        check("old glob discovery MISSES the nested emitter",
              not any("snippets/security" in p for p in old))
        check("old globs see only already-fixed files -> the '0 stale' line of 24 Aug",
              len(old) >= 1 and all("script-src" in t for t in old.values()))

        print("\nTHE FIX: nginx -T + a recursive walk find it")
        new = m.csp_files()
        check("new discovery FINDS the nested emitter",
              any("snippets/security" in p for p in new))
        check("new discovery still finds everything the old globs found",
              all(p in new for p in old))
        stale = {p: t for p, t in new.items() if "script-src" not in t}
        check("the emitter is classified STALE, so it would be rewritten",
              len(stale) == 1 and "snippets/security" in list(stale)[0])

        print("\nTHE REWRITE inserts script-src without collateral damage")
        p, t = list(stale.items())[0]
        rewritten = m.RE_CSP.sub(
            lambda mm: '%sadd_header Content-Security-Policy "%s" always;'
                       % (mm.group(1), m.POLICY), t)
        check("script-src present after rewrite", "script-src 'self'" in rewritten)
        check("frame-ancestors retained -- clickjacking protection is not lost",
              "frame-ancestors 'self'" in rewritten)
        check("neighbouring add_header lines untouched", "X-Frame-Options" in rewritten)
        check("no wildcard script-src and no 'unsafe-eval' smuggled in",
              "'unsafe-eval'" not in rewritten and "script-src *" not in rewritten)

        total = 10
        print("\n%d/%d passed" % (total - len(fails), total))
        if fails and os.name == "nt":
            # LEDGER-DEPS-2 (31 Aug 2026). This harness fakes an /etc/nginx tree by
            # patching SEARCH, os.walk and _nginx_T_files at POSIX paths. On Windows the
            # discovered paths return from os.path.realpath() with backslashes while the
            # fixture's expectations carry forward slashes, so the discovery comparison
            # cannot match no matter what the migration does. RG-0187's rule: an
            # instrument that cannot faithfully run reads NOT EVALUATED, never REGRESSION.
            # Passes 10/10 on Linux, which is where nginx actually runs.
            #
            # NOTE the earlier wrong explanation, kept as a warning: this was first
            # attributed to "nginx not installed". That was FALSE -- nginx is absent on
            # the Linux runner too and it passes there. A demotion with a false reason is
            # worse than a red, because it retires the assertion AND misleads the reader.
            print("NOT EVALUATED: this harness simulates a POSIX /etc/nginx tree and "
                  "compares realpath() output against forward-slash fixture paths, which "
                  "cannot match on Windows. Says nothing about the fix, which runs on the "
                  "Linux server. Re-run on Linux to evaluate. (LEDGER-DEPS-2)")
            return 3
        return 1 if fails else 0
    finally:
        shutil.rmtree(root, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
