#!/usr/bin/env python3
"""axiom props — scene furniture and explanatory objects.

Every prop is a plain function(ink, ...) in world coordinates so it can be staged,
scaled and lit like the characters. Props are meant to do explanatory work:
a rock shows strata, an hourglass shows a decay clock, a board carries a diagram.
"""
from __future__ import annotations

import math

from film.style import (DEEP, INK, INK_SOFT, MOSS, MOON, NIGHT2, OCHRE, PAPER, ROSE,
                    SAND, SAND_D, SLATE, SLATE_L, STONE, STONE_D, TERRA, WHITE, font)


# ---------------------------------------------------------------- furniture --
def table(ink, x, y, w=520, h=26, legs=200, top=(146, 108, 72), dark=(112, 80, 52)):
    ink.rrect(x - w / 2, y - h, x + w / 2, y, r=8, fill=top, outline=INK, width=4)
    ink.line([(x - w / 2 + 30, y), (x - w / 2 + 30, y + legs)], width=9, colour=dark)
    ink.line([(x + w / 2 - 30, y), (x + w / 2 - 30, y + legs)], width=9, colour=dark)


def bench(ink, x, y, w=760, h=30, legs=170):
    ink.rrect(x - w / 2, y - h, x + w / 2, y, r=6, fill=(158, 150, 138), outline=INK, width=4)
    ink.line([(x - w / 2 + 40, y), (x - w / 2 + 40, y + legs)], width=10, colour=(120, 114, 104))
    ink.line([(x + w / 2 - 40, y), (x + w / 2 - 40, y + legs)], width=10, colour=(120, 114, 104))
    ink.line([(x - 40, y - h + 8), (x - 40, y - 60)], width=5, colour=(120, 114, 104))
    ink.line([(x + 40, y - h + 8), (x + 40, y - 60)], width=5, colour=(120, 114, 104))


def chair(ink, x, y, s=1.0, col=(150, 112, 76)):
    ink.rrect(x - 46 * s, y - 20 * s, x + 46 * s, y + 6 * s, r=6 * s, fill=col, outline=INK, width=4 * s)
    ink.line([(x - 40 * s, y + 4 * s), (x - 40 * s, y + 96 * s)], width=8 * s, colour=col)
    ink.line([(x + 40 * s, y + 4 * s), (x + 40 * s, y + 96 * s)], width=8 * s, colour=col)
    ink.line([(x - 44 * s, y - 20 * s), (x - 44 * s, y - 128 * s)], width=9 * s, colour=col)
    ink.line([(x + 44 * s, y - 20 * s), (x + 44 * s, y - 128 * s)], width=9 * s, colour=col)
    ink.rrect(x - 50 * s, y - 128 * s, x - 30 * s, y - 40 * s, r=6 * s, fill=col, outline=INK, width=3.5 * s)
    ink.rrect(x + 30 * s, y - 128 * s, x + 50 * s, y - 40 * s, r=6 * s, fill=col, outline=INK, width=3.5 * s)


def chalkboard(ink, x, y, w=760, h=470, frame=(140, 104, 66), writing=None, title=None,
               chalk=(244, 246, 240), t=0.0, reveal=1.0):
    ink.rrect(x - w / 2 - 18, y - h / 2 - 18, x + w / 2 + 18, y + h / 2 + 18, r=10, fill=frame, outline=INK, width=5)
    ink.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, r=6, fill=(52, 84, 68), outline=INK, width=4)
    if title:
        ink.text((x - w / 2 + 30, y - h / 2 + 28), title, role="caps", size=40, fill=chalk)
    if writing:
        lines = writing if isinstance(writing, list) else [writing]
        for i, line in enumerate(lines):
            if reveal < i / max(1, len(lines)):
                continue
            role = "math" if any(c in line for c in "∇²−≈×÷") else "hand"
            ink.text((x - w / 2 + 34, y - h / 2 + 110 + i * 62), line, role=role, size=48, fill=chalk)


def wall_clock(ink, x, y, r=80, t=0.0, hands=True, face=(252, 248, 236)):
    ink.ellipse(x - r, y - r, x + r, y + r, fill=face, outline=INK, width=6)
    for i in range(12):
        a = i / 12 * 2 * math.pi
        ink.line([(x + math.sin(a) * r * 0.80, y - math.cos(a) * r * 0.80),
                  (x + math.sin(a) * r * 0.92, y - math.cos(a) * r * 0.92)], width=4, colour=INK_SOFT)
    if hands:
        a = t * 0.9
        ink.line([(x, y), (x + math.sin(a) * r * 0.5, y - math.cos(a) * r * 0.5)], width=7)
        ink.line([(x, y), (x + math.sin(a * 12) * r * 0.74, y - math.cos(a * 12) * r * 0.74)], width=5)


