#!/usr/bin/env python3
"""watch_alert.py -- raise the daily watch's alarm WITHOUT touching the origin.

ALERT-OFFORIGIN-1 (5 Sep 2026, closes DW-097; the class DW-073 carried as a residual).

THE FAULT THIS EXISTS TO KILL
  The watch's RED alert was one SSH command to the box it watches: parse RESEND_API_KEY
  out of /etc/marketsquare/resend.watch.conf, then curl Resend from the origin. So the
  alarm rode the same transport as the whole class of failure it reports. Twice in anger
  (26 Aug, 5 Sep) the origin was unreachable, the verdict was RED, and no email could be
  sent -- David found out hours later by reading a report.

  A fire alarm wired through the room that is on fire is not an alarm.

THE LANES, tried in this order:
  1. WORKER  -- POST /alert on the Cloudflare Worker `trustsquare-uptime`. Independent
                egress, its own Resend key, its own schedule; owes the origin nothing.
                This is the lane that works on the bad day.
  2. ORIGIN  -- the legacy ssh+curl path, kept as a FALLBACK ONLY. It is not deleted,
                because a Cloudflare-side problem is a real (if rarer) failure too, and
                two independent lanes beat one. It must never be tried first again.

USAGE
  python3 scripts/watch_alert.py --reason "3 LOCKED fixes rotted" --line "ledger exit 1" ...
  python3 scripts/watch_alert.py --dry            # authenticate + validate, send nothing
  python3 scripts/watch_alert.py --level TEST --reason "alert path proof" --no-fallback

EXIT  0 = delivered (or dry run authenticated)   1 = NOT delivered by any lane.
      A non-zero exit is itself a finding: the alarm is deaf and must be reported as such.
"""
import argparse, json, os, re, subprocess, sys, urllib.error, urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MARKER = REPO / "ops" / "cloudflare" / "UPTIME_DEPLOYED.md"
KEYFILE = REPO / ".secrets" / "watch_alert_key.txt"
ORIGIN_USER, ORIGIN_HOST = "msdeploy", "178.104.73.239"


def worker_url():
    """Read the Worker URL from its deploy marker rather than hardcoding it twice.
    One source of truth: if the Worker is ever redeployed under a new name, the marker
    is what changes, and this follows it (the same rule RG-0138's liveness probe uses)."""
    try:
        m = re.search(r"https://[a-z0-9.-]+\.workers\.dev", MARKER.read_text(encoding="utf-8", errors="replace"))
        return m.group(0) if m else ""
    except OSError:
        return ""


def ingest_key():
    k = os.environ.get("WATCH_ALERT_KEY", "").strip()
    if k:
        return k
    try:
        return KEYFILE.read_text(encoding="utf-8").strip()
    except OSError:
        return ""


def via_worker(level, reason, lines, dry):
    """Lane 1. Returns (ok, detail). Never raises."""
    url, key = worker_url(), ingest_key()
    if not url:
        return False, "no Worker URL in ops/cloudflare/UPTIME_DEPLOYED.md"
    if not key:
        return False, "no ingest key (.secrets/watch_alert_key.txt or WATCH_ALERT_KEY)"
    payload = json.dumps({"level": level, "reason": reason, "lines": lines, "dry": bool(dry)}).encode()
    req = urllib.request.Request(
        url.rstrip("/") + "/alert", data=payload, method="POST",
        headers={"Authorization": "Bearer " + key, "Content-Type": "application/json",
                 "User-Agent": "trustsquare-watch-alert/1"})
    try:
        with urllib.request.urlopen(req, timeout=25) as r:
            out = json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:200]
        return False, "HTTP %s %s" % (e.code, detail)
    except Exception as e:  # noqa: BLE001 -- an alarm lane may never raise
        return False, str(e)[:200]
    if dry:
        return bool(out.get("would_send")), json.dumps(out, separators=(",", ":"))[:400]
    return bool(out.get("sent")), json.dumps(out, separators=(",", ":"))[:400]


def via_origin(level, reason, lines):
    """Lane 2, FALLBACK ONLY -- the old ssh+curl path. Dies exactly when the origin does,
    which is the whole reason lane 1 exists. Kept for the Cloudflare-side failure case."""
    subprocess.run(["bash", str(REPO / "load_sandbox_ssh.sh")], capture_output=True, timeout=90)
    html = "<p>" + "</p><p>".join([reason] + list(lines)) + "</p>"
    remote = (
        "KEY=$(grep -oP 'RESEND_API_KEY=\\K[A-Za-z0-9_\\-]+' /etc/marketsquare/resend.watch.conf) "
        "&& curl -s -X POST https://api.resend.com/emails "
        "-H \"Authorization: Bearer $KEY\" -H 'Content-Type: application/json' "
        "-d @- <<'JSON'\n" + json.dumps({
            "from": "TrustSquare Watch <support@mail.trustsquare.co>",
            "to": ["dmcontiki2@gmail.com"],
            "subject": "WATCH %s: %s" % (level, reason),
            "html": html,
        }) + "\nJSON"
    )
    try:
        p = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
             "%s@%s" % (ORIGIN_USER, ORIGIN_HOST), remote],
            capture_output=True, text=True, timeout=90)
    except Exception as e:  # noqa: BLE001
        return False, str(e)[:200]
    out = (p.stdout or "").strip()
    return ('"id"' in out), (out[:200] or (p.stderr or "").strip()[:200])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", default="RED", choices=["RED", "AMBER", "TEST"])
    ap.add_argument("--reason", default="unspecified")
    ap.add_argument("--line", action="append", default=[], dest="lines")
    ap.add_argument("--dry", action="store_true", help="authenticate and validate, send nothing")
    ap.add_argument("--no-fallback", action="store_true", help="worker lane only (proves independence)")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    result = {"level": a.level, "reason": a.reason, "dry": a.dry, "lanes": []}

    ok, detail = via_worker(a.level, a.reason, a.lines, a.dry)
    result["lanes"].append({"lane": "worker", "ok": ok, "detail": detail})
    if not ok and not a.dry and not a.no_fallback:
        ok2, detail2 = via_origin(a.level, a.reason, a.lines)
        result["lanes"].append({"lane": "origin-ssh", "ok": ok2, "detail": detail2})
        ok = ok or ok2

    result["delivered"] = ok
    result["by"] = next((l["lane"] for l in result["lanes"] if l["ok"]), None)
    if a.json:
        print(json.dumps(result, indent=2))
    else:
        for l in result["lanes"]:
            print("[%s] %-10s %s" % ("ok" if l["ok"] else "FAIL", l["lane"], l["detail"]))
        print(("DELIVERED via %s" % result["by"]) if ok else
              "ALERT PATH BROKEN -- no lane delivered. This is itself a HIGH finding.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
