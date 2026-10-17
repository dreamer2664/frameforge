#!/usr/bin/env python3
"""Render single frames of the film to PNG for fast visual checks."""
import argparse
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import post
import render3d as R
import scene as S


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--times", default="10")
    ap.add_argument("--out", default="work/preview")
    ap.add_argument("--kind", default="hero")
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--subframes", type=int, default=1)
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    film = S.Film()
    times = [float(x) for x in args.times.split(",")]
    for t in times:
        t0 = time.time()
        acc = None
        dacc = None
        for s in range(args.subframes):
            u = (s + 0.5) / args.subframes - 0.5
            ts = t + u * 0.5 / film.story["format"]["fps"]
            if args.kind == "loop":
                cam = film.loop_camera(ts)
                sc = film.build_loop(ts, cam=cam)
            else:
                cam = film.camera(ts)
                sc = film.build(ts, cam=cam)
            r = R.render(sc, cam, args.width, args.height)
            acc = r.color if acc is None else acc + r.color
            dacc = r.depth if dacc is None else dacc + r.depth
        acc /= args.subframes
        dacc /= args.subframes
        k = S.sample_keys(film.story["camera"]["keys"], t, ["eye", "target"])
        focus = float(np.linalg.norm(np.asarray(k["target"], float) - np.asarray(k["eye"], float)))
        img = post.finish(acc, dacc, frame_index=int(t * 100), focus=focus)
        p = out / f"{args.kind}-{t:06.2f}.png"
        Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8)).save(p)
        print(f"{p}  ({time.time()-t0:.1f}s)")


if __name__ == "__main__":
    main()
