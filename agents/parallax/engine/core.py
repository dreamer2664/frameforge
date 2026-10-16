"""parallax engine core — purpose-built deterministic 3D rasteriser (numpy).

Not a general engine: exactly what the film needs — extruded glyph solids,
boxes/portal gates, ground plane, emissive textured plates, one moving point
light + cool fill, shadow map, exponential fog, glow, grain. Flat-shaded
mineral look; z-buffer; near-plane clipping; deterministic frame-time.
"""
import hashlib
import math
import pickle
from pathlib import Path

import numpy as np
import uharfbuzz as hb
from fontTools.ttLib import TTFont
from mapbox_earcut import triangulate_float32 as earcut
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------- math / easing
def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def lerp(a, b, p):
    return a + (b - a) * p

def smoothstep(p):
    p = clamp(p)
    return p * p * (3 - 2 * p)

def ease_out_cubic(p):
    p = clamp(p)
    return 1 - (1 - p) ** 3

def ease_in_out(p):
    p = clamp(p)
    return p * p * p * (p * (p * 6 - 15) + 10)

def srgb_to_linear(c):
    c = np.asarray(c, dtype=np.float64) / 255.0
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def linear_to_srgb_u8(c):
    c = np.clip(c, 0.0, 1.0)
    s = np.where(c <= 0.0031308, c * 12.92, 1.055 * np.power(c, 1 / 2.4) - 0.055)
    return (s * 255.0 + 0.5).astype(np.uint8)

def norm(v):
    v = np.asarray(v, dtype=np.float64)
    n = np.linalg.norm(v)
    return v / n if n > 1e-12 else v

# ---------------------------------------------------------------- camera
class Camera:
    def __init__(self, pos, target, fov=38.0, roll=0.0, near=0.05):
        self.pos = np.asarray(pos, dtype=np.float64)
        fwd = norm(np.asarray(target, dtype=np.float64) - self.pos)
        up = np.array([0.0, 1.0, 0.0])
        right = norm(np.cross(fwd, up))
        if roll:
            c, s = math.cos(roll), math.sin(roll)
            up2 = up * c + right * s
            right = norm(np.cross(fwd, up2))
        up = np.cross(right, fwd)
        self.R = np.stack([right, up, fwd])          # rows: cam axes in world
        self.fov = fov
        self.near = near

    def to_cam(self, pts):                            # (N,3) world -> cam
        return (pts - self.pos) @ self.R.T

    def project(self, cam, W, H):
        f = (H * 0.5) / math.tan(math.radians(self.fov) * 0.5)
        z = np.maximum(cam[:, 2], 1e-6)
        x = W * 0.5 + f * cam[:, 0] / z
        y = H * 0.5 - f * cam[:, 1] / z
        return np.stack([x, y], axis=1), f

# ---------------------------------------------------------------- glyph meshes
_FONT_CACHE = {}

def _font_objs(path):
    if path not in _FONT_CACHE:
        blob = hb.Blob.from_file_path(path)
        face = hb.Face(blob)
        hbf = hb.Font(face)
        ttf = TTFont(path)
        _FONT_CACHE[path] = (hbf, face, ttf.getGlyphSet(), ttf["head"].unitsPerEm)
    return _FONT_CACHE[path]

class _RecPen:
    def __init__(self):
        self.ops = []
    def moveTo(self, p): self.ops.append(("m", p))
    def lineTo(self, p): self.ops.append(("l", p))
    def curveTo(self, *pts): self.ops.append(("c", pts))
    def qCurveTo(self, *pts): self.ops.append(("q", pts))
    def closePath(self): self.ops.append(("z", None))
    def endPath(self): self.ops.append(("z", None))

def _flat_q(pts, n=10):
    """flatten quadratic/cubic chain: pts = control points + end point."""
    out = []
    for i in range(1, n + 1):
        t = i / n
        # de Casteljau for arbitrary degree
        P = [np.asarray(p, dtype=np.float64) for p in pts]
        while len(P) > 1:
            P = [(1 - t) * P[k] + t * P[k + 1] for k in range(len(P) - 1)]
        out.append(tuple(P[0]))
    return out

