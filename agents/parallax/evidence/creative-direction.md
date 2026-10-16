# parallax — original creative direction (chosen autonomously, no poll)

Date: 2026-10-16Z. Brand on screen: **KINETIC**. Production identity: parallax (never on screen).
Baseline studied: agents/parallax/evidence/baseline-study.md (own decoded-frame observations of r03).

## Three materially different spatial concepts compared (private work products)

### A. "Light gives form" — extruded serif architecture in a dark world, lit by the brand's travelling point  ✔ SELECTED
- World: matte ground plane + Fraunces letterforms extruded into real solids (monoliths, gates, one giant
  passable letter). The KINETIC filament/point is not a drawn stroke here — it is the **moving key light**
  of the world. Letters exist in darkness until the light passes and gives them mass, rim and cast shadow.
- Camera: low dolly over ground, lateral track between monolith rows (occlusion as storytelling),
  push **through the counter of a giant letter** (type opens a passage; the ink→paper palette cut is
  motivated as emerging into lit space on the other side), crane-up reveal, 90° arc around the K monolith.
- Material/light: matte mineral faces, warm amber key + cool glass fill, exponential fog for near/mid/far,
  soft projected ground shadows, restrained glow only on the light itself.
- Why it wins: it is exactly the commission's ask — type as a designed object in space, camera moves that
  reveal information, three+ distinct choreographies (dolly/scale, gate-corridor rhythm, letter-passage,
  arc signature), and it keeps every strand of Kinetic's DNA (point→line→world, two-field palette,
  Fraunces+Inter, draw-on light) while adding the missing dimension. The moving-light idea prevents the
  "stock text extrusion" look: nothing is lit uniformly, silhouettes and shadow sweeps carry the image.
- Risks and mitigations: giant-type monotony → scale contrast (monoliths vs 20-px Inter plates), asymmetry,
  fog layers; readability → every story phrase gets a settled frontal moment at full size; 2-core render
  budget → purpose-built numpy z-buffer rasteriser, no general engine.

### B. "Paper diorama" — 2.5D cut-paper stage, layered planes, tilt-shift drift  ✘
- Warm, tactile, on-palette; cheap to render. But it stays a stack of flat cards with parallax offsets —
  the commission names this exact failure mode. Type never becomes an object; no occlusion logic beyond
  layer order; the camera can only drift. Rejected as the main system (its paper material survives as the
  lit-side world after the passage).

### C. "Ring corridor" — one-point-perspective tunnel of glowing orbit rings, type on cylinder walls  ✘
- Strong velocity and loop-friendly, but reads as generic neon tech-tunnel, fights the restrained palette,
  and curved type fails the readability bar at phone size. Rejected, not blended.

## One-sentence promise

**A single travelling point of light enters a dark architecture of words and, passing through it, gives every
letterform mass, shadow and room — until one word opens as a passage and the light walks through into a lit world.**

## Emotional arc

curiosity (darkness, one igniting light) → awe (true scale: letters as monoliths, shadow sweeps) →
momentum (gliding between forms, gates firing in rhythm) → passage (push through the letter; world inverts
to lit paper) → clarity (crane-up: the monoliths form an open frame around the horizon) → resolution
(arc around the K monolith; light comes to rest; a last slow push-in, not a frozen card).

## Storyboard — hero "DEPTH OF THOUGHT" (~44 s, 1920×1080, 24 fps, editable in storyboard_parallax.json)

| # | Time | Beat | Spatial action / camera | Type in space |
|---|---|---|---|---|
| 1 | 0.0–3.5 | SPARK | Black. Light ignites in deep space; slow dolly in; light passes close left of lens (whoosh) and for 6 frames rakes a giant near letter edge (occlusion hook: something huge is here). | tag plate "01 / SPARK" |
| 2 | 3.5–9.0 | SCALE | Low forward dolly over ground; ahead, extruded "A thought" stands as a monument; light orbits it once, shadow sweeps; faces light progressively. | "A thought" solid, frontal settle 6.8–9.0; plate "starts with one point." |
| 3 | 9.0–15.0 | DIRECTION | Lateral track between two monolith rows; near letters occlude mid ones; filament draws a real 3D curve threading the row, letters ignite in sequence. | "Give it a line." on mid monolith face; plate "A direction is a decision." |
| 4 | 15.0–20.5 | RHYTHM | Camera rises, looks down a corridor of three extruded portal gates; light threads gate 1→2→3; camera pushes through each aperture (frame-within-frame). | gate lintels carry "pause" "pulse" "repeat" |
| 5 | 20.5–27.0 | PASSAGE | Giant "world" ahead; camera pushes into the counter of the 'o'; interior glow builds; at the membrane the field inverts ink→paper; emerge into lit pale-stone world. | "A world" giant; beyond: plate "becomes a place to go." |
| 6 | 27.0–33.0 | ROOM | Crane-up + pull-back reveal: monoliths are arranged as an open rectangular frame around the horizon (Kinetic's drawn quadrilateral, now architecture); cool fill + warm key. | "Make room." two solid words at two depths; plate "for the unexpected." |
| 7 | 33.0–39.0 | MEANING | World dims back to ink as camera settles low/frontal; filament (now warm+cool pair) sweeps an underline in 3D beneath the facing type. | "Meaning, in motion." extruded, frontal, settled |
| 8 | 39.0–44.5 | SIGNATURE | 90° arc around tall K monolith; its three strokes catch light in sequence; wordmark plate ignites; final image: low wide, K + receding letter field, light at rest at its base; 0.5%/s push-in continues to last frame. | K monolith + "KINETIC" plate + "Ideas, in motion." |

## Loop (10.24 s @ 25 fps, same world, seamless by construction)

Slow 360° orbit at fixed radius/height around the K monolith on the ink field; the warm light orbits in
counter-phase at a different radius; ground shadow, rim phase and fog all close on the period; centre plate
"Ideas, in motion." faces the start azimuth. Every oscillator (camera azimuth, light azimuth, glow pulse,
audio LFOs) is an integer multiple of 1/10.24 Hz so encoded video and AAC audio wrap exactly (method
inherited from Kinetic loop-design, rebuilt for this system).

## Sound (procedural, authored; narration: none — the film is a pure motion identity piece)

- Warm drone bed (detuned partials + filtered noise), level/filter track camera speed.
- Air/whoosh swells when the light passes lens or a gate aperture.
- Material ticks (decaying inharmonic partials, stone-on-stone) as letterforms ignite; three chimes on the
  K strokes; soft reverse-swell + low boom at the passage inversion.
- Mix targets: −16 LUFS ±1.5 integrated, ≤ −1 dBTP, AAC 48 k ≥160 kbps; measured on the exact file.

## Type and palette (system, not copies)

- Fraunces (OFL, from Kinetic's licensed set — same binaries, provenance re-recorded in source-rights) for
  extruded display solids; Inter (OFL) for emissive micro-plates and wordmark.
- Ink field #0b0d10→#141821 gradient fog; paper field #efe9df→#d9d2c6; warm key #ffb469/#ff8a3c; cool fill
  #9fc4d8; letter faces matte mineral #cfc7ba (lit side) / #2a2f36 (ink side).
- Glow budget: light core + ≤12 px halo; no bloom stacks, no particles, no neon.
