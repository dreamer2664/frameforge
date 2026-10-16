#!/usr/bin/env python3
"""axiom renderer — deterministic frame renderer for the whole film.

  python3 render.py --timeline work/timeline.json --out renders/r01.mp4 [--scale 0.5]
                    [--from 0 --to 120] [--frames tmp/frames/%06d.png] [--fps 24]

Pipeline: timeline.json (measured cue durations) -> per-frame scene draw at the requested
pixel scale -> transitions (cut / crossfade / slide) -> optional PNG frame dump -> FFmpeg
encode. Everything downstream of `time` is pure: same t gives the same pixels.
"""
from __future__ import annotations

import argparse, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from film.stage import Stage                     # noqa: E402
from film.style import Camera, clamp, ease_io, ease_out, smooth   # noqa: E402
from film import scenes_a, scenes_b, scenes_c     # noqa: E402

REG = {}
REG.update(scenes_a.REG)
REG.update(scenes_b.REG)
REG.update(scenes_c.REG)

FFMPEG = str(Path.home() / ".cache/frameforge/bin/ffmpeg")


def shot_at(tl: dict, t: float) -> dict:
    shots = tl["shots"]
    lo, hi = 0, len(shots) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if shots[mid]["end"] <= t:
            lo = mid + 1
        else:
            hi = mid
    return shots[lo]


def transition_for(tl: dict, shot: dict) -> tuple[str, float, str]:
    """Deliberate cuts by default; fades at chapter openings and the final card."""
    ch = str(shot["chapter"])
    nxt = next((s for s in tl["shots"] if s["chapter"] == shot["chapter"] and s["start"] >= shot["end"]), None)
    if shot["id"] == "s77":
        return ("fade", 0.0, "none")
    if nxt is None:      # last shot of a chapter -> crossfade into the next chapter
        return ("crossfade", 1.15, "none")
    if shot["id"] in ("s49", "s58", "s68", "s26", "s42", "s51", "s34"):
        return ("crossfade", 0.9, "none")
    return ("cut", 0.0, "none")


def chapter_card_for(tl: dict, t: float):
    for cid, cc in tl["chapters"].items():
        if cc["card_start"] <= t <= cc["card_end"]:
            return cid, cc, t - cc["card_start"]
    return None, None, None


def render_frame(tl: dict, t: float, pix: float, W: int, H: int) -> Image.Image:
    shot = shot_at(tl, t)
    local = t - shot["start"]
    stage = Stage(pix=pix, bg=shot.get("bg", "parchment"), t=local, shot=shot, W=W, H=H)
    from film import cast as _cast
    _cast.CURRENT_T = local          # drives each character's idle breathing for this frame
    fn = REG.get(shot["scene"])
    if fn is None:
        stage.ink.rrect(200, 400, 1720, 680, r=20, fill=(250, 240, 220), outline=(200, 60, 60), width=6)
        stage.ink.text((960, 500), f"missing scene: {shot['scene']}", role="display", size=60, anchor="ma")
    else:
        fn(stage)
    # chapter card overlay (never burned narration: number + the chapter question only)
    cid, cc, ct = chapter_card_for(tl, t)
    if cid is not None and ct is not None:
        stages = [stage]
        stage.chapter_card(cid, cc["card"], ct, dur=cc["card_dur"])
    return stage.finish()


def render_range(tl: dict, out: Path, scale: float, fps: int, t0: float, t1: float,
                 audio: Path | None, total_dur: float, crf: int, preset: str, workers: str,
                 x264_params: str | None = None, x264_threads: int = 2):
    W, H = int(round(1920 * scale)), int(round(1080 * scale))
    pix = scale
    n0, n1 = int(t0 * fps), int(t1 * fps)
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if audio:
        cmd += ["-ss", f"{t0:.3f}", "-i", str(audio)]
    cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-pix_fmt", "yuv420p",
            "-threads", str(x264_threads), "-g", str(fps * 2)]
    if x264_params:
        cmd += ["-x264-params", x264_params]
    if audio:
        cmd += ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-shortest",
                "-af", "aresample=async=1:first_pts=0"]
    cmd += ["-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    ok, t = 0, n0 / fps
    try:
        while True:
            f = int(round(t * fps))
            if f >= n1:
                break
            img = render_frame(tl, t, pix, W, H)
            proc.stdin.write(img.tobytes())
            ok += 1
            t = (f + 1) / fps
            if ok % 120 == 0:
                print(f"  ..{ok} frames encoded (t={t:.1f}s)", flush=True)
    except BrokenPipeError:
        print("ffmpeg closed the pipe early", file=sys.stderr)
    finally:
        try:
            proc.stdin.close()
        except Exception:
            pass
        rc = proc.wait()
    return ok, rc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=str(HERE.parent / "work" / "timeline.json"))
    ap.add_argument("--out", default=None)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--from", dest="t0", type=float, default=0.0)
    ap.add_argument("--to", dest="t1", type=float, default=None)
    ap.add_argument("--audio", default=None)
    ap.add_argument("--crf", type=int, default=18)
    ap.add_argument("--preset", default="medium")
    ap.add_argument("--frames-dir", default=None, help="also write PNG frames here")
    ap.add_argument("--x264-params", default=None,
                    help="bound encoder memory, e.g. rc-lookahead=12:sync-lookahead=0:bframes=2")
    ap.add_argument("--video-only", action="store_true", help="skip audio; mux separately")
    ap.add_argument("--x264-threads", type=int, default=2,
                    help="encoder threads; keep low so the Python renderer keeps a core")
    a = ap.parse_args()

    tl = json.loads(Path(a.timeline).read_text())
    missing = [cid for cid, c in tl["cues"].items() if not str(c.get("file", "")).endswith(".wav")]
    if missing:
        raise SystemExit(f"refusing to render: {len(missing)} cues have no narration file in "
                         f"{a.timeline} (looks like a placeholder/smoke timeline). "
                         f"Rebuild with: python3 -c \"from film import timeline; timeline.build('am_michael')\"")
    total = tl["total_duration"]
    t0, t1 = a.t0, (a.t1 if a.t1 is not None else total)
    out = Path(a.out or (HERE.parent / "renders" / f"r01-{int(a.scale*100)}p.mp4"))
    out.parent.mkdir(parents=True, exist_ok=True)
    audio = Path(a.audio) if (a.audio and not a.video_only) else None
    print(f"render {out} scale={a.scale} fps={a.fps} window={t0:.1f}-{t1:.1f}s of {total:.1f}s "
          f"({int((t1-t0)*a.fps)} frames)", flush=True)
    ok, rc = render_range(tl, out, a.scale, a.fps, t0, t1, audio, total, a.crf, a.preset, "2",
                          a.x264_params, a.x264_threads)
    print(json.dumps({"frames_written": ok, "ffmpeg_exit": rc, "out": str(out),
                      "bytes": out.stat().st_size if out.exists() else 0}, indent=2))
    return 0 if rc == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
