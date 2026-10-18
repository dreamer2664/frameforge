#!/usr/bin/env python3
"""Build the static art for 'LAST SHIFT - WARD 7', then splice it into ONE html file.

Why one file: the film's own end card claims a single self-contained page, and
the renderer screenshots that page, so the typefaces must travel with it. The
page is self-contained: no network, no sidecar, no build step at playback time.

Inputs   : fonts/*.ttf (OFL)
Outputs  : build/fonts/*.woff2     subset (variable pinned where useful)
           build/night.html         the film, every asset inlined
           build/manifest.json      sizes + sha256 of what went in
"""
from __future__ import annotations

import base64
import hashlib
import json
import re
import shutil
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
BUILD = HERE / "build"

CHARS = (
    "".join(chr(c) for c in range(32, 127))
    + "°·—–…‘’“”±×•●▲▼■□→←↑↓"
)


# --------------------------------------------------------------------------- #
# fonts
# --------------------------------------------------------------------------- #
def _subset(font, text: str) -> None:
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
    """Pin a variable font to one instance (the heavy display cut)."""
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
    instance_font(FONTS / "Archivo-var.ttf", out / "archivo-black.woff2", {"wght": 900, "wdth": 88})
    made["archivo-black.woff2"] = (out / "archivo-black.woff2").stat().st_size
    return made


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
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html)
    left = re.findall(r"__[A-Z]+__", html)
    if left:
        raise SystemExit(f"unsubstituted placeholders: {sorted(set(left))}")


def main() -> None:
    BUILD.mkdir(parents=True, exist_ok=True)
    src = HERE / "night.src.html"
    if not src.exists():
        raise SystemExit("night.src.html is missing - write the film first")
    fonts = build_fonts()
    out = BUILD / "night.html"
    splice(src, out)
    manifest = {
        "film": "last-shift-ward-7",
        "html": {
            "path": "build/night.html",
            "bytes": out.stat().st_size,
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        },
        "fonts": fonts,
        "licences": ["OFL-1.1 (Archivo, Inter, IBM Plex Mono)"],
    }
    (BUILD / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
