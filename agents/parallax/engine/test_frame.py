"""One-frame smoke test of the parallax engine (not the film)."""
import sys, time
from pathlib import Path
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import core as C

HERE = Path(__file__).resolve().parent
FRA = HERE.parent / "fonts" / "Fraunces.ttf"
INT = HERE.parent / "fonts" / "Inter-Medium.ttf"

def main(out="work/smoke.png", W=960, H=540):
    W, H = int(W), int(H)
    t0 = time.time()
    fb = C.Frame(W, H)
    fog = dict(amb=C.srgb_to_linear((26, 30, 38)) * 0.9, color=C.srgb_to_linear((16, 19, 25)), density=0.016)
    light = dict(pos=np.array([-13.0, 9.5, -14.0]), color=C.srgb_to_linear((255, 176, 105)), energy=4.2,
                 ref=26.0, fill=0.22, fill_color=C.srgb_to_linear((150, 190, 215)), fill_dir=(-0.45, 0.75, -0.35))
    cam = C.Camera((0.0, 3.4, 4.0), (0.0, 4.6, -30.0), fov=40.0)
    C.background(fb, C.srgb_to_linear((10, 12, 16)), C.srgb_to_linear((16, 19, 25)))
    cache = str(HERE.parent / "work" / "meshcache")
    ground = C.quad_mesh(400, 400)
    ground = C.transform_mesh(ground, pos=(0, 0, -60), rot_x=-np.pi / 2)
    w1 = C.word_mesh(str(FRA), "A thought", 6.0, 1.6, cache)
    w1 = C.transform_mesh(w1, pos=(0, 6.2, -30), rot_y=0.14)
    w2 = C.word_mesh(str(FRA), "a world", 4.2, 1.2, cache)
    w2 = C.transform_mesh(w2, pos=(-14, 4.4, -52), rot_y=0.5)
    w3 = C.word_mesh(str(FRA), "line", 3.4, 1.0, cache)
    w3 = C.transform_mesh(w3, pos=(13, 3.6, -44), rot_y=-0.55)
    mat = dict(albedo=C.srgb_to_linear((188, 180, 166)), spec=0.10, shin=30.0,
               ignite_amp=0.0)
    sm = C.ShadowMap(640)
    sm.build(light["pos"], np.array([0, 4, -32.0]),
             [(w1["verts"], w1["tris"]), (w2["verts"], w2["tris"]), (w3["verts"], w3["tris"])])
    gmat = dict(albedo=C.srgb_to_linear((98, 100, 108)), spec=0.04, shin=14.0)
    C.draw_triangles(fb, ground["verts"], ground["tris"], ground["normals"], cam, gmat, light, fog, sm, t=0.0)
    for m in (w1, w2, w3):
        C.draw_triangles(fb, m["verts"], m["tris"], m["normals"], cam, mat, light, fog, sm, t=0.0)
    # light core billboard
    lv = cam.to_cam(light["pos"][None])
    if lv[0, 2] > cam.near:
        pr, _ = cam.project(lv, W, H)
        yy, xx = np.mgrid[0:H, 0:W]
        d2 = ((xx - pr[0, 0]) ** 2 + (yy - pr[0, 1]) ** 2)
        core = np.exp(-d2 / 90.0) + 0.55 * np.exp(-d2 / 900.0)
        fb.glow += core[:, :, None] * C.srgb_to_linear((255, 190, 120))[None, None, :] * 1.6
        fb.col += core[:, :, None] * C.srgb_to_linear((255, 214, 160))[None, None, :] * 1.4
    img = C.post(fb, 0.0)
    Image.fromarray(img).save(out)
    print(f"wrote {out} in {time.time()-t0:.2f}s  ({W}x{H})")

if __name__ == "__main__":
    main(*sys.argv[1:])
