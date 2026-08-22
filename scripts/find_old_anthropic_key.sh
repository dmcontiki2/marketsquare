#!/bin/bash
# find_old_anthropic_key.sh - print the CONSOLE HINT of the burnt key so David can
# identify it in the Anthropic list. Prints a prefix only - the same characters the
# console itself displays - never the whole key.
echo "  Searching backups for the key that was live on this box before today..."
for f in /etc/environment.bak-* /etc/systemd/system/marketsquare.service.d/*.bak-* ; do
  [ -f "$f" ] || continue
  v=$(grep -ho 'ANTHROPIC_API_KEY=.*' "$f" 2>/dev/null | head -1 | cut -d= -f2- | tr -d '"')
  if [ -n "$v" ]; then
    echo "  found in: $(basename $f)"
    echo "  console hint: ${v:0:16}...${v: -1}"
    echo "  (match this against the Anthropic list - THAT is the burnt key)"
    exit 0
  fi
done
echo "  [X] no backup on this box still carries the old key"
