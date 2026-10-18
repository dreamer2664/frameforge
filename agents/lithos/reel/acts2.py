"""KINETIC REEL v2 — screen content (1920x1200 @30fps, 384 frames = 12.8s).
Design bar: beat the 'cheap motion' verdict. Real easing, display type, glow,
shaded metaballs, spiral rose, serpentine ribbons. No flat clip-art.
Palette: ink/cream/coral/blue — brand continuity with r03.
"""
import math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageChops
import numpy as np

W, H = 1920, 1200
FPS = 30
DUR = 12.8
FONTS = Path('/home/user/work/frameforge/agents/lithos/px/fonts')

INK = (14, 16, 22)
CREAM = (242, 238, 230)
CORAL = (255, 107, 53)
CORAL_HI = (255, 140, 79)
BLUE = (43, 79, 216)
NAVY = (13, 27, 61)
WHITE = (247, 245, 240)
CYAN = (127, 232, 255)
GREY = (120, 128, 148)

_fcache = {}


def font(name, size):
    key = (name, size)
    if key not in _fcache:
        if name == 'disp':
            f = ImageFont.truetype(str(FONTS / 'Archivo-var.ttf'), size)
            try:
                f.set_variation_by_axes([900])
            except Exception:
                pass
        elif name == 'ui':
            f = ImageFont.truetype(str(FONTS / 'Inter-Medium.ttf'), size)
        elif name == 'uib':
            f = ImageFont.truetype(str(FONTS / 'Inter-SemiBold.ttf'), size)
        else:
            f = ImageFont.truetype(str(FONTS / 'Inter-Regular.ttf'), size)
        _fcache[key] = f
    return _fcache[key]


# ---------- easing ----------
def cl01(x):
    return max(0.0, min(1.0, x))


def mix(a, b, t):
    return a + (b - a) * t


def eo_cubic(t):
    t = cl01(t)
    return 1 - (1 - t) ** 3


def ei_cubic(t):
    t = cl01(t)
    return t ** 3


def eio_cubic(t):
    t = cl01(t)
    return 4 * t * t * t if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def eo_back(t, s=1.7):
    t = cl01(t)
    t -= 1
    return 1 + t * t * ((s + 1) * t + s)


def eo_elastic(t, p=0.42):
    t = cl01(t)
    if t == 0 or t == 1:
        return t
    return 2 ** (-10 * t) * math.sin((t - p / 4) * (2 * math.pi) / p) + 1


def seg(t, a, b):
    """normalized time within [a,b]"""
    return cl01((t - a) / (b - a)) if b > a else 0.0


# ---------- drawing helpers ----------
def glow(img, radius=26, strength=0.85, color=None):
    """screen-glow: blurred bright pass composited back"""
    bright = img.filter(ImageFilter.GaussianBlur(radius))
    if color is not None:
        bright = ImageChops.multiply(bright, Image.new('RGB', img.size, color))
    return Image.blend(img, ImageChops.add(img, bright, scale=1.0, offset=0), strength * 0.5)


def soft_shadow(draw_size, draw_fn, blur=18, alpha=110, offset=(0, 10)):
    layer = Image.new('RGBA', draw_size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    sh = layer.split()[3].filter(ImageFilter.GaussianBlur(blur))
    out = Image.new('RGBA', draw_size, (0, 0, 0, 0))
    shadow = Image.new('RGBA', draw_size, (0, 0, 0, alpha))
    shadow.putalpha(ImageChops.multiply(sh, Image.new('L', draw_size, alpha)))
    out.alpha_composite(shadow, offset)
    out.alpha_composite(layer)
    return out


def capsule(d, cx, cy, w, h, fill, outline=None, width=3):
    r = min(w, h) / 2
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=r,
                        fill=fill, outline=outline, width=width)


def chip(d, x, y, text, fg, bg=None, size=26, pad=14):
    f = font('uib', size)
    bb = d.textbbox((0, 0), text, font=f)
    tw, th = bb[2] - bb[0], bb[3] - bb[1]
    if bg:
        d.rounded_rectangle([x, y, x + tw + 2 * pad, y + th + int(pad * 1.4)], radius=8, fill=bg)
    d.text((x + pad, y + int(pad * 0.6)), text, font=f, fill=fg)
    return tw + 2 * pad


