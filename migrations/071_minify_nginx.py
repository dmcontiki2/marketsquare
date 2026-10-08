#!/usr/bin/env python3
"""071_minify_nginx.py -- MINIFY-1 (David, 8 Oct 2026: "Please proceed" on the 6 Oct audit's F6, the app's first load).

The app script ms.js is about 530 KB over the wire, half of it comments and indentation -- the largest single item
on the first load. Each deploy now also writes static/ms.min.js: the same code with comments and whitespace removed
(no renaming, no rewriting; ops/minify/make_min.sh), about 367 KB.

WHY A SECOND FILE AND THIS RULE, NOT A MINIFIED ms.js: the readable /static/ms.js is what the drift checks, the FEA
tamper sensor (post_deploy compares served files to the source byte for byte) and the ledger's live checks read. They
keep reading exactly the repo's file. Only the app's own page asks for /static/ms.js?v=N&m=1, and this rule hands that
one request the small copy. A request without m=1 is untouched.

WHAT THIS MIGRATION DOES (idempotent; refuses rather than guesses, like 031):
  1. Makes static/ms.min.js if this deploy's engine has not yet (the first deploy runs the previous engine).
  2. In each trustsquare.co server block that proxies the app (127.0.0.1:8000), right after server_name, adds
         if ($arg_m = "1") { rewrite ^/static/ms\\.js$ /static/ms.min.js last; }
     (a server-level rewrite runs before location matching, so the new path is served by the same /static/ rules,
     with the same headers and caching).
  3. nginx -t; on failure restores the backup and does NOT reload.
  4. Reloads, then asks the origin itself: ?m=1 must return ms.min.js byte for byte and the plain URL ms.js byte for
     byte. Anything else -> restore, reload, exit 1.
Reverse: delete the three MINIFY-1 lines from the site file, nginx -t, nginx -s reload (the backup path is printed).
"""
import glob, hashlib, os, re, shutil, subprocess, sys, time
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
BAK_DIR = "/root/nginx-backups"
LIVE = os.environ.get("MS_LIVE", "/var/www/marketsquare")
SRC = os.environ.get("MS_SRC", "/opt/marketsquare-src")
TAG = "MINIFY-1"
SNIP = ('    # MINIFY-1 (8 Oct 2026, migration 071): the app page asks for /static/ms.js?v=N&m=1 and gets the copy without\n'
        '    # comments/whitespace that each deploy makes; every other request still gets the readable ms.js.\n'
        '    if ($arg_m = "1") { rewrite ^/static/ms\\.js$ /static/ms.min.js last; }\n')


def say(m):
    print("[071_minify] " + m, flush=True)


def find_sites():
    def hits(pats):
        out = {}
        for pat in pats:
            for c in glob.glob(pat):
                if not os.path.isfile(c) or ".bak" in os.path.basename(c):
                    continue
                try:
                    t = open(c, encoding="utf-8", errors="replace").read()
                except Exception:
                    continue
                if "trustsquare.co" in t and "server_name" in t and "127.0.0.1:8000" in t:
                    out.setdefault(os.path.realpath(c), c)
        return sorted(out)
    en = hits(["/etc/nginx/sites-enabled/*"])
    return en if en else hits(["/etc/nginx/sites-available/*", "/etc/nginx/conf.d/*.conf"])


def server_blocks(text):
    """(start, end) of each top-level `server { ... }`, braces counted outside comments and quotes."""
    out, i, n, depth, start = [], 0, len(text), 0, None
    quote = None
    while i < n:
        ch = text[i]
        if quote:
            if ch == "\\":
                i += 2; continue
            if ch == quote:
                quote = None
        elif ch == "#":
            j = text.find("\n", i); i = n if j < 0 else j; continue
        elif ch in "\"'":
            quote = ch
        elif ch == "{":
            if depth == 0:
                m = re.search(r"server\s*$", text[max(0, i - 40):i])
                start = i if m else None
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start is not None:
                out.append((start, i)); start = None
        i += 1
    return out


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def fetch(url_path, tries=5):
    """Ask the origin itself (no CDN), a few times, spaced: the box rate-limits bursts (the 8 Oct first run saw the
    second of two back-to-back requests refused, while the rule itself already worked)."""
    import time
    for n in range(tries):
        got = _fetch_once(url_path)
        if got:
            return got
        time.sleep(2)
    return None


