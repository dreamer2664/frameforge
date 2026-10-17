# Revision 1 — graded iris / vault chiaroscuro (lithos)

**Stage:** hard-shot r00 (8.000 s, 1920x1080, SHA 93bb967a7188fbff...) was
rendered, muxed with the score and measured before the full render.

**Symptom (measured, not assumed):** the vault beat (t = 0–3.5 s) — designed as
a dark letter-interior mystery hook with a sweeping blade of sun — measured
luma 0.41–0.66 with **dark% 0.0** across the whole beat: the sunlit bite of
the C reads flat and open, with no chiaroscuro and no deep value anchor. The
blade's motion was present (inter-frame residual 0.04–0.21 in the beat) but
the value story was not.

**Change:** a timeline exposure key (`exposure_keys` in storyboard.json, wired
through `scene.exposure_at(t)` → `post.finish`): 0.42x through the vault,
0.44 at 2.8 s, ramping 0.78 at 4.6 s to 1.0 by 6.5 s — the eye adapts as the
camera exits the letter. Render + preview pipelines both honour the key.

**After (1280x720 previews, measured):**

| t | luma before | luma after | dark% after | p90 after |
|---|---|---|---|---|
| 0.5 | 0.658 | 0.444 | 0.0 | 0.673 |
| 2.0 | 0.613* | 0.403 | 0.0 | 0.534 |
| 3.2 | — | 0.453 (blade bump) | 0.0 | 0.647 |
| 5.0 | 0.597 | 0.565 | 11.3 | 0.750 |

(*before-value at 2.0 s from the hard-shot 0.5 s grid; the 1280x720 preview
runs are not pixel-identical to the 1080p encode but the means agree to ~0.02.)

The whole opening beat is ~35% darker with a clear emergent ramp into light —
a change any viewer would notice. The exit beat now carries 11% deep shadow
(the C's shade side) where the opening carries none.

**Not changed:** camera, geometry, type, light rig, score. The hard-shot video
is superseded by the r01 master (same pipeline including this grading); the
superseded hard-shot numbers above stay in the record as the "before".