def hourglass(ink, x, y, s=1.0, fill=1.0, sand=(232, 176, 78), t=0.0, label=None):
    """fill: fraction of sand still in the top chamber (1 = just turned)."""
    w, h = 96 * s, 150 * s
    ink.poly([(x - w, y - h), (x + w, y - h), (x + 12 * s, y), (x - 12 * s, y)], fill=(236, 232, 222, 150),
             outline=INK, width=5 * s)
    ink.poly([(x - 12 * s, y), (x + 12 * s, y), (x + w, y + h), (x - w, y + h)], fill=(236, 232, 222, 150),
             outline=INK, width=5 * s)
    # sand
    top_h = (h - 16 * s) * max(0.02, fill)
    ink.poly([(x - w + 22 * s, y - h + 12 * s), (x + w - 22 * s, y - h + 12 * s),
              (x + 12 * s, y - h + 12 * s + top_h)], fill=sand)
    bot_h = (h - 20 * s) * (1.0 - fill)
    ink.poly([(x - w + 16 * s, y + h - 14 * s), (x + w - 16 * s, y + h - 14 * s),
              (x + 16 * s, y + h - 14 * s - bot_h), (x - 16 * s, y + h - 14 * s - bot_h)], fill=sand)
    if fill > 0.02:
        ink.line([(x, y - 10 * s), (x, y + 6 * s)], width=4 * s, colour=sand)
    ink.line([(x - w - 12 * s, y - h - 10 * s), (x + w + 12 * s, y - h - 10 * s)], width=10 * s)
    ink.line([(x - w - 12 * s, y + h + 10 * s), (x + w + 12 * s, y + h + 10 * s)], width=10 * s)
    for sx in (-1, 1):
        ink.line([(x + sx * (w + 6 * s), y - h - 6 * s), (x + sx * (w + 6 * s), y + h + 6 * s)], width=7 * s)
    if label:
        ink.text((x, y + h + 44 * s), label, role="caps", size=30 * s, fill=INK_SOFT, anchor="ma")


# ------------------------------------------------------------- earth & rock --
def strata_block(ink, x, y, w=900, h=280, layers=None, angle=0.0, sky=None):
    """A block of sedimentary layers, optionally tilted by `angle` radians."""
    layers = layers or [(0.0, 0.28, SAND_D), (0.28, 0.52, (198, 172, 138)), (0.52, 0.74, (176, 150, 118)),
                        (0.74, 1.0, (152, 128, 100))]
    cx, cy = x, y
    for a0, a1, col in layers:
        pts = []
        for (ux, uy) in ((-0.5, -a0), (0.5, -a0), (0.5, -a1), (-0.5, -a1)):
            px, py = ux * w, uy * h
            ca, sa = math.cos(angle), math.sin(angle)
            pts.append((cx + px * ca - py * sa, cy + px * sa + py * ca))
        ink.poly(pts, fill=col, outline=(120, 100, 80), width=2.2)
        ink.line([pts[3], pts[0]], width=2.4, colour=(120, 100, 80))


def cross_section_earth(ink, x, y, r=260, t=0.0, show_core=True, label_rings=True):
    ink.ellipse(x - r, y - r, x + r, y + r, fill=(58, 92, 76), outline=INK, width=6)
    ink.ellipse(x - r * 0.84, y - r * 0.84, x + r * 0.84, y + r * 0.84, fill=(196, 128, 78))
    ink.ellipse(x - r * 0.56, y - r * 0.56, x + r * 0.56, y + r * 0.56, fill=(226, 172, 96))
    if show_core:
        ink.ellipse(x - r * 0.26, y - r * 0.26, x + r * 0.26, y + r * 0.26, fill=(250, 232, 150))
    if label_rings:
        ink.text((x + r * 0.72, y - r * 0.72), "crust", role="caps", size=26, fill=INK_SOFT)
        ink.text((x + r * 0.38, y - r * 0.30), "mantle", role="caps", size=26, fill=(70, 44, 30))
        ink.text((x - r * 0.16, y + r * 0.06), "core", role="caps", size=26, fill=(120, 90, 20))


def gravestone(ink, x, y, s=1.0, text_top="1650", lines=("ANNO MUNDI", "710"), cracked=False):
    w, h = 120 * s, 168 * s
    ink.rrect(x - w / 2, y - h, x + w / 2, y + 10 * s, r=26 * s, fill=(196, 192, 184), outline=INK, width=5 * s)
    if cracked:
        ink.line([(x - w * 0.30, y - h + 6 * s), (x - w * 0.05, y - h * 0.55), (x + w * 0.22, y - h * 0.60)],
                 width=4 * s, colour=(120, 116, 110))
    ink.text((x, y - h + 28 * s), text_top, role="display", size=54 * s, fill=INK, anchor="ma")
    for i, line in enumerate(lines):
        ink.text((x, y - h + 96 * s + i * 30 * s), line, role="caps", size=26 * s, fill=(70, 70, 74), anchor="ma")


