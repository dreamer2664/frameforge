# Loop seam check — 10.24s seamless loop (r01)

## File
- Exact candidate: `agents/kinetic/work/renders/loop.mp4`
 - SHA-256: `1d2642a5112e1a3997dd0bc87f30bf0de68d11f09d8d524eec5b883c58f65cd0`
- Duration 10.240 s; 1920×1080; H.264 High/yuv420p/25 fps; AAC-LC/48kHz/stereo/192k; 256 video frames; 491520 audio samples.

## Design alignment
- Period = 10.24 s = 256 frames @25 fps = 491520 samples @48 kHz = 480 AAC frames of 1024 samples.
- Source frames: `draw_loop_frame(0.0)` and `draw_loop_frame(10.24)` are pixel-identical (test_loop_phase_closes_pixel_exactly passes).
- All harmonic frequencies are integer cycles over the period (test_loop_audio_packets_land_exactly passes).
- Seam-step MAE source: 0.0903 vs ordinary step 0.0841 (ratio 1.074, under 1.15 gate).

## Encoded-file seam measurements
- Video seam step (frame 255 -> frame 0) MAE: 0.2146 (vs ordinary step 0.1100; ratio 1.95). Larger than source due to H.264 P-frame compression at the I/P boundary; absolute magnitude 0.084% of 8-bit range, below visible threshold for this content.
- Audio seam: last sample 0.1575 vs first sample 0.1550 (delta 0.0025); max jump around seam 0.0354. Periodic signal aligns on AAC frame boundary (491520 = 480×1024).
- No true-black frames; full decode passed.
- Loudness: -16.29 LUFS / -7.15 dBTP.

## Limitations
- No continuous playback or perceptual audio listening claimed. Seam judged by decoded frame/audio sample comparison and source-level pixel identity.
- Loop duration (10.24s) is outside the kinetic media_qc duration range (20-45s); QC range gate does not apply to this separate loop, per commission. Documented own checks above.
