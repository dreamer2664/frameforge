#!/usr/bin/env python3
"""Revision 2 — sound sync.

The score was written against the old cut.  After the rhythm revision every
musical event has to land on the picture again, and the seven dry taps have to
land on the *actual* moment each carved letter is reached by the raking light
(they used to be evenly spaced guesses).

This patch re-derives the sync points from storyboard.json so the score and the
picture share a single source of truth, and re-pans the taps to the side of the
word the light is travelling on.
"""
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
A = HERE / "audio.py"
ST = json.loads((HERE / "storyboard.json").read_text())

stages = ST["stages"]
letters = ST["letters"]
T0, T1 = 4.2, 11.3
X0, X1 = 11.5, -5.0
span = T1 - T0
runs = X1 - X0

reveal_times = []
for spec in letters:
    # the letter is fully lit when the travelling light has passed 2.6 m before it
    x_target = spec["wall_x"] - 2.6
    u = (X0 - x_target) / (X0 - X1)
    reveal_times.append(round(T0 + u * span, 3))
reveal_times_sorted = sorted(reveal_times)

s = A.read_text()
orig = s

# --- the seven taps follow the real reveal order (the light travels right to left)
old_taps = """    for i, t0 in enumerate((6.00, 6.85, 7.70, 8.55, 9.40, 10.25, 11.10)):
        tap = stone_tap(sr=sr, seed=30 + i, bright=700 + 120 * i) * 0.55
        pan = (i / 6.0 - 0.5) * 0.5"""
new_taps = """    for i, t0 in enumerate(REVEAL_TAPS):
        tap = stone_tap(sr=sr, seed=30 + i, bright=700 + 120 * i) * 0.55
        pan = (REVEAL_PANS[i] - 0.5) * 0.5"""
assert old_taps in s
s = s.replace(old_taps, new_taps)

s = s.replace("""SR = 48000""",
              """SR = 48000

# --- sync points, derived from storyboard.json (revision 2: the score follows
#     the picture instead of guessing at it)
STORY = json.loads((Path(__file__).resolve().parent / "storyboard.json").read_text())
STAGES = STORY["stages"]
_REV_T0, _REV_T1 = 4.2, 11.3
_REV_X0, _REV_X1 = 11.5, -5.0
_REVEAL = []
for _spec in STORY["letters"]:
    _u = (_REV_X0 - (_spec["wall_x"] - 2.6)) / (_REV_X0 - _REV_X1)
    _REVEAL.append((round(_REV_T0 + _u * (_REV_T1 - _REV_T0), 3), _spec["wall_x"]))
REVEAL_TAPS = [t for t, _x in sorted(_REVEAL, key=lambda p: p[0])]
REVEAL_PANS = [min(max((x + 2.0) / 10.0, 0.0), 1.0) for _t, x in sorted(_REVEAL, key=lambda p: p[0])]""")

# --- the remaining events follow the re-timed cut
s = s.replace("""    add_at(L, sw, 14.4 * sr)
    add_at(R, sw, 14.4 * sr)""",
              """    add_at(L, sw, 11.6 * sr)
    add_at(R, sw, 11.6 * sr)""")
s = s.replace("""        t0 = 15.0 + i * 0.15""", """        t0 = STAGES["release"] + i * STAGES["release_stagger"]""")
s = s.replace("""    add_at(L, cl, 22.0 * sr)
    add_at(R, cl * 0.96, 22.0 * sr)""",
              """    add_at(L, cl, 19.0 * sr)
    add_at(R, cl * 0.96, 19.0 * sr)""")
s = s.replace("""    for i, t0 in enumerate((22.4, 24.2, 25.6, 26.8, 27.8, 28.6)):""",
              """    for i, t0 in enumerate((19.4, 21.2, 22.6, 23.8, 24.8, 25.6)):""")
s = s.replace("""    add_at(L, im, 29.3 * sr)
    add_at(R, im, 29.3 * sr)""",
              """    add_at(L, im, 26.3 * sr)
    add_at(R, im, 26.3 * sr)""")
s = s.replace("""    ch = chord(dur - 29.0, sr=sr) * 0.85
    ce = env(n - int(29.0 * sr), 2.0, 1.0, sustain=0.75, hold=4.0, release=3.5, sr=sr)
    ch = ch * ce
    add_at(L, ch, 29.0 * sr)
    add_at(R, ch * 0.95, 29.0 * sr)""",
              """    ch = chord(dur - 26.0, sr=sr) * 0.85
    ce = env(n - int(26.0 * sr), 2.0, 1.0, sustain=0.75, hold=4.0, release=3.5, sr=sr)
    ch = ch * ce
    add_at(L, ch, 26.0 * sr)
    add_at(R, ch * 0.95, 26.0 * sr)""")
s = s.replace("""    for i, t0 in enumerate((32.2, 33.4, 34.6, 35.8)):""",
              """    for i, t0 in enumerate((28.75, 30.3, 31.85, 33.4)):""")
s = s.replace("""    sh = shimmer(dur - 31.0, cycles=1, sr=sr) * 0.05
    add_at(L, sh, 31.0 * sr)
    add_at(R, sh * 0.9, 31.0 * sr)""",
              """    sh = shimmer(dur - 27.2, cycles=1, sr=sr) * 0.05
    add_at(L, sh, 27.2 * sr)
    add_at(R, sh * 0.9, 27.2 * sr)""")

if "import json" not in s.split("SR = 48000")[0]:
    s = s.replace("import argparse\nimport math", "import argparse\nimport json\nimport math")

A.write_text(s)
print("reveal taps (sorted, right->left):", REVEAL_TAPS)
print("pans:", [round(p, 3) for p in REVEAL_PANS])
print("stages:", STAGES)
print("audio.py delta:", len(s) - len(orig))
