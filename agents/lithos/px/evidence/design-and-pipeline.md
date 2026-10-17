# Design and pipeline — lithos / THE LONG LIGHT

## The idea

A golden stone observatory court at low sun. Language stands as architecture:
the seven letters of KINETIC, extruded limestone monuments on a shallow arc.
A taller gnomon **I** keeps a dial inscribed into the floor — *point · line ·
form · world* along its arc, the promise *ideas, in motion.* at its terminus.
The sun is the protagonist's hand: over 42 seconds its azimuth sweeps ~35°,
the shadows of the word rake toward the lens like clock hands, and the shadow's
edge crosses the inscribed words in order. The camera wakes **inside the bite
of a giant stone C** (type as a building), exits through the letter's mouth,
walks a colonnade where piers occlude the monuments, tracks the dial as the
shadow sweeps, then cranes up to reveal the court as an instrument — and the
sentence completes when the shadow lands on the promise.

## Why it is spatial (the craft bar, by construction)

* **Near/mid/far in every wide shot:** piers 2–8 m from the lens (near),
  monuments + gnomon 15–30 m (mid), hills + sky dome beyond (far). Measured
  depth spans: 7–422 m (vault) … 20–1262 m (aerial).
* **Occlusion:** the colonnade walks in front of the monuments; the monuments
  overlap each other at oblique angles; the gnomon crosses the word; measured
  block-shift spread 2.7–4.7 px (planar reference: 1.9).
* **A camera that reveals:** the exit-through-the-letter-mouth (we were inside
  a glyph), the colonnade lateral (parallax), and the crane to plan-view (the
  dial reads as an instrument only from above).
* **Light with direction:** one hard shadow-mapped sun at 17° elevation; long
  cast shadows are the film's co-protagonist; the moving shadow edges crawl
  over **static relief** (floor inscriptions, pier bases, bevelled plinths) —
  the handoff §2.4 trap (moving light on a blank plane reads as a moving wall)
  designed out from the start.
* **Typography as object:** 2.6 m extrusion depth (6.5 m caps = 40–60 px of
  visible side wall at master framing), bevelled, self-shadowing; used as
  architecture twice (the C pavilion at 20 m cap; the gnomon as instrument).

## The pipeline (unchanged engine contract)

```
storyboard.json ──► scene.Film.build(t) ──► meshes + lights + camera
                                             │
                    render3d.render(scene, camera, w, h, jitter) ──► linear HDR
                                             │
              post.finish(linear, depth, frame_index, exposure=3.5·exposure_at(t))
                                             │
                    ffmpeg rawvideo pipe ──► H.264 segment (CRF 16)
```

* `storyboard.json` is the single source of truth: sun keys, camera keys, world
  metrics, dial stations and times, fog, beats, exposure keys, revision log.
* The scene builder is a pure function of `t`; everything is seeded (stone
  texture seed 11, grain seed 1000+frame·7919, score deterministic). Two runs
  of the same storyboard produce the same frames.
* **The score is derived from the picture's geometry:** station tick times are
  the exact shadow-edge crossings computed from the sun keys; the colonnade
  tick is the camera's measured pier crossing (11.053 s); the terminus hit is
  the shadow-tip landing (29.5 s). If the picture is retimed, re-derive.

## Known measured facts of the type

`validate_type.py` PASS (glyphs rebuilt independently via fontTools'
SVGPathPen: outline deviation, polygon area, triangulation area). True
advances from the font's own hmtx; the word layout is computed at runtime.
