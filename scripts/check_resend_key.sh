#!/bin/bash
# check_resend_key.sh - read-only verification. PRINTS NO SECRET VALUES.
f=/etc/systemd/system/marketsquare.service.d/resend.conf
if [ -f "$f" ]; then
  echo "  [OK] drop-in file exists"
  echo "  [--] last written : $(stat -c %y "$f" | cut -d. -f1)"
  echo "  [--] Environment lines: $(grep -c Environment "$f")"
  echo "  [--] permissions  : $(stat -c %a "$f")"
else
  echo "  [X]  drop-in file MISSING - the key write did NOT happen"
fi
echo "  [--] service      : $(systemctl is-active marketsquare)"
echo "  [--] running since: $(systemctl show -p ActiveEnterTimestamp --value marketsquare)"
p=$(systemctl show -p MainPID --value marketsquare)
if grep -aq 'RESEND_API_KEY=' /proc/$p/environ; then
  echo "  [OK] running process HAS a Resend key loaded"
else
  echo "  [X]  running process has NO Resend key"
fi
