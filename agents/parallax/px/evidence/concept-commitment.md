# Spatial concept study — parallax / KINETIC hero + loop

Private design record (not published as a separate asset; archived with this agent's evidence).
Written during production, before the final camera move and type treatment were locked.

## 1. What the baseline r03 actually is (measured, not assumed)

Decoded frames of the published r03 hero (SHA `99dc27911b3e…`, 27.000 s) and loop
(SHA `1d2642a5…`, 10.240 s) were extracted and inspected frame by frame.

* The entire film is **planar**: ink-on-cream 2D typography, chapter labels, rules, plates.
* There is **no camera**. Nothing changes size, parallax, or occlusion; the "spatial"
  language is produced by scaling and sliding flat cards.
* The type is a **picture of type**, not an object: it never occupies a surface, casts
  a shadow, or moves in a way that implies mass.
* The arc is point → line → word → frame, and the last ~3.6 s are a static end card.
* Colour: ink black + amber accent + cream paper, all high-key and flat.

Conclusion: the craft bar (genuine depth, near/mid/far planes, occlusion, a camera
that reveals) is **not** met by the baseline, and a 2D solution would fail it too.
The successor therefore has to be a **constructed 3D space**, not a 2D motion system.

## 2. Three materially different spatial concepts considered

### Concept A — "The Aperture" (rejected)
A single monumental slit in a white museum wall; the camera dollies straight in,
the slit opens into a deep corridor of identical columns, and the word is cut out of
the far end. Strength: one strong idea, very clean. Rejected: the corridor of
identical columns has no *meaning* to reveal, the type would be a flat cut-out at the
end, and the white-on-white key gives no place for a warm/cool material contrast —
it risks looking like a generic architectural render.

### Concept B — "The Quarry" (rejected)
A wide open-pit mine at dusk; the letters are carved blocks of stone that the
camera orbits at scale; dust, long shadows, a low sun. Strength: real scale and
texture, a naturally warm/cool split. Rejected: an open pit reads *open air*, and
the brief's material/light world (cold stone, one hard source) was better served by
interior space; also the letter-blocks in daylight risk looking like a product shot
rather than a designed sequence.

### Concept C — "The Hall and the Gate" (COMMITTED)
A dark stone hall, lit by one raking slot of daylight. The carved word **KINETIC**
stands carved into a rear wall; the letters hinge outward and stand up, one after
another, as if the wall releases them; they rotate into the depth of the hall and
align into a monumental **letter-gate**. The camera accelerates through the gate and
emerges on the other side into a warm chamber where the word has re-formed, upright
and lit, resting on a stone plinth. Haze, amber key against cool fill, no neon.

Why this one:

* It gives **three meaningfully different spatial moments** (carved wall → field of
  monoliths → monumental gate → warm chamber), each with its own camera language:
  a slow push, a lateral reveal, a fast fly-through, a settling arc.
* The reveal is **diegetic**: the gate is literally made of the letters of the word,
  so the information revealed (the word becoming an object, then an architecture)
  is the information of the film.
* It supports **purposeful near/mid/far planes** (piers in the near field, the
  monolith field in the mid, the slot light and the wall in the far), real
  **occlusion** (letters pass behind piers and in front of the haze), and a
  perspective that reads as depth rather than as a scaled card.
* The warm/cool material story (cold grey stone → warm amber chamber) gives a
  designed light arc and a memorable final image (the word standing in warm light).
* It is buildable honestly in a bespoke rasteriser: carved depth, hinged letters,
  shadow-casting monoliths, volumetric haze, and a slot light are all within reach,
  and each can be *measured* afterwards.

## 3. Committed parameter set (what the film must deliver)

| Item | Value |
|---|---|
| Hero | 40.0 s, 1920×1080, 24 fps, 960 frames |
| Loop | 9.6 s, 1920×1080, 25 fps, 240 frames, seamless at the sample level |
| Type | Archivo variable (OFL), true advances, spelled KINETIC, extruded and beveled |
| Palette | cold stone (0.048–0.075 linear), warm key 3000 K, cool fill, amber practicals |
| Camera | 13 keys, spline-interpolated, 3 planes minimum in every wide shot |
| Sound | original composed score only (no stock, no copyrighted material, no narration) |

Nothing in the film names the production identity; the on-screen brand stays
**KINETIC**. The candidate is a new film in its own folder and is not an edit of,
or a successor claim on, the delivered r03.
