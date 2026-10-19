# kinetic — dimension (r05)

40-second real-time-3D motion film, commissioned 2026-10-19 after r04 scored 4/10
("long way to go"): **"Experiment with three.js, take as much time as you need,
release a full video. 40 seconds. Cool and spectacular."**

- **Engine:** three.js (WebGL2) rendered headless — Playwright + Chromium SwiftShader,
  deterministic `applyTime(t)` scene state, frames captured via `canvas.toDataURL('image/jpeg', .93)`.
- **Output:** 1080×1920 @ 30 fps, 1200 frames, exactly 40.000 s. h264 crf17 + AAC 192k, −16.0 LUFS / −5.3 dBTP.
- **Score:** `score3.py` — 120 BPM (bar = 2 s) F-minor cinematic techno; every act cut lands on a
  bar line (4/8/14/20/28/34 s), impacts at 1.0/36.0 s. Mastered with high-shelf −2.5 dB @9 kHz + LP 17.5 kHz
  (r04 HF-noise law) and loudnorm −16.

## Act map (visual ↔ musical bar)

| t (s) | act | music |
|---|---|---|
| 0–4 | IGNITION: flicker-on cluster → implosion → shock ring + shell | drone + tick + riser, **impact at 1.0** |
| 4–8 | FORM: shell morphs onto chrome torus knot, shards orbit | build: pulse kicks + sub + stabs |
| 8–14 | TYPE: vertical MOTION column flies in (8–11.5), then 5-deep letter tunnel fly-through | drop 1: 4-on-floor + arp, hat fill 11.5 |
| 14–20 | MATERIAL: rounded-box triad — chrome → glass → wireframe | groove + melodic motif |
| 20–28 | STORM: hyperspace tube/streak run → vortex point field | double-time storm + tension strings + riser |
| 28–34 | MONOLITH: silhouette city rises against gradient sun, low-angle glide | anthem: half-time drums + wide pads + lead |
| 34–40 | FINALE: implosion to a star (34–36), flash, then `kinetic. / motion, engineered.` lockup inside halo ring | impact 34, biggest impact + resolve chord 36, fade |

## Pipeline lessons (see ../research/threejs-video-pipeline.md)

- **SwiftShader WebGL renders 1080×1920 in ~0.4–0.9 s/frame** — a full 40 s film (1200 frames)
  renders in ~17 min on 2 CPU cores. This beats offline path-tracing (r04: ~48 s/frame) by ~60×
  and unlocked real iteration (5 full keyframe review passes).
- Chromium needs `libnspr4` etc (`npx playwright install-deps chromium`), and
  `--use-gl=angle --use-angle=swiftshader --enable-unsafe-swiftshader`.
- three.js ESM + troika-three-text need an **importmap** covering troika's transitive bare imports
  (`troika-three-utils`, `troika-worker-utils`, `webgl-sdf-generator`, `bidi-js`).
- **AfterimagePass buffers carry over between non-contiguous test seeks** — keyframe reviews must
  warm up ~0.4 s of seeks before each still, or you chase ghost artifacts that don't exist in playback.
- ffmpeg OOM-kills on combined 1200-JPEG decode + loudnorm + x264 in a 2 GB sandbox — master audio
  separately, encode video separately, `c:v copy` to mux.
- End-card lockup must be measured (Box3) and **fit-scaled against the horizontal world width**
  (`2·d·tan(fov_v/2)·W/H`) — using the vertical angle overflows portrait frames.

## Review record (honest)

- 5 keyframe passes (v1 whiteout → v2 exposure fix → v3 composition → v4 vertical type + sun → v5 lockup),
  each watched via contact sheets with `read_file` before the next change.
- Full 37-sample watch of the finished encode. One real defect found (black dead-beat at 13.2 s
  between letter columns) → 5-column tunnel → re-rendered frames 320–419 only → re-encoded.
- Camera paths kept clear of geometry (monolith corridor cleared |x|<2.9, type letters part during
  the fly-through); none of the 37 samples clip geometry.

## Files

- `film.html` / `film.js` — the entire film (scene, acts, post chain, `applyTime(t)`).
- `score3.py` — the score.
- `render.mjs` — frame renderer (start/end range for partial re-renders).
- `capture.mjs` / `sheetcap.mjs` — spike + keyframe-review tooling.
- `fonts/ArchivoBlack-Regular.ttf` (OFL, Google Fonts) + `Inter-SemiBold.ttf` (OFL).
