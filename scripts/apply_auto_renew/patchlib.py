"""AUTO-RENEW-1 patch helpers: asserted-unique string replacement, .bak-autorenew-<ts> copy, verified write-back."""
import os, sys, time, hashlib

TS = os.environ.get("AR_TS") or time.strftime("%Y%m%d-%H%M%S", time.gmtime())


def load(path):
    b = open(path, "rb").read()
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    is_crlf = crlf > lf
    s = b.decode("utf-8")
    if is_crlf:
        s = s.replace("\r\n", "\n")
    return s, is_crlf, b


def save(path, s, is_crlf, orig_bytes, tag="autorenew"):
    bak = "%s.bak-%s-%s" % (path, tag, TS)
    if not os.path.exists(bak):
        with open(bak, "wb") as f:
            f.write(orig_bytes)
    out = s.replace("\n", "\r\n") if is_crlf else s
    data = out.encode("utf-8")
    with open(path, "wb") as f:
        f.write(data)
        f.flush()
        try:
            os.fsync(f.fileno())
        except Exception:
            pass
    back = open(path, "rb").read()
    assert back == data, "write-back mismatch on %s (%d vs %d bytes)" % (path, len(back), len(data))
    print("  wrote %s  %d bytes  sha256 %s  (backup %s)" % (
        os.path.basename(path), len(data), hashlib.sha256(data).hexdigest()[:16], os.path.basename(bak)))


def rep(s, old, new, count=1):
    n = s.count(old)
    assert n == count, "anchor found %d time(s), expected %d: %r" % (n, count, old[:90])
    return s.replace(old, new)


def root():
    r = sys.argv[1] if len(sys.argv) > 1 else "."
    assert os.path.exists(os.path.join(r, "bea_main.py")), "not the repo root: %s" % r
    return r
