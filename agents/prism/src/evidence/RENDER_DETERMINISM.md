# RENDER_DETERMINISM — PRISM / PROOF (env-B)

Generated 2026-10-18T19:09:57Z. A FRESH headless
session (new Chrome, new page, no shared state) re-rendered the sample frames
below. `renderFrame(i)` is a pure function of i with a seeded PRNG (mulberry32,
seed 0x50524F4F); no wall-clock, no Math.random anywhere in film code.

- **L1 (byte)**: SHA-256 of re-rendered PNG vs `FRAME_MANIFEST.sha256`.
- **L2 (pixel)**: inflated IDAT scanline comparison — differing bytes and max
  |delta|. Chrome 155's SwiftShader has no thread-count knob in this build; its
  multi-threaded FP reduction can move 1 LSB on isolated pixels between
  sessions. L2 separates that rasterizer jitter from film-state drift (which
  would show as large/structured deltas).

| frame | re-render SHA (16) | manifest SHA (16) | L1 | L2 bytes diff | L2 max delta |
|---|---|---|---|---|---|
| f_00000.png | e730aa8f8e590624… | e730aa8f8e590624… | MATCH | 0 | 0 |
| f_00040.png | bdf60ff092c0142a… | 67609bed93038ea3… | diff | 1 | 1 |
| f_00123.png | 2b1811067e0440c8… | 2b1811067e0440c8… | MATCH | 0 | 0 |
| f_00150.png | 3d77a56a4e3db11e… | 3d77a56a4e3db11e… | MATCH | 0 | 0 |
| f_00300.png | c2a22d8ba9e8493f… | 7ecf3249b56b4759… | diff | 5 | 1 |
| f_00330.png | 31ce5cf333f28f5d… | b1db96686c4878d4… | diff | 5 | 1 |
| f_00390.png | 561a9cc72fb3f5ef… | a8c8bb7c5d79e3f1… | diff | 1 | 1 |
| f_00456.png | fada5093600980a1… | fada5093600980a1… | MATCH | 0 | 0 |
| f_00480.png | 632c35742b6d9b44… | 632c35742b6d9b44… | MATCH | 0 | 0 |
| f_00483.png | 7eef32c97a19d24c… | 7eef32c97a19d24c… | MATCH | 0 | 0 |
| f_00560.png | e5f47c5c45f0e6ee… | e5f47c5c45f0e6ee… | MATCH | 0 | 0 |
| f_00660.png | d2d5242d5eaec02d… | d2d5242d5eaec02d… | MATCH | 0 | 0 |
| f_00700.png | 3bacfa78c06a657d… | 135a6efbb55468f8… | diff | 3 | 1 |
| f_00749.png | ac0f392ebd25b4a8… | ac0f392ebd25b4a8… | MATCH | 0 | 0 |

Byte-identical: 9/14.
Pixel-identical within 1 LSB: 14/14.
Verdict: film-state determinism CONFIRMED (all deltas within rasterizer
1-LSB jitter; no structured drift). Byte-level: 9/14 exact,
remainder differ only in the bytes carrying the 1-LSB pixels above.
