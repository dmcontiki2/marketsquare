#!/usr/bin/env python3
"""rotate_secrets.py — rotate TrustSquare's SELF-ISSUED secrets. RUNS ON THE SERVER.

Written 7 Aug 2026 after a diagnostic command dumped the whole production secret
set into a chat transcript. David's standing instruction from that moment: never
hand him a command whose output contains secrets and ask him to paste it back.
So this script PRINTS NO VALUES — ever. Only key NAMES and pass/fail marks.

WHAT IT ROTATES (self-issued only — nothing here needs a third-party dashboard):
    MS_ADMIN_KEY  MS_DEPLOY_KEY  MS_MAINT_KEY  MS_ADMIN_PASSWORD  LAUNCH_CODE_SECRET

WHAT IT DOES NOT TOUCH: MS_API_KEY (already public in ms.js by design), and every
third-party key (Resend, Cloudflare, Numista, JustTCG, Travelpayouts) — those are
issued by someone else's dashboard and cannot be rotated from here.

STRUCTURAL FIX INCLUDED: the secrets currently live as inline Environment= lines in
the unit, so anyone who can run `systemctl cat` sees them all — which is exactly how
they leaked. They move to /etc/marketsquare/secrets.env, root-owned 0600.

SAFETY: every file backed up first; health-checked after restart; AUTOMATIC ROLLBACK
to the exact previous state if the service does not come back. Idempotent-ish: run it
again and you simply get another fresh set.
"""
import hashlib, json, os, re, secrets, shutil, subprocess, sys, time
from datetime import datetime

UNIT = "marketsquare"
SECRETS_ENV = "/etc/marketsquare/secrets.env"
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP_DIR = "/root/secret-rotation-backups/%s" % STAMP
OUT_FILE = "/root/ts_rotated_latest.txt"   # fixed name so the collecting .bat needs no globbing
HEALTH = "http://127.0.0.1:8000/health"

ROTATE = {
    "MS_ADMIN_KEY":       lambda: "msq_admin_"  + secrets.token_hex(20),
    "MS_DEPLOY_KEY":      lambda: "msq_deploy_" + secrets.token_hex(20),
    "MS_MAINT_KEY":       lambda: "ms_maint_"   + secrets.token_urlsafe(32),
    "MS_ADMIN_PASSWORD":  lambda: secrets.token_urlsafe(18),
    "LAUNCH_CODE_SECRET": lambda: secrets.token_hex(32),
}

def sh(cmd, check=False):
    r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=90)
    if check and r.returncode != 0:
        raise RuntimeError("command failed: %s\n%s" % (cmd, (r.stderr or "")[:300]))
    return r.stdout.strip()

def say(mark, msg):
    print("  [%s] %s" % (mark, msg))

def unit_files():
    """The unit fragment plus any drop-ins — every place an Environment= can hide."""
    files = []
    frag = sh("systemctl show %s -p FragmentPath --value" % UNIT)
    if frag and os.path.exists(frag):
        files.append(frag)
    drop = sh("systemctl show %s -p DropInPaths --value" % UNIT)
    for d in (drop or "").split():
        if os.path.exists(d):
            files.append(d)
    return files

def running_env():
    """Read the LIVE process environment via /proc — the only honest proof that a new
    value actually reached the running service rather than merely landing in a file."""
    pid = sh("systemctl show %s -p MainPID --value" % UNIT)
    if not pid or pid == "0":
        return {}
    try:
        with open("/proc/%s/environ" % pid, "rb") as fh:
            raw = fh.read().decode("utf-8", "replace")
    except Exception:
        return {}
    out = {}
    for item in raw.split("\0"):
        if "=" in item:
            k, v = item.split("=", 1)
            out[k] = v
    return out

