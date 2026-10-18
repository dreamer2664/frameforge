# Reference analysis — vm.tiktok.com/ZN8S7WKHd

Source under study: the linked TikTok, `@neildegracce/video/7696876445888466198`.
It was downloaded once for private study (`/home/user/ref/tiktok/`, outside every
clone and outside Git) and **no frame of it is redistributed** in this
repository, in the release, or in the archive. What follows is a written
analysis of *technique* - the thing a 1:1 replica has to match.

## Measured facts

| property | value |
|---|---|
| duration | 14.0667 s (844 frames) |
| raster | 1920x1080, 60/1 fps, HEVC + AAC 44.1 kHz |
| loudness | peak 0.686, RMS 0.111 |
| transients | 0.5, 1.5, 3.75, 5.25, 6.0, 7.5, 9.0, 9.75, 11.25, 12.25 s |

Palette, sampled per frame from the decoded file (top -> bottom of frame):

```
backdrop      #9d9891 (y=20)  ->  #63615d (y=1070)
floor bloom   #a75d31
accent orange #f86838 (cards) / #ff841a (hot) / #fe7647 (wordmark)
letters       #37363d      caption #e3e3dc
cream board   #e8e0d8 / #e0e0d8
app surfaces  #202820 / #282828, titlebar #7c7a76
```

## Beat sheet (reference seconds)

| t | beat | what happens |
|---|---|---|
| 0.00-0.45 | empty plate | defocused studio, cool grey-green, no elements |
| 0.45-1.75 | chrome type | heavy extruded word on a glass slab, letters fly in one by one, warm floor bloom |
| 1.75-2.05 | scale-through | the word becomes a giant thin-stroke outline and blows past camera |
| 2.05-3.65 | squash & stretch | glossy orange ball bouncing rightward on a white baseline, dotted motion path, orange diamond keyframes, caption |
| 3.65-3.95 | cut to the app | dark dotted-grid field, an editor window materialises |
| 3.95-5.45 | the editor | viewport running the same scene + an easing graph (channels, curve, playhead, keyframes), live time/frame readout |
| 5.45-6.25 | back to the studio | the ball flattens and streaks, "Morph." caption |
| 6.25-7.35 | morph | a chrome turbine disc with a hot orange core |
| 7.35-7.58 | flash | one frame of full orange |
| 7.58-9.90 | the light board | a cream plane of UI primitives (type specimen, orange card with three dots, glass cube, stripes, bars, a curve) with a dolly and depth of field |
| 9.90-10.35 | odometer | the digits roll |
| 10.35-11.05 | stat card | "900 frames." + a smaller line, last digit orange, on a white card over blurred giant numerals |
| 11.05-11.50 | scatter | the board's pieces fly apart |
| 11.50-12.55 | wordmark | letters assemble out of blur on the cream |
| 12.55-14.07 | fade to black | mean luma 226 -> 8.8 |

## Technique inventory (what a replica must reproduce)

1. A photographic, defocused studio plate with a warm floor bounce - not a flat fill.
2. Extruded display type whose material is read through *light*, not through a colour.
3. A glass slab in front of the type that refracts what is behind it.
4. Physics with squash and stretch, and a trail that stretches with speed.
5. A motion path drawn as a dotted spline with **keyframe diamonds on the baseline** -
   the path is the animation, not an annotation of it.
6. A motion editor as a real UI: titlebar, tabs, a live `t / frame / fps` readout,
   a channel list, an easing curve that changes from linear to eased, a playhead.
7. The viewport inside the editor shows *the same scene* as the film.
8. A morph that turns one object into another material, not a cut.
9. A single-frame full-colour flash used as a chapter break.
10. A light "board" of UI primitives in perspective with a real dolly and depth of
    field - the primitives are the product being sold.
11. An odometer that rolls to the real frame count of the piece.
12. A wordmark that assembles with motion blur and then sits on a fading ground.

## What belongs to the reference and must NOT be reused

The word shown in chrome, the creator's name on the end card, the exact caption
wording, the file name in the titlebar, the label set of the primitives and the
music. A replica that reuses any of those is a copy, not a replica.

`cadence` replaces every one of them: see `design-and-build.md`.
