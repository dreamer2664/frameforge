# Three.js → video pipeline research (r05 "dimension", 2026-10-19)

Commissioned pivot after r04 (Blender offline render) scored 4/10: experiment with
three.js and ship a 40 s "cool and spectacular" film. This note records what makes
WebGL-filmmaking work in a 2-core CPU sandbox, distilled from the r05 build.

## 1. Headless capture is the renderer

- **Playwright + Chromium headless shell + SwiftShader** (`--use-gl=angle --use-angle=swiftshader
  --enable-unsafe-swiftshader`) gives a real WebGL2 context with `preserveDrawingBuffer`.
- Measured: **0.4–0.9 s per 1080×1920 frame** (simple scenes at the low end, bloom+afterimage+
  2k particles at the high end). 1200 frames ≈ 17 min on 2 cores.
- Capture via `canvas.toDataURL('image/jpeg', 0.93)` returned to Node — faster than CDP screenshots
  and already compressed for disk.
- Determinism: the entire scene is `applyTime(t)` — a pure function of time (no wall-clock,
  no accumulated physics state). Seeded PRNG (mulberry32) for every "random" constant.

## 2. Why it looks expensive

- **PMREM + RoomEnvironment** (procedural, no HDR download): metals need a world to reflect;
  chrome/glass without an env map reads as plastic. `scene.environmentIntensity ≈ 0.38–0.5`
  keeps it from washing out.
- **UnrealBloomPass** is the single biggest "spectacular" signal. Keep threshold high (0.85+)
  and strength moderate (0.5) or additive particle systems nuke the frame to white (v1 defect).
- **AfterimagePass** gives cheap motion-smear/trails — the "whip" look of expensive motion design.
  Set damp per act (0.12 calm, 0.55 type tunnel, 0.68 storm) and force **0 within ±0.22 s of cuts**
  so acts don't smear into each other.
- Custom ShaderPass after OutputPass for grade: chromatic aberration, vignette, film grain,
  S-curve, flash/fade uniforms. Everything the r04 grade did in Python now happens in-frame.
- Additive `THREE.Points` with a tiny custom ShaderMaterial (soft round sprites, per-particle
  seed/phase) is the cheapest path to "particle storm" (1600–2400 points, zero per-frame JS cost
  if the vertex shader computes motion from `uT`).

## 3. 3D type in the browser

- **troika-three-text** renders any TTF as crisp SDF text in the scene, with per-mesh transforms
  (letters animate individually). Needs an importmap for its bare deps:
  `troika-three-utils`, `troika-worker-utils`, `webgl-sdf-generator`, `bidi-js`.
- Portrait (9:16) frames are TALL, not wide: a single horizontal word overflows almost any
  reasonable focal length. **Vertical staggered letter columns** (letters alternating left/right
  of the camera axis) are portrait-native AND open a flight corridor for fly-throughs.
- End-card lockups must be **measured at runtime** (Box3) and fit-scaled against the horizontal
  world width `2·d·tan(fov_v/2)·aspect`. Using tan(fov_v/2) alone overflows by ~2×.

## 4. Camera language that survived review

- Cuts on musical bar lines (4/8/14/20/28/34 s at 120 BPM = 2 s bars) + 2-frame flash + fov punch.
- One continuous "one-shot" act is worth more than many static ones: the letter tunnel (2.2 s
  fly-through) and the storm run (8 s of forward flight) carried the film.
- Never clip geometry: clear instanced-scene corridors for the camera path (monoliths were
  pushed out of |x|<2.9 for a ±1.35 m sway), and open type corridors during fly-throughs.

## 5. Audio for 40 s

- 120 BPM = 2 s bars makes 40 s exactly 20 bars — act cuts land on bars for free.
- Structure: intro → build → drop → groove/motif → storm (double-time + tension strings) →
  anthem (half-time + wide pads) → finale (impacts at 34/36 + resolve chord + tail).
- r04's HF law holds: dark-filter hats/claps, verify with `showspectrumpic` + band-RMS;
  master shelf −2.5 dB @9 kHz + LP 17.5 kHz, loudnorm −16 LUFS / TP −1.5 at mux.

## 6. Sandbox traps (2 GB RAM, 2 cores)

- Chromium needs system libs: `npx playwright install-deps chromium` (libnspr4 etc).
- ffmpeg dies (OOM kill) when decoding 1200 JPEGs + loudnorm + x264 in one process:
  master audio separately, encode video separately, mux with `-c:v copy`.
- x264 `preset fast -threads 2` at crf17 is RAM-safe; `medium` is not, in this box.
- WebGL context + npm packages live in node_modules (snapshot-excluded) — sources only in git.
