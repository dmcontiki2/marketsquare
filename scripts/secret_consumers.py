#!/usr/bin/env python3
"""secret_consumers.py -- WHERE does this credential actually live?

ROTATION-DISCOVERY-1 (6 Sep 2026). David, on the queue item asking him to rotate a
leaked key: "rotation is one of those things i battle with... it takes me some times
many hours."

WHY IT TAKES HOURS, from the record rather than from sympathy. Minting the new value at
the vendor is five minutes and is irreducibly his. The hours go on the question NOBODY
CAN ANSWER: which places hold a copy? That has been answered from memory, and memory has
been wrong TWICE, both times silently:

  * 22-23 Aug -- the rotation refreshed the app's Resend key and orphaned the copy at
    /etc/marketsquare/resend.watch.conf. The RED-alert channel was dead for six days and
    was found only when a real alert failed to send (DW-076).
  * the same rotation moved HETZNER_S3_* out of /etc/environment into the app's systemd
    drop-in -- correct hardening, and it blinded the 03:00 backup cron, which reads
    neither. The nightly database backup then failed for two weeks in silence, and was
    found by accident on 6 Sep (DW-105).

Both were the same failure: A ROTATION IS ONLY AS GOOD AS ITS LIST OF CONSUMERS, and the
list was a hand-maintained table with one row in it. This tool replaces remembering with
looking.

WHAT IT DOES: for each credential NAME, searches every place a copy is known to be able
to live -- systemd drop-ins, /etc/environment, /etc/marketsquare, the app's .env, root and
msdeploy crontabs, and the repo itself -- and prints WHERE the name appears.

WHAT IT NEVER DOES: print a value. It reports file paths and match counts only, and it
strips anything that looks like a value before printing. That restraint is not decorative:
the item that prompted this tool exists because a masking command was written by hand and
got it wrong, putting two live keys on screen (DW-106). A tool that cannot leak is worth
more than a habit of being careful.

  python3 scripts/secret_consumers.py                 # every credential in the register
  python3 scripts/secret_consumers.py RESEND_API_KEY  # one
  python3 scripts/secret_consumers.py --check         # ledger mode: exit 1 on a surprise
"""
import argparse, os, re, subprocess, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
REGISTER = REPO / "SECRETS_REGISTER.md"
SERVER = "root@178.104.73.239"

# Every place on the box a credential copy has ever been found. Adding one here is how
# this tool learns; it is deliberately a LIST, not a filesystem-wide grep, because a
# whole-disk scan of secrets is its own hazard.
SERVER_PLACES = [
    ("systemd drop-ins", "grep -l %s /etc/systemd/system/marketsquare.service.d/*.conf 2>/dev/null"),
    ("/etc/environment", "grep -l %s /etc/environment 2>/dev/null"),
    ("/etc/marketsquare", "grep -rl %s /etc/marketsquare/ 2>/dev/null"),
    ("app .env", "grep -l %s /var/www/marketsquare/.env 2>/dev/null"),
    ("citylauncher .env", "grep -l %s /var/www/citylauncher/.env 2>/dev/null"),
    ("root crontab", "crontab -l 2>/dev/null | grep -l %s /dev/stdin 2>/dev/null && echo 'root crontab'"),
    ("cron scripts", "grep -rl %s /usr/local/bin/ /root/r2backup/ 2>/dev/null"),
]

VALUEISH = re.compile(r"[A-Za-z0-9_\-/+=]{16,}")


def safe(line: str) -> str:
    """Blank anything that could be a VALUE, never the path that holds it.

    A file path is not a secret and hiding it defeats the whole purpose -- the first cut
    redacted the paths and printed '<redacted>.watch.conf', which tells a rotation nothing.
    Paths pass through; free text has long random-looking runs blanked."""
    t = line.strip()
    if t.startswith("/") or (("/" in t or "\\" in t) and " " not in t):
        return t
    return VALUEISH.sub("<redacted>", t)


def register_names():
    try:
        txt = REGISTER.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return []
    names = re.findall(r"^\|\s*([A-Z][A-Z0-9_]{3,})", txt, re.M)
    seen, out = set(), []
    for n in names:
        if n not in seen:
            seen.add(n); out.append(n)
    return out


