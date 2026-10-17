# SUCCESSOR HANDOFF — "give language a body" (a second parallax-style spatial-typography film)

**Who this is for.** A successor agent who has been handed the same commission:
build one original 35–55 s 1920×1080 **KINETIC** hero film plus a deliberately
designed 8–12 s **seamless loop**, in its own folder, with a real 3D /
depth-aware visual system, typography as a physical object, a composed original
score, two consequential revision passes, an honest exact-file review, and a
real publication to `dreamer2664/storagecode`.

**Who wrote it.** `parallax` (production identity of the first film in this
line). Everything below is first-hand: every command was actually run, every
number was actually measured, every failure actually happened.

**Read this file end to end before you touch anything.** The fastest part of
this job is not the rendering — it is the ten minutes of reading, because
almost every expensive mistake below was made *before* reading.

---

## 0. TL;DR — the ten commands that matter

```bash
# 0. arm yourself (credentials, clones, name)
export FRAMEFORGE_KIT=/absolute/path/to/YOUR_PRIVATE_KIT.md   # <- your stamped packet
python3 - <<'PY'
import os,re
from pathlib import Path
kit=Path(os.environ['FRAMEFORGE_KIT']).read_text()
keys=dict(re.findall(r'^(CHATCODE_TOKEN|GITHUB_TOKEN)=([^\s]+)$',kit,re.M))
assert set(keys)=={'CHATCODE_TOKEN','GITHUB_TOKEN'} and all('PENDING-ISSUE' not in v for v in keys.values())
p=Path.home()/'.private'; p.mkdir(exist_ok=True); p.chmod(0o700)
(p/'parallax.env').write_text(''.join(k+'='+v+'\n' for k,v in keys.items())); (p/'parallax.env').chmod(0o600)
ask=p/'frameforge-askpass.sh'
ask.write_text('#!/bin/sh\ncase "$1" in *Username*) printf "%s\\n" x-access-token ;; *) printf "%s\\n" "$GITHUB_TOKEN" ;; esac\n'); ask.chmod(0o700)
PY
set -a; . ~/.private/parallax.env; set +a
export GIT_ASKPASS=$HOME/.private/frameforge-askpass.sh GIT_TERMINAL_PROMPT=0
export CHATCODE_AGENT=parallax
git clone https://github.com/dreamer2664/frameforge.git
git clone https://github.com/dreamer2664/chatcode.git
git clone https://github.com/dreamer2664/storagecode.git
for r in frameforge chatcode storagecode; do git -C "$r" config user.name parallax; git -C "$r" config user.email parallax@chatcode.local; done
python3 chatcode/bin/chatcode init --name parallax
python3 chatcode/bin/chatcode whoami

# 1. claim your card (a lease, not a promise) and keep it alive every 30 min
python3 chatcode/bin/chatcode tasks claim t-20261016-8735 --hours 6
python3 chatcode/bin/chatcode tasks heartbeat t-20261016-8735 --note "real checkpoint"

# 2. toolchain
python3 -m pip install numpy scipy fonttools Pillow mapbox_earcut
python3 frameforge/ops/bootstrap_media.py          # -> ~/.cache/frameforge/bin/{ffmpeg,ffprobe}

# 3. THE FILM: copy agents/parallax/px/ into your own folder and run it
cd frameforge/agents/parallax/px
python3 audio.py --out work/audio                 # ~6 s
sh work/render_hero.sh                            # ~95 min at 1920x1080
sh work/render_loop.sh                            # ~20 min
sh work/endgame.sh                                # mux + proxy rough cuts

# 4. measure
python3 qc.py --hero work/renders/hero-master.mp4 --loop work/renders/loop-master.mp4 \
              --out work/qc --frames --dense --gate --source-loop work/audio/loop.wav
python3 ../ops/media_qc.py parallax work/renders/hero-master.mp4 --out work/qc/media-qc-hero.json

# 5. publish + archive (see §12 for the exact command)
python3 ../ops/release.py parallax --video ... --asset ... --title "..." --revision r01
python3 ../ops/archive.py parallax --run r01-<hash12> --file ...
```

Everything else in this document is the context that makes those commands
work the first time.

---

## 1. The job, precisely

### 1.1 The deliverable

| | required | what I shipped |
|---|---|---|
| hero | 35–55 s, 1920×1080, 16:9 | **40.000 s**, 1920×1080, 24 fps, 960 frames |
| loop | 8–12 s, seamless | **9.600 s**, 1920×1080, 25 fps, 240 frames |
| brand on screen | KINETIC only | KINETIC only; the production identity `parallax` never appears in the film |
| container | MP4 H.264 / yuv420p, faststart | yes, `moov` before `mdov`… before `mdat` |
| audio | AAC 48 kHz ≥160 kbit/s | 207 kbit/s (hero) / 195 kbit/s (loop) |
| loudness | ≈−16 LUFS ±1.5 | **−16.1 LUFS** both |
| true peak | ≤ −1 dBTP | −6.9 dBTP (hero), −11.1 dBTP (loop) |
| A/V tail | mismatch ≤ 250 ms | **0.000 s** (video and audio both end at exactly 40.000 s) |

### 1.2 The gates (all of these must be provable, not asserted)

1. **Cold study of the predecessor** (Kinetic r03): decode the *published*
   bytes, verify their SHA-256, open real frames, and write down what is
   actually wrong with it. My r03 study: 54 decoded frames, three contact
   sheets opened with vision, the verdict was "entirely planar 2D — point →
   line → word → frame, a static 3.5 s end card, no camera, no occlusion, the
   type is never an object."
2. **Compare ≥3 materially different spatial concepts privately**, then commit
   to one in writing. Mine are in `agents/parallax/px/evidence/concept-commitment.md`
   (A: a single monolithic type object; B: a typographic city; C: a stone hall
   where the word is carved, released, becomes a gate, and re-forms on a
   plinth — C won).
3. **Hard-shot proof**: a *real* 5–10 s 1920×1080 MP4 with sound, muxed and
   inspected, not a still. Mine: `work/evidence/hardshot-8s-1080p.mp4`
   (8.000 s, 1920×1080, 24 fps, AAC 48 kHz).
4. **A complete rough cut of both** hero and loop. Mine: 960×540 proxies
   (`work/rough/hero-rough-cut.mp4`, `loop-rough-cut.mp4`) produced from the
   *final* masters so the proxy is the real edit.
5. **Two consequential revision passes** with before/after evidence (I did
   three). Each pass must change something a viewer would notice, and each
   must be *recorded* (see §10 for the three).
6. **Exact-file review of the final MP4** every ≤0.5 s, plus dense 0.1–0.2 s
   samples at the transitions, plus full-size frames, plus a 640×360 phone
   check, and an explicit statement that no continuous playback was possible.
7. **Loop gate on the encoded MP4** (not on the source): geometry, position,
   velocity, light phase, audio seam — with exact numbers.
8. **Publish** hero + loop + poster + code/config + manifests + licences +
   receipts + review + handoff to `frameforge` and `storagecode`, and verify
   the remote bytes/hashes.

### 1.3 The craft bar (this is where the work actually is)

* Real depth: purposeful near/mid/far planes, perspective, occlusion, and a
  camera move that *reveals information*. A flat-card parallax filter is
  explicitly insufficient.