def _glyph_rings(glyphset, gname):
    pen = _RecPen()
    glyphset[gname].draw(pen)
    rings, cur, start = [], [], None
    for kind, arg in pen.ops:
        if kind == "m":
            cur = [tuple(arg)]; start = tuple(arg)
        elif kind == "l":
            cur.append(tuple(arg))
        elif kind == "c":
            cur.extend(_flat_q([cur[-1]] + list(arg), 10))
        elif kind == "q":
            if len(arg) > 1:
                cur.extend(_flat_q([cur[-1]] + list(arg), 10))
            else:  # true quadratic with implicit on-curve: treat control+end
                cur.extend(_flat_q([cur[-1]] + list(arg), 10))
        elif kind == "z":
            if cur and cur[-1] == start:
                cur = cur[:-1]
            if len(cur) >= 3:
                rings.append(cur)
            cur, start = [], None
    return rings

def _ring_area(r):
    a = 0.0
    for i in range(len(r)):
        x0, y0 = r[i]; x1, y1 = r[(i + 1) % len(r)]
        a += x0 * y1 - x1 * y0
    return a * 0.5

def _pip(pt, ring):
    x, y = pt; inside = False
    n = len(ring)
    j = n - 1
    for i in range(n):
        xi, yi = ring[i]; xj, yj = ring[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi + 1e-30) + xi:
            inside = not inside
        j = i
    return inside

def _dedup(ring, eps=0.35):
    out = []
    for p in ring:
        if not out or (abs(p[0] - out[-1][0]) + abs(p[1] - out[-1][1])) > eps:
            out.append(p)
    if len(out) > 1 and (abs(out[0][0] - out[-1][0]) + abs(out[0][1] - out[-1][1])) < eps:
        out = out[:-1]
    return out

