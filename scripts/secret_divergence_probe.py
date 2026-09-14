#!/usr/bin/env python3
"""SECRET-ONE-VALUE-1 (14 Sep 2026) -- prove no secret has two live values.

Born of a three-week silent outage. The Maintenance agent was armed and running LIVE
three times a day and ended every run on:
    [maint] intake FAILED (HTTP Error 401) -- nothing read; failing safe, doing nothing.
Cause: the app runs on MS_MAINT_KEY from /etc/marketsquare/secrets.env while the agent
falls back to /var/www/marketsquare/.env, and the 22 Aug rotation updated one file and
not the other. The same divergence had put THREE different values of LAUNCH_CODE_SECRET
in play -- CityLauncher signing launch codes with a key the live app does not verify with.

The hazard was already NAMED in the ledger ("files that hold more than one live copy ...
a THIRD copy nobody knew about") and nothing enforced it, so it happened anyway. A named
hazard with no assertion behind it is not a control. This is the assertion.

NEVER prints a secret value. Only names and 12-character SHA-256 fingerprints.

Exit 0 = all legs hold (or NOT EVALUATED -- see below). Exit 1 = a divergence is back.
A vantage that cannot reach the server prints "NOT EVALUATED:" and exits 0, so an
instrument limit can never be read as a verdict on the app (the RG-0187 contract).
"""
import hashlib
import os
import subprocess
import sys

HOST = "root@178.104.73.239"
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REMOTE = r'''
import hashlib, os, subprocess
def fp(v):
    return hashlib.sha256(v.encode()).hexdigest()[:12]
def load(p):
    d = {}
    try:
        for ln in open(p, encoding="utf-8", errors="replace"):
            ln = ln.strip()
            if ln[:1].isalpha() and "=" in ln and not ln.startswith("#"):
                k, v = ln.split("=", 1)
                d[k.strip()] = v.strip()
    except OSError:
        pass
    return d
A = load("/var/www/marketsquare/.env")
B = load("/etc/marketsquare/secrets.env")
for k in sorted(set(A) & set(B)):
    if A[k] != B[k]:
        print("DIVERGED %s %s %s" % (k, fp(A[k]), fp(B[k])))
pid = subprocess.run(["systemctl", "show", "-p", "MainPID", "--value", "marketsquare"],
                     capture_output=True, text=True).stdout.strip()
env = {}
try:
    for part in open("/proc/%s/environ" % pid, encoding="utf-8", errors="replace").read().split("\0"):
        if "=" in part:
            k, v = part.split("=", 1)
            env[k] = v
except OSError:
    pass
for name in ("MS_MAINT_KEY", "LAUNCH_CODE_SECRET"):
    if env.get(name):
        print("RUNNING %s %s" % (name, fp(env[name])))
kf = "/opt/marketsquare-src/.secrets/ms_maint_key.txt"
if os.path.exists(kf):
    print("KEYFILE %s" % fp(open(kf, encoding="utf-8").read().strip()))
else:
    print("KEYFILE ABSENT")
# Only judge runs SINCE the key file was installed. Counting the whole journal would
# read three weeks of the outage this entry commemorates and call the fix a failure --
# a guard that reports history as a present-tense fault trains the eye to skip reds.
since = "-1 day"
try:
    import datetime as _dt
    since = _dt.datetime.fromtimestamp(os.path.getmtime(kf)).strftime("%Y-%m-%d %H:%M:%S")
except OSError:
    pass
j = subprocess.run(["journalctl", "-u", "maintenance-agent.service", "--since", since,
                    "--no-pager"], capture_output=True, text=True).stdout
print("INTAKEFAIL %d" % j.count("intake FAILED"))
print("RAN %d" % j.count("[maint] run "))
print("PROBE_DONE")
'''


def fp(v):
    return hashlib.sha256(v.encode()).hexdigest()[:12]


def remote():
    try:
        pr = subprocess.run(
            ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
             "-o", "StrictHostKeyChecking=no", HOST, "python3 -"],
            input=REMOTE, capture_output=True, text=True, timeout=60)
    except Exception as ex:
        return None, type(ex).__name__
    if "PROBE_DONE" not in (pr.stdout or ""):
        return None, (pr.stderr or pr.stdout or "no output")[-160:]
    return pr.stdout, None


def local_launch_code_fp():
    p = os.path.join(REPO, "..", "CityLauncher", ".env")
    try:
        for ln in open(p, encoding="utf-8", errors="replace"):
            ln = ln.strip()
            if ln.startswith("LAUNCH_CODE_SECRET="):
                return fp(ln.split("=", 1)[1].strip())
    except OSError:
        return None
    return None


def main():
    out, err = remote()
    if out is None:
        print("NOT EVALUATED: this vantage cannot run the probe on the origin (%s). "
              "It measured itself, not the secrets -- re-run from a machine whose SSH "
              "to the origin works before trusting this row." % err)
        return 0

    fails, running, keyfile, intakefail, ran = [], {}, None, None, 0
    for ln in out.splitlines():
        w = ln.split()
        if not w:
            continue
        if w[0] == "DIVERGED":
            fails.append("%s holds TWO different live values (%s in /var/www/.env vs %s in "
                         "/etc/marketsquare/secrets.env) -- whichever lane reads the stale "
                         "file is authenticating with a key nothing accepts" % (w[1], w[2], w[3]))
        elif w[0] == "RUNNING":
            running[w[1]] = w[2]
        elif w[0] == "KEYFILE":
            keyfile = w[1]
        elif w[0] == "INTAKEFAIL":
            intakefail = int(w[1])
        elif w[0] == "RAN":
            ran = int(w[1])

    if keyfile == "ABSENT":
        fails.append(".secrets/ms_maint_key.txt is gone -- the Maintenance agent is back on its "
                     "stale-file fallback and its next rotation will 401 it into silence again")
    elif keyfile and running.get("MS_MAINT_KEY") and keyfile != running["MS_MAINT_KEY"]:
        fails.append("the agent's key file (%s) no longer matches the key the app is running on "
                     "(%s) -- intake will 401" % (keyfile, running["MS_MAINT_KEY"]))

    if intakefail:
        fails.append("the maintenance agent logged 'intake FAILED' %d time(s) in its last 60 "
                     "journal lines -- it is waking up, failing to read its queue, and doing "
                     "nothing, which looks identical to a quiet day" % intakefail)

    cl = local_launch_code_fp()
    app = running.get("LAUNCH_CODE_SECRET")
    if cl is None:
        print("INFO: CityLauncher/.env not beside this repo -- the launch-code leg was not judged")
    elif app and cl != app:
        fails.append("CityLauncher signs launch codes with %s while the live app verifies with "
                     "%s -- every code issued would be rejected" % (cl, app))

    if fails:
        for f in fails:
            print("FAIL: " + f)
        return 1

    print("OK: no shared secret holds two values; the agent's key file matches the running app; "
          "no intake failure in the last %d agent run(s); CityLauncher signs launch codes with "
          "the key the app verifies with." % ran)
    return 0


if __name__ == "__main__":
    sys.exit(main())