def fig_label(d, code, title, fg=GREY):
    f = font('uib', 27)
    d.text((110, 88), f'{code}  /  {title}', font=f, fill=fg)
    d.line([110, 136, 300, 136], fill=fg, width=3)


def grain(img, amt=4):
    n = np.array(img).astype(np.int16)
    noise = np.random.default_rng(7).integers(-amt, amt + 1, n.shape[:2])[:, :, None]
    n = np.clip(n + noise, 0, 255).astype(np.uint8)
    return Image.fromarray(n)


# ---------- ACT 0: THE DOT (elastic capsule on a ruler) ----------
def act_dot(t, f):
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    fig_label(d, '00', 'THE DOT')
    # ruler
    y0 = 720
    d.line([160, y0, 1760, y0], fill=(70, 76, 96), width=3)
    for i in range(33):
        x = 160 + i * 50
        h = 26 if i % 4 == 0 else 12
        d.line([x, y0, x, y0 + h], fill=(70, 76, 96), width=3)
        if i % 8 == 0:
            d.text((x - 10, y0 + 40), f'{i:02d}', font=font('ui', 24), fill=(70, 76, 96))
    # capsule journey: 3 elastic hops along the ruler
    u = seg(t, 0.15, 1.42)
    # piecewise hops with elastic landings
    stops = [240, 640, 1130, 1560]
    n_hops = 3
    hop = min(int(u * n_hops), n_hops - 1)
    hu = cl01(u * n_hops - hop)
    x = mix(stops[hop], stops[hop + 1], eo_cubic(hu))
    # arc height
    arc = math.sin(math.pi * hu) * (110 + hop * 26)
    cy = y0 - 62 - arc
    # squash-stretch: stretch at peak velocity, squash at landing
    vel = math.sin(math.pi * min(1.0, hu * 1.06))
    land = max(0.0, (hu - 0.86) / 0.14) if hu > 0.86 else 0.0
    sq = 1 - 0.38 * land * land
    st = 1 + 0.22 * vel - 0.10 * land
    w, h = 150 * sq * st, 64 * st * sq
    if t < 0.15:
        # anticipation crouch before first hop
        a = seg(t, 0, 0.15)
        w, h = 150 * (1 + 0.25 * a), 64 * (1 - 0.3 * a)
        x, cy = stops[0], y0 - 62
    # glow trail
    for k in range(7):
        gu = max(0.0, hu - k * 0.028)
        gx = mix(stops[hop], stops[hop + 1], eo_cubic(gu))
        garc = math.sin(math.pi * gu) * (110 + hop * 26)
        gcy = y0 - 62 - garc
        ga = int(46 * (1 - k / 7))
        capsule(d, gx, gcy, w * 0.92, h * 0.92, (CORAL[0], CORAL[1] // 2, CORAL[2] // 3))
    body = soft_shadow(im.size, lambda dd: capsule(dd, x, cy, w, h, CORAL_HI), blur=22, alpha=140, offset=(0, 14))
    im.alpha_composite(body.convert('RGBA')) if im.mode == 'RGBA' else None
    im.paste(body.convert('RGB'), (0, 0), body.split()[3])
    d = ImageDraw.Draw(im)
    # highlight stripe on capsule
    d.ellipse([x - w * 0.28, cy - h * 0.34, x + w * 0.18, cy - h * 0.02], fill=(255, 214, 190))
    # micro labels
    d.text((1520, 420), 'ELASTIC', font=font('ui', 30), fill=(90, 98, 120))
    d.text((1520, 458), 'SQUASH + STRETCH', font=font('uib', 30), fill=CORAL)
    return glow(im, 20, 0.5)


# ---------- ACT 1: TYPE (whip-in, invert flash, flipping letters) ----------
def _letter_img(ch, size, color):
    f = font('disp', size)
    bb = f.getbbox(ch)
    w, h = bb[2] - bb[0] + 40, bb[3] - bb[1] + 40
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(img).text((20 - bb[0], 20 - bb[1]), ch, font=f, fill=color)
    return img


def act_type(t, f):
    dark = t < 1.94 or t >= 2.02
    # invert flash around 1.95-2.02
    flash = 1.0
    if 1.94 <= t < 2.02:
        flash = 0.0
    bg = INK if dark else CREAM
    fg = WHITE if dark else (18, 18, 20)
    im = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(im)
    fig_label(d, '01', 'TYPE', GREY if dark else (120, 118, 112))
    word1, word2 = 'motion', 'design'
    S = 250
    fdisp = font('disp', S)

    def layout(word):
        xs, x = [], 0
        for ch in word:
            xs.append(x)
            x += int(fdisp.getlength(ch)) - 8
        return xs, x

    # line 1: whip-in 1.55-1.95 with per-letter stagger + smear ghosts
    base_y = 420
    xs, total_w = layout(word1)
    x0 = (W - total_w) // 2
    for i, ch in enumerate(word1):
        lt = seg(t, 1.55 + i * 0.045, 1.86 + i * 0.045)
        e = eo_back(lt, 1.2)
        dx = mix(-900, 0, e)
        alpha = 1.0
        if lt < 0.8:
            # smear ghosts (thin, translucent)
            for k in range(3):
                gx = dx - k * 42 * (1 - lt)
                let = _letter_img(ch, S, fg)
                let = let.rotate(mix(14, 0, e), expand=True, resample=Image.BICUBIC)
                a = let.split()[3].point(lambda v: int(v * 0.22 * (1 - k / 3) * (1 - lt)))
                let.putalpha(a)
                im.paste(let, (int(x0 + xs[i] + gx), int(base_y - let.size[1] / 2)), let)
        let = _letter_img(ch, S, fg)
        rot = mix(14, 0, e)
        if abs(rot) > 0.2:
            let = let.rotate(rot, expand=True, resample=Image.BICUBIC)
        im.paste(let, (int(x0 + xs[i] + dx), int(base_y - let.size[1] / 2)), let)
    # orange tittle on 'i' of 'motion' (index 3) — centered on the stem
    if t >= 1.86:
        iw = int(fdisp.getlength('i'))
        ix = x0 + xs[3] + iw // 2 - 17
        bob = 6 * math.sin((t - 1.86) * 5.2)
        d.ellipse([ix, base_y - 152 + bob, ix + 34, base_y - 118 + bob], fill=CORAL)
    # line 2 'design': letters flip in 2.1-2.9
    base_y2 = 760
    xs2, total_w2 = layout(word2)
    x02 = (W - total_w2) // 2
    for i, ch in enumerate(word2):
        lt = seg(t, 2.12 + i * 0.06, 2.52 + i * 0.06)
        e = eo_back(lt, 1.1)
        ang = mix(90, 0, e)
        sy = abs(math.cos(math.radians(ang))) * 0.96 + 0.04
        let = _letter_img(ch, S, fg)
        let = let.resize((let.size[0], max(2, int(let.size[1] * sy))), Image.BICUBIC)
        im.paste(let, (int(x02 + xs2[i]), int(base_y2 - let.size[1] / 2)), let)
    # rolling letter flips during the hold + tittle on 'design' (i=2)
    iw2 = int(fdisp.getlength('i'))
    ix2 = x02 + xs2[2] + iw2 // 2 - 17
    if t >= 2.9:
        d.ellipse([ix2, base_y2 - 152, ix2 + 34, base_y2 - 118], fill=CORAL)
    for j, cyc in enumerate((2.62, 3.12, 3.58)):
        li = (1, 4, 3)[j]
        if cyc < t < cyc + 0.34:
            pu = seg(t, cyc, cyc + 0.34)
            ang = 360 * eo_cubic(pu)
            sy = abs(math.cos(math.radians(ang))) * 0.96 + 0.04
            let = _letter_img(word2[li], S, fg)
            let = let.resize((let.size[0], max(2, int(let.size[1] * sy))), Image.BICUBIC)
            im.paste(let, (int(x02 + xs2[li]), int(base_y2 - let.size[1] / 2)), let)
    # subtle breathe on the whole block 2.5-3.9
    if 2.4 < t < 3.95:
        br = 1 + 0.012 * math.sin((t - 2.4) * 2.6)
        im2 = im.resize((int(W * br), int(H * br)), Image.BICUBIC)
        ox, oy = (im2.size[0] - W) // 2, (im2.size[1] - H) // 2
        im = im2.crop((ox, oy, ox + W, oy + H))
        d = ImageDraw.Draw(im)
    # zoom-through 3.95-4.35: scale up + darken
    if t >= 3.95:
        z = seg(t, 3.95, 4.35)
        k = 1 + 1.6 * z * z
        im = im.resize((int(W * k), int(H * k)), Image.BICUBIC)
        ox, oy = (im.size[0] - W) // 2, (im.size[1] - H) // 2
        im = im.crop((ox, oy, ox + W, oy + H))
        dim = Image.new('RGB', (W, H), CREAM)
        im = Image.blend(im, dim, z * 0.92)
        d = ImageDraw.Draw(im)
    return im


# ---------- ACT 2: BAUHAUS TILES ----------
def act_tiles(t, f):
    im = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(im)
    fig_label(d, '02', 'SOLID + SHAPE', (120, 118, 112))
    cols, rows = 6, 4
    m = 40
    gw, gh = (W - 2 * m) / cols, (H - 2 * m - 120) / rows
    rnd = random.Random(11)
    for r in range(rows):
        for c in range(cols):
            lt = seg(t, 4.35 + (r * cols + c) * 0.011, 4.52 + (r * cols + c) * 0.011)
            if lt <= 0:
                continue
            e = eo_back(lt, 1.45)
            x, y = m + c * gw, 120 + m + r * gh
            cx, cy = x + gw / 2, y + gh / 2
            s = 0.78 * e
            w, h = gw * s, gh * s
            kind = (r * 7 + c * 3 + rnd.randint(0, 2)) % 6
            col = [INK, BLUE, CORAL, CREAM][(r + c) % 4]
            col2 = [CORAL, INK, BLUE, INK][(r * 2 + c) % 4]
            if kind == 0:
                d.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=col)
            elif kind == 1:
                d.pieslice([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 0, 90, fill=col)
            elif kind == 2:
                d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=col)
                for i in range(4):
                    yy = cy - h / 2 + h * (i + 0.5) / 4
                    d.line([cx - w / 2, yy, cx + w / 2, yy], fill=col2, width=max(2, int(h / 14)))
            elif kind == 3:
                d.polygon([(cx, cy - h / 2), (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)], fill=col)
            elif kind == 4:
                d.ellipse([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], outline=col, width=max(4, int(h / 12)))
            else:
                d.rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], fill=col)
                d.pieslice([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 180, 360, fill=col2)
    # beat accents 4.9-5.2: two tiles flip
    if t > 4.85:
        for (r, c) in ((1, 2), (2, 4)):
            pu = seg(t, 4.85 + (r + c) * 0.03, 5.1 + (r + c) * 0.03)
            ang = 180 * eo_cubic(pu)
            x, y = m + c * gw, 120 + m + r * gh
            cx, cy = x + gw / 2, y + gh / 2
            sy = abs(math.cos(math.radians(ang)))
            col = CORAL if (r + c) % 2 else BLUE
            d.rectangle([cx - gw * 0.39, cy - gh * 0.39 * sy, cx + gw * 0.39, cy + gh * 0.39 * sy], fill=col)
    return im


# ---------- ACT 3: SERPENTINE RIBBONS + PILL ----------
def act_pattern(t, f):
    im = Image.new('RGB', (W, H), CREAM)
    d = ImageDraw.Draw(im)
    fig_label(d, '03', 'PATTERN', (120, 118, 112))
    u = t - 5.2
    for k in range(9):
        yb = 180 + k * 118
        pts = []
        for xi in range(0, W + 20, 20):
            yy = yb + 62 * math.sin(xi / 210.0 + u * 2.2 + k * 0.55) + 18 * math.sin(xi / 67.0 - u * 1.4)
            pts.append((xi, yy))
        d.line(pts, fill=INK, width=22, joint='curve')
    # drifting coral pill along a ribbon
    px = mix(320, 1500, eio_cubic(seg(t, 5.2, 5.6)))
    py = 180 + 3 * 118 + 62 * math.sin(px / 210.0 + u * 2.2 + 3 * 0.55)
    capsule(d, px, py, 120, 54, CORAL)
    return im


# ---------- ACT 4: SMEAR TRAILS ----------
def act_smear(t, f):
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    fig_label(d, '04', 'SMEAR')
    u = seg(t, 5.6, 6.0)
    x = mix(180, 1740, ei_cubic(u) * 0.35 + u * 0.65)
    y = 620 + 210 * math.sin(u * math.pi * 1.6)
    # slit-scan vertical ghost stack
    for k in range(16):
        yy = y - k * 16 * (0.4 + u)
        a = (1 - k / 16) ** 1.6
        r = 92 * (1 - k / 22)
        col = tuple(int(mix(CORAL[i], 28, 1 - a)) for i in range(3))
        d.ellipse([x - r * (1 + u * 0.4), yy - r, x + r * (1 + u * 0.4), yy + r], fill=col)
    # leading ball
    capsule(d, x, y, 170, 170, WHITE)
    d.ellipse([x - 34, y - 34, x + 34, y + 34], fill=CORAL)
    # speed lines
    for k in range(8):
        yy = y - 300 + k * 80
        d.line([160, yy, 160 + 260 + k * 30, yy], fill=(46, 52, 72), width=4)
    return glow(im, 16, 0.55)


# ---------- ACT 5: PARTICLES (burst, sphere, rings, terrain, spiral rose, implode) ----------
def _sphere_pts(n, seed=3):
    rnd = random.Random(seed)
    pts = []
    for i in range(n):
        y = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(max(0.0, 1 - y * y))
        th = i * 2.399963
        pts.append((math.cos(th) * r, y, math.sin(th) * r))
    return pts


def act_particle(t, f):
    im = Image.new('RGB', (W, H), (10, 14, 30))
    d = ImageDraw.Draw(im)
    fig_label(d, '05', 'PARTICLES')
    cx, cy = W / 2, 640
    rnd = random.Random(5)
    if t < 6.28:
        # burst
        u = seg(t, 6.0, 6.28)
        for i in range(64):
            a = i / 64 * 2 * math.pi + 0.7
            dist = eo_cubic(u) * (260 + (i * 37) % 320)
            r = 10 + (i % 5) * 3
            x, yy = cx + math.cos(a) * dist, cy + math.sin(a) * dist * 0.72
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=WHITE if i % 3 else CORAL)
    elif t < 6.85:
        # dense rotating sphere
        u = seg(t, 6.28, 6.85)
        rot = u * 2.2
        pts = _sphere_pts(240)
        proj = []
        for (x, y, z) in pts:
            x2 = x * math.cos(rot) - z * math.sin(rot)
            z2 = x * math.sin(rot) + z * math.cos(rot)
            s = 420 * (0.65 + 0.35 * eo_back(seg(t, 6.28, 6.5)))
            depth = (z2 + 1) / 2
            proj.append((cx + x2 * s, cy + y * s * 0.95, 3 + depth * 9, depth))
        for (x, yy, r, dp) in sorted(proj, key=lambda p: p[3]):
            col = tuple(int(mix(120, 255, dp)) for _ in range(3))
            d.ellipse([x - r, yy - r, x + r, yy + r], fill=col)
    elif t < 7.25:
        # concentric rings + glowing core
        u = seg(t, 6.85, 7.25)
        for k in range(7):
            rr = (110 + k * 74) * (0.86 + 0.14 * eo_back(u))
            a = int(255 * (1 - k / 8))
            for i in range(60):
                th = i / 60 * 2 * math.pi + t * (0.7 + k * 0.12)
                x, yy = cx + math.cos(th) * rr, cy + math.sin(th) * rr * 0.62
                r = 6 if k < 3 else 4
                d.ellipse([x - r, yy - r, x + r, yy + r], fill=(220, 228, 255))
        for rad, col in ((150, (255, 120, 60)), (92, (255, 190, 120)), (46, (255, 240, 220))):
            d.ellipse([cx - rad, cy - rad * 0.62, cx + rad, cy + rad * 0.62], fill=col)
    elif t < 7.62:
        # wave terrain
        u = seg(t, 7.25, 7.62)
        for r in range(16):
            for c in range(46):
                x = 180 + c * 35
                z = r / 15
                yy = 760 - r * 26 + 90 * math.sin(c * 0.28 + t * 3 + r * 0.5) * (0.35 + 0.65 * z)
                rr = 3 + z * 6
                dp = 100 + int(155 * z)
                d.ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=(dp, dp, 255 if r % 4 == 0 else dp + 20))
    elif t < 7.86:
        # THE SPIRAL ROSE (the act that was amateur — now a glowing rose)
        u = seg(t, 7.62, 7.86)
        sc = mix(0.5, 1.0, eo_back(u, 0.9))
        th_max = 2.15 * math.pi
        for arm in range(6):
            pts = []
            for i in range(90):
                th = i / 89 * th_max + t * 3.2 + arm * (2 * math.pi / 6)
                r = (24 + 300 * (i / 89) ** 0.88) * sc
                x, yy = cx + math.cos(th) * r, cy + math.sin(th) * r * 0.86
                pts.append((x, yy))
            for i in range(len(pts) - 1):
                wdt = max(2, int(10 * (1 - i / len(pts)) + 2))
                d.line([pts[i], pts[i + 1]], fill=(232, 238, 255), width=wdt)
        for rad, col in ((118 * sc, (255, 105, 50)), (74 * sc, (255, 168, 108)), (38 * sc, (255, 236, 218))):
            d.ellipse([cx - rad, cy - rad * 0.86, cx + rad, cy + rad * 0.86], fill=col)
    else:
        # implode
        u = seg(t, 7.86, 8.0)
        for i in range(90):
            a = i / 90 * 2 * math.pi * 3
            r = (1 - ei_cubic(u)) * (240 + (i * 17) % 160)
            x, yy = cx + math.cos(a) * r, cy + math.sin(a) * r * 0.8
            rr = 3 + 4 * (1 - u)
            d.ellipse([x - rr, yy - rr, x + rr, yy + rr], fill=(210, 220, 255))
        cr = mix(30, 8, ei_cubic(u))
        d.ellipse([cx - cr, cy - cr, cx + cr, cy + cr], fill=CORAL_HI)
    return glow(im, 18, 0.6)


