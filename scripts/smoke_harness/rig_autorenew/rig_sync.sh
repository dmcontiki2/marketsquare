#!/bin/bash
# Build the rig copy from the patched tree. The two origin constants are rewritten in the RIG COPY ONLY.
set -e
rm -rf /home/claude/rig && mkdir -p /home/claude/rig
cd /home/claude/ms && git ls-files -z -co --exclude-standard | tar --null -cf - -T - | tar -xf - -C /home/claude/rig
sed -i "s#^const BEA_URL = 'https://trustsquare.co';#const BEA_URL = location.origin;#" /home/claude/rig/ms.js
sed -i "s#^  var BEA = 'https://trustsquare.co';#  var BEA = location.origin;#" /home/claude/rig/marketsquare.html
grep -c "^const BEA_URL = location.origin;" /home/claude/rig/ms.js; grep -c "var BEA = location.origin" /home/claude/rig/marketsquare.html
