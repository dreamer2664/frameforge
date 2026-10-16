#!/usr/bin/env python3
"""Build the parallax film scene from storyboard.json, frame by frame.

All creative decisions (camera path, light keys, letter choreography, copy
placement) live in storyboard.json; this module only turns that data into
geometry and transforms, so the film can be re-timed without touching code.
"""
from __future__ import annotations

import json
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import render3d as R
import type3d

HERE = Path(__file__).resolve().parent
STORY = json.loads((HERE / "storyboard.json").read_text())


# ----------------------------------------------------------------- interpolation
def sample_keys(keys, t, fields, smooth=True):
    """Piecewise cubic-Hermite sample of a keyed list of dicts."""
    times = [k["t"] for k in keys]
    if t <= times[0]:
        return {f: keys[0][f] for f in fields}
    if t >= times[-1]:
        return {f: keys[-1][f] for f in fields}
    i = 0
    for k in range(len(times) - 1):
        if times[k] <= t <= times[k + 1]:
            i = k
            break
    t0, t1 = times[i], times[i + 1]
    h = max(t1 - t0, 1e-6)
    u = (t - t0) / h
    n = len(times)
    out = {}
    for f in fields:
        v0 = np.asarray(keys[i][f], dtype=np.float64)
        v1 = np.asarray(keys[i + 1][f], dtype=np.float64)
        if smooth:
            if i > 0:
                vm = np.asarray(keys[i - 1][f], dtype=np.float64)
                m0 = (v1 - vm) / max(times[i + 1] - times[i - 1], 1e-3) * h
            else:
                m0 = v1 - v0
            if i + 2 < n:
                vp = np.asarray(keys[i + 2][f], dtype=np.float64)
                m1 = (vp - v0) / max(times[i + 2] - times[i], 1e-3) * h
            else:
                m1 = v1 - v0
            lim = 4.0 * np.abs(v1 - v0) + 1e-6
            m0 = np.clip(m0, -lim, lim)
            m1 = np.clip(m1, -lim, lim)
        else:
            m0 = m1 = np.zeros_like(v0)
        u2 = u * u
        u3 = u2 * u
        out[f] = ((2 * u3 - 3 * u2 + 1) * v0 + (u3 - 2 * u2 + u) * m0
                  + (-2 * u3 + 3 * u2) * v1 + (u3 - u2) * m1)
    return out


def ease(a, b, t, kind="smooth"):
    if t <= 0:
        return 0.0
    if t >= 1:
        return 1.0
    if kind == "linear":
        return t
    if kind == "in":
        return t * t * t
    if kind == "out":
        return 1 - (1 - t) ** 3
    return t * t * (3 - 2 * t)


def smoothstep(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3 - 2 * x)


def lerp_pose(p0, p1, u):
    return {
        "pos": (1 - u) * np.asarray(p0["pos"], float) + u * np.asarray(p1["pos"], float),
        "rot": (1 - u) * np.asarray(p0["rot"], float) + u * np.asarray(p1["rot"], float),
    }


def euler_matrix(rx, ry, rz):
    cx, sx = math.cos(rx), math.sin(rx)
    cy, sy = math.cos(ry), math.sin(ry)
    cz, sz = math.cos(rz), math.sin(rz)
    rxm = np.array([[1, 0, 0], [0, cx, -sx], [0, sx, cx]], float)
    rym = np.array([[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]], float)
    rzm = np.array([[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]], float)
    return rzm @ rym @ rxm


