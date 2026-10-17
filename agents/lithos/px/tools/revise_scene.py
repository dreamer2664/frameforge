#!/usr/bin/env python3
"""Revision 2 — material, light and type readability.

Applies the art-direction fixes to scene.py:

  1. the carved wall gets its own (brighter) stone material and a grazing
     "rake" light, so the word sits in lit stone instead of a black void;
  2. the chamber behind the arch becomes a room with a floor, wider walls and
     a graded back wall instead of a flat cream card;
  3. the plinth/bench/piers use world-scale UVs (no more smeared wood grain);
  4. copy that is too close to the lens fades out instead of filling the frame;
  5. the practical light windows follow the re-timed cut.
"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "scene.py"
s = P.read_text()
orig = s


def sub(old, new, count=1):
    global s
    if s.count(old) < count:
        raise SystemExit("PATTERN NOT FOUND:\n" + old[:200])
    s = s.replace(old, new, count)


# ---------------------------------------------------------------- 1. wall material
sub('''        stone_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                               texture=self.stone, texture_uv=(1.0, 1.0))

        # ---- floor''',
    '''        stone_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                               texture=self.stone, texture_uv=(1.0, 1.0))
        # the wall carries the word: it must read as lit stone, not as a void
        wall_mat = R.Material(base=tuple(pal["wall"]), spec=0.09, shininess=20.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))

        # ---- floor''')

# the wall pieces in build() use the wall material
sub('''            q = quad(*p, normal=(0, 0, 1), uv=uvs)
            scene.meshes.append((q[0], q[1], q[2], q[3], stone_mat, False))

        # ---- piers flanking the hall''',
    '''            q = quad(*p, normal=(0, 0, 1), uv=uvs)
            scene.meshes.append((q[0], q[1], q[2], q[3], wall_mat, False))

        # ---- piers flanking the hall''')

# ... and the same wall in build_loop()
sub('''        stone_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                               texture=self.stone, texture_uv=(1.0, 1.0))
        q = quad([-46, 0, 30], [46, 0, 30], [46, 0, -40], [-46, 0, -40],''',
    '''        stone_mat = R.Material(base=tuple(pal["stone"]), spec=0.07, shininess=18.0,
                               texture=self.stone, texture_uv=(1.0, 1.0))
        wall_mat = R.Material(base=tuple(pal["wall"]), spec=0.09, shininess=20.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))
        q = quad([-46, 0, 30], [46, 0, 30], [46, 0, -40], [-46, 0, -40],''')

sub('''            q = quad(*p, normal=(0, 0, 1), uv=uvs)
            scene.meshes.append((q[0], q[1], q[2], q[3], stone_mat, False))
        pier_mat''',
    '''            q = quad(*p, normal=(0, 0, 1), uv=uvs)
            scene.meshes.append((q[0], q[1], q[2], q[3], wall_mat, False))
        pier_mat''')

# ---------------------------------------------------------------- 2. chamber = a room
sub('''        # ---- the chamber behind the arch
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
                                        texture=self.glow_tex, additive=True, alpha=0.30), False))''',
    '''        # ---- the chamber behind the arch: a room, not a lit card
        cz = w.get("chamber_z", -34.0)
        cx = w.get("chamber_x", 20.0)
        ch_h = w.get("chamber_h", 13.0)
        chamber_mat = R.Material(base=tuple(pal["stone"]), spec=0.05, shininess=14.0,
                                 texture=self.stone, texture_uv=(1.0, 1.0),
                                 emissive=(0.030, 0.017, 0.008))
        q = quad([-cx, 0, cz], [cx, 0, cz], [cx, ch_h, cz], [-cx, ch_h, cz], normal=(0, 0, 1),
                 uv=[(0, 0), (cx, 0), (cx, ch_h), (0, ch_h)])
        scene.meshes.append((q[0], q[1], q[2], q[3], chamber_mat, False))
        for x_s in (-cx, cx):
            q = quad([x_s, 0, cz], [x_s, 0, -4], [x_s, ch_h, -4], [x_s, ch_h, cz],
                     normal=(-1 if x_s > 0 else 1, 0, 0), uv=[(0, 0), (8, 0), (8, ch_h), (0, ch_h)])
            scene.meshes.append((q[0], q[1], q[2], q[3], chamber_mat, False))
        q = quad([-cx, ch_h, cz], [cx, ch_h, cz], [cx, ch_h, -4], [-cx, ch_h, -4],
                 normal=(0, -1, 0), uv=[(0, 0), (cx, 0), (cx, 8), (0, 8)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.02, shininess=8.0,
                                        emissive=(0.020, 0.011, 0.005)), False))
        # floor of the chamber, catching the warm light
        q = quad([-cx, 0.01, cz], [cx, 0.01, cz], [cx, 0.01, -4], [-cx, 0.01, -4],
                 normal=(0, 1, 0), uv=[(0, 0), (cx, 0), (cx, 8), (0, 8)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=tuple(pal["stone"]), spec=0.10, shininess=26.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))

        # ---- graded warm glow deep in the chamber (seen through the arch)
        q = quad([-cx + 1, 0, cz + 0.12], [cx - 1, 0, cz + 0.12],
                 [cx - 1, ch_h - 1, cz + 0.12], [-cx + 1, ch_h - 1, cz + 0.12],
                 normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0.34, 0.19, 0.085),
                                        texture=self.glow_tex, additive=True, alpha=0.20), False))''')

# ---------------------------------------------------------------- 3. plinth material
sub('''        scene.meshes.append((*box_mesh(0.0, w["plinth_h"] / 2, (pz0 + pz1) / 2,
                                       13.4, w["plinth_h"], pz1 - pz0),
                             R.Material(base=tuple(pal["stone_light"]), spec=0.08, shininess=20.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))''',
    '''        scene.meshes.append((*box_mesh(0.0, w["plinth_h"] / 2, (pz0 + pz1) / 2,
                                       13.4, w["plinth_h"], pz1 - pz0),
                             R.Material(base=tuple(pal.get("plinth", pal["stone_light"])),
                                        spec=0.08, shininess=20.0,
                                        texture=self.stone, texture_uv=(1.0, 1.0)), False))''')

# ---------------------------------------------------------------- 4. copy near-camera fade
sub('''            tex = self.copy_textures[(c["text"], c.get("small", False))]''',
    '''            if cam is not None:
                # copy written on stone is unreadable when the lens is on top of
                # it: fade it out before it can smear across the frame
                d = float(np.linalg.norm(np.asarray(cam.eye, float)
                                         - np.asarray(c["pos"], float)))
                if d < 4.2:
                    fade *= float(np.clip((d - 2.4) / 1.8, 0.0, 1.0))
            tex = self.copy_textures[(c["text"], c.get("small", False))]''')

# ---------------------------------------------------------------- 5. light windows
sub('''        arch_i = arch["intensity"] * (0.35 + 0.65 * min(1.0, max(0.0, (t - 18.0) / 6.0)))''',
    '''        arch_i = arch["intensity"] * (0.35 + 0.65 * min(1.0, max(0.0, (t - 15.5) / 5.0)))''')
sub('''        rel_i = rel["intensity"] * (1.0 if 15.0 <= t <= 24.0
                                    else max(0.0, 1.0 - abs(t - 19.5) / 5.0) * 0.5)''',
    '''        rel_i = rel["intensity"] * (1.0 if 12.2 <= t <= 21.0
                                    else max(0.0, 1.0 - abs(t - 16.6) / 4.5) * 0.5)''')
sub('''        ch_i = ch["intensity"] * max(0.0, min(1.0, (t - 27.0) / 4.0))''',
    '''        ch_i = ch["intensity"] * max(0.0, min(1.0, (t - 24.0) / 4.0))''')

# ---------------------------------------------------------------- 6. the rake light
sub('''        scene.lights.append(R.Light(kind="directional", color=tuple(wash["color"]),
                                    intensity=wash["intensity"], direction=tuple(wash["dir"])))''',
    '''        scene.lights.append(R.Light(kind="directional", color=tuple(wash["color"]),
                                    intensity=wash["intensity"], direction=tuple(wash["dir"])))
        # a grazing light along the wall: gives the stone a value gradient and
        # lets the carved letters throw long shadows across it
        scene.lights.append(R.Light(kind="directional", color=(1.0, 0.80, 0.58),
                                    intensity=0.78, direction=(0.94, 0.15, 0.30)))''')

# the loop needs the same treatment
sub('''        scene.lights.append(R.Light(kind="directional", color=(0.32, 0.44, 0.66), intensity=0.24,
                                    direction=(0.55, -0.26, -0.79)))''',
    '''        scene.lights.append(R.Light(kind="directional", color=(0.32, 0.44, 0.66), intensity=0.24,
                                    direction=(0.55, -0.26, -0.79)))
        scene.lights.append(R.Light(kind="directional", color=(1.0, 0.80, 0.58), intensity=0.78,
                                    direction=(0.94, 0.15, 0.30)))''')

if s == orig:
    raise SystemExit("no change applied")
P.write_text(s)
print("scene.py patched:", len(s) - len(orig), "bytes delta")