def healthy(tries=10, gap=3):
    """Health via urllib, NOT curl-through-a-shell.

    v1 ran: sh("curl -s -o /dev/null -w \'%%{http_code}\' -m 5 " + HEALTH). That string
    never passes through %-formatting, so curl received a literal %% - which it reads as
    an escaped percent - and printed "%{http_code}" as text. The comparison to "200"
    could NEVER be true, on any server, in any state. The 7 Aug run therefore rolled a
    perfectly healthy service back and then declared the rollback unhealthy too.
    No shell, no quoting, no format string: fewer parts, less to go wrong."""
    import urllib.request as _u
    # ALWAYS send a User-Agent. The default "Python-urllib/3.x" is 403'd by the
    # Cloudflare WAF - proven 7 Aug: bare urlopen -> 403, same URL with any UA -> 200.
    # This probe hits 127.0.0.1 and so bypasses Cloudflare entirely, but the habit
    # costs nothing and removes the whole class of "the probe was blocked, not the
    # service down".
    req = _u.Request(HEALTH, headers={"User-Agent": "ts-rotate-healthcheck"})
    for i in range(tries):
        try:
            if _u.urlopen(req, timeout=5).getcode() == 200:
                return True
        except Exception:
            pass
        if i < tries - 1:
            time.sleep(gap)
    return False

print("=" * 66)
print("  TrustSquare secret rotation   %s" % STAMP)
print("  NOTHING BELOW PRINTS A SECRET VALUE.")
print("=" * 66)

if os.geteuid() != 0:
    print("  must run as root."); sys.exit(2)

files = unit_files()
if not files:
    print("  could not locate the systemd unit for %s — nothing changed." % UNIT); sys.exit(2)
os.makedirs(BACKUP_DIR, mode=0o700, exist_ok=True)
for f in files:
    shutil.copy2(f, os.path.join(BACKUP_DIR, os.path.basename(f) + ".orig"))
if os.path.exists(SECRETS_ENV):
    shutil.copy2(SECRETS_ENV, os.path.join(BACKUP_DIR, "secrets.env.orig"))
say("ok", "backed up %d unit file(s) -> %s" % (len(files), BACKUP_DIR))

# ── 0. PROVE THE INSTRUMENT FIRST ─────────────────────────────────────────
# The service is healthy right now - it has not been touched yet. So if the health
# check cannot see that, the check is broken, and its verdict on anything we do
# next is worthless. v1 skipped this step and rolled back a healthy service on a
# false negative. Same rule the regression ledger carries: prove the check before
# you trust its green (or its red).
if not healthy(tries=4, gap=2):
    print()
    say("!!", "the health probe cannot see a HEALTHY service before any change was made.")
    say("  ", "Either %s is not the right endpoint, or the probe itself is broken." % HEALTH)
    say("  ", "ABORTING - nothing has been touched. Fix the probe, not the server.")
    sys.exit(3)
say("ok", "health probe verified against the untouched service - its verdict can be trusted")

before = running_env()
if not before:
    say("!!", "could not read the running process environment — continuing, but the")
    say("  ", "post-restart proof will be weaker.")

# ── 1. new values ─────────────────────────────────────────────────────────
new = {k: gen() for k, gen in ROTATE.items()}
say("ok", "generated %d new secrets: %s" % (len(new), ", ".join(sorted(new))))

# ── 2. strip the rotated keys from every unit file ────────────────────────
pat = re.compile(r'^\s*Environment\s*=\s*"?(%s)=' % "|".join(ROTATE), re.I)
stripped = 0
for f in files:
    lines = open(f, encoding="utf-8", errors="replace").read().splitlines(True)
    keep = [ln for ln in lines if not pat.match(ln)]
    stripped += len(lines) - len(keep)
    txt = "".join(keep)
    if "EnvironmentFile=%s" % SECRETS_ENV not in txt and f == files[0]:
        # Append inside [Service] so it is read; later Environment= would override it,
        # which is exactly why the inline copies were stripped above.
        m = list(re.finditer(r"^\[Service\]\s*$", txt, re.M))
        if not m:
            say("!!", "no [Service] section in %s — aborting, nothing written." % f); sys.exit(2)
        ins = txt.find("\n", m[0].end()) + 1
        txt = txt[:ins] + "EnvironmentFile=-%s\n" % SECRETS_ENV + txt[ins:]
    open(f, "w", encoding="utf-8", newline="").write(txt)
