#!/usr/bin/env python3
"""reel.build - 768 frames @60fps -> out/kinetic-reel.mp4 + out/poster.png"""
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import film

FF = str(Path.home() / ".cache/frameforge/bin/ffmpeg")
W, H, FPS = 1080, 1920, 60
DUR = 12.8
N = int(DUR * FPS)
OUT = Path("out")
OUT.mkdir(exist_ok=True)

cmd = [FF, "-y", "-hide_banner", "-loglevel", "error",
       "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
       "-i", "work/score.m4a",
       "-c:v", "libx264", "-preset", "medium", "-crf", "17", "-pix_fmt", "yuv420p",
       "-movflags", "+faststart", "-c:a", "aac", "-b:a", "192k", "-shortest",
       str(OUT / "kinetic-reel.mp4")]
proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
for n in range(N):
    t = n / FPS
    frame = film.render_frame(t)
    proc.stdin.write(frame.tobytes())
    if n % 60 == 0:
        print(f"frame {n}/{N} t={t:.2f}", flush=True)
proc.stdin.close()
proc.wait()
if proc.returncode != 0:
    raise SystemExit("ffmpeg failed")
print("wrote", OUT / "kinetic-reel.mp4")

# poster at the dashboard beat
Image.fromarray(film.render_frame(10.5)).save(OUT / "poster.png")
print("wrote", OUT / "poster.png")
