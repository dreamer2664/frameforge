# Review 1 - contact-sheet findings and the corrections they caused

Method: spot frames were rendered straight out of the renderer at 1920x1080
(`render.py --times ... --png-dir ...`), read by eye, and the finding was
turned into a change in `flux.src.html`. No frame was judged from a thumbnail
alone and no change was made without re-rendering the affected frame.

## Round A - the first eight spot frames

| t | finding | cause | fix |
|---|---|---|---|
| 1.35 | the chrome word was orange, the extrusion was a black band, the glass slab read as a solid rectangle, the floor bloom was a fire | the metal gradient was warm; 16 stacked opaque copies; the slab's inset shadows drew hard edges; the glow layer was at 0.56 opacity | cool the metal to ivory, blur the copies, drop the slab to 0.11, shrink the bloom |
| 2.80 | the ball left an orange rectangle behind it; the arcs were flat and wide; the core highlight was weak; the dots and diamonds were too big | the trail was a hard-edged gradient block; ARC_W 248 vs ARC_H 252; the core's gradient stopped at 38% | round the trail, narrow the arc, rebuild the core, halve the dot radii |
| 4.20 | a hard vertical seam in the viewport: the scene was 1920 wide and the ball travelled out of it; the channel value collided with the graph; the second keyframe marker was a square | the scene had to be 4000 wide to hold the whole path; the graph started at x=330 under a 300 px channel column | scene/paths to 4000 wide, the graph to x=392 w=770, the marker to a diamond |
| 8.20 | the dolly was too shallow and the orange card sat too high; the cream was grey | the camera had no vertical travel; the cream plate was 6% under the reference's value | add `panY` 150 -> 0, start the zoom at 2.05, lift the plate to #E8E4DB |
| 10.80 | the odometer was unreadable: the digit strips overlapped and showed "0011"; the ghost numerals were full strength | `STRIP_H 200` was shorter than the 300 px glyph, and the CSS gave `.strip` a fixed 180x2000 box that **scaled the canvas**; the ghost's opacity was 0.9 | `STRIP_H 232`, `DIGIT_W 192`, one slot tall, no CSS box, the ghost at 0.13 |
| 12.20 | the wordmark's last two letters overlapped | the CSS `letter-spacing:-.035em` was applied *and* the letters were placed by measured advance | letter-spacing 0, the advance does the tracking |

## Round B - after the first 900-frame render

The full render exposed one defect that no spot frame had caught:

* **The film never faded to black.** The luma timeline was flat at 189 from
  12.5 s to the end, and the last frames were cream instead of black.
  Cause: `smooth(T.fade, T.fade+1.25)` was called **without the time
  argument**, so `x` was `undefined`, the easing returned `NaN`, and
  `style.opacity = "NaN"` is an invalid value the browser silently discards -
  the element kept its previous opacity. Two calls were affected (the plate
  fade and the wordmark fade). Fix: pass `t`. Symptom -> cause -> fix is
  recorded here because the failure mode is silent: a bad value is ignored,
  not reported.
* **The ball was off screen during the morph.** The ball's position is a
  function of time, and by 5.46 s it had travelled to x=2510 - past the
  right edge - so the squash beat played out of frame. Fix: the morph beat
  uses its own in-frame base position (1210 + 320 px of travel).
* The path and its diamonds were still drawn during the morph beat; they now
  fade out with the squash.

## Round C - the second spot pass

* The studio floor pool was still a fire: glow opacity 0.16+0.09, 1280x600.
* The extrusion still read as a hard shadow under the letters: 16 stacked
  copies with a dark gradient. Now 10 copies, a light gradient
  (#DEDAD1 -> #86837B), a 3 px blur and 1.7 px spacing.
* The glass slab's inset bottom edge drew a hard line: removed.
* The turbine's core was a fuzzy smudge: rebuilt as a defined sphere with a
  halo, a hot spot and a solid terminator.
* The board's orange card carried a 27 px label where the reference carries a
  10 px one: reduced to 12 px mono / 21 px bold.
* The graph label now flips to "ease-out cubic" as soon as the curve starts
  to ease (threshold 0.12) instead of at the half-way point.
* The wordmark's letters now arrive with 34 px of blur and a 75 ms stagger.
