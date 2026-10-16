#!/usr/bin/env python3
"""Poster + YouTube thumbnail, drawn with the film's own toolkit so they match exactly.

  python3 tools/poster.py --outdir final
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from PIL import Image  # noqa: E402

from film import props as P  # noqa: E402
from film.style import (INK, PAPER, SLATE, TERRA, Ink, font, paper_bg)  # noqa: E402

GOLD = (216, 155, 60)
GREEN = (110, 139, 75)
DARK = (28, 34, 52)


def title_block(ik: Ink, cx: int, y: int, big: int, small: int, fit: str = "How Old Is the Earth?"):
    ik.text((cx, y), fit, role="display", size=big, fill=INK, anchor="ma")
    ik.text((cx, y + int(big * 0.78)), "Three clocks that had to be broken",
            role="label", size=small, fill=SLATE, anchor="ma")


def four_marks(ik: Ink, cx: int, y: int, gap: int, scale: float = 1.0, labels: bool = True):
    xs = [cx - 1.5 * gap, cx - 0.5 * gap, cx + 0.5 * gap, cx + 1.5 * gap]
    P.scroll_paper(ik, xs[0], y + 30 * scale, s=0.55 * scale, w=230 * scale, h=150 * scale, lines=4)
    P.planet(ik, xs[1], y - 6 * scale, r=int(58 * scale), kind="sun")
    P.hourglass(ik, xs[2], y, s=0.62 * scale, fill=0.55, t=0.0)
    P.meteorite(ik, xs[3], y + 6 * scale, s=0.72 * scale)
    if labels:
        for x, (name, year) in zip(xs, (("a book", "1650"), ("a cooling ball", "1862"),
                                        ("an hourglass", "1904"), ("a meteorite", "1956"))):
            ik.text((x, y + 152 * scale), name, role="label", size=int(46 * scale),
                    fill=(78, 74, 68), anchor="ma")
            ik.text((x, y + 198 * scale), year, role="caps", size=int(38 * scale),
                    fill=TERRA, anchor="ma")


def strata(ik: Ink, w: int, h: int, band: int = 168) -> None:
    """The film's own motif: flat beds, then steep grey beds cut off across them."""
    for i, col in enumerate(((198, 188, 168), (176, 162, 142), (150, 134, 116), (126, 110, 94))):
        yy = h - band + i * (band // 4)
        ik.rrect(-20, yy, w + 20, yy + band // 4 + 2, r=0, fill=col)
    ik.line([(-20, h - band), (w + 20, h - band + 4)], width=8, colour=(92, 80, 68))
    for i in range(9):
        x = 80 + i * 230
        ik.poly([(x, h - 6), (x + 104, h - 6), (x + 60, h - band + 16), (x - 44, h - band + 16)],
                fill=(122, 126, 134), outline=(74, 78, 86), width=3)
    for i in range(9):
        x = 80 + i * 230
        ik.line([(x - 44, h - band + 16), (x + 60, h - band + 16)], width=4, colour=(58, 62, 70))


def poster(w=1920, h=1080) -> Image.Image:
    img = paper_bg(w, h, tint=(252, 240, 214), vignette=0.09)
    ik = Ink(img)
    strata(ik, w, h, band=150)
    ik.text((w // 2, 182), "How Old Is the Earth?", role="display", size=126, fill=INK, anchor="ma")
    ik.text((w // 2, 330), "Three clocks that had to be broken", role="label", size=62, fill=SLATE, anchor="ma")
    ik.line([(w // 2 - 460, 438), (w // 2 + 460, 438)], width=5, colour=(176, 166, 150))
    four_marks(ik, w // 2, 556, 430, 1.05)
    ik.text((w // 2, 806), "in 1788 the answer was that there is no number at all",
            role="sans", size=38, fill=(96, 90, 82), anchor="ma")
    ik.text((w // 2, 858), "axiom   ·   15 minutes 44 seconds   ·   sources and credits in the release notes",
            role="caps", size=30, fill=(84, 78, 70), anchor="ma")
    return img


def thumb(w=1280, h=720) -> Image.Image:
    img = paper_bg(w, h, tint=(252, 240, 214), vignette=0.12, grain_strength=4)
    ik = Ink(img)
    strata(ik, w, h, band=132)
    ik.text((w // 2, 132), "How Old", role="display", size=148, fill=INK, anchor="ma")
    ik.text((w // 2, 262), "Is the Earth?", role="display", size=148, fill=INK, anchor="ma")
    ik.text((w // 2, 430), "four clocks, one number", role="label", size=64, fill=TERRA, anchor="ma")
    ik.text((40, 60), "axiom", role="caps", size=46, fill=(96, 90, 82), anchor="la")
    return img


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--outdir", default=str(ROOT / "final"))
    args = ap.parse_args()
    out = Path(args.outdir)
    out.mkdir(parents=True, exist_ok=True)
    p = out / "axiom-poster-1920x1080.png"
    t = out / "axiom-thumbnail-1280x720.jpg"
    poster().save(p)
    thumb().save(t, quality=92)
    print(f"{p}\n{t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
