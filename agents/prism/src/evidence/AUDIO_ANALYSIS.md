# AUDIO_ANALYSIS — PRISM / PROOF (env-B)

Generated 2026-10-18T18:58:19Z. Master: `audio/master_audio.wav`, 48 000 Hz, stereo, 24-bit,
25.000 s, fully self-synthesised (`audio/synth.py`, seeded numpy; no samples).

## Loudness (ffmpeg ebur128, peak=true)
```
Summary:

  Integrated loudness:
    I:         -13.7 LUFS
    Threshold: -24.4 LUFS

  Loudness range:
    LRA:        10.5 LU
    Threshold: -34.1 LUFS
    LRA low:   -19.9 LUFS
    LRA high:   -9.4 LUFS

  True peak:
    Peak:       -1.1 dBFS
[out#0/null @ 0x55ad61a3a100] video:0KiB audio:4688KiB subtitle:0KiB other streams:0KiB global headers:0KiB muxing overhead: unknown
size=N/A time=00:00:25.00 bitrate=N/A speed= 165x
```
Spec: integrated -14 LUFS +/- 1 => measured value above must lie in [-15,-13].
True peak spec <= -1 dBTP.

## Sample stats (ffmpeg astats)
DC offset: ['-0.001209', '-0.001210']
Peak level dB: ['-1.632830', '-1.632830']

## Silence map (silencedetect, -45 dB, min 0.4 s)
[silencedetect @ 0x7f6098001d00] silence_start: 15.167875
[silencedetect @ 0x7f6098001d00] silence_end: 16.000083 | silence_duration: 0.832208
(The final 0.35 s fade-out is a documented design beat, §15.6.)

## Hit alignment
Every SFX hit is placed at sample = round(frame/30*48000) — the same frame
constants the visuals use (evidence/events.json). Alignment error = 0 samples
by construction; the visual event and its hit share one frame index.
See EVENT_MAP.md for the full table.