* Typography as a designed spatial object: correct spelling, real-size
  readability, extruded/physical presence, used as architecture.
* Coherent art direction: material, scale, light, atmosphere, colour.
  Restrained glow. Controlled DOF. Purposeful motion blur. **No generic
  AI-neon.**
* ≥3 meaningfully different spatial/choreographic moments plus a memorable
  reveal. A first-second hook. An intentional final image.
* Original composed sound; narration optional; the voice is chosen privately
  (never ask Carlo). **No claim of listening that did not happen.**

### 1.4 The laws that are not negotiable

* Never publish, commit, archive, screenshot or wire the private stamped kit
  (KIT-DBF340). Never put the GitHub token in a repo, a release, an
  `events.jsonl` line, a chatcode note or an ntfy message. The wires and the
  repos are public.
* Do not touch `agents/kinetic/`; do not claim Kinetic's identity; do not
  edit another producer's folder or `status/*.json`.
* New code → `frameforge`. Durable media/data/receipts → `storagecode`
  (the only primary archive). `dreamer2664/storage` is retired/read-only.
* Immutable release tags `frameforge/<agent>/rNN-<hash12>`; append-only to
  `storagecode/data/INDEX.md` and `PUSHES.md`. No force-push, no reusing
  another producer's tag.
* Truthful heartbeat: an evidence-bearing update every ≤5 minutes and at
  every stage transition. During long commands, monitor the *real* child
  process. **Never fake progress, listening, playback, metrics or external
  approval.** Record a pending sync honestly if the network fails.
* Card `t-20261016-8735` in `dreamer2664/chatcode`: renew the lease every
  ≤30 minutes, and finish in `review` with real links. Never forge a quorum
  ballot, never mark it `done` improperly.
* `captchaproject` / `captchaprogram` are never touched. The 98/95 wall is
  never manipulated. OUTPOST MARS and the Windows/PC bridge stay paused. No
  reward-chasing.

---

## 2. What I built (so you can go further, not just repeat it)

### 2.1 The film

*Title:* **KINETIC — "Give language a body"**.

A word is carved into the end wall of a dark stone hall. A raking shaft of
light travels along the stone and finds the letters one by one, each throwing
a long shadow across the wall. Then the stone lets go: the letters hinge out
of the wall, float into the hall as a field of monoliths at seven depths,
swing together into a monumental doorway made of type, and the camera
accelerates through that doorway into a warm chamber — where the letters have
landed as a row on a plinth, upright, lit, and the promise is written in light
on the stone.

The reveal is diegetic: **the gate *is* the word**.

### 2.2 Structure (the revised timings)

| beat | s | space | what the frame must do |
|---|---|---|---|
| hall | 0.0–4.2 | deep hall, piers near, slot of light at x = 12.4 m, amber doorway at the left | establish scale and the one hard source; hook inside the first second |
| wall | 4.2–12.2 | the carved word on the rear wall (z = −4 m) | the light finds the letters; the word assembles in stone |
| release | 12.2–19.4 | the hall full of floating letters at seven depths | the stone lets go; the nearest letter sweeps the lens |
| gate | 19.4–26.4 | the letters align into a 6.8 m wide letter-gate at z = −3 m | the word becomes architecture; the camera goes through it |
| monument | 26.4–40.0 | a warm chamber: graded back wall at z = −34 m, side walls at x = ±20 m, two piers, a plinth | the word re-forms as an object; the final image holds and breathes |

### 2.3 The world in numbers (all in `storyboard.json`)

```
rear wall      z = -4.0 m          arch opening x = -6.4 … -2.8 m, y = 0 … 6.4 m
carved word    x = -1.899 0.293 1.170 3.338 5.214 7.229 8.013 m   (11.8 m wide)
               cap 2.0 m, base y = 0.90 m, extrusion depth 0.5 m
bench          x = -2.5 … 10.5 m, top y = 0.9 m
slot of light  x = 12.4 m, y = 5.2 … 13.0 m
piers          x = ±12.0 m at z = 20, 12, 4 m
letter-gate    two columns (x = -8.0, -1.2 m) x three rows (y = 1.0, 3.7, 6.4 m)
               + the C as the keystone at (-4.6, 8.2, -3.0)
plinth         z = -16.4 … -15.0 m, top y = 1.20 m, 13.4 m wide
chamber        back wall z = -34 m, side walls x = ±20 m, ceiling y = 13 m,
               piers at x = ±9.6 m, z = -20 m
camera         13 keys, fov 36°–48°, spline-interpolated
lights         1 shadow-casting warm key (rotating rake) + cool fill + soft wash
               + grazing wall rake + travelling point light + 4 practicals
fog            density 0.026 → 0.015, cold blue-black → warm brown
```

### 2.4 The honest note on the walls (the one thing the reviewer noticed)

> *"the walls were bugging out and moving around"*

You will see this too, and you should know it is **not** geometry moving:
it is the *light* moving on a flat surface. Three things conspire:

1. the **travelling band of light** on the rear wall (the 6.4 m warm band that
   follows the light that finds the letters) slides across a completely flat
   wall — the eye reads a moving texture on a flat plane as the plane moving;
2. the **letters' shadows** slide across the same wall as the letters hinge
   out, which is a second, faster-moving pattern on the same flat plane;
3. the wall is **flat and untextured in value** apart from the stone grain, so
   there is no static reference (a course line, a recess, a change of
   material) to anchor the eye and prove the wall is standing still.

**Fixes I would try next time** (in order of cost):

* give the wall **static architectural relief** — a course line, a recessed
  panel, a chamfered edge — so the eye has a fixed reference while the light
  moves across it (cheapest, biggest win);
* make the travelling band **narrower and dimmer**, or give it a soft, fixed
  falloff at its trailing edge so it reads as light rather than as texture;
* **shorten the band's travel** or replace the wall sweep with a *static*
  raking light and a moving *shadow* only (a moving shadow is a classic
  depth cue; a moving band of illumination on a flat wall is not);
* break the wall plane with the **piers crossing the light** (already in the
  scene, but the band washes over them) so the light has edges to die against.

If you reuse this scene, do this first — it is a five-minute geometry change
and it removes the only thing a reviewer picked out of the whole film.

---

## 3. The environment (measure before you trust)

### 3.1 The box

| resource | value | consequence |
|---|---|---|
| CPU | **2 cores** (nproc = 2) | one 1080p render ≈ 1.15 cores; a second parallel render will not fit |
| RAM | **1.98 GB total, ~470 MB available** with one render running | **two renders in parallel = OOM kill** (I lost one attempt this way: exit 137) |
| swap | none | an OOM kill is immediate and total |
| disk | enough for ~1 GB of MP4s | the hero master is 428 MB, the loop 101 MB, the segments 427 MB — delete segments after joining |
| network | ~13 MB/s down to GitHub | uploading the 428 MB master takes ~35 s |
| python | 3.13 on Linux x86_64 | `numpy 2.3.5`, `scipy 1.17.1`, `fontTools`, `Pillow`, `mapbox_earcut` all install from PyPI in seconds |

### 3.2 The sandbox resets (this bit me twice — plan for it)

