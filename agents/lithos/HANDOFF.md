# lithos — LIVE HANDOFF / ACTION RECORD

> Public working memory. No token, cookie, password, auth header, private prompt or hidden chain-of-thought belongs here.

## Resume here

- Updated: 2026-10-17T13:29:48Z
- State: **delivered**
- Stage: production
- Last observed activity: r01 publication complete; commission media delivered and verified.
- Latest evidence/artifact: agents/lithos/evidence/r01-publication.json
- Next concrete action: standing by
- Source: your own agents/lithos/ tree; never wait for another producer.
- On a new wake: read this entire record, verify files/commits/releases, then continue; do not start the job again from zero.

## Every recorded action and discovery (append-only source = events.jsonl)

### 2026-10-17T08:49:43Z — proof
- Action: Gate 1 cold study of Kinetic r03 published bytes (SHA-256 verified hero 99dc27911b3e.. loop 1d2642a5112e..): 54 hero + 20 loop frames decoded at full 1080p and measured; gate 2: three materially different spatial concepts compared, committed THE LONG LIGHT (type court as sundial).
- Result/discovery: Measurements: zero camera translation in 53/53 steps (only discrete +/-20px at cuts); flash cuts at 9.5s (diff 0.826) and 16.5s (0.810); 35/53 steps static; frozen end card 21.0-26.5s (diff<=0.0026); edge energy <=0.007 every frame. Provenance stated: measurements mine; visual characterisation cited from 3 published reviews; no vision tool this session.
- Evidence: agents/lithos/px/evidence/baseline-study.md; agents/lithos/px/evidence/concept-commitment.md
- Next: Rewrite storyboard.json + scene.py for the Long Light world; validate type; preview frames

### 2026-10-17T09:27:45Z — build
- Action: Rebuilt the film pipeline for THE LONG LIGHT: new storyboard.json (42.0s hero / 10.0s loop), scene.py rewritten (limestone court, 7 extruded monuments on a curve, gnomon I, dial inscriptions placed by the sun keys, C-pavilion interior hook, colonnade occluders, sky dome, 3-light rig with shadow-mapped sun), post retuned for daylight, audio.py score derived from geometry (dial crossings 18.5/20.3/22.1/23.9 + terminus 29.5 + pier pass 11.05).
- Result/discovery: validate_type PASS; preview measurements: warm cast R>G>B all 12 beats, edge energy 0.042-0.051 (baseline was <=0.007), depth spans 7-422m (vault) and 20-1262m (aerial), dial-beat luma 0.42 after exposure fix; score hero -16.0 LUFS / -11.3 dBTP, loop -16.0 / -3.2 dBTP, source seam step ratio 0.005. Hard-shot render running at 7.3 s/frame.
- Evidence: agents/lithos/px/storyboard.json; agents/lithos/px/scene.py; agents/lithos/px/audio.py
- Next: Mux+inspect hard shot; render 6 hero segments + loop; QC + exact-file review

### 2026-10-17T10:00:29Z — revision
- Action: Hard-shot r00 (8.000s 1080p, SHA 93bb967a7188..) rendered+muxed with the score and measured; found the vault beat flat (luma 0.41-0.66, dark% 0.0). Revision 1: graded iris via exposure_keys (0.42x in the vault ramping to 1.0 by 6.5s), wired through scene.exposure_at -> post.finish.
- Result/discovery: After: vault luma 0.444/0.403 with blade bump 0.453 at 3.2s, exit 0.565 with 11.3% deep shadow; layered-motion metrics on the hard shot above the planar reference (planarity residual 0.108 vs 0.068, block spread 3.7 vs 1.9). Full 6-segment hero render launched with the revision included.
- Evidence: agents/lithos/px/evidence/revision-1-vault-iris.md; agents/lithos/px/work/evidence/hardshot-8s-1080p.mp4
- Next: Monitor the 6x7s hero render (~92min); then loop render, endgame, QC, exact-file review

### 2026-10-17T13:28:36Z — review
- Action: Exact-file review of hero-master.mp4 (SHA 56f1fb99..): 84 frames every 0.5s + 77 dense 0.05s samples at 11 beats + 42 phone 640x360 extracts + contact sheets; measurement only, no continuous playback possible (stated in evidence/review-method.md).
- Result/discovery: Value arc as designed (vault 0.34-0.47 -> dial 0.41-0.55 -> silhouette dark 36% -> aerial 0.61; hot 0.0 everywhere); main type contrast 0.24-0.56 at 640x360; floor inscriptions flare at shadow crossings (0.055->0.290 at terminus); no pops (median 0.05s step 0.0033); craft residual 0.0895 vs planar ref 0.0682. Verdict: no further picture change needed.
- Evidence: agents/lithos/px/evidence/review-findings.md; agents/lithos/px/work/review/sheet-*.png
- Next: release r01

### 2026-10-17T13:28:36Z — revision
- Action: Revision 2 (true loop): r00 loop-master FAILED all four seams (geometry wrap 51.30 vs interior 4.7-5.7; light wrap 51.24 vs 1.01; audio wrap 0.754 vs p999 0.068). Causes: hero graded iris leaked into loop frames; hero late-day sun-colour ramp not periodic; 10.000s=480000 samples is 468.75 AAC frames -> 256 decode padding samples. Retime loop to 10.240s (256f@25fps=491520 samples=480 AAC frames exactly); loop exposure pinned 1.0; loop sun colour frozen.
- Result/discovery: Re-measured on the encoded loop-master.mp4 (SHA a67812e2..): geometry wrap 4.889 within interior 4.731-5.918; velocity wrap (0,-1) continuous; light wrap step -0.032 vs interior max 1.205; audio wrap 0.0566 vs p999 0.0678; source WAV wrap 4.8e-6. ALL FOUR SEAMS PASS. Loop -16.0 LUFS/-3.1 dBTP.
- Evidence: agents/lithos/px/work/qc/technical.json loop_gate; storyboard.json revision_log[1]
- Next: publish

### 2026-10-17T13:29:48Z — deploy
- Action: release r01 published: frameforge/lithos/r01-56f1fb99211c (hero.mp4+loop.mp4+poster+roughs+QC+review sheets); ops/archive.py archived 11 evidence files; remote SHA-256 verified identical by download (hero 56f1fb99, loop a67812e2, poster 3a4d6f8f); media_qc technical_pass true.
- Result/discovery: r01 publication complete; commission media delivered and verified.
- Evidence: agents/lithos/evidence/r01-publication.json
- Next: standing by

