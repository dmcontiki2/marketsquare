#!/usr/bin/env python3
"""
quiet_commit.py -- QUIET-COMMIT-1 (18 Sep 2026). Commit work that is waiting on tree silence,
WITHOUT a human watching for the silence.

    python3 scripts/quiet_commit.py --reason "..." [--quiet-minutes 8] [--max-attempts 12]

Why this exists. SO-5/RUL-140 says: after a run of updates, wait for the tree to be silent (no
other lane writing) and then commit ONCE. On 18 Sep the stand-up did the waiting part correctly --
it found a concurrent lane mid-edit in bea_main.py and RULINGS.md and stood its commit down rather
than sweep half-finished work into a release, which is the 17 Sep fault David named. But standing
down left the work uncommitted on disk with NOTHING WATCHING FOR THE SILENCE. "It will be committed
when the tree goes quiet" was true of nobody: the session ends, and the condition is never re-tested.
A deferred item with no watcher is the defect class David has repeatedly named as the cause of
recurring errors -- so the wait itself has to be machinery, exactly as WORK-LOCK-1 made the
stand-off machinery rather than a memory.

How it waits. Each invocation tests silence ONCE and then either commits or RE-QUEUES ITSELF on the
host queue, so the ~20-minute autodeploy tick becomes the retry clock. This mirrors request_deploy.py's
documented contract ("a BLOCKED gate is retried every 20 min by the agent until it clears") instead
of inventing a second waiting mechanism. It never sleeps, never holds the tick, and gives up after
--max-attempts so a permanently busy tree cannot queue forever.

What counts as silence. No tracked or untracked file under the repo modified in the last
--quiet-minutes, and no work_lock held by another owner. Ignored when judging silence, because they
are noise this process or the machinery itself makes: .git/, host_queue/, *.bak-*, __pycache__,
.maint_agent/, ledger_runs/, _verify_rig/, log files that append on their own, and the deploy/lock
markers. A false "quiet" reading is the whole risk here, so the ignore list is deliberately narrow:
anything a human or an agent would call source is in scope.

Safety. This commits; it does NOT push and does NOT deploy -- deploys stay with request_deploy.py and
its gate. It refuses to run if the tree is clean (nothing to commit) so a stray queue entry is inert.
"""
import argparse, os, subprocess, sys, time, json, fnmatch
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
LOCK = os.path.join(REPO, '.work_lock')
MARK = os.path.join(REPO, 'host_queue', 'QUIET_COMMIT_ATTEMPTS.txt')
REASON_FILE = os.path.join(REPO, 'host_queue', 'QUIET_COMMIT_REASON.txt')

IGNORE_DIRS = ('.git/', 'host_queue/', '__pycache__/', '.maint_agent/', 'ledger_runs/',
               '_verify_rig/', '_to_delete/', 'node_modules/', '.secrets/')
IGNORE_GLOBS = ('*.bak-*', '*.pyc', '*.log', '*_log.txt', 'nightly_ship_log.txt',
                'fw_selfheal_log.txt', 'DEPLOY_RESULT.txt', 'CL_DEPLOY_RESULT.txt',
                '.work_lock', '.work_lock.released-*', 'autodeploy_agent_log.txt')

def git(*a):
    return subprocess.run(['git', *a], cwd=REPO, env=ENV,
                          capture_output=True, text=True).stdout.strip()

def _ignored(rel):
    rel = rel.replace('\\', '/')
    if any(rel.startswith(d) or ('/' + d) in rel for d in IGNORE_DIRS):
        return True
    base = os.path.basename(rel)
    return any(fnmatch.fnmatch(base, g) or fnmatch.fnmatch(rel, g) for g in IGNORE_GLOBS)

def recently_written(quiet_minutes):
    """Return the files written inside the quiet window -- the evidence, not just a verdict."""
    cutoff = time.time() - quiet_minutes * 60
    hot = []
    for root, dirs, files in os.walk(REPO):
        dirs[:] = [d for d in dirs if not _ignored(os.path.relpath(os.path.join(root, d), REPO) + '/')]
        for fn in files:
            p = os.path.join(root, fn)
            rel = os.path.relpath(p, REPO)
            if _ignored(rel):
                continue
            try:
                if os.path.getmtime(p) > cutoff:
                    hot.append(rel)
            except OSError:
                continue
            if len(hot) > 40:
                return hot
    return hot

