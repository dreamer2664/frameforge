#!/usr/bin/env bash
# Download the commissioned reference (public YouTube) for visual study only.
# Copyrighted download stays in local cache; never committed / never re-published.
set -u
cd "$(dirname "$0")/../../.."
ROOT="$(pwd)"
export PATH="$HOME/.cache/frameforge/bin:$PATH"
OUT="$ROOT/agents/axiom/work/ref"
mkdir -p "$OUT"
LOG="$ROOT/agents/axiom/work/ref-fetch.log"
exec >>"$LOG" 2>&1
echo "=== $(date -u +%FT%TZ) fetch start ==="
URL='https://www.youtube.com/watch?v=XVQdhpwO75g'
echo "--- list formats ---"
python3 -m yt_dlp --no-warnings --no-playlist --list-formats "$URL" 2>&1 | tail -40
echo "--- try full AV (video+audio) at <=720p ---"
python3 -m yt_dlp --no-warnings --no-playlist \
  -f "bv*[height<=720]+ba/b[height<=720]" --merge-output-format mp4 \
  -o "$OUT/ref17.%(ext)s" "$URL" 2>&1 | tail -25
echo "--- fallback: best video-only stream ---"
python3 -m yt_dlp --no-warnings --no-playlist -f "bv*/b" \
  -o "$OUT/ref17_videoonly.%(ext)s" "$URL" 2>&1 | tail -15
echo "--- also grab the auto/manual english subtitles if public ---"
python3 -m yt_dlp --no-warnings --no-playlist --skip-download \
  --write-auto-subs --write-subs --sub-langs 'en.*' --sub-format vtt \
  -o "$OUT/ref17.subs" "$URL" 2>&1 | tail -10
ls -la "$OUT"
echo "=== $(date -u +%FT%TZ) fetch end ==="
