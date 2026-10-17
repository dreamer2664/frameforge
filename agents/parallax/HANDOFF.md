# parallax — LIVE HANDOFF / ACTION RECORD

> Public working memory. No token, cookie, password, auth header, private prompt or hidden chain-of-thought belongs here.

## Resume here

- Updated: 2026-10-17T08:07:39Z
- State: **delivered**
- Stage: delivery
- Last observed activity: agents/parallax/HANDOFF-successor.md (57 KB) is committed in frameforge and archived to storagecode; the copy that carries the live GitHub/chatcode tokens is a local, mode-600 file outside every clone (/home/user/KINETIC_SUCCESSOR_HANDOFF.md) because the repos and the ntfy wires are public and the crew key is shared - the repository copy contains the arming procedure instead, and it was verified to contain no token literal
- Latest evidence/artifact: agents/parallax/HANDOFF-successor.md
- Next concrete action: Nothing outstanding: the candidate is published, verified, and the card is in review
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

### 2026-10-16T12:06:42Z — build
- Action: Completed the parallax renderer/scene/score pipeline: fixed 7-letter type layout, shadow depth comparison, UV orientation, additive-texture path, box winding; wrote audio.py (original score, measured -16 LUFS, seam-exact loop)
- Result/discovery: 1080p hero segment render running in the background; audio masters written to agents/parallax/work/audio
- Evidence: agents/parallax/work/audio/hero.wav
- Next: finish hero segments, render loop, mux, QC, revision passes, publish

### 2026-10-16T12:09:05Z — recovery
- Action: Sandbox reset at 12:06 UTC wiped the private key dir, the ffmpeg cache, the git metadata and the pip packages mid-render; rebuilt credentials from the private kit, re-cloned the three repos, restored ffmpeg from the BtbN build, reinstalled mapbox_earcut, and isolated this wake's implementation in agents/parallax/px/ so the concurrent wake's files are not touched
- Result/discovery: Toolchain restored; 1080p hero render restarted from segment 0; score recomposed at -16.0 LUFS (hero and loop) with a loop seam step of 0.00003
- Evidence: agents/parallax/px/work/audio/hero.m4a
- Next: finish the five hero segments, render the loop, mux, QC, revision passes, publish

### 2026-10-16T12:24:16Z — revision
- Action: Revision 1 (whole-cut rhythm): re-timed every timed element of the storyboard with a piecewise time map (6.0->4.2, 15.0->12.2, 22.4->19.4, 29.4->26.4); the gate forms 3 s earlier, the monument arrival gains 3 s of screen time, and the camera now converges on the gate centre line so no letter fills the frame
- Result/discovery: Beats now hall 0-4.2 / wall 4.2-12.2 / release 12.2-19.4 / gate 19.4-26.4 / monument 26.4-40.0; before/after frames captured at 1280x720 (work/rev1/before vs work/rev2/after2); revision log stored in storyboard.json and evidence/revision-1-rhythm.md
- Evidence: agents/parallax/px/evidence/revision-1-rhythm.md
- Next: Revision 2: material, light, type readability, sound sync

### 2026-10-16T12:24:16Z — revision
- Action: Revision 2 (material/light/type/sound): the carved wall got its own stone material plus a travelling band of light and a grazing rake light, the chamber became a graded room with piers instead of a flat cream card, box UVs became world-scale (the plinth no longer reads as smeared wood), copy fades out when the lens is within 4.2 m, and the score was re-derived from the storyboard so the seven taps land on the actual letter-reveal times (6.819-11.084 s) and pan with the light
- Result/discovery: Wall reads as lit stone with a value gradient; final image is the word on a plinth in a receding warm room; hero -16.00 LUFS / -12.80 dBTP, loop -16.00 LUFS / -14.20 dBTP, loop seam step 0.00003; before/after frames in work/rev2/after2 and after4
- Evidence: agents/parallax/px/evidence/revision-2-material-light-type-sound.md
- Next: Final 1920x1080 hero render, then the loop, then QC and publication