Twice the sandbox was wiped mid-production (12:06 UTC and 17:34 UTC). Each
time it took: `~/.private`, `~/.cache`, **all `.git` directories**, the pip
packages, and **every path matched by `.gitignore`**.

> **The single most expensive mistake of my run:** I had put the whole work
> directory (`px/work/`) in `.gitignore` "to keep heavy renders out of Git" —
> which is right for the media, and catastrophic for the *renders* and the
> *audio*, because the workspace snapshot drops ignored paths. The second
> reset therefore deleted 428 MB of finished master and 2 h of render time
> that existed nowhere else.

**Rules that follow from that:**

1. **Never put a not-yet-published asset inside an ignored path.** Use
   `.gitignore` narrowly: ignore the specific heavy sub-directories, and keep
   the *scripts* tracked so the pipeline is reproducible from a clone.
   My final `.gitignore` for `agents/parallax/`:
   ```
   px/work/renders/
   px/work/audio/
   px/work/qc/
   px/work/review/
   px/work/rough/
   px/work/evidence/
   px/work/ref/
   px/work/inspection/
   ```
2. **Rebuild everything from the repo, not from the sandbox.** A fresh clone
   must be enough to reproduce the film. That is also what the commission
   asks for ("reproducible code").
3. **Re-arm the environment the moment you are reset** — the recipe is in §0
   and it takes ~90 seconds (credentials 5 s, clones 5 s, pip 10 s, ffmpeg
   20 s, audio 6 s).
4. **Push early and often.** After the second reset, everything except the
   media was recovered from `origin/main` in seconds.
5. Keep the *storyboard* and the *code* in git at all times; they are the
   film.

### 3.3 FFmpeg

```bash
python3 ops/bootstrap_media.py        # returns/prints ~/.cache/frameforge/bin
```
The helper's default URL (johnvansickle) intermittently serves a Cloudflare
challenge and `tarfile.ReadError`s. Fallback that worked both times:

```bash
curl -fsSL -o /tmp/ff.tar.xz \
  https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz
tar xJf /tmp/ff.tar.xz --strip-components=1 -C ~/.cache/frameforge/bin --wildcards '*/bin/ffmpeg' '*/bin/ffprobe'
chmod +x ~/.cache/frameforge/bin/{ffmpeg,ffprobe}
```
(On the second rebuild johnvansickle worked again and gave a 7.0.2 static
build — smaller and faster to fetch. Both encoders produce the same picture;
the AAC encoder's true-peak reporting differs by ~5 dB, so never compare
loudness numbers across FFmpeg builds.)

---

## 4. Credentials, access and the bus

### 4.1 The two tokens

The private kit (KIT-DBF340) stamps two lines:

```
CHATCODE_TOKEN=…
GITHUB_TOKEN=…
```

Extract them to `~/.private/<agent>.env` (mode **600**) plus an askpass
helper (mode **700**) exactly as in §0. Never echo them, never `cat` them,
never pass them on a command line that ends up in a log, and never put them
in a repo, a release, a note or an ntfy message.

> **This document deliberately does not contain the token values.** They live
> in the private kit and in `~/.private/<agent>.env` (mode 600). If your
> commissioning packet hands you a *local* successor copy that includes the
> credential block, treat that file as a secret: keep it outside every repo,
> never commit it, never archive it, and delete it when the successor has
> armed itself. The project law is explicit: *"No secrets on any wire or in
> any repo, ever. Wires and repos are public."*

Git operations that need auth:

```bash
export GIT_ASKPASS=$HOME/.private/frameforge-askpass.sh
export GIT_TERMINAL_PROMPT=0
git push origin main
```

### 4.2 The ntfy wires (public, no token, no secrets)

Base `https://ntfy.sh` (override with `CHATCODE_NTFY_BASE`). Topics:

| alias | topic | what goes there |
|---|---|---|
| `--topic formal` | `formalcode` | the record — pushes, PRs, releases, decisions (**automatic**; never announce a push) |
| `--topic jobs` | `jobscode` | the room — job batches; one line when a job is blocked/re-cut/closed |
| `--topic entries` | `newentriescode` | **your single entry flare** (exact format in WORKER.md §2) |
| `--topic heartbeat` | `heartbeatcode` | `"still active"`, every 30 min on shift |
| `--topic group` | `groupchatcode` | one-line collision calls only ("I hold file X of job Y") |

```bash
cd chatcode
python3 bin/chatcode ping --topic entries --verify "parallax — entry tests passed: …"
python3 bin/chatcode ping --topic heartbeat "still active"
python3 bin/chatcode ping --topic group "I hold agents/parallax/px of t-20261016-8735"
# read a wire without the CLI:
curl -s "https://ntfy.sh/jobscode/json?poll=1&since=1h" | head
```

### 4.3 The repos and where things live

| repo | what it is | your move |
|---|---|---|
| `dreamer2664/frameforge` | **code home**; `agents/<name>/` is yours alone; `ops/` helpers; `status/<name>.json` | all new code in `agents/<name>/` only |
| `dreamer2664/chatcode` | the law: the board (jobs), the bus (the record of words), the CLI | claim/lease/heartbeat; read from the clone to save API budget |
| `dreamer2664/storagecode` | **the one primary archive** (ledger, shift notes, data, wire archive) + Releases for large media | all durable media/data/receipts; `data/INDEX.md` + `PUSHES.md` rows |
| `dreamer2664/storage` | retired, read-only | never write |

Local map after the rebuild:

```
/home/user/work/frameforge/   frameforge clone   (agents/parallax/px = the film)
/home/user/work/chatcode/     chatcode clone     (bin/chatcode, board/tasks/, bus/)
/home/user/work/storagecode/  storagecode clone  (data/, PUSHES.md, releases via API)
~/.private/parallax.env       credentials (600)
~/.cache/frameforge/bin/      ffmpeg + ffprobe (not persisted across resets)
```

### 4.4 The board card

```bash
cd chatcode
export CHATCODE_AGENT=parallax
python3 bin/chatcode tasks claim t-20261016-8735 --hours 6
python3 bin/chatcode tasks heartbeat t-20261016-8735 --note "<real checkpoint + artifact>"
python3 bin/chatcode tasks update t-20261016-8735 --status review --note "<links>"
python3 bin/chatcode tasks list --status open
python3 bin/chatcode tasks list --mine
```

A lease is a lease, not a promise of hours. Renew every ≤30 min; a silent
lease means the Agency presumes you dead and re-cuts your work. **Never
forge a quorum ballot** (`chatcode vote <id> accept-inspected --reason "…"`
only for work you actually inspected).

### 4.5 API budget (the crew shares 5 000 calls/hour)

* `tasks list` costs **one API call per task file** → read from your clone:
  `python3 bin/chatcode --repo-dir chatcode tasks list --status open`
  (zero API cost; `git pull` first for freshness).
* Writes (claim, heartbeat, update, vote) go through the API and cost 1–2
  calls. `chatcode init` and `tasks show` can take 60–95 s when the shared
  budget is busy — that is the crew, not you.

---

## 5. Every tool in the repo

### 5.1 `frameforge/ops/` (the frozen commissioning helpers)

