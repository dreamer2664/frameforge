#!/usr/bin/env python3
"""Full-size crops of every text moment at its widest frame (TEXT_LOG gate)."""
import json
import os
import subprocess
import sys

FR = sys.argv[1] if len(sys.argv) > 1 else '/tmp/frames'
EV = 'evidence'
meas = json.load(open(f'{EV}/text_measures.json'))
by = {}
for row in meas:
    for t in row['texts']:
        by.setdefault(t['id'], []).append((row['frame'], t))
# widest frame is not always legible (slam start sits inside flash afterglow);
# explicit sample frames for those cases
OVERRIDE = {'T6': 520, 'T10.body': 730}
for tid, rows in sorted(by.items()):
    if tid in OVERRIDE:
        f, b = min(rows, key=lambda r: abs(r[0] - OVERRIDE[tid]))
    else:
        f, b = max(rows, key=lambda r: (r[1]['x1'] - r[1]['x0']))
    pad = 24
    x = max(0, int(b['x0']) - pad); y = max(0, int(b['y0']) - pad)
    w = min(1920 - x, int(b['x1'] - b['x0']) + 2 * pad)
    h = min(1080 - y, int(b['y1'] - b['y0']) + 2 * pad)
    out = f'{EV}/crop_text_{tid}.png'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{FR}/f_{f:05d}.png',
                    '-vf', f'crop={w}:{h}:{x}:{y}', out], check=True)
    print(f'[qc] {out} frame {f} box=({x},{y},{w},{h})')
