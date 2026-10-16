# Source rights & provenance — parallax KINETIC hero + loop (r01)

| Asset | Provenance | License / right |
|---|---|---|
| Fraunces (display serif) | `agents/parallax/fonts/Fraunces.ttf`, copied from `agents/kinetic/fonts/` licensed set | SIL OFL 1.1 — license text in `fonts/licenses/` |
| Inter (UI/sans) | `agents/parallax/fonts/Inter-*.ttf`, same set | SIL OFL 1.1 — license text in `fonts/licenses/` |
| FFmpeg static builds | downloaded by `ops/bootstrap_media.py` into `~/.cache/frameforge/bin/` (LGPL/GPL static builds, used unmodified as CLI tools) | ffmpeg.org license; tool use only, no code linked |
| Visuals | 100% procedural: `engine/core.py` numpy rasteriser + `scenes_px/*.json` geometry/type data | original work of this agent |
| Score / SFX | 100% procedural synthesis: `audio_px.py` (oscillators, filtered noise, cues) — no samples, no libraries, no presets | original work of this agent |
| Narration | NOT used (Kokoro/`ops/tts.py` never invoked for this film) | n/a |
| Stock footage / images / templates | none | n/a |
| Kinetic r03 reference | `work/ref/{hero,loop}.mp4` kept as private baseline for DNA study only; no frames, audio, or copy reused in output | internal reference, not distributed |

No third-party copyrighted material appears in `work/renders/hero-r01.mp4` or `work/renders/loop-r01.mp4` beyond the OFL-licensed typefaces named above (embedded as rendered glyphs, permitted by OFL for document/embedding use).
