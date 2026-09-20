#!/usr/bin/env python3
"""DEPLOY-GATE-ALL-1 -- install the local git hooks that gate the deploy ref.

Why (DW-136, 18 Sep 2026): on 18 Sep a deploy rode while the regression board
read REGRESSION, and nothing stopped it. The push used the raw lane the runbook
itself documents -- `git push origin HEAD:deploy` -- and that lane runs no
pre-deploy scan. RG-0381 had fixed the lane a HUMAN double-clicks
(deploy_marketsquare.bat never set PREDEPLOY_MODE, so for four months it printed
"Verdict: DANGER" and shipped anyway), but its premise -- that the automated
lanes always stop on a red -- does not reach a bare git push.

A hook is the right shape because it sits on the TRANSPORT, not on any one
wrapper script: you cannot dodge it by choosing a different .bat. It can only be
passed deliberately and visibly, via PREDEPLOY_MODE=warn or --no-verify.

Idempotent: safe to re-run any time, and it must be re-run after a fresh clone,
because git hooks are local to a clone and are never carried by git itself.

    python3 scripts/install_git_hooks.py           # install / repair
    python3 scripts/install_git_hooks.py --check   # report only, exit 1 if wrong
"""
from __future__ import annotations

import argparse
import os
import stat
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK_DIR = os.path.join(REPO, ".git", "hooks")
PRE_PUSH = os.path.join(HOOK_DIR, "pre-push")
MARKER = "DEPLOY-GATE-ALL-1"

# NOTE ON ORDERING, which is the whole of RG-0381's lesson: PREDEPLOY_MODE is
# exported BEFORE predeploy_check.py runs. predeploy_check defaults to 'warn'
# and returns 0 unless the mode is strict, so setting it afterwards is the same
# as not setting it at all.
HOOK = r'''#!/bin/sh
# DEPLOY-GATE-ALL-1 -- pre-push gate on the deploy ref (DW-136, RG-0422).
# Installed by scripts/install_git_hooks.py. Re-run that after a fresh clone;
# git does not carry hooks.
#
# Fires ONLY for refs/heads/deploy -- the ref that actually ships. Pushing main
# deploys nothing (mirror backup only), so main is deliberately untouched.
#
# Escape hatch, named and visible:  PREDEPLOY_MODE=warn git push ...
#                             or:   git push --no-verify ...
# A gate with no escape hatch gets commented out the first time it is wrong.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0
GATED=0
while read -r _local_ref _local_sha remote_ref _remote_sha; do
    case "$remote_ref" in
        refs/heads/deploy) GATED=1 ;;
    esac
done
[ "$GATED" = "1" ] || exit 0

echo ""
echo "  DEPLOY-GATE-ALL-1: publishing the deploy ref -- running the pre-deploy scan."

if [ "${PREDEPLOY_MODE}" = "warn" ]; then
    echo "  PREDEPLOY_MODE=warn set deliberately -- scan is advisory, push allowed."
    PREDEPLOY_MODE=warn
    export PREDEPLOY_MODE
    python3 "$REPO_ROOT/predeploy_check.py" || true
    exit 0
fi

# Strict BEFORE the scan runs (RG-0381).
PREDEPLOY_MODE=strict
export PREDEPLOY_MODE
python3 "$REPO_ROOT/predeploy_check.py"
rc=$?
if [ "$rc" != "0" ]; then
    echo ""
    echo "  PUSH REFUSED -- the pre-deploy scan reached a DANGER verdict."
    echo "  This is the gate DW-136 was raised for: on 18 Sep 2026 a deploy rode"
    echo "  while the board read REGRESSION, because this lane had no gate."
    echo ""
    echo "  Fix the cause, or push deliberately with one of:"
    echo "      PREDEPLOY_MODE=warn git push origin HEAD:deploy"
    echo "      git push --no-verify origin HEAD:deploy"
    echo ""
    exit 1
fi
echo "  Pre-deploy scan: ok -- push allowed."
exit 0
'''


def _installed_ok() -> tuple[bool, list[str]]:
    problems = []
    if not os.path.isdir(HOOK_DIR):
        return False, [".git/hooks does not exist (not a git working tree?)"]
    if not os.path.isfile(PRE_PUSH):
        return False, ["pre-push hook is not installed"]
    body = open(PRE_PUSH, encoding="utf-8", errors="replace").read()
    if MARKER not in body:
        problems.append("pre-push exists but is not ours (no %s marker) -- left alone"
                        % MARKER)
    if "predeploy_check.py" not in body:
        problems.append("pre-push does not run predeploy_check.py")
    if "refs/heads/deploy" not in body:
        problems.append("pre-push does not key on refs/heads/deploy")
    if not os.access(PRE_PUSH, os.X_OK):
        problems.append("pre-push is not executable -- git ignores it silently")
    return (not problems), problems


def install(force: bool = False) -> int:
    if not os.path.isdir(HOOK_DIR):
        print("no .git/hooks here -- nothing to install")
        return 1
    if os.path.isfile(PRE_PUSH):
        existing = open(PRE_PUSH, encoding="utf-8", errors="replace").read()
        if MARKER not in existing and not force:
            print("REFUSING: a pre-push hook exists that is not ours. Inspect it, then "
                  "re-run with --force if it is safe to replace.\n  %s" % PRE_PUSH)
            return 1
    with open(PRE_PUSH, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HOOK)
    os.chmod(PRE_PUSH, os.stat(PRE_PUSH).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    ok, problems = _installed_ok()
    if not ok:
        print("installed but verification failed:")
        for p in problems:
            print("  -", p)
        return 1
    print("pre-push deploy gate installed and verified: %s" % PRE_PUSH)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="install the local deploy-ref push gate")
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if not armed")
    ap.add_argument("--force", action="store_true", help="replace a foreign pre-push hook")
    a = ap.parse_args()
    if a.check:
        ok, problems = _installed_ok()
        if ok:
            print("pre-push deploy gate: ARMED")
            return 0
        print("pre-push deploy gate: NOT ARMED")
        for p in problems:
            print("  -", p)
        return 1
    return install(force=a.force)


if __name__ == "__main__":
    sys.exit(main())
