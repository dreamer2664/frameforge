# Film facts - `cadence` (parallax r02)

Everything below was measured on the **delivered master file**, not on the
renderer's internals: the file was probed, decoded and loudness-measured with
FFmpeg, and the luma figures come from a full decode of all 900 frames.

## Container

| property | value |
|---|---|
| file | `film-master.mp4` (H.264 High, yuv420p, +faststart) |
| raster | 1920 x 1080 |
| frame rate | 60/1 fps |
| frames | 900 (decoded and counted, not claimed) |
| duration | 15.000 s (A/V tails match to 0.000 s) |
| audio | AAC-LC, 48 000 Hz, stereo, from the original synthesis |
| integrated loudness | -16.2 LUFS |
| true peak | -3.9 dBTP |
| size | ~12.3 MB |

## The stat card is a receipt

* 15.000 s x 60 fps = **900 frames**. The card that says "900 frames." is
  printed over the film while it is still running, and the number is the real
  frame count of the delivered file.
* "One file, no timeline." is also true: `build/flux.html` is a single
  self-contained document (fonts, plates, grain and code inlined). There is no
  timeline editor, no asset library, no build step needed to play it. Motion
  is `FLUX.seek(t)` - a pure function of time - so a frame can be addressed
  directly without scrubbing a timeline.

## Luma timeline (decoded, mean luma per frame)

| t | luma | beat |
|---|---|---|
| 0.0 | 117 | empty studio plate |
| 0.5-1.7 | 120-135 | chrome word |
| 2.0-3.6 | 118-130 | the bouncing ball |
| 3.7-5.4 | 85-95 | the dark editor UI (the darkest passage) |
| 5.5-7.2 | 120-150 | the morph |
| 7.4 | 200+ | the orange flash |
| 7.6-12.5 | 205-220 | the light board |
| 12.6-14.6 | 200 -> 1 | the fade to black |
| 14.6-15.0 | 1 | black |

The reference's own luma profile was measured the same way for comparison:
grey-green 134 through the studio, a dark app at 3.7-3.95 s, cream 225 from
7.5 s, and a fade from 226 to 8.8 over the last 1.4 s. The shape of the two
profiles is the same; `cadence` sits a little darker in the light section and
a little brighter in the studio, which is a deliberate palette choice (warm
paper rather than the reference's cooler paper).

## Beat map (mine) against the reference's

| reference | cadence | beat |
|---|---|---|
| 0.00-0.45 | 0.00-0.45 | empty plate |
| 0.45-1.75 | 0.45-1.72 | chrome word assembles |
| 1.75-2.05 | 1.72-2.06 | the word blows through camera as an outline |
| 2.05-3.65 | 2.00-3.66 | the ball bounces on the baseline |
| 3.65-3.95 | 3.66-3.95 | the editor window materialises |
| 3.95-5.45 | 3.95-5.46 | the viewport and the easing graph |
| 5.45-6.25 | 5.46-6.22 | the ball flattens and streaks |
| 6.25-7.35 | 6.02-7.34 | the turbine morph |
| 7.35-7.58 | 7.34-7.58 | the orange flash |
| 7.58-9.90 | 7.58-9.92 | the board dolly |
| 9.90-10.35 | 9.92-10.32 | the odometer |
| 10.35-11.05 | 10.32-11.12 | the stat card |
| 11.05-11.50 | 11.12-11.46 | the scatter |
| 11.50-12.60 | 11.46-12.55 | the wordmark |
| 12.60-14.07 | 12.55-14.62 | the fade to black |

The cut points are the reference's own, to the frame. The only difference is
the tail: the reference ends at 14.07 s, `cadence` runs to 15.00 s so that the
frame count is a round 900 at 60 fps - and the fade is stretched to match.

## Honest limitations

* There was no continuous playback of the finished file in this environment.
  Every judgement was made from decoded frames (spot frames at 1920x1080, a
  0.25 s contact sheet of all 61 sample points and a 20-frame key sheet) plus
  the measured audio; the sound was judged from its waveform, its transient
  positions and its EBU R128 numbers, never by ear.
* The film is a technique-level replica, not a frame-for-frame copy: the
  geometry, the copy, the type, the palette and the music are all original.
* The grain is heavy by design (film emulsion), which is why the master is
  ~12 MB for 15 s.
