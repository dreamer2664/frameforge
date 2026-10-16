# Source, font and rights ledger

Updated 2026-10-15. This ledger applies to the Kinetic commissioned film and its small supporting assets. It does not imply sponsorship or endorsement by any reference creator or font author.

## Original creative / audio materials

- All shapes, wordmark/monogram, layouts, paths, camera timing and animation code are created specifically in `agents/kinetic/` for this project.
- The score and accents are synthesized procedurally from oscillators, deterministic envelopes and generated noise by `audio.py`; no borrowed track, sample, stock asset, voice, or online audio service is used. No narration, so no voice or caption sidecar is applicable.
- No external photo, footage, logo, mascot, product screenshot, stock image, or reference clip appears in the delivered composition.
- The two commissioned TikTok references were fetched only for internal study, decoded to private samples under ignored `work/refs/`, and are not redistributed or used as compositional source assets. Their public URLs and observed design principles are in `reference-study.md`.

## Included font files and licenses

The fonts are distributed under the SIL Open Font License (OFL); the exact license texts used are retained under `fonts/licenses/`. Font files are unmodified binaries; their SHA-256 values below pin the copies used. The chosen hero system is Fraunces display + Inter UI. Playfair Display is retained for the documented internal comparison board only.

| Font file | Name-table version / pinned source | Actual source URL | SHA-256 | License |
|---|---|---|---|---|
| `fonts/Fraunces.ttf` | Fraunces 1.000, source commit tag in name table `[b76b70a41]`, variable axes `opsz 9–144`, `wght 100–900`, `SOFT`, `WONK` | `https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/Fraunces%5BSOFT%2CWONK%2Copsz%2Cwght%5D.ttf` | `177ff6c0f14e5550a3c624247cd1189611d4eb65d000b14944c63d967958abbb` | `fonts/licenses/Fraunces-OFL.txt`; Google Fonts OFL source `https://raw.githubusercontent.com/google/fonts/main/ofl/fraunces/OFL.txt` |
| `fonts/Inter-Regular.ttf` | Inter 4.000, `git-a52131595` | Inter v4.0 release: `https://github.com/rsms/inter/releases/tag/v4.0` (source archive `Inter-4.0.zip`) | `64f8be6e55c37e32ef03da99714bf3aa58b8f2099bfe4f759a7578e3b8291123` | `fonts/licenses/Inter-OFL.txt`; archive `LICENSE.txt` |
| `fonts/Inter-Medium.ttf` | Inter 4.000, `git-a52131595` | same Inter v4.0 archive | `1bda81124d6ae26ed16a7201e2bd93766af5a3b14faf79eea14d191ebbd41146` | same retained OFL text |
| `fonts/Inter-SemiBold.ttf` | Inter 4.000, `git-a52131595` | same Inter v4.0 archive | `0dc98e8aa59585394880f25ab89e6d915ad5134522e961b046ca51fad3a18255` | same retained OFL text |
| `fonts/Inter-Bold.ttf` | Inter 4.000, `git-a52131595` | same Inter v4.0 archive; used in static candidate board | `0cb1bc1335372d9e3a0cf6f5311c7cce87af90d2a777fdeec18be605a2a70bc1` | same retained OFL text |
| `fonts/PlayfairDisplay.ttf` | Playfair Display 1.203, variable `wght 400–900` | `https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/PlayfairDisplay%5Bwght%5D.ttf` | `c40f2293766a503bc70cce9e512ef844a4ccb7cbcde792fe2ea31d191917d8d6` | `fonts/licenses/PlayfairDisplay-OFL.txt`; Google Fonts OFL source `https://raw.githubusercontent.com/google/fonts/main/ofl/playfairdisplay/OFL.txt` |

The official release ZIP used for Inter was extracted into the project font folder; exact TTF file hashes were measured after extraction. Fraunces and Playfair Display were fetched from the Google Fonts repository and their upstream name-table versions and binary hashes were inspected. No font name is inferred from a reference video.

## Software / production environment (not bundled as artwork)

- Python 3.13.16; Pillow 12.3.0; NumPy 2.3.5; fontTools present for font-version/axis inspection.
- FFmpeg/ffprobe 7.0.2 static build for raster-to-H.264/AAC encoding and exact-file decode/measurement. Tool binary is installed in the local user cache and is not redistributed.
- yt-dlp 2026.8.19 was used only to retrieve the public reference clips for private study; it is not an input to the film renderer.
- No paid services, API-generated imagery, model-generated voice, or external runtime service is part of playback.

## Rights boundary

Do not extract/reference-download assets into a public release. Reuse only the original Kinetic compositions and the OFL-licensed font files with their notices. Keep source clips and intermediate frames out of the source repository and public archive.
