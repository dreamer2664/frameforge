# Operations — concrete helpers, not a substitute for making films

Python 3.10+; Pillow for contact sheets. The commissioning runtime was Python 3.13.16/Linux x86_64. Each producer owns its own renderer, assets, creative choices, review and final delivery. No cross-producer dependency is permitted.

## Working layout / ownership

```
briefs/KINETIC.md, SCRIBBLE.md, AXIOM.md, PARALLAX.md, GLYPHCRAFT.md   clean public charters, placeholders only
agents/<name>/                          only that producer writes here
  HANDOFF.md                            one exhaustive rendered action/failure/discovery/resume MD
  events.jsonl                          append-only journal that generates the MD
  evidence/                             small source/rights/review/QC/publication receipts
  render.py / scene data / config ...    your actual source, stack chosen by you
  work/, renders/, final/                ignored heavy outputs; archive before stopping
status/<name>.json                      last observed state, not a fake presence signal
research/REFERENCE_STUDY.md              actual commissioning visual observations, limitations included
```

Use separate clones. Do not edit another producer's folder/status or rely on another producer's renderer/voice. Shared helpers are frozen commissioning conveniences; build a role-specific alternative inside your own folder if needed. Private stamped MD packets stay **outside** this repository. `.gitignore` is a guard, not permission to copy a live key here.

## Media bootstrap and real visual inspection

```
python3 ops/bootstrap_media.py
python3 -m pip install Pillow
python3 ops/visualize.py agents/kinetic/renders/r01.mp4 --out agents/kinetic/work/r01-view --every 0.5
```

The bootstrap uses system FFmpeg/ffprobe if found through the helper API; otherwise installs local static binaries to `~/.cache/frameforge/bin`. It installs only regular archive members, records source/archive SHA and needs no root. It is Linux x86_64/arm64 specific; use a legitimate installed toolchain elsewhere. Binaries/models/reference clips are never committed. Restore may clear cache; reinstall.

`visualize.py` probes the **actual media**, decodes JPEGs with FFmpeg (AV1/HEVC supported), writes timecoded multi-page contact sheets and an inspection manifest. This does not open/understand them for you. Open **every** sheet and meaningful individual frames with your available vision tool. Record observed timestamps/problems and fixes in your journal. Decode/capture more densely at transitions. A thumbnail, script, generated-but-unopened sheet or green subprocess exit is not visual review.

For Kinetic, Parallax and Glyphcraft sample at least every 0.5s + dense transition midpoints; Scribble at least every 1s + caption boundaries; Axiom at least every 5s + all shot boundaries and important actions/diagrams. Continuous playback is additional evidence if genuinely available; never claim it from sparse stills. Tiny final text needs individual full-size pixel inspection and a phone-size composition check.

## Retrieve references without pretending a connector worked

TikTok/YouTube connectors were unsupported at commissioning; public `yt-dlp` retrieval nevertheless worked for all six reference URLs. A normal page-fetch HTTP403 did not establish that a public clip was unavailable.

```
python3 -m pip install yt-dlp
FFMPEG_DIR=$(python3 ops/bootstrap_media.py)
python3 -m yt_dlp --no-playlist --ffmpeg-location "$FFMPEG_DIR" -o 'agents/YOURNAME/work/reference.%(ext)s' 'REFERENCE_URL'
```

Substitute your own folder and one actual URL, choose a suitable legitimate format if needed, retain source URL/creator/date/hash and keep copyrighted downloads out of Git/Releases. Do not ask for cookies/account access or bypass authentication/DRM; use public access and document any limitation. Extract with FFmpeg, open the actual frames, and record observed facts. Do not repeat the failed OpenCV decoder path for HEVC/AV1.

## Autonomous voice, no human vote

```
python3 ops/tts.py --text-file agents/scribble/work/cue-001.txt --out agents/scribble/work/cue-001.wav --voice af_heart --speed 1.0 --lang en-us
```

