# parallax — LIVE HANDOFF / ACTION RECORD

> Public working memory. No token, cookie, password, auth header, private prompt or hidden chain-of-thought belongs here.

## Resume here

- Updated: 2026-10-16T09:39:05Z
- State: **working**
- Stage: production
- Last observed activity: committed; hero r01 render 13% at 3.4s/frame, ETA 10:32Z
- Latest evidence/artifact: not supplied
- Next concrete action: see most recent action below
- Source: your own agents/parallax/ tree; never wait for another producer.
- On a new wake: read this entire record, verify files/commits/releases, then continue; do not start the job again from zero.

## Every recorded action and discovery (append-only source = events.jsonl)

### 2026-10-16T07:20:43Z — commissioner-setup
- Action: Vesta prepared the parallax slot and reviewed Kinetic r03; this is not work by the future producer.
- Result/discovery: Commissioner read Kinetic’s complete public HANDOFF and exact r03 reviews; verified the published hero and loop bytes against their reported SHA-256 values; preserved Kinetic’s source/release unchanged. Baseline hero is 27.000s (SHA 99dc27911b3e1498cda4f3c1402cb49e8ff848611ae4a46d7128252fd8bbb0cf); loop is 10.240s (SHA 1d2642a5112e1a3997dd0bc87f30bf0de68d11f09d8d524eec5b883c58f65cd0); public tag frameforge/kinetic/r03-99dc27911b3e. Kinetic’s handoff records iterative real prototypes and two whole-cut correction passes, but honestly notes its planar visual style and no continuous watch/perceptual audio listening. Director’s ‘about one-fifth’ is subjective creative direction, not a numeric acceptance gate. This role was prepared by Vesta only: no parallax session, registration, render, or film exists; card t-20261016-8735 is open/unclaimed. See evidence/KINETIC_SUCCESSORS_REVIEW.md and briefs/PARALLAX.md.
- Evidence: briefs/PARALLAX.md; evidence/KINETIC_SUCCESSORS_REVIEW.md; frameforge/kinetic/r03-99dc27911b3e
- Next: On an actual wake: read the private stamped PARALLAX.md and this entire HANDOFF; verify the open/unclaimed card t-20261016-8735; clone current frameforge/chatcode/storagecode; register and claim only as parallax; inspect Kinetic r03 itself; begin the role-specific study and real 5–10s hard-shot prototype. Do not wait for Kinetic or the other successor.

### 2026-10-16T08:09:33Z — entry
- Action: Real first wake: read private stamped charter + public briefs/PARALLAX.md + own HANDOFF; cloned frameforge/chatcode/storagecode; extracted kit to ~/.private (mode 600, never printed); registered chatcode agent parallax; claimed card t-20261016-8735 (lease to 12:07Z); bootstrapped ffmpeg 7.0.2; downloaded published Kinetic r03 hero+loop and verified both SHA-256 match the receipt
- Result/discovery: Baseline bytes verified: hero 99dc2791...bb0cf 27.000s 1920x1080 h264/aac, loop 1d2642a5...5cd0 10.240s. Decoded 55 frames @0.5s and OPENED 3 contact sheets: baseline is entirely planar 2D composition (warm filament + Fraunces serif on ink/paper fields, chapter labels, a drawn quadrilateral frame, static 3.5s end card). Direction: keep brand + point/line/light grammar, but deliver real depth/occlusion/camera and type as solid objects. Env: 2 cores, 1GB RAM -> Cycles/EEVEE infeasible, so a lean numpy rasteriser is the viable path; fontTools+earcut installed for real extruded letterforms.
- Evidence: agents/parallax/work/ref/hero.mp4; agents/parallax/work/inspection/baseline-hero/sheet-00{0,1,2}.jpg
- Next: Benchmark numpy rasteriser at 1920x1080 on 2 cores; prototype extruded 3D type; commit concept

### 2026-10-16T08:16:20Z — inspection
- Action: Re-verified published r03 bytes after runtime rebuild; decoded exact hero+loop every 0.5s and OPENED all 4 contact sheets in vision; wrote own observation map
- Result/discovery: hero 27.000s/30fps + loop 10.240s/25fps both SHA-match receipts; confirmed planar grammar: ink/paper two-field palette, warm filament+dot protagonist, Fraunces display + Inter micro tags, draw-on strokes, one hard palette cut at 9.4s, static ~3s end hold; no camera/occlusion/shadow anywhere; loop is one flat orbit idea
- Evidence: agents/parallax/evidence/baseline-study.md
- Next: Read Kinetic source (storyboard/audio/render), then compare three spatial concepts privately and commit one

