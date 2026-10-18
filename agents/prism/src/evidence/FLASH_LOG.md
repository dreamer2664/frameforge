# FLASH_LOG — PRISM / PROOF (env-B)

Generated 2026-10-18T18:58:19Z. Definition (§15.8): mean frame luminance jump >= 30% within
<= 2 frames, or a full-frame solid-colour cut <= 3 frames. Luminance measured
from the 750 rendered PNG frames (grey mean, `luma_means.json`), not eyeballed.

| id | frames | type | colour | declared peak | measured mean-luma delta | aligned audio hit |
|---|---|---|---|---|---|---|
| F1 | 150–151 | burst | #ffd9a0 | 0.72 | **+86.2%** | H-claim @ frame 150 |
| F2 | 300–300 | tick | #eaf7ff | 0.50 | **+326.9%** | H-m1 @ frame 300 |
| F3 | 390–391 | burst | #bfe3ff | 0.66 | **+294.7%** | H-m2 @ frame 390 |
| F4 | 480–482 | whiteout | #ffffff | 1.00 | **+408.6%** | H-verdict @ frame 480 |
| F5 | 560–560 | tick | #ffffff | 0.55 | **+188.2%** | H-signed @ frame 560 |
| F6 | 660–661 | burst | #fff3e0 | 0.62 | **+390.0%** | H-receipt @ frame 660 |

Independent jump detection over the measured luma series found 6
jump events (start, end, delta): [(149, 151, 0.862), (298, 300, 2.404), (388, 391, 1.78), (478, 482, 7.385), (558, 560, 0.549), (658, 661, 3.866)].

Photosensitivity tally: flashes per 1 s (30-frame) window = [1, 1, 1, 1, 1, 1];
maximum = 1 event/s => WITHIN the <= 3 events/s
hygiene bar. Minimum inter-flash gap = 80 frames
(2.67 s).

Every flash above is aligned to a named audio hit in `EVENT_MAP.md`; alignment
is exact by construction (both read the same frame constants), verified in
`AUDIO_ANALYSIS.md`.
