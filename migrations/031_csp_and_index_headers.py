#!/usr/bin/env python3
"""031_csp_and_index_headers.py — CSP-SCRIPT-SRC-1 + INDEX-HEADERS-1 (24 Aug 2026).

TWO FAULTS, ONE NGINX EDIT. Both found by probing on 24 Aug, the day
Travelpayouts came back and David asked "don't let them breach us again".

FAULT 1 — THE INDEX SERVES NO SECURITY HEADERS AT ALL
-----------------------------------------------------
Measured 24 Aug 2026 21:53 UTC, cache MISS so this is the ORIGIN answering:

    GET /terms   -> x-frame-options, x-content-type-options, referrer-policy,
                    content-security-policy: frame-ancestors 'self',
                    strict-transport-security          (all five present)
    GET /?cb=... -> NONE OF THEM. Not one.

Cause is the nginx `add_header` inheritance rule, which is a footgun rather
than a bug: add_header directives are inherited from the enclosing level ONLY
IF the current level declares no add_header of its own. `location = / {}`
declares its own Cache-Control (`public, max-age=300, stale-while-revalidate=600`
— visible on / and absent on /terms), and that single directive silently
DISCARDS the entire inherited security-header set.

So the one page that matters most — index.html, which is both the public front
door AND the document that renders the SA Smart ID / passport upload flow, and
which is the exact page the Travelpayouts loader was pasted into on 2 Aug —
has been serving naked. nginx_security_headers.conf on disk says otherwise,
which is why nobody caught it: the file was READ, the page was never PROBED.

FAULT 2 — THERE IS NO script-src ANYWHERE
-----------------------------------------
The CSP is `frame-ancestors 'self'` and nothing else, so even where headers DO
arrive, the browser will execute a script from any origin on the internet. A
full CSP was deferred on 16 Jul because the index carries ~163 inline onclick
handlers. That deferral is the reason the 3 Aug loader ran to completion.

'unsafe-inline' keeps all 163 handlers working AND still blocks every remote
origin — which is the whole breach vector. The thing that was "too hard" was
never needed to close this.

WHAT THIS MIGRATION DOES
  1. Rewrites the Content-Security-Policy line in the security-headers include
     to the full policy below (keeping frame-ancestors, adding script-src etc).
  2. Adds `include <that file>;` INSIDE `location = / {`, so the index gets the
     set back despite its own Cache-Control. Belt: the include is idempotent.
  3. nginx -t; on failure restore the backup and exit non-zero WITHOUT reloading.
  4. Reload; re-verify; on failure restore and reload again.

THE POLICY, AND WHY EACH ROW IS WHAT IT IS (measured, not guessed —
scripts/no_remote_code_guard.py inventoried the whole deployable surface):
  default-src 'self'            everything not named below is same-origin only
  script-src  'self' 'unsafe-inline' unpkg.com cdnjs.cloudflare.com
                                'unsafe-inline' = the ~163 inline handlers.
                                unpkg = Leaflet static tags. cdnjs = Leaflet
                                loaded dynamically by ms.js aiLeaflet().
                                NO 'unsafe-eval'. NO wildcard. tp-em.com and
                                every other affiliate host is refused BY THE
                                BROWSER now, not merely by our discipline.
  style-src   'self' 'unsafe-inline' fonts.googleapis.com unpkg.com cdnjs...
  font-src    'self' fonts.gstatic.com data:
  img-src     'self' data: blob: https:  (permissive on purpose: images are
                                passive, and listing/uploaded imagery moves
                                between R2/CDN hosts — a wrong img-src breaks
                                the shop front for zero security gain)
  connect-src 'self' https:     the app's own API is same-origin; left open so
                                a future integration cannot be broken by this
                                migration. TIGHTEN LATER (see below).
  frame-src   'self'            no third-party framed documents
  object-src  'none'            no Flash/applet/embed vector
  base-uri    'self'            stops <base> hijacking of every relative URL
  form-action 'self'            credentials cannot be POSTed off-site
  frame-ancestors 'self'        unchanged, the clickjacking control we had

HONEST LIMIT, RECORDED RATHER THAN HIDDEN: `connect-src https:` means a script
that DID somehow execute could still phone home. Closing that needs the app's
own outbound calls inventoried at runtime, which is a post-launch job. It is
recorded as ledger RG-0180 OPEN rather than being quietly left out. script-src
is the control that stops the script existing in the first place, and that one
is tight.

REVERSING IT (a real rollback, one command, prints the exact path on apply):
    cp <printed backup> <site file> && nginx -t && nginx -s reload

VERIFY after applying (anonymous, from anywhere):
    curl -sI 'https://trustsquare.co/?cb=1' | grep -i content-security-policy
      -> must contain script-src
    curl -sI https://trustsquare.co/terms  | grep -i content-security-policy
      -> same policy
Regression ledger RG-0178 (script-src enforced) and RG-0179 (the index carries
the same headers as the API paths) assert exactly this, live, every session.
"""
import glob, os, re, shutil, subprocess, sys
from datetime import datetime, timezone

APPLY = "--apply" in sys.argv
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
CSP_LINE = ('add_header Content-Security-Policy    "%s"  always;   '
            '# CSP-SCRIPT-SRC-1 24 Aug 2026\n' % POLICY)


def say(m):
    print("[031_csp] " + m, flush=True)