def word_mesh(font_path, text, size, depth, cache_dir=None):
    """Extruded solid mesh for `text`. Returns dict with verts (M,3),
    tris (T,3) int32, normals (T,3), ignite (T,) x-centre fraction per tri."""
    key = hashlib.sha1(f"{font_path}|{text}|{size:.3f}|{depth:.3f}".encode()).hexdigest()[:16]
    if cache_dir:
        cp = Path(cache_dir) / f"mesh-{key}.pkl"
        if cp.exists():
            with open(cp, "rb") as f:
                return pickle.load(f)
    hbf, face, glyphset, upem = _font_objs(font_path)
    buf = hb.Buffer(); buf.add_str(text); buf.guess_segment_properties()
    hb.shape(hbf, buf)
    s = size / upem
    pen_x = 0.0
    allrings = []          # (ring2d, glyph_idx)
    glyph_adv = []
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        gname = hbf.glyph_to_string(info.codepoint)
        for r in _glyph_rings(glyphset, gname):
            r2 = [(pen_x + (pos.x_offset + p[0]) * s, (pos.y_offset + p[1]) * s) for p in r]
            r2 = _dedup(r2)
            if len(r2) >= 3:
                allrings.append((r2, len(glyph_adv)))
        pen_x += pos.x_advance * s
        glyph_adv.append(pen_x)
    width = pen_x
    # centre horizontally
    allrings = [([(x - width / 2, y) for x, y in r], g) for r, g in allrings]
    verts, tris, normals, ignite = [], [], [], []
    hd = depth * 0.5
    # ---- per-glyph processing (rings grouped so holes triangulate with outers)
    verts, tris, normals, ignite = [], [], [], []
    rings_by_glyph = {}
    for r, g in allrings:
        rings_by_glyph.setdefault(g, []).append(r)
    gcenters = {}
    for g in rings_by_glyph:
        xs = [p[0] for r in rings_by_glyph[g] for p in r]
        gcenters[g] = (min(xs) + max(xs)) / 2 if xs else 0.0
    eps = 0.0035 * size / 6.0
    for g, rings in rings_by_glyph.items():
        # containment forest + non-zero-winding hole rule (overlapping contours
        # with same winding as their container are separate solids, not holes)
        info = []
        for r in rings:
            cont = [o for o in rings if o is not r and _pip(r[0], o)]
            depth = len(cont)
            parent = None
            if cont:
                parent = min(cont, key=lambda o: abs(_ring_area(o)))
            info.append(dict(r=r, depth=depth, parent=parent,
                             sign=1.0 if _ring_area(r) > 0 else -1.0))
        for d in info:
            ps = next((p["sign"] for p in info if p["r"] is d["parent"]), None)
            d["hole"] = (d["depth"] % 2 == 1) and ps is not None and d["sign"] != ps
        groups = []
        for d in info:
            if not d["hole"]:
                groups.append([d])
        for d in info:
            if d["hole"]:
                host = None
                cur = d
                while cur["parent"] is not None and host is None:
                    cur = next(x for x in info if x["r"] is cur["parent"])
                    if not cur["hole"]:
                        host = cur
                if host is None:
                    groups.append([d])     # degenerate: treat as own solid
                else:
                    next(grp for grp in groups if grp[0] is host).append(d)
        groups.sort(key=lambda gr: -abs(_ring_area(gr[0]["r"])))
        for gi, grp in enumerate(groups):
            off = eps * gi
            flat, ends, spans, is_hole = [], [], [], []
            for d in sorted(grp, key=lambda d: 0 if not d["hole"] else 1):
                rr = d["r"] if (d["sign"] > 0) != d["hole"] else d["r"][::-1]
                is_hole.append(d["hole"])
                spans.append((len(flat), len(rr)))
                flat.extend(rr)
                ends.append(len(flat))
            arr = np.array(flat, dtype=np.float32)
            tri = earcut(arr, np.array(ends, dtype=np.uint32)).reshape(-1, 3)
            base = len(verts)
            nf = len(flat)
            h0, h1 = hd - off, -hd - off
            verts.extend([(x, y, h0) for x, y in flat])       # front cap
            verts.extend([(x, y, h1) for x, y in flat])       # back cap
            for t in tri:
                tris.append((base + t[0], base + t[1], base + t[2]))
                normals.append((0, 0, 1))
                ignite.append(gcenters[g])
                tris.append((base + nf + t[0], base + nf + t[2], base + nf + t[1]))
                normals.append((0, 0, -1))
                ignite.append(gcenters[g])
            for (start, ln), h in zip(spans, is_hole):
                for i in range(ln):
                    a = start + i; b = start + (i + 1) % ln
                    ax, ay = flat[a]; bx, by = flat[b]
                    dx, dy = bx - ax, by - ay
                    L = math.hypot(dx, dy) + 1e-12
                    nx, ny = (dy / L, -dx / L) if not h else (-dy / L, dx / L)
                    v0 = len(verts)
                    verts.extend([(ax, ay, h0), (bx, by, h0), (bx, by, h1), (ax, ay, h1)])
                    tris.extend([(v0, v0 + 1, v0 + 2), (v0, v0 + 2, v0 + 3)])
                    normals.extend([(nx, ny, 0), (nx, ny, 0)])
                    ignite.extend([gcenters[g], gcenters[g]])
    out = {
        "verts": np.asarray(verts, dtype=np.float64),
        "tris": np.asarray(tris, dtype=np.int32),
        "normals": np.asarray(normals, dtype=np.float64),
        "ignite": np.asarray(ignite, dtype=np.float64),
        "width": width,
    }
    if cache_dir:
        Path(cache_dir).mkdir(parents=True, exist_ok=True)
        with open(Path(cache_dir) / f"mesh-{key}.pkl", "wb") as f:
            pickle.dump(out, f)
    return out

def box_mesh(w, h, d):
    hw, hh, hd = w / 2, h / 2, d / 2
    v = [(-hw, -hh, -hd), (hw, -hh, -hd), (hw, hh, -hd), (-hw, hh, -hd),
         (-hw, -hh, hd), (hw, -hh, hd), (hw, hh, hd), (-hw, hh, hd)]
    f = [(4, 5, 6, 4, 6, 7, (0, 0, 1)), (1, 0, 3, 1, 3, 2, (0, 0, -1)),
         (5, 1, 2, 5, 2, 6, (1, 0, 0)), (0, 4, 7, 0, 7, 3, (-1, 0, 0)),
         (7, 6, 2, 7, 2, 3, (0, 1, 0)), (0, 1, 5, 0, 5, 4, (0, -1, 0))]
    verts, tris, normals, ignite = [], [], [], []
    for a, b, c, d2, e, g, n in f:
        base = len(verts)
        verts.extend([v[a], v[b], v[c], v[d2], v[e], v[g]])
        tris.extend([(base, base + 1, base + 2), (base + 3, base + 4, base + 5)])
        normals.extend([n, n]); ignite.extend([0.0, 0.0])
    return {"verts": np.asarray(verts), "tris": np.asarray(tris, dtype=np.int32),
            "normals": np.asarray(normals, dtype=np.float64),
            "ignite": np.asarray(ignite), "width": w}