# ---------- ACT 6: ORGANIC CLAY (shaded metaballs -> mitosis -> bead row) ----------
def act_organic(t, f):
    im = Image.new('RGB', (W, H), BLUE)
    d = ImageDraw.Draw(im)
    fig_label(d, '06', 'ORGANIC', (160, 180, 255))
    # metaball field via numpy
    xs = np.arange(W)
    ys = np.arange(H)
    X, Y = np.meshgrid(xs, ys)
    field = np.zeros((H, W), dtype=np.float32)

    def add_blob(bx, by, r):
        nonlocal field
        field += np.exp(-(((X - bx) ** 2 + (Y - by) ** 2) / (2 * (r * 0.62) ** 2)))

    if t < 8.62:
        u = seg(t, 8.0, 8.62)
        rnd = random.Random(9)
        for i in range(9):
            a = i / 9 * 2 * math.pi
            dist = mix(420, 300, eo_cubic(u)) * (0.7 + 0.3 * math.sin(i * 2.4))
            bx = 960 + math.cos(a + u * 1.2) * dist * 1.35
            by = 640 + math.sin(a + u * 1.2) * dist * 0.72
            add_blob(bx, by, 120 + (i * 23) % 60)
        add_blob(960, 640, 170)
    elif t < 9.12:
        u = seg(t, 8.62, 9.12)
        add_blob(960, 640, mix(250, 330, eo_cubic(u)))
        add_blob(960 + 40 * math.sin(u * 6), 640, mix(150, 330, eo_cubic(u)))
    elif t < 9.58:
        u = seg(t, 9.12, 9.58)
        gap = mix(0, 300, eo_back(u, 1.2))
        add_blob(960 - gap, 640, 190)
        add_blob(960 + gap, 640, 190)
        add_blob(960 - gap * 0.5, 640 - 30, 60)
        add_blob(960 + gap * 0.5, 640 + 30, 60)
    else:
        # morph to bead row
        u = seg(t, 9.58, 10.0)
        for i in range(11):
            bx = mix(260 + i * 140, 210 + i * 152, u)
            by = mix(640, 660 + 36 * math.sin(i * 0.9 + u * 6), u)
            r = mix(88, 44, u)
            add_blob(bx, by, r)
    # shade the field: clay look with real form
    thr = 0.55
    gy, gx = np.gradient(field)
    nz = 0.045
    norm = np.sqrt(gx ** 2 + gy ** 2 + nz ** 2)
    lx, ly, lz = -0.5, -0.68, 0.54
    lam = (-gx * lx - gy * ly + nz * lz) / norm
    shade = np.clip(0.22 + 0.95 * lam, 0, 1)
    dark = np.array((156, 52, 18), dtype=np.float32)
    bright = np.array((255, 152, 92), dtype=np.float32)
    rgb = dark[None, None, :] * (1 - shade[:, :, None]) + bright[None, None, :] * shade[:, :, None]
    spec = np.clip(lam, 0, 1) ** 14 * 150
    rgb += spec[:, :, None]
    a = np.clip((field - thr) * 7, 0, 1)
    # drop shadow of the blob onto the blue
    sh = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(26))
    sh = np.array(sh).astype(np.float32) / 255.0
    out = np.array(im, dtype=np.float32)
    out *= (1 - np.roll(np.roll(sh, 26, axis=0), 18, axis=1)[:, :, None] * 0.38)
    out = out * (1 - a[:, :, None]) + np.clip(rgb, 0, 255) * a[:, :, None]
    im = Image.fromarray(out.astype(np.uint8))
    d = ImageDraw.Draw(im)
    if t > 9.9:
        d.text((1500, 1020), 'MORPH', font=font('uib', 30), fill=(170, 190, 255))
    return im


