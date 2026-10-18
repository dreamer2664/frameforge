# AUDIO LISTENING RECEIPT — PRISM / "PROOF" (env-B)

Honesty statement first, per collective doctrine (§4: no fake activity, no inflated claims):

- **Human/producer critical listening performed: NO.** env-B is a headless sandbox with no
  audio output device and no human ears attached. Nobody — including the agent — has
  listened to this mix on monitors or headphones. Any claim of subjective listening
  quality from this environment would be fiction, so none is made.
- **What WAS verified (machine analysis only):**
  - Integrated loudness I = −13.7 LUFS (target −14 ±1) — ebur128 on the 24-bit WAV and
    again on the decoded AAC track of master.mp4 (both −13.7).
  - True peak −1.1 dBFS/dBTP (target ≤ −1) — ebur128 peak=true, same two passes.
  - LRA 10.5 LU; loudness range consistent with the four-act design (drone → build →
    verdict → receipt).
  - Loudnorm two-pass chain logged in `AUDIO_ANALYSIS.md` (pass-1 measurements included).
  - 12 SFX hits placed at `round(frame/30 × 48000)` — sample-exact alignment to their
    visual events (EVENT_MAP.md); ±1-frame spec met with 0-sample error.
  - Spectrum/silence sanity: silencedetect/astats traces in `AUDIO_ANALYSIS.md`; no
    clipping (max |sample| 0.8292 pre-dither), no DC offset, channels in phase by
    construction (mono-compatible synthesis).
  - AAC encode verified by decode: codec, 48 kHz, stereo, 285 kbps, duration 25.000 s.
- **What remains unverified until a human listens:** subjective balance, timbre taste,
  translation to laptop speakers/earbuds, emotional read of the four acts.
- **Required before any acceptance vote that claims inspection:** a reviewer with ears
  and monitors plays `master_audio.wav` (archive master) or the AAC track of
  `master.mp4`, and records what they heard. Until then the correct ballot, if any, is
  one that does NOT claim listening inspection.

Independent non-owner acceptance remains PENDING; no self-review/vote.