# ------------------------------------------------------------------ text texture
@lru_cache(maxsize=64)
def text_texture(text: str, size: int = 300, tracking: float = 0.0, weight: int = 450,
                 width: int = 100, glow: float = 8.0,
                 color: tuple = (1.0, 0.88, 0.70)) -> np.ndarray:
    """Tinted RGBA lettering on transparent, returned as float32 (h,w,4).

    The canvas is sized to the measured advance of the whole run, so long
    lines are never clipped, and v = 0 is the TOP row of the image.
    """
    path = str(HERE / STORY["type"]["caption"]["file"])
    font = ImageFont.truetype(path, size)
    try:
        font.set_variation_by_axes([float(weight), float(width)])
    except Exception:
        pass
    probe = ImageDraw.Draw(Image.new("RGBA", (8, 8)))
    widths = [probe.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * size * max(len(text) - 1, 0)
    pad = int(size * 0.35)
    w_img = max(16, int(total) + 2 * pad)
    img = Image.new("RGBA", (w_img, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    y = int(size * 0.78)
    for ch, wch in zip(text, widths):
        d.text((x, y), ch, fill=(255, 255, 255, 255), font=font, anchor="ls")
        x += wch + tracking * size
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    rgb = np.asarray(img).astype(np.float32) / 255.0
    if glow > 0:
        blur = np.asarray(img.filter(ImageFilter.GaussianBlur(glow))).astype(np.float32) / 255.0
        a = np.clip(rgb[:, :, 3] + blur[:, :, 3], 0, 1)
        rgb = np.concatenate([np.repeat(np.asarray(color, np.float32)[None, None, :],
                                         rgb.shape[0], axis=0).repeat(rgb.shape[1], axis=1),
                              a[:, :, None]], axis=2)
    return rgb.astype(np.float32)


@lru_cache(maxsize=8)
def soft_rect_texture(size=256, feather=0.34, warm=(1.0, 0.74, 0.46)) -> np.ndarray:
    """A soft-edged rectangle used for the pool of light on the floor."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = np.abs((xx / (size - 1)) * 2 - 1)
    v = np.abs((yy / (size - 1)) * 2 - 1)
    m = np.clip(1.0 - (u * u + v * v) * 0.75, 0, 1)
    m = m ** 2.4
    tex = np.repeat(m[:, :, None], 3, axis=2) * np.asarray(warm, np.float32)[None, None, :]
    return tex.astype(np.float32)


@lru_cache(maxsize=8)
def glow_texture(size=256) -> np.ndarray:
    """Soft warm haze: bright low and centred, fading up and to the sides."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = (xx / (size - 1)) * 2 - 1
    v = yy / (size - 1)
    h = np.clip(1.0 - u ** 2, 0, 1) ** 1.5
    g = np.clip(1.0 - v * 0.85, 0, 1) ** 1.8
    m = (h * g).astype(np.float32)
    return np.repeat(m[:, :, None], 3, axis=2).astype(np.float32)


@lru_cache(maxsize=8)
def shaft_texture(size=256) -> np.ndarray:
    """Vertical soft beam: bright at the top, fading to nothing at the floor."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = np.abs((xx / (size - 1)) * 2 - 1)
    v = (yy / (size - 1))  # 0 at the top (the slit), 1 at the floor
    h = np.clip(1.0 - u ** 3, 0, 1) ** 2
    g = np.clip(1.0 - v, 0, 1) ** 1.7
    m = h * g
    return np.repeat(m[:, :, None], 3, axis=2).astype(np.float32)


# ----------------------------------------------------------------- letter meshes
def build_letter_meshes():
    w = STORY["world"]
    out = []
    for spec in STORY["letters"]:
        m, _ = type3d.text_mesh(spec["ch"], str(HERE / STORY["type"]["display"]["file"]),
                                wght=STORY["type"]["display"]["wght"],
                                wdth=STORY["type"]["display"]["wdth"],
                                cap_height=w["letter_cap"], depth=w["letter_depth"],
                                tracking=0.02)
        out.append(m)
    return out


# ------------------------------------------------------------------- geometry
def quad(v0, v1, v2, v3, normal=None, uv=None):
    v = np.array([v0, v1, v2, v3], dtype=np.float32)
    if normal is None:
        n = np.cross(v[1] - v[0], v[2] - v[0])
        n = n / max(np.linalg.norm(n), 1e-9)
    else:
        n = np.asarray(normal, dtype=np.float32)
    u = np.array(uv if uv else [(0, 0), (1, 0), (1, 1), (0, 1)], dtype=np.float32)
    t = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
    return v, np.tile(n, (4, 1)), u, t


def stone_texture(seed=7, size=512):
    """Deterministic procedural stone: two scales of value noise plus grain."""
    from scipy.ndimage import zoom
    rng = np.random.default_rng(seed)
    base = rng.random((size // 8, size // 8)).astype(np.float32)
    img = zoom(base, size / base.shape[0], order=3)[:size, :size]
    if img.shape != (size, size):
        img = np.pad(img, ((0, max(0, size - img.shape[0])), (0, max(0, size - img.shape[1]))),
                     mode="edge")[:size, :size]
    img = np.clip(img, 0, 1)
    blot = zoom(rng.random((size // 32 + 1, size // 32 + 1)).astype(np.float32),
                size / (size // 32 + 1), order=3)[:size, :size]
    grain = rng.normal(0, 0.010, (size, size)).astype(np.float32)
    tex = np.clip(img * 0.22 + blot * 0.12 + 0.62 + grain, 0, 1.4)
    return np.repeat(tex[:, :, None], 3, axis=2).astype(np.float32)


def box_mesh(cx, cy, cz, sx, sy, sz):
    """Axis-aligned box with outward-facing winding and per-face normals."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    c = [(cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
         (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
         (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
         (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)]
    faces = [
        (0, 3, 2, 1, (0, 0, -1)),    # back
        (4, 5, 6, 7, (0, 0, 1)),     # front
        (0, 4, 7, 3, (-1, 0, 0)),    # left
        (1, 2, 6, 5, (1, 0, 0)),     # right
        (0, 1, 5, 4, (0, -1, 0)),    # bottom
        (3, 7, 6, 2, (0, 1, 0)),     # top
    ]
    v, n, u, t = [], [], [], []
    for a, b, cc, d, nrm in faces:
        i = len(v)
        v.extend([c[a], c[b], c[cc], c[d]])
        n.extend([nrm] * 4)
        u.extend([(0, 0), (1, 0), (1, 1), (0, 1)])
        t.extend([[i, i + 1, i + 2], [i, i + 2, i + 3]])
    return (np.array(v, dtype=np.float32), np.array(n, dtype=np.float32),
            np.array(u, dtype=np.float32), np.array(t, dtype=np.int32))


def blade(a, b, width):
    """A camera-agnostic ribbon between two points (used for light shafts)."""
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d = b - a
    side = np.cross(d, np.array([0.0, 1.0, 0.0]))
    n = np.linalg.norm(side)
    side = side / n if n > 1e-6 else np.array([1.0, 0.0, 0.0])
    v = np.array([a - side * width / 2, b - side * width / 2,
                  b + side * width / 2, a + side * width / 2], dtype=np.float32)
    u = np.array([[0, 1], [0, 0], [1, 0], [1, 1]], dtype=np.float32)
    t = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
    nrm = np.tile(np.cross(side, d).astype(np.float32), (4, 1))
    return v, nrm, u, t


# ------------------------------------------------------------------ the film
class Film:
    def __init__(self):
        self.story = STORY
        self.w = STORY["world"]
        self.pal = STORY["palette"]
        self.letter_meshes = build_letter_meshes()
        self.stone = stone_texture()
        self.pool_tex = soft_rect_texture()
        self.shaft_tex = shaft_texture()
        self.glow_tex = glow_texture()
        self.copy_textures = {}
        for c in STORY["copy"]:
            key = (c["text"], c.get("small", False))
            if key not in self.copy_textures:
                self.copy_textures[key] = text_texture(
                    c["text"], size=260, tracking=0.17, weight=450, glow=9.0)

    # ---------------------------------------------------------------- letters
    def letter_poses(self, t):
        s = self.story["stages"]
        w = self.w
        poses = []
        for i, spec in enumerate(self.story["letters"]):
            t_rel = s["release"] + i * s["release_stagger"]
            wall = {"pos": np.array([spec["wall_x"], w["bench_h"], w["wall_z"]]),
                    "rot": np.array([0.0, 0.0, 0.0])}
            tip = {"pos": np.array([spec["wall_x"], w["bench_h"] + 0.10, w["wall_z"] + 1.45]),
                   "rot": np.array([math.radians(52.0), math.radians(-7.0 + 2.6 * i), 0.0])}
            field = {"pos": np.array(spec["field"], float),
                     "rot": np.array([math.radians(a) for a in spec["field_rot"]])}
            gate = {"pos": np.array(spec["gate"], float), "rot": np.array([0.0, 0.0, 0.0])}
            row = {"pos": np.array(spec["row"], float), "rot": np.array([0.0, 0.0, 0.0])}
            if t < t_rel:
                p = wall
            elif t < t_rel + s["release_dur"]:
                p = lerp_pose(wall, tip, ease(0, 1, (t - t_rel) / s["release_dur"], "in"))
            elif t < s["field"] + 0.9:
                u = ease(0, 1, (t - t_rel - s["release_dur"])
                         / max(s["field"] - t_rel - s["release_dur"], 1e-3))
                p = lerp_pose(tip, field, u)
            elif t < s["assemble"]:
                u = ease(0, 1, (t - s["field"] - 0.9)
                         / max(s["assemble"] - s["field"] - 0.9, 1e-3))
                p = lerp_pose(field, gate, u)
            elif t < s["fly"]:
                p = gate
            elif t < s["row"]:
                p = lerp_pose(gate, row, ease(0, 1, (t - s["fly"]) / max(s["row"] - s["fly"], 1e-3), "in"))
            else:
                p = row
            poses.append(p)
        return poses

    # ------------------------------------------------------------------ reveal
    def reveal(self, t):
        """0..1 per letter: how much of the raking light has reached it."""
        out = []
        u = float(np.clip((t - 6.0) / 7.0, 0.0, 1.0))
        x_light = 11.0 - 14.0 * u
        for spec in self.story["letters"]:
            r = (spec["wall_x"] - x_light) / 2.6
            out.append(smoothstep(r))
        return out

    def reveal_light(self, t):
        """Position/intensity of the light that travels along the carved word."""
        u = float(np.clip((t - 6.0) / 7.0, 0.0, 1.0))
        x_light = 11.0 - 14.0 * u
        i = 1.05 * smoothstep((t - 5.4) / 1.2) * (1.0 - smoothstep((t - 13.4) / 1.6))
        return x_light, i

    # ------------------------------------------------------------------ scene
    def build(self, t, cam=None):
        st = self.story
        w = self.w
        pal = self.pal
        pr = st["lights"]["practicals"]
        scene = R.Scene()
        scene.ambient_sky = (0.020, 0.024, 0.036)
        scene.ambient_ground = (0.012, 0.009, 0.007)
        fog = sample_keys(st["fog"]["keys"], t, ["color", "density"])
        scene.fog_color = tuple(float(x) for x in fog["color"])
        scene.fog_density = float(fog["density"])

        z = w["wall_z"]
        op = w["wall_opening"]
        stone_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                               texture=self.stone, texture_uv=(1.0, 1.0))

        # ---- floor
        q = quad([-46, 0, 30], [46, 0, 30], [46, 0, -40], [-46, 0, -40],
                 normal=(0, 1, 0), uv=[(0, 0), (26, 0), (26, 35), (0, 35)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.10, shininess=26.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))

        # ---- end wall, solid apart from the arch
        for p, uvs in [
            (([-30, 0, z], [op["x0"], 0, z], [op["x0"], 16, z], [-30, 16, z]),
             [(0, 0), (6.0, 0), (6.0, 4.2), (0, 4.2)]),
            (([op["x1"], 0, z], [30, 0, z], [30, 16, z], [op["x1"], 16, z]),
             [(0, 0), (8.5, 0), (8.5, 4.2), (0, 4.2)]),
            (([op["x0"], op["y1"], z], [op["x1"], op["y1"], z], [op["x1"], 16, z], [op["x0"], 16, z]),
             [(0, 0), (1.0, 0), (1.0, 2.6), (0, 2.6)]),
        ]:
            q = quad(*p, normal=(0, 0, 1), uv=uvs)
            scene.meshes.append((q[0], q[1], q[2], q[3], stone_mat, False))

        # ---- piers flanking the hall
        pier_mat = R.Material(base=tuple(pal["stone_light"]), spec=0.05, shininess=14.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))
        for z_p in (20.0, 12.0, 4.0):
            for x_p in (-w["pier_x"], w["pier_x"]):
                scene.meshes.append((*box_mesh(x_p, 4.2, z_p, 1.4, 8.4, 1.3), pier_mat))

        # ---- bench carrying the carved word
        bx0, bx1 = w["bench_x"]
        bz0, bz1 = w["bench_z"]
        scene.meshes.append((*box_mesh((bx0 + bx1) / 2, w["bench_h"] / 2, (bz0 + bz1) / 2,
                                       bx1 - bx0, w["bench_h"], bz1 - bz0),
                             R.Material(base=tuple(pal["stone_light"]), spec=0.07, shininess=20.0), False))

        # ---- the slot of light
        slot = pr["slot"]
        q = quad([slot["x"] - 0.14, slot["y"][0], slot["z"]],
                 [slot["x"] + 0.14, slot["y"][0], slot["z"]],
                 [slot["x"] + 0.14, slot["y"][1], slot["z"]],
                 [slot["x"] - 0.14, slot["y"][1], slot["z"]], normal=(0, 0, 1))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0),
                                        emissive=tuple(np.array(slot["color"]) * slot["intensity"])), False))

        # ---- the chamber behind the arch
        q = quad([-14, 0, -30], [14, 0, -30], [14, 12, -30], [-14, 12, -30], normal=(0, 0, 1),
                 uv=[(0, 0), (4, 0), (4, 1.2), (0, 1.2)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.05, shininess=14.0,
                                        texture=self.stone, texture_uv=(2.0, 1.0),
                                        emissive=(0.085, 0.050, 0.026)), False))
        for x_s in (-14.0, 14.0):
            q = quad([x_s, 0, -30], [x_s, 0, -4], [x_s, 12, -4], [x_s, 12, -30],
                     normal=(-1 if x_s > 0 else 1, 0, 0), uv=[(0, 0), (4, 0), (4, 1.2), (0, 1.2)])
            scene.meshes.append((q[0], q[1], q[2], q[3],
                                 R.Material(base=tuple(pal["stone"]), spec=0.04, shininess=12.0,
                                            texture=self.stone, texture_uv=(2.0, 1.0),
                                            emissive=(0.085, 0.050, 0.026)), False))
        q = quad([-14, 12, -30], [14, 12, -30], [14, 12, -4], [-14, 12, -4], normal=(0, -1, 0),
                 uv=[(0, 0), (4, 0), (4, 2.0), (0, 2.0)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.02, shininess=8.0), False))

        # ---- warm glow deep in the chamber (seen through the arch)
        q = quad([-13, 0, -29.9], [13, 0, -29.9], [13, 11, -29.9], [-13, 11, -29.9],
                 normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0.55, 0.31, 0.15),
                                        texture=self.glow_tex, additive=True, alpha=0.30), False))

        # ---- the plinth the row lands on
        pz0, pz1 = w["plinth_z"]
        scene.meshes.append((*box_mesh(0.0, w["plinth_h"] / 2, (pz0 + pz1) / 2,
                                       13.4, w["plinth_h"], pz1 - pz0),
                             R.Material(base=tuple(pal["stone_light"]), spec=0.08, shininess=20.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))

        # ---- pool of light on the floor under the slot
        q = quad([3.0, 0.012, -1.2], [10.0, 0.012, -1.2], [10.0, 0.012, 4.4], [3.0, 0.012, 4.4],
                 normal=(0, 1, 0))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=self.pool_tex, additive=True,
                                        alpha=0.10, double_sided=True), False))

        # ---- blade of light falling from the slot
        v, n, u, t2 = blade((slot["x"], slot["y"][1], slot["z"]),
                            (4.2, 0.0, 1.6), 2.6)
        scene.meshes.append((v, n, u, t2,
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=self.shaft_tex, additive=True,
                                        alpha=0.045, double_sided=True), False))

        # ---- the carved letters
        rev = self.reveal(t)
        for i, (m, pose) in enumerate(zip(self.letter_meshes, self.letter_poses(t))):
            R3 = euler_matrix(*pose["rot"])
            v = m.verts.astype(np.float64) @ R3.T + pose["pos"]
            k = 0.34 + 0.66 * rev[i]
            mat = R.Material(base=tuple(np.array(pal["letter"]) * k), spec=0.14, shininess=30.0,
                             texture=self.stone, texture_uv=(0.0016, 0.0016))
            scene.meshes.append((v.astype(np.float32),
                                 (m.normals.astype(np.float64) @ R3.T).astype(np.float32),
                                 m.uvs, m.tris, mat))

        # ---- copy written in light on the stone
        for c in st["copy"]:
            if not (c["t_in"] <= t <= c["t_out"]):
                continue
            fade = min(ease(0, 1, (t - c["t_in"]) / 0.9, "out"),
                       ease(0, 1, (c["t_out"] - t) / 0.9, "out"))
            tex = self.copy_textures[(c["text"], c.get("small", False))]
            h, wpx = tex.shape[:2]
            quad_w = c["width"]
            quad_h = quad_w * h / wpx
            px, py, pz = c["pos"]
            v = np.array([[px - quad_w / 2, py - quad_h / 2, pz],
                          [px + quad_w / 2, py - quad_h / 2, pz],
                          [px + quad_w / 2, py + quad_h / 2, pz],
                          [px - quad_w / 2, py + quad_h / 2, pz]], dtype=np.float32)
            # v = 0 is the BOTTOM row of the texture: the image must not flip
            u = np.array([[0, 1], [1, 1], [1, 0], [0, 0]], dtype=np.float32)
            t2 = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
            n = np.tile(np.array([0, 0, 1], np.float32), (4, 1))
            scene.meshes.append((v, n, u, t2,
                                 R.Material(base=(0, 0, 0), emissive=(0, 0, 0), texture=tex,
                                            additive=True, alpha=float(fade) * 0.42,
                                            double_sided=True), False))

        # ---- lights
        # the shadow volume follows the letters so the map stays dense
        lp = np.array([p_["pos"] for p_ in self.letter_poses(t)])
        ctr = lp.mean(axis=0)
        spread = float(max(lp[:, 0].max() - lp[:, 0].min(),
                           lp[:, 1].max() - lp[:, 1].min()))
        extent = max(7.0, spread * 0.75 + 2.5)
        key = sample_keys(st["lights"]["key"]["keys"], t, ["dir", "color", "intensity"])
        fill = sample_keys(st["lights"]["fill"]["keys"], t, ["dir", "color", "intensity"])
        wash = st["lights"]["wash"]
        scene.lights.append(R.Light(kind="directional", color=tuple(key["color"]),
                                    intensity=float(key["intensity"]), direction=tuple(key["dir"]),
                                    cast_shadow=True, shadow_extent=extent,
                                    shadow_center=tuple(float(x) for x in ctr), shadow_res=2048))
        scene.lights.append(R.Light(kind="directional", color=tuple(fill["color"]),
                                    intensity=float(fill["intensity"]), direction=tuple(fill["dir"])))
        scene.lights.append(R.Light(kind="directional", color=tuple(wash["color"]),
                                    intensity=wash["intensity"], direction=tuple(wash["dir"])))
        xl, xi = self.reveal_light(t)
        if xi > 0.01:
            scene.lights.append(R.Light(kind="point", color=tuple(slot["color"]),
                                        intensity=xi, position=(xl, 1.35, -1.10)))
        arch = pr["arch"]
        arch_i = arch["intensity"] * (0.35 + 0.65 * min(1.0, max(0.0, (t - 18.0) / 6.0)))
        scene.lights.append(R.Light(kind="point", color=tuple(arch["color"]),
                                    intensity=arch_i, position=tuple(arch["pos"])))
        rel = pr["release"]
        rel_i = rel["intensity"] * (1.0 if 15.0 <= t <= 24.0
                                    else max(0.0, 1.0 - abs(t - 19.5) / 5.0) * 0.5)
        scene.lights.append(R.Light(kind="point", color=tuple(rel["color"]),
                                    intensity=max(rel_i, 0.0), position=tuple(rel["pos"])))
        ch = pr["chamber"]
        ch_i = ch["intensity"] * max(0.0, min(1.0, (t - 27.0) / 4.0))
        scene.lights.append(R.Light(kind="point", color=tuple(ch["color"]),
                                    intensity=ch_i, position=tuple(ch["pos"])))
        return scene

    # ---------------------------------------------------------------- camera
    def camera(self, t):
        k = sample_keys(self.story["camera"]["keys"], t, ["eye", "target", "fov"])
        return R.Camera(eye=tuple(float(x) for x in k["eye"]),
                        target=tuple(float(x) for x in k["target"]),
                        fov=float(k["fov"]), near=0.05, far=260.0)

    # ------------------------------------------------------------------ loop
    def build_loop(self, t, cam=None):
        st = self.story
        w = self.w
        pal = self.pal
        pr = st["lights"]["practicals"]
        T = st["loop"]["duration_seconds"]
        a = 2.0 * math.pi * t / T
        scene = R.Scene()
        scene.ambient_sky = (0.020, 0.025, 0.036)
        scene.ambient_ground = (0.012, 0.009, 0.007)
        scene.fog_color = (0.030, 0.024, 0.021)
        scene.fog_density = 0.024

        z = w["wall_z"]
        op = w["wall_opening"]
        stone_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                               texture=self.stone, texture_uv=(1.0, 1.0))
        q = quad([-46, 0, 30], [46, 0, 30], [46, 0, -40], [-46, 0, -40],
                 normal=(0, 1, 0), uv=[(0, 0), (26, 0), (26, 35), (0, 35)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.10, shininess=26.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))
        for p, uvs in [
            (([-30, 0, z], [op["x0"], 0, z], [op["x0"], 16, z], [-30, 16, z]),
             [(0, 0), (6.0, 0), (6.0, 4.2), (0, 4.2)]),
            (([op["x1"], 0, z], [30, 0, z], [30, 16, z], [op["x1"], 16, z]),
             [(0, 0), (8.5, 0), (8.5, 4.2), (0, 4.2)]),
            (([op["x0"], op["y1"], z], [op["x1"], op["y1"], z], [op["x1"], 16, z], [op["x0"], 16, z]),
             [(0, 0), (1.0, 0), (1.0, 2.6), (0, 2.6)]),
        ]:
            q = quad(*p, normal=(0, 0, 1), uv=uvs)
            scene.meshes.append((q[0], q[1], q[2], q[3], stone_mat, False))
        pier_mat = R.Material(base=tuple(pal["stone_light"]), spec=0.05, shininess=14.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))
        for z_p in (20.0, 12.0, 4.0):
            for x_p in (-w["pier_x"], w["pier_x"]):
                scene.meshes.append((*box_mesh(x_p, 4.2, z_p, 1.4, 8.4, 1.3), pier_mat))
        bx0, bx1 = w["bench_x"]
        bz0, bz1 = w["bench_z"]
        scene.meshes.append((*box_mesh((bx0 + bx1) / 2, w["bench_h"] / 2, (bz0 + bz1) / 2,
                                       bx1 - bx0, w["bench_h"], bz1 - bz0),
                             R.Material(base=tuple(pal["stone_light"]), spec=0.07, shininess=20.0), False))
        slot = pr["slot"]
        q = quad([slot["x"] - 0.14, slot["y"][0], slot["z"]],
                 [slot["x"] + 0.14, slot["y"][0], slot["z"]],
                 [slot["x"] + 0.14, slot["y"][1], slot["z"]],
                 [slot["x"] - 0.14, slot["y"][1], slot["z"]], normal=(0, 0, 1))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0),
                                        emissive=tuple(np.array(slot["color"]) * slot["intensity"])), False))
        letter_mat = R.Material(base=tuple(pal["letter"]), spec=0.14, shininess=30.0,
                                texture=self.stone, texture_uv=(0.0016, 0.0016))
        for m, spec in zip(self.letter_meshes, self.story["letters"]):
            v = m.verts.astype(np.float64) + np.array([spec["wall_x"], w["bench_h"], w["wall_z"]])
            scene.meshes.append((v.astype(np.float32), m.normals, m.uvs, m.tris, letter_mat))
        v, n, u, t2 = blade((slot["x"], slot["y"][1], slot["z"]), (4.2, 0.0, 1.6), 2.6)
        scene.meshes.append((v, n, u, t2,
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=self.shaft_tex, additive=True,
                                        alpha=0.045, double_sided=True), False))

        th = 0.62 + 0.30 * math.sin(a)
        scene.lights.append(R.Light(kind="directional", color=(1.0, 0.76, 0.48),
                                    intensity=1.05,
                                    direction=(-math.sin(th), -0.26, -math.cos(th)),
                                    cast_shadow=True, shadow_extent=11.0,
                                    shadow_center=(4.0, 2.0, -3.4), shadow_res=2048))
        scene.lights.append(R.Light(kind="directional", color=(0.32, 0.44, 0.66), intensity=0.24,
                                    direction=(0.55, -0.26, -0.79)))
        scene.lights.append(R.Light(kind="directional", color=(0.62, 0.60, 0.58), intensity=0.08,
                                    direction=(0.10, 0.16, 0.98)))
        xl = 4.0 + 4.2 * math.cos(a)
        scene.lights.append(R.Light(kind="point", color=tuple(slot["color"]),
                                    intensity=1.6, position=(xl, 2.45, -2.30)))
        return scene

    def loop_camera(self, t):
        T = self.story["loop"]["duration_seconds"]
        a = 2.0 * math.pi * t / T
        eye = (3.6 + 1.30 * math.sin(a), 2.05 + 0.22 * math.sin(2 * a + 0.5),
               10.6 + 1.10 * math.cos(a))
        target = (3.6 + 0.35 * math.sin(a), 2.05, self.w["wall_z"])
        return R.Camera(eye=eye, target=target, fov=38.0, near=0.05, far=260.0)
