#!/bin/bash
# mount_check.sh - torn-mount detector (MOUNT-READ-1 permanent fix, S140).
#
# THE FAULT: the bash sandbox reaches C:\Users\David\Projects over a virtiofs/FUSE mount that can
# serve a PERSISTENTLY TRUNCATED (torn mid-file) copy of a file for an entire session, while the
# real Windows file (and git) is complete. Acting on that torn view = false alarms; writing it
# back from bash = overwriting the good Windows file with a truncated one (the recurring
# MOUNT-TEAR / ms.js / bea_main.py truncations in the CHANGELOG).
#
# WHY THIS SCRIPT IS RELIABLE WHERE A PYTHON GUARD WASN'T: a guard whose own code lives on the
# torn mount can't be trusted to run (bash literally could not read mount_guard.py whole). So this
# detector is meant to be RUN FROM /tmp (off the mount) and it checks sizes via `git cat-file`,
# which reads git's OBJECT STORE - not the FUSE file view. Copy it to /tmp at session start:
#     cp /sessions/<id>/mnt/MarketSquare/mount_check.sh /tmp/ && chmod +x /tmp/mount_check.sh
# then run it before trusting any bash read or doing any write-back:
#     /tmp/mount_check.sh /sessions/<id>/mnt/MarketSquare [file ...]
#
# Exit 0 = mount whole · 1 = torn file(s) found · 2 = bad project path.
cd "$1" || exit 2
FILES="${@:2}"
[ -z "$FILES" ] && FILES="CLAUDE.md STATUS.md BACKLOG.md CHANGELOG.md AGENT_BRIEFING.md CHANGE_REGISTER.md AUDIT_PROGRESS.md ms.js ms.css bea_main.py marketsquare.html marketsquare_admin.html smoke_test.py"
torn=0
for f in $FILES; do
  [ -f "$f" ] || continue
  mnt=$(wc -c < "$f")
  head=$(git cat-file -s "HEAD:$f" 2>/dev/null)   # committed size via object store (not FUSE)
  [ -z "$head" ] && { printf "  [skip] %-24s (not at HEAD)\n" "$f"; continue; }
  lastnl=$(tail -c1 "$f" | wc -l)                 # 0 => ends mid-line => torn signal
  ismod=$(git status --porcelain -- "$f" | grep -c .)
  if [ "$mnt" = "$head" ]; then
    printf "  [ ok ] %-24s %d bytes\n" "$f" "$mnt"
  elif [ "$lastnl" = "0" ] && [ "$mnt" -lt "$head" ]; then
    printf "  [TORN] %-24s mount=%d head=%d, ends mid-line\n" "$f" "$mnt" "$head"; torn=1
  elif [ "$ismod" -gt 0 ]; then
    printf "  [edit] %-24s mount=%d head=%d (modified, ends clean)\n" "$f" "$mnt" "$head"
  elif [ "$mnt" -lt "$head" ]; then
    printf "  [TORN] %-24s mount=%d head=%d (clean file served short)\n" "$f" "$mnt" "$head"; torn=1
  fi
done
[ "$torn" = "1" ] && { echo "  >> MOUNT TORN - do NOT write-back from bash; use the Read/Edit file-tools (true file) or pull the authoritative copy."; exit 1; }
echo "  >> mount whole - safe to proceed"
exit 0
