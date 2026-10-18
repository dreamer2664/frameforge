# THIRD_PARTY — PRISM / PROOF

All third-party components used by the film, with exact versions and licences.
Versions are pinned in `package.json` / `package-lock.json` (lockfile shipped).

| Component | Version | Licence | Role |
|---|---|---|---|
| three | 0.186.1 | MIT | WebGL scene graph, shaders, post-processing (`examples/jsm` composers) |
| puppeteer | 25.14.0 | Apache-2.0 | headless Chrome driver for the deterministic frame pipeline |
| Chrome for Testing | 155.0.8059.79 | BSD-3-Clause (Chrome) | WebGL 2.0 / SwiftShader software renderer |
| esbuild | 0.28.2 | MIT | bundler (single-file IIFE bundle incl. fonts as data URIs) |
| @fontsource/archivo-black | 5.3.0 | OFL-1.1 | display face (see RIGHTS.md) |
| @fontsource/ibm-plex-mono | 5.3.0 | OFL-1.1 | mono face (see RIGHTS.md) |
| ffmpeg | 7.1.5-0+deb13u1 | LGPL-2.1+ / GPL-2 (x264) | encode, decode verification, loudness measurement |
| numpy | 2.3.5 | BSD-3-Clause | audio synthesis math |
| Python | 3.13.16 | PSF | audio synth + evidence scripts |

No other runtime dependencies. No CDN fetches at render time: fonts are
embedded in the bundle as data URIs; the page loads from `file://` with zero
network requests (verifiable in `TECHNICAL_RECEIPT.md`).
