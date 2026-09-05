#!/usr/bin/env python3
"""check_bat_crlf.py — BAT-CRLF-1 (26 Aug 2026).

WHY THIS GUARD EXISTS
---------------------
David ran add_secret.bat and it "flickered on and off" -- a window that opened
and closed too fast to read, having done nothing. Three faults stacked, and the
first one is the class:

  1. THE REPO FORCED LF ONTO WINDOWS SCRIPTS. .gitattributes carried
     `* text=auto eol=lf` -- correct for everything that reaches the Linux
     server, and wrong for every .bat. cmd.exe reads a batch file byte by byte
     and expects CRLF; a caret line-continuation followed by a bare LF does NOT
     continue the line, so a 15-caret PowerShell block was mangled into garbage.
  2. The caret continuations themselves -- fragile for exactly that reason.
  3. No `pause` on any exit path, so every failure closed the window unread.

Sixteen .bat and ten .ps1 files were LF-only when this was found, including the
whole nightly deploy lane -- they survived only by having no carets and no
labels. ROTATE_SECRETS.bat, the secrets lane, had five carets and was one run
away from the same silent failure.

CLASS: a script's line endings belong to the INTERPRETER that reads it, never to
the repo's default. And a script a human runs BY HAND must never close without
saying why -- an unreadable failure is indistinguishable from doing nothing.

Run:  python3 scripts/check_bat_crlf.py     (exit 0 = clean, 1 = a fault)
Stdlib only. Reads files, changes nothing. Ledger RG-0194.
"""
import os
import re
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "_to_delete", "node_modules", "__pycache__", "venv"}
WIN_EXT = (".bat", ".cmd", ".ps1")

# Bats that legitimately never wait for a human: scheduled tasks and lanes called
# by other scripts. A pause in these would hang an unattended run forever.
UNATTENDED = {
    "autodeploy_agent.bat",          # AUTODEPLOY-AGENT-1 (RUL-092): 20-min tick, nobody present
    "nightly_ship.bat", "nightly_tsl.bat", "register_nightly_ship.bat",
    "register_nightly_tsl.bat", "commit_checkpoint.bat", "git_unlock.bat",
    "prune_backups.bat", "refresh_dashboard.bat", "media_push.bat",
    "release.bat", "deploy_web.py", "tsl_selftest.bat", "commit.bat",
    # writes only to its own log file, no console output at all -- a pause would
    # hang it forever with nobody there to press a key
    "publish_whitepaper_auto.bat",
    # UNATTENDED-ALLOWLIST-1 (5 Sep 2026): anything on host_queue/ALLOWLIST.txt is run by
    # the 20-minute agent with nobody present, so a waiting prompt would hang it forever --
    # the opposite of the flicker this file guards against. Added when deploy_uptime_worker
    # .bat arrived allowlisted and was flagged for lacking a pause it must never have.
    "deploy_uptime_worker.bat",
    "clean_stoploss_cities.bat", "launch_day_wave.bat", "club_import.py",
    "resend_broken_link_now.bat", "send_human_clicks_now.bat",
}


def win_scripts():
    for root, dirs, names in os.walk(REPO):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for n in names:
            if n.lower().endswith(WIN_EXT) and ".bak" not in n:
                yield os.path.join(root, n)


def main():
    fails, warns = [], []

    ga = os.path.join(REPO, ".gitattributes")
    try:
        attrs = open(ga, encoding="utf-8", errors="replace").read()
    except OSError:
        attrs = ""
    if not re.search(r"^\*\.bat\s+text\s+eol=crlf", attrs, re.M):
        fails.append(".gitattributes no longer pins *.bat to eol=crlf -- the repo default "
                     "(text=auto eol=lf) will hand Windows LF-only batch files again, and a "
                     "caret continuation on an LF line silently mangles the command")

    for p in sorted(win_scripts()):
        rel = os.path.relpath(p, REPO)
        base = os.path.basename(p)
        try:
            raw = open(p, "rb").read()
        except OSError:
            continue
        if b"\n" in raw and b"\r\n" not in raw:
            fails.append("%s has LF-only line endings -- cmd.exe expects CRLF" % rel)
            continue
        # a bare LF among CRLFs is the same fault, one line at a time
        if re.search(rb"(?<!\r)\n", raw.replace(b"\r\n", b"")):
            pass  # nothing left after stripping CRLF means it is clean

        if not base.lower().endswith(".bat"):
            continue
        text = raw.decode("utf-8", errors="replace")
        carets = len(re.findall(r"\^\r?\n", text))
        if carets:
            warns.append("%s uses %d caret line-continuation(s) -- they work only while the "
                         "file stays CRLF; a single long line cannot be broken by line endings"
                         % (rel, carets))
        if base in UNATTENDED:
            continue
        # An interactive bat must not be able to exit without saying why.
        exits = len(re.findall(r"^\s*exit /b [1-9]", text, re.M | re.I))
        pauses = len(re.findall(r"^\s*pause\s*$", text, re.M | re.I))
        if exits and pauses == 0:
            fails.append("%s can exit with an error and has no `pause` -- the window closes "
                         "before David can read why (the 26 Aug flicker exactly)" % rel)

    for w in warns:
        print("  WARN  " + w)
    for f in fails:
        print("  FAIL  " + f)
    if not fails:
        print("  OK    every Windows script is CRLF; every hand-run .bat can say why it stopped")
    print("\n%d fail, %d warn" % (len(fails), len(warns)))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
