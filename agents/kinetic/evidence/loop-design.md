# Separate motion loop — design and seam plan

## Concept

A calm, repeating field from the same ink/ember/cool-glass system: the phrase “Ideas, in motion.” remains still and readable while two fine ellipses orbit at different radii, one warm and one cool, each with one travelling point and a short restrained trail. It is not a hero excerpt; it is composed as a continuous state. The screen contains no controls, fake product UI, captions or external assets.

## Exact cycle decision

The loop duration is **10.24 s**, deliberately chosen to align the three timebases rather than rounded to a decorative 10.0 s:

- 256 picture frames at 25 fps = 10.24 s.
- 491,520 PCM samples at 48,000 Hz = 10.24 s.
- 491,520 / 1,024 = 480 AAC access frames, with no partial audio packet at the cut.
- Every generated oscillator completes an integer number of cycles over 10.24 s. Its breath envelope, moving points, trail opacity, and background-light phase all use the same 10.24-second period.

The underlying frame function was preflight-tested at t=0 and t=10.24: decoded source-frame pixel difference is exactly zero. Its last-to-first 25fps source-frame mean absolute delta is 0.09033, versus 0.08409 for first-to-second (ratio 1.0742); this is source math only, not yet an exact MP4 seam pass.

## Actual-media gate still pending

The source-level check does not certify the encoded loop. After export, probe exact MP4 geometry/codecs/duration and full decode; measure AAC loudness/true peak; decode consecutive copies; inspect dense frames around 10.24 s; compare video motion delta and decoded audio sample discontinuity at the wrap. No perceptual audio listening is claimed. Record exact hashes and results here after the actual loop file exists.