say("ok", "removed %d inline Environment= line(s) for the rotated keys" % stripped)
say("ok", "unit now reads %s" % SECRETS_ENV)

# ── 3. write the 0600 secrets file ────────────────────────────────────────
os.makedirs("/etc/marketsquare", mode=0o755, exist_ok=True)
existing = {}
if os.path.exists(SECRETS_ENV):
    for ln in open(SECRETS_ENV, encoding="utf-8", errors="replace"):
        if "=" in ln and not ln.strip().startswith("#"):
            k, v = ln.strip().split("=", 1)
            existing[k] = v
existing.update(new)
fd = os.open(SECRETS_ENV, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as fh:
    fh.write("# TrustSquare service secrets — root-only (0600).\n")
    fh.write("# Rotated %s. Do NOT move these back into the unit file:\n" % STAMP)
    fh.write("# anything in the unit is visible to `systemctl cat`.\n")
    for k in sorted(existing):
        fh.write("%s=%s\n" % (k, existing[k]))
os.chmod(SECRETS_ENV, 0o600)
say("ok", "wrote %s (0600, root) with %d key(s)" % (SECRETS_ENV, len(existing)))

# ── 4. restart, verify, roll back if it does not come up ──────────────────
sh("systemctl daemon-reload")
sh("systemctl restart %s" % UNIT)
if not healthy():
    say("!!", "SERVICE DID NOT COME BACK — ROLLING BACK")
    for f in files:
        b = os.path.join(BACKUP_DIR, os.path.basename(f) + ".orig")
        if os.path.exists(b):
            shutil.copy2(b, f)
    ob = os.path.join(BACKUP_DIR, "secrets.env.orig")
    if os.path.exists(ob):
        shutil.copy2(ob, SECRETS_ENV)
    elif os.path.exists(SECRETS_ENV):
        os.remove(SECRETS_ENV)
    sh("systemctl daemon-reload"); sh("systemctl restart %s" % UNIT)
    back = healthy()          # once, not twice - each call can cost 30s
    say("ok" if back else "!!",
        "rolled back; service healthy again" if back
        else "ROLLED BACK BUT STILL UNHEALTHY - check: journalctl -u %s -n 40" % UNIT)
    print("\n  NOTHING WAS ROTATED. The old secrets are still in force.")
    sys.exit(1)
say("ok", "service healthy after restart")

# ── 5. prove each value actually reached the RUNNING process ──────────────
after = running_env()
allgood = True
for k in sorted(new):
    got = after.get(k)
    if got is None:
        say("!!", "%s: NOT PRESENT in the running process" % k); allgood = False
    elif hashlib.sha256(got.encode()).hexdigest() == hashlib.sha256(new[k].encode()).hexdigest():
        say("ok", "%s: rotated and live" % k)
    else:
        say("!!", "%s: present but NOT the new value (something else still sets it)" % k)
        allgood = False

# ── 6. hand the values over as a FILE, never as terminal output ───────────
fd = os.open(OUT_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as fh:
    fh.write("TrustSquare rotated secrets %s\n" % STAMP)
    fh.write("Fetch this file, then DELETE it from the server.\n\n")
    for k in sorted(new):
        fh.write("%s=%s\n" % (k, new[k]))
say("ok", "new values written to %s (0600) — collect it, then delete it" % OUT_FILE)

print("=" * 66)
print("  RESULT: %s" % ("all %d rotated and verified live" % len(new) if allgood
                        else "ROTATED WITH WARNINGS — read the !! lines above"))
print("  Old values remain in %s if you need to compare." % BACKUP_DIR)
print("=" * 66)
sys.exit(0 if allgood else 1)
