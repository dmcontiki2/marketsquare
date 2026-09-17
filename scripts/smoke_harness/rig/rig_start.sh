#!/bin/bash
pkill -f rig_run.py 2>/dev/null; sleep 1
cd /home/claude/rig
MS_API_KEY=ms_mk_2026_pretoria_admin MS_REVIEW_SECRET=rigsecret_rigsecret_rigsecret_rigsecret MS_JWT_SECRET=rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt MS_ADMIN_KEY=rigadminkey setsid nohup python3 /home/claude/rig_run.py > /home/claude/rig.log 2>&1 < /dev/null &
for i in $(seq 1 16); do sleep 3; curl -s -m 3 http://127.0.0.1:8000/health >/dev/null 2>&1 && { echo "rig up (~$((i*3))s)"; break; }; done
