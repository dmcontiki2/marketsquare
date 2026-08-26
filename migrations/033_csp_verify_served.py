#!/usr/bin/env python3
"""033_csp_verify_served.py — CSP-SCRIPT-SRC-2 (25 Aug 2026).

WHY THERE IS A 033 WHEN 031 SAID "ok"
-------------------------------------
Migration 031 ran on the 24 Aug 22:47 deploy and recorded result "ok". Half of
it worked: the index went from serving NO security headers to serving all five
(the `location = /` include landed — INDEX-HEADERS-1 is genuinely closed).

The other half did not take. The served policy on / and /terms is still
`frame-ancestors 'self'` with no script-src, measured after the deploy.

031's mistake is the exact class this project keeps relearning, and it is mine:
IT DECLARED SUCCESS FROM THE WRITE, NOT FROM A PROBE. It asserted the string
landed in the file it had chosen, ran `nginx -t`, reloaded, and reported ok —
without ever asking the server what it now actually serves. A file write is
READ-grade evidence. Only the response is PROBED. 031 also globbed
/etc/nginx/*.conf, snippets/, conf.d/ and includes/ but NOT sites-enabled/ or
sites-available/, so a CSP declared in the vhost itself was never a candidate,
and a second add_header at a level nginx prefers will quietly win.

WHAT 033 DOES DIFFERENTLY
  1. Finds EVERY add_header Content-Security-Policy under /etc/nginx —
     sites-enabled and sites-available included this time — and rewrites each
     one that lacks script-src. Multiple definitions are normal, not a reason
     to refuse; the refusal in 031 was aimed at the wrong risk.
  2. nginx -t, restore-on-failure, reload — as before.
  3. THEN PROVES IT. Fetches http://127.0.0.1/ with a Host header and reads the
     Content-Security-Policy off the RESPONSE. If script-src is not in what the
     server actually returns, it RESTORES every backup, reloads, and exits 1.
     A migration that cannot prove its own effect must not claim it.

The policy is unchanged from 031 — inventoried, not guessed. script-src allows
'self', 'unsafe-inline' (the ~163 inline onclick handlers), unpkg.com and
cdnjs.cloudflare.com (Leaflet, static and dynamic). No 'unsafe-eval', no
wildcard. tp-em.com and every other affiliate host is refused by the BROWSER.

REVERSING IT: the exact per-file rollback commands are printed on apply.
VERIFY:  curl -sI 'https://trustsquare.co/?cb=1' | grep -i content-security
Ledger RG-0178 asserts the served header, on both the index and an app path.
"""
import glob, os, re, shutil, subprocess, sys

APPLY = "--apply" in sys.argv
from datetime import datetime, timezone
TS = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
BAK_DIR = "/root/nginx-backups"

POLICY = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' https://unpkg.com https://cdnjs.cloudflare.com; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://unpkg.com https://cdnjs.cloudflare.com; "
    "font-src 'self' https://fonts.gstatic.com data:; "
    "img-src 'self' data: blob: https:; "
    "connect-src 'self' https:; "
    "frame-src 'self'; "
    "object-src 'none'; "
    "base-uri 'self'; "
    "form-action 'self'; "
    "frame-ancestors 'self'"
)
RE_CSP = re.compile(r'^([ \t]*)add_header\s+Content-Security-Policy\b[^;]*;[^\n]*$', re.M | re.I)
SEARCH = ("/etc/nginx/*.conf", "/etc/nginx/snippets/*", "/etc/nginx/conf.d/*",
          "/etc/nginx/includes/*", "/etc/nginx/sites-enabled/*", "/etc/nginx/sites-available/*")


def say(m):
    print("[033_csp] " + m, flush=True)


def _nginx_T_files():
    """Every file nginx ACTUALLY reads, from `nginx -T`.

    CSP-SCRIPT-SRC-3 (26 Aug 2026). The 24 Aug run of this migration reported
    "CSP declared in N file(s); 0 still lack script-src" and then measured a
    served policy of `frame-ancestors 'self'` -- i.e. it rewrote every file it
    could SEE and the emitter was not among them. That is a search defect, not a
    server defect: SEARCH below is a fixed list of globs, none of them recursive
    (`snippets/*` misses `snippets/security/*`) and all of them under /etc/nginx
    (an include by absolute path from anywhere else is invisible).

    `nginx -T` dumps the fully-resolved configuration and names each source file
    on a `# configuration file <path>:` line. That is the authoritative set --
    it cannot miss an include, wherever it lives. Falls back to the old globs if
    nginx -T is unavailable, so this is strictly additive.
    """
    found = []
    try:
        r = subprocess.run(["nginx", "-T"], capture_output=True, text=True, timeout=30)
        if r.returncode == 0:
            for line in (r.stdout or "").splitlines():
                m = re.match(r"^#\s*configuration file\s+(/\S+?):\s*$", line)
                if m:
                    found.append(m.group(1))
    except Exception as ex:
        say("nginx -T unavailable (%s) -- falling back to the fixed globs" % repr(ex)[:60])
    return found


