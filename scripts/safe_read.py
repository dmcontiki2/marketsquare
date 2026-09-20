#!/usr/bin/env python3
"""SAFE-READ-1 -- verification that reads after the mount has SETTLED.

Why this exists (DW-137, 19 Sep 2026, and it nearly cost data):

The Projects folder is a virtiofs/FUSE bridge to David's Windows disk. On
19 Sep the daily watch backed up OPEN_ITEMS.md with `cp` -- 318,127 bytes on
disk, the copy byte-identical -- then read the copy back to verify it. The read
returned 29,737 bytes. About 9% of the file. No exception, no short-read
warning, nothing in any log. A re-read moments later returned the full file,
and `cmp` on six fresh copies said IDENTICAL every time, so the WRITE was
always sound. The fault is a stale or partial READ through the bridge before
the page cache settles.

That is dangerous in one specific place, and it is the place we always are:
CLAUDE.md makes a `cp` backup the ONLY undo on this mount (unlink is blocked),
and the standing method is write-then-verify-by-reading. A session that reads
back short concludes its own write truncated and "restores" from a file it has
just misread. The recovery step becomes the data-loss step.

The cure is not to read more carefully. It is to never trust a SINGLE read of a
just-written file: re-read until two consecutive reads agree, and compare
against what the writer actually produced rather than against one fresh read.

Use it:
    from safe_read import settled_read, verify_after_write, safe_backup

    data = settled_read(path)                 # bytes, or raises UnsettledRead
    verify_after_write(path, expected_text)   # raises WriteVerifyFailed
    bak = safe_backup(path)                   # cp + prove the copy, returns path

From the shell:
    python3 scripts/safe_read.py --verify <path> --expect-bytes <n>
    python3 scripts/safe_read.py --backup <path>
    python3 scripts/safe_read.py --selftest
"""
from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import sys
import time

__all__ = ["settled_read", "verify_after_write", "safe_backup",
           "UnsettledRead", "WriteVerifyFailed", "SETTLE_TRIES", "SETTLE_DELAY_S"]

# Two consecutive agreeing reads is the property. The tries/delay are generous
# on purpose: the whole point is that being slow is cheaper than being wrong,
# and in the measured good case this costs one extra read.
SETTLE_TRIES = 8
SETTLE_DELAY_S = 0.25


class UnsettledRead(OSError):
    """Consecutive reads of one path never agreed -- the mount is not settled."""


class WriteVerifyFailed(OSError):
    """A settled read of a just-written file does not match what was written."""


def _digest(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def settled_read(path, tries: int = SETTLE_TRIES, delay: float = SETTLE_DELAY_S) -> bytes:
    """Read `path` until two consecutive reads return identical bytes.

    Returns those bytes. Raises UnsettledRead if `tries` reads never agree --
    which is itself a finding worth reporting, never something to paper over
    by returning the last read and hoping.
    """
    prev = None
    prev_len = -1
    for _ in range(max(2, tries)):
        blob = open(path, "rb").read()
        dig = _digest(blob)
        if prev is not None and dig == prev:
            return blob
        prev, prev_len = dig, len(blob)
        time.sleep(delay)
    raise UnsettledRead(
        "%s never settled: %d reads disagreed (last %d bytes). Do NOT restore from "
        "a backup on the strength of this read -- the file on disk is probably fine "
        "and the READ is what is short (DW-137)." % (path, max(2, tries), prev_len))


def verify_after_write(path, expected, tries: int = SETTLE_TRIES,
                       delay: float = SETTLE_DELAY_S) -> bytes:
    """Prove a just-written file matches what the writer produced.

    `expected` may be bytes or str (encoded utf-8). Compares against the
    WRITER'S OWN output, not against a second fresh read -- that is the
    distinction DW-137 turned on.
    """
    want = expected.encode("utf-8") if isinstance(expected, str) else bytes(expected)
    got = settled_read(path, tries=tries, delay=delay)
    if got != want:
        raise WriteVerifyFailed(
            "%s: settled read is %d bytes / sha %s but the writer produced %d bytes / "
            "sha %s -- the write genuinely did not land."
            % (path, len(got), _digest(got)[:16], len(want), _digest(want)[:16]))
    return got


def safe_backup(path, suffix: str = None) -> str:
    """Copy `path` beside itself and PROVE the copy before returning.

    A backup you have not proved is not an undo -- and on this mount `cp` back
    is the only undo there is, because unlink is blocked.
    """
    src = settled_read(path)
    stamp = suffix or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    dst = "%s.bak-%s" % (path, stamp)
    shutil.copy2(path, dst)
    copy = settled_read(dst)
    if copy != src:
        raise WriteVerifyFailed(
            "backup %s does not match %s (%d vs %d bytes) -- do not rely on it"
            % (dst, path, len(copy), len(src)))
    return dst


def _selftest() -> int:
    import tempfile
    d = tempfile.mkdtemp()
    p = os.path.join(d, "probe.txt")
    body = ("x" * 4096 + "\n") * 40
    open(p, "w", encoding="utf-8").write(body)

    assert settled_read(p) == body.encode(), "settled_read returned the wrong bytes"
    verify_after_write(p, body)
    bak = safe_backup(p)
    assert os.path.isfile(bak), "safe_backup made no file"
    print("ok   settled_read / verify_after_write / safe_backup agree on a real file")

    # The failure legs must actually fire, or this module is decoration.
    try:
        verify_after_write(p, body + "drift")
    except WriteVerifyFailed:
        print("ok   verify_after_write RAISES when the file does not match the writer")
    else:
        print("FAIL verify_after_write accepted a mismatch")
        return 1

    # A path whose content changes under us must never settle.
    import itertools
    counter = itertools.count()
    real_open = open
    q = os.path.join(d, "flap.txt")
    open(q, "w", encoding="utf-8").write("seed")

    g = globals()
    def flapping(name, *a, **k):
        if name == q and a and "b" in str(a[0]):
            real_open(q, "w", encoding="utf-8").write("v%d" % next(counter))
        return real_open(name, *a, **k)
    g["open"] = flapping
    try:
        settled_read(q, tries=4, delay=0.01)
    except UnsettledRead:
        print("ok   settled_read RAISES UnsettledRead when reads never agree")
    else:
        print("FAIL settled_read returned a value for a file that never settled")
        return 1
    finally:
        g["open"] = real_open

    shutil.rmtree(d, ignore_errors=True)
    print("SAFE-READ-1 selftest: all legs pass")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="DW-137 read-after-settle verification")
    ap.add_argument("--verify", metavar="PATH")
    ap.add_argument("--expect-bytes", type=int, default=None)
    ap.add_argument("--backup", metavar="PATH")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()

    if a.selftest:
        return _selftest()
    if a.backup:
        print(safe_backup(a.backup))
        return 0
    if a.verify:
        blob = settled_read(a.verify)
        print("settled: %d bytes sha=%s" % (len(blob), _digest(blob)[:16]))
        if a.expect_bytes is not None and len(blob) != a.expect_bytes:
            print("MISMATCH: expected %d bytes" % a.expect_bytes)
            return 1
        return 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