# ---------- ACT 7: DATA DASHBOARD ----------
def act_data(t, f):
    im = Image.new('RGB', (W, H), NAVY)
    d = ImageDraw.Draw(im)
    fig_label(d, '07', 'DATA + UI', (120, 150, 230))
    u = seg(t, 10.0, 11.2)
    # KPI row
    labels = ['SESSIONS', 'RENDERS', 'FRAME', 'GRADE']
    rnd = random.Random(21)
    for i, lb in enumerate(labels):
        x = 150 + i * 430
        n = 8200 + int(u * 120 + rnd.randint(0, 40) + i * 137 + 200 * math.sin(u * 9 + i))
        d.text((x, 210), lb, font=font('ui', 28), fill=(110, 140, 220))
        d.text((x, 252), f'{n:04d}', font=font('uib', 92), fill=WHITE)
    # sparkline
    pts = []
    for i in range(90):
        xx = 150 + i * 18.2
        yy = 560 - 60 * math.sin(i * 0.21 + u * 5) - 34 * math.sin(i * 0.53 + u * 2.2) - i * 0.28 * u * 10 / 4
        pts.append((xx, yy))
    d.line(pts, fill=(200, 218, 255), width=5, joint='curve')
    d.ellipse([pts[-1][0] - 12, pts[-1][1] - 12, pts[-1][0] + 12, pts[-1][1] + 12], fill=CORAL)
    # bars
    n_bars = 16
    for i in range(n_bars):
        hgt = (170 + 150 * abs(math.sin(i * 0.8 + u * 3.4))) * eo_cubic(seg(t, 10.06 + i * 0.018, 10.5 + i * 0.018))
        x = 150 + i * 105
        capsule(d, x, 1010 - hgt / 2, 56, hgt, WHITE)
    d.line([150, 1020, 1810, 1020], fill=(60, 90, 180), width=3)
    return im


