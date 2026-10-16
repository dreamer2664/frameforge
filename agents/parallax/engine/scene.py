"""Scene track evaluation for the parallax film (data-driven, editable)."""
import json
import math
from pathlib import Path

import numpy as np

import core as C


def _catmull(keys_t, keys_v, t):
    """smooth spline through key values (list of float arrays)."""
    n = len(keys_t)
    if n == 1:
        return np.asarray(keys_v[0], dtype=np.float64)
    if t <= keys_t[0]:
        return np.asarray(keys_v[0], dtype=np.float64)
    if t >= keys_t[-1]:
        return np.asarray(keys_v[-1], dtype=np.float64)
    i = max(0, min(n - 2, next(k for k in range(n - 1) if keys_t[k] <= t <= keys_t[k + 1])))
    p0 = keys_v[max(0, i - 1)]; p1 = keys_v[i]; p2 = keys_v[i + 1]; p3 = keys_v[min(n - 1, i + 2)]
    u = (t - keys_t[i]) / max(1e-9, keys_t[i + 1] - keys_t[i])
    p0 = np.asarray(p0, float); p1 = np.asarray(p1, float)
    p2 = np.asarray(p2, float); p3 = np.asarray(p3, float)
    return 0.5 * ((2 * p1) + (-p0 + p2) * u + (2 * p0 - 5 * p1 + 4 * p2 - p3) * u * u
                  + (-p0 + 3 * p1 - 3 * p2 + p3) * u ** 3)


class Scene:
    def __init__(self, path):
        self.d = json.load(open(path))
        self.fps = self.d.get("fps", 24)
        self.W = self.d.get("W", 1920)
        self.H = self.d.get("H", 1080)
        self.duration = self.d["duration"]
        self.base = Path(path).resolve().parent.parent   # agents/parallax
        self._mesh_cache = {}

    # ---- tracks
    def camera(self, t):
        ks = self.d["camera"]
        ts = [k["t"] for k in ks]
        pos = _catmull(ts, [k["pos"] for k in ks], t)
        tgt = _catmull(ts, [k["target"] for k in ks], t)
        fov = float(_catmull(ts, [[k.get("fov", 38)] for k in ks], t)[0])
        roll = float(_catmull(ts, [[k.get("roll", 0.0)] for k in ks], t)[0])
        return C.Camera(pos, tgt, fov=fov, roll=roll)

    def light(self, t):
        ks = self.d["light"]
        ts = [k["t"] for k in ks]
        pos = _catmull(ts, [k["pos"] for k in ks], t)
        energy = float(_catmull(ts, [[k.get("energy", 4.0)] for k in ks], t)[0])
        return pos, energy

    def paper(self, t):
        ks = self.d.get("paper_keys", [{"t": -1, "p": 0}, {"t": 1e9, "p": 0}])
        for a, b in zip(ks, ks[1:]):
            if a["t"] <= t <= b["t"]:
                u = (t - a["t"]) / max(1e-9, b["t"] - a["t"])
                return a["p"] + (b["p"] - a["p"]) * C.smoothstep(u)
        return ks[-1]["p"] if t > ks[-1]["t"] else ks[0]["p"]

    def palette(self, t):
        p = self.paper(t)
        ink, pap = self.d["palette"]["ink"], self.d["palette"]["paper"]
        mix = lambda k: tuple(C.lerp(a, b, p) for a, b in zip(ink[k], pap[k]))
        return dict(top=mix("top"), bottom=mix("bottom"), amb=mix("amb"),
                    ground=mix("ground"), fogd=C.lerp(ink.get("fogd", 0.016), pap.get("fogd", 0.012), p)), p

    # ---- objects
    def mesh_for(self, o):
        key = (o["kind"], o.get("text"), o.get("size"), o.get("depth"), o.get("w"), o.get("h"))
        if key not in self._mesh_cache:
            cache = str(self.base / "work" / "meshcache")
            if o["kind"] == "word":
                font = self.base / "fonts" / ("Fraunces.ttf" if o.get("font", "fraunces") == "fraunces" else "Inter-SemiBold.ttf")
                m = C.word_mesh(str(font), o["text"], o["size"], o.get("depth", 1.2), cache)
            elif o["kind"] == "portal":
                m = C.portal_mesh(o["w"], o["h"], o.get("bar", 0.7), o.get("depth", 1.0))
            elif o["kind"] == "ground":
                m = C.quad_mesh(o.get("size", 400), o.get("size", 400))
                m = C.transform_mesh(m, pos=(0, 0, -60), rot_x=-math.pi / 2)
            elif o["kind"] == "box":
                m = C.box_mesh(o["w"], o["h"], o.get("depth", 1.0))
            self._mesh_cache[key] = m
        return self._mesh_cache[key]

    def objects(self, t):
        out = []
        for o in self.d.get("objects", []):
            ks = o.get("keys", [{"t": 0}])
            ts = [k["t"] for k in ks]
            pos = _catmull(ts, [k.get("pos", [0, 0, 0]) for k in ks], t)
            rot_y = float(_catmull(ts, [[k.get("rot_y", 0.0)] for k in ks], t)[0])
            rot_x = float(_catmull(ts, [[k.get("rot_x", 0.0)] for k in ks], t)[0])
            scale = float(_catmull(ts, [[k.get("scale", 1.0)] for k in ks], t)[0])
            vis = True
            if "t0" in o:
                vis = o["t0"] <= t <= o.get("t1", 1e9)
            if not vis:
                continue
            out.append((o, pos, rot_y, rot_x, scale))
        return out

    def plates(self, t):
        out = []
        for p in self.d.get("plates", []):
            t0, t1 = p["t0"], p["t1"]
            if not (t0 - 0.01 <= t <= t1 + 0.01):
                continue
            fade = p.get("fade", 0.4)
            a = C.clamp(min((t - t0) / fade, (t1 - t) / fade, 1.0))
            if a <= 0:
                continue
            out.append((p, C.smoothstep(a)))
        return out

    def cues(self):
        return self.d.get("cues", [])