def outcrop_siccar(ink, x, y, s=1.0, top=None, frac=None):
    """Siccar Point in stylised section: a solid mass of near-vertical greywacke,
    bevelled flat by erosion, with shallow red sandstone laid on top.

    top/frac let a caller animate the two units separately (the four-step diagram)."""
    grey, grey_dark = (124, 128, 136), (74, 78, 86)
    reds = ((190, 100, 74), (172, 86, 66), (200, 112, 84), (166, 80, 62))
    x0, x1 = x - 340 * s, x + 340 * s          # extent of the lower unit
    ytop, ybot = y - 200 * s, y + 150 * s      # its top and bottom
    if frac is None or frac > 0.0:
        ink.poly([(x0 - 40 * s, ybot), (x1 + 40 * s, ybot), (x1 + 10 * s, ytop), (x0 - 10 * s, ytop)],
                 fill=grey, outline=grey_dark, width=4 * s)
        # bedding planes, steeply dipping to the right
        for i in range(9):
            bx = x0 + 40 * s + i * 78 * s
            ink.line([(bx + 26 * s, ytop + 6 * s), (bx - 24 * s, ybot - 6 * s)],
                     width=3 * s, colour=(96, 100, 108))
        # a couple of thin pale veins: this rock was squeezed
        for bx in (-220, 140):
            ink.line([(x + bx * s + 18 * s, ytop + 10 * s), (x + bx * s - 14 * s, ybot - 10 * s)],
                     width=2.4 * s, colour=(158, 160, 166))
    surf = [(x0 - 60 * s, ytop), (x - 150 * s, ytop - 6 * s), (x + 60 * s, ytop + 4 * s), (x1 + 60 * s, ytop - 2 * s)]
    if frac is None or frac > 0.45:
        ink.line(surf, width=7 * s, colour=(70, 74, 82))      # the erosion surface
    if frac is None or frac > 0.7:
        for i, col in enumerate(reds[:3]):                     # shallow red beds on top
            yy = ytop - 8 * s - i * 40 * s
            ink.poly([(x0 - 80 * s, yy + 6 * s), (x1 + 80 * s, yy - 2 * s),
                      (x1 + 80 * s, yy - 30 * s), (x0 - 80 * s, yy - 22 * s)],
                     fill=col, outline=(124, 62, 50), width=3 * s)
    if top is not None:
        return surf


def zircon(ink, x, y, s=1.0, glow=1.0):
    ink.poly([(x - 26 * s, y + 22 * s), (x - 10 * s, y - 34 * s), (x + 12 * s, y - 38 * s),
              (x + 28 * s, y + 10 * s), (x + 4 * s, y + 30 * s)], fill=(226, 196, 130), outline=INK, width=4 * s)
    if glow > 0:
        for i in range(3):
            r = (30 + i * 12) * s * (0.6 + glow * 0.6)
            ink.ellipse(x - r, y - r, x + r, y + r, outline=(240, 210, 150, 90 - i * 22), width=2.5 * s)


def meteorite(ink, x, y, s=1.0):
    ink.poly([(x - 70 * s, y - 20 * s), (x - 30 * s, y - 66 * s), (x + 46 * s, y - 58 * s),
              (x + 76 * s, y + 6 * s), (x + 24 * s, y + 56 * s), (x - 48 * s, y + 44 * s)],
             fill=(74, 70, 78), outline=(40, 38, 44), width=5 * s)
    for (dx, dy, rr) in ((-24, -14, 12), (18, -6, 9), (6, 26, 11), (-30, 18, 8)):
        ink.ellipse(x + dx * s - rr * s, y + dy * s - rr * s, x + dx * s + rr * s, y + dy * s + rr * s,
                    fill=(58, 54, 62))


# ------------------------------------------------------ books and documents --
def book(ink, x, y, w=220, h=300, title="", colour=(150, 62, 58), s=1.0, spine=True, sub=""):
    ink.rrect(x - w / 2, y - h, x + w / 2, y, r=8, fill=colour, outline=INK, width=5)
    ink.rrect(x - w / 2 + 12, y - h + 22, x + w / 2 - 12, y - 22, r=5, fill=(236, 224, 196), outline=INK, width=3)
    if title:
        cols = title.split("\n")
        for i, line in enumerate(cols):
            ink.text((x, y - h * 0.62 + i * 40 * s), line, role="display", size=34 * s, fill=INK, anchor="ma")
    if sub:
        ink.text((x, y - 60 * s), sub, role="caps", size=24 * s, fill=(90, 84, 76), anchor="ma")


