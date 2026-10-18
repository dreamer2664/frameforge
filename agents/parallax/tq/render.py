#!/usr/bin/env python3
"""Render the reel.

The film is one self-contained html file; this drives it in Chromium frame by
frame (FLUX.seek(t) recomputes every element) and pipes the frames straight
into ffmpeg, so nothing lands on disk except the encoder's input.

    python3 render.py --out work/render/film-silent.mp4
    python3 render.py --times 1.2,2.8,4.2 --png-dir work/check   # spot frames
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve().parent
BUILD = HERE / "build" / "flux.html"
WORK = HERE / "work"
FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")
CHROME_ARGS = [
    "--no-sandbox",
    "--disable-dev-shm-usage",
    "--hide-scrollbars",
    "--force-color-profile=srgb",
    "--disable-lcd-text",
    "--font-render-hinting=none",
    "--disable-partial-raster",
]


def open_page(pw, scale: float):
    browser = pw.chromium.launch(args=CHROME_ARGS)
    ctx = browser.new_context(viewport={"width": 1920, "height": 1080},
                              device_scale_factor=scale, reduced_motion="reduce")
    page = ctx.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
    page.goto(BUILD.as_uri())
    page.wait_for_function("window.FLUX && window.FLUX.ready === true", timeout=30000)
    if errors:
        raise SystemExit("page errors: " + " | ".join(errors[:6]))
    return browser, ctx, page


def render(args) -> None:
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    frames = args.frames
    fps = args.fps
    cmd = [FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
           "-f", "image2pipe", "-vcodec", "png", "-r", str(fps), "-i", "-",
           "-an", "-c:v", "libx264", "-preset", args.preset, "-crf", str(args.crf),
           "-pix_fmt", "yuv420p", "-r", str(fps), "-movflags", "+faststart", str(out)]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    t0 = time.time()
    with sync_playwright() as pw:
        browser, ctx, page = open_page(pw, 1.0)
        try:
            for i in range(frames):
                t = i / fps
                page.evaluate(f"FLUX.seek({t:.6f})")
                png = page.screenshot(type="png")
                proc.stdin.write(png)
                if (i + 1) % 30 == 0:
                    el = time.time() - t0
                    print(f"  frame {i+1}/{frames}  {el:6.1f}s  {1000*el/(i+1):5.1f} ms/frame", flush=True)
            if args.poster:
                page.evaluate(f"FLUX.seek({args.poster_t:.6f})")
                page.screenshot(path=str(args.poster))
                print(f"  poster written: {args.poster}", flush=True)
        finally:
            browser.close()
    proc.stdin.close()
    rc = proc.wait()
    if rc != 0:
        raise SystemExit(f"ffmpeg exited {rc}")
    print(f"wrote {out} ({out.stat().st_size} bytes) in {time.time()-t0:.1f}s", flush=True)


def spot(args) -> None:
    """Render individual frames to png for review."""
    d = Path(args.png_dir)
    d.mkdir(parents=True, exist_ok=True)
    times = [float(x) for x in args.times.split(",")]
    with sync_playwright() as pw:
        browser, ctx, page = open_page(pw, 1.0)
        try:
            for t in times:
                page.evaluate(f"FLUX.seek({t:.6f})")
                name = d / (("t%06.2f" % t).replace(".", "_") + ".png")
                page.screenshot(path=str(name))
                print("  ", name, flush=True)
        finally:
            browser.close()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(WORK / "render" / "film-silent.mp4"))
    ap.add_argument("--frames", type=int, default=900)
    ap.add_argument("--fps", type=int, default=60)
    ap.add_argument("--crf", type=int, default=16)
    ap.add_argument("--preset", default="slow")
    ap.add_argument("--poster", default=str(WORK / "poster.png"))
    ap.add_argument("--poster-t", type=float, default=1.35)
    ap.add_argument("--times", default="")
    ap.add_argument("--png-dir", default=str(WORK / "check"))
    ap.add_argument("--no-poster", action="store_true")
    args = ap.parse_args()
    if not BUILD.exists():
        raise SystemExit("build/flux.html missing - run make_assets.py first")
    if args.times:
        spot(args)
        return
    if args.no_poster:
        args.poster = None
    render(args)


if __name__ == "__main__":
    main()
