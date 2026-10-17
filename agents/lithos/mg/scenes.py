#!/usr/bin/env python3
"""mg.scenes - the film. Pure functions of time against storyboard.json.

Palette twist (mine): the reference lives in gold and flips to blue; this film
lives in a cool 'midnight aurora' (teal/violet ribbons, amber accent) and the
response flips it MOLTEN (gold/coral). All copy is original.
"""
import json
import math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import (W, H, Canvas, font, text_rgba, chars_rgba, rounded_rect,
                    glow_under, smear, place, smoothstep, ease_out, ease_in,
                    ease_io)

ROOT = Path(__file__).resolve().parent
SB = json.loads((ROOT / "storyboard.json").read_text())
COPY = SB["copy"]
FPS = SB["format"]["fps"]

RIBBON_SEED = np.random.default_rng(7)


def palette(t):
    """Palette dict with the flip lerp applied."""
    p1, p2 = SB["palettes"]["aurora"], SB["palettes"]["molten"]
    f0, f1 = SB["flip"]["t_start"], SB["flip"]["t_end"]
    u = 0.0 if t < f0 else (1.0 if t > f1 else ease_io((t - f0) / (f1 - f0)))
    out = {}
    for k in p1:
        a, b = np.array(p1[k], float), np.array(p2[k], float)
        out[k] = a + (b - a) * u
    out["flip_u"] = u
    return out


def ribbons(t, pal, zoom=1.0, drift=(0.0, 0.0)):
    """Flowing light-silk folds on mostly-black: 3 big diagonal ribbons with
    a narrow bright core and a wide soft halo (the reference's silhouette
    discipline: black is the canvas, light is the subject)."""
    h, w = H // 4, W // 4
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    xx = xx / w
    yy = yy / h
    field = np.zeros((h, w, 3), dtype=np.float32)
    cols = pal["ribbons"]
    specs = [
        # (anchor_x, slope, amp, freq, phase, speed, halfwidth, color, gain)
        (0.30, -0.16, 0.055, 1.4, 0.0, 0.10, 0.045, 0, 0.85),
        (0.52, -0.20, 0.065, 1.1, 2.1, 0.08, 0.038, 1, 0.75),
        (0.74, -0.14, 0.050, 1.6, 4.0, 0.11, 0.042, 2, 0.70),
    ]
    for ax, slope, amp, freq, ph, sp, hw, ci, gain in specs:
        cx = ax + slope * (yy - 0.5) + amp * np.sin(yy * freq * 2 * math.pi + t * sp * 2 * math.pi / 5 + ph)
        u = (xx - cx) / hw
        core = np.exp(-u * u)
        halo = np.exp(-(u * 0.32) ** 2) * 0.38
        m = (core * 0.9 + halo) * gain
        col = np.array(cols[ci % len(cols)], dtype=np.float32) / 255.0
        field += m[:, :, None] * col[None, None, :]
    # one deep background ribbon (structure without glare)
    ax, slope, amp, freq, ph, sp, hw, ci, gain = (0.12, -0.10, 0.04, 1.2, 5.2, 0.06, 0.10, 3, 1.15)
    cx = ax + slope * (yy - 0.5) + amp * np.sin(yy * freq * 2 * math.pi + t * sp * 2 * math.pi / 5 + ph)
    u = (xx - cx) / hw
    col = np.array(cols[ci % len(cols)], dtype=np.float32) / 255.0
    field += (np.exp(-u * u) * gain)[:, :, None] * col[None, None, :]
    edge = np.clip(1.3 - 1.5 * np.abs(xx - 0.5) * 2, 0, 1)[:, :, None]
    field *= edge
    im = Image.fromarray((np.clip(field, 0, 1) * 255).astype(np.uint8))
    im = im.filter(ImageFilter.GaussianBlur(7)).resize((W, H), Image.LANCZOS)
    out = np.asarray(im, dtype=np.float32) / 255.0
    bg = np.array(pal["bg_base"], dtype=np.float32) / 255.0
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None, None]
    canvas = np.zeros((H, W, 3), dtype=np.float32)
    canvas[:] = bg * (0.75 + 0.25 * (1 - g))
    return canvas + out * 0.5


