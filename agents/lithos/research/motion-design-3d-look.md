# Motion-design research addendum — real 3D look (from producer `blender`'s methodology)

**lithos · 2026-10-18 · applies to: any frameforge video deliverable that must look genuinely 3D**

## Why this note exists

The first KINETIC reel (r03) used a hand-rolled 2D perspective stage (PIL quads + fake
mirrors). The human verdict: "it looks like it was made in the 1800s… make them actually
look 3d and not a stop motion video made by a newborn." The fix was not more 2D tricks —
it was adopting the physically based workflow that producer **blender** documents in
`buildinglab` (shifts/2026-10-16-blender.md, design/HANDOFF.md, design/build_blockout.py).

## The recipe that makes renders look 3D (transcribed from blender's pipeline)

1. **Real geometry in a real 3D engine.** Blender-native meshes with believable dimensions
   (metric scale), bevels on every hard edge so edges catch light. Form must survive close
   views: thickness, reveals, gaps, seams.
2. **Physically based materials (Principled BSDF).** Base Color + Roughness + Metallic,
   with proper **sRGB→linear conversion** of hex colors: `((c/255+.055)/1.055)**2.4`.
   Blender's own note: initial renders looked washed-out until palette values were
   converted to linear. Avoid the "one glossy material" shortcut.
3. **Cycles + AgX.** `scene.render.engine='CYCLES'`, `scene.view_settings.view_transform='AgX'`
   (optionally look='AgX - Punchy'). AgX alone converts "CG demo" into "filmic image".
4. **Real lights:** area lights (DISK/RECT, physically sized), a dim SUN for direction,
   and — crucially — **emissive screens that actually light the scene** (screen glow
   spills onto keyboard/desk automatically in Cycles).
5. **Camera craft:** longer lens from further away (product-shot compression), camera near
   subject height, deliberate DOF (`dof.use_dof`, f/4–5.6), small dutch roll.
6. **Headless discipline:** `blender -b --python-exit-code 1 --python script.py` —
   Blender exits 0 even on Python exceptions without `--python-exit-code 1`.
   Debian Blender 4.3.2 (apt): no OpenImageDenoise → denoise in post; 20–32 CPU samples.
7. **Visual inspection law:** a successful render command is not inspection. Open every
   delivered frame at full size, record defects, fix, re-inspect (blender's evidence/
   visual-review.json discipline; matches the human's "you gotta visualize" law).

## Bug ladder actually hit in the reel v2 stage rebuild (record so nobody repeats them)

- `primitive_cube_add(size=1)` spans ±0.5 → `scale = dims/2` halves everything while
  placement math assumes full size → parts "float" apart. Rule: `size=1` cube + `scale=dims`.
- Default startup objects (a 2 m cube at origin!) survive `open_mainfile` on a fresh
  session and swallow the whole scene, blocking lights. Purge `bpy.data.objects` first.
- Portrait render + Blender's AUTO sensor fit puts the 36 mm sensor on the **vertical**
  dimension (1080×1920 → only ≈16.4° horizontal FOV at 70 mm). Frame the camera for that.
- Metallic materials over a black world look black. Real diffuse response + local lights
  (or a brighter albedo) is what makes a dark laptop read.
- Cycles `use_persistent_data` does NOT save per-frame texture reload cost; budget
  ~60–70 s/frame at 1080×1920 / 20 samples / CPU in a 2-core sandbox.

## What stayed 2D (and why)

The laptop **screen content** is 2D motion design rendered to PNGs and mapped onto the
screen's emission texture. That is exactly how real mograph-on-device shots work, and it
keeps the act animation (type, particles, metaballs, UI) fast to iterate. Metaball "clay"
look: gaussian field + threshold + gradient-normal lighting + specular + drop shadow.
Glow: blurred bright-pass composited back. Display type: Archivo Black, per-glyph
advances (`font.getlength`), letter flips as vertical-scale squashes, smears as translucent
ghost copies.

## Audio note (same commission)

The r03 synthesized score was rejected ("fork scratching a blackboard"). The fix was not
louder oscillators but production: layered kick (pitch-swept sine + click), sidechained
sub, claps (staggered noise bursts + filtered tail), dark hats, filtered-saw plucks/pads
with envelopes, risers/impacts on cuts, reverb send, stereo width, tanh bus saturation,
then loudness fit to −16 LUFS / ≤ −1.5 dBTP. Spectrogram review (showspectrumpic) is the
honest stand-in for listening: check that HF noise does not saturate 5–20 kHz and that
rhythmic gaps exist.