# ---------- ACT 8: DEFOCUS ----------
def act_defocus(t, f):
    base = act_data(11.12, f)
    u = seg(t, 11.2, 11.55)
    k = 2 + 26 * ei_cubic(u)
    im = base.filter(ImageFilter.GaussianBlur(k))
    im = Image.blend(im, Image.new('RGB', (W, H), (200, 230, 255)), u * 0.35)
    if u > 0.2:
        arr = np.array(im).astype(np.float32)
        for s in range(1, 9):
            arr += np.roll(arr, s * 10, axis=1) * (0.10 * u)
        arr = np.clip(arr / (1 + 6.5 * u), 0, 255)
        im = Image.fromarray(arr.astype(np.uint8))
    return im


# ---------- ACT 9: MONTAGE RECAP ----------
_montage_calls = [
    (act_dot, 0.72), (act_type, 2.72), (act_tiles, 4.72), (act_pattern, 5.38),
    (act_particle, 6.62), (act_particle, 7.12), (act_organic, 8.72), (act_data, 10.42),
]


def act_montage(t, f):
    u = seg(t, 11.55, 11.95)
    idx = min(int(u * len(_montage_calls)), len(_montage_calls) - 1)
    fn, tt = _montage_calls[idx]
    im = fn(tt, f)
    # flash
    fl = 1 - (u * len(_montage_calls) - idx) / 1
    if fl > 0.72:
        im = Image.blend(im, Image.new('RGB', (W, H), WHITE), (fl - 0.72) / 0.28)
    if u > 0.86:
        im = Image.blend(im, Image.new('RGB', (W, H), CYAN), (u - 0.86) / 0.14)
    return im