def open_folio(ink, x, y, s=1.0, title="ANNALES", left_lines=0, right_gloss=True):
    w, h = 300 * s, 190 * s
    ink.poly([(x - w, y - 20 * s), (x, y - 46 * s), (x + w, y - 20 * s), (x + w, y + h - 30 * s),
              (x, y + h), (x - w, y + h - 30 * s)], fill=(238, 228, 202), outline=INK, width=4 * s)
    ink.line([(x, y - 44 * s), (x, y + h - 2 * s)], width=3.4 * s, colour=(150, 138, 116))
    ink.text((x - w * 0.52, y + 6 * s), title, role="display", size=40 * s, fill=(60, 54, 48))
    for i in range(left_lines):
        ink.line([(x - w * 0.52, y + (52 + i * 22) * s), (x - w * 0.12, y + (50 + i * 22) * s)],
                 width=3 * s, colour=(120, 112, 100))
    if right_gloss:
        for i in range(5):
            ink.line([(x + w * 0.12, y + (40 + i * 24) * s), (x + w * 0.54, y + (38 + i * 24) * s)],
                     width=2.6 * s, colour=(150, 142, 128))


def scroll_paper(ink, x, y, s=1.0, w=520, h=180, lines=6):
    ink.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, r=8, fill=(246, 238, 216), outline=INK, width=4)
    for i in range(lines):
        ink.line([(x - w / 2 + 30, y - h / 2 + 30 + i * (h - 50) / max(1, lines - 1)),
                  (x + w / 2 - 30 - (18 if i % 3 else 0), y - h / 2 + 30 + i * (h - 50) / max(1, lines - 1))],
                 width=3, colour=(140, 132, 116))


def genealogy_grid(ink, x, y, s=1.0, rows=6, names=None, highlight=None, reveal=1.0):
    names = names or ["Adam", "Seth", "Enosh", "Kenan", "Mahalalel", "Jared"]
    ink.rrect(x - 210 * s, y - 40 * s, x + 210 * s, y + (rows * 46 + 20) * s, r=10,
              fill=(248, 242, 224), outline=INK, width=4.5)
    for i, n in enumerate(names[:rows]):
        if reveal < (i + 1) / rows:
            continue
        yy = y + i * 46 * s
        ink.ellipse(x - 178 * s, yy - 2 * s, x - 150 * s, yy + 26 * s, fill=SLATE_L, outline=INK, width=3)
        ink.text((x - 134 * s, yy + 2 * s), n, role="label", size=32 * s, fill=INK)
        ink.text((x + 150 * s, yy + 2 * s), f"{930 - i * 105}", role="caps", size=26 * s, fill=(120, 112, 100))
        if highlight == i:
            ink.rrect(x - 196 * s, yy - 8 * s, x + 196 * s, yy + 34 * s, r=8, outline=TERRA, width=4)


# ------------------------------------------------------------ lab and sky ----
def telescope(ink, x, y, s=1.0, aim=-0.5, t=0.0):
    ink.line([(x, y), (x - 44 * s, y + 130 * s)], width=8 * s, colour=(120, 96, 66))
    ink.line([(x, y), (x + 44 * s, y + 130 * s)], width=8 * s, colour=(120, 96, 66))
    ink.line([(x, y), (x, y + 140 * s)], width=8 * s, colour=(120, 96, 66))
    lens = (x + math.cos(aim) * 96 * s, y + math.sin(aim) * 96 * s)
    ink.line([(x, y), lens], width=26 * s, colour=(86, 108, 140))
    ink.ellipse(lens[0] - 26 * s, lens[1] - 26 * s, lens[0] + 26 * s, lens[1] + 26 * s, fill=(60, 82, 112),
                outline=INK, width=5 * s)
    ink.ellipse(x - 30 * s, y - 30 * s, x + 30 * s, y + 30 * s, fill=(120, 146, 176), outline=INK, width=5 * s)


def star_field(ink, times, cx=960, cy=420, r=520):
    for (a, rr, sz) in times:
        x = cx + math.cos(a) * rr
        y = cy + math.sin(a) * rr
        ink.ellipse(x - sz, y - sz, x + sz, y + sz, fill=(255, 255, 240))


def planet(ink, x, y, r=150, kind="earth", tilt=0.2, t=0.0):
    if kind == "earth":
        ink.ellipse(x - r, y - r, x + r, y + r, fill=(84, 138, 180), outline=INK, width=6)
        blobs = [(-0.4, -0.3, 0.34), (0.15, 0.1, 0.42), (0.5, -0.45, 0.22), (-0.15, 0.55, 0.26)]
        for (bx, by, bs) in blobs:
            ink.ellipse(x + bx * r - bs * r * 0.5, y + by * r - bs * r * 0.36,
                        x + bx * r + bs * r * 0.5, y + by * r + bs * r * 0.36, fill=(122, 166, 108))
    elif kind == "sun":
        ink.ellipse(x - r, y - r, x + r, y + r, fill=OCHRE, outline=(200, 140, 40), width=6)


