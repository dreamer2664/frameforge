#!/usr/bin/env python3
"""Real extruded letterforms from a variable font, as renderable meshes.

Pipeline: fontTools (variable instancing) -> recorded pen -> flattened contours
-> mapbox_earcut triangulation (holes supported) -> front/back caps + side
walls -> world-space mesh. Everything is deterministic: no random values, the
same font file and axis settings always produce the same vertices.
"""
from __future__ import annotations

import functools
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from fontTools.pens.recordingPen import RecordingPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
import mapbox_earcut as earcut

FONT_DIR = Path(__file__).resolve().parent / "fonts"


# ---------------------------------------------------------------- font loading
@functools.lru_cache(maxsize=32)
def load_font(path: str, wght: float | None = None, wdth: float | None = None):
    """Load a (possibly variable) font, instancing the requested axis values."""
    font = TTFont(path, lazy=False)
    if "fvar" in font:
        limits = {}
        if wght is not None:
            limits["wght"] = float(wght)
        if wdth is not None:
            limits["wdth"] = float(wdth)
        if limits:
            font = instancer.instantiateVariableFont(font, limits, inplace=True)
    return font


def axis_range(path: str, tag: str):
    font = TTFont(path, lazy=False)
    if "fvar" not in font:
        return None
    for axis in font["fvar"].axes:
        if axis.axisTag == tag:
            return (axis.minValue, axis.defaultValue, axis.maxValue)
    return None


# ------------------------------------------------------------ contour extraction
def _quad(out, p0, ctrl, p1, tol=7.0):
    """Append a flattened quadratic Bezier (p0 -> ctrl -> p1) to `out`."""
    d = (np.hypot(ctrl[0] - p0[0], ctrl[1] - p0[1])
         + np.hypot(p1[0] - ctrl[0], p1[1] - ctrl[1]))
    n = int(np.clip(d / max(tol, 1e-3), 2, 28))
    for i in range(1, n + 1):
        t = i / n
        u = 1.0 - t
        out.append((u * u * p0[0] + 2 * u * t * ctrl[0] + t * t * p1[0],
                    u * u * p0[1] + 2 * u * t * ctrl[1] + t * t * p1[1]))


def _flatten_qcurve(points, out, tol=7.0, start=None):
    """Flatten a TrueType qCurveTo.

    `points` is [off-curve..., on-curve].  Consecutive off-curve points imply
    an on-curve point at their midpoint, so the curve is a chain of quadratics:
    p0 -> q1 -> m1, m1 -> q2 -> m2, ... -> qn -> p_end.
    """
    on = points[-1]
    offs = points[:-1]
    if len(offs) == 0:
        out.append((on[0], on[1]))
        return
    if len(offs) == 1:
        _quad(out, start, offs[0], on, tol)
        return
    mids = [((offs[i][0] + offs[i + 1][0]) / 2.0, (offs[i][1] + offs[i + 1][1]) / 2.0)
            for i in range(len(offs) - 1)]
    cur = start
    for i, ctrl in enumerate(offs):
        nxt = mids[i] if i < len(mids) else on
        _quad(out, cur, ctrl, nxt, tol)
        cur = nxt


def _flatten_ccurve(p0, points, out, tol=7.0):
    """Flatten a cubic curve (CFF) into a polyline."""
    c1, c2, p3 = points
    d = (np.hypot(c1[0] - p0[0], c1[1] - p0[1])
         + np.hypot(c2[0] - c1[0], c2[1] - c1[1])
         + np.hypot(p3[0] - c2[0], p3[1] - c2[1]))
    n = int(np.clip(d / max(tol, 1e-3), 3, 28))
    for i in range(1, n + 1):
        t = i / n
        u = 1.0 - t
        x = (u ** 3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t ** 3 * p3[0])
        y = (u ** 3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t ** 3 * p3[1])
        out.append((x, y))


def _contours_from_recording(value, tol=7.0):
    contours = []
    cur = None
    pen = (0.0, 0.0)
    for op, args in value:
        if op == "moveTo":
            if cur and len(cur) > 2:
                contours.append(cur)
            pt = args[0]
            cur = [(pt[0], pt[1])]
            pen = (pt[0], pt[1])
        elif op == "lineTo":
            cur.append((args[0][0], args[0][1]))
            pen = (args[0][0], args[0][1])
        elif op == "qCurveTo":
            pts = [(p[0], p[1]) for p in args]
            _flatten_qcurve(pts, cur, tol, start=pen)
            pen = cur[-1]
        elif op == "curveTo":
            pts = [(p[0], p[1]) for p in args]
            _flatten_ccurve(pen, pts, cur, tol)
            pen = cur[-1]
        elif op == "closePath":
            if cur and len(cur) > 2:
                contours.append(cur)
            cur = None
    if cur and len(cur) > 2:
        contours.append(cur)
    return contours


