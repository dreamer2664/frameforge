# Kinetic reference study — observed motion and design principles

Study performed 2026-10-15 from public clips retrieved with `yt-dlp` 2026.8.19 and decoded using FFmpeg 7.0.2-static. The two original downloaded MP4s are retained only under ignored `agents/kinetic/work/refs/`; no frames, audio, logos, text, or code from them are used in the film.

## Retrieval and inspection record

- Reference A: `https://vm.tiktok.com/ZN8SAhoXP/` redirected to `@zensu.visuals/video/7670123707980991776`. FFprobe: 13.000998 s, 1024×576, 30 fps, H.264/AAC. Decoded one JPEG every 0.5 s, 26 frames from 0.00 through 12.50 s; opened the actual full contact sheet at `work/refs/ref1_sheet.jpg` (1200×2295) and the actual first frame at `work/refs/ref1_frames/f_0001.jpg`.
- Reference B: `https://vm.tiktok.com/ZN8SARgMg/` redirected to `@robiimotion/video/7676881388053777686`. FFprobe: 17.000 s, 1280×720, 30 fps, HEVC/AAC. Decoded one JPEG every 0.5 s, 34 frames from 0.00 through 16.50 s; opened the actual full contact sheet at `work/refs/ref2_sheet.jpg` (1200×3060).
- Exact extraction commands used `python3 -m yt_dlp --no-playlist --ffmpeg-location /home/user/.cache/frameforge/bin -o 'agents/kinetic/work/refs/refN.%(ext)s' <public-short-url>`. FFmpeg decode used `fps=2,scale=<native width>:<native height>`.
- Limitation: this was timecoded still inspection, not continuous playback. Timing between samples and precise cut frames are bounded to the 0.5-second sample interval. Audio tracks were not perceptually listened to; no soundtrack or sound claim is inferred from their presence.

## A — “Motion Design for Claude”, 13.001 s

| Approx. time | What is visible in the decoded sample | Motion / cut confidence |
|---|---|---|
| 0.00–0.50 | Near-black field with large folded amber/orange luminous ribbons; a small radial accent and light wordmark enter by 0.50. | Strong light-to-mark reveal, but only sampled every half second. |
| 1.00–2.00 | The warm shapes pull back; compact outlined chips (Create / Write / Code / Life Stuff / Learn) assemble into a row, with a pointer visible around 2.00. | Chip row is a coherent intermediate state, not a static hero screen. Exact ease/cursor trajectory unmeasured. |
| 2.50–4.00 | Palette drops toward black. A small composer appears; prompt grows from short partial text around 3.00 to a longer line by 4.00. | Interface enters quickly; actual typing/cut cadence is only coarsely sampled. |
| 4.50–5.50 | Code-like material briefly becomes a small floating/tilted block, then resolves into a warm amber rounded website card reading “Premium Motion Design.” | Clear content-to-object transition; card/border is the payoff. |
| 6.00–8.50 | Card holds while the prompt changes; warm amber card and surrounding light transition to blue/purple. | The color change moves the same card concept forward; it is not an unrelated scene reset. |
| 9.00–10.00 | Blue card holds, then disappears into a lone warm radial accent on black. | Distinct end-signature chapter. |
| 10.50–11.00 | Small centered mark with short “Built with …” end copy, then a quiet dark tail at 11.50–12.50. | End copy resolves and leaves negative space; final black sampled, not assumed to be intentional design. |

**Transfer, not imitation:** light can become a control, a line of text can become an object, and an object can carry a new color state. Kinetic instead uses one continuous filament to turn a point into a route, rhythm, frame, then an original K signature. It uses no chip labels, Claude/Anthropic marks, copied interface, copied script, or source soundtrack.

## B — “Meet Claude”, 17.000 s

| Approx. time | What is visible in the decoded sample | Motion / cut confidence |
|---|---|---|
| 0.00–2.50 | Black field, warm glow low in frame and one small warm point. Fine centered italic text appears and changes over the opening seconds; the bright point tracks the line. | restrained, small-scale opening before the large type moment; exact point speed not measured. |
| 3.00–3.50 | Oversized italic phrase grows/crops across frame; warm white moves toward a cool mint tint in the sampled frames. | An intentional macro-scale jump is visible. The precise ease is unknown. |
| 4.00–5.50 | Hard palette inversion to pale cream; a centered warm radial mark rotates/changes orientation and settles. | Distinct color-state transition, sampled at 0.5-second intervals. The mark is not reused. |
| 6.00–7.00 | The pale image dims; warm mark returns on a dark field and a fine-bordered composer appears. | Light → mark → restrained UI hand-off. |
| 7.50–9.00 | Composer widens; a small prompt appears; a dropdown/control is shown. | UI is fine and quiet. No copied dimensions or labels are used. |
| 9.50–11.50 | Large serif “Welcome, Robi” sits above a dark outlined composer; the composer changes content and object state underneath. | Contrast between expressive serif headline and small UI sans is clear. |
| 12.00–14.00 | Warm icon/object transition into a text/code response panel. | Content panel carries the same story into a new state. |
| 14.50–15.50 | Bright pale field with a small centered orange tile; then a quiet dark frame at 16.00–16.50. | Small endmark/word at center is an abrupt scale reduction; timing needs actual playback to judge. |

**Transfer, not imitation:** carefully change scale, reserve small UI for secondary information, contrast an expressive display face with a legible sans, and use a purposeful palette inversion. Kinetic uses its own restrained warm-to-paper-to-night cycle and an independently drawn monogram.

## Kinetic motion decisions

1. No unrelated preset cuts: the same bright point and its drawn filament are the continuity object across eight beats.
2. Reveal order is meaningful: point → line → word rhythm → drawn frame → opened space → K monogram.
3. The film uses a warm ink opening, a brief paper/cool-light inversion during the “frame opens” beat, and a return to warm night for the payoff and signature.
4. Type is wiped by the travelling seam; “A thought” becomes “A world” in the same typographic slot. These are masks tied to the illustrated path, not generic opacity fades.
5. User interfaces are not needed for this concept; no fake product controls, prices, model labels, feature claims, or live service are depicted.
6. The reference sound cannot be evaluated from these stills, so the film uses a newly synthesized, procedural score and authored transition accents.

## Evidence coverage / limitation

- Both full contact sheets were opened and reviewed; they contain chronological samples at 2 Hz across the full durations, 60 total decoded frames. One full-resolution first frame of A was additionally opened.
- No continuous playback, original audio listening, exact reference font identification, or frame-accurate cut/ease analysis is claimed.
- This is a principle study, not an asset pack. Copyrighted source files and extracted samples remain outside Git and are not deliverables.
