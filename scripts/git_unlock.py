#!/usr/bin/env python3
"""git_unlock.py -- sandbox twin of git_unlock.bat (GIT-LOCK-3, 16 Aug 2026).

WHY THIS EXISTS
---------------
The Projects mount is a virtiofs/FUSE bridge: the sandbox CANNOT unlink files
in .git (Operation not permitted), but it CAN rename them -- proven 16 Aug 2026
(git commit itself works, and commit's final step is rename(index.lock, index)).
So when sandbox-side git dies or aborts mid-write (failed pathspec, timeout,
reaped process) it strands a lock file that del/rm cannot remove from here, and
the next committer -- sandbox, host, or the 05:45 nightly -- hits
"Unable to create .git/<name>.lock: File exists".

GIT-LOCK-1 (30 Jul) fixed the HOST lane: every git-writing .bat calls
git_unlock.bat first. GIT-LOCK-2 (11 Aug) widened the .bat to the lock class.
This file is the missing SANDBOX lane: same rule, rename-aside instead of del.

THE RULE (same as the .bat): touch a lock ONLY when no git process is running
here AND the lock is stale by age. A lock with a live git behind it is never
touched. Healed locks are renamed into .git/stale_locks/ where the host sweep
(git_unlock.bat) deletes them on its next run.

USAGE
  python3 scripts/git_unlock.py            heal + report (run before any sandbox git write)
  python3 scripts/git_unlock.py --check    report only; exit 1 if a blocking stale lock exists
"""
import glob, os, subprocess, sys, time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GITDIR = os.path.join(REPO, ".git")
ASIDE = os.path.join(GITDIR, "stale_locks")
STALE_SECONDS = 15 * 60          # generous: host git is invisible from here
BLOCKING = ("index.lock", "HEAD.lock", "packed-refs.lock")


def git_running():
    try:
        return subprocess.run(["pgrep", "-x", "git"], capture_output=True).returncode == 0
    except Exception:
        return True   # cannot tell -> assume live, touch nothing (fail safe)


def stale(path):
    """The .bat's rule, adapted: a lock with no git behind it is by definition
    stale -- but host/other-sandbox git is invisible here, so 0-BYTE locks (the
    strand signature: git aborted, FUSE blocked the unlink) get a 60 s belt and
    non-empty locks (possibly a live index mid-write) keep the full threshold."""
    try:
        age = time.time() - os.path.getmtime(path)
        if os.path.getsize(path) == 0:
            # GIT-LOCK-4 (27 Aug 2026). A 0-byte lock is the strand signature: git aborted
            # and FUSE blocked the unlink. If pgrep can also PROVE no git process is running,
            # there is nothing the age can add -- the lock is unambiguously abandoned, and
            # waiting 60 s only blocks the retry that would clear it. Measured cost of not
            # doing this: one WAVE-HALFSTALL-1 commit took FIVE attempts, each failure
            # planting a fresh 0-byte lock inside the previous one's belt.
            # The belt stays for the case that matters -- git_running() returning True, or
            # failing and defaulting to True, in which case we touch nothing.
            if not git_running():
                return True
            return age > 60
        return age > STALE_SECONDS
    except OSError:
        return False


def main():
    check_only = "--check" in sys.argv
    if not os.path.isdir(GITDIR):
        print("git_unlock.py: no .git here (%s) -- nothing to do" % GITDIR); return 0
    targets = [os.path.join(GITDIR, n) for n in BLOCKING]
    targets += sorted(glob.glob(os.path.join(GITDIR, "next-index-*.lock")))
    asides  = sorted(glob.glob(os.path.join(GITDIR, "HEAD.lock.stale-*")))
    present = [p for p in targets if os.path.exists(p)]
    stale_blocking = [p for p in present if os.path.basename(p) in BLOCKING and stale(p)]
    stale_all = [p for p in present if stale(p)]
    fresh = [p for p in present if not stale(p)]

    for p in fresh:
        print("  fresh lock left in place (<%d min): .git/%s" % (STALE_SECONDS // 60, os.path.basename(p)))
    if check_only:
        for p in stale_all:
            print("  STALE: .git/" + os.path.basename(p))
        if asides:
            print("  %d HEAD.lock.stale-* asides await the host sweep" % len(asides))
        return 1 if stale_blocking else 0

    if not stale_all and not asides:
        print("git_unlock.py: no stale locks, nothing to sweep"); return 0
    if git_running():
        print("git_unlock.py: a git process is live here -- leaving all locks in place"); return 0

    os.makedirs(ASIDE, exist_ok=True)
    ts = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    healed = 0
    for p in stale_all + asides:
        dest = os.path.join(ASIDE, "%s.%s" % (os.path.basename(p), ts))
        try:
            os.rename(p, dest)                 # rename works where unlink is blocked
            healed += 1
            print("  healed: .git/%s -> stale_locks/" % os.path.basename(p))
        except OSError as e:
            print("  FAILED to aside .git/%s (%s)" % (os.path.basename(p), e))
    orphans = len(glob.glob(os.path.join(GITDIR, "objects", "*", "tmp_obj_*")))
    if orphans:
        print("  note: %d orphaned tmp_obj files in .git/objects (host sweep deletes them)" % orphans)
    print("git_unlock.py: %d lock(s)/aside(s) healed by rename" % healed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
