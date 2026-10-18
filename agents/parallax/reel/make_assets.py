#!/usr/bin/env python3
"""Build the static assets the film needs, then splice them into ONE html file.

Why: the film's own end-card claims "840 frames. / One HTML file." — that claim
has to be literally true, so the fonts and the grain tile are embedded as
base64 and the page is self-contained (no network, no sidecar files).

Outputs (all under this folder):
  fonts/*.woff2        subset of Inter (variable) + IBM Plex Mono (OFL)
  work/noise.png       256x256 film-grain tile (numpy)
  build/flux.html      the final single-file film, with fonts spliced in
"""
from __future__ import annotations

import base64
import io
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
FONTS = HERE / "fonts"
WORK = HERE / "work"
BUILD = HERE / "build"

# Every glyph the film can possibly draw. Subsetting to this set keeps the
# embedded fonts tiny (a few KB each) so the html stays a single tidy file.
GLYPHS = (
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    " .,:;!?&/()[]{}<>%*+-=#@'\""
    "·—–…°"
)


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)


def subset(src: Path, out: Path, extra: list[str] | None = None) -> Path:
    out.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable, "-m", "fontTools.subset", str(src),
        "--text=" + GLYPHS,
        "--flavor=woff2",
        "--layout-features=kern,liga,calt,tnum,ss01,zero",
        "--no-hinting",
        "--desubroutinize",
        "--name-IDs=",
        "--output-file=" + str(out),
    ]
    if extra:
        cmd += extra
    run(cmd)
    return out


def grain_tile(size: int = 256, seed: int = 20261018) -> Path:
    """Film grain: a tileable, luminance-only noise field.

    Tiles seamlessly because the noise is generated in the frequency domain and
    summed with integer-frequency cosine pairs -> the result is periodic.
    """
    rng = np.random.default_rng(seed)
    out = np.zeros((size, size), dtype=np.float32)
    for _ in range(6):
        fx, fy = rng.integers(1, size // 2, size=2)
        phase = rng.uniform(0, 2 * np.pi)
        amp = 1.0 / (fx + fy)
        out += amp * np.cos(2 * np.pi * (fx * np.arange(size)[:, None] / size
                                        + fy * np.arange(size)[None, :] / size) + phase)
    out -= out.mean()
    out /= max(out.std(), 1e-6)
    # push to a slightly heavier, filmic distribution
    out = np.sign(out) * np.abs(out) ** 0.85
    v = np.clip(128 + out * 46, 0, 255).astype(np.uint8)
    rgba = np.zeros((size, size, 4), dtype=np.uint8)
    rgba[..., 0] = rgba[..., 1] = rgba[..., 2] = v
    rgba[..., 3] = 255
    WORK.mkdir(parents=True, exist_ok=True)
    p = WORK / "noise.png"
    Image.fromarray(rgba, "RGBA").save(p, optimize=True)
    return p


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def main() -> int:
    BUILD.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)

    inter = FONTS / "Inter-var.ttf"
    mono = FONTS / "IBMPlexMono-Regular.ttf"
    mono_sb = FONTS / "IBMPlexMono-SemiBold.ttf"
    for f in (inter, mono, mono_sb):
        if not f.exists():
            print(f"missing font {f}", file=sys.stderr)
            return 1

    inter_w2 = subset(inter, BUILD / "inter.woff2")
    mono_w2 = subset(mono, BUILD / "mono.woff2")
    monosb_w2 = subset(mono_sb, BUILD / "monosb.woff2")
    noise = grain_tile()

    src = (HERE / "flux.src.html").read_text()
    fonts_css = f"""@font-face{{font-family:'Inter';src:url(data:font/woff2;base64,{b64(inter_w2)}) format('woff2');font-weight:100 900;font-style:normal;font-display:block}}
@font-face{{font-family:'PlexMono';src:url(data:font/woff2;base64,{b64(mono_w2)}) format('woff2');font-weight:400;font-style:normal;font-display:block}}
@font-face{{font-family:'PlexMono';src:url(data:font/woff2;base64,{b64(monosb_w2)}) format('woff2');font-weight:600;font-style:normal;font-display:block}}
"""
    src = src.replace("/*__FONTS__*/", fonts_css)
    src = src.replace("__NOISE__", b64(noise))
    out = BUILD / "flux.html"
    out.write_text(src)

    manifest = {
        "inter_bytes": inter_w2.stat().st_size,
        "mono_bytes": mono_w2.stat().st_size,
        "monosb_bytes": monosb_w2.stat().st_size,
        "noise_bytes": noise.stat().st_size,
        "html_bytes": out.stat().st_size,
        "html_sha256": __import__("hashlib").sha256(out.read_bytes()).hexdigest(),
        "glyphs": len(GLYPHS),
    }
    (BUILD / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
