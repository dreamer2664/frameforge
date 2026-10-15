#!/usr/bin/env bash
# axiom — one-shot environment bootstrap (ffmpeg, yt-dlp, Kokoro TTS runtime+models).
# Logs to agents/axiom/work/bootstrap.log. Idempotent; safe to re-run after a cache wipe.
set -u
cd "$(dirname "$0")/../../.."   # frameforge root
ROOT="$(pwd)"
mkdir -p agents/axiom/work
LOG="$ROOT/agents/axiom/work/bootstrap.log"
exec >>"$LOG" 2>&1
echo "=================== $(date -u +%FT%TZ) bootstrap start ==================="
echo "--- 1/3 ffmpeg+ffprobe ---"
python3 ops/bootstrap_media.py || echo "BOOTSTRAP_MEDIA_FAILED"
ls -la "$HOME/.cache/frameforge/bin" 2>/dev/null || true

echo "--- 2/3 yt-dlp ---"
python3 -m pip install --quiet --disable-pip-version-check yt-dlp 2>&1 | tail -3
python3 -m yt_dlp --version || echo "YTDLP_FAILED"

echo "--- 3/3 kokoro onnx runtime + models (first synthesis = real access test) ---"
printf 'A single clear sentence to verify the narration engine actually produces audio.\n' > agents/axiom/work/_boot_cue.txt
python3 ops/tts.py --text-file agents/axiom/work/_boot_cue.txt \
  --out agents/axiom/work/_boot_cue.wav --voice af_heart --speed 1.0 --lang en-us \
  || echo "TTS_BOOTSTRAP_FAILED"
ls -la agents/axiom/work/_boot_cue.wav 2>/dev/null || true
echo "=================== $(date -u +%FT%TZ) bootstrap end ==================="