def find_headers_file():
    """The include that currently defines frame-ancestors."""
    hits = []
    for pat in ("/etc/nginx/*.conf", "/etc/nginx/snippets/*", "/etc/nginx/conf.d/*",
                "/etc/nginx/includes/*", "/var/www/marketsquare/nginx*"):
        for c in glob.glob(pat):
            if not os.path.isfile(c) or ".bak" in os.path.basename(c):
                continue
            try:
                t = open(c, encoding="utf-8", errors="replace").read()
            except Exception:
                continue
            if "Content-Security-Policy" in t and "frame-ancestors" in t:
                hits.append(os.path.realpath(c))
    return sorted(set(hits))


def find_site():
    def _hits(pats):
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
        return list(out.items())
    en = _hits(["/etc/nginx/sites-enabled/*"])
    return en if en else _hits(["/etc/nginx/sites-available/*", "/etc/nginx/conf.d/*.conf"])


RE_CSP = re.compile(r'^[ \t]*add_header\s+Content-Security-Policy\b.*$\n?', re.M | re.I)
RE_ROOT_LOC = re.compile(r'(location\s*=\s*/\s*\{)', re.I)


def backup(path):
    os.makedirs(BAK_DIR, exist_ok=True)          # OUTSIDE the globbed dirs (NGINX-BAK-LOOP-1)
    dest = os.path.join(BAK_DIR, os.path.basename(path) + ".bak-031-" + TS)
    shutil.copy2(path, dest)
    return dest


def nginx_test():
    r = subprocess.run(["nginx", "-t"], capture_output=True, text=True)
    return r.returncode == 0, (r.stderr or r.stdout).strip()


def main():
    hfiles = find_headers_file()
    sites = find_site()
    if not hfiles:
        say("REFUSING: could not find the file that defines Content-Security-Policy. "
            "Not guessing where to write an nginx header.")
        return 1
    if not sites:
        say("REFUSING: could not identify the trustsquare.co site file.")
        return 1
    if len(hfiles) > 1:
        say("REFUSING: %d files define a CSP (%s). Ambiguous — a human decides which."
            % (len(hfiles), ", ".join(hfiles)))
        return 1

    hfile = hfiles[0]
    site = sites[0][0]
    say("headers include : " + hfile)
    say("site file       : " + site)

    htext = open(hfile, encoding="utf-8", errors="replace").read()
    stext = open(site, encoding="utf-8", errors="replace").read()

    need_csp = "script-src" not in htext
    inc_line = "    include %s;   # INDEX-HEADERS-1 24 Aug 2026: location = / declares its own\n" \
               "    # Cache-Control, which per nginx inheritance DISCARDS every inherited add_header.\n" \
               "    # Without this include the front page — the one carrying the ID-upload flow —\n" \
               "    # serves with no CSP, no X-Frame-Options and no HSTS. Probed naked on 24 Aug.\n" % hfile
    m = RE_ROOT_LOC.search(stext)
    if not m:
        say("REFUSING: no `location = / {` block found in the site file — cannot place the include "
            "without guessing.")
        return 1
    need_inc = hfile not in stext.split(m.group(1), 1)[1][:1200]

    if not need_csp and not need_inc:
        say("already applied — CSP carries script-src and location = / includes the header file. "
            "Nothing to do (idempotent).")
        return 0

    say("will change: %s%s" % ("[CSP -> full policy] " if need_csp else "",
                               "[include headers inside location = /]" if need_inc else ""))
    if not APPLY:
        say("DRY RUN — re-run with --apply. New policy would be:")
        say("  " + POLICY)
        return 0

    hbak = backup(hfile)
    sbak = backup(site)
    say("backup headers : " + hbak)
    say("backup site    : " + sbak)

    try:
        if need_csp:
            if RE_CSP.search(htext):
                htext = RE_CSP.sub(CSP_LINE, htext, count=1)
            else:
                htext = htext.rstrip("\n") + "\n" + CSP_LINE
            open(hfile, "w", encoding="utf-8").write(htext)
            assert "script-src" in open(hfile, encoding="utf-8").read(), "CSP write did not land"

        if need_inc:
            stext = stext.replace(m.group(1), m.group(1) + "\n" + inc_line, 1)
            open(site, "w", encoding="utf-8").write(stext)
            assert hfile in open(site, encoding="utf-8").read(), "include write did not land"

        ok, msg = nginx_test()
        if not ok:
            say("nginx -t FAILED — restoring both files, NOT reloading:\n" + msg)
            shutil.copy2(hbak, hfile); shutil.copy2(sbak, site)
            return 1

        r = subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        if r.returncode != 0:
            say("reload FAILED — restoring and reloading the old config:\n" + (r.stderr or r.stdout))
            shutil.copy2(hbak, hfile); shutil.copy2(sbak, site)
            subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
            return 1
    except Exception as ex:
        say("EXCEPTION (%r) — restoring both files" % ex)
        shutil.copy2(hbak, hfile); shutil.copy2(sbak, site)
        subprocess.run(["nginx", "-s", "reload"], capture_output=True, text=True)
        return 1

    say("APPLIED. Verify:")
    say("  curl -sI 'https://trustsquare.co/?cb=1' | grep -i content-security-policy")
    say("  (must contain script-src)")
    say("Rollback: cp %s %s && cp %s %s && nginx -t && nginx -s reload" % (hbak, hfile, sbak, site))
    return 0


if __name__ == "__main__":
    sys.exit(main())
