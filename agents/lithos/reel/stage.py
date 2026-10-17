#!/usr/bin/env python3
"""reel.stage - the persistent 3D-laptop studio frame: camera drift, laptop,
screen projection, glossy floor reflection, headline overlay + its mirror."""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

from engine import (W, H, font, text_rgba, quad_project, smoothstep)

CORAL = (224, 120, 86)

# canonical laptop geometry at camera rest (frame space, 1080x1920)
CAN = {
    "sTL": (232.0, 468.0), "sTR": (958.0, 412.0),
    "sBR": (996.0, 1024.0), "sBL": (198.0, 1142.0),
    "fL": (138.0, 1338.0), "fR": (1046.0, 1178.0),
}


def camera(t):
    """Slow orbit + push-in."""
    s = 1.0 + 0.20 * smoothstep(t / 12.8) + 0.030 * math.sin(t * 0.42)
    yaw = 12.0 * math.sin(t * 0.30 + 0.4) + 6.0 * smoothstep(t / 12.8)
    dx = 16.0 * math.sin(t * 0.23 + 1.2)
    dy = -26.0 * smoothstep(t / 12.8) + 7.0 * math.sin(t * 0.35)
    cx = (CAN["sTL"][0] + CAN["sTR"][0] + CAN["sBL"][0] + CAN["sBR"][0]) / 4
    cy = (CAN["sTL"][1] + CAN["sTR"][1] + CAN["sBL"][1] + CAN["sBR"][1]) / 4
    out = {}
    for k, (x, y) in CAN.items():
        x2 = x + yaw * ((y - cy) / 700.0) * 3.0
        out[k] = (cx + (x2 - cx) * s + dx, cy + (y - cy) * s + dy)
    return out


def screen_quad(cam):
    return [cam["sTL"], cam["sTR"], cam["sBR"], cam["sBL"]]


