# Revision 1 — whole-cut rhythm

**What was wrong (measured, not guessed).** The first complete pass of the cut
was judged frame by frame at 1280×720 (`work/rev1/before/`, contact sheet
`work/rev1/sheet-before.png`). Three faults showed up:

1. The film spent its first six seconds in a near-empty dark hall before any
   information arrived. The gate — the thing the film is about — did not exist
   until 22.4 s, i.e. past the halfway point of a 40 s film.
2. The action was bunched: the release, the assembly and the flight through the
   gate all happened inside 15.0–29.4 s, and the camera was still accelerating
   at the moment the letters were supposed to have landed.
3. The arrival was short. The monument existed from 29.4 s to 40.0 s but the
   camera was nearly parked from 34.2 s on, so the last six seconds were a
   still frame with a caption rather than an image.

**What changed.** One piecewise-linear time map was applied to *every* timed
element of the storyboard, so picture and score moved together:

| old (s) | new (s) | why |
|---|---|---|
| 0.0 | 0.0 | the hook keeps its first frame |
| 6.0 | 4.2 | the hall is a doorway into the film, not a scene in it |
| 15.0 | 12.2 | the stone lets go 2.8 s earlier |
| 22.4 | 19.4 | the gate forms at 56 % of the film instead of 56 %… but with the action already moving |
| 29.4 | 26.4 | the monument arrives with 13.6 s to live instead of 10.6 s |
| 40.0 | 40.0 | the final image still ends the film |

Resulting beats: hall 0.0–4.2, wall 4.2–12.2, release 12.2–19.4, gate
19.4–26.4, monument 26.4–40.0. Stage times (the letters' own choreography):
release 12.2, field 14.535, assemble 19.4, gate 23.2, fly 26.4, row 29.992.

Because the camera spline is sampled at the new key times, the *speed* of the
camera changes with the cut: the push through the hall is 1.43× faster, the
release is 1.03× faster, and the arrival is 1.29× slower. The gate pass is
consequently a held, readable moment instead of a blur.

**The camera path was also corrected for the same reason.** In the old cut the
approach to the gate ran straight past the right-hand column of letters: the
camera was at x = −1.6 m while the "E" of the gate stood at x = −1.2 m, 3.2 m
away and 2 m tall, so the letter filled the frame as a flat cream shape
(`work/rev1/before/hero-028.00.png`). The camera now converges on the gate's
centre line (x = −4.6 m) before it crosses the plane of the letters:

| t (s) | eye | target |
|---|---|---|
| 20.00 | (−1.0, 1.95, 3.0) | (−2.6, 2.6, −3.4) |
| 23.20 | (−3.8, 1.90, 0.2) | (−4.4, 3.2, −4.2) |
| 26.00 | (−4.6, 1.85, −2.6) | (−4.6, 3.4, −10.0) |
| 28.97 | (−4.6, 1.80, −6.4) | (−4.6, 2.6, −16.0) |

**Before / after.** The pre-revision frames are in `work/rev1/before/`
(t = 2, 6, 10, 13, 17, 21, 25, 28, 31, 35, 39 s, 1280×720) and the
post-revision frames in `work/rev2/after2/` and `work/rev2/after4/`
(t = 4, 8, 10, 13, 17, 21, 25, 28, 31, 35, 39 s, 1280×720), so the same film
times can be compared directly. The before/after pairs that show the rhythm
change most clearly are t = 21 s (before: letters still hinging out of the
wall; after: the field of monoliths is already moving toward the gate) and
t = 31 s (before: the camera is buried in a letter; after: the word has landed
on the plinth and the room opens around it).

**Reproducibility.** The change is a script, not a hand edit:
`tools/revise_storyboard.py` (time map, stage times, gate path) and
`tools/revise_scene.py` / `tools/revise_scene2.py` (material, light, type).
The pre-revision storyboard and scene are preserved as
`work/rev1/storyboard-before.json` and `work/rev1/scene-before.py`, and the
full audit trail of every remapped key is stored inside the storyboard under
`revision_log`.
