# Hard-shot prototype r01 — exact-file review

## Exact media / measurements

- Exact file: `agents/kinetic/work/renders/prototype-hardshot-r01.mp4` (prototype only; not the hero)
- SHA-256: `082556bbb3d1cde0ba4dabccbd8dfca9fed6259a4ab9e557586207b638356a71`
- 8.000 s; 1920×1080; H.264/yuv420p/30 fps; AAC/48 kHz/195,653 bit/s; 704,250 bytes.
- This is a 240-frame render of master timeline 9.0–17.0 s, muxed with the 9.0–17.0 slice of the procedural score after two-pass loudness normalization. Prototype AAC measurement: −16.3 LUFS integrated, −4.6 dBTP. The sound was numerically measured, not perceptually listened to.

## Actual review coverage

- Opened the decoded exact-file contact sheet with samples at `0.0, 0.5, 1.0, …, 7.5, 7.9 s` (master time 9.0–16.9 s).
- Opened full-size decoded frames at relative 2.5 s / master 11.5 s, 4.0 s / 13.0 s, and 7.5 s / 16.5 s.
- Extracted and opened a dense contact sheet from the exact MP4 at master 10.4–11.2 s in 0.1 s increments (nine decoded frames). This is still sampled visual inspection, not continuous playback.

## Findings and revision

- **Palette:** the hard cut at master 9.4 cleanly replaces the earlier muddy full-screen grey. The same filament and polygon outline keep the story connected. The return to ink at 16.5 is dark, not grey.
- **Morph:** the new phrase is legible by master 10.9–11.0; the 0.1-second samples around 10.7–10.8 briefly form a hybrid of the old and new glyphs at the moving seam. It reads as a transformation but holds the hybrid a fraction too long. **r02 edit:** shorten the seam wipe to 0.28 seconds; the warm seam remains the cause of the substitution.
- **Frame-relative title:** at master 13.0 the leading `M` is now inside the expanded frame rather than outside it. The word then resolves cleanly as the frame outruns it. **r02 edit:** use a fast ease-out on the opening mask so it does not hold a single-letter fragment for too long.
- **Subtitle:** “becomes a place to go.” is clearly readable at master 11.5 after the shorter, darker fade. This is a substantive fix from the very faint r00 subtitle.
- **Meaning transition:** master 16.5 is a brief dark beat with the point and section label, then the headline begins to appear. The full-screen palette is now intentional, but the headline reveal is too slow at first. **r02 edit:** use a faster ease-out for “Meaning,” to avoid a lingering isolated `M`.
- Labels in this r01 source still use the earlier duplicate numbering; r02 renumbers the sequence consistently from 01 through 07.

## Current state

The actual 8-second prototype now proves the visual grammar, licensed display/UI type, path-led word replacement, asymmetric frame expansion, purposeful warm/paper/ink palette states, and a real authored audio pipeline. r00’s observed contrast and transition defects are materially corrected. r01 is not a final; the next 0.28-second morph and faster type-entry changes still need to be rendered and inspected in r02, then the complete hero will be rough-cut and receive two whole-film inspect/revise passes.
