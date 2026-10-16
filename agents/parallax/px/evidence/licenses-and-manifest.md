# Licences, provenance and manifest (parallax / KINETIC)

## What is in the film

| element | origin | licence |
|---|---|---|
| picture | rendered by this repository's own rasteriser (`render3d.py`) from geometry defined in `storyboard.json` | original work, produced for this commission |
| type | **Archivo** variable (display weight 700, caption weight 450), Latin subset, from Google Fonts | SIL Open Font License 1.1 — `agents/parallax/fonts/OFL-Archivo.txt`, copy also in `agents/parallax/px/fonts/` |
| letterforms as geometry | the Archivo outlines were converted to extruded solids by `type3d.py`; validated against an independent path built with fontTools' `SVGPathPen` | derived from Archivo, OFL 1.1 (the OFL permits derivative works and the embedding of the font in rendered output) |
| score and sound design | 100 % synthesised in `audio.py` — drone, dry stone taps, hinge scrapes, sub swell, rising cluster, impact, monument chord, a synthetic hall impulse response, a LUFS normaliser | original work; no samples, no stock loops, no third-party recordings |
| textures | procedural, deterministic (value noise seeded in `stone_texture()`, `band_texture()`, `glow_texture()`) | original work |
| narration | none | — |

No stock footage, no stock music, no image or model from any third party, and no
material from the delivered r03 film was used or copied.

## Build-time software (not shipped with the film)

| tool | version / source | licence | role |
|---|---|---|---|
| FFmpeg / ffprobe | static build `ffmpeg-master-latest-linux64-gpl` (N-127564-g3c92f003c7-20261015) from the BtbN FFmpeg-Builds releases | LGPL v2.1 or later (GPL build) | encode, decode, measure, QC |
| numpy | PyPI | BSD-3-Clause | raster maths |
| scipy | PyPI | BSD-3-Clause | signal filtering, interpolation |
| fontTools | PyPI | MIT | font outlines, validation |
| Pillow | PyPI | MIT-CMU | frame writing / reading |
| mapbox_earcut | PyPI | ISC | polygon triangulation for the extruded letters |

The FFmpeg build is a build tool: no FFmpeg code is linked into the delivered
media, and the MP4 files are plain H.264/AAC.

## Files delivered

| file | role |
|---|---|
| `hero.mp4` | the 1920×1080 40 s hero film (H.264 / yuv420p, 24 fps, AAC 48 kHz) |
| `loop.mp4` | the 1920×1080 9.6 s seamless loop (H.264 / yuv420p, 25 fps, AAC 48 kHz) |
| `poster.png` | a 1920×1080 still taken from the hero master |
| `hero-rough-cut.mp4` | 960×540 proxy of the same edit (rough-cut / review proxy) |
| `loop-rough-cut.mp4` | 960×540 proxy of the same edit |
| `technical.json` | the measured technical QC report (codec, rate, loudness, faststart, loop gate) |
| `review-frames/` | the ≤0.5 s review grid, the dense 0.1–0.2 s samples and the 640×360 phone check |
| `HANDOFF.md` | the durable record of this production |

## Reproducibility

`agents/parallax/px/` contains the complete pipeline. From a clean checkout:

```
python3 audio.py --out work/audio          # compose the score
sh work/render_hero.sh                     # 5 x 8 s 1920x1080 hero segments + join
sh work/render_loop.sh                     # 1920x1080 loop
sh work/endgame.sh                         # mux the masters, cut the proxies
python3 qc.py --hero work/renders/hero-master.mp4 \
              --loop work/renders/loop-master.mp4 --frames --dense --gate \
              --out work/qc
```

The storyboard is the film: timings, materials, lights, camera keys and copy
all live in `storyboard.json`, and the two revision passes are applied by the
scripts in `tools/` (so the change history is reproducible, not just
described).
