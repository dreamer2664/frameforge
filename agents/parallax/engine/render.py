"""parallax renderer CLI: scene JSON -> PNG frames (deterministic, resumable)."""
import argparse
import math
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as C
from scene import Scene


def plate_quad(p, cam, tex_shape):
    """world quad for a plate; screen-anchored, billboard or fixed orientation."""
    th, tw = tex_shape
    aspect = tw / th
    h = p.get("h", 0.5)
    if p.get("screen") and p.get("screen_frac"):
        d0 = p.get("depth", 10.0)
        h = p["screen_frac"] * 2 * math.tan(math.radians(cam.fov) * 0.5) * d0
    q = C.quad_mesh(h * aspect, h)
    if p.get("screen"):
        d = p.get("depth", 10.0)
        fy = math.tan(math.radians(cam.fov) * 0.5) * d
        fx = fy * (16.0 / 9.0)
        cx = (p["screen"][0] * 2 - 1) * fx
        cy = (1 - p["screen"][1] * 2) * fy
        B = np.stack([cam.R[0], cam.R[1], -cam.R[2]])   # x=right y=up z=toward camera
        v = q["verts"] @ B + (cam.pos + cam.R.T @ np.array([cx, cy, d]))
        out = dict(q); out["verts"] = v
        return out
    if p.get("billboard", True):
        B = np.stack([cam.R[0], cam.R[1], -cam.R[2]])
        v = q["verts"] @ B + np.asarray(p["pos"], float)
        out = dict(q); out["verts"] = v
        return out
    q = C.transform_mesh(q, pos=p["pos"], rot_y=p.get("rot_y", 0.0), rot_x=p.get("rot_x", 0.0))
    return q


