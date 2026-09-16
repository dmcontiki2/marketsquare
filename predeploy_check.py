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

# GIT-BLIND-1 (15 Sep 2026). Two faults in one call, found by the daily maintenance
# loop after this scan reported "0 file(s) uncommitted" against a tree with five
# modified files -- including bea_main.py, a deploy target.
#
# (a) It did not set GIT_OPTIONAL_LOCKS=0. CLAUDE.md has required that on every
#     sandbox git invocation since GIT-LOCK-3 (16 Aug): read-only git takes an index
#     lock on the FUSE-shared .git, and on this mount `git status` then sat past the
#     20s timeout every time.
# (b) Worse than the hang: the except swallowed it and returned an empty string, which
#     is indistinguishable from a CLEAN TREE. So `dirty` was empty, `modified` was
#     False for every target, and the torn-file detection -- the one genuinely
#     dangerous condition this control exists to catch, and the only thing that makes
#     the strict nightly abort -- could never fire. A monitor that cannot see reported
#     all clear.
#
# Blindness is now VISIBLE and is NOT a failure (the RG-0187 contract: an instrument
# limit is NOT EVALUATED, never a FAIL and never a silent pass). It is never added to
# `danger`, so it cannot abort a good nightly on a slow git; it is printed and it is
# stamped into deploy_audit.log as dirty=? so no future reader mistakes "could not
# look" for "nothing to see".
_GIT_ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')
GIT_BLIND = []          # reasons, if git could not answer at all


def _git(args, timeout=45):
    """(ok, stdout). ok is False when git could not answer -- never conflated with ''."""
    try:
        r = subprocess.run(['git'] + args, cwd=HERE, capture_output=True,
                           text=True, timeout=timeout, env=_GIT_ENV)
        if r.returncode != 0:
            return False, ''
        return True, r.stdout
    except Exception as exc:
        GIT_BLIND.append('%s: %s' % (' '.join(args[:2]), type(exc).__name__))
        return False, ''


def _head_size(rel):
    ok, out = _git(['cat-file', '-s', 'HEAD:' + rel], timeout=30)
    if ok and out.strip().isdigit():
        return int(out.strip())
    return None

