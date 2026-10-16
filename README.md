# Frameforge

**Three original independent code-first video producers, plus two independent successors to Kinetic.**

| Producer | Original film commission | Clean public charter | Working memory | Goal card |
|---|---|---|---|---|
| **Kinetic** | Premium motion / kinetic typography, 20–45s landscape hero + 8–12s loop; own agent name instead of Claude | [KINETIC.md](briefs/KINETIC.md) | [HANDOFF](agents/kinetic/HANDOFF.md) | [e800](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261015-e800.json) |
| **Scribble** | 45–75s target vertical stickman explainer, expressive situations and deliberately researched caption typography | [SCRIBBLE.md](briefs/SCRIBBLE.md) | [HANDOFF](agents/scribble/HANDOFF.md) | [5856](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261015-5856.json) |
| **Axiom** | 14–18min landscape illustrated question film, situated characters/costumes/props, sparse keywords rather than full burned-in subtitles | [AXIOM.md](briefs/AXIOM.md) | [HANDOFF](agents/axiom/HANDOFF.md) | [d413](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261015-d413.json) |

**Historical status at initial commissioning (2026-10-15):** the three original slots were prepared with open/unclaimed cards; no new identity was registered on their behalf. Current activity is always read from the live status files and task cards; the Kinetic r03 release is a published candidate, not an acceptance claim. A prepared brief, software test or successful TTS fixture is not a finished video.


## Kinetic successor pair (commissioned 2026-10-16)

The original Kinetic r03 candidate is published and in asynchronous review; its immutable code/media are the baseline, not a live dependency. These two new producers are separate, standalone candidates with non-overlapping craft focuses. Both new cards were verified open and unclaimed; neither producer is registered or awake because a folder/card exists.

| Successor | Independent focus | Clean public charter | Starter handoff | Goal card |
|---|---|---|---|---|
| **Parallax** | Cinematic spatial typography, camera blocking, real depth/occlusion/material/light | [PARALLAX.md](briefs/PARALLAX.md) | [HANDOFF](agents/parallax/HANDOFF.md) | [8735](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-8735.json) |
| **Glyphcraft** | Expressive authored letterforms and semantically motivated glyph transformations | [GLYPHCRAFT.md](briefs/GLYPHCRAFT.md) | [HANDOFF](agents/glyphcraft/HANDOFF.md) | [c3b5](https://github.com/dreamer2664/chatcode/blob/main/board/tasks/t-20261016-c3b5.json) |

Both must create a new 35–55s 1920×1080 KINETIC hero and an 8–12s designed loop; both work independently from separate clones and leave `agents/kinetic/` untouched. The Director’s “about one-fifth” feedback is a subjective ambition cue, not a grade or hours quota. [Commissioner baseline review](evidence/KINETIC_SUCCESSORS_REVIEW.md) and its [decoded visual-sample receipt](evidence/KINETIC_BASELINE_VISUAL_SAMPLE_REVIEW.json) record the exact public hashes, observed picture stream and strict limits; no full-speed watch, audio listening or acceptance is claimed.

## Start here

- Director: give **one private stamped MD to each new AI session**. Each contains the complete standalone role + operating rules + the existing universal kit credentials. Those private files are deliberately **not in this public repository**. Do not publish them.
- Producer: read your entire charter, actual own HANDOFF and [operations](ops/README.md); register only when actually awake, claim your own card and begin. You choose topic, voice, fonts, tools, music and all edits. **No creative/voice polls for the Director.**
- Each agent uses its own clone, owns `agents/<name>/` and `status/<name>.json`, builds its own complete renderer/voice/assets and publishes its own film. No waiting for another producer, old V01–V04 tools, a paid editor or Mars.

## Observe actual work

[**Progress dashboard**](https://dreamer2664.github.io/frameforge/) · [self-contained snapshot](STATUS.html) · [raw status files](status/)

Mandatory evidence-bearing updates every <=5 minutes while actually working, plus every meaningful stage/failure/inspection/delivery. Real long render processes have a tracked-child observer. Status becomes overdue/stale by timestamp; no fake presence loop, invented percentages or claim of continued AI thought after a session ends. The dashboard fetches public status every minute in a network-enabled browser; a sandboxed file viewer shows an explicitly labelled embedded snapshot.

Every action/discovery/failure/fix/decision/resume instruction goes into the producer's **one exhaustive HANDOFF.md**, backed by append-only events. Logs distinguish the commissioner's setup from future producer actions. Keep stage evidence, commands, measured media metadata, reviews, remote links and exact continuation steps.

## Reference-informed, actually visual

[Reference study](research/REFERENCE_STUDY.md): all five TikToks and the 17:30 YouTube picture stream were retrieved; **49 actual decoded frames** were inspected, with timestamped observations and clear limits. This is sampled visual analysis, not an invented continuous audiovisual watch or exact font identification. Copyrighted source clips/stills remain outside public Git.

The two motion assets are 16:9; the three shorts 9:16. The long example uses expressive heads/hair, varied pastel settings, contextual roles/props and selective diagram/keyword text. Each agent must now inspect its own exports, not merely generate unviewed contact sheets. At least two consequential revision passes, exact-file technical checks and timecoded creative self-review precede delivery.

## Tooling that was actually proved

- Rootless FFmpeg/ffprobe, including HEVC/AV1 decode.
- Noninteractive local Kokoro ONNX voice generation: a real 9.076s WAV, no Director voice vote.
- A clearly labelled **technical fixture**, TTS→1080p H.264/AAC→full decode/loudness/hash/contact sheets. Not a film; first AAC true-peak overshoot was rejected, headroom was increased and the output remeasured.
- **20 offline safety/behaviour tests**: the initial 18 commissioning checks plus two regressions for the successor identities, status/dashboard coverage and 35–55s QC ranges ([exact run](evidence/KINETIC_SUCCESSOR_TESTS.txt)).

[Exact setup receipts/limits](evidence/SETUP_VERIFICATION.json) · [Commissioner action/failure/handoff record](evidence/COMMISSIONER_HANDOFF.md)

```
python3 -m pip install Pillow
python3 -m unittest discover -s tests -v
```

## One primary archive, no false completion

Source and live workspaces: **dreamer2664/frameforge**. Durable media/QC/rights/source/review/handoff archives: **[dreamer2664/storagecode](https://github.com/dreamer2664/storagecode)**, isolated `frameforge/<agent>/...` Release tags and `data/frameforge/<agent>/...` paths. Formalcode records source pushes automatically through the existing reusable workflow; no second empire state publisher is introduced. Retired `dreamer2664/storage` is read-only.

Final means actual complete exported/published film + inspection/QC + reproducible code + honest limitations—not a pitch, script, engine PR, calibration clip, green tests or shift ending. External room review can occur asynchronously; never forge ballots. These are separate commissions, **not automatically accepted entries in the older ten-film campaign**.

**OUTPOST MARS and its PC/Windows bridge remain paused.** Never touch captchaproject/captchaprogram. Preserve secrets and append-only evidence. Make good films; report only what actually happened.
