# Review method — lithos / THE LONG LIGHT

## What this production could and could not do (read first)

This film was built, rendered and reviewed **headless**: no display, no audio
device, no vision tool in the agent session, no human listener. Therefore:

* I have **not** watched the film play. No continuous playback is claimed.
* I have **not** listened to the score. No perceptual listening is claimed.
* Where this production says "reviewed", it means: the delivered MP4s were
  **decoded and measured** (pixel statistics, depth of the render's own
  geometry, loudness/seam numbers), and every sampled frame was written to
  disk at full size and published as labelled contact sheets **for human eyes**.
* Visual characterisations of *depicted content* in the evidence set are
  either (a) geometric facts about the scene that this code placed (positions,
  sizes, sight-lines — provable from `storyboard.json` + `scene.py`), or
  (b) measurements on decoded pixels. Nothing is claimed as "seen".

This is the same honesty rule the commission states for sound ("no claim of
listening that did not happen"), applied to the picture too.

## Review coverage (on the delivered files)

1. **Every ≤ 0.5 s of the hero** decoded at full 1920×1080 (`work/qc/frames/`,
   85 samples for 42.0 s) and assembled into labelled contact sheets
   (`work/review/sheet-00..nn.png`) — published for human inspection.
2. **Dense 0.1 s samples** around every structural transition (`work/qc/dense/`):
   3.5 s (vault→exit), 8.0 s (exit→colonnade), 11.05 s (pier pass), 17.0 s
   (colonnade→dial), 18.5 / 20.3 / 22.1 / 23.9 s (station crossings), 26.0 s
   (dial→rise), 29.5 s (terminus landing), 34.0 s (rise→still).
3. **The loop** decoded every 0.5 s + its encoded seam gate (geometry, position,
   velocity, light phase, audio seam) with exact numbers.
4. **Phone check** at 640×360 (41 samples).
5. **Craft probe** (`tools/craft_probe.py`) on the delivered hero and on the
   Kinetic r03 baseline with the same tool: planarity residual after global
   shift, 3×3 block-shift spread (layered motion), occlusion-edge candidates,
   luma/edge/dark/hot per sample. A flat-card film and a spatial film score
   differently; both numbers are published.
6. **Depth evidence from the render itself** (not guessable from the codec):
   per-frame depth-buffer percentiles (near/mid/far span in one frame) at every
   beat, recorded in `work/qc/depth-spans.json`.
7. **Technical QC**: `qc.py` (container, codec, rates, faststart atom order,
   A/V tail, loudness + true peak, full decode) and the house `ops/media_qc.py`.
8. **Full-size single frames** at 0.5, 2.0, 5.0, 10.0, 19.0, 23.0, 29.5, 33.5,
   41.0 s extracted and published as individual files.

## Defect policy

Any defect that a measurement can prove (caption outside frame — n/a here,
all text is diegetic world geometry; loudness out of range; seam step above the
interior's own step distribution; luma/contrast below the legibility floor of
the inscription contrast ratio) is fixed and the affected material re-rendered,
with before/after numbers recorded in the revision evidence. Two consequential
revision passes are the minimum; each must change something a viewer would
notice and be recorded.

## What the review explicitly does not claim

* No frame was looked at by a human or a vision model inside this session.
* No audio was heard by anyone in this chain.
* "Readable at real size" for the diegetic inscriptions is established by
  geometry (cap heights and camera distances are computed; e.g. the gnomon is
  7.2 m at 23.6 m from the dial centre, the station words are 0.52 m caps and
  are crossed at frame-centre distances of X m at 1920 px — numbers in
  film-facts.md), not by a viewing test.
