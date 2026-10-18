#!/usr/bin/env bash
# PRISM / PROOF — QC contact sheets (tile-based, from the 750 rendered frames).
#   qc_grid_every25.png      every 25th frame, 30 tiles
#   qc_text_<id>.png         every frame of each text moment (small tiles)
#   qc_flash_<id>.png        +-3 frames around each flash
set -euo pipefail
FR=${1:-/tmp/frames}; EV=${2:-evidence}; export FR
mkdir -p "$EV" /tmp/qc
sheet() { # sheet <out> <cols> <rows> <scale> <frame...>
  local out=$1 cols=$2 rows=$3 sc=$4; shift 4
  rm -rf /tmp/qc/s; mkdir -p /tmp/qc/s
  local i=0
  for f in "$@"; do
    ln -sf "$FR/f_$(printf '%05d' "$f").png" "/tmp/qc/s/$(printf '%03d' $i).png"; i=$((i+1))
  done
  ffmpeg -v error -y -framerate 1 -i /tmp/qc/s/%03d.png \
    -vf "scale=${sc},tile=${cols}x${rows}" -frames:v 1 "$EV/$out"
  echo "[qc] $out ($# tiles)"
}
cd "$(dirname "$0")/.."

every25=$(python3 -c "print(' '.join(str(i) for i in range(0,750,25)))")
sheet qc_grid_every25.png 6 5 384:216 $every25

python3 - <<'PY'
import json, subprocess, os, shutil
ev = json.load(open('evidence/events.json'))
FR = os.environ.get('FR', '/tmp/frames')
for t in ev['texts']:
    frs = list(range(t['in'], t['out'] + 1))
    n = len(frs); cols = 12; rows = (n + cols - 1) // cols
    args = ['bash', 'evidence/qc_grids.sh', 'x']  # not used; sheets built below
    # build directly with ffmpeg tile via symlinks
    d = '/tmp/qc/t'; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for i, f in enumerate(frs):
        os.symlink(f'{FR}/f_{f:05d}.png', f'{d}/{i:03d}.png')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-i', f'{d}/%03d.png',
                    '-vf', f'scale=240:135,tile={cols}x{rows}', '-frames:v', '1',
                    f'evidence/qc_text_{t["id"]}.png'], check=True)
    print(f'[qc] qc_text_{t["id"]}.png ({n} frames)')
for fl in ev['flashes']:
    frs = list(range(fl['frame'] - 3, fl['frame'] + fl['dur'] + 4))
    d = '/tmp/qc/f'; shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    for i, f in enumerate(frs):
        os.symlink(f'{FR}/f_{f:05d}.png', f'{d}/{i:03d}.png')
    cols = len(frs); 
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-framerate', '1', '-i', f'{d}/%03d.png',
                    '-vf', f'scale=480:270,tile={cols}x1', '-frames:v', '1',
                    f'evidence/qc_flash_{fl["id"]}.png'], check=True)
    print(f'[qc] qc_flash_{fl["id"]}.png ({cols} frames)')
PY
echo "[qc] done"
