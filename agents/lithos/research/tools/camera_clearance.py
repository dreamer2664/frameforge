#!/usr/bin/env python3
"""camera_clearance.py — gate: the camera eye must keep distance from world
geometry (r01 post-mortem tool). Renders the clearance curve + path plots.

  python3 camera_clearance.py --times 0,0.25,...,42 --out clearance.json
"""
import argparse, json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'px'))
import scene as S  # noqa: E402

def point_tri_dist(P, T):
    a, b, c = T[:, 0], T[:, 1], T[:, 2]
    ab, ac, ap = b - a, c - a, P - a
    d1 = (ab * ap).sum(1); d2 = (ac * ap).sum(1)
    bp = P - b; d3 = (ab * bp).sum(1); d4 = (ac * bp).sum(1)
    cp = P - c; d5 = (ab * cp).sum(1); d6 = (ac * cp).sum(1)
    vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
    denom = va + vb + vc
    safe = np.where(denom == 0, 1.0, denom)
    v = np.clip(np.where(denom != 0, vb / safe, 0.0), 0, 1)
    w = np.clip(np.where(denom != 0, vc / safe, 0.0), 0, 1)
    s = v + w; over = s > 1; s_safe = np.where(s == 0, 1.0, s)
    v = np.where(over, v / s_safe, v); w = np.where(over, w / s_safe, w)
    closest = a + v[:, None] * ab + w[:, None] * ac
    return np.linalg.norm(P - closest, axis=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--times', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--min-clearance', type=float, default=0.6)
    a = ap.parse_args()
    times = [float(x) for x in a.times.split(',')]
    film = S.Film()
    sc = film.build_world(0.0, loop=False)
    tris = []
    for m in sc.meshes:
        v = np.asarray(m[0], float); idx = np.asarray(m[3], np.int64)
        if idx.size and v.size:
            tris.append(v[idx])
    T = np.concatenate(tris) if tris else np.zeros((0, 3, 3))
    rows = []
    for t in times:
        cam = film.camera(t)
        P = np.asarray(cam.eye, float)
        d = point_tri_dist(P, T)
        rows.append({'t': t, 'eye': [round(float(x), 3) for x in P],
                     'min_clearance_m': round(float(d.min()), 3)})
    bad = [r for r in rows if r['min_clearance_m'] < a.min_clearance]
    Path(a.out).write_text(json.dumps({'min_clearance_required': a.min_clearance,
                                       'samples': rows, 'violations': bad}, indent=1))
    print(f'samples {len(rows)}  violations {len(bad)}')
    for r in bad:
        print(' ', r['t'], r['min_clearance_m'], r['eye'])
    sys.exit(1 if bad else 0)

if __name__ == '__main__':
    main()