# ---------- ACT 10: END CARD ----------
def act_end(t, f):
    im = Image.new('RGB', (W, H), INK)
    d = ImageDraw.Draw(im)
    word = 'kinetic'
    u = seg(t, 12.02, 12.42)
    n = min(len(word), int(u * len(word) * 1.15))
    typed = word[:n]
    f1 = font('disp', 210)
    bb = d.textbbox((0, 0), word, font=f1)
    x0 = (W - (bb[2] - bb[0])) // 2
    y0 = 500
    d.text((x0, y0), typed, font=f1, fill=WHITE)
    tw = d.textbbox((0, 0), typed, font=f1)[2]
    # caret -> period morph 12.42-12.6
    if t < 12.42:
        d.rectangle([x0 + tw + 18, y0 + 28, x0 + tw + 38, y0 + 168], fill=CORAL)
    else:
        m = seg(t, 12.42, 12.6)
        ch = mix(140, 26, eo_cubic(m))
        cw = mix(20, 26, eo_cubic(m))
        d.ellipse([x0 + tw + 12, y0 + 168 - ch, x0 + tw + 12 + cw, y0 + 168], fill=CORAL)
    # tagline types
    tag = 'motion, engineered.'
    u2 = seg(t, 12.38, 12.74)
    n2 = min(len(tag), int(u2 * len(tag) * 1.2))
    d.text((x0 + 6, y0 + 260), tag[:n2], font=font('ui', 54), fill=(168, 174, 192))
    if u2 > 0.1:
        d.line([x0 + 6, y0 + 356, x0 + 6 + int(560 * eo_cubic(u2)), y0 + 356], fill=(52, 58, 78), width=3)
    return glow(im, 14, 0.4)


# ---------- router ----------
def screen_frame(t):
    t = t % (DUR + 1)
    if t < 1.55:
        return act_dot(t, 0)
    if t < 4.35:
        return act_type(t, 1)
    if t < 5.2:
        return act_tiles(t, 2)
    if t < 5.6:
        return act_pattern(t, 3)
    if t < 6.0:
        return act_smear(t, 4)
    if t < 8.0:
        return act_particle(t, 5)
    if t < 10.0:
        return act_organic(t, 6)
    if t < 11.2:
        return act_data(t, 7)
    if t < 11.55:
        return act_defocus(t, 8)
    if t < 11.95:
        return act_montage(t, 9)
    return act_end(t, 10)


if __name__ == '__main__':
    import sys
    out = Path(sys.argv[1] if len(sys.argv) > 1 else '/tmp/act-test')
    out.mkdir(parents=True, exist_ok=True)
    for fr in range(0, 384, 8):
        t = fr / FPS
        screen_frame(t).save(out / f'{fr:04d}.png')
    print('ACTS_OK', len(list(out.glob("*.png"))))