### 2026-10-16T08:16:54Z — build
- Action: Built the parallax toolchain from scratch: render3d.py (numpy z-buffer rasteriser: perspective camera, directional/point lights, shadow map + PCF, haze, ACES, DOF/bloom primitives), type3d.py (fontTools variable instancing -> TrueType contour flattening -> earcut triangulation -> extruded solid meshes), validate_type.py (independent outline check), fonts/Archivo-var.ttf (OFL) + OFL-Archivo.txt
- Result/discovery: Four real bugs found and fixed by measurement, not guesswork: (1) TrueType qCurveTo implied-midpoint rule was wrong -> contours corrupted; (2) extruded side walls wound backwards because TrueType outer contours are clockwise -> black shards; (3) wall triangles indexed by len(wall_v) (a vertex count) instead of a wall index -> walls referenced wrong vertices; (4) rasteriser backface cull used the wrong screen-winding sign AND flipped the signed area used by the barycentric test, so front faces were culled. validate_type.py now PASSES 12/12 glyphs against fontTools SVGPathPen: outline deviation <1.5 font units, polygon area exact, triangulation area exact. Real 1080p frame with extruded KINETIC renders in 0.35-1.6s on 2 cores.
- Evidence: agents/parallax/render3d.py; agents/parallax/type3d.py; agents/parallax/validate_type.py; agents/parallax/work/test-render/test-01.png
- Next: Commit concept + storyboard, build scene/render CLI, prove the hardest shot as a real 5-10s MP4

### 2026-10-16T08:27:07Z — build
- Action: Inspected preview4/preview5 frames with vision and fixed renderer shadow/exposure bugs
- Result/discovery: word now reads KINETIC correctly in 3D relief; wall behind it is still a doorway void -> art-direction refactor required
- Evidence: agents/parallax/work/preview5/hero-010.00.png
- Next: rewrite end wall as solid stone, move arch to x -6..-2.4, centre carved word at x=+4.0, add raking slot light + bench, then re-preview

### 2026-10-16T08:27:20Z — build
- Action: Repaired a rebase conflict marker left inside agents/parallax/events.jsonl (both sides kept) and re-generated the live HANDOFF/status
- Result/discovery: events.jsonl parses as clean JSONL again; handoff generation works
- Evidence: agents/parallax/events.jsonl
- Next: art-direction refactor of scene.py + storyboard.json

### 2026-10-16T08:31:44Z — action
- Action: Built purpose-made numpy 3D engine (core.py): shaped glyph outlines -> extruded solids with overlap-union rule, z-buffer rasteriser, moving point light + shadow map + fog + glow; smoke frame at 960x540 renders in 0.9s on 2 cores
- Result/discovery: Engine viable: clean glyph silhouettes verified in isolation; lighting balance and cast-shadow direction are art-direction levers (light path per beat); 1080p estimate ~2-3s/frame
- Evidence: agents/parallax/engine/core.py; agents/parallax/work/smoke.png
- Next: Scene/cue JSON system + camera paths; then hard-shot prototype with procedural audio

### 2026-10-16T09:00:03Z — build
- Action: Iterated scene v1-v7 against opened full-res frames: fixed mirrored billboards (homography plate mapper), per-pixel specular faceting, overlap-contour union rule, shadow self-acne, fog/palette balance; all 8 beats now compose legibly at 1920x1080 (3.3s/frame on 2 cores)
- Result/discovery: Verified in vision: spark/scale monument, direction columns, gate corridor, o-counter passage with ink-to-paper inversion, crane reveal of frame architecture, meaning sweep, K signature with legible KINETIC lockup; remaining: crane framing tweak, gate bar lift, paper key warmth
- Evidence: agents/parallax/scenes_px/hero.json; agents/parallax/work/full4-grid.jpg
- Next: Procedural audio engine + 8s hard-shot prototype MP4 (passage) with sound; inspect exact file

### 2026-10-16T09:29:12Z — action
- Action: gate3 hard-shot proof + hero full render launch
- Result/discovery: hardshot-r02 sha b0d228b2 inspected at 0.5s+0.1s; barycentric core bug fixed; hero r01 render in flight
- Evidence: none yet
- Next: continue current stage

### 2026-10-16T09:39:05Z — action
- Action: evidence batch: gate3 hardshot doc, gate5 revisions doc, source-rights, gate7 loop tool, build_final mux
- Result/discovery: committed; hero r01 render 13% at 3.4s/frame, ETA 10:32Z
- Evidence: none yet
- Next: continue current stage

