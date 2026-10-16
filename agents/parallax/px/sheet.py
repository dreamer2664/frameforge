#!/usr/bin/env python3
"""Build a labelled contact sheet from a folder of frame PNGs (evidence helper)."""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=4)
    ap.add_argument("--cell", type=int, default=480)
    args = ap.parse_args()
    files = sorted(Path(args.src).glob("*.png"))
    if not files:
        raise SystemExit("no frames")
    cell = args.cell
    label_h = 26
    rows = (len(files) + args.cols - 1) // args.cols
    sheet = Image.new("RGB", (args.cols * cell, rows * (cell + label_h)), (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(f).convert("RGB")
        w, h = im.size
        sc = cell / w
        im = im.resize((cell, int(h * sc)), Image.LANCZOS)
        x = (i % args.cols) * cell
        y = (i // args.cols) * (cell + label_h)
        sheet.paste(im, (x, y))
        draw.text((x + 8, y + cell + 6), f.stem, fill=(235, 220, 200))
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out)
    print(args.out, sheet.size)


if __name__ == "__main__":
    main()
