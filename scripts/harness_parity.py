#!/usr/bin/env python3
"""harness_parity.py -- HARNESS-PARITY-1 (RUL-193, 1 Oct 2026): quick.html and genie/HARNESS.html stay identical.

The cloud ship gate (ops/cloudship/cloud_branch_ship.sh) refuses every cloud branch while the two differ.
On 1 Oct a laptop ship changed quick.html alone and so blocked the cloud lane until a cloud session noticed.
--fix: if only ONE of the two changed since GitHub's main, copy it over the other (that is the edit someone
meant). If BOTH changed differently, change nothing and exit 3 -- that is a merge for a person/session.
Without --fix it only reports (exit 0 = identical, 3 = differ).
"""
import os, subprocess, sys
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
A, B = 'quick.html', os.path.join('genie', 'HARNESS.html')
ENV = dict(os.environ, GIT_OPTIONAL_LOCKS='0')

def rd(p):
    with open(os.path.join(REPO, p), 'rb') as f: return f.read()

def at_origin(p):
    r = subprocess.run(['git', 'show', 'origin/main:' + p.replace(os.sep, '/')], cwd=REPO, env=ENV, capture_output=True)
    return r.stdout if r.returncode == 0 else None

def norm(b): return b.replace(b'\r\n', b'\n') if b is not None else None

def main():
    a, b = rd(A), rd(B)
    if norm(a) == norm(b):
        print('harness-parity: quick.html == genie/HARNESS.html'); return 0
    if '--fix' not in sys.argv:
        print('harness-parity: quick.html and genie/HARNESS.html DIFFER -- run scripts/harness_parity.py --fix'); return 3
    oa, ob = norm(at_origin(A)), norm(at_origin(B))
    a_moved, b_moved = norm(a) != oa, norm(b) != ob
    if a_moved and not b_moved:
        with open(os.path.join(REPO, B), 'wb') as f: f.write(a)
        print('harness-parity: copied quick.html -> genie/HARNESS.html (only quick.html had changed)'); return 0
    if b_moved and not a_moved:
        with open(os.path.join(REPO, A), 'wb') as f: f.write(b)
        print('harness-parity: copied genie/HARNESS.html -> quick.html (only HARNESS.html had changed)'); return 0
    print('harness-parity: BOTH quick.html and genie/HARNESS.html changed, differently -- nothing copied; '
          'merge them by hand so they are identical'); return 3

if __name__ == '__main__':
    sys.exit(main())
