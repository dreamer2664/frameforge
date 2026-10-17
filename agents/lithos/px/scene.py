#!/usr/bin/env python3
"""THE LONG LIGHT — KINETIC hero + loop scene builder (lithos).

A golden stone observatory court. The seven letters of KINETIC stand as
monumental extruded type along a shallow curve; a taller gnomon I stands at
the centre of a dial inscribed into the floor; one hard low sun sweeps ~35
degrees across the film and the shadows write the rest of the sentence.

The scene builder is a pure function of t: any frame can be regenerated.
Everything is seeded and deterministic.

Engine contract (kept from the px pipeline, rewired to this world):
  Film().build(t) -> render3d.Scene     (hero)
  Film().build_loop(t) -> render3d.Scene
  Film().camera(t) / .loop_camera(t) -> render3d.Camera
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np

import render3d as R
import type3d

HERE = Path(__file__).resolve().parent
STORY = json.loads((HERE / "storyboard.json").read_text())


# ---------------------------------------------------------------- sampling
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


def smoothstep(x):
    x = float(np.clip(x, 0.0, 1.0))
    return x * x * (3.0 - 2.0 * x)


# ---------------------------------------------------------------- textures
def glow_texture(size=256):
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    r = np.sqrt((x - size / 2) ** 2 + (y - size / 2) ** 2) / (size / 2)
    g = np.clip(1.0 - r, 0.0, 1.0) ** 2.2
    return np.stack([g, g * 0.72, g * 0.46], axis=2).astype(np.float32)


def sky_texture(size=64):
    """Vertical gradient: warm gold horizon -> cool blue zenith (v = 0 bottom)."""
    v = np.linspace(0.0, 1.0, size * 4, dtype=np.float32)
    warm = np.stack([0.62 * np.ones_like(v), 0.42 * np.ones_like(v), 0.24 * np.ones_like(v)], axis=1)
    cool = np.stack([0.10 * np.ones_like(v), 0.17 * np.ones_like(v), 0.34 * np.ones_like(v)], axis=1)
    k = (v ** 0.7)[:, None]
    grad = warm * (1 - k) + cool * k
    band = np.clip((v - 0.30) * 1.8, 0, 1)[:, None]
    grad = grad * (1 - band * 0.25)
    return np.repeat(grad[None, :, :], size, axis=0).astype(np.float32)


def stone_texture(seed=11, size=512):
    """Deterministic procedural limestone: two scales of value noise plus grain."""
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
    grain = rng.normal(0, 0.006, (size, size)).astype(np.float32)
    # faint horizontal courses: a static relief cue for the eye (handoff §2.4)
    yy = np.arange(size, dtype=np.float32)[:, None]
    course = 0.012 * (0.5 + 0.5 * np.sin(yy / (size / 9.0))) * (img > 0.45)
    tex = np.clip(img * 0.20 + blot * 0.12 + 0.62 + grain + course, 0, 1.4)
    return np.repeat(tex[:, :, None], 3, axis=2).astype(np.float32)


# ---------------------------------------------------------------- geometry
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


def box_mesh(cx, cy, cz, sx, sy, sz):
    """Axis-aligned box; world-scale UVs (metres) per face."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    c = [(cx - hx, cy - hy, cz - hz), (cx + hx, cy - hy, cz - hz),
         (cx + hx, cy + hy, cz - hz), (cx - hx, cy + hy, cz - hz),
         (cx - hx, cy - hy, cz + hz), (cx + hx, cy - hy, cz + hz),
         (cx + hx, cy + hy, cz + hz), (cx - hx, cy + hy, cz + hz)]
    faces = [
        (0, 3, 2, 1, (0, 0, -1)),
        (4, 5, 6, 7, (0, 0, 1)),
        (0, 4, 7, 3, (-1, 0, 0)),
        (1, 2, 6, 5, (1, 0, 0)),
        (0, 1, 5, 4, (0, -1, 0)),
        (3, 7, 6, 2, (0, 1, 0)),
    ]
    v, n, u, t = [], [], [], []
    for a, b, cc, d, nrm in faces:
        i = len(v)
        v.extend([c[a], c[b], c[cc], c[d]])
        n.extend([nrm] * 4)
        nax = 0 if abs(nrm[0]) > 0.5 else (1 if abs(nrm[1]) > 0.5 else 2)
        ax, ay = [i for i in range(3) if i != nax]
        u.extend([(c[p][ax], c[p][ay]) for p in (a, b, cc, d)])
        t.extend([[i, i + 1, i + 2], [i, i + 2, i + 3]])
    return (np.array(v, dtype=np.float32), np.array(n, dtype=np.float32),
            np.array(u, dtype=np.float32), np.array(t, dtype=np.int32))


