#!/usr/bin/env python3
"""reel.acts - screen-content renderers. Each returns RGB uint8 (960, 1536, 3)."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from engine import font, text_rgba, rounded_rect, smoothstep, ease_out, ease_in, ease_io

SW, SH = 1536, 960
CORAL = (232, 110, 72)
CORAL2 = (255, 140, 90)
BLUE = (27, 63, 216)
AMBER = (245, 166, 35)
VERM = (232, 84, 42)
CREAM = (242, 233, 216)
WHITE = (240, 240, 238)

BRAND = "KINETIC / MOTION REEL 2026"


def _lab(d, s, x, y, size=17, color=(210, 205, 200), mono=True):
    fnt = font("mono_b" if mono else "ui_b", size)
    d.text((x, y), s, font=fnt, fill=color)


def chrome(im, chapter, tc="00:00 / 157 BPM"):
    """UI chrome: brand line, timecode, chapter tag."""
    d = ImageDraw.Draw(im)
    _lab(d, BRAND, 46, 36, 16, (190, 185, 182))
    _lab(d, tc, SW - 330, 36, 15, (170, 165, 162))
    if chapter:
        _lab(d, chapter, 46, SH - 62, 18, (215, 210, 205))
    return im


def dots_bg(warm=True, t=0.0):
    im = Image.new("RGB", (SW, SH), (22, 19, 18) if warm else (14, 14, 16))
    # warm horizon glow
    g = np.zeros((SH, SW, 3), np.float32)
    yy = np.linspace(0, 1, SH)[:, None]
    if warm:
        g[:, :, 0] = 42 * np.exp(-((yy - 0.55) ** 2) / 0.06)
        g[:, :, 1] = 26 * np.exp(-((yy - 0.55) ** 2) / 0.06)
        g[:, :, 2] = 14 * np.exp(-((yy - 0.55) ** 2) / 0.06)
    a = np.asarray(im).astype(np.float32) + g
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    for y in range(60, SH - 40, 56):
        for x in range(40, SW - 20, 56):
            d.ellipse([x, y, x + 3, y + 3], fill=(96, 90, 86))
    return im


# ============================================================ 00 THE DOT
def act_dot(t):
    """t in [0, 1.55]: elastic ruler + glowing pill pops (squash & stretch)."""
    im = dots_bg(True, t)
    d = ImageDraw.Draw(im)

    y_line = 585
    # pop events: (t0, t1)
    # pill state: gaussian envelopes for up/height
    def pill_state(t):
        # three pops
        st = {"x": 760, "y": y_line, "h": 46, "w": 86, "ant": 0}
        pops = [(0.08, 0.30, 0.62), (0.55, 0.85, 1.2), (1.12, 1.32, 1.52)]
        for (a, b, c) in pops:
            if t >= a:
                u = (t - a) / (c - a)
                if u < 1.0:
                    rise = smoothstep(u / 0.32)
                    fall = 1 - smoothstep((u - 0.62) / 0.38)
                    st["h"] = 46 + 150 * rise * fall
                    st["w"] = 86 - 16 * rise * fall
                    st["ant"] = max(0.0, math.sin(min(1, u / 0.7) * math.pi)) * 46
        return st

    st = pill_state(t)
    # elastic line: sag under the pill
    sag = (st["h"] - 34) * 0.28
    pts = []
    for x in range(180, 1360, 8):
        dd = abs(x - st["x"])
        y = y_line + sag * math.exp(-(dd ** 2) / (2 * 210 ** 2)) + 10 * math.sin((x - 180) / 560.0 + t * 3) * 0.2
        pts.append((x, y))
    d.line(pts, fill=(238, 236, 232), width=7)
    # ruler ticks
    for i in range(31):
        x = 190 + i * 38.5
        dd = abs(x - st["x"])
        y = y_line + sag * math.exp(-(dd ** 2) / (2 * 210 ** 2))
        h = 15 if i % 5 else 26
        d.line([(x, y + 8), (x, y + 8 + h)], fill=(175, 170, 165), width=2)

    # pill with echo streaks + glow
    glow = Image.new("RGB", (SW, SH), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = st["x"], y_line + sag - st["h"] * 0.5 - 26
    for k in range(7):
        ek = k / 7.0
        alpha = int(210 * (1 - ek) ** 1.6)
        yoff = cy + k * 10
        h = max(18, st["h"] * (1 - ek * 0.3))
        w = max(24, st["w"] * (1 - ek * 0.12))
        col = (alpha, int(alpha * 0.45), int(alpha * 0.12))
        gd.rounded_rectangle([cx - w / 2, yoff - h / 2, cx + w / 2, yoff + h / 2],
                             radius=int(w / 2), fill=col)
    if st["ant"] > 0:
        gd.line([(cx, cy - st["h"] / 2), (cx, cy - st["h"] / 2 - st["ant"])],
                fill=(230, 130, 70), width=6)
        gd.ellipse([cx - 8, cy - st["h"] / 2 - st["ant"] - 8, cx + 8, cy - st["h"] / 2 - st["ant"] + 8],
                   fill=(255, 210, 160))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.int32) + np.asarray(glow).astype(np.int32), 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([cx - st["w"] / 2, cy - st["h"] / 2, cx + st["w"] / 2, cy + st["h"] / 2],
                        radius=int(st["w"] / 2), fill=(255, 196, 140))
    d.rounded_rectangle([cx - st["w"] / 2 + 8, cy - st["h"] / 2 + 8,
                         cx + st["w"] / 2 - 8, cy + st["h"] / 2 - 8],
                        radius=int(st["w"] / 2), fill=(255, 240, 210))

    chrome(im, "00 / THE DOT")
    d = ImageDraw.Draw(im)
    _lab(d, "FIG. 01", 330, y_line + 78, 17)
    _lab(d, "SQUASH + STRETCH", SW - 430, y_line + 78, 17)
    return np.asarray(im)


# ============================================================ 01 TYPE
def _letter_pos(s, size):
    fnt = font("ui_b", size)
    widths = [fnt.getlength(c) + 6 for c in s]
    return fnt, widths, sum(widths)


def act_type(t):
    """t in [1.55, 4.35]: whip assembly, invert flash, lockup, flips, zoom-through."""
    t = min(max(t, 1.55), 4.35)
    dark_bg = 4.0 if t < 1.95 else None

    # phase colours
    invert = smoothstep((t - 1.97) / 0.13)
    bg = tuple(int(a + (b - a) * invert) for a, b in zip((16, 14, 13), (240, 238, 233)))
    txt = tuple(int(a + (b - a) * invert) for a, b in zip((240, 238, 233), (28, 26, 24)))

    im = Image.new("RGB", (SW, SH), bg)
    d = ImageDraw.Draw(im)

    def draw_word(s, size, cx, cy, t0, flip_phase=0.0):
        fnt, widths, total = _letter_pos(s, size)
        x = cx - total / 2
        for i, c in enumerate(s):
            li = t0 + i * 0.036
            u = ease_out(np.clip((t - li) / 0.34, 0, 1))
            if u <= 0:
                x += widths[i]
                continue
            ang = (1 - u) * (28 if i % 2 == 0 else -34)
            sc = 0.7 + 0.3 * u
            # split-flap: squash x
            fl = 1.0
            if flip_phase > 0:
                fl = abs(math.cos(t * 6.2 + i * 1.7 + flip_phase))
                fl = 0.15 + 0.85 * fl
            ch = text_rgba(c, fnt, txt)
            ch = ch.resize((max(1, int(ch.size[0] * sc * fl)), max(1, int(ch.size[1] * sc))), Image.LANCZOS)
            ch = ch.rotate(ang, expand=True, resample=Image.BICUBIC)
            im.paste(ch, (int(x + widths[i] / 2 - ch.size[0] / 2), int(cy - ch.size[1] / 2)), ch)
            x += widths[i]

    # word 1: "motion" flies 1.55-1.92
    if t < 2.42:
        draw_word("motion", 232, SW / 2, 420, 1.52)
    # word 2: "design" flies 2.45-2.80; lockup raises word1
    else:
        y1 = 420 - smoothstep((t - 2.45) / 0.3) * 105
        draw_word("motion", 232, SW / 2, y1, 1.52, flip_phase=0.6 if t > 3.2 else 0)
        draw_word("design", 232, SW / 2, y1 + 255, 2.45, flip_phase=1.2 if t > 3.2 else 0)
        # orange tittles over the i's (motion: idx 3, design: idx 2)
        for (s, size, yy, t0, idx) in (("motion", 232, y1, 1.52, 3), ("design", 232, y1 + 255, 2.45, 2)):
            fnt, widths, total = _letter_pos(s, size)
            x = SW / 2 - total / 2 + sum(widths[:idx]) + widths[idx] / 2
            if t > t0 + 0.35:
                r = 15
                d.ellipse([x - r, yy - 150 - r, x + r, yy - 150 + r], fill=CORAL)

    # invert flash sphere
    if 1.93 < t < 2.16:
        u = smoothstep((t - 1.93) / 0.20)
        r = 60 + u * 1400
        d2 = ImageDraw.Draw(im)
        d2.ellipse([SW / 2 - r, 430 - r, SW / 2 + r, 430 + r],
                   outline=(255, 250, 240), width=int(30 * (1 - u)) if u < 0.98 else 0)

    # zoom-through: scale everything up about the tittle + defocus
    if t >= 3.95:
        u = smoothstep((t - 3.95) / 0.38)
        z = 1 + u * 5.5
        im = im.resize((int(SW * z), int(SH * z)), Image.LANCZOS)
        # centre crop about (SW/2, 300)
        cx = int(SW / 2 * z)
        cy = int(300 * z)
        im = im.crop((cx - SW // 2, cy - SH // 2, cx + SW // 2, cy - SH // 2 + SH))
        im = im.filter(ImageFilter.GaussianBlur(2 + 26 * u))
        d = ImageDraw.Draw(im)
        # orange sun grows from the tittle position
        r = 30 + u * 1500
        d.ellipse([SW // 2 - r, 300 - r, SW // 2 + r, 300 + r], fill=CORAL)

    chrome(im, "01 / TYPE")
    return np.asarray(im)


# ============================================================ 02 SHAPE (bauhaus relief tiles)
_TILE_STATES = None
_TILE_T0 = 4.35


def _tile_rng(i):
    return np.random.RandomState(1234 + i)


def act_shape(t):
    """t in [4.35, 5.20]: extruded bauhaus tiles rearranging."""
    global _TILE_STATES
    cols, rows = 7, 5
    tw, th = SW / cols, SH / rows
    im = Image.new("RGB", (SW, SH), (238, 235, 228))
    d = ImageDraw.Draw(im)
    colors = [BLUE, AMBER, (18, 18, 20), CREAM, (232, 235, 238)]

    tloc = t - _TILE_T0
    seg = int(tloc / 0.28)          # rearrange step
    f = ease_io((tloc / 0.28) % 1.0)

    def shape_of(cell, step):
        r = _tile_rng(cell * 31 + step * 97)
        return int(r.randint(0, 8)), int(r.randint(0, len(colors)))

    def draw_tile(ox, oy, kind, ci, cell):
        c = colors[ci]
        x0, y0 = ox + 6, oy + 6
        x1, y1 = ox + tw - 6, oy + th - 6
        ex = 7  # extrusion
        side = tuple(int(v * 0.45) for v in c)
        face = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        if kind == 0:  # full square
            d.polygon([(x0 + ex, y0 + ex), (x1 + ex, y0 + ex), (x1 + ex, y1 + ex), (x0 + ex, y1 + ex)], fill=side)
            d.rectangle([x0, y0, x1, y1], fill=c)
        elif kind == 1:  # circle
            d.ellipse([x0 + ex, y0 + ex, x1 + ex, y1 + ex], fill=side)
            d.ellipse([x0, y0, x1, y1], fill=c)
        elif kind == 2:  # half circle (up)
            d.pieslice([x0 + ex, y0 + ex, x1 + ex, y1 + ex], 180, 360, fill=side)
            d.pieslice([x0, y0, x1, y1], 180, 360, fill=c)
        elif kind == 3:  # quarter circle
            d.pieslice([x0 + ex, y0 + ex, x1 + ex, y1 + ex], 180, 270, fill=side)
            d.pieslice([x0, y0, x1, y1], 180, 270, fill=c)
        elif kind == 4:  # diamond
            pts = [((x0 + x1) / 2, y0), (x1, (y0 + y1) / 2), ((x0 + x1) / 2, y1), (x0, (y0 + y1) / 2)]
            d.polygon([(px + ex, py + ex) for px, py in pts], fill=side)
            d.polygon(pts, fill=c)
        elif kind == 5:  # stripes
            n = 4
            for k in range(n):
                yy0 = y0 + k * (y1 - y0) / n + 5
                yy1 = y0 + (k + 1) * (y1 - y0) / n - 5
                d.rectangle([x0 + ex, yy0 + ex, x1 + ex, yy1 + ex], fill=side)
                d.rectangle([x0, yy0, x1, yy1], fill=c)
        elif kind == 6:  # triangle
            pts = [(x0, y1), (x1, y1), (x1, y0)]
            d.polygon([(px + ex, py + ex) for px, py in pts], fill=side)
            d.polygon(pts, fill=c)
        else:  # ring
            d.ellipse([x0 + ex, y0 + ex, x1 + ex, y1 + ex], fill=side)
            d.ellipse([x0, y0, x1, y1], fill=c)
            m = (x1 - x0) * 0.28
            d.ellipse([x0 + m, y0 + m, x1 - m, y1 - m], fill=(238, 235, 228))

    for r in range(rows):
        for c in range(cols):
            cell = r * cols + c
            k0, c0 = shape_of(cell, seg)
            k1, c1 = shape_of(cell, seg + 1)
            ox, oy = c * tw, r * th
            # slide-in of new tile from the right during f<0.5
            draw_tile(ox, oy, k0, c0, cell)
            if f > 0.55:
                ox2 = ox + (1 - ease_io((f - 0.55) / 0.45)) * tw
                im2 = Image.new("RGB", (int(tw), int(th)), (238, 235, 228))
                # draw incoming tile clipped
                save = im
                im = im  # keep simple: draw incoming over
                draw_tile(ox2, oy, k1, c1, cell)
    chrome(im, "02 / SHAPE")
    return np.asarray(im)


# ============================================================ 03 PATTERN (squiggle maze)
def act_pattern(t):
    """t in [5.20, 5.60]: morphing meander ribbons + drifting dot."""
    im = Image.new("RGB", (SW, SH), (214, 214, 208))
    d = ImageDraw.Draw(im)
    tloc = t - 5.20
    rows = 11
    for r in range(rows):
        y0 = (r + 0.5) * SH / rows
        amp = 26 + 12 * math.sin(r * 1.7 + tloc * 1.5)
        pts = []
        for x in range(-40, SW + 40, 14):
            y = y0 + amp * math.sin(x / 118.0 + r * 1.1 + tloc * 2.2) \
                + 9 * math.sin(x / 47.0 - r * 0.7 - tloc * 3.1)
            pts.append((x, y))
        d.line(pts, fill=(18, 18, 18), width=15, joint="curve")
        for (ex, ey) in (pts[0], pts[-1]):
            d.ellipse([ex - 8, ey - 8, ex + 8, ey + 8], fill=(18, 18, 18))
    # vertical connectors to make it maze-like
    for c in range(10):
        x0 = (c + 0.5) * SW / 10
        pts = []
        for y in range(-20, SH + 20, 14):
            x = x0 + 18 * math.sin(y / 90.0 + c * 1.3 - tloc * 1.8)
            pts.append((x, y))
        if (c + int(tloc * 2)) % 2 == 0:
            d.line(pts, fill=(18, 18, 18), width=15, joint="curve")
    dx = SW / 2 + 140 * math.sin(tloc * 2.6)
    dy = SH / 2 + 70 * math.cos(tloc * 2.1)
    d.ellipse([dx - 36, dy - 36, dx + 36, dy + 36], fill=CORAL)
    chrome(im, "03 / PATTERN")
    return np.asarray(im)


def act_smear(t):
    """t in [5.60, 6.00]: vertical slit-scan melt to black."""
    base = Image.fromarray(act_pattern(5.58))
    u = smoothstep((t - 5.60) / 0.34)
    # vertical stretch smear
    a = np.asarray(base).astype(np.float32)
    out = np.zeros_like(a)
    n = 14
    for k in range(n):
        sh = np.roll(a, int(k * 18 * u), axis=0) * (1 - k / n) ** 1.5
        out += sh
    out *= (1 - u * 0.96)
    # keep the dot alive
    d = ImageDraw.Draw(Image.fromarray(out.astype(np.uint8)))
    dx, dy = SW / 2, SH / 2
    rr = 30 * (1 - 0.3 * u)
    img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(img)
    d.ellipse([dx - rr, dy - rr, dx + rr, dy + rr], fill=CORAL)
    chrome(img, "03 / PATTERN")
    return np.asarray(img)


# ============================================================ 04 PARTICLE
def _fib_sphere(n):
    i = np.arange(n) + 0.5
    phi = np.arccos(1 - 2 * i / n)
    theta = np.pi * (1 + 5 ** 0.5) * i
    return np.stack([np.cos(theta) * np.sin(phi), np.sin(theta) * np.sin(phi), np.cos(phi)], axis=1)


def _proj(P, scale=520, camz=2.6):
    z = P[:, 2] + camz
    f = scale / np.maximum(z, 0.35)
    return P[:, 0] * f + SW / 2, P[:, 1] * f + SH / 2, f


def _dots(im, xs, ys, f, col=(200, 214, 255), alpha=1.0, k=0.014):
    d = ImageDraw.Draw(im, "RGBA")
    n = len(xs)
    for i in range(n):
        r = max(1.0, f[i] * k)
        a = int(255 * alpha * (0.35 + 0.65 * min(1.0, r / 3)))
        d.ellipse([xs[i] - r, ys[i] - r, xs[i] + r, ys[i] + r], fill=(*col, a))


def act_particle(t):
    """t in [6.0, 8.0]: burst -> sphere -> rings -> terrain -> spiral -> implode."""
    im = Image.new("RGB", (SW, SH), (6, 8, 16))
    glow = Image.new("RGB", (SW, SH), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    rng = np.random.RandomState(7)
    N = 1100
    dirs = rng.randn(N, 3)
    dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)

    if t < 6.35:
        u = ease_out(np.clip((t - 6.0) / 0.32, 0, 1))
        P = dirs * (0.12 + u * 1.15)
        xs, ys, f = _proj(P, 560, 2.5)
        _dots(im, xs, ys, f, k=0.016)
        gd.ellipse([SW / 2 - 70, SH / 2 - 70, SW / 2 + 70, SH / 2 + 70], fill=(60, 40, 20))
    elif t < 6.70:
        u = (t - 6.35) / 0.35
        P = _fib_sphere(N) * (1.02 + 0.05 * math.sin(t * 3))
        ang = u * 1.2
        R = np.array([[math.cos(ang), 0, math.sin(ang)], [0, 1, 0], [-math.sin(ang), 0, math.cos(ang)]])
        P = P @ R.T
        xs, ys, f = _proj(P, 560, 2.5)
        _dots(im, xs, ys, f, k=0.014)
        gd.ellipse([SW / 2 - 44, SH / 2 - 44, SW / 2 + 44, SH / 2 + 44], fill=(70, 45, 22))
    elif t < 7.18:
        u = (t - 6.70) / 0.48
        rings = 15
        pts = []
        for k in range(rings):
            a0 = k * math.pi / rings + u * 1.4
            n = 80
            tt = np.linspace(0, 2 * math.pi, n)
            R0 = 1.05 * math.sin(math.pi * (k + 0.5) / rings) ** 0.8
            x = R0 * np.cos(tt)
            y = R0 * np.sin(tt) * 0.36
            z = R0 * np.sin(tt) * 0.92
            M = np.stack([x, y, z], axis=1)
            c, s = math.cos(a0), math.sin(a0)
            M = M @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T
            pts.append(M)
        P = np.concatenate(pts, 0)
        xs, ys, f = _proj(P, 560, 2.5)
        _dots(im, xs, ys, f, k=0.011)
        gd.ellipse([SW / 2 - 38, SH / 2 - 38, SW / 2 + 38, SH / 2 + 38], fill=(80, 50, 24))
    elif t < 7.58:
        u = (t - 7.18) / 0.40
        gx = np.linspace(-1, 1, 40)
        gz = np.linspace(-1, 1, 24)
        X, Z = np.meshgrid(gx, gz)
        Y = 0.16 * np.sin(3.2 * X + t * 3.4) * np.cos(2.6 * Z + t * 2.2) + 0.06 * np.sin(6 * X - t * 4)
        P = np.stack([X.ravel(), Y.ravel(), Z.ravel() * 0.85], axis=1)
        ang = 0.5 + u * 0.5
        c, s = math.cos(ang), math.sin(ang)
        P = P @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T
        P[:, 1] += 0.18 * P[:, 2]
        P[:, 1] *= 1.15
        xs, ys, f = _proj(P, 620, 2.4)
        _dots(im, xs, ys, f, col=(210, 222, 255), k=0.012)
    elif t < 7.95:
        u = (t - 7.58) / 0.37
        tt = np.linspace(0.3, 6.2 * math.pi, N // 3)
        arms = []
        for a in range(3):
            r = 0.115 * np.exp(0.112 * tt)
            ph = a * 2.09
            x = r * np.cos(tt + u * 2.2 + ph)
            y = r * np.sin(tt + u * 2.2 + ph) * 0.55
            z = 0.10 * r * np.sin(tt * 0.7 + ph)
            arms.append(np.stack([x, y, z], axis=1))
        P = np.concatenate(arms, 0)
        xs, ys, f = _proj(P, 560, 2.5)
        _dots(im, xs, ys, f, k=0.013)
        gd.ellipse([SW / 2 - 50, SH / 2 - 50, SW / 2 + 50, SH / 2 + 50], fill=(50, 34, 18))
    else:
        u = ease_in(np.clip((t - 7.95) / 0.10, 0, 1))
        tt = np.linspace(0.3, 6.2 * math.pi, N)
        r = 0.115 * np.exp(0.112 * tt) * (1 - u)
        x = r * np.cos(tt)
        y = r * np.sin(tt) * 0.55
        P = np.stack([x, y, np.zeros_like(x)], axis=1)
        xs, ys, f = _proj(P, 560, 2.5)
        _dots(im, xs, ys, f, k=0.012)
        gd.ellipse([SW / 2 - 260 * (1 - u), SH / 2 - 260 * (1 - u),
                    SW / 2 + 260 * (1 - u), SH / 2 + 260 * (1 - u)], fill=(220, 220, 230))

    glow = glow.filter(ImageFilter.GaussianBlur(26))
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.int32) + np.asarray(glow).astype(np.int32), 0, 255).astype(np.uint8))
    chrome(im, "04 / PARTICLE")
    return np.asarray(im)


# ============================================================ 05 ORGANIC
def _clay(d, cx, cy, r, color, elong=1.0, ang=0.0):
    """soft-shaded 3D-ish blob (capsule when elong != 1)."""
    w = r * (1.0 if elong >= 1 else elong)
    h = r * (elong if elong >= 1 else 1.0)
    bb = [cx - w, cy - h, cx + w, cy + h]
    d.ellipse(bb, fill=color)
    hi = tuple(min(255, int(c * 1.35)) for c in color)
    d.ellipse([cx - w * 0.55, cy - h * 0.72, cx + w * 0.15, cy + h * 0.05], fill=hi)


def act_organic(t):
    """t in [8.0, 10.0]: clay blobs bloom -> merge -> mitosis -> row -> bars."""
    im = Image.new("RGB", (SW, SH), BLUE)
    g = np.zeros((SH, SW, 3), np.float32)
    yy = np.linspace(-1, 1, SH)[:, None]
    xx = np.linspace(-1, 1, SW)[None, :]
    rad = np.sqrt(xx ** 2 + yy ** 2)
    g[:, :, 2] = 30 * (1 - np.clip(rad, 0, 1))
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) + g, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)

    rng = np.random.RandomState(11)
    n = 12
    tx = (rng.rand(n) - 0.5) * 900
    ty = (rng.rand(n) - 0.5) * 560
    cols = [(247, 168, 132), (240, 128, 88), (250, 190, 150)]

    if t < 8.80:
        u = ease_out(np.clip((t - 8.0) / 0.55, 0, 1))
        for i in range(n):
            wob = 22 * math.sin(t * 1.7 + i * 1.4)
            cx = SW / 2 + tx[i] * u + wob
            cy = SH / 2 + ty[i] * u + wob * 0.6
            r = 34 + 26 * u * (0.6 + 0.4 * ((i * 7) % 5) / 4)
            _clay(d, cx, cy, r, cols[i % 3])
    elif t < 9.20:
        u = ease_io((t - 8.80) / 0.40)
        for i in range(n):
            cx = SW / 2 + tx[i] * (1 - u)
            cy = SH / 2 + ty[i] * (1 - u)
            r = (34 + 26 * (0.6 + 0.4 * ((i * 7) % 5) / 4)) * (1 - 0.35 * u)
            _clay(d, cx, cy, r, cols[i % 3])
        R = 70 + u * 60
        _clay(d, SW / 2, SH / 2, R, CORAL)
    elif t < 9.60:
        u = (t - 9.20) / 0.40
        # mitosis: 1 -> 2 -> 4 -> 5
        stages = [
            (0.00, 0.22, [(0, 0, 1.0)]),
            (0.22, 0.45, [(-160, 0, 0.85), (160, 0, 0.85)]),
            (0.45, 0.72, [(-190, -80, 0.7), (-190, 80, 0.7), (190, -80, 0.7), (190, 80, 0.7)]),
            (0.72, 1.01, [(-260, -60, 0.62), (-90, 60, 0.62), (90, -60, 0.62), (260, 60, 0.62), (0, -120, 0.62)]),
        ]
        for (a, b, cells) in stages:
            if u >= a:
                uu = ease_out(np.clip((u - a) / (b - a), 0, 1))
                for (dx, dy, sc) in cells:
                    stretch = 1 + 0.25 * math.sin(uu * math.pi)
                    _clay(d, SW / 2 + dx * uu, SH / 2 + dy * uu,
                          60 * sc * (0.8 + 0.2 * uu) * stretch, CORAL, elong=1.0)
    elif t < 10.0:
        u = (t - 9.60) / 0.40
        nn = 12
        for i in range(nn):
            x = SW / 2 + (i - (nn - 1) / 2) * 105
            grow = ease_out(np.clip((u - i * 0.035) / 0.45, 0, 1))
            el = 1.0 + grow * (2.2 if i % 3 != 1 else 1.2) * (0.8 + 0.2 * math.sin(i * 2.2))
            cy = SH / 2 + 60 - 30 * el
            _clay(d, x, cy, 34, CREAM if i % 4 else CORAL, elong=el)
    chrome(im, "05 / ORGANIC")
    return np.asarray(im)


# ============================================================ 06 DATA
def act_data(t):
    """t in [10.0, 11.2]: dashboard with rolling KPIs, sparkline, spectrum bars."""
    im = Image.new("RGB", (SW, SH), BLUE)
    g = np.zeros((SH, SW, 3), np.float32)
    yy = np.linspace(-1, 1, SH)[:, None]
    g[:, :, 2] = 22 * (1 - (yy + 1) / 2)
    g[:, :, 0] = 6 * (1 - (yy + 1) / 2)
    im = Image.fromarray(np.clip(np.asarray(im).astype(np.float32) + g, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(im)

    # KPI row
    kpis = [("FRAMES RENDERED", 622), ("BEATS PER MINUTE", 119), ("LINES OF CODE", 2323), ("SHOTS", 348)]
    for i, (lab, val) in enumerate(kpis):
        x = 70 + i * 360
        roll = int(2 * (t - 10.0) * (2 + i)) % 10
        v = val + int((t - 10.0) * (2.4 + i * 1.1))
        s = str(v).zfill(4)
        fnt = font("mono_b", 84)
        # digit blur on the last digit
        for j, ch in enumerate(s):
            col = CREAM
            if j == len(s) - 1:
                col = (200, 210, 235)
            d.text((x + j * 52, 210), ch, font=fnt, fill=col)
        _lab(d, lab, x, 320, 20, (215, 222, 245))
        d.line([(x, 352), (x + 260, 352)], fill=(140, 165, 235), width=2)

    # sparkline panel
    d.rectangle([70, 420, SW - 70, 640], fill=(36, 78, 226))
    fnt = font("mono_b", 18)
    _lab(d, "OUTPUT", 90, 432, 16, (170, 190, 240))
    pts = []
    rng = np.random.RandomState(5)
    vals = np.cumsum(rng.randn(140) * 0.6) + 40
    for i in range(140):
        x = 100 + i * (SW - 240) / 139
        y = 560 - vals[i] * 1.2 - 8 * math.sin(i * 0.4 + t * 3)
        pts.append((x, y))
    d.line(pts, fill=WHITE, width=3)
    hx, hy = pts[-1]
    d.ellipse([hx - 13, hy - 13, hx + 13, hy + 13], fill=CORAL)

    # spectrum bars
    n = 12
    for i in range(n):
        x = 110 + i * 112
        h = 60 + 120 * abs(math.sin(i * 1.3 + t * 5 + math.sin(t * 2 + i)))
        if i % 5 == 0:
            h *= 1.25
        y1 = 860
        y0 = y1 - h
        d.rounded_rectangle([x, y0, x + 64, y1], radius=32, fill=CREAM)
        d.line([(x + 8, y0 - 16), (x + 56, y0 - 16)], fill=(150, 175, 240), width=3)
    _lab(d, "SPECTRUM / LIVE", 110, 880, 18, (215, 222, 245))

    tc = f"00:{int(11 + t - 10):02d} / 157 BPM"
    chrome(im, "06 / DATA", tc)
    return np.asarray(im)


# ============================================================ 07 RECAP + END
def act_defocus(t):
    base = Image.fromarray(act_data(11.19))
    u = smoothstep((t - 11.20) / 0.32)
    im = base.filter(ImageFilter.GaussianBlur(2 + 34 * u))
    a = np.asarray(im).astype(np.float32)
    # vertical streaks
    out = a.copy()
    for k in range(1, 10):
        out += np.roll(a, k * 22 * u, axis=0) * (1 - k / 10)
    out = out / (1 + 5 * u)
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    chrome(im, "06 / DATA")
    return np.asarray(im)


def act_montage(t):
    """t in [11.55, 11.95]: 4-5 hard flashes recycling earlier worlds."""
    slot = int((t - 11.55) / 0.08)
    if slot <= 0:
        return act_type(3.7)
    if slot == 1:
        return act_shape(5.0)
    if slot == 2:
        return act_particle(7.75)
    return act_organic(8.5)


def act_end(t):
    """t in [12.0, 12.8]: end card - wordmark, caret becomes period, typed tagline."""
    im = Image.new("RGB", (SW, SH), (14, 12, 12))
    d = ImageDraw.Draw(im)
    u = ease_out(np.clip((t - 12.0) / 0.22, 0, 1))
    fnt = font("ui_b", 210)
    word = "kinetic"
    wm = text_rgba(word, fnt, (244, 240, 232))
    sc = 0.92 + 0.08 * u
    wm = wm.resize((int(wm.size[0] * sc), int(wm.size[1] * sc)), Image.LANCZOS)
    x = SW / 2 - wm.size[0] / 2
    y = SH / 2 - wm.size[1] / 2 - 60
    im.paste(wm, (int(x), int(y)), wm)

    # caret slides in from right, becomes the period
    wx = x + wm.size[0]
    wy = y + wm.size[1] * 0.62
    if t < 12.42:
        cu = ease_out(np.clip((t - 12.18) / 0.22, 0, 1))
        cx = SW - 120 + (wx + 34 - (SW - 120)) * cu
        ch_h = 150 * (1 - 0.55 * smoothstep((t - 12.30) / 0.12))
        d.rounded_rectangle([cx - 12, wy - ch_h, cx + 12, wy], radius=8, fill=CORAL)
    else:
        pu = ease_out(np.clip((t - 12.42) / 0.18, 0, 1))
        r = 14 + 8 * pu
        d.ellipse([wx + 22 - r, wy - r * 1.6, wx + 22 + r, wy], fill=CORAL)

    # tagline types in
    tag = "motion, engineered."
    fnt2 = font("ui_med", 62)
    n = int(ease_out(np.clip((t - 12.46) / 0.34, 0, 1)) * len(tag))
    tag_im = text_rgba(tag[:n], fnt2, (190, 180, 170))
    im.paste(tag_im, (int(SW / 2 - tag_im.size[0] / 2), int(y + wm.size[1] + 36)), tag_im)

    chrome(im, "")
    return np.asarray(im)
