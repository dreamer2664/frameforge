#!/usr/bin/env python3
"""mg.build - render the film: frames -> H.264 + AAC mux, poster, contact sheets.

Fast windows get 3-tap subframe accumulation (motion blur), per the reference
craft notes and research/motion-design-research.md.
"""
import json
import subprocess
import sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent
SB = json.loads((ROOT / "storyboard.json").read_text())
W, H = SB["format"]["width"], SB["format"]["height"]
FPS = SB["format"]["fps"]
DUR = SB["format"]["duration_seconds"]
FF = "/home/user/.cache/frameforge/bin/ffmpeg"

FAST = [(1.25, 1.60), (2.68, 2.76), (5.18, 5.60), (6.62, 6.82),
        (8.48, 8.88), (10.02, 10.32), (11.78, 11.98)]


def in_fast(t):
    return any(a <= t <= b for a, b in FAST)


def render_frame(t):
    sys.path.insert(0, str(ROOT))
    import film
    if in_fast(t):
        taps = [t - 1 / 90, t, t + 1 / 90]
        arrs = [film.render_frame(max(0, tt)) for tt in taps]
        return (0.25 * arrs[0] + 0.5 * arrs[1] + 0.25 * arrs[2]).astype(np.uint8)
    return film.render_frame(t)


def main():
    out = ROOT / "out"
    out.mkdir(exist_ok=True)
    raw = out / "frames.raw"
    n = int(DUR * FPS)
    with open(raw, "wb") as fh:
        for i in range(n):
            t = i / FPS
            arr = render_frame(t)
            fh.write(arr.tobytes())
            if i % 30 == 0:
                print(f"frame {i}/{n} t={t:.2f}", flush=True)
    video = out / "title-machine.mp4"
    subprocess.run([FF, "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                    "-s", f"{W}x{H}", "-r", str(FPS), "-i", str(raw),
                    "-i", str(ROOT / "work" / "score.m4a"),
                    "-c:v", "libx264", "-preset", "slow", "-crf", "15",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart",
                    "-c:a", "copy", "-shortest", str(video)], check=True)
    # poster at the flip hold
    subprocess.run([FF, "-y", "-v", "error", "-ss", "9.2", "-i", str(video),
                    "-frames:v", "1", str(out / "poster.png")], check=True)
    print("wrote", video)


if __name__ == "__main__":
    main()
