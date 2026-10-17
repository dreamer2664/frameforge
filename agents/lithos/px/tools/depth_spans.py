#!/usr/bin/env python3
"""Depth-span recorder — per-beat near/mid/far evidence from the render's own
depth buffer (lithos). Cheap: 960x540, one frame per beat.

Usage:
  python3 tools/depth_spans.py --times 0.5,2,5,10,14,19,23,28,33.5,41 \
      --out work/qc/depth-spans.json
"""
import argparse, json, sys
from pathlib import Path
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import scene as S
import render3d as R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--times", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--height", type=int, default=540)
    args = ap.parse_args()
    film = S.Film()
    rows = []
    for t in [float(x) for x in args.times.split(",")]:
        cam = film.camera(t)
        sc = film.build(t)
        r = R.render(sc, cam, args.width, args.height)
        d = np.asarray(r.depth, dtype=np.float64)
        d = d[np.isfinite(d) & (d > 0.05)]
        row = {
            "t": t,
            "d01": round(float(np.percentile(d, 1)), 2),
            "d05": round(float(np.percentile(d, 5)), 2),
            "d25": round(float(np.percentile(d, 25)), 2),
            "d50": round(float(np.percentile(d, 50)), 2),
            "d75": round(float(np.percentile(d, 75)), 2),
            "d95": round(float(np.percentile(d, 95)), 2),
            "span_d05_d95": round(float(np.percentile(d, 95) - np.percentile(d, 5)), 2),
            "eye": [round(float(x), 2) for x in cam.eye],
            "target": [round(float(x), 2) for x in cam.target],
        }
        rows.append(row)
        print(row)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"beats": rows}, indent=1))
    print("wrote", args.out)


if __name__ == "__main__":
    main()