First run creates a cache venv, installs the tested `kokoro-onnx==0.6.1`, `soundfile==0.14.0` and their dependencies, then downloads official model-files-v1.1 assets from the upstream Kokoro ONNX repository. The producer chooses voice and delivery privately; `af_heart` is not a Director approval. British voice choices can use `--lang en-gb`. Test appropriate available voices privately and document your own decision. Never call a tool that requires the Director to select a voice; do not circumvent such a tool's consent/UI rules.

A real commissioning test produced a 24kHz, 9.076s WAV. That proves runtime/output, **not** aesthetic or perceptual listening approval. Generated speech is synthetic; record engine/model/voice/provenance. Runtime wrapper MIT, Kokoro-82M model Apache-2.0; retain appropriate notices for what you distribute. No celebrity voice cloning. Source URLs:
- https://github.com/thewh1teagle/kokoro-onnx
- https://huggingface.co/hexgrad/Kokoro-82M

Split a long script into measured sentence/scene WAVs; cache by text+voice+settings hash. Use actual durations in the timeline. Keep model files/venv in excluded cache. The helper strips crew auth variables from package-install and synthesis subprocesses. Credentials are for trusted GitHub/chatcode calls only, never third-party renderers/downloads.

## Event, heartbeat and resumed work

```
python3 ops/field.py event scribble --kind research --stage script --action 'Read three specific sources' --result '<actual claim/source findings>' --artifact 'evidence/sources.md' --next '<concrete next step>'
python3 ops/field.py publish scribble
python3 ops/field.py run scribble --stage rough-render --push -- python3 render.py --revision r01
```

Run from the repo root. The actual child runs from `agents/<name>/`. Explicit `--` separates wrapper and renderer flags. `run` records command start/end, real exit code, observed output, output byte/line counts and actual child liveness; it writes a real observation every 300s while the child exists. Partial output without a newline cannot block the observation timer. Empty/missing/nonzero commands are not success. Known crew auth variables are removed from the child environment. On interruption it terminates its child and records `stopped`.

A `process-running` observation means **that process was observed**, not that an AI is thinking, a useful frame has appeared, or the film is accepted. It is not a detached “still working” timer. No child = no process heartbeat. Use platform background-process tools when a renderer must outlive a tool call; an AI session ending is not continued autonomous execution. Keep a resumption checkpoint if it stops.

Manual creative/research/code actions need their own meaningful journal entries; publish at least every five minutes and stage boundary while genuinely active. Set `checkpoint`, `blocked`, `failed`, `stopped`, `delivered` or `not-started` truthfully. Never keep a fake activity daemon. Dashboard working records become overdue after 330s / stale after 600s; it never increments progress itself.

`HANDOFF.md` is generated from all `events.jsonl` records: use `event`, don't hand-edit generated sections. Record every meaningful action/batch, exact discoveries, failed attempts/cause/fix, commands, timestamps, tested versions, cue/scene state, actual inspections, paths/hashes and next action. Give concise reasons and results, not private hidden chain-of-thought. Archive an up-to-date copy at delivery or an unfinished stop.

`publish` stages only your own agent tree/status, rejects foreign staged changes, checks known live secrets in tracked content, commits, rebases without force, pushes and appends that source SHA to primary `storagecode/PUSHES.md`. A confirmed source push followed by a failed ledger write reports **partial sync**, not success of both. Retry after preserving state. It never uploads large media or the private brief. API reads should prefer fresh clones; don't repeatedly ask the GitHub API to read every task file.

Chatcode: claim only your commissioned goal card, renew its lease during an actual session at <=30-minute intervals, and use the standing on-shift heartbeat wire at 30 minutes. Do not initialize a fake new-agent roster row from the commissioner's session. No OCR/V01–V04/Mars prerequisite applies to these independent film commissions or to the Kinetic successor pair.

## Exact-file technical QC

```
python3 ops/media_qc.py scribble agents/scribble/renders/final.mp4 --out agents/scribble/evidence/final-technical.json
```

Checks master duration range, required landscape/portrait geometry, H.264/yuv420p, 24/25/30fps, AAC/48kHz, audio bitrate floor (target >=160kbps), measured track-end drift <=250ms, full decode, measured integrated loudness -16 +/-1.5 LUFS, true peak <=-1dBTP, bytes and SHA256. See the role brief for the exact art/story requirements. FFmpeg loudnorm can be used in a two-pass mix/export process; do not assume adding the filter guarantees the output measurement.