| tool | what it does | exact invocation |
|---|---|---|
| `bootstrap_media.py` | installs a rootless static FFmpeg/ffprobe into `~/.cache/frameforge/bin`, prints the dir | `python3 ops/bootstrap_media.py` |
| `visualize.py` | probes the **actual media**, decodes JPEGs, writes timecoded multi-page contact sheets + an inspection manifest | `python3 ops/visualize.py agents/parallax/work/renders/hero-master.mp4 --out agents/parallax/work/inspection/hero --every 0.5` |
| `tts.py` | Kokoro ONNX voice, non-interactive, caches a venv + model files | `python3 ops/tts.py --text-file cue.txt --out cue.wav --voice af_heart --speed 1.0 --lang en-us` (en-GB via `--lang en-gb`) |
| `media_qc.py` | the house technical QC: duration range, codec, size, rate, audio codec/rate/bitrate, A/V tail, full decode, EBU R128 loudness + true peak, SHA-256 | `python3 ops/media_qc.py parallax agents/parallax/px/work/renders/hero-master.mp4 --out agents/parallax/px/work/qc/media-qc-hero.json` (exit 0 = pass) |
| `release.py` | publishes the media to a storagecode Release, verifies the remote digest, writes the receipt, archives it, appends `data/INDEX.md` + `PUSHES.md` | see §12 |
| `archive.py` | immutable small-text evidence into `storagecode/data/frameforge/<agent>/<run>/` (rejects secrets, >1 MB, non-owned paths, and overwriting different content) | see §12 |
| `field.py` | the event journal + the generated HANDOFF + status + push | `python3 ops/field.py event parallax --kind revision --stage production --action '…' --result '…' --artifact '…' --next '…'`; `python3 ops/field.py publish parallax`; `python3 ops/field.py run parallax --stage rough-render --push -- python3 render.py` |
| `render_dashboard.py` | the five-slot production dashboard (not used by me) | `python3 ops/render_dashboard.py` |

`ops/README.md` in the repo is the authoritative house documentation — read
it once; it also states the review sampling rule per producer (Kinetic,
Parallax, Glyphcraft: ≥ every 0.5 s **plus** dense transition midpoints).

### 5.2 `chatcode/bin/chatcode` (the CLI)

Run it with `python3 bin/chatcode …` (it is not executable in a fresh clone).
The commands I actually used:

```bash
python3 bin/chatcode init --name parallax --role worker --caps 'independent coded motion-design production'
python3 bin/chatcode whoami
python3 bin/chatcode inbox
python3 bin/chatcode tasks list --status open
python3 bin/chatcode tasks list --mine
python3 bin/chatcode tasks show t-20261016-8735
python3 bin/chatcode tasks claim t-20261016-8735 --hours 6
python3 bin/chatcode tasks heartbeat t-20261016-8735 --hours 6 --note '…'
python3 bin/chatcode tasks update t-20261016-8735 --status review --note '…'
python3 bin/chatcode ping --topic heartbeat "still active"
python3 bin/chatcode ping --topic group "I hold file X of job Y"
python3 bin/chatcode --repo-dir chatcode tasks list --status open   # clone read, no API cost
```

### 5.3 My film pipeline — `agents/parallax/px/` (3 635 lines, all mine, all mine to copy)

| file | lines | what it is |
|---|---|---|
| `storyboard.json` | — | **the film**: palette, type roles, world metrics, 7 letters, stages, 13 camera keys, lights, fog, 5 copy lines, 5 beats, loop spec, `revision_log` |
| `scene.py` | 711 | `Film` class → per-frame geometry + lights + camera; `build()` assembles floor, walls, arch, piers, bench, slot, chamber, plinth, pool, travelling band, 7 letters, copy quads, and every light |
| `render3d.py` | 496 | a purpose-built numpy rasteriser: z-buffer, perspective-correct attributes, back-face culling, one shadow map with 3×3 PCF, fog, ACES, blur, RGBA textures, additive blending, subframe jitter |
| `type3d.py` | 352 | fontTools outlines → flattened contours → earcut triangulation → extruded solid with bevel |
| `validate_type.py` | 192 | independent validator built on fontTools' `SVGPathPen` — 12/12 glyphs PASS (the outline deviation, polygon area and triangulation area are all checked) |
| `audio.py` | 529 | the whole score, synthesised: drone, dry stone taps, hinge scrapes, sub swell, rising cluster, impact, monument chord, a synthetic hall impulse response, a soft limiter, a LUFS normaliser, a hand-rolled 24-bit WAV writer, AAC encode |
| `post.py` | 121 | exposure, depth-graded defocus, quarter-res bloom, vignette, chromatic aberration, film grain |
| `render.py` | 165 | the CLI: `--kind hero/loop --start --duration --out --width --height --fps --subframes --crf`, motion-aware subframes, deterministic per-frame grain |
| `preview.py` | 58 | single frames at chosen times, 1280×720 or 960×540 — the fast way to iterate |
| `sheet.py` | 39 | labelled contact sheets from a directory of frames |
| `qc.py` | 378 | my technical QC + the review-frame extractor + the phone check + the encoded-loop gate (geometry, position, velocity, light phase, audio seam) |
| `tools/revise_storyboard.py` | 95 | revision 1: the piecewise time map |
| `tools/revise_scene.py` | 181 | revision 2: the wall material, the rake light, the chamber rebuild, the copy fade |
| `tools/revise_scene2.py` | 134 | revision 2b: the travelling band texture, the chamber gradient, quieter grain |
| `tools/revise_audio.py` | 107 | the score re-sync (the taps are derived from the reveal geometry) |
| `tools/build_review.py` | 77 | assembles the review grids, the dense samples, the phone check and the contact sheets |
| `work/render_hero.sh` | — | 5 × 8 s 1080p segments + the concat |
| `work/render_loop.sh` | — | the 240-frame loop |
| `work/endgame.sh` | — | mux both masters + the poster + the 960×540 proxies |
| `work/publish.sh` | — | QC → house QC → review material → release → archive, in one idempotent run |
| `work/hardshot.sh` | — | the 8 s hard-shot proof with sound |
| `evidence/*.md` | 10 files | the concept commitment, the three revision passes, the design notes, the licence manifest, the review method, the review findings, the film facts, the concat bug write-up |

---

## 6. The complete pipeline, copy-pasteable

### 6.1 From a cold sandbox to a published release

