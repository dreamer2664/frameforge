#!/usr/bin/env python3
"""QC_GRID.md — index of every contact sheet / crop in the evidence package."""
import json
import os

ev = json.load(open('evidence/events.json'))
md = """# QC_GRID — PRISM / PROOF (env-B)

Visual audit trail. Open these at full size; the film is judged here, not in
the scene graph. All sheets are built from the 750 rendered PNG frames by
`evidence/qc_grids.sh` / `evidence/qc_crops.py`.

## Master grid
| file | content |
|---|---|
| `qc_grid_every25.png` | every 25th frame (30 tiles, 6×5) — the whole film in one sheet |

## Text moments (every frame of each moment, 240×135 tiles)
| file | id | string | frames |
|---|---|---|---|
"""
for t in ev['texts']:
    n = t['out'] - t['in'] + 1
    md += f"| `qc_text_{t['id']}.png` | {t['id']} | {t['str']} | {t['in']}–{t['out']} ({n}) |\n"
md += """
## Full-size crops (TEXT_LOG gate)
`crop_text_<id>.png` — each moment at its widest frame, full resolution,
±24 px pad. If any glyph pixel lies outside the 90% box, `TEXT_LOG.md` shows
a negative margin and the file does not ship.

## Flashes (±3 frames around every flash, 480×270 tiles)
| file | id | frames |
|---|---|---|
"""
for f in ev['flashes']:
    md += f"| `qc_flash_{f['id']}.png` | {f['id']} | {f['frame'] - 3}–{f['frame'] + f['dur'] + 3} |\n"
md += "\nFiles present: %d\n" % len([f for f in os.listdir('evidence') if f.startswith(('qc_', 'crop_'))])
open('evidence/QC_GRID.md', 'w').write(md)
print('QC_GRID.md written')