def portal_mesh(w, h, t, d):
    """rectangular gate: four bars forming an aperture w×h, bar thickness t."""
    parts = []
    for mesh, ox, oy in [
        (box_mesh(w + 2 * t, t, d), 0, h / 2 + t / 2),
        (box_mesh(w + 2 * t, t, d), 0, -h / 2 - t / 2),
        (box_mesh(t, h, d), -w / 2 - t / 2, 0),
        (box_mesh(t, h, d), w / 2 + t / 2, 0),
    ]:
        vv = mesh["verts"].copy(); vv[:, 1] += oy; vv[:, 0] += ox
        parts.append((vv, mesh["tris"], mesh["normals"]))
    verts, tris, normals, ignite = [], [], [], []
    for vv, tt, nn in parts:
        base = len(verts)
        verts.extend(vv.tolist())
        tris.extend((base + tt).tolist())
        normals.extend(nn.tolist()); ignite.extend([0.0] * len(tt))
    return {"verts": np.asarray(verts), "tris": np.asarray(tris, dtype=np.int32),
            "normals": np.asarray(normals), "ignite": np.asarray(ignite), "width": w}

def quad_mesh(w, h):
    hw, hh = w / 2, h / 2
    verts = np.array([(-hw, -hh, 0), (hw, -hh, 0), (hw, hh, 0), (-hw, hh, 0)], float)
    tris = np.array([(0, 1, 2), (0, 2, 3)], np.int32)
    normals = np.array([(0, 0, 1), (0, 0, 1)], float)
    return {"verts": verts, "tris": tris, "normals": normals,
            "ignite": np.zeros(2), "width": w, "uv": np.array([(0, 0), (1, 0), (1, 1), (0, 1)], float)}

def transform_mesh(mesh, pos=(0, 0, 0), rot_y=0.0, rot_x=0.0, scale=1.0):
    v = mesh["verts"] * scale
    if rot_x:
        c, s = math.cos(rot_x), math.sin(rot_x)
        v = v @ np.array([[1, 0, 0], [0, c, -s], [0, s, c]]).T
    if rot_y:
        c, s = math.cos(rot_y), math.sin(rot_y)
        v = v @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T
    v = v + np.asarray(pos, dtype=float)
    n = mesh["normals"]
    if rot_x:
        c, s = math.cos(rot_x), math.sin(rot_x)
        n = n @ np.array([[1, 0, 0], [0, c, -s], [0, s, c]]).T
    if rot_y:
        c, s = math.cos(rot_y), math.sin(rot_y)
        n = n @ np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]]).T
    out = dict(mesh)
    out["verts"] = v; out["normals"] = n
    return out

# ---------------------------------------------------------------- plates (text textures)
_PLATE_CACHE = {}

