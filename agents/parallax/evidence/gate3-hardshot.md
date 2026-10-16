# Gate 3 — hard-shot proof (passage 20.0–28.0 s) with sound

**Candidate:** `work/renders/hardshot-r02.mp4` (1920×1080, 24 fps, H.264 crf18 yuv420p, AAC 192 k 48 kHz, faststart, 8.000 s)
sha256 `b0d228b220fcb9a4ae99be49039e3675c71da9de66c3ccd78f6ed3d54329e96c`
Frames: `work/hard2/f00480..f00672.png` (SSAA off); audio slice 20–28 s of `work/audio/hero-r01.wav` (procedural, −16.6 LUFS integrated over full hero).

## Decoded-frame inspection (encoded file, not source PNGs)
- `work/inspection/hard2-sheet.jpg` — every 0.5 s (17 tiles): gate frames pass warm-lit (20.0–21.0), monument "world" fills frame (22.0–23.5), counter bore + light orb (23.8–24.4), inversion flash to paper (24.5–25.1), emergence pale field (25.5), "Make room." + frame architecture (26.5–28.0). No black frames, no missing glyphs, captions inside frame.
- `work/inspection/hard2-dense-sheet.jpg` — every 0.1 s across the hardest transform (23.8–26.2, 25 tiles): continuous motion, no z-fighting, no union seams, no facet stripes; mid-blend mud confined to 24.4–24.6 (0.3 s) → shortened inversion window in revision 2.

## Faults found & fixed between r01 and r02 (engine-level)
1. **Barycentric cyclic misassignment** (root cause of "facet stripes"): edge a→b is the barycentric of vertex *c*; I had w0→a. Silhouettes unaffected, but per-pixel lighting/depth evaluated at displaced intra-triangle points → wedge shading + part of shadow acne. Fixed in `engine/core.py` (`draw_triangles` + `ShadowMap.build`). Before: `work/o_iso.png` top; after: r02 sheet 22.0–24.0 clean mineral caps.
2. Gate front bars too black → albedo (118,114,108), t1 21.0.
3. Interior too dark too long → inversion 24.3–25.1 (then 24.5–25.0), counter rim ignite amp 0.5 σ0.8.
4. Diagonal horizon seam → ground quad 2000 @ z −400.
5. Crane clipped "Make room." → key 29.5: pos (0,7.5,−96), tgt (0,4.6,−126), fov 54 (revision 2 also floats the words into the frame opening).

## Sound
Slice carries gate whooshes (20.1/21.6 ticks), swell 23.2, boom moved to 24.5 to land on inversion midpoint; measured on muxed file via ffmpeg ebur128 (progress + summary). Audio fully procedural (`audio_px.py`), deterministic seeds, no external assets.

**Verdict:** engine is stable at production size; proceed to full hero. Toolchain (numpy rasteriser + ffmpeg) retained — no switch needed.
