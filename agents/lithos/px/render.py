#!/usr/bin/env python3
"""Render the parallax film to H.264 segments.

Usage:
  python3 render.py --kind hero --start 0 --duration 6.0 --out work/renders/seg-01.mp4
  python3 render.py --kind loop --out work/renders/loop.mp4
  python3 render.py --kind hero --all --out work/renders/hero.mp4

Rendering is frame-time deterministic: subframes are sampled at fixed shutter
offsets and the post chain is a pure function of the frame index.
"""
from __future__ import annotations

import argparse
import math
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import post
import render3d as R
import scene as S

FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")


def camera_and_scene(film, kind, t):
    if kind == "loop":
        return film.loop_camera(t), film.build_loop(t)
    return film.camera(t), film.build(t)


def render_segment(film, kind, start, duration, out_path, width, height, fps,
                   subframes=2, shutter=0.5, focus=None, aperture=0.9, seed=0,
                   crf=16, log_every=10, motion_subframes=True, motion_threshold=0.08):
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    nframes = int(round(duration * fps))
    cmd = [FFMPEG, "-hide_banner", "-loglevel", "error", "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{width}x{height}",
           "-r", str(fps), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", str(crf),
           "-pix_fmt", "yuv420p", "-profile:v", "high", "-movflags", "+faststart",
           str(out_path)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t_start = time.time()
    try:
        for i in range(nframes):
            t = start + (i + 0.5) / fps
            acc = None
            depth_acc = None
            nsub = subframes
            if motion_subframes and subframes > 1:
                # only spend a second sample where the camera actually moves
                nsub = 2 if camera_speed(film, kind, t, fps) > motion_threshold else 1
            for s in range(nsub):
                u = (s + 0.5) / nsub - 0.5
                ts = t + u * shutter / fps
                cam, sc = camera_and_scene(film, kind, ts)
                jitter = ((s % 2) * 0.5 - 0.25, (s // 2) * 0.5 - 0.25) if subframes > 1 else (0.0, 0.0)
                r = R.render(sc, cam, width, height, jitter=jitter)
                if acc is None:
                    acc = r.color
                    depth_acc = r.depth
                else:
                    acc += r.color
                    depth_acc = r.depth
            acc /= nsub
            depth_acc /= nsub
            foc = focus if focus is not None else cam_focus(film, kind, t)
            img = post.finish(acc, depth_acc, frame_index=seed + i, focus=foc,
                              aperture=aperture)
            proc.stdin.write((np.clip(img, 0, 1) * 255.0 + 0.5).astype(np.uint8).tobytes())
            if (i + 1) % log_every == 0 or i == nframes - 1:
                el = time.time() - t_start
                rate = (i + 1) / max(el, 1e-6)
                print(f"  {kind} frame {i+1}/{nframes}  t={t:7.3f}s  "
                      f"{el:6.1f}s elapsed  {rate:5.2f} fps  eta {(nframes-i-1)/max(rate,1e-6):6.1f}s",
                      flush=True)
    finally:
        proc.stdin.close()
        proc.wait()
    print(f"wrote {out_path} ({out_path.stat().st_size} bytes, {nframes} frames)", flush=True)
    return out_path


def camera_speed(film, kind, t, fps):
    """Screen-space magnitude of the camera move per frame (metres)."""
    d = 0.5 / fps
    if kind == "loop":
        a = film.loop_camera(max(t - d, 0.0))
        b = film.loop_camera(t + d)
    else:
        a = film.camera(max(t - d, 0.0))
        b = film.camera(t + d)
    return float(np.linalg.norm(np.asarray(b.eye, float) - np.asarray(a.eye, float)))


def cam_focus(film, kind, t):
    """Focus distance: the point the camera is looking at."""
    if kind == "loop":
        return 9.0
    k = S.sample_keys(film.story["camera"]["keys"], t, ["eye", "target"])
    eye = np.asarray(k["eye"], float)
    tgt = np.asarray(k["target"], float)
    return float(np.linalg.norm(tgt - eye))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kind", choices=["hero", "loop"], default="hero")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float, default=0.0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=0)
    ap.add_argument("--height", type=int, default=0)
    ap.add_argument("--fps", type=int, default=0)
    ap.add_argument("--subframes", type=int, default=2)
    ap.add_argument("--shutter", type=float, default=0.5)
    ap.add_argument("--aperture", type=float, default=0.9)
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--no-motion-subframes", action="store_true")
    args = ap.parse_args()

    film = S.Film()
    st = film.story
    if args.kind == "loop":
        w = st["format"]["width"]
        h = st["format"]["height"]
        fps = st["loop"]["fps"]
        dur = st["loop"]["duration_seconds"]
    else:
        w = st["format"]["width"]
        h = st["format"]["height"]
        fps = st["format"]["fps"]
        dur = st["format"]["duration_seconds"]
    if args.width:
        w = args.width
        h = args.height or int(w * 9 / 16)
    if args.fps:
        fps = args.fps

    if args.all:
        # one file, whole timeline
        render_segment(film, args.kind, args.start, dur, args.out, w, h, fps,
                       subframes=args.subframes, shutter=args.shutter,
                       aperture=args.aperture, crf=args.crf,
                       motion_subframes=not args.no_motion_subframes)
    else:
        d = args.duration or (dur - args.start)
        render_segment(film, args.kind, args.start, d, args.out, w, h, fps,
                       subframes=args.subframes, shutter=args.shutter,
                       aperture=args.aperture, crf=args.crf,
                       motion_subframes=not args.no_motion_subframes)


if __name__ == "__main__":
    main()