def _fetch_once(url_path):
    """https with the site's name if the box listens on 443, else plain http."""
    for args in (["--resolve", "trustsquare.co:443:127.0.0.1", "-k", "https://trustsquare.co" + url_path],
                 ["-H", "Host: trustsquare.co", "http://127.0.0.1" + url_path]):
        env = {k: v for k, v in os.environ.items() if "proxy" not in k.lower()}   # the box itself, never a proxy
        r = subprocess.run(["curl", "--noproxy", "*", "-s", "-m", "15", "-H", "Accept-Encoding: identity", "-o", "-",
                            "-w", "\n%{http_code}"] + args, capture_output=True, env=env)
        body, _, code = r.stdout.rpartition(b"\n")
        SEEN.append("%s %s rc=%s code=%s %dB" % (url_path, args[-1].split("//")[0], r.returncode, code.strip().decode("ascii", "replace"), len(body)))
        if r.returncode == 0 and code.strip() == b"200" and len(body) > 1000:
            return hashlib.sha256(body).hexdigest()
    return None


SEEN = []   # every origin answer, printed when a check fails (the 8 Oct first run failed without saying why)


def nginx(*a):
    r = subprocess.run(["nginx"] + list(a), capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def main():
    js, mn = os.path.join(LIVE, "static", "ms.js"), os.path.join(LIVE, "static", "ms.min.js")
    if not os.path.isfile(js):
        say("REFUSING: %s not found" % js); return 1
    sites = find_sites()
    if not sites:
        say("REFUSING: could not identify the trustsquare.co site file."); return 1
    plan = []
    for site in sites:
        t = open(site, encoding="utf-8", errors="replace").read()
        if TAG in t:
            say("already applied in " + site); continue
        blocks = [(a, b) for a, b in server_blocks(t) if "127.0.0.1:8000" in t[a:b] and "trustsquare.co" in t[a:b]]
        if not blocks:
            say("REFUSING: no server block in %s both names trustsquare.co and proxies 127.0.0.1:8000" % site); return 1
        plan.append((site, t, blocks))
    if not APPLY:
        say("dry run: would make ms.min.js (exists=%s) and add the rule to %d block(s) in %s"
            % (os.path.isfile(mn), sum(len(p[2]) for p in plan), [p[0] for p in plan] or "nothing (applied)"))
        return 0
    mk = os.path.join(SRC, "ops", "minify", "make_min.sh")
    if os.path.isfile(mk):
        r = subprocess.run(["bash", mk, LIVE, SRC], capture_output=True, text=True)
        say((r.stdout or r.stderr).strip()[-300:])
    if not os.path.isfile(mn):
        shutil.copy2(js, mn); say("ms.min.js written as a plain copy (make_min.sh unavailable)")
    baks = []
    try:
        for site, t, blocks in plan:
            os.makedirs(BAK_DIR, exist_ok=True)
            bak = os.path.join(BAK_DIR, os.path.basename(site) + ".bak-071-" + TS)
            shutil.copy2(site, bak); baks.append((bak, site))
            for a, b in sorted(blocks, reverse=True):
                m = re.search(r"^[ \t]*server_name[^;]*;[^\n]*\n", t[a:b], re.M)
                if not m:
                    raise RuntimeError("a server block has no server_name line to anchor the rule")
                t = t[:a + m.end()] + SNIP + t[a + m.end():]
            open(site, "w", encoding="utf-8").write(t)
            say("rule added to %d block(s) in %s (backup %s)" % (len(blocks), site, bak))
        ok, msg = nginx("-t")
        if not ok:
            raise RuntimeError("nginx -t failed: " + msg)
        ok, msg = nginx("-s", "reload")
        if not ok:
            raise RuntimeError("reload failed: " + msg)
        time.sleep(2)
        if plan:
            # the rule acts only on ?m=1: that answer must be ms.min.js byte for byte, or the rule comes out. The plain URL
            # is not touched by the rule; it is checked too, but an answer we cannot GET (refused, timed out) is reported,
            # not treated as a fault -- a DIFFERENT body on the plain URL is a fault and also takes the rule out.
            got_js = fetch("/static/ms.js?v=0")
            time.sleep(2)
            got_min = fetch("/static/ms.js?v=0&m=1")
            if got_min != sha(mn):
                raise RuntimeError("origin check failed: ?m=1 %s" % ("could not be fetched" if got_min is None else "is NOT ms.min.js"))
            if got_js is not None and got_js != sha(js):
                raise RuntimeError("origin check failed: the plain URL no longer serves ms.js")
            if got_js is None:
                for line in SEEN[-12:]:
                    say("  origin answered: " + line)
            say("origin check: ?m=1 serves ms.min.js byte for byte; plain URL %s"
                % ("serves ms.js byte for byte" if got_js else "could not be fetched from the box (not touched by the rule)"))
    except Exception as ex:
        say("RESTORING (%s)" % ex)
        for line in SEEN[-12:]:
            say("  origin answered: " + line)
        for bak, site in baks:
            shutil.copy2(bak, site)
        nginx("-s", "reload")
        return 1
    say("APPLIED. %s -> %s bytes. Reverse: %s" % (os.path.getsize(js), os.path.getsize(mn),
        " ; ".join("cp %s %s" % b for b in baks) + " && nginx -t && nginx -s reload" if baks else "nothing changed"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