def render_frame(sc, t, W, H, samples=1):
    acc = None
    for s in range(samples):
        tt = t + (s / samples) / sc.fps if samples > 1 else t
        fb = C.Frame(W, H)
        pal, paper = sc.palette(tt)
        cam = sc.camera(tt)
        lpos, energy = sc.light(tt)
        warm = C.srgb_to_linear((255, 176, 105))
        cool = C.srgb_to_linear((150, 190, 215))
        light = dict(pos=lpos, color=warm, energy=energy, ref=sc.d.get("light_ref", 26.0),
                     fill=sc.d.get("fill", 0.22), fill_color=cool,
                     fill_dir=tuple(sc.d.get("fill_dir", [-0.45, 0.75, -0.35])))
        fog = dict(amb=C.srgb_to_linear(pal["amb"]) * 0.9,
                   color=C.srgb_to_linear(pal["bottom"]), density=pal["fogd"])
        # background + atmosphere around light screen pos
        lv = cam.to_cam(lpos[None])
        ls = None
        if lv[0, 2] > cam.near:
            pr, _ = cam.project(lv, W, H)
            ls = (pr[0, 0] / W, pr[0, 1] / H)
        C.background(fb, C.srgb_to_linear(pal["top"]), C.srgb_to_linear(pal["bottom"]),
                     ls, warm=(1.0, 0.55, 0.25), amt=sc.d.get("atmo", 0.10))
        objs = sc.objects(tt)
        solids = []
        for o, pos, ry, rx, scl in objs:
            m = sc.mesh_for(o)
            if o["kind"] != "ground":
                m = C.transform_mesh(m, pos=pos, rot_y=ry, rot_x=rx, scale=scl)
            solids.append((o, m))
        import os as _os
        sm = None
        if not _os.environ.get("PX_NOSHADOW"):
            sm = C.ShadowMap(sc.d.get("shadow_res", 640))
            occ = [(m["verts"], m["tris"]) for o, m in solids if o["kind"] in ("word", "portal", "box")]
            if occ:
                sm.build(lpos, np.mean([np.mean(v, axis=0) for v, _ in occ], axis=0), occ)
        for o, m in solids:
            if o["kind"] == "ground":
                mat = dict(albedo=C.srgb_to_linear(pal["ground"]), spec=0.05, shin=16.0)
            else:
                alb = o.get("albedo", [188, 180, 166])
                alb = tuple(C.lerp(a, b, paper) for a, b in zip(alb, o.get("albedo_paper", alb)))
                mat = dict(albedo=C.srgb_to_linear(alb), spec=o.get("spec", 0.10), shin=o.get("shin", 30.0))
                ig = o.get("ignite")
                if ig and ig["t0"] <= tt <= ig["t0"] + ig["dur"] + 1.2:
                    mat = dict(mat)
                    mat["ignite_amp"] = ig.get("amp", 0.3)
                    mat["ignite_sigma"] = ig.get("sigma", 0.55)
                    mat["ignite_col"] = C.srgb_to_linear((255, 170, 95))
            ign = m.get("ignite") if mat.get("ignite_amp") else None
            if ign is not None:
                w = m["verts"][:, 0]
                ign = ig["t0"] + ig["dur"] * np.clip((m["ignite"] - w.min()) / max(1e-6, w.max() - w.min()), 0, 1)
                # per-tri value already per tri in m['ignite']; recompute per tri:
                ign = ig["t0"] + ig["dur"] * np.clip((m["ignite"] - m["ignite"].min()) / max(1e-6, m["ignite"].max() - m["ignite"].min()), 0, 1)
            C.draw_triangles(fb, m["verts"], m["tris"], m["normals"], cam, mat, light, fog, sm,
                             ignite_t=ign, t=tt)
        # plates
        for p, alpha in sc.plates(tt):
            font = sc.base / "fonts" / ("Inter-Medium.ttf" if p.get("font", "inter") == "inter" else "Fraunces.ttf")
            tex, tcol = C.plate_texture(p["text"], str(font), p.get("px", 40),
                                        color=tuple(p.get("color", [255, 240, 220])), tracking=p.get("track", 0))
            q = plate_quad(p, cam, tex.shape)
            C.draw_plate(fb, q, tex, C.srgb_to_linear(tuple(p.get("color", [255, 240, 220]))) * 1.6,
                         cam, glow_amt=p.get("glow", 0.5), alpha=alpha)
        # light core
        if lv[0, 2] > cam.near:
            pr, _ = cam.project(lv, W, H)
            yy, xx = np.mgrid[0:H, 0:W]
            d2 = (xx - pr[0, 0]) ** 2 + (yy - pr[0, 1]) ** 2
            r2 = (W / 960.0) ** 2
            core = np.exp(-d2 / (90 * r2)) + 0.5 * np.exp(-d2 / (900 * r2))
            fb.glow += core[:, :, None] * C.srgb_to_linear((255, 190, 120))[None, None, :] * 1.6
            fb.col += core[:, :, None] * C.srgb_to_linear((255, 214, 160))[None, None, :] * 1.2
        img = C.post(fb, tt, grain=sc.d.get("grain", 1.3), vignette=sc.d.get("vignette", 0.16),
                     glow_strength=sc.d.get("glow_strength", 0.55), exposure=sc.d.get("exposure", 1.0))
        acc = img.astype(np.float32) if acc is None else acc + img.astype(np.float32)
    return (acc / samples).astype(np.uint8)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scene", required=True)
    ap.add_argument("--out", required=True, help="dir for PNG frames")
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--duration", type=float, default=None)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--fps", type=int, default=None)
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--only", default=None, help="comma list of frame indices")
    ap.add_argument("--workers", type=int, default=1)
    a = ap.parse_args()
    sc = Scene(a.scene)
    fps = a.fps or sc.fps
    W, H = int(sc.W * a.scale), int(sc.H * a.scale)
    dur = a.duration if a.duration is not None else sc.duration
    n = int(round(dur * fps))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    if a.only:
        idxs = [int(x) for x in a.only.split(",")]
    else:
        idxs = list(range(n))
    t0 = time.time()
    if a.workers > 1:
        import multiprocessing as mp
        chunks = [idxs[i::a.workers] for i in range(a.workers)]
        with mp.Pool(a.workers, initializer=_wk_init, initargs=(a.scene, W, H, a.samples, fps)) as pool:
            for _ in pool.imap_unordered(_wk_run, [(c, str(out)) for c in chunks]):
                pass
    else:
        _wk_init(a.scene, W, H, a.samples, fps)
        _wk_run((idxs, str(out)))
    dt = time.time() - t0
    print(f"rendered {len(idxs)} frames {W}x{H} in {dt:.1f}s ({dt/max(1,len(idxs)):.2f}s/frame)")


_WK = {}

def _wk_init(scene, W, H, samples, fps):
    _WK.update(sc=Scene(scene), W=W, H=H, samples=samples, fps=fps)

def _wk_run(args):
    idxs, out = args
    sc, W, H, samples, fps = _WK["sc"], _WK["W"], _WK["H"], _WK["samples"], _WK["fps"]
    for i in idxs:
        t = i / fps
        img = render_frame(sc, t, W, H, samples)
        Image.fromarray(img).save(f"{out}/f{i:05d}.png")
    return len(idxs)


if __name__ == "__main__":
    main()
