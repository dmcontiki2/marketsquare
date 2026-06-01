#!/usr/bin/env python3
"""
fea_integrity_check.py - TrustSquare FEA integrity fingerprint (OBSERVE-ONLY).

The deterministic, "done-as-standard" version of the health/security monitor's
step 3. It fetches the live index plus the versioned ms.js / ms.css assets,
*validates* each response is the real asset (not a transient Cloudflare/origin
blip), retries through transients, then diffs byte sizes + ?v= versions against
fea_baseline.json.

Why this exists
---------------
On the 2026-06-01 monitor run a bare `?cb=` fetch of ms.js/ms.css briefly
returned a 1360-byte generic page with HTTP 200 (a transient edge blip), which
looked like a whole-file size change and nearly produced a false tamper ALERT.
A separate prior gotcha was an off-by-one from measuring sizes via shell command
substitution (which strips trailing newlines). This script removes both failure
modes by validating + retrying, and by measuring raw byte length in-process.

What counts as a signal
-----------------------
  * same version, different byte size  -> ALERT (tamper / corruption / bad deploy)
  * version bumped (e.g. v128 -> v129) -> NOTE  (looks like a legit deploy;
                                                  refresh baseline after confirming)
  * BEA /health version changed         -> ALERT
  * cannot get a valid response         -> exit 3 (could not measure; NOT a tamper claim)

This script NEVER edits code, deploys, blocks IPs, or writes to the BEA. Read-only.

Usage
-----
  python3 fea_integrity_check.py                 # check vs baseline -> OK / ALERT
  python3 fea_integrity_check.py --json          # same, machine-readable
  python3 fea_integrity_check.py --update-baseline   # accept current live as the
                                                     # new baseline (run ONLY after a
                                                     # confirmed, intentional deploy)

Exit codes: 0 = OK, 2 = ALERT (mismatch), 3 = could not measure (network/edge).
"""

import argparse
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error

BASE = "https://trustsquare.co"
BASELINE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fea_baseline.json")
UA = "Mozilla/5.0 (TrustSquareMonitor/1.0; +integrity-check; read-only)"

RETRIES = 4
BACKOFF_S = 1.5  # grows linearly per attempt

# Sane floors - the real files are far above these. Anything smaller is a blip.
MIN_BYTES = {"index": 50_000, "ms.js": 200_000, "ms.css": 20_000}
# Substring the Content-Type must contain for each asset.
EXPECT_CT = {"index": "text/html", "ms.js": "javascript", "ms.css": "css"}


def _fetch_curl(url):
    """Fetch via curl (proven against this Cloudflare setup). Returns (status, ct, body_bytes)."""
    import tempfile
    fd, path = tempfile.mkstemp()
    os.close(fd)
    try:
        out = subprocess.run(
            ["curl", "-sS", "-L", "--max-time", "25", "-A", UA,
             "-o", path, "-w", "%{http_code}\t%{content_type}", url],
            capture_output=True, text=True, timeout=35,
        )
        meta = (out.stdout or "").strip().split("\t")
        status = int(meta[0]) if meta and meta[0].isdigit() else 0
        ct = meta[1] if len(meta) > 1 else ""
        with open(path, "rb") as f:
            body = f.read()
        return status, ct, body
    finally:
        try:
            os.unlink(path)
        except OSError:
            pass


def _fetch_urllib(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=25) as r:
        body = r.read()
        return getattr(r, "status", 200), r.headers.get("Content-Type", ""), body


def fetch(url):
    """Prefer curl (battle-tested vs CF here); fall back to urllib."""
    if shutil.which("curl"):
        return _fetch_curl(url)
    return _fetch_urllib(url)


def _looks_like_html(body):
    head = body[:256].lstrip().lower()
    return head.startswith(b"<!doctype html") or head.startswith(b"<html")


def measure(name, url):
    """Fetch with validation + retry. Returns {bytes, content_type, body, attempts} or raises."""
    last = "no attempt"
    for attempt in range(1, RETRIES + 1):
        sep = "&" if "?" in url else "?"
        u = f"{url}{sep}cb={random.randint(1, 2_000_000_000)}"
        try:
            status, ct, body = fetch(u)
            n = len(body)
            ct_ok = EXPECT_CT[name] in (ct or "").lower()
            floor_ok = n >= MIN_BYTES[name]
            # Assets must NOT be HTML; the index obviously is.
            html_ok = True if name == "index" else not _looks_like_html(body)
            if status == 200 and ct_ok and floor_ok and html_ok:
                return {"bytes": n, "content_type": ct, "body": body, "attempts": attempt}
            last = (f"status={status} ct={ct!r} bytes={n} "
                    f"ct_ok={ct_ok} floor_ok={floor_ok} html_ok={html_ok}")
        except (urllib.error.URLError, urllib.error.HTTPError, OSError, ValueError) as e:
            last = f"fetch error: {e}"
        time.sleep(BACKOFF_S * attempt)
    raise RuntimeError(f"{name}: no valid response after {RETRIES} attempts (last: {last})")


def parse_versions(index_body):
    txt = index_body.decode("utf-8", "replace")
    js = re.search(r"ms\.js\?v=(\d+)", txt)
    css = re.search(r"ms\.css\?v=(\d+)", txt)
    if not js or not css:
        raise RuntimeError("could not parse ms.js / ms.css ?v= from index HTML")
    return int(js.group(1)), int(css.group(1))


