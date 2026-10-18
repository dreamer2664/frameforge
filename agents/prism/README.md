# PRISM — `agents/prism/src` — "PROOF"

Motion-design producer tree (frameforge). This directory is the complete,
rebuildable source of the 25.00 s three.js film **PROOF** and of its evidence
package.

## What is here
| path | what |
|---|---|
| `film/` | the film: constants, seeded utilities, event timeline, typography overlay, 3D world, grade chain, page host |
| `render.mjs` | deterministic headless renderer (Chrome + SwiftShader, `renderFrame(i)`) |
| `render_all.sh` | crash-tolerant full render (resume-aware 25-frame chunks + retry) |
| `encode.sh` | frames → video master (CRF 12) → distribution (CRF 18 + AAC 320k) |
| `audio/synth.py` | original soundtrack synthesiser (numpy, seeded; no samples) |
| `evidence/` | receipts: logs, manifests, measured TEXT/FLASH logs, QC grids, generators |
| `bootstrap.sh` | idempotent environment provision (ffmpeg, Chrome libs, npm, bundle) |
| `render.sh` | ONE command: clean checkout → masters → evidence |
| `publish.py` | storagecode release + asset upload + readback |

## Rebuild
```bash
bash render.sh          # ~40 min on 2 CPU / 2 GB (software WebGL)
```

## Design in one paragraph
Four acts on 750 frames: an amber field where *a claim is noise*; an ice
instrument grid that measures everything; a white verdict that explodes the
specimen and slams PROOF; a paper receipt card that ends, honestly, on
"INDEPENDENT ACCEPTANCE PENDING." Eleven designed text moments, six logged
flashes, a 120 bpm score built from the same frame constants as the picture.

Licence: MIT (`LICENSE`). Third party: `THIRD_PARTY.md`. Rights: `RIGHTS.md`.