def main():
    now = time.time()
    dirty = set()
    _ok, _status = _git(['status', '--porcelain'])
    if not _ok:
        GIT_BLIND.append('status --porcelain returned nothing usable')
    for line in _status.splitlines():
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
    if GIT_BLIND:
        print('  Working tree: NOT EVALUATED - git could not answer (%s).' % '; '.join(GIT_BLIND[:2]))
        print('    ^^ the torn-file check needs git and did NOT run. This is a blind scan,')
        print('       not a clean one: treat every "ok" below as unproven for tornness.')
    else:
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
    # Evidence-true trust invariant (24 Jul 2026): a Trust Score headline must equal
    # the evidence shown beside it. Run the source-level guard so a deploy that would
    # ship a diverged headline (the 87-over-50 class) is caught here, not by a buyer.
    try:
        import subprocess as _sp
        _tf = os.path.join(HERE, 'test_trust_evidence_true.py')
        if os.path.isfile(_tf):
            _tt = _sp.run([sys.executable, _tf, HERE], capture_output=True, text=True, timeout=30)
            if _tt.returncode != 0:
                danger.append('trust-evidence-true')
                print('  !! EVIDENCE-TRUE: trust headline/evidence check FAILED:')
                for _l in (_tt.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                print('  Evidence-true trust check: ok')
    except Exception as _e:
        print('  [evidence-true] check skipped: %r' % _e)

    # SCOREBOARD-1 guard suite (3 Aug 2026): the scoreboard's class rules — quality
    # is a GATE not a weight, 'unconfigured' is configuration not outage, flag-off
    # means ZERO probe spend — must hold on every deploy that ships the agent.
    try:
        import subprocess as _sp2
        _sf = os.path.join(HERE, 'test_ai_scoreboard.py')
        if os.path.isfile(_sf):
            _st = _sp2.run([sys.executable, _sf, HERE], capture_output=True, text=True, timeout=45)
            if _st.returncode != 0:
                danger.append('scoreboard-guards')
                print('  !! SCOREBOARD: guard suite FAILED:')
                for _l in (_st.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                print('  Scoreboard guard suite: ok')
    except Exception as _e:
        print('  [scoreboard] check skipped: %r' % _e)

    # BASE-40 canon guard (28 Jul 2026): every surface that writes or previews a
    # Trust Score must carry the universal 40-point base and the scorer's caps.
    # Added after the 40->5 bug: a base-less panel total gained write authority
    # (JNR-FIX-2 self-heal) and rewrote stored scores on profile view. The
    # evidence-true check above could not catch it (list and headline were wrong
    # together); this one checks the arithmetic canon itself.
    try:
        import subprocess as _sp2
        _tf2 = os.path.join(HERE, 'test_trust_base40.py')
        if os.path.isfile(_tf2):
            _tb = _sp2.run([sys.executable, _tf2, HERE], capture_output=True, text=True, timeout=30)
            if _tb.returncode != 0:
                danger.append('trust-base40')
                print('  !! BASE-40: trust arithmetic canon check FAILED:')
                for _l in (_tb.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                print('  Base-40 trust canon check: ok')
    except Exception as _e:
        print('  [base-40] check skipped: %r' % _e)

    # ONE-EVIDENCE-SET ratchet (15 Sep 2026, TRUST-ONE-SET-1). The two guards above
    # both passed while the buyer-facing panel was counting a different evidence set
    # from the scorer and writing its answer over the stored score. This one checks
    # that there is still exactly ONE evidence builder and that no surface writes a
    # score for a question it was not asked.
    try:
        import subprocess as _sp2b
        _tf2b = os.path.join(HERE, 'test_trust_one_set.py')
        if os.path.isfile(_tf2b):
            _to = _sp2b.run([sys.executable, _tf2b, HERE], capture_output=True, text=True, timeout=30)
            if _to.returncode != 0:
                danger.append('trust-one-set')
                print('  !! ONE-SET: a trust surface built its own evidence again:')
                for _l in (_to.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                print('  One-evidence-set trust check: ok')
    except Exception as _e:
        print('  [one-set] check skipped: %r' % _e)

    # PG-readiness ratchet (29 Jul 2026): the SQLite-specific surface must never
    # grow, so the post-launch Postgres move stays cheap (David's DB ruling).
    try:
        import subprocess as _sp3
        _tf3 = os.path.join(HERE, 'test_pg_readiness.py')
        if os.path.isfile(_tf3):
            _tp = _sp3.run([sys.executable, _tf3, HERE], capture_output=True, text=True, timeout=30)
            if _tp.returncode != 0:
                danger.append('pg-readiness')
                print('  !! PG-READINESS: SQLite-ism count grew:')
                for _l in (_tp.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                _rem = ''
                for _l in (_tp.stdout or '').splitlines():
                    if _l.startswith('PASS'):
                        _rem = _l.split('ratchet:',1)[-1].strip()
                print('  PG-readiness ratchet: ok — remaining to convert: ' + _rem)
    except Exception as _e:
        print('  [pg-readiness] check skipped: %r' % _e)

    # Maintenance Agent tripwires (B1, 29 Jul 2026): complaint pipeline guards —
    # fault codes, immediate ACK, working send path. See MAINTENANCE_AGENT.md.
    try:
        import subprocess as _sp4
        _tf4 = os.path.join(HERE, 'test_maintenance_agent.py')
        if os.path.isfile(_tf4):
            _tm = _sp4.run([sys.executable, _tf4, HERE], capture_output=True, text=True, timeout=30)
            if _tm.returncode != 0:
                danger.append('maintenance-agent')
                print('  !! MAINTENANCE: complaint-pipeline guard FAILED:')
                for _l in (_tm.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                print('  Maintenance-agent guards: ok')
    except Exception as _e:
        print('  [maintenance] check skipped: %r' % _e)

    # Tester fault-intake tripwires (MAINT-B1b, 5 Aug 2026): the in-app NCR channel —
    # table, endpoints, fail-closed flag, reference + ACK, widget on every tester page.
    try:
        import subprocess as _sp5
        _tf5 = os.path.join(HERE, 'test_tester_intake.py')
        if os.path.isfile(_tf5):
            _ti = _sp5.run([sys.executable, _tf5, HERE], capture_output=True, text=True, timeout=60)
            if _ti.returncode != 0:
                danger.append('tester-intake')
                print('  !! TESTER INTAKE: fault-report guard FAILED:')
                for _l in (_ti.stdout or '').splitlines():
                    if _l.startswith('FAIL'):
                        print('       ' + _l)
            else:
                print('  Tester fault-intake guards: ok')
    except Exception as _e:
        print('  [tester-intake] check skipped: %r' % _e)

    verdict = 'DANGER' if danger else ('REVIEW' if recent else 'ok')
    print('  Verdict: %s   (logged -> deploy_audit.log)' % verdict)
    print('  ------------------------------------------------------------')
    try:
        with open(LOG, 'a', encoding='utf-8') as f:
            f.write('%s mode=%s dirty=%s changed=%d recent=%s danger=%s verdict=%s\n'
                    % (stamp, MODE, ('?' if GIT_BLIND else str(len(dirty))), len(rows),
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
