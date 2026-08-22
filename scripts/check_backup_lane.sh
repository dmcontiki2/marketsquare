#!/bin/bash
# check_backup_lane.sh - does the encrypted R2 backup lane still authenticate? NO SECRETS.
echo "  === encrypted backup lane (rclone -> R2 trustsquare-backups) ==="
CFG=$(ls /root/.config/rclone/rclone.conf /root/r2backup/rclone.conf 2>/dev/null | head -1)
if [ -z "$CFG" ]; then echo "  [X] no rclone config found"; exit 1; fi
echo "  [--] config: $CFG (modified $(stat -c %y "$CFG" | cut -d. -f1))"
echo "  [--] remotes: $(rclone --config "$CFG" listremotes 2>/dev/null | tr '\n' ' ')"
echo "  [--] testing access (lists directories only, downloads nothing)..."
if timeout 60 rclone --config "$CFG" lsd r2crypt: >/tmp/_r2out 2>/tmp/_r2err; then
  echo "  [OK] BACKUP LANE WORKING - remote reachable and readable"
  n=$(timeout 60 rclone --config "$CFG" ls r2crypt: 2>/dev/null | wc -l)
  echo "  [--] objects visible through the crypt layer: $n"
else
  echo "  [X]  BACKUP LANE FAILED:"
  sed 's/^/       /' /tmp/_r2err | head -5
fi
echo "  [--] last backup cron: $(grep -h r2 /etc/crontab /etc/cron.d/* 2>/dev/null | head -1)"
LOG=$(ls -t /root/r2backup/*.log /var/log/r2backup* 2>/dev/null | head -1)
[ -n "$LOG" ] && echo "  [--] newest backup log: $LOG ($(stat -c %y "$LOG" | cut -d. -f1))"
rm -f /tmp/_r2out /tmp/_r2err
