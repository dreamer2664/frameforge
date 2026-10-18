# EVENT_MAP — PRISM / PROOF (env-B)

Master timeline. 750 frames @ 30 fps = 25.00 s. Every visual event, flash and
audio hit below reads the SAME frame constants (`film/events.js`, exported to
`evidence/events.json`); the audio synth places hits at
sample = round(frame/30*48000), so picture/sound alignment is exact (0 samples).

## Acts
| act | frames | seconds | title | picture |
|---|---|---|---|---|
| I | 0–179 | 0.00–6.00 | THE CLAIM | amber field: dust, glow, scanline; type asserts |
| II | 180–449 | 6.00–15.00 | THE MEASUREMENT | ice instrument grid, specimen, ring, counters |
| III | 450–659 | 15.00–22.00 | THE VERDICT | white-out, exploded diagram, hero PROOF, stabs |
| IV | 660–749 | 22.00–25.00 | THE RECEIPT | paper receipt card, acceptance-pending kicker |

## Text moments (11)
| id | string | in | out | cap px | mode | anchor (x,y) |
|---|---|---|---|---|---|---|
| T1 | SIGNAL // UNVERIFIED | 8 | 92 | 40 | type | left (168,966) |
| T2 | A CLAIM IS NOISE. | 40 | 176 | 96 | track | center (960,540) |
| T3 | FRAME 000/750 | 196 | 442 | 44 | counter | right (1752,132) |
| T4 | dLUMA +38.2%  DRIFT 0.004px | 236 | 372 | 40 | fade | left (168,132) |
| T5 | MEASURE EVERYTHING. | 330 | 446 | 78 | track | center (960,852) |
| T6 | PROOF | 483 | 656 | 255 | slam | center (960,470) |
| T7 | MEASURED. | 500 | 528 | 64 | stab | center (960,700) |
| T8 | REPRODUCIBLE. | 530 | 558 | 64 | stab | center (960,700) |
| T9 | SIGNED. | 560 | 596 | 64 | stab | center (960,700) |
| T10 | RECEIPT | 668 | 749 | 56 | fade | left (510,300) |
| T11 | INDEPENDENT ACCEPTANCE PENDING. | 700 | 749 | 44 | fade | center (960,962) |

## Flashes (6)
| id | frame | dur | type | colour | peak | audio hit |
|---|---|---|---|---|---|---|
| F1 | 150 | 2 | burst | #ffd9a0 | 0.72 | H-claim |
| F2 | 300 | 1 | tick | #eaf7ff | 0.5 | H-m1 |
| F3 | 390 | 2 | burst | #bfe3ff | 0.66 | H-m2 |
| F4 | 480 | 3 | whiteout | #ffffff | 1 | H-verdict |
| F5 | 560 | 1 | tick | #ffffff | 0.55 | H-signed |
| F6 | 660 | 2 | burst | #fff3e0 | 0.62 | H-receipt |

## Audio hits (12)
| id | frame | time s | kind |
|---|---|---|---|
| H-t2 | 40 | 1.3333 | slam |
| H-claim | 150 | 5.0000 | impact |
| H-m1 | 300 | 10.0000 | tickhard |
| H-t5 | 330 | 11.0000 | slam |
| H-m2 | 390 | 13.0000 | impact |
| H-verdict | 480 | 16.0000 | drop |
| H-proof | 483 | 16.1000 | slam |
| H-stab1 | 500 | 16.6667 | stab |
| H-stab2 | 530 | 17.6667 | stab |
| H-signed | 560 | 18.6667 | tickhard |
| H-receipt | 660 | 22.0000 | stamp |
| H-last | 744 | 24.8000 | tick |

## Music structure
| section | frames | seconds | content |
|---|---|---|---|
| drone | 0–179 | 0.00–6.00 | 55 Hz detuned drone + sub, sparse calibration ticks |
| build | 180–449 | 6.00–15.00 | 120 bpm quarters (every 15 f), hats on 8ths, pad, riser 300→480 |
| verdict | 450–659 | 15.00–22.00 | sub drop + crash @480, pad, three stabs @500/530/560 |
| receipt | 660–749 | 22.00–25.00 | warm pad, stamp @660, final tick @744, 0.35 s design fade |

## Camera
| act | move | curve |
|---|---|---|
| I | dolly z 26→15, y 0.4→0.2 | inOutQuint |
| II | orbit r19, a −0.55→1.35 rad, y 6.5→3.0 | inOutCubic |
| III | push z 22→13.5 | outQuint |
| IV | static (receipt card) | linear |
Impact shake (seeded value-noise, decaying 16 f) on H-claim/H-m2/H-verdict/H-receipt.