def rot_xform(mesh, rx=0.0, ry=0.0, rz=0.0, offset=(0.0, 0.0, 0.0), about=None):
    """Rotate a mesh about its own centroid (or `about` point), then translate."""
    v, n, u, t = mesh
    v = v.astype(np.float64).copy()
    n = n.astype(np.float64).copy()
    cx, cy, cz = about if about is not None else (
        float(v[:, 0].mean()), float(v[:, 1].mean()), float(v[:, 2].mean()))
    Rx = np.array([[1, 0, 0],
                   [0, math.cos(rx), -math.sin(rx)],
                   [0, math.sin(rx), math.cos(rx)]])
    Ry = np.array([[math.cos(ry), 0, math.sin(ry)],
                   [0, 1, 0],
                   [-math.sin(ry), 0, math.cos(ry)]])
    Rz = np.array([[math.cos(rz), -math.sin(rz), 0],
                   [math.sin(rz), math.cos(rz), 0],
                   [0, 0, 1]])
    M = Rz @ Ry @ Rx
    v -= (cx, cy, cz)
    v = v @ M.T
    n = n @ M.T
    v += (cx, cy, cz) + np.asarray(offset, dtype=np.float64)
    return (v.astype(np.float32), n.astype(np.float32), u, t)


# ---------------------------------------------------------------- the sun
def sun_az(t):
    """Hero sun azimuth (radians) — the sundial's hand."""
    k = sample_keys(STORY["sun"]["az_keys"], t, ["az"])
    return float(k["az"])


def sun_az_loop(t):
    T = STORY["loop"]["duration_seconds"]
    a = 2.0 * math.pi * t / T
    return 0.10 + 0.05 * math.sin(a)


def sun_dir(az):
    """Travel direction of the sunlight (points FROM the sun TO the court)."""
    el = math.radians(STORY["sun"]["elevation_deg"])
    return np.array([math.sin(az) * math.cos(el), -math.sin(el),
                     math.cos(az) * math.cos(el)], dtype=np.float64)


def sun_intensity(t):
    k = sample_keys(STORY["sun"]["intensity_keys"], t, ["i"])
    return float(k["i"])


# ---------------------------------------------------------------- dial math
def gnomon_spec():
    return STORY["world"]["gnomon"]


def shadow_tip(az, height=None):
    """World XZ where the shadow tip of a height-h post lands."""
    g = gnomon_spec()
    h = height if height is not None else g["cap"]
    el = math.radians(STORY["sun"]["elevation_deg"])
    L = h / math.tan(el)
    return (g["x"] + math.sin(az) * L, g["z"] + math.cos(az) * L), L


def dial_geometry():
    """Station positions and crossing times (score sync is derived from this)."""
    d = STORY["world"]["dial"]
    out = []
    for text, tk in zip(d["stations"], d["station_times"]):
        az = sun_az(tk)
        (x, z), L = shadow_tip(az)
        out.append({"text": text, "t": tk, "az": az, "x": x, "z": z, "radius": L})
    (x, z), L = shadow_tip(sun_az(d["terminus_time"]))
    out.append({"text": d["terminus_text"], "t": d["terminus_time"],
                "az": sun_az(d["terminus_time"]), "x": x, "z": z, "radius": L})
    return out


# ---------------------------------------------------------------- type
FONT_DISPLAY = str(HERE / STORY["type"]["display"]["file"])
FONT_INSCR = str(HERE / STORY["type"]["inscription"]["file"])


def text_mesh(text, font_path, wght=700, wdth=100, depth=0.12, cap_height=None,
              tracking=0.0):
    return type3d.text_mesh(text, font_path, wght=wght, wdth=wdth,
                            depth=depth, cap_height=cap_height, tracking=tracking)