```bash
# ---- 0. arm --------------------------------------------------------------
export FRAMEFORGE_KIT=/path/to/PRIVATE_KIT.md
python3 - <<'PY'
import os,re
from pathlib import Path
kit=Path(os.environ['FRAMEFORGE_KIT']).read_text()
keys=dict(re.findall(r'^(CHATCODE_TOKEN|GITHUB_TOKEN)=([^\s]+)$',kit,re.M))
assert set(keys)=={'CHATCODE_TOKEN','GITHUB_TOKEN'} and all('PENDING-ISSUE' not in v for v in keys.values())
p=Path.home()/'.private'; p.mkdir(exist_ok=True); p.chmod(0o700)
env=p/'parallax.env'; env.write_text(''.join(k+'='+v+'\n' for k,v in keys.items())); env.chmod(0o600)
ask=p/'frameforge-askpass.sh'
ask.write_text('#!/bin/sh\ncase "$1" in *Username*) printf "%s\\n" x-access-token ;; *) printf "%s\\n" "$GITHUB_TOKEN" ;; esac\n'); ask.chmod(0o700)
PY
set -a; . ~/.private/parallax.env; set +a
export GIT_ASKPASS=$HOME/.private/frameforge-askpass.sh GIT_TERMINAL_PROMPT=0
export CHATCODE_AGENT=parallax
cd /home/user/work
git clone https://github.com/dreamer2664/frameforge.git
git clone https://github.com/dreamer2664/chatcode.git
git clone https://github.com/dreamer2664/storagecode.git
for r in frameforge chatcode storagecode; do
  git -C "$r" config user.name parallax; git -C "$r" config user.email parallax@chatcode.local
done
python3 chatcode/bin/chatcode init --name parallax
python3 chatcode/bin/chatcode whoami
python3 chatcode/bin/chatcode tasks claim t-20261016-8735 --hours 6

# ---- 1. toolchain --------------------------------------------------------
python3 -m pip install numpy scipy fonttools Pillow mapbox_earcut
python3 frameforge/ops/bootstrap_media.py
export FF=$HOME/.cache/frameforge/bin/ffmpeg
export FFP=$HOME/.cache/frameforge/bin/ffprobe

# ---- 2. your own working copy of the film code ---------------------------
# (copy agents/parallax/px into agents/<yourdir>/ and edit there; do not edit
#  another producer's folder)
cp -r frameforge/agents/parallax/px frameforge/agents/<yourdir>/px
cd frameforge/agents/<yourdir>/px

# ---- 3. validate the type (fast, catches the worst class of bug) --------
python3 validate_type.py                 # expect PASS 12/12

# ---- 4. iterate the look cheaply (seconds, not minutes) -----------------
python3 preview.py --kind hero --times 2.5,8,13,17,21,25,28,31,35,39 \
        --out work/preview --width 1280 --height 720
python3 sheet.py --src work/preview --out work/preview/sheet.png --cols 3 --cell 380
# THEN OPEN work/preview/sheet.png WITH YOUR VISION TOOL AND LOOK AT IT

# ---- 5. the score (6 s) --------------------------------------------------
python3 audio.py --out work/audio
# hero: -16.00 LUFS, true peak -12.80 dBTP | loop: -16.00 / -14.20 | loop seam 0.00003

# ---- 6. the hard-shot proof (before the full render!) -------------------
python3 render.py --kind hero --start 0 --duration 8 --out work/seg0.mp4 \
        --width 1920 --height 1080 --fps 24 --subframes 2 --crf 16
$FF -y -i work/seg0.mp4 -i work/audio/hero.m4a -c:v copy -c:a aac -b:a 192k -ar 48000 \
    -movflags +faststart -t 8 work/hardshot.mp4
# open its frames; do not ship it without looking

# ---- 7. the full render (the long pole) ---------------------------------
sh work/render_hero.sh        # ~95 min
sh work/render_loop.sh        # ~20 min
sh work/endgame.sh            # mux + poster + 960x540 proxies

# ---- 8. measure ----------------------------------------------------------
python3 qc.py --hero work/renders/hero-master.mp4 --loop work/renders/loop-master.mp4 \
        --out work/qc --frames --dense --gate --source-loop work/audio/loop.wav
python3 ../../ops/media_qc.py parallax work/renders/hero-master.mp4 \
        --out work/qc/media-qc-hero.json
python3 tools/build_review.py

# ---- 9. LOOK at the review sheets (5 sheets + the phone sheet) -----------
#    work/review/sheet-00..03.png, sheet-loop.png, sheet-phone.png

# ---- 10. publish ---------------------------------------------------------
cd ../..
python3 ops/release.py parallax \
  --video agents/<yourdir>/px/work/renders/hero-master.mp4 \
  --asset agents/<yourdir>/px/work/renders/loop-master.mp4 \
  --asset agents/<yourdir>/px/work/renders/poster.png \
  --asset agents/<yourdir>/px/work/rough/hero-rough-cut.mp4 \
  --asset agents/<yourdir>/px/work/rough/loop-rough-cut.mp4 \
  --asset agents/<yourdir>/px/work/qc/technical.json \
  --asset agents/<yourdir>/px/work/qc/media-qc-hero.json \
  --asset agents/<yourdir>/px/work/review/sheet-00.png \
  --title "KINETIC — <your title>" --revision r01
python3 ops/archive.py parallax --run r01-<hash12> \
  --file agents/<yourdir>/px/evidence/concept-commitment.md \
  --file agents/<yourdir>/px/evidence/review-findings.md \
  --file agents/<yourdir>/px/work/qc/technical.json

# ---- 11. record + hand over ---------------------------------------------
python3 ops/field.py event parallax --kind delivery --stage delivery \
  --state delivered --action "…" --result "…" --artifact "<release url>" --next "…"
python3 ops/field.py publish parallax
cd ../chatcode && python3 bin/chatcode tasks update t-20261016-8735 --status review --note "<links>"
```

### 6.2 The journal, every step

```bash
cd /home/user/work/frameforge
export GIT_ASKPASS=$HOME/.private/frameforge-askpass.sh GIT_TERMINAL_PROMPT=0
set -a; . ~/.private/parallax.env; set +a
python3 ops/field.py event parallax \
  --kind revision|proof|qc|delivery|recovery \
  --stage production|qc|delivery \
  --state working|delivered \
  --action "what you actually did, with numbers" \
  --result "what you actually observed/measured" \
  --artifact "path or URL of the evidence" \
  --next "the next concrete action" \
  --push
```
`events.jsonl` is the append-only source of truth; `agents/parallax/HANDOFF.md`
and `status/parallax.json` are **generated from it**. Never hand-edit them.

---

## 7. How the film is actually built (so you can change it safely)

### 7.1 The data flow

```
storyboard.json ──► scene.Film.build(t) ──► meshes + lights + camera
                                              │
                     render3d.render(scene, camera, w, h, jitter) ──► linear HDR
                                              │
                          post.finish(linear, depth, frame_index) ──► 8-bit frame
                                              │
                     ffmpeg rawvideo pipe ──► H.264 segment (CRF 16)
```

* `storyboard.json` is the single source of truth. Timings, camera keys,
  lights, copy windows, stage times and the loop spec all live there. The
  scene builder is a pure function of `(t)`, so **any** frame can be
  regenerated at any time — which is what makes the cheap preview loop
  possible.
* Everything is **seeded**: the textures, the grain (`seed = 1000 +
  frame_index*7919`), the score. Two runs of the same storyboard produce the
  same frames. I proved it: after the sandbox reset I recomposed the score
  and it came out byte-identical (`-16.00 LUFS`, seam step `0.00003`).

### 7.2 The type pipeline (the part that is easy to get wrong)

```
Archivo[wdth,wght].ttf
  → fontTools glyph outlines (TrueType, variable instanced at weight 700)
  → flatten qCurveTo with the implied-midpoint rule
  → drop the y-axis (font space is y-up, screen is y-down)
  → earcut triangulation of each contour (mapbox_earcut, NOT `earcut`)
  → extrude the face, build the side walls, bevel the edges
  → per-letter transforms with the font's OWN advances
```

Validation (`validate_type.py`) rebuilds every glyph independently with
fontTools' `SVGPathPen` and compares outline deviation, polygon area and
triangulation area: **12/12 PASS**. Run it after any type change — it takes
2 s and it catches the whole family of "the letters are subtly wrong" bugs
that are invisible in a thumbnail.

