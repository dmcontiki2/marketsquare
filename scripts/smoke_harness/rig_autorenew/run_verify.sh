#!/bin/bash
# fresh rig + the rendered proof, in the background; pid in rigdata/verify.pid
[ -f /home/claude/rigdata/verify.pid ] && kill "$(cat /home/claude/rigdata/verify.pid)" 2>/dev/null
rm -rf /home/claude/rigdata; /home/claude/rigkit/rig_start.sh >/dev/null 2>&1
python3 - <<'PY'
import sys; sys.path.insert(0,'/home/claude/rigkit')
from rig_lib import *
sql("UPDATE launch_switches SET mode='live' WHERE id=1")
PY
rm -rf "${SHOT_DIR:-/home/claude/shots/AUTO_RENEW_shots}"
cd /home/claude/rigkit && setsid nohup python3 -u verify_auto_renew.py > /home/claude/rigdata/verify.log 2>&1 &
echo $! > /home/claude/rigdata/verify.pid
