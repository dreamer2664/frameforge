# LAST SHIFT — WARD 7 · review notes

Every revision below was made because a rendered frame was actually opened and
looked at. Three review passes: one on spot frames during the build, one on the
exact master (every 0.5 s), one on the measured file.

## Pass 1 — spot frames during the build (build/check → build/check9)

**1. The captions rendered as nothing at all.**
Symptom: spot frames showed the graphics but an empty lower third.
Cause: the caption markup nests a `.ln` line wrapper inside `.cap`, and the
style sheet set `opacity:0` on *every* span in the caption block, so the line
wrapper — not the word — was the element that stayed invisible, and the words
inherited its zero.
Fix: the style rule now targets the word class only (`.cap .w`), the line
wrapper is unstyled, and each word carries its own opacity.

**2. The corridor was a white wash for its whole scene.**
Symptom: frames from 44 s onward were near-white.
Cause: the flash rectangle's opacity was computed as `1 - inv(t, flash, flash+0.18)`,
which is 1 for every t *before* the flash, so a 92 %-white overlay covered the
corridor from the moment the scene began.
Fix: the flash is now gated to a window (`t >= flash && t < flash + 0.20`), and
inside that window it holds at 0.95 for two frames and decays to 0.

**3. The lift box on the plan was a solid light-grey rectangle.**
Cause: the fill colour was left at the label colour (`#8b99a4`) when the lift
box was filled, because the text colour was set after the stair box was filled
and the fill colour was never restored.
Fix: the fill colour is set explicitly before each box.

**4. The accent words were white and still carried their `*` marker.**
Cause: the accent marker was detected with `endsWith("*")`, but the word was
`FOOTSTEPS*.` — the marker sits inside the word, not at its end.
Fix: the marker is detected anywhere in the word and stripped, so the accent
applies to the whole word and the marker never reaches the screen.

**5. The plan was half as bright as the reference.**
Measured: mean frame luma 9.6–12.4 against the reference reel's 20.6–26.2.
Fix: a measured lift pass over every surface (page base, panel bases, plan
fills, wall strokes, bed blocks, corridor floor and rings) plus a smaller
vignette; the plan was also scaled up and re-centred so it fills the frame.
Result: mean frame luma 13.3–19.0, in the reference's register while staying
darker at the edges.

**6. The plan clipped its own stair block and the door marks were illegible.**
Cause: the slow push-in scaled about the wrong centre, and the doors were
12×6 px rectangles.
Fix: the plan is scaled about its own centre at 1.07–1.11, the ward was narrowed
so the stair and lift blocks stay inside the frame, and every door is now an
architectural symbol (an opening knocked out of the corridor wall plus a swing
arc), which is also what makes "count the doors" legible.

## Pass 2 — exact-file review of the first full master (every 0.5 s, 140 frames)

**7. The scare flash was one frame long.**
Measured on the master: the frame at 55.30 s jumps to a mean luma of 139.7 and
55.40 s is already back to 77. At 30 fps that is 33 ms of white — below the
threshold where it reads as a hit.
Fix: the flash now holds at 0.95 for two frames and decays over four, and the
master was re-rendered in full (2100 frames, 261 s) and re-measured.

**8. The corridor's red creep arrived too early and too evenly.**
Fix: the creep now starts at 47.6 s and saturates at 56.5 s, so the red arrives
with the footsteps rather than sitting under the trolleys.

## Honest limitations

* The film was reviewed from decoded frames, contact sheets and measured audio
  only. No continuous playback of the master was performed in this sandbox.
* The replica is technique-level, not frame-for-frame: the story, the drawing
  system, the palette, the type and the sound are all original.
* `luma_change_mean` is small (0.157) and 2068 of 2099 frame-to-frame mean
  luma deltas are below 0.5. That is the nature of a dark, static-composition
  film measured on the *whole-frame* mean; the contact sheets in this release
  show the picture and the captions changing continuously throughout.
