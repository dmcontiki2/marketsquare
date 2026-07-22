#!/bin/bash
# warm_video_cache.sh - pre-warm Cloudflare's edge cache for the in-app tutor videos
# (added 22 Jul 2026). WHY: the tutor .mp4s are large; on a COLD CF cache the first
# viewer pulls the whole file from origin -> on mobile that looks like a broken/
# spinning video (the exact failure David's testers hit). Every deploy purges CF,
# so run this straight after a purge. URLs (incl. ?v= keys) are read from the local
# ms.js so the warm list can never drift from what the app actually requests.
set -uo pipefail
SERVER="${MS_SERVER:-msdeploy@178.104.73.239}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mapfile -t URLS < <(grep -oE "/static/videos/[^\"']+\.mp4\?v=[A-Za-z0-9]+" "$HERE/ms.js" | sort -u)
if [ "${#URLS[@]}" -eq 0 ]; then echo "no video URLs found in ms.js"; exit 0; fi
echo "Warming ${#URLS[@]} tutor videos on Cloudflare edge..."
for u in "${URLS[@]}"; do
  read -r code cf < <(ssh -o ConnectTimeout=15 "$SERVER" \
    "curl -s -o /dev/null -w '%{http_code} ' 'https://trustsquare.co$u'; curl -sI 'https://trustsquare.co$u' | grep -io 'cf-cache-status: [A-Z]*' | awk '{print \$2}'")
  echo "  $code  ${cf:-?}  $u"
done
echo "done - all should read HIT."