def glyph_contours(font, ch: str, tol=7.0):
    """Return the flattened contours of one character, in font units."""
    cmap = font.getBestCmap()
    name = cmap.get(ord(ch))
    if name is None:
        raise KeyError(f"glyph missing for {ch!r}")
    pen = RecordingPen()
    font.getGlyphSet()[name].draw(pen)
    return _contours_from_recording(pen.value, tol=tol)


def rdp(points, tol):
    """Ramer-Douglas-Peucker simplification of a closed polyline."""
    pts = np.asarray(points, dtype=np.float64)
    if len(pts) < 3:
        return pts
    keep = np.zeros(len(pts), dtype=bool)
    keep[0] = keep[-1] = True
    stack = [(0, len(pts) - 1)]
    while stack:
        i, j = stack.pop()
        if j <= i + 1:
            continue
        a, b = pts[i], pts[j]
        ab = b - a
        L = np.hypot(ab[0], ab[1])
        seg = pts[i + 1:j]
        if L < 1e-9:
            d = np.hypot(seg[:, 0] - a[0], seg[:, 1] - a[1])
        else:
            d = np.abs(ab[0] * (a[1] - seg[:, 1]) - (a[0] - seg[:, 0]) * ab[1]) / L
        k = int(np.argmax(d))
        if d[k] > tol:
            keep[i + 1 + k] = True
            stack.append((i, i + 1 + k))
            stack.append((i + 1 + k, j))
    return pts[keep]


def _signed_area(pts):
    x = pts[:, 0]
    y = pts[:, 1]
    return 0.5 * float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1)))


# ------------------------------------------------------------------ mesh making
@dataclass
class Mesh:
    verts: np.ndarray  # (N,3) float32
    normals: np.ndarray  # (N,3) float32
    uvs: np.ndarray  # (N,2) float32
    tris: np.ndarray  # (M,3) int32
    groups: dict = field(default_factory=dict)  # name -> (start,count) triangle range

    def merged(self, other: "Mesh", offset: int = 0):
        return Mesh(
            np.concatenate([self.verts, other.verts]),
            np.concatenate([self.normals, other.normals]),
            np.concatenate([self.uvs, other.uvs]),
            np.concatenate([self.tris, other.tris + len(self.verts)]),
        )


def extrude_glyph(contours, depth=1.0, scale=1.0, origin=(0.0, 0.0), smooth=False,
                  cap_tol=4.0, wall_tol=9.0):
    """Extrude one glyph's contours into a closed solid mesh.

    Contours are in font units; the first (largest |area|) is the outer shell,
    every other contour is a hole.
    """
    polys = []
    for c in contours:
        arr = np.asarray(c, dtype=np.float64)
        if len(arr) > 1 and np.allclose(arr[0], arr[-1]):
            arr = arr[:-1]
        polys.append(arr)
    if not polys:
        return Mesh(np.zeros((0, 3), np.float32), np.zeros((0, 3), np.float32),
                    np.zeros((0, 2), np.float32), np.zeros((0, 3), np.int32))

    areas = [_signed_area(p) for p in polys]
    outer_idx = int(np.argmax(np.abs(areas)))
    outer = polys[outer_idx]
    outer_ccw = areas[outer_idx] > 0
    holes = []
    for i, p in enumerate(polys):
        if i == outer_idx:
            continue
        pts = p
        if (_signed_area(pts) > 0) == outer_ccw:  # force holes opposite winding
            pts = pts[::-1]
        holes.append(pts)

    # ---- triangulate the 2D region (outer + holes) with earcut
    if cap_tol:
        outer = rdp(outer, cap_tol)
        holes = [rdp(h, cap_tol) for h in holes]
    verts2d = [outer] + holes
    flat = np.concatenate([p for p in verts2d], axis=0)
    # mapbox_earcut wants the EXCLUSIVE end index of every ring
    ring_ends = np.cumsum([len(p) for p in verts2d]).astype(np.uint32)
    tri = earcut.triangulate_float32(flat.astype(np.float32), ring_ends)
    tri = np.asarray(tri, dtype=np.int64).reshape(-1, 3)
    if len(tri) == 0:
        return Mesh(np.zeros((0, 3), np.float32), np.zeros((0, 3), np.float32),
                    np.zeros((0, 2), np.float32), np.zeros((0, 3), np.int32))

    verts2 = flat[tri].reshape(-1, 2)  # 3 verts per triangle, duplicated
    n_tris = len(tri)
    half = depth * 0.5

    # ---- front cap (z = +half), back cap (z = -half)
    front = np.column_stack([verts2, np.full(len(verts2), half)])
    back = np.column_stack([verts2, np.full(len(verts2), -half)])
    normals_front = np.tile(np.array([0, 0, 1.0]), (n_tris * 3, 1))
    normals_back = np.tile(np.array([0, 0, -1.0]), (n_tris * 3, 1))
    uvs = np.column_stack([verts2[:, 0], verts2[:, 1]]).astype(np.float32)

    tris_front = np.arange(n_tris * 3, dtype=np.int32).reshape(n_tris, 3)
    tris_back = tris_front[:, ::-1] + n_tris * 3

    # ---- side walls for every contour edge
    wall_v = []
    wall_n = []
    wall_uv = []
    wall_tris = []
    base = n_tris * 6  # front cap + back cap vertices come first
    wall_count = 0
    for p in ([rdp(outer, wall_tol)] if wall_tol else [outer]) + \
             ([rdp(h, wall_tol) for h in holes] if wall_tol else holes):
        ccw = _signed_area(p) > 0
        n = len(p)
        for i in range(n):
            a = p[i]
            b = p[(i + 1) % n]
            d = b - a
            ln = np.hypot(d[0], d[1])
            if ln < 1e-9:
                continue
            # outward normal for a CCW outer contour
            nx, ny = (d[1] / ln, -d[0] / ln) if ccw else (-d[1] / ln, d[0] / ln)
            k = base + wall_count * 4
            wall_v.extend([
                (a[0], a[1], -half), (b[0], b[1], -half),
                (a[0], a[1], half), (b[0], b[1], half)])
            wall_n.extend([(nx, ny, 0)] * 4)
            wall_uv.extend([(a[0], a[1]), (b[0], b[1]), (a[0], a[1]), (b[0], b[1])])
            # winding must agree with the outward normal we just computed:
            # a CCW contour needs (a-,b-,b+)/(a-,b+,a+), a CW contour the reverse
            if ccw:
                wall_tris.extend([(k, k + 1, k + 3), (k, k + 3, k + 2)])
            else:
                wall_tris.extend([(k, k + 3, k + 1), (k, k + 2, k + 3)])
            wall_count += 1

    verts = np.concatenate([front, back, np.array(wall_v, dtype=np.float64)
                            if wall_v else np.zeros((0, 3))])
    normals = np.concatenate([normals_front, normals_back,
                               np.array(wall_n, dtype=np.float64) if wall_n else np.zeros((0, 3))])
    uvs_all = np.concatenate([uvs, uvs, np.array(wall_uv, dtype=np.float64)
                              if wall_uv else np.zeros((0, 2))])
    tris_all = np.concatenate([tris_front, tris_back,
                               np.array(wall_tris, dtype=np.int32) if wall_tris
                               else np.zeros((0, 3), np.int32)])

    # transform: scale + origin shift (x right, y up, z out of the face)
    verts = verts * np.array([scale, scale, 1.0])
    verts[:, 0] += origin[0]
    verts[:, 1] += origin[1]

    return Mesh(verts.astype(np.float32), normals.astype(np.float32),
                uvs_all.astype(np.float32), tris_all.astype(np.int32))


