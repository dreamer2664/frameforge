# RIGHTS — PRISM / PROOF

Everything in the deliverable is original or open-licensed with receipts.
Nothing scraped, nothing ripped, no identifiable-artist mimicry.

## Code
- Film source (`film/`, `render.mjs`, `png.mjs`, `encode.sh`, `bootstrap.sh`):
  original, MIT (see `LICENSE`).
- three.js r186 (MIT) and its `examples/jsm` post-processing modules (MIT):
  used unmodified, attributed in `THIRD_PARTY.md`.
- Evidence/analysis scripts: original, MIT.

## Fonts (open licences only)
| Face | Version | Licence | Source |
|---|---|---|---|
| Archivo Black | 5.3.0 (fontsource package) | SIL OFL 1.1 | npm `@fontsource/archivo-black`; licence text at `node_modules/@fontsource/archivo-black/LICENSE`; files `film/fonts/archivo-black-latin-400-normal.woff2` |
| IBM Plex Mono (400/500/600/700) | 5.3.0 (fontsource package) | SIL OFL 1.1 | npm `@fontsource/ibm-plex-mono`; licence text at `node_modules/@fontsource/ibm-plex-mono/LICENSE`; files `film/fonts/ibm-plex-mono-latin-*-normal.woff2` |

Cap-height ratios used for px-exact type (measured, not assumed): display
0.72 cap/em, mono 0.70 cap/em — measured with canvas `measureText` on the
actual woff2 files at 1000 px em (script of record: `film/text.js`
`CAP_RATIO`, cross-checked during styleframe QC).

## Textures / geometry
100% procedural: instanced icosahedra, line grids, canvas-generated radial
glow sprites and glyph atlases. No imported textures, no scanned assets.

## Audio
Fully self-synthesised by `audio/synth.py` (numpy, seeded `0x50524F4F`):
oscillators, seeded noise, FFT filtering, soft-clip. No samples, no loops,
no commercial or AI-mimic material. The generator IS the receipt: re-running
it reproduces the master bit-for-bit from the same seed and `events.json`.

## Theme / IP
"PROOF" is an original concept (claim → measurement → verdict → receipt).
No franchise, characters, logos or lyrics. On-screen strings are original
text authored for this film.

## On-screen factual strings
The receipt card quotes the commission packet's SHA-256 prefix
(`F29F865C…`) and the render seed — both facts of record, not third-party IP.
