#!/usr/bin/env python3
"""test_hostqueue_watchdog1.py -- HOSTQUEUE-WATCHDOG-1 (25 Sep 2026).

The outage this is red on: autodeploy_agent.bat -- Claude's only hands outside the sandbox
(RUL-095) -- stopped after 13:15:06Z on 25 Sep and nothing noticed for 7h31m. By the evening
stand-up five commits were stranded unpushed, including the 25 Sep inspection's critical fixes,
so nothing had reached the mirror and nothing could deploy. Every site-facing instrument read
green throughout, correctly: the site was fine. A healthy site is not evidence that the way to
change it is open.

Pins both signals, because 25 Sep tripped only the second one:
  * a permission-backed request queued past two whole ticks  -> STALLED
  * commits committed but never pushed for more than a tick  -> STALLED
and pins that ordinary states are NOT reported as trouble, so the watchdog stays worth reading.

  python3 scripts/test_hostqueue_watchdog1.py
"""
import importlib.util, os, subprocess, sys, tempfile, time

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TARGET = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "scripts", "maintenance_agent.py")

def load(repo):
    src = TARGET
    if not src.endswith(".py"):          # allow pointing at a .bak- copy of the pre-fix source
        import shutil
        src = os.path.join(tempfile.mkdtemp(prefix="maint-src-"), "maint_under_test.py")
        shutil.copy(TARGET, src)
    spec = importlib.util.spec_from_file_location("maint_under_test", src)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    mod.REPO = repo
    mod.say = lambda *a, **k: None
    return mod

def fixture(pending_age_s=None, unpushed_age_s=None, result_age_s=3600):
    """A throwaway repo with a host_queue/ and, optionally, unpushed commits."""
    repo = tempfile.mkdtemp(prefix="hq-test-")
    q = os.path.join(repo, "host_queue"); os.makedirs(os.path.join(q, "done"))
    r = os.path.join(q, "done", "20260101-000000-000_git_push_x.result")
    open(r, "w").write("ok"); os.utime(r, (time.time() - result_age_s,) * 2)
    if pending_age_s is not None:
        f = os.path.join(q, "20260101-000001-000_git_push_x.req")
        open(f, "w").write("action=git_push"); os.utime(f, (time.time() - pending_age_s,) * 2)
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0", GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
    def g(*a, **k):
        e = k.pop("env", env)
        return subprocess.run(["git", *a], cwd=repo, env=e, capture_output=True, text=True, **k)
    g("init", "-q", "-b", "main"); open(os.path.join(repo, "a"), "w").write("1")
    g("add", "-A"); g("commit", "-qm", "base")
    g("update-ref", "refs/remotes/origin/main", "HEAD")      # mirror == HEAD
    if unpushed_age_s is not None:
        when = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(time.time() - unpushed_age_s))
        open(os.path.join(repo, "b"), "w").write("2"); g("add", "-A")
        g("commit", "-qm", "unpushed", env=dict(env, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when))
    return repo

def main():
    fails = []
    def check(name, cond, got=""):
        print("%-62s %s" % (name, "ok" if cond else "FAIL " + str(got)))
        if not cond: fails.append(name)

    m = load(HERE)
    if not hasattr(m, "_hostqueue_lane"):
        print("has _hostqueue_lane()".ljust(62), "FAIL (absent -- nothing watches the host lane)")
        print("\nRED: the host-action lane has no detector -- %s" % TARGET); return 1

    # 1. quiet and current: not trouble
    m.REPO = fixture(); r = m._hostqueue_lane()
    check("quiet queue, nothing unpushed -> OK", r["state"] == "OK", r)

    # 2. a request queued 5 min ago: one tick has not passed, not trouble
    m.REPO = fixture(pending_age_s=5 * 60); r = m._hostqueue_lane()
    check("request queued 5 min ago -> OK (inside one tick)", r["state"] == "OK", r)

    # 3. a request queued 90 min ago: the executor is not running
    m.REPO = fixture(pending_age_s=90 * 60); r = m._hostqueue_lane()
    check("request queued 90 min ago -> STALLED", r["state"] == "STALLED", r)

    # 4. THE 25 SEP SHAPE: nothing queued, but commits stranded for hours
    m.REPO = fixture(unpushed_age_s=5 * 3600); r = m._hostqueue_lane()
    check("nothing queued but commits unpushed 5 h -> STALLED", r["state"] == "STALLED", r)
    check("  and it counts them", r.get("ahead") == 1, r.get("ahead"))

    # 5. a commit pushed-ahead only moments ago is ordinary, not trouble
    m.REPO = fixture(unpushed_age_s=120); r = m._hostqueue_lane()
    check("a commit 2 min old -> OK (a push is allowed to be in flight)", r["state"] == "OK", r)

    print()
    if fails:
        print("RED: %d check(s) failed -- %s" % (len(fails), TARGET)); return 1
    print("GREEN: a host lane that is not running, and work stranded by one, both report "
          "themselves -- %s" % TARGET)
    return 0

if __name__ == "__main__":
    sys.exit(main())