def text_mesh(text, font_path, wght=700, wdth=100, depth=0.12, cap_height=None,
              tracking=0.0, tol=7.0, scale_units=None):
    """Build a mesh of a whole text run. Returns (mesh, advance_width)."""
    font = load_font(font_path, wght=wght, wdth=wdth)
    upem = font["head"].unitsPerEm
    # cap height from the 'H' glyph
    hcont = glyph_contours(font, "H", tol=tol)
    harr = np.asarray(hcont[0], dtype=np.float64)
    cap = float(harr[:, 1].max() - harr[:, 1].min())
    sc = (cap_height / cap) if cap_height else (scale_units or 1.0 / upem)
    meshes = []
    pen_x = 0.0
    for ch in text:
        if ch == " ":
            pen_x += 0.28 * upem * sc
            continue
        contours = glyph_contours(font, ch, tol=tol)
        if not contours:
            pen_x += 0.3 * upem * sc
            continue
        m = extrude_glyph(contours, depth=depth * sc * upem / 1.0 if False else depth,
                          scale=sc, origin=(pen_x, 0.0))
        meshes.append(m)
        adv = font["hmtx"][font.getBestCmap()[ord(ch)]][0] * sc
        pen_x += adv + tracking * sc
    if not meshes:
        return Mesh(np.zeros((0, 3), np.float32), np.zeros((0, 3), np.float32),
                    np.zeros((0, 2), np.float32), np.zeros((0, 3), np.int32)), 0.0
    total = meshes[0]
    for m in meshes[1:]:
        total = total.merged(m)
    # normalise so the baseline sits at y = 0
    miny = float(total.verts[:, 1].min())
    total.verts[:, 1] -= miny
    total.verts[:, 0] -= float(total.verts[:, 0].min())
    return total, pen_x


if __name__ == "__main__":
    import sys
    p = FONT_DIR / "Archivo-var.ttf"
    print("axis wght:", axis_range(str(p), "wght"))
    print("axis wdth:", axis_range(str(p), "wdth"))
    m, w = text_mesh("KINETIC", str(p), wght=700, wdth=100, cap_height=1.0)
    print("verts", m.verts.shape, "tris", m.tris.shape, "width", w)
    print("bbox", m.verts.min(axis=0), m.verts.max(axis=0))
