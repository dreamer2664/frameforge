#!/usr/bin/env python3
"""Revision 2b — the wall as lit stone, and the chamber as a room.

Fixes found by inspecting the revised frames:

  * the wall was uniformly lit and read as flat card -> the wall is dimmer
    again and a *travelling* band of light (the same light that finds the
    letters) now rakes across it, so the stone has a value gradient and the
    carved letters keep their long shadows;
  * the stone texture was magnified into sandpaper -> less grain, smaller tiles;
  * the chamber read as a flat cream card -> the glow is now a vertical
    gradient (a lit floor receding into darkness) instead of a bright panel.
"""
from pathlib import Path

P = Path(__file__).resolve().parent.parent / "scene.py"
s = P.read_text()
orig = s


def sub(old, new):
    global s
    if old not in s:
        raise SystemExit("PATTERN NOT FOUND:\n" + old[:200])
    s = s.replace(old, new, 1)


# --- a travelling band texture (warm, soft in x and y)
sub('''def stone_texture(seed=7, size=512):''',
    '''def band_texture(size=256):
    """A soft band of warm light: bright along the middle, fading in x and y."""
    x = np.linspace(-1.0, 1.0, size, dtype=np.float32)
    prof = np.exp(-3.4 * x * x)
    prof = (prof - prof.min()) / max(prof.max() - prof.min(), 1e-6)
    band = np.tile(prof, (size // 4, 1))
    y = np.linspace(0.0, 1.0, size // 4, dtype=np.float32)
    fall = (0.25 + 0.75 * (1.0 - y) ** 1.6)[:, None]
    band = band * fall
    rgb = np.stack([band * 1.0, band * 0.70, band * 0.42], axis=2)
    return rgb.astype(np.float32)


def stone_texture(seed=7, size=512):''')

# --- quieter grain in the stone
sub('''    grain = rng.normal(0, 0.010, (size, size)).astype(np.float32)''',
    '''    grain = rng.normal(0, 0.0045, (size, size)).astype(np.float32)''')

# --- the wall: dimmer, smaller tiles
sub('''        wall_mat = R.Material(base=tuple(pal["wall"]), spec=0.09, shininess=20.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))''',
    '''        wall_mat = R.Material(base=tuple(pal["wall"]), spec=0.09, shininess=20.0,
                              texture=self.stone, texture_uv=(3.0, 3.0))''')
s = s.replace('''        wall_mat = R.Material(base=tuple(pal["wall"]), spec=0.09, shininess=20.0,
                              texture=self.stone, texture_uv=(1.0, 1.0))''',
              '''        wall_mat = R.Material(base=tuple(pal["wall"]), spec=0.09, shininess=20.0,
                              texture=self.stone, texture_uv=(3.0, 3.0))''')

# --- the travelling band of light on the wall (build + build_loop share the text)
band_build = '''        # ---- the travelling band of light on the carved wall
        if "band" in self._band_cache:
            band_tex = self._band_cache["band"]
        else:
            band_tex = band_texture()
            self._band_cache["band"] = band_tex
        x_band, i_band = self.reveal_light(t)
        bw = 6.4
        q = quad([x_band - bw / 2, 0.0, z + 0.03], [x_band + bw / 2, 0.0, z + 0.03],
                 [x_band + bw / 2, 8.4, z + 0.03], [x_band - bw / 2, 8.4, z + 0.03],
                 normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=band_tex, additive=True,
                                        alpha=0.115 * min(1.0, i_band / 1.25),
                                        double_sided=True), False))

'''
sub('''        # ---- the carved letters
        rev = self.reveal(t)''',
    band_build + '''        # ---- the carved letters
        rev = self.reveal(t)''')

# --- the loop gets a static band instead (its light rotates)
sub('''        letter_mat = R.Material(base=tuple(pal["letter"]), spec=0.14, shininess=30.0,
                                texture=self.stone, texture_uv=(0.0016, 0.0016))''',
    '''        if "band" in self._band_cache:
            band_tex = self._band_cache["band"]
        else:
            band_tex = band_texture()
            self._band_cache["band"] = band_tex
        q = quad([3.0, 0.0, z + 0.03], [10.4, 0.0, z + 0.03], [10.4, 8.4, z + 0.03],
                 [3.0, 8.4, z + 0.03], normal=(0, 0, 1),
                 uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=band_tex, additive=True, alpha=0.085,
                                        double_sided=True), False))
        letter_mat = R.Material(base=tuple(pal["letter"]), spec=0.14, shininess=30.0,
                                texture=self.stone, texture_uv=(0.0016, 0.0016))''')

# --- the chamber glow becomes a vertical gradient, dimmer
sub('''        q = quad([-cx + 1, 0, cz + 0.12], [cx - 1, 0, cz + 0.12],
                 [cx - 1, ch_h - 1, cz + 0.12], [-cx + 1, ch_h - 1, cz + 0.12],
                 normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0.34, 0.19, 0.085),
                                        texture=self.glow_tex, additive=True, alpha=0.20), False))''',
    '''        q = quad([-cx + 1, 0, cz + 0.12], [cx - 1, 0, cz + 0.12],
                 [cx - 1, ch_h - 1, cz + 0.12], [-cx + 1, ch_h - 1, cz + 0.12],
                 normal=(0, 0, 1), uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
        scene.meshes.append((q[0], q[1], q[2], q[3],
                             R.Material(base=(0, 0, 0), emissive=(0, 0, 0),
                                        texture=self.chamber_tex, additive=True,
                                        alpha=0.42, double_sided=True), False))''')

# --- the chamber gradient texture
sub('''        self.glow_tex = glow_texture()''',
    '''        self.glow_tex = glow_texture()
        self._band_cache = {}
        # the chamber light: bright at the floor, falling away into the dark
        gx = np.linspace(0.0, 1.0, 64, dtype=np.float32)
        gy = np.linspace(0.0, 1.0, 64, dtype=np.float32)
        fall = np.exp(-2.2 * gy)[:, None] * (0.55 + 0.45 * (1.0 - np.abs(gx - 0.5) * 2.0) ** 2)[None, :]
        self.chamber_tex = np.stack([fall * 1.0, fall * 0.62, fall * 0.30], axis=2).astype(np.float32)''')

# --- the rake light is dimmer now that the band carries the drama
s = s.replace('''        scene.lights.append(R.Light(kind="directional", color=(1.0, 0.80, 0.58),
                                    intensity=0.78, direction=(0.94, 0.15, 0.30)))''',
              '''        scene.lights.append(R.Light(kind="directional", color=(1.0, 0.80, 0.58),
                                    intensity=0.45, direction=(0.94, 0.15, 0.30)))''')

# --- the wall albedo: between the old void and the new flat card
P.write_text(s)
print("scene.py delta:", len(s) - len(orig))
