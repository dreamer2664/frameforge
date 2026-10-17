# Spatial concept study — lithos / KINETIC hero + loop

Private design record for `lithos` (card `t-20261017-32df`), written before the
camera is locked. Companion to `baseline-study.md` (what r03 is missing).

## 0. The brief these concepts must answer

- Real space: near/mid/far planes, perspective, **occlusion**, a camera that
  **reveals information**; never a flat-card parallax.
- Typography as a designed physical object: extruded, beveled, correct
  spelling/advances, readable at real size, **used as architecture**.
- One coherent material/light world; restrained glow; controlled DOF;
  purposeful motion blur; **no generic AI-neon**.
- ≥3 meaningfully different spatial moments + one memorable reveal; a
  first-second hook; an intentional final image.
- Original composed score, derived from the picture's geometry.
- Genuinely new in the film line: not Kinetic r03 (planar), not parallax's
  "Hall and the Gate" (cold stone interior, letters hinging out of a wall,
  letter-gate fly-through). Not a re-run of parallax's rejected concepts
  either (white aperture corridor; quarry letter-blocks).

## 1. Three materially different spatial concepts

### Concept 1 — "THE LONG LIGHT" (open court of standing type; the word as a sundial) — **COMMITTED**

**World.** A high limestone observatory court at low golden sun (elevation
~10°). The seven letters of **KINETIC** stand as monumental extruded stone
(cap 6.5 m, depth 2.6 m) along a shallow arc. One upright **I** is placed as
the gnomon of a semicircular dial inscribed into the floor (a dark basalt arc
inlay with the words *point · line · form · world* at angular stations and
*ideas, in motion.* at the arc's terminus). Near plane: a colonnade of square
piers at the court edge (hard occluders) and a low parapet; mid: the standing
letters; far: a hazed valley and graded sky. One hard sun (warm, shadow-
casting, azimuth sweeps ~25° across the film — a designed sundial compression)
+ cool sky fill + warm floor bounce. All type on screen is **diegetic**
(inscriptions and monuments) — no UI captions, so no caption-framing defects.

**Beats / spatial moments.**
1. *Vault hook (0–3.5 s):* the camera starts **inside the counter of the C**
   — the letter is a vaulted chamber; a blade of sunlight (the letter's own
   aperture shadow edge) sweeps the interior. First-second hook: the blade
   crosses the lens while the C's aperture frames a slice of the sunlit court.
2. *Exit and colonnade (3.5–14 s):* the camera **exits through the C's
   opening** — the reveal that we were inside a letter — and tracks along the
   colonnade; piers sweep the near field and **occlude the standing letters**;
   long shadows rake toward the lens.
3. *The dial (14–24 s):* low lateral track past the letters (letters occlude
   each other and the valley); the gnomon **I's shadow tip sweeps the inscribed
   arc**, crossing *point → line → form → world* — the score's ticks are
   computed from these exact crossings.
4. *Rise / reveal (24–33 s):* crane up and back; the whole dial reads as an
   instrument; the shadow tip lands on *ideas, in motion.* — the sentence
   completes on the floor. The reveal is diegetic: **the word tells time; light
   writes the rest of the sentence.**
5. *Final image (33–42 s):* high golden three-quarter: the standing word, its
   parallel shadows, the dial, warm haze; slow settle and breath.

**Loop (10.0 s, 25 fps).** Sun azimuth = A·sin(2πt/T): the shadows swing along
the dial and return (a metronome made of light); dust drifts with wrapped
phases; a whisper of camera breathing on the same period. Seam closes by
construction; measured afterwards on the encoded file.

**Why this one.**
- Three+ genuinely different spaces (letter-interior vault → colonnade canyon
  with near-field occlusion → open dial court → aerial plan) and a reveal that
  is *information* (the dial reads; the sentence completes).
- Depth is structural: near piers / mid letters / far valley, real occlusion,
  long cast shadows (the classic depth cue), moving shadow edges over static
  relief (the exact fix for parallax's "moving wall" trap — §2.4 of the
  handoff).
- The type is architecture twice over: inhabited (we live inside the C at t=0)
  and monumental (the standing word), plus incised floor type at a third scale.
- Open-air warm world vs parallax's cold interior — the line of films gains a
  second climate instead of a second hall.
- Buildable honestly in the bespoke rasteriser: shadow-mapped directional sun,
  extruded/beveled type, procedural limestone + basalt inlay, fog, DOF, bloom,
  additive sky/sun; every craft claim measurable afterwards.

### Concept 2 — "THE PRESS" (machine interior; the word is printed, then inhabited)

A colossal letterpress interior: bronze gears and a type bed (near gears
occluding mid machinery), lead slugs spelling KINETIC travel to the platen;
the camera goes under the platen at the strike and passes **through the
impression** into a paper world where the ink word stands as a solid on the
sheet. Reveal: the word we were inside is the printed word. Strengths:
mechanical choreography, strong occlusion, a literal transformation.
Rejected for this run: the mechanism demands ~40 articulated parts to avoid
looking like a diagram; "inside a machine" competes with the type for
attention; and the strongest moments (gears, steam) are not about language.

### Concept 3 — "THE APERTURE HOUSE" (camera-obscura; the word is made of light)

A dark rotunda whose dome is pierced by letter-shaped apertures; sunlight
falls through them as seven light volumes, spelling KINETIC in pools on the
floor; the camera rises through one aperture to reveal the building's plan is
the word; final: exterior dusk with the letter-windows glowing. Strengths:
light as typography is the purest "give language a body" inversion; very
restrained. Rejected: the "light finds the letters one by one" ignition beat
repeats parallax's wall-reveal grammar (their taps/light-finding sequence);
without that beat the concept loses its choreography; and a dark interior
again would make the line of films one-note.

### Earlier sketches dropped before full comparison

- *The Tide* — letters rising from a mirror lagoon (reflections, mist layers).
  Dropped: fakeable-but-risky reflections in a software rasteriser; "monoliths
  in haze" too close to parallax's seven-depth monolith field; weaker reveal.
- *The Letter Canyon* — letter-buildings as a city street at human scale.
  Dropped: adjacency to parallax's rejected "typographic city"; urban props
  would dominate the type.

## 2. Committed parameter set

| Item | Value |
|---|---|
| Hero | 42.0 s, 1920×1080, 24 fps, 1008 frames |
| Loop | 10.0 s, 1920×1080, 25 fps, 250 frames, seamless by construction + measured |
| Type | Archivo variable (OFL), true advances, spelled KINETIC, extruded 2.6 m + bevel |
| Dial | basalt arc inlay r≈16–20 m from the gnomon I; stations *point·line·form·world*; terminus *ideas, in motion.* |
| Light | one hard warm sun (azimuth sweep ~25°, elevation ~10°) + cool sky fill + warm bounce + haze; no neon |
| Material | warm limestone (procedural, seeded) + dark basalt inlay + graded sky |
| Camera | ~12 keys, spline-interpolated; starts inside the C counter; exits through its aperture; ends high three-quarter |
| Sound | original synthesised score; ticks derived from measured shadow-tip crossings; air/wind texture; warm chord on the reveal |
| On-screen text | diegetic only (monuments + floor inscriptions); brand KINETIC only |

Nothing in the film names the production identity. This is a new candidate in
`agents/lithos/`, not an edit of Kinetic r03 or parallax r01.