def moon(ink, x, y, r=90):
    ink.ellipse(x - r, y - r, x + r, y + r, fill=MOON, outline=(200, 194, 172), width=4)
    for (dx, dy, rr) in ((-0.3, -0.2, 0.18), (0.25, 0.1, 0.24), (0.0, 0.45, 0.14)):
        ink.ellipse(x + dx * r - rr * r, y + dy * r - rr * r, x + dx * r + rr * r, y + dy * r + rr * r,
                    fill=(214, 206, 182))


def boat(ink, x, y, s=1.0, sail=True):
    ink.poly([(x - 120 * s, y), (x + 120 * s, y), (x + 86 * s, y + 52 * s), (x - 86 * s, y + 52 * s)],
             fill=(150, 104, 70), outline=INK, width=5 * s)
    if sail:
        ink.line([(x, y), (x, y - 210 * s)], width=7 * s, colour=(120, 86, 58))
        ink.poly([(x + 6 * s, y - 204 * s), (x + 96 * s, y - 60 * s), (x + 6 * s, y - 60 * s)],
                 fill=(240, 234, 214), outline=INK, width=4 * s)
        ink.poly([(x - 6 * s, y - 190 * s), (x - 84 * s, y - 60 * s), (x - 6 * s, y - 60 * s)],
                 fill=(226, 218, 196), outline=INK, width=4 * s)


def church(ink, x, y, s=1.0):
    ink.poly([(x - 90 * s, y), (x - 90 * s, y - 150 * s), (x + 90 * s, y - 150 * s), (x + 90 * s, y)],
             fill=(174, 168, 156), outline=INK, width=5 * s)
    ink.poly([(x - 100 * s, y - 150 * s), (x, y - 232 * s), (x + 100 * s, y - 150 * s)],
             fill=(140, 134, 124), outline=INK, width=5 * s)
    ink.rrect(x + 40 * s, y - 250 * s, x + 74 * s, y - 150 * s, r=4, fill=(174, 168, 156), outline=INK, width=4)
    ink.poly([(x + 36 * s, y - 250 * s), (x + 57 * s, y - 296 * s), (x + 78 * s, y - 250 * s)],
             fill=(140, 134, 124), outline=INK, width=4)
    ink.line([(x + 57 * s, y - 320 * s), (x + 57 * s, y - 300 * s)], width=4 * s)
    ink.line([(x + 49 * s, y - 312 * s), (x + 65 * s, y - 312 * s)], width=4 * s)
    ink.rrect(x - 26 * s, y - 96 * s, x + 26 * s, y, r=18 * s, fill=(110, 96, 78), outline=INK, width=4)


def lab_bench(ink, x, y, s=1.0, t=0.0, bubbles=True):
    ink.rrect(x - 300 * s, y - 20 * s, x + 300 * s, y + 12 * s, r=6, fill=(156, 148, 136), outline=INK, width=4)
    ink.line([(x - 260 * s, y), (x - 260 * s, y + 150 * s)], width=10 * s, colour=(124, 118, 108))
    ink.line([(x + 260 * s, y), (x + 260 * s, y + 150 * s)], width=10 * s, colour=(124, 118, 108))
    for i, (dx, col) in enumerate(((-160, (168, 210, 214)), (-60, (206, 170, 196)), (60, (176, 206, 168)),
                                   (170, (224, 200, 150)))):
        bx = x + dx * s
        ink.rrect(bx - 26 * s, y - 76 * s, bx + 26 * s, y - 18 * s, r=8, fill=(238, 242, 240, 210),
                  outline=INK, width=3.6 * s)
        fill_h = (44 + 14 * math.sin(t * (1.0 + i * 0.4))) * s
        ink.rrect(bx - 22 * s, y - 22 * s - fill_h, bx + 22 * s, y - 22 * s, r=6, fill=col)
        if bubbles:
            for j in range(2):
                rr = (4 + 2 * j) * s
                by = y - 30 * s - ((t * 30 + j * 22) % 40) * s
                ink.ellipse(bx - rr, by - rr, bx + rr, by + rr, outline=(230, 236, 238), width=2)


def micro_scope(ink, x, y, s=1.0):
    ink.rrect(x - 26 * s, y - 150 * s, x + 26 * s, y - 60 * s, r=8, fill=(96, 104, 116), outline=INK, width=4)
    ink.line([(x, y - 60 * s), (x, y - 14 * s)], width=10 * s, colour=(96, 104, 116))
    ink.rrect(x - 70 * s, y - 20 * s, x + 60 * s, y + 10 * s, r=6, fill=(120, 128, 140), outline=INK, width=4)
    ink.line([(x - 40 * s, y - 40 * s), (x + 30 * s, y - 78 * s)], width=8 * s, colour=(120, 128, 140))
    ink.ellipse(x + 24 * s, y - 92 * s, x + 46 * s, y - 70 * s, outline=INK, width=3.5 * s)


