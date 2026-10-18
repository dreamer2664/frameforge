"""Stage render: 384 frames @30fps. Camera drift + act-locked punch-ins, screen texture
per frame, lean Cycles. blender -b --python-exit-code 1 --python render_stage.py
"""
import bpy, math, time
from pathlib import Path
from mathutils import Vector, Quaternion

ROOT = Path('/home/user/work/frameforge/agents/lithos/reel')
FPS = 30
N = 384

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'scene/reel-stage.blend'))
sc = bpy.context.scene

# lean cycles (measured: ~50s/frame at 20 samples on this box)
sc.cycles.samples = 20
sc.cycles.adaptive_threshold = 0.06
sc.cycles.use_adaptive_sampling = True
sc.cycles.max_bounces = 4
sc.cycles.diffuse_bounces = 2
sc.cycles.glossy_bounces = 2
sc.cycles.transmission_bounces = 0
sc.cycles.transparent_max_bounces = 0
sc.cycles.sample_clamp_indirect = 4.0
sc.render.use_persistent_data = True

cam = bpy.data.objects['CAM_MAIN']
cam.rotation_mode = 'QUATERNION'
base_loc = Vector((0.225, -1.045, 0.315))
target = Vector((0, 0.125, 0.118))
view = (base_loc - target).normalized()  # push-in = move toward target along -view

CUTS = [1.55, 4.35, 6.0, 8.0, 10.0, 11.55]

mat = bpy.data.materials['screen_emission']
texnode = mat.node_tree.nodes['ScreenTex']
SCR = Path('/tmp/reel-screen')
img = bpy.data.images.load(str(SCR / '0000.png'), check_existing=False)
texnode.image = img
sc.render.image_settings.file_format = 'JPEG'
sc.render.image_settings.quality = 93

out_dir = Path('/tmp/reel-frames')
out_dir.mkdir(parents=True, exist_ok=True)

t0 = time.time()
for fr in range(N):
    t = fr / FPS
    # drift
    loc = base_loc + Vector((
        math.sin(t * 0.55) * 0.010 + math.sin(t * 1.31) * 0.0035,
        math.sin(t * 0.42 + 1.3) * 0.012,
        math.sin(t * 0.61 + 2.2) * 0.008))
    # punch-ins at cuts
    push = 0.0
    for tc in CUTS:
        u = (t - tc) / 0.55
        if 0 < u < 1:
            push += 0.042 * math.sin(math.pi * u) ** 0.8
    # final sustained push on the end card
    if t >= 12.0:
        push += 0.075 * min(1.0, (t - 12.0) / 0.8) ** 0.7
    loc = loc - view * push
    cam.location = loc
    roll = math.radians(-5.0 + 0.55 * math.sin(t * 0.37) + 0.25 * math.sin(t * 1.1))
    cam.rotation_quaternion = (target - loc).to_track_quat('-Z', 'Y') @ Quaternion((0, 0, 1), roll)

    img.filepath = str(SCR / f'{fr:04d}.png')
    img.reload()
    sc.render.filepath = str(out_dir / f'{fr:04d}.jpg')
    bpy.ops.render.render(write_still=True)
    if fr % 4 == 0 or fr == N - 1:
        el = time.time() - t0
        eta = el / (fr + 1) * (N - fr - 1)
        print(f'FRAME {fr}/{N} elapsed={el:.0f}s eta={eta:.0f}s', flush=True)
print('RENDER_DONE', flush=True)
