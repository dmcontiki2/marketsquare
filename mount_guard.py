#!/usr/bin/env python3
"""
mount_guard.py - detect a TORN SANDBOX MOUNT before it can corrupt anything (MOUNT-READ-1 fix, S140).

THE FAULT THIS CATCHES
----------------------
The bash sandbox reaches C:\\Users\\David\\Projects over a virtiofs/FUSE mount. For large files
that have just been written from the Windows/file-tool side, the bash mount can serve a
PERSISTENTLY TRUNCATED copy for the whole session: `wc -l file` shows a short prefix while the
real Windows file (and git) is complete. If an agent then (a) reports git/file state from that
torn view, it raises false alarms; or worse (b) Python-writes the file back from bash, it
OVERWRITES the good Windows file with the truncated copy. This has bitten repeatedly
(MOUNT-TEAR-1, the ms.js/bea_main.py/dashboard.html truncations in the CHANGELOG).

HOW IT DETECTS WITHOUT TRUSTING THE TORN VIEW
---------------------------------------------
git stores its own object copy of every committed file, read through the git object store, NOT
through the FUSE file view. So `git show HEAD:<file>` is an independent oracle. The guard
compares, for each tracked file, the BASH-MOUNT byte length against the GIT-HEAD byte length.
A mount that serves FEWER bytes than HEAD for a committed-clean file is torn. (Files legitimately
edited-but-uncommitted are reported separately as 'modified', not torn, so real work isn't flagged.)

EXIT CODES
  0  mount is whole (no torn files)             -> safe to proceed
  1  one or more files are TORN on the mount    -> DO NOT write-back from bash; use the file-tools
                                                   / pull the authoritative copy first

USAGE
  python3 mount_guard.py                 # check the high-value docs + code
  python3 mount_guard.py --all           # check every tracked text file
  python3 mount_guard.py f1 f2 ...       # check specific files
"""
import subprocess, sys, os

# the files most often torn / most dangerous if torn (docs the loop writes + the big code files)
DEFAULT = ["CLAUDE.md", "STATUS.md", "BACKLOG.md", "CHANGELOG.md", "AGENT_BRIEFING.md",
           "CHANGE_REGISTER.md", "AUDIT_PROGRESS.md", "ms.js", "ms.css", "bea_main.py",
           "marketsquare.html", "marketsquare_admin.html", "smoke_test.py"]


def git_head_bytes(path):
    """Authoritative size from git's object store (does NOT go through the FUSE file view)."""
    try:
        out = subprocess.run(["git", "show", "HEAD:" + path], capture_output=True)
        if out.returncode != 0:
            return None  # not tracked at HEAD (new file) - can't compare, skip
        return len(out.stdout)
    except Exception:
        return None


def git_is_modified(path):
    """Is this path legitimately modified (staged/unstaged) vs HEAD? Then a size diff is real work,
    not a torn mount."""
    try:
        out = subprocess.run(["git", "status", "--porcelain", "--", path],
                             capture_output=True, text=True)
        return bool(out.stdout.strip())
    except Exception:
        return False


def mount_bytes(path):
    try:
        return os.path.getsize(path)
    except OSError:
        return None


def _ends_mid_content(path):
    """A whole text file in this repo ends with a newline. A torn (truncated-mid-write) copy ends
    mid-line with no trailing newline. Return a short reason string if it looks cut, else ''."""
    try:
        with open(path, "rb") as fh:
            if os.path.getsize(path) == 0:
                return ""  # empty is its own case, handled by size check
            fh.seek(-1, os.SEEK_END)
            last = fh.read(1)
        if last not in (b"\n", b"\r"):
            return "no trailing newline - ends mid-line"
        return ""
    except OSError:
        return "unreadable"


def tracked_text_files():
    out = subprocess.run(["git", "ls-files"], capture_output=True, text=True)
    files = []
    for f in out.stdout.splitlines():
        if f.endswith((".md", ".py", ".js", ".css", ".html", ".json", ".txt", ".bat")):
            files.append(f)
    return files


def main(argv):
    if "--all" in argv:
        files = tracked_text_files()
    elif argv:
        files = argv
    else:
        files = DEFAULT

    torn, modified, ok, skipped = [], [], [], []
    for f in files:
        if not os.path.exists(f):
            skipped.append((f, "absent on mount"))
            continue
        head = git_head_bytes(f)
        mnt = mount_bytes(f)
        if head is None:
            skipped.append((f, "not at HEAD (new/untracked)"))
            continue
        if mnt is None:
            torn.append((f, "?", head, "unreadable on mount"))
            continue
        if mnt == head:
            ok.append(f)
        elif git_is_modified(f):
            # A real edit -> size differs legitimately. BUT a modified file can ALSO be torn on
            # the mount (the dangerous masked case). A whole text file ends cleanly (final newline,
            # or a closing token); a torn one is cut mid-content. If a modified file is SMALLER
            # than HEAD *and* ends mid-line, treat it as torn, not as clean work.
            cut = _ends_mid_content(f)
            if mnt < head and cut:
                torn.append((f, mnt, head,
                             "MODIFIED but mount copy is smaller than committed AND ends mid-content "
                             "(%s) - likely torn, do not write-back" % cut))
            else:
                modified.append((f, mnt, head))
        elif mnt < head:
            # clean per git, yet the mount serves fewer bytes than committed => TORN
            torn.append((f, mnt, head, "mount serves %d of %d committed bytes (TRUNCATED)" % (mnt, head)))
        else:
            # mount bigger than HEAD but git says clean - unusual; flag for a look
            torn.append((f, mnt, head, "mount LARGER than committed but git-clean (inspect)"))

    print("MOUNT GUARD  -  %d ok · %d modified(real) · %d TORN · %d skipped"
          % (len(ok), len(modified), len(torn), len(skipped)))
    for f, mnt, head, why in torn:
        print("  [TORN] %-24s %s" % (f, why))
    for f, mnt, head in modified:
        print("  [edit] %-24s mount=%d head=%d (legitimately modified - not torn)" % (f, mnt, head))
    if torn:
        print("\n  ⚠️  DO NOT write-back any TORN file from bash - it will overwrite the good Windows")
        print("      copy with a truncated one. Use the Read/Edit file-tools (they hit the true file),")
        print("      or pull the authoritative copy from the server/git before editing.")
        return 1
    print("  mount is whole - safe to proceed.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
