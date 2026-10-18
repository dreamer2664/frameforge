# cadence - a 1:1 replica of a motion-design reel, rebuilt from scratch

`cadence` is the second film by **parallax** in the frameforge project. It is a
15.000 s / 900-frame / 1920x1080 / 60 fps reel built to match a third-party
TikTok reference in look, technique and pacing - and to share none of its
content.

* Reference studied (private, never redistributed): `vm.tiktok.com/ZN8S7WKHd`
  (`@neildegracce/video/7696876445888466198`).
* What is mine: the word, the copy, the layout, the geometry, the palette, the
  typefaces, the primitives, the score, the identity (`cadence`).
* What is shared with the reference: the *craft* - extruded type under a glass
  slab, a physics ball with a dotted keyframed path, a motion editor with a
  live readout and an easing graph, a morph, a full-colour flash, a light
  board of UI primitives dollied in perspective, a rolling frame counter, a
  wordmark that assembles out of blur.

## Run it

```bash
python3 make_assets.py                 # fonts -> woff2, plates, grain, build/flux.html
python3 render.py                      # 900 frames -> work/render/film-silent.mp4
python3 score.py                       # work/audio/score.wav
python3 qc.py --film work/render/film-silent.mp4 --score work/audio/score.wav \
              --master work/render/film-master.mp4 --sheets work/review
```

`build/flux.html` is the film itself: open it in any browser and press play -
it is one file, with the fonts, the plates and the grain inside it.

## Evidence

* `evidence/reference-analysis.md` - what was measured off the reference and
  what must not be reused.
* `evidence/design-and-build.md` - the concept, the identity, the copy, the
  build system, the score.
* `evidence/review-1-corrections.md` - what the first contact-sheet review
  found and what was changed.
* `evidence/film-facts.md` - the measured facts of the delivered master.
