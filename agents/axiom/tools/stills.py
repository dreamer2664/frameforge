#!/usr/bin/env python3
"""Render named stills straight from the timeline (no encoding), for review passes.

Usage:
  python3 tools/stills.py --timeline work/timeline.json --out work/review/r02 \
      --shots s21,s24,s27 --per-shot 2 --scale 1.0
  python3 tools/stills.py ... --times 250.0,612.5

Writes JPGs named <shot>-<t>s.jpg plus a contact sheet, and prints a manifest JSON.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from film.render import render_frame  # noqa: E402


def sheet(paths: list[Path], out: Path, cols: int = 4, tw: int = 460) -> Path:
    ims = [Image.open(p).convert("RGB") for p in paths]
    rows = (len(ims) + cols - 1) // cols
    th = int(tw * 9 / 16)
    sh = Image.new("RGB", (cols * tw, rows * th), (22, 22, 26))
    for i, im in enumerate(ims):
        sh.paste(im.resize((tw, th)), ((i % cols) * tw, (i // cols) * th))
    out.parent.mkdir(parents=True, exist_ok=True)
    sh.save(out, quality=88)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeline", default=str(ROOT / "work/timeline.json"))
    ap.add_argument("--out", required=True)
    ap.add_argument("--shots", default="", help="comma list of shot ids")
    ap.add_argument("--times", default="", help="comma list of times in seconds")
    ap.add_argument("--per-shot", type=float, default=2.0, help="how many stills per shot")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--tw", type=int, default=460)
    args = ap.parse_args()

    tl = json.loads(Path(args.timeline).read_text())
    outdir = Path(args.out)
    outdir.mkdir(parents=True, exist_ok=True)

    want: list[tuple[str, float]] = []
    shots = [s for s in args.shots.split(",") if s]
    for sid in shots:
        shot = next((s for s in tl["shots"] if s["id"] == sid), None)
        if not shot:
            print(f"no such shot {sid}")
            continue
        n = max(1, int(args.per_shot))
        for k in range(n):
            frac = (k + 1) / (n + 1)
            want.append((sid, round(shot["start"] + shot["dur"] * frac, 3)))
    for t in [x for x in args.times.split(",") if x]:
        tt = float(t)
        sid = next((s["id"] for s in tl["shots"] if s["start"] <= tt <= s["end"]), "t")
        want.append((sid, tt))

    made = []
    for sid, t in want:
        W, H = int(round(1920 * args.scale)), int(round(1080 * args.scale))
        img = render_frame(tl, t, args.scale, W, H)
        p = outdir / f"{sid}-{t:07.1f}s.jpg"
        img.save(p, quality=92)
        made.append(p)
    if made:
        sh = sheet(made, outdir / "sheet.jpg", cols=args.cols, tw=args.tw)
        print(json.dumps({"stills": [str(p) for p in made], "sheet": str(sh)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