def mass_spectrometer(ink, x, y, s=1.0, t=0.0):
    ink.rrect(x - 190 * s, y - 190 * s, x + 190 * s, y + 40 * s, r=16, fill=(178, 184, 190, 255),
              outline=INK, width=5)
    ink.rrect(x - 150 * s, y - 156 * s, x + 150 * s, y - 40 * s, r=10, fill=(58, 66, 78), outline=INK, width=4)
    for i in range(6):
        ink.ellipse(x - 130 * s + i * 44 * s, y - 120 * s, x - 104 * s + i * 44 * s, y - 94 * s,
                    fill=(120, 200, 220) if i % 2 else (232, 176, 92))
    ink.rrect(x - 120 * s, y - 26 * s, x + 120 * s, y + 26 * s, r=8, fill=(96, 104, 116), outline=INK, width=4)
    ink.text((x, y - 6 * s), "ISOTOPE  RATIOS", role="caps", size=26 * s, fill=(240, 240, 236), anchor="mm")
    ink.line([(x - 190 * s, y + 40 * s), (x - 190 * s, y + 150 * s)], width=12 * s, colour=(140, 146, 152))
    ink.line([(x + 190 * s, y + 40 * s), (x + 190 * s, y + 150 * s)], width=12 * s, colour=(140, 146, 152))


def printer_paper(ink, x, y, s=1.0, line="4.55", t=0.0, frac=1.0):
    ink.rrect(x - 150 * s, y - 96 * s, x + 150 * s, y + 30 * s, r=6, fill=(252, 250, 244), outline=INK, width=4)
    ink.text((x, y - 30 * s), line[: max(1, int(len(line) * frac))], role="display", size=76 * s,
             fill=INK, anchor="mm")


def rock_layers_tilt(ink, x, y, w=700, h=220, angle=0.35, layers=5, palette=None):
    palette = palette or [(178, 150, 118), (156, 128, 98), (196, 172, 140), (140, 116, 90), (206, 186, 156)]
    for i in range(layers):
        yy = y - i * (h / layers)
        ink.poly([(x - w / 2, yy), (x + w / 2, yy - w * angle), (x + w / 2, yy - w * angle + h / layers),
                  (x - w / 2, yy + h / layers)], fill=palette[i % len(palette)], outline=(110, 92, 72), width=2.4)


def tunnel(ink, x, y, s=1.0, depth=520):
    """A borehole cross-section: rock hatch, then a warming core with a thermometer."""
    ink.poly([(x - 96 * s, y), (x + 96 * s, y), (x + 60 * s, y + depth * s), (x - 60 * s, y + depth * s)],
             fill=(186, 176, 158), outline=INK, width=4)
    for i in range(14):                      # rock hatch either side of the hole
        yy = y + 26 * s + i * (depth * s - 40 * s) / 14
        ink.line([(x - 92 * s, yy), (x - 70 * s, yy + 16 * s)], width=2.6 * s, colour=(150, 140, 124))
        ink.line([(x + 70 * s, yy), (x + 92 * s, yy + 16 * s)], width=2.6 * s, colour=(150, 140, 124))
    ink.poly([(x - 30 * s, y), (x + 30 * s, y), (x + 18 * s, y + depth * s), (x - 18 * s, y + depth * s)],
             fill=(120, 108, 96), outline=INK, width=3)
    n = 10
    for i in range(n):                       # the gradient: cool near the surface, warm deep
        k = i / (n - 1)
        yy = y + k * depth * s
        warm = (140 + int(100 * k), 90 + int(20 * k), 66 - int(30 * k))
        ink.rrect(x - 28 * s, yy, x + 28 * s, yy + depth * s / n + 1, r=0, fill=warm)
    ink.line([(x, y + 6 * s), (x, y + depth * s - 8 * s)], width=5, colour=(248, 246, 236))
    ink.ellipse(x - 14 * s, y + depth * s - 4 * s, x + 14 * s, y + depth * s + 26 * s,
                fill=(232, 96, 76), outline=INK, width=3)


def hill(ink, x, y, w=900, h=220, col=MOSS, col2=(88, 116, 62)):
    ink.ellipse(x - w / 2, y - h * 2, x + w / 2, y + h * 0.2, fill=col)
    ink.ellipse(x - w / 3, y - h * 1.6, x + w * 0.6, y + h * 0.2, fill=col2)


def grass(ink, x, y, w=1920, cluster=14, col=MOSS):
    for i in range(cluster):
        bx = x - w / 2 + i * (w / cluster)
        ink.line([(bx, y), (bx - 6, y - 16), (bx - 2, y - 30)], width=3, colour=col)


def tent(ink, x, y, s=1.0, col=(196, 140, 96)):
    ink.poly([(x - 150 * s, y), (x, y - 190 * s), (x + 150 * s, y)], fill=col, outline=INK, width=5)
    ink.poly([(x - 40 * s, y), (x, y - 96 * s), (x + 40 * s, y)], fill=(120, 84, 56), outline=INK, width=4)