def csp_files():
    """Return {realpath: text} for every nginx file that DECLARES a CSP.

    Union of three sources so nothing can hide: what nginx says it reads
    (authoritative), a RECURSIVE walk of /etc/nginx, and the original globs.
    """
    cands = list(_nginx_T_files())

    for root, _dirs, names in os.walk("/etc/nginx"):        # recursive, unlike SEARCH
        for n in names:
            cands.append(os.path.join(root, n))

    for pat in SEARCH:                                      # original behaviour, kept
        cands.extend(glob.glob(pat))

    out = {}
    seen = set()
    for c in cands:
        try:
            rp = os.path.realpath(c)
        except Exception:
            continue
        if rp in seen:
            continue
        seen.add(rp)
        if not os.path.isfile(rp) or ".bak" in os.path.basename(rp):
            continue
        try:
            t = open(rp, encoding="utf-8", errors="replace").read()
        except Exception:
            continue
        if RE_CSP.search(t):
            out[rp] = t
    return out


def served_csp():
    """Ask the SERVER what it serves. The only evidence that counts."""
    try:
        import http.client
        conn = http.client.HTTPConnection("127.0.0.1", 80, timeout=10)
        conn.request("GET", "/", headers={"Host": "trustsquare.co",
                                          "User-Agent": "TrustSquare-Migration/033"})
        r = conn.getresponse()
        val = r.getheader("Content-Security-Policy") or ""
        r.read()
        conn.close()
        return val
    except Exception as ex:
        return "ERROR:" + repr(ex)[:80]


def main():
    files = csp_files()
    if not files:
        say("REFUSING: no add_header Content-Security-Policy found anywhere under /etc/nginx. "
            "Not guessing where to write one.")
        return 1

    # CSP-SCRIPT-SRC-4 (26 Aug 2026) -- THE BUG THAT MADE 033 FAIL TWICE.
    # This line used to read:  if "script-src" not in t   -- i.e. it asked whether
    # the FILE TEXT mentioned script-src. /etc/nginx/snippets/security_headers.conf
    # carries a COMMENT reading "A full Content-Security-Policy (script-src/style-src
    # /img-src) is deliberately ...". That comment contains the literal string
    # "script-src", so the only file that actually needed rewriting tested as
    # already-fixed, `stale` came back EMPTY, the migration rewrote NOTHING
    # ("restoring 0 file(s)" in the 02:07Z run), and then failed honestly because the
    # served header had of course not changed. Two deploys, both undiagnosable from
    # the failure text alone.
    # CLASS -- and it is the same class as the CRLF false positive fixed in
    # audit_global_qa.py the same morning: THE PROGRAM COMPARED THE WRONG THING.
    # Staleness is a property of the DIRECTIVE, never of the surrounding prose, so
    # comments are stripped and only the add_header values are tested.
    def _directive_values(text):
        """Every add_header Content-Security-Policy value in `text`, comments removed."""
        uncommented = "\n".join(
            ln for ln in text.splitlines() if not ln.lstrip().startswith("#"))
        return [m.group(0) for m in RE_CSP.finditer(uncommented)]

    stale = {}
    for p, t in files.items():
        vals = _directive_values(t)
        if not vals:
            continue                      # only a comment mentioned CSP here
        if any("script-src" not in v for v in vals):
            stale[p] = t
    say("CSP declared in %d file(s); %d still lack script-src" % (len(files), len(stale)))
    for p in files:
        say("   %s  %s" % ("NEEDS FIX" if p in stale else "already ok", p))

    before = served_csp()
    say("served CSP BEFORE: %r" % before[:110])
    # Both halves must agree before claiming success: the SERVED header proves the
    # effect, `stale` proves no declaration was left behind to win a later reload.
    if "script-src" in before and not stale:
        say("already applied and PROVEN on the served response. Nothing to do.")
        return 0
    if not APPLY:
        say("DRY RUN — re-run with --apply.")
        return 0

    os.makedirs(BAK_DIR, exist_ok=True)
    backups = {}
    try:
        for p, t in stale.items():
            dest = os.path.join(BAK_DIR, os.path.basename(p) + ".bak-033-" + TS)
            shutil.copy2(p, dest)
            backups[p] = dest
            new = RE_CSP.sub(lambda m: '%sadd_header Content-Security-Policy "%s" always;'
                                       '   # CSP-SCRIPT-SRC-2 25 Aug 2026' % (m.group(1), POLICY), t)
            open(p, "w", encoding="utf-8").write(new)
            assert "script-src" in open(p, encoding="utf-8").read(), "write did not land in " + p
            say("rewrote %s (backup %s)" % (p, dest))

        r = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("nginx -t failed:\n" + (r.stderr or r.stdout))
        r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError("reload failed:\n" + (r.stderr or r.stdout))

        after = served_csp()
        say("served CSP AFTER : %r" % after[:110])
        if "script-src" not in after:
            # CSP-SCRIPT-SRC-3: do not just fail -- say WHERE the surviving policy
            # lives. The 24 Aug failure was undiagnosable precisely because it did not.
            for _p, _t in sorted(csp_files().items()):
                for _v in _directive_values(_t):
                    say("   STILL DECLARES CSP: %s :: %s" % (_p, _v.strip()[:90]))
            raise RuntimeError("the server still does not SERVE script-src after the reload — "
                               "something else is emitting the header (the STILL DECLARES lines "
                               "above name every file nginx reads that sets one). Not claiming "
                               "success.")
    except Exception as ex:
        say("FAILED (%s) — restoring %d file(s) and reloading" % (str(ex)[:180], len(backups)))
        for p, dest in backups.items():
            shutil.copy2(dest, p)
        subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        say("restored. The site is exactly as it was before this migration ran.")
        return 1

    say("APPLIED AND PROVEN on the served response.")
    for p, dest in backups.items():
        say("rollback: cp %s %s && nginx -t && nginx -s reload" % (dest, p))
    return 0


if __name__ == "__main__":
    sys.exit(main())
