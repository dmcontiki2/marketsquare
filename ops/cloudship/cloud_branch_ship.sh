#!/bin/bash
# ─────────────────────────────────────────────────────────────────────────────
#  CLOUD-SHIP-1 (30 Sep 2026) — ships the story walks that Claude Code cloud sessions push.
#
#  A cloud session has no SSH, so it cannot use scripts/request_deploy.py. It pushes a branch
#  named claude/<anything> to GitHub instead, with "[ship]" in the tip commit's message. Every
#  2 minutes this job (on the server, which can push to main) fetches those branches and, for
#  each new [ship] tip:
#    1. takes origin/main forward to it -- a fast-forward, or a clean merge (a conflict is refused);
#    2. runs the gates: py_compile of every .py, node --check of every .js, route_policy.json parses,
#       quick.html == genie/HARNESS.html, build_help.py --check (screens looked up where /qa/help-image
#       wrote them), and no change under ops/ or .github/ (a branch never edits the deploy machinery) --
#       except the generated HELP-STORIES-1 block of deploy_manifest.txt, which lists a new guide's files;
#    3. pushes the result to main and deploy -> marketsquare-deploy.timer ships it (health-checked,
#       auto-rollback) as it does every other change.
#  Each tip is tried once; the outcome is written to $STATUS, which GET /qa/ship-status returns
#  so the cloud session can see "SHIPPED" or why not without SSH.
#  Installed to /usr/local/sbin (the copy runs, never the repo's), so no branch can change this job.
# ─────────────────────────────────────────────────────────────────────────────
set -u
SRC=/opt/marketsquare-src
WT=/opt/ms-cloudship
STDIR=/var/lib/ms-cloudship
STATUS=$STDIR/status.txt
SEEN=$STDIR/seen.txt
IMG=/var/www/marketsquare/help/img
mkdir -p "$STDIR"; chmod 755 "$STDIR"; touch "$SEEN" "$STATUS"; chmod 644 "$STATUS"
exec 9>/run/ms-cloudship.lock; flock -n 9 || exit 0

say() { echo "$(date -u +%Y-%m-%dT%H:%MZ) $*" >> "$STATUS"; tail -n 60 "$STATUS" > "$STATUS.t" && mv "$STATUS.t" "$STATUS"; chmod 644 "$STATUS"; }

cd "$SRC" || exit 0
git fetch -q --prune origin '+refs/heads/claude/*:refs/remotes/origin/claude/*' '+refs/heads/main:refs/remotes/origin/main' '+refs/heads/deploy:refs/remotes/origin/deploy' 2>/dev/null || exit 0
[ -d "$WT/.git" ] || [ -f "$WT/.git" ] || git worktree add -q --detach "$WT" origin/main 2>/dev/null

for ref in $(git for-each-ref --format='%(refname:short)' refs/remotes/origin/claude/); do
  tip=$(git rev-parse "$ref")
  grep -qx "$tip" "$SEEN" && continue
  git log -1 --format=%B "$tip" | grep -q '\[ship\]' || continue
  echo "$tip" >> "$SEEN"
  br=${ref#origin/}
  cd "$WT" || exit 0
  git reset -q --hard; git clean -qfd
  git checkout -q --detach origin/main
  if git merge-base --is-ancestor origin/main "$tip"; then
    git checkout -q --detach "$tip"
  elif ! git -c user.name="CLOUD-SHIP-1" -c user.email="dmcontiki2@gmail.com" merge -q --no-ff --no-edit -m "CLOUD-SHIP-1 merge $br [ship]" "$tip" >/dev/null 2>&1; then
    git merge --abort 2>/dev/null
    say "REFUSED $br ${tip:0:7}: conflicts with main -- rebase the branch on origin/main and push again"
    cd "$SRC"; continue
  fi
  new=$(git rev-parse HEAD)
  fail=""
  touched=$(git diff --name-only origin/main "$new")
  echo "$touched" | grep -vx 'ops/autodeploy/deploy_manifest.txt' | grep -qE '^(ops/|\.github/)' && fail="it changes ops/ or .github/ (deploy machinery stays with the laptop lanes)"
  # the manifest may change only inside the block build_help.py generates (a new guide's files)
  if [ -z "$fail" ] && echo "$touched" | grep -qx 'ops/autodeploy/deploy_manifest.txt'; then
    git show origin/main:ops/autodeploy/deploy_manifest.txt > /tmp/ms-cloudship.man0
    python3 - /tmp/ms-cloudship.man0 ops/autodeploy/deploy_manifest.txt <<'PY' || fail="deploy_manifest.txt changed outside the HELP-STORIES-1 block"
import sys, re
def strip(p):
    t = open(p, encoding="utf-8").read()
    return re.sub(r"# ── HELP-STORIES-1:.*?# ── end HELP-STORIES-1 ──\n?", "", t, flags=re.S)
sys.exit(0 if strip(sys.argv[1]) == strip(sys.argv[2]) else 1)
PY
  fi
  if [ -z "$fail" ]; then
    for f in $(echo "$touched" | grep -E '\.py$'); do
      [ -f "$f" ] && ! python3 -m py_compile "$f" 2>/dev/null && { fail="$f does not compile"; break; }
    done
  fi
  if [ -z "$fail" ]; then
    for f in $(echo "$touched" | grep -E '\.js$'); do
      [ -f "$f" ] && ! node --check "$f" 2>/dev/null && { fail="$f does not parse"; break; }
    done
  fi
  [ -z "$fail" ] && ! python3 -c "import json;json.load(open('route_policy.json'))" 2>/dev/null && fail="route_policy.json does not parse"
  [ -z "$fail" ] && ! cmp -s quick.html genie/HARNESS.html && fail="quick.html differs from genie/HARNESS.html"
  if [ -z "$fail" ]; then
    out=$(TS_HELP_IMG=$IMG python3 scripts/build_help.py --check 2>&1) || fail="build_help --check: $(echo "$out" | grep -E 'ERROR|STALE' | head -2 | tr '\n' ' ')"
  fi
  find . -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null
  if [ -n "$fail" ]; then
    say "REFUSED $br ${tip:0:7}: $fail"
    cd "$SRC"; continue
  fi
  if git push -q origin "$new:refs/heads/main" "$new:refs/heads/deploy" 2>/tmp/ms-cloudship.err; then
    say "SHIPPED $br ${tip:0:7} as ${new:0:7} -> live in ~2 min (health-checked, auto-rollback)"
    git -C "$SRC" fetch -q origin main deploy 2>/dev/null
  else
    say "REFUSED $br ${tip:0:7}: push to main/deploy failed ($(tail -1 /tmp/ms-cloudship.err)) -- will retry on the next [ship] commit"
  fi
  cd "$SRC"
done
exit 0
