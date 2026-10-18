# cadence - concept, copy and build

## The idea

A motion-system reel in the visual language of a browser-based animation tool.
The subject is **cadence**: a timing system, named for the thing that decides
*when*. Everything in the film is about time - a ball that obeys gravity, a
graph of an easing curve, a frame counter that rolls, a wordmark that lands on
the beat.

The conceit that makes the film honest: the end card claims **"900 frames."**
and **"One file, no timeline."** Both are true of this film. The film is 900
frames at 60 fps (15.000 s), and the delivered artefact is a single
self-contained HTML file - no build step, no timeline editor, no sidecar. The
stat card is not decoration; it is a receipt.

## Identity (all of it mine)

| element | choice |
|---|---|
| system name / wordmark | **cadence** (lowercase grotesk, leading letter in accent orange) |
| hero word in chrome | **CADENCE** (Archivo Black, cut to wght 900 / wdth 88) |
| app window | `cadence.html` |
| captions | "Stretch & squash." / "Timing." / "Melt." |
| board primitives | Motion type / Bounce / Volume / Ribbon / Count / Route |
| stat card | **900** (last digit orange) + "frames." + "One file, no timeline." |
| palette | backdrop #a09b93 -> #63615c, floor bloom #a75d31, accent #fb6a34, hot #ff841a, cream #e8e3da, panel #1b1b19, ink #2f2f36 |
| type | Archivo (variable, pinned for the display cut), Inter (variable), IBM Plex Mono (UI) - all OFL |

The reference's chrome word, its creator's name, its caption wording, its file
name, its primitive labels and its music are **not** used.

## The build

```
tq/
  flux.src.html    the film: one page, every frame computed by FLUX.seek(t)
  make_assets.py   subsets the fonts, paints the plates, splices base64 in
  render.py        drives Chromium frame by frame, pipes PNG into ffmpeg
  score.py         the original score (numpy synthesis)
  qc.py            mux, measure, contact sheets
  build/flux.html  the delivered single file (1.19 MB, self-contained)
```

* **Motion is a pure function of time.** `FLUX.seek(t)` recomputes every
  element's transform, opacity and filter from `t` alone. There is no
  animation timeline, no CSS keyframes, no physics that has to be stepped -
  which is what makes "no timeline" true rather than a slogan.
* **Static art is pre-rendered.** The chrome letters, the turbine disc and the
  odometer digits are painted once into canvases at load time; per frame the
  film only moves things. That is why a 1920x1080 frame costs ~0.5 s in
  headless Chromium and not 5 s.
* **The plates are generated, not photographed.** `make_assets.py` paints the
  studio backdrop (gradient + key light + defocused bands + warm floor bounce +
  grain) and the cream board (paper + a huge soft rounded card + shadow) with
  numpy, so the film carries no third-party imagery at all.
* **The ball and the path are the same function.** `ballState(t)` returns the
  position; the dotted spline and the orange keyframe diamonds are drawn from
  the same contact table, so the path is always exactly where the ball went.
* **The editor is honest.** The titlebar reads the real frame counter of this
  render; at t = 3.700 s it reads `t 3.700 s - frame 222 / 900 - 60 fps`,
  which is the true state of the film at that instant.

## The score

`score.py` synthesises 15.000 s of original bed at 48 kHz: a 120 BPM pulse
(0.5 s per beat - the same grid the edit is cut on), a filtered bass line in
A-A-F-G, noise ticks, a sub drone, a warm five-voice pad under the light
section, a bell on the wordmark, a noise riser into the orange flash and
impacts placed on the picture events. It is limited and normalised to
-16.0 LUFS / -1.5 dBTP. No sample of the reference's audio is used.
