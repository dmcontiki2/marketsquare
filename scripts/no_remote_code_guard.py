#!/usr/bin/env python3
"""no_remote_code_guard.py - REMOTE-CODE-GUARD-1 (24 Aug 2026).

WHY THIS EXISTS
---------------
On 2 Aug 2026 a Travelpayouts "Drive" loader was pasted into the <head> of
marketsquare.html and 9 adventures maps. It fetched code from tp-em.com -- a
different registrable domain from travelpayouts.com -- into the SAME document
that carries the identity-document upload flow, with no SRI and no script-src
CSP. A network capture on 3 Aug of a LOCKED page load showed it pulling 4
further chunks, POSTing to /collect and /collect_batch, and calling
/link-switch/v1/convert with the visited URL. David's ruling, 3 Aug: no
third-party code on the app at all.

WHAT WENT WRONG WITH THE FIRST FIX
----------------------------------
RG-0025 was written to assert the absence of two literal strings:
"tp-em.com" and "NTU3Mzkx.js". That catches the exact loader we already
removed and NOTHING ELSE. A new snippet from a new host -- which is precisely
what a re-approved affiliate account hands you -- sails past it green. The
ledger's own scope rule says most faults are a CLASS, not an instance. This
guard is the class.

WHAT IT ASSERTS
---------------
Across every file the deploy manifest actually ships, NO remote code may be
referenced from any origin that is not in ALLOWED below, by ANY of the routes
that were available to the 3 Aug loader:

  * <script src="https://host/...">        static tag
  * document.createElement('script') + .src = 'https://...'   the loader's shape
  * <iframe src="https://host/...">        remote document with script rights
  * <link rel=stylesheet href="https://...">  and @import url(https://...)
  * import('https://...') / importScripts('https://...')

ALLOWED is an ALLOWLIST WITH REASONS, not a blocklist. A blocklist can only
ever name yesterday's attacker. Adding a host here is a deliberate, dated act
and shows up in the diff -- which is the point.

EXIT CODES
  0  clean
  1  at least one violation (a host not on the allowlist)
Advisory findings (allowed host, but no Subresource Integrity) print as NOTE
and do NOT fail the run -- they are honest debt, recorded rather than hidden.

USAGE
  python3 scripts/no_remote_code_guard.py           # human report
  python3 scripts/no_remote_code_guard.py --json    # for the regression ledger
  python3 scripts/no_remote_code_guard.py --self-test  # prove it can FAIL
"""
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MANIFEST = os.path.join(REPO, "ops", "autodeploy", "deploy_manifest.txt")

# ---------------------------------------------------------------------------
# THE ALLOWLIST. Host -> why it is here. Adding a row is a deliberate decision.
# Every row was measured on the surface on 24 Aug 2026, not assumed.
# ---------------------------------------------------------------------------
ALLOWED = {
    "unpkg.com":
        "Leaflet 1.9.4 CSS+JS, static <script>/<link> tags on marketsquare.html, "
        "studyabroad_teaser.html and the two studywork maps. Pre-dates the breach; "
        "eyeballed and kept deliberately (RG-0025 note). No SRI - see NOTE debt.",
    "cdnjs.cloudflare.com":
        "Leaflet 1.9.4, loaded DYNAMICALLY by ms.js aiLeaflet() for the AI route map. "
        "Found 24 Aug 2026 by this guard's first run - it had never been inventoried "
        "anywhere, and it is the same createElement('script') shape as the 3 Aug "
        "loader. Kept (it is Leaflet, and the AI route map needs it) but now VISIBLE.",
    "fonts.googleapis.com":
        "Google Fonts stylesheet on marketsquare.html, marketsquare_admin.html, "
        "support.html. Stylesheet only - no script rights.",
    "fonts.gstatic.com":
        "Font files pulled by the fonts.googleapis.com stylesheet. Passive assets.",
}

# Named explicitly so the INTENT survives even if someone rewrites the logic.
# These are not the mechanism -- ALLOWED is. This is the note to the next session.
DENIED_BY_RULING = {
    "tp-em.com":          "the 3 Aug 2026 Travelpayouts Drive loader itself",
    "tp.media":           "Travelpayouts CDN - same lane, same ruling",
    "travelpayouts.com":  "affiliate scripts of any kind (RUL-041: link-outs only)",
    "www.travelpayouts.com": "as above",
    "emrld.cc":           "Travelpayouts link-switch host seen in the 3 Aug capture",
}