### 2026-10-16T12:46:37Z — proof
- Action: Hard-shot proof: rendered and muxed a real 8.000 s 1920x1080 H.264/AAC segment of the film (the opening of the hero with the composed score) and inspected it as decoded frames
- Result/discovery: work/evidence/hardshot-8s-1080p.mp4 = 8.000 s, 1920x1080, 24 fps, AAC 48 kHz 192 kbps, 84.8 Mbit/s video; decoded frames show the carved word KINETIC in relief on a lit stone wall, the raking light travelling right to left, the copy 'We set it in stone.', the slot of light at frame right and the arch at frame left; no missing glyphs, no black tail
- Evidence: agents/parallax/px/work/evidence/hardshot-8s-1080p.mp4
- Next: Finish segments 1-4, then the loop, then the exact-file review

### 2026-10-16T14:23:54Z — build
- Action: Rendered the final hero: five 1920x1080 8-second segments (960 frames, 24 fps, CRF 16) joined into hero-silent.mp4, then muxed with the re-synced score into hero-master.mp4
- Result/discovery: hero-master.mp4 = 40.000 s, 1920x1080, H.264 yuv420p 24 fps, AAC 48 kHz stereo 192 kbps, video and audio both exactly 40.000 s (no tail mismatch), 427,918,562 bytes, SHA256 01d27eb834e0419b8f2511f92a7d91c78d9b0cbfe55d3fd00e99ec8c655cf162; house QC ops/media_qc.py reports technical_pass=true with zero violations; integrated loudness -16.04 LUFS, true peak -11.79 dBTP
- Evidence: agents/parallax/px/work/renders/hero-master.mp4
- Next: Render the 240-frame loop, then the exact-file review and the loop gate, then publish

### 2026-10-16T15:04:26Z — revision
- Action: Exact-file review of the 1920x1080 master (0.5 s decode grid read frame by frame, dense 0.1-0.2 s samples, 640x360 phone check, full decode) found two caption-framing defects: the opening line sat at x=-9.6 m, outside the frame for its whole 3.05 s life, and the release line was crossed by the swinging N and then ran off the right edge while still at full alpha until 19.6 s
- Result/discovery: Both fixed in the storyboard (copy 1 moved above the carved word; copy 3 shortened to 'The stone lets go.' and closed at 16.0 s) and segments 0-2 re-rendered; the camera, lights, materials, choreography, type and the whole 16-40 s section are unchanged and the score is unchanged; the loop gate passed on the encoded MP4 (wrap mean abs diff 5.396 inside the interior range 5.373-5.405, wrap motion 0.92 px vs interior 0.88-0.94 px, wrap luminance step -0.014 vs interior max 0.062, source audio seam step 2.8e-05 over 460800 samples)
- Evidence: agents/parallax/px/evidence/revision-3-caption-framing.md
- Next: Re-mux, re-run the QC and the review grid on the corrected master, then publish

### 2026-10-16T17:39:47Z — recovery
- Action: Second sandbox reset at 17:34 UTC wiped the rendered media, the private credential directory, the ffmpeg cache and all git metadata; the whole environment was rebuilt from scratch
- Result/discovery: Credentials re-extracted from the private stamped kit into ~/.private/parallax.env (600) with the askpass helper (700), all three repos re-cloned, FFmpeg 7.0.2 static restored, numpy/scipy/fontTools/Pillow/mapbox_earcut reinstalled, the score recomposed byte-for-byte identically (hero -16.00 LUFS / -12.80 dBTP, loop -16.00 / -14.20, loop seam step 0.00003), the pipeline scripts restored into git (only heavy media stays ignored) and the 1920x1080 hero re-render restarted with the revision-3 caption fix; the card lease was renewed to 23:37:29Z
- Evidence: agents/parallax/px/work/render_hero.sh
- Next: Finish the hero render, then the loop, then the QC, the exact-file review and the publication

