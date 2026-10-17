# Exact-file review — lithos / KINETIC "The Long Light" hero r01

**Reviewed bytes:** `work/renders/hero-master.mp4` (SHA-256 recorded in
`work/qc/technical.json`; 42.000 s, 1920x1080, 24 fps).

**Honesty statement (required, restated from `review-method.md`):** no
continuous playback is possible for the reviewer of record. The review is
**measurement of the exact delivered frames + published contact sheets
(`work/review/*.png`) for human eyes**. No claim of watching the film is made
or implied. Every statement below carries the measurement behind it.

## Coverage (as specified)

* **every 0.5 s** — 84 full-size 1920x1080 PNG extracts (`work/qc/frames/`),
  measured luma / dark% / hot% / p10 / p90 / warm (`work/review/review-0p5s.json`).
* **dense 0.05 s samples at 11 beat centres** — 77 frames (`work/qc/dense/`).
* **640x360 phone extracts** — 42 frames (`work/qc/phone/`).
* **contact sheets** — `sheet-00..03.png` (every 0.5 s), `sheet-dense.png`,
  `sheet-phone.png`, plus `sheet-loop.png` for the loop edge frames.

## Findings (with numbers)

1. **Value arc is the designed one.** Vault luma 0.34-0.47 (iris-graded, rev 1),
   exit climbs to 0.71, colonnade holds 0.60-0.70 with shadow pools (dark% up to
   10 at t=19), the dial beat sits lower at 0.41-0.55 (dark% 3-9 — the
   shadow-grazing beat), the rise hits the film's darkest values (t=26-27:
   dark% 36/20, luma 0.32/0.42 — the monument silhouette against the sky), then
   the aerial settles at 0.61. Hot% is 0.0 everywhere; warm R>B on 41/43 samples
   (the two exceptions are the sky-dominated silhouette beat, t=26-27 — blue
   skylight in shadow is the palette's mixed-light design).
2. **The first-second hook reads at phone size.** t=0: band p90-p10 = 0.345 at
   640x360 (the C's rim against its dark interior). The half-second around t=1.0
   is the film's flattest moment (p90-p10 = 0.047): the fog-filled letter
   interior mid-push, deliberately dark and quiet before the blade arrives at
   1.5 s (t=2-3 back to 0.21-0.28). Kept as designed.
3. **Main type reads at 640x360.** Monument-band contrast at phone size:
   0.34 (t=10) / 0.44 (t=12) / 0.33 (t=14) / 0.34 (t=16) / 0.39 (t=18) /
   0.56 (t=26) / 0.24 (t=36).
4. **The floor inscriptions behave as the design promised** — relief text that
   flares when the shadow edge crosses. Measured band contrast at the terminus:
   0.055 (t=29.35, before) -> 0.176 (29.40) -> 0.220 (29.45) -> 0.227 (29.50)
   -> 0.290 (29.55) as the shadow lands on "ideas, in motion." Between
   crossings the relief contrast sits at 0.03-0.13 (real carved stone in flat
   light reads the same way). No revision: the measured flare IS the idea.
5. **No pops.** Median 0.05 s luma step is 0.0033. The largest steps are the
   designed shadow-edge sweeps at the dial stations (e.g. 0.619 -> 0.455 across
   20.25-20.30, the 'line' station) and are continuous ramps in the 0.05 s grid,
   not single-frame jumps.
6. **Craft (delivered bytes, 0.5 s grid, n=83 pairs):** planarity residual mean
   0.0895 / max 0.2735 (planar Kinetic r03 reference: 0.0682 / 0.8121), block
   spread 3.28 px mean (ref 1.89), occlusion edges present in 79/83 pairs
   (mean 6.8, ref 5.3). Layered motion above the planar reference throughout.
7. **Depth spans (measured):** colonnade d05-d95 = 28.4 m; rise = 77.2 m;
   aerial = 557 m. Near/mid/far separation holds in every wide.

## Verdict

No further picture revision is required by the review. The two consequential
revision passes of record are **rev 1 (graded iris / vault chiaroscuro)** and
**rev 2 (true loop: retimed 10.240 s, hero-only iris, frozen loop sun colour)** —
both with before/after measurements in `storyboard.json` `revision_log` and in
this folder's `revision-1-vault-iris.md`. The loop seam re-measurement is in
`work/qc/technical.json` `loop_gate`.