RE_SCRIPT_TAG = re.compile(r'<script[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']', re.I)
RE_IFRAME     = re.compile(r'<iframe[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']', re.I)
RE_LINK       = re.compile(r'<link[^>]*\bhref\s*=\s*["\']([^"\']+)["\']', re.I)
RE_IMPORT_CSS = re.compile(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', re.I)
RE_DYN_SRC    = re.compile(r'\.src\s*=\s*["\'](https?:)?//([^"\'/]+)', re.I)
RE_DYN_MAKE   = re.compile(r'createElement\(\s*["\']script["\']\s*\)', re.I)
RE_DYN_IMPORT = re.compile(r'(?:\bimport\(|importScripts\()\s*["\'](https?:)?//([^"\'/]+)', re.I)

REMOTE = re.compile(r'^(?:https?:)?//', re.I)


def host_of(url):
    return re.sub(r'^(?:https?:)?//', '', url, flags=re.I).split('/')[0].split('?')[0].lower()


def manifest_sources():
    """The files the deploy ACTUALLY ships - the real attack surface."""
    out = []
    if not os.path.isfile(MANIFEST):
        return out
    for line in open(MANIFEST, encoding="utf-8", errors="replace"):
        line = line.strip()
        if not line or line.startswith("#") or "|" not in line:
            continue
        out.append(line.split("|")[0].strip())
    return out


def scan_text(rel, text):
    """Return (violations, notes) for one file's text."""
    v, notes = [], []

    def check(url, kind, script_rights):
        if not REMOTE.match(url or ""):
            return
        h = host_of(url)
        if h in ALLOWED:
            if script_rights and 'integrity=' not in text:
                notes.append((rel, h, kind, "allowed host but no Subresource Integrity on this file"))
            return
        why = DENIED_BY_RULING.get(h)
        tail = (" - " + why) if why else ""
        v.append((rel, h, kind, "origin is NOT on the allowlist" + tail))

    for m in RE_SCRIPT_TAG.finditer(text):
        check(m.group(1), "<script src>", True)
    for m in RE_IFRAME.finditer(text):
        check(m.group(1), "<iframe src>", True)
    for m in RE_LINK.finditer(text):
        check(m.group(1), "<link href>", False)
    for m in RE_IMPORT_CSS.finditer(text):
        check(m.group(1), "@import", False)
    for m in RE_DYN_IMPORT.finditer(text):
        check("//" + m.group(2), "dynamic import()", True)

    # The 3 Aug loader's exact shape: build a <script> element, then set .src.
    if RE_DYN_MAKE.search(text):
        for m in RE_DYN_SRC.finditer(text):
            check("//" + m.group(2), "createElement('script') + .src", True)

    return v, notes


def run():
    violations, notes, scanned = [], [], 0
    for rel in manifest_sources():
        p = os.path.join(REPO, rel)
        if not os.path.isfile(p) or not rel.lower().endswith((".html", ".js", ".css")):
            continue
        scanned += 1
        text = open(p, encoding="utf-8", errors="replace").read()
        v, n = scan_text(rel, text)
        violations += v
        notes += n
    return scanned, violations, notes


def self_test():
    """PROVE THE CHECK CAN FAIL (the ledger's 7 Aug rule) before trusting its green."""
    cases = [
        ('<script src="https://tp-em.com/NTU3Mzkx.js?t=557391"></script>', "the actual 3 Aug loader tag"),
        ('var s=document.createElement("script");s.src="https://tp.media/x.js";', "the loader's dynamic shape, new host"),
        ('<script src="https://evil.example/a.js"></script>', "any unknown host"),
        ('<iframe src="https://tp-em.com/frame"></iframe>', "remote iframe"),
        ('<link rel="stylesheet" href="https://evil.example/a.css">', "remote stylesheet"),
    ]
    ok = True
    for src, label in cases:
        v, _ = scan_text("SELFTEST", src)
        good = bool(v)
        print("  [%s] catches: %s" % ("OK" if good else "X ", label))
        ok = ok and good
    clean = '<script src="/static/ms.js"></script><script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>'
    v, _ = scan_text("SELFTEST", clean)
    print("  [%s] stays quiet on legitimate local + allowlisted refs" % ("OK" if not v else "X "))
    ok = ok and not v
    return 0 if ok else 1


def main():
    if "--self-test" in sys.argv:
        rc = self_test()
        print("\nself-test %s" % ("PASSED - the guard can fail, so its green means something"
                                  if rc == 0 else "FAILED - do not trust this guard"))
        return rc

    scanned, violations, notes = run()

    if "--json" in sys.argv:
        print(json.dumps({
            "scanned": scanned,
            "violations": [{"file": f, "host": h, "kind": k, "why": w} for f, h, k, w in violations],
            "notes": [{"file": f, "host": h, "kind": k, "why": w} for f, h, k, w in notes],
        }, indent=2))
        return 1 if violations else 0

    print("REMOTE-CODE-GUARD - %d deployable html/js/css files scanned" % scanned)
    print("allowlisted origins: " + ", ".join(sorted(ALLOWED)))
    if violations:
        print("\n%d VIOLATION(S) - remote code from an un-allowlisted origin:" % len(violations))
        for f, h, k, w in violations:
            print("  [X ] %-34s %-32s %s" % (h, k, f))
            print("       %s" % w)
        print("\nThis is the 3 Aug 2026 class. Either the reference is wrong and comes out,")
        print("or the host is a deliberate decision and goes into ALLOWED with a reason.")
    else:
        print("\n[ OK ] no remote code outside the allowlist")
    if notes:
        print("\n%d NOTE(S) - allowed, but unpinned (no SRI). Honest debt, not a failure:" % len(notes))
        for f, h, k, w in notes:
            print("  [--] %-34s %-32s %s" % (h, k, f))
    return 1 if violations else 0


if __name__ == "__main__":
    sys.exit(main())