### 2026-10-16T18:20:51Z — proof
- Action: Re-issued the hard-shot proof from the rebuilt render: a real 8.000 s 1920x1080 H.264/AAC MP4 with the composed score, taken from the delivered opening of the hero, and inspected as decoded frames
- Result/discovery: work/evidence/hardshot-8s-1080p.mp4 = 8.000 s, 1920x1080, 24 fps, AAC 48 kHz 190 kbit/s, 85 Mbit/s video; the decoded frame at t=2.6 s shows the caption 'A word is a heavy thing.' now fully inside the frame above the carved word (the revision-3 fix), the amber doorway at frame left, the slot of light at frame right and the light pool on the floor; no missing glyphs and no black tail
- Evidence: agents/parallax/px/work/evidence/hardshot-8s-1080p.mp4
- Next: Finish hero segments 2-4, the loop, the QC and the publication

### 2026-10-16T20:02:32Z — delivery
- Action: Published the parallax candidate 'KINETIC - Give language a body' to storagecode: the 40.000 s hero, the 9.600 s seamless loop, the poster, both 960x540 rough-cut proxies, the measured technical QC (own tool + house tool), and the five contact sheets of the exact-file review
- Result/discovery: Release https://github.com/dreamer2664/storagecode/releases/tag/frameforge/parallax/r01-ce4424a3fb16 ; hero-master.mp4 = 428,176,773 B, SHA256 ce4424a3fb1615cfce3c23610e1dfab406e0853b1dbf64b672d965e99f532cec, 1920x1080 H.264 yuv420p 24 fps 960 frames, AAC 48 kHz 207 kbit/s, -16.1 LUFS, -6.9 dBTP, faststart, audio and video tails both 40.000 s (mismatch 0.000 s); loop-master.mp4 = 100,886,150 B, SHA256 cd7efe7e08aa92ea0ed5e66101148e5eceb4c21b0247fc3b42c4685835edbe54, 1920x1080 25 fps 240 frames, -16.1 LUFS, -11.1 dBTP; all 13 assets re-verified by re-download and SHA comparison; house QC ops/media_qc.py technical_pass=true with zero violations; loop gate on the encoded MP4 green (wrap mean abs diff 5.396 inside the interior range 5.373-5.405, wrap motion 0.92 px vs interior 0.88-0.94 px, wrap luminance step -0.014 vs interior max 0.062, source audio seam 2.8e-05 over 460800 samples); durable archive at https://github.com/dreamer2664/storagecode/tree/main/data/frameforge/parallax/r01-ce4424a3fb16 with the concept commitment, the three revision passes, the review method and findings, the licence manifest and both QC reports; code at dreamer2664/frameforge 03d3f31 in agents/parallax/px
- Evidence: https://github.com/dreamer2664/storagecode/releases/tag/frameforge/parallax/r01-ce4424a3fb16
- Next: Board card t-20261016-8735 to review with the real links; the candidate is published, not accepted by a human

### 2026-10-17T08:07:39Z — handoff
- Action: Wrote a full successor handoff for the next agent in this line (a second spatial-typography KINETIC film): every tool in the repo with its exact invocation, the complete copy-pasteable pipeline from a cold sandbox to a published release, the measured render/QC/upload timings, the three revision passes and their before/after evidence, the rasteriser/type/audio/QC bug ledger, the art-direction and realism lessons, the ntfy wire topics and shortcuts, the credential arming procedure, and an honest write-up of the one thing the reviewer noticed (the travelling light band on a flat wall reads as the wall moving) with four ranked fixes
- Result/discovery: agents/parallax/HANDOFF-successor.md (57 KB) is committed in frameforge and archived to storagecode; the copy that carries the live GitHub/chatcode tokens is a local, mode-600 file outside every clone (/home/user/KINETIC_SUCCESSOR_HANDOFF.md) because the repos and the ntfy wires are public and the crew key is shared - the repository copy contains the arming procedure instead, and it was verified to contain no token literal
- Evidence: agents/parallax/HANDOFF-successor.md
- Next: Nothing outstanding: the candidate is published, verified, and the card is in review