# ---------------------------------------------------------------- the K mark
def kmark(size=340, pal=None):
    """KINETIC mark: rounded tile, double chevron, spark dot (original)."""
    pal = pal or SB["palettes"]["aurora"]
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = int(size * 0.22)
    tile = rounded_rect((size, size), r, fill=tuple((np.array(pal["panel"]) * 1.25).astype(int)),
                        stroke=tuple(np.array(pal["panel_line"]).astype(int)), stroke_w=3)
    im.alpha_composite(tile)
    col = tuple(int(c) for c in pal["type"])
    acc = tuple(int(c) for c in pal["accent"])
    s = size / 10
    for k, x0 in enumerate((3.0, 5.2)):
        pts = [(x0 * s, 2.6 * s), ((x0 + 1.6) * s, 5 * s), (x0 * s, 7.4 * s),
               ((x0 + 0.75) * s, 7.4 * s), ((x0 + 2.35) * s, 5 * s), ((x0 + 0.75) * s, 2.6 * s)]
        d.polygon(pts, fill=(col if k == 0 else acc) + (255,))
    rr = size * 0.045
    d.ellipse([size - 2.6 * s - rr, 5 * s - rr, size - 2.6 * s + rr, 5 * s + rr], fill=acc + (255,))
    return im


# ------------------------------------------------------------ typed accents
def typed_line(s, t, t0, fnt, pal, cps=13.0, fade_s=0.22):
    """Typewriter text: newest glyphs in the accent, cooling to type color."""
    n = len(s)
    shown = int(np.clip((t - t0) * cps, 0, n))
    if shown <= 0:
        return None, 0
    base = text_rgba(s[:shown], fnt, tuple(int(c) for c in pal["type"]))
    # repaint the tail glyphs in accent
    acc = np.array(pal["accent_hot"], float)
    typ = np.array(pal["type"], float)
    arr = np.asarray(base).astype(np.float32)
    if shown > 0:
        # find glyph x-extents roughly via per-char draw and paste at offset
        pass
    # simpler: draw char by char onto a canvas
    pad = 12
    widths = [fnt.getbbox(c)[2] - fnt.getbbox(c)[0] + 2 for c in s]
    total_w = int(sum(widths)) + pad * 2
    bb = fnt.getbbox("Hg")
    total_h = bb[3] - bb[1] + pad * 2
    out = Image.new("RGBA", (total_w, total_h), (0, 0, 0, 0))
    dr = ImageDraw.Draw(out)
    x = pad
    for i, c in enumerate(s):
        if i >= shown:
            break
        age = (t - (t0 + i / cps)) / fade_s
        col = acc + (acc - acc) * 0 if age < 1 else typ
        col = acc + (typ - acc) * ease_io(age)
        dr.text((x, pad), c, font=fnt, fill=tuple(int(v) for v in col) + (255,))
        x += widths[i]
    return out, total_w


