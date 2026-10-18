# LAST SHIFT — WARD 7

A 70.000 s / 2100 frame / 30 fps portrait (1080×1920) horror storytime film,
built as a **technique replica** of a studied TikTok reel with an entirely
original story, palette, type, drawing system and score.

* Film source: `night.src.html` — one self-contained page; every element is a
  pure function of time (`window.FLUX.seek(t)`).
* Built film: `build/night.html` — the same page with the typefaces inlined as
  base64 woff2 (no network, no sidecar, no build step at playback time).
* Build: `make_assets.py` → `render.py` → `score.py` → `qc.py`.
* Evidence: `evidence/` (story + technique map, measured facts, review notes).

## Rebuild from a cold checkout

```bash
cd agents/parallax/ward

# 1. fonts: OFL (Archivo, Inter, IBM Plex Mono). The TTFs live in ward/fonts
python3 make_assets.py            # -> build/night.html + build/manifest.json

# 2. picture: Chromium drives FLUX.seek(t) frame by frame, piped into ffmpeg
python3 render.py --out work/render/film-silent.mp4 \
                  --frames 2100 --fps 30 --crf 16 --preset medium \
                  --poster work/poster.png --poster-t 39.5
# spot frames for review instead of a full render:
python3 render.py --times 4.4,23.8,39.5,55.4 --png-dir work/check

# 3. sound: own synthesised bed, no voice
python3 score.py --out work/audio/score.wav

# 4. mux + measure the delivered file + contact sheets
python3 qc.py --film work/render/film-silent.mp4 --score work/audio/score.wav \
              --master work/render/film-master.mp4 --out work/qc --sheets work/review
```

Requires `playwright` + a Chromium build, `fonttools` (with `brotli`), `numpy`,
`scipy`, `pillow` and an FFmpeg 7 binary at `~/.cache/frameforge/bin/ffmpeg`.

## The film in one paragraph

St. Aldate's Hospital, Ward 7, 04:12. The night porter has three rules posted
on the wall. The lift stops at a floor the building does not have, the shift log
records a round nobody was rostered for, every door on the ward opens at once
and something is standing in each one. The ward has forty beds and forty-one
doors. The posted board always had an empty fourth rule; the end card supplies
it — *if the door is open, it is not for you*.

## Layout

```
night.src.html   the film (source of truth)
make_assets.py   font subsetting -> one self-contained html
render.py        Chromium -> PNG -> ffmpeg (portrait 1080x1920 @ 30)
score.py         the 70 s bed (room tone, clock, lift metal, 41 door clicks)
qc.py            mux + measure + contact sheets
fonts/           OFL typefaces (subset at build time)
evidence/        story/technique map, measured facts, review notes
build/, work/    generated, gitignored
```
