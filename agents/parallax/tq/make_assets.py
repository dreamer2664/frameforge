#!/usr/bin/env python3
"""Build the static art for the 'cadence' reel, then splice it into ONE html file.

Why one file: the film's own end card claims "900 frames. / One file, no timeline."
That claim has to be literally true, so the typefaces, the grain tile, the studio
backdrop and the glow sprites are embedded as base64 and the page is
self-contained: no network, no sidecar, no build step at playback time.

Inputs   : fonts/*.ttf (OFL)
Outputs  : build/fonts/*.woff2      subset (variable kept where useful)
           work/{noise.png,studio.jpg,cream.jpg,glow.png,shadow.png}
           build/flux.html            the film, with every asset inlined
           build/manifest.json        sizes + sha256 of what went in
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
WORK = HERE / "work"
BUILD = HERE / "build"

CHARS = "".join(chr(c) for c in range(32, 127)) + "°·—–…‘’“”±×"


# --------------------------------------------------------------------------- #
# fonts
# --------------------------------------------------------------------------- #
def _subset(font, text: str):
    from fontTools import subset

    opts = subset.Options()
    opts.flavor = "woff2"
    opts.desubroutinize = True
    opts.hinting = False
    opts.layout_features = ["kern", "liga", "calt", "tnum", "ccmp"]
    opts.name_IDs = ["*"]
    opts.notdef_outline = True
    opts.recalc_bounds = True
    opts.drop_tables = [t for t in opts.drop_tables if t != "GPOS"] + ["GPOS"]
    sub = subset.Subsetter(options=opts)
    sub.populate(text=text)
    sub.subset(font)


def subset_font(src: Path, dst: Path) -> None:
    from fontTools.ttLib import TTFont

    font = TTFont(str(src))
    _subset(font, CHARS)
    font.flavor = "woff2"
    dst.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(dst))


def instance_font(src: Path, dst: Path, axes: dict) -> None:
    """Pin a variable font to one instance (used for the canvas-set display face)."""
    from fontTools.ttLib import TTFont
    from fontTools.varLib import instancer

    font = TTFont(str(src))
    font = instancer.instantiateVariableFont(font, axes, inplace=True, updateFontNames=False)
    _subset(font, CHARS)
    font.flavor = "woff2"
    dst.parent.mkdir(parents=True, exist_ok=True)
    font.save(str(dst))


def build_fonts() -> dict:
    out = BUILD / "fonts"
    if out.exists():
        shutil.rmtree(out)
    made = {}
    jobs = [
        ("Inter-var.ttf", "inter.woff2", None),
        ("IBMPlexMono-Regular.ttf", "mono.woff2", None),
        ("IBMPlexMono-Medium.ttf", "mono-medium.woff2", None),
        ("IBMPlexMono-SemiBold.ttf", "mono-semibold.woff2", None),
    ]
    for src_name, out_name, axes in jobs:
        src = FONTS / src_name
        if not src.exists():
            raise SystemExit(f"missing font: {src}")
        dst = out / out_name
        if axes:
            instance_font(src, dst, axes)
        else:
            subset_font(src, dst)
        made[out_name] = dst.stat().st_size
    # display face for the canvas work: Archivo pinned to a heavy, slightly narrow cut
    instance_font(FONTS / "Archivo-var.ttf", out / "archivo-black.woff2", {"wght": 900, "wdth": 88})
    made["archivo-black.woff2"] = (out / "archivo-black.woff2").stat().st_size
    return made


# --------------------------------------------------------------------------- #
# art
# --------------------------------------------------------------------------- #
def _blur(a: np.ndarray, r: float) -> np.ndarray:
    im = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))
    return np.asarray(im).astype(np.float32)


def studio_backdrop(w: int = 1920, h: int = 1080) -> Image.Image:
    """The blurred photographic studio: cool grey-green wall, warm floor bounce."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = xx / w
    v = yy / h

    top = np.array([0xA0, 0x9B, 0x93], np.float32)
    bot = np.array([0x63, 0x61, 0x5C], np.float32)
    img = top[None, None, :] * (1 - v)[..., None] + bot[None, None, :] * v[..., None]

    def blob(cx, cy, rx, ry, gain):
        d = ((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2
        return (gain * np.exp(-d * 2.2))[..., None]

    img += blob(0.50, -0.16, 0.62, 0.55, 34.0)     # key light, upper centre
    img += blob(0.14, 0.02, 0.30, 0.34, 9.0)       # cool secondary, upper left
    bands = np.sin(u * 9.0 + 0.6) * 2.6 + np.sin(u * 23.0) * 1.4
    img += bands[..., None]
    d = ((u - 0.5) / 0.52) ** 2 + ((v - 1.02) / 0.30) ** 2
    floor = np.exp(-d * 2.0)[..., None]
    img = img * (1 - 0.35 * floor) + np.array([0xA7, 0x5D, 0x31], np.float32)[None, None, :] * 0.62 * floor
    r = np.sqrt((u - 0.5) ** 2 + (v - 0.5) ** 2)
    img *= (1.0 - 0.30 * np.clip(r * 1.55, 0, 1) ** 2)[..., None]

    img = _blur(img, 3.0)
    rng = np.random.default_rng(4)
    img += rng.normal(0, 1.7, img.shape[:2])[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def cream_backdrop(w: int = 1920, h: int = 1080) -> Image.Image:
    """The light UI board: warm paper with one huge soft rounded card."""
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    u = xx / w
    v = yy / h
    base = np.array([0xE8, 0xE4, 0xDB], np.float32)
    img = np.broadcast_to(base, (h, w, 3)).copy()
    img += (5.0 * (1.0 - v))[..., None]

    card = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([150, 70, w - 120, h - 30], radius=150, fill=255)
    card = card.filter(ImageFilter.GaussianBlur(26))
    c = np.asarray(card).astype(np.float32) / 255.0
    img = img * (1 - c[..., None] * 0.18) + np.array([0xF5, 0xF2, 0xEC], np.float32)[None, None, :] * c[..., None] * 0.18

    sh = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(sh)
    d.rounded_rectangle([186, 108, w - 86, h + 4], radius=150, fill=255)
    sh = sh.filter(ImageFilter.GaussianBlur(60))
    s = np.asarray(sh).astype(np.float32) / 255.0
    img *= (1.0 - 0.07 * s)[..., None]

    r = np.sqrt((u - 0.5) ** 2 + (v - 0.5) ** 2)
    img *= (1.0 - 0.06 * np.clip(r * 1.5, 0, 1) ** 2)[..., None]
    img = _blur(img, 2.0)
    rng = np.random.default_rng(9)
    img += rng.normal(0, 1.5, img.shape[:2])[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def glow_sprite(n: int = 512) -> Image.Image:
    """Warm radial glow with alpha - the floor light and the hot core."""
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u = (xx - n / 2) / (n / 2)
    v = (yy - n / 2) / (n / 2)
    d = np.sqrt(u * u + v * v)
    a = np.clip(1.0 - d, 0, 1) ** 2.1
    core = np.clip(1.0 - d * 2.6, 0, 1) ** 1.5
    rgb = (np.array([0xFF, 0x8A, 0x2E], np.float32)[None, None, :] * (1 - core[..., None])
           + np.array([0xFF, 0xE2, 0xB0], np.float32)[None, None, :] * core[..., None])
    out = np.dstack([rgb, (a * 255.0)[..., None]])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def shadow_sprite(n: int = 256) -> Image.Image:
    yy, xx = np.mgrid[0:n, 0:n].astype(np.float32)
    u = (xx - n / 2) / (n / 2)
    v = (yy - n / 2) / (n / 2)
    d = np.sqrt(u * u + v * v)
    a = np.clip(1.0 - d, 0, 1) ** 2.4
    out = np.dstack([np.zeros((n, n, 3), np.float32), (a * 255.0)[..., None]])
    return Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA")


def noise_tile(n: int = 256) -> Image.Image:
    rng = np.random.default_rng(17)
    a = np.clip(rng.normal(0.5, 0.16, (n, n)), 0, 1)
    out = np.dstack([(a * 255).astype(np.uint8)] * 3)
    return Image.fromarray(out)


def build_art() -> dict:
    WORK.mkdir(parents=True, exist_ok=True)
    studio = WORK / "studio.jpg"
    cream = WORK / "cream.jpg"
    glow = WORK / "glow.png"
    shadow = WORK / "shadow.png"
    noise = WORK / "noise.png"
    studio_backdrop().save(studio, quality=92, optimize=True)
    cream_backdrop().save(cream, quality=93, optimize=True)
    glow_sprite().save(glow, optimize=True)
    shadow_sprite().save(shadow, optimize=True)
    noise_tile().save(noise, optimize=True)
    return {p.name: p.stat().st_size for p in (studio, cream, glow, shadow, noise)}


# --------------------------------------------------------------------------- #
# splice
# --------------------------------------------------------------------------- #
def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def splice(src: Path, out: Path) -> None:
    html = src.read_text()
    faces = [
        ("archivo-black.woff2", "Archivo Black", "900", "normal"),
        ("inter.woff2", "Inter", "100 900", "normal"),
        ("mono.woff2", "IBM Plex Mono", "400", "normal"),
        ("mono-medium.woff2", "IBM Plex Mono", "500", "normal"),
        ("mono-semibold.woff2", "IBM Plex Mono", "600", "normal"),
    ]
    css = []
    for name, fam, weight, style in faces:
        css.append(
            "@font-face{font-family:'%s';src:url(data:font/woff2;base64,%s) format('woff2');"
            "font-weight:%s;font-style:%s;font-display:block;}" % (fam, b64(BUILD / "fonts" / name), weight, style)
        )
    html = html.replace("/*__FONTS__*/", "\n".join(css))
    for key, path in (("__NOISE__", WORK / "noise.png"), ("__STUDIO__", WORK / "studio.jpg"),
                      ("__CREAM__", WORK / "cream.jpg"), ("__GLOW__", WORK / "glow.png"),
                      ("__SHADOW__", WORK / "shadow.png")):
        html = html.replace(key, b64(path))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    left = re.findall(r"__[A-Z]+__", html)
    if left:
        raise SystemExit(f"unsubstituted placeholders: {sorted(set(left))}")


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    src = HERE / "flux.src.html"
    if not src.exists():
        raise SystemExit("flux.src.html is missing - write the film first")
    fonts = build_fonts()
    art = build_art()
    out = BUILD / "flux.html"
    splice(src, out)
    manifest = {
        "film": "cadence",
        "html": {"path": "build/flux.html", "bytes": out.stat().st_size,
                 "sha256": hashlib.sha256(out.read_bytes()).hexdigest()},
        "fonts": fonts,
        "art": art,
        "licences": ["OFL-1.1 (Archivo, Inter, IBM Plex Mono)"],
    }
    (BUILD / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
