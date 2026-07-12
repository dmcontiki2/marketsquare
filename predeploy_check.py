#!/usr/bin/env python3
# predeploy_check.py - MarketSquare PRE-DEPLOY change scan (added 9 Jul 2026)
# -----------------------------------------------------------------------------
# Detective control for the multi-session concurrency gap: before a deploy ships
# the working tree, this reports EXACTLY what is about to go live, flags files
# another session may have changed since, and appends every run to
# deploy_audit.log so a scan is never lost to luck.
#
# NON-FATAL BY DESIGN (same rule as the Step 7 auto-commit): a monitor must never
# break a good deploy. Default mode = 'warn' -> always exits 0 (informational,
# never aborts). Set PREDEPLOY_MODE=strict to exit 1 on a genuinely dangerous
# change (a torn/incomplete file) so deploy_marketsquare.bat can abort.
import os, sys, subprocess, time
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
LOG  = os.path.join(HERE, 'deploy_audit.log')
MODE = os.environ.get('PREDEPLOY_MODE', 'warn').lower()
RECENT_MIN = int(os.environ.get('PREDEPLOY_RECENT_MIN', '25'))

# The files the deploy actually ships (kept in sync with deploy_marketsquare.bat).
TARGETS = [
    'marketsquare.html', 'marketsquare_admin.html', 'ms.js', 'ms.css',
    'privacy.html', 'terms.html', 'support.html', 'assets/service-worker.js',
    'bea_main.py', 'auth.py', 'database.py', 'storage.py', 'payments.py',
    'ai_provider.py', 'ai_service_tiers.py', 'launch_redemption.py',
    'wonders.json', 'demo_listings.json', 'demo_sellers.json',
]
TEXT_EXT = ('.py', '.js', '.css', '.html', '.json')

def _git(args):
    try:
        r = subprocess.run(['git'] + args, cwd=HERE, capture_output=True,
                           text=True, timeout=20)
        return r.stdout if r.returncode == 0 else ''
    except Exception:
        return ''

def _head_size(rel):
    try:
        r = subprocess.run(['git', 'cat-file', '-s', 'HEAD:' + rel], cwd=HERE,
                           capture_output=True, text=True, timeout=15)
        if r.returncode == 0 and r.stdout.strip().isdigit():
            return int(r.stdout.strip())
    except Exception:
        pass
    return None

def main():
    now = time.time()
    dirty = set()
    for line in _git(['status', '--porcelain']).splitlines():
        if line.strip():
            dirty.add(line[3:].strip().replace('\\', '/'))
    rows, recent, danger = [], [], []
    for rel in TARGETS:
        p = os.path.join(HERE, rel)
        if not os.path.isfile(p):
            continue
        st = os.stat(p)
        size, age_min = st.st_size, (now - st.st_mtime) / 60.0
        modified = rel in dirty
        is_recent = modified and age_min <= RECENT_MIN
        torn = False
        if rel.endswith(TEXT_EXT) and size > 1:
            try:
                with open(p, 'rb') as f:
                    f.seek(-1, 2); last = f.read(1)
                hsz = _head_size(rel)
                if last != b'\n' and hsz is not None and size < hsz:
                    torn = True   # ends mid-line AND shorter than committed = torn
            except Exception:
                pass
        if modified:
            flags = ['modified']
            if is_recent: flags.append('RECENT(<%dm)' % RECENT_MIN); recent.append(rel)
            if torn: flags.append('TORN'); danger.append(rel)
            rows.append((rel, size, age_min, flags))
    stamp = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    print('  ------------------------------------------------------------')
    print('  PRE-DEPLOY CHANGE SCAN   %s   mode=%s' % (stamp, MODE))
    print('  Working tree: %d file(s) uncommitted; %d deploy target(s) changed.'
          % (len(dirty), len(rows)))
    for rel, size, age, flags in sorted(rows, key=lambda r: r[2]):
        print('    - %-32s %8d B  %5.0f min ago  [%s]'
              % (rel, size, age, ', '.join(flags)))
    if recent:
        print('  >> HEADS-UP: %d target(s) changed in the last %d min - could be'
              ' another session:' % (len(recent), RECENT_MIN))
        print('     ' + ', '.join(recent))
    if danger:
        print('  !! DANGER: torn/incomplete file(s): ' + ', '.join(danger))
    verdict = 'DANGER' if danger else ('REVIEW' if recent else 'ok')
    print('  Verdict: %s   (logged -> deploy_audit.log)' % verdict)
    print('  ------------------------------------------------------------')
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write('%s mode=%s dirty=%d changed=%d recent=%s danger=%s verdict=%s\n'
                    % (stamp, MODE, len(dirty), len(rows),
                       '|'.join(recent) or '-', '|'.join(danger) or '-', verdict))
    except Exception:
        pass
    if danger:
        try:
            fn = os.path.join(HERE, 'DEPLOY_REVIEW_%s.flag'
                              % datetime.now().strftime('%Y%m%d-%H%M%S'))
            with open(fn, 'w', encoding='utf-8') as f:
                f.write('Pre-deploy scan flagged torn/incomplete file(s):\n  %s\n'
                        'See deploy_audit.log. Fix or restore before deploying.\n'
                        % ', '.join(danger))
        except Exception:
            pass
        if MODE == 'strict':
            return 1
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:   # a monitor must never break a deploy
        print('  [predeploy_check] non-fatal error: %r (continuing)' % e)
        sys.exit(0)