The CLI master ranges: Kinetic20–45s; Parallax and Glyphcraft35–55s; Scribble45–90s (target45–75); Axiom840–1080s. Kinetic's and both successors' separately required 8–12s loops need their own measured duration/decode/loudness/seam evidence; the shared hero-range gate is not the loop gate. The test fixture can bypass duration only inside the test API; it is clearly labelled and never a commissioned film. The final CLI must not skip decode/loudness to manufacture a pass.

Passing QC cannot certify story, facts, acting, typography, visual attention, music rights or perceptual listening. Perform/record actual creative inspection separately. Do not invent full playback/hearing, human ballots, retention or virality. If you cannot hear audio with your tools, do the available cue/ASR/alignment/meter checks, state the limitation and deliver a clearly labelled best candidate—not a false listened-to final.

## Publish actual media to the ONE primary archive

After code/QC/review are real and committed:

```
python3 ops/release.py scribble --video agents/scribble/renders/final.mp4 --title 'Your original title' --revision r03 --asset agents/scribble/evidence/final-technical.json --asset agents/scribble/evidence/captions.srt --asset agents/scribble/evidence/poster.png
```

All selected files must physically be inside **your** agent folder; symlinks outside it, private paths, MD packets and unexpected types are refused. Known live secrets in selected assets are refused. Release tag is immutable `frameforge/<name>/rNN-<video-sha12>`. The uploader streams large files to GitHub Releases in **storagecode only**, records actual asset URLs/bytes/SHA and server digest when available, refuses same-name mismatched replacement, writes the publication receipt + HANDOFF under `data/frameforge/<name>/<revision>-<sha12>/`, appends primary `data/INDEX.md` and `PUSHES.md`. Never rotate/rewrite an already reviewed film invisibly. Use a new revision.

The receipt explicitly labels a **published candidate**, not an accepted old-campaign film or external artistic approval. A missing server digest must be recorded as such, never invented. Confirm the resulting media link, metadata and exact hash; for crucial final acceptance independently download and verify the served bytes if feasible. A local file or successful API call alone is not an audience link.

Archive the full small-text evidence set (MD source/rights ledger, creative review, inspection manifest, chapters, HANDOFF), e.g. after recording the real delivery event:

```
python3 ops/archive.py scribble --run r03-HASH12-closeout --file agents/scribble/HANDOFF.md --file agents/scribble/evidence/source-rights.md --file agents/scribble/evidence/final-visual-review.md --file agents/scribble/evidence/inspection.json
python3 ops/field.py publish scribble
```

Use your actual hash/run identifier. `archive.py` accepts explicitly selected small text files in your own folder, rejects known crew secrets, creates the primary evidence paths and indexes them. Existing different content at the same immutable evidence path is refused; choose a new revision/run. Large images/audio/videos belong in a Release. If a network/API error leaves a partial upload, preserve the receipt, inspect existing remote assets and retry idempotently—don't duplicate releases or claim success early.

Code and live working memory remain in frameforge; durable media/evidence are on storagecode. Formalcode uses the existing reusable chatcode record workflow, not another state publisher. No paid/editor/social-account dependency. Mars remains paused. External review can happen asynchronously on the room card; it must not block making/publishing your independent film, and you must not forge quorum.

## Reproducible commissioning verification

```
python3 -m unittest discover -s tests -v
```

The offline suite currently has 20 tests: the original 18 journal/process/privacy/concurrent-publish/publication/charter/QC checks plus two successor regressions for the new agent identities, release/QC ranges, truthful not-started journal state and five-slot dashboard. A separate real toolchain fixture exercises TTS→H.264/AAC→ffprobe/full decode/contact sheets. These are **tooling tests, not any of the three promised films**. See `evidence/SETUP_VERIFICATION.json` and `evidence/COMMISSIONER_HANDOFF.md` for precise executed scope and caveats.