def bea_version():
    try:
        _, _, body = fetch(f"{BASE}/health")
        return json.loads(body).get("version")
    except Exception:
        return None


def gather():
    """Fetch + validate everything. Raises RuntimeError on inability to measure."""
    idx = measure("index", f"{BASE}/")
    vjs, vcss = parse_versions(idx["body"])
    js = measure("ms.js", f"{BASE}/static/ms.js?v={vjs}")
    css = measure("ms.css", f"{BASE}/static/ms.css?v={vcss}")
    return {
        "bea_version": bea_version(),
        "index_bytes": idx["bytes"],
        "ms_js": {"version": vjs, "bytes": js["bytes"]},
        "ms_css": {"version": vcss, "bytes": css["bytes"]},
        "attempts": {"index": idx["attempts"], "ms.js": js["attempts"], "ms.css": css["attempts"]},
    }


def compare(live, base):
    """Return (alerts, notes). alerts => real signal; notes => benign/deploy."""
    alerts, notes = [], []

    if base.get("bea_version") and live["bea_version"] != base["bea_version"]:
        alerts.append(f"BEA /health version {base['bea_version']} -> {live['bea_version']}")

    if live["index_bytes"] != base["index_bytes"]:
        d = live["index_bytes"] - base["index_bytes"]
        alerts.append(f"index bytes {base['index_bytes']} -> {live['index_bytes']} (delta {d:+d})")

    for key, label in (("ms_js", "ms.js"), ("ms_css", "ms.css")):
        lv, bv = live[key], base[key]
        if lv["version"] != bv["version"]:
            notes.append(
                f"{label} version {bv['version']} -> {lv['version']} "
                f"(bytes {bv['bytes']} -> {lv['bytes']}); looks like a deploy - "
                f"confirm against CHANGELOG, then refresh with --update-baseline"
            )
        elif lv["bytes"] != bv["bytes"]:
            d = lv["bytes"] - bv["bytes"]
            alerts.append(
                f"{label} v{lv['version']} bytes {bv['bytes']} -> {lv['bytes']} (delta {d:+d}) "
                f"- SAME version, size changed = tamper/corruption signal"
            )

    return alerts, notes


def load_baseline():
    with open(BASELINE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def write_baseline(live):
    payload = {
        "_comment": ("TrustSquare FEA integrity baseline. Refresh ONLY after a confirmed, "
                     "intentional deploy: python3 fea_integrity_check.py --update-baseline. "
                     "A same-version byte delta is a tamper/corruption signal, not a deploy."),
        "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bea_version": live["bea_version"],
        "index_bytes": live["index_bytes"],
        "ms_js": live["ms_js"],
        "ms_css": live["ms_css"],
    }
    with open(BASELINE_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
        f.write("\n")
    return payload


def ok_line(live):
    return (f"FEA integrity OK - index {live['index_bytes']}B, "
            f"ms.js v{live['ms_js']['version']} {live['ms_js']['bytes']}B, "
            f"ms.css v{live['ms_css']['version']} {live['ms_css']['bytes']}B, "
            f"BEA {live['bea_version']} - matches baseline.")


def main():
    ap = argparse.ArgumentParser(description="TrustSquare FEA integrity fingerprint (read-only).")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--update-baseline", action="store_true",
                    help="accept current live state as new baseline (after a confirmed deploy)")
    args = ap.parse_args()

    try:
        live = gather()
    except RuntimeError as e:
        msg = f"COULD NOT MEASURE - {e}. No tamper conclusion drawn; no action taken."
        print(json.dumps({"status": "could_not_measure", "error": str(e)}) if args.json else msg)
        return 3

    if args.update_baseline:
        payload = write_baseline(live)
        if args.json:
            print(json.dumps({"status": "baseline_updated", "baseline": payload}, indent=2))
        else:
            print("Baseline updated to current live state:")
            print(f"  index {payload['index_bytes']}B, "
                  f"ms.js v{payload['ms_js']['version']} {payload['ms_js']['bytes']}B, "
                  f"ms.css v{payload['ms_css']['version']} {payload['ms_css']['bytes']}B, "
                  f"BEA {payload['bea_version']}")
        return 0

    if not os.path.exists(BASELINE_PATH):
        payload = write_baseline(live)
        if args.json:
            print(json.dumps({"status": "baseline_seeded", "baseline": payload}, indent=2))
        else:
            print(f"No baseline found - seeded fea_baseline.json from current live state. {ok_line(live)}")
        return 0

    base = load_baseline()
    alerts, notes = compare(live, base)

    if args.json:
        print(json.dumps({
            "status": "alert" if alerts else "ok",
            "live": {k: live[k] for k in ("bea_version", "index_bytes", "ms_js", "ms_css")},
            "attempts": live["attempts"],
            "alerts": alerts,
            "notes": notes,
        }, indent=2))
    else:
        if alerts:
            print("ALERT - FEA integrity fingerprint mismatch (no action taken; observe-only):")
            for a in alerts:
                print(f"  * {a}")
            for n in notes:
                print(f"  (note) {n}")
            print("David or a gated agent must decide. This monitor never remediates.")
        else:
            print(ok_line(live))
            for n in notes:
                print(f"  (note) {n}")

    return 2 if alerts else 0


if __name__ == "__main__":
    sys.exit(main())
