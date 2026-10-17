# r01 camera post-mortem — "the camera is passing through walls"

User report on the released hero (`frameforge/lithos/r01-56f1fb99211c`):
"i can't even see half the video because the camera is passing through walls."
The r01 review was measurement-only (no playback) and missed it.

## Measured cause (2026-10-17)

Point-to-mesh clearance of the camera eye along the hero path (all 3 980
world triangles, sampled every 0.25 s):

| t (s) | clearance (m) | where |
|---|---|---|
| 0.00 | 1.19 | vault interior |
| 0.75 | 0.53 | vault dolly |
| 1.00 | 0.34 | vault dolly |
| 1.25 | **0.16** | vault dolly |
| 1.50 | **0.03** | vault dolly — INSIDE the C's wall thickness |
| 1.75 | 0.23 | vault exit |
| 2.00 | 0.44 | vault exit |
| 2.25+ | 0.67 → 2.85 | recovered (colonnade holds 2.7–2.85 m) |
| 23.5 | 1.44 | dial beat (closest approach to the gnomon) |
| 26+ | > 5 | rise/aerial (safe) |

**The vault dolly (t ≈ 0.75–2.0 s, worst 0.033 m at t = 1.5 s) clips the
letter-C's inner wall.** With `near = 0.08`, any surface closer than ~0.1 m
engulfs the lens — the wall's interior faces fill the frame = "passing through
walls". Secondary contributor: the exit at t ≈ 3.5–4.25 s passes 0.9 m from
the C's mouth edge (a huge near-plane wipe that can read as a wall pass).

Root cause: camera keys tuned against 0.5 s preview stills, never against a
continuous clearance check; the clip window is 1.25 s long between two sampled
previews.

## Fixes (standing)

1. **`tools/camera_clearance.py`** — eye-to-mesh distance + near-plane
   occupancy along any camera path; gate: min clearance ≥ 0.6 m (and no
   surface within `2 × near` of the eye). Must run before any render.
2. **Camera path visualization** — top-down + side-on path plots with the
   world silhouettes, plus per-frame clearance curve, published to
   `work/review/` alongside contact sheets.
3. **Review discipline**: vision review of dense contact sheets is now
   possible (frame extraction + visual inspection tooling) and mandatory in
   addition to numeric QC. The "measurement-only" limitation of r01 is gone.

The new 2.5D mograph film has no 3D walls to clip, but the same discipline
applies: every camera/layer transform is logged, bounded, and reviewed
visually at 0.1 s granularity before release.
