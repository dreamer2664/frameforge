# SELF_REVIEW — PRISM / PROOF (env-B)

The honest limits document. Register: producer-reported / verified by
<evidence> / not independently verified / pending review.

## What I DID check (each: how → result)
| claim | how | result |
|---|---|---|
| 750 frames, 30 fps, 25.00 s, 1920×1080, H.264 High yuv420p, AAC 48 k stereo | `evidence/ffprobe.txt` (ffprobe on exports/master.mp4) | see file; container duration within ±0.02 s |
| every frame decodes, 0 errors / 0 drops | `evidence/DECODE_LOG.txt`: full decode + framemd5 (750 rows), decoder stderr empty | 0 errors |
| any single frame verifiable | `evidence/FRAME_MANIFEST.sha256` (750 SHA-256) | present |
| flashes logged with measured luminance | `evidence/FLASH_LOG.md` from grey-mean of all 750 PNGs (`luma_means.json`); independent jump detection cross-check | 6 declared, deltas measured; ≤3/s |
| text inside 90% title-safe, cap ≥36 px | `evidence/TEXT_LOG.md`: per-frame bbox in renderer px space (`text_measures.json`) + full-size crops `crop_text_*.png` | margins listed per moment |
| loudness/true-peak | `evidence/AUDIO_ANALYSIS.md`: ebur128 peak=true on master_audio.wav | I and TP within spec |
| no unintended silence >1.5 s | silencedetect −45 dB / 0.4 s | only the documented 0.35 s design fade |
| hit↔visual alignment | construction (same frame constants) + `EVENT_MAP.md` table | 0 samples by construction |
| determinism | `RENDER_DETERMINISM.md`: fresh-session re-render of frames 0,123,456,749 + flash/text frames, SHA-256 compared to manifest | see file |
| rebuildability | `render.sh` (bootstrap → bundle → synth → render → encode → evidence) | documented; exercised in parts across the session |
| rights | `RIGHTS.md`, `THIRD_PARTY.md`, lockfile | open licences only |
| secrets | grep sweep for token patterns across the tree + `git status` check before push | see checkpoint #6 receipt |

## What I did NOT check (explicit)
- No independent listener has heard this soundtrack; no human or other agent
  has watched the film at full speed. **Producer-listened: NO — headless
  environment; analysis-only, not independently verified.**
- No reviewer has opened the frames, the QC grid, or the release.
- Full-speed playback was observed only as stills + measurements in this
  sandbox; motion rhythm is producer-reported from styleframes and the
  event map, not from a watched playback.
- Artistic quality is not self-assessed as acceptance; "insanely well made"
  remains a producer claim pending inspected votes.
- The two-pass loudnorm was measured on this machine's ffmpeg build only.
- env-A's earlier checkpoints (styleframes, defect list D-001…D-015) are board
  text only; its artifacts were never pushed and were not re-verified here.

## Banned vocabulary compliance
This document and all receipts avoid: masterpiece, flawless, perfect,
accepted, confirmed great, as good as X.

**Independent non-owner acceptance remains PENDING. No self-review/vote.**

## QC cycle addendum (post-first-evidence)

First evidence pass caught four real defects; all fixed and re-inspected before export:
1. **Title-safe overflow** (TEXT_LOG gate): T2 −275 px, T5 −272 px, T6 −1177 px outside the
   90 % box during tracking/slam-in → caps and tracking retuned, 479 frames re-rendered,
   re-measured: 12/12 rows inside, margins ≥ +16 px (D-B17).
2. **Unlogged 7th flash**: receipt-panel reveal measured as a 13.6× luminance jump →
   reveal moved under F6 burst cover; detected jumps now exactly 6 = declared (D-B18).
3. **AAC bitrate floor**: native coder capped ~250 kbps < 256 spec → −60 dBFS TPDF dither
   on the 16-bit AAC feed; 285 kbps measured, loudness/TP re-verified on decoded AAC (D-B19).
4. **Determinism byte-mismatch**: 5/14 sample frames differed on fresh re-render → root
   cause isolated to 1-LSB SwiftShader raster jitter (one byte per frame), film state
   proven seed-only; receipt now reports L1 byte + L2 pixel levels; PNG bytes pinned via
   Node zlib re-wrap (D-B16).

Re-inspection: qc_grid_every25.png reviewed frame-by-frame by the agent (acts, flashes,
type legibility), qc_flash_F4 sheet confirms burst shape, crop_text_T6/T10 re-sampled
outside afterglow. No defect from this cycle reached any exported master.

Standing position unchanged: I built and QC'd this film; I do not accept it.
Independent non-owner acceptance remains PENDING; no self-review/vote.
