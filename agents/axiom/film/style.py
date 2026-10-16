#!/usr/bin/env python3
"""axiom film engine — style core: palette, fonts, ink primitives, camera, easing.

Time comes from a frame/cue timeline (see timeline.py); nothing here is screen-recorded.
All drawing is deterministic: same t -> same pixels (seeded noise only for grain).
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ASSETS = Path(__file__).resolve().parents[1] / "assets"
FONTS = ASSETS / "fonts"

# ---------------------------------------------------------------- palette ----
PAPER = (246, 241, 228)
PAPER_WARM = (243, 233, 214)
PAPER_COOL = (238, 240, 238)
INK = (35, 38, 43)
INK_SOFT = (90, 94, 102)
SLATE = (46, 74, 107)
SLATE_L = (127, 168, 201)
TERRA = (196, 98, 63)
OCHRE = (216, 155, 60)
MOSS = (110, 139, 75)
PLUM = (122, 78, 126)
ROSE = (201, 123, 133)
DEEP = (28, 33, 48)
NIGHT = (18, 22, 38)
NIGHT2 = (32, 40, 66)
MOON = (233, 226, 198)
STONE = (176, 168, 152)
STONE_D = (140, 132, 118)
SAND = (214, 197, 165)
SAND_D = (186, 166, 132)
WHITE = (252, 250, 245)

SKIN = (251, 246, 236)
SKIN2 = (240, 226, 205)   # slightly warmer for a second character
HAIR = {
    "ink": (48, 46, 52), "brown": (108, 74, 48), "auburn": (150, 78, 44),
    "gold": (206, 158, 62), "grey": (196, 194, 190), "white": (240, 238, 232),
    "green": (92, 130, 84), "plum": (110, 70, 120), "blue": (58, 88, 130),
    "rust": (168, 92, 60), "sand": (206, 180, 132),
}

# ------------------------------------------------------------------ fonts ----
_FONT_CACHE: dict[tuple, ImageFont.FreeTypeFont] = {}


_MISSING_CACHE: dict[tuple, set] = {}


def missing_glyphs(role: str, text: str) -> set:
    """Which characters this face cannot draw. Detected by comparing the rendered glyph with
    the private-use glyph (guaranteed absent), so tofu boxes can be substituted automatically."""
    key = (role, "")
    if key not in _MISSING_CACHE:
        f = font(role, 48)
        probe = Image.new("L", (90, 90), 0)
        ImageDraw.Draw(probe).text((12, 12), "\ue000", font=f, fill=255)
        _MISSING_CACHE[key] = {"_ref": probe.tobytes(), "missing": set()}
    cache = _MISSING_CACHE[key]
    out = set()
    for ch in set(text):
        if ch in cache["missing"]:
            out.add(ch)
            continue
        if ch.isspace():
            continue
        f = font(role, 48)
        im = Image.new("L", (90, 90), 0)
        ImageDraw.Draw(im).text((12, 12), ch, font=f, fill=255)
        if im.tobytes() == cache["_ref"]:
            cache["missing"].add(ch)
            out.add(ch)
    return out


def text_runs(text: str, role: str, size: int):
    """Split text into (substring, font) runs so symbols the display face lacks (arrows,
    ∇ ² α µ) are drawn from the math face instead of appearing as empty boxes."""
    bad = missing_glyphs(role, text)
    if not bad:
        return [(text, font(role, size))]
    runs, cur, cur_bad = [], "", None
    for ch in text:
        b = ch in bad
        if cur and b != cur_bad:
            runs.append((cur, font("math", size) if cur_bad else font(role, size)))
            cur = ch
        else:
            cur += ch
        cur_bad = b
    if cur:
        runs.append((cur, font("math", size) if cur_bad else font(role, size)))
    return runs


def draw_text_runs(draw, xy, text, role, size, fill, anchor="la", align="left",
                   stroke_width=0, stroke_fill=None):
    """Draw mixed-font text as one visually continuous line at screen pixels."""
    runs = text_runs(text, role, size)
    if len(runs) == 1:
        draw.text(xy, text, font=runs[0][1], fill=fill, anchor=anchor, align=align,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
        return
    total = sum(f.getlength(t) for t, f in runs)
    x, y = xy
    if anchor[0] == "m":
        x -= total / 2
    elif anchor[0] == "r":
        x -= total
    for t, f in runs:
        draw.text((x, y), t, font=f, fill=fill, anchor="l" + anchor[1], align=align,
                  stroke_width=stroke_width, stroke_fill=stroke_fill)
        x += f.getlength(t)


def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    """role in {display, display_light, label, hand, note, sans, sans_bold, caps}"""
    spec = {
        "display": ("PlaypenSans[wght].ttf", {"Weight": 700}),
        "display_light": ("PlaypenSans[wght].ttf", {"Weight": 450}),
        "display_x": ("PlaypenSans[wght].ttf", {"Weight": 800}),
        "label": ("PatrickHand-Regular.ttf", None),
        "caps": ("PatrickHandSC-Regular.ttf", None),
        "hand": ("Caveat[wght].ttf", {"Weight": 600}),
        "sans": ("PublicSans[wght].ttf", {"Weight": 500}),
        "sans_bold": ("PublicSans[wght].ttf", {"Weight": 700}),
        "sans_light": ("PublicSans[wght].ttf", {"Weight": 350}),
        "inter": ("Inter[opsz,wght].ttf", {"Optical size": 32, "Weight": 500}),
        # symbols the display faces lack (∇ ² − ≈ ×): DejaVu Sans, Debian system font,
        # used ONLY for mathematical notation so formulas never turn into tofu boxes.
        "math": ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", None),
    }[role]
    fn, axes = spec
    if not str(fn).startswith("/") and not (FONTS / fn).exists():
        fn = Path(fn)
    key = (str(fn), size, tuple(sorted((axes or {}).items())))
    if key not in _FONT_CACHE:
        f = ImageFont.truetype(str(FONTS / fn), size)
        if axes:
            names = [a["name"] for a in f.get_variation_axes()]
            f.set_variation_by_axes([axes.get(n, 400) for n in names])
        _FONT_CACHE[key] = f
    return _FONT_CACHE[key]


# ----------------------------------------------------------------- easing ----
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = clamp(x)
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = clamp(x)
    return x ** 3


def ease_io(x):
    x = clamp(x)
    return 0.5 * (1 - math.cos(math.pi * x))


def pulse(t, period=1.0, sharp=2.0):
    """0..1 periodic bump, useful for ticks."""
    p = (t % period) / period
    return (1 - abs(2 * p - 1)) ** sharp


def seg(t, t0, t1):
    """normalised progress of t inside [t0,t1], clamped."""
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return clamp((t - t0) / (t1 - t0))


# ----------------------------------------------------------------- camera ----
@dataclass
class Camera:
    """World is authored in 1920x1080 design units; camera maps world->pixels.

    `pix` is pixels per world unit (1.0 = final 1920x1080; 0.5 = 960x540 draft).
    """
    cx: float = 960.0
    cy: float = 540.0
    zoom: float = 1.0
    pix: float = 1.0

    def screen(self, x, y):
        p = self.pix
        return (((x - self.cx) * self.zoom + 960.0) * p, ((y - self.cy) * self.zoom + 540.0) * p)

    def lerp_to(self, other: "Camera", u: float) -> "Camera":
        u = clamp(u)
        return Camera(
            self.cx + (other.cx - self.cx) * u,
            self.cy + (other.cy - self.cy) * u,
            self.zoom + (other.zoom - self.zoom) * u,
            other.pix,
        )


def cam_path(t, keys):
    """keys: [(time, Camera), ...] -> interpolated camera with smoothstep segments."""
    if not keys:
        return Camera()
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, c0), (t1, c1) in zip(keys, keys[1:]):
        if t <= t1:
            return c0.lerp_to(c1, smooth((t - t0) / max(1e-6, t1 - t0)))
    return keys[-1][1]


# ------------------------------------------------------------- primitives ----
def _c(v):
    """Coerce a colour (possibly computed with floats) into what PIL accepts."""
    if isinstance(v, (tuple, list)):
        if len(v) == 4:
            return (int(v[0]), int(v[1]), int(v[2]), int(v[3]))
        return (int(v[0]), int(v[1]), int(v[2]))
    return v


class Ink:
    """Thin wrapper over an ImageDraw with camera-aware helpers and ink shadows."""

    def __init__(self, img: Image.Image, cam: Camera | None = None, width: float = 5.0,
                 colour=INK, shadow: float = 0.0):
        self.img = img
        self.d = ImageDraw.Draw(img, "RGBA")
        self.cam = cam or Camera()
        self.width = width
        self.colour = colour
        self.shadow = shadow

    # ---- transform helpers
    def w2s(self, x, y):
        return self.cam.screen(x, y)

    def s(self, v):
        return v * self.cam.zoom * self.cam.pix

    def line(self, pts, width=None, colour=None, joint="curve"):
        w = self.s(width or self.width)
        p = [self.w2s(*q) for q in pts]
        self.d.line(p, fill=_c(colour or self.colour), width=max(1, int(round(w))), joint=joint)
        # round caps
        r = max(1, int(round(w / 2)))
        for q in (p[0], p[-1]):
            self.d.ellipse([q[0] - r, q[1] - r, q[0] + r, q[1] + r], fill=_c(colour or self.colour))

    def poly(self, pts, fill=None, outline=None, width=None):
        p = [self.w2s(*q) for q in pts]
        self.d.polygon(p, fill=_c(fill), outline=_c(outline))
        if outline:
            self.d.line(p + [p[0]], fill=_c(outline), width=max(1, int(round(self.s(width or self.width)))),
                        joint="curve")

    def ellipse(self, x0, y0, x1, y1, fill=None, outline=None, width=None):
        a = self.w2s(x0, y0)
        b = self.w2s(x1, y1)
        self.d.ellipse([a, b], fill=_c(fill), outline=_c(outline),
                       width=max(1, int(round(self.s(width or self.width)))) if outline else 0)

    def rrect(self, x0, y0, x1, y1, r=18, fill=None, outline=None, width=None):
        a = self.w2s(x0, y0)
        b = self.w2s(x1, y1)
        rad = self.s(r)
        self.d.rounded_rectangle([a, b], radius=rad, fill=_c(fill), outline=_c(outline),
                                 width=max(1, int(round(self.s(width or self.width)))) if outline else 0)

    def text(self, xy, s, role="label", size=44, fill=None, anchor="la", align="left",
             stroke=0, stroke_fill=None):
        x, y = self.w2s(*xy)
        draw_text_runs(self.d, (x, y), s, role, max(6, int(round(self.s(size)))), fill or INK,
                       anchor=anchor, align=align, stroke_width=int(round(self.s(stroke))),
                       stroke_fill=stroke_fill)

    def text_px(self, xy, s, role="label", size=44, fill=None, anchor="la", align="left"):
        draw_text_runs(self.d, xy, s, role, max(6, int(round(size))), fill or INK,
                       anchor=anchor, align=align)


def measure(text, role, size) -> tuple[int, int]:
    f = font(role, size)
    box = f.getbbox(text)
    return box[2] - box[0], box[3] - box[1]


def wrap(text, role, size, max_w) -> list[str]:
    """Greedy word wrap measured with the actual font at the actual size."""
    f = font(role, size)
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if f.getlength(trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def fit_text(text, role, max_w, max_h, start=120, min_size=28, line_gap=1.08):
    """Largest size at which the text block fits; returns (size, lines)."""
    size = start
    while size > min_size:
        lines = wrap(text, role, size, max_w)
        f = font(role, size)
        h = len(lines) * size * line_gap
        widest = max(f.getlength(l) for l in lines) if lines else 0
        if h <= max_h and widest <= max_w:
            return size, lines
        size -= 2
    return min_size, wrap(text, role, min_size, max_w)


# ------------------------------------------------------------ background ----
_grain_cache: dict[tuple, Image.Image] = {}


def grain(w, h, strength=6, seed=7):
    key = (w, h, strength, seed)
    if key not in _grain_cache:
        rnd = random.Random(seed)
        small = Image.new("L", (w // 3, h // 3))
        small.putdata([128 + rnd.randint(-strength, strength) for _ in range((w // 3) * (h // 3))])
        _grain_cache[key] = small.resize((w, h), Image.BILINEAR)
    return _grain_cache[key]


# Backgrounds are pure functions of their arguments (grain is seeded, the vignette is a
# deterministic blur), so identical calls can be computed once and copied per frame. This is
# what makes a full 1080p render affordable on two cores. Returned images are always copies:
# scenes draw on top of them.
_BG_CACHE: dict = {}


def _cached_bg(key, builder, limit=12):
    img = _BG_CACHE.get(key)
    if img is None:
        if len(_BG_CACHE) >= limit:
            _BG_CACHE.clear()
        img = _BG_CACHE[key] = builder()
    return img.copy()


def paper_bg(w=1920, h=1080, base=PAPER, tint=None, vignette=0.06, grain_strength=5):
    return _cached_bg(("paper", w, h, base, tint, vignette, grain_strength),
                      lambda: _paper_bg_build(w, h, base, tint, vignette, grain_strength))


def _paper_bg_build(w=1920, h=1080, base=PAPER, tint=None, vignette=0.06, grain_strength=5):
    img = Image.new("RGB", (w, h), base)
    if tint:
        grd = Image.new("L", (1, h))
        for y in range(h):
            u = y / max(1, h - 1)
            grd.putpixel((0, y), int(255 * (0.55 - 0.55 * u)))
        band = Image.new("RGB", (w, h), tint)
        img = Image.composite(band, img, grd.resize((w, h)))
    img = Image.blend(img, Image.merge("RGB", (grain(w, h, grain_strength),) * 3), 0.10)
    if vignette > 0:
        mask = Image.new("L", (w, h), 0)
        md = ImageDraw.Draw(mask)
        md.ellipse([-w * 0.25, -h * 0.35, w * 1.25, h * 1.35], fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(160))
        dark = Image.new("RGB", (w, h), (228, 222, 206))
        img = Image.composite(img, dark, mask)
    return img


def night_bg(w=1920, h=1080, seed=3, stars=140):
    return _cached_bg(("night", w, h, seed, stars), lambda: _night_bg_build(w, h, seed, stars))


def _night_bg_build(w=1920, h=1080, seed=3, stars=140):
    img = Image.new("RGB", (w, h), NIGHT)
    d = ImageDraw.Draw(img)
    for y in range(h):
        u = y / h
        c = tuple(int(NIGHT[i] + (NIGHT2[i] - NIGHT[i]) * u) for i in range(3))
        d.line([(0, y), (w, y)], fill=c)
    rnd = random.Random(seed)
    for _ in range(stars):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h * 0.85)
        r = rnd.choice([1, 1, 1.4, 2.0])
        a = rnd.randint(120, 245)
        d.ellipse([x - r, y - r, x + r, y + r], fill=(a, a, min(255, a + 20)))
    return img
