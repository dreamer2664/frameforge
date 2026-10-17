# reel — KINETIC MOTION REEL 2026 (the motionlovee-reference replica)

**Deliverable:** `out/kinetic-reel.mp4` — 12.8 s · **1080×1920 portrait · 60 fps** · H.264 + AAC 44.1 kHz,
≈ −16 LUFS / ≤ −1.5 dBTP. Also `out/poster.png`.

Replicates `https://vm.tiktok.com/ZN8StAsTQ/` (motionlovee, "Want the skill?") structurally and
technically — with **own copy and own branding** per standing rules (no copied text; branded
KINETIC/lithos; "don't make it obvious"). Full reference anatomy:
`../research/reference-analysis-motionlovee.md`.

## What the film is

A persistent **3D laptop studio shot** (MacBook 3/4 view on a glossy black floor, slow orbit +
push-in, mirror reflection, tilted bold-italic headline + coral 12-petal asterisk overlay and
their reflections). The laptop screen runs a **motion-design showreel** in chaptered acts:

| t | chapter | screen act |
|---|---------|------------|
| 0.00-1.55 | 00 / THE DOT | dotted-grid studio, **elastic ruler** + glowing pill squash&stretch pops with echo streaks (FIG. 01 / SQUASH + STRETCH) |
| 1.55-1.95 | 01 / TYPE | letters whip in with tumble -> "motion" |
| 1.95-2.40 | 01 / TYPE | **white sphere invert flash**, letters flip to dark-on-white |
| 2.40-3.20 | 01 / TYPE | "design" flies in -> two-line lockup, **orange i-tittles** |
| 3.20-3.95 | 01 / TYPE | split-flap letter cycles + push-in |
| 3.95-4.35 | 01 / TYPE | **zoom-through** the tittle -> orange sun floods the screen |
| 4.35-5.20 | 02 / SHAPE | **extruded Bauhaus relief tiles** (circles/diamonds/stripes/triangles) rearranging |
| 5.20-5.60 | 03 / PATTERN | morphing **meander ribbons** + drifting orange dot |
| 5.60-6.00 | 03 / PATTERN | vertical slit-scan smear -> black |
| 6.00-8.00 | 04 / PARTICLE | starburst -> **point-cloud sphere** -> **armillary rings** -> **wave terrain** -> **3-arm spiral galaxy** -> implosion flash |
| 8.00-9.20 | 05 / ORGANIC | **clay blobs** bloom on royal blue -> metaball merge |
| 9.20-10.00 | 05 / ORGANIC | **mitosis** 1->2->4->5 -> dots multiply into a row -> stretch into capsule bars |
| 10.00-11.20 | 06 / DATA | **live dashboard**: rolling KPI odometers, sparkline with the dot at its head, spectrum capsules |
| 11.20-11.55 | 06 / DATA | defocus rack-out |
| 11.55-11.95 | 07 / RECAP | rapid montage flashes on the 16th-note grid |
| 12.00-12.80 | 08 / END | end card: **"kinetic."** + orange caret becomes the period + typed tagline "motion, engineered." |

Copy: headline overlay `kinetic thinks in motion.` · brandline `KINETIC / MOTION REEL 2026` ·
end `kinetic.` / `motion, engineered.` — all original. Technique vocabulary (FIG. 01,
SQUASH + STRETCH, chapter names) kept as UI scheme = industry terms, not creative copy.

## Score (`score.py`)
157 BPM (matches the reference's 16th grid 0.0955 s). Two intro hits (0.08/0.33), atmospheric
pad, then 16th tick/hat + quarter kicks from 2.38 to the end; storyboard accents: invert impact
1.95, riser->flood 3.98, burst 6.00, implode 7.95, dashboard 10.00, montage hits 11.55-11.87,
end-card impact 12.00. Loudnorm gain-fit -> −16 LUFS.

## Architecture (`agents/lithos/reel/`)
- `engine.py` — px-engine port: fonts, text_rgba, quad_project/persp_coeffs, smear, easing. (W,H=1080×1920)
- `stage.py` — the persistent frame: `camera(t)` slow-orbit corners, `laptop_rgba()` (bezel,
  bilinear keyboard), screen `quad_project`, light-spill **under** the content, `mirror_layer()`
  glossy floor, overlay + its frame-flip mirror.
- `acts.py` — one renderer per screen world (elastic ruler, type whip/invert/flip/zoom, relief
  tiles, meander, slit-scan, particles, clay, dashboard, defocus, montage, end card).
- `film.py` — `screen_frame(t)` act routing; `render_frame(t)` -> stage(frame).
- `score.py` / `build.py` — audio; rawvideo->libx264 crf17 mux with AAC + poster.

## Visual review log (user law: visualize what you make — every pass was SEEN)
**V1 (act smoke, 23 frames):** terrain dots catastrophically oversized (projection `f` misused as
dot size — points flew/clogged); squiggles read as boxed arcs not meanders; spiral too small/dim;
pill/type undersized; floor reflection too faint; headline mirror missing.
**V2 (fix sheet):** unified normalized particle projection (`_dots(k=0.011-0.016)`), meander
ribbons, 3-arm spiral, bigger type/pill, stronger reflection, headline mirror = frame-flip
(lands bottom like the reference).
**V3 (full-film sheets, 30 frames):** structure matches the reference act-for-act; found the
**glow-spill layer dimming all screen content ~36%** (composited over the screen) -> moved under
the content. End card verified at 1:1: cream "kinetic." + orange period + typing tagline.

## r01 lesson compliance
The stage is a fixed camera-on-laptop framing with analytic drift — no camera can clip through
geometry. For any future true-3D shot, `../research/tools/camera_clearance.py` remains the gate.

## Reproduce
```
python3 score.py   # -> work/score.wav / score.m4a
python3 build.py   # 768 frames -> out/kinetic-reel.mp4 + out/poster.png
```
Build outputs gitignored; media ships via the storagecode release.
