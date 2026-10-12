#!/usr/bin/env python3
"""paystack_plans_sync.py -- AUTO-RENEW-1 (RUL-224, 12 Oct 2026) MAINTENANCE.

Makes sure Paystack holds one monthly plan for each paid product (Starter, Pro, Agency Pro seat) and that
the app knows each plan's code. Plans are made ONCE, here -- never by a checkout. Idempotent: a plan the
app already knows is left alone, and a plan that already exists on the Paystack account is adopted, not
made twice.

Run it ON THE SERVER (the Paystack key lives only in the running app, and stays there: this script asks
the app to do the work through its admin route and never reads or prints the key):

    python3 scripts/paystack_plans_sync.py            # make or adopt whatever is missing
    python3 scripts/paystack_plans_sync.py --dry-run  # only report what exists

Arming the switch (launch_switches.auto_renew, David's act on the +1 page) runs the same step by itself,
and the app retries hourly while the switch is on and a plan is missing -- so this script is the manual
lane for checking or preparing, not a step anybody has to remember.
Exit 0 = every plan is known. Exit 1 = something is missing or failed (printed). Exit 2 = could not run.
"""
import json, os, sys, urllib.request, urllib.error

BASE = os.environ.get("MS_LOCAL_URL", "http://127.0.0.1:8000")


def _proc_env():
    """Environment of the running app (the marketsquare service), so the admin key is the one it holds --
    the same read scripts/ops_sweep.py uses. Never printed."""
    try:
        import subprocess
        pid = subprocess.run(["systemctl", "show", "-p", "MainPID", "marketsquare"],
                             capture_output=True, text=True).stdout.strip().split("=")[1]
        env = {}
        with open("/proc/%s/environ" % pid, "rb") as f:
            for kv in f.read().split(b"\0"):
                if b"=" in kv:
                    k, v = kv.decode(errors="replace").split("=", 1)
                    env[k] = v
        return env
    except Exception:
        return {}


def main():
    dry = "--dry-run" in sys.argv[1:]
    key = (os.environ.get("MS_ADMIN_KEY") or _proc_env().get("MS_ADMIN_KEY") or "").strip()
    if not key:
        print("could not run: no MS_ADMIN_KEY in this environment or in the running app (run this on the server)")
        return 2
    req = urllib.request.Request(BASE + "/admin/auto-renew/plans" + ("?dry_run=1" if dry else ""), data=b"",
                                 method="POST", headers={"X-Admin-Key": key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            out = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print("could not run: the app answered HTTP %s on /admin/auto-renew/plans" % e.code)
        return 2
    except Exception as e:
        print("could not run: %s" % type(e).__name__)
        return 2
    print("Paystack key mode: %s   switch: %s   %s" % (out.get("key_mode"), "ON" if out.get("switch_on") else "OFF",
                                                      "(dry run - nothing was made)" if out.get("dry_run") else ""))
    bad = 0
    for p in out.get("plans", []):
        line = "  %-12s %-8s %s" % (p.get("product"), p.get("state"), p.get("plan_code") or "")
        if p.get("reason"):
            line += "  (%s)" % p["reason"]
        print(line)
        if p.get("state") in ("missing", "failed"):
            bad += 1
    if out.get("reason"):
        print("  " + str(out["reason"]))
    if bad or not out.get("ok", False):
        print("NOT COMPLETE: %d plan(s) missing or failed" % bad)
        return 1
    print("ALL PLANS KNOWN")
    return 0


if __name__ == "__main__":
    sys.exit(main())