def word_layout():
    """Lay the seven monuments out along a shallow curve with true advances."""
    w = STORY["world"]
    caps, depth, gap = w["letter_cap"], w["letter_depth"], w["letter_gap"]
    specs = []
    total = 0.0
    for ch in "KINETIC":
        m, adv = text_mesh(ch, FONT_DISPLAY, wght=STORY["type"]["display"]["wght"],
                           wdth=STORY["type"]["display"]["wdth"],
                           cap_height=caps, depth=depth)
        specs.append({"ch": ch, "mesh": m, "adv": adv})
        total += adv
    total += gap * (len(specs) - 1)
    x = -total / 2.0
    for s in specs:
        s["cx"] = x + s["adv"] / 2.0
        x += s["adv"] + gap
        s["cz"] = w["word_z"] - w["word_curve"] * s["cx"] ** 2
        s["yaw"] = math.radians(-0.62 * s["cx"])
    return specs


class Film:
    def __init__(self):
        self.story = STORY
        self.w = STORY["world"]
        self.pal = STORY["palette"]
        self.stone = stone_texture()
        self.sky_tex = sky_texture()
        self.glow_tex = glow_texture()
        self.word = word_layout()
        g = self.w["gnomon"]
        self.gnomon_mesh, _ = text_mesh("I", FONT_DISPLAY,
                                        wght=STORY["type"]["display"]["wght"],
                                        wdth=STORY["type"]["display"]["wdth"],
                                        cap_height=g["cap"], depth=g["depth"])
        self._inscr_cache = {}

    # -------------------------------------------------------------- helpers
    def _inscription_mesh(self, text, cap, depth):
        key = (text, cap, depth)
        if key not in self._inscr_cache:
            self._inscr_cache[key] = text_mesh(
                text, FONT_INSCR, wght=STORY["type"]["inscription"]["wght"],
                wdth=STORY["type"]["inscription"]["wdth"],
                cap_height=cap, depth=depth, tracking=0.04)
        return self._inscr_cache[key]

    def sun(self, t, loop=False):
        az = sun_az_loop(t) if loop else sun_az(t)
        d = sun_dir(az)
        if loop:
            i = 2.15
        else:
            i = sun_intensity(t)
        col = np.array(self.pal["sun"], float) * (1.0 - 0.22 * smoothstep((t - 4.0) / 38.0)) + \
            np.array(self.pal["sun_late"], float) * (0.22 * smoothstep((t - 4.0) / 38.0))
        return d, tuple(col), i

    # --------------------------------------------------------------- world
    def build_world(self, t, loop=False):
        st, w, pal = self.story, self.w, self.pal
        scene = R.Scene()
        scene.ambient_sky = tuple(st["lights"]["ambient_sky"])
        scene.ambient_ground = tuple(st["lights"]["ambient_ground"])
        fog = sample_keys(st["fog"]["keys"], t, ["color", "density"])
        scene.fog_color = tuple(float(x) for x in fog["color"])
        scene.fog_density = float(fog["density"])

        stone_mat = R.Material(base=tuple(pal["limestone"]), spec=0.10, shininess=26.0,
                               texture=self.stone, texture_uv=(0.35, 0.35))
        letter_mat = R.Material(base=tuple(pal["letter_stone"]), spec=0.12, shininess=30.0,
                                texture=self.stone, texture_uv=(0.55, 0.55))
        basalt_mat = R.Material(base=tuple(pal["basalt"]), spec=0.16, shininess=40.0)
        valley_mat = R.Material(base=tuple(pal["valley"]), spec=0.03, shininess=8.0)

        # ---- valley below the platform (far ground)
        q = quad([-460, w["valley_y"], -420], [460, w["valley_y"], -420],
                 [460, w["valley_y"], 420], [-460, w["valley_y"], 420], normal=(0, 1, 0),
                 uv=[(0, 0), (60, 0), (60, 60), (0, 60)])
        scene.meshes.append((q[0], q[1], q[2], q[3], valley_mat, False))

        # ---- the court platform
        px0, px1 = w["platform"]["x"]
        pz0, pz1 = w["platform"]["z"]
        eh = w["platform"]["edge_h"]
        scene.meshes.append((*box_mesh((px0 + px1) / 2, -eh / 2, (pz0 + pz1) / 2,
                                       px1 - px0, eh, pz1 - pz0), stone_mat, False))

        # ---- distant hills: three hazed ridges
        for hx, hz, hh in w["hills"]:
            scene.meshes.append((*box_mesh(hx, w["valley_y"] + hh / 2 - 1.0, hz,
                                           260.0, hh, 26.0), valley_mat, False))

        # ---- sky dome (inverted box, emissive gradient)
        s = w["sky_size"]
        sky_mat = R.Material(base=(0, 0, 0), emissive=(0.30, 0.26, 0.23),
                             texture=self.sky_tex, texture_uv=(1.0, 1.0),
                             double_sided=True)
        for nrm, pts in [
            ((0, -1, 0), [(-s, s, s), (s, s, s), (s, s, -s), (-s, s, -s)]),          # ceiling
            ((0, 0, 1), [(-s, -s, -s), (s, -s, -s), (s, s, -s), (-s, s, -s)]),       # north
            ((0, 0, -1), [(s, -s, s), (-s, -s, s), (-s, s, s), (s, s, s)]),          # south
            ((1, 0, 0), [(-s, -s, s), (-s, -s, -s), (-s, s, -s), (-s, s, s)]),       # west
            ((-1, 0, 0), [(s, -s, -s), (s, -s, s), (s, s, s), (s, s, -s)]),          # east
        ]:
            q = quad(*pts, normal=nrm, uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
            scene.meshes.append((q[0], q[1], q[2], q[3], sky_mat, False))

        # ---- sun glow (restrained additive billboard at the sun direction)
        d, col, inten = self.sun(t, loop=loop)
        sun_pos = -d * 300.0 + np.array([0.0, 40.0, 0.0])
        gz = 70.0
        q = quad([sun_pos[0] - gz, sun_pos[1] - gz, sun_pos[2]],
                 [sun_pos[0] + gz, sun_pos[1] - gz, sun_pos[2]],
                 [sun_pos[0] + gz, sun_pos[1] + gz, sun_pos[2]],
                 [sun_pos[0] - gz, sun_pos[1] + gz, sun_pos[2]], normal=(0, 0, 1))
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=self.glow_tex, additive=True,
                                        alpha=0.12, double_sided=True), False))

        # ---- colonnade: piers + lintel (near occluders)
        pier_x, pier_z = w["colonnade"]["x"], w["colonnade"]["z"]
        pw, ph, pd = w["colonnade"]["pier"]
        for x_p in pier_x:
            scene.meshes.append((*box_mesh(x_p, ph / 2, pier_z, pw, ph, pd), stone_mat, True))
        for x_p in (min(pier_x), max(pier_x)):
            span = max(pier_x) - min(pier_x) + 8.0
        # lintel beams over each run
        scene.meshes.append((*box_mesh(-21.0, w["colonnade"]["lintel_y"], pier_z,
                                       16.5, 1.3, 2.4), stone_mat, True))
        scene.meshes.append((*box_mesh(21.0, w["colonnade"]["lintel_y"], pier_z,
                                       16.5, 1.3, 2.4), stone_mat, True))

        # ---- low parapet behind the colonnade line (camera-side edge)
        scene.meshes.append((*box_mesh(0.0, 0.45, pz1 - 2.0, px1 - px0, 0.9, 0.8),
                             stone_mat, True))

        # ---- the seven monuments
        for s in self.word:
            m = s["mesh"]
            mesh = rot_xform((m.verts, m.normals, m.uvs, m.tris),
                             ry=s["yaw"], about=(float(m.verts[:, 0].mean()),
                                                 float(m.verts[:, 1].mean()),
                                                 float(m.verts[:, 2].mean())))
            v = mesh[0].copy()
            # centre the glyph footprint on (cx, cz), stand it on the floor
            v[:, 0] += s["cx"] - float(v[:, 0].mean())
            v[:, 2] += s["cz"] - float(v[:, 2].mean())
            v[:, 1] -= float(v[:, 1].min())
            scene.meshes.append((v, mesh[1], mesh[2], mesh[3], letter_mat, True))

        # ---- the gnomon I
        g = w["gnomon"]
        m = self.gnomon_mesh
        v = m.verts.copy()
        v[:, 0] += g["x"] - float((v[:, 0].min() + v[:, 0].max()) / 2)
        v[:, 2] += g["z"] - float((v[:, 2].min() + v[:, 2].max()) / 2)
        v[:, 1] -= float(v[:, 1].min())
        scene.meshes.append((v, m.normals, m.uvs, m.tris, letter_mat, True))

        # ---- dial inscriptions (basalt inlay, shallow, flat on the floor)
        for stn in dial_geometry():
            cap = (w["dial"]["terminus_cap"] if "in motion" in stn["text"]
                   else w["dial"]["station_cap"])
            m, adv = self._inscription_mesh(stn["text"], cap, w["dial"]["station_depth"])
            mesh = rot_xform((m.verts, m.normals, m.uvs, m.tris),
                             rx=math.radians(-90.0),
                             about=(float(m.verts[:, 0].mean()),
                                    float(m.verts[:, 1].mean()),
                                    float(m.verts[:, 2].mean())))
            v = mesh[0].copy()
            v[:, 0] += stn["x"] - float(v[:, 0].mean())
            v[:, 2] += stn["z"] - float(v[:, 2].mean())
            v[:, 1] += 0.02 - float(v[:, 1].mean())
            scene.meshes.append((v, mesh[1], mesh[2], mesh[3], basalt_mat, False))

        # ---- the C pavilion: type as a building (we start inside its bite)
        cp = w["cpavilion"]
        m, adv = text_mesh("C", FONT_DISPLAY, wght=STORY["type"]["display"]["wght"],
                           wdth=STORY["type"]["display"]["wdth"],
                           cap_height=cp["cap"], depth=cp["depth"])
        mesh = rot_xform((m.verts, m.normals, m.uvs, m.tris),
                         ry=math.radians(cp["yaw_deg"]),
                         about=(float(m.verts[:, 0].mean()), float(m.verts[:, 1].mean()),
                                float(m.verts[:, 2].mean())))
        v = mesh[0].copy()
        v[:, 0] += cp["x"] - float(v[:, 0].mean())
        v[:, 2] += cp["z"] - float(v[:, 2].mean())
        v[:, 1] -= float(v[:, 1].min())
        scene.meshes.append((v, mesh[1], mesh[2], mesh[3], letter_mat, True))

        # ---- lights
        scene.lights.append(R.Light(kind="directional", color=col, intensity=inten,
                                    direction=tuple(d), cast_shadow=True,
                                    shadow_extent=50.0, shadow_center=(0.0, 2.0, 4.0),
                                    shadow_res=2048))
        fl = st["lights"]["sky_fill"]
        scene.lights.append(R.Light(kind="directional", color=tuple(fl["color"]),
                                    intensity=fl["intensity"], direction=tuple(fl["dir"])))
        bo = st["lights"]["bounce"]
        scene.lights.append(R.Light(kind="directional", color=tuple(bo["color"]),
                                    intensity=bo["intensity"], direction=tuple(bo["dir"])))
        return scene

    def build(self, t, cam=None):
        return self.build_world(t, loop=False)

    def build_loop(self, t, cam=None):
        return self.build_world(t, loop=True)

    # -------------------------------------------------------------- camera
    def camera(self, t):
        k = sample_keys(self.story["camera"]["keys"], t, ["eye", "target", "fov"])
        return R.Camera(eye=tuple(float(x) for x in k["eye"]),
                        target=tuple(float(x) for x in k["target"]),
                        fov=float(k["fov"]), near=0.08, far=900.0)

    def loop_camera(self, t):
        T = self.story["loop"]["duration_seconds"]
        a = 2.0 * math.pi * t / T
        eye = (-11.2 + 1.15 * math.sin(a), 3.1 + 0.30 * math.sin(2 * a),
               13.8 + 1.05 * math.cos(a))
        target = (0.6 + 0.25 * math.sin(a), 1.6, 6.0 + 0.35 * math.cos(a))
        return R.Camera(eye=eye, target=target, fov=42.0, near=0.08, far=900.0)
