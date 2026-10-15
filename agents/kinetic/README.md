# Kinetic — “A thought becomes a world”

An original, deterministic, time-based 27-second 1920×1080 H.264 kinetic-typography film and separate 10.24-second seamless loop (25fps, 256 frames). The working renderer draws at 1280×720 and encodes through FFmpeg Lanczos scaling to 1920×1080. Every cue is frame/time driven at 30 fps; no screen recording or remote rendering service.

## Run

Requirements: Python 3.10+, Pillow 12.x, NumPy 2.x, FFmpeg/ffprobe. From the repository root, install the local FFmpeg toolchain with `python3 ops/bootstrap_media.py` if system binaries are absent. Set `FFMPEG_BIN` only if the binary is not in the helper cache or `PATH`.

```bash
cd agents/kinetic
python3 -m pip install -r requirements.txt
python3 render.py --kind hero --out work/hero-picture.mp4
python3 audio.py --kind hero --out work/hero.wav
# Mix/measure with the two-pass loudnorm recipe in evidence/production-notes.md.
python3 render.py --kind loop --out work/loop-picture.mp4
python3 audio.py --kind loop --out work/loop.wav
```

`storyboard.json` is the editable scene/timing/art-direction sheet; `audio_cues.json` is the editable cue map. `render.py` accepts `--start`, `--duration`, and `--fps` for prototype ranges. The audio generator accepts `--start` and `--duration` for deterministic cue windows. Audio is procedurally generated; no sample, voice, stock music or external asset is required.

## Source and evidence

- `fonts/` contains only the licensed font candidates used in production and their full OFL texts; exact hashes/versions/source URLs are in `evidence/source-rights.md`.
- `evidence/` records reference study, concept and type trials, rights, final technical/visual reviews, loop seam checks and publication receipts.
- `work/` and `renders/` are ignored build areas; private reference downloads and raw frames stay under `work/refs/` and must never be published.
- `HANDOFF.md` is the generated durable action record. Add entries using `python3 ops/field.py event kinetic ...`; do not hand-edit generated history.

There is no narration; captions are not applicable. Final perceptual audio listening is not claimed unless a real listening tool becomes available; retain meter, waveform, codec and seam checks as the actual evidence.
