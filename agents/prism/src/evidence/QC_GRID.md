# QC_GRID — PRISM / PROOF (env-B)

Visual audit trail. Open these at full size; the film is judged here, not in
the scene graph. All sheets are built from the 750 rendered PNG frames by
`evidence/qc_grids.sh` / `evidence/qc_crops.py`.

## Master grid
| file | content |
|---|---|
| `qc_grid_every25.png` | every 25th frame (30 tiles, 6×5) — the whole film in one sheet |

## Text moments (every frame of each moment, 240×135 tiles)
| file | id | string | frames |
|---|---|---|---|
| `qc_text_T1.png` | T1 | SIGNAL // UNVERIFIED | 8–92 (85) |
| `qc_text_T2.png` | T2 | A CLAIM IS NOISE. | 40–176 (137) |
| `qc_text_T3.png` | T3 | FRAME 000/750 | 196–442 (247) |
| `qc_text_T4.png` | T4 | dLUMA +38.2%  DRIFT 0.004px | 236–372 (137) |
| `qc_text_T5.png` | T5 | MEASURE EVERYTHING. | 330–446 (117) |
| `qc_text_T6.png` | T6 | PROOF | 483–656 (174) |
| `qc_text_T7.png` | T7 | MEASURED. | 500–528 (29) |
| `qc_text_T8.png` | T8 | REPRODUCIBLE. | 530–558 (29) |
| `qc_text_T9.png` | T9 | SIGNED. | 560–596 (37) |
| `qc_text_T10.png` | T10 | RECEIPT | 668–749 (82) |
| `qc_text_T11.png` | T11 | INDEPENDENT ACCEPTANCE PENDING. | 700–749 (50) |

## Full-size crops (TEXT_LOG gate)
`crop_text_<id>.png` — each moment at its widest frame, full resolution,
±24 px pad. If any glyph pixel lies outside the 90% box, `TEXT_LOG.md` shows
a negative margin and the file does not ship.

## Flashes (±3 frames around every flash, 480×270 tiles)
| file | id | frames |
|---|---|---|
| `qc_flash_F1.png` | F1 | 147–155 |
| `qc_flash_F2.png` | F2 | 297–304 |
| `qc_flash_F3.png` | F3 | 387–395 |
| `qc_flash_F4.png` | F4 | 477–486 |
| `qc_flash_F5.png` | F5 | 557–564 |
| `qc_flash_F6.png` | F6 | 657–665 |

Files present: 32
