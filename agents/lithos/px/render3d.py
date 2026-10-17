#!/usr/bin/env python3
"""A small, film-scoped 3D rasteriser (numpy only).

Deliberately not a general engine: it renders exactly what this film needs --
perspective camera, z-buffered solid meshes with real extruded letterforms,
directional/point lighting with one shadow map, haze, tone-mapped output,
depth-of-field, bloom and grain. Everything is frame-time deterministic.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np

F32 = np.float32


# ------------------------------------------------------------------ math helpers
def normalize(v):
    v = np.asarray(v, dtype=F32)
    n = np.linalg.norm(v, axis=-1, keepdims=True)
    out = v / np.maximum(n, 1e-9)
    bad = (n < 1e-6).reshape(-1)
    if np.any(bad):
        out = np.array(out, copy=True)
        out[bad] = np.array([0.0, 0.0, 1.0], dtype=F32)
    return out


def look_at(eye, target, up=(0.0, 1.0, 0.0)):
    eye = np.asarray(eye, dtype=F32)
    target = np.asarray(target, dtype=F32)
    up = np.asarray(up, dtype=F32)
    f = normalize(target - eye)
    s = normalize(np.cross(f, up))
    u = np.cross(s, f)
    m = np.eye(4, dtype=F32)
    m[0, :3] = s
    m[1, :3] = u
    m[2, :3] = -f
    m[0, 3] = -float(s @ eye)
    m[1, 3] = -float(u @ eye)
    # third row is -f, so the translation is -(-f).eye = f.eye
    m[2, 3] = float(f @ eye)
    return m


def perspective(fov_deg, aspect, near, far):
    f = 1.0 / math.tan(math.radians(fov_deg) * 0.5)
    m = np.zeros((4, 4), dtype=F32)
    m[0, 0] = f / aspect
    m[1, 1] = f
    m[2, 2] = (far + near) / (near - far)
    m[2, 3] = (2 * far * near) / (near - far)
    m[3, 2] = -1.0
    return m


def ortho(l, r, b, t, n, f):
    m = np.eye(4, dtype=F32)
    m[0, 0] = 2.0 / (r - l)
    m[1, 1] = 2.0 / (t - b)
    m[2, 2] = -2.0 / (f - n)
    m[0, 3] = -(r + l) / (r - l)
    m[1, 3] = -(t + b) / (t - b)
    m[2, 3] = -(f + n) / (f - n)
    return m


def mat4_mul(a, b):
    return (a @ b).astype(F32)


def xform(m, verts):
    """Apply a 4x4 matrix to (N,3) vertices."""
    v = np.concatenate([verts, np.ones((len(verts), 1), dtype=F32)], axis=1)
    return (m @ v.T).T[:, :3]


# ------------------------------------------------------------------ scene types
@dataclass
class Material:
    base: tuple = (0.6, 0.6, 0.6)
    spec: float = 0.05
    shininess: float = 24.0
    emissive: tuple = (0.0, 0.0, 0.0)
    texture: np.ndarray | None = None  # (H,W,3) or (H,W,4) float32
    texture_uv: tuple = (1.0, 1.0)  # uv scale
    texture_offset: tuple = (0.0, 0.0)
    double_sided: bool = False
    alpha: float = 1.0
    blend: bool = False  # alpha blended (no depth write)
    additive: bool = False  # additive light writing


@dataclass
class Light:
    kind: str = "directional"  # directional | point
    color: tuple = (1.0, 1.0, 1.0)
    intensity: float = 1.0
    direction: tuple = (0.0, -1.0, 0.0)  # for directional (pointing FROM light)
    position: tuple = (0.0, 0.0, 0.0)  # for point
    cast_shadow: bool = False
    shadow_extent: float = 14.0
    shadow_center: tuple = (0.0, 0.0, 0.0)
    shadow_res: int = 1024


@dataclass
class Scene:
    meshes: list = field(default_factory=list)  # (verts, normals, uvs, tris, material)
    lights: list = field(default_factory=list)
    ambient_sky: tuple = (0.05, 0.06, 0.09)
    ambient_ground: tuple = (0.03, 0.025, 0.02)
    ambient_intensity: float = 1.0
    fog_color: tuple = (0.02, 0.025, 0.035)
    fog_density: float = 0.012
    fog_height: float = 0.0


@dataclass
class Camera:
    eye: tuple = (0.0, 0.0, 6.0)
    target: tuple = (0.0, 0.0, 0.0)
    up: tuple = (0.0, 1.0, 0.0)
    fov: float = 38.0
    near: float = 0.05
    far: float = 400.0
    shift: tuple = (0.0, 0.0)  # lens shift in NDC (for framing without rotating)

    def matrices(self, width, height):
        view = look_at(self.eye, self.target, self.up)
        proj = perspective(self.fov, width / height, self.near, self.far)
        proj = proj.copy()
        proj[0, 2] += self.shift[0]
        proj[1, 2] += self.shift[1]
        return view, proj


# ------------------------------------------------------------------ rasteriser
class Raster:
    """Z-buffered triangle rasteriser with perspective-correct attributes."""

    def __init__(self, width, height):
        self.w = width
        self.h = height
        self.color = np.zeros((height, width, 3), dtype=F32)
        self.depth = np.full((height, width), np.inf, dtype=F32)
        self.world = np.zeros((height, width, 3), dtype=F32)
        self.normal = np.zeros((height, width, 3), dtype=F32)
        self.uv = np.zeros((height, width, 2), dtype=F32)
        self.obj = np.full((height, width), -1, dtype=np.int32)

    # ---- shadow pass: depth only, orthographic
    def shadow_pass(self, meshes, view, proj, res):
        depth = np.full((res, res), np.inf, dtype=F32)
        for mi, mesh in enumerate(meshes):
            verts, normals, uvs, tris, mat = mesh[0], mesh[1], mesh[2], mesh[3], mesh[4]
            cast = mesh[5] if len(mesh) > 5 else True
            if len(tris) == 0 or not cast:
                continue
            vc = xform(view, verts)
            pc = xform(proj, vc)
            w = -vc[:, 2]  # camera-space depth is the clip-space w
            sx = (pc[:, 0] / np.maximum(w, 1e-6) * 0.5 + 0.5) * res
            sy = (0.5 - pc[:, 1] / np.maximum(w, 1e-6) * 0.5) * res
            for t in tris:
                if w[t[0]] <= 0.01 or w[t[1]] <= 0.01 or w[t[2]] <= 0.01:
                    continue
                p0 = (sx[t[0]], sy[t[0]], w[t[0]])
                p1 = (sx[t[1]], sy[t[1]], w[t[1]])
                p2 = (sx[t[2]], sy[t[2]], w[t[2]])
                x0 = max(0, int(min(p0[0], p1[0], p2[0])))
                x1 = min(res - 1, int(max(p0[0], p1[0], p2[0])) + 1)
                y0 = max(0, int(min(p0[1], p1[1], p2[1])))
                y1 = min(res - 1, int(max(p0[1], p1[1], p2[1])) + 1)
                if x1 < x0 or y1 < y0:
                    continue
                xs = np.arange(x0, x1 + 1, dtype=F32)
                ys = np.arange(y0, y1 + 1, dtype=F32)
                gx, gy = np.meshgrid(xs, ys)
                d = ((p1[1] - p2[1]) * (p0[0] - p2[0]) + (p2[0] - p1[0]) * (p0[1] - p2[1]))
                if abs(d) < 1e-9:
                    continue
                l0 = ((p1[1] - p2[1]) * (gx - p2[0]) + (p2[0] - p1[0]) * (gy - p2[1])) / d
                l1 = ((p2[1] - p0[1]) * (gx - p2[0]) + (p0[0] - p2[0]) * (gy - p2[1])) / d
                l2 = 1.0 - l0 - l1
                inside = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
                if not inside.any():
                    continue
                zz = l0 * p0[2] + l1 * p1[2] + l2 * p2[2]
                sub = depth[y0:y1 + 1, x0:x1 + 1]
                upd = inside & (zz < sub)
                sub[upd] = zz[upd]
        return depth

    # ---- main pass
    def draw(self, meshes, view, proj, width, height, lights, scene, shadows,
             jitter=(0.0, 0.0)):
        W, H = self.w, self.h
        for mi, mesh in enumerate(meshes):
            verts, normals, uvs, tris, mat = mesh[0], mesh[1], mesh[2], mesh[3], mesh[4]
            if len(tris) == 0:
                continue
            vc = xform(view, verts)          # camera space
            pc = xform(proj, vc)
            w = -vc[:, 2]  # camera-space depth == clip-space w
            with np.errstate(divide="ignore", invalid="ignore"):
                ndc_x = pc[:, 0] / np.where(np.abs(w) > 1e-6, w, 1e-6)
                ndc_y = pc[:, 1] / np.where(np.abs(w) > 1e-6, w, 1e-6)
            sx = (ndc_x * 0.5 + 0.5) * W + jitter[0]
            sy = (0.5 - ndc_y * 0.5) * H + jitter[1]
            iw = 1.0 / np.where(np.abs(w) > 1e-6, w, 1e-6)
            for t in tris:
                wv = w[t]
                if wv[0] <= self._near or wv[1] <= self._near or wv[2] <= self._near:
                    # clip the triangle against the near plane
                    poly = self._clip_near(t, vc)
                    if poly is None:
                        continue
                    for tri in poly:
                        self._raster_tri(tri, verts, normals, uvs, vc, w, sx, sy, iw,
                                         mi, mat, lights, scene, shadows, W, H)
                    continue
                self._raster_tri(t, verts, normals, uvs, vc, w, sx, sy, iw,
                                 mi, mat, lights, scene, shadows, W, H)

    def _clip_near(self, tri, vc):
        near = self._near
        pts = []
        for idx in tri:
            x, y, z = vc[idx]
            pts.append((idx, x, y, z, -z))
        out = []
        for i in range(3):
            a = pts[i]
            b = pts[(i + 1) % 3]
            ain = a[4] > near
            bin_ = b[4] > near
            if ain:
                out.append(a)
            if ain != bin_:
                t = (near - a[4]) / (b[4] - a[4])
                out.append((a[0], a[1] + (b[1] - a[1]) * t, a[2] + (b[2] - a[2]) * t,
                            a[3] + (b[3] - a[3]) * t, near))
        if len(out) < 3:
            return None
        tris = []
        for i in range(1, len(out) - 1):
            tris.append([out[0][0], out[i][0], out[i + 1][0]])
        return tris

    def _raster_tri(self, tri, verts, normals, uvs, vc, w, sx, sy, iw,
                    mi, mat, lights, scene, shadows, W, H):
        i0, i1, i2 = tri
        x0, x1, x2 = sx[i0], sx[i1], sx[i2]
        y0, y1, y2 = sy[i0], sy[i1], sy[i2]
        minx = max(0, int(min(x0, x1, x2)))
        maxx = min(W - 1, int(max(x0, x1, x2)) + 1)
        miny = max(0, int(min(y0, y1, y2)))
        maxy = min(H - 1, int(max(y0, y1, y2)) + 1)
        if maxx < minx or maxy < miny:
            return
        # backface cull
        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        if abs(area) < 1e-9:
            return
        # screen y points down, so a front-facing triangle (world normal toward
        # the camera) has a NEGATIVE signed area here
        if area >= 0 and not mat.double_sided:
            return
        # keep the SIGNED area: the edge functions below must use the same
        # orientation as the triangle, otherwise the inside test inverts
        xs = np.arange(minx, maxx + 1, dtype=F32)
        ys = np.arange(miny, maxy + 1, dtype=F32)
        gx, gy = np.meshgrid(xs, ys)
        l0 = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / area
        l1 = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / area
        l2 = 1.0 - l0 - l1
        inside = (l0 >= -1e-6) & (l1 >= -1e-6) & (l2 >= -1e-6)
        if not inside.any():
            return
        iw0, iw1, iw2 = iw[i0], iw[i1], iw[i2]
        wsum = l0 * iw0 + l1 * iw1 + l2 * iw2
        zz = 1.0 / np.maximum(wsum, 1e-9)  # perspective-correct depth
        dbuf = self.depth[miny:maxy + 1, minx:maxx + 1]
        upd = inside & (zz < dbuf) & (wsum > 1e-6)
        if not upd.any():
            return
        l0u, l1u, l2u = l0[upd], l1[upd], l2[upd]
        iws = wsum[upd]
        pw0, pw1, pw2 = l0u * iw0, l1u * iw1, l2u * iw2
        # world position
        wp = (pw0[:, None] * verts[i0] + pw1[:, None] * verts[i1]
              + pw2[:, None] * verts[i2]) / iws[:, None]
        nrm = (pw0[:, None] * normals[i0] + pw1[:, None] * normals[i1]
               + pw2[:, None] * normals[i2]) / iws[:, None]
        uv = (pw0[:, None] * uvs[i0] + pw1[:, None] * uvs[i1]
              + pw2[:, None] * uvs[i2]) / iws[:, None]
        if not (mat.additive or mat.blend):
            # transparent geometry must never occlude what is behind it
            dbuf[upd] = zz[upd]
        self.world[miny:maxy + 1, minx:maxx + 1][upd] = wp
        self.normal[miny:maxy + 1, minx:maxx + 1][upd] = nrm
        self.uv[miny:maxy + 1, minx:maxx + 1][upd] = uv
        self.obj[miny:maxy + 1, minx:maxx + 1][upd] = mi
        # shading
        col = self._shade(wp, nrm, uv, mat, lights, scene, shadows, mi)
        cbuf = self.color[miny:maxy + 1, minx:maxx + 1]
        if mat.additive:
            cbuf[upd] = cbuf[upd] + col[:, :3] * col[:, 3:4]
        elif mat.blend:
            a = col[:, 3:4]
            cbuf[upd] = cbuf[upd] * (1.0 - a) + col[:, :3] * a
        else:
            cbuf[upd] = col[:, :3]

    def _shade(self, wp, nrm, uv, mat, lights, scene, shadows, mi):
        n = normalize(nrm)
        eye = np.asarray(self._eye, dtype=F32)
        view = normalize(eye - wp)
        base = np.asarray(mat.base, dtype=F32)
        out = np.zeros((len(wp), 4), dtype=F32)
        # hemisphere ambient
        hemi = 0.5 + 0.5 * n[:, 1]
        amb = (np.asarray(scene.ambient_ground, dtype=F32)
               + (np.asarray(scene.ambient_sky, dtype=F32)
                  - np.asarray(scene.ambient_ground, dtype=F32)) * hemi[:, None])
        out[:, :3] = amb * scene.ambient_intensity * base
        for li, light in enumerate(lights):
            if light.kind == "directional":
                L = normalize(np.asarray(light.direction, dtype=F32))[None, :]
                ld = np.full(len(wp), 1e6, dtype=F32)
            else:
                lp = np.asarray(light.position, dtype=F32)
                delta = lp - wp
                ld = np.linalg.norm(delta, axis=1)
                L = delta / np.maximum(ld, 1e-6)[:, None]
            ndl = np.sum(n * L, axis=1)
            diff = np.clip(ndl, 0.0, None)
            if light.cast_shadow and shadows is not None:
                sm = shadows[li]
                diff = diff * sm["factor"](wp, n, light)
            hv = normalize(L + view)
            ndh = np.clip(np.sum(n * hv, axis=1), 0.0, None)
            spec = np.power(ndh, mat.shininess) * mat.spec * diff
            lc = np.asarray(light.color, dtype=F32) * light.intensity
            if light.kind == "point":
                atten = 1.0 / (1.0 + 0.06 * ld + 0.006 * ld * ld)
                lc = lc * atten[:, None]
            out[:, :3] += (diff[:, None] * lc) * base
            out[:, :3] += spec[:, None] * lc
        em = np.asarray(mat.emissive, dtype=F32)
        out[:, :3] += em[None, :]
        out[:, 3] = 1.0
        if mat.texture is not None:
            tex = mat.texture
            th, tw = tex.shape[:2]
            u = (uv[:, 0] * mat.texture_uv[0] + mat.texture_offset[0]) % 1.0
            v = (uv[:, 1] * mat.texture_uv[1] + mat.texture_offset[1]) % 1.0
            xi = np.clip((u * tw).astype(np.int32), 0, tw - 1)
            yi = np.clip((v * th).astype(np.int32), 0, th - 1)
            t = tex[yi, xi]
            if t.shape[1] == 4:
                if mat.additive:
                    # an additive surface carries its own colour: the texture
                    # is the light, not a multiplier of it
                    out[:, :3] = out[:, :3] + t[:, :3]
                else:
                    out[:, :3] *= t[:, :3]
                out[:, 3] = out[:, 3] * t[:, 3]
            else:
                if mat.additive:
                    out[:, :3] = out[:, :3] + t
                else:
                    out[:, :3] *= t
        out[:, 3] = out[:, 3] * mat.alpha
        return out


# ------------------------------------------------------------------ scene render
def build_shadow(light: Light, scene: Scene, meshes, res=1024):
    if light.kind != "directional":
        return None
    d = normalize(np.asarray(light.direction, dtype=F32))
    c = np.asarray(light.shadow_center, dtype=F32)
    eye = c + d * 30.0
    view = look_at(eye, c, (0.0, 1.0, 0.0) if abs(d[1]) < 0.9 else (0.0, 0.0, 1.0))
    e = light.shadow_extent
    proj = ortho(-e, e, -e, e, 0.1, 60.0)
    r = Raster(res, res)
    r._near = 0.05
    r.shadow_pass(meshes, view, proj, res)
    sdepth = r.depth
    mvp = mat4_mul(proj, view)
    return {"depth": sdepth, "mvp": mvp, "res": res, "bias": 0.02,
            "extent": light.shadow_extent, "view": view}

    # (shadow sampling closure is attached by make_shadow_factor)


def make_shadow_factor(sh):
    depth = sh["depth"]
    mvp = sh["mvp"]
    res = sh["res"]
    bias = sh["bias"]
    extent = sh["extent"]
    view = sh["view"]

    def factor(wp, n, light):
        d = normalize(np.asarray(light.direction, dtype=F32))
        ndl = np.clip(np.sum(n * d, axis=1), 0.0, None)
        texel = 2.0 * extent / res
        wp = wp + n * (texel * 2.6 / np.maximum(ndl, 0.20))[:, None]
        p = xform(mvp, wp)
        x = p[:, 0] * 0.5 + 0.5
        y = 0.5 - p[:, 1] * 0.5
        xi = np.clip((x * res).astype(np.int32), 0, res - 1)
        yi = np.clip((y * res).astype(np.int32), 0, res - 1)
        cur = -xform(view, wp)[:, 2]
        b = bias * (0.6 + 3.0 * (1.0 - ndl))
        step = 2  # PCF radius in shadow-map texels
        ref = depth[yi, xi]
        lit = (cur - b) <= ref
        # 3x3 PCF over a 2-texel stride (9 taps, same soft edge as the old 5x5)
        acc = lit.astype(F32)
        cnt = 1.0
        for dx in (-2, 0, 2):
            for dy in (-2, 0, 2):
                if dx == 0 and dy == 0:
                    continue
                x2 = np.clip(xi + dx, 0, res - 1)
                y2 = np.clip(yi + dy, 0, res - 1)
                r2 = depth[y2, x2]
                acc += ((cur - b) <= r2).astype(F32)
                cnt += 1.0
        return acc / cnt

    return factor


def render(scene: Scene, camera: Camera, width: int, height: int, subframes=1,
           sub_time=0.0, sub_shutter=0.0, exposure=1.0, shadow_res=1024,
           jitter=(0.0, 0.0)):
    """Render one frame. Returns (linear HDR colour, linear depth)."""
    r = Raster(width, height)
    r._near = camera.near
    r._eye = np.asarray(camera.eye, dtype=F32)
    view, proj = camera.matrices(width, height)
    shadows = []
    for light in scene.lights:
        if light.cast_shadow and light.kind == "directional":
            sh = build_shadow(light, scene, scene.meshes, res=shadow_res)
            sh["factor"] = make_shadow_factor(sh)
            shadows.append(sh)
        else:
            shadows.append(None)
    r.draw(scene.meshes, view, proj, width, height, scene.lights, scene, shadows,
           jitter=jitter)
    return r


# ------------------------------------------------------------------ post
def aces_filmic(x):
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    return np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0.0, 1.0)


def box_blur(img, radius):
    """Fast separable box blur with numpy cumulative sums (periodic edges)."""
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
        zero = np.zeros_like(np.take(cs, [0], axis=axis))
        cs = np.concatenate([zero, cs], axis=axis)
        hi = np.take(cs, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
        lo = np.take(cs, np.arange(0, n), axis=axis)
        out = (hi - lo) / np.float32(2 * r + 1)
    return out


def gaussianish(img, sigma):
    """Three box passes approximate a Gaussian closely enough for bloom."""
    r = max(1, int(sigma * 0.9))
    out = img
    for _ in range(3):
        out = box_blur(out, r)
    return out
