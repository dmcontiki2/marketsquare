#!/bin/bash
# Start the stand-in and the app. A made-up TEST key; grants allowed on the rig only.
pkill -f rigkit/rig_run.py 2>/dev/null; pkill -f rigkit/rig_front.py 2>/dev/null; pkill -f rigkit/paystack_standin.py 2>/dev/null; sleep 1
mkdir -p /home/claude/rigdata
export RIG_PS_KEY="sk_test_rig_0123456789abcdef"
RIG_PS_KEY=$RIG_PS_KEY RIG_ORIGIN=http://127.0.0.1:8080 setsid nohup python3 /home/claude/rigkit/paystack_standin.py > /home/claude/rigdata/standin.log 2>&1 &
MS_API_KEY=ms_mk_2026_pretoria_admin MS_REVIEW_SECRET=rigsecret_rigsecret_rigsecret_rigsecret \
MS_JWT_SECRET=rigjwt_rigjwt_rigjwt_rigjwt_rigjwt_rigjwt MS_ADMIN_KEY=rigadminkey \
PAYSTACK_SECRET_KEY=$RIG_PS_KEY ALLOW_TEST_PAYMENTS=1 TUPPENCE_MONTHLY_ENABLED=1 \
setsid nohup python3 /home/claude/rigkit/rig_run.py > /home/claude/rigdata/rig.log 2>&1 &
setsid nohup python3 /home/claude/rigkit/rig_front.py > /home/claude/rigdata/front.log 2>&1 &
for i in $(seq 1 30); do sleep 2; curl -s -m 3 http://127.0.0.1:8000/health >/dev/null 2>&1 && { echo "rig up (~$((i*2))s)"; break; }; done
curl -s -m 3 http://127.0.0.1:8999/__standin/state | head -c 200; echo