def wheelbarrow(ink, x, y, s=1.0, load=(150, 120, 90)):
    ink.poly([(x - 90 * s, y - 40 * s), (x + 70 * s, y - 40 * s), (x + 46 * s, y + 20 * s),
              (x - 70 * s, y + 20 * s)], fill=(140, 148, 156), outline=INK, width=4)
    ink.poly([(x - 80 * s, y - 40 * s), (x + 60 * s, y - 40 * s), (x + 34 * s, y - 78 * s),
              (x - 52 * s, y - 78 * s)], fill=load, outline=INK, width=4)
    ink.ellipse(x - 96 * s, y + 4 * s, x - 44 * s, y + 56 * s, outline=INK, width=6 * s)
    ink.line([(x + 60 * s, y - 8 * s), (x + 150 * s, y - 44 * s)], width=8 * s, colour=(140, 148, 156))


def arrow(ink, x0, y0, x1, y1, w=6, colour=TERRA, head=22, curved=0.0):
    if curved:
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2 - curved
        pts = []
        for i in range(17):
            u = i / 16
            px = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u * u * x1
            py = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u * u * y1
            pts.append((px, py))
        ink.line(pts, width=w, colour=colour)
        x0, y0 = pts[-6]
    else:
        ink.line([(x0, y0), (x1, y1)], width=w, colour=colour)
    a = math.atan2(y1 - y0, x1 - x0)
    ink.poly([(x1, y1), (x1 - head * math.cos(a - 0.4), y1 - head * math.sin(a - 0.4)),
              (x1 - head * math.cos(a + 0.4), y1 - head * math.sin(a + 0.4))], fill=colour)


def thought_bubble(ink, x, y, w=260, h=150, text=None, role="label", size=34, tail=(0, 60)):
    ink.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, r=40, fill=WHITE, outline=INK, width=4)
    tx, ty = x + tail[0], y + h / 2 + tail[1]
    for i, r in enumerate((16, 10, 6)):
        ink.ellipse(tx - r, ty - r - i * 26, tx + r, ty + r - i * 26, fill=WHITE, outline=INK, width=3.4)
    if text:
        ink.text((x, y), text, role=role, size=size, fill=INK, anchor="mm")


def speech_bubble(ink, x, y, w=300, h=150, text=None, role="label", size=36, tail=(-80, 40)):
    ink.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, r=26, fill=WHITE, outline=INK, width=4)
    ink.poly([(x + tail[0], y + h / 2 - 6), (x + tail[0] + 40, y + h / 2 - 6), (x + tail[0] + 6, y + h / 2 + tail[1])],
             fill=WHITE, outline=INK)
    ink.line([(x + tail[0] + 3, y + h / 2 - 5), (x + tail[0] + 6, y + h / 2 + tail[1])], width=4)
    if text:
        ink.text((x, y), text, role=role, size=size, fill=INK, anchor="mm")


# ------------------------------------------------------------ set dressing --
def rug(ink, x, y, w=620, h=150, col=(178, 120, 96), col2=(150, 98, 78)):
    ink.rrect(x - w / 2, y - h, x + w / 2, y, r=14, fill=col, outline=(120, 80, 64), width=4)
    for i in range(3):
        ink.rrect(x - w / 2 + 34 + i * 44, y - h + 18, x - w / 2 + 60 + i * 44, y - 18, r=6,
                  fill=col2, outline=(120, 80, 64), width=2)


def bookshelf(ink, x, y, w=420, h=300, col=(140, 106, 74)):
    ink.rrect(x - w / 2, y - h, x + w / 2, y, r=8, fill=col, outline=(96, 72, 50), width=5)
    for row in range(2):
        yy = y - h + 26 + row * (h / 2)
        ink.line([(x - w / 2 + 10, yy + h / 2 - 40), (x + w / 2 - 10, yy + h / 2 - 40)], width=5, colour=(96, 72, 50))
        bx = x - w / 2 + 20
        seed = (row * 7 + int(x)) % 5
        while bx < x + w / 2 - 60:
            bw = (26 + ((bx + seed * 7) % 3) * 10)
            bh = (h / 2 - 60) * (0.72 + ((bx + seed) % 4) * 0.07)
            ink.rrect(bx, yy + h / 2 - 44 - bh, bx + bw, yy + h / 2 - 44, r=3,
                      fill=[(150, 90, 80), (96, 112, 130), (140, 130, 96), (110, 96, 120)][(int(bx) + seed) % 4],
                      outline=(88, 70, 60), width=2)
            bx += bw + 6


