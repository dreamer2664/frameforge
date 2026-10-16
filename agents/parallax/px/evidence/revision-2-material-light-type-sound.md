# Revision 2 — material, light, type readability and sound sync

Four defects were found by inspecting the revised frames of revision 1. Each
one is a craft-bar failure, and each one is fixed with a measurable change.

---

## 2.1 The carved wall was a black void

**Symptom.** In the pre-revision frames the word floated on pure black: the
letters were bright, the stone behind them was not there at all
(`work/rev1/before/hero-010.00.png`, `hero-013.00.png`). A word that is
supposed to be *set in stone* was not in any stone.

**Cause.** The wall shared the hall's `stone` albedo (0.048 linear) and was
lit almost edge-on: the key light at t = 9–12 s arrives at
`dir = (0.68…0.80, 0.34…0.32, 0.65…0.50)`, so `N·L` on a wall whose normal is
`(0, 0, 1)` is only 0.50–0.65, and the *whole* wall was inside the shadow
volume of the letters it carried.

**Fix.**
* a dedicated wall material, albedo 0.075 linear (still dark stone, but stone
  rather than void), with the texture tiled at 2 m instead of 6 m so the grain
  is not magnified into sandpaper;
* a grazing "rake" light (`dir = (0.94, 0.15, 0.30)`, intensity 0.45) that
  gives the wall a value gradient along its length and lets the letters throw
  long shadows across it;
* a **travelling band of light** on the wall plane (`scene.py`,
  `band_texture()`): a 6.4 m warm band that follows the same light that finds
  the letters, so the wall is lit where the light is and dark where it has
  not arrived yet. The band is additive and dim (alpha ≤ 0.115), so the
  letters' shadows survive it.

**Result.** The word is now set into a lit stone wall with a visible value
gradient (`work/rev2/after2/hero-013.00.png`).

---

## 2.2 The chamber behind the arch was a flat cream card

**Symptom.** Whenever the camera looked through the arch — at t = 20, 25 and
28 s in the pre-revision cut, and in the final beat — the frame was filled by
one bright, evenly lit rectangle. That is the exact "flat card" failure the
brief calls out.

**Cause.** The chamber was a single 28 × 12 m quad at z = −30 with a uniform
emissive, plus an additive glow panel of the same size in front of it.

**Fix.** The chamber is now a room:
* back wall at z = −34 with a **graded** texture (a vertical falloff: warm at
  the floor, dark at the ceiling) so the space recedes into darkness;
* side walls at x = ±20 and a ceiling at y = 13;
* a floor at y = 0.01 that catches the warm practical;
* the additive glow reduced to alpha 0.26 and re-shaped into a vertical
  gradient;
* two piers at x = ±9.6, z = −20, so the final image has a middle plane
  between the word and the back wall;
* the practical over the chamber dimmed and delayed to match the new timing.

**Result.** `work/rev2/after3/hero-039.00.png`: the word stands on a plinth in
a warm, graded room with two piers behind it and the ceiling fading to black.

---

## 2.3 Surfaces were smeared: the plinth looked like varnished wood

**Symptom.** The plinth in the final beat showed long horizontal streaks — a
13.4 m stone block with one texture tile stretched across it.

**Cause.** `box_mesh()` gave every face UVs of 0…1, so a texture tile was
stretched over the whole face: 13.4 m wide, 1.2 m tall.

**Fix.** `box_mesh()` now derives UVs from world coordinates in metres, per
face, choosing the two axes that are not the face normal. One tile is always
the same physical size on every face of every box (piers, bench, plinth).

---

## 2.4 Copy written on stone was unreadable when the lens was on it

**Symptom.** At t = 28 s in the pre-revision cut the line "Weight becomes
motion." was a huge white smear across the frame, clipped at both edges.

**Cause.** The copy is a quad on the wall (or the arch) with a fixed physical
width; when the camera flew within two metres of it, the line filled the
frame.

**Fix.** Copy fades out as the lens approaches: below 4.2 m the alpha ramps to
zero, reaching zero at 2.4 m. Copy is now only ever read at a distance that
makes it copy.

---

## 2.5 The score was not synchronised to the picture

**Symptom.** The seven dry taps in movement 2 were evenly spaced guesses
(6.00, 6.85, 7.70, 8.55, 9.40, 10.25, 11.10 s) and did not coincide with the
moment the raking light reached each letter. The hinges were hard-coded to
15.0 s and the gate cluster to 22.0 s, so revision 1 moved the picture and
left the music behind.

**Fix.** The score now derives its sync points from the storyboard, and the
taps are computed from the actual reveal geometry — the light enters at
x = +11.5 m at t = 4.2 s and travels to x = −5.0 m at t = 11.3 s; a letter is
fully lit when the light has passed 2.6 m in front of it:

| letter | x (m) | fully lit at (s) | tap | pan |
|---|---|---|---|---|
| C | 8.013 | 6.819 | 1 | right |
| I | 7.229 | 7.157 | 2 | right |
| T | 5.214 | 8.024 | 3 | centre-right |
| E | 3.338 | 8.831 | 4 | centre |
| N | 1.170 | 9.764 | 5 | centre-left |
| I | 0.293 | 10.141 | 6 | left |
| K | −1.899 | 11.084 | 7 | left |

The taps are panned with the travelling light, so the sound crosses the
stereo field in the same direction as the light crosses the wall. Every other
musical event (hinges at 12.2 + 0.15 s, the gate cluster at 19.0 s, the gate
taps 19.4–25.6 s, the impact at 26.3 s, the monument chord at 26.0 s, the
monument taps 28.75–33.4 s, the air at 27.2 s) is taken from the re-timed
stages.

**Measured result.** hero −16.00 LUFS / −12.80 dBTP; loop −16.00 LUFS /
−14.20 dBTP; loop seam step 0.00003 against a peak of 0.196 (sample-exact,
before the AAC encode).

---

## 2.6 A note on the type

The letterforms themselves were re-checked rather than changed: Archivo
variable at weight 700 with the font's own advances, so the word is spelled
K-I-N-E-T-I-C with correct spacing and the correct `C` aperture. The
extruded-and-beveled solid was validated against an independent path built
with fontTools' SVGPathPen (`validate_type.py`, 12/12 glyphs PASS). The
only type-adjacent change in this revision is the texture scale on the letter
solids (0.0016 → 1.2 per metre), which removed a magnified-noise speckle that
made the stone look like sandpaper.
