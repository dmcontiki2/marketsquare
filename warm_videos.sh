#!/bin/bash
# warm_videos.sh (server-side) - warm Cloudflare edge for the in-app tutor videos.
# Run right after a CF purge so the first mobile viewer never hits a cold 40-75MB
# origin pull (the stall David's testers saw, 22 Jul 2026). URLs are read from the
# SERVED ms.js so the list can never drift from what the app requests.
set -uo pipefail
cd /var/www/marketsquare || exit 0
urls=$(grep -oE "/static/videos/[^\"']+\.mp4\?v=[A-Za-z0-9]+" static/ms.js | sort -u)
n=0
for u in $urls; do
  curl -s -o /dev/null "https://trustsquare.co$u" && n=$((n+1))
done
echo "warmed $n tutor videos on the CF edge"
