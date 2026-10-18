# TEXT_LOG — PRISM / PROOF (env-B)

Generated 2026-10-18T18:58:19Z. Bounding boxes are measured in the renderer's screen-space
orthographic overlay where 1 unit = 1 pixel at 1920x1080, sampled every frame
of every text moment (`text_measures.json`, produced by
`node render.mjs --measure`). Title-safe box = 90% => x in [96,1824],
y in [54,1024]. Minimum cap-height spec = 36 px.

| id | string | in | out | cap px | tightest margins L/R/T/B (px) | inside 90% box | crop |
|---|---|---|---|---|---|---|---|
| T10.body | RECEIPT | 668 | 749 | 56 | 414 / 373 / 296 / 342 | YES | qc_text_T10.body.png |
| T1 | SIGNAL // UNVERIFIED | 8 | 92 | 40 | 72 / 856 / 892 / 38 | YES | qc_text_T1.png |
| T2 | A CLAIM IS NOISE. | 40 | 176 | 96 | 115 / 115 / 438 / 422 | YES | qc_text_T2.png |
| T3 | FRAME 000/750 | 196 | 442 | 44 | 1108 / 72 / 56 / 870 | YES | qc_text_T3.png |
| T4 | dLUMA +38.2%  DRIFT 0.004px | 236 | 372 | 40 | 72 / 730 / 58 / 872 | YES | qc_text_T4.png |
| T5 | MEASURE EVERYTHING. | 330 | 446 | 78 | 58 / 58 / 759 / 119 | YES | qc_text_T5.png |
| T6 | PROOF | 483 | 656 | 255 | 30 / 30 / 263 / 401 | YES | qc_text_T6.png |
| T7 | MEASURED. | 500 | 528 | 64 | 570 / 570 / 614 / 284 | YES | qc_text_T7.png |
| T8 | REPRODUCIBLE. | 530 | 558 | 64 | 459 / 459 / 614 / 284 | YES | qc_text_T8.png |
| T9 | SIGNED. | 560 | 596 | 64 | 659 / 659 / 614 / 284 | YES | qc_text_T9.png |
| T10 | RECEIPT | 668 | 749 | 56 | 414 / 894 / 218 / 696 | YES | qc_text_T10.png |
| T11 | INDEPENDENT ACCEPTANCE PENDING. | 700 | 749 | 44 | 279 / 279 / 886 / 40 | YES | qc_text_T11.png |

All moments inside the 90% title-safe box: YES.
Cap-heights: minimum declared = 40 px (spec >= 36).
Full-size crops for every moment are in `qc_text_*.png` (QC_GRID.md index).
