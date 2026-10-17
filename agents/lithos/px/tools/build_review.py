#!/usr/bin/env python3
"""Build review contact sheets from the QC extractions (reproducible)."""
import sys
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
QC = ROOT / "work" / "qc"
OUT = ROOT / "work" / "review"


def sheet(files, cols, cell_w, out, title):
    if not files:
        return
    rows = (len(files) + cols - 1) // cols
    im0 = Image.open(files[0])
    ar = im0.height / im0.width
    cw, ch = cell_w, int(cell_w * ar)
    pad, top = 6, 34
    s = Image.new("RGB", (cols * cw + pad * (cols + 1), rows * ch + pad * (rows + 1) + top), (18, 18, 18))
    d = ImageDraw.Draw(s)
    d.text((10, 9), f"{title}   ({len(files)} frames; full-size PNGs are in work/qc/)", fill=(230, 230, 230))
    for i, f in enumerate(files):
        r, c = divmod(i, cols)
        th = Image.open(f).resize((cw, ch), Image.LANCZOS)
        x, y = pad + c * (cw + pad), top + pad + r * (ch + pad)
        s.paste(th, (x, y))
        d.text((x + 3, y + 3), f.stem[1:], fill=(255, 220, 120))
    s.save(out)
    print("wrote", out)


def main():
    OUT.mkdir(exist_ok=True)
    frames = sorted((QC / "frames").glob("t*.png"))
    for i in range(0, len(frames), 21):
        sheet(frames[i:i + 21], 7, 260, OUT / f"sheet-{i // 21:02d}.png",
              f"KINETIC hero r01 — every 0.5 s, frames {i}-{min(i + 21, len(frames)) - 1}")
    sheet(sorted((QC / "phone").glob("t*.png")), 7, 180, OUT / "sheet-phone.png",
          "KINETIC hero r01 — 640x360 phone check (every 1.0 s)")
    sheet(sorted((QC / "dense").glob("t*.png")), 11, 150, OUT / "sheet-dense.png",
          "KINETIC hero r01 — dense 0.05 s samples at beat centres")
    sheet(sorted((QC / "gate" / "edge").glob("edge_*.png")), 4, 300, OUT / "sheet-loop.png",
          "KINETIC loop r01 — encoded loop edge frames (last 4, first 4) + numeric gate in work/qc/technical.json")


if __name__ == "__main__":
    main()
