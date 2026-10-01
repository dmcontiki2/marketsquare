#!/usr/bin/env python3
"""sync_origin.py -- SYNC-ORIGIN-1 (RUL-193, 1 Oct 2026): take GitHub's newer commits in BEFORE any push.

David, 1 Oct 2026: "so that nothing is stopped, wiped, overwritten between the cloud and laptop,
except if it is done by design." Cloud sessions ship straight to GitHub main/deploy (CLOUD-SHIP-1),
so the laptop can fall behind without knowing it. On 1 Oct it was 61 commits behind: every laptop
push would have been refused (stopped), and a forced one would have wiped the cloud's work.

Every lane that pushes calls this first. It:
  1. fetches origin;
  2. if origin/<branch> is already inside HEAD -> nothing to do (exit 0);
  3. else takes it in -- fast-forward when HEAD has nothing of its own, otherwise a normal merge commit;
  4. on ANY conflict (or uncommitted local work the merge would touch) it aborts the merge, leaves every
     file exactly as it was, writes SYNC_CONFLICT.txt naming the files, and exits 3 -- the caller then
     stops BEFORE pushing. A conflict is a decision for a person or a session, never for a script.
Never rebases, never resets, never forces. Exit 4 = GitHub unreachable (do not push blind).

    python scripts/sync_origin.py [--repo PATH] [--branch main] [--check]
--check reports how far behind/ahead the tree is and changes nothing.
"""
import os, subprocess, sys
from datetime import datetime, timezone

def _arg(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a and a.index(name) + 1 < len(a) else default

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(_arg('--repo', os.path.dirname(HERE)))
BRANCH = _arg('--branch', 'main')
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0', GIT_MERGE_AUTOEDIT='no')
REPORT = os.path.join(REPO, 'SYNC_CONFLICT.txt')

def git(*a, timeout=180):
    r = subprocess.run(['git', *a], cwd=REPO, env=ENV, capture_output=True, text=True, timeout=timeout)
    return r.returncode, (r.stdout or '').strip(), (r.stderr or '').strip()

def say(msg):
    print('sync-origin [%s]: %s' % (os.path.basename(REPO), msg))

def main():
    up = 'origin/' + BRANCH
    rc, _, err = git('fetch', '-q', 'origin', BRANCH)
    if rc:
        say('could not reach GitHub (%s) -- NOT safe to push blind; stopping' % (err.splitlines() or ['?'])[-1][:120])
        return 4
    behind = git('rev-list', '--count', 'HEAD..' + up)[1] or '0'
    ahead = git('rev-list', '--count', up + '..HEAD')[1] or '0'
    if behind == '0':
        say('in step with %s (this tree is %s commit(s) ahead)' % (up, ahead))
        if os.path.exists(REPORT):
            os.replace(REPORT, REPORT + '.resolved')   # an old conflict note must not read as current
        return 0
    if '--check' in sys.argv:
        say('BEHIND %s by %s commit(s), ahead by %s -- the next push takes them in first' % (up, behind, ahead))
        return 0
    if ahead == '0':
        rc, out, err = git('merge', '--ff-only', '-q', up)
        how = 'fast-forward'
    else:
        rc, out, err = git('merge', '--no-ff', '--no-edit', '-q', '-m',
                           'SYNC-ORIGIN-1: take in %s (%s commit(s) from the cloud/GitHub)' % (up, behind), up)
        how = 'merge'
    if rc == 0:
        say('took in %s commit(s) from %s by %s -> %s' % (behind, up, how, git('rev-parse', '--short', 'HEAD')[1]))
        if os.path.exists(REPORT):
            os.replace(REPORT, REPORT + '.resolved')
        return 0
    conflicted = git('diff', '--name-only', '--diff-filter=U')[1].splitlines()
    if os.path.exists(os.path.join(REPO, '.git', 'MERGE_HEAD')) or conflicted:
        git('merge', '--abort')
    detail = (err or out).splitlines()
    with open(REPORT, 'w', encoding='utf-8') as f:
        f.write('SYNC-ORIGIN-1 STOP %s\n' % datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ'))
        f.write('This tree could not take in %s commit(s) from %s cleanly, so NOTHING was pushed and\n'
                'nothing was overwritten. The merge was aborted; every file is as it was.\n\n' % (behind, up))
        if conflicted:
            f.write('Files changed on BOTH sides:\n' + ''.join('  - %s\n' % c for c in conflicted) + '\n')
        f.write('git said:\n' + ''.join('  %s\n' % l for l in detail[-12:]) + '\n')
        f.write('To finish: merge %s by hand (keep both sides\' intent), commit, then ship again.\n' % up)
    why = next((l for l in detail if 'overwritten' in l or l.lower().startswith('error')), detail[-1] if detail else '?')
    say('STOP -- %s commit(s) on %s could not be taken in cleanly (%s); nothing pushed, nothing overwritten. '
        'See SYNC_CONFLICT.txt' % (behind, up, ', '.join(conflicted[:6]) or why[:140]))
    return 3

if __name__ == '__main__':
    sys.exit(main())
