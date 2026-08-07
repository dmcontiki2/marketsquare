#!/usr/bin/env python3
"""whatbroke.py v4 - READ-ONLY server probe.

v3 could HANG forever: output was captured, so if ssh asked for a passphrase the
prompt was invisible and the run sat there until it was killed - and the timeout
then crashed the script before it wrote anything. v4:
  * BatchMode=yes      -> never prompts; fails fast with a real reason
  * ConnectTimeout=10  -> a blocked port errors in 10s, not minutes
  * every failure is caught and REPORTED, never silent
"""
import os, subprocess, datetime
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVER = os.environ.get("MS_SERVER_ROOT", "root@178.104.73.239")
SH = os.path.join(REPO, "scripts", "whatbroke_remote.sh")
OPTS = ["-o", "BatchMode=yes", "-o", "ConnectTimeout=10",
        "-o", "StrictHostKeyChecking=accept-new"]

def run(cmd, t=90):
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=t)
        return r.returncode, r.stdout or "", r.stderr or ""
    except subprocess.TimeoutExpired:
        return 124, "", "TIMED OUT after %ds - the connection stalled." % t
    except Exception as e:
        return 125, "", "could not start: %r" % (e,)

out = []
print("probing %s (fails fast, never prompts) ..." % SERVER)
rc, so, se = run(["scp"] + OPTS + [SH, SERVER + ":/tmp/wb.sh"], 45)
out.append("scp rc=%d %s" % (rc, se.strip()[:400]))
if rc == 0:
    rc2, so2, se2 = run(["ssh"] + OPTS + [SERVER, "bash /tmp/wb.sh; rm -f /tmp/wb.sh /tmp/f.json"], 120)
    out.append("ssh rc=%d" % rc2)
    out.append(so2)
    if se2.strip():
        out.append("--- stderr ---\n" + se2.strip()[:1000])
else:
    out.append("COULD NOT REACH THE SERVER.\n"
               "  'Permission denied (publickey)' -> your SSH key is not loaded for this shell.\n"
               "  'Connection timed out'          -> the Hetzner firewall is not allowing this IP.\n"
               "  'TIMED OUT'                     -> packets are being dropped (firewall/network).")
body = "\n".join(out)
path = os.path.join(REPO, "whatbroke_%s.txt" % datetime.datetime.now().strftime("%H%M%S"))
try:
    open(path, "w", encoding="utf-8").write(body + "\n")
except Exception as e:
    print("(could not write file: %r)" % (e,))
print()
print(body)
print()
print("saved:", path)
