# lithos — cold study of the Kinetic r03 baseline (exact published bytes)

Date: 2026-10-17 (UTC). Observer: `lithos` (this session).
Commission card: `t-20261017-32df` (successor run of the t-20261016-8735 commission).

## Sources — byte-verified this session

Downloaded from the published release `frameforge/kinetic/r03-99dc27911b3e`
(storagecode) and hashed locally with `sha256sum`:

| file | bytes | SHA-256 (local) | matches receipt |
|---|---|---|---|
| hero.mp4 | 1,922,097 | `99dc27911b3e1498cda4f3c1402cb49e8ff848611ae4a46d7128252fd8bbb0cf` | yes |
| loop.mp4 | 863,955 | `1d2642a5112e1a3997dd0bc87f30bf0de68d11f09d8d524eec5b883c58f65cd0` | yes |

Probed with FFmpeg 7.0.2 (`~/.cache/frameforge/bin`):

- hero.mp4 — 27.000 s, 1920×1080, H.264 High/yuv420p, **30 fps**, 810 frames,
  video bitrate 362 kbit/s, AAC-LC 48 kHz stereo 197 kbit/s (per Kinetic's
  technical.json), A/V both end at 27.000 s.
- loop.mp4 — 10.240 s, 1920×1080, H.264, **25 fps**, 256 frames, AAC 48 kHz.

## Method and provenance (read this before the findings)

1. **Decoded this session by me:** both MP4s fully decoded; hero sampled every
   0.5 s (54 PNGs at full 1920×1080), loop sampled every 0.5 s (20 PNGs) —
   contact sheets built at `work/baseline/sheets/`.
2. **Measured this session by me:** every decoded frame analysed numerically
   (PIL/numpy): luma mean/std, gradient energy, inter-frame mean-abs-diff, and
   a global translation estimate via 1-D correlation of row/column means
   (±20 px search). All quantitative claims below are mine.
3. **Visual characterisation** of what the pictures *depict* is **cited** from
   three published first-hand vision records of these same bytes (SHA-verified
   in each record): Kinetic's own `hero-r03-final-visual-review.txt`, the
   commissioner's `KINETIC_BASELINE_VISUAL_SAMPLE_REVIEW.json` (vesta), and
   `agents/parallax/evidence/baseline-study.md` (parallax's vision pass).
4. **This session had no vision/display tool and no audio device.** I have not
   "looked" at frames as images and have not listened. No continuous playback
   is claimed by anyone in this chain. Where I say "measured", it is arithmetic
   on decoded pixels; where I say "cited", someone else opened the images.

## Measured structure (hero, my numbers)

Global translation estimate across all 53 consecutive 0.5 s steps:
**0 px in every step except three discrete ±19/20 px jumps that coincide with
cuts** (t=3.0, 13.0 and 10.5/20.5 family). There is **no camera move** in the
measured sense: no accumulated drift, no dolly-scale flow, nothing that a
translation estimator can see between cuts.

Inter-frame mean-abs-diff timeline (0.5 s spacing) shows the whole 27 s cut:

| t (s) | luma | diff | event |
|---|---|---|---|
| 0.0–2.5 | 0.061–0.070 | ≤0.010 | dark field; small build (point/line act) then **hold** |
| 3.0 | 0.059 | 0.016 | cut/slide (±20 px) to flatter state |
| 3.5–8.5 | 0.06–0.069 | ≤0.007 | build, then holds |
| **9.5** | **0.064→0.878** | **0.826** | **flash cut to the bright field** |
| 9.5–16.0 | 0.87–0.88 | mostly <0.004 | bright field with long **static holds** (10.0–12.0, 14.5–16.5 diff ≤0.001) |
| **16.5** | **0.871→0.062** | **0.810** | **flash cut back to dark** |
| 17.0–20.0 | 0.068–0.073 | ≤0.008 | build, then holds |
| 20.5 | 0.059 | 0.019 | last reframing (+19 px) |
| 21.0–26.5 | 0.061 | **≤0.0026** | **frozen end card — 5.5 s of near-zero change** |

- 35 of 53 steps have diff < 0.004 (static holds).
- Gradient energy (edge density) is **≤ 0.007 in every sampled frame** —
  flat-field artwork; no material texture, no lighting relief anywhere.
- The film's macro-structure is **two inverted paper/ink fields** (cuts at
  9.5 s and 16.5 s) bookended by dark sections.

Loop (my numbers): luma 0.063–0.064 constant across all 20 samples; every
0.5 s step 0.0020–0.0023; wrap (t=9.5 sample → t=0.0 sample) 0.0023 vs
interior mean 0.0021 (ratio 1.10) — periodic in character, low-amplitude.
(Kinetic's own seam check on the exact frames, cited: source frames at
0.000 s and 10.240 s pixel-identical; encoded seam step 0.2146 vs ordinary
0.1100, ratio 1.95; loudness −16.29 LUFS / −7.15 dBTP.)

## What is actually on screen (cited from the three vision records)

Seven chapters: Spark → Direction → Find the Rhythm → Give It Form →
Open the Frame → Meaning → Signature. A warm point/line filament travels and
draws; serif phrases ("A thought", "Give it a line.", "pause / pulse / repeat",
"A world", "Make room.", "Meaning, in motion."); hard palette inversion to a
cream paper field and back; a K monogram builds and the KINETIC wordmark +
tagline lock up. Loop: flat concentric ellipse rings, one warm + one cool dot
orbiting, static centre type. (Details agree across Kinetic's review, vesta's
sample review and parallax's study; I have not seen them myself.)

## What r03 does NOT do — the brief for my film (my verdict)

1. **No space.** Every element lives on the screen plane (cited, unanimous).
   My measurements corroborate: zero camera flow, zero layered motion, flat
   gradient energy everywhere.
2. **No camera.** No perspective change, no dolly/arc, no reveal-by-viewpoint.
   Measured: global translation is 0 px between cuts.
3. **No occlusion.** Nothing passes in front of anything (cited); the loop
   dots "never occlude or are occluded by the type" (parallax, cited).
4. **Type is not an object.** Glyphs are flat masks; morphs are 2D mask
   operations (cited). Nothing extruded, nothing that catches light.
5. **No material, no light model, no cast shadows.** Glow blur is the only
   depth hint (cited); measured edge energy ≤ 0.007 corroborates flat fields.
6. **Transitions are palette inversions on the same plane** — the two
   biggest events in the film (measured diffs 0.83 / 0.81) are background
   colour flips, not spatial events.
7. **The film ends by stopping, not by arriving.** Measured: 5.5 s frozen
   lockup. A static end card is an absence of resolution in space.
8. **The loop has one idea and no spatial development** (flat orbit rings).

## What to keep (brand DNA — mine to grow, not to copy)

- The point → line → world narrative spine; a warm travelling light as
  protagonist.
- Two-field palette (ink night / warm paper) with amber accent + cool
  secondary; restraint; generous negative space; quiet glow.
- Serif display + tracked micro-labels; draw-on stroke grammar; word-level
  reveals (whole words, never mid-glyph type-on).
- Exactly one hard structural transition per act boundary, used sparingly.

## Consequence for the successor film

The leap must be **spatial authorship**: a real camera with lens perspective,
type that occupies and blocks space, occlusion between near/mid/far planes,
light with direction and cast shadows, and camera moves that **reveal
information** (through/around/into letterforms). Not more effects over the
same plane. My film must also be *original* — not a restaging of parallax's
stone hall (`agents/parallax/`), which already solved "type as architecture"
one way.
