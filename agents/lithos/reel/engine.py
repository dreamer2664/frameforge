#!/usr/bin/env python3
"""mg.engine - 2.5D mograph compositor.

Layers are RGBA PIL images composited onto a float32 RGB canvas; finishing
adds bloom, vignette and seeded grain. Smears are echo trails along a motion
vector (the AE 'mograph smear' technique from research/motion-design-research.md).
Everything is a pure function of time - deterministic, seeded.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1080, 1920
FONTS = {
    "ui": "/home/user/work/frameforge/agents/lithos/px/fonts/Inter-SemiBold.ttf",
    "ui_b": "/home/user/work/frameforge/agents/lithos/px/fonts/Inter-SemiBold.ttf",
    "mono_b": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    "ui_med": "/home/user/work/frameforge/agents/lithos/px/fonts/Inter-Medium.ttf",
    "serif": "/home/user/work/frameforge/agents/lithos/px/fonts/Fraunces.ttf",
    "mono": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
}
_font_cache = {}


def font(name, size):
    key = (name, size)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(FONTS[name], size)
    return _font_cache[key]


def smoothstep(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = float(np.clip(x, 0.0, 1.0))
    return 1 - (1 - x) ** 3


def ease_in(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x ** 3


def ease_io(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3 - 2 * x)


class Canvas:
    def __init__(self, w=W, h=H, bg=(0, 0, 0)):
        self.buf = np.zeros((h, w, 3), dtype=np.float32)
        self.buf[:] = np.array(bg, dtype=np.float32) / 255.0

    def comp(self, rgba, pos=(0, 0), opacity=1.0, add=False):
        """Composite an RGBA PIL image at pos (top-left)."""
        if rgba is None or opacity <= 0:
            return
        layer = np.asarray(rgba, dtype=np.float32) / 255.0
        a = layer[:, :, 3:4] * opacity
        x, y = int(pos[0]), int(pos[1])
        h, w = layer.shape[:2]
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.buf.shape[1], x + w), min(self.buf.shape[0], y + h)
        if x1 <= x0 or y1 <= y0:
            return
        src = layer[y0 - y:y1 - y, x0 - x:x1 - x]
        aa = a[y0 - y:y1 - y, x0 - x:x1 - x]
        region = self.buf[y0:y1, x0:x1]
        if add:
            region += src[:, :, :3] * aa
        else:
            region *= (1 - aa)
            region += src[:, :, :3] * aa

    def add_field(self, rgb, mask):
        """Add an RGB field weighted by mask [0,1] (both full-frame arrays)."""
        self.buf += rgb.astype(np.float32) * mask[:, :, None]

    def finish(self, bloom_thresh=0.78, bloom_gain=0.30, vignette=0.26,
               grain=0.012, seed=0):
        img = np.clip(self.buf, 0.0, 1.0)
        bright = np.clip(img - bloom_thresh, 0, None) / max(1e-6, 1 - bloom_thresh)
        if bright.max() > 0:
            b1 = np.asarray(Image.fromarray((bright * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(22)), dtype=np.float32) / 255.0
            b2 = np.asarray(Image.fromarray((bright * 255).astype(np.uint8)).filter(
                ImageFilter.GaussianBlur(70)), dtype=np.float32) / 255.0
            img = np.clip(img + bloom_gain * b1 + 0.35 * bloom_gain * b2, 0, 1)
        if vignette > 0:
            h, w = img.shape[:2]
            yy, xx = np.mgrid[0:h, 0:w]
            r = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
            img *= (1 - vignette * np.clip(r - 0.45, 0, 1.2))[..., None]
        if grain > 0:
            rng = np.random.default_rng(1000 + seed)
            img = np.clip(img + rng.normal(0, grain, img.shape), 0, 1)
        return (img * 255 + 0.5).astype(np.uint8)


# ------------------------------------------------------------- text helpers

def text_rgba(s, fnt, color, tracking=0.0):
    """Render a string to RGBA with optional tracking (px)."""
    if not s:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    if tracking == 0:
        bbox = fnt.getbbox(s)
        im = Image.new("RGBA", (bbox[2] - bbox[0] + 20, bbox[3] - bbox[1] + 20), (0, 0, 0, 0))
        ImageDraw.Draw(im).text((10 - bbox[0], 10 - bbox[1]), s, font=fnt, fill=tuple(color) + (255,))
        return im
    # tracked: draw char by char
    widths = [fnt.getbbox(c)[2] - fnt.getbbox(c)[0] + tracking for c in s]
    total = int(sum(widths)) + 20
    bbox = fnt.getbbox("Hg")
    im = Image.new("RGBA", (total, bbox[3] - bbox[1] + 24), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 10
    for c, w in zip(s, widths):
        d.text((x, 12), c, font=fnt, fill=tuple(color) + (255,))
        x += w
    return im


def chars_rgba(s, fnt, color, tracking=0.0):
    """Per-character RGBA layers plus advances [(img, x_offset), ...]."""
    out = []
    x = 0
    for c in s:
        im = text_rgba(c, fnt, color)
        out.append((im, x))
        adv = fnt.getbbox(c)[2] - fnt.getbbox(c)[0]
        x += adv + tracking
    return out, x


# ------------------------------------------------------------ shape helpers

def rounded_rect(size, radius, fill=None, stroke=None, stroke_w=3):
    im = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if fill:
        d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius, fill=tuple(fill) + (255,))
    if stroke:
        d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius,
                            outline=tuple(stroke[:3]) + (stroke[3] if len(stroke) > 3 else 255,),
                            width=stroke_w)
    return im


def glow_under(im, color, radius=18, gain=0.8):
    """Return an RGBA of the silhouette of im, blurred, in `color` (a glow)."""
    a = np.asarray(im)[:, :, 3].astype(np.float32) / 255.0
    g = Image.fromarray((a * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(radius))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    col = np.zeros((im.size[1], im.size[0], 4), dtype=np.uint8)
    col[:, :, 0], col[:, :, 1], col[:, :, 2] = color[0], color[1], color[2]
    col[:, :, 3] = (np.asarray(g, dtype=np.float32) * gain).astype(np.uint8)
    return Image.fromarray(col)


def smear(im, vx, vy, n=9, decay=0.72):
    """Echo smear along (vx, vy): stacked copies with decaying alpha."""
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    total = 0.0
    for i in range(n - 1, -1, -1):
        w = decay ** i
        total += w
        layer = im.copy()
        alpha = np.asarray(layer)[:, :, 3].astype(np.float32) * (w / total)
        layer.putalpha(Image.fromarray(alpha.astype(np.uint8)))
        out.alpha_composite(layer, dest=(int(-vx * i), int(-vy * i)) if (vx or vy) else (0, 0))
    return out


def place(canvas, im, cx, cy, opacity=1.0, add=False, angle=0.0, scale=1.0):
    """Place an RGBA image centred at (cx, cy), optional rotation/scale."""
    if im is None or opacity <= 0:
        return
    if scale != 1.0 or angle != 0.0:
        w = max(2, int(im.size[0] * scale))
        h = max(2, int(im.size[1] * scale))
        im = im.resize((w, h), Image.LANCZOS)
        if angle != 0.0:
            im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    canvas.comp(im, pos=(int(cx - im.size[0] / 2), int(cy - im.size[1] / 2)),
                opacity=opacity, add=add)


def persp_coeffs(dst_quad, src_quad):
    """Coefficients for PIL PERSPECTIVE: maps OUTPUT coords -> INPUT coords."""
    A = []
    B = []
    for (xd, yd), (xs, ys) in zip(dst_quad, src_quad):
        A.append([xd, yd, 1, 0, 0, 0, -xd * xs, -yd * xs])
        A.append([0, 0, 0, xd, yd, 1, -xd * ys, -yd * ys])
        B += [xs, ys]
    import numpy as _np
    res = _np.linalg.solve(_np.array(A, dtype=_np.float64), _np.array(B, dtype=_np.float64))
    return [float(v) for v in res]


def quad_project(im, corners, out_size):
    """Project im (a rect) so its corners land at `corners` [(tl),(tr),(br),(bl)]
    of out_size. True perspective via PERSPECTIVE coefficients."""
    w, h = im.size
    src = [(0, 0), (w, 0), (w, h), (0, h)]
    coeffs = persp_coeffs([tuple(map(float, p)) for p in corners], src)
    return im.transform(out_size, Image.PERSPECTIVE, coeffs, resample=Image.BICUBIC)
