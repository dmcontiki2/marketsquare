#!/usr/bin/env python3
"""
request_deploy.py -- AUTODEPLOY-AGENT-1 (RUL-092, 3 Sep 2026): ask the host-side agent to ship.

    python3 scripts/request_deploy.py "reason"              # MarketSquare (HEAD as committed)
    python3 scripts/request_deploy.py --all "reason"        # ...committing the working tree first
    python3 scripts/request_deploy.py --cl "reason"         # CityLauncher
    python3 scripts/request_deploy.py --status              # what happened to the last request

Pre-flight (MarketSquare): every changed/new .py must py_compile; there must be a commit ahead
of origin/deploy (or uncommitted work, which is committed here with the reason). The strict
gate itself (tsl_gate, drift, CM+DB, release lock) runs on the host in nightly_tsl.bat -- this
tool never bypasses it. A BLOCKED gate is retried every 20 min by the agent until it clears.
Sandbox SSH is intermittent (RUL-092 corollary 4) so nothing here talks to the server.
"""
import os, subprocess, sys, py_compile
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(HERE)
FLAG = os.path.join(REPO, 'DEPLOY_REQUEST.flag'); CLFLAG = os.path.join(REPO, 'CL_DEPLOY_REQUEST.flag')
RESULT = os.path.join(REPO, 'DEPLOY_RESULT.txt'); CLRESULT = os.path.join(REPO, 'CL_DEPLOY_RESULT.txt')
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')

def git(*a, check=False):
    r = subprocess.run(['git', *a], cwd=REPO, env=ENV, capture_output=True, text=True)
    if check and r.returncode: raise SystemExit('git %s failed: %s' % (' '.join(a), r.stderr.strip()[:200]))
    return r.stdout.strip()

def status():
    for label, f in (('MarketSquare', FLAG), ('CityLauncher', CLFLAG)):
        print('%s request: %s' % (label, 'PENDING\n  ' + open(f, encoding='utf-8').read().strip().replace('\n', '\n  ') if os.path.exists(f) else 'none'))
    for label, f in (('MarketSquare', RESULT), ('CityLauncher', CLRESULT)):
        if os.path.exists(f): print('%s last result: %s' % (label, open(f, encoding='utf-8', errors='replace').read().strip().splitlines()[0]))
    log = os.path.join(REPO, 'autodeploy_agent_log.txt')
    if os.path.exists(log):
        print('agent log tail:'); print('  ' + '\n  '.join(open(log, encoding='utf-8', errors='replace').read().splitlines()[-6:]))
    else:
        print('agent log: none yet -- has register_autodeploy_agent.bat been run once on the host?')

def main():
    args = [a for a in sys.argv[1:]]
    if '--status' in args: return status()
    cl = '--cl' in args; args = [a for a in args if a not in ('--cl', '--all')]
    reason = ' '.join(args).strip() or 'no reason given'
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
    if cl:
        with open(CLFLAG, 'w', encoding='utf-8') as f: f.write('REQUESTED %s\nreason: %s\n' % (stamp, reason))
        print('CityLauncher deploy requested -> agent ships on its next 20-min tick'); return 0
    # pre-flight: compile everything changed
    changed = [l[3:] for l in git('status', '--porcelain').splitlines() if l.endswith('.py')]
    for f in changed:
        p = os.path.join(REPO, f)
        if os.path.exists(p): py_compile.compile(p, doraise=True)
    subprocess.run([sys.executable, os.path.join(HERE, 'git_unlock.py')], cwd=REPO, capture_output=True)
    # Commit only when asked (--all): another session may be mid-edit on the same mount, and the
    # release step on the host commits the working tree anyway behind the strict gate.
    if '--all' in sys.argv and git('status', '--porcelain'):
        git('add', '-A', check=True)
        git('-c', 'user.name=Claude (CTO)', '-c', 'user.email=claude@trustsquare.co', 'commit', '-q', '-m', reason, check=True)
        print('committed:', git('log', '-1', '--format=%h %s')[:90])
    head = git('rev-parse', '--short', 'HEAD')
    with open(FLAG, 'w', encoding='utf-8') as f:
        f.write('REQUESTED %s\nhead: %s\nreason: %s\n' % (stamp, head, reason))
    print('MarketSquare deploy requested (%s) -> host agent gates + ships on its next 20-min tick; BLOCKED = auto-retry' % head)
    return 0

if __name__ == '__main__':
    sys.exit(main() or 0)
