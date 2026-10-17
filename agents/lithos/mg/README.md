# mg — TITLE MACHINE (the "Motion Design for KINETIC/lithos" film)

**Deliverable:** `out/title-machine.mp4` — 13.0 s · 1920×1080 · 30 fps · H.264 crf15 + AAC 48 kHz stereo, −16.0 LUFS / ≤ −1.5 dBTP.
Also `out/poster.png` (t=9.2 s, molten card), `out/lithos-logo.{svg,png,-dark.png}` (brand mark).

## Structure (see storyboard.json for the full beat map)

| t | beat |
|---|------|
| 0.00 | aurora ribbon folds, K-mark pops |
| 0.55 | "KINETIC" type-on (per-char colour decay amber→white) |
| 1.25 | whip → tool chips fly in with smear trails (Shape/Score/Light/**Cut**/Loop) |
| 1.85–2.36 | Cut chip ignites → cursor arrives → click |
| 2.70 | HARD CUT (white flash) to dark console |
| 2.80 | prompt type-on "make a title that moves like light." (newest chars amber) |
| 3.65 | panel **refits into the composer bar** (type shrinks with it), model chip `lithos-1` |
| 4.30 | motion-curve rain (3 depth layers: bezier curves + keyframe labels) |
| 5.20 | generated site card swings in — "IDEAS, IN MOTION." (serif display) |
| 6.70 | prompt 2 "now make it molten." |
| 7.30 | anticipation: send button glows, world dims, riser |
| **8.50** | **palette flip aurora→molten** (inverted vs reference) + card flip |
| 8.70 | molten orbit |
| 10.05 | streak exit |
| 10.15 | lithos mark (hex stone + light seam) |
| 10.35 | "Built by lithos" per-char arc fly-in |
| 11.18 | lockup (crossfade to kerned word) |
| 11.80 | streak exit → black tail to 13.00 |

Score: 120 BPM bed (kick/hat/bass/pad) + storyboard-derived whoosh/impact/riser/letter-ticks,
`work/score.wav` (24-bit master) + `score.m4a` — measured −16.0 LUFS / −2.67 dBTP.

## Visual review log (user law: "you gotta visualize the videos you make")

Every revision was **seen** via `read_file` vision on rendered sheets/crops. Findings & fixes:

**R0 — first 9 test frames (work/test-sheet.png):**
1. ribbon cores blown out white (bloom 0.62/0.55 + wide halos) — whole frame washed;
2. panels/composer placed top-left (place() centres — given corner coords);
3. card rotated 90°+mirrored — PIL `Image.QUAD` maps a source quad onto the output rect
   (unwarp), it is NOT a projection;
4. outro chars overlapped (text_rgba pad ≠ advance);
5. bloom ate type/logo contrast.

**R1 — ribbon redesign (mostly-black folds), true perspective (`quad_project`/`persp_coeffs`
with `Image.PERSPECTIVE` output→input coeffs), bloom 0.78/0.30, `put_tl` top-left placement,
shadowed type, padding-corrected char layout, card rescaled (nav was clipping the frame top).
Verified on work/rev1-sheet.png / rev2-sheet.png.

**R2 — composer bar was opaque and pasted OVER the prompt type (draw-order bug);
caret collided with the model chip. Bar now draws first, type on top; type refits (×0.78) as
the panel collapses into the bar; chip/send hugged right. Outro: per-char only during flight,
crossfade at 11.18 to the kerned `text_rgba` word (per-char assembly lacks pair kerning).**

**R3 — `world_gain` table had a gap at 6.65–7.30 (ribbons snapped to full brightness while
prompt 2 typed). Filled at 0.32.**

Full-film watch (contact sheets every 15th frame + spot crops of every text surface):
whip smears read as motion; type-on tails amber; rain depth works; card flip + molten palette
flip land on the 8.50 musical hit; lockup kerning clean; black tail matches score.

## r01 camera post-mortem lesson
This film is a 2.5D mograph compositor — there is no camera that can clip through geometry
(the r01 failure mode). For any future px/3D shot, `../research/tools/camera_clearance.py`
is the gate (≥0.35 m world clearance every subframe).

## Reproduce
```
python3 score.py   # -> work/score.wav / score.m4a
python3 build.py   # 390 frames -> out/title-machine.mp4 + out/poster.png
python3 logo.py    # -> out/lithos-logo.svg + PNGs
```
Build outputs (`work/`, `out/*.png`, `out/*.mp4`, `*.raw`) are gitignored; release artefacts
ship via the storagecode r02 release.
