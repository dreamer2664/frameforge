# Film facts — lithos / KINETIC "The Long Light" (release r01)

All numbers below are measured from the delivered bytes (see
`work/qc/technical.json`, `work/qc/craft-hero.json`, `work/qc/depth-spans.json`).

## The film

* **hero** — 42.000 s, 1920x1080, 24.0 fps, 1008 frames, H.264 High@ yuv420p,
  CRF 16, 2 subframes during camera motion; AAC 48 kHz stereo 226 kbit/s.
* **loop** — 10.240 s, 1920x1080, 25.0 fps, 256 frames (deliberately designed
  seamless loop; period = 480 AAC frames = 491520 samples exactly); same encode
  spec.
* **poster** — 1920x1080 PNG from t = 33.5 s.
* Both MP4s: `ftyp moov free mdat` (faststart), A/V tail mismatch 0.000 s.
* Score: synthesised in `audio.py`, cues derived from the storyboard's dial
  geometry (`scene.dial_geometry()`); hero -16.0 LUFS / -11.3 dBTP, loop
  -16.0 LUFS / -3.1 dBTP (spec: -16.0 +/- 1.5, TP <= -1 dBTP).

## The loop gate (on the ENCODED loop-master.mp4)

| check | measured | verdict |
|---|---|---|
| geometry (wrap vs interior mean-abs-diff) | wrap 4.889 vs interior 4.731-5.918 | within interior range |
| position/velocity (brute shift, px) | wrap (0, -1) vs interior (0, 0)/(1, 1) | continuous |
| light phase (mean luma step) | wrap -0.032 vs interior max 1.205 | continuous |
| audio seam (decoded wrap step) | wrap 0.0566 vs local p999 0.0678 (source WAV wrap 4.8e-6) | seam_ok |
| duration / frames / samples | 10.240 s / 256 / 491520 | in 8-12 s spec |

## Story

A golden stone observatory court at low sun. The word KINETIC stands as
architecture (43.7 m of extruded limestone monuments on a shallow arc; caps
6.5 m; extrusion depth 2.6 m). A taller gnomon "I" keeps the floor dial
(point · line · form · world; the promise "ideas, in motion." at its terminus).
The camera wakes inside the bite of the giant stone C (type as a building),
exits through its mouth, walks a colonnade as the sun's blade sweeps the court,
tracks the dial as the shadows rake across the inscribed words, cranes up to
reveal the court as an instrument — and the shadow's tip lands on the promise
to complete the sentence — then settles into a still orbit at the end of the
day.

## Delivered files (all SHA-256 recorded in `work/qc/technical.json` and in the
publication receipt)

`hero.mp4`, `loop.mp4`, `poster.png`, rough cuts (`hero-rough-cut.mp4`,
`loop-rough-cut.mp4`), `technical.json`, `media-qc-hero.json`, review sheets
`sheet-00..03.png`, `sheet-dense.png`, `sheet-phone.png`, `sheet-loop.png`, and
the full evidence set in `agents/lithos/px/evidence/`.
