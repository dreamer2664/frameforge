# KINETIC MOTION REEL 2026 — production book (v2)

**Producer:** lithos · **Task:** t-20261017-32df · **Replica target:** TikTok
`https://vm.tiktok.com/ZN8StAsTQ/` (motionlovee, 12.79 s portrait 1080×1920, real ~30 fps)

v2 is a ground-up rebuild after the human verdict on r03: *"it's just bad… it looks like it
was made in the 1800s… sound is absolutely horrible… make them actually look 3d."* The
structure/beats of r03 were kept (they matched the reference act-for-act); everything about
how they LOOK and SOUND was rebuilt.

## Pipeline

```
acts2.py      screen content: 384 PNG (1920x1200 @30fps) — 11 designed acts
build_scene.py  Blender stage: laptop+desk+room, PBR, AgX, Cycles -> scene/reel-stage.blend
render_stage.py Cycles CPU loop: per-frame screen texture + camera drift/punch-ins -> work/frames
grade.py      post: shadow-denoise, bloom, vignette, grain, S-contrast -> work/graded
score2.py     157 BPM produced score (sidechain, layered drums, pads, risers) -> work/score2.wav
build2.py     score gain-fit (-16 LUFS) + libx264 crf17 mux + poster + QC
```

Rebuild: `python3 acts2.py && blender -b --python-exit-code 1 --python blender/build_scene.py`
then `blender -b --python-exit-code 1 --python render_stage.py` (~7 h CPU),
`python3 grade.py && python3 score2.py && python3 build2.py`.

## 3D stage (the "actually look 3D" fix)

Follows producer blender's buildinglab methodology (see
`research/motion-design-3d-look.md`): real geometry at metric scale (0.322×0.228 m deck,
0.212 m lid, 102° opening, 70-key keyboard, trackpad), beveled edges, Principled BSDF
(sRGB→linear hex), Cycles + AgX Punchy, area key/fill + dim sun + emissive screen that
lights the room for real, glossy dark desk (real reflections, no fake mirror layer),
70 mm lens at ~1.2 m with −5° dutch roll and DOF f/5.6. Camera drifts (±1 cm) with
punch-ins at act cuts and a push-in on the end card.

Fixed during build (recorded in research note): half-size scale bug (`size=1` cube spans
±0.5), default startup cube swallowing the scene, portrait sensor-fit FOV math, metallic
black-hole materials.

## Screen acts (v2.1 — all watched on contact sheets)

| act | time | design |
|---|---|---|
| 00 THE DOT | 0–1.55 | coral capsule, elastic squash-stretch hops along a ruler, glow trail |
| 01 TYPE | 1.55–4.35 | Archivo Black "motion design", whip-in smears, invert flash 1.95, flipping letters, orange tittles, zoom-through |
| 02 SOLID + SHAPE | 4.35–5.2 | Bauhaus tiles pop with stagger + flips (cream/navy/coral/black) |
| 03 PATTERN | 5.2–5.6 | flowing serpentine ribbons + drifting coral pill |
| 04 SMEAR | 5.6–6.0 | slit-scan comet with vertical ghost stack |
| 05 PARTICLES | 6.0–8.0 | burst → rotating dot sphere → glowing rings → dot terrain → **tight spiral rose** → implode |
| 06 ORGANIC | 8.0–10.0 | shaded clay metaballs (gaussian field + gradient normals + spec + drop shadow), merge, mitosis, bead row |
| 07 DATA + UI | 10.0–11.2 | navy dashboard: rolling KPIs, sparkline w/ marker, staggered bar growth |
| 08 DEFOCUS | 11.2–11.55 | blur + streak ramp-out |
| 09 MONTAGE | 11.55–11.95 | 8 recap flashes + cyan blowout |
| 10 END | 12.0–12.8 | "kinetic." wordmark, caret→period morph, typed "motion, engineered." |

## Copy / brand (unchanged standing rules)

Headline "kinetic thinks in motion." · end "kinetic." + "motion, engineered." · brand
Kinetic with own 12-petal coral starburst (never the Claude mark) · UI vocab generic
(FIG. 01, ELASTIC / SQUASH + STRETCH, 00/THE DOT … 08/END).

## Score v2

157 BPM (reference tempo), F-minor-ish: intro pluck → drop at 1.55 (kick/clap/sub) →
hats at 4.35 → fill/riser at 5.28 → arp at 6.0 → pad lift at 8.0 → busiest at 10.0 →
sweep-down at 11.02 → 4 montage hits → impact + chord tail at 12.0. Sidechained sub,
layered kick (pitch sweep + click), staggered claps, dark hats, filtered saws, reverb
send, bus saturation. Measured (not listened): spectrogram shows rhythmic gaps and no
HF saturation after the noise-budget fix; loudness fit to −16 LUFS / ≤ −1.5 dBTP at mux.

## Review log (honest)

- **r03 (2D stage):** released; user verdict — unpostable. Specific faults accepted as
  true after side-by-side review: far camera/mockup look, watermark-like fake mirror,
  amateur acts (dot-ball "spiral", fried-egg blobs), soft type, dead room, bad audio.
- **v2 stage iterations (each frame opened and looked at):** (1) smoke PBR cube ✓;
  (2) first laptop — lid floated (half-scale bug), crushed blacks → geometry fixed;
  (3) too far/wide → tele product framing; (4) washed silver → dark body mood;
  (5) 18-sample noise accepted with post shadow-denoise plan. Hero frame accepted.
- **v2.1 acts:** sheet 1 — type letter-spacing broken ("moti on"), misplaced tittles,
  flat holds → fixed with per-glyph advances, stem-centered tittles, rolling flips,
  breathe. Sheet 2 — spiral rose spilled arcs off-frame (tightened to 2.15π rose),
  metaballs flat (clay shading rewritten: lambert + spec + drop shadow). Accepted.
- **score v2:** first mix saturated 5–20 kHz broadband (the blackboard problem) —
  hats/claps/reverb noise budget cut, side channel darkened. Spectrogram re-checked:
  structure + gaps OK.
- **v2 full film watch:** see FINAL REVIEW below (filled at delivery).

## Specs

- Video: 1080×1920, 30 fps (reference's real cadence), h264 crf17 yuv420p, 12.8 s
- Audio: AAC 192 k, 44.1 kHz stereo, −16 LUFS / ≤ −1.5 dBTP
- Render: Blender 4.3.2 Cycles CPU, 20 samples + adaptive 0.06, AgX Punchy, no OIDN
  (Debian build) → shadow-denoise in grade.py
