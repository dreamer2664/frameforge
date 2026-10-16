# Revision 3 — delivery QC: caption framing

This is not a creative revision; it is what the exact-file review of the
delivered master found, and it is recorded as a third pass because the fix
required re-rendering picture.

## How it was found

The final 1920×1080 master was decoded on a 0.5 s grid (80 frames) and read
frame by frame (`work/review/sheet-00.png` … `sheet-03.png`). Two caption
defects were visible in the grid that had not been visible in the 1280×720
previews used for revisions 1 and 2, because the previews were sampled at
different moments.

## Defect 1 — the opening caption never made it into the frame

* **Symptom.** "A word is a heavy thing." (1.68–4.73 s) was cut off by the
  left edge of the frame for its entire life. The grid at t = 1.5 s shows
  only "…d is a heavy thing."; at t = 2.0–3.0 s only the tail of the line is
  inside the frame.
* **Cause.** The caption quad sat at **x = −9.6 m**, but the camera in that
  beat is on the carved word: the eye moves from (0.0, 1.70, 22.0) to
  (2.2, 1.72, 13.8) while the target stays at x = 1.2…3.2, so the frame's
  left edge never reaches x = −9.6 m. The caption was simply outside the
  shot for 3.05 s.
* **Fix.** The caption was moved to **x = 4.0 m, y = 3.75 m** — the same wall
  position the other wall captions use, directly above the carved word and
  inside the frame for the whole line (the frame spans x ≈ [−6.2, 7.8] at
  1.68 s and [−3.3, 7.9] at 4.73 s; the caption spans x = [1.7, 6.3]).

## Defect 2 — the release caption ran out of the frame

* **Symptom.** "And the stone lets go." (13.76–19.60 s) was crossed by the N
  as it swung out of the wall (≈13.5–15.0 s) and then, from ≈16 s, it ran off
  the right-hand edge of the frame while still at full alpha: at t = 18.5 s
  only the word "And" is still on screen, and at t = 19.5 s the line has left
  the frame entirely.
* **Cause.** The camera swings right and then forward from 16.3 s, and the
  caption is painted on the rear wall, so the camera leaves the caption
  behind while the caption's time window is still open.
* **Fix.** The line was shortened to **"The stone lets go."** (width 4.4 → 3.8
  m, so the swinging N no longer crosses it) and its window was closed at
  **16.0 s** — before the camera can leave it. It is now on screen, fully
  inside the frame, from 13.76 s to 16.0 s.

## What did not change

* The camera, the lights, the materials, the choreography, the type and the
  whole 16–40 s section are untouched: the re-rendered segments 0–2 differ
  from the previous ones only in the pixels of the two caption quads.
* The score is unchanged — the captions are not keyed to the music.
* Segments 3 and 4 (24–40 s) were not re-rendered at all, and the loop was
  not re-rendered (it carries no captions).

## Evidence

* Before: `work/review/sheet-00.png` (copy 1 cut off at the left edge) and
  `work/review/sheet-01.png` (copy 3 crossed by the N and leaving the frame).
* After: the same two sheets regenerated from the corrected master.
* The pre-fix storyboard is preserved as `work/rev3-storyboard-before.json`,
  and the pre-fix segments as `work/renders/hero-seg-{0,1,2}.prev.mp4`.
* The change is scripted and recorded in `storyboard.json` under
  `revision_log.revision_3_delivery_qc`.