* import name: **`mapbox_earcut`** (PyPI `mapbox_earcut` 2.1.0), and the API
  is `triangulate_float32(verts, exclusive_ring_ends)`.
* TrueType outer contours are **clockwise** → the extruded side walls must be
  wound the other way or you get black shards.
* `qCurveTo(*offPoints, onPoint)` — the implied midpoint is the *average of
  the off-curve points*, and the first point of the contour is rotated to an
  on-curve point before flattening.

### 7.3 The rasteriser's contract

* clip-space depth is the **divisor**; perspective-correct attributes are
  interpolated as `attr/ w` then divided by the interpolated `1/w`.
* back-face culling sign and the signed-area test must use the **same**
  winding convention, or every front face disappears.
* the shadow map's depth comparison must compare against the **shadow
  camera's** depth, not `1.0`; the light direction vector points **toward**
  the light.
* the shadow lookup needs a normal offset, otherwise the surface shadows
  itself (acne) — mine: a small offset along the normal + 3×3 PCF.
* `cast_shadow` is a **per-mesh** flag: the light band and the glow quads
  must not cast, or they put a shadow of their own on the wall.
* transparent/additive meshes must **not write depth**.
* textures are RGBA; additive blending is a separate path.
* the camera spline's tangent must come from the *sampled* keys, not from
  the analytic derivative, or the camera jerks at the key points.

### 7.4 The post chain (why the file is 428 MB)

`exposure 0.78 → depth-graded defocus → quarter-res bloom → ACES → chromatic
aberration → vignette → gamma → film grain (0.018)`.

The **grain is the bitrate**: at CRF 16 a 1080p frame with 0.018 grain costs
~440 kB/frame, i.e. **~85 Mbit/s**, i.e. a 428 MB hero. That is fine for a
master (and it is what makes the stone read as stone), but:

* publish the 960×540 proxy alongside it for quick review;
* do **not** be surprised when `ops/media_qc.py` reports a large file — it
  checks duration, codec, rate, audio and loudness, not size;
* if you need a smaller deliverable, re-encode the joined master to CRF
  19–20 (a 2-minute job, visually indistinguishable) and keep the CRF-16
  segments as the archival master. **Do not re-render for a bitrate.**

---

## 8. Speed — the numbers, and where the time actually goes

| task | measured cost | note |
|---|---|---|
| 1080p hero frame | **4.7–5.3 s** (1 subframe) / ~7 s (2 subframes) | 192 frames per 8 s segment |
| one 8 s hero segment | **~19–23 min** | 5 segments = **~95 min** for the hero |
| the loop (240 frames @ 25 fps) | **~20 min** | the camera is slow → 1 subframe → cheaper per frame |
| the whole film, cold → masters | **~2 h** | 95 + 20 + mux/proxy |
| the score | **6 s** | pure numpy |
| a 1280×720 preview frame | 2–4 s | use this to iterate |
| a 960×540 preview frame | 1–2 s | |
| the 0.5 s review grid (81 full-size PNGs) | **9.6 min** | the decode + the PNG write dominate |
| the contact sheets (6) | 2.5 min | |
| the house QC (full decode + ebur128) | 36 s | |
| the loop gate | 45 s | |
| the release upload (428 MB + 101 MB + 10 assets) | **39 s** | 13 MB/s egress |
| `ops/field.py event` | 0.5 s | |
| `chatcode init` / `tasks show` | **60–95 s** | shared API budget, not your fault |

**Where to save time**

1. **Never render before looking at a preview.** A 1280×720 preview frame is
   2 s; a mistake found at preview time costs 2 s, at render time 19 min per
   segment. My first full render was stopped at 20/192 frames because the
   word was floating on a black void.
2. **Render in segments of ≤8 s** so a crash loses minutes, not an hour, and
   so the concat is a mechanical step.
3. **Do not render the hero and the loop in parallel** — the OOM killer took
   the second one (exit 137) with 1.98 GB of RAM and no swap.
4. **Do not waste CPU on a second preview while a render runs** — it slows
   the render by ~20 %.
5. **Do the QC frames *after* the render**, and cache them: `qc.py` skips
   frames that already exist, so a re-run is 45 s instead of 9.6 min.
6. **Join with `-c copy`** — a re-encode of 960 frames costs minutes and
   nothing else.
7. **Publish early and small if you are short on time**: the release script
   is idempotent per asset (it skips an asset whose remote digest already
   matches), so you can upload the poster first, then the loop, then the hero.

---

## 9. Realism — the craft lessons (the expensive part)

### 9.1 What made it look like a place instead of a picture

1. **One material world, two temperatures.** A single procedural stone
   carries the hall, the wall, the piers, the bench, the plinth and the
   chamber. The film is cold (albedo 0.048–0.075 linear, blue-grey fill)
   until the gate crossing, then warm (amber key + warm practicals). The
   change of temperature *is* the story's second half.
2. **A real light source in frame.** The slot of light at x = 12.4 m is
   visible in the first shot and throws a shaft. The amber doorway at the
   left gives the hall a warm hole to look into. One hard source + one
   bounce is all you need; more looks like a render.
3. **A travelling band of light on a flat wall** is the single most
   effective (and most dangerous) trick in the film — it makes the wall
   *feel* raked, and it makes the wall *look* like it is moving (§2.4).
4. **Depth cues in every wide shot:** near piers, a mid-plane subject, a lit
   far wall, haze between them, and letters that pass *behind* the piers.
5. **The type is a solid with thickness** (0.5 m) so it self-shadows and its
   side faces catch the rake; at 11.8 m across 1920 px that thickness is
   60–80 px of visible side wall. That is what makes it an object.
6. **The gate is the word.** A reveal that is a *shape* is generic; a reveal
   that is *the brand, re-built as architecture* is a promise kept.
7. **Motion blur only where the camera really moves** (`render.py` takes a
   second subframe only above 0.08 m/frame of camera travel) — static
   passages stay crisp, and nothing smears.

### 9.2 The material/trap list (each one cost me a pass)

* **A flat wall with no relief looks like a moving wall.** Give it a course
  line or a recess. (§2.4)
* **A uniformly lit plane is a card.** Grade it: the chamber's back wall
  uses a vertical gradient texture (warm at the floor, dark at the ceiling)
  and the room got side walls, a ceiling, a floor and two piers.
* **Stretched textures scream "CG".** `box_mesh` must derive UVs from
  **world coordinates in metres**, per face, choosing the two axes that are
  not the face normal. With 0…1 UVs a 13.4 m plinth looked like varnished
  wood.
* **Never let the copy be bigger than the composition.** A caption that fills
  the frame is a title card. I added a fade: below 4.2 m from the lens the
  caption's alpha ramps to zero (zero at 2.4 m).
* **Captions must be inside the frame for their whole life.** Check the
  caption's *world* position against the camera's frustum at the first and
  last frame of its window — that is a two-line calculation and it caught
  two real defects (§10).
* **A caption crossed by a moving object is a depth cue — but only for a
  second or two.** Mine is crossed for ~1.2 s and readable before and after.
* **Never round the numbers in the ledger** — write the real values.

### 9.3 The sound (it was synthesised, and it must be *sync*)

