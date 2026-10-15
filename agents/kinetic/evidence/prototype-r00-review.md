# Hard-shot prototype r00 — exact file review

## Exact file and pipeline

- File: `agents/kinetic/work/renders/prototype-hardshot.mp4` (ignored working output; not a hero deliverable)
- SHA-256: `ad389a3eecec8fa567860fc75d91ff8a4045c6223089b20359c89e130cb9d531`
- Probe: 8.000 s; 1920×1080; H.264 / yuv420p / 30 fps; AAC 48 kHz / 192,982 bit/s target-equivalent. 1,237,497 bytes.
- Picture is a deterministic 240-frame render from master timeline 9.0–17.0 s; sound slice is from the full 27.0 s procedural hero cue WAV. Prototype is real encoded media with actual sound, not a still or a screen recording.
- Audio source SHA-256: `54e6edabe305bcc20ae7ae2cd59080243fa520d95f999c5758c6930bd111b13b`. Measurement of the unnormalised source: −31.7 LUFS integrated, −19.83 dBTP. It is intentionally an early mix, too quiet for final delivery; the final master will be loudness-managed and independently remeasured.

## Visual inspection actually performed

- Opened `work/inspection/prototype/sheet-000.jpg`, decoded from the exact MP4 at relative `0.0, 0.5, 1.0, …, 7.5, 7.9 s` (the corresponding master times are 9.0–16.9 s).
- Opened full-size decoded frames at relative 2.5 s / master 11.5 s; 4.0 s / 13.0 s; and 7.5 s / 16.5 s. Separately opened actual pre-export full-resolution smoke frames at master 10.8, 11.0 and 11.2 s to inspect the glyph seam.
- This was chronological still inspection, not a continuous playback and not perceptual listening.

## Timecoded observations and changes driven by them

- **9.0–9.5:** the three-word rhythm reads, and the outlined frame begins coherently. The long dark↔paper crossfade reaches an unattractive uniform grey by 9.5. **Change:** make the palette state a deliberate short hard inversion at 9.4; the continuous filament/frame carries continuity across it instead of a mid-grey dissolve.
- **11.0–11.2:** “A thought” resolves to “A world”; the moving seam is visible, but the unequal-width old word leaves a final `t` for an extra fraction of a second. **Change:** shorten the wipe to finish at 10.94 (full word is settled by 11.0) while keeping the seam bounded to actual glyph widths.
- **11.5:** the subtitle “becomes a place to go.” is low-opacity and too faint at the sampled instant. **Change:** increase its ink contrast and shorten its fade to finish by 11.58.
- **13.0:** only the initial `M` of “Make room.” is on-screen; it begins outside/against the frame’s left edge while the frame expands. **Change:** animate the headline’s x-position from the inner edge of the small frame to its final left margin, keeping it inside the evolving shape throughout the reveal.
- **16.5:** the paper-to-night blend produces a blank, flat grey screen around the scene boundary. **Change:** replace the full-screen dissolve with a single beat-linked palette inversion at 16.5; start the payoff filament at the same 180×520 endpoint where the previous line finished.
- **Overall:** source-level smoke frames showed the signature connector lingering beyond the K and an unnecessary endpoint dot. Those were removed before this MP4 prototype; exact source-smoke path is `work/frame-smoke/`.

## Verdict and next action

**Prototype is viable but not polished:** it proves an original hard shot with a real path-driven word replacement, outlined material/frame action, paper/night palette inversion, and a procedural audio cue path. The review found transition contrast, frame-relative type placement, and subtitle timing defects; those are fixed in renderer source for the next 8-second prototype. Next: encode the corrected picture with loudness-managed audio, decode and inspect the exact new file densely around 10.5–11.1 and 12.4–13.2 master time, then begin the full rough cut.
