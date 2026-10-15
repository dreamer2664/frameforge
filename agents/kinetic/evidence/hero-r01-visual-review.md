# Full hero rough cut r01 — exact-file visual review

## Exact file and technical result

- Exact candidate: `agents/kinetic/work/renders/hero-r01.mp4` (rough cut; **not** a final release)
- SHA-256: `1f1ea285f3f8bbd44b068b20c0daf6c0970c02b64dbda774ee3d31f5bd4f7110`
- 27.000 s; 1920×1080; H.264 High/yuv420p/30 fps; AAC-LC/48 kHz/stereo/197,393 bit/s; 1,909,132 bytes. Video/audio track ends both 27.000 s; 810 video frames.
- `ops/media_qc.py kinetic` returned `technical_pass: true`, no violations; measured output loudness −16.15 LUFS and true peak −4.09 dBTP. Full decode passed. FFmpeg `blackdetect` reported no threshold-qualified black interval. This is technical evidence only, not artistic or listening approval.

## What was actually opened

1. Opened all three chronological decoded contact sheets from the exact MP4, covering `0.0, 0.5, 1.0, …, 26.5, 26.9 s` (55 samples across the complete 27 seconds).
2. Opened eight dense transition sheets: 0.1s samples for the hook (0.0–1.1), direction cut (2.9–3.7), rhythm handoff (6.0–6.8), palette cut/type morph (9.2–11.1), opening words (12.4–13.5), meaning entry (16.3–17.2), signature construction (20.4–23.6), and end-card settling (23.2–24.0). All sheets are under ignored `work/inspection/hero-r01/dense/`.
3. Opened actual full-resolution decoded frames at 0.0, 0.5, 10.5, 13.0, 16.5, 17.0, 21.5 and 26.9s; opened full-size transition frames at 9.2, 9.3 and 9.4s to confirm the palette-cut contrast defect.
4. Opened an actual 640×360 phone-scale sheet at 1.0, 4.5, 7.5, 11.5, 13.5, 17.5, 23.5 and 26.5s. Main display words, the wordmark and tagline stay readable at that scale; small section labels remain secondary as intended.
5. Playback/continuous viewing and perceptual audio listening were not available. The visual review is timecoded decoded-pixel inspection; the sound result is supported only by cue timing, codec, loudness/peak measurements and seam analyses as available.

## Timecoded observations

- **0.0–1.1 — Spark:** first frame has one luminous point; the title starts drawing at 0.2s, reads “A thou…” at 0.5s, and is complete by about 0.7s. Supporting copy resolves just after. The opening action is readable within the first second, but the reveal can finish sooner without losing its restrained pace.
- **1.5–2.9 — Hold:** “A thought / starts with one point.” holds cleanly with the landed filament. This is a purposeful reading hold rather than an empty scene; low-res frame-delta analysis confirms that some consecutive images are visually very similar.
- **2.9–6.0 — Direction:** the original point carries across the cut; “Give it a line.” becomes readable by about 3.9s; the line continues to its endpoint. Fine supporting copy is still legible at the 640×360 check.
- **6.0–9.1 — Rhythm:** one baseline enters from the same traveling filament; “pause,” “pulse,” “repeat” arrive in order by about 8.5s, then hold long enough to read. No missing glyphs or collisions observed.
- **9.2–9.3 — defect found:** the frame beat starts while the field is still ink, but the new “A thought” title and `04 / GIVE IT FORM` label are already in dark blue on that dark field. Full-size samples show genuinely low contrast; the point is visible but text is not. At 9.4 the hard palette inversion to paper restores contrast. **r02 change:** use warm/ivory label, outline, and type while the field is dark, then switch to dark type/cool outline at the 9.4 paper cut.
- **10.6–10.7 — Morph:** the moving seam creates one brief intermediate “A wought” hybrid at 10.6, then resolves to “A world” by 10.7. It lasts one sampled frame and is tied to the actual traveling seam; the chosen typography remains crisp after it settles.
- **11.5 — Form:** “A world / becomes a place to go.” is high-contrast and readable inside the asymmetrical frame.
- **12.4–16.4 — Opening:** frame expands, “Make” then “room.” settle, and the cool filament draws an underline. At 13.5 the headline is clear but the support “for the unexpected.” is still very low-opacity at phone scale; it becomes clearer by 14.0. **r02 change:** move the support fade to a shorter 13.30–13.58 ease-out so it is legible alongside the settled title.
- **16.5–18.0 — Meaning:** a brief dark point/label breath follows the paper field; “Meaning,” becomes readable by 16.9, “in motion.” begins around 17.2 and is complete by about 18.0. The pause is brief and purposeful, not a black frame.
- **18.0–20.5 — Payoff:** the line travels to punctuation under “Meaning, / in motion.”; the phrase holds for reading before its path resolves into the logo sequence.
- **20.5–23.4 — Signature:** point/connector travels into the original three-stroke K, then KINETIC locks beside it and the tagline appears. The motion is sequential, with no detached old connector by the lockup.
- **23.4–27.0 — End:** deliberate readable logo/tagline hold with a subtle warm light phase; not a fade-to-black or accidental tail. The signature remains legible in the 640×360 view.

## Motion / static-frame diagnostic

An additional downscaled (320×180, luma) adjacent-frame mean-absolute-difference scan covered all 810 decoded frames. It found near-static runs during designed reading holds: about 1.5–3.0s (opening phrase), 4.4–6.1s (direction phrase), 10.7–12.5s (“A world”), 14.2–16.5s (open-frame line/phrase), 18.7–20.5s (payoff), and 23.4–27.0s (end card). These contain readable narrative text/signature; none is a blank dropped-frame interval, and the exact output has no detected black tail. The 3.6-second closing hold is intentional. The scan is a coarse motion diagnostic, not proof of continuous playback.

## Concrete r02 polish

1. The palette cut at 9.4 is structurally good, but **pre-cut form copy is low contrast**. Match the ink-side copy/label to warm ivory and invert to dark type with the paper field.
2. Bring “for the unexpected.” in with a shorter, faster ease-out; phone-scale r01 showed it lagging behind the display phrase.
3. Finish the opening “A thought” mask a little earlier (about 0.68s instead of 0.80s), preserving the dot/path action but strengthening the first-second hook.
4. Re-render the whole 27-second film, then review the exact r02 export again at 0.5s intervals and dense around the modified cuts. The current r01 is a rough cut, not a final master.
