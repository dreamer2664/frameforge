"""Grade pass: shadow-denoise (no OIDN in Debian Blender), bloom, vignette, grain, contrast.
python3 grade.py  (reads work/frames -> writes work/graded)
"""
import numpy as np
from pathlib import Path
from PIL import Image, ImageFilter

ROOT = Path('/home/user/work/frameforge/agents/lithos/reel')
SRC = Path('/tmp/reel-frames')
DST = Path('/tmp/reel-graded')
DST.mkdir(parents=True, exist_ok=True)


def grade(im):
    a = np.asarray(im).astype(np.float32)
    luma = a @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    # 1) shadow-weighted denoise: blend toward a light blur where dark
    blur = np.asarray(im.filter(ImageFilter.GaussianBlur(1.7))).astype(np.float32)
    w = np.clip(1.0 - luma / 110.0, 0, 1)[:, :, None] * 0.55
    a = a * (1 - w) + blur * w
    # 2) bloom around the screen highlights
    hot = np.clip((luma - 195) / 60.0, 0, 1)
    hot_im = Image.fromarray((hot * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(26))
    bloom = np.asarray(hot_im).astype(np.float32) / 255.0
    a += bloom[:, :, None] * np.array([54, 58, 70], dtype=np.float32)
    # 3) vignette
    h, w_ = luma.shape
    yy, xx = np.mgrid[0:h, 0:w_]
    r = np.sqrt(((xx - w_ / 2) / (w_ / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    a *= (1 - 0.16 * np.clip(r, 0, 1.4) ** 2.1)[:, :, None]
    # 4) gentle S-contrast
    x = np.clip(a / 255.0, 0, 1)
    x = x * x * (3 - 2 * x) * 0.32 + x * 0.68
    a = x * 255.0
    # 5) grain
    rng = np.random.default_rng(3)
    a += rng.standard_normal(luma.shape)[:, :, None] * 2.0
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


files = sorted(SRC.glob('*.jpg'))
for i, f in enumerate(files):
    grade(Image.open(f).convert('RGB')).save(DST / f.name)
    if i % 40 == 0:
        print('graded', i, flush=True)
print('GRADE_OK', len(files))
