#!/usr/bin/env python3
"""Render real typography candidates at film scale so the choice is inspected, not assumed."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FD = Path(__file__).resolve().parents[1] / "assets/fonts"
OUT = Path(__file__).resolve().parents[1] / "work/typography-specimen.png"

CANDIDATES = [
    ("Caveat",        "Caveat[wght].ttf",       dict(wght=700)),
    ("Patrick Hand",  "PatrickHand-Regular.ttf", None),
    ("Patrick HandSC","PatrickHandSC-Regular.ttf", None),
    ("Playpen Sans",  "PlaypenSans[wght].ttf",  dict(wght=600)),
    ("Archivo Black", "ArchivoBlack-Regular.ttf", None),
    ("Nunito",        "Nunito[wght].ttf",       dict(wght=800)),
    ("Lexend",        "Lexend[wght].ttf",       dict(wght=600)),
    ("Inter",         "Inter[opsz,wght].ttf",   dict(wght=600, opsz=32)),
    ("Public Sans",   "PublicSans[wght].ttf",   dict(wght=650)),
]
TITLE = "How Old Is the Earth?"
LABEL = "no vestige of a beginning"
NUMB  = "4.54 billion years  \u2022  4004 BC  \u2022  1650"

def load(fn, size, axes):
    """axes: {'Weight': 700, 'Optical size': 32} — values applied in font axis order."""
    f = ImageFont.truetype(str(FD / fn), size)
    if axes:
        names = [a["name"] for a in f.get_variation_axes()]
        vals = [axes.get(n, a["default"]) for n, a in zip(names, f.get_variation_axes())]
        f.set_variation_by_axes(vals)
    return f

W, H = 1920, 1500
img = Image.new("RGB", (W, H), (247, 243, 233))
d = ImageDraw.Draw(img)
y = 26
d.text((40, y), "axiom typography candidate comparison \u2014 rendered with the actual film renderer (Pillow/FreeType)",
       font=ImageFont.truetype(str(FD / "Inter[opsz,wght].ttf"), 26), fill=(60, 55, 50))
y += 56
for name, fn, axes in CANDIDATES:
    try:
        t = load(fn, 92, axes); l = load(fn, 52, axes); n = load(fn, 34, axes)
    except Exception as e:
        d.text((40, y + 20), f"{name}: FAILED {e}", font=ImageFont.truetype(str(FD / "Inter[opsz,wght].ttf"), 28), fill=(200, 40, 40)); y += 118; continue
    d.text((44, y), name, font=ImageFont.truetype(str(FD / "Inter[opsz,wght].ttf"), 24), fill=(150, 140, 130))
    d.text((44, y + 26), TITLE, font=t, fill=(30, 28, 26))
    d.text((44, y + 128), LABEL + "     " + NUMB, font=l, fill=(60, 58, 55))
    y += 128 + 84
img.save(OUT, quality=92)
print(OUT, img.size)