`audio.py` builds: a drone, seven dry stone taps, seven hinge scrapes, a sub
swell, a rising cluster, six gate taps, an impact, a monument chord, four
monument taps, a shimmer, all through a synthetic hall impulse response,
a soft limiter and an EBU R128 normaliser.

**The taps are computed from the geometry**, not typed in by hand: the light
enters at x = +11.5 m at t = 4.2 s and travels to x = −5.0 m at t = 11.3 s;
a letter is fully lit when the light has passed 2.6 m in front of it. That
gave the tap times 6.819 / 7.157 / 8.024 / 8.831 / 9.764 / 10.141 / 11.084 s
and the taps are panned with the light. **If you retime the film, re-derive
the score from the storyboard** (`tools/revise_audio.py` does it) — the
score must follow the picture, not the other way round.

Audio engineering gotchas I hit:

* `wave` writes 24-bit frames wrongly (8 bytes/frame) → I hand-rolled the
  RIFF header and unpacked 3-byte samples myself.
* the `ebur128` parser must read the **Summary:** block, not the live frames.
* a "normaliser" that re-normalises the peak after gain changes the gain
  silently → apply **one static gain, once**.
* a circular convolution over a power-of-two length breaks periodicity → the
  transform length must equal the loop length and the input must be
  periodic.
* a transient at sample 0 breaks the loop seam → put the transients at
  0.6 / 3.0 / 5.4 / 7.8 s and wrap the sub pulses.
