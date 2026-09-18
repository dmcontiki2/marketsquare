#!/usr/bin/env python3
"""work_lock.py -- WORK-LOCK-1 (RUL-140, David 17 Sep 2026): a lane told to stand off a scope
must not edit that scope, and the telling must be a FILE every lane can check, not a memory.

David's words: "i expressly warned the Maintenance loop you are busy with design changes to
the models and it should not interfere" -- and it interfered anyway (17 Sep: the daily-watch
CTO lane inserted a hard cost ceiling into bea_main.py mid-edit, which then shipped inside
another session's release). A verbal stand-off has no machinery; this file is the machinery.

  python3 scripts/work_lock.py take  "<owner>" "<why>" <path-or-glob> [<path-or-glob> ...]
  python3 scripts/work_lock.py check <path> [<path> ...]      # exit 3 if any path is locked
  python3 scripts/work_lock.py show
  python3 scripts/work_lock.py release "<owner>"

The lock lives at <repo>/.work_lock (JSON, gitignored). EVERY lane -- daily watch, CTO fixer,
maintenance agent, batch builds, scheduled tasks -- runs `check` on a file before editing it and
STOPS on exit 3: it records the finding it wanted to fix (ledger / DAILY_WATCH) and leaves the
file alone. A lock older than 12 hours is reported STALE by `show` and `check` treats it as
expired, so a dead session can never freeze the repo. Scope paths are repo-relative; globs
follow fnmatch ('bea_main.py', 'scripts/*', 'ai_*').
"""
import fnmatch, json, os, sys, time
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOCK = os.path.join(REPO, ".work_lock")
TTL_S = 12 * 3600

def _load():
    try:
        with open(LOCK, encoding="utf-8") as fh:
            return json.load(fh)
    except Exception:
        return None

def _age(d):
    return time.time() - float(d.get("taken_at_epoch") or 0)

def take(owner, why, scopes):
    d = _load()
    if d and _age(d) < TTL_S and d.get("owner") != owner:
        print("REFUSED: %s holds the lock on %s (%s) -- release or wait" % (d["owner"], d["scope"], d["why"]))
        return 3
    d = {"owner": owner, "why": why, "scope": list(scopes), "taken_at_epoch": time.time(),
         "taken_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with open(LOCK, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=1)
    print("LOCKED %s by %s: %s" % (d["scope"], owner, why)); return 0

def check(paths):
    d = _load()
    if not d:
        print("no lock"); return 0
    if _age(d) >= TTL_S:
        print("lock by %s is STALE (%.1fh) -- treated as expired" % (d["owner"], _age(d) / 3600)); return 0
    hit = []
    for p in paths:
        rel = os.path.relpath(os.path.abspath(p), REPO).replace("\\", "/")
        if any(fnmatch.fnmatch(rel, s) or rel == s or rel.startswith(s.rstrip("/") + "/") for s in d["scope"]):
            hit.append(rel)
    if hit:
        print("LOCKED by %s since %s -- %s\n  do NOT edit: %s\n  record the finding instead; the owner ships it."
              % (d["owner"], d["taken_at"], d["why"], ", ".join(hit)))
        return 3
    print("clear (lock by %s covers %s, not these paths)" % (d["owner"], d["scope"])); return 0

def show():
    d = _load()
    if not d:
        print("no lock"); return 0
    print(json.dumps(dict(d, age_hours=round(_age(d) / 3600, 2), stale=_age(d) >= TTL_S), indent=1)); return 0

def release(owner):
    d = _load()
    if not d:
        print("no lock"); return 0
    if d.get("owner") != owner and _age(d) < TTL_S:
        print("REFUSED: lock is held by %s, not %s" % (d["owner"], owner)); return 3
    # WORK-LOCK-2 (18 Sep 2026): the sandbox mount refuses unlink (same FUSE/permission class
    # that forced RENAME on git locks -- GIT-LOCK-3 / RG-0015 / RG-0379). os.remove() here raised
    # PermissionError and left the lock in place, so `release` reported a crash and every later
    # lane read exit 3 and stood off a file nobody was editing -- a lock that cannot be released
    # is a repo that freezes for TTL. Rename is the only move the mount allows, and renaming the
    # lock aside is equivalent to removing it because _load() only ever reads LOCK by that name.
    try:
        os.remove(LOCK)
    except OSError:
        aside = LOCK + ".released-" + time.strftime("%Y%m%d-%H%M%S", time.gmtime())
        try:
            os.replace(LOCK, aside)
        except OSError as e:
            print("REFUSED: cannot release the lock (neither unlink nor rename): %s" % e)
            return 4
    print("released"); return 0

if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit(2)
    cmd = a[0]
    if cmd == "take" and len(a) >= 4: sys.exit(take(a[1], a[2], a[3:]))
    if cmd == "check" and len(a) >= 2: sys.exit(check(a[1:]))
    if cmd == "show": sys.exit(show())
    if cmd == "release" and len(a) >= 2: sys.exit(release(a[1]))
    print(__doc__); sys.exit(2)
