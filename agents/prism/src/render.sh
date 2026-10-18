#!/usr/bin/env bash
# NOTE: frames live on REAL DISK (/opt/prismframes). /tmp on this class of box
# is a ~1 GB tmpfs: 750 PNGs there eat RAM (OOM-kills Chrome/ffmpeg) and hit
# ENOSPC. Never render into /tmp again — see FAILED_ATTEMPTS D-B14/B16.
# PRISM / PROOF — ONE-COMMAND REBUILD from a clean checkout.
# Reproduces: bundle -> events -> audio master -> 750 frames -> masters ->
# evidence package -> QC grids. No network except npm/apt (bootstrap).
set -euo pipefail
cd "$(dirname "$0")"

echo "== [1/9] environment =="
bash bootstrap.sh

echo "== [2/9] bundle =="
npx esbuild film/page.js --bundle --format=iife --outfile=film/page.bundle.js \
  --loader:.woff2=dataurl --target=chrome120 --log-level=warning

echo "== [3/9] events (single source of temporal truth) =="
node render.mjs --dump-events --out evidence/events.json

echo "== [4/9] audio master (synth + two-pass loudnorm to -14 LUFS / TP -1.0) =="
python3 audio/synth.py evidence/events.json audio/master_pre.wav
M=$(ffmpeg -hide_banner -i audio/master_pre.wav -af loudnorm=I=-14:TP=-1.0:LRA=11:print_format=json -f null - 2>&1 | sed -n '/{/,/}/p')
mI=$(echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['input_i'])")
mT=$(echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['input_tp'])")
mL=$(echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['input_lra'])")
mTh=$(echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['input_thresh'])")
mO=$(echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['target_offset'])")
ffmpeg -v error -y -i audio/master_pre.wav \
  -af "loudnorm=I=-14:TP=-1.0:LRA=11:measured_I=$mI:measured_TP=$mT:measured_LRA=$mL:measured_thresh=$mTh:offset=$mO:linear=true" \
  -ar 48000 -ac 2 -c:a pcm_s24le audio/master_audio.wav

echo "== [5/9] 750 frames (crash-tolerant, resume-aware) =="
bash render_all.sh

echo "== [6/9] encode masters =="
bash encode.sh /opt/prismframes exports

echo "== [7/9] text measurements =="
node render.mjs --measure --from 0 --to 749 --chunk 25 --out evidence/text_measures.json

echo "== [8/9] evidence package =="
python3 evidence/gen_event_map.py
python3 evidence/make_evidence.py /opt/prismframes exports evidence
bash evidence/qc_grids.sh /opt/prismframes evidence
python3 evidence/qc_crops.py /opt/prismframes

echo "== [9/9] done =="
echo "Deliverables: exports/master.mp4 exports/master_video.mp4 audio/master_audio.wav"
echo "Evidence:     evidence/ (see evidence/INDEX or QC_GRID.md)"