# ------------------------------------------------------------------- chips
def chip(label, icon, fnt_size=34, ignited=0.0, pal=None, hot=False):
    pal = pal or SB["palettes"]["aurora"]
    fnt = font("ui", fnt_size)
    lab = text_rgba(label, fnt, tuple(int(c) for c in pal["type"]))
    icon_s = fnt_size + 10
    padx, pady = fnt_size, int(fnt_size * 0.62)
    w = padx * 2 + icon_s + 14 + lab.size[0]
    h = fnt_size + pady * 2
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    line = np.array(pal["panel_line"], float)
    if ignited > 0:
        acc = np.array(pal["accent"], float)
        line = line + (np.array([acc[0], acc[1], acc[2], 220]) - line) * ignited
    fill = np.array(pal["panel"], float) * (1 + 0.5 * ignited)
    body = rounded_rect((w, h), h // 2, fill=tuple(fill.astype(int)),
                        stroke=tuple(line.astype(int)), stroke_w=3)
    im.alpha_composite(body)
    # icon: rounded square with a simple glyph
    ic = Image.new("RGBA", (icon_s, icon_s), (0, 0, 0, 0))
    di = ImageDraw.Draw(ic)
    r = icon_s // 4
    di.rounded_rectangle([0, 0, icon_s - 1, icon_s - 1], r,
                         fill=tuple((np.array(pal["type"], float) * 0.12).astype(int)))
    col = tuple(int(c) for c in (pal["accent"] if ignited > 0.4 else pal["type"]))
    cx = icon_s / 2
    if icon == "shape":
        di.polygon([(cx, 8), (icon_s - 8, icon_s - 10), (8, icon_s - 10)], outline=col, width=3)
    elif icon == "score":
        for k, hh in enumerate((0.35, 0.7, 0.5, 0.85)):
            x = 10 + k * ((icon_s - 20) / 3)
            di.line([(x, icon_s * (0.5 - hh / 2 + 0.25)), (x, icon_s * (0.5 + hh / 2 + 0.25))], fill=col, width=3)
    elif icon == "light":
        di.ellipse([cx - 6, cx - 6, cx + 6, cx + 6], outline=col, width=3)
        for k in range(8):
            a = k * math.pi / 4
            di.line([(cx + 11 * math.cos(a), cx + 11 * math.sin(a)),
                     (cx + 16 * math.cos(a), cx + 16 * math.sin(a))], fill=col, width=3)
    elif icon == "cut":
        di.line([(10, 10), (icon_s - 10, icon_s - 10)], fill=col, width=3)
        di.line([(icon_s - 10, 10), (10, icon_s - 10)], fill=col, width=3)
    elif icon == "loop":
        di.arc([8, 8, icon_s - 8, icon_s - 8], 300, 240, fill=col, width=3)
        di.polygon([(icon_s - 12, 6), (icon_s - 4, 14), (icon_s - 16, 18)], fill=col)
    im.alpha_composite(ic, dest=(padx, (h - icon_s) // 2))
    im.alpha_composite(lab, dest=(padx + icon_s + 14, (h - lab.size[1]) // 2))
    return im


def cursor_rgba(size=72):
    im = Image.new("RGBA", (size, int(size * 1.35)), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(4, 2), (4, size * 1.05), (size * 0.28, size * 0.8), (size * 0.46, size * 1.22),
           (size * 0.62, size * 1.14), (size * 0.45, size * 0.72), (size * 0.78, size * 0.72)]
    d.polygon(pts, fill=(244, 246, 251, 255), outline=(12, 14, 20, 255))
    return im


# ----------------------------------------------------------------- console
def console_panel(pal, w=1360, h=620, caret=True, t=0.0):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    line = tuple(int(c) for c in pal["panel_line"])
    fill = tuple(int(c) for c in pal["panel"])
    body = rounded_rect((w, h), 36, fill=fill, stroke=line, stroke_w=2)
    im.alpha_composite(body)
    return im


def composer(pal, width=1360, h=120, send_glow=0.0):
    im = Image.new("RGBA", (width, h), (0, 0, 0, 0))
    line = tuple(int(c) for c in pal["panel_line"])
    fill = tuple(int(c) for c in pal["panel"])
    im.alpha_composite(rounded_rect((width, h), h // 2, fill=fill, stroke=line, stroke_w=2))
    # model chip
    fnt = font("ui_med", 30)
    chip_im = text_rgba(COPY["model_chip"], fnt, tuple(int(c) for c in pal["type"]))
    cbox = rounded_rect((chip_im.size[0] + 44, 56), 28,
                        fill=tuple((np.array(pal["panel"], float) * 1.8).astype(int)), stroke=line, stroke_w=2)
    im.alpha_composite(cbox, dest=(width - 420, (h - 56) // 2))
    im.alpha_composite(chip_im, dest=(width - 420 + 22, (h - chip_im.size[1]) // 2))
    # send button
    acc = np.array(pal["accent"], float)
    btn = rounded_rect((64, 64), 18, fill=tuple((acc * (0.55 + 0.45 * send_glow)).astype(int)))
    im.alpha_composite(btn, dest=(width - 96, (h - 64) // 2))
    d = ImageDraw.Draw(im)
    cx, cy = width - 96 + 32, h // 2
    d.polygon([(cx, cy - 14), (cx + 13, cy + 2), (cx + 5, cy + 2), (cx + 5, cy + 15),
               (cx - 5, cy + 15), (cx - 5, cy + 2), (cx - 13, cy + 2)], fill=(12, 14, 20, 255))
    return im


# -------------------------------------------------------------------- card
def card_page(pal, molten_u=0.0):
    """The generated site page (flat). molten_u blends toward the flip look."""
    w, h = 1560, 980
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    # gradient background
    top = np.array(pal["ribbons"][0], float) * (0.45 - 0.12 * molten_u) + \
        np.array(pal["ribbons"][3], float) * (0.25 + 0.1 * molten_u)
    bot = np.array(pal["bg_base"], float) * 1.25
    for y in range(h):
        u = y / h
        col = (top * (1 - u) + bot * u).astype(int)
        d.line([(0, y), (w, y)], fill=tuple(col) + (255,))
    # glow sweep
    glow = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    dg = ImageDraw.Draw(glow)
    dg.ellipse([w * 0.35, -h * 0.45, w * 1.25, h * 0.65],
               fill=tuple((np.array(pal["ribbons"][1], float) * 0.55).astype(int)) + (110,))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    im.alpha_composite(glow)
    # nav
    fnt = font("ui_med", 34)
    x = 84
    navc = tuple(int(c) for c in pal["type"])
    mark = kmark(64, pal)
    im.alpha_composite(mark, dest=(70, 52))
    x = 160
    for item in COPY["card_nav"]:
        t = text_rgba(item, fnt, navc)
        im.alpha_composite(t, dest=(x, 62))
        x += t.size[0] + 54
    # headline
    hf = font("serif", 132)
    y = 300
    for line in COPY["card_headline"]:
        t = text_rgba(line, hf, (250, 250, 252))
        im.alpha_composite(t, dest=(84, y))
        y += 150
    # button
    bf = font("ui", 40)
    lab = text_rgba(COPY["card_button"], bf, (14, 16, 22))
    bw, bh = lab.size[0] + 72, 88
    im.alpha_composite(rounded_rect((bw, bh), 44, fill=(250, 250, 252)), dest=(84, y + 30))
    im.alpha_composite(lab, dest=(84 + 36, y + 30 + (bh - lab.size[1]) // 2))
    return im


# -------------------------------------------------------------------- rain
_RAIN = {}
def rain_glyph(i, pal):
    """One 'motion curve' glyph: a bezier with keyframe diamonds + label."""
    key = (i, tuple(int(v) for v in pal["accent"]))
    if key in _RAIN:
        return _RAIN[key]
    rng = np.random.default_rng(100 + i)
    w, h = 300, 120
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    acc = tuple(int(c) for c in pal["accent"])
    typ = tuple(int(c) for c in pal["type"])
    pts = []
    for k in range(33):
        u = k / 32
        x = 10 + u * (w - 20)
        y = h * 0.65 - (h * 0.42) * (1 - (1 - u) ** 2) + rng.normal(0, 2)
        pts.append((x, y))
    d.line(pts, fill=acc + (230,), width=3)
    for u in (0.0, 1.0):
        x = 10 + u * (w - 20)
        y = h * 0.65 - (h * 0.42) * (1 - (1 - u) ** 2)
        s = 7
        d.polygon([(x, y - s), (x + s, y), (x, y + s), (x - s, y)], fill=typ + (255,))
    label = rng.choice(["ease-out 0.4s", "x: 120  y: -80", "scale 1.02", "rot -2.0",
                        "blur 12", "0.25s", "stagger 43ms", "speed 20px/f",
                        "hold 0.6s", "pop 1.04", "slide -240", "fade 8f",
                        "overshoot 1.1", "anticipate 0.12", "squash 0.94", "trail 9",
                        "yaw 7.5deg", "pitch 2deg", "bounce out", "cubic-io"])
    fnt = font("mono", 22)
    d.text((12, h - 34), str(label), font=fnt, fill=typ + (170,))
    _RAIN[key] = im
    return im


def rain_layer(t, pal, depth, cam_y=0.0):
    """One parallax depth of rain. depth 0 near, 2 far."""
    speed = (520, 320, 180)[depth]
    gain = (1.0, 0.62, 0.38)[depth]
    scale = (1.0, 0.8, 0.62)[depth]
    rng = np.random.default_rng(50 + depth)
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ncols = (5, 6, 7)[depth]
    for c in range(ncols):
        x0 = 80 + c * (W - 160) / (ncols - 1) - 150
        for k in range(4):
            g = rain_glyph((depth * 20 + c * 4 + k) % 12, pal)
            y = (k * 360 + rng.uniform(0, 200) - (t * speed + cam_y * (depth + 1) * 0.3)) % (H + 300) - 150
            if depth == 2:
                g = g.filter(ImageFilter.GaussianBlur(3))
            gi = g if scale == 1.0 else g.resize((int(g.size[0] * scale), int(g.size[1] * scale)), Image.LANCZOS)
            layer.alpha_composite(gi, dest=(int(x0), int(y)))
    a = np.asarray(layer).copy()
    a[:, :, 3] = (a[:, :, 3] * gain).astype(np.uint8)
    return Image.fromarray(a)
