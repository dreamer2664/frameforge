#!/usr/bin/env python3
"""Frame finishing: tone mapping, depth of field, bloom, grain, vignette.

All effects are deterministic functions of the frame index, so two renders of
the same timeline produce byte-identical pictures.
"""
from __future__ import annotations

import numpy as np

F32 = np.float32


def aces_filmic(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * d * 0 + c * x + d) + e), 0.0, 1.0)


def box_blur(img, radius):
    if radius < 1:
        return img
    out = img
    for axis in (0, 1):
        n = out.shape[axis]
        r = min(radius, n // 2)
        pad = [(0, 0), (0, 0), (0, 0)]
        pad[axis] = (r, r)
        padded = np.pad(out, pad, mode="edge")
        cs = np.cumsum(padded, axis=axis, dtype=np.float32)
        zero_shape = list(cs.shape)
        zero_shape[axis] = 1
        zero = np.zeros(zero_shape, dtype=F32)
        cs = np.concatenate([zero, cs], axis=axis)
        hi = np.take(cs, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
        lo = np.take(cs, np.arange(0, n), axis=axis)
        out = (hi - lo) / F32(2 * r + 1)
    return out


def blur(img, sigma):
    """Three box passes approximate a Gaussian."""
    r = max(1, int(sigma * 0.72))
    out = img
    for _ in range(3):
        out = box_blur(out, r)
    return out


def depth_of_field(color, depth, focus, aperture=0.9, max_coc=18.0):
    """Depth-aware defocus. `depth` is linear distance in world units."""
    d = np.where(np.isfinite(depth), depth, 1e6)
    coc = np.abs(1.0 / np.maximum(d, 0.05) - 1.0 / max(focus, 0.05)) * aperture
    coc = np.clip(coc * max_coc, 0.0, max_coc)
    far = blur(color, 9.0)
    near = blur(color, 22.0)
    a1 = np.clip(coc / 6.0, 0.0, 1.0)
    a2 = np.clip((coc - 6.0) / 12.0, 0.0, 1.0)
    out = color * (1.0 - a1)[..., None] + far * a1[..., None]
    out = out * (1.0 - a2)[..., None] + near * a2[..., None]
    return out


def bloom(color, threshold=0.85, strength=0.16, radius=26):
    lum = color.max(axis=2)
    mask = np.clip((lum - threshold) / max(1e-6, 1.0 - threshold), 0.0, 1.0)
    b = blur(color * mask[..., None], radius)
    return color + b * strength


def vignette(color, amount=0.36, power=1.6):
    h, w = color.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(F32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    r = np.sqrt(((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2) / 1.4142
    v = np.clip(1.0 - amount * np.power(np.clip(r, 0, 1), power), 0.0, 1.0)
    return color * v[..., None]


def grain(color, amount=0.020, seed=0):
    rng = np.random.default_rng(seed)
    h, w = color.shape[:2]
    n = rng.normal(0.0, 1.0, (h, w)).astype(F32)
    n = (n - n.mean()) / max(n.std(), 1e-6)
    return color + n[..., None] * amount


def chromatic(color, amount=1.1):
    if amount <= 0:
        return color
    h, w = color.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(F32)
    cx, cy = (w - 1) / 2.0, (h - 1) / 2.0
    dx = (xx - cx) / cx
    dy = (yy - cy) / cy
    r = np.clip(xx + dx * amount, 0, w - 1).astype(np.int32)
    c = np.clip(xx - dx * amount, 0, w - 1).astype(np.int32)
    out = color.copy()
    out[:, :, 0] = color[yy.astype(np.int32), r, 0]
    out[:, :, 2] = color[yy.astype(np.int32), c, 2]
    return out


def finish(linear, depth, frame_index, exposure=1.0, focus=7.0, aperture=0.9,
           dof=True, bloom_strength=0.16, grain_amount=0.020, vignette_amount=0.36,
           chroma=1.1, shadow_lift=0.0):
    """Linear HDR frame -> finished 8-bit-ish float image in [0,1]."""
    img = linear * exposure
    if dof:
        img = depth_of_field(img, depth, focus, aperture=aperture)
    img = bloom(img, strength=bloom_strength)
    if shadow_lift:
        img = img + shadow_lift * (1.0 - np.clip(img.mean(axis=2, keepdims=True), 0, 1))
    img = aces_filmic(img)
    img = chromatic(img, chroma)
    img = vignette(img, amount=vignette_amount)
    img = np.clip(img, 0.0, 1.0) ** (1 / 2.2)
    img = grain(img, amount=grain_amount, seed=1000 + frame_index * 7919)
    return np.clip(img, 0.0, 1.0)
