# Shift note — lithos, card t-20261017-32df (end of r01 delivery)

**Last session block (this note supersedes the previous shift note below it):**
RELEASED `frameforge/lithos/r01-56f1fb99211c` — hero.mp4 42.000 s + loop.mp4
10.240 s (all four loop seams PASS on encoded bytes) + poster + rough cuts +
technical.json + media-qc-hero.json + craft-hero.json + 7 review sheets.
Remote SHA-256 verified by download: hero 56f1fb99.., loop a67812e2..,
poster 3a4d6f8f.. — all IDENTICAL to local. ops/media_qc: technical_pass true,
violations []. Evidence archive: `data/frameforge/lithos/r01-56f1fb99211c/`
+ INDEX.md + PUSHES.md appended. Two consequential revisions with before/after
numbers (rev 1 graded iris; rev 2 true loop). Review = measurement of exact
frames + published contact sheets; no continuous playback possible (stated in
`px/evidence/review-method.md`).

**Best starting points for any successor:**
- The full picture is `px/evidence/film-facts.md` + `px/work/qc/technical.json`.
- Reproduce: `px/audio.py` (score) then `px/work/render_hero.sh`,
  `px/work/render_loop.sh`, `px/work/endgame.sh`, `px/work/publish.sh`.
- The engine contract lives in `px/scene.py` docstrings; storyboard.json is
  the single source of truth (including the revision log).
- Gotchas hit here (don't repeat): AAC encodes must be whole frames
  (loop = 480 frames = 10.240 s), hero grading keys must never leak into
  loops, `ops/media_qc.py`/`release.py`/`field.py` AGENTS rosters need the
  producer name at onboarding, and never probe a file while its renderer is
  still writing.

---
# Previous shift note (kept for context)

Read `/home/user/uploads/KINETIC_SUCCESSOR_HANDOFF (1).md` and "start working":
build one original 35–55 s 1920×1080 KINETIC hero film + deliberately designed
8–12 s seamless loop (MP4 H.264/yuv420p/faststart, AAC 48 kHz ≥160 kbit/s,
≈−16 LUFS ±1.5, true peak ≤ −1 dBTP, A/V tail ≤250 ms), real 3D/depth-aware
visuals (near/mid/far, perspective, occlusion, camera that reveals), typography
as physical extruded object used as architecture, coherent art direction (no
generic AI-neon), ≥3 spatial/choreographic moments + memorable reveal,
first-second hook, intentional final image, brand "KINETIC" only on screen.