def other_lock(me):
    try:
        with open(LOCK, encoding='utf-8') as fh:
            d = json.load(fh)
    except Exception:
        return None
    if time.time() - float(d.get('taken_at_epoch') or 0) > 12 * 3600:
        return None                      # expired -- WORK-LOCK-1's own TTL
    return None if d.get('owner') == me else d.get('owner')

def _attempts():
    try:
        return int(open(MARK).read().strip() or 0)
    except Exception:
        return 0

def _bump(n):
    try:
        os.makedirs(os.path.dirname(MARK), exist_ok=True)
        with open(MARK, 'w') as fh:
            fh.write(str(n))
    except OSError:
        pass

def main():
    ap = argparse.ArgumentParser()
    # HOST-QUEUE reality (proven 18 Sep, first live tick): host_queue_worker.py runs an
    # allowlisted run_py entry with NO ARGUMENTS -- the request's `reason` field is metadata for
    # the log, not argv. --reason was required, so the very first real invocation died with
    # "the following arguments are required: --reason" and committed nothing. The mechanism built
    # to stop work sitting uncommitted sat uncommitted. So: the reason is OPTIONAL and is read
    # from a file the requester leaves beside the queue, falling back to a generic message. A tool
    # the queue cannot invoke is not a tool.
    ap.add_argument('--reason', default=None)
    ap.add_argument('--quiet-minutes', type=float, default=8.0)
    ap.add_argument('--max-attempts', type=int, default=12)
    ap.add_argument('--owner', default='quiet-commit')
    a = ap.parse_args()

    if not a.reason:
        try:
            a.reason = open(REASON_FILE, encoding='utf-8').read().strip() or None
        except OSError:
            a.reason = None
    if not a.reason:
        a.reason = 'Claude working-tree commit (QUIET-COMMIT-1, reason file absent)'

    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    if not git('status', '--porcelain'):
        print('%s quiet_commit: tree is clean -- nothing to commit, request is inert' % stamp)
        _bump(0); return 0

    held = other_lock(a.owner)
    hot = recently_written(a.quiet_minutes)
    n = _attempts() + 1

    if held or hot:
        why = ('work_lock held by %s' % held) if held else \
              ('%d file(s) written in the last %g min: %s' % (len(hot), a.quiet_minutes,
                                                              ', '.join(sorted(hot)[:6])))
        if n >= a.max_attempts:
            print('%s quiet_commit: GIVING UP after %d attempts -- %s' % (stamp, n, why))
            print('   the tree has not gone quiet; a human or the owning lane must commit.')
            _bump(0); return 1
        print('%s quiet_commit: NOT QUIET (attempt %d/%d) -- %s' % (stamp, n, a.max_attempts, why))
        _bump(n)
        r = subprocess.run([sys.executable, os.path.join(HERE, 'request_host_action.py'),
                            'run_py', r'MarketSquare\scripts\quiet_commit.py',
                            '--permission', "David, 3 Sep 2026 (RUL-095): commit + push of Claude's "
                                            "own work is permitted, no re-ask",
                            '--reason', a.reason],
                           capture_output=True, text=True)
        print('   re-queued for the next ~20-min tick:', (r.stdout or r.stderr).strip()[:160])
        return 0

    print('%s quiet_commit: QUIET (nothing written in %g min, no foreign lock) -- committing'
          % (stamp, a.quiet_minutes))
    subprocess.run([sys.executable, os.path.join(HERE, 'git_unlock.py')],
                   capture_output=True, text=True)
    subprocess.run(['git', 'add', '-A'], cwd=REPO, env=ENV, capture_output=True, text=True)
    msg = '%s\n\nCommitted by QUIET-COMMIT-1 after the tree went quiet (SO-5/RUL-140).' % a.reason
    r = subprocess.run(['git', 'commit', '-m', msg], cwd=REPO, env=ENV,
                       capture_output=True, text=True)
    print((r.stdout or r.stderr).strip()[-400:])
    _bump(0)
    return 0 if r.returncode == 0 else 1

if __name__ == '__main__':
    sys.exit(main())
