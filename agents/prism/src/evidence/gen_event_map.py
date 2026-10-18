#!/usr/bin/env python3
"""EVENT_MAP.md — the reviewer's table of contents, generated from the one
source of temporal truth (events.json) so picture and sound cannot drift."""
import json

ev = json.load(open('evidence/events.json'))
acts = [('I', 0, 179, 'THE CLAIM', 'amber field: dust, glow, scanline; type asserts'),
        ('II', 180, 449, 'THE MEASUREMENT', 'ice instrument grid, specimen, ring, counters'),
        ('III', 450, 659, 'THE VERDICT', 'white-out, exploded diagram, hero PROOF, stabs'),
        ('IV', 660, 749, 'THE RECEIPT', 'paper receipt card, acceptance-pending kicker')]

md = """# EVENT_MAP — PRISM / PROOF (env-B)

Master timeline. 750 frames @ 30 fps = 25.00 s. Every visual event, flash and
audio hit below reads the SAME frame constants (`film/events.js`, exported to
`evidence/events.json`); the audio synth places hits at
sample = round(frame/30*48000), so picture/sound alignment is exact (0 samples).

## Acts
| act | frames | seconds | title | picture |
|---|---|---|---|---|
"""
for a, f0, f1, title, pic in acts:
    md += f"| {a} | {f0}–{f1} | {f0/30:.2f}–{(f1+1)/30:.2f} | {title} | {pic} |\n"

md += "\n## Text moments (11)\n| id | string | in | out | cap px | mode | anchor (x,y) |\n|---|---|---|---|---|---|---|\n"
for t in ev['texts']:
    md += (f"| {t['id']} | {t['str']} | {t['in']} | {t['out']} | {t['cap']} | {t['mode']} | "
           f"{t['anchor']} ({t['x']},{t['y']}) |\n")

md += "\n## Flashes (6)\n| id | frame | dur | type | colour | peak | audio hit |\n|---|---|---|---|---|---|---|\n"
for f in ev['flashes']:
    md += (f"| {f['id']} | {f['frame']} | {f['dur']} | {f['type']} | {f['color']} | {f['peak']} | "
           f"{f['hit']} |\n")

md += "\n## Audio hits (12)\n| id | frame | time s | kind |\n|---|---|---|---|\n"
for h in sorted(ev['hits'], key=lambda h: h['frame']):
    md += f"| {h['id']} | {h['frame']} | {h['frame']/30:.4f} | {h['kind']} |\n"

md += """
## Music structure
| section | frames | seconds | content |
|---|---|---|---|
| drone | 0–179 | 0.00–6.00 | 55 Hz detuned drone + sub, sparse calibration ticks |
| build | 180–449 | 6.00–15.00 | 120 bpm quarters (every 15 f), hats on 8ths, pad, riser 300→480 |
| verdict | 450–659 | 15.00–22.00 | sub drop + crash @480, pad, three stabs @500/530/560 |
| receipt | 660–749 | 22.00–25.00 | warm pad, stamp @660, final tick @744, 0.35 s design fade |

## Camera
| act | move | curve |
|---|---|---|
| I | dolly z 26→15, y 0.4→0.2 | inOutQuint |
| II | orbit r19, a −0.55→1.35 rad, y 6.5→3.0 | inOutCubic |
| III | push z 22→13.5 | outQuint |
| IV | static (receipt card) | linear |
Impact shake (seeded value-noise, decaying 16 f) on H-claim/H-m2/H-verdict/H-receipt.
"""
open('evidence/EVENT_MAP.md', 'w').write(md)
print('EVENT_MAP.md written')