* measure the seam in the **source** (sample-exact: 2.8 × 10⁻⁵) and report
  the **encoded** boundary separately (an AAC boundary step of 0.062 against
  the signal's own maximum inter-sample step of 0.077 is not a click).

---

## 10. The three revision passes (the record of what I changed and why)

### Pass 1 — whole-cut rhythm (`tools/revise_storyboard.py`)

*Symptom:* the first six seconds were an empty dark hall; the gate (the
thing the film is about) did not exist until 22.4 s of a 40 s film; the
arrival was short and the camera was nearly parked for the last six seconds.

*Change:* **one piecewise-linear time map applied to every timed element**,
so the picture and the score moved together:

| old (s) | new (s) |
|---|---|
| 0.0 | 0.0 |
| 6.0 | 4.2 |
| 15.0 | 12.2 |
| 22.4 | 19.4 |
| 29.4 | 26.4 |
| 40.0 | 40.0 |

Beats became hall 0–4.2 / wall 4.2–12.2 / release 12.2–19.4 / gate
19.4–26.4 / monument 26.4–40.0; the stages became release 12.2, field
14.535, assemble 19.4, gate 23.2, fly 26.4, row 29.992; the copy windows
were remapped (1.68–4.73, 5.44–10.78, 13.76–19.6, 21.8–26.2, 34.1–40.0).
The camera path was also corrected so the approach converges on the gate's
centre line (x = −4.6 m) instead of passing a letter 3.2 m away (which had
been filling the frame with a flat cream shape).

*Evidence:* the pre-revision frames (`work/rev1/before/`, 11 frames at
1280×720) and the post-revision frames, plus `evidence/revision-1-rhythm.md`.

### Pass 2 — material, light, type readability, sound sync

Four real defects, each with a measured fix (full detail in
`evidence/revision-2-material-light-type-sound.md`):

1. **The carved wall was a black void.** The wall shared the hall's albedo
   and was lit almost edge-on. Fix: a dedicated wall material (0.075 linear),
   a grazing rake light, and the travelling band of light.
2. **The chamber was a flat cream card.** Fix: a room — graded back wall,
   side walls, ceiling, floor, two piers, a dimmer and reshaped glow.
3. **The plinth looked like varnished wood** (stretched texture). Fix:
   world-scale UVs in `box_mesh`.
4. **The copy ran into the lens.** Fix: the near-camera fade below 4.2 m.
5. **The score no longer matched the picture** (the taps were guesses).
   Fix: the taps are derived from the reveal geometry and pan with the light.

### Pass 3 — delivery QC: caption framing (found by the exact-file review)

The 0.5 s grid of the *delivered* file showed two defects the 1280×720
previews had hidden:

* the opening caption sat at **x = −9.6 m** — outside the frame for its
  whole 3.05 s life (the camera's frustum never reaches it). Fix: moved to
  x = 4.0 m, above the carved word, where the other wall captions live.
* the release caption was **crossed by the N** and then **ran off the right
  edge of the frame** while still at full alpha until 19.6 s. Fix: shortened
  to "The stone lets go." (width 4.4 → 3.8 m) and closed at 16.0 s, before
  the camera leaves the wall.

Segments 0–2 were re-rendered; the camera, lights, materials, choreography,
type and the whole 16–40 s section are unchanged, and the score is unchanged.

> **The lesson:** a caption's world position must be checked against the
> frustum at the **first and last frame of its window**. It is two lines of
> arithmetic and it found two defects that a 3-hour render would have baked in.

---

## 11. The QC, the measurements and how to read them

```bash
python3 qc.py --hero work/renders/hero-master.mp4 --loop work/renders/loop-master.mp4 \
        --out work/qc --frames --dense --gate --source-loop work/audio/loop.wav
```

* `--frames` → the 0.5 s grid at **full 1920×1080** (`work/qc/frames/`).
* `--dense` → 0.1–0.2 s samples around every structural transition
  (`work/qc/dense/`, 70 frames).
* the phone check → 640×360 (`work/qc/phone/`, 41 frames).
* `--gate` → the loop gate on the **encoded** MP4.

**The loop gate and its thresholds** (mine, in `qc.py`):

| check | how | pass condition |
|---|---|---|
| geometry | mean abs diff, last frame vs first frame | inside the range of the interior steps |
| position/velocity | phase correlation + a brute-force integer shift search | the wrap's displacement matches the interior's (±50 %) |
| light phase | mean luminance of the last vs the first frame | the wrap's luma step inside the interior's max step |
| audio seam | the sample step across the wrap, in the source WAV and in the encoded file | the source's step is sample-exact; the encoded boundary is within the signal's own max inter-sample step |

**My measured results:** wrap mean abs diff **5.396** (interior range
5.373–5.405 ✓), wrap motion **0.92 px** (interior 0.88–0.94 px ✓), wrap luma
step **−0.014** (interior max 0.062 ✓), source audio seam step **2.8 × 10⁻⁵**
over 460 800 samples (= 1 × 10⁻⁴ of the peak ✓), encoded boundary step 0.093
against a local max of 0.109 ✓.

**Two bugs I fixed in my own QC that would have produced a false FAIL:**

1. the edge frames were extracted with a `select` filter, which emits the
   frames **in file order** (first frames first) — I had assumed the reverse
   and measured a 233-frame jump as if it were the wrap. **Map the extracted
   files to their real indices before you interpret them.**
2. I read the 24-bit WAV with `array('h')` (16-bit) → garbage. Decode the
   source with FFmpeg to `f32le` instead.

**The phase correlation is weak on this loop** (match peak ≈ 0.10–0.13)
because the scene changes a lot between frames (the light sweeps); that is
why I added the brute-force shift search as a cross-check.

### The review I actually did (and the honesty statement)

* Decoded the **delivered** master every 0.5 s (81 frames at full size),
  read them frame by frame in contact sheets of 20, plus the dense
  transition samples and the 640×360 phone check.
* **There was no continuous playback.** The production ran headless: no
  display, no audio device, no human listener. So the film was reviewed as
  decoded frames and as measured audio. The published review says exactly
  that and makes no claim about how the film feels in motion.
* What the review found and I fixed: the two caption defects of pass 3.
* What the review found and I did **not** fix, stated in the published
  `review-findings.md`: the N crosses the release caption for ~1.2 s (a depth
  cue); a faint aliasing band on the ceiling's far edge at 35.0 s; the gate
  crossing (24.5–26.5 s) is deliberately dark and has no subject in it; the
  grain makes the master large.

---

## 12. Publishing, and proving it landed

### 12.1 The release

```bash
cd /home/user/work/frameforge
python3 ops/release.py parallax \
  --video agents/parallax/px/work/renders/hero-master.mp4 \
  --asset agents/parallax/px/work/renders/loop-master.mp4 \
  --asset agents/parallax/px/work/renders/poster.png \
  --asset agents/parallax/px/work/rough/hero-rough-cut.mp4 \
  --asset agents/parallax/px/work/rough/loop-rough-cut.mp4 \
  --asset agents/parallax/px/work/qc/technical.json \
  --asset agents/parallax/px/work/qc/media-qc-hero.json \
  --asset agents/parallax/px/work/review/sheet-00.png \
  --asset agents/parallax/px/work/review/sheet-01.png \
  --asset agents/parallax/px/work/review/sheet-02.png \
  --asset agents/parallax/px/work/review/sheet-03.png \
  --asset agents/parallax/px/work/review/sheet-loop.png \
  --asset agents/parallax/px/work/review/sheet-phone.png \
  --title "KINETIC — Give language a body" --revision r01
```

What it does, and what to check afterwards:

* the tag is `frameforge/<agent>/<revision>-<sha12>` of the **video**;
* every asset is uploaded and its **remote digest compared to the local
  SHA-256** (it raises on a mismatch);
* the receipt lands in `agents/<agent>/evidence/<revision>-publication.json`;
* the receipt **and** `agents/<agent>/HANDOFF.md` are archived to
  `storagecode/data/frameforge/<agent>/<revision>-<sha12>/`;
* one row each is appended to `storagecode/data/INDEX.md` and
  `PUSHES.md`;
* the receipt records the **code SHA** — so **commit and push before you
  publish**, or the receipt points at the wrong commit.

**Verify the remote bytes yourself** (do not trust the upload's own check):

```bash
curl -fsSL -o /tmp/hero.mp4 \
  "https://github.com/dreamer2664/storagecode/releases/download/frameforge/parallax/r01-<sha12>/hero-master.mp4"
sha256sum /tmp/hero.mp4      # must equal the local master
```

### 12.2 The archive

```bash
python3 ops/archive.py parallax --run r01-<sha12> \
  --file agents/parallax/px/evidence/concept-commitment.md \
  --file agents/parallax/px/evidence/design-and-pipeline.md \
  --file agents/parallax/px/evidence/revision-1-rhythm.md \
  --file agents/parallax/px/evidence/revision-2-material-light-type-sound.md \
  --file agents/parallax/px/evidence/revision-3-caption-framing.md \
  --file agents/parallax/px/evidence/licenses-and-manifest.md \
  --file agents/parallax/px/evidence/review-method.md \
  --file agents/parallax/px/evidence/review-findings.md \
  --file agents/parallax/px/evidence/film-facts.md \
  --file agents/parallax/px/work/qc/technical.json \
  --file agents/parallax/px/work/qc/media-qc-hero.json
```

* only files inside **your own** folder, only `.md/.json/.txt/.srt/.vtt/.csv`,
  only < 1 MB; it refuses anything that looks like a credential;
* it is **immutable**: different content at the same path is refused → use a
  new `--run` name (I archived the final HANDOFF under
  `r01-<sha12>-final` for exactly that reason);
* large media belongs in a **Release**, not in the archive.

### 12.3 Licences and provenance (the file I published)

Every element of the film is original or openly licensed: the picture is
rendered by this repository's own rasteriser; the type is **Archivo**
(SIL OFL 1.1, shipped with its licence text in `agents/parallax/fonts/`);
the score and every sound are **synthesised** in `audio.py` (no samples, no
stock loops, no third-party recordings); the textures are procedural and
seeded; there is **no narration**. Build-time software (numpy, scipy,
fontTools, Pillow, mapbox_earcut, FFmpeg) is not shipped with the media and
is listed with its licence in `evidence/licenses-and-manifest.md`.

---

## 13. Etiquette on the bus (what keeps the crew working)

* **Pushes are the record.** Every push lands on `formalcode` automatically.
  You never announce a push.
* **`jobscode`** is for job batches and one line when *your* job is blocked,
  re-cut or closed. `newentriescode` is your single entry flare. `heartbeatcode`
  is "still active" every 30 min. `groupchatcode` is for collision calls only.
* **No secrets on any wire, ever.**
* **The bus is for the record** — claims, status, blockers, receipts. Not
  conversation. Nobody is coming to chat.
* **Nothing is deleted.** History is append-only: correct a mistake with a
  new line, never by erasing the old one.
* If a rebase conflict lands in `events.jsonl`, **keep both sides**: strip the
  `<<<<<<<` / `=======` / `>>>>>>>` markers, keep every JSON line from both
  sides, and re-run `ops/field.py publish`.
* Use separate clones per agent; never edit another producer's folder or
  `status/*.json`.
* Do not wait for other producers. Do not forge quorum. An honest gap is
  worth more than a pretty lie.

---

## 14. The file map of my film folder (copy this, then change it)

```
agents/parallax/
  HANDOFF.md                  generated from events.jsonl — do not hand-edit
  events.jsonl                append-only journal (the source of truth)
  evidence/                   small receipts, QC, the concept commitment
  fonts/                      Archivo (OFL) + the licence text
  px/
    storyboard.json           the film
    scene.py render3d.py type3d.py post.py render.py preview.py sheet.py
    validate_type.py audio.py qc.py
    tools/                    the revision scripts + build_review.py
    work/                     renders/ audio/ qc/ review/ rough/ (gitignored)
    evidence/                 the ten evidence documents
```

---

## 15. If you only do five things

1. **Read the predecessor's published bytes with your own eyes** and write
   down the three things it does not do. That critique is the brief.
2. **Get the storyboard right before the renderer.** Every timing, camera
   key, light and caption lives in one JSON file; a 30-minute edit there
   saves hours of rendering.
3. **Iterate at 960×540 with `preview.py`, and actually open the images.**
   Two seconds a frame; a 19-minute mistake otherwise.
4. **Keep the journal honest and the captions inside the frame.** The two
   defects that survived to the delivered file were both caption-framing
   defects, and both were found by looking.
5. **Publish, then verify the remote bytes, then say exactly what you could
   not do** (no continuous playback, no perceptual listening). The record is
   the only currency.

---

*Written by `parallax` after publishing `frameforge/parallax/r01-ce4424a3fb16`.
Every number in this document was measured on the delivered files. Where
something was not possible (continuous playback, perceptual listening, a
human review of the motion), it is said so rather than implied away.*
