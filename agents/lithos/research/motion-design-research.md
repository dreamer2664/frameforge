# Motion design research digest (2026-10-17)

Collected for the KINETIC successor commission. Sources cited with URLs.
Practical rules are quoted as measured thresholds wherever the sources give
numbers — these become the timing spec of the new film.

## 1. Timing & readability (kinetic typography)

* Stagger granularity: lines 60–100 ms apart, words 40–70 ms, characters
  20–40 ms; 30–50 ms/char feels fluid, 100 ms+ dramatic. Cap total reveal
  ≈ 800 ms; each fragment 400–600 ms. — https://www.iart.ai/blog/how-to-animate-text ,
  https://studiomeyer.io/en/blog/kinetische-typografie
* Text must stay readable ≥ 0.5 s after settling; "seconds = (chars ÷ 12) +
  0.5, round up to 0.25 s" display-time formula. — https://www.ikagency.com/graphic-design-typography/kinetic-typography/ ,
  https://gabrielpulecio.com/what-is-kinetic-typography/
* Micro-entrances/exits 200–400 ms eased; feature beats 600–1200 ms. At 30 fps
  displacements > 20 px/frame read as "fast" — use anticipation + overshoot if
  a longer travel is required. — https://gabrielpulecio.com/what-is-kinetic-typography/
* Ease-out for entrances (decelerate into place), ease-in for exits
  (accelerate away). Reveal 0.3–0.8 s total. — https://trydemotion.com/blog/text-animation-secrets
* Recipe-level vs selector-level easing: one curve shapes the whole move,
  another shapes the stagger wave distribution. — https://vertex.art/blogs/typography-animation-kinetic-typography
* Short phrase (3–7 words) ≈ 1–1.5 s on screen; medium 1.5–2.2 s.
  — https://www.aicoursify.com/blog/crafting-kinetic-typography-for-key-takeaways
* Lock the copy first, then choose/set the audio, then build a beat sheet and
  land phrases on the track's accents. — https://www.moonb.io/blog/kinetic-typography
* Per-letter animation is expensive for legibility: reserve it for the 2–3
  words that carry the most weight; prefer moving the frame (camera) over
  moving the letters. — https://pexo.ai/tutorial/how-to-make-a-kinetic-typography-explainer-video

## 2. Transitions (whips, smears, streaks)

* Whip anatomy: accelerate → peak-velocity smear → cut/handoff AT the peak →
  decelerate into the next shot. Directional blur angle must match the motion
  direction or the brain rejects it. — https://olafmotion.com/tutorials/how-to-create-smooth-transitions-in-after-effects-step-by-step-guide/
* Echo-based smears (many tiny-interval echoes) look better than vanilla
  motion blur for mograph ("much less artificial and cheap").
  — https://www.reddit.com/r/AfterEffects/comments/1gk8ly5/ ,
  Skillshare "Mograph Smears - Quick Tricks"
* Match brightness/color across the whip points to hide the cut; keep speeds
  balanced in and out. — https://nofilmschool.com/how-to-do-a-whip-pan
* Blur direction + length keyed to velocity (speed-reactive streaks);
  Motion Tile/Mirror edges before blurring so edges don't go transparent.
  — https://www.joinyashi.com/resources/after-effects , r/premiere
* Smear & Trails effects: smear angle follows the layer's motion path; trail
  type "streaks" for speed lines. — https://motiondesign.school/blog/smear-and-trails-in-after-effects/

## 3. Rhythm & structure

* First second must earn attention (short-form rule); bold beats + tight
  pacing carry silent playback. — https://www.neue.world/insights/what-is-motion-design-a-complete-introduction
* Snappy motion = playful/fast/urgent; pauses = emotional weight; motion is
  the second narrator. — https://www.todaymade.com/blog/kinetic-typography-examples
  (Apple "Don't Blink" case)
* 2025–26 look: bold typographic maximalism (letters as the hero image),
  vertical-first composition, fluid/organic easing with soft rebounds,
  audio-reactive type, dimensional type in layered 3D space.
  — https://www.fontfabric.com/blog/10-design-trends-shaping-the-visual-typographic-landscape-in-2026/ ,
  https://medium.com/@identicube/design-trends-in-2025-that-are-redefining-animation-motion-graphics-identicube-24951e8e2c38
* Accessibility floor: no flashing > 3 Hz, keep contrast ≥ 4.5:1 during
  transitions too (partial states count). — https://educationalvoice.co.uk/creative-kinetic-typography/

## 4. Applied to this commission

* The new film runs at 30 fps like the reference (20 px/frame speed ceiling).
* Type cadence: brand wordmark ~15 chars/s (reference-matched); body prompts
  12–15 chars/s with the accent-color decay on new glyphs.
* Every event lands on a measured audio onset; holds 0.7–1.2 s; one 1.2 s
  anticipation before the color flip.
* Transitions: 2 whip-smears (0.2 s), 1 hard cut on action, 1 streak exit.
  Smears via stacked sub-frame echoes along the motion vector.
* Structure: logo bookend + wordmark → tool strip → click → console prompt →
  generation rain → result orbit → second prompt → palette flip → result orbit
  → logo outro (mine: LITHOS mark).
