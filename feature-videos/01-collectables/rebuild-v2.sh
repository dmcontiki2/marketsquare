#!/usr/bin/env bash
# Rebuild collectables-advert-v2-FINAL.mp4 from the 4 AI clips + 3 UI inserts + logo sting.
# Reconstructed 2026-06-15 (prior build script lived in the temp session-outputs folder,
# which is cleared between sessions — this copy lives in the repo so it persists).
#
# Assembly order (matches the as-built v2 / the scheduled-task spec):
#   hook -> logo-sting -> snap -> typing -> report-insert -> save-forward -> payoff -> listing -> logo-sting
#
# Output: 720x1280, 30fps, yuv420p, AAC stereo 48k.
#
# Usage:
#   ./rebuild-v2.sh            # builds the real FINAL next to this script
#   OUT=/path/test.mp4 ./rebuild-v2.sh   # builds to a custom path (e.g. for a dry run)
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KIT="$HERE/../production-kit"
OUT="${OUT:-$HERE/collectables-advert-v2-FINAL.mp4}"

# Inputs in assembly order. The logo sting is used twice (positions 2 and 9).
INPUTS=(
  "$HERE/clips/c3-hook.mp4"            # 1 HOOK   (couch, girlfriend, holds Bodyguard card)
  "$KIT/logo-sting-1.6s.mp4"           # 2 STING
  "$HERE/clips/c1-snap.mp4"            # 3 SNAP   (holds + snaps the Bodyguard card)
  "$HERE/clips/c2-typing.mp4"          # 4 TYPING (types listing; "city, Pretoria")
  "$HERE/inserts/report-insert.mp4"    # 5 REPORT-INSERT (R350 market report)
  "$HERE/inserts/insert-save-forward.mp4" # 6 SAVE/FORWARD
  "$HERE/clips/c4-payoff.mp4"          # 7 PAYOFF (lists automatically)
  "$HERE/inserts/listing-insert.mp4"   # 8 LISTING-INSERT
  "$KIT/logo-sting-1.6s.mp4"           # 9 STING (out)
)

for f in "${INPUTS[@]}"; do
  [ -f "$f" ] || { echo "MISSING INPUT: $f" >&2; exit 1; }
done

# Build ffmpeg args: normalize every segment to 720x1280/30fps + stereo 48k, then concat.
args=(); fc=""; n=${#INPUTS[@]}
for i in "${!INPUTS[@]}"; do
  args+=(-i "${INPUTS[$i]}")
  fc+="[${i}:v]scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p[v${i}];"
  fc+="[${i}:a]aresample=48000,aformat=channel_layouts=stereo[a${i}];"
done
for i in "${!INPUTS[@]}"; do fc+="[v${i}][a${i}]"; done
fc+="concat=n=${n}:v=1:a=1[v][a]"

ffmpeg -y "${args[@]}" -filter_complex "$fc" -map "[v]" -map "[a]" \
  -c:v libx264 -preset medium -crf 19 -pix_fmt yuv420p -r 30 \
  -c:a aac -b:a 192k -ar 48000 -ac 2 -movflags +faststart "$OUT"

echo "Built: $OUT"
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height,r_frame_rate,channels \
  -of default=noprint_wrappers=1 "$OUT"
