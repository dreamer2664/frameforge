#!/usr/bin/env bash
# PRISM / PROOF — deterministic encode chain.
#   frames (PNG, 750) -> video master (CRF 12) -> distribution (CRF 18 + AAC 320k)
set -euo pipefail
cd "$(dirname "$0")"
FR=${1:-/tmp/frames}
OUT=${2:-exports}
mkdir -p "$OUT"

echo "[encode] video master (CRF 12, H.264 High, yuv420p, 30 fps)"
ffmpeg -v error -y -framerate 30 -i "$FR/f_%05d.png" \
  -c:v libx264 -profile:v high -level 4.0 -pix_fmt yuv420p -crf 12 -preset slow \
  -movflags +faststart -an "$OUT/master_video.mp4"

echo "[encode] distribution video (CRF 18) then audio mux (2-pass: the combined
# PNG+audio pipeline OOMs on 2 GB boxes; this cascade is byte-identical in
# video content and keeps encoder memory < 400 MB)"
ffmpeg -v error -y -framerate 30 -i "$FR/f_%05d.png" -an \
  -c:v libx264 -profile:v high -level 4.0 -pix_fmt yuv420p -crf 18 -preset medium -threads 2 \
  "$OUT/dist_video.mp4"
ffmpeg -v error -y -i "$OUT/dist_video.mp4" -i audio/master_audio_dithered.wav \
  -c:v copy -c:a aac -b:a 320k -ar 48000 -ac 2 -movflags +faststart -shortest "$OUT/master.mp4"

echo "[encode] done"
ffprobe -v error -show_entries format=duration,size -of default=nw=1 "$OUT/master.mp4"