def plate_texture(text, font_path, px, color=(255, 240, 220), tracking=0, weight=None, pad=24):
    key = (text, font_path, px, tuple(color), tracking)
    if key in _PLATE_CACHE:
        return _PLATE_CACHE[key]
    f = ImageFont.truetype(font_path, px)
    sp = tracking
    ws = [f.getbbox(ch)[2] - f.getbbox(ch)[0] if ch != " " else px // 3 for ch in text]
    W = sum(ws) + sp * max(0, len(text) - 1) + pad * 2
    H = int(px * 1.7) + pad * 2
    img = Image.new("L", (W, H), 0)
    d = ImageDraw.Draw(img)
    x = pad
    asc, desc = f.getmetrics()
    for ch, w in zip(text, ws):
        bb = f.getbbox(ch)
        d.text((x - bb[0], pad + (H - 2 * pad - (asc + desc)) // 2), ch, font=f, fill=255)
        x += w + sp
    arr = np.asarray(img, dtype=np.float32) / 255.0
    _PLATE_CACHE[key] = (arr, np.array(color, dtype=np.float64) / 255.0)
    return _PLATE_CACHE[key]

# ---------------------------------------------------------------- rasteriser
class Frame:
    def __init__(self, W, H):
        self.W, self.H = W, H
        self.col = np.zeros((H, W, 3), np.float64)
        self.z = np.full(H * W, np.inf, np.float64)   # flat z-buffer
        self.glow = np.zeros((H, W, 3), np.float64)

def _clip_near(poly_cam, near):
    out = []
    n = len(poly_cam)
    for i in range(n):
        a, b = poly_cam[i], poly_cam[(i + 1) % n]
        ain, bin_ = a[2] >= near, b[2] >= near
        if ain:
            out.append(a)
        if ain != bin_:
            t = (near - a[2]) / (b[2] - a[2])
            out.append(a + (b - a) * t)
    return out

def draw_triangles(fb, verts_w, tris, normals, cam, mat, light, fog, shadow,
                   shading=True, emissive=None, ignite_t=None, t=0.0):
    """verts_w (M,3) world; tris (T,3); mat dict(albedo,spec,ambient_mul)."""
    W, H = fb.W, fb.H
    colf = fb.col.reshape(-1, 3); glowf = fb.glow.reshape(-1, 3)
    camv = cam.to_cam(verts_w)
    proj, fpx = cam.project(camv, W, H)
    albedo = np.asarray(mat["albedo"], np.float64)
    spec = mat.get("spec", 0.08)
    shin = mat.get("shin", 26.0)
    lpos = light["pos"]; lcol = np.asarray(light["color"], np.float64) * light["energy"]
    fcol = np.asarray(light.get("fill_color", (0.35, 0.45, 0.55)), np.float64) * light.get("fill", 0.35)
    fdir = norm(np.asarray(light.get("fill_dir", (-0.45, 0.75, -0.35))))
    amb = np.asarray(fog["amb"], np.float64)
    fogc = np.asarray(fog["color"], np.float64)
    fogd = fog["density"]
    for ti in range(len(tris)):
        i0, i1, i2 = tris[ti]
        nrm = normals[ti]
        cw = verts_w[[i0, i1, i2]]
        cc = camv[[i0, i1, i2]]
        if (cc[:, 2] < cam.near).all():
            continue
        ctr = cw.mean(axis=0)
        vd = ctr - cam.pos
        if shading and np.dot(nrm, vd) >= 0 and not mat.get("double", False):
            continue
        if (cc[:, 2] < cam.near).any():
            poly = _clip_near(cc, cam.near)
            if len(poly) < 3:
                continue
            poly = np.asarray(poly)
            pr, _ = cam.project(poly, W, H)
            pw = cam.pos + poly @ cam.R          # back to world
            subtris = [(0, k, k + 1) for k in range(1, len(poly) - 1)]
        else:
            pr = proj[[i0, i1, i2]]
            pw = cw
            poly = cc
            subtris = [(0, 1, 2)]
        xs = pr[:, 0]; ys = pr[:, 1]
        minx, maxx = int(math.floor(xs.min())), int(math.ceil(xs.max()))
        miny, maxy = int(math.floor(ys.min())), int(math.ceil(ys.max()))
        if maxx < 0 or minx >= W or maxy < 0 or miny >= H:
            continue
        minx, maxx = max(0, minx), min(W - 1, maxx)
        miny, maxy = max(0, miny), min(H - 1, maxy)
        for a, b, c in subtris:
            pa, pb, pc = pr[a], pr[b], pr[c]
            wa, wb, wc = pw[a], pw[b], pw[c]
            za, zb, zc = poly[a, 2], poly[b, 2], poly[c, 2]
            d = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
            if abs(d) < 1e-9:
                continue
            gx = np.arange(minx, maxx + 1) + 0.5
            gy = np.arange(miny, maxy + 1) + 0.5
            PX, PY = np.meshgrid(gx, gy)
            w0 = (pb[0] - pa[0]) * (PY - pa[1]) - (pb[1] - pa[1]) * (PX - pa[0])
            w1 = (pc[0] - pb[0]) * (PY - pb[1]) - (pc[1] - pb[1]) * (PX - pb[0])
            w2 = (pa[0] - pc[0]) * (PY - pc[1]) - (pa[1] - pc[1]) * (PX - pc[0])
            if d > 0:
                mask = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            else:
                mask = (w0 <= 0) & (w1 <= 0) & (w2 <= 0)
                w0, w1, w2 = -w0, -w1, -w2
            if not mask.any():
                continue
            ia, ib, ic = 1 / za, 1 / zb, 1 / zc
            wa_ = (w0 / d) * ia; wb_ = (w1 / d) * ib; wc_ = (w2 / d) * ic
            s = wa_ + wb_ + wc_
            la, lb, lc = wa_ / s, wb_ / s, wc_ / s
            zpix = 1.0 / s
            ys_i, xs_i = np.nonzero(mask)
            flat = (ys_i + miny) * W + (xs_i + minx)
            if (zpix[ys_i, xs_i] < fb.z[flat]).any():
                zm = zpix[ys_i, xs_i] < fb.z[flat]
                ys_i, xs_i, flat = ys_i[zm], xs_i[zm], flat[zm]
                zm2 = zpix[ys_i, xs_i]
                if len(flat) == 0:
                    continue
                la_, lb_, lc_ = la[ys_i, xs_i], lb[ys_i, xs_i], lc[ys_i, xs_i]
                P = la_[:, None] * wa + lb_[:, None] * wb + lc_[:, None] * wc
                fb.z[flat] = zm2
                if not shading:
                    colf[flat] = mat["albedo"]
                    continue
                L = lpos[None, :] - P
                dist = np.linalg.norm(L, axis=1)
                Ln = L / dist[:, None]
                ndl = np.clip(np.einsum("ij,j->i", Ln, nrm), 0, 1)
                att = 1.0 / (1.0 + (dist / light.get("ref", 26.0)) ** 2)
                sh = 1.0
                if shadow is not None:
                    sh = shadow.sample(lpos, P, nrm)
                V = norm(cam.pos - ctr)
                Hh = norm(Ln + V[None, :])
                spc = (np.clip(np.einsum("ij,j->i", Hh, nrm), 0, 1) ** shin) * spec
                fillv = max(0.0, float(np.dot(fdir, nrm)))
                fill = np.full(len(P), fillv)
                base = albedo[None, :] * (amb[None, :] * mat.get("amb_mul", 1.0)
                        + lcol[None, :] * (ndl * att * sh)[:, None]
                        + fcol[None, :] * fill[:, None])
                base += lcol[None, :] * (spc * att * sh)[:, None]
                em = 0.0
                if emissive is not None:
                    em = emissive
                if ignite_t is not None and mat.get("ignite_amp", 0.0):
                    ig = ignite_t[ti]
                    pulse = math.exp(-(((t - ig) / 0.55) ** 2))
                    em += mat["ignite_amp"] * pulse
                if em:
                    base = base + np.asarray(mat.get("ignite_col", (1.0, 0.55, 0.25)))[None, :] * em
                fg = 1.0 - np.exp(-((zm2 * fogd) ** 2))
                col = base * (1 - fg)[:, None] + fogc[None, :] * fg[:, None]
                colf[flat] = col
                if em:
                    glowf[flat] += np.asarray(mat.get("ignite_col", (1.0, 0.55, 0.25)))[None, :] * (em * 0.9)

def draw_plate(fb, quad_w, tex, tcol, cam, glow_amt=0.8, alpha=1.0):
    """textured emissive quad (already world-transformed, uv in mesh['uv'])."""
    W, H = fb.W, fb.H
    colf = fb.col.reshape(-1, 3); glowf = fb.glow.reshape(-1, 3)
    camv = cam.to_cam(quad_w["verts"])
    if (camv[:, 2] < cam.near).all():
        return
    proj, _ = cam.project(camv, W, H)
    uv = quad_w["uv"]
    for a, b, c in [(0, 1, 2), (0, 2, 3)]:
        pa, pb, pc = proj[a], proj[b], proj[c]
        za, zb, zc = camv[a, 2], camv[b, 2], camv[c, 2]
        ua, ub, uc = uv[a], uv[b], uv[c]
        d = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
        if abs(d) < 1e-9:
            continue
        minx, maxx = int(max(0, math.floor(min(pa[0], pb[0], pc[0])))), int(min(W - 1, math.ceil(max(pa[0], pb[0], pc[0]))))
        miny, maxy = int(max(0, math.floor(min(pa[1], pb[1], pc[1])))), int(min(H - 1, math.ceil(max(pa[1], pb[1], pc[1]))))
        if maxx <= minx or maxy <= miny:
            continue
        gx = np.arange(minx, maxx + 1) + 0.5
        gy = np.arange(miny, maxy + 1) + 0.5
        PX, PY = np.meshgrid(gx, gy)
        w0 = (pb[0] - pa[0]) * (PY - pa[1]) - (pb[1] - pa[1]) * (PX - pa[0])
        w1 = (pc[0] - pb[0]) * (PY - pb[1]) - (pc[1] - pb[1]) * (PX - pb[0])
        w2 = (pa[0] - pc[0]) * (PY - pc[1]) - (pa[1] - pc[1]) * (PX - pc[0])
        if d > 0:
            mask = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
        else:
            mask = (w0 <= 0) & (w1 <= 0) & (w2 <= 0)
            w0, w1, w2 = -w0, -w1, -w2
        if not mask.any():
            continue
        ia, ib, ic = 1 / za, 1 / zb, 1 / zc
        s = (w0 / d) * ia + (w1 / d) * ib + (w2 / d) * ic
        la = (w0 / d) * ia / s; lb = (w1 / d) * ib / s; lc = (w2 / d) * ic / s
        zpix = 1.0 / s
        ys_i, xs_i = np.nonzero(mask)
        flat = (ys_i + miny) * W + (xs_i + minx)
        zm = zpix[ys_i, xs_i] < fb.z[flat]
        ys_i, xs_i, flat = ys_i[zm], xs_i[zm], flat[zm]
        if len(flat) == 0:
            continue
        la_, lb_, lc_ = la[ys_i, xs_i], lb[ys_i, xs_i], lc[ys_i, xs_i]
        U = la_[:, None] * ua + lb_[:, None] * ub + lc_[:, None] * uc
        th, tw = tex.shape
        tx = np.clip((U[:, 0] * (tw - 1)).astype(int), 0, tw - 1)
        ty = np.clip(((1 - U[:, 1]) * (th - 1)).astype(int), 0, th - 1)
        a_ = tex[ty, tx] * alpha
        keep = a_ > 0.02
        ys_i, xs_i, flat, a_ = ys_i[keep], xs_i[keep], flat[keep], a_[keep]
        if len(flat) == 0:
            continue
        colf[flat] = colf[flat] * (1 - a_)[:, None] + (tcol[None, :] * 1.35) * a_[:, None]
        glowf[flat] += tcol[None, :] * (a_[:, None] * glow_amt)
        fb.z[flat] = np.minimum(fb.z[flat], zpix[keep])

# ---------------------------------------------------------------- shadow map
class ShadowMap:
    def __init__(self, size=768):
        self.size = size
        self.depth = None

    def build(self, lpos, target, meshes, fov=110.0, near=0.3, far=400.0):
        S = self.size
        fwd = norm(target - lpos)
        up = np.array([0.0, 1.0, 0.0])
        if abs(fwd[1]) > 0.95:
            up = np.array([0.0, 0.0, 1.0])
        right = norm(np.cross(fwd, up)); up2 = np.cross(right, fwd)
        R = np.stack([right, up2, fwd])
        self.R, self.lpos, self.fov, self.near = R, lpos, fov, near
        f = (S * 0.5) / math.tan(math.radians(fov) * 0.5)
        self.f = f
        depth = np.full(S * S, np.inf)
        for verts_w, tris in meshes:
            cv = (verts_w - lpos) @ R.T
            z = cv[:, 2]
            keep = (z >= near).all(axis=0) if z.ndim > 1 else None
            projx = S * 0.5 + f * cv[:, 0] / np.maximum(z, 1e-6)
            projy = S * 0.5 - f * cv[:, 1] / np.maximum(z, 1e-6)
            for ti in range(len(tris)):
                i0, i1, i2 = tris[ti]
                if min(cv[i0, 2], cv[i1, 2], cv[i2, 2]) < near:
                    continue
                pa, pb, pc = (projx[i0], projy[i0]), (projx[i1], projy[i1]), (projx[i2], projy[i2])
                za, zb, zc = cv[i0, 2], cv[i1, 2], cv[i2, 2]
                d = (pb[0] - pa[0]) * (pc[1] - pa[1]) - (pb[1] - pa[1]) * (pc[0] - pa[0])
                if abs(d) < 1e-9:
                    continue
                minx, maxx = int(max(0, math.floor(min(pa[0], pb[0], pc[0])))), int(min(S - 1, math.ceil(max(pa[0], pb[0], pc[0]))))
                miny, maxy = int(max(0, math.floor(min(pa[1], pb[1], pc[1])))), int(min(S - 1, math.ceil(max(pa[1], pb[1], pc[1]))))
                if maxx <= minx or maxy <= miny:
                    continue
                gx = np.arange(minx, maxx + 1) + 0.5
                gy = np.arange(miny, maxy + 1) + 0.5
                PX, PY = np.meshgrid(gx, gy)
                w0 = (pb[0] - pa[0]) * (PY - pa[1]) - (pb[1] - pa[1]) * (PX - pa[0])
                w1 = (pc[0] - pb[0]) * (PY - pb[1]) - (pc[1] - pb[1]) * (PX - pb[0])
                w2 = (pa[0] - pc[0]) * (PY - pc[1]) - (pa[1] - pc[1]) * (PX - pc[0])
                if d > 0:
                    mask = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
                else:
                    mask = (w0 <= 0) & (w1 <= 0) & (w2 <= 0)
                    w0, w1, w2 = -w0, -w1, -w2
                if not mask.any():
                    continue
                s = (w0 / d) / za + (w1 / d) / zb + (w2 / d) / zc
                zpix = 1.0 / s
                ys_i, xs_i = np.nonzero(mask)
                flat = (ys_i + miny) * S + (xs_i + minx)
                zm = zpix[ys_i, xs_i] < depth[flat]
                depth[flat[zm]] = zpix[ys_i, xs_i][zm]
        self.depth = depth.reshape(S, S)

    def sample(self, lpos, P, nrm):
        if self.depth is None:
            return np.ones(len(P))
        S = self.size
        P = P + nrm[None, :] * 0.15
        cv = (P - lpos) @ self.R.T
        z = cv[:, 2]
        px = S * 0.5 + self.f * cv[:, 0] / np.maximum(z, 1e-6)
        py = S * 0.5 - self.f * cv[:, 1] / np.maximum(z, 1e-6)
        xi = np.clip(px.astype(int), 0, S - 1)
        yi = np.clip(py.astype(int), 0, S - 1)
        inside = (px >= 0) & (px < S) & (py >= 0) & (py < S)
        bias = 0.05 + 0.006 * z
        lit = (z - bias) <= self.depth[yi, xi]
        out = np.where(inside, np.where(lit, 1.0, 0.18), 1.0)
        return out

# ---------------------------------------------------------------- post
def _boxblur(a, r):
    if r < 1:
        return a
    k = 2 * r + 1
    pw = ((r + 1, r), (0, 0)) + ((0, 0),) * (a.ndim - 2)
    pad = np.pad(a, pw, mode="edge")
    c = np.cumsum(pad, axis=0)
    a = (c[k:, :] - c[:-k, :]) / k
    pw = ((0, 0), (r + 1, r)) + ((0, 0),) * (a.ndim - 2)
    pad = np.pad(a, pw, mode="edge")
    c = np.cumsum(pad, axis=1)
    return (c[:, k:] - c[:, :-k]) / k

def _gauss3(a, r):
    return _boxblur(_boxblur(_boxblur(a, r), r), r)

def post(fb, t, grain=1.4, vignette=0.16, glow_strength=0.55, exposure=1.0):
    W, H = fb.W, fb.H
    g = fb.glow
    if g.any():
        halo = (_gauss3(g, 2) * 0.45 + _gauss3(g, 6) * 0.35 + _gauss3(g, 14) * 0.30)
        fb.col += halo * glow_strength
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    fb.col *= (1.0 - vignette * np.clip(r - 0.55, 0, 1) ** 1.6)[:, :, None]
    fb.col *= exposure
    rng = np.random.default_rng(int(t * 1000) % (2 ** 31))
    fb.col += (rng.uniform(-1, 1, (H, W, 1)) * grain) / 255.0
    return linear_to_srgb_u8(fb.col)

def background(fb, top, bottom, light_screen=None, warm=(1.0, 0.62, 0.3), amt=0.0):
    W, H = fb.W, fb.H
    yy = np.linspace(0, 1, H)[:, None]
    grad = np.asarray(top)[None, None, :] * (1 - yy[:, :, None]) + np.asarray(bottom)[None, None, :] * yy[:, :, None]
    if light_screen is not None and amt > 0:
        xx = np.linspace(0, 1, W)[None, :]
        d2 = (xx - light_screen[0]) ** 2 + (yy - light_screen[1]) ** 2
        grad = grad + np.asarray(warm)[None, None, :] * (amt * np.exp(-d2 / 0.16))[:, :, None]
    fb.col = np.broadcast_to(grad, (H, W, 3)).copy()
