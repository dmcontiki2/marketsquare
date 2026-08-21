#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
eula_sync.py — THE ONE WRITER for the EULA body.

Why this exists (EULA-FORK-1, 14 Aug 2026):
    The EULA lived in THREE hand-maintained copies — eula_clean.html (the
    nominal source), terms.html (the deployed page) and the _EULA_HTML string
    literal inside ms.js (the in-app acceptance modal, i.e. the copy users
    actually agree to). On 14 Aug 2026 they had silently forked: terms.html was
    v1.12 while eula_clean.html and ms.js were still v1.11, missing SS6.1B
    entirely. Users were accepting an older agreement than the one published.
    Nothing detected it, because nothing compared them.

    Same shape as CHANGELOG-COLLISION-1 and STATUS-COLLISION-1: the fix is
    machinery, not memory. eula_clean.html is the SOURCE. This script is the
    only thing that writes the other two.

Usage:
    python3 scripts/eula_sync.py            # sync terms.html + ms.js from eula_clean.html
    python3 scripts/eula_sync.py --check    # exit 1 if out of sync, write nothing

Idempotent: a second run changes nothing. Refuses rather than guesses if an
anchor is missing.
"""
import io, json, os, sys, shutil, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE  = os.path.join(ROOT, "eula_clean.html")
TERMS   = os.path.join(ROOT, "terms.html")
MSJS    = os.path.join(ROOT, "ms.js")

BODY_START = "<p><strong>TrustSquare</strong></p>"
# EULA-ANCHOR-1 (20 Aug 2026): the end anchor used to hardcode the full Country-Schedule
# list, so ADDING a schedule (v1.14: France, Portugal, New Zealand, Argentina) silently
# broke the sync guard. Anchor on the stable prefix instead and find the paragraph end,
# so the list can grow without disarming the one writer. Still refuses rather than guesses.
BODY_END_PREFIX = "· Republic of South Africa · Country Schedules:"
BODY_END_CLOSE  = "</em></p>\n"
JS_KEY     = 'const _EULA_HTML = "'


def rd(p):
    return io.open(p, encoding="utf-8").read()


def wr(p, s):
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def canon():
    """The authoritative EULA body: the whole of eula_clean.html."""
    s = rd(SOURCE)
    if BODY_START not in s or _end_index(s) is None:
        sys.exit("REFUSING: eula_clean.html is missing its start/end anchors.")
    if len(s) < 50000:
        sys.exit("REFUSING: eula_clean.html is %d bytes — too short to be the EULA." % len(s))
    return s


def _end_index(s):
    """Index just past the closing </em></p> of the version/schedules footer line.

    Returns None when the anchor is absent — callers refuse rather than guess.
    """
    j = s.find(BODY_END_PREFIX)
    if j == -1:
        return None
    k = s.find(BODY_END_CLOSE, j)
    if k == -1:
        return None
    return k + len(BODY_END_CLOSE)


def terms_span(s):
    i = s.find(BODY_START)
    end = _end_index(s)
    if i == -1 or end is None:
        sys.exit("REFUSING: terms.html is missing its body anchors.")
    return i, end


def js_span(s):
    k = s.find(JS_KEY)
    if k == -1:
        sys.exit("REFUSING: ms.js has no _EULA_HTML literal.")
    p = k + len(JS_KEY)
    while True:                      # walk to the real closing quote
        if s[p] == "\\":
            p += 2
            continue
        if s[p] == '"':
            break
        p += 1
    return k + len(JS_KEY) - 1, p + 1


def main():
    check = "--check" in sys.argv
    body = canon()
    ts = time.strftime("%Y%m%d-%H%M%S")
    drift = []

    t = rd(TERMS)
    a, b = terms_span(t)
    if t[a:b] != body:
        drift.append("terms.html")
        if not check:
            shutil.copy2(TERMS, TERMS + ".bak-%s-eulasync" % ts)
            wr(TERMS, t[:a] + body + t[b:])

    m = rd(MSJS)
    a2, b2 = js_span(m)
    want = json.dumps(body, ensure_ascii=True)
    if m[a2:b2] != want:
        drift.append("ms.js")
        if not check:
            shutil.copy2(MSJS, MSJS + ".bak-%s-eulasync" % ts)
            wr(MSJS, m[:a2] + want + m[b2:])

    if check:
        if drift:
            print("EULA OUT OF SYNC with eula_clean.html: %s" % ", ".join(drift))
            return 1
        print("EULA in sync (%d bytes) across eula_clean.html, terms.html, ms.js" % len(body))
        return 0

    print("synced: %s" % (", ".join(drift) if drift else "nothing to do — already in sync"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
