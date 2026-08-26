#!/usr/bin/env python3
"""split_rotated_secrets.py — fan the rotation dump out into the per-purpose files
the local tooling reads, then leave NO combined dump behind.

WHY THIS EXISTS (SECRET-ONSCREEN-1, 26 Aug 2026)
------------------------------------------------
ROTATE_SECRETS.bat step [3/4] scp'd the server's combined values file to
`.secrets\\rotated_secrets.txt` and left it there permanently. On 26 Aug that
landmine went off: Claude asked David to open Notepad for an unrelated paste,
Notepad restored its previous tab -- that very file -- and Claude's screenshot
captured five live credentials. The 7 Aug rule ("never print a secret value")
held perfectly; the gap was that a secrets file was allowed to PERSIST somewhere
a GUI could restore it.

So the dump stops being a resting place and becomes a transit buffer:
    server -> rotated_secrets.txt -> [this script] -> per-purpose files -> dump gone

WHAT IT WRITES (preserving each file's existing format exactly):
    .secrets/deploy_keys.txt   MS_ADMIN_KEY=, MS_DEPLOY_KEY=   (MS_DEPLOY_TOKEN
                               is NOT in the rotated set -- it is the GitHub
                               token, rotated on its own lane. PRESERVED byte-safe.)
    .secrets/ms_maint_key.txt  bare MS_MAINT_KEY value, no key name (its format)

NOT WRITTEN ANYWHERE:
    MS_ADMIN_PASSWORD   -- a human credential. Belongs in David's password
                           manager, not on disk. Reported as present, never stored.
    LAUNCH_CODE_SECRET  -- server-side only; nothing local consumes it.

PRINTS NO VALUES -- EVER. Only key names, lengths and 8-char sha256 fingerprints,
which is enough to prove the right value landed in the right file and enough to
detect drift later, and useless to anyone who reads the output.

USAGE:
    python3 scripts/split_rotated_secrets.py            # split, keep the dump
    python3 scripts/split_rotated_secrets.py --shred    # split, then remove the dump
"""
import hashlib, os, re, shutil, sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SEC = os.path.join(REPO, ".secrets")
DUMP = os.path.join(SEC, "rotated_secrets.txt")
DEPLOY = os.path.join(SEC, "deploy_keys.txt")
MAINT = os.path.join(SEC, "ms_maint_key.txt")
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")

def fp(v):
    return hashlib.sha256(v.encode()).hexdigest()[:8]

def say(mark, msg):
    print("  [%s] %s" % (mark, msg))

def read_dump():
    if not os.path.exists(DUMP):
        print("  [!!] no %s -- nothing to split. Run ROTATE_SECRETS.bat first." % DUMP)
        sys.exit(1)
    vals = {}
    for line in open(DUMP, encoding="utf-8", errors="replace").read().splitlines():
        m = re.match(r"^([A-Z0-9_]+)\s*=\s*(\S+)\s*$", line.strip())
        if m:
            vals[m.group(1)] = m.group(2)
    return vals

def backup(path):
    if os.path.exists(path):
        b = "%s.bak-%s" % (path, STAMP)
        shutil.copy2(path, b)
        return os.path.basename(b)
    return None

def update_kv_file(path, updates):
    """Rewrite KEY=VALUE lines in place. Keys absent from `updates` are preserved
    byte-for-byte -- this is what protects MS_DEPLOY_TOKEN."""
    lines = open(path, encoding="utf-8").read().splitlines() if os.path.exists(path) else []
    seen, out = set(), []
    for line in lines:
        m = re.match(r"^([A-Z0-9_]+)\s*=\s*(.*)$", line.strip())
        if m and m.group(1) in updates:
            k = m.group(1)
            out.append("%s=%s" % (k, updates[k]))
            seen.add(k)
        else:
            out.append(line)
    for k, v in updates.items():
        if k not in seen:
            out.append("%s=%s" % (k, v))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(out) + "\n")
    return seen

def main():
    shred = "--shred" in sys.argv
    print("=" * 66)
    print("  split_rotated_secrets  %s" % STAMP)
    print("  NOTHING BELOW PRINTS A SECRET VALUE.")
    print("=" * 66)

    vals = read_dump()
    say("ok", "read %d key(s) from the dump: %s" % (len(vals), ", ".join(sorted(vals))))

    # ---- deploy_keys.txt -------------------------------------------------
    upd = {k: vals[k] for k in ("MS_ADMIN_KEY", "MS_DEPLOY_KEY") if k in vals}
    if upd:
        b = backup(DEPLOY)
        before = set(re.findall(r"^([A-Z0-9_]+)=", open(DEPLOY).read(), re.M)) if os.path.exists(DEPLOY) else set()
        update_kv_file(DEPLOY, upd)
        after = set(re.findall(r"^([A-Z0-9_]+)=", open(DEPLOY).read(), re.M))
        for k in sorted(upd):
            say("ok", "deploy_keys.txt  %-16s -> sha256:%s" % (k, fp(upd[k])))
        preserved = sorted(before - set(upd))
        if preserved:
            say("ok", "deploy_keys.txt  PRESERVED untouched: %s" % ", ".join(preserved))
        if before - after:
            say("!!", "deploy_keys.txt LOST key(s): %s -- restore %s" % (", ".join(sorted(before - after)), b))
            sys.exit(1)
        if b:
            say("ok", "backup kept: %s" % b)

    # ---- ms_maint_key.txt (bare value, no key name) ----------------------
    if "MS_MAINT_KEY" in vals:
        b = backup(MAINT)
        with open(MAINT, "w", encoding="utf-8", newline="\n") as f:
            f.write(vals["MS_MAINT_KEY"] + "\n")
        say("ok", "ms_maint_key.txt MS_MAINT_KEY     -> sha256:%s (bare value, format preserved)" % fp(vals["MS_MAINT_KEY"]))
        if b:
            say("ok", "backup kept: %s" % b)

    # ---- the two that are deliberately NOT stored ------------------------
    if "MS_ADMIN_PASSWORD" in vals:
        say("--", "MS_ADMIN_PASSWORD present in the dump and deliberately NOT written to any file.")
        say("--", "     Put it in your password manager, then shred the dump.")
    if "LAUNCH_CODE_SECRET" in vals:
        say("--", "LAUNCH_CODE_SECRET is server-side only -- nothing local reads it. Not stored.")

    # ---- shred -----------------------------------------------------------
    print()
    if shred:
        if "MS_ADMIN_PASSWORD" in vals:
            say("!!", "REFUSING to shred: the dump still holds MS_ADMIN_PASSWORD, which lives")
            say("!!", "     nowhere else. Save it to your password manager, then delete the file")
            say("!!", "     yourself. A script must not destroy the only copy of a human credential.")
            sys.exit(2)
        os.remove(DUMP)
        say("ok", "dump shredded -- no combined secrets file remains on this PC.")
    else:
        say("--", "dump left in place. Save MS_ADMIN_PASSWORD, then DELETE %s" % DUMP)

    print("=" * 66)
    print("  RESULT: local tooling now holds the LIVE keys.")
    print("=" * 66)

if __name__ == "__main__":
    main()
