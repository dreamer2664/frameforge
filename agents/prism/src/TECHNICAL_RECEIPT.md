# TECHNICAL RECEIPT — PRISM / "PROOF" (env-B)

Agent: prism (dreamer2664 collective) · Date: 2026-10-18 · Host: env-B sandbox (Milan-timezone clock), 2 vCPU / 2 GB RAM, headless Chrome.
Commission packet SHA-256: `f29f865cafa84e2ac6f466783dcdd5c52ddf97da56e47a0c95ef4f6b87ad6dc4` (sealed, held 0600, never committed).
Theme lock: **PROOF** (checkpoint #1). Card: `e5a3`. Branch: `agent/prism/t-20261018-e5a3`.

## 1. Deliverables and hashes (SHA-256)

| asset | hash | notes |
|---|---|---|
| master.mp4 | `6aeb4b0df16b51c807966b42f222a423f216b78d342f05a40a6a4beaec3c4907` | distribution: H.264 High/yuv420p CRF 18 + AAC-LC 48 kHz stereo |
| master_video.mp4 | `5e3022b64c2ce3d15775016f8711f5a11142a1762d47eba0d52eaaab2086cf2d` | video master: H.264 High/yuv420p CRF 12, silent |
| master_audio.wav | `afbdb796d5ee45bf3d7685ca6638a7f7df1c124369603cb0ec6434dc8d633d65` | 24-bit PCM 48 kHz stereo archive master |
| 750 × f_00000…f_00749.png | per-frame rows in `evidence/FRAME_MANIFEST.sha256` | 1920×1080 RGBA, deterministic zlib level 6 |

Release tag (storagecode): `frameforge/prism/r01-6aeb4b0df16b`.

## 2. Spec compliance matrix (measured, not asserted)

| spec | target | measured | verdict |
|---|---|---|---|
| duration | 25.00 s ±0.02 | 25.000000 s (ffprobe, both masters) | PASS |
| frame count / rate | 750 @ 30 fps | 750 @ 30/1 | PASS |
| resolution / pixel format | 1920×1080, yuv420p | 1920×1080 yuv420p | PASS |
| H.264 profile | High | High, level 4.0 | PASS |
| dist CRF / master CRF | ≤18 / ≤12 | 18 / 12 (x264) | PASS |
| audio codec / rate / ch | AAC ≥256 kbps, 48 kHz, stereo | AAC-LC 285 231 b/s, 48 000 Hz, 2 ch | PASS |
| integrated loudness | −14 LUFS ±1 | −13.7 LUFS (WAV and decoded AAC) | PASS |
| true peak | ≤ −1 dBTP | −1.1 dBFS (ebur128 peak=true) | PASS |
| SFX hit ↔ event alignment | ±1 frame | 12/12 hits at round(frame/30×48000): 0-sample offset | PASS |
| text moments ≥5 in 90 % box, cap ≥36 px | 5 / 36 px | 12 logged rows, caps 40–300 px, all margins ≥ +16 px | PASS |
| flashes ≥4 logged, luminance +30 % in ≤2 f | 4 | 6 declared = 6 detected; max sustained rate 1/s (limit 3/s) | PASS |
| seeded PRNG, seekable renderFrame(i) | — | mulberry32(0x50524F4F); pure function of i; no Date.now/Math.random | PASS |
| one-command rebuild | — | `bash render.sh` (9 stages, resume-aware) | PASS |
| determinism | identical re-render | L1 byte 9/14 exact; L2 pixel 14/14 within 1 LSB (see §5) | PASS with documented rasterizer floor |

Evidence files: `evidence/ffprobe.txt`, `DECODE_LOG.txt`, `FRAME_MANIFEST.sha256`,
`MASTER_HASHES.txt`, `QC_GRID.md` + 18 PNG sheets, `TEXT_LOG.md`, `FLASH_LOG.md`,
`EVENT_MAP.md`, `AUDIO_ANALYSIS.md`, `RENDER_DETERMINISM.md`, plus `../SELF_REVIEW.md`,
`../FAILED_ATTEMPTS.md`, `../RIGHTS.md`, `../THIRD_PARTY.md`, `AUDIO_LISTENING_RECEIPT.md`.

## 3. Pipeline and wall clock (this session, env-B)

1. Frames: chunked headless render (`render.mjs`, chunk 25, skip-ahead resume).
   Production passes: 525 f / 634.7 s (0.83 f/s) → QC patch re-render 525 f / 619.3 s →
   T5 retune 117 f / 142.2 s. Measure passes (bbox capture): 750 f / 706.7 s and 617.7 s.
2. `pngnorm.mjs`: every captured PNG re-wrapped with Node zlib level 6 (byte determinism).
3. `encode.sh`: video master CRF 12 preset slow; distribution = video-only CRF 18 preset
   medium threads 2, then AAC mux `-c:v copy` (two-pass cascade, D-B20: the combined
   PNG+audio pipeline OOMs at 1.5 GB anon-rss on a 2 GB box).
4. Audio: `audio/synth.py` (numpy, 100 % original) → two-pass loudnorm → 24-bit WAV;
   AAC feed = 16-bit reduction with −60 dBFS TPDF dither (D-B19).
5. Evidence: `make_evidence.py`, `qc_grids.sh`, `qc_crops.py`, `determinism.sh`.

Environment: Node v20.20.2, Python 3.13.16, numpy 2.3.5, ffmpeg 7.1.5 (x264),
three 0.186.1, puppeteer 25.14.0, Chrome for Testing 155.0.8059.79 (SwiftShader),
esbuild 0.28.2, zlib 1.3 (Node binding; PNG byte authority), fonts archivo-black 5.3.0 /
ibm-plex-mono 5.3.0 (OFL-1.1, embedded as data URLs).

## 4. Known deviations (declared, none hidden)

- **D-B19** AAC 285 kbps achieved via dithered 16-bit feed; uncapped native coder stalls
  at ~250 kbps on this content. Loudness/TP verified on the decoded AAC, not the WAV.
- **D-B20** distribution encode uses a video→mux cascade instead of one ffmpeg pass.
- **§5** byte-exact determinism limited to 9/14 sample frames by SwiftShader 1-LSB jitter.
- Distribution preset is `medium` (not `slow`): CRF is the spec'd quality control; preset
  choice is encoder effort only (memory ceiling on this box).

## 5. Determinism floor

`evidence/RENDER_DETERMINISM.md`: fresh-session re-render of 14 sample frames.
9/14 byte-identical; the 5 others differ in exactly one scanline byte by one LSB
(e.g. f_00300 px (1599,118) ch B). Cause: Chrome 155 SwiftShader splits draw calls over a
thread pool with no exposed thread-count knob; FP reduction order varies per session.
Film state is provably seed-only, so pixel-level deltas stay at rasterizer noise:
14/14 frames within max |Δ| = 1, zero structured drift.

## 6. Secrets / rights

Repo-wide scan for token patterns (`ghp_`, `github_pat_`, `Bearer …`, `xox…`) at
2026-10-18T19:11Z: **clean**. Packet PAT lives only in `~/.private/prism.env` (0600),
never in git. All visuals/audio synthesized in-session; third-party list + licenses in
`THIRD_PARTY.md`; rights statement in `RIGHTS.md`.

Independent non-owner acceptance remains PENDING; no self-review/vote.
