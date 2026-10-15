# Creative direction — selected autonomously

## Promise and emotional arc

**One-sentence promise:** Kinetic turns one small thought into a world with shape, rhythm, and room to move.

**Arc:** curiosity (a point) → direction (a line) → rhythm (three deliberate beats) → expansion (a thought is replaced by a world) → clarity (the frame opens) → quiet signature (the moving line resolves to K).

This is a motion-design identity piece, not a product demo. There are no claims about a real AI service, no fabricated controls, and no narration simply to fill time. The copy is short enough to choreograph as real type.

## Three materially different boards compared

`concept-boards.png` is the actual private art-direction study; it was made from licensed font files and original vector shapes. These alternatives are internal reasoning artefacts, not a request for Director selection.

1. **Single point → living world — selected.** Near-black/warm copper/cool glass; a serif display phrase and Inter support labels; one bright filament carries the viewer from point to path to rhythm to an open frame. It provides a specific story and a visual continuity device. The K is drawn from three asymmetric strokes rather than a radial burst.
2. **Paper engine.** Cream/ink/mineral blue; Playfair Display + Inter; a ruled editorial grid and modular field. Strongly legible and composed, but it makes the film read as a static title page and offers less emotional transformation.
3. **Signal / echo.** Charcoal/electric mint/coral/violet; Inter-only, all caps, stepped vertical bars. The bold rhythm is immediate, but it lands in generic high-energy tech shorthand and weakens the intimate story of an idea becoming a world.

Chosen board 1 for its warm-to-cool material progression, human display voice, continuous line grammar and original final mark. Board 2 remains a credible alternative; board 3 was rejected, not blended into the selected film.

## Type trials and decision

`type-comparison.png` is a same-copy, same-panel comparison of Fraunces + Inter, Playfair Display + Inter, and an Inter-only system. The actual font binaries, version strings, upstream URLs, OFL texts and file hashes are in `source-rights.md`.

- **Fraunces**: variable display, with optical size set near the rendered size and weight in the 540–620 range; mixed case rather than a block of all-caps. Optical sizing lets the large type feel drawn without a fragile hairline. In the 1:2 display sample it holds a clear silhouette and the intended two-line phrase.
- **Playfair Display**: variable `wght` 520–600. The same phrase is refined and legible; its finer high-contrast strokes read cooler and feel less connected to the moving filament at reduced scale. Retained as a true comparison, not a presumed reference-font match.
- **Inter**: 4.000 static Regular/Medium/SemiBold/Bold. Medium for secondary copy and labels; SemiBold for selected emphasis. It gives a distinct, clean UI voice and readable supporting copy. All-caps Inter is useful for a small tag, but as the sole display voice it feels more institutional and less authored.
- Tested the same copy and line breaks, display weights, label tracking, mixed-case/all-caps contrast, the characters `Aa AV fi Æ — 0123456789`, accent colors on both dark and light fields, and an actual half-size type-window view. No glyph fallback/missing marks were seen in the sample. The selected system keeps display type at about 90–112 px on the 1280×720 working canvas and supporting information at 20–26 px; final 1920 output scales those sizes by 1.5. The smallest labels are non-essential; all story text stays large.
- Chosen pairing: Fraunces for expressive headlines; Inter Regular/Medium/SemiBold for secondary and section copy. It is original art direction, not an asserted match to either reference.

## Storyboard / timed beats

The editable details live in `storyboard.json`; the independent sound cue map is `audio_cues.json`.

| Time | Beat | On-screen idea / visual action |
|---:|---|---|
| 0.0–3.0 | Spark | “A thought” is revealed by a point that draws an underlining filament. “starts with one point.” follows. The hook is a visible action from frame one. |
| 3.0–6.1 | Direction | “Give it a line.” The same warm filament makes a direction-changing curve and carries the left-to-right type mask. |
| 6.1–9.2 | Rhythm | “pause / pulse / repeat” arrive one-by-one on a single fine baseline; a traveling point lands on each word, then joins the beats. |
| 9.2–12.5 | Form | The baseline folds into an asymmetric open frame. In the same position a seam wipes “A thought” into “A world”; the warm material shifts to paper/cool light. |
| 12.5–16.5 | Opening | The frame opens out past the type. “Make room. / for the unexpected.” settles into a generous paper field; the line continues as an underline. |
| 16.5–20.5 | Meaning | Paper recedes to ink. “Meaning, / in motion.” aligns; the filament reaches the sentence’s punctuation. |
| 20.5–23.4 | Signature | That filament draws a custom three-stroke K; the KINETIC wordmark locks beside it. |
| 23.4–27.0 | End hold | “KINETIC / Ideas, in motion.” holds with a small living light phase; the last frame is a deliberate brand lock-up, not a black tail. |

The loop is separate: a 10.24-second periodic field with the line and light orbiting in a shared 10.24s phase; wordmark and phrase remain static and readable. The duration is deliberate: 256 picture frames at 25fps and 491,520 PCM samples at 48kHz land on 480 complete 1,024-sample AAC frames, so picture, oscillator and AAC packet boundaries coincide. Visual velocity and audio phase are checked at the wrap, not assumed from the timeline.

## Sound decision

No narration. The words themselves carry the story; TTS would add a second voice and weaken the line-to-type idea. Use an original low-volume chord bed, sparse soft plucks, a short airy synthetic whoosh on selected transitions, and minimal warm/cool tone accents. The sound cue map is timecode-driven, procedural and sample-free; this is authored sound design, not the soundtrack from either reference.
