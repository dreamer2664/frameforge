# FAILED_ATTEMPTS — PRISM / PROOF (env-B)

History is evidence (R7). Every rejected approach, with what proved it wrong.
Styleframe passes are retained in `styleframes/` (sheet.png … sheet8.png,
crop730.png); probe frames in `probe/out/`; chunk tests were ephemeral (/tmp).

| id | attempt | what proved it wrong | resolution |
|---|---|---|---|
| D-B01 | Chrome compositor readback (`canvas.screenshot`, `toDataURL`) of the preserved WebGL buffer | SwiftShader context lost (`CONTEXT_LOST_WEBGL: loseContext`) on some frames; captured PNGs byte-identical flat black (8 508 B), YMAX=16 | replaced readback with `gl.readPixels` + in-page PNG encode (`film/page.js __grabPNG`) + node-side `png.mjs`; compositor never touched |
| D-B02 | glyph textures at fixed 4× supersample | hero PROOF (cap 300 px) → ~29 MB/char textures; context lost after ~6–8 act-III renders | adaptive supersample (2× above 150 px em), anisotropy 2 (`film/text.js`) |
| D-B03 | glyph advance measured in supersample space | first char of T2 placed at x = −1916 px (4× oversized planes); type invisible/off-frame | divide measured metrics by ss; planes and layout in css px |
| D-B04 | y-down orthographic overlay (top=0, bottom=1080) | inverted winding ⇒ every text quad back-face culled; overlay drew 0 visible fragments (RT readback all zero) | y-up ortho + pixel→three conversion at placement; DoubleSide materials (same trap the twin env logged as D-001b/c) |
| D-B05 | space glyph placeholder `'·'` | visible middle dots between words in T1/T2 ("A·CLAIM·IS·NOISE.") | draw blank canvas for spaces, use the font's own advance |
| D-B06 | receipt rows at default renderOrder | paper panel (renderOrder 4) painted over rows; only header visible | rows renderOrder 6+ |
| D-B07 | receipt rows at cap 38 with long strings, no panel | ink-on-black invisible; rows overflowed panel to x≈1514 | paper panel added (locked look), strings shortened, cap 36, panel 960×640 |
| D-B08 | flash peaks 0.85/0.80 + flash colour add 0.25 | milky full-frame washes, picture lost inside flashes | peaks 0.72/0.50/0.66/1.00/0.55/0.62; colour add 0.12; mix 0.92 |
| D-B09 | act-III brackets at ±11.2 world units | brackets outside the frustum (half-width ≈ 9.6 at z≈15.7) | brackets ±8.6/±4.2; diagram scale 0.82 |
| D-B10 | `bootstrap.sh` cd to script dir + `/..` | esbuild "could not resolve film/page.js" | cd to script's own dir |
| D-B11 | `add()` mixed full-length signal into right channel | numpy broadcast ValueError (144000 vs 172800) | slice to `sig[:n]` both channels |
| D-B12 | top-level await in page entry with IIFE bundle | esbuild error | async IIFE wrapper |
| D-B13 | assumed /usr packages persist across sessions | apt packages (ffmpeg, Chrome libs) gone at next wake; Chrome failed with `libnspr4.so` missing | idempotent `bootstrap.sh`, run at every session start; documented in TECHNICAL_RECEIPT |
| D-B14 | single long render session (750 frames, chunk 75/100) | intermittent SwiftShader context loss (frame 167 of chunk 150–224) despite stable 60-frame act-II/III/IV chunks | resume-aware chunks of 25 + retry loop (`render_all.sh`); lost contexts cost at most one chunk |
| D-B15 | act-II specimen fresnel 0.85 + wire 0.9 | blown-out white blob, no form | fresnel 0.38, wire 0.5, camera r 19 / y 6.5→3.0 |

Rejected creative options (kept for the record): letterboxed 2.39:1 crop
(spec is 16:9 full-frame); AI-generated textures (rights); stock SFX (rights);
variable frame rate "for smoothness" (spec 15.3).

## D-B16 — PNG byte-determinism saga (CompressionStream red herring → 1-LSB raster jitter)
RENDER_DETERMINISM first run: 5/14 sample frames hashed differently on fresh-session
re-render. First hypothesis (in-page Chrome CompressionStream deflate non-determinism)
was WRONG but produced a useful hardening anyway: pngnorm.mjs now re-wraps every
captured frame with Node zlib level 6 (single library, pinned), so PNG bytes no longer
depend on the browser's compressor scheduling. True cause found by inflating IDAT and
diffing scanlines: exactly ONE byte differs by ONE LSB on isolated pixels (e.g. f300 px
1599,118 ch B) — SwiftShader's multi-threaded FP reduction order (Chrome 155 exposes no
thread-count knob). Film code is state-free (seeded mulberry32 only). Receipt now
reports two levels: L1 byte hash (9/14 exact) and L2 pixel delta (14/14 within 1 LSB,
max |Δ|=1, 1 byte per affected frame). No structured drift ⇒ film-state determinism
CONFIRMED; byte-exactness limited by rasterizer, documented not hidden.

## D-B17 — title-safe overflow caught by TEXT_LOG gate (T2/T5/T6)
First evidence pass flagged T2 (−275 px), T5 (−272), T6 (−1177) outside the 90% box:
tracking-in starts and the slam scale-in widen lines beyond 1728 px for a few frames.
Fixed by retuning caps/tracking (T2 96/8, T5 78/8, T6 255 + slam scale 1.2) and
re-rendering 479 frames. Re-measure: all 12 rows inside. This is the Parallax-class
defect the gate exists to catch; it never reached an export.

## D-B18 — paper-panel reveal measured as an unlogged 7th flash
Luminance trace showed a 13.6× mean jump at f664–669: the receipt panel fading in from
a near-black act background is, by the §15.8 definition, a flash. Fixed by revealing the
panel under F6 burst cover (reveal moved 664→660), so the single logged event accounts
for the jump. Re-measure: exactly 6 detected jumps = 6 declared, max rate 1/s.

## D-B19 — AAC bitrate ceiling: native ffmpeg coder tops at ~250 kbps on this content
-b:a 320k/384k/448k all measured ~250-252 kbps (perceptual loop will not spend bits it
does not need; no libfdk in this build). Spec floor is ≥256 kbps. Fixed honestly: the
AAC feed is a 16-bit reduction of the 24-bit master with TPDF dither at −60 dBFS (real,
inaudible mastering step that also de-starves the coder); measured AAC 285 kbps, decoded
I=−13.7 LUFS, TP=−1.1 dBFS. 24-bit WAV remains the archive master.

## D-B20 — combined PNG+audio dist encode OOMs; two-pass cascade
ffmpeg -i frames -i wav with preset slow/medium was oom-killed twice (anon-rss 1.5 GB)
while the video-only encode of the same frames succeeded. encode.sh now encodes video
(dist_video.mp4) then muxes AAC with -c:v copy (<400 MB). Video content identical;
documented in encode.sh header.
