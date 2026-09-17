#!/bin/bash
# copy staged edits over the rig clone
U=/mnt/user-data/uploads/Projects/MarketSquare
for f in bea_main.py ms.js ms.css marketsquare.html zoom_engine.py test_zoom_engine.py dashboard.server.html feature_flags.py quick.html; do
  [ -f "$U/$f" ] && cp "$U/$f" /home/claude/rig/$f && echo "synced $f"
done
# rig-only rewrite: the FEA talks to its own origin, never the live server
sed -i "s#^const BEA_URL = 'https://trustsquare.co';#const BEA_URL = location.origin;#" /home/claude/rig/ms.js
grep -n "^const BEA_URL" /home/claude/rig/ms.js
sed -i "s#^  var BEA = 'https://trustsquare.co';#  var BEA = location.origin;#" /home/claude/rig/marketsquare.html
grep -c "var BEA = location.origin" /home/claude/rig/marketsquare.html
cp $U/fide_registry_seed.json.gz /home/claude/rig/ 2>/dev/null && echo synced seed
mkdir -p /home/claude/rig/migrations && cp $U/migrations/0*.py /home/claude/rig/migrations/ 2>/dev/null && echo synced migrations
