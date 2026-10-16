# Exact-file review — method and honesty statement

## What was reviewed

The review was performed on the **delivered files** — `hero.mp4` and `loop.mp4`
as they are published (the bytes whose SHA-256 appears in the publication
receipt) — not on intermediate renders and not on a proxy.

## Method

1. **Technical measurement** (`qc.py`, `ops/media_qc.py`): container, codec,
   pixel format, picture size, frame rate, audio codec / sample rate /
   bitrate, integrated loudness (EBU R128, `ebur128`), true peak, faststart
   atom order, audio/picture tail mismatch, and a full decode of every frame
   with `-xerror`.
2. **Frame grid at ≤ 0.5 s**: every frame of the hero is decoded at 0.5 s
   intervals (81 frames for a 40.0 s film) and saved at full 1920×1080.
3. **Dense samples**: around each structural transition (the reveal, the
   release, the gate crossing, the landing) frames are sampled every 0.05 s
   across a ±0.15 s window, i.e. at 0.1–0.2 s density, to catch anything the
   0.5 s grid would step over.
4. **Contact sheets**: the grid is reviewed in sheets of 20 frames
   (`work/review/sheet-*.png`) — opened and read frame by frame — and the
   phone check (640×360) is reviewed as a separate sheet.
5. **Loop gate on the encoded file**: first/last frame geometry, the
   position/velocity continuity across the wrap, the light-phase continuity
   (mean luminance) and the audio seam, all measured on the published MP4.

## What was *not* possible — stated plainly

* **There was no continuous playback.** This production ran in a headless
  container with no display, no audio device and no human listener. The film
  was therefore reviewed as decoded frames and as measured audio data, never
  as a moving image with sound. Every statement below about the film is
  backed either by a decoded frame or by a measurement; no claim is made
  about how the film *feels* in motion, and no claim of "listening" is made.
* **The audio was judged by measurement, not by ear**: integrated loudness,
  true peak, the loop seam step, the sync points of every musical event
  against the picture, and the spectral placement of the score were checked
  numerically. The composition's musical quality is a creative judgement, not
  a measured fact.
* **Motion blur, depth of field and the perceived smoothness of the camera
  move were inferred from the rendered frames and from the subframe settings
  used to produce them**, not from watching the film move.

## The honest limitation of this method

A 0.5 s grid plus 0.1–0.2 s dense sampling can catch composition, exposure,
type, black tails, missing glyphs, cut problems and obvious motion errors. It
cannot certify that a 1-frame flicker or a single-frame artefact never occurs
between two sampled frames. Where the film's own motion is fast (the gate
crossing, 19.4–26.4 s) the dense sampling was tightened, and the segment
boundaries (0, 8, 16, 24, 32, 40 s — the points where the render was joined
from separate encodes) were checked explicitly.

*(The per-frame findings of the review are recorded in the handover event
stream and in `technical.json`; the contact sheets are published with the
release.)*
