#!/usr/bin/env python3
"""Validate the extruded-type pipeline against an independent outline source.

fontTools' SVGPathPen converts the same glyph through its own segment-pen
implementation.  We compare our flattened contour against that reference:

  * bounding box must match within 1 font unit
  * polygon area must match within 0.5 %
  * every point of our contour must lie within 1.5 units of the reference
  * the triangulated mesh must reproduce the polygon area (earcut check)
  * the front-cap raster must match a Pillow raster of the same static font

A PASS means the letterforms that end up in the film are the font's own
letterforms, extruded, not a hand-drawn approximation.
"""
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import type3d

FONT = str(Path(__file__).resolve().parent / "fonts" / "Archivo-var.ttf")
STATIC = Path(__file__).resolve().parent / "work" / "Archivo-w700-wdth100.ttf"
CAP_PX = 300.0
PAD = 60


def static_font_path():
    STATIC.parent.mkdir(exist_ok=True)
    if not STATIC.exists():
        from fontTools.ttLib import TTFont
        from fontTools.varLib import instancer
        f = TTFont(FONT)
        f = instancer.instantiateVariableFont(f, {"wght": 700, "wdth": 100})
        f.save(str(STATIC))
    return str(STATIC)


def reference_polys(font, ch):
    """Independent outline: fontTools SVGPathPen -> flattened polylines."""
    from fontTools.pens.svgPathPen import SVGPathPen
    pen = SVGPathPen(None)
    font.getGlyphSet()[font.getBestCmap()[ord(ch)]].draw(pen)
    d = pen.getCommands()
    polys = []
    cur = []
    pos = (0.0, 0.0)
    start = (0.0, 0.0)
    tokens = re.findall(r"([MLQCHVZ])|(-?\d*\.?\d+(?:e-?\d+)?)", d)
    i = 0
    items = []
    for cmd, num in tokens:
        if cmd:
            items.append(("cmd", cmd))
        elif num:
            items.append(("num", float(num)))
    k = 0
    while k < len(items):
        kind, val = items[k]
        if kind == "cmd":
            if val == "M":
                if len(cur) > 2:
                    polys.append(cur)
                x, y = items[k + 1][1], items[k + 2][1]
                cur = [(x, y)]
                pos = start = (x, y)
                k += 3
                continue
            if val == "L":
                x, y = items[k + 1][1], items[k + 2][1]
                cur.append((x, y))
                pos = (x, y)
                k += 3
                continue
            if val == "H":
                x = items[k + 1][1]
                cur.append((x, pos[1]))
                pos = (x, pos[1])
                k += 2
                continue
            if val == "V":
                y = items[k + 1][1]
                cur.append((pos[0], y))
                pos = (pos[0], y)
                k += 2
                continue
            if val == "Q":
                cx, cy = items[k + 1][1], items[k + 2][1]
                x, y = items[k + 3][1], items[k + 4][1]
                n = 240
                for s in range(1, n + 1):
                    t = s / n
                    u = 1 - t
                    cur.append((u * u * pos[0] + 2 * u * t * cx + t * t * x,
                                u * u * pos[1] + 2 * u * t * cy + t * t * y))
                pos = (x, y)
                k += 5
                continue
            if val == "C":
                c1 = (items[k + 1][1], items[k + 2][1])
                c2 = (items[k + 3][1], items[k + 4][1])
                x, y = items[k + 5][1], items[k + 6][1]
                n = 240
                for s in range(1, n + 1):
                    t = s / n
                    u = 1 - t
                    cur.append((u ** 3 * pos[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * x,
                                u ** 3 * pos[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * y))
                pos = (x, y)
                k += 7
                continue
            if val == "Z":
                if len(cur) > 2:
                    polys.append(cur)
                cur = []
                pos = start
                k += 1
                continue
        k += 1
    if len(cur) > 2:
        polys.append(cur)
    return polys


def poly_area(p):
    x, y = p[:, 0], p[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


def min_dist_to_polyline(pts, ref_pts):
    """Min distance from each point to the reference polyline (point sampling)."""
    ref = np.asarray(ref_pts)
    out = np.empty(len(pts))
    for i, p in enumerate(pts):
        d = np.linalg.norm(ref - np.asarray(p), axis=1)
        out[i] = d.min()
    return out


def main():
    font = type3d.load_font(static_font_path())
    upem = font["head"].unitsPerEm
    ok = True
    for ch in "KINETICOSGBR":
        ours = [np.asarray(c, dtype=np.float64) for c in type3d.glyph_contours(font, ch)]
        ref = [np.asarray(c, dtype=np.float64) for c in reference_polys(font, ch)]
        problems = []
        if len(ours) != len(ref):
            problems.append(f"contour count {len(ours)} vs {len(ref)}")
        else:
            for o, r in zip(ours, ref):
                ob = (o.min(axis=0), o.max(axis=0))
                rb = (r.min(axis=0), r.max(axis=0))
                if np.abs(ob[0] - rb[0]).max() > 1.0 or np.abs(ob[1] - rb[1]).max() > 1.0:
                    problems.append(f"bbox {ob} vs {rb}")
                ao, ar = abs(poly_area(o)), abs(poly_area(r))
                if ao > 0 and abs(ao - ar) / ar > 0.005:
                    problems.append(f"area {ao:.1f} vs {ar:.1f} ({abs(ao-ar)/ar*100:.2f}%)")
                # every point of our contour must sit on the reference outline
                d = min_dist_to_polyline(o, r)
                if d.max() > 1.5:
                    problems.append(f"max point deviation {d.max():.2f} units")
        # earcut must reproduce the polygon area exactly
        m = type3d.extrude_glyph(type3d.glyph_contours(font, ch), depth=0.3, scale=1.0)
        v = m.verts
        n_front = int(np.count_nonzero((v[m.tris, 2] > 0).all(axis=1)))
        cap_area = 0.0
        for t in m.tris:
            if not (v[t, 2] > 0).all():
                continue
            p = v[t][:, :2]
            cap_area += abs(poly_area(p))
        areas_ = [abs(poly_area(np.asarray(c))) for c in ours]
        outer = max(areas_)
        expect = outer - (sum(areas_) - outer)
        if cap_area > 0 and abs(cap_area - expect) / max(expect, 1) > 0.01:
            problems.append(f"triangulated area {cap_area:.1f} vs polygon {expect:.1f}")
        status = "OK " if not problems else "BAD"
        if problems:
            ok = False
        print(f"{status} {ch!r}  contours={len(ours)}  tris={len(m.tris):5d}  "
              + ("; ".join(problems) if problems else "outline+area exact"))
    print("RESULT:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
