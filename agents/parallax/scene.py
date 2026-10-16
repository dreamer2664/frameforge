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
                 width: int = 100, glow: float = 8.0) -> np.ndarray:
    """White RGBA lettering on transparent, returned as float32 (h,w,4)."""
    path = str(HERE / STORY["type"]["caption"]["file"])
    font = ImageFont.truetype(path, size)
    try:
        font.set_variation_by_axes([float(weight), float(width)])
    except Exception:
        pass
    img = Image.new("RGBA", (size * 4, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = 40
    y = int(size * 0.76)
    for ch in text:
        d.text((x, y), ch, fill=(255, 255, 255, 255), font=font, anchor="ls")
        x += int(d.textlength(ch, font=font)) + int(tracking * size)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    if glow > 0:
        blur = img.filter(ImageFilter.GaussianBlur(glow))
        a = Image.new("RGBA", img.size, (255, 255, 255, 0))
        a = Image.alpha_composite(a, blur)
        a = Image.alpha_composite(a, img)
        img = a
    arr = np.asarray(img).astype(np.float32) / 255.0
    return arr


@lru_cache(maxsize=8)
def soft_rect_texture(size=256, feather=0.34, warm=(1.0, 0.74, 0.46)) -> np.ndarray:
    """A soft-edged rectangle used for the pool of light on the floor."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    u = np.abs((xx / (size - 1)) * 2 - 1)
    v = np.abs((yy / (size - 1)) * 2 - 1)
    m = np.clip(1.0 - (u ** 6 + v ** 6) / 2.0, 0, 1)
    m = m ** 1.6
    tex = np.repeat(m[:, :, None], 3, axis=2) * np.asarray(warm, np.float32)[None, None, :]
    return tex.astype(np.float32)


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
    grain = rng.normal(0, 0.022, (size, size)).astype(np.float32)
    tex = np.clip(img * 0.22 + blot * 0.12 + 0.62 + grain, 0, 1.4)
    return np.repeat(tex[:, :, None], 3, axis=2).astype(np.float32)


def box_mesh(cx, cy, cz, sx, sy, sz):
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    v = np.array([[cx - hx, cy - hy, cz - hz], [cx + hx, cy - hy, cz - hz],
                  [cx + hx, cy + hy, cz - hz], [cx - hx, cy + hy, cz - hz],
                  [cx - hx, cy - hy, cz + hz], [cx + hx, cy - hy, cz + hz],
                  [cx + hx, cy + hy, cz + hz], [cx - hx, cy + hy, cz + hz]], dtype=np.float32)
    n = np.array([[0, 0, -1], [0, 0, -1], [0, 0, -1], [0, 0, -1],
                  [0, 0, 1], [0, 0, 1], [0, 0, 1], [0, 0, 1]], dtype=np.float32)
    u = np.tile(np.array([[0, 0], [1, 0], [1, 2], [0, 2]], np.float32), (2, 1))
    t = np.array([[0, 1, 2], [0, 2, 3], [4, 6, 5], [4, 7, 6],
                  [0, 4, 5], [0, 5, 1], [3, 2, 6], [3, 6, 7]], np.int32)
    return v, n, u, t


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
            wall = {"pos": np.array([spec["wall_x"], w["plinth_h"], w["wall_z"]]),
                    "rot": np.array([0.0, 0.0, 0.0])}
            tip = {"pos": np.array([spec["wall_x"] * 0.92, w["plinth_h"] + 0.3, w["wall_z"] + 1.25]),
                   "rot": np.array([math.radians(50.0), math.radians(-6.0 + 2.4 * i), 0.0])}
            field_z = 2.2 - 0.95 * i
            field_x = spec["wall_x"] * 0.72 + 0.4 * math.sin(i * 1.7)
            field = {"pos": np.array([field_x, w["plinth_h"] + 0.5 + 0.3 * (i % 3), field_z]),
                     "rot": np.array([math.radians(22.0 - 5.0 * (i % 3)),
                                      math.radians(-9.0 + 3.6 * i),
                                      math.radians(1.5 * (i - 2.5))])}
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

    # ------------------------------------------------------------------ scene
    def build(self, t, cam=None):
        st = self.story
        w = self.w
        pal = self.pal
        scene = R.Scene()
        scene.ambient_sky = (0.022, 0.027, 0.040)
        scene.ambient_ground = (0.013, 0.010, 0.008)
        scene.ambient_intensity = 1.0
        fog = sample_keys(st["fog"]["keys"], t, ["color", "density"])
        scene.fog_color = tuple(float(x) for x in fog["color"])
        scene.fog_density = float(fog["density"])

        # ---- floor
        q = quad([-46, 0, 26], [46, 0, 26], [46, 0, -40], [-46, 0, -40],
                 normal=(0, 1, 0), uv=[(0, 0), (26, 0), (26, 33), (0, 33)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.10, shininess=26.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))

        # ---- partition wall with a doorway opening
        op = w["wall_opening"]
        z = w["wall_z"]
        wall_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))
        for p in [
            ([-30, 0, z], [-30, 16, z], [op["x0"], 16, z], [op["x0"], 0, z]),
            ([op["x1"], 0, z], [op["x1"], 16, z], [30, 16, z], [30, 0, z]),
            ([op["x0"], op["y1"], z], [op["x1"], op["y1"], z], [op["x1"], 16, z], [op["x0"], 16, z]),
        ]:
            q = quad(*p, normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 3.2), (0, 3.2)])
            scene.meshes.append((q[0], q[1], q[2], q[3], wall_mat, False))

        # ---- piers along the hall
        pier_mat = R.Material(base=tuple(pal["stone_light"]), spec=0.05, shininess=14.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))
        for z_p in (16.0, 9.0, 2.0, -2.6):
            for x_p in (-7.6, 7.6):
                scene.meshes.append((*box_mesh(x_p, 4.2, z_p, 1.5, 8.4, 1.4), pier_mat))

        # ---- plinth under the carved word
        q = quad([-7.6, 0, z + 0.35], [7.6, 0, z + 0.35], [7.6, w["plinth_h"], z + 0.35],
                 [-7.6, w["plinth_h"], z + 0.35], normal=(0, 0, 1),
                 uv=[(0, 0), (3, 0), (3, 0.5), (0, 0.5)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone_light"]), spec=0.08, shininess=20.0,
                                        texture=self.stone, texture_uv=(0.5, 0.5)), False))

        # ---- the slit of light above the doorway
        pr = st["lights"]["practicals"]
        slit = pr["slit"]
        q = quad([-slit["size"][0] / 2, slit["pos"][1], slit["pos"][2] - 0.02],
                 [slit["size"][0] / 2, slit["pos"][1], slit["pos"][2] - 0.02],
                 [slit["size"][0] / 2, slit["pos"][1] + slit["size"][1], slit["pos"][2] - 0.02],
                 [-slit["size"][0] / 2, slit["pos"][1] + slit["size"][1], slit["pos"][2] - 0.02],
                 normal=(0, 0, 1))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0),
                                        emissive=tuple(np.array(slit["color"]) * slit["intensity"])), False))

        # ---- the letters
        letter_mat = R.Material(base=tuple(pal["letter"]), spec=0.12, shininess=30.0,
                                texture=self.stone, texture_uv=(0.35, 0.35))
        for m, pose in zip(self.letter_meshes, self.letter_poses(t)):
            R3 = euler_matrix(*pose["rot"])
            v = m.verts.astype(np.float64) @ R3.T + pose["pos"]
            scene.meshes.append((v.astype(np.float32),
                                 (m.normals.astype(np.float64) @ R3.T).astype(np.float32),
                                 m.uvs, m.tris, letter_mat))

        # ---- chamber plinth
        q = quad([-7.4, 0, -13.30], [7.4, 0, -13.30], [7.4, 1.20, -13.30], [-7.4, 1.20, -13.30],
                 normal=(0, 0, 1), uv=[(0, 0), (3, 0), (3, 0.5), (0, 0.5)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone_light"]), spec=0.08, shininess=20.0,
                                        texture=self.stone, texture_uv=(0.5, 0.5)), False))
        q = quad([-7.4, 1.20, -15.6], [7.4, 1.20, -15.6], [7.4, 1.20, -13.30], [-7.4, 1.20, -13.30],
                 normal=(0, 1, 0), uv=[(0, 0), (3, 0), (3, 0.5), (0, 0.5)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.06, shininess=18.0,
                                        texture=self.stone, texture_uv=(0.5, 0.5)), False))

        # ---- pool of light on the floor under the slit
        pool = pr["pool"]
        q = quad([pool["pos"][0] - pool["size"][0] / 2, 0.012, pool["pos"][2] - pool["size"][1] / 2],
                 [pool["pos"][0] + pool["size"][0] / 2, 0.012, pool["pos"][2] - pool["size"][1] / 2],
                 [pool["pos"][0] + pool["size"][0] / 2, 0.012, pool["pos"][2] + pool["size"][1] / 2],
                 [pool["pos"][0] - pool["size"][0] / 2, 0.012, pool["pos"][2] + pool["size"][1] / 2],
                 normal=(0, 1, 0))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=self.pool_tex, additive=True,
                                        alpha=pool["intensity"], double_sided=True), False))

        # ---- light shaft (camera-facing volume between the slit and the floor)
        if cam is not None:
            eye = np.asarray(cam.eye, float)
            c = np.array([0.0, 3.6, 0.2])
            fwd = c - eye
            fwd[1] = 0.0
            n = np.linalg.norm(fwd)
            fwd = fwd / n if n > 1e-6 else np.array([0.0, 0.0, -1.0])
            right = np.cross(fwd, np.array([0.0, 1.0, 0.0]))
            right = right / max(np.linalg.norm(right), 1e-6)
            for k, (wdt, hgt, al) in enumerate(((7.4, 7.6, 0.30), (5.2, 7.4, 0.22), (3.0, 7.2, 0.16))):
                corners = [c - right * wdt / 2 + np.array([0, hgt / 2, 0]),
                           c + right * wdt / 2 + np.array([0, hgt / 2, 0]),
                           c + right * wdt / 2 + np.array([0, -hgt / 2, 0]),
                           c - right * wdt / 2 + np.array([0, -hgt / 2, 0])]
                v = np.array(corners, dtype=np.float32)
                u = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
                t2 = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
                nn = np.tile(-fwd.astype(np.float32), (4, 1))
                scene.meshes.append((v, nn, u, t2,
                                     R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                                texture=self.shaft_tex, additive=True,
                                                alpha=al, double_sided=True), False))

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
            u = np.array([[0, 0], [1, 0], [1, 1], [0, 1]], dtype=np.float32)
            t2 = np.array([[0, 1, 2], [0, 2, 3]], dtype=np.int32)
            n = np.tile(np.array([0, 0, 1], np.float32), (4, 1))
            scene.meshes.append((v, n, u, t2,
                                 R.Material(base=(0, 0, 0), emissive=(0, 0, 0), texture=tex,
                                            additive=True, alpha=float(fade) * 0.95,
                                            double_sided=True), False))

        # ---- lights
        key = sample_keys(st["lights"]["key"]["keys"], t, ["dir", "color", "intensity"])
        fill = sample_keys(st["lights"]["fill"]["keys"], t, ["dir", "color", "intensity"])
        wash = st["lights"]["wash"]
        scene.lights.append(R.Light(kind="directional", color=tuple(key["color"]),
                                    intensity=float(key["intensity"]), direction=tuple(key["dir"]),
                                    cast_shadow=True, shadow_extent=14.0,
                                    shadow_center=(0.0, 2.2, -5.0), shadow_res=1024))
        scene.lights.append(R.Light(kind="directional", color=tuple(fill["color"]),
                                    intensity=float(fill["intensity"]), direction=tuple(fill["dir"])))
        scene.lights.append(R.Light(kind="directional", color=tuple(wash["color"]),
                                    intensity=wash["intensity"], direction=tuple(wash["dir"])))
        scene.lights.append(R.Light(kind="point", color=tuple(slit["color"]),
                                    intensity=slit["intensity"] * 0.9, position=tuple(slit["pos"])))
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
                        fov=float(k["fov"]), near=0.05, far=220.0)

    # ------------------------------------------------------------------ loop
    def build_loop(self, t, cam=None):
        st = self.story
        w = self.w
        pal = self.pal
        T = st["loop"]["duration_seconds"]
        a = 2.0 * math.pi * t / T
        scene = R.Scene()
        scene.ambient_sky = (0.020, 0.025, 0.036)
        scene.ambient_ground = (0.012, 0.009, 0.007)
        scene.fog_color = (0.030, 0.024, 0.021)
        scene.fog_density = 0.024
        q = quad([-46, 0, 26], [46, 0, 26], [46, 0, -40], [-46, 0, -40],
                 normal=(0, 1, 0), uv=[(0, 0), (26, 0), (26, 33), (0, 33)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.10, shininess=26.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))
        op = w["wall_opening"]
        z = w["wall_z"]
        wall_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))
        for p in [
            ([-30, 0, z], [-30, 16, z], [op["x0"], 16, z], [op["x0"], 0, z]),
            ([op["x1"], 0, z], [op["x1"], 16, z], [30, 16, z], [30, 0, z]),
            ([op["x0"], op["y1"], z], [op["x1"], op["y1"], z], [op["x1"], 16, z], [op["x0"], 16, z]),
        ]:
            q = quad(*p, normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 3.2), (0, 3.2)])
            scene.meshes.append((q[0], q[1], q[2], q[3], wall_mat, False))
        letter_mat = R.Material(base=tuple(pal["letter"]), spec=0.12, shininess=30.0,
                                texture=self.stone, texture_uv=(0.35, 0.35))
        for m, spec in zip(self.letter_meshes, self.story["letters"]):
            v = m.verts.astype(np.float64) + np.array([spec["wall_x"], w["plinth_h"], w["wall_z"]])
            scene.meshes.append((v.astype(np.float32), m.normals, m.uvs, m.tris, letter_mat))
        q = quad([-7.6, 0, z + 0.35], [7.6, 0, z + 0.35], [7.6, w["plinth_h"], z + 0.35],
                 [-7.6, w["plinth_h"], z + 0.35], normal=(0, 0, 1),
                 uv=[(0, 0), (3, 0), (3, 0.5), (0, 0.5)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone_light"]), spec=0.08, shininess=20.0,
                                        texture=self.stone, texture_uv=(0.5, 0.5)), False))
        slit = st["lights"]["practicals"]["slit"]
        q = quad([-slit["size"][0] / 2, slit["pos"][1], slit["pos"][2] - 0.02],
                 [slit["size"][0] / 2, slit["pos"][1], slit["pos"][2] - 0.02],
                 [slit["size"][0] / 2, slit["pos"][1] + slit["size"][1], slit["pos"][2] - 0.02],
                 [-slit["size"][0] / 2, slit["pos"][1] + slit["size"][1], slit["pos"][2] - 0.02],
                 normal=(0, 0, 1))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0),
                                        emissive=tuple(np.array(slit["color"]) * slit["intensity"])), False))
        lx = 0.88 * math.cos(a) - 0.05
        lz = 0.46 + 0.14 * math.sin(a)
        scene.lights.append(R.Light(kind="directional", color=(1.0, 0.78, 0.52),
                                    intensity=1.05, direction=(lx, -0.24, lz),
                                    cast_shadow=True, shadow_extent=14.0,
                                    shadow_center=(0.0, 2.2, -5.0), shadow_res=1024))
        scene.lights.append(R.Light(kind="directional", color=(0.32, 0.44, 0.66), intensity=0.28,
                                    direction=(-0.55, -0.30, -0.78)))
        scene.lights.append(R.Light(kind="directional", color=(0.62, 0.60, 0.58), intensity=0.09,
                                    direction=(0.10, 0.16, 0.98)))
        scene.lights.append(R.Light(kind="point", color=tuple(slit["color"]),
                                    intensity=slit["intensity"] * 2.4, position=tuple(slit["pos"])))
        return scene

    def loop_camera(self, t):
        T = self.story["loop"]["duration_seconds"]
        a = 2.0 * math.pi * t / T
        eye = (1.3 + 1.15 * math.sin(a), 1.62 + 0.20 * math.sin(2 * a + 0.5),
               6.8 + 0.8 * math.cos(a))
        target = (0.0 + 0.25 * math.sin(a), 1.95, self.w["wall_z"])
        return R.Camera(eye=eye, target=target, fov=36.0, near=0.05, far=220.0)