def window_view(ink, x, y, w=340, h=420, sky=(168, 200, 224), night=False):
    ink.rrect(x - w / 2 - 14, y - h / 2 - 14, x + w / 2 + 14, y + h / 2 + 14, r=10, fill=(126, 104, 80))
    ink.rrect(x - w / 2, y - h / 2, x + w / 2, y + h / 2, r=6,
              fill=(30, 38, 58) if night else sky)
    if night:
        for i in range(9):
            sx, sy = x - w / 2 + 30 + (i * 71) % (w - 60), y - h / 2 + 24 + (i * 47) % (h - 60)
            ink.ellipse(sx - 2, sy - 2, sx + 2, sy + 2, fill=(240, 238, 220))
        ink.ellipse(x + w * 0.22, y - h * 0.28, x + w * 0.22 + 46, y - h * 0.28 + 46, fill=(232, 226, 200))
    else:
        ink.ellipse(x - w * 0.24, y - h * 0.22, x - w * 0.24 + 70, y - h * 0.22 + 70, fill=(252, 244, 206))
        ink.poly([(x - w / 2, y + h * 0.22), (x - w * 0.1, y - h * 0.05), (x + w / 2, y + h * 0.26),
                  (x + w / 2, y + h / 2), (x - w / 2, y + h / 2)], fill=(126, 158, 118))
    ink.line([(x, y - h / 2), (x, y + h / 2)], width=8, colour=(126, 104, 80))
    ink.line([(x - w / 2, y), (x + w / 2, y)], width=8, colour=(126, 104, 80))
    # light spill on the floor
    ink.poly([(x - w / 2, y + h / 2), (x + w / 2, y + h / 2), (x + w * 0.9, y + h / 2 + 230),
              (x - w * 0.9, y + h / 2 + 230)], fill=(252, 244, 214, 40))


def plant(ink, x, y, s=1.0, pot=(178, 116, 92)):
    ink.poly([(x - 42 * s, y - 90 * s), (x + 42 * s, y - 90 * s), (x + 30 * s, y), (x - 30 * s, y)],
             fill=pot, outline=(126, 82, 64), width=4)
    for i, (dx, h, tilt) in enumerate(((-26, 110, -0.5), (0, 140, 0.0), (26, 96, 0.5), (-10, 120, -0.25), (12, 126, 0.3))):
        ink.line([(x + dx * s, y - 88 * s), (x + (dx + tilt * 40) * s, y - (88 + h) * s)],
                 width=5 * s, colour=(94, 128, 82))
        ink.ellipse(x + (dx + tilt * 40) * s - 22 * s, y - (88 + h) * s - 26 * s,
                    x + (dx + tilt * 40) * s + 22 * s, y - (88 + h) * s + 12 * s,
                    fill=(110, 148, 92), outline=(78, 108, 68), width=2.4 * s)


def lamp(ink, x, y, s=1.0, warm=True):
    ink.line([(x, y), (x, y - 150 * s)], width=7 * s, colour=(96, 88, 80))
    ink.poly([(x - 54 * s, y - 150 * s), (x + 54 * s, y - 150 * s), (x + 34 * s, y - 210 * s),
              (x - 34 * s, y - 210 * s)], fill=(214, 186, 132) if warm else (170, 176, 184),
             outline=(120, 100, 70), width=4)
    ink.ellipse(x - 40 * s, y - 12 * s, x + 40 * s, y + 12 * s, fill=(110, 100, 88))


def stool(ink, x, y, s=1.0, col=(150, 112, 78)):
    ink.rrect(x - 44 * s, y - 22 * s, x + 44 * s, y, r=8 * s, fill=col, outline=(104, 76, 52), width=4 * s)
    for dx in (-30, 30):
        ink.line([(x + dx * s, y), (x + dx * s * 1.2, y + 90 * s)], width=8 * s, colour=(104, 76, 52))


def notebook_stack(ink, x, y, n=4, col=(240, 232, 212)):
    for i in range(n):
        ink.rrect(x - 90 + i * 6, y - i * 12, x + 90 - i * 6, y - 8 - i * 12, r=4,
                  fill=col, outline=(170, 158, 136), width=3)


def rock_sample(ink, x, y, s=1.0, col=(120, 118, 124)):
    """An angular, faceted rock chunk (not a bell): reads as stone at any size."""
    ink.poly([(x - 46 * s, y), (x - 34 * s, y - 30 * s), (x - 10 * s, y - 52 * s),
              (x + 20 * s, y - 46 * s), (x + 42 * s, y - 20 * s), (x + 34 * s, y)],
             fill=col, outline=(70, 70, 76), width=4 * s)
    ink.poly([(x - 34 * s, y - 30 * s), (x - 10 * s, y - 52 * s), (x - 4 * s, y - 22 * s)],
             fill=(min(255, col[0] + 22), min(255, col[1] + 22), min(255, col[2] + 22)),
             outline=(70, 70, 76), width=3)
    ink.line([(x - 4 * s, y - 22 * s), (x + 42 * s, y - 20 * s)], width=2.4 * s, colour=(92, 92, 98))
    ink.line([(x - 4 * s, y - 22 * s), (x + 10 * s, y)], width=2.4 * s, colour=(92, 92, 98))