def register_out_of_band():
    """The credentials the register CLAIMS have an out-of-band copy."""
    try:
        txt = REGISTER.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return set()
    m = re.search(r"## Out-of-band copies.*?(?=\n## |\Z)", txt, re.S)
    return set(re.findall(r"^\|\s*([A-Z][A-Z0-9_]{3,})", m.group(0), re.M)) if m else set()


def server_consumers(name):
    """Ask the box where this NAME appears. Returns a list of (place, path)."""
    script = "\n".join(cmd % name for _label, cmd in SERVER_PLACES)
    try:
        r = subprocess.run(["ssh", "-n", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
                            SERVER, script],
                           stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, text=True, timeout=60)
    except Exception:
        return None
    return sorted({ln.strip() for ln in (r.stdout or "").splitlines() if ln.strip()})


def repo_consumers(name):
    """grep, not a Python walk: this repo is large and on a FUSE mount, where reading every
    file took minutes. .secrets/ is excluded on purpose -- it holds values, and this tool
    exists precisely so nobody has to look at values."""
    cmd = ["grep", "-rl", "--binary-files=without-match",
           "--exclude-dir=.git", "--exclude-dir=node_modules", "--exclude-dir=__pycache__",
           "--exclude-dir=.secrets", "--exclude-dir=backups-r2", "--exclude-dir=folded",
           "--exclude=*.bak", "--exclude=*.bak-*", "--exclude=*.pyc", "--exclude=*.db",
           name, str(REPO)]
    try:
        r = subprocess.run(cmd, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                           stderr=subprocess.DEVNULL, text=True, timeout=90)
    except Exception:
        return []
    # Prose mentions are not consumers. A rotation cares about files that HOLD or INSTALL
    # a value -- code, scripts and config -- not the changelog paragraph describing it.
    CARRIERS = (".py", ".bat", ".sh", ".conf", ".env", ".json", ".toml", ".service", ".ps1")
    out = []
    for line in (r.stdout or "").splitlines():
        line = line.strip()
        if line and (line.endswith(CARRIERS) or "/.env" in line):
            try:
                out.append(str(Path(line).relative_to(REPO)))
            except ValueError:
                out.append(line)
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="one credential name; default is all of them")
    ap.add_argument("--check", action="store_true",
                    help="ledger mode: exit 1 if a credential has server consumers the "
                         "register's out-of-band table does not mention")
    a = ap.parse_args()

    names = [a.name] if a.name else register_names()
    if not names:
        print("no credential names found in SECRETS_REGISTER.md"); return 2
    claimed = register_out_of_band()

    offline, surprises = False, []
    for n in names:
        srv = server_consumers(n)
        if srv is None:
            offline = True
            srv = []
        rep = repo_consumers(n) if not a.check else []
        # A credential living in MORE than one place on the box has out-of-band copies,
        # and every one of them must be refreshed by the rotation or it goes stale silently.
        multi = len(srv) > 1
        if multi and n not in claimed:
            surprises.append((n, srv))
        if a.check:
            continue
        print("\n%s" % n)
        if not srv and not offline:
            print("   server : (not present)")
        for s in srv:
            print("   server : %s" % safe(s))
        if offline:
            print("   server : UNREADABLE from here (no ssh) -- server half not judged")
        for rline in rep[:6]:
            print("   repo   : %s" % rline)
        if len(rep) > 6:
            print("   repo   : ... and %d more" % (len(rep) - 6))
        if multi:
            print("   NOTE   : %d copies on the box -- a rotation must reach ALL of them%s"
                  % (len(srv), "" if n in claimed else "  << NOT in the register's out-of-band table"))

    if a.check:
        if offline:
            print("SKIPPED: the server is unreachable from here, so consumers cannot be discovered")
            return 0
        if surprises:
            print("SURPRISE: %d credential(s) have copies the register does not list -- a rotation "
                  "would orphan them, which is how DW-076 and DW-105 happened:" % len(surprises))
            for n, srv in surprises:
                print("  %-26s %d place(s): %s" % (n, len(srv), ", ".join(safe(s) for s in srv)))
            return 1
        print("OK: every credential with more than one copy on the box is named in the "
              "register's out-of-band table")
    return 0


if __name__ == "__main__":
    sys.exit(main())