def asterisk_rgba(size=250, color=CORAL, petals=12):
    im = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = cy = size
    w = size * 0.062
    for i in range(petals):
        a = i * (2 * math.pi / petals) + 0.13
        r = size * 0.86 * (0.88 + 0.12 * ((i * 7) % 5) / 4.0)
        x1 = cx + size * 0.13 * math.cos(a); y1 = cy + size * 0.13 * math.sin(a)
        x2 = cx + r * math.cos(a);           y2 = cy + r * math.sin(a)
        d.line([(x1, y1), (x2, y2)], fill=(*color, 255), width=int(w * 2))
        d.ellipse([x2 - w, y2 - w, x2 + w, y2 + w], fill=(*color, 255))
    d.ellipse([cx - size * 0.13, cy - size * 0.13, cx + size * 0.13, cy + size * 0.13],
              fill=(*color, 255))
    return im.crop((size // 2, size // 2, size * 3 // 2, size * 3 // 2))


def _bilin(a, b, c, d, u, v):
    top = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u)
    bot = (d[0] + (c[0] - d[0]) * u, d[1] + (c[1] - d[1]) * u)
    return (top[0] + (bot[0] - top[0]) * v, top[1] + (bot[1] - top[1]) * v)


def laptop_rgba(cam):
    """Laptop body + bezel + keyboard as RGBA (transparent bg)."""
    sTL, sTR, sBR, sBL = cam["sTL"], cam["sTR"], cam["sBR"], cam["sBL"]
    fL, fR = cam["fL"], cam["fR"]
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    base = [sBL, sBR, fR, fL]

    d.polygon([sBL, sBR, fR, fL], fill=(30, 29, 31, 255))
    rows, cols = 6, 14
    for r in range(rows):
        v0 = 0.10 + r * 0.105
        v1 = v0 + 0.082
        for c in range(cols):
            u0 = 0.045 + c * 0.0665
            u1 = u0 + 0.056
            k = [_bilin(*base, u0, v0), _bilin(*base, u1, v0),
                 _bilin(*base, u1, v1), _bilin(*base, u0, v1)]
            g = int(52 - 4 * r + 6 * ((r + c) % 2))
            d.polygon(k, fill=(g, g - 2, g - 4, 255))
    tp = [_bilin(*base, 0.32, 0.78), _bilin(*base, 0.68, 0.78),
          _bilin(*base, 0.68, 0.985), _bilin(*base, 0.32, 0.985)]
    d.polygon(tp, fill=(38, 37, 40, 255))
    d.polygon([fL, fR, (fR[0] + 4, fR[1] + 16), (fL[0] - 4, fL[1] + 18)], fill=(16, 15, 17, 255))
    d.polygon([sBL, fL, (fL[0] - 4, fL[1] + 18), (sBL[0] - 5, sBL[1] + 14)], fill=(12, 11, 13, 255))

    cx = sum(p[0] for p in (sTL, sTR, sBR, sBL)) / 4
    cy = sum(p[1] for p in (sTL, sTR, sBR, sBL)) / 4

    def out(p, k=1.030):
        return (cx + (p[0] - cx) * k, cy + (p[1] - cy) * k)
    bTL, bTR, bBR, bBL = out(sTL), out(sTR), out(sBR), out(sBL)
    d.polygon([bBL, bBR, (bBR[0] - 4, bBR[1] + 9), (bBL[0] - 4, bBL[1] + 9)], fill=(20, 19, 22, 255))
    d.polygon([bTL, bTR, bBR, bBL], fill=(22, 21, 25, 255))
    d.polygon([bTL, bTR, bBR, bBL], outline=(60, 58, 64, 255), width=3)
    return im


def overlay_rgba(t):
    """Headline + asterisk as RGBA layer."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ast = asterisk_rgba(252)
    im.alpha_composite(ast, dest=(28, 118))
    fnt = font("ui_b", 74)
    head = text_rgba("kinetic thinks in motion.", fnt, (242, 242, 240), tracking=-1.0)
    # italic shear
    sh = Image.new("RGBA", (head.size[0] + 70, head.size[1] + 12), (0, 0, 0, 0))
    for y in range(head.size[1]):
        xs = int((head.size[1] - y) * 0.16)
        sh.paste(head.crop((0, y, head.size[0], y + 1)), (xs, y))
    im.alpha_composite(sh, dest=(150, 300))
    return im


def mirror_layer(im, y_floor, squash=0.92, fade=110.0, blur=1.6, gain=1.0):
    """Vertical mirror of an RGBA layer about y_floor, squashed + faded."""
    yf = int(y_floor)
    src = im.crop((0, 0, W, min(yf, H)))
    fl = src.transpose(Image.FLIP_TOP_BOTTOM)
    fl = fl.resize((W, max(1, int(fl.size[1] * squash))), Image.LANCZOS)
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    out.paste(fl, (0, yf))
    a = np.array(out).astype(np.float32)
    d = np.arange(H) - yf
    fall = np.clip(1.0 - d / fade, 0, 1)
    a[:, :, 3] *= (np.where(d >= 0, fall, 0.0) * gain)[:, None]
    out = Image.fromarray(a.astype(np.uint8))
    return out.filter(ImageFilter.GaussianBlur(blur))


class Stage:
    def __init__(self):
        self._ov = overlay_rgba(0)

    def stage_rgba(self, t, screen_content_rgb):
        cam = camera(t)
        laptop = laptop_rgba(cam)
        warped = quad_project(Image.fromarray(screen_content_rgb).convert("RGBA"),
                              screen_quad(cam), (W, H))
        # screen light spill UNDER the content (never dim the screen itself)
        spill = warped.filter(ImageFilter.GaussianBlur(80))
        sa = np.array(spill).astype(np.float32)
        sa[:, :, 0:3] *= 0.5
        sa[:, :, 3] = (sa[:, :, 3] * 0.8).astype(np.uint8)
        stage = Image.alpha_composite(laptop, Image.fromarray(sa.astype(np.uint8)))
        stage = Image.alpha_composite(stage, warped)
        return stage, cam

    def frame(self, t, screen_content_rgb):
        cam = camera(t)
        stage, cam = self.stage_rgba(t, screen_content_rgb)

        # bg: dark studio + floor gradient
        bg = Image.new("RGBA", (W, H), (8, 8, 10, 255))
        g = np.linspace(0, 30, H, dtype=np.float32)[:, None]
        grad = np.zeros((H, W, 4), np.uint8)
        grad[:, :, 0] = (g * 0.55).astype(np.uint8)
        grad[:, :, 1] = (g * 0.55).astype(np.uint8)
        grad[:, :, 2] = (g * 0.8).astype(np.uint8)
        grad[:, :, 3] = 255
        bg = Image.alpha_composite(bg, Image.fromarray(grad))

        y_floor = max(cam["fL"][1], cam["fR"][1]) + 14

        # reflections: stage + overlay text, then stage over
        r_stage = mirror_layer(stage, y_floor, squash=0.92, fade=300.0, blur=2.0, gain=1.05)
        out = Image.alpha_composite(bg, r_stage)
        out = Image.alpha_composite(out, stage)

        r_ov = self._ov.transpose(Image.FLIP_TOP_BOTTOM).filter(ImageFilter.GaussianBlur(1.8))
        ra = np.array(r_ov).astype(np.float32)
        ra[:, :, 3] *= 0.52
        r_ov = Image.fromarray(ra.astype(np.uint8))
        out = Image.alpha_composite(out, r_ov)
        out = Image.alpha_composite(out, self._ov)
        return np.array(out.convert("RGB"))
