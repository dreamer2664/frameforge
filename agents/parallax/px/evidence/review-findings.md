# Exact-file review — findings

The review was performed on the delivered master (`hero.mp4`, 40.000 s,
1920×1080, 24 fps) and on the delivered loop (`loop.mp4`, 9.600 s, 1920×1080,
25 fps) — the files as published, not the renderer output.

**Method** (see `review-method.md`): a 0.5 s decode grid read frame by frame in
contact sheets, dense 0.1–0.2 s samples around every structural transition, a
640×360 phone check, a full-decode integrity pass, and the loop gate measured
on the encoded MP4. **There was no continuous playback** — the production ran
headless, with no display and no audio device, so nothing here is a claim
about how the film feels in motion or how the score sounds.

## What the review found — the good

* **The wordmark is never wrong.** KINETIC is spelled correctly in every
  frame it appears in (0–12 s on the wall, 19.4–26.4 s as the letter-gate,
  29–40 s on the plinth), with correct advances, real extrusion, visible
  side faces and cast shadows. It is the only type that carries the film and
  it is always readable.
* **No black tail, no missing glyph, no frozen frame.** The last frame of the
  hero is a complete final image (the word on the plinth, the copy beneath
  it); the video and audio both end at exactly 40.000 s (tail mismatch
  0.000 s).
* **Depth and occlusion are real.** The grid shows piers in front of the
  light shaft, letters passing behind and in front of each other, the gate's
  columns framing the warm chamber beyond, and the chamber's piers behind the
  plinth.
* **The light travels.** The raking band on the wall moves from the right
  (the T and I lit at 5.5–7 s) to the left (the K lit at 11 s) exactly as the
  score's seven taps describe.
* **The loop passes every gate**: the wrap's mean frame difference (5.396) is
  inside the interior range (5.373–5.405); the wrap's horizontal motion
  (0.92 px) matches the interior steps (0.88–0.94 px); the wrap's mean
  luminance step (−0.014) is inside the interior range (max 0.062); the source
  audio's seam step is 2.8 × 10⁻⁵ (1 × 10⁻⁴ of the peak) over 460 800
  samples, and the encoded AAC boundary step (0.062) is within the signal's
  own maximum inter-sample step (0.077).

## What the review found — and what was fixed

Two caption-framing defects were found in the 0.5 s grid and fixed in a third
pass (see `revision-3-caption-framing.md`):

1. the opening caption sat outside the frame for its whole life (x = −9.6 m);
2. the release caption was crossed by the swinging N and then ran off the
   right edge of the frame while still at full alpha.

Both were fixed in the storyboard and the affected picture (segments 0–2) was
re-rendered; the corrected master was then re-reviewed with the same method.

## Things a reviewer should know

* **Film grain is deliberate and strong.** The picture carries a 0.018
  amplitude grain, which is why the H.264 master is 428 MB for 40 s
  (≈85 Mbit/s). The grain is what makes the stone read as stone rather than
  as flat card, and it is the reason the master is large; a 960×540 proxy of
  the same edit is published alongside it.
* **One caption is crossed by a letter.** The N swings across the release
  caption between roughly 12.6 s and 13.8 s. After revision 3 the line is
  shorter and it closes at 16.0 s instead of running out of frame, so the
  caption is fully readable from 12.0 s to 12.6 s and again from 13.9 s to
  15.5 s — but the crossing itself remains, and it reads as a depth cue (a
  letter passing in front of the wall) rather than as a legibility failure.
* **The frame at 35.0 s shows a faint aliasing band on the ceiling's far
  edge** where the bright ceiling meets the dark back wall at a grazing
  angle. It is a one-band artefact of the rasteriser, visible only in that
  frame, and it is not corrected.
* **The gate crossing (24.5–26.5 s) is deliberately dark.** The camera passes
  between the gate's columns, the frame is mostly the letter-gate's stone and
  a warm glow beyond, and the word is not in shot. It is the only stretch of
  the film with no subject in it, and it is the transition that earns the
  chamber.
* **No audience testing, no perceptual listening, no continuous playback.**
  The composition was judged from frames; the sound was judged from
  measurements; the film has not been watched by a human.
