#!/usr/bin/env python3
"""Craft probe — measurable depth evidence on a DELIVERED MP4 (lithos).

Because this production ran headless (no vision tool, no playback), the craft
bar's spatial claims are verified by measurement on decoded frames:

  * planarity_residual — mean abs residual after the best global translation
    is removed from consecutive frames. A flat-card film scores ~0 wherever
    nothing changes (Kinetic r03 measured 0 px translation in 53/53 steps);
    a real 3D scene keeps a structured residual wherever near and far planes
    disagree (parallax/occlusion).
  * block_parallax — independent integer shifts of a 3x3 grid of blocks
    between consecutive samples; the spread of block shifts is direct
    evidence of layered motion (a flat card has zero spread).
  * occlusion_edges — count of strong depth-discontinuity candidates
    (large local gradient of the block-shift field).
  * plus luma / edge energy / dark & hot fractions per sample.

Usage:
  python3 tools/craft_probe.py --video work/renders/hero-master.mp4 \
      --every 0.5 --out work/qc/craft-hero.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

FFMPEG = str(Path.home() / ".cache" / "frameforge" / "bin" / "ffmpeg")


def extract(video, every, out_dir):
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for f in out_dir.glob("*.png"):
        f.unlink()
    fps = 1.0 / every
    subprocess.check_call([FFMPEG, "-v", "error", "-y", "-i", str(video),
                           "-vf", f"fps={fps}", "-q:v", "2", str(out_dir / "f_%04d.png")])
    return sorted(out_dir.glob("*.png"))


def block_shifts(a, b, blocks=3, search=12):
    """Integer shift of each block of `a` best matching `b`."""
    H, W = a.shape
    bh, bw = H // blocks, W // blocks
    shifts = np.zeros((blocks, blocks, 2), dtype=np.int32)
    for bi in range(blocks):
        for bj in range(blocks):
            pa = a[bi * bh:(bi + 1) * bh, bj * bw:(bj + 1) * bw]
            pa = pa - pa.mean()
            best, bs = (0, 0), -1e18
            for dy in range(-search, search + 1, 2):
                for dx in range(-search, search + 1, 2):
                    y0, x0 = bi * bh + dy, bj * bw + dx
                    if y0 < 0 or x0 < 0 or y0 + bh > H or x0 + bw > W:
                        continue
                    pb = b[y0:y0 + bh, x0:x0 + bw]
                    pb = pb - pb.mean()
                    v = float((pa * pb).sum())
                    if v > bs:
                        bs, best = v, (dy, dx)
            shifts[bi, bj] = best
    return shifts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--every", type=float, default=0.5)
    ap.add_argument("--out", required=True)
    ap.add_argument("--work", default=None)
    args = ap.parse_args()
    work = Path(args.work or (Path(args.out).parent / "_frames"))
    files = extract(args.video, args.every, work)
    rows = []
    prev = None
    prev_blocks = None
    for i, f in enumerate(files):
        img = np.asarray(Image.open(f).convert("RGB"), dtype=np.float32) / 255.0
        g = img @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
        gs = g[::4, ::4]
        edge = float(np.abs(np.diff(g, axis=1)).mean() + np.abs(np.diff(g, axis=0)).mean())
        row = {
            "t": round(i * args.every, 3),
            "luma": round(float(g.mean()), 4),
            "edge": round(edge, 4),
            "dark_pct": round(float((g < 0.10).mean() * 100), 2),
            "hot_pct": round(float((g > 0.95).mean() * 100), 2),
        }
        if prev is not None:
            # best global shift (coarse grid then refine) on the downsample
            best, bs = (0, 0), -1e18
            for dy in range(-8, 9):
                for dx in range(-8, 9):
                    y0, x0 = 8 + dy, 8 + dx
                    pb = gs[y0:y0 + gs.shape[0] - 16, x0:x0 + gs.shape[1] - 16]
                    pa = gs[8:8 + pb.shape[0], 8:8 + pb.shape[1]]
                    v = float((pa * pb).sum())
                    if v > bs:
                        bs, best = v, (dy, dx)
            dy, dx = best
            H, W = g.shape
            yy, xx = np.mgrid[0:H, 0:W]
            sy, sx = np.clip(yy - dy * 4, 0, H - 1), np.clip(xx - dx * 4, 0, W - 1)
            comp = prev[sy, sx]  # previous frame, resampled at the global shift
            residual = float(np.abs(comp - g)[8:-8, 8:-8].mean())
            row["global_shift_px"] = [dx * 4, dy * 4]
            row["planarity_residual"] = round(residual, 4)
            row["inter_diff"] = round(float(np.abs(g - prev).mean()), 4)
            bl = block_shifts(gs, prev[::4, ::4] if prev.shape != gs.shape else gs, blocks=3, search=6)
            # block shifts of CURRENT frame matching PREVIOUS (inverted motion)
            b0 = block_shifts(gs, prev[::4, ::4], blocks=3, search=6)
            spread = float(np.std(b0.reshape(-1, 2), axis=0).mean())
            row["block_spread_px"] = round(spread, 2)
            row["block_shifts"] = b0.reshape(-1, 2).tolist()
            # occlusion candidates: neighbouring blocks that disagree strongly
            d = 0
            for bi in range(3):
                for bj in range(3):
                    for di, dj in ((0, 1), (1, 0)):
                        if bi + di < 3 and bj + dj < 3:
                            v = np.abs(b0[bi, bj] - b0[bi + di, bj + dj]).sum()
                            if v >= 6:
                                d += 1
            row["occlusion_edges"] = d
        rows.append(row)
        prev = g
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps({"video": str(args.video), "every": args.every,
                                          "samples": rows}, indent=1))
    # summary
    res = [r["planarity_residual"] for r in rows if "planarity_residual" in r]
    spr = [r["block_spread_px"] for r in rows if "block_spread_px" in r]
    occ = [r["occlusion_edges"] for r in rows if "occlusion_edges" in r]
    print(f"samples: {len(rows)}")
    print(f"planarity_residual: mean {np.mean(res):.4f} max {max(res):.4f}")
    print(f"block_spread_px:    mean {np.mean(spr):.2f} max {max(spr):.2f}")
    print(f"occlusion_edges:    mean {np.mean(occ):.1f} frames with >=1: "
          f"{sum(1 for o in occ if o >= 1)}/{len(occ)}")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
